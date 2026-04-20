"""Visualization tab layout and callbacks for the GMCORE Dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import markdown as _md_lib

import dash_bootstrap_components as dbc
import numpy as np
from dash import ALL, Input, Output, State, callback, callback_context, dcc, html, no_update
from dash.exceptions import PreventUpdate

from gmcore_dashboard.dashboard.colormaps import ALL_SCALES, get_default_colorscale
from gmcore_dashboard.dashboard.inspector import (
    get_smart_colormap,
    inspect_nc,
    load_slice_axis,
    load_terrain_field,
    load_terrain_slice,
    load_variable_slice,
)
from gmcore_dashboard.dashboard.plots import (
    create_empty_figure,
    plot_lat_height,
    plot_lon_height,
    plot_map_2d,
    plot_time_series,
)
from gmcore_dashboard.dashboard.scanner import scan_testbed
from gmcore_dashboard.dashboard.case_meta import (
    CASE_DEFAULT_ANALYSES,
    CASE_DISPLAY_NAMES,
    get_map_background,
)


THEME = dbc.themes.FLATLY
CARD_CLASS = "border"
LEVEL_DIMS = {"lev", "ilev"}
PLOTTABLE_TYPES = {
    "lat_height",
    "lon_height",
    "map_2d",
    "map_2d_with_level",
    "static_map",
    "time_series",
}


def create_layout(testbed_root: str = "") -> dbc.Container:
    """Create the main visualization tab layout."""
    resolved_root = _resolve_testbed_root(testbed_root)
    testbed_data = scan_testbed(resolved_root)

    return dbc.Container(
        fluid=True,
        className="py-2 px-3",
        children=[
            dcc.Store(id="viz-testbed-data", data=testbed_data),
            dcc.Store(id="viz-nc-meta"),
            dcc.Store(id="viz-current-case-dir"),
            dcc.Interval(id="viz-interval", interval=1000, n_intervals=0, disabled=True),
            dcc.Store(id="viz-analysis-store", data={}, storage_type="local"),
            # ── Fullscreen overlay ──
            _build_fullscreen_overlay(),
            dbc.Row(
                className="g-2",
                children=[
                    dbc.Col(
                        _build_sidebar(testbed_data, resolved_root),
                        width=2,
                        className="pe-1",
                    ),
                    dbc.Col(_build_main_panel(), width=10),
                ],
            ),
        ],
    )


def _build_sidebar(testbed_data: dict[str, list[dict[str, Any]]], testbed_root: str) -> dbc.Card:
    return dbc.Card(
        className=f"{CARD_CLASS} viz-sidebar",
        children=[
            dbc.CardHeader(
                html.Span("Cases", className="small fw-bold"),
                className="py-2 px-2",
            ),
            dbc.CardBody(
                [
                    html.Div(
                        Path(testbed_root).name,
                        className="text-muted mb-2",
                        style={"fontSize": "0.7rem", "opacity": "0.6"},
                    ),
                    _build_case_tree(testbed_data),
                ],
                className="py-1 px-2",
                style={"maxHeight": "calc(100vh - 160px)", "overflowY": "auto"},
            ),
        ],
    )


def _build_main_panel() -> html.Div:
    return html.Div(
        [
            # ── Compact Controls Toolbar ──
            html.Div(
                className="viz-toolbar glass-panel mb-2 p-3",
                children=[
                    # ── Data and View Configuration ──
                    dbc.Row(
                        className="g-3 align-items-end mb-3 form-row",
                        children=[
                            dbc.Col(
                                [
                                    html.Label("File", className="viz-ctrl-label"),
                                    dcc.Dropdown(
                                        id="viz-file-dropdown",
                                        options=[],
                                        value=None,
                                        placeholder="Select case…",
                                        clearable=False,
                                        className="viz-dropdown",
                                    ),
                                ],
                                lg=4, md=6,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Variable", className="viz-ctrl-label"),
                                    dcc.Dropdown(
                                        id="viz-var-dropdown",
                                        options=[],
                                        value=None,
                                        placeholder="Select variable…",
                                        clearable=False,
                                        className="viz-dropdown",
                                    ),
                                ],
                                lg=4, md=6,
                            ),
                            dbc.Col(
                                html.Div(
                                    id="viz-view-container",
                                    style={"display": "none"},
                                    children=[
                                        html.Label("View", className="viz-ctrl-label"),
                                        dbc.Select(
                                            id="viz-view-mode",
                                            options=[
                                                {"label": "水平", "value": "horizontal"},
                                                {"label": "x 剖面", "value": "zonal"},
                                                {"label": "y 剖面", "value": "meridional"},
                                            ],
                                            value="horizontal",
                                            className="viz-select",
                                        ),
                                    ],
                                ),
                                lg=2, md=4,
                            ),
                            dbc.Col(
                                html.Div(
                                    id="viz-level-container",
                                    className="px-2",
                                    style={"display": "none"},
                                    children=[
                                        html.Label("Level", id="viz-level-label", className="viz-ctrl-label"),
                                        html.Div(
                                            className="pt-1",
                                            children=[
                                                dcc.Slider(
                                                    id="viz-level-slider",
                                                    min=0, max=0, step=1, value=0, marks={0: "0"},
                                                    tooltip={"placement": "bottom", "always_visible": False},
                                                    className="viz-slider",
                                                )
                                            ]
                                        )
                                    ],
                                ),
                                lg=2, md=8,
                            ),
                        ],
                    ),
                    # ── Visuals and Time Controls ──
                    dbc.Row(
                        className="g-3 align-items-center form-row mt-1 border-top pt-3 viz-toolbar-bottom",
                        children=[
                            dbc.Col(
                                [
                                    html.Label("Colormap", className="viz-ctrl-label"),
                                    dcc.Dropdown(
                                        id="viz-cmap-dropdown",
                                        options=[{"label": scale, "value": scale} for scale in ALL_SCALES],
                                        value="RdBu_r",
                                        clearable=False,
                                        className="viz-dropdown",
                                    ),
                                ],
                                lg=2, md=3,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Mode", className="viz-ctrl-label"),
                                    dbc.Select(
                                        id="viz-color-mode",
                                        options=[
                                            {"label": "Auto", "value": "auto"},
                                            {"label": "Global", "value": "global"},
                                            {"label": "Manual", "value": "manual"},
                                        ],
                                        value="auto",
                                        className="viz-select",
                                    ),
                                ],
                                lg=2, md=3,
                            ),
                            dbc.Col(
                                dbc.Row(
                                    id="viz-color-range-controls",
                                    className="g-2",
                                    style={"display": "none"},
                                    children=[
                                        dbc.Col(dbc.Input(id="viz-color-min", type="number", placeholder="Min", size="sm")),
                                        dbc.Col(dbc.Input(id="viz-color-max", type="number", placeholder="Max", size="sm")),
                                    ],
                                ),
                                lg=3, md=6,
                            ),
                            dbc.Col(
                                html.Div(
                                    className="d-flex align-items-center w-100 ps-lg-3 mt-md-2 mt-lg-0",
                                    children=[
                                        dbc.Button(
                                            "▶",
                                            id="viz-play-btn",
                                            color="primary",
                                            className="viz-play-btn shadow-sm me-3",
                                            disabled=True,
                                        ),
                                        html.Div(
                                            className="flex-grow-1",
                                            children=[
                                                dcc.Slider(
                                                    id="viz-time-slider",
                                                    min=0, max=0, step=1, value=0, marks={0: "0"},
                                                    tooltip={"placement": "bottom"},
                                                    updatemode="mouseup",
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                lg=5, md=12,
                            ),
                        ],
                    ),
                ],
            ),
            # ── Plot + Analysis Side by Side ──
            dbc.Row(
                className="g-2",
                children=[
                    dbc.Col(
                        [
                            html.Div(
                                className="viz-plot-wrap",
                                style={"minHeight": "450px", "height": "100%"},
                                children=[
                                    dcc.Graph(
                                        id="viz-main-plot",
                                        figure=create_empty_figure("Select a case, file, and variable"),
                                        config={"displaylogo": False, "responsive": True},
                                        style={"minHeight": "450px", "height": "100%"},
                                    ),
                                ],
                            ),
                            html.Div(
                                id="viz-var-info",
                                className="viz-var-info mt-1",
                            ),
                        ],
                        md=7,
                    ),
                    dbc.Col(
                        _build_analysis_panel(),
                        md=5,
                    ),
                ],
            ),
            # ── Multi-variable grid (same case/file, N variables side-by-side) ──
            dbc.Card(
                className="mt-3",
                children=[
                    dbc.CardHeader(
                        [
                            html.Span("Multi-variable grid", className="me-2"),
                            html.Small(
                                "same case & file, choose 2+ variables to compare",
                                className="text-muted",
                            ),
                        ]
                    ),
                    dbc.CardBody(
                        [
                            html.Div(
                                [
                                    html.Label("Variables", className="viz-ctrl-label"),
                                    dcc.Checklist(
                                        id="viz-multivar-checklist",
                                        options=[],
                                        value=[],
                                        inline=True,
                                        labelStyle={"marginRight": "0.9rem"},
                                        inputClassName="me-1",
                                    ),
                                ],
                                className="mb-2",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Label("Columns", className="viz-ctrl-label"),
                                            dbc.Select(
                                                id="viz-multivar-cols",
                                                options=[
                                                    {"label": "1", "value": "1"},
                                                    {"label": "2", "value": "2"},
                                                    {"label": "3", "value": "3"},
                                                ],
                                                value="2",
                                                className="viz-select",
                                            ),
                                        ],
                                        md=2,
                                    ),
                                    dbc.Col(
                                        html.Small(
                                            "Time/level/view settings above also apply here.",
                                            className="text-muted",
                                        ),
                                        md=10,
                                        className="d-flex align-items-end",
                                    ),
                                ],
                                className="g-2 mb-2",
                            ),
                            html.Div(
                                id="viz-multivar-grid",
                                children=[
                                    html.Div(
                                        "Tick 2+ variables above to render a grid.",
                                        className="text-muted text-center py-4",
                                    )
                                ],
                            ),
                        ]
                    ),
                ],
            ),
        ]
    )


def _build_fullscreen_overlay() -> html.Div:
    """Build the fullscreen overlay for presenting analysis content."""
    return html.Div(
        id="viz-fullscreen-overlay",
        className="viz-fullscreen-overlay viz-fullscreen-hidden",
        children=[
            # Top bar with close button
            html.Div(
                className="viz-fullscreen-topbar",
                children=[
                    html.Span(id="viz-fullscreen-title", className="viz-fullscreen-title"),
                    html.Button(
                        "\u00d7",  # ×
                        id="viz-fullscreen-close",
                        className="viz-fullscreen-close",
                        n_clicks=0,
                    ),
                ],
            ),
            # Scrollable content area
            html.Div(
                className="viz-fullscreen-content",
                children=dcc.Markdown(
                    id="viz-fullscreen-md",
                    children="",
                    link_target="_blank",
                    dangerously_allow_html=True,
                    mathjax=True,
                    className="viz-analysis-md viz-fullscreen-md-inner",
                ),
            ),
        ],
    )


def _build_analysis_panel() -> dbc.Card:
    """Build the markdown-based case analysis panel."""
    return dbc.Card(
        className=f"{CARD_CLASS} viz-analysis-panel",
        children=[
            dbc.CardHeader(
                [
                    html.Span("Case Analysis", className="small fw-bold"),
                    html.Button(
                        "\u26f6",  # ⛶ expand icon
                        id="viz-fullscreen-open",
                        className="viz-fullscreen-open-btn",
                        n_clicks=0,
                        title="Fullscreen preview",
                    ),
                ],
                className="py-2 px-2 d-flex justify-content-between align-items-center",
            ),
            dbc.CardBody(
                html.Div(
                    className="viz-analysis-tabs",
                    children=[
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    dcc.Textarea(
                                        id="viz-analysis-editor",
                                        placeholder=(
                                            "Write case analysis in Markdown\u2026\n\n"
                                        ),
                                        value="",
                                        className="viz-analysis-editor",
                                    ),
                                    label="Edit",
                                    tab_id="analysis-edit",
                                ),
                                dbc.Tab(
                                    html.Div(
                                        dcc.Markdown(
                                            id="viz-analysis-preview",
                                            children="",
                                            link_target="_blank",
                                            dangerously_allow_html=True,
                                            mathjax=True,
                                            className="viz-analysis-md",
                                        ),
                                        className="viz-analysis-preview-wrap",
                                    ),
                                    label="Preview",
                                    tab_id="analysis-preview",
                                ),
                            ],
                            id="viz-analysis-tabs",
                            active_tab="analysis-edit",
                        )
                    ],
                ),
                className="p-0",
                style={"flex": "1", "overflow": "hidden", "display": "flex", "flexDirection": "column"},
            ),
        ],
    )


def _build_case_tree(testbed_data: dict[str, list[dict[str, Any]]]) -> html.Div:
    items = []
    for category in sorted(testbed_data):
        cases = sorted(testbed_data.get(category, []), key=lambda item: item.get("name", ""))
        ran_count = sum(1 for case in cases if case.get("nc_files"))
        rows = []
        for case in cases:
            name = case.get("name", "unknown")
            nc_files = case.get("nc_files") or []
            has_output = len(nc_files) > 0
            dot_class = (
                "case-status-dot has-output" if has_output else "case-status-dot no-output"
            )
            tooltip = (
                f"{len(nc_files)} NetCDF output file(s)"
                if has_output
                else "No NetCDF output yet"
            )
            display_name = CASE_DISPLAY_NAMES.get(name, name)
            rows.append(
                html.Div(
                    className="case-row d-flex align-items-center",
                    children=[
                        html.Span(className=dot_class, title=tooltip),
                        dbc.Button(
                            display_name,
                            id={"type": "case-btn", "index": name},
                            color="link",
                            size="sm",
                            className="text-start flex-grow-1 py-1",
                            n_clicks=0,
                        ),
                    ],
                )
            )
        items.append(
            dbc.AccordionItem(
                html.Div(rows, className="d-grid gap-1"),
                title=f"{category} ({ran_count}/{len(cases)})",
                item_id=f"viz-{category}",
            )
        )

    children: list[Any] = [
        dbc.Accordion(
            items,
            id="viz-case-accordion",
            start_collapsed=True,
            always_open=True,
            active_item=[],
        )
    ]
    if not items:
        children.append(
            html.Div("No GMCORE test cases were found in the configured testbed root.", className="small text-muted mt-2")
        )
    return html.Div(children)


def _resolve_testbed_root(testbed_root: str) -> str:
    if testbed_root:
        return str(Path(testbed_root).expanduser().resolve())
    return _default_testbed_root()


def _default_testbed_root() -> str:
    project_root = Path(__file__).resolve().parents[3]
    candidates = [
        project_root / "run" / "GMCORE-TESTBED",
        project_root / "GMCORE-TESTBED",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return str(candidate.resolve())
    return str(candidates[0].resolve())


def _iter_cases(testbed_data: dict[str, list[dict[str, Any]]] | None):
    if not isinstance(testbed_data, dict):
        return ()
    for cases in testbed_data.values():
        if not isinstance(cases, list):
            continue
        for case_info in cases:
            if isinstance(case_info, dict):
                yield case_info


def _find_case_info(
    testbed_data: dict[str, list[dict[str, Any]]] | None, case_name: str
) -> dict[str, Any] | None:
    for case_info in _iter_cases(testbed_data):
        if case_info.get("name") == case_name:
            return case_info
    return None


def _find_variable_meta(nc_meta: dict[str, Any] | None, var_name: str) -> dict[str, Any] | None:
    if not isinstance(nc_meta, dict):
        return None
    variables = nc_meta.get("variables", [])
    if not isinstance(variables, list):
        return None
    for variable in variables:
        if isinstance(variable, dict) and variable.get("name") == var_name:
            return variable
    return None


def _list_nc_files(case_dir: str) -> list[str]:
    root = Path(case_dir)
    if not root.is_dir():
        return []
    return [
        str(path.resolve())
        for path in sorted(root.glob("*.nc"), key=lambda item: item.stat().st_mtime, reverse=True)
        if path.is_file()
    ]


def _build_file_options(nc_files: list[str]) -> list[dict[str, str]]:
    return [{"label": Path(path).name, "value": path} for path in nc_files]


def _build_variable_options(nc_meta: dict[str, Any] | None) -> list[dict[str, str]]:
    options = []
    variables = (nc_meta or {}).get("variables", [])
    if not isinstance(variables, list):
        return options

    for variable in variables:
        if not isinstance(variable, dict):
            continue
        name = variable.get("name")
        if not name:
            continue
        long_name = variable.get("long_name") or ""
        dims = tuple(variable.get("dims") or ())
        dims_label = ", ".join(str(dim) for dim in dims) or "scalar"
        label = f"{name} [{dims_label}]"
        if long_name:
            label = f"{label} - {long_name}"
        options.append({"label": label, "value": name})
    return options


def _default_variable_name(nc_meta: dict[str, Any] | None) -> str | None:
    variables = (nc_meta or {}).get("variables", [])
    if not isinstance(variables, list):
        return None

    for variable in variables:
        if isinstance(variable, dict) and variable.get("name") == "u" and variable.get("plot_type") in PLOTTABLE_TYPES:
            return "u"

    for variable in variables:
        if isinstance(variable, dict) and variable.get("plot_type") in PLOTTABLE_TYPES:
            return variable.get("name")

    for variable in variables:
        if isinstance(variable, dict) and variable.get("name"):
            return variable.get("name")

    return None


def _build_time_marks(time_steps: int) -> tuple[int, dict[int, str]]:
    count = max(int(time_steps or 0), 0)
    max_idx = max(count - 1, 0)
    if max_idx == 0:
        return 0, {0: "0"}

    step_count = 5
    marks = {
        int(round(step * max_idx / step_count)): str(int(round(step * max_idx / step_count)))
        for step in range(step_count + 1)
    }
    marks[max_idx] = str(max_idx)
    return max_idx, dict(sorted(marks.items()))


_LAT_DIM_NAMES = {"lat", "ilat"}
_LON_DIM_NAMES = {"lon", "ilon"}


def _dim_size_for(variable_meta: dict[str, Any] | None, candidates: set[str]) -> int:
    if not isinstance(variable_meta, dict):
        return 0
    dims = list(variable_meta.get("dims") or [])
    shape = list(variable_meta.get("shape") or [])
    for dim_name, dim_size in zip(dims, shape):
        if dim_name in candidates:
            return int(dim_size)
    return 0


def _format_axis_value(value: Any, view_mode: str) -> str:
    """Format a coordinate value for slider marks / plot titles."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not np.isfinite(f):
        return str(value)
    if view_mode == "zonal":
        return f"{f:.1f}°"
    if view_mode == "meridional":
        return f"{f:.1f}°"
    if float(int(f)) == f:
        return f"{int(f)}"
    return f"{f:.2f}"


def _build_index_slider(variable_meta: dict[str, Any] | None,
                        view_mode: str,
                        axis_values: Any = None,
                        ) -> tuple[int, dict[int, str], int]:
    """Return ``(max_idx, marks, default_value)`` for the slice slider.

    When ``axis_values`` is provided, mark labels are the physical coordinate
    (level / lat / lon) instead of raw indices — matching the coordinate
    mapping used on the horizontal plots' axes.
    """
    if view_mode == "zonal":
        candidates = _LAT_DIM_NAMES
    elif view_mode == "meridional":
        candidates = _LON_DIM_NAMES
    else:
        candidates = LEVEL_DIMS
    size = _dim_size_for(variable_meta, candidates)
    max_idx = max(size - 1, 0)

    if axis_values is not None:
        axis_values = np.asarray(axis_values).ravel()
        if axis_values.size == 0:
            axis_values = None

    def _label(idx: int) -> str:
        if axis_values is not None and 0 <= idx < axis_values.size:
            return _format_axis_value(axis_values[idx], view_mode)
        return str(idx)

    if max_idx == 0:
        return 0, {0: _label(0)}, 0

    step_count = 4 if axis_values is not None else 6
    mark_indices = {
        int(round(step * max_idx / step_count)) for step in range(step_count + 1)
    }
    mark_indices.add(0)
    mark_indices.add(max_idx)
    marks = {idx: _label(idx) for idx in sorted(mark_indices)}
    default_value = max_idx // 2
    return max_idx, marks, default_value


def _index_label_for(view_mode: str) -> str:
    if view_mode == "zonal":
        return "Latitude idx"
    if view_mode == "meridional":
        return "Longitude idx"
    return "Level"


def _safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _current_range(data: Any) -> tuple[float | None, float | None]:
    try:
        finite = np.asarray(data, dtype=float)
    except (TypeError, ValueError):
        return None, None

    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return None, None
    return float(np.min(finite)), float(np.max(finite))


def _auto_color_bounds(data: Any, symmetric: bool) -> tuple[float | None, float | None]:
    data_min, data_max = _current_range(data)
    if data_min is None or data_max is None:
        return None, None
    if not symmetric:
        return None, None
    limit = max(abs(data_min), abs(data_max))
    return -limit, limit


def _color_bounds(
    data: Any,
    color_mode: str,
    color_min: Any,
    color_max: Any,
    symmetric: bool,
    global_min: float | None = None,
    global_max: float | None = None,
) -> tuple[float | None, float | None]:
    if color_mode == "manual":
        manual_min = _safe_float(color_min)
        manual_max = _safe_float(color_max)
        if manual_min is not None and manual_max is not None and manual_min > manual_max:
            manual_min, manual_max = manual_max, manual_min
        return manual_min, manual_max
    if color_mode == "global" and global_min is not None and global_max is not None:
        if not symmetric:
            return global_min, global_max
        limit = max(abs(global_min), abs(global_max))
        return -limit, limit
    return _auto_color_bounds(data, symmetric)


def _format_number(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.6g}"
    return str(value)


def _format_time_label(time_val: Any) -> str:
    """Convert raw time coordinate to a readable label."""
    import datetime as dt

    if time_val is None:
        return ""

    # If it's already a datetime-like object from xarray/numpy
    if hasattr(time_val, 'strftime'):
        try:
            return time_val.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass

    # If it's a numpy datetime64
    try:
        import numpy as _np
        if isinstance(time_val, _np.datetime64):
            ts = (time_val - _np.datetime64('1970-01-01T00:00:00')) / _np.timedelta64(1, 's')
            return dt.datetime.utcfromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass

    # If it's a large integer (nanoseconds since epoch, typical from xarray)
    try:
        val = float(time_val)
        if abs(val) > 1e15:  # nanoseconds
            ts = val / 1e9
            return dt.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
        elif abs(val) > 1e9:  # seconds
            return dt.datetime.utcfromtimestamp(val).strftime("%Y-%m-%d %H:%M")
        else:
            # Likely a relative time (hours, days)
            return f"{val:.1f}"
    except Exception:
        pass

    return str(time_val)


def _plot_title(var_name: str, coords: dict[str, Any]) -> str:
    pieces = [var_name]
    if "time" in coords:
        time_label = _format_time_label(coords['time'])
        if time_label:
            pieces.append(f"t={time_label}")
    # Only show "lev=..." when lev is a scalar (horizontal slice).
    lev_val = coords.get("lev")
    if lev_val is not None and not hasattr(lev_val, "__len__"):
        pieces.append(f"lev={_format_number(lev_val)}")
    if "slice_lat" in coords:
        pieces.append(f"lat={_format_number(coords['slice_lat'])}°")
    if "slice_lon" in coords:
        pieces.append(f"lon={_format_number(coords['slice_lon'])}°")
    return " | ".join(pieces)


def _figure_for_data(
    plot_type: str,
    var_name: str,
    units: str,
    data: Any,
    coords: dict[str, Any],
    colorscale: str,
    zmin: float | None,
    zmax: float | None,
    symmetric: bool,
    background: str = "coastline",
    topo: tuple[Any, Any, Any] | None = None,
):
    title = _plot_title(var_name, coords)

    if plot_type in {"map_2d", "map_2d_with_level", "static_map"}:
        return plot_map_2d(
            data,
            coords.get("lat"),
            coords.get("lon"),
            title=title,
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            symmetric=symmetric,
            background=background,
            topo=topo,
        )

    if plot_type == "lat_height":
        return plot_lat_height(
            data,
            coords.get("lat"),
            coords.get("lev"),
            title=title,
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            topo=topo,
        )

    if plot_type == "lon_height":
        return plot_lon_height(
            data,
            coords.get("lon"),
            coords.get("lev"),
            title=title,
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            topo=topo,
        )

    if plot_type == "time_series":
        return plot_time_series(coords.get("time"), data, title=title, ylabel=units or var_name)

    if plot_type == "scalar":
        scalar_value = np.asarray(data).reshape(()).item()
        return create_empty_figure(f"{var_name} = {_format_number(scalar_value)}")

    return create_empty_figure(f"{var_name} is not plottable in this dashboard")


def _build_var_info(
    var_name: str | None,
    var_meta: dict[str, Any] | None,
    data: Any = None,
) -> list[html.Div]:
    if not var_name:
        return [html.Div("Select a variable to inspect.")]

    if not isinstance(var_meta, dict):
        return [html.Div(f"Metadata for {var_name} is unavailable.")]

    data_min, data_max = _current_range(data)
    shape = tuple(var_meta.get("shape") or ())

    rows = [
        html.Div([html.Strong("Name: "), html.Span(var_name)]),
        html.Div([html.Strong("Shape: "), html.Span(str(shape) if shape else "N/A")]),
        html.Div(
            [
                html.Strong("Long Name: "),
                html.Span(var_meta.get("long_name") or "N/A"),
            ]
        ),
        html.Div([html.Strong("Units: "), html.Span(var_meta.get("units") or "N/A")]),
        html.Div(
            [
                html.Strong("Data Range: "),
                html.Span(f"{_format_number(data_min)} to {_format_number(data_max)}"),
            ]
        ),
    ]
    return rows


def _default_colorscale_for_variable(file_path: str | None, var_name: str | None) -> str:
    if not file_path or not var_name:
        return "RdBu_r"

    default_scale = get_default_colorscale(var_name)
    if default_scale in ALL_SCALES:
        return default_scale

    try:
        data, _ = load_variable_slice(file_path, var_name, time_idx=0, level_idx=0)
        smart_scale, _ = get_smart_colormap(var_name, data)
        if smart_scale in ALL_SCALES:
            return smart_scale
    except Exception:
        pass

    return "RdBu_r"


@callback(
    Output("viz-file-dropdown", "options"),
    Output("viz-file-dropdown", "value"),
    Output("viz-current-case-dir", "data"),
    Input({"type": "case-btn", "index": ALL}, "n_clicks"),
    Input("viz-preview-request", "data"),
    State({"type": "case-btn", "index": ALL}, "id"),
    State("viz-testbed-data", "data"),
)
def update_nc_files_for_case(
    _clicks: list[int] | None,
    preview_request: dict[str, Any] | None,
    case_ids: list[dict[str, str]] | None,
    testbed_data: dict[str, list[dict[str, Any]]] | None,
):
    ctx = callback_context
    triggered_id = ctx.triggered_id

    # -- Handle Preview Request --
    if triggered_id == "viz-preview-request" and isinstance(preview_request, dict):
        file_path = preview_request.get("file_path")
        if isinstance(file_path, str) and file_path:
            candidate = Path(file_path).expanduser()
            if candidate.is_file():
                resolved_file = str(candidate.resolve())
                case_dir = candidate.resolve().parent.as_posix()
                nc_files = _list_nc_files(case_dir)
                if resolved_file not in nc_files:
                    nc_files.insert(0, resolved_file)
                # clear preview request is actually not needed if we just return the new options,
                # Dash will maintain the visualization.
                return _build_file_options(nc_files), resolved_file, case_dir

    # -- Handle Normal Case Selection --
    case_name = triggered_id.get("index") if isinstance(triggered_id, dict) else None
    if not case_name and case_ids:
        for case_id in case_ids:
            if isinstance(case_id, dict) and case_id.get("index"):
                case_name = case_id["index"]
                break

    if not case_name:
        return [], None, None

    case_info = _find_case_info(testbed_data, case_name)
    case_dir = case_info.get("path") if case_info else None
    nc_files = _list_nc_files(case_dir) if case_dir else []
    options = _build_file_options(nc_files)
    value = nc_files[0] if nc_files else None
    return options, value, case_dir


@callback(
    Output("viz-var-dropdown", "options"),
    Output("viz-var-dropdown", "value"),
    Output("viz-nc-meta", "data"),
    Output("viz-time-slider", "max"),
    Output("viz-time-slider", "marks"),
    Input("viz-file-dropdown", "value"),
)
def update_variables_for_file(file_path: str | None):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if not file_path:
        return [], None, None, 0, {0: "0"}

    try:
        nc_meta = inspect_nc(file_path)
    except Exception as exc:
        return [], None, {"error": str(exc), "variables": [], "time_steps": 0}, 0, {0: "0"}

    options = _build_variable_options(nc_meta)
    default_var = _default_variable_name(nc_meta)
    max_idx, marks = _build_time_marks(nc_meta.get("time_steps", 0))
    return options, default_var, nc_meta, max_idx, marks


@callback(
    Output("viz-level-slider", "max"),
    Output("viz-level-slider", "marks"),
    Output("viz-level-slider", "value"),
    Output("viz-level-container", "style"),
    Output("viz-view-container", "style"),
    Output("viz-view-mode", "value"),
    Output("viz-level-label", "children"),
    Output("viz-cmap-dropdown", "value"),
    Output("viz-color-min", "value"),
    Output("viz-color-max", "value"),
    Input("viz-var-dropdown", "value"),
    Input("viz-view-mode", "value"),
    Input("viz-nc-meta", "data"),
    State("viz-file-dropdown", "value"),
)
def update_variable_controls(
    var_name: str | None,
    view_mode: str | None,
    nc_meta: dict[str, Any] | None,
    file_path: str | None,
):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    hidden = {"display": "none"}
    block = {"display": "block"}

    if not var_name:
        return (0, {0: "0"}, 0, hidden, hidden, "horizontal", "Level",
                "RdBu_r", None, None)

    variable_meta = _find_variable_meta(nc_meta, var_name)
    plot_type = (variable_meta or {}).get("plot_type")
    is_3d = plot_type == "map_2d_with_level"

    effective_view = (view_mode or "horizontal") if is_3d else "horizontal"

    # Reset view to horizontal whenever the variable itself changes.
    if ctx.triggered_id == "viz-var-dropdown":
        effective_view = "horizontal"

    if is_3d:
        axis_values = load_slice_axis(file_path, var_name, effective_view) if file_path else None
        max_idx, marks, default_value = _build_index_slider(
            variable_meta, effective_view, axis_values=axis_values,
        )
    else:
        max_idx, marks, default_value = 0, {0: "0"}, 0

    level_style = block if is_3d else hidden
    view_style = block if is_3d else hidden
    label = _index_label_for(effective_view)

    colorscale = _default_colorscale_for_variable(file_path, var_name)
    return (max_idx, marks, default_value, level_style, view_style, effective_view,
            label, colorscale, None, None)


@callback(
    Output("viz-color-range-controls", "style"),
    Input("viz-color-mode", "value"),
)
def toggle_manual_color_controls(color_mode: str):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    return {"display": "flex"} if color_mode == "manual" else {"display": "none"}


@callback(
    Output("viz-main-plot", "figure"),
    Output("viz-var-info", "children"),
    Input("viz-var-dropdown", "value"),
    Input("viz-time-slider", "value"),
    Input("viz-level-slider", "value"),
    Input("viz-view-mode", "value"),
    Input("viz-cmap-dropdown", "value"),
    Input("viz-color-mode", "value"),
    Input("viz-color-min", "value"),
    Input("viz-color-max", "value"),
    Input("viz-nc-meta", "data"),
    State("viz-file-dropdown", "value"),
)
def update_main_plot(
    var_name: str | None,
    time_idx: int | None,
    level_idx: int | None,
    view_mode: str | None,
    colorscale: str | None,
    color_mode: str,
    color_min: Any,
    color_max: Any,
    nc_meta: dict[str, Any] | None,
    file_path: str | None,
):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if not file_path or not var_name:
        return create_empty_figure("Select a case, file, and variable"), _build_var_info(var_name, None)

    if isinstance(nc_meta, dict) and nc_meta.get("error"):
        message = f"Unable to inspect file: {nc_meta['error']}"
        return create_empty_figure(message), [html.Div(message)]

    variable_meta = _find_variable_meta(nc_meta, var_name)
    plot_type = (variable_meta or {}).get("plot_type", "unknown")
    units = (variable_meta or {}).get("units") or ""

    # Vertical cross-sections only apply to 3-D variables.
    if plot_type != "map_2d_with_level":
        view_mode = "horizontal"
    effective_view = view_mode or "horizontal"

    try:
        data, coords = load_variable_slice(
            file_path,
            var_name,
            time_idx=time_idx if time_idx is not None else 0,
            level_idx=level_idx,
            view_mode=effective_view,
        )
    except Exception as exc:
        message = f"Unable to load {var_name}: {exc}"
        return create_empty_figure(message), [html.Div(message)]

    # Dispatch plot type: for 3-D vars, zonal → (lon, lev); meridional → (lat, lev).
    effective_plot_type = plot_type
    if plot_type == "map_2d_with_level":
        if effective_view == "zonal":
            effective_plot_type = "lon_height"
        elif effective_view == "meridional":
            effective_plot_type = "lat_height"

    resolved_scale = colorscale or _default_colorscale_for_variable(file_path, var_name)
    try:
        smart_scale, smart_symmetric = get_smart_colormap(var_name, data)
    except Exception:
        smart_scale, smart_symmetric = "Viridis", False
    if resolved_scale not in ALL_SCALES and smart_scale in ALL_SCALES:
        resolved_scale = smart_scale

    global_min, global_max = None, None
    if color_mode == "global":
        from gmcore_dashboard.dashboard.inspector import load_variable_global_range
        global_min, global_max = load_variable_global_range(
            file_path, var_name, level_idx, view_mode=effective_view,
        )

    zmin, zmax = _color_bounds(
        data, color_mode, color_min, color_max, smart_symmetric, global_min, global_max
    )

    # If only time slider changed, apply a surgical payload patch.
    if ctx.triggered_id == "viz-time-slider" and effective_plot_type in PLOTTABLE_TYPES:
        import dash
        import numpy as np
        from gmcore_dashboard.dashboard.plots import _prepare_grid, _prepare_series, _resolve_color_limits, _finite_values
        
        patched_figure = dash.Patch()
        title = _plot_title(var_name, coords)
        patched_figure["layout"]["title"]["text"] = title
        
        if effective_plot_type == "time_series":
            time_axis, series = _prepare_series(coords.get("time"), data)
            # Prevent silent JSON serialization crashes on NaNs
            if series is not None:
                series = np.where(np.isnan(series), None, series).tolist()
                patched_figure["data"][0]["y"] = series
            if time_axis is not None:
                patched_figure["data"][0]["x"] = time_axis.tolist()
        elif effective_plot_type != "scalar":
            grid = _prepare_grid(data)
            if grid is not None:
                # Prevent null injection by correctly resolving the padding for flat/zero data
                finite_data = _finite_values(data)
                final_zmin, final_zmax = _resolve_color_limits(finite_data, zmin, zmax, smart_symmetric)
                patched_figure["data"][0]["zmin"] = final_zmin
                patched_figure["data"][0]["zmax"] = final_zmax

                # NaNs crash standard json payload generation. Replace with None objects.
                safe_grid = np.where(np.isnan(grid), None, grid).tolist()
                patched_figure["data"][0]["z"] = safe_grid
        
        info = _build_var_info(var_name, variable_meta, data)
        return patched_figure, info

    case_name = Path(file_path).parent.name if file_path else None
    background = get_map_background(case_name)
    topo = None
    if background == "topography":
        if effective_view in {"zonal", "meridional"}:
            topo = load_terrain_slice(file_path, effective_view, level_idx)
        else:
            topo = load_terrain_field(file_path)

    figure = _figure_for_data(
        effective_plot_type,
        var_name,
        units,
        data,
        coords,
        resolved_scale,
        zmin,
        zmax,
        smart_symmetric,
        background=background,
        topo=topo,
    )
    info = _build_var_info(var_name, variable_meta, data)
    return figure, info


@callback(
    Output("viz-interval", "disabled"),
    Output("viz-play-btn", "children"),
    Output("viz-play-btn", "color"),
    Output("viz-play-btn", "disabled"),
    Output("viz-time-slider", "value"),
    Input("viz-play-btn", "n_clicks"),
    Input("viz-interval", "n_intervals"),
    Input("viz-time-slider", "max"),
    Input("viz-file-dropdown", "value"),
    State("viz-interval", "disabled"),
    State("viz-time-slider", "value"),
)
def handle_time_playback(
    _play_clicks: int | None,
    _n_intervals: int | None,
    slider_max: int | None,
    _file_path: str | None,
    interval_disabled: bool | None,
    slider_value: int | None,
):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    max_idx = max(int(slider_max or 0), 0)
    current_value = int(slider_value or 0)
    current_value = max(0, min(current_value, max_idx))
    can_play = max_idx > 0
    triggered = ctx.triggered_id

    if triggered == "viz-play-btn":
        if not can_play:
            return True, "Play", "secondary", True, 0
        new_disabled = not bool(interval_disabled)
        return (
            new_disabled,
            "Play" if new_disabled else "Pause",
            "secondary" if new_disabled else "warning",
            False,
            current_value,
        )

    if triggered == "viz-interval":
        if bool(interval_disabled):
            raise PreventUpdate
        next_value = 0 if current_value >= max_idx else current_value + 1
        return False, "Pause", "warning", False, next_value

    return True, "Play", "secondary", not can_play, 0


# ── Analysis Panel Callbacks ──


@callback(
    Output("viz-analysis-preview", "children"),
    Input("viz-analysis-tabs", "active_tab"),
    State("viz-analysis-editor", "value"),
)
def update_analysis_preview(active_tab: str, content: str | None):
    if active_tab != "analysis-preview":
        raise PreventUpdate
    if not content:
        return "*No content yet. Switch to Edit tab to start writing.*"
    # Return raw markdown — let dcc.Markdown handle rendering (including mathjax)
    return content


@callback(
    Output("viz-fullscreen-overlay", "className"),
    Output("viz-fullscreen-md", "children"),
    Output("viz-fullscreen-title", "children"),
    Input("viz-fullscreen-open", "n_clicks"),
    Input("viz-fullscreen-close", "n_clicks"),
    State("viz-analysis-editor", "value"),
    State("viz-current-case-dir", "data"),
    prevent_initial_call=True,
)
def toggle_fullscreen(n_open: int, n_close: int, content: str | None, case_dir: str | None):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    triggered = ctx.triggered_id
    if triggered == "viz-fullscreen-open" and content:
        title = Path(case_dir).name if case_dir else ""
        return (
            "viz-fullscreen-overlay viz-fullscreen-visible",
            content,
            title,
        )
    # close
    return "viz-fullscreen-overlay viz-fullscreen-hidden", no_update, no_update


@callback(
    Output("viz-analysis-store", "data"),
    Output("viz-analysis-editor", "value"),
    Input("viz-current-case-dir", "data"),
    Input("viz-analysis-editor", "value"),
    State("viz-analysis-store", "data"),
)
def sync_analysis_content(
    case_dir: str | None,
    editor_value: str | None,
    store_data: dict[str, str] | None,
):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    store_data = store_data or {}
    triggered = ctx.triggered_id

    if triggered == "viz-current-case-dir":
        content = store_data.get(case_dir or "", "")
        if not content and case_dir:
            case_name = Path(case_dir).name
            content = CASE_DEFAULT_ANALYSES.get(case_name, "")
        return store_data, content

    if triggered == "viz-analysis-editor" and case_dir:
        store_data[case_dir] = editor_value or ""
        return store_data, no_update

    raise PreventUpdate


# ── Multi-variable grid (same file, N variables side-by-side) ────────────────


@callback(
    Output("viz-multivar-checklist", "options"),
    Output("viz-multivar-checklist", "value"),
    Input("viz-nc-meta", "data"),
    State("viz-multivar-checklist", "value"),
)
def update_multivar_checklist(nc_meta: dict[str, Any] | None, current: list[str] | None):
    options = _build_variable_options(nc_meta)
    allowed = {opt["value"] for opt in options}
    preserved = [v for v in (current or []) if v in allowed]
    return options, preserved


def _multivar_cell(
    file_path: str,
    var_name: str,
    nc_meta: dict[str, Any] | None,
    time_idx: int,
    level_idx: int | None,
    view_mode: str,
    col_width: int,
) -> dbc.Col:
    variable_meta = _find_variable_meta(nc_meta, var_name)
    plot_type = (variable_meta or {}).get("plot_type", "unknown")
    units = (variable_meta or {}).get("units") or ""
    if plot_type != "map_2d_with_level":
        effective_view = "horizontal"
    else:
        effective_view = view_mode or "horizontal"

    try:
        data, coords = load_variable_slice(
            file_path,
            var_name,
            time_idx=time_idx if time_idx is not None else 0,
            level_idx=level_idx,
            view_mode=effective_view,
        )
    except Exception as exc:  # noqa: BLE001
        fig = create_empty_figure(f"{var_name}: {exc}")
        return dbc.Col(dcc.Graph(figure=fig, config={"displaylogo": False}), md=col_width)

    effective_plot_type = plot_type
    if plot_type == "map_2d_with_level":
        if effective_view == "zonal":
            effective_plot_type = "lon_height"
        elif effective_view == "meridional":
            effective_plot_type = "lat_height"

    resolved_scale = _default_colorscale_for_variable(file_path, var_name)
    try:
        smart_scale, smart_symmetric = get_smart_colormap(var_name, data)
    except Exception:
        smart_scale, smart_symmetric = "Viridis", False
    if resolved_scale not in ALL_SCALES and smart_scale in ALL_SCALES:
        resolved_scale = smart_scale

    zmin, zmax = _color_bounds(data, "auto", None, None, smart_symmetric, None, None)

    case_name = Path(file_path).parent.name if file_path else None
    background = get_map_background(case_name)
    topo = None
    if background == "topography":
        if effective_view in {"zonal", "meridional"}:
            topo = load_terrain_slice(file_path, effective_view, level_idx)
        else:
            topo = load_terrain_field(file_path)

    figure = _figure_for_data(
        effective_plot_type,
        var_name,
        units,
        data,
        coords,
        resolved_scale,
        zmin,
        zmax,
        smart_symmetric,
        background=background,
        topo=topo,
    )
    return dbc.Col(
        dcc.Graph(
            figure=figure,
            config={"displaylogo": False, "responsive": True},
            style={"height": "360px"},
        ),
        md=col_width,
        className="mb-2",
    )


@callback(
    Output("viz-multivar-grid", "children"),
    Input("viz-multivar-checklist", "value"),
    Input("viz-multivar-cols", "value"),
    Input("viz-time-slider", "value"),
    Input("viz-level-slider", "value"),
    Input("viz-view-mode", "value"),
    State("viz-file-dropdown", "value"),
    State("viz-nc-meta", "data"),
)
def render_multivar_grid(
    var_names: list[str] | None,
    cols_value: str | None,
    time_idx: int | None,
    level_idx: int | None,
    view_mode: str | None,
    file_path: str | None,
    nc_meta: dict[str, Any] | None,
):
    selection = [v for v in (var_names or []) if v]
    if not selection or not file_path:
        return html.Div(
            "Tick 2+ variables above to render a grid.",
            className="text-muted text-center py-4",
        )
    try:
        n_cols = max(1, min(3, int(cols_value or 2)))
    except (TypeError, ValueError):
        n_cols = 2
    col_width = max(4, 12 // n_cols)

    cells = [
        _multivar_cell(
            file_path=file_path,
            var_name=var_name,
            nc_meta=nc_meta,
            time_idx=time_idx or 0,
            level_idx=level_idx,
            view_mode=view_mode or "horizontal",
            col_width=col_width,
        )
        for var_name in selection
    ]
    return dbc.Row(cells, className="g-2")


__all__ = ["create_layout"]
