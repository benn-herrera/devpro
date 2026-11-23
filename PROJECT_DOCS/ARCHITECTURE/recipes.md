## Recipes

`just agents`, `just render`, `just retake-reference`, `just tag`, `just check-wheel` and
`just dev-dashboard` reach `python3 -m devpro`; no recipe stands in front of `install` or
`install-agents-file`, which are reached as verbs of the command alone (Install, Install entry).
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
Scripts read a harness's `HarnessText` values through `python3 -m devpro harness NAME KEY`: the
maintainer scripts' reader, and not part of the consumer CLI. It, `dev-render` and
`render-agents-file` are registered at parser build only where `DEVPRO_DEV` is `1` (SPEC.md,
Package and Command); each script that runs one of them — `render-agents-file.sh` and
`_harness-value.sh` — exports `DEVPRO_DEV=1` once. The `{plugin}`-templated keys
bind to the one plugin, so `harness` takes no selection flag. `devtools/scripts/_harness-value.sh` is the one shell reader of harness
values, for `_render-slot.sh`. The
version is read through `python3 -m devpro --version`. `just tag` reads it there to create the signed annotated tag `v<version>`: it refuses while
`devpro/` has uncommitted changes and again while that tag already exists, and it pushes nothing.
CONVENTIONS.md states where the version is written down, and the order a bump takes against its tag.

`just build` runs `python -m build --no-isolation` in `.venv` and runs no devpro.
`just check-wheel` reaches `python3 -m devpro` from the working tree for the version, and the
throwaway venv's Python with `PYTHONPATH` at the working tree for the checkout side of its install
comparison, so the wrapper records one interpreter on both sides; it runs the `devpro` console
script only from that throwaway venv. Packaging states both.

**Toolchain.** This repository's justfile needs `just` 1.27.0 or later, for the `[doc]` recipe
attribute; a consuming project's floor is 1.33.0 or later where the devpro line ships — the include
line the install writes into the consuming project's runner file, on every project install — for
the `import?` it uses, the kb line with the kbase component riding the same floor (README.md, and
SPEC.md, Guide and README). It runs its recipes under
`bash`. The dicing and check verbs run through the `devpro` command — `python3 -m devpro` in the
checkout's venv — so no import or snippet stands between this checkout and its `docs` surface:
`just check-links` runs the absorbed verb directly. A design's delta application is verified by
`check-design --deltas-applied`; this repository runs it as
`just dev-check-design-deltas-applied`, over the absorbed verb. `dev-dashboard` runs the dashboard
verb with any further arguments through to it — `just dev-dashboard --port 8791` pins the port —
and the board is the dashboard's landing surface: the URL opens on it, at `/board/`, and the
profiler view is the second view at `/profiler/`. The
dev-check recipes run the absorbed verbs. The `_venv`
recipe creates `.venv`
where its python is absent or older than the floor, from the first `python3` on `PATH`. It installs
the `dev` dependency group `pyproject.toml` declares, with pip, so the first run needs the network.
The suite needs `bun`, `perl` and `kbase` (at least `KBASE_MIN_VERSION`) on `PATH`.
`tests/test_guardrail.py`, `tests/test_opencode_entry.py` and `tests/test_kbase_surface.py` fail
rather than skip without them, because a skip would hide drift. `just lint` needs `shellcheck` on
`PATH`, and where it is absent the recipe fails, naming it, rather than skip the shell check.
