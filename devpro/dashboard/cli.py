"""The dashboard verb's argparse surface and dispatch: `devpro dashboard [<project-dir>] [--port <number>]`.

`devpro.cli` imports `add_verbs` while building its parser, so no module the
verb dispatches to is imported by it; `run` asks its server's module for `serve` where it dispatches.
"""

import argparse
import os
import sys

PORT_RANGE = range(0, 65536)


def port(text: str) -> int:
    """The port text names, 0 to 65535, refusing any other as the usage error a bad value is."""
    number = int(text)
    if number not in PORT_RANGE:
        raise argparse.ArgumentTypeError(f"{text} is not a port: 0 to 65535")
    return number


def project_dir(text: str) -> str:
    """The directory text names, refused as the usage error the board verb gave where it is not one."""
    if not os.path.isdir(text):
        raise argparse.ArgumentTypeError(f"no such directory: {text}")
    return text


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
        type=project_dir,
        metavar="project-dir",
        help="a directory inside the project to serve; default the project the current directory is in",
    )
    dashboard.add_argument(
        "--port",
        type=port,
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
