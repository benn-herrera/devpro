"""The dicing verbs' argparse surface and dispatch: `devpro <verb>` for each of them.

`add_verbs` adds the five verbs to `devpro.cli.build_parser`'s subparsers; `run` dispatches one and
returns its exit status: 0 on success, 1 when a check or step fails, 2 on a refusal. A verb's
implementation is imported where that verb is dispatched, so registering the verbs imports none.
"""

import argparse
import os
import sys
from typing import TextIO


def _refuse_unreadable(roots: list[str], *, err: TextIO) -> bool:
    """Report each markdown file under roots that cannot be read as a file; True if any."""
    from .linkcheck import markdown_files

    unreadable = [f for f in markdown_files(roots) if not (os.path.isfile(f) and os.access(f, os.R_OK))]
    for f in unreadable:
        print(f"cannot read: {f}", file=err)
    return bool(unreadable)


def _add_split_level(parser: argparse.ArgumentParser) -> None:
    # choices are compared as written, so "04" is refused like any other value outside them. The
    # options and the default are the SPEC's fixed three, and argparse prints a default from this
    # form, so registering the verb needs no import; the path imports the constant it plans with.
    parser.add_argument(
        "--split-level",
        choices=["2", "3", "4"],
        default="4",
        help="deepest heading level that splits into sections (default %(default)s)",
    )


def add_verbs(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """Add the five dicing verbs to subparsers, each refusing abbreviations."""
    dice_one = subparsers.add_parser(
        "dice-doc", help="dice one document, then check it reassembles and its links resolve", allow_abbrev=False
    )
    _add_split_level(dice_one)
    dice_one.add_argument("monolith", help="the markdown document to dice")
    dice_one.add_argument("out", help="output directory, absent or empty")
    dice_one.add_argument("map", nargs="?", default="", help="link map TSV")

    undicing = subparsers.add_parser(
        "undice",
        help="write a diced tree back out as one document, then check it dices back",
        allow_abbrev=False,
    )
    _add_split_level(undicing)
    undicing.add_argument("tree", help="a diced tree's directory, holding its entry-point.md")
    undicing.add_argument("monolith", help="the document to write; must not exist")

    many = subparsers.add_parser(
        "dice-docs", help="dice the documents a manifest TSV lists, then verify them all", allow_abbrev=False
    )
    many.add_argument("manifest", help="manifest TSV naming the documents and their output directories")
    many.add_argument("src", help="directory the manifest's files are read from")
    many.add_argument("work", help="directory for intermediates")

    links = subparsers.add_parser(
        "check-links", help="check the relative links and anchors of markdown files", allow_abbrev=False
    )
    links.add_argument("roots", nargs="+", metavar="root", help="a directory, walked for every .md, or one file")

    tree = subparsers.add_parser(
        "check-tree",
        help="check every document of a diced tree is linked from its parent and reachable",
        allow_abbrev=False,
    )
    tree.add_argument("roots", nargs="+", metavar="root", help="a diced tree's directory, holding its entry-point.md")


def run(args: argparse.Namespace, *, parser: argparse.ArgumentParser) -> int:
    """Run the dicing verb `args.verb` names and return its exit status. parser reports a refusal as
    a usage error, exiting 2. The stdout and stderr this writes are reconfigured to utf-8 with
    surrogateescape, as the dicing reads and writes whatever bytes the documents hold."""
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="surrogateescape")
    out, err = sys.stdout, sys.stderr
    run_dir = os.getcwd()  # the one read of the working directory: every pass below is given it
    verb = args.verb
    if verb == "dice-doc":
        from .dicedoc import dice_doc

        return dice_doc(
            args.monolith, args.out, args.map, root=run_dir, stdout=out, stderr=err, deepest=int(args.split_level)
        )
    if verb == "undice":
        from .dicedoc import undice

        return undice(args.tree, args.monolith, root=run_dir, stdout=out, stderr=err, deepest=int(args.split_level))
    if verb == "dice-docs":
        from .manifest import dice_docs

        return dice_docs(args.manifest, args.src, args.work, root=run_dir, stdout=out, stderr=err)
    if verb == "check-links":
        missing = [root for root in args.roots if not os.path.exists(root)]
        if missing:
            parser.error(f"no such root: {', '.join(missing)}")
        if _refuse_unreadable(args.roots, err=err):
            return 2
        from .linkcheck import check_markdown_links

        try:
            return 0 if check_markdown_links(args.roots, out=out, err=err) else 1
        except OSError as e:
            # a file that became unreadable after the pre-check above, which cannot catch a race
            print(f"cannot read: {e.filename if e.filename is not None else ', '.join(args.roots)}", file=err)
            return 2
    if verb == "check-tree":
        missing = [root for root in args.roots if not os.path.isdir(root)]
        if missing:
            parser.error(f"no such directory: {', '.join(missing)}")
        if _refuse_unreadable(args.roots, err=err):
            return 2
        from .treecheck import check_trees

        try:
            return 0 if check_trees(args.roots, out=out, err=err) else 1
        except OSError as e:
            print(f"cannot read: {e.filename if e.filename is not None else ', '.join(args.roots)}", file=err)
            return 2
    raise AssertionError(f"{verb} is no dicing verb")
