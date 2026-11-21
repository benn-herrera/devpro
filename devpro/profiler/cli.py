"""The profiler verb's argparse surface and dispatch: `devpro profiler <subcommand>`.

`add_verbs` adds one `profiler` verb to `devpro.cli.build_parser`'s subparsers; `run` dispatches it and
returns its exit status. The verb's subcommand line is parsed where it is dispatched, so registering the
verb imports only this module.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def add_verbs(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """Add the `profiler` verb to subparsers, carrying its subcommand and options as one remainder.

    The remainder is passed through as the profiler's own command line: the subcommands parse their
    options themselves, and a launcher's arguments reach them unchanged."""
    profiler = subparsers.add_parser(
        "profiler",
        help="record a session's tool calls and show them as a tree or a page",
        allow_abbrev=False,
    )
    profiler.add_argument(
        "arguments", nargs=argparse.REMAINDER, help="serve | tree | init | doctor | capture <harness>"
    )


def read_stdin() -> str:
    """The hook payload on stdin, and nothing where it cannot be read."""
    try:
        return sys.stdin.buffer.read().decode("utf-8", "replace")
    except OSError:
        return ""


def run(args: argparse.Namespace) -> int:
    """Run the profiler subcommand `args.arguments` names, and return its exit status."""
    from .capture import capture
    from .hooks import USAGE, doctor, init
    from .pages import UsageError, serve, tree
    from .values import project_dir

    sys.stdout.reconfigure(encoding="utf-8")
    arguments = args.arguments
    command = arguments[0] if arguments else None
    rest = arguments[1:]
    if command == "capture":
        # A profiler must never break or slow down the session it watches, so no error leaves capture.
        try:
            capture(rest[0] if rest else "unknown", read_stdin())
        except Exception:
            pass
        return 0
    try:
        if command == "tree":
            color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
            print(tree(rest, project_dir(os.getcwd()), color=color))
            return 0
        if command == "serve":
            serve(rest)
            return 0
        if command == "init":
            print(init(rest, Path.cwd()))
            return 0
        if command == "doctor":
            print(doctor(Path.cwd()))
            return 0
    except UsageError as error:
        print(error, file=sys.stderr)
        return 1
    print(USAGE)
    return 1 if command else 0
