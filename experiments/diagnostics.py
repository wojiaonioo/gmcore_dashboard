from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from gmcore_dashboard.config import get_gmcore_root
from .models import DiagnosticSpec
from .store import Store, utcnow


def default_diagnostics_path() -> Path:
    return Path(__file__).with_name("diagnostics.yaml")


def load_diagnostics(path: str | Path | None = None) -> dict[str, Any]:
    diagnostics_path = Path(path) if path is not None else default_diagnostics_path()
    with diagnostics_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    data.setdefault("sets", {})
    data.setdefault("diagnostics", {})
    data.setdefault("interactive_only", [])
    return data


def _spec_map(path: str | Path | None = None) -> dict[str, DiagnosticSpec]:
    raw = load_diagnostics(path)
    specs: dict[str, DiagnosticSpec] = {}
    for set_name, names in raw["sets"].items():
        for name in names:
            entry = raw["diagnostics"][name]
            specs[name] = DiagnosticSpec(
                name=name,
                script=(get_gmcore_root() / entry["script"]).resolve(),
                input_glob=str(entry["input_glob"]),
                args=[str(item) for item in entry.get("args", [])],
                outputs=[str(item) for item in entry.get("outputs", [])],
                set_name=str(set_name),
            )
    return specs


def _render_args(args: list[str], metadata: dict[str, Any]) -> list[str]:
    context = {
        "case_name": metadata["derived"]["case_name"],
        "hours_per_sol": metadata.get("hours_per_sol", metadata["run_config"].get("hours_per_sol", 24)),
        "my": metadata.get("my", 1),
    }
    return [arg.format(**context) for arg in args]


def _resolve_input_file(spec: DiagnosticSpec, metadata: dict[str, Any]) -> Path:
    experiment_dir = Path(metadata["paths"]["experiment_dir"])
    pattern = spec.input_glob.format(case_name=metadata["derived"]["case_name"])
    candidates = sorted(experiment_dir.glob(pattern))
    if not candidates:
        raise FileNotFoundError(f"No diagnostic input matched pattern {pattern!r}")
    return candidates[0].resolve()


def _write_manifest(diag_dir: Path, payload: dict[str, Any]) -> None:
    path = diag_dir / "manifest.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_diagnostic(
    exp_id: str,
    name: str,
    *,
    store: Store | None = None,
    timeout_s: int = 300,
) -> dict[str, Any]:
    store = store or Store()
    metadata = store.load_metadata(exp_id)
    specs = _spec_map()
    if name not in specs:
        raise KeyError(f"Unknown diagnostic: {name}")
    spec = specs[name]
    input_file = _resolve_input_file(spec, metadata)
    diag_dir = Path(metadata["paths"]["diagnostics_dir"]) / spec.name
    diag_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(metadata["run_config"]["python"]),
        str(spec.script),
        "-i",
        str(input_file),
        *_render_args(spec.args, metadata),
    ]
    subprocess.run(
        command,
        cwd=diag_dir,
        check=True,
        timeout=timeout_s,
        text=True,
    )
    pngs = [str((diag_dir / name).resolve()) for name in spec.outputs if (diag_dir / name).is_file()]
    manifest = {
        "name": spec.name,
        "generated_at": utcnow(),
        "input_file": str(input_file),
        "artifacts": pngs,
    }
    _write_manifest(diag_dir, manifest)
    diagnostics = dict(metadata.get("diagnostics") or {})
    diagnostics[spec.name] = manifest
    store.touch(exp_id, diagnostics=diagnostics)
    return manifest


def run_diagnostic_set(
    exp_id: str,
    set_name: str = "core",
    *,
    store: Store | None = None,
    timeout_s: int = 300,
) -> list[dict[str, Any]]:
    store = store or Store()
    raw = load_diagnostics()
    names = list(raw["sets"].get(set_name, []))
    if not names:
        raise KeyError(f"Unknown diagnostic set: {set_name}")
    manifests = []
    for name in names:
        manifests.append(run_diagnostic(exp_id, name, store=store, timeout_s=timeout_s))
    return manifests
