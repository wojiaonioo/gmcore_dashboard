from __future__ import annotations

"""Main entry point for the GMCORE Dashboard."""

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, dcc, html, callback, ctx
from flask import abort, send_from_directory
from pathlib import Path
from werkzeug.utils import safe_join

from gmcore_dashboard.config import get_gmcore_root, get_testbed_root, get_experiments_root
from gmcore_dashboard.i18n import t, set_locale, get_locale
from gmcore_dashboard.dashboard.tabs.build_run import create_layout as create_build_run_layout
from gmcore_dashboard.dashboard.tabs.configure import create_layout as create_configure_layout
from gmcore_dashboard.dashboard.tabs.experiments import create_layout as create_experiments_layout
from gmcore_dashboard.dashboard.tabs.monitor import create_layout as create_monitor_layout
from gmcore_dashboard.dashboard.tabs.multi_view import create_layout as create_multi_view_layout
from gmcore_dashboard.dashboard.tabs.visualize import create_layout as create_visualize_layout


def create_app() -> Dash:
    """Create and configure the Dash application."""
    GMCORE_ROOT = get_gmcore_root()
    TESTBED_ROOT = get_testbed_root()
    EXPERIMENTS_ROOT = get_experiments_root()
    EXPERIMENTS_ROOT_RESOLVED = EXPERIMENTS_ROOT.resolve()

    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.FLATLY,
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
        ],
        suppress_callback_exceptions=True,
    )
    app.title = "GMCORE 仪表盘"

    def _bi(name: str, *, cls: str = "") -> html.I:
        return html.I(className=f"bi bi-{name} {cls}".strip())

    @app.server.route("/experiments-assets/<path:asset_path>")
    def experiments_assets(asset_path: str):
        full = safe_join(str(EXPERIMENTS_ROOT), asset_path)
        if not full:
            abort(404)
        try:
            resolved = Path(full).resolve(strict=True)
        except (FileNotFoundError, OSError):
            abort(404)
        if not resolved.is_file():
            abort(404)
        try:
            resolved.relative_to(EXPERIMENTS_ROOT_RESOLVED)
        except ValueError:
            abort(404)
        return send_from_directory(str(EXPERIMENTS_ROOT), asset_path)

    def _build_navbar(locale: str = "zh") -> html.Div:
        return html.Div(
            className="navbar",
            children=dbc.Container(
                fluid=True,
                className="d-flex align-items-center justify-content-between px-2",
                children=[
                    html.Div(
                        className="d-flex align-items-center",
                        children=[
                            html.Span(
                                className="navbar-brand",
                                children=[
                                    html.Span(_bi("globe2"), className="brand-mark"),
                                    html.Span(
                                        [
                                            html.Span("GMCORE"),
                                            html.Span(t("brand_sub", locale), className="brand-sub"),
                                        ],
                                        className="brand-text",
                                    ),
                                    html.Span(className="brand-divider d-none d-lg-inline-block"),
                                    html.Span(
                                        [
                                            _bi("cpu"),
                                            html.Span(t("brand_tagline", locale)),
                                        ],
                                        className="nav-chip d-none d-lg-inline-flex",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="d-flex align-items-center gap-2",
                        children=[
                            html.Span(
                                [
                                    _bi("folder2-open"),
                                    html.Span(TESTBED_ROOT.name),
                                ],
                                className="nav-chip nav-chip--info nav-chip--mono d-none d-xl-inline-flex",
                                title=str(TESTBED_ROOT),
                            ),
                            html.Span(
                                [html.Span(className="nav-chip-dot"), html.Span(t("status_online", locale))],
                                className="nav-chip nav-chip--ok d-none d-md-inline-flex",
                            ),
                            html.Span(
                                [_bi("tag"), html.Span("v4.1.0")],
                                className="nav-chip nav-chip--mono d-none d-md-inline-flex",
                            ),
                            dbc.Button(
                                [_bi("translate"), html.Span(t("lang_switch", locale), className="ms-1")],
                                id="btn-lang-toggle",
                                size="sm",
                                outline=True,
                                color="secondary",
                                className="nav-chip nav-chip--mono",
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _build_tabs(locale: str = "zh") -> dbc.Tabs:
        return dbc.Tabs(
            id="main-tabs",
            active_tab="visualize",
            children=[
                dbc.Tab(label=t("tab_visualize", locale),   tab_id="visualize",   tab_class_name="tab-ico tab-ico--visualize"),
                dbc.Tab(label=t("tab_experiments", locale), tab_id="experiments", tab_class_name="tab-ico tab-ico--experiments"),
                dbc.Tab(label=t("tab_multi_view", locale),  tab_id="multi_view",  tab_class_name="tab-ico tab-ico--multiview"),
                dbc.Tab(label=t("tab_configure", locale),   tab_id="configure",   tab_class_name="tab-ico tab-ico--configure"),
                dbc.Tab(label=t("tab_build_run", locale),   tab_id="build_run",   tab_class_name="tab-ico tab-ico--buildrun"),
                dbc.Tab(label=t("tab_monitor", locale),     tab_id="monitor",     tab_class_name="tab-ico tab-ico--monitor"),
            ],
        )

    def _missing_testbed_banner(locale: str = "zh") -> dbc.Alert | None:
        if TESTBED_ROOT.exists():
            return None
        return dbc.Alert(
            [
                html.Div(t("testbed_not_found_title", locale), className="fw-semibold"),
                html.Div(f"{t('testbed_not_found_msg', locale)} {TESTBED_ROOT}"),
            ],
            className="missing-testbed-alert glass mt-3 mb-0",
        )

    def _visualize_tab(locale: str = "zh") -> html.Div:
        if not TESTBED_ROOT.exists():
            return html.Div(
                className="placeholder-tab-shell",
                children=[
                    dbc.Alert(
                        [
                            html.H4(t("viz_unavailable_title", locale), className="alert-heading"),
                            html.P(t("viz_unavailable_msg", locale), className="mb-2"),
                            html.Code(str(TESTBED_ROOT)),
                        ],
                        color="danger",
                        className="missing-testbed-alert glass",
                    )
                ],
            )
        return html.Div(
            className="tab-panel",
            children=[create_visualize_layout(testbed_root=TESTBED_ROOT.as_posix())],
        )

    def _experiments_tab() -> html.Div:
        return html.Div(
            className="tab-panel",
            children=[create_experiments_layout(gmcore_root=GMCORE_ROOT, testbed_root=TESTBED_ROOT)],
        )

    def _multi_view_tab() -> html.Div:
        return html.Div(
            className="tab-panel",
            children=[create_multi_view_layout(gmcore_root=GMCORE_ROOT, testbed_root=TESTBED_ROOT)],
        )

    def _configure_tab(locale: str = "zh") -> html.Div:
        if not TESTBED_ROOT.exists():
            return html.Div(
                className="placeholder-tab-shell",
                children=[
                    dbc.Alert(
                        [
                            html.H4(t("cfg_unavailable_title", locale), className="alert-heading"),
                            html.P(t("cfg_unavailable_msg", locale), className="mb-2"),
                            html.Code(str(TESTBED_ROOT)),
                        ],
                        color="danger",
                        className="missing-testbed-alert glass",
                    )
                ],
            )
        return html.Div(
            className="tab-panel",
            children=[create_configure_layout(testbed_root=TESTBED_ROOT.as_posix())],
        )

    def _render_tab_content(active_tab: str | None, locale: str = "zh") -> html.Div:
        if active_tab == "experiments":
            return _experiments_tab()
        if active_tab == "multi_view":
            return _multi_view_tab()
        if active_tab == "configure":
            return _configure_tab(locale)
        if active_tab == "build_run":
            return html.Div(
                className="tab-panel",
                children=[
                    create_build_run_layout(
                        gmcore_root=GMCORE_ROOT.as_posix(),
                        testbed_root=TESTBED_ROOT.as_posix(),
                    )
                ],
            )
        if active_tab == "monitor":
            return html.Div(
                className="tab-panel",
                children=[
                    create_monitor_layout(
                        gmcore_root=GMCORE_ROOT.as_posix(),
                        testbed_root=TESTBED_ROOT.as_posix(),
                    )
                ],
            )
        return _visualize_tab(locale)

    app.layout = html.Div(
        className="main-shell",
        children=[
            dcc.Store(id="locale-store", data="zh", storage_type="local"),
            html.Div(id="navbar-container", children=[_build_navbar("zh")]),
            dcc.Store(id="viz-preview-request"),
            dcc.Store(id="exp-custom-root", storage_type="local"),
            dbc.Container(
                fluid=True,
                className="main-content",
                children=[
                    html.Div(id="testbed-banner", children=[_missing_testbed_banner("zh")]),
                    html.Div(id="tabs-container", children=[_build_tabs("zh")]),
                    html.Div(id="tab-content", children=_render_tab_content("visualize", "zh")),
                ],
            ),
        ],
    )

    @app.callback(
        Output("locale-store", "data"),
        Input("btn-lang-toggle", "n_clicks"),
        State("locale-store", "data"),
        prevent_initial_call=True,
    )
    def toggle_locale(n_clicks, current_locale):
        return "en" if current_locale == "zh" else "zh"

    @app.callback(
        Output("navbar-container", "children"),
        Output("testbed-banner", "children"),
        Output("tabs-container", "children"),
        Input("locale-store", "data"),
    )
    def update_shell_locale(locale):
        locale = locale or "zh"
        set_locale(locale)
        return (
            _build_navbar(locale),
            _missing_testbed_banner(locale),
            _build_tabs(locale),
        )

    @app.callback(
        Output("tab-content", "children"),
        Input("main-tabs", "active_tab"),
        State("locale-store", "data"),
    )
    def switch_tab(active_tab: str | None, locale: str | None) -> html.Div:
        return _render_tab_content(active_tab, locale or "zh")

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=False, host="127.0.0.1", port=8151, use_reloader=False)
