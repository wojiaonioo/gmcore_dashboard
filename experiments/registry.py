from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from gmcore_dashboard.config import get_gmcore_root
from .models import ResolvedExperiment


def default_registry_path() -> Path:
    return Path(__file__).resolve().with_name("registry.yaml")


def _discover_python() -> str:
    """Find the Python interpreter, preferring conda gmcore env."""
    import shutil
    import sys

    for base in ("~/anaconda3", "~/miniconda3", "~/miniforge3", "~/mambaforge"):
        candidate = Path(base).expanduser() / "envs" / "gmcore" / "bin" / "python"
        if candidate.is_file():
            return str(candidate)
    found = shutil.which("python3") or shutil.which("python")
    return found or sys.executable


def _resolve_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return (get_gmcore_root() / path).resolve()


def load_registry(path: str | Path | None = None) -> dict[str, Any]:
    registry_path = Path(path) if path is not None else default_registry_path()
    with registry_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    data.setdefault("defaults", {})
    data.setdefault("baselines", {})
    data.setdefault("experiments", {})
    return data


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _resolve_node(
    name: str,
    registry: dict[str, Any],
    stack: set[str] | None = None,
) -> dict[str, Any]:
    stack = set() if stack is None else set(stack)
    if name in stack:
        raise ValueError(f"Cyclic experiment inheritance detected at {name!r}")
    stack.add(name)
    experiments = registry.get("experiments", {})
    baselines = registry.get("baselines", {})
    defaults = registry.get("defaults", {})
    if name not in experiments:
        raise KeyError(f"Unknown experiment: {name}")
    node = deepcopy(experiments[name])
    parent_name = node.get("parent")
    baseline_name = node.get("baseline")
    if parent_name:
        base = _resolve_node(parent_name, registry, stack)
    else:
        base = deepcopy(defaults)
        if baseline_name:
            if baseline_name not in baselines:
                raise KeyError(f"Unknown baseline: {baseline_name}")
            base = deep_merge(base, baselines[baseline_name])
    node.pop("parent", None)
    return deep_merge(base, node)


def resolve_experiment(name: str, path: str | Path | None = None) -> ResolvedExperiment:
    registry = load_registry(path)
    experiments = registry.get("experiments", {})
    parent_name = experiments.get(name, {}).get("parent") if isinstance(experiments, dict) else None
    merged = _resolve_node(name, registry)
    params = dict(merged.get("params") or {})
    defaults = registry.get("defaults", {})
    workspace_root = _resolve_path(merged.get("workspace_root", defaults.get("workspace_root", "tools/gmcore_dashboard/experiments/experiments")))
    executable = _resolve_path(merged.get("executable", defaults.get("executable")))
    python_default = defaults.get("python") or _discover_python()
    python = _resolve_path(merged.get("python", python_default))
    template = _resolve_path(merged.get("template"))
    return ResolvedExperiment(
        name=name,
        description=str(merged.get("description", "")),
        baseline=merged.get("baseline"),
        parent_name=parent_name,
        template=template,
        requested_params=params,
        workspace_root=workspace_root if workspace_root is not None else Path(),
        executable=executable if executable is not None else Path(),
        python=python if python is not None else Path(_discover_python()),
        mpi_launcher=str(merged.get("mpi_launcher", defaults.get("mpi_launcher", "mpirun"))),
        mpi_ranks=int(merged.get("mpi_ranks", defaults.get("mpi_ranks", 1))),
        timeout_s=int(merged.get("timeout_s", defaults.get("timeout_s", 0))),
        hours_per_sol=int(merged.get("hours_per_sol", defaults.get("hours_per_sol", 24))),
        diagnostics_set=str(merged.get("diagnostics_set", defaults.get("diagnostics_set", "core"))),
        my=int(merged.get("my", defaults.get("my", 1))),
    )
