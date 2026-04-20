from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from gmcore_dashboard.config import get_namelist_sources


_GROUP_RE = re.compile(r"namelist\s*/\s*([A-Za-z_][A-Za-z0-9_]*)\s*/", re.IGNORECASE)
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_KNOWN_GROUPS = {"gmcore_control", "gomars_v1_control"}
_BLOCK_END_RE = re.compile(r"^(contains|end\b|module\b|subroutine\b|function\b)", re.IGNORECASE)


def _default_sources() -> dict[str, Path]:
    return get_namelist_sources()


def _extract_groups(source: Path) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    lines = source.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        match = _GROUP_RE.search(lines[index])
        if not match:
            index += 1
            continue
        group = match.group(1)
        params: list[str] = []
        index += 1
        while index < len(lines):
            line = lines[index].split("!")[0].strip()
            if not line:
                index += 1
                continue
            if _BLOCK_END_RE.match(line):
                break
            cleaned = line.replace("&", " ")
            for part in cleaned.split(","):
                token = part.strip()
                if token and _IDENT_RE.match(token):
                    params.append(token)
            index += 1
        groups[group] = params
    return groups


@lru_cache(maxsize=1)
def _catalog_state() -> tuple[dict[str, str], dict[str, list[str]]]:
    sources = _default_sources()
    catalog: dict[str, str] = {}
    collisions: dict[str, set[str]] = {}
    for source in sources.values():
        for group, params in _extract_groups(source).items():
            for param in params:
                existing = catalog.get(param)
                if existing is None:
                    catalog[param] = group
                    continue
                if existing != group:
                    collisions.setdefault(param, {existing}).add(group)
    return catalog, {key: sorted(value) for key, value in collisions.items()}


def load_param_catalog() -> dict[str, str]:
    return dict(_catalog_state()[0])


def detect_collisions() -> dict[str, list[str]]:
    return dict(_catalog_state()[1])


def route_param(name: str) -> str:
    if "." in name:
        group, _param = name.split(".", 1)
        if group not in _KNOWN_GROUPS:
            raise KeyError(f"Unknown namelist group: {group}")
        return group
    catalog, collisions = _catalog_state()
    if name in collisions:
        groups = ", ".join(collisions[name])
        raise ValueError(f"Parameter {name!r} is ambiguous across groups: {groups}")
    if name not in catalog:
        raise KeyError(f"Unknown namelist parameter: {name}")
    return catalog[name]
