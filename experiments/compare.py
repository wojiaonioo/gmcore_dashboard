from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import ComparisonRecord
from .store import Store


def _collect_pngs(metadata: dict[str, Any]) -> dict[str, str]:
    pngs: dict[str, str] = {}
    diagnostics = metadata.get("diagnostics") or {}
    for manifest in diagnostics.values():
        for path in manifest.get("artifacts", []):
            candidate = Path(path)
            pngs[candidate.stem] = candidate.resolve().as_posix()
    if pngs:
        return pngs
    root = Path(metadata["paths"]["diagnostics_dir"])
    if root.is_dir():
        for path in root.rglob("*.png"):
            pngs[path.stem] = path.resolve().as_posix()
    return pngs


def _diff_mapping(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key in sorted(set(left) | set(right)):
        left_value = left.get(key)
        right_value = right.get(key)
        if left_value != right_value:
            payload[key] = {"left": left_value, "right": right_value}
    return payload


def compare_experiments(a_id: str, b_id: str, *, store: Store | None = None) -> dict[str, Any]:
    store = store or Store()
    left_metadata = store.load_metadata(a_id)
    right_metadata = store.load_metadata(b_id)
    left_metrics = store.load_metrics(a_id) or {}
    right_metrics = store.load_metrics(b_id) or {}
    left_pngs = _collect_pngs(left_metadata)
    right_pngs = _collect_pngs(right_metadata)
    image_pairs = []
    for stem in sorted(set(left_pngs) | set(right_pngs)):
        image_pairs.append(
            {
                "stem": stem,
                "left": left_pngs.get(stem),
                "right": right_pngs.get(stem),
            }
        )
    record = ComparisonRecord(
        left_experiment_id=a_id,
        right_experiment_id=b_id,
        parameter_diff=_diff_mapping(
            dict(left_metadata.get("requested_params") or {}),
            dict(right_metadata.get("requested_params") or {}),
        ),
        metric_diff=_diff_mapping(
            dict(left_metrics.get("metrics") or {}),
            dict(right_metrics.get("metrics") or {}),
        ),
        image_pairs=image_pairs,
    )
    return {
        "left": {
            "experiment_id": a_id,
            "name": left_metadata.get("name"),
            "status": left_metadata.get("status"),
        },
        "right": {
            "experiment_id": b_id,
            "name": right_metadata.get("name"),
            "status": right_metadata.get("status"),
        },
        **record.to_dict(),
    }
