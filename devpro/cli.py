"""`devpro <verb>` (or `python3 -m devpro <verb>`): the argparse surface and dispatch.

The report is `print`: a short-lived CLI whose exit code is its contract, where
a logging setup would be a second reporting regime.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from devpro import __version__
from devpro.components import COMPONENTS, NAME, Components, selection
from devpro.context import (
    DEFAULT_FAMILY,
    DEFAULT_HARNESS,
    HarnessSettings,
    MapSupply,
    Render,
    build_render,
    families,
    harness_named,
    map_spec,
    read_settings,
)
from devpro.errors import InputError
from devpro.vocabulary import HarnessText, key

_DRY_RUN_HELP = "print what the install would create, change and remove; write nothing"

DICING_VERBS = (
    "dice-doc",
    "undice",
    "dice-docs",
    "check-links",
    "check-tree",
    "check-plan",
    "check-design",
    "check-roadmap",
    "kanban",
)
"""The dicing verbs, added by `devpro.dicing.cli.add_verbs` and dispatched to its `run`."""

PROFILER_VERB = "profiler"
"""The profiler verb, added by `devpro.profiler.cli.add_verbs` and dispatched to its `run`."""


def _add_tuning_flags(verb: argparse.ArgumentParser, *, harness_default: str | None, harness_help: str) -> None:
    verb.add_argument("--harness", default=harness_default, metavar="NAME", help=harness_help)
    verb.add_argument(
        "--family",
        default=DEFAULT_FAMILY,
        metavar="NAME",
        help=f"the model family to tune for: one of {', '.join(families())}; default %(default)s",
    )
    verb.add_argument(
        "--config-file",
        metavar="FILE",
        default=None,
        help=(
            "[<harness>] settings, install among them, and [<harness>-model-map] entries; read in place of "
            "~/.config/devpro/devpro.cfg"
        ),
    )


def _add_components(verb: argparse.ArgumentParser) -> None:
    verb.add_argument(
        "--components",
        metavar="CSV",
        default=None,
        help=f"the optional components to turn on, comma-separated: {', '.join(COMPONENTS)}; default none",
    )


def build_parser() -> argparse.ArgumentParser:
    """One verb, required: `render --out DIR` and `install TARGET [--subdir DIR] [--verbose] [--dry-run]`,
    each with the tuning flags; `install-agents-file DIR [--harness NAME] [--dry-run]`;
    `render-agents-file HARNESS OUT`; the nine dicing verbs `devpro.dicing.cli.add_verbs` adds, the
    `profiler` verb `devpro.profiler.cli.add_verbs` adds; and one maintainer helper hidden from `--help`:
    `harness NAME KEY`.
    Each verb but `harness`, `install-agents-file`, the dicing verbs and `profiler` takes
    `[--components=CSV]`, turning no optional component on by default. The top-level `--version` prints the bare version. allow_abbrev=False on every parser.
    """
    from devpro.dicing.cli import add_verbs
    from devpro.profiler.cli import add_verbs as add_profiler_verbs

    parser = argparse.ArgumentParser(prog="devpro", allow_abbrev=False)
    parser.add_argument("--version", action="version", version=__version__)
    # The hidden verbs are added without help, and the verb list is set below from every other: argparse
    # (3.9) still prints a subparser added with help=SUPPRESS, as "==SUPPRESS==", and lists every choice
    # in the usage line.
    verbs = parser.add_subparsers(dest="verb", required=True)
    render = verbs.add_parser("render", help="render the definitions into DIR", allow_abbrev=False)
    _add_components(render)
    render.add_argument("--out", required=True, type=Path, metavar="DIR", help="an existing output root")
    _add_tuning_flags(render, harness_default=DEFAULT_HARNESS, harness_help="the harness to render for")
    installing = verbs.add_parser(
        "install", help="render the set into its install directory and copy its packages", allow_abbrev=False
    )
    _add_components(installing)
    installing.add_argument("target", type=Path, metavar="TARGET", help="an existing project or harness directory")
    installing.add_argument(
        "--subdir",
        metavar="DIR",
        default=None,
        help="the harness directory is TARGET/DIR, TARGET being the project root, DIR inside it; empty makes it TARGET itself",
    )
    installing.add_argument("--verbose", "-v", action="store_true", help="report every file written")
    installing.add_argument("--dry-run", action="store_true", help=_DRY_RUN_HELP)
    _add_tuning_flags(
        installing,
        harness_default=None,
        harness_help=(
            "the harness to install for; without it, every harness the devpro settings file names, else "
            "detected from TARGET"
        ),
    )
    agents_file = verbs.add_parser("install-agents-file", help="install the agents file block", allow_abbrev=False)
    agents_file.add_argument("directory", type=Path, metavar="DIR")
    agents_file.add_argument(
        "--harness",
        metavar="NAME",
        default=None,
        help="inferred, when absent or empty, from DIR being a harness's user directory",
    )
    agents_file.add_argument(
        "--dry-run", action="store_true", help="print which files the install would create or change; write nothing"
    )
    fresh = verbs.add_parser("render-agents-file", help="write a fresh agents file to OUT", allow_abbrev=False)
    _add_components(fresh)
    fresh.add_argument("harness", metavar="HARNESS")
    fresh.add_argument("out", type=Path, metavar="OUT")
    query = verbs.add_parser("harness", allow_abbrev=False)
    query.add_argument("name", metavar="NAME")
    query.add_argument("key", choices=[key(part) for part in HarnessText], metavar="KEY")
    add_verbs(verbs)
    add_profiler_verbs(verbs)
    hidden = {"harness"}
    verbs.metavar = "{" + ",".join(name for name in verbs.choices if name not in hidden) + "}"
    return parser


def _tuned(args: argparse.Namespace, *, harness: str, supply: MapSupply | None, components: str) -> Render:
    ctx = build_render(harness=harness, components=components, family=args.family, supply=supply)
    print(f"tuning: family={ctx.family.name} category[{map_spec(ctx.category_map)}] harness={ctx.harness.name}")
    return ctx


def _supply(settings: dict[str, HarnessSettings] | None, harness: str) -> MapSupply | None:
    """The devpro settings file's map for `harness`, where there is a file and it names that harness."""
    entry = None if settings is None else settings.get(harness)
    return None if entry is None else entry.supply


def _run(args: argparse.Namespace, *, parser: argparse.ArgumentParser) -> None:
    if args.verb == "render":
        from devpro.render import render_all, write_renders

        settings, _ = read_settings(args.config_file)
        components = args.components or ""
        renders = render_all(
            _tuned(args, harness=args.harness, supply=_supply(settings, args.harness), components=components)
        )
        for path in write_renders(args.out, renders):
            print(f"wrote {path}")
    elif args.verb == "install":
        from devpro.install import components_value, install_selected, preflighted_install, uncommitted_sources
        from devpro.install_target import resolve_install_target

        settings, path = read_settings(args.config_file)
        # One iteration of `install_selected`'s loop, minus the harness prefix: the two paths install the
        # same way, so a change to either belongs in both.
        if args.harness is not None or settings is None:
            target = resolve_install_target(args.target, harness=args.harness, plugin=NAME, subdir=args.subdir)
            preflighted_install(
                target.harness_dir,
                _tuned(
                    args,
                    harness=target.harness,
                    supply=_supply(settings, target.harness),
                    components=components_value(args.components, settings, target.harness),
                ),
                verbose=args.verbose,
                project_root=target.project_root,
                uncommitted=uncommitted_sources,
                dry_run=args.dry_run,
            )
        else:
            install_selected(
                args.target,
                settings,
                path=path,
                tuned=lambda harness, supply, components: _tuned(
                    args, harness=harness, supply=supply, components=components
                ),
                components=args.components,
                subdir=args.subdir,
                verbose=args.verbose,
                dry_run=args.dry_run,
                uncommitted=uncommitted_sources,
            )
    elif args.verb == "install-agents-file":
        from devpro.agents_file import preflighted_agents_file_install
        from devpro.install import uncommitted_sources
        from devpro.install_target import agents_file_harness

        harness = harness_named(agents_file_harness(args.directory, args.harness))
        preflighted_agents_file_install(
            args.directory, harness, Components(), uncommitted=uncommitted_sources, dry_run=args.dry_run
        )
    elif args.verb == "render-agents-file":
        from devpro.agents_file import scope_name
        from devpro.render import render_agents_file

        harness = harness_named(args.harness)
        text = render_agents_file(harness, selection(args.components or ""), scope=scope_name(harness, args.out.parent))
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    elif args.verb in DICING_VERBS:
        from devpro.dicing.cli import run as run_dicing

        sys.exit(run_dicing(args, parser=parser))
    elif args.verb == PROFILER_VERB:
        from devpro.profiler.cli import run as run_profiler

        sys.exit(run_profiler(args))
    else:
        bound = harness_named(args.name).bound(NAME)
        print(bound.text(HarnessText("_".join(args.key.split("-")))))


def main(argv: list[str] | None = None) -> None:
    """Run the verb. An InputError or OSError prints `error: <msg>` on stderr and exits 2."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _run(args, parser=parser)
    except (InputError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
