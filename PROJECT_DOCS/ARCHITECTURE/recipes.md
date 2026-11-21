## Recipes

`just install <target> [--components=CSV]`, `just agents`, `just render`,
`just retake-reference`, `just install-agents-file <dir> [--harness=NAME] [--dry-run]`,
`just tag` and `just check-wheel` reach `python3 -m devpro`: `install`,
`agents` and `install-agents-file` each run the verb directly in
one line; `install` takes `target *args` and `install-agents-file` takes `dir *args`,
and each forwards all of it as `"$@"`, so `--components=CSV`, `--harness=NAME` and `--dry-run` all
reach the verb, which defaults the components to none;
`agents` installs the devpro set into this checkout in one line — the target alone, no
`--components` and no `--harness` flag, the harness left to the install's own inference;
`render` and `retake-reference` go through the private `_render-slot.sh`, which calls
`python3 -m devpro install <slot>/devpro --components=kbase` with `--subdir=` once,
into `<slot>/devpro/`, where a nested plugin's install also writes the project's `AGENTS.md` and,
under claude, the `CLAUDE.md` redirect beside it (Agents File, Placement), and through the private
`render-agents-file HARNESS OUT` script, which may be an
earlier revision's copy run inside that revision's worktree, where that worktree's own justfile
supplies `GEN` and the worktree holds the package `GEN` names. `tag` goes through `--version`, which
prints the version bare and nothing else, so the `v` of `v<version>` is the recipe's;
`check-wheel` through `--version` and through `install` (see the paragraph on `build` below).
Scripts read a harness's `HarnessText` values through
`python3 -m devpro harness NAME KEY`: the maintainer
scripts' reader, hidden from `--help` and not part of the consumer CLI. The `{plugin}`-templated keys
bind to the one plugin, so `harness` takes no selection flag. `devtools/scripts/_harness-value.sh` is the one shell reader of harness
values, for `_render-slot.sh`. The
version is read through `python3 -m devpro --version`. `just tag` reads it there to create the signed annotated tag `v<version>`: it refuses while
`devpro/` has uncommitted changes and again while that tag already exists, and it pushes nothing.
CONVENTIONS.md states where the version is written down, and the order a bump takes against its tag.

`just build` runs `python -m build --no-isolation` in `.venv` and runs no devpro.
`just check-wheel` reaches `python3 -m devpro` from the working tree for the version and for the
checkout side of its install comparison, and runs the `devpro` console script only from its
throwaway venv. Packaging states both.

**Toolchain.** This repository's justfile needs `just` 1.27.0 or later, for the `[doc]` recipe
attribute; a consuming project's floor is 1.33.0 or later where the kbase component ships, for the
`import?` of the kb include line
(SPEC.md, Guide and README). It runs its recipes under
`bash`. The dicing and check verbs run through the `devpro` command — `python3 -m devpro` in the
checkout's venv — so no import or snippet stands between this checkout and its `docs` surface:
`just check-links` runs the absorbed verb directly. A design's delta application is verified by
`check-design --deltas-applied`; this repository runs it as
`just dev-check-design-deltas-applied`, over the absorbed verb. The `docdicer-repo`, `dev-dd` and
`dev-kanban` recipes, and `docdicer-repo.sh` with its test, retire with the hosted clone; the
dev-check recipes run the absorbed verbs. The `_venv`
recipe creates `.venv`
where its python is absent. On macOS it makes it from `/usr/bin/python3` where present, the Xcode
command-line tools' Python 3.9.6, so the suite there runs on the Python 3.9 floor. It installs the
pinned tools with pip, so the first run needs the network. The suite needs `bun`, `perl` and
`kbase` (at least `KBASE_MIN_VERSION`) on `PATH`. `tests/test_guardrail.py`,
`tests/test_opencode_entry.py` and `tests/test_kbase_surface.py` fail rather than skip without
them, because a skip would hide drift.
