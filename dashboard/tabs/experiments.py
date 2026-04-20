"""Experiments tab layout and callbacks for the GMCORE Dashboard."""

from __future__ import annotations

import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import (
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    ctx,
    dash_table,
    dcc,
    html,
)
from dash.exceptions import PreventUpdate

from gmcore_dashboard.experiments.dashboard_backend import (
    load_compare,
    load_detail,
    load_sweep_family,
    newest_nc_for,
    scan_experiments,
)


CARD_CLASS = "border"
LOG_STYLE = {
    "backgroundColor": "#0a0a14",
    "border": "1px solid rgba(99, 102, 241, 0.14)",
    "borderRadius": "10px",
    "color": "#cbd5f5",
    "fontFamily": "'JetBrains Mono', 'Fira Code', monospace",
    "fontSize": "0.82rem",
    "lineHeight": "1.45",
    "margin": 0,
    "maxHeight": "360px",
    "minHeight": "360px",
    "overflowY": "auto",
    "padding": "0.9rem",
    "whiteSpace": "pre-wrap",
}
STATUS_COLORS = {
    "created": "secondary",
    "queued": "secondary",
    "running": "info",
    "completed": "success",
    "failed": "danger",
    "timeout": "warning",
    "cancelled": "secondary",
    "interrupted": "warning",
}
SWEEP_PARAM_OPTIONS = [
    {"label": "alpha_d", "value": "alpha_d"},
    {"label": "tau_thresh", "value": "tau_thresh"},
    {"label": "alpha_n", "value": "alpha_n"},
]
SWEEP_METRIC_OPTIONS = [
    {"label": "CDOD Peak Ratio", "value": "cdod610.peak_ratio"},
    {"label": "CDOD Annual Mean", "value": "cdod610.annual_mean"},
    {"label": "CDOD Primary Peak", "value": "cdod610.primary_peak.value"},
    {"label": "CDOD Secondary Peak", "value": "cdod610.secondary_peak.value"},
    {"label": "DDL Flux Integral", "value": "dust_lifting.ddl_flux_integral"},
    {"label": "WSL Flux Integral", "value": "dust_lifting.wsl_flux_integral"},
    {"label": "WSL / DDL Ratio", "value": "dust_lifting.wsl_to_ddl_ratio"},
]


def _resolve_root(path: Path | str) -> Path:
    return Path(path).expanduser().resolve()


def _default_experiments_root(gmcore_root: str | None) -> Path:
    if gmcore_root:
        return Path(gmcore_root).expanduser().resolve() / "tools" / "experiments" / "experiments"
    return Path(__file__).resolve().parents[3] / "tools" / "experiments" / "experiments"


def _experiments_root(gmcore_root: str | None, custom_root: str | None = None) -> Path:
    if custom_root and custom_root.strip():
        p = Path(custom_root.strip()).expanduser().resolve()
        if p.is_dir():
            return p
    return _default_experiments_root(gmcore_root)


def _status_color(status: str | None) -> str:
    return STATUS_COLORS.get(str(status or "").lower(), "secondary")


def _format_value(value: Any) -> str:
    if value in (None, ""):
        return "—"
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, list):
        return ", ".join(_format_value(item) for item in value)
    if isinstance(value, dict):
        return ", ".join(f"{key}={_format_value(val)}" for key, val in sorted(value.items()))
    return str(value)


def _flatten_metric_rows(data: Any, prefix: str = "") -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if isinstance(data, dict):
        for key, value in sorted(data.items()):
            label = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten_metric_rows(value, label))
        return rows
    rows.append({"metric": prefix or "value", "value": _format_value(data)})
    return rows


def _nested_get(data: dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for token in dotted_key.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(token)
    return current


def _empty_figure(message: str) -> go.Figure:
    figure = go.Figure()
    figure.update_layout(
        template="plotly_white",
        margin={"l": 20, "r": 20, "t": 60, "b": 40},
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 14},
            }
        ],
    )
    return figure


def _render_tags(tags: list[str] | None) -> list[Any]:
    if not tags:
        return [html.Span("无标签", className="text-muted small")]
    return [dbc.Badge(tag, color="light", text_color="dark", className="me-1") for tag in tags]


def _render_diag_grid(items: list[dict[str, Any]] | None) -> Any:
    diagnostics = items or []
    if not diagnostics:
        return dbc.Alert("No diagnostic PNGs are available for this experiment yet.", color="light", className="mb-0")

    cards = []
    for item in diagnostics:
        asset_path = item.get("asset_path")
        cards.append(
            dbc.Col(
                dbc.Card(
                    className=CARD_CLASS,
                    children=[
                        dbc.CardImg(src=asset_path, top=True) if asset_path else html.Div("图片缺失", className="p-4 text-muted"),
                        dbc.CardBody(
                            [
                                html.Div(item.get("name", "diagnostic"), className="small fw-semibold"),
                            ],
                            className="p-2",
                        ),
                    ],
                ),
                md=6,
                xl=4,
                className="mb-3",
            )
        )
    return dbc.Row(cards, className="g-3")


def _render_compare_grid(payload: dict[str, Any]) -> Any:
    pairs = payload.get("paired_diagnostics") or []
    detail_a = payload.get("a") or {}
    detail_b = payload.get("b") or {}
    title_a = detail_a.get("name", "Experiment A")
    title_b = detail_b.get("name", "Experiment B")

    if not pairs:
        return dbc.Alert("No paired diagnostics available for these experiments.", color="light", className="mb-0")

    rows = []
    for pair in pairs:
        item_a = pair.get("a")
        item_b = pair.get("b")
        rows.append(
            dbc.Row(
                className="g-3 mb-3",
                children=[
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardHeader(f"{pair.get('name', 'Diagnostic')} · {title_a}"),
                                dbc.CardBody(
                                    dbc.CardImg(src=item_a.get("asset_path"), top=True)
                                    if item_a and item_a.get("asset_path")
                                    else html.Div("诊断缺失", className="text-muted")
                                ),
                            ],
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardHeader(f"{pair.get('name', 'Diagnostic')} · {title_b}"),
                                dbc.CardBody(
                                    dbc.CardImg(src=item_b.get("asset_path"), top=True)
                                    if item_b and item_b.get("asset_path")
                                    else html.Div("诊断缺失", className="text-muted")
                                ),
                            ],
                        ),
                        md=6,
                    ),
                ],
            )
        )
    return html.Div(rows)


def _build_registry_filters() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader("Filters"),
            dbc.CardBody(
                [
                    dbc.Label("Search", html_for="exp-search", className="form-label-sm mb-1 fw-bold text-secondary"),
                    dbc.Input(id="exp-search", type="text", placeholder="Search experiments...", size="sm", className="mb-3"),
                    dbc.Label("Status", html_for="exp-status-filter", className="form-label-sm mb-1 fw-bold text-secondary"),
                    dcc.Dropdown(
                        id="exp-status-filter",
                        multi=True,
                        options=[
                            {"label": "Created", "value": "created"},
                            {"label": "Queued", "value": "queued"},
                            {"label": "Running", "value": "running"},
                            {"label": "Completed", "value": "completed"},
                            {"label": "Failed", "value": "failed"},
                            {"label": "Interrupted", "value": "interrupted"},
                        ],
                        placeholder="All statuses",
                        className="mb-3",
                    ),
                    dbc.Label("Tags", html_for="exp-tag-filter", className="form-label-sm mb-1 fw-bold text-secondary"),
                    dcc.Dropdown(
                        id="exp-tag-filter",
                        multi=True,
                        options=[],
                        placeholder="All tags",
                    ),
                ]
            ),
        ],
    )


def _build_table_card() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader("Experiments"),
            dbc.CardBody(
                className="p-0",
                children=[
                    dash_table.DataTable(
                        id="exp-table",
                        columns=[
                            {"name": "ID", "id": "experiment_id"},
                            {"name": "Name", "id": "name"},
                            {"name": "Status", "id": "status"},
                            {"name": "alpha_d", "id": "alpha_d"},
                            {"name": "tau_thresh", "id": "tau_thresh"},
                            {"name": "alpha_n", "id": "alpha_n"},
                            {"name": "Created", "id": "created_at"},
                            {"name": "Tags", "id": "tags"},
                        ],
                        hidden_columns=["experiment_id"],
                        data=[],
                        page_size=12,
                        row_selectable="single",
                        selected_rows=[],
                        sort_action="native",
                        filter_action="none",
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "padding": "0.5rem",
                            "fontSize": "0.82rem",
                            "textAlign": "left",
                            "whiteSpace": "normal",
                            "height": "auto",
                        },
                        style_header={"fontWeight": "bold"},
                    )
                ],
            ),
        ],
    )


def _build_actions_card() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader("Create / Run"),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            dbc.Badge("Idle", id="exp-run-status-badge", color="secondary", className="me-2"),
                            html.Span("已选试验状态", className="small text-secondary"),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        className="g-2",
                        children=[
                            dbc.Col(dbc.Button("Create", id="exp-create-btn", color="primary", className="w-100"), width=6),
                            dbc.Col(
                                dbc.Button(
                                    "Run Selected",
                                    id="exp-run-selected-btn",
                                    color="success",
                                    className="w-100",
                                    disabled=True,
                                ),
                                width=6,
                            ),
                        ],
                    ),
                ]
            ),
        ],
    )


def _build_detail_tab() -> dbc.Tab:
    return dbc.Tab(
        label="详情",
        tab_id="exp-detail-tab",
        children=[
            dbc.Row(
                className="g-3 mt-1",
                children=[
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            className="d-flex justify-content-between align-items-start flex-wrap gap-2",
                                            children=[
                                                html.Div(
                                                    [
                                                        html.H4("未选择试验", id="exp-detail-title", className="mb-2"),
                                                        html.Div(
                                                            [
                                                                dbc.Badge("Idle", id="exp-detail-status-badge", color="secondary", className="me-2"),
                                                                html.Span(id="exp-detail-tags"),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    className="d-flex gap-2",
                                                    children=[
                                                        dbc.Button(
                                                            "Open in Visualize",
                                                            id="exp-open-viz-btn",
                                                            color="secondary",
                                                            outline=True,
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Run",
                                                            id="exp-run-btn",
                                                            color="success",
                                                            disabled=True,
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        html.Hr(),
                                        html.Div(id="exp-meta-summary", className="small"),
                                    ]
                                )
                            ],
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardHeader("Parameters"),
                                dbc.CardBody(
                                    dash_table.DataTable(
                                        id="exp-param-table",
                                        columns=[
                                            {"name": "Parameter", "id": "parameter"},
                                            {"name": "Value", "id": "value"},
                                        ],
                                        data=[],
                                        page_action="none",
                                        style_table={"height": "320px", "overflowY": "auto"},
                                        style_cell={"textAlign": "left", "fontSize": "0.82rem", "padding": "0.4rem"},
                                    )
                                ),
                            ],
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardHeader("Metrics"),
                                dbc.CardBody(
                                    dash_table.DataTable(
                                        id="exp-metric-table",
                                        columns=[
                                            {"name": "Metric", "id": "metric"},
                                            {"name": "Value", "id": "value"},
                                        ],
                                        data=[],
                                        page_action="none",
                                        style_table={"height": "320px", "overflowY": "auto"},
                                        style_cell={"textAlign": "left", "fontSize": "0.82rem", "padding": "0.4rem"},
                                    )
                                ),
                            ],
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardHeader("Diagnostics"),
                                dbc.CardBody(html.Div(id="exp-diagnostic-grid")),
                            ],
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardHeader("Log"),
                                dbc.CardBody(
                                    [
                                        html.Pre(id="exp-log-console", style=LOG_STYLE),
                                        html.Div(id="exp-log-scroll-trigger", style={"display": "none"}),
                                    ]
                                ),
                            ],
                        ),
                        width=12,
                    ),
                ],
            )
        ],
    )


def _build_compare_tab() -> dbc.Tab:
    return dbc.Tab(
        label="对比分析",
        tab_id="exp-compare-tab",
        children=[
            dbc.Row(
                className="g-3 mt-1",
                children=[
                    dbc.Col(
                        [
                            dbc.Label("Experiment A", html_for="exp-compare-a", className="fw-bold text-secondary small"),
                            dcc.Dropdown(id="exp-compare-a", options=[], value=None, clearable=False),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Experiment B", html_for="exp-compare-b", className="fw-bold text-secondary small"),
                            dcc.Dropdown(id="exp-compare-b", options=[], value=None, clearable=False),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardHeader("Parameter Differences"),
                                dbc.CardBody(
                                    dash_table.DataTable(
                                        id="exp-compare-param-table",
                                        columns=[
                                            {"name": "Parameter", "id": "parameter"},
                                            {"name": "A", "id": "a"},
                                            {"name": "B", "id": "b"},
                                            {"name": "Status", "id": "status_text"},
                                            {"name": "Changed", "id": "changed"},
                                        ],
                                        hidden_columns=["changed"],
                                        data=[],
                                        page_action="none",
                                        style_table={"height": "280px", "overflowY": "auto"},
                                        style_cell={"textAlign": "left", "fontSize": "0.82rem", "padding": "0.4rem"},
                                        style_data_conditional=[],
                                    )
                                ),
                            ],
                        ),
                        width=12,
                    ),
                    dbc.Col(html.Div(id="exp-compare-grid"), width=12),
                ],
            )
        ],
    )


def _build_sweep_tab() -> dbc.Tab:
    return dbc.Tab(
        label="参数扫描",
        tab_id="exp-sweep-tab",
        children=[
            dbc.Row(
                className="g-3 mt-1",
                children=[
                    dbc.Col(
                        [
                            dbc.Label("Sweep Family", html_for="exp-sweep-family", className="fw-bold text-secondary small"),
                            dcc.Dropdown(id="exp-sweep-family", options=[], value=None, clearable=False),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("X Axis", html_for="exp-sweep-param", className="fw-bold text-secondary small"),
                            dcc.Dropdown(id="exp-sweep-param", options=SWEEP_PARAM_OPTIONS, value="alpha_d", clearable=False),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Metric", html_for="exp-sweep-metric", className="fw-bold text-secondary small"),
                            dcc.Dropdown(id="exp-sweep-metric", options=SWEEP_METRIC_OPTIONS, value="cdod610.peak_ratio", clearable=False),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            className=CARD_CLASS,
                            children=[
                                dbc.CardHeader("Sweep Trend"),
                                dbc.CardBody(dcc.Graph(id="exp-sweep-graph", figure=_empty_figure("Select a sweep family"))),
                            ],
                        ),
                        width=12,
                    ),
                ],
            )
        ],
    )


def _scan_templates() -> list[dict[str, str]]:
    tpl_dir = Path(__file__).resolve().parents[2] / "experiments" / "templates"
    if not tpl_dir.is_dir():
        return []
    options = []
    for f in sorted(tpl_dir.glob("*.nml")):
        label = f.stem.replace("_", " ").title()
        options.append({"label": f"{label}  ({f.name})", "value": f.as_posix()})
    return options


def _build_create_modal() -> dbc.Modal:
    template_options = _scan_templates()

    return dbc.Modal(
        id="exp-create-modal",
        is_open=False,
        size="lg",
        children=[
            dbc.ModalHeader(dbc.ModalTitle("Create Experiment"), close_button=False),
            dbc.ModalBody(
                [
                    dbc.Row(
                        className="g-3",
                        children=[
                            dbc.Col(
                                [
                                    dbc.Label(
                                        [html.I(className="bi bi-file-earmark-code me-1"), "Namelist Template"],
                                        html_for="exp-template-select",
                                    ),
                                    dcc.Dropdown(
                                        id="exp-template-select",
                                        options=template_options,
                                        value=template_options[0]["value"] if template_options else None,
                                        placeholder="Select template...",
                                        clearable=True,
                                    ),
                                    html.Div(
                                        id="exp-template-hint",
                                        className="small text-muted mt-1",
                                        children=f"{len(template_options)} templates available in tools/experiments/templates/",
                                    ),
                                ],
                                width=12,
                            ),
                            dbc.Col(
                                dbc.Collapse(
                                    dbc.Card(
                                        className="border",
                                        children=[
                                            dbc.CardHeader(
                                                [
                                                    html.Span(html.I(className="bi bi-eye"), className="ch-icon"),
                                                    html.Span("模板预览", className="ch-title"),
                                                ],
                                            ),
                                            dbc.CardBody(
                                                html.Pre(
                                                    id="exp-template-preview",
                                                    style={
                                                        "maxHeight": "200px",
                                                        "fontSize": "0.75rem",
                                                        "margin": 0,
                                                    },
                                                ),
                                            ),
                                        ],
                                    ),
                                    id="exp-template-preview-collapse",
                                    is_open=False,
                                ),
                                width=12,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Base Experiment", html_for="exp-base-select"),
                                    dcc.Dropdown(id="exp-base-select", options=[], value=None),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Experiment Name", html_for="exp-name-input"),
                                    dbc.Input(id="exp-name-input", type="text", placeholder="dust-tuning-run"),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("alpha_d", html_for="exp-alpha-d-input"),
                                    dbc.Input(id="exp-alpha-d-input", type="number", value=5.0e-11, step="any"),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("tau_thresh", html_for="exp-tau-thresh-input"),
                                    dbc.Input(id="exp-tau-thresh-input", type="number", value=0.04, step="any"),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("alpha_n", html_for="exp-alpha-n-input"),
                                    dbc.Input(id="exp-alpha-n-input", type="number", value=5.0e-5, step="any"),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("备注", html_for="exp-notes-input"),
                                    dbc.Textarea(id="exp-notes-input", placeholder="试验备注（选填）", style={"minHeight": "120px"}),
                                ],
                                width=12,
                            ),
                        ],
                    )
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Cancel", id="exp-create-cancel", color="secondary", outline=True),
                    dbc.Button("Create", id="exp-create-submit", color="primary"),
                    dbc.Button("Create + Run", id="exp-create-run-submit", color="success"),
                    dbc.Button("Close", id="exp-create-close", color="secondary", className="d-none"),
                ]
            ),
        ],
    )


def _build_settings_strip(default_root: str) -> dbc.Card:
    return dbc.Card(
        className="border mb-3",
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-gear"), className="ch-icon"),
                    html.Span(
                        [
                            "Experiments Directory",
                            html.Span("跨会话持久化", className="ch-subtitle"),
                        ],
                        className="ch-title",
                    ),
                    html.Span(
                        [html.I(className="bi bi-check2"), " Applied"],
                        id="exp-dir-applied-badge",
                        className="badge bg-success ch-actions",
                        style={"display": "none"},
                    ),
                ]
            ),
            dbc.CardBody(
                dbc.Row(
                    className="g-2 align-items-end",
                    children=[
                        dbc.Col(
                            [
                                dbc.Label(
                                    [html.I(className="bi bi-folder2 me-1"), "Root Path"],
                                    html_for="exp-custom-root-input",
                                    className="form-label-sm mb-1 fw-bold text-secondary",
                                ),
                                dbc.Input(
                                    id="exp-custom-root-input",
                                    type="text",
                                    value=default_root,
                                    placeholder=default_root,
                                    size="sm",
                                    className="font-monospace",
                                    style={"fontSize": "var(--fs-sm)"},
                                ),
                                html.Div(
                                    id="exp-dir-status",
                                    className="small text-muted mt-1",
                                    style={"fontSize": "var(--fs-xs)"},
                                ),
                            ],
                            md=8, lg=9,
                        ),
                        dbc.Col(
                            dbc.Button(
                                [html.I(className="bi bi-check-lg me-1"), "Apply"],
                                id="exp-apply-dir-btn",
                                color="primary",
                                size="sm",
                                className="w-100",
                            ),
                            md=2, lg=1,
                        ),
                        dbc.Col(
                            dbc.Button(
                                [html.I(className="bi bi-arrow-counterclockwise me-1"), "Reset"],
                                id="exp-reset-dir-btn",
                                color="secondary",
                                outline=True,
                                size="sm",
                                className="w-100",
                            ),
                            md=2, lg=2,
                        ),
                    ],
                ),
            ),
        ],
    )


def create_layout(gmcore_root: Path, testbed_root: Path) -> dbc.Container:
    resolved_gmcore_root = _resolve_root(gmcore_root)
    resolved_testbed_root = _resolve_root(testbed_root)
    default_exp_root = _default_experiments_root(resolved_gmcore_root.as_posix()).as_posix()

    return dbc.Container(
        fluid=True,
        className="py-2",
        children=[
            dcc.Store(id="exp-gmcore-root", data=resolved_gmcore_root.as_posix()),
            dcc.Store(id="exp-testbed-root", data=resolved_testbed_root.as_posix()),
            dcc.Store(id="exp-default-root", data=default_exp_root),
            dcc.Store(id="exp-registry-store", data=[]),
            dcc.Store(id="exp-selected-exp-store"),
            dcc.Store(id="exp-compare-store", data={}),
            dcc.Store(id="exp-run-store", data={"status": "idle", "message": "Idle"}),
            dcc.Interval(id="exp-poll-interval", interval=2000, n_intervals=0),
            dbc.Alert(id="exp-action-feedback", is_open=False, color="secondary", className="glass mb-3"),
            _build_settings_strip(default_exp_root),
            _build_create_modal(),
            dbc.Row(
                className="g-3",
                children=[
                    dbc.Col(
                        [
                            _build_registry_filters(),
                            dbc.Alert(
                                [
                                    html.H5("暂无试验", className="alert-heading"),
                                    html.P("创建首个试验以开始参数调优。", className="mb-3"),
                                    dbc.Button("Create First Experiment", id="exp-empty-create-btn", color="primary"),
                                ],
                                id="exp-empty-state",
                                color="light",
                                is_open=False,
                                className="mb-3",
                            ),
                            html.Div(
                                id="exp-table-shell",
                                children=[
                                    _build_table_card(),
                                    _build_actions_card(),
                                ],
                                className="d-flex flex-column gap-3",
                            ),
                        ],
                        width=12,
                        lg=4,
                        xl=3,
                        className="d-flex flex-column gap-3",
                    ),
                    dbc.Col(
                        dbc.Tabs(
                            id="exp-view-tabs",
                            active_tab="exp-detail-tab",
                            children=[
                                _build_detail_tab(),
                                _build_compare_tab(),
                                _build_sweep_tab(),
                            ],
                        ),
                        width=12,
                        lg=8,
                        xl=9,
                    ),
                ],
            ),
        ],
    )


def _build_create_command(cli_path: Path, payload: dict[str, Any]) -> list[str]:
    command = [sys.executable, cli_path.as_posix(), "create", payload["name"]]
    if payload.get("base"):
        command.extend(["--base", str(payload["base"])])
    for key in ("alpha_d", "tau_thresh", "alpha_n"):
        if payload.get(key) not in (None, ""):
            command.extend(["--set", f"{key}={payload[key]}"])
    if payload.get("notes"):
        command.extend(["--description", str(payload["notes"])])
    return command


def _run_create_and_maybe_launch(gmcore_root: str, payload: dict[str, Any], run_after_create: bool) -> None:
    cli_path = Path(gmcore_root).expanduser().resolve() / "tools" / "experiments" / "cli.py"
    if not cli_path.is_file():
        return
    create_cmd = _build_create_command(cli_path, payload)
    result = subprocess.run(create_cmd, cwd=Path(gmcore_root).as_posix(), capture_output=True, text=True)
    if result.returncode != 0 or not run_after_create:
        return
    created_id = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    if not created_id:
        return
    subprocess.run(
        [sys.executable, cli_path.as_posix(), "run", created_id],
        cwd=Path(gmcore_root).as_posix(),
        capture_output=True,
        text=True,
    )


def _run_existing_experiment(gmcore_root: str, experiment_id: str) -> None:
    cli_path = Path(gmcore_root).expanduser().resolve() / "tools" / "experiments" / "cli.py"
    if not cli_path.is_file():
        return
    subprocess.run(
        [sys.executable, cli_path.as_posix(), "run", experiment_id],
        cwd=Path(gmcore_root).as_posix(),
        capture_output=True,
        text=True,
    )


# ── Settings strip callbacks ──────────────────────────────────────────

@callback(
    Output("exp-template-preview", "children"),
    Output("exp-template-preview-collapse", "is_open"),
    Input("exp-template-select", "value"),
    prevent_initial_call=True,
)
def preview_template(template_path: str | None):
    if not template_path:
        return "", False
    p = Path(template_path)
    if not p.is_file():
        return f"Template file not found: {template_path}", True
    content = p.read_text(encoding="utf-8")
    return content, True


@callback(
    Output("exp-custom-root", "data"),
    Output("exp-custom-root-input", "value"),
    Output("exp-dir-status", "children"),
    Output("exp-dir-applied-badge", "style"),
    Input("exp-apply-dir-btn", "n_clicks"),
    Input("exp-reset-dir-btn", "n_clicks"),
    State("exp-custom-root-input", "value"),
    State("exp-default-root", "data"),
    prevent_initial_call=True,
)
def apply_or_reset_dir(
    _apply: int | None,
    _reset: int | None,
    input_value: str | None,
    default_root: str | None,
):
    triggered = ctx.triggered_id
    if triggered == "exp-reset-dir-btn":
        return default_root or "", default_root or "", f"Reset to default: {default_root}", {"display": "none"}

    path_str = (input_value or "").strip()
    if not path_str:
        return no_update, no_update, "Path cannot be empty.", {"display": "none"}

    p = Path(path_str).expanduser().resolve()
    if not p.is_dir():
        try:
            p.mkdir(parents=True, exist_ok=True)
            msg = f"Created and applied: {p.as_posix()}"
        except OSError as exc:
            return no_update, no_update, f"Cannot create directory: {exc}", {"display": "none"}
    else:
        msg = f"Applied: {p.as_posix()}"

    is_default = p.as_posix() == (default_root or "")
    badge_style = {"display": "none"} if is_default else {}
    return p.as_posix(), p.as_posix(), msg, badge_style


@callback(
    Output("exp-registry-store", "data"),
    Output("exp-tag-filter", "options"),
    Output("exp-compare-a", "options"),
    Output("exp-compare-b", "options"),
    Output("exp-sweep-family", "options"),
    Output("exp-base-select", "options"),
    Output("exp-empty-state", "is_open"),
    Output("exp-table-shell", "style"),
    Input("exp-poll-interval", "n_intervals"),
    State("exp-gmcore-root", "data"),
    State("exp-custom-root", "data"),
)
def refresh_registry(_n_intervals: int, gmcore_root: str | None, custom_root: str | None = None):
    registry = scan_experiments(_experiments_root(gmcore_root, custom_root))
    tags = sorted({tag for item in registry for tag in (item.get("tags") or [])})
    tag_options = [{"label": tag, "value": tag} for tag in tags]
    exp_options = [{"label": item.get("name", item.get("experiment_id")), "value": item.get("experiment_id")} for item in registry]
    sweep_ids = sorted({item.get("sweep_id") for item in registry if item.get("sweep_id")})
    sweep_options = [{"label": sweep_id, "value": sweep_id} for sweep_id in sweep_ids]
    is_empty = len(registry) == 0
    return (
        registry,
        tag_options,
        exp_options,
        exp_options,
        sweep_options,
        exp_options,
        is_empty,
        {"display": "none"} if is_empty else {"display": "block"},
    )


@callback(
    Output("exp-table", "data"),
    Input("exp-search", "value"),
    Input("exp-status-filter", "value"),
    Input("exp-tag-filter", "value"),
    Input("exp-registry-store", "data"),
)
def filter_table(
    search_value: str | None,
    status_values: list[str] | str | None,
    tag_values: list[str] | str | None,
    registry: list[dict[str, Any]] | None,
):
    items = registry or []
    search_text = (search_value or "").strip().lower()
    statuses = status_values if isinstance(status_values, list) else ([status_values] if status_values else [])
    tags = tag_values if isinstance(tag_values, list) else ([tag_values] if tag_values else [])

    filtered = []
    for item in items:
        name = str(item.get("name", ""))
        status = str(item.get("status", ""))
        item_tags = [str(tag) for tag in (item.get("tags") or [])]
        haystack = " ".join([name, status, item.get("baseline") or "", " ".join(item_tags)]).lower()

        if search_text and search_text not in haystack:
            continue
        if statuses and status not in statuses:
            continue
        if tags and not set(tags).intersection(item_tags):
            continue

        filtered.append(
            {
                "experiment_id": item.get("experiment_id"),
                "name": name,
                "status": status,
                "alpha_d": _format_value(item.get("alpha_d")),
                "tau_thresh": _format_value(item.get("tau_thresh")),
                "alpha_n": _format_value(item.get("alpha_n")),
                "created_at": item.get("created_at", ""),
                "tags": ", ".join(item_tags),
            }
        )
    return filtered


@callback(
    Output("exp-selected-exp-store", "data"),
    Input("exp-table", "selected_rows"),
    Input("exp-table", "data"),
)
def select_experiment(selected_rows: list[int] | None, table_data: list[dict[str, Any]] | None):
    rows = table_data or []
    if not rows:
        return None
    if selected_rows:
        index = min(selected_rows[0], len(rows) - 1)
        return rows[index].get("experiment_id")
    return rows[0].get("experiment_id")


@callback(
    Output("exp-detail-title", "children"),
    Output("exp-detail-status-badge", "children"),
    Output("exp-detail-status-badge", "color"),
    Output("exp-detail-tags", "children"),
    Output("exp-meta-summary", "children"),
    Output("exp-param-table", "data"),
    Output("exp-metric-table", "data"),
    Output("exp-diagnostic-grid", "children"),
    Output("exp-log-console", "children"),
    Output("exp-open-viz-btn", "disabled"),
    Output("exp-run-btn", "disabled"),
    Output("exp-run-selected-btn", "disabled"),
    Output("exp-run-status-badge", "children"),
    Output("exp-run-status-badge", "color"),
    Input("exp-selected-exp-store", "data"),
    State("exp-gmcore-root", "data"),
    State("exp-custom-root", "data"),
)
def render_detail(selected_experiment_id: str | None, gmcore_root: str | None, custom_root: str | None = None):
    if not selected_experiment_id:
        return (
            "未选择试验",
            "Idle",
            "secondary",
            [html.Span("从列表中选择一个试验", className="text-muted small")],
            [html.Div("无可用元数据。", className="text-muted")],
            [],
            [],
            dbc.Alert("Select an experiment to view diagnostics.", color="light", className="mb-0"),
            "",
            True,
            True,
            True,
            "Idle",
            "secondary",
        )

    detail = load_detail(selected_experiment_id, _experiments_root(gmcore_root, custom_root))
    if not detail:
        return (
            "Experiment not found",
            "Missing",
            "warning",
            [html.Span("记录不可用", className="text-muted small")],
            [html.Div("Experiment detail could not be loaded.", className="text-muted")],
            [],
            [],
            dbc.Alert("No diagnostics available.", color="light", className="mb-0"),
            "",
            True,
            True,
            True,
            "Missing",
            "warning",
        )

    metadata = detail.get("metadata", {})
    params = detail.get("params", {})
    metrics = detail.get("metrics", {})
    nc_path = newest_nc_for(selected_experiment_id, _experiments_root(gmcore_root, custom_root))
    status = str(detail.get("status", "created"))
    meta_summary = [
        html.Div(f"Baseline: {_format_value(detail.get('baseline'))}", className="mb-1"),
        html.Div(f"Created: {_format_value(detail.get('created_at'))}", className="mb-1"),
        html.Div(f"Updated: {_format_value(detail.get('updated_at'))}", className="mb-1"),
        html.Div(f"Sweep: {_format_value(detail.get('sweep_id'))}", className="mb-1"),
        html.Div(f"Directory: {_format_value(metadata.get('paths', {}).get('experiment_dir'))}", className="mb-0"),
    ]
    param_rows = [{"parameter": key, "value": _format_value(value)} for key, value in sorted(params.items())]
    metric_rows = _flatten_metric_rows(metrics)
    return (
        detail.get("name", selected_experiment_id),
        status.replace("_", " ").title(),
        _status_color(status),
        _render_tags(detail.get("tags")),
        meta_summary,
        param_rows,
        metric_rows,
        _render_diag_grid(detail.get("diagnostics")),
        detail.get("log_tail") or "No log output captured yet.",
        nc_path is None,
        False,
        False,
        status.replace("_", " ").title(),
        _status_color(status),
    )


@callback(
    Output("main-tabs", "active_tab", allow_duplicate=True),
    Output("viz-preview-request", "data", allow_duplicate=True),
    Input("exp-open-viz-btn", "n_clicks"),
    State("exp-selected-exp-store", "data"),
    State("exp-gmcore-root", "data"),
    State("exp-custom-root", "data"),
    prevent_initial_call=True,
)
def open_in_visualize(_n_clicks: int | None, selected_experiment_id: str | None, gmcore_root: str | None, custom_root: str | None = None):
    if not selected_experiment_id:
        raise PreventUpdate
    nc_path = newest_nc_for(selected_experiment_id, _experiments_root(gmcore_root, custom_root))
    if nc_path is None:
        raise PreventUpdate
    return "visualize", {"file_path": nc_path.as_posix(), "requested_at": datetime.now().isoformat()}


@callback(
    Output("exp-create-modal", "is_open"),
    Input("exp-create-btn", "n_clicks"),
    Input("exp-empty-create-btn", "n_clicks"),
    Input("exp-create-cancel", "n_clicks"),
    Input("exp-create-close", "n_clicks"),
    Input("exp-create-submit", "n_clicks"),
    Input("exp-create-run-submit", "n_clicks"),
    State("exp-create-modal", "is_open"),
    prevent_initial_call=True,
)
def create_experiment_modal(
    _open_clicks: int | None,
    _empty_open_clicks: int | None,
    _cancel_clicks: int | None,
    _close_clicks: int | None,
    _create_clicks: int | None,
    _create_run_clicks: int | None,
    is_open: bool,
):
    triggered = ctx.triggered_id
    if triggered in {"exp-create-btn", "exp-empty-create-btn"}:
        return True
    return False


@callback(
    Output("exp-action-feedback", "children"),
    Output("exp-action-feedback", "color"),
    Output("exp-action-feedback", "is_open"),
    Output("exp-run-store", "data"),
    Input("exp-create-submit", "n_clicks"),
    Input("exp-create-run-submit", "n_clicks"),
    Input("exp-run-selected-btn", "n_clicks"),
    Input("exp-run-btn", "n_clicks"),
    State("exp-base-select", "value"),
    State("exp-name-input", "value"),
    State("exp-alpha-d-input", "value"),
    State("exp-tau-thresh-input", "value"),
    State("exp-alpha-n-input", "value"),
    State("exp-notes-input", "value"),
    State("exp-selected-exp-store", "data"),
    State("exp-gmcore-root", "data"),
    prevent_initial_call=True,
)
def submit_experiment_actions(
    _create_clicks: int | None,
    _create_run_clicks: int | None,
    _run_selected_clicks: int | None,
    _run_detail_clicks: int | None,
    base_experiment: str | None,
    experiment_name: str | None,
    alpha_d: float | None,
    tau_thresh: float | None,
    alpha_n: float | None,
    notes: str | None,
    selected_experiment_id: str | None,
    gmcore_root: str | None,
):
    if not gmcore_root:
        return "GMCORE root is not configured.", "danger", True, {"status": "error", "message": "Missing GMCORE root"}

    cli_path = Path(gmcore_root).expanduser().resolve() / "tools" / "experiments" / "cli.py"
    if not cli_path.is_file():
        return (
            "Experiment CLI is not available (tools/experiments/cli.py missing).",
            "danger",
            True,
            {"status": "error", "message": "Missing tools/experiments/cli.py"},
        )

    triggered = ctx.triggered_id
    if triggered in {"exp-create-submit", "exp-create-run-submit"}:
        if not experiment_name:
            return "Enter an experiment name before submitting.", "warning", True, {"status": "invalid", "message": "Missing experiment name"}
        payload = {
            "base": base_experiment,
            "name": experiment_name,
            "alpha_d": alpha_d,
            "tau_thresh": tau_thresh,
            "alpha_n": alpha_n,
            "notes": notes,
        }
        run_after_create = triggered == "exp-create-run-submit"
        threading.Thread(
            target=_run_create_and_maybe_launch,
            args=(gmcore_root, payload, run_after_create),
            daemon=True,
            name=f"exp-create-{experiment_name}",
        ).start()
        message = f"Submitted create request for {experiment_name}."
        if run_after_create:
            message = f"Submitted create + run request for {experiment_name}."
        return message, "info", True, {"status": "submitted", "message": message, "experiment": experiment_name}

    if triggered in {"exp-run-selected-btn", "exp-run-btn"}:
        if not selected_experiment_id:
            return "Select an experiment before launching a run.", "warning", True, {"status": "invalid", "message": "未选择试验"}
        threading.Thread(
            target=_run_existing_experiment,
            args=(gmcore_root, selected_experiment_id),
            daemon=True,
            name=f"exp-run-{selected_experiment_id}",
        ).start()
        message = f"Submitted run request for {selected_experiment_id}."
        return message, "success", True, {"status": "submitted", "message": message, "experiment": selected_experiment_id}

    raise PreventUpdate


@callback(
    Output("exp-compare-store", "data"),
    Input("exp-compare-a", "value"),
    Input("exp-compare-b", "value"),
)
def sync_compare_store(compare_a: str | None, compare_b: str | None):
    return {"a": compare_a, "b": compare_b}


@callback(
    Output("exp-compare-param-table", "data"),
    Output("exp-compare-param-table", "style_data_conditional"),
    Output("exp-compare-grid", "children"),
    Input("exp-compare-a", "value"),
    Input("exp-compare-b", "value"),
    State("exp-registry-store", "data"),
    State("exp-gmcore-root", "data"),
    State("exp-custom-root", "data"),
)
def compare_render(
    compare_a: str | None,
    compare_b: str | None,
    registry: list[dict[str, Any]] | None,
    gmcore_root: str | None,
    custom_root: str | None = None,
):
    items = registry or []
    if not items:
        return [], [], dbc.Alert("No experiments available for comparison.", color="light", className="mb-0")

    resolved_a = compare_a or items[0].get("experiment_id")
    resolved_b = compare_b
    if not resolved_b and len(items) > 1:
        resolved_b = items[1].get("experiment_id")
    if not resolved_a or not resolved_b:
        return [], [], dbc.Alert("Select two experiments to compare.", color="light", className="mb-0")

    payload = load_compare(resolved_a, resolved_b, _experiments_root(gmcore_root, custom_root))
    styles = [
        {
            "if": {"filter_query": '{changed} = "yes"'},
            "backgroundColor": "rgba(255, 193, 7, 0.18)",
        }
    ]
    return payload.get("param_rows", []), styles, _render_compare_grid(payload)


@callback(
    Output("exp-sweep-family", "value"),
    Input("exp-sweep-family", "options"),
    State("exp-sweep-family", "value"),
)
def default_sweep_family(options: list[dict[str, str]] | None, current_value: str | None):
    values = [option["value"] for option in (options or [])]
    if current_value in values:
        return current_value
    return values[0] if values else None


@callback(
    Output("exp-sweep-graph", "figure"),
    Input("exp-sweep-family", "value"),
    Input("exp-sweep-param", "value"),
    Input("exp-sweep-metric", "value"),
    State("exp-gmcore-root", "data"),
    State("exp-custom-root", "data"),
)
def sweep_render(
    sweep_id: str | None,
    param_name: str | None,
    metric_name: str | None,
    gmcore_root: str | None,
    custom_root: str | None = None,
):
    if not sweep_id or not param_name or not metric_name:
        return _empty_figure("Select a sweep family")

    records = load_sweep_family(sweep_id, _experiments_root(gmcore_root, custom_root))
    if not records:
        return _empty_figure("No sweep experiments found")

    plot_rows = []
    for record in records:
        x_value = record.get(param_name)
        y_value = _nested_get(record.get("metrics", {}), metric_name)
        if x_value in (None, "") or y_value in (None, ""):
            continue
        plot_rows.append((float(x_value), float(y_value), record))

    if not plot_rows:
        return _empty_figure("Selected sweep family has no metric values yet")

    plot_rows.sort(key=lambda item: item[0])
    figure = go.Figure(
        data=[
            go.Scatter(
                x=[item[0] for item in plot_rows],
                y=[item[1] for item in plot_rows],
                mode="lines+markers",
                text=[item[2].get("name", item[2].get("experiment_id")) for item in plot_rows],
                marker={"size": 10, "color": "#2c7fb8"},
                line={"color": "#2c7fb8", "width": 2},
                hovertemplate="%{text}<br>x=%{x}<br>y=%{y}<extra></extra>",
            )
        ]
    )
    figure.update_layout(
        template="plotly_white",
        margin={"l": 40, "r": 20, "t": 40, "b": 40},
        xaxis_title=param_name,
        yaxis_title=metric_name,
    )
    return figure


clientside_callback(
    """
    function(content) {
        const node = document.getElementById("exp-log-console");
        if (node) {
            node.scrollTop = node.scrollHeight;
        }
        return "";
    }
    """,
    Output("exp-log-scroll-trigger", "children"),
    Input("exp-log-console", "children"),
)


__all__ = ["create_layout"]
