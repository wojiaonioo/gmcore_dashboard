from __future__ import annotations

"""Build and run process manager for the GMCORE Dashboard."""

import collections
import dataclasses
import os
import shlex
import signal
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Optional


@dataclasses.dataclass
class ProcessInfo:
    job_id: str
    label: str
    process: subprocess.Popen
    status: str
    exit_code: Optional[int]
    start_time: float
    end_time: Optional[float]
    cwd: str
    metadata: dict[str, object] = dataclasses.field(default_factory=dict)


class JobManager:
    def __init__(self, gmcore_root: str, conda_env: str = "gmcore"):
        self.gmcore_root = Path(gmcore_root).expanduser().resolve()
        self.conda_env = conda_env
        self.conda_prefix = self._find_conda_prefix()
        self.build_dir = self.gmcore_root / "build"
        self.processes: dict[str, ProcessInfo] = {}
        self.logs: dict[str, collections.deque[str]] = {}
        self._lock = threading.Lock()

    def _find_conda_prefix(self) -> str:
        try:
            result = subprocess.run(
                ["conda", "info", "--envs"],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            result = None

        if result is not None and result.returncode == 0:
            for raw_line in result.stdout.splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if not parts:
                    continue
                if parts[0] == self.conda_env and parts[-1].startswith("/"):
                    return parts[-1]

        # Portable fallback: probe common conda install locations.
        candidates = []
        for var in ("CONDA_ROOT", "CONDA_EXE"):
            raw = os.environ.get(var)
            if not raw:
                continue
            base = Path(raw).parent if var == "CONDA_EXE" else Path(raw)
            candidates.append(base / "envs" / self.conda_env)
        for base in ("~/anaconda3", "~/miniconda3", "~/miniforge3",
                     "~/mambaforge", "/opt/conda"):
            candidates.append(Path(base).expanduser() / "envs" / self.conda_env)
        for cand in candidates:
            if cand.is_dir():
                return str(cand)
        # Last resort: return the best-guess path (may not exist) so the
        # caller's error surfaces as a missing-env rather than silent misroute.
        return str(candidates[-1]) if candidates else self.conda_env

    def _conda_cmd(self, cmd: str) -> str:
        return (
            f"conda run --no-capture-output -n {shlex.quote(self.conda_env)} "
            f"bash -c {shlex.quote(cmd)}"
        )

    def configure(self, build_type: str = "Release", extra_cmake_args: str = "") -> str:
        self.build_dir.mkdir(parents=True, exist_ok=True)

        cmake_cmd = f"cmake .. -DCMAKE_BUILD_TYPE={shlex.quote(build_type)}"
        if extra_cmake_args.strip():
            cmake_cmd = f"{cmake_cmd} {extra_cmake_args.strip()}"

        cmd = self._conda_cmd(
            " && ".join(
                [
                    self._env_exports(),
                    f"cd {shlex.quote(str(self.build_dir))}",
                    cmake_cmd,
                ]
            )
        )
        job_id = self._new_job_id()
        self._start_process(
            job_id,
            cmd,
            label="Configure",
            cwd=str(self.build_dir),
            metadata={"kind": "configure"},
        )
        return job_id

    def build(self, jobs: int = 0) -> str:
        if jobs <= 0:
            jobs = os.cpu_count() or 1

        cmd = self._conda_cmd(
            " && ".join(
                [
                    self._env_exports(),
                    f"make -j{jobs} -C {shlex.quote(str(self.build_dir))}",
                ]
            )
        )
        job_id = self._new_job_id()
        self._start_process(
            job_id,
            cmd,
            label="Build",
            cwd=str(self.build_dir),
            metadata={"kind": "build"},
        )
        return job_id

    def run_case(self, case_name: str, nprocs: int = 2, work_dir: str = None) -> str:
        case_dir = self._resolve_case_dir(case_name, work_dir)
        namelist_path = case_dir / "namelist"
        if not case_dir.is_dir():
            raise FileNotFoundError(f"Case directory not found: {case_dir}")
        if not namelist_path.is_file():
            raise FileNotFoundError(f"Namelist not found: {namelist_path}")

        executable = self.build_dir / self._get_executable_name(case_name)
        if not executable.is_file():
            raise FileNotFoundError(f"Executable not found: {executable}")

        nprocs = max(1, int(nprocs))
        cmd = self._conda_cmd(
            " && ".join(
                [
                    self._env_exports(),
                    f"cd {shlex.quote(str(case_dir))}",
                    (
                        f"mpiexec -np {nprocs} "
                        f"{shlex.quote(str(executable))} namelist"
                    ),
                ]
            )
        )
        job_id = self._new_job_id()
        self._start_process(
            job_id,
            cmd,
            label=f"Run: {case_name}",
            cwd=str(case_dir),
            metadata={
                "kind": "run",
                "case_name": case_name,
                "nprocs": nprocs,
                "work_dir": str(case_dir),
            },
        )
        return job_id

    def build_and_run(
        self, case_name: str, nprocs: int = 2, build_type: str = "Release"
    ) -> str:
        configure_job_id = self.configure(build_type=build_type)
        self._ensure_completed(configure_job_id, f"Configure failed for {case_name}")

        build_job_id = self.build()
        self._ensure_completed(build_job_id, f"Build failed for {case_name}")

        run_job_id = self.run_case(case_name, nprocs=nprocs)
        return run_job_id

    def _start_process(
        self,
        job_id: str,
        cmd: str,
        label: str,
        cwd: str = None,
        metadata: Optional[dict[str, object]] = None,
    ) -> None:
        requested_cwd = Path(cwd).expanduser() if cwd is not None else self.gmcore_root
        process_cwd = str(requested_cwd if requested_cwd.is_dir() else self.gmcore_root)
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=process_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            preexec_fn=os.setsid,
        )
        info = ProcessInfo(
            job_id=job_id,
            label=label,
            process=process,
            status="running",
            exit_code=None,
            start_time=time.time(),
            end_time=None,
            cwd=process_cwd,
            metadata=dict(metadata or {}),
        )

        with self._lock:
            self.processes[job_id] = info
            self.logs[job_id] = collections.deque(maxlen=5000)

        reader = threading.Thread(
            target=self._read_process_output,
            args=(job_id,),
            daemon=True,
            name=f"job-reader-{job_id}",
        )
        reader.start()

    def get_status(self, job_id: str) -> dict:
        with self._lock:
            info = self.processes.get(job_id)
            if info is None:
                return {
                    "job_id": job_id,
                    "label": "",
                    "status": "not_found",
                    "exit_code": None,
                    "pid": None,
                    "start_time": 0.0,
                    "elapsed": 0.0,
                }

            self._refresh_process_state(info)
            status = info.status
            exit_code = info.exit_code
            pid = info.process.pid
            start_time = info.start_time
            label = info.label
            cwd = info.cwd
            metadata = dict(info.metadata)

        return {
            "job_id": job_id,
            "label": label,
            "status": status,
            "exit_code": exit_code,
            "pid": pid,
            "start_time": start_time,
            "elapsed": (info.end_time or time.time()) - start_time,
            "cwd": cwd,
            "metadata": metadata,
        }

    def get_logs(self, job_id: str, last_n: int = 100) -> list[str]:
        with self._lock:
            job_logs = self.logs.get(job_id)
            if job_logs is None:
                return []

            lines = list(job_logs)

        if last_n <= 0:
            return lines
        return lines[-last_n:]

    def get_log_count(self, job_id: str) -> int:
        with self._lock:
            job_logs = self.logs.get(job_id)
            if job_logs is None:
                return 0
            return len(job_logs)

    def stop(self, job_id: str) -> bool:
        with self._lock:
            info = self.processes.get(job_id)
            if info is None:
                return False

            self._refresh_process_state(info)
            if info.status != "running":
                return False

            pid = info.process.pid

        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            info.process.wait(timeout=5)
        except ProcessLookupError:
            return False
        except subprocess.TimeoutExpired:
            return False
        except OSError:
            return False

        with self._lock:
            self._refresh_process_state(info)

        return True

    def list_jobs(self) -> list[dict]:
        with self._lock:
            job_ids = list(self.processes.keys())

        jobs = [self.get_status(job_id) for job_id in job_ids]
        jobs.sort(key=lambda item: item["start_time"], reverse=True)
        return jobs

    def clean_build(self) -> str:
        clean_cmd = self._conda_cmd(
            " && ".join(
                [
                    self._env_exports(),
                    f"make clean -C {shlex.quote(str(self.build_dir))}",
                ]
            )
        )
        clean_job_id = self._new_job_id()
        self._start_process(
            clean_job_id,
            clean_cmd,
            label="Clean",
            cwd=str(self.build_dir),
            metadata={"kind": "clean"},
        )
        self._ensure_completed(clean_job_id, "Clean build failed")
        return self.configure()

    def _env_exports(self) -> str:
        return " && ".join(
            [
                # Strip host-shell pollution that overrides env RPATH / pkg-config
                "unset LD_LIBRARY_PATH LIBRARY_PATH PKG_CONFIG_PATH "
                "C_INCLUDE_PATH CPATH FPATH LDFLAGS CPPFLAGS "
                "CFLAGS FFLAGS CXXFLAGS",
                f"export CONDA_PREFIX={shlex.quote(self.conda_prefix)}",
                'export NETCDF_ROOT="$CONDA_PREFIX"',
                # Force MPI wrappers so CMake picks parallel-enabled netcdf/hdf5
                "export CC=mpicc CXX=mpicxx FC=mpifort",
            ]
        )

    def _get_executable_name(self, case_name: str) -> str:
        if case_name.startswith("adv_"):
            return "gmcore_adv_driver.exe"
        return "gmcore_driver.exe"

    def _resolve_case_dir(self, case_name: str, work_dir: Optional[str]) -> Path:
        if work_dir is None:
            return self.gmcore_root / "run" / "GMCORE-TESTBED" / case_name

        case_dir = Path(work_dir).expanduser()
        if not case_dir.is_absolute():
            case_dir = self.gmcore_root / case_dir
        return case_dir.resolve()

    def _new_job_id(self) -> str:
        return str(uuid.uuid4())[:8]

    def _append_log(self, job_id: str, line: str) -> None:
        with self._lock:
            job_logs = self.logs.get(job_id)
            if job_logs is not None:
                job_logs.append(line)

    def _read_process_output(self, job_id: str) -> None:
        with self._lock:
            info = self.processes.get(job_id)

        if info is None:
            return

        try:
            if info.process.stdout is not None:
                for line in info.process.stdout:
                    self._append_log(job_id, line.rstrip("\n"))
        except Exception as exc:
            self._append_log(job_id, f"[job-manager] log reader failed: {exc}")
        finally:
            if info.process.stdout is not None:
                info.process.stdout.close()

            exit_code = info.process.wait()
            with self._lock:
                current = self.processes.get(job_id)
                if current is not None:
                    current.exit_code = exit_code
                    current.status = "completed" if exit_code == 0 else "failed"
                    if current.end_time is None:
                        current.end_time = time.time()

    def _refresh_process_state(self, info: ProcessInfo) -> None:
        exit_code = info.process.poll()
        if exit_code is None:
            return

        info.exit_code = exit_code
        info.status = "completed" if exit_code == 0 else "failed"
        if info.end_time is None:
            info.end_time = time.time()

    def _wait_for_completion(self, job_id: str) -> dict:
        while True:
            status = self.get_status(job_id)
            if status["status"] != "running":
                return status
            time.sleep(0.25)

    def _ensure_completed(self, job_id: str, message: str) -> None:
        status = self._wait_for_completion(job_id)
        if status["status"] != "completed":
            raise RuntimeError(
                f"{message} (job_id={job_id}, exit_code={status['exit_code']})"
            )
