from __future__ import annotations

"""Scientific colormap definitions for GMCORE Dashboard."""

# Plotly built-in colorscales that work well for atmospheric data
SEQUENTIAL_SCALES = [
    "Viridis",
    "Plasma",
    "Inferno",
    "Magma",
    "Cividis",
    "Blues",
    "YlOrRd",
    "YlGnBu",
    "Turbo",
    "Hot",
]

DIVERGING_SCALES = [
    "RdBu_r",
    "RdYlBu_r",
    "BrBG",
    "PiYG",
    "PRGn",
    "Spectral",
    "coolwarm",
    "bwr",
]

# Variable-specific default colorscales
VAR_DEFAULTS = {
    # Wind components
    "u": "RdBu_r",
    "v": "RdBu_r",
    "w": "RdBu_r",
    "w_lev": "RdBu_r",
    # Thermodynamic
    "t": "Turbo",
    "pt": "Turbo",
    "temperature": "Turbo",
    # Pressure
    "ph": "YlOrRd",
    "phs": "YlOrRd",
    # Geopotential
    "gz": "Viridis",
    "gz_lev": "Viridis",
    "gzs": "terrain",
    # Vorticity
    "pv": "RdBu_r",
    "vor": "RdBu_r",
    # Tracers
    "q1": "YlGnBu",
    "q2": "YlGnBu",
    "q3": "YlGnBu",
    "q4": "YlGnBu",
    "qr": "Blues",
    # Energy
    "te": "Plasma",
    "tpe": "Plasma",
}

ALL_SCALES = SEQUENTIAL_SCALES + DIVERGING_SCALES


def get_default_colorscale(var_name: str) -> str:
    """Get the default colorscale for a variable name."""
    # Exact match
    if var_name in VAR_DEFAULTS:
        return VAR_DEFAULTS[var_name]
    # Prefix match
    for prefix in ("q", "bg_", "adv_"):
        if var_name.startswith(prefix):
            return "YlGnBu"
    # Default
    return "Viridis"


def is_diverging(var_name: str) -> bool:
    """Check if a variable typically needs a diverging colorscale."""
    diverging_patterns = ["pv", "vor", "w", "du", "dpt", "diff", "anom"]
    name_lower = var_name.lower()
    for pat in diverging_patterns:
        if pat in name_lower:
            return True
    if var_name in ("u", "v"):
        return True
    return False
