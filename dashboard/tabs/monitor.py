"""Live monitor tab layout and callbacks for the GMCORE Dashboard."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, clientside_callback, ctx, dcc, html
from dash.exceptions import PreventUpdate

from gmcore_dashboard.dashboard.job_manager import JobManager
from gmcore_dashboard.dashboard.log_parser import LogParser
from gmcore_dashboard.dashboard.scanner import scan_testbed
from gmcore_dashboard.dashboard.tabs.build_run import _get_job_manager


CARD_CLASS = "border"
CONSOLE_STYLE = {
    "backgroundColor": "#0a0a14",
    "border": "1px solid rgba(99, 102, 241, 0.14)",
    "borderRadius": "10px",
    "color": "#a0ffa0",
    "fontFamily": "'JetBrains Mono', 'Fira Code', monospace",
    "fontSize": "0.78rem",
    "lineHeight": "1.45",
    "margin": 0,
    "maxHeight": "500px",
    "minHeight": "500px",
    "overflowY": "auto",
    "padding": "0.9rem",
    "whiteSpace": "pre-wrap",
}
FILE_META_STYLE = {"fontFamily": "'JetBrains Mono', 'Fira Code', monospace", "fontSize": "0.76rem"}


def create_layout(gmcore_root: str, testbed_root: str) -> dbc.Container:
    """Create the live monitor tab layout."""
    resolved_gmcore_root = _resolve_root(gmcore_root)
    resolved_testbed_root = _resolve_root(testbed_root)
    _get_job_manager(resolved_gmcore_root)
    testbed_data = scan_testbed(resolved_testbed_root)

    return dbc.Container(
        fluid=True,
        className="py-3",
        children=[
            dcc.Store(id="mon-gmcore-root", data=resolved_gmcore_root),
            dcc.Store(id="mon-testbed-root", data=resolved_testbed_root),
            dcc.Store(id="mon-testbed-data", data=testbed_data),
            dcc.Store(id="mon-active-job"),
            dcc.Store(id="mon-log-offset"),
            dcc.Interval(id="mon-interval", interval=2000, n_intervals=0),
            html.Div(id="mon-scroll-trigger", style={"display": "none"}),
            _build_status_bar(),
            dbc.Row(
                className="g-3 mt-1",
                children=[
                    dbc.Col(_build_log_console_card(), width=8),
                    dbc.Col(
                        [
                            _build_progress_card(),
                            _build_output_files_card(),
                            _build_system_info_card(),
                        ],
                        width=4,
                    ),
                ],
            ),
        ],
    )


def _build_status_bar() -> dbc.Card:
    return dbc.Card(
        className=f"{CARD_CLASS} card-accent",
        children=[
            dbc.CardBody(
                dbc.Row(
                    className="g-3 align-items-center",
                    children=[
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.I(className="bi bi-broadcast"),
                                        html.Span("Active Job"),
                                    ],
                                    className="stat-tile-label d-inline-flex align-items-center gap-1 mb-1",
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            "No active job selected",
                                            id="mon-job-name",
                                            className="fw-semibold me-2",
                                            style={"fontSize": "var(--fs-lg)", "color": "var(--text-1)"},
                                        ),
                                        dbc.Badge(
                                            "Idle",
                                            id="mon-status-badge",
                                            color="secondary",
                                            pill=True,
                                        ),
                                    ],
                                    className="d-flex align-items-center flex-wrap gap-2",
                                ),
                            ],
                            md=7,
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    [
                                        html.I(className="bi bi-clock-history me-1"),
                                        "Job History",
                                    ],
                                    html_for="mon-job-select",
                                    className="mb-1",
                                ),
                                dcc.Dropdown(
                                    id="mon-job-select",
                                    options=[],
                                    value=None,
                                    placeholder="No jobs available",
                                    clearable=False,
                                ),
                            ],
                            md=5,
                        ),
                    ],
                )
            )
        ],
    )


def _build_log_console_card() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-terminal"), className="ch-icon"),
                    html.Span("Log Console", className="ch-title"),
                    html.Span(
                        [
                            html.I(className="bi bi-arrow-repeat me-1"),
                            "Live tail",
                        ],
                        className="badge bg-secondary ch-actions",
                    ),
                ]
            ),
            dbc.CardBody(
                [
                    html.Div(
                        className="log-chrome",
                        children=[
                            html.Span(className="lc-dot"),
                            html.Span(className="lc-dot"),
                            html.Span(className="lc-dot"),
                            html.Span("gmcore.run.log", className="lc-title"),
                        ],
                    ),
                    html.Pre(id="mon-log-console", style=CONSOLE_STYLE, children=""),
                    dbc.Row(
                        className="g-2 mt-3",
                        children=[
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="bi bi-trash3 me-2"), "Clear Log"],
                                    id="mon-clear-btn",
                                    color="secondary",
                                    className="w-100",
                                ),
                                sm=6,
                            ),
                            dbc.Col(
                                dcc.Clipboard(
                                    content=None,
                                    children=[html.I(className="bi bi-clipboard me-2"), "Copy to Clipboard"],
                                    id="mon-copy-btn",
                                    target_id="mon-log-console",
                                    title="Copy monitor log output",
                                    className="btn btn-outline-info w-100",
                                ),
                                sm=6,
                            ),
                        ],
                    ),
                ]
            ),
        ],
    )


def _build_progress_card() -> dbc.Card:
    return dbc.Card(
        className=f"{CARD_CLASS} mb-3",
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-bar-chart-steps"), className="ch-icon"),
                    html.Span("Progress", className="ch-title"),
                ]
            ),
            dbc.CardBody(
                [
                    dbc.Progress(
                        id="mon-progress",
                        value=0,
                        label="0%",
                        animated=False,
                        striped=False,
                        color="info",
                        className="mb-3",
                    ),
                    html.Div(
                        className="stat-grid",
                        children=[
                            html.Div(
                                className="stat-tile",
                                children=[
                                    html.Div(
                                        [html.I(className="bi bi-stopwatch"), html.Span("Elapsed")],
                                        className="stat-tile-label",
                                    ),
                                    html.Div(
                                        "—",
                                        id="mon-elapsed",
                                        className="stat-tile-value stat-tile-value--mono",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="stat-tile",
                                children=[
                                    html.Div(
                                        [html.I(className="bi bi-hourglass-split"), html.Span("ETA")],
                                        className="stat-tile-label",
                                    ),
                                    html.Div(
                                        "—",
                                        id="mon-eta",
                                        className="stat-tile-value stat-tile-value--mono",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="mt-3 pt-3",
                        style={"borderTop": "1px solid var(--border)"},
                        children=[
                            html.Div(
                                [html.I(className="bi bi-flag me-1"), html.Span("Current Step")],
                                className="stat-tile-label mb-1",
                            ),
                            html.Div(
                                "Awaiting progress markers",
                                id="mon-current-step",
                                className="fw-semibold",
                                style={"fontSize": "var(--fs-md)", "color": "var(--text-1)"},
                            ),
                        ],
                    ),
                ]
            ),
        ],
    )


def _build_output_files_card() -> dbc.Card:
    return dbc.Card(
        className=f"{CARD_CLASS} mb-3",
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-file-earmark-binary"), className="ch-icon"),
                    html.Span("Output Files", className="ch-title"),
                ]
            ),
            dbc.CardBody(id="mon-output-files"),
        ],
    )


def _build_system_info_card() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-info-circle"), className="ch-icon"),
                    html.Span("System Info", className="ch-title"),
                ]
            ),
            dbc.CardBody(id="mon-system-info"),
        ],
    )


def _resolve_root(root: str) -> str:
    return Path(root).expanduser().resolve().as_posix()


def _pick_job_id(
    jobs: list[dict[str, object]],
    preferred_job_id: str | None,
) -> str | None:
    job_ids = {str(job["job_id"]) for job in jobs}
    if preferred_job_id and preferred_job_id in job_ids:
        return preferred_job_id

    running_job = next((job for job in jobs if job.get("status") == "running"), None)
    if running_job is not None:
        return str(running_job["job_id"])

    if jobs:
        return str(jobs[0]["job_id"])

    return None


def _job_options(jobs: list[dict[str, object]]) -> list[dict[str, str]]:
    options: list[dict[str, str]] = []
    for job in jobs:
        job_id = str(job["job_id"])
        label = str(job.get("label") or "Unnamed job")
        status = str(job.get("status") or "unknown").replace("_", " ").title()
        options.append({"label": f"{job_id} · {label} · {status}", "value": job_id})
    return options


def _status_badge_props(status: str) -> tuple[str, str, str]:
    colors = {
        "running": "info",
        "completed": "success",
        "failed": "danger",
        "idle": "secondary",
        "not_found": "secondary",
    }
    badge_text = status.replace("_", " ").title()
    class_name = "status-running" if status == "running" else ""
    return badge_text, colors.get(status, "secondary"), class_name


def _coerce_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


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
    testbed_data: dict[str, list[dict[str, Any]]] | None,
    case_name: str | None,
) -> dict[str, Any] | None:
    if not case_name:
        return None
    for case_info in _iter_cases(testbed_data):
        if case_info.get("name") == case_name:
            return case_info
    return None


def _status_metadata(status: dict[str, Any]) -> dict[str, Any]:
    metadata = status.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _status_case_name(status: dict[str, Any]) -> str | None:
    metadata = _status_metadata(status)
    case_name = metadata.get("case_name")
    if isinstance(case_name, str) and case_name:
        return case_name

    label = str(status.get("label") or "")
    if label.startswith("Run: "):
        return label.split("Run: ", 1)[1].strip() or None
    return None


def _status_nprocs(status: dict[str, Any]) -> str:
    nprocs = _status_metadata(status).get("nprocs")
    if nprocs in (None, ""):
        return "—"
    return str(nprocs)


def _format_timestamp(epoch_seconds: object) -> str:
    try:
        return datetime.fromtimestamp(float(epoch_seconds)).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError, OSError):
        return "—"


def _format_filesize(size_bytes: int) -> str:
    size = float(max(size_bytes, 0))
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def _format_duration(seconds: object) -> str:
    try:
        total_seconds = max(0, int(float(seconds or 0)))
    except (TypeError, ValueError):
        total_seconds = 0
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _build_progress_details(
    status: dict[str, Any],
    log_lines: list[str],
    testbed_data: dict[str, list[dict[str, Any]]] | None,
) -> tuple[float, str, bool, bool, str, str, str]:
    case_name = _status_case_name(status)
    case_info = _find_case_info(testbed_data, case_name)
    config = case_info.get("config") if isinstance(case_info, dict) else {}
    total_days = _coerce_float((config or {}).get("run_days"))
    total_hours = _coerce_float((config or {}).get("run_hours"))

    parser = LogParser(total_days=total_days, total_hours=total_hours)
    start_time = status.get("start_time")
    try:
        if start_time:
            parser.start_time = datetime.fromtimestamp(float(start_time))
    except (TypeError, ValueError, OSError):
        parser.start_time = None

    for line in log_lines:
        parser.parse_line(line)

    progress = parser.get_progress()
    percent = float(progress["percent"])
    current_step = str(progress["current_step_str"])

    if total_days > 0:
        if parser.current_day > 0:
            current_step = f"Day {parser.current_day:.0f} / {total_days:g}"
        else:
            current_step = f"Run target: {total_days:g} days"
    elif total_hours > 0:
        if parser.current_hour > 0:
            current_step = f"Hour {parser.current_hour:.1f} / {total_hours:g}"
        else:
            current_step = f"Run target: {total_hours:g} hours"
    elif case_name:
        current_step = current_step if current_step != "Hour 0.0" else f"Monitoring {case_name}"
    else:
        current_step = "Awaiting progress markers"

    status_value = str(status.get("status") or "idle")
    if status_value == "completed" and _status_metadata(status).get("kind") == "run":
        percent = 100.0
        if current_step in {"Awaiting progress markers", "Hour 0.0"}:
            current_step = "Run completed"

    if status_value != "running":
        elapsed_str = _format_duration(status.get("elapsed"))
        eta_str = "00:00:00" if status_value == "completed" and percent >= 100 else "—"
    else:
        elapsed_str = str(progress["elapsed_str"])
        eta_str = str(progress["eta_str"])

    return (
        percent,
        f"{percent:.1f}%",
        status_value == "running",
        status_value == "running",
        elapsed_str,
        eta_str,
        current_step,
    )


def _render_output_files(status: dict[str, Any]) -> Any:
    metadata = _status_metadata(status)
    if metadata.get("kind") != "run":
        return html.Div(
            "Output files are shown for case run jobs only.",
            className="small text-muted",
        )

    case_dir = metadata.get("work_dir") or status.get("cwd")
    if not case_dir:
        return html.Div("No case working directory available for this job.", className="small text-muted")

    root = Path(str(case_dir))
    if not root.is_dir():
        return html.Div("Working directory is not available on disk.", className="small text-muted")

    nc_files = [
        path
        for path in sorted(root.glob("*.nc"), key=lambda item: item.stat().st_mtime, reverse=True)
        if path.is_file()
    ]
    if not nc_files:
        return html.Div("No NetCDF outputs found yet.", className="small text-muted")

    items: list[Any] = []
    for path in nc_files:
        stat = path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        items.append(
            dbc.ListGroupItem(
                className="bg-transparent text-light border-secondary",
                children=dbc.Row(
                    className="g-2 align-items-center",
                    children=[
                        dbc.Col(
                            [
                                html.Div(path.name, className="fw-semibold"),
                                html.Div(
                                    f"{_format_filesize(stat.st_size)} · {modified}",
                                    className="text-secondary",
                                    style=FILE_META_STYLE,
                                ),
                            ],
                            width=8,
                        ),
                        dbc.Col(
                            dbc.Button(
                                [html.I(className="bi bi-eye me-1"), "Preview"],
                                id={"type": "mon-preview-btn", "path": path.as_posix()},
                                color="secondary",
                                outline=True,
                                size="sm",
                                className="w-100",
                            ),
                            width=4,
                        ),
                    ],
                ),
            )
        )
    return dbc.ListGroup(items, flush=True)


def _render_system_info(status: dict[str, Any]) -> list[Any]:
    case_name = _status_case_name(status) or "—"
    pid = str(status.get("pid") or "—")
    nprocs = _status_nprocs(status)
    started = _format_timestamp(status.get("start_time"))

    def _tile(label: str, value: str, *, mono: bool = True, title: str | None = None) -> html.Div:
        value_class = "stat-tile-value" + (" stat-tile-value--mono" if mono else "")
        return html.Div(
            [
                html.Div(label, className="stat-tile-label"),
                html.Div(value, className=value_class, title=title or value),
            ],
            className="stat-tile",
        )

    return [
        html.Div(
            className="stat-grid",
            children=[
                _tile("PID", pid),
                _tile("nprocs", nprocs),
            ],
        ),
        html.Div(
            className="mt-2",
            children=[
                _tile("Case", case_name, title=case_name),
            ],
        ),
        html.Div(
            className="mt-2",
            children=[
                _tile("Started", started),
            ],
        ),
    ]


def _update_console_text(
    manager: JobManager,
    job_id: str | None,
    current_text: str | None,
    log_offset: object,
    *,
    reload_all: bool,
    clear_display: bool,
) -> tuple[str, int]:
    if not job_id:
        return "", 0

    total_count = manager.get_log_count(job_id)
    if clear_display:
        return "", total_count

    recent_lines = manager.get_logs(job_id, last_n=200)
    if reload_all or log_offset in (None, ""):
        return "\n".join(recent_lines), total_count

    try:
        current_offset = max(0, int(log_offset))
    except (TypeError, ValueError):
        current_offset = 0

    if total_count <= current_offset:
        return current_text or "", current_offset

    base_index = max(0, total_count - len(recent_lines))
    start_index = max(current_offset, base_index)
    relative_start = max(0, start_index - base_index)
    new_lines = recent_lines[relative_start:]

    if not new_lines:
        return current_text or "", total_count

    segments: list[str] = []
    existing_text = current_text or ""
    if existing_text:
        segments.append(existing_text)

    if existing_text and current_offset < base_index:
        segments.append(f"[... {base_index - current_offset} earlier lines omitted ...]")

    segments.append("\n".join(new_lines))
    return "\n".join(segment for segment in segments if segment), total_count


@callback(
    Output("mon-job-select", "options"),
    Output("mon-job-select", "value"),
    Input("mon-interval", "n_intervals"),
    State("mon-active-job", "data"),
    State("mon-gmcore-root", "data"),
    State("mon-job-select", "value"),
)
def refresh_job_selector(
    _n_intervals: int,
    active_job_id: str | None,
    gmcore_root: str | None,
    current_selection: str | None,
):
    if not gmcore_root:
        return [], None

    manager = _get_job_manager(gmcore_root)
    jobs = manager.list_jobs()
    selected_job_id = _pick_job_id(jobs, active_job_id or current_selection)
    return _job_options(jobs), selected_job_id


@callback(
    Output("mon-job-name", "children"),
    Output("mon-status-badge", "children"),
    Output("mon-status-badge", "color"),
    Output("mon-status-badge", "className"),
    Output("mon-log-console", "children"),
    Output("mon-log-offset", "data"),
    Output("mon-progress", "value"),
    Output("mon-progress", "label"),
    Output("mon-progress", "animated"),
    Output("mon-progress", "striped"),
    Output("mon-elapsed", "children"),
    Output("mon-eta", "children"),
    Output("mon-current-step", "children"),
    Output("mon-output-files", "children"),
    Output("mon-system-info", "children"),
    Output("mon-active-job", "data"),
    Input("mon-interval", "n_intervals"),
    Input("mon-job-select", "value"),
    Input("mon-clear-btn", "n_clicks"),
    State("mon-gmcore-root", "data"),
    State("mon-testbed-data", "data"),
    State("mon-active-job", "data"),
    State("mon-log-offset", "data"),
    State("mon-log-console", "children"),
)
def refresh_monitor(
    _n_intervals: int,
    selected_job_id: str | None,
    _clear_clicks: int | None,
    gmcore_root: str | None,
    testbed_data: dict[str, list[dict[str, Any]]] | None,
    current_active_job_id: str | None,
    log_offset: object,
    current_console: str | None,
):
    if not gmcore_root:
        badge_text, badge_color, badge_class = _status_badge_props("idle")
        return (
            "GMCORE root is not configured",
            badge_text,
            badge_color,
            badge_class,
            "",
            0,
            0,
            "0%",
            False,
            False,
            "—",
            "—",
            "Awaiting progress markers",
            html.Div("No job output is available.", className="small text-muted"),
            _render_system_info({"pid": None, "start_time": None, "label": "", "metadata": {}}),
            None,
        )

    manager = _get_job_manager(gmcore_root)
    jobs = manager.list_jobs()
    active_job_id = _pick_job_id(jobs, selected_job_id or current_active_job_id)
    if not active_job_id:
        badge_text, badge_color, badge_class = _status_badge_props("idle")
        return (
            "No jobs recorded yet",
            badge_text,
            badge_color,
            badge_class,
            "",
            0,
            0,
            "0%",
            False,
            False,
            "—",
            "—",
            "Awaiting progress markers",
            html.Div("No NetCDF outputs to display.", className="small text-muted"),
            _render_system_info({"pid": None, "start_time": None, "label": "", "metadata": {}}),
            None,
        )

    status = manager.get_status(active_job_id)
    status_value = str(status.get("status") or "idle")
    badge_text, badge_color, badge_class = _status_badge_props(status_value)
    reload_all = (
        ctx.triggered_id == "mon-job-select" and active_job_id != current_active_job_id
    ) or current_active_job_id != active_job_id
    clear_display = ctx.triggered_id == "mon-clear-btn"
    console_text, new_offset = _update_console_text(
        manager,
        active_job_id,
        current_console,
        log_offset,
        reload_all=reload_all,
        clear_display=clear_display,
    )
    recent_lines = manager.get_logs(active_job_id, last_n=200)
    (
        progress_value,
        progress_label,
        progress_animated,
        progress_striped,
        elapsed_str,
        eta_str,
        current_step,
    ) = _build_progress_details(status, recent_lines, testbed_data)

    job_name = f"{status.get('label') or 'Unnamed job'} ({active_job_id})"
    return (
        job_name,
        badge_text,
        badge_color,
        badge_class,
        console_text,
        new_offset,
        progress_value,
        progress_label,
        progress_animated,
        progress_striped,
        elapsed_str,
        eta_str,
        current_step,
        _render_output_files(status),
        _render_system_info(status),
        active_job_id,
    )


@callback(
    Output("main-tabs", "active_tab", allow_duplicate=True),
    Output("viz-preview-request", "data", allow_duplicate=True),
    Input({"type": "mon-preview-btn", "path": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def preview_output_file(_clicks: list[int | None]):
    if not ctx.triggered or not ctx.triggered[0].get("value"):
        raise PreventUpdate

    if not isinstance(ctx.triggered_id, dict):
        raise PreventUpdate

    file_path = ctx.triggered_id.get("path")
    if not isinstance(file_path, str) or not file_path:
        raise PreventUpdate

    return "visualize", {"file_path": file_path, "requested_at": datetime.now().isoformat()}


clientside_callback(
    """
    function(children) {
        var el = document.getElementById('mon-log-console');
        if (el) el.scrollTop = el.scrollHeight;
        return '';
    }
    """,
    Output("mon-scroll-trigger", "children"),
    Input("mon-log-console", "children"),
)


__all__ = ["create_layout"]
