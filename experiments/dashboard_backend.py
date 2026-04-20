"""Pure query helpers backing the experiments dashboard."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

try:
    from gmcore_dashboard.experiments.compare import compare_experiments
except Exception:  # pragma: no cover - stage-C compatibility fallback
    compare_experiments = None


def _default_root() -> Path:
    return Path(__file__).resolve().parent / "experiments"


def _resolve_root(root: Path | str | None) -> Path:
    if root is None:
        return _default_root()
    return Path(root).expanduser().resolve()


def _db_path(root: Path) -> Path:
    return root / "experiments.db"


def _connect(root: Path) -> sqlite3.Connection | None:
    db_path = _db_path(root)
    if not db_path.is_file():
        return None
    conn = sqlite3.connect(db_path.as_posix())
    conn.row_factory = sqlite3.Row
    return conn


def _loads_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _flatten_params(data: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    if "resolved_params_by_group" in data and isinstance(data["resolved_params_by_group"], dict):
        flattened: dict[str, Any] = {}
        for group_values in data["resolved_params_by_group"].values():
            if isinstance(group_values, dict):
                flattened.update(group_values)
        return flattened
    return dict(data)


def _tail_text(path: Path, max_lines: int = 200) -> str:
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[-max_lines:])


def _metadata_from_row(row: sqlite3.Row, root: Path) -> dict[str, Any]:
    metadata = _loads_json(row["metadata_json"])
    experiment_dir = (
        metadata.get("paths", {}).get("experiment_dir")
        if isinstance(metadata.get("paths"), dict)
        else None
    )
    if not experiment_dir:
        experiment_dir = str((root / str(row["experiment_id"])).resolve())
    metadata.setdefault("paths", {})
    metadata["paths"].setdefault("experiment_dir", experiment_dir)
    return metadata


def _metric_summary(metrics: dict[str, Any]) -> dict[str, Any]:
    return metrics if isinstance(metrics, dict) else {}


def _record_from_row(row: sqlite3.Row, root: Path) -> dict[str, Any]:
    metadata = _metadata_from_row(row, root)
    metrics = _metric_summary(_loads_json(row["metrics_json"]))
    params = _flatten_params(metadata)
    tags = metadata.get("tags") if isinstance(metadata.get("tags"), list) else []
    return {
        "experiment_id": row["experiment_id"],
        "name": row["name"],
        "baseline": row["baseline"],
        "parent_experiment_id": row["parent_experiment_id"],
        "sweep_id": row["sweep_id"],
        "sweep_index": row["sweep_index"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "pid": row["pid"],
        "exit_code": row["exit_code"],
        "tags": tags,
        "metadata": metadata,
        "metrics": metrics,
        "alpha_d": params.get("alpha_d"),
        "tau_thresh": params.get("tau_thresh"),
        "alpha_n": params.get("alpha_n"),
    }


def scan_experiments(root: Path | str | None = None) -> list[dict[str, Any]]:
    root_path = _resolve_root(root)
    conn = _connect(root_path)
    if conn is None:
        return []
    try:
        rows = conn.execute(
            """
            SELECT
              experiment_id, name, baseline, parent_experiment_id,
              sweep_id, sweep_index, status, created_at, updated_at,
              pid, exit_code, metadata_json, metrics_json
            FROM experiments
            ORDER BY updated_at DESC, created_at DESC
            """
        ).fetchall()
    finally:
        conn.close()
    return [_record_from_row(row, root_path) for row in rows]


def _load_row(exp_id: str, root: Path) -> sqlite3.Row | None:
    conn = _connect(root)
    if conn is None:
        return None
    try:
        return conn.execute(
            """
            SELECT
              experiment_id, name, baseline, parent_experiment_id,
              sweep_id, sweep_index, status, created_at, updated_at,
              pid, exit_code, metadata_json, metrics_json
            FROM experiments
            WHERE experiment_id = ?
            """,
            (exp_id,),
        ).fetchone()
    finally:
        conn.close()


def load_detail(exp_id: str, root: Path | str | None = None) -> dict[str, Any]:
    root_path = _resolve_root(root)
    row = _load_row(exp_id, root_path)
    if row is None:
        return {}

    record = _record_from_row(row, root_path)
    metadata = record["metadata"]
    exp_dir = Path(metadata.get("paths", {}).get("experiment_dir", root_path / exp_id))
    metadata_path = exp_dir / "metadata.json"
    metrics_path = exp_dir / "metrics.json"

    if metadata_path.is_file():
        metadata = _loads_json(metadata_path.read_text(encoding="utf-8", errors="replace"))
        metadata.setdefault("paths", {})
        metadata["paths"].setdefault("experiment_dir", exp_dir.as_posix())
    if metrics_path.is_file():
        record["metrics"] = _loads_json(metrics_path.read_text(encoding="utf-8", errors="replace"))

    paths = metadata.get("paths") if isinstance(metadata.get("paths"), dict) else {}
    log_candidates = [
        Path(paths.get("run_log", exp_dir / "logs" / "run.log")),
        exp_dir / "log.txt",
    ]
    diagnostics_dir = Path(
        paths.get("diagnostics_dir", exp_dir / "artifacts" / "diagnostics")
    )

    diagnostics: list[dict[str, Any]] = []
    if diagnostics_dir.is_dir():
        for path in sorted(diagnostics_dir.rglob("*.png")):
            try:
                relative = path.relative_to(root_path).as_posix()
            except ValueError:
                relative = path.name
            diagnostics.append(
                {
                    "name": path.name,
                    "path": path.as_posix(),
                    "relative_path": relative,
                    "asset_path": f"/experiments-assets/{relative}",
                }
            )

    log_path = next((candidate for candidate in log_candidates if candidate.is_file()), None)
    record["metadata"] = metadata
    record["params"] = _flatten_params(metadata)
    record["diagnostics"] = diagnostics
    record["log_tail"] = _tail_text(log_path) if log_path else ""
    return record


def load_compare(a_id: str, b_id: str, root: Path | str | None = None) -> dict[str, Any]:
    root_path = _resolve_root(root)
    detail_a = load_detail(a_id, root_path)
    detail_b = load_detail(b_id, root_path)
    payload: dict[str, Any] = {}

    if compare_experiments is not None:
        try:
            compared = compare_experiments(a_id, b_id)
            if isinstance(compared, dict):
                payload.update(compared)
        except Exception:
            payload = {}

    params_a = detail_a.get("params", {})
    params_b = detail_b.get("params", {})
    param_rows = payload.get("param_rows")
    if not isinstance(param_rows, list):
        param_rows = []
        for name in sorted(set(params_a) | set(params_b)):
            value_a = params_a.get(name)
            value_b = params_b.get(name)
            is_changed = value_a != value_b
            param_rows.append(
                {
                    "parameter": name,
                    "a": value_a,
                    "b": value_b,
                    "changed": "yes" if is_changed else "",
                    "status_text": "Changed" if is_changed else "Same",
                }
            )
    else:
        for row in param_rows:
            if "status_text" not in row:
                row["status_text"] = "Changed" if row.get("changed") == "yes" else "Same"

    diag_map_a = {item["name"]: item for item in detail_a.get("diagnostics", [])}
    diag_map_b = {item["name"]: item for item in detail_b.get("diagnostics", [])}
    paired = []
    for name in sorted(set(diag_map_a) | set(diag_map_b)):
        paired.append({"name": name, "a": diag_map_a.get(name), "b": diag_map_b.get(name)})

    payload.update({"a": detail_a, "b": detail_b, "param_rows": param_rows, "paired_diagnostics": paired})
    return payload


def load_sweep_family(sweep_id: str, root: Path | str | None = None) -> list[dict[str, Any]]:
    if not sweep_id:
        return []
    return [record for record in scan_experiments(root) if record.get("sweep_id") == sweep_id]


def newest_nc_for(exp_id: str, root: Path | str | None = None) -> Path | None:
    detail = load_detail(exp_id, root)
    metadata = detail.get("metadata", {})
    exp_dir = Path(metadata.get("paths", {}).get("experiment_dir", _resolve_root(root) / exp_id))
    candidates = list(exp_dir.glob("*.h0*.nc")) + list((exp_dir / "output").glob("*.h0*.nc"))
    candidates = [path for path in candidates if path.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)
