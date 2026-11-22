"""The dashboard verb's argparse surface and dispatch: `devpro dashboard [<project-dir>] [--port <number>]`.

`add_verbs` adds one `dashboard` verb to `devpro.cli.build_parser`'s subparsers; `run` serves it and
returns its exit status. `devpro.cli` imports `add_verbs` while building its parser, so no module the
verb dispatches to is imported by it; `run` asks its server's module for `serve` where it dispatches.
"""

from __future__ import annotations

import argparse
import sys


def add_verbs(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """Add the `dashboard` verb to subparsers, with the project directory it serves and the one
    option a served port takes."""
    dashboard = subparsers.add_parser(
        "dashboard",
        help="serve the session records and the project's board on 127.0.0.1",
        allow_abbrev=False,
    )
    dashboard.add_argument(
        "project_dir",
        nargs="?",
        metavar="project-dir",
        help="a directory inside the project to serve; default the project the current directory is in",
    )
    dashboard.add_argument(
        "--port",
        type=int,
        choices=range(0, 65536),
        default=0,
        metavar="NUMBER",
        help="the port to bind on 127.0.0.1, 0 to 65535; default %(default)s, a free port the system chooses",
    )


def run(args: argparse.Namespace) -> int:
    """Serve the dashboard until interrupted, the URL printed once on stdout, and return its exit status."""
    from devpro.dashboard.server import serve

    sys.stdout.reconfigure(encoding="utf-8")
    serve(args.project_dir, args.port)
    return 0
