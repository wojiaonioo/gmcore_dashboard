"""Build and run tab layout and callbacks for the GMCORE Dashboard."""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, clientside_callback, ctx, dcc, html
from dash.exceptions import PreventUpdate

from gmcore_dashboard.dashboard.job_manager import JobManager
from gmcore_dashboard.dashboard.scanner import scan_testbed


CARD_CLASS = "border"
BUILD_JOB_LABELS = {"Build", "Clean", "Configure"}
TERMINAL_STYLE = {
    "backgroundColor": "#0a0a14",
    "border": "1px solid rgba(99, 102, 241, 0.14)",
    "borderRadius": "10px",
    "color": "#cbd5f5",
    "fontFamily": "'JetBrains Mono', 'Fira Code', monospace",
    "fontSize": "0.82rem",
    "lineHeight": "1.45",
    "margin": 0,
    "maxHeight": "400px",
    "overflowY": "auto",
    "padding": "0.9rem",
    "whiteSpace": "pre-wrap",
}
BUILD_LOG_STYLE = {
    **TERMINAL_STYLE,
    "maxHeight": "300px",
}
_JOB_MANAGERS: dict[str, JobManager] = {}
_JOB_MANAGERS_LOCK = threading.Lock()


def create_layout(gmcore_root: str, testbed_root: str) -> dbc.Container:
    """Create the Build & Run tab layout."""
    resolved_gmcore_root = _resolve_root(gmcore_root)
    resolved_testbed_root = _resolve_root(testbed_root)
    _get_job_manager(resolved_gmcore_root)
    testbed_data = scan_testbed(resolved_testbed_root)

    return dbc.Container(
        fluid=True,
        className="py-2",
        children=[
            dcc.Store(id="br-build-run-gmcore-root", data=resolved_gmcore_root),
            dcc.Store(id="br-build-run-testbed-root", data=resolved_testbed_root),
            dcc.Store(id="br-build-run-active-job"),
            dcc.Interval(id="br-job-interval", interval=2000, n_intervals=0),
            html.Div(id="br-run-log-scroll", style={"display": "none"}),
            html.Div(id="br-build-log-scroll", style={"display": "none"}),
            dbc.Alert(
                id="br-action-feedback",
                is_open=False,
                color="secondary",
                className="glass mb-3",
            ),
            dbc.Row(
                className="g-3",
                children=[
                    # Left Sidebar: Controls
                    dbc.Col(
                        [
                            _build_configuration_card(),
                            _build_run_configuration_card(testbed_data, resolved_testbed_root),
                            _build_quick_actions_card(),
                        ],
                        width=12, lg=4, xl=3,
                        className="d-flex flex-column gap-3",
                    ),
                    # Right Main Area: Status and Logs
                    dbc.Col(
                        [
                            _build_job_status_card(),
                            _build_log_viewer_card(),
                        ],
                        width=12, lg=8, xl=9,
                        className="d-flex flex-column gap-3",
                    ),
                ],
            ),
        ],
    )


def _build_configuration_card() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-hammer"), className="ch-icon"),
                    html.Span("编译配置", className="ch-title"),
                ]
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        className="g-2",
                        children=[
                            dbc.Col(
                                [
                                    dbc.Label("构建类型", html_for="br-build-type", className="form-label-sm mb-1 fw-bold text-secondary"),
                                    dbc.RadioItems(
                                        id="br-build-type",
                                        options=[
                                            {"label": "Release", "value": "Release"},
                                            {"label": "Debug", "value": "Debug"},
                                        ],
                                        value="Release",
                                        inline=True,
                                        className="form-control-sm border-0 bg-transparent px-0",
                                    ),
                                ],
                                width=12,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("精度", html_for="br-build-precision", className="form-label-sm mb-1 fw-bold text-secondary"),
                                    dbc.Select(
                                        id="br-build-precision",
                                        options=[
                                            {"label": "R4（单精度）", "value": "R4"},
                                            {"label": "R8（双精度）", "value": "R8"},
                                            {"label": "R16（四倍精度）", "value": "R16"},
                                        ],
                                        value="R8",
                                        size="sm",
                                    ),
                                ],
                                width=12,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label(
                                        "附加 CMake 参数",
                                        html_for="br-build-extra-cmake",
                                        className="form-label-sm mb-1 fw-bold text-secondary",
                                    ),
                                    dbc.Input(
                                        id="br-build-extra-cmake",
                                        type="text",
                                        placeholder="-DENABLE_FEATURE=ON",
                                        size="sm",
                                    ),
                                ],
                                width=12,
                            ),
                        ],
                    ),
                    dbc.Row(
                        className="g-2 mt-2",
                        children=[
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="bi bi-hammer me-2"), "Build"],
                                    id="br-build-btn",
                                    color="primary",
                                    className="w-100 fw-medium",
                                    size="sm",
                                ),
                                width=6,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="bi bi-eraser me-2"), "Clean"],
                                    id="br-build-clean-btn",
                                    color="warning",
                                    className="w-100 fw-medium",
                                    size="sm",
                                ),
                                width=6,
                            ),
                        ],
                    ),
                    dbc.Collapse(
                        id="br-build-log-collapse",
                        is_open=False,
                        className="mt-3",
                        children=html.Pre(id="br-build-log", style=BUILD_LOG_STYLE),
                    ),
                ]
            ),
        ],
    )


def _build_run_configuration_card(
    testbed_data: dict[str, list[dict[str, object]]],
    testbed_root: str,
) -> dbc.Card:
    options = _build_case_options(testbed_data)
    helper_text = (
        f"正在扫描算例目录： {Path(testbed_root).as_posix()}"
        if options
        else f"未找到可运行算例： {Path(testbed_root).as_posix()}"
    )

    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-rocket-takeoff"), className="ch-icon"),
                    html.Span("运行配置", className="ch-title"),
                ]
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        className="g-2",
                        children=[
                            dbc.Col(
                                [
                                    dbc.Label("算例选择", className="form-label-sm mb-1 fw-bold text-secondary"),
                                    html.Div(
                                        className="d-flex gap-2 mb-2",
                                        children=[
                                            dbc.Button(
                                                "全选",
                                                id="br-select-all-btn",
                                                color="secondary",
                                                outline=True,
                                                size="sm",
                                                className="py-0 px-2"
                                            ),
                                            dbc.Button(
                                                "取消全选",
                                                id="br-deselect-all-btn",
                                                color="secondary",
                                                outline=True,
                                                size="sm",
                                                className="py-0 px-2"
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={
                                            "maxHeight": "140px",
                                            "overflowY": "auto",
                                            "border": "1px solid #dce3eb",
                                            "borderRadius": "4px",
                                            "padding": "4px 8px",
                                            "backgroundColor": "#fafbfc",
                                        },
                                        children=dbc.Checklist(
                                            id="br-run-case-select",
                                            options=options,
                                            value=[],
                                            className="case-checklist",
                                            style={"fontSize": "0.80rem"},
                                        ),
                                    ),
                                    dbc.FormText(helper_text, color="secondary", style={"fontSize": "0.7rem", "display": "block", "marginTop": "4px"}),
                                ],
                                width=12,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("MPI 进程数", html_for="br-run-nprocs", className="form-label-sm mb-1 fw-bold text-secondary"),
                                    dbc.Input(
                                        id="br-run-nprocs",
                                        type="number",
                                        min=1,
                                        max=128,
                                        step=1,
                                        value=2,
                                        size="sm",
                                    ),
                                ],
                                width=12,
                            ),
                            dbc.Col(
                                [
                                    dcc.Slider(
                                        id="br-run-nprocs-slider",
                                        min=1,
                                        max=32,
                                        step=1,
                                        value=2,
                                        marks={
                                            1: "1",
                                            2: "2",
                                            4: "4",
                                            8: "8",
                                            16: "16",
                                            32: "32",
                                        },
                                        tooltip={"placement": "bottom"},
                                        className="py-1"
                                    ),
                                ],
                                width=12,
                            ),
                        ],
                    ),
                    dbc.Row(
                        className="g-2 mt-2",
                        children=[
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="bi bi-play-fill me-1"), "Run"],
                                    id="br-run-btn",
                                    color="success",
                                    className="w-100 fw-medium",
                                    size="sm",
                                ),
                                width=6,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="bi bi-stop-fill me-2"), "终止"],
                                    id="br-run-stop-btn",
                                    color="danger",
                                    className="w-100 fw-medium",
                                    disabled=True,
                                    size="sm",
                                ),
                                width=6,
                            ),
                        ],
                    ),
                ]
            ),
        ],
    )


def _build_quick_actions_card() -> dbc.Card:
    return dbc.Card(
        className=f"{CARD_CLASS} h-100",
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-lightning-charge"), className="ch-icon"),
                    html.Span("快捷操作", className="ch-title"),
                ]
            ),
            dbc.CardBody(
                className="p-3",
                children=[
                    dbc.Button(
                        [html.I(className="bi bi-lightning-charge-fill me-2"), "Build + Run Selected Case"],
                        id="br-quick-run-btn",
                        color="info",
                        className="w-100 fw-semibold text-white shadow-sm",
                        style={"backgroundColor": "#3498db", "borderColor": "#3498db"}
                    )
                ],
            ),
        ],
    )


def _build_job_status_card() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-list-task"), className="ch-icon"),
                    html.Span("作业状态", className="ch-title"),
                ]
            ),
            dbc.CardBody(
                className="p-0 border-top",
                children=[
                    html.Div(
                        style={
                            "maxHeight": "280px",
                            "overflowY": "auto",
                        },
                        children=[
                            dbc.Table(
                                id="br-job-table",
                                bordered=False,
                                hover=True,
                                responsive=True,
                                size="sm",
                                className="align-middle mb-0 text-dark",
                                children=[
                                    html.Thead(
                                        html.Tr(
                                            [
                                                html.Th("ID", style={"paddingLeft": "1rem"}),
                                                html.Th("Label"),
                                                html.Th("Status"),
                                                html.Th("Elapsed"),
                                                html.Th("Actions", className="text-end", style={"paddingRight": "1rem"}),
                                            ],
                                            className="table-light"
                                        )
                                    ),
                                    html.Tbody(id="br-job-table-body"),
                                ],
                            )
                        ]
                    )
                ]
            ),
        ],
    )


def _build_log_viewer_card() -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader(
                [
                    html.Span(html.I(className="bi bi-terminal"), className="ch-icon"),
                    html.Span("日志查看器", className="ch-title"),
                ]
            ),
            dbc.CardBody(
                className="p-0 border-top",
                children=[
                    html.Pre(
                        id="br-run-log",
                        style={**TERMINAL_STYLE, "border": "none", "borderRadius": "0", "margin": 0, "maxHeight": "400px", "height": "400px"},
                        children="Waiting for build or run activity...",
                    )
                ]
            ),
        ],
    )


def _resolve_root(root: str) -> str:
    return Path(root).expanduser().resolve().as_posix()


def _get_job_manager(gmcore_root: str) -> JobManager:
    resolved_root = _resolve_root(gmcore_root)
    with _JOB_MANAGERS_LOCK:
        manager = _JOB_MANAGERS.get(resolved_root)
        if manager is None:
            manager = JobManager(resolved_root)
            _JOB_MANAGERS[resolved_root] = manager
    return manager


def _build_case_options(
    testbed_data: dict[str, list[dict[str, object]]]
) -> list[dict[str, object]]:
    options: list[dict[str, object]] = []

    for category in sorted(testbed_data):
        cases = sorted(
            testbed_data[category],
            key=lambda case: str(case.get("name", "")),
        )
        for case in cases:
            case_name = str(case.get("name", ""))
            options.append({"label": case_name, "value": case_name})

    return options


def _all_case_values(
    testbed_data: dict[str, list[dict[str, object]]]
) -> list[str]:
    return [opt["value"] for opt in _build_case_options(testbed_data)]


def _compose_cmake_args(precision: str | None, extra_args: str | None) -> str:
    precision_flags = {
        "R4": "-DR4=ON -DR16=OFF",
        "R8": "-DR4=OFF -DR16=OFF",
        "R16": "-DR4=OFF -DR16=ON",
    }
    parts = [precision_flags.get(precision or "R8", precision_flags["R8"])]
    if extra_args and extra_args.strip():
        parts.append(extra_args.strip())
    return " ".join(parts)


def _wait_for_job_completion(manager: JobManager, job_id: str) -> dict[str, object]:
    while True:
        status = manager.get_status(job_id)
        if status["status"] != "running":
            return status
        time.sleep(0.25)


def _continue_build_after_configure(manager: JobManager, configure_job_id: str) -> None:
    configure_status = _wait_for_job_completion(manager, configure_job_id)
    if configure_status["status"] == "completed":
        manager.build()


def _run_clean_build(manager: JobManager) -> None:
    configure_job_id = manager.clean_build()
    _continue_build_after_configure(manager, configure_job_id)


def _run_quick_build_and_run(
    manager: JobManager,
    case_name: str,
    nprocs: int,
    build_type: str,
) -> None:
    manager.build_and_run(case_name, nprocs=nprocs, build_type=build_type)


def _run_multiple_cases(
    manager: JobManager,
    case_names: list[str],
    nprocs: int,
) -> None:
    """Run multiple cases sequentially, waiting for each to finish."""
    for case_name in case_names:
        try:
            job_id = manager.run_case(case_name, nprocs=nprocs)
            _wait_for_job_completion(manager, job_id)
        except Exception:
            _LOGGER.exception("Failed to run case %r", case_name)


def _quick_run_multiple_cases(
    manager: JobManager,
    case_names: list[str],
    nprocs: int,
    build_type: str,
) -> None:
    """Build once, then run multiple cases sequentially."""
    try:
        cmake_args = _compose_cmake_args(None, None)
        configure_job_id = manager.configure(build_type=build_type, extra_cmake_args=cmake_args)
        configure_status = _wait_for_job_completion(manager, configure_job_id)
        if configure_status["status"] != "completed":
            _LOGGER.warning("Configure step did not complete: %s", configure_status.get("status"))
            return
        build_job_id = manager.build()
        build_status = _wait_for_job_completion(manager, build_job_id)
        if build_status["status"] != "completed":
            _LOGGER.warning("Build step did not complete: %s", build_status.get("status"))
            return
    except Exception:
        _LOGGER.exception("Quick build failed before running cases")
        return
    _run_multiple_cases(manager, case_names, nprocs)


def _coerce_nprocs(value: object, upper: int = 128) -> int:
    try:
        coerced = int(value)
    except (TypeError, ValueError):
        return 1
    return max(1, min(upper, coerced))


def _latest_running_job(jobs: list[dict[str, object]]) -> dict[str, object] | None:
    return next((job for job in jobs if job["status"] == "running"), None)


def _latest_build_job(jobs: list[dict[str, object]]) -> dict[str, object] | None:
    running_build = next(
        (
            job
            for job in jobs
            if job["label"] in BUILD_JOB_LABELS and job["status"] == "running"
        ),
        None,
    )
    if running_build is not None:
        return running_build

    return next((job for job in jobs if job["label"] in BUILD_JOB_LABELS), None)


def _build_jobs_running(jobs: list[dict[str, object]]) -> bool:
    return any(
        job["label"] in BUILD_JOB_LABELS and job["status"] == "running" for job in jobs
    )


def _pick_active_job_id(
    jobs: list[dict[str, object]],
    current_active_job_id: str | None,
) -> str | None:
    job_ids = {str(job["job_id"]) for job in jobs}
    if current_active_job_id and current_active_job_id in job_ids:
        return current_active_job_id

    latest_running = _latest_running_job(jobs)
    if latest_running is not None:
        return str(latest_running["job_id"])

    if jobs:
        return str(jobs[0]["job_id"])

    return None


def _format_elapsed(seconds: object) -> str:
    total_seconds = max(0, int(float(seconds or 0)))
    minutes, secs = divmod(total_seconds, 60)
    hours, mins = divmod(minutes, 60)

    if hours:
        return f"{hours:d}h {mins:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes:d}m {secs:02d}s"
    return f"{secs:d}s"


def _status_badge(status: str) -> dbc.Badge:
    colors = {
        "running": "info",
        "completed": "success",
        "failed": "danger",
    }
    class_name = "status-running" if status == "running" else ""
    return dbc.Badge(
        status.replace("_", " ").title(),
        color=colors.get(status, "secondary"),
        pill=True,
        className=class_name,
    )


def _render_job_table(
    jobs: list[dict[str, object]],
    active_job_id: str | None,
) -> list[html.Tr]:
    if not jobs:
        return [
            html.Tr(
                [
                    html.Td(
                        "No jobs yet. Build or run a case to populate the queue.",
                        colSpan=5,
                        className="text-secondary fst-italic py-3",
                    )
                ]
            )
        ]

    rows: list[html.Tr] = []
    for job in jobs:
        job_id = str(job["job_id"])
        is_active = job_id == active_job_id
        actions = [
            dbc.Button(
                "View",
                id={"type": "br-job-view", "job_id": job_id},
                size="sm",
                color="secondary",
                outline=not is_active,
            )
        ]
        if is_active:
            actions.append(
                dbc.Badge("Selected", color="light", text_color="dark", className="ms-2")
            )

        rows.append(
            html.Tr(
                [
                    html.Td(html.Code(job_id)),
                    html.Td(str(job["label"])),
                    html.Td(_status_badge(str(job["status"]))),
                    html.Td(_format_elapsed(job["elapsed"])),
                    html.Td(html.Div(actions, className="d-flex justify-content-end align-items-center")),
                ]
            )
        )

    return rows


def _render_job_log(
    manager: JobManager,
    job_id: str | None,
    empty_message: str,
) -> str:
    if not job_id:
        return empty_message

    status = manager.get_status(job_id)
    lines = manager.get_logs(job_id, last_n=0)
    header = [
        f"$ job {status['job_id']} [{status['label']}]",
        f"status={status['status']} elapsed={_format_elapsed(status['elapsed'])}",
        "",
    ]
    if not lines:
        header.append("No log output captured yet.")
        return "\n".join(header)

    return "\n".join(header + lines)


@callback(
    Output("br-action-feedback", "children"),
    Output("br-action-feedback", "color"),
    Output("br-action-feedback", "is_open"),
    Output("br-build-run-active-job", "data", allow_duplicate=True),
    Input("br-build-btn", "n_clicks"),
    Input("br-build-clean-btn", "n_clicks"),
    Input("br-run-btn", "n_clicks"),
    Input("br-run-stop-btn", "n_clicks"),
    Input("br-quick-run-btn", "n_clicks"),
    State("br-build-type", "value"),
    State("br-build-precision", "value"),
    State("br-build-extra-cmake", "value"),
    State("br-run-case-select", "value"),
    State("br-run-nprocs", "value"),
    State("br-build-run-gmcore-root", "data"),
    prevent_initial_call=True,
)
def handle_actions(
    _build_clicks: int | None,
    _clean_clicks: int | None,
    _run_clicks: int | None,
    _stop_clicks: int | None,
    _quick_clicks: int | None,
    build_type: str | None,
    precision: str | None,
    extra_cmake_args: str | None,
    selected_cases: list[str] | None,
    nprocs: int | None,
    gmcore_root: str | None,
):
    if not gmcore_root:
        return "GMCORE root is not configured.", "danger", True, None

    manager = _get_job_manager(gmcore_root)
    jobs = manager.list_jobs()
    triggered_id = ctx.triggered_id

    cases = selected_cases or []

    if triggered_id == "br-build-btn":
        if _build_jobs_running(jobs):
            return "A configure/build job is already running.", "warning", True, None

        cmake_args = _compose_cmake_args(precision, extra_cmake_args)
        try:
            configure_job_id = manager.configure(
                build_type=build_type or "Release",
                extra_cmake_args=cmake_args,
            )
        except Exception as exc:
            return f"Build failed to start: {exc}", "danger", True, None

        threading.Thread(
            target=_continue_build_after_configure,
            args=(manager, configure_job_id),
            daemon=True,
            name=f"br-build-{configure_job_id}",
        ).start()
        return (
            f"Started configure + build pipeline from job {configure_job_id}.",
            "info",
            True,
            configure_job_id,
        )

    if triggered_id == "br-build-clean-btn":
        if _build_jobs_running(jobs):
            return "A configure/build job is already running.", "warning", True, None

        threading.Thread(
            target=_run_clean_build,
            args=(manager,),
            daemon=True,
            name="br-clean-build",
        ).start()
        return (
            "Started clean + rebuild pipeline.",
            "warning",
            True,
            None,
        )

    if triggered_id == "br-run-btn":
        if not cases:
            return "Select at least one case before starting a run.", "warning", True, None

        nprocs_value = _coerce_nprocs(nprocs)
        if len(cases) == 1:
            try:
                job_id = manager.run_case(cases[0], nprocs=nprocs_value)
            except Exception as exc:
                return f"Run failed to start: {exc}", "danger", True, None
            return (
                f"Started {cases[0]} with {nprocs_value} MPI processes.",
                "success",
                True,
                job_id,
            )
        else:
            threading.Thread(
                target=_run_multiple_cases,
                args=(manager, cases, nprocs_value),
                daemon=True,
                name="br-multi-run",
            ).start()
            return (
                f"Queued {len(cases)} cases to run sequentially.",
                "success",
                True,
                None,
            )

    if triggered_id == "br-run-stop-btn":
        running_job = _latest_running_job(jobs)
        if running_job is None:
            return "No running job to stop.", "secondary", True, None

        stopped = manager.stop(str(running_job["job_id"]))
        if not stopped:
            return "Failed to stop the latest running job.", "danger", True, None

        return (
            f"Stopped job {running_job['job_id']} ({running_job['label']}).",
            "danger",
            True,
            str(running_job["job_id"]),
        )

    if triggered_id == "br-quick-run-btn":
        if _build_jobs_running(jobs):
            return (
                "A configure/build job is already running. Wait for it before quick run.",
                "warning",
                True,
                None,
            )
        if not cases:
            return "Select at least one case before starting a quick run.", "warning", True, None

        if len(cases) == 1:
            threading.Thread(
                target=_run_quick_build_and_run,
                args=(
                    manager,
                    cases[0],
                    _coerce_nprocs(nprocs),
                    build_type or "Release",
                ),
                daemon=True,
                name="br-quick-run",
            ).start()
            return (
                f"Started build + run pipeline for {cases[0]}.",
                "info",
                True,
                None,
            )
        else:
            threading.Thread(
                target=_quick_run_multiple_cases,
                args=(
                    manager,
                    cases,
                    _coerce_nprocs(nprocs),
                    build_type or "Release",
                ),
                daemon=True,
                name="br-quick-multi-run",
            ).start()
            return (
                f"Started build + run pipeline for {len(cases)} cases.",
                "info",
                True,
                None,
            )

    raise PreventUpdate


@callback(
    Output("br-run-case-select", "value"),
    Input("br-select-all-btn", "n_clicks"),
    Input("br-deselect-all-btn", "n_clicks"),
    State("br-build-run-testbed-root", "data"),
    prevent_initial_call=True,
)
def handle_select_all(
    _select_all: int | None,
    _deselect_all: int | None,
    testbed_root: str | None,
):
    if not testbed_root:
        return []
    triggered_id = ctx.triggered_id
    if triggered_id == "br-select-all-btn":
        testbed_data = scan_testbed(testbed_root)
        return _all_case_values(testbed_data)
    return []


@callback(
    Output("br-run-nprocs", "value"),
    Output("br-run-nprocs-slider", "value"),
    Input("br-run-nprocs", "value"),
    Input("br-run-nprocs-slider", "value"),
    prevent_initial_call=True,
)
def sync_nprocs(
    input_value: int | None,
    slider_value: int | None,
):
    triggered_id = ctx.triggered_id

    if triggered_id == "br-run-nprocs-slider":
        value = _coerce_nprocs(slider_value, upper=32)
        return value, value

    value = _coerce_nprocs(input_value, upper=128)
    return value, min(value, 32)


@callback(
    Output("br-build-run-active-job", "data", allow_duplicate=True),
    Input({"type": "br-job-view", "job_id": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def select_job_from_table(_clicks: list[int | None]):
    if not isinstance(ctx.triggered_id, dict):
        raise PreventUpdate
    return str(ctx.triggered_id["job_id"])


@callback(
    Output("br-job-table-body", "children"),
    Output("br-run-log", "children"),
    Output("br-build-log", "children"),
    Output("br-build-log-collapse", "is_open"),
    Output("br-build-run-active-job", "data"),
    Output("br-build-btn", "disabled"),
    Output("br-build-clean-btn", "disabled"),
    Output("br-quick-run-btn", "disabled"),
    Output("br-run-stop-btn", "disabled"),
    Input("br-job-interval", "n_intervals"),
    State("br-build-run-gmcore-root", "data"),
    State("br-build-run-active-job", "data"),
)
def refresh_jobs(
    _n_intervals: int,
    gmcore_root: str | None,
    current_active_job_id: str | None,
):
    if not gmcore_root:
        empty_rows = _render_job_table([], None)
        return (
            empty_rows,
            "GMCORE root is not configured.",
            "No build jobs yet.",
            False,
            None,
            False,
            False,
            False,
            True,
        )

    manager = _get_job_manager(gmcore_root)
    jobs = manager.list_jobs()
    active_job_id = _pick_active_job_id(jobs, current_active_job_id)
    latest_build_job = _latest_build_job(jobs)
    build_job_id = None if latest_build_job is None else str(latest_build_job["job_id"])
    build_busy = _build_jobs_running(jobs)
    latest_running = _latest_running_job(jobs)

    return (
        _render_job_table(jobs, active_job_id),
        _render_job_log(
            manager,
            active_job_id,
            "Waiting for build or run activity...",
        ),
        _render_job_log(
            manager,
            build_job_id,
            "No configure/build log output yet.",
        ),
        build_job_id is not None,
        active_job_id,
        build_busy,
        build_busy,
        build_busy,
        latest_running is None,
    )


clientside_callback(
    """
    function(content) {
        const node = document.getElementById("br-run-log");
        if (node) {
            node.scrollTop = node.scrollHeight;
        }
        return "";
    }
    """,
    Output("br-run-log-scroll", "children"),
    Input("br-run-log", "children"),
)


clientside_callback(
    """
    function(content) {
        const node = document.getElementById("br-build-log");
        if (node) {
            node.scrollTop = node.scrollHeight;
        }
        return "";
    }
    """,
    Output("br-build-log-scroll", "children"),
    Input("br-build-log", "children"),
)
