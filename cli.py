"""CLI entry point for launching the GMCORE Dashboard web app."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gmcore-dashboard",
        description="Launch the GMCORE Dashboard web application.",
    )
    parser.add_argument(
        "--gmcore-root",
        metavar="PATH",
        help="Path to GMCORE source root (default: $GMCORE_ROOT or auto-detect)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8151,
        help="Port to bind (default: 8151)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Dash debug mode",
    )
    args = parser.parse_args(argv)

    if args.gmcore_root:
        from gmcore_dashboard.config import set_gmcore_root
        set_gmcore_root(args.gmcore_root)

    from gmcore_dashboard.dashboard.app import create_app

    app = create_app()
    app.run(debug=args.debug, host=args.host, port=args.port, use_reloader=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
