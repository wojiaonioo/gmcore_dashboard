from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import f90nml

from .param_catalog import route_param


def read_template(path: str | Path) -> f90nml.Namelist:
    return f90nml.read(str(Path(path)))


def apply_overrides(
    namelist: f90nml.Namelist,
    overrides: dict[str, Any],
    *,
    case_name: str | None = None,
) -> f90nml.Namelist:
    updated = copy.deepcopy(namelist)
    merged = dict(overrides)
    if case_name is not None:
        merged["case_name"] = case_name
    for key, value in merged.items():
        group = route_param(key)
        param = key.split(".", 1)[-1]
        section = updated.setdefault(group, f90nml.Namelist())
        section[param] = value
    return updated


def write_namelist(namelist: f90nml.Namelist, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    namelist.write(str(output_path), force=True)
    return output_path
