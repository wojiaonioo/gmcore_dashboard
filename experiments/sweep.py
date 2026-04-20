from __future__ import annotations

import hashlib
import json
import re
from dataclasses import replace
from itertools import product
from typing import Any, Iterable

from .models import ResolvedExperiment


_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def sanitize_experiment_name(name: str) -> str:
    """Turn an arbitrary label into a filesystem-safe slug.

    Strips path separators and other unsafe characters so registry-authored
    names cannot escape the experiments workspace.
    """
    if not isinstance(name, str):
        raise TypeError("Experiment name must be a string")
    slug = _SAFE_NAME_RE.sub("_", name).strip("._")
    if not slug:
        raise ValueError(f"Experiment name {name!r} has no path-safe characters")
    return slug


def stable_child_name(parent_name: str, index: int, overrides: dict[str, Any]) -> str:
    parent_slug = sanitize_experiment_name(parent_name)
    digest = hashlib.sha1(
        json.dumps(overrides, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8]
    return f"{parent_slug}__idx_{index:03d}__{digest}"


def expand_factorial(
    parent: ResolvedExperiment,
    axes: dict[str, Iterable[Any]],
) -> list[ResolvedExperiment]:
    keys = sorted(axes)
    values = [list(axes[key]) for key in keys]
    children: list[ResolvedExperiment] = []
    for index, combo in enumerate(product(*values), start=1):
        overrides = dict(zip(keys, combo))
        child_name = stable_child_name(parent.name, index, overrides)
        child = replace(
            parent,
            name=child_name,
            requested_params={**parent.requested_params, **overrides},
            resolved_params_by_group={},
            sweep_id=parent.sweep_id or parent.name,
            sweep_index=index,
        )
        children.append(child)
    return children
