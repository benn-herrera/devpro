"""The profiler verb's argparse surface and dispatch: `devpro profiler <subcommand>`.

The verb's subcommand line is parsed where it is dispatched, so registering the verb
imports only this module.
"""

import argparse
import os
import sys
from pathlib import Path

# The hook payload a capture reads at most: a hook's stdin is bounded by what the host writes there, and
# a read with no bound waits out a host that never closes the pipe. Every read of it is bounded, the
# capture's included, so the bound is module scope rather than the capture's own.
PAYLOAD_LIMIT = 8 * 1024 * 1024


def add_verbs(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """Add the `profiler` verb to subparsers, carrying its subcommand and options as one remainder.

    The remainder is passed through as the profiler's own command line: the subcommands parse their
    options themselves, and the wrapper's arguments reach them unchanged."""
    profiler = subparsers.add_parser(
        "profiler",
        help="record a session's tool calls and show them as a tree or a page",
        allow_abbrev=False,
    )
    profiler.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        help="tree | init | doctor | repair | capture <harness>",
    )


def read_stdin() -> str:
    """The hook payload on stdin, bounded to `PAYLOAD_LIMIT` bytes and nothing where it cannot be read:
    a hook's stdin is a pipe a host writes, and a capture that read it whole would wait out a host that
    never closes it."""
    try:
        return sys.stdin.buffer.read(PAYLOAD_LIMIT).decode("utf-8", "replace")
    except OSError:
        return ""


def silent_stdout() -> None:
    """Point this process's stdout at the null device, for the capture's duration: the child writes
    nothing to the hook's stdout, which Claude Code reads as its hook JSON. An unbuffered write still
    reaches the terminal it was opened on, and `print(..., file=sys.stdout)` takes what is now here."""
    sys.stdout.flush()
    sys.stdout = open(os.devnull, "w", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    """Run the profiler subcommand `args.arguments` names, and return its exit status."""
    from .capture import capture
    from .hooks import USAGE, doctor, init
    from .pages import UsageError, tree
    from .stores import repair_child_ids
    from .values import project_dir

    sys.stdout.reconfigure(encoding="utf-8")
    arguments = args.arguments
    command = arguments[0] if arguments else None
    rest = arguments[1:]
    if command == "capture":
        # The never-block contract, owned here: a profiler must never break or slow down the session it
        # watches, so the payload read is bounded, the child's stdout never reaches the hook's own —
        # Claude Code reads hook JSON there — and no error leaves capture.
        silent_stdout()
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
        if command == "init":
            print(init(rest, Path.cwd()))
            return 0
        if command == "doctor":
            print(doctor(Path.cwd()))
            return 0
        if command == "repair":
            repaired, null, left = repair_child_ids(project_dir(os.getcwd()))
            print(f"repaired: {repaired} edges; null: {null} records (no child id)")
            for file in left:
                print(f"left {file} as it stands: a capture appended to it while it was read", file=sys.stderr)
            return 0
    except UsageError as error:
        print(error, file=sys.stderr)
        return 1
    print(USAGE)
    return 1 if command else 0
