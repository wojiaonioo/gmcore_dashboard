"""Centralized path configuration for the GMCORE Dashboard package.

All modules that need GMCORE_ROOT, TESTBED_ROOT, etc. should import from here
rather than computing paths from __file__. This decouples the package layout
from the GMCORE source tree so it can live as an external submodule.
"""

from __future__ import annotations

import os
from pathlib import Path


def _discover_gmcore_root() -> Path:
    """Discover GMCORE_ROOT from environment or parent layout.

    Resolution order:
      1. GMCORE_ROOT environment variable (explicit override)
      2. Walk up from this file looking for CMakeLists.txt with 'gmcore' marker
    """
    env_root = os.environ.get("GMCORE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    current = Path(__file__).resolve().parent
    for _ in range(5):
        current = current.parent
        cmake = current / "CMakeLists.txt"
        if cmake.is_file() and "gmcore" in cmake.read_text(errors="ignore").lower():
            return current

    raise RuntimeError(
        "Cannot determine GMCORE_ROOT. "
        "Set the GMCORE_ROOT environment variable or run from within the GMCORE tree."
    )


_gmcore_root: Path | None = None


def get_gmcore_root() -> Path:
    global _gmcore_root
    if _gmcore_root is None:
        _gmcore_root = _discover_gmcore_root()
    return _gmcore_root


def set_gmcore_root(path: str | Path) -> None:
    global _gmcore_root
    _gmcore_root = Path(path).expanduser().resolve()


def get_testbed_root() -> Path:
    return get_gmcore_root() / "run" / "GMCORE-TESTBED"


def get_experiments_root() -> Path:
    return get_gmcore_root() / "tools" / "gmcore_dashboard" / "experiments" / "experiments"


def get_namelist_sources() -> dict[str, Path]:
    root = get_gmcore_root()
    return {
        "gmcore": root / "src" / "utils" / "namelist_mod.F90",
        "gomars": root / "src" / "physics" / "gomars_v1" / "gomars_v1_namelist_mod.F90",
    }
