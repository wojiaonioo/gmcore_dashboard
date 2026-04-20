"""Plotly-based scientific plotting utilities for the GMCORE Dashboard."""

from __future__ import annotations

import functools
import re
import uuid
from typing import Any

import numpy as np
import plotly.graph_objects as go
from plotly.colors import get_colorscale
from plotly.exceptions import PlotlyError

from .colormaps import ALL_SCALES, get_default_colorscale, is_diverging


PLOT_TEMPLATE = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f8f9fb",
    font=dict(color="#2c3e50", family="Inter, sans-serif", size=12),
    margin=dict(l=60, r=20, t=45, b=50),
    coloraxis=dict(
        colorbar=dict(
            outlinewidth=0,
            tickcolor="#5a6d80",
        )
    ),
)

_GRID_COLOR = "rgba(0, 0, 0, 0.06)"
_AXIS_LINE_COLOR = "#ccd1d9"
_SERIES_COLOR = "#2980b9"
_SCALE_ALIASES = {
    "bwr": "RdBu_r",
    "coolwarm": "RdBu_r",
    "terrain": "Earth",
}
_IGNORE_TITLE_TOKENS = {
    "cross",
    "height",
    "lat",
    "latitude",
    "level",
    "lon",
    "longitude",
    "map",
    "section",
    "time",
}


@functools.lru_cache(maxsize=1)
def _coastline_data() -> tuple[list[float | None], list[float | None]] | None:
    """Load Natural Earth 110m coastline coordinates (cached)."""
    try:
        import cartopy.feature as cfeature
    except ImportError:
        return None

    lons: list[float | None] = []
    lats: list[float | None] = []
    coast = cfeature.NaturalEarthFeature("physical", "coastline", "110m")
    for geom in coast.geometries():
        lines = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
        for line in lines:
            coords = np.array(line.coords)
            lons.extend(coords[:, 0].tolist())
            lats.extend(coords[:, 1].tolist())
            lons.append(np.nan)  # gap between segments
            lats.append(np.nan)
    return lons, lats


def _add_coastlines(fig: go.Figure, lon_max: float = 180.0) -> None:
    """Overlay coastline lines on a Cartesian lon/lat figure."""
    data = _coastline_data()
    if data is None:
        return
    orig_lons, orig_lats = data
    lons = np.array(orig_lons, dtype=float)
    lats = np.array(orig_lats, dtype=float)
    
    # If the data domain spans [0, 360], shift negative coastlines to match
    if lon_max > 180.0:
        lons = np.where(lons < 0, lons + 360.0, lons)
        
        # Insert NaNs where a segment jumps across the wrap point (> 180 degrees)
        diffs = np.zeros_like(lons)
        diffs[1:] = np.abs(lons[1:] - lons[:-1])
        with np.errstate(invalid='ignore'):
            jump_idx = np.where(diffs > 180.0)[0]
            
        if len(jump_idx) > 0:
            lons = np.insert(lons, jump_idx, np.nan)
            lats = np.insert(lats, jump_idx, np.nan)

    fig.add_trace(
        go.Scatter(
            x=lons,
            y=lats,
            mode="lines",
            line=dict(color="rgba(50, 50, 50, 0.45)", width=0.8),
            showlegend=False,
            hoverinfo="skip",
        )
    )


def _add_topography(
    fig: go.Figure,
    topo: tuple[Any, Any, Any] | None,
) -> None:
    """Overlay light iso-contours of idealized surface geopotential / height."""
    if topo is None:
        return
    topo_values, topo_lat, topo_lon = topo
    grid = _prepare_grid(topo_values)
    if grid is None:
        return
    finite = _finite_values(grid)
    if finite.size == 0:
        return
    vmin = float(np.nanmin(finite))
    vmax = float(np.nanmax(finite))
    if not np.isfinite(vmin) or not np.isfinite(vmax) or vmax - vmin < 1e-6:
        # Flat field → nothing meaningful to draw.
        return
    lat_values = _prepare_axis(topo_lat, grid.shape[0])
    lon_values = _prepare_axis(topo_lon, grid.shape[1])
    fig.add_trace(
        go.Contour(
            x=lon_values,
            y=lat_values,
            z=grid,
            showscale=False,
            contours=dict(
                coloring="none",
                showlines=True,
                start=vmin + (vmax - vmin) * 0.1,
                end=vmax,
                size=(vmax - vmin) / 6.0,
            ),
            line=dict(color="rgba(60, 60, 60, 0.55)", width=0.7),
            hoverinfo="skip",
            showlegend=False,
        )
    )


def plot_map_2d(
    data,
    lat,
    lon,
    title: str = "",
    colorscale=None,
    zmin=None,
    zmax=None,
    symmetric: bool = False,
    background: str = "coastline",
    topo: tuple[Any, Any, Any] | None = None,
) -> go.Figure:
    """Create a lat-lon heatmap whose backdrop matches the case setup.

    ``background`` selects the backdrop:

    - ``"coastline"`` — draw Natural Earth coastlines (real-earth cases).
    - ``"topography"`` — overlay iso-contours of ``topo`` (idealized terrain).
    - ``"none"`` — draw no backdrop (pure idealized grid).
    """
    grid = _prepare_grid(data)
    if grid is None:
        return create_empty_figure("No map data available")

    finite = _finite_values(grid)
    if finite.size == 0:
        return create_empty_figure("Map contains only NaN values")

    lat_values = _prepare_axis(lat, grid.shape[0])
    lon_values = _prepare_axis(lon, grid.shape[1])
    scale = _resolve_colorscale(colorscale, title)
    resolved_zmin, resolved_zmax = _resolve_color_limits(
        finite,
        zmin=zmin,
        zmax=zmax,
        symmetric=symmetric,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Heatmap(
            x=lon_values,
            y=lat_values,
            z=grid,
            colorscale=scale,
            zmin=resolved_zmin,
            zmax=resolved_zmax,
            hoverongaps=False,
            colorbar=_colorbar_config(),
            hovertemplate=(
                "Longitude: %{x:.2f}<br>"
                "Latitude: %{y:.2f}<br>"
                "Value: %{z:.3~g}<extra></extra>"
            ),
        )
    )
    lon_min, lon_max = float(lon_values[0]), float(lon_values[-1])
    lat_min, lat_max = float(lat_values[0]), float(lat_values[-1])
    
    if background == "coastline":
        _add_coastlines(fig, lon_max=lon_max)
    elif background == "topography":
        _add_topography(fig, topo)
    _apply_layout(fig, title=title, xlabel="Longitude (°)", ylabel="Latitude (°)")

    # Lock axis range to data extent and maintain physical 1:1 aspect ratio
    fig.update_xaxes(range=[lon_min, lon_max], constrain="domain")
    fig.update_yaxes(range=[lat_min, lat_max], scaleanchor="x", scaleratio=1, constrain="domain")
    return fig


def _add_terrain_strip(
    fig: go.Figure,
    topo: tuple[Any, Any] | None,
    xlabel: str,
) -> bool:
    """Attach a small topography silhouette on a secondary y-axis.

    Returns ``True`` if a strip was added, so the caller can reserve layout
    domain for it.
    """
    if topo is None:
        return False
    values, coord = topo
    try:
        values = np.asarray(values, dtype=float).ravel()
        coord = np.asarray(coord, dtype=float).ravel()
    except Exception:
        return False
    if values.size == 0 or coord.size == 0 or values.size != coord.size:
        return False
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return False
    vmax = float(np.nanmax(finite))
    vmin = float(np.nanmin(finite))
    if vmax - vmin < 1.0:  # flat / noise → no mountain, skip
        return False
    fig.add_trace(
        go.Scatter(
            x=coord,
            y=values,
            mode="lines",
            line=dict(color="rgba(60, 45, 35, 0.9)", width=1.2),
            fill="tozeroy",
            fillcolor="rgba(120, 100, 90, 0.55)",
            name="terrain",
            yaxis="y2",
            xaxis="x",
            hovertemplate=(
                f"{xlabel}: %{{x:.2f}}<br>"
                "Surface: %{y:.1f} m<extra></extra>"
            ),
            showlegend=False,
        )
    )
    return True


def _apply_terrain_layout(fig: go.Figure, invert_y: bool) -> None:
    """Split plot into [main 82%] / [terrain 18%] panels sharing the x-axis."""
    fig.update_layout(
        yaxis=dict(
            domain=[0.18, 1.0],
            autorange="reversed" if invert_y else True,
        ),
        yaxis2=dict(
            domain=[0.0, 0.15],
            anchor="x",
            title=dict(text="topo (m)", standoff=2),
            rangemode="tozero",
            showgrid=False,
            zeroline=True,
            zerolinecolor="#ccd1d9",
            ticks="outside",
        ),
    )


def plot_lat_height(
    data,
    lat,
    lev,
    title: str = "",
    colorscale=None,
    zmin=None,
    zmax=None,
    invert_y: bool = True,
    topo: tuple[Any, Any] | None = None,
) -> go.Figure:
    """Create a latitude-height contour cross section."""
    grid = _prepare_grid(data)
    if grid is None:
        return create_empty_figure("No latitude-height data available")

    finite = _finite_values(grid)
    if finite.size == 0:
        return create_empty_figure("Latitude-height section contains only NaN values")

    lat_values = _prepare_axis(lat, grid.shape[1])
    lev_values = _prepare_axis(lev, grid.shape[0])
    scale = _resolve_colorscale(colorscale, title)
    resolved_zmin, resolved_zmax = _resolve_color_limits(finite, zmin=zmin, zmax=zmax)

    fig = go.Figure()
    fig.add_trace(
        go.Contour(
            x=lat_values,
            y=lev_values,
            z=grid,
            colorscale=scale,
            zmin=resolved_zmin,
            zmax=resolved_zmax,
            connectgaps=False,
            colorbar=_colorbar_config(),
            contours=dict(coloring="heatmap", showlines=False),
            hovertemplate=(
                "Latitude: %{x:.2f}<br>"
                "Level: %{y}<br>"
                "Value: %{z:.3~g}<extra></extra>"
            ),
        )
    )
    _apply_layout(
        fig,
        title=title,
        xlabel="Latitude (°)",
        ylabel="Level",
        invert_y=invert_y,
    )
    if _add_terrain_strip(fig, topo, "Latitude"):
        _apply_terrain_layout(fig, invert_y)
    return fig


def plot_lon_height(
    data,
    lon,
    lev,
    title: str = "",
    colorscale=None,
    zmin=None,
    zmax=None,
    invert_y: bool = True,
    topo: tuple[Any, Any] | None = None,
) -> go.Figure:
    """Create a longitude-height contour cross section."""
    grid = _prepare_grid(data)
    if grid is None:
        return create_empty_figure("No longitude-height data available")

    finite = _finite_values(grid)
    if finite.size == 0:
        return create_empty_figure("Longitude-height section contains only NaN values")

    lon_values = _prepare_axis(lon, grid.shape[1])
    lev_values = _prepare_axis(lev, grid.shape[0])
    scale = _resolve_colorscale(colorscale, title)
    resolved_zmin, resolved_zmax = _resolve_color_limits(finite, zmin=zmin, zmax=zmax)

    fig = go.Figure()
    fig.add_trace(
        go.Contour(
            x=lon_values,
            y=lev_values,
            z=grid,
            colorscale=scale,
            zmin=resolved_zmin,
            zmax=resolved_zmax,
            connectgaps=False,
            colorbar=_colorbar_config(),
            contours=dict(coloring="heatmap", showlines=False),
            hovertemplate=(
                "Longitude: %{x:.2f}<br>"
                "Level: %{y}<br>"
                "Value: %{z:.3~g}<extra></extra>"
            ),
        )
    )
    _apply_layout(
        fig,
        title=title,
        xlabel="Longitude (°)",
        ylabel="Level",
        invert_y=invert_y,
    )
    if _add_terrain_strip(fig, topo, "Longitude"):
        _apply_terrain_layout(fig, invert_y)
    return fig


def plot_time_series(time_vals, data, title: str = "", ylabel: str = "") -> go.Figure:
    """Create a simple line plot for 1D time series data."""
    time_axis, series = _prepare_series(time_vals, data)
    if time_axis is None or series is None:
        return create_empty_figure("No time-series data available")

    finite = _finite_values(series)
    if finite.size == 0:
        return create_empty_figure("Time series contains only NaN values")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time_axis,
            y=series,
            mode="lines",
            line=dict(color=_SERIES_COLOR, width=2),
            connectgaps=False,
            hovertemplate="Time: %{x}<br>Value: %{y:.3~g}<extra></extra>",
        )
    )
    _apply_layout(fig, title=title, xlabel="Time", ylabel=ylabel or "Value")
    return fig


def create_empty_figure(message: str = "Select a variable to plot") -> go.Figure:
    """Return an empty figure with a centered annotation."""
    fig = go.Figure()
    fig.update_layout(
        **PLOT_TEMPLATE,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text=message,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="#7f8c8d"),
            )
        ],
    )
    return fig


def _prepare_grid(data: Any) -> np.ndarray | None:
    if data is None:
        return None

    try:
        array = np.asarray(data, dtype=float)
    except (TypeError, ValueError):
        return None

    if array.size == 0:
        return None

    array = np.squeeze(array)
    if array.ndim == 0:
        return array.reshape(1, 1)
    if array.ndim == 1:
        return array.reshape(1, -1)
    if array.ndim != 2:
        return None
    return array


def _prepare_axis(values: Any, expected_size: int) -> np.ndarray:
    if expected_size <= 0:
        return np.array([], dtype=float)

    if values is None:
        return np.arange(expected_size)

    axis = np.asarray(values)
    if axis.size == 0:
        return np.arange(expected_size)

    axis = np.squeeze(axis)
    if axis.ndim == 0:
        return np.full(expected_size, axis.item())

    axis = axis.reshape(-1)
    if axis.size == expected_size:
        return axis

    return np.arange(expected_size)


def _prepare_series(time_vals: Any, data: Any) -> tuple[np.ndarray | None, np.ndarray | None]:
    if data is None:
        return None, None

    try:
        series = np.asarray(data, dtype=float)
    except (TypeError, ValueError):
        return None, None

    if series.size == 0:
        return None, None

    series = np.squeeze(series)
    if series.ndim == 0:
        series = series.reshape(1)
    else:
        series = series.reshape(-1)

    if time_vals is None:
        return np.arange(series.size), series

    time_axis = np.asarray(time_vals)
    if time_axis.size == 0:
        return np.arange(series.size), series

    time_axis = np.squeeze(time_axis)
    if time_axis.ndim == 0:
        time_axis = np.full(series.size, time_axis.item())
    else:
        time_axis = time_axis.reshape(-1)

    if time_axis.size == series.size:
        return time_axis, series

    limit = min(time_axis.size, series.size)
    if limit == 0:
        return None, None

    return time_axis[:limit], series[:limit]


def _finite_values(array: np.ndarray) -> np.ndarray:
    finite = np.asarray(array, dtype=float)
    return finite[np.isfinite(finite)]


def _resolve_color_limits(
    finite: np.ndarray,
    zmin=None,
    zmax=None,
    symmetric: bool = False,
) -> tuple[float | None, float | None]:
    if finite.size == 0:
        return None, None

    auto_min, auto_max = _robust_bounds(finite)

    resolved_zmin = auto_min if zmin is None else float(zmin)
    resolved_zmax = auto_max if zmax is None else float(zmax)

    if symmetric:
        bound = max(abs(resolved_zmin), abs(resolved_zmax))
        if bound == 0.0:
            bound = 1.0
        return -bound, bound

    if resolved_zmin == resolved_zmax:
        padding = 1.0 if resolved_zmin == 0.0 else abs(resolved_zmin) * 0.05
        resolved_zmin -= padding
        resolved_zmax += padding

    if resolved_zmin > resolved_zmax:
        resolved_zmin, resolved_zmax = resolved_zmax, resolved_zmin

    return resolved_zmin, resolved_zmax


def _robust_bounds(finite: np.ndarray) -> tuple[float, float]:
    if finite.size < 3:
        lower = float(np.min(finite))
        upper = float(np.max(finite))
    else:
        lower, upper = np.nanpercentile(finite, [2, 98])
        lower = float(lower)
        upper = float(upper)

    if lower == upper:
        lower = float(np.min(finite))
        upper = float(np.max(finite))

    return lower, upper


def _resolve_colorscale(colorscale: Any, title: str) -> Any:
    if colorscale is not None:
        return _normalize_colorscale(colorscale)

    var_name = _infer_var_name(title)
    if not var_name:
        return "Viridis"

    default_scale = get_default_colorscale(var_name)
    if default_scale not in ALL_SCALES and not _is_valid_colorscale(default_scale):
        default_scale = "RdBu_r" if is_diverging(var_name) else "Viridis"

    return _normalize_colorscale(default_scale)


def _normalize_colorscale(colorscale: Any) -> Any:
    if not isinstance(colorscale, str):
        return colorscale

    canonical = _match_registered_scale(colorscale)
    if canonical is None:
        canonical = colorscale

    canonical = _SCALE_ALIASES.get(canonical, canonical)
    if _is_valid_colorscale(canonical):
        return canonical

    return "Viridis"


def _match_registered_scale(colorscale: str) -> str | None:
    lowered = colorscale.lower()
    for scale_name in ALL_SCALES:
        if scale_name.lower() == lowered:
            return scale_name
    return None


def _is_valid_colorscale(colorscale: str) -> bool:
    try:
        get_colorscale(colorscale)
    except (PlotlyError, TypeError, ValueError):
        return False
    return True


def _infer_var_name(title: str) -> str:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", title.lower())
    if not tokens:
        return ""

    for token in tokens:
        if token in _IGNORE_TITLE_TOKENS:
            continue
        return token

    return tokens[0]


def _colorbar_config() -> dict[str, Any]:
    return dict(
        len=0.88,
        thickness=16,
        tickformat=".3~g",
        outlinewidth=0,
        tickcolor="#5a6d80",
        tickfont=dict(color="#5a6d80"),
        title=dict(text=""),
    )


def _apply_layout(
    fig: go.Figure,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    invert_y: bool = False,
) -> None:
    fig.update_layout(
        **PLOT_TEMPLATE,
        uirevision="constant",
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=13)),
        xaxis=dict(
            title=xlabel,
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            linecolor=_AXIS_LINE_COLOR,
            ticks="outside",
            tickcolor="#b0b8c0",
        ),
        yaxis=dict(
            title=ylabel,
            showgrid=True,
            gridcolor=_GRID_COLOR,
            zeroline=False,
            linecolor=_AXIS_LINE_COLOR,
            ticks="outside",
            tickcolor="#b0b8c0",
            autorange="reversed" if invert_y else True,
        ),
    )


__all__ = [
    "PLOT_TEMPLATE",
    "create_empty_figure",
    "plot_lat_height",
    "plot_lon_height",
    "plot_map_2d",
    "plot_time_series",
]
