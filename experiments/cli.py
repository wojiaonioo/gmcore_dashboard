from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .compare import compare_experiments
from .diagnostics import run_diagnostic, run_diagnostic_set
from .metrics import extract_metrics
from .models import Status
from .namelist_io import apply_overrides, read_template, write_namelist
from .registry import default_registry_path, load_registry, resolve_experiment
from .runner import recover_running_experiments, run_experiment
from .store import Store, utcnow
from .sweep import expand_factorial, stable_child_name


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    return str(value)


def _materialize_experiment(
    resolved,
    *,
    experiment_id: str,
    store: Store,
) -> str:
    if resolved.template is None:
        raise ValueError(f"Experiment {resolved.name!r} has no template")
    experiment_dir = store.root / experiment_id
    experiment_dir.mkdir(parents=True, exist_ok=False)
    namelist_path = experiment_dir / "namelist"
    log_path = experiment_dir / "logs" / "run.log"
    diagnostics_dir = experiment_dir / "artifacts" / "diagnostics"
    metrics_path = experiment_dir / "metrics.json"

    namelist = read_template(resolved.template)
    namelist = apply_overrides(namelist, resolved.requested_params, case_name=experiment_id)
    write_namelist(namelist, namelist_path)

    created_at = utcnow()
    parent_experiment_id = None
    if resolved.parent_name:
        matches = store.list_experiments(name=resolved.parent_name)
        if matches:
            parent_experiment_id = matches[0]["experiment_id"]
    metadata = {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "name": resolved.name,
        "baseline": resolved.baseline,
        "parent_experiment_id": parent_experiment_id,
        "sweep_id": resolved.sweep_id,
        "sweep_index": resolved.sweep_index,
        "description": resolved.description,
        "status": Status.CREATED.value,
        "created_at": created_at,
        "updated_at": created_at,
        "requested_params": resolved.requested_params,
        "resolved_params_by_group": {
            "gmcore_control": dict(namelist.get("gmcore_control", {})),
            "gomars_v1_control": dict(namelist.get("gomars_v1_control", {})),
        },
        "paths": {
            "experiment_dir": experiment_dir.as_posix(),
            "namelist": namelist_path.as_posix(),
            "run_log": log_path.as_posix(),
            "diagnostics_dir": diagnostics_dir.as_posix(),
            "metrics_json": metrics_path.as_posix(),
        },
        "run_config": {
            "mpi_ranks": resolved.mpi_ranks,
            "timeout_s": resolved.timeout_s,
            "executable": resolved.executable.as_posix(),
            "launcher": resolved.mpi_launcher,
            "python": resolved.python.as_posix(),
        },
        "derived": {
            "case_name": experiment_id,
            "expected_output_globs": [
                f"{experiment_id}.h0*.nc",
                f"{experiment_id}.h1*.nc",
                f"{experiment_id}.h2*.nc",
            ],
        },
        "my": resolved.my,
        "hours_per_sol": resolved.hours_per_sol,
        "outputs": [],
        "exit_code": None,
        "pid": None,
        "diagnostics": {},
    }
    store.insert_experiment(metadata)
    return experiment_id


def _create_command(args: argparse.Namespace) -> int:
    resolved = resolve_experiment(args.name, args.registry)
    store = Store(resolved.workspace_root)
    experiment_id = stable_child_name(resolved.name, 0, resolved.requested_params)
    _materialize_experiment(resolved, experiment_id=experiment_id, store=store)
    print(experiment_id)
    return 0


def _run_command(args: argparse.Namespace) -> int:
    store = Store(args.workspace)
    recover_running_experiments(store)
    record = run_experiment(args.experiment_id, store=store)
    print(json.dumps(record.to_dict(), indent=2, default=_json_default))
    return 0 if record.exit_code == 0 else 1


def _sweep_command(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    node = registry["experiments"].get(args.name)
    if not node:
        raise KeyError(f"Unknown experiment: {args.name}")
    sweep = node.get("sweep") or {}
    axes = sweep.get("axes") or {}
    if not axes:
        raise ValueError(f"Experiment {args.name!r} does not declare a sweep")
    parent = resolve_experiment(args.name, args.registry)
    store = Store(parent.workspace_root)
    created_ids = []
    for child in expand_factorial(parent, axes):
        experiment_id = stable_child_name(parent.name, child.sweep_index or 0, {
            key: child.requested_params[key] for key in sorted(axes)
        })
        created_ids.append(_materialize_experiment(child, experiment_id=experiment_id, store=store))
        if args.run:
            run_experiment(experiment_id, store=store)
    print(json.dumps(created_ids, indent=2))
    return 0


def _diag_command(args: argparse.Namespace) -> int:
    store = Store(args.workspace)
    if args.name:
        payload = run_diagnostic(args.experiment_id, args.name, store=store)
    else:
        payload = run_diagnostic_set(args.experiment_id, args.set_name, store=store)
    print(json.dumps(payload, indent=2, default=_json_default))
    return 0


def _metrics_command(args: argparse.Namespace) -> int:
    store = Store(args.workspace)
    record = extract_metrics(args.experiment_id, store=store)
    print(json.dumps(record.to_dict(), indent=2, default=_json_default))
    return 0


def _compare_command(args: argparse.Namespace) -> int:
    store = Store(args.workspace)
    payload = compare_experiments(args.left, args.right, store=store)
    print(json.dumps(payload, indent=2, default=_json_default))
    return 0


def _list_command(args: argparse.Namespace) -> int:
    store = Store(args.workspace)
    rows = store.list_experiments(status=args.status, sweep_id=args.sweep_id)
    print(json.dumps(rows, indent=2))
    return 0


def _status_command(args: argparse.Namespace) -> int:
    store = Store(args.workspace)
    metadata = store.load_metadata(args.experiment_id)
    print(json.dumps(metadata, indent=2, default=_json_default))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.experiments.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create one experiment from registry")
    create_parser.add_argument("name")
    create_parser.add_argument(
        "--registry",
        type=Path,
        default=default_registry_path(),
    )
    create_parser.set_defaults(func=_create_command)

    run_parser = subparsers.add_parser("run", help="Run one materialized experiment")
    run_parser.add_argument("experiment_id")
    run_parser.add_argument("--workspace", type=Path, default=None)
    run_parser.set_defaults(func=_run_command)

    sweep_parser = subparsers.add_parser("sweep", help="Expand a factorial sweep")
    sweep_parser.add_argument("name")
    sweep_parser.add_argument(
        "--registry",
        type=Path,
        default=default_registry_path(),
    )
    sweep_parser.add_argument("--run", action="store_true")
    sweep_parser.set_defaults(func=_sweep_command)

    diag_parser = subparsers.add_parser("diag", help="Run diagnostics for an experiment")
    diag_parser.add_argument("experiment_id")
    diag_parser.add_argument("--workspace", type=Path, default=None)
    diag_group = diag_parser.add_mutually_exclusive_group(required=False)
    diag_group.add_argument("--name")
    diag_group.add_argument("--set-name", default="core")
    diag_parser.set_defaults(func=_diag_command)

    metrics_parser = subparsers.add_parser("metrics", help="Extract scalar metrics")
    metrics_parser.add_argument("experiment_id")
    metrics_parser.add_argument("--workspace", type=Path, default=None)
    metrics_parser.set_defaults(func=_metrics_command)

    compare_parser = subparsers.add_parser("compare", help="Compare two experiments")
    compare_parser.add_argument("left")
    compare_parser.add_argument("right")
    compare_parser.add_argument("--workspace", type=Path, default=None)
    compare_parser.set_defaults(func=_compare_command)

    list_parser = subparsers.add_parser("list", help="List experiments in the store")
    list_parser.add_argument("--workspace", type=Path, default=None)
    list_parser.add_argument("--status")
    list_parser.add_argument("--sweep-id")
    list_parser.set_defaults(func=_list_command)

    status_parser = subparsers.add_parser("status", help="Show experiment metadata")
    status_parser.add_argument("experiment_id")
    status_parser.add_argument("--workspace", type=Path, default=None)
    status_parser.set_defaults(func=_status_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
