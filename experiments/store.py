from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .models import Status


_SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
  experiment_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  baseline TEXT,
  parent_experiment_id TEXT,
  sweep_id TEXT,
  sweep_index INTEGER,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  pid INTEGER,
  exit_code INTEGER,
  metadata_json TEXT NOT NULL,
  metrics_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_sweep ON experiments(sweep_id);
"""


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    return value


def default_workspace_root(root: str | Path | None = None) -> Path:
    if root is not None:
        return Path(root).expanduser().resolve()
    return (Path(__file__).resolve().parent / "experiments").resolve()


class Store:
    def __init__(self, root: str | Path | None = None):
        self.root = default_workspace_root(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "experiments.db"
        self._bootstrap()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def _bootstrap(self) -> None:
        with self.connect() as conn:
            conn.executescript(_SCHEMA)

    def _existing_metrics_json(self, experiment_id: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT metrics_json FROM experiments WHERE experiment_id = ?",
                (experiment_id,),
            ).fetchone()
        return None if row is None else row["metrics_json"]

    def _write_metadata_snapshot(self, metadata: dict[str, Any]) -> None:
        experiment_dir = Path(metadata["paths"]["experiment_dir"])
        experiment_dir.mkdir(parents=True, exist_ok=True)
        path = experiment_dir / "metadata.json"
        path.write_text(json.dumps(_normalize(metadata), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _write_metrics_snapshot(self, metadata: dict[str, Any], metrics: dict[str, Any]) -> None:
        path = Path(metadata["paths"]["metrics_json"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_normalize(metrics), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _upsert_metadata(self, metadata: dict[str, Any], metrics_json: str | None) -> None:
        normalized = _normalize(metadata)
        metadata_text = json.dumps(normalized, sort_keys=True)
        self._write_metadata_snapshot(normalized)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO experiments (
                  experiment_id, name, baseline, parent_experiment_id, sweep_id, sweep_index,
                  status, created_at, updated_at, pid, exit_code, metadata_json, metrics_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(experiment_id) DO UPDATE SET
                  name=excluded.name,
                  baseline=excluded.baseline,
                  parent_experiment_id=excluded.parent_experiment_id,
                  sweep_id=excluded.sweep_id,
                  sweep_index=excluded.sweep_index,
                  status=excluded.status,
                  created_at=excluded.created_at,
                  updated_at=excluded.updated_at,
                  pid=excluded.pid,
                  exit_code=excluded.exit_code,
                  metadata_json=excluded.metadata_json,
                  metrics_json=excluded.metrics_json
                """,
                (
                    normalized["experiment_id"],
                    normalized["name"],
                    normalized.get("baseline"),
                    normalized.get("parent_experiment_id"),
                    normalized.get("sweep_id"),
                    normalized.get("sweep_index"),
                    normalized["status"],
                    normalized["created_at"],
                    normalized["updated_at"],
                    normalized.get("pid"),
                    normalized.get("exit_code"),
                    metadata_text,
                    metrics_json,
                ),
            )

    def insert_experiment(self, metadata: dict[str, Any]) -> None:
        metadata = dict(metadata)
        metadata.setdefault("created_at", utcnow())
        metadata.setdefault("updated_at", metadata["created_at"])
        self._upsert_metadata(metadata, metrics_json=None)

    def save_metadata(self, metadata: dict[str, Any]) -> None:
        metadata = dict(metadata)
        metadata["updated_at"] = utcnow()
        metrics_json = self._existing_metrics_json(metadata["experiment_id"])
        self._upsert_metadata(metadata, metrics_json)

    def update_status(self, experiment_id: str, status: str | Status, **fields: Any) -> dict[str, Any]:
        metadata = self.load_metadata(experiment_id)
        metadata["status"] = status.value if isinstance(status, Status) else str(status)
        metadata["updated_at"] = utcnow()
        metadata.update(_normalize(fields))
        metrics_json = self._existing_metrics_json(experiment_id)
        self._upsert_metadata(metadata, metrics_json)
        return metadata

    def touch(self, experiment_id: str, **fields: Any) -> dict[str, Any]:
        metadata = self.load_metadata(experiment_id)
        metadata["updated_at"] = utcnow()
        metadata.update(_normalize(fields))
        metrics_json = self._existing_metrics_json(experiment_id)
        self._upsert_metadata(metadata, metrics_json)
        return metadata

    def load_metadata(self, experiment_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT metadata_json FROM experiments WHERE experiment_id = ?",
                (experiment_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown experiment id: {experiment_id}")
        return json.loads(row["metadata_json"])

    def load_metrics(self, experiment_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT metrics_json FROM experiments WHERE experiment_id = ?",
                (experiment_id,),
            ).fetchone()
        if row is None or row["metrics_json"] is None:
            return None
        return json.loads(row["metrics_json"])

    def update_metrics(self, experiment_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
        metadata = self.load_metadata(experiment_id)
        metrics_payload = _normalize(metrics)
        self._write_metrics_snapshot(metadata, metrics_payload)
        metrics_text = json.dumps(metrics_payload, sort_keys=True)
        metadata["updated_at"] = utcnow()
        self._upsert_metadata(metadata, metrics_text)
        return metrics_payload

    def list_experiments(
        self,
        *,
        status: str | None = None,
        sweep_id: str | None = None,
        name: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if status:
            clauses.append("status = ?")
            params.append(status)
        if sweep_id:
            clauses.append("sweep_id = ?")
            params.append(sweep_id)
        if name:
            clauses.append("name = ?")
            params.append(name)
        query = """
            SELECT experiment_id, name, baseline, parent_experiment_id, sweep_id, sweep_index,
                   status, created_at, updated_at, pid, exit_code
            FROM experiments
        """
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC"
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def iter_running(self) -> list[dict[str, Any]]:
        return self.list_experiments(status=Status.RUNNING.value)
