# Recipes

`just agents`, `just render`, `just retake-reference`, `just tag`, `just check-wheel` and
`just dev-dashboard` reach `python3 -m devpro`; no recipe stands in front of `install` or
`install-agents-file`, which are reached as verbs of the command alone (Install, Install entry).
`agents` builds the wheel and installs this repository's own set from the built package beside it
(Install, Installing this repository), the target alone and any `install` flags it passes through —
an alternate `--config-file` among them — with no
`--components` and no `--harness` flag by default, the harness left to the install's own inference;
`render` and `retake-reference` go through the private `_render-slot.sh`, which calls
`python3 -m devpro install <slot>/devpro --components=kbase` with `--subdir=` once,
into `<slot>/devpro/`, where a nested plugin's install also writes the project's `AGENTS.md` and,
under claude, the `CLAUDE.md` redirect beside it (Agents File, Placement), and through the private
`render-agents-file HARNESS OUT` script, which may be an
earlier revision's copy run inside that revision's worktree, where that worktree's own justfile
supplies `GEN` and the worktree holds the package `GEN` names. `tag` goes through `--version`, which
prints the version bare and nothing else, so the `v` of `v<version>` is the recipe's;
`check-wheel` through `--version` and through a working-tree `install` (see the paragraph on `build`
below).
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
comparison — that interpreter is the `install` that reach runs, and the one the floor guard refuses
where it is below the floor, before the venv is made — so the wrapper records one interpreter on both
sides; it runs the `devpro` console script only from that throwaway venv. Packaging states both.

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
The suite needs `bun`, `perl` and `kbase` (at least `KBASE_MIN_VERSION`) on `PATH`, and `firefox`
for the `slow` surface, whose screenshot test drives it.
`tests/test_guardrail.py`, `tests/test_opencode_entry.py`, `tests/test_kbase_surface.py` and
`devtools/tests/test_screenshot.py` fail rather than skip without the one they need, because a skip
would hide drift. `just lint` needs `shellcheck` on
`PATH`, and where it is absent the recipe fails, naming it, rather than skip the shell check.
`just lint` also type-checks what ships: the opencode harness's shipped TypeScript resources
(`index.ts`, `guardrail.ts`, `profiler.ts`) through `bunx tsc --noEmit` under a `tsconfig`, checked
against the host's published declarations — `@opencode/plugin`'s own types are the authority, no
devpro-owned stand-in for a published package shadows them. The declarations reach the check as a
dev-time dependency installed before `tsc` runs — a root `package.json` holds it, and the pin's
version has no second home: a resource's header keeps the floor it already names and names no
version of the moment — and the check
reads what ships: the host's transitive declarations are not this check's mandate, `skipLibCheck`
keeping the program over the resources. The check settles the declared surface only: where the
host's runtime reports something its declarations do not publish, the reads are observed, shipped
behavior and the gap is the opencode doc's. The compiler rides unpinned — `bunx` takes the latest at
run time. The check's mandate is what ships: the test runners' TypeScript is dev-time only and
outside it. One more pass, `bunx tsc -p devtools/tsconfig.json --noEmit`, type-checks the
repository's own `devtools/screenshot.ts` under `devtools/tsconfig.json`: a dev tool, checked though
it does not ship. One more still type-checks the Python: mypy in its strict mode over `devpro/` and
`devtools/`, run through the venv's own interpreter, nothing bespoke built around it — the checker a
`dev`-group dependency like the venv's other tools, its configuration `pyproject.toml`'s, a line
with the compatible-release specifier the group's lines already take. The gate's paths are mypy's
arguments — the package and the dev tool; the recipe's other checks' arguments are not the gate's,
and `tests/` stays outside them until a test tree's signal proves worth the
quieting its fixture indirection asks. A checker release changes what the gate reports only with a
change to the group line: the pin is the record, as the other tools' are.

`just screenshot <page> [--base <url>] [--viewport <W>x<H>] [--color-scheme light|dark]
[--wait-for <selector>] [--timeout <ms>] [--out <png>]` runs
`devtools/screenshot.ts` under bun: `puppeteer-core`, a dev dependency in the same root
`package.json`, drives the `firefox` on `PATH` headless over WebDriver BiDi — Puppeteer owning the
profile, the flags and the handshake, no browser downloaded — settles the page as the load lands,
the fonts come ready and the selector appears where one is given, then, where no selector was given,
waits for network idle within a bound and advisably — its expiry never fails the run, since a page
that keeps requesting is still ready to shoot — and writes a PNG, by default under
`.devpro-temp/screenshots/`, printing its path. It is the development loop's view of a rendered page
and asserts nothing about the pixels. The private `_js-deps` recipe installs that
`package.json`'s dependencies from `bun.lock`, frozen, for `screenshot`, `lint` and `test`;
`just js-lock` installs them unfrozen, rewriting `bun.lock`, after a change to that
`package.json`'s dependencies.
