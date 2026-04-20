"""CLI entry point for launching the GMCORE Dashboard web app."""

from __future__ import annotations

import argparse
import socket
import sys


def _find_free_port(host: str, start: int = 8151, end: int = 8199) -> int:
    """Find an available port in [start, end], fallback to OS-assigned."""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
                return port
            except OSError:
                continue
    # All ports in range occupied — let OS pick one
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]


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
        default=None,
        help="Port to bind (default: auto-select from 8151+)",
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

    port = args.port if args.port is not None else _find_free_port(args.host)

    from gmcore_dashboard.dashboard.app import create_app

    app = create_app()
    app.run(debug=args.debug, host=args.host, port=port, use_reloader=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
