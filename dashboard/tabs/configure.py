"""Namelist configuration editor tab for the GMCORE Dashboard."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

import dash_ace
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate

from gmcore_dashboard.dashboard.scanner import parse_namelist, scan_testbed


CARD_CLASS = "border"
MONO_STYLE = {"fontFamily": "'JetBrains Mono', 'Fira Code', monospace"}
EDITOR_SHELL_STYLE = {
    "backgroundColor": "#0a0a14",
    "border": "1px solid rgba(99, 102, 241, 0.14)",
    "borderRadius": "10px",
    "overflow": "hidden",
}
REFERENCE_TABLE_STYLE = {
    "fontSize": "0.86rem",
}
REQUIRED_FIELDS = ("nlon", "nlat", "test_case", "case_name")

PARAM_REFERENCE = {
    # Grid
    "nlon": ("integer", "", "Number of longitude grid cells"),
    "nlat": ("integer", "", "Number of latitude grid cells"),
    "nlev": ("integer", "1", "Number of vertical levels"),
    "planet": ("string", "'earth'", "Planet type: earth or mars"),
    # Time
    "run_days": ("real", "0", "Simulation duration in days"),
    "run_hours": ("real", "0", "Simulation duration in hours"),
    "dt_dyn": ("real", "0", "Dynamics time step (seconds)"),
    "dt_adv": ("real", "0", "Advection time step (seconds)"),
    "dt_phys": ("real", "0", "Physics time step (seconds)"),
    "time_scheme": ("string", "'wrfrk3'", "Time integration scheme"),
    # Case
    "test_case": ("string", "'N/A'", "Test case identifier"),
    "case_name": ("string", "'N/A'", "Case name for output files"),
    "case_desc": ("string", "'N/A'", "Case description"),
    # Vertical
    "vert_coord_scheme": ("string", "'hybrid'", "Vertical coordinate type"),
    "vert_coord_template": ("string", "'N/A'", "Vertical level template"),
    "ptop": ("real", "219.4", "Top pressure (Pa)"),
    "nonhydrostatic": ("logical", ".false.", "Enable non-hydrostatic mode"),
    # Advection
    "bg_adv_scheme": ("string", "'ffsl'", "Background advection scheme"),
    "pt_adv_scheme": ("string", "'upwind'", "Potential temperature advection"),
    "limiter_type": ("string", "'mono'", "Flux limiter type"),
    "upwind_order_pv": ("integer", "3", "PV upwind order"),
    # Damping
    "use_div_damp": ("logical", ".false.", "Enable divergence damping"),
    "use_vor_damp": ("logical", ".false.", "Enable vorticity damping"),
    "use_smag_damp": ("logical", ".false.", "Enable Smagorinsky damping"),
    "div_damp_coef2": ("real", "1/128", "2nd-order div damping coefficient"),
    # Physics
    "physics_suite": ("string", "'N/A'", "Physics suite name"),
    # Output
    "history_interval": ("string", "'N/A'", "History output interval"),
    "output_h0_new_file": ("string", "''", "New file policy: one_file, by_day, etc"),
    "output_h0_dtype": ("string", "'r4'", "Output data type"),
    "advection": ("logical", ".false.", "Pure advection mode"),
    # MPI
    "nproc_x": ("integer(20)", "0", "Process layout in x"),
    "nproc_y": ("integer(20)", "0", "Process layout in y"),
    "filter_coef_a": ("real", "3.8", "Filter coefficient a"),
    "filter_coef_b": ("real", "0.5", "Filter coefficient b"),
}

_ASSIGNMENT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")
_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(
    r"^[+-]?(?:(?:\d+\.\d*|\.\d+|\d+)(?:[eEdD][+-]?\d+)?|\d+[eEdD][+-]?\d+)$"
)
_INTEGER_EXPR_RE = re.compile(r"^[0-9\s+\-*/()]+$")
_REAL_EXPR_RE = re.compile(r"^[0-9\s+\-*/().eEdD]+$")


def create_layout(testbed_root: str) -> dbc.Container:
    """Create the Namelist Configuration Editor tab layout."""
    resolved_root = _resolve_testbed_root(testbed_root)
    testbed_data = scan_testbed(resolved_root)
    case_options = _build_case_options(testbed_data)
    first_case = _first_case_name(testbed_data)

    return dbc.Container(
        fluid=True,
        className="py-3",
        children=[
            dcc.Store(id="cfg-testbed-root", data=resolved_root),
            dcc.Store(id="cfg-current-file"),
            dbc.Row(
                className="g-3",
                children=[
                    dbc.Col(
                        _build_selector_column(
                            case_options=case_options,
                            first_case=first_case,
                            testbed_root=resolved_root,
                        ),
                        width=4,
                    ),
                    dbc.Col(_build_editor_column(first_case), width=8),
                ],
            ),
            dbc.Row(
                className="g-3 mt-1",
                children=[dbc.Col(_build_reference_card(), width=12)],
            ),
        ],
    )


def _build_selector_column(
    case_options: list[dict[str, object]],
    first_case: str | None,
    testbed_root: str,
) -> html.Div:
    return html.Div(
        [
            dbc.Card(
                className=f"{CARD_CLASS} mb-3",
                children=[
                    dbc.CardHeader(
                        [
                            html.Span(html.I(className="bi bi-folder2-open"), className="ch-icon"),
                            html.Span("算例与文件选择", className="ch-title"),
                        ]
                    ),
                    dbc.CardBody(
                        [
                            html.Div(
                                Path(testbed_root).as_posix(),
                                className="small text-muted mb-3",
                                style=MONO_STYLE,
                            ),
                            dbc.Label("Case", html_for="cfg-case-select"),
                            dcc.Dropdown(
                                id="cfg-case-select",
                                options=case_options,
                                value=first_case,
                                placeholder="Select a test case",
                                clearable=False,
                                className="dash-dropdown",
                            ),
                            dbc.Card(
                                className="mt-3 bg-black bg-opacity-25 border-secondary",
                                children=[
                                    dbc.CardHeader(
                                        [
                                            html.Span(html.I(className="bi bi-info-circle"), className="ch-icon"),
                                            html.Span("当前 Namelist 信息", className="ch-title"),
                                        ]
                                    ),
                                    dbc.CardBody(id="cfg-case-info"),
                                ],
                            ),
                        ]
                    ),
                ],
            ),
            dbc.Card(
                className=CARD_CLASS,
                children=[
                    dbc.CardHeader(
                        [
                            html.Span(html.I(className="bi bi-files"), className="ch-icon"),
                            html.Span("克隆模板", className="ch-title"),
                        ]
                    ),
                    dbc.CardBody(
                        [
                            dbc.Label("Template Source", html_for="cfg-template-source"),
                            dcc.Dropdown(
                                id="cfg-template-source",
                                options=case_options,
                                value=first_case,
                                placeholder="Select a template case",
                                clearable=False,
                                className="dash-dropdown mb-3",
                            ),
                            dbc.Label("New Case Name", html_for="cfg-new-case-name"),
                            dbc.Input(
                                id="cfg-new-case-name",
                                type="text",
                                placeholder="example.360x180",
                                className="mb-3",
                            ),
                            dbc.Row(
                                className="g-2",
                                children=[
                                    dbc.Col(
                                        [
                                            dbc.Label("nlon", html_for="cfg-new-nlon"),
                                            dbc.Input(
                                                id="cfg-new-nlon",
                                                type="number",
                                                min=1,
                                                step=1,
                                                placeholder="360",
                                            ),
                                        ],
                                        md=6,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("nlat", html_for="cfg-new-nlat"),
                                            dbc.Input(
                                                id="cfg-new-nlat",
                                                type="number",
                                                min=1,
                                                step=1,
                                                placeholder="180",
                                            ),
                                        ],
                                        md=6,
                                    ),
                                ],
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-file-earmark-plus me-2"), "New Case from Template"],
                                id="cfg-new-case-btn",
                                color="primary",
                                className="w-100 mt-3",
                            ),
                        ]
                    ),
                ],
            ),
        ]
    )


def _build_editor_column(first_case: str | None) -> dbc.Card:
    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader(
                html.Div(
                    id="cfg-editor-title",
                    children=_editor_title(first_case),
                )
            ),
            dbc.CardBody(
                [
                    html.Div(
                        style=EDITOR_SHELL_STYLE,
                        children=[
                            dash_ace.DashAceEditor(
                                id="cfg-editor",
                                mode="fortran",
                                theme="monokai",
                                fontSize=14,
                                width="100%",
                                height="500px",
                                enableBasicAutocompletion=True,
                                enableLiveAutocompletion=True,
                                showPrintMargin=False,
                                showGutter=True,
                                highlightActiveLine=True,
                                value="",
                            )
                        ],
                    ),
                    dbc.Row(
                        className="g-2 mt-3",
                        children=[
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="bi bi-save2 me-2"), "保存"],
                                    id="cfg-save-btn",
                                    color="success",
                                    className="w-100",
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="bi bi-arrow-counterclockwise me-2"), "还原"],
                                    id="cfg-revert-btn",
                                    color="secondary",
                                    className="w-100",
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="bi bi-check2-circle me-2"), "Validate"],
                                    id="cfg-validate-btn",
                                    color="info",
                                    className="w-100",
                                ),
                                md=3,
                            ),
                        ],
                    ),
                    dbc.Alert(
                        id="cfg-status-alert",
                        is_open=False,
                        color="secondary",
                        className="glass mt-3 mb-0",
                    ),
                ]
            ),
        ],
    )


def _build_reference_card() -> dbc.Card:
    rows = [
        html.Tr(
            [
                html.Td(html.Code(name), style=MONO_STYLE),
                html.Td(type_name),
                html.Td(html.Code(default_value or " "), style=MONO_STYLE),
                html.Td(description),
            ]
        )
        for name, (type_name, default_value, description) in sorted(PARAM_REFERENCE.items())
    ]

    return dbc.Card(
        className=CARD_CLASS,
        children=[
            dbc.CardHeader(
                dbc.Button(
                    [html.I(className="bi bi-book me-2"), "Parameter Reference"],
                    id="cfg-param-ref-toggle",
                    color="secondary",
                    className="w-100 text-start",
                )
            ),
            dbc.Collapse(
                id="cfg-param-ref",
                is_open=False,
                children=dbc.CardBody(
                    dbc.Table(
                        bordered=False,
                        hover=True,
                        responsive=True,
                        size="sm",
                        className="align-middle mb-0 text-light",
                        style=REFERENCE_TABLE_STYLE,
                        children=[
                            html.Thead(
                                html.Tr(
                                    [
                                        html.Th("Parameter name"),
                                        html.Th("Type"),
                                        html.Th("Default value"),
                                        html.Th("Description"),
                                    ]
                                )
                            ),
                            html.Tbody(rows),
                        ],
                    )
                ),
            ),
        ],
    )


def _resolve_testbed_root(testbed_root: str) -> str:
    return Path(testbed_root).expanduser().resolve().as_posix()


def _build_case_options(
    testbed_data: dict[str, list[dict[str, Any]]]
) -> list[dict[str, object]]:
    options: list[dict[str, object]] = []

    for category in sorted(testbed_data):
        grouped_cases = sorted(
            testbed_data[category],
            key=lambda case: str(case.get("name", "")),
        )
        if not grouped_cases:
            continue

        options.append(
            {
                "label": category,
                "options": [
                    {
                        "label": str(case.get("name", "")),
                        "value": str(case.get("name", "")),
                    }
                    for case in grouped_cases
                ],
            }
        )

    return options


def _first_case_name(testbed_data: dict[str, list[dict[str, Any]]]) -> str | None:
    for category in sorted(testbed_data):
        cases = sorted(
            testbed_data[category],
            key=lambda case: str(case.get("name", "")),
        )
        if cases:
            return str(cases[0].get("name", ""))
    return None


def _find_case_info(testbed_root: str | None, case_name: str | None) -> dict[str, Any] | None:
    if not testbed_root or not case_name:
        return None

    testbed_data = scan_testbed(testbed_root)
    for cases in testbed_data.values():
        for case in cases:
            if str(case.get("name", "")) == case_name:
                return case
    return None


def _resolve_namelist_path(testbed_root: str | None, case_name: str | None) -> Path | None:
    case_info = _find_case_info(testbed_root, case_name)
    if not case_info:
        return None
    case_dir = Path(str(case_info.get("path", "")))
    namelist_path = case_dir / "namelist"
    return namelist_path if namelist_path.is_file() else None


def _editor_title(case_name: str | None) -> str:
    return f"Namelist Editor — {case_name or 'No case selected'}"


def _parse_namelist_text(text: str) -> dict[str, Any]:
    parameters: dict[str, Any] = {}
    current_assignment = ""
    in_group = False

    for raw_line in text.splitlines():
        line = _strip_comments(raw_line).strip()
        if not line:
            continue

        if line.startswith("&"):
            if current_assignment:
                _store_assignment(current_assignment, parameters)
                current_assignment = ""
            in_group = True
            continue

        if not in_group:
            continue

        if line == "/":
            if current_assignment:
                _store_assignment(current_assignment, parameters)
                current_assignment = ""
            in_group = False
            continue

        if _ASSIGNMENT_RE.match(line):
            if current_assignment:
                _store_assignment(current_assignment, parameters)
            current_assignment = line
            continue

        current_assignment = f"{current_assignment} {line}".strip()

    if current_assignment:
        _store_assignment(current_assignment, parameters)

    return parameters


def _store_assignment(text: str, parameters: dict[str, Any]) -> None:
    for assignment in _split_assignment_segments(text):
        if "=" not in assignment:
            continue

        key, value = assignment.split("=", 1)
        key = key.strip()
        if not key:
            continue

        parameters[key] = _parse_value(value.strip().rstrip(","))


def _parse_value(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""

    parts = _split_top_level_commas(value)
    if len(parts) > 1:
        return [_parse_value(part) for part in parts]

    lowered = value.lower()
    if lowered == ".true.":
        return True
    if lowered == ".false.":
        return False

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        quote = value[0]
        inner = value[1:-1]
        return inner.replace(quote * 2, quote)

    if _INT_RE.fullmatch(value):
        return int(value)

    if _FLOAT_RE.fullmatch(value):
        return float(re.sub(r"[dD]", "e", value))

    return value


def _split_assignment_segments(text: str) -> list[str]:
    segments: list[str] = []
    start = 0
    in_single = False
    in_double = False
    index = 0

    while index < len(text):
        char = text[index]

        if char == "'" and not in_double:
            if in_single and index + 1 < len(text) and text[index + 1] == "'":
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            if in_double and index + 1 < len(text) and text[index + 1] == '"':
                index += 2
                continue
            in_double = not in_double
        elif char == "," and not in_single and not in_double:
            tail = text[index + 1 :]
            if _ASSIGNMENT_RE.match(tail):
                segments.append(text[start:index].strip())
                start = index + 1

        index += 1

    tail_segment = text[start:].strip()
    if tail_segment:
        segments.append(tail_segment)

    return segments


def _split_top_level_commas(text: str) -> list[str]:
    parts: list[str] = []
    start = 0
    in_single = False
    in_double = False
    index = 0

    while index < len(text):
        char = text[index]

        if char == "'" and not in_double:
            if in_single and index + 1 < len(text) and text[index + 1] == "'":
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            if in_double and index + 1 < len(text) and text[index + 1] == '"':
                index += 2
                continue
            in_double = not in_double
        elif char == "," and not in_single and not in_double:
            parts.append(text[start:index].strip())
            start = index + 1

        index += 1

    parts.append(text[start:].strip())
    return [part for part in parts if part]


def _strip_comments(text: str) -> str:
    characters: list[str] = []
    in_single = False
    in_double = False
    index = 0

    while index < len(text):
        char = text[index]

        if char == "'" and not in_double:
            characters.append(char)
            if in_single and index + 1 < len(text) and text[index + 1] == "'":
                characters.append(text[index + 1])
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            characters.append(char)
            if in_double and index + 1 < len(text) and text[index + 1] == '"':
                characters.append(text[index + 1])
                index += 2
                continue
            in_double = not in_double
        elif char == "!" and not in_single and not in_double:
            break
        else:
            characters.append(char)

        index += 1

    return "".join(characters)


def _format_summary_value(value: Any) -> str:
    if value in (None, ""):
        return "N/A"
    if isinstance(value, bool):
        return ".true." if value else ".false."
    if isinstance(value, list):
        return ", ".join(_format_summary_value(item) for item in value)
    return str(value)


def _resolution_summary(config: dict[str, Any]) -> str:
    nlon = config.get("nlon")
    nlat = config.get("nlat")
    if nlon in (None, "") or nlat in (None, ""):
        return "N/A"
    return f"{nlon} x {nlat}"


def _pick_time_step(config: dict[str, Any]) -> str:
    for key in ("dt_dyn", "dt_adv", "dt_phys"):
        value = config.get(key)
        if value not in (None, ""):
            return f"{value} s"
    return "N/A"


def _info_line(label: str, value: str, code: bool = False) -> html.Div:
    rendered_value: html.Component
    if code:
        rendered_value = html.Code(value, style=MONO_STYLE)
    else:
        rendered_value = html.Span(value)

    return html.Div(
        [
            html.Span(f"{label}: ", className="text-muted"),
            rendered_value,
        ],
        className="small mb-2",
    )


def _build_case_info(selected_case: str | None, current_file: str | None, editor_value: str | None):
    parsed: dict[str, Any] = {}

    if editor_value and editor_value.strip():
        parsed = _parse_namelist_text(editor_value)
    elif current_file:
        parsed = parse_namelist(current_file)

    if not selected_case and not current_file:
        return [
            html.Div("选择算例以查看其 namelist。", className="small text-muted")
        ]

    info_badges = [
        dbc.Badge(
            f"{len(parsed)} parameters parsed",
            color="info",
            pill=True,
            className="mb-3",
        )
    ]

    file_display = current_file or "No namelist selected"
    return [
        html.Div(info_badges, className="d-flex gap-2 flex-wrap"),
        _info_line("Selected case", selected_case or "N/A"),
        _info_line("case_name", _format_summary_value(parsed.get("case_name"))),
        _info_line("test_case", _format_summary_value(parsed.get("test_case"))),
        _info_line("resolution", _resolution_summary(parsed)),
        _info_line("time step", _pick_time_step(parsed)),
        _info_line("history", _format_summary_value(parsed.get("history_interval"))),
        html.Hr(className="border-secondary my-3"),
        html.Div("文件", className="small text-muted text-uppercase mb-1"),
        html.Div(file_display, className="small text-break", style=MONO_STYLE),
    ]


def _build_alert_children(title: str, details: list[str]) -> list[Any]:
    children: list[Any] = [html.Div(title, className="fw-semibold")]
    if not details:
        return children

    preview = details[:6]
    children.append(
        html.Ul([html.Li(detail) for detail in preview], className="mb-0 mt-2 small")
    )
    if len(details) > len(preview):
        children.append(
            html.Div(
                f"+{len(details) - len(preview)} more notes",
                className="small text-muted mt-2",
            )
        )
    return children


def _normalize_type(type_name: str) -> str:
    lowered = type_name.lower()
    if lowered.startswith("integer"):
        return "integer"
    if lowered.startswith("real"):
        return "real"
    if lowered.startswith("string"):
        return "string"
    if lowered.startswith("logical"):
        return "logical"
    return lowered


def _looks_numeric_expression(value: str, allow_float: bool) -> bool:
    candidate = value.strip()
    if not candidate or not any(char.isdigit() for char in candidate):
        return False
    pattern = _REAL_EXPR_RE if allow_float else _INTEGER_EXPR_RE
    return bool(pattern.fullmatch(candidate))


def _assess_scalar_type(expected_type: str, value: Any) -> tuple[str, str | None]:
    if expected_type == "logical":
        if isinstance(value, bool):
            return "ok", None
        return "error", f"expected logical, got {value!r}"

    if expected_type == "integer":
        if isinstance(value, bool):
            return "error", f"expected integer, got {value!r}"
        if isinstance(value, int):
            return "ok", None
        if isinstance(value, str) and _looks_numeric_expression(value, allow_float=False):
            return "warning", f"integer expression {value!r} could not be fully verified"
        return "error", f"expected integer, got {value!r}"

    if expected_type == "real":
        if isinstance(value, bool):
            return "error", f"expected real, got {value!r}"
        if isinstance(value, (int, float)):
            return "ok", None
        if isinstance(value, str) and _looks_numeric_expression(value, allow_float=True):
            return "warning", f"real expression {value!r} could not be fully verified"
        return "error", f"expected real, got {value!r}"

    if expected_type == "string":
        if isinstance(value, str):
            return "ok", None
        return "error", f"expected string, got {value!r}"

    return "ok", None


def _assess_value_type(key: str, value: Any, expected_type: str) -> tuple[str, str] | None:
    normalized = _normalize_type(expected_type)
    values = value if isinstance(value, list) else [value]
    warning_message: str | None = None

    for item in values:
        severity, detail = _assess_scalar_type(normalized, item)
        if severity == "error" and detail:
            return "error", f"{key}: {detail}"
        if severity == "warning" and detail and warning_message is None:
            warning_message = f"{key}: {detail}"

    if warning_message:
        return "warning", warning_message
    return None


def _validate_namelist_text(text: str) -> tuple[list[Any], str]:
    if not text.strip():
        return _build_alert_children("Validation failed.", ["The editor is empty."]), "danger"

    errors: list[str] = []
    warnings: list[str] = []
    parsed = _parse_namelist_text(text)
    stripped_lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not any(line.startswith("&") for line in stripped_lines):
        errors.append("Missing namelist group header like '&gmcore_control'.")
    if "/" not in stripped_lines:
        errors.append("Missing terminating '/' for the namelist group.")

    for field in REQUIRED_FIELDS:
        if field not in parsed or parsed[field] in (None, ""):
            errors.append(f"Missing required field '{field}'.")

    for key, value in parsed.items():
        reference = PARAM_REFERENCE.get(key)
        if reference is None:
            continue

        assessment = _assess_value_type(key, value, reference[0])
        if assessment is None:
            continue
        severity, message = assessment
        if severity == "error":
            errors.append(message)
        else:
            warnings.append(message)

    if errors:
        details = [f"Parsed {len(parsed)} parameters."] + errors + warnings
        return _build_alert_children("Validation failed.", details), "danger"

    if warnings:
        details = [f"Parsed {len(parsed)} parameters."] + warnings
        return _build_alert_children("Validation completed with warnings.", details), "warning"

    return (
        _build_alert_children(
            "Validation passed.",
            [f"Parsed {len(parsed)} parameters and all required fields are present."],
        ),
        "success",
    )


def _escape_fortran_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _replace_or_insert_assignment(text: str, key: str, raw_value: str) -> str:
    pattern = re.compile(
        rf"(^\s*{re.escape(key)}\s*=\s*)(.*?)(\s*(?:!.*)?$)",
        re.IGNORECASE | re.MULTILINE,
    )
    replacement = lambda match: f"{match.group(1)}{raw_value}{match.group(3)}"
    updated_text, replacements = pattern.subn(replacement, text, count=1)
    if replacements:
        return updated_text

    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "/":
            lines.insert(index, f"  {key} = {raw_value}")
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    if text.strip():
        return f"{text.rstrip()}\n  {key} = {raw_value}\n"

    return f"&gmcore_control\n  {key} = {raw_value}\n/\n"


def _apply_case_overrides(text: str, case_name: str, nlon: int, nlat: int) -> str:
    updated = _replace_or_insert_assignment(text, "case_name", _escape_fortran_string(case_name))
    updated = _replace_or_insert_assignment(updated, "nlon", str(nlon))
    updated = _replace_or_insert_assignment(updated, "nlat", str(nlat))
    return updated


def _coerce_positive_int(value: Any) -> int | None:
    try:
        coerced = int(value)
    except (TypeError, ValueError):
        return None
    return coerced if coerced > 0 else None


@callback(
    Output("cfg-editor", "value"),
    Output("cfg-current-file", "data"),
    Input("cfg-case-select", "value"),
    Input("cfg-revert-btn", "n_clicks"),
    State("cfg-testbed-root", "data"),
    State("cfg-current-file", "data"),
)
def load_or_revert_namelist(
    case_name: str | None,
    _revert_clicks: int | None,
    testbed_root: str | None,
    current_file: str | None,
):
    triggered_id = ctx.triggered_id
    namelist_path: Path | None

    if triggered_id == "cfg-revert-btn":
        if current_file:
            namelist_path = Path(current_file)
        else:
            namelist_path = _resolve_namelist_path(testbed_root, case_name)
    else:
        namelist_path = _resolve_namelist_path(testbed_root, case_name)

    if namelist_path is None or not namelist_path.is_file():
        return "", None

    return namelist_path.read_text(encoding="utf-8"), namelist_path.as_posix()


@callback(
    Output("cfg-case-info", "children"),
    Output("cfg-editor-title", "children"),
    Input("cfg-editor", "value"),
    Input("cfg-case-select", "value"),
    State("cfg-current-file", "data"),
)
def refresh_case_info(
    editor_value: str | None,
    selected_case: str | None,
    current_file: str | None,
):
    parsed = _parse_namelist_text(editor_value or "") if editor_value else {}
    display_name = str(parsed.get("case_name") or selected_case or "No case selected")
    return _build_case_info(selected_case, current_file, editor_value), _editor_title(display_name)


@callback(
    Output("cfg-status-alert", "children"),
    Output("cfg-status-alert", "color"),
    Output("cfg-status-alert", "is_open"),
    Output("cfg-case-select", "options"),
    Output("cfg-case-select", "value"),
    Output("cfg-template-source", "options"),
    Input("cfg-save-btn", "n_clicks"),
    Input("cfg-validate-btn", "n_clicks"),
    Input("cfg-new-case-btn", "n_clicks"),
    State("cfg-editor", "value"),
    State("cfg-current-file", "data"),
    State("cfg-testbed-root", "data"),
    State("cfg-template-source", "value"),
    State("cfg-new-case-name", "value"),
    State("cfg-new-nlon", "value"),
    State("cfg-new-nlat", "value"),
    prevent_initial_call=True,
)
def handle_editor_actions(
    _save_clicks: int | None,
    _validate_clicks: int | None,
    _new_case_clicks: int | None,
    editor_value: str | None,
    current_file: str | None,
    testbed_root: str | None,
    template_source: str | None,
    new_case_name: str | None,
    new_nlon: Any,
    new_nlat: Any,
):
    triggered_id = ctx.triggered_id

    if triggered_id == "cfg-save-btn":
        if not current_file:
            return (
                _build_alert_children("Save failed.", ["No namelist file is currently selected."]),
                "danger",
                True,
                no_update,
                no_update,
                no_update,
            )

        namelist_path = Path(current_file)
        backup_path = namelist_path.with_name("namelist.bak")

        try:
            shutil.copy2(namelist_path, backup_path)
            namelist_path.write_text(editor_value or "", encoding="utf-8")
        except Exception as exc:
            return (
                _build_alert_children("Save failed.", [str(exc)]),
                "danger",
                True,
                no_update,
                no_update,
                no_update,
            )

        return (
            _build_alert_children(
                "Namelist saved.",
                [
                    f"Backup written to {backup_path.as_posix()}.",
                    f"Updated {namelist_path.as_posix()}.",
                ],
            ),
            "success",
            True,
            no_update,
            no_update,
            no_update,
        )

    if triggered_id == "cfg-validate-btn":
        alert_children, color = _validate_namelist_text(editor_value or "")
        return alert_children, color, True, no_update, no_update, no_update

    if triggered_id == "cfg-new-case-btn":
        if not testbed_root:
            return (
                _build_alert_children("Case creation failed.", ["Testbed root is not configured."]),
                "danger",
                True,
                no_update,
                no_update,
                no_update,
            )

        case_name = (new_case_name or "").strip()
        if not case_name:
            return (
                _build_alert_children("Case creation failed.", ["Provide a new case name."]),
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        if case_name in {".", ".."} or "/" in case_name or "\\" in case_name:
            return (
                _build_alert_children(
                    "Case creation failed.",
                    ["Use a simple directory name without path separators."],
                ),
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        if not template_source:
            return (
                _build_alert_children("Case creation failed.", ["Select a template source case."]),
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )

        nlon = _coerce_positive_int(new_nlon)
        nlat = _coerce_positive_int(new_nlat)
        if nlon is None or nlat is None:
            return (
                _build_alert_children(
                    "Case creation failed.",
                    ["nlon and nlat must both be positive integers."],
                ),
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )

        template_case = _find_case_info(testbed_root, template_source)
        if not template_case:
            return (
                _build_alert_children(
                    "Case creation failed.",
                    [f"Template case '{template_source}' could not be found."],
                ),
                "danger",
                True,
                no_update,
                no_update,
                no_update,
            )

        testbed_path = Path(testbed_root)
        template_dir = Path(str(template_case.get("path", "")))
        target_dir = testbed_path / case_name

        if target_dir.exists():
            return (
                _build_alert_children(
                    "Case creation failed.",
                    [f"Target directory already exists: {target_dir.as_posix()}"],
                ),
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )

        created_dir = False
        try:
            shutil.copytree(
                template_dir,
                target_dir,
                ignore=shutil.ignore_patterns("__pycache__", "namelist.bak"),
            )
            created_dir = True
            namelist_path = target_dir / "namelist"
            template_text = namelist_path.read_text(encoding="utf-8")
            updated_text = _apply_case_overrides(template_text, case_name, nlon, nlat)
            namelist_path.write_text(updated_text, encoding="utf-8")
        except Exception as exc:
            if created_dir and target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)
            return (
                _build_alert_children("Case creation failed.", [str(exc)]),
                "danger",
                True,
                no_update,
                no_update,
                no_update,
            )

        refreshed_cases = scan_testbed(testbed_root)
        refreshed_options = _build_case_options(refreshed_cases)
        return (
            _build_alert_children(
                "New case created.",
                [
                    f"Cloned {template_source} into {target_dir.as_posix()}.",
                    f"Updated case_name='{case_name}', nlon={nlon}, nlat={nlat}.",
                ],
            ),
            "success",
            True,
            refreshed_options,
            case_name,
            refreshed_options,
        )

    raise PreventUpdate


@callback(
    Output("cfg-param-ref", "is_open"),
    Input("cfg-param-ref-toggle", "n_clicks"),
    State("cfg-param-ref", "is_open"),
    prevent_initial_call=True,
)
def toggle_parameter_reference(n_clicks: int | None, is_open: bool):
    if not n_clicks:
        raise PreventUpdate
    return not is_open
