"""Multi-view tab: dynamic grid of independent NetCDF panels.

Each cell chooses its own experiment, h0 file, variable, view (horizontal /
zonal / meridional), time step, and vertical level. Cells are added/removed
dynamically; layout reflows through ``mv-columns`` (1/2/3 per row).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
import numpy as np
from dash import ALL, MATCH, Input, Output, State, callback, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate

from gmcore_dashboard.dashboard.inspector import inspect_nc, load_variable_slice
from gmcore_dashboard.dashboard.plots import plot_lat_height, plot_lon_height, plot_map_2d
from gmcore_dashboard.experiments.dashboard_backend import scan_experiments

CARD_CLASS = "border"
DEFAULT_COLS = 2
VIEW_OPTIONS = [
    {"label": "水平面", "value": "horizontal"},
    {"label": "纬向剖面（lat–lev）", "value": "zonal"},
    {"label": "经向剖面（lon–lev）", "value": "meridional"},
]


def create_layout(gmcore_root: Path, testbed_root: Path) -> dbc.Container:
    """Top-level Multi-view tab layout."""

    gmcore_root = Path(gmcore_root) if gmcore_root else Path.cwd()

    return dbc.Container(
        fluid=True,
        className="p-2",
        children=[
            dcc.Store(id="mv-cells-store", data=[0, 1]),
            dcc.Store(id="mv-next-index", data=2),
            dcc.Store(id="mv-gmcore-root", data=str(gmcore_root)),
            _build_toolbar(),
            html.Div(id="mv-grid", className="mv-grid mt-2"),
        ],
    )


def _build_toolbar() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS + " mb-2",
        children=[
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button("+ 添加面板", id="mv-add-cell", color="primary", size="sm"),
                            width="auto",
                        ),
                        dbc.Col(
                            dbc.Button(
                                "清空全部", id="mv-clear-cells", color="secondary", outline=True, size="sm"
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Span("列数：", className="me-2 small text-muted"),
                                    dbc.ButtonGroup(
                                        [
                                            dbc.Button("1", id={"type": "mv-cols-btn", "value": 1}, size="sm", outline=True),
                                            dbc.Button("2", id={"type": "mv-cols-btn", "value": 2}, size="sm", outline=True, active=True),
                                            dbc.Button("3", id={"type": "mv-cols-btn", "value": 3}, size="sm", outline=True),
                                        ],
                                    ),
                                ],
                                className="d-flex align-items-center",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Div(id="mv-status", className="small text-muted"),
                        ),
                    ],
                    className="align-items-center g-2",
                ),
                className="p-2",
            )
        ],
    )


def _cell_card(index: int, column_count: int) -> dbc.Col:
    """Return a single grid cell. ID pattern = {"type": "mv-xxx", "index": index}."""
    col_width = max(1, int(12 / max(1, column_count)))
    return dbc.Col(
        width=col_width,
        className="mb-2",
        children=dbc.Card(
            className=CARD_CLASS,
            children=[
                dbc.CardHeader(
                    dbc.Row(
                        [
                            dbc.Col(html.Span(f"面板 {index + 1}", className="fw-bold small"), width="auto"),
                            dbc.Col(
                                dbc.Button(
                                    "×",
                                    id={"type": "mv-remove-btn", "index": index},
                                    color="link",
                                    size="sm",
                                    className="text-danger py-0 px-2",
                                ),
                                width="auto",
                                className="ms-auto",
                            ),
                        ],
                        className="align-items-center g-0",
                    ),
                    className="py-1",
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    _label_above(
                                        "数值试验",
                                        dcc.Dropdown(
                                            id={"type": "mv-exp", "index": index},
                                            placeholder="选择试验",
                                            clearable=False,
                                        ),
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    _label_above(
                                        "文件",
                                        dcc.Dropdown(
                                            id={"type": "mv-file", "index": index},
                                            placeholder="选择输出文件",
                                            clearable=False,
                                        ),
                                    ),
                                    md=6,
                                ),
                            ],
                            className="g-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    _label_above(
                                        "变量",
                                        dcc.Dropdown(
                                            id={"type": "mv-var", "index": index},
                                            placeholder="选择变量",
                                            clearable=False,
                                        ),
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    _label_above(
                                        "视图",
                                        dbc.RadioItems(
                                            id={"type": "mv-view", "index": index},
                                            options=VIEW_OPTIONS,
                                            value="horizontal",
                                            inline=True,
                                            inputClassName="me-1",
                                            labelClassName="me-2 small",
                                        ),
                                    ),
                                    md=6,
                                ),
                            ],
                            className="g-2 mt-1",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    _label_above(
                                        "时间",
                                        dcc.Slider(
                                            id={"type": "mv-time", "index": index},
                                            min=0,
                                            max=0,
                                            value=0,
                                            step=1,
                                            marks=None,
                                            tooltip={"placement": "bottom", "always_visible": False},
                                        ),
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    _label_above(
                                        "层次/切片",
                                        dcc.Slider(
                                            id={"type": "mv-level", "index": index},
                                            min=0,
                                            max=0,
                                            value=0,
                                            step=1,
                                            marks=None,
                                            tooltip={"placement": "bottom", "always_visible": False},
                                        ),
                                    ),
                                    md=6,
                                ),
                            ],
                            className="g-2 mt-1",
                        ),
                        dcc.Loading(
                            type="dot",
                            children=dcc.Graph(
                                id={"type": "mv-figure", "index": index},
                                config={"displaylogo": False, "displayModeBar": "hover"},
                                style={"height": "320px"},
                            ),
                        ),
                    ],
                    className="p-2",
                ),
            ],
        ),
    )


def _label_above(label: str, control: Any) -> html.Div:
    return html.Div(
        [
            html.Div(label, className="small text-muted mb-1"),
            control,
        ]
    )


# ─── Grid reflow: render cells whenever the cell list or column count changes ───
@callback(
    Output("mv-grid", "children"),
    Input("mv-cells-store", "data"),
    Input({"type": "mv-cols-btn", "value": ALL}, "n_clicks"),
    State({"type": "mv-cols-btn", "value": ALL}, "id"),
)
def render_grid(cell_indices, n_clicks_list, btn_ids):
    cols = DEFAULT_COLS
    if ctx.triggered_id and isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get("type") == "mv-cols-btn":
        cols = int(ctx.triggered_id.get("value") or DEFAULT_COLS)
    if not cell_indices:
        return dbc.Alert(
            '暂无面板。点击「+ 添加面板」开始多场对比。',
            color="light",
            className="text-center",
        )
    return dbc.Row([_cell_card(idx, cols) for idx in cell_indices], className="g-2")


# ─── Cell add / remove / clear ───
@callback(
    Output("mv-cells-store", "data"),
    Output("mv-next-index", "data"),
    Input("mv-add-cell", "n_clicks"),
    Input("mv-clear-cells", "n_clicks"),
    Input({"type": "mv-remove-btn", "index": ALL}, "n_clicks"),
    State("mv-cells-store", "data"),
    State("mv-next-index", "data"),
    prevent_initial_call=True,
)
def mutate_cells(_add, _clear, _remove_clicks, cells, next_idx):
    triggered = ctx.triggered_id
    cells = list(cells or [])
    next_idx = int(next_idx or 0)
    if triggered == "mv-add-cell":
        cells.append(next_idx)
        next_idx += 1
    elif triggered == "mv-clear-cells":
        cells = []
    elif isinstance(triggered, dict) and triggered.get("type") == "mv-remove-btn":
        # Ignore initial phantom clicks (value == None) emitted during layout render.
        trig = ctx.triggered[0] if ctx.triggered else None
        if not trig or not trig.get("value"):
            raise PreventUpdate
        target = triggered.get("index")
        cells = [idx for idx in cells if idx != target]
    else:
        raise PreventUpdate
    return cells, next_idx


# ─── Experiment dropdown options (one-shot per cell mount) ───
@callback(
    Output({"type": "mv-exp", "index": MATCH}, "options"),
    Input({"type": "mv-exp", "index": MATCH}, "id"),
    State("mv-gmcore-root", "data"),
)
def fill_experiment_options(_id, gmcore_root):
    rows = scan_experiments(_experiments_root(gmcore_root))
    return [
        {
            "label": f"{row['name']} · {row['status']} · {row['experiment_id'][-12:]}",
            "value": row["experiment_id"],
        }
        for row in rows
    ]


# ─── File options: populate when experiment changes ───
@callback(
    Output({"type": "mv-file", "index": MATCH}, "options"),
    Output({"type": "mv-file", "index": MATCH}, "value"),
    Input({"type": "mv-exp", "index": MATCH}, "value"),
    State("mv-gmcore-root", "data"),
)
def fill_file_options(exp_id, gmcore_root):
    if not exp_id:
        return [], None
    files = _nc_files_for(exp_id, gmcore_root)
    options = [{"label": Path(p).name, "value": p} for p in files]
    value = files[0] if files else None
    return options, value


# ─── Variable + slider bounds: populate when file changes ───
@callback(
    Output({"type": "mv-var", "index": MATCH}, "options"),
    Output({"type": "mv-var", "index": MATCH}, "value"),
    Output({"type": "mv-time", "index": MATCH}, "max"),
    Output({"type": "mv-time", "index": MATCH}, "marks"),
    Output({"type": "mv-time", "index": MATCH}, "value"),
    Input({"type": "mv-file", "index": MATCH}, "value"),
)
def fill_variable_options(file_path):
    if not file_path or not Path(file_path).is_file():
        return [], None, 0, None, 0
    meta = inspect_nc(file_path)
    variables = [v for v in meta.get("variables", []) if _is_plottable(v)]
    options = [{"label": v["name"], "value": v["name"]} for v in variables]
    default_var = variables[0]["name"] if variables else None
    time_max = max(0, int(meta.get("time_steps", 1)) - 1)
    marks = None
    if time_max > 0:
        step = max(1, time_max // 6)
        marks = {i: str(i) for i in range(0, time_max + 1, step)}
    return options, default_var, time_max, marks, 0


# ─── Level slider: reacts to variable + view ───
@callback(
    Output({"type": "mv-level", "index": MATCH}, "max"),
    Output({"type": "mv-level", "index": MATCH}, "marks"),
    Output({"type": "mv-level", "index": MATCH}, "value"),
    Input({"type": "mv-var", "index": MATCH}, "value"),
    Input({"type": "mv-view", "index": MATCH}, "value"),
    State({"type": "mv-file", "index": MATCH}, "value"),
)
def update_level_slider(var_name, view_mode, file_path):
    if not (var_name and file_path and Path(file_path).is_file()):
        return 0, None, 0
    meta = inspect_nc(file_path)
    file_dims = meta.get("dims") or {}
    var_meta = next((v for v in meta.get("variables", []) if v.get("name") == var_name), None)
    if not var_meta:
        return 0, None, 0
    # Map per-variable dim names → sizes using file-level dim table.
    sizes = {d: int(file_dims.get(d, 0)) for d in var_meta.get("dims") or ()}
    count = _slice_count(sizes, view_mode)
    if count <= 1:
        return 0, None, 0
    step = max(1, (count - 1) // 6)
    marks = {i: str(i) for i in range(0, count, step)}
    return count - 1, marks, 0


# ─── Render the figure for a single cell ───
@callback(
    Output({"type": "mv-figure", "index": MATCH}, "figure"),
    Input({"type": "mv-var", "index": MATCH}, "value"),
    Input({"type": "mv-view", "index": MATCH}, "value"),
    Input({"type": "mv-time", "index": MATCH}, "value"),
    Input({"type": "mv-level", "index": MATCH}, "value"),
    State({"type": "mv-file", "index": MATCH}, "value"),
    State({"type": "mv-exp", "index": MATCH}, "value"),
)
def render_cell(var_name, view_mode, time_idx, level_idx, file_path, exp_id):
    if not (var_name and file_path and Path(file_path).is_file()):
        return _empty_fig("请选择试验、文件和变量")
    try:
        data, coords = load_variable_slice(
            filepath=file_path,
            var_name=var_name,
            view_mode=view_mode or "horizontal",
            time_idx=int(time_idx or 0),
            level_idx=int(level_idx or 0),
        )
    except Exception as exc:  # noqa: BLE001 — surface error inside figure
        return _empty_fig(f"加载失败：{exc}")

    data = np.asarray(data)
    if data.size == 0 or not np.any(np.isfinite(data)):
        return _empty_fig("All values non-finite")

    title_prefix = exp_id.split("__")[0] if exp_id else ""
    title = f"{title_prefix} · {var_name}" if title_prefix else var_name

    try:
        if view_mode == "zonal":
            fig = plot_lat_height(
                data,
                lat=coords.get("lat"),
                lev=coords.get("lev"),
                title=title,
                colorscale="Viridis",
            )
        elif view_mode == "meridional":
            fig = plot_lon_height(
                data,
                lon=coords.get("lon"),
                lev=coords.get("lev"),
                title=title,
                colorscale="Viridis",
            )
        else:
            fig = plot_map_2d(
                data,
                lat=coords.get("lat"),
                lon=coords.get("lon"),
                title=title,
                colorscale="Viridis",
                background="none",
            )
    except Exception as exc:  # noqa: BLE001
        return _empty_fig(f"Render failed: {exc}")

    fig.update_layout(
        margin={"l": 40, "r": 20, "t": 40, "b": 40},
        font={"size": 10},
    )
    return fig


# ─── Status line ───
@callback(
    Output("mv-status", "children"),
    Input("mv-cells-store", "data"),
)
def render_status(cells):
    n = len(cells or [])
    if n == 0:
        return "Empty canvas"
    return f"{n} cell{'s' if n != 1 else ''} · Ctrl/Cmd+scroll zooms plot · double-click card header to fullscreen"


# ─── Helpers ───
def _experiments_root(gmcore_root: str | None) -> Path:
    if gmcore_root:
        return Path(gmcore_root) / "tools" / "experiments" / "experiments"
    return Path(__file__).resolve().parents[3] / "tools" / "experiments" / "experiments"


def _nc_files_for(exp_id: str, gmcore_root: str | None) -> list[str]:
    root = _experiments_root(gmcore_root) / exp_id
    if not root.is_dir():
        return []
    return [str(p) for p in sorted(root.glob(f"{exp_id}.h0*.nc")) if p.is_file()]


def _is_plottable(variable_entry: dict[str, Any]) -> bool:
    dims = variable_entry.get("dims") or ()
    return any(d in {"lat", "lon", "lev", "nlat", "nlon", "nlev", "time"} for d in dims)


def _slice_count(sizes: dict[str, int], view_mode: str) -> int:
    if view_mode == "zonal":
        return int(sizes.get("lon", sizes.get("nlon", 0)))
    if view_mode == "meridional":
        return int(sizes.get("lat", sizes.get("nlat", 0)))
    return int(sizes.get("lev", sizes.get("nlev", 0)))


def _empty_fig(message: str) -> dict:
    return {
        "data": [],
        "layout": {
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "annotations": [
                {
                    "text": message,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 12, "color": "#7a8794"},
                }
            ],
            "margin": {"l": 20, "r": 20, "t": 20, "b": 20},
            "plot_bgcolor": "#f8f9fb",
        },
    }
