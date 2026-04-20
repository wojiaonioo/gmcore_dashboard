from __future__ import annotations

import os
import queue
import signal
import sqlite3
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from .models import RunRecord, Status
from .store import Store, utcnow


_STRIP_ENV_VARS = [
    "LD_LIBRARY_PATH",
    "LIBRARY_PATH",
    "PKG_CONFIG_PATH",
    "C_INCLUDE_PATH",
    "CPATH",
    "FPATH",
    "LDFLAGS",
    "CPPFLAGS",
    "CFLAGS",
    "FFLAGS",
    "CXXFLAGS",
]


def _find_conda_prefix(env_name: str = "gmcore") -> str | None:
    candidates = [
        Path("~/anaconda3").expanduser() / "envs" / env_name,
        Path("~/miniconda3").expanduser() / "envs" / env_name,
        Path("~/miniforge3").expanduser() / "envs" / env_name,
        Path("~/mambaforge").expanduser() / "envs" / env_name,
        Path("/opt/conda") / "envs" / env_name,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.as_posix()
    return None


def clean_env() -> dict[str, str]:
    env = dict(os.environ)
    for name in _STRIP_ENV_VARS:
        env.pop(name, None)
    prefix = _find_conda_prefix()
    if prefix:
        env["CONDA_PREFIX"] = prefix
        env["NETCDF_ROOT"] = prefix
    return env


def build_run_command(experiment: dict[str, Any]) -> list[str]:
    run_config = experiment["run_config"]
    return [
        str(run_config["launcher"]),
        "-n",
        str(run_config["mpi_ranks"]),
        str(run_config["executable"]),
        "namelist",
    ]


def _pid_alive(pid: int | None) -> bool:
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def recover_running_experiments(store: Store | None = None) -> list[str]:
    store = store or Store()
    recovered: list[str] = []
    for row in store.iter_running():
        experiment_id = str(row["experiment_id"])
        metadata = store.load_metadata(experiment_id)
        pid = metadata.get("pid")
        if not isinstance(pid, int) or not _pid_alive(pid):
            store.update_status(experiment_id, Status.INTERRUPTED, pid=None)
            recovered.append(experiment_id)
    return recovered


def _reader_thread(stdout: Any, sink: queue.Queue[str | None]) -> None:
    try:
        if stdout is not None:
            for line in stdout:
                sink.put(line.rstrip("\n"))
    finally:
        sink.put(None)


def _discover_outputs(metadata: dict[str, Any]) -> list[str]:
    experiment_dir = Path(metadata["paths"]["experiment_dir"])
    case_name = str(metadata["derived"]["case_name"])
    files = sorted(experiment_dir.glob(f"{case_name}.h*.nc"))
    return [path.resolve().as_posix() for path in files if path.is_file()]


def _terminate_process_group(proc: subprocess.Popen[str], grace_s: float = 5.0) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=grace_s)
    except ProcessLookupError:
        return
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()


def _run_lock_path(experiment_dir: Path) -> Path:
    return experiment_dir / ".run.lock"


def _acquire_run_lock(experiment_dir: Path) -> int:
    lock_path = _run_lock_path(experiment_dir)
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                pid = int(lock_path.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                pid = None
            if pid is not None and _pid_alive(pid):
                raise RuntimeError(
                    f"Experiment directory is already in use by pid {pid}: {experiment_dir}"
                )
            lock_path.unlink(missing_ok=True)
            continue
        os.write(fd, f"{os.getpid()}\n".encode("utf-8"))
        return fd


def _release_run_lock(experiment_dir: Path, fd: int | None) -> None:
    if fd is None:
        return
    try:
        os.close(fd)
    except OSError:
        pass
    _run_lock_path(experiment_dir).unlink(missing_ok=True)


def _safe_touch(store: Store, experiment_id: str, **fields: Any) -> None:
    try:
        store.touch(experiment_id, **fields)
    except sqlite3.OperationalError:
        pass


def run_experiment(experiment_id: str, store: Store | None = None) -> RunRecord:
    store = store or Store()
    recover_running_experiments(store)
    metadata = store.load_metadata(experiment_id)
    experiment_dir = Path(metadata["paths"]["experiment_dir"])
    log_path = Path(metadata["paths"]["run_log"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_run_command(metadata)
    timeout_s = int(metadata["run_config"].get("timeout_s", 0) or 0)
    start_monotonic = time.monotonic()
    started_at = utcnow()
    lock_fd = _acquire_run_lock(experiment_dir)

    proc: subprocess.Popen[str] | None = None
    timed_out = False
    exit_code: int = -1
    try:
        store.update_status(experiment_id, Status.QUEUED)
        proc = subprocess.Popen(
            command,
            cwd=experiment_dir,
            env=clean_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            start_new_session=True,
        )
        store.update_status(
            experiment_id,
            Status.RUNNING,
            pid=proc.pid,
            started_at=started_at,
        )

        last_heartbeat = time.monotonic()
        read_queue: queue.Queue[str | None] = queue.Queue()
        reader = threading.Thread(target=_reader_thread, args=(proc.stdout, read_queue), daemon=True)
        reader.start()

        with log_path.open("a", encoding="utf-8") as handle:
            while True:
                try:
                    item = read_queue.get(timeout=0.5)
                except queue.Empty:
                    item = None
                if timeout_s > 0 and (time.monotonic() - start_monotonic) >= timeout_s:
                    timed_out = True
                    _terminate_process_group(proc)
                    break
                if item is None:
                    if proc.poll() is not None and not reader.is_alive():
                        break
                else:
                    handle.write(item + "\n")
                    handle.flush()
                if (time.monotonic() - last_heartbeat) >= 5.0:
                    _safe_touch(store, experiment_id, pid=proc.pid)
                    last_heartbeat = time.monotonic()

        if proc.stdout is not None:
            proc.stdout.close()
        exit_code = proc.wait()
    finally:
        _release_run_lock(experiment_dir, lock_fd)

    outputs = _discover_outputs(metadata)
    ended_at = utcnow()
    final_status = (
        Status.TIMEOUT
        if timed_out
        else (Status.COMPLETED if exit_code == 0 else Status.FAILED)
    )
    store.update_status(
        experiment_id,
        final_status,
        pid=None,
        exit_code=exit_code,
        ended_at=ended_at,
        outputs=outputs,
    )
    return RunRecord(
        experiment_id=experiment_id,
        status=final_status,
        pid=None,
        exit_code=exit_code,
        started_at=started_at,
        ended_at=ended_at,
        log_path=log_path,
        output_files=[Path(path) for path in outputs],
    )
