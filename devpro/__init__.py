"""devpro: agent definitions as code.

A definition module is its rendered text with holes: `DEFINITIONS`, a tuple of
`Definition` values whose body is a string built at import from the module's
own triple-quoted text and the shared text of `devpro.clauses`, so two
definitions cannot disagree about text they share. The only holes left for
render time are the placeholders `vocabulary.hole` spells for a harness string
or a family overlay anchor, filled once by `render.filled_body`.

    errors.py        the one error, InputError, reported as exit 2
    vocabulary.py    categories, tools, anchors, kinds, harness texts and the placeholder spelling
    loading.py       the one loader of the instance packages below
    definition.py    the Definition and SkillFile values: kind, output paths, frontmatter values, text
    clauses.py       shared text: constants, and small functions for text with slots
    harness.py       the harness dataclass, its `{plugin}` templates and their binding
    harnesses/       one module per harness, each defining HARNESS
    components.py    the one name every install takes and each optional component's member list
    family.py        the family dataclass and its overlays, and how to author one
    families/        one module per family, each defining FAMILY
    context.py       Render, the devpro settings file and the map's grammar
    definitions/     one module per definition, each defining DEFINITIONS; the modules that render
                     agents and skills sit in agents/ and skills/, the agents file's at the top
    render.py        definition to file text, the banner, the writer, and the agents file's text
    install_target.py where an install lands: its harness, harness directory and project root, from the target
    preflight.py     the install run into a scratch copy first: up to date, --dry-run, or the real run
    install_base.py  what the install modules share: package and checkout roots, the kb-tools package
                     paths, path checks, UTF-8 reading
    runner_file.py   the runner include lines, one per snippet set the install passes in
    install.py       the install: renders, the shipped packages' stamped copy, and the prune
    agents_file.py   the agents-file install: the marker span, redirects, and the rolling backup
    cli.py           the argparse surface
    __main__.py      the `-m` entry

Usage, where `python3 -m devpro` is the same command as `devpro`; a checkout
runs it from the repository root with that root on PYTHONPATH:

    devpro install TARGET [--components=CSV] [--subdir DIR] [--verbose]
        [--dry-run] [--harness NAME] [--family NAME] [--config-file=FILE]
    devpro install-agents-file DIR [--harness NAME] [--dry-run]
    devpro --version

and, only where the environment's DEVPRO_DEV is 1, the maintainer verbs:

    devpro dev-render --out DIR [--components=CSV] [--harness NAME] [--family NAME]
        [--config-file=FILE]
    devpro render-agents-file HARNESS OUT [--components=CSV]
    devpro harness NAME KEY

The one name is `components.NAME`: every install writes it, and every `{plugin}` template fills it.
`--components` turns optional components on, comma-separated. The render is deterministic:
the text of every file is a function of the definition, the components, the harness,
the family and the category map, and of nothing else.
"""

__version__ = "0.18.0"
