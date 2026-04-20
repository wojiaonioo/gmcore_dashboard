from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Status(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


def _to_primitive(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _to_primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_primitive(item) for item in value]
    return value


@dataclass(slots=True)
class ExperimentSpec:
    name: str
    baseline: str | None = None
    parent: str | None = None
    description: str = ""
    template: Path | None = None
    params: dict[str, Any] = field(default_factory=dict)
    sweep: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(asdict(self))


@dataclass(slots=True)
class ResolvedExperiment:
    name: str
    description: str = ""
    baseline: str | None = None
    parent_name: str | None = None
    template: Path | None = None
    requested_params: dict[str, Any] = field(default_factory=dict)
    resolved_params_by_group: dict[str, dict[str, Any]] = field(default_factory=dict)
    workspace_root: Path = Path()
    executable: Path = Path()
    python: Path = Path()
    mpi_launcher: str = "mpirun"
    mpi_ranks: int = 1
    timeout_s: int = 0
    hours_per_sol: int = 24
    diagnostics_set: str = "core"
    my: int = 1
    sweep_id: str | None = None
    sweep_index: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(asdict(self))


@dataclass(slots=True)
class RunRecord:
    experiment_id: str
    status: Status
    pid: int | None = None
    exit_code: int | None = None
    started_at: str | None = None
    ended_at: str | None = None
    log_path: Path | None = None
    output_files: list[Path] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(asdict(self))


@dataclass(slots=True)
class MetricRecord:
    experiment_id: str
    computed_at: str
    metrics: dict[str, Any] = field(default_factory=dict)
    source_files: list[Path] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(asdict(self))


@dataclass(slots=True)
class DiagnosticSpec:
    name: str
    script: Path
    input_glob: str
    args: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    set_name: str = "core"
    interactive_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(asdict(self))


@dataclass(slots=True)
class ComparisonRecord:
    left_experiment_id: str
    right_experiment_id: str
    parameter_diff: dict[str, Any] = field(default_factory=dict)
    metric_diff: dict[str, Any] = field(default_factory=dict)
    image_pairs: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_primitive(asdict(self))
