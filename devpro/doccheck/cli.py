"""The check verbs' argparse surface and dispatch: `devpro check-plan`, `devpro check-design` and
`devpro check-roadmap`.

`add_verbs` adds the three verbs to `devpro.cli.build_parser`'s subparsers; `run` dispatches one and
returns its exit status: 0 on success, 1 when a check fails, 2 on a refusal. A verb's implementation
is imported where that verb is dispatched, so registering the verbs imports none.
"""

import argparse
import os
import sys


def add_verbs(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """Add the three check verbs to subparsers, each refusing abbreviations."""
    plan = subparsers.add_parser(
        "check-plan", help="check a plan's status form, as the board reads it", allow_abbrev=False
    )
    plan.add_argument(
        "plan",
        nargs="?",
        help="the plan, or a diced plan's entry-point.md; default the active plan of the project the current"
        " directory is in",
    )

    checked_design = subparsers.add_parser(
        "check-design",
        help="check a design's final form and its delta pairs against their targets",
        allow_abbrev=False,
    )
    checked_design.add_argument(
        "--deltas-applied",
        action="store_true",
        help="check the design's delta claims as applied: every pair must have landed",
    )
    checked_design.add_argument(
        "design",
        nargs="?",
        help="the design, or a diced design's entry-point.md; default the active design of the project the"
        " current directory is in",
    )

    checked_roadmap = subparsers.add_parser(
        "check-roadmap", help="check ROADMAP.md's ticket layout, as the board reads it", allow_abbrev=False
    )
    checked_roadmap.add_argument(
        "roadmap",
        nargs="?",
        help="the roadmap's markdown file; default ROADMAP.md of the project the current directory is in",
    )


def run(args: argparse.Namespace, *, parser: argparse.ArgumentParser) -> int:
    """Run the check verb `args.verb` names and return its exit status. parser reports a refusal as
    a usage error, exiting 2. The stdout and stderr this writes are reconfigured to utf-8 with
    surrogateescape, as the checks quote whatever bytes the documents hold."""
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="surrogateescape")
    out, err = sys.stdout, sys.stderr
    run_dir = os.getcwd()  # the one read of the working directory: every check below is given it
    verb = args.verb
    if verb == "check-plan":
        if args.plan is not None and not os.path.isfile(args.plan):
            parser.error(
                f"no such plan file: {args.plan} (name a plan's markdown file, or a diced plan's entry-point.md)"
            )
        from .plancheck import check_plan

        return check_plan(args.plan, start=run_dir, stdout=out, stderr=err)
    if verb == "check-design":
        if args.design is not None and not os.path.isfile(args.design):
            parser.error(
                f"no such design file: {args.design} (name a design's markdown file, or a diced design's entry-point.md)"
            )
        from .plancheck import check_design

        return check_design(args.design, start=run_dir, stdout=out, stderr=err, deltas_applied=args.deltas_applied)
    if verb == "check-roadmap":
        if args.roadmap is not None and not os.path.isfile(args.roadmap):
            parser.error(f"no such roadmap file: {args.roadmap} (name a roadmap's markdown file)")
        from .plancheck import check_roadmap

        return check_roadmap(args.roadmap, start=run_dir, stdout=out, stderr=err)
    raise AssertionError(f"{verb} is no check verb")
