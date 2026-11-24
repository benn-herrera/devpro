## Repo Layout

```
PROJECT_DOCS/           the contract trees — THESIS, SPEC, ARCHITECTURE, CONVENTIONS — as small leaf files, one `entry-point.md` per volume; the root `THESIS.md`, `SPEC.md`, `ARCHITECTURE.md` and `CONVENTIONS.md` are pointers to them, not sources; checked by `just check-links`
agent-sandboxing/       setup for running a coding agent as an unprivileged local user — never installed
images/                 the images README.md shows (`kanban.webp`, the board) — never installed and not package data; checked by `just check-links` through README's links
pyproject.toml          the package's build configuration — setuptools, the version read from `devpro.__version__`, the package-data globs, the `devpro` console script (Packaging)
dist/                   gitignored build product — what `just build` writes: the wheel and sdist; created on demand
rendered/               gitignored build product — this repo's own rendered tree, one slot per rendering, each holding one slot project (`rendered/<slug>/devpro/`), and the four `reference*` slots, one per harness plus gemma, `render-diff` compares against (justfile RENDERED_DIR); created on demand
homebrew-tap/           gitignored hosted clone — the tap this project's formula lives in (`Formula/devpro.rb`), cloned beside this repository by `just tap-repo` and updated by `just tap-update` (Homebrew Delivery); never installed and not package data
devpro/                 the generator package, run as python3 -m devpro — definitions as Python values rendered into a named output root; the package docstring lists its modules
  components.py         the definition selection: the member lists of the optional components (`kbase`), the required set being every discovered definition no component names, with `ships(name)` (Rendering, Harnesses and families); which definitions ship is SPEC.md, Deployed Surfaces, Plugins (CONVENTIONS.md, Plugin membership has one home)
  kb-tools/             shipped package, owned by `kbase` and so delivered only with the kbase component — the runner snippets (kb.just, kb.mk) a project install writes the consuming project's include line for, which run `kbase` from `PATH`; nothing importable; installed under <install-dir>/skills/kbase/kb-tools/, inside the kbase skill's own directory (KB_TOOLS_DIR, devpro/install_base.py)
  preflight.py          the install preflight — the unchanged install run into a scratch copy of the paths it manages and compared with the real paths, behind the up-to-date report and `--dry-run` (Install, Renders and copies)
  profiler/             the absorbed activity profiler — the harness-profiler project's capture, tree, page render and committed-hook wiring as devpro code, run as the `profiler` verb's `capture`, `tree`, `init`, `doctor` and `repair`, its records served by the `dashboard` verb's profiler view (Install, Harness profiler); importable Python, standard library only, carrying `view.html` and the decoration's `deco.js` as the package data its render and the dashboard's pages read (Packaging), its stores and the install migration devpro/install.py calls (`stores.py`), beside the committed-hook wiring in `hooks.py`; it ships no harness resource, its commands running the tree's own wrapper (Install, Harness profiler)
  dashboard/            the dashboard verb and devpro's one loopback server — `cli.py` the verb's argparse surface, `server.py` the server on `127.0.0.1`, the `/` redirect to `/board/`, the `/profiler/` and `/page/<session-id>` routes of the profiler view, the `/api/state` endpoint the nav's deco polls on every view, the `/board/` and `/api/*` routes it hands to the board panel, and the one host guard and reply both panels' handlers share; the rendering is neither file's, the profiler view `devpro/profiler/pages.py`'s index and pages as they stand and the board panel `devpro/kanban`'s (Install, Harness profiler); importable Python, standard library only. Its project root is `dashboard_root`'s walk, the check verbs' `planform.find_project_root`'s deliberate twin: the walk is repeated rather than shared, so the dashboard's root walk calls nothing of the check seam; through its board panel the dashboard loads `doccheck/`'s model, and runs none of the check verbs. The two differ where their callers do: `find_project_root` answers None where no `.git` sits above, and the check verbs refuse; `dashboard_root` falls back to the directory named — or the directory the command runs in — and serves it
  dicing/               the absorbed dicing package — the docdicer project's dicer and its tree and link checks as devpro code, run as devpro's dicing verbs, `check-links` and `check-tree` among them (Dicing and Checks); importable Python, the absorbed project's contract documents carried into Dicing and Checks, its tests joining the devpro test surface
  doccheck/             the workflow documents' validation — `planform.py` the model of the plan, design and roadmap forms, `plancheck.py` the check verbs' implementation, `cli.py` the `check-plan`, `check-design` and `check-roadmap` verbs' argparse and dispatch (Packaging); importable Python
  kanban/               the board, the dashboard's board panel — it presents the document set `doccheck/`'s model reads and validates nothing itself; importable Python, its assets (kanban/assets/) package data (Packaging)
  runner-snippets/      shipped in the devpro tools package, delivered by every install — the runner snippets (devpro.just, devpro.mk) a project install writes the consuming project's include line for, which run devpro through the installation's wrapper, `tools/devpro.sh`; nothing importable; installed under <install-dir>/tools/runner-snippets/ (the `SHIPPED_PACKAGES` row, devpro/install.py)
  development-tools/    shipped package, owned by `development` and so delivered by every project install — `cold-read.sh`, a bash script that runs one agent on one brief with no tools; nothing importable; installed under <install-dir>/skills/development/scripts/, inside the development skill's own directory (DEVELOPMENT_SCRIPTS_PACKAGE, devpro/install.py)
  harnesses/resources/  one directory per harness, named for it — the harness resources that harness ships, copied into the plugin's install directory as they stand and never rendered (HARNESS_RESOURCES_SOURCE, devpro/install.py); `opencode/index.ts` (the plugin entry), `opencode/guardrail.ts` and `opencode/profiler.ts` (the activity capture, Install, Harness profiler), and `claude/hooks/guardrail.pl` and `claude/hooks/state-table-reminder.sh`, and no `__init__.py`, so `load` still reads one harness per module; mage ships none
devtools/               repository-maintenance tooling — never installed; imported from the devpro project root as `devtools.*`
  scripts/              the shell scripts behind the justfile recipes (justfile)
  reference-maps/       the two static devpro settings files `retake-reference` names with --config-file, one harness's model map each (justfile)
  render_diff.py        the text comparison of two rendered slots (justfile `render-diff`); reads rendered output only and never imports the generator
  clause_join_sites.py  the list of definition-body units that join a `clauses.*` interpolation to the module's own text (justfile `clause-join-sites`); splits units with `render_diff.py`'s line classification, `line_kinds`
  dupe_sweep/           the duplication sweep, run as `python3 -m devtools.dupe_sweep` — enumerates one-idea-two-places candidates over the owned python trees, the string literals the trees carry among its sentence units (justfile `sweep-python`)
    __init__.py         package docstring (what the sweep is for, its passes, candidates not verdicts)
    __main__.py         the `-m` entry
    corpus.py           the corpus read from git, never a directory walk; the sweep's error
    clustering.py       units, containment scoring, shingle-blocked clustering, union-find grouping
    normalization.py    text to lower-cased words, `@!…!@` placeholders dropped
    python_corpus.py    what the python pass reads: `CODE_PREFIXES` — devpro, devtools — less `CODE_UNSWEPT`, parsed
    shapes.py           one concept, two implementations: function structural shapes
    constants.py        one constant, two definitions: module-level literals and their candidates
    doc_sentences.py    one rule, two homes: docstring and comment sentences
    definition_text.py  one rule, two homes: the sentences the definition modules carry as string literals, docstrings left to `doc_sentences.py`
    report.py           headers, candidate lists, the file-pair tally
    passes.py           the `python` pass and its defaults
    cli.py              argparse surface and dispatch
  tests/                the devtools test suite — dupe_sweep (`test_dupe_sweep` and its import-structure test), clause_join_sites and render_diff — run as the `dupe_sweep` test surface (`just test dupe_sweep`)
tests/                  the root test suite, the `devpro` package's tests and the repository-wide checks, run as the `devpro` test surface (`just test devpro`) with the `cold_read` marker excluded by default — the cold-read suite's subprocess cases run as the `cold-read` surface (`just test cold-read`) — never installed
```

The package's modules depend one way: `kanban/` imports `doccheck/` and `dicing/`,
`doccheck/` imports `dicing/`, `profiler/` reads `kanban/`'s stylesheet as package data,
`dashboard/` imports the panels it serves, and none of them depends on a module that depends on it.

The three deployed surfaces are absent from this listing: no rendered definition is checked in, so
there is no copy to serve from, compare against or drift from; each is rendered to order into the
output root an invocation names.
