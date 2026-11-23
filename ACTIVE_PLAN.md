# ACTIVE PLAN — an installation that runs its own devpro, and the surface and modules around it

Design: [ACTIVE_DESIGN/entry-point.md](ACTIVE_DESIGN/entry-point.md). Every package's lifetime is
**shipped**. Packages run serially in the shared tree, in the order below.

## Status

| Package | State | Rating | Agent |
|---|---|---|---|
| P1 | landed | expert | `devpro:python-coder` |
| P2 | landed | expert | `devpro:python-coder` |
| P3 | landed | expert | `devpro:python-coder` |
| P4a | dispatchable | expert | `devpro:python-coder` |
| P4b | dispatchable | expert | `devpro:shell-dsl-coder` |
| P4c | dispatchable | expert | `devpro:prompt-engineer` |
| P5 | dispatchable | mechanical | `devpro:tech-writer` |
| P6 | dispatchable | expert | post-plan reviewers |
| P7 | drafted | expert | per the burndown |

## Common to every package

- Project documents: THESIS, SPEC, ARCHITECTURE, CONVENTIONS, read through their `entry-point.md`
  under `PROJECT_DOCS/`, and the design leaves the package cites.
- A design pair is applied to its target verbatim, its relative links rebased to the target's
  directory. `just dev-check-design-deltas-applied` confirms it.
- Every new test states the defect it fails on before the change (the test-precondition clause the
  coder definitions carry); each package's list below names that defect.
- A test failing on behavior the package does not state it changes is reported as a finding, never
  edited to pass.
- Done-line, unless the package states otherwise: `just test`, `just lint`, `just dev-check-links`
  and `just dev-check-design-deltas-applied`, run once at the package's end. Until P4c lands,
  `just dev-check-design-deltas-applied` fails only on the pairs the *Pair assignment* table gives to
  later packages; any other pair it reports is the package's failure.
- Package data is moved with `git mv`, so the wheel check, which compares package data with
  `git ls-files --cached --others --exclude-standard`, sees the move.
- Changing a definition changes the rendered reference slots; they are re-taken after acceptance
  (CONVENTIONS.md, Reference retakes follow acceptance), not by the package.
- Each fact's search excludes the doc trees: run it with `-- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'`;
  their hits are the pairs'. Line numbers are at the plan's base commit, `b9d741c`; a line in a file
  an earlier package edits is cited by its symbol.

## Pair assignment

Each SPEC and ARCHITECTURE pair is cited by its design leaf and its ordinal among that leaf's
`**As it stands:**` blocks. 61 pairs: 25 SPEC, 36 ARCHITECTURE.

| Design leaf | P1 | P2 | P3 | P4a | P4b | P4c |
|---|---|---|---|---|---|---|
| [spec-delta/package-and-command](ACTIVE_DESIGN/spec-delta/package-and-command.md) (2) | | | 1 | 2 | | |
| [spec-delta/surfaces-and-layout](ACTIVE_DESIGN/spec-delta/surfaces-and-layout.md) (2) | | | 1 | 2 | | |
| [spec-delta/plugins](ACTIVE_DESIGN/spec-delta/plugins.md) (8) | | | 1, 2, 3 | 4, 5, 6, 7, 8 | | |
| [spec-delta/install-destination](ACTIVE_DESIGN/spec-delta/install-destination.md) (3) | | | 2, 3 | 1 | | |
| [spec-delta/installed-tree](ACTIVE_DESIGN/spec-delta/installed-tree.md) (4) | | | | 1, 2, 3 | | 4 |
| [spec-delta/shipped-files](ACTIVE_DESIGN/spec-delta/shipped-files.md) (3) | | | 3 | 1 | | 2 |
| [spec-delta/guide-and-readme](ACTIVE_DESIGN/spec-delta/guide-and-readme.md) (2) | | | 1, 2 | | | |
| [spec-delta/write-safety](ACTIVE_DESIGN/spec-delta/write-safety.md) (1) | | | | 1 | | |
| [architecture-delta/harness-profiler](ACTIVE_DESIGN/architecture-delta/harness-profiler.md) (12) | 4, 5 | 3, 6 | 7, 8, 9 | 11, 12 | 1, 2, 10 | |
| [architecture-delta/install-entry](ACTIVE_DESIGN/architecture-delta/install-entry.md) (1) | | | 1 | | | |
| [architecture-delta/packaging](ACTIVE_DESIGN/architecture-delta/packaging.md) (2) | | 2 | | 1 | | |
| [architecture-delta/plugins](ACTIVE_DESIGN/architecture-delta/plugins.md) (4) | | | | 1, 2, 3, 4 | | |
| [architecture-delta/recipes](ACTIVE_DESIGN/architecture-delta/recipes.md) (2) | | | 1, 2 | | | |
| [architecture-delta/renders-and-copies](ACTIVE_DESIGN/architecture-delta/renders-and-copies.md) (3) | | | | 1, 2, 3 | | |
| [architecture-delta/repo-layout](ACTIVE_DESIGN/architecture-delta/repo-layout.md) (4) | | 1, 2, 4 | | 3 | | |
| [architecture-delta/structural-rules](ACTIVE_DESIGN/architecture-delta/structural-rules.md) (1) | | | 1 | | | |
| [architecture-delta/subsystem-map](ACTIVE_DESIGN/architecture-delta/subsystem-map.md) (7) | | | 7 | | 4, 6 | 1, 2, 3, 5 |
| **pairs per package** | 2 | 6 | 18 | 24 | 5 | 6 |

2 + 6 + 18 + 24 + 5 + 6 = 61. The Code delta entry,
[code-delta/harness-profiler](ACTIVE_DESIGN/code-delta/harness-profiler.md), is P1's.

A pair that states two packages' outcomes goes to the later package, and the earlier package
changes the code it describes without applying it: harness-profiler pair 3 (its `LAYER_MARK` and
`served_page` already in the code, `devpro/profiler/pages.py:56`, `:855`; P2's stylesheet path) to P2; packaging pair 1 (P2's `kanban/assets` glob, P4a's `runner-snippets` glob
and the copy) and repo-layout pair 3 (P2's module rows, P4a's `runner-snippets` row) to P4a.

## P1 strict_fill fills literal marks only

Agent `devpro:python-coder`; expert (which index slots become marks and which literal text is the
agent's call).

- **Applies:** the Code delta entry; architecture-delta/harness-profiler pairs 4, 5.
- **Scope:** `devpro/profiler/pages.py` (`strict_fill`, `DATA_SLOT` → `DATA_MARK`, `ZEBRA_MARKS`,
  `HARNESS_MARKS`, `INDEX`), `devpro/profiler/view.html` where a mark it carries changes,
  `tests/test_devpro_profiler.py`.
- **Facts:**
  - `git grep -l -F strict_fill -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `devpro/profiler/pages.py
    tests/test_devpro_profiler.py`.
  - `git grep -l -F DATA_SLOT -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `devpro/profiler/pages.py
    tests/test_devpro_profiler.py`.
  - `git grep -l -F ZEBRA_MARKS -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `devpro/profiler/pages.py`.
  - The index template's slots: `devpro/profiler/pages.py:938-939`,
    `.harness.$class_opencode { background: $opencode; }` and
    `.harness.$class_claude { background: $claude; }`.
  - `strict_fill` splits slots from marks at `devpro/profiler/pages.py:122-123`
    (`name.isidentifier() and name.isascii()`).
- **Tests pinning the behavior:** the `strict_fill` and page-render tests in
  `tests/test_devpro_profiler.py` (the `BAND_LEGEND` fill at `:1200-1203` among them); in scope.
- **New test:** a fill whose value carries another key's mark refuses. Defect: today
  `strict_fill` refuses a value carrying its own mark only, so a value carrying a later mark is
  read as that mark and filled.

## P2 doccheck and kanban module homes

Agent `devpro:python-coder`; expert (the check verbs' argparse moves into a module of their own).

- **Applies:** architecture-delta/harness-profiler pairs 3, 6; architecture-delta/packaging pair 2;
  architecture-delta/repo-layout pairs 1, 2, 4.
- **Scope:**
  - `git mv` `devpro/dicing/kanban/planform.py` and `devpro/dicing/kanban/plancheck.py` into a new
    `devpro/doccheck/` (with `__init__.py` and a new `cli.py` holding `check-plan`, `check-design`
    and `check-roadmap`'s argparse and dispatch, lazy, with `add_verbs` and `run`);
  - `git mv devpro/dicing/kanban` (`__init__.py`, `board.py`, `server.py`, `assets/`) to
    `devpro/kanban/`;
  - `devpro/dicing/cli.py` (drops the three check verbs; keeps `check-links`, `check-tree` and the
    dicing verbs), `devpro/cli.py` (composes `devpro.doccheck.cli.add_verbs` beside the other
    three), `devpro/dashboard/__init__.py`, `devpro/dashboard/server.py`,
    `devpro/profiler/pages.py`, `pyproject.toml` (`dicing/kanban/assets/**/*` →
    `kanban/assets/**/*`);
  - `tests/test_devpro.py` (the exemption tuple of `test_every_import_is_at_module_level`, `:1520`,
    gains `devpro/doccheck/cli.py`, and its comment the fifth entry point; and
    `test_importing_the_entry_point_imports_no_verb_module` (`:1569`) gains
    `('devpro.doccheck', 'devpro.doccheck.cli')`),
    `tests/dicing/test_board.py`, `test_plancheck.py`, `test_planform.py`, `test_server.py`,
    `test_cli_surface.py`, `tests/dashboard/test_server.py`. Tests stay in their directories.
- **Facts:**
  - `git grep -l -F .kanban -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `devpro/dashboard/__init__.py
    devpro/dashboard/server.py devpro/dicing/cli.py devpro/profiler/pages.py
    tests/dashboard/test_server.py tests/dicing/test_board.py tests/dicing/test_plancheck.py
    tests/dicing/test_planform.py tests/dicing/test_server.py`.
  - `git grep -l -F planform -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `devpro/dicing/kanban/board.py
    devpro/dicing/kanban/plancheck.py tests/dicing/test_plancheck.py tests/dicing/test_planform.py`.
  - `git grep -l -F dicing/kanban -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `pyproject.toml` (`:30`,
    `"dicing/kanban/assets/**/*"`).
  - `devpro/dicing/cli.py:166-180` imports `.kanban.plancheck` for the three check verbs.
  - `grep -n '^from \.' devpro/dicing/kanban/*.py` →
    - `planform.py:17-23`: seven `..dicerlib` modules — anchors, heads, linkcheck, linkrewrite,
      linkscan, reassemble, textfile;
    - `plancheck.py:12-13`: `..dicerlib.textfile` and `.planform`;
    - `board.py:21-28`: seven `..dicerlib` modules — heads, linkcheck, linkrewrite, linkscan,
      outline, reassemble, textfile — and `.planform`;
    - `server.py:36-38`: `from ... import __version__`, `..dicerlib.textfile` and `.board`.

    After the move they import `devpro.dicing.dicerlib.*` and `devpro.doccheck.planform`, and
    `server.py`'s `from ... import __version__` is `from .. import __version__`.
- **Target arrows:** `devpro.kanban` → `devpro.doccheck` → `devpro.dicing`; nothing in
  `devpro.dicing` imports `devpro.doccheck` or `devpro.kanban`; nothing in `devpro.doccheck` imports
  `devpro.kanban`. `dicerlib` stays where it is.
- **Tests pinning the behavior:** those listed in scope; `tests/dicing/test_cli_surface.py` pins
  that `devpro --help` lists each verb, which holds unchanged;
  `test_importing_the_entry_point_imports_no_verb_module` pins the lazy registration chains, the
  doccheck pair among them after this package; `test_the_import_graph_is_acyclic`
  (`tests/test_devpro.py`) pins that no module imports one that imports it.
- **New test:** none; the move changes no behavior a test can observe. The one-way package rule
  (repo-layout pair 4) gets no test of its own: one written against `devpro.doccheck` and
  `devpro.kanban` passes before the change, where neither package exists, so it names no defect it
  fails on (`clauses.TEST_PRECONDITION`).

## P3 install surface: the gated maintainer verbs, the retired recipes, the profiler skill

Agent `devpro:python-coder`; expert (where the gate sits in parser construction).

- **Applies:** spec-delta/package-and-command pair 1; spec-delta/surfaces-and-layout pair 1;
  spec-delta/plugins pairs 1, 2, 3; spec-delta/install-destination pairs 2, 3;
  spec-delta/shipped-files pair 3; spec-delta/guide-and-readme pairs 1, 2;
  architecture-delta/harness-profiler pairs 7, 8, 9; architecture-delta/install-entry pair 1;
  architecture-delta/recipes pairs 1, 2; architecture-delta/structural-rules pair 1;
  architecture-delta/subsystem-map pair 7.
- **Scope — the gate:** `devpro/cli.py` (`render` → `dev-render`; `dev-render`,
  `render-agents-file` and `harness` registered only where `DEVPRO_DEV` is `1`),
  `devpro/__init__.py` (its verb list), `devtools/scripts/render.sh`, `_render-slot.sh`,
  `render-agents-file.sh` and `_harness-value.sh` (each exports `DEVPRO_DEV=1` once; none calls the
  `render` verb, per the `"render"` fact), `tests/test_devpro.py`, `tests/test_devpro_install.py`.
- **Scope — the recipes:** `justfile` (the `install` and `install-agents-file` recipes and their
  comment blocks, `justfile:30-47`). No test names them; the documents that do are the two
  CONVENTIONS leaves below and the install-entry and recipes pairs
  (`git grep -n -E 'just install(-agents-file)?([^a-z-]|$)' -- ':!ACTIVE_DESIGN'` →
  `PROJECT_DOCS/ARCHITECTURE/install/install-entry.md:3`, `PROJECT_DOCS/ARCHITECTURE/recipes.md:3`,
  `:4`, and the two CONVENTIONS leaves' `:6` and `:3`).
- **Scope — the rename:** `git mv devpro/definitions/skills/show_profile.py
  devpro/definitions/skills/profiler.py` and its skill name; `devpro/profiler/values.py`
  (`SHOW_SKILL`), `devpro/profiler/hooks.py` (its skill copy and messages; `init` also unlinks
  `.claude/skills/show-profile/SKILL.md` an older `init` wrote, and its directory where that leaves
  it empty, beside the `hp.py`/`view.html` unlink), `devpro/definitions/skills/guide.py` (its
  reference), `tests/test_devpro_install.py` (`_SHOW_PROFILE`), `tests/test_devpro_profiler.py`,
  `tests/profiler_capture_runner.ts`.
- **Scope — CONVENTIONS** (carried by this plan; no design pair covers them):
  - `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/agents-file-changes-explicitly.md`:
    "Adopt with `just install-agents-file <dir> [--harness NAME]`," becomes "Adopt with
    `just dev-devpro install-agents-file <dir> [--harness NAME]`,".
  - `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/install-parameters-ship-with-their-flags.md`:
    "`just install` reaches the verb only through the flags" becomes "`devpro install` reaches the
    verb only through the flags", and "ships a capability no recipe can ask for" becomes "ships a
    capability no command line can ask for".
- **Facts:**
  - `git grep -l -F '"render"' -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `devpro/cli.py
    tests/test_devpro.py tests/test_devpro_install.py`.
  - `git grep -l -F render-agents-file -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `devpro/__init__.py
    devpro/cli.py devtools/scripts/_render-slot.sh devtools/scripts/render-agents-file.sh
    devtools/scripts/render.sh justfile tests/test_devpro_install.py`.
  - The gated verbs run directly in two of the four scripts: `_harness-value.sh:10` runs
    `python3 -m "${GEN}" harness`, `render-agents-file.sh:15` runs `python3 -m "${GEN}"
    render-agents-file`. `render.sh:60` calls `_render-slot.sh`, which calls `_harness-value.sh`
    (`:37-38`) and `render-agents-file.sh` (`:53`) and runs the ungated `install` (`:54`). Each of
    the four is also a recipe body of its own (the `render`, `_render-slot`, `render-agents-file` and
    `_harness-value` recipes, `justfile:126`, `:130`, `:141`, `:145`), so each
    exports `DEVPRO_DEV=1` once, as recipes pair 2 states.
  - `git grep -l -F show-profile -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `README.md
    devpro/definitions/skills/guide.py devpro/definitions/skills/show_profile.py
    devpro/profiler/hooks.py devpro/profiler/values.py tests/profiler_capture_runner.ts
    tests/test_devpro_install.py tests/test_devpro_profiler.py`; `README.md` is P5's.
  - `git grep -l -F SHOW_SKILL -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → `devpro/profiler/hooks.py
    devpro/profiler/values.py`.
  - `git grep -l -F _SHOW_PROFILE -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` →
    `tests/test_devpro_install.py`.
  - `git grep -l -F show_profile -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` → no file; no code names the
    module. The doc trees' one target hit is `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md`,
    subsystem-map pair 7's, the rename's own.
  - `justfile:35` is `install target *args:`; `justfile:46` is `install-agents-file dir *args:`.
- **Tests pinning the behavior:** `tests/test_devpro_install.py:709`
  (`test_the_help_usage_line_lists_every_verb_but_the_hidden_one`), the `render` verb's tests in
  `tests/test_devpro.py` and `tests/test_devpro_install.py`,
  `test_init_lays_down_the_launcher_and_clears_an_older_runs_files` in
  `tests/test_devpro_profiler.py`; in scope.
- **New tests:**
  - Without `DEVPRO_DEV=1`, `devpro --help` lists none of `dev-render`, `render-agents-file`,
    `harness`, and each is refused as an invalid choice. Defect: today `--help` lists `render` and
    `render-agents-file`, and `harness` runs.
  - `init` over a repository holding `.claude/skills/show-profile/SKILL.md` removes it. Defect:
    after the rename an older `init`'s skill stands beside the new one.

## P4a The installation's own copy and wrapper, and the tools package

Agent `devpro:python-coder`; expert (the wrapper's text, the ownerless rows, the version report).

- **Applies:** spec-delta/package-and-command pair 2; spec-delta/surfaces-and-layout pair 2;
  spec-delta/plugins pairs 4, 5, 6, 7, 8; spec-delta/install-destination pair 1;
  spec-delta/installed-tree pairs 1, 2, 3; spec-delta/shipped-files pair 1;
  spec-delta/write-safety pair 1; architecture-delta/harness-profiler pairs 11, 12;
  architecture-delta/packaging pair 1; architecture-delta/plugins pairs 1, 2, 3, 4;
  architecture-delta/renders-and-copies pairs 1, 2, 3; architecture-delta/repo-layout pair 3.
- **Scope:**
  - `git mv devpro/dicing-snippets/runner-snippets devpro/runner-snippets`, removing
    `devpro/dicing-snippets/`; `pyproject.toml` (`dicing-snippets/**/*` → `runner-snippets/**/*`);
  - `devpro/install.py`: `ShippedPackage` owner optional; `SHIPPED_PACKAGES` (`:112`) loses the
    dicing-snippets row and gains `runner-snippets` → `tools/runner-snippets` and the package itself
    (`PACKAGE_ROOT`) → `tools/devpro`, both ownerless; ownerless rows ship on every install, user-level
    included; the copy to `tools/devpro/` takes `_shipped` (`:178`) and no banner
    (`STAMPED_SUFFIXES`, `:159`); the wrapper `tools/devpro.sh` written with the running
    interpreter's base executable, behaving as spec-delta/shipped-files pair 2 states; the report
    names the replaced copy's version (`tools/devpro/__init__.py`) and the installed one; the
    install removes an earlier install's `skills/docdicer/dicing-snippets/` whole, as
    spec-delta/write-safety pair 1 states (the mechanism is this package's call; `--dry-run`
    reports the removal as it reports others);
  - `devpro/install_base.py`, `devpro/runner_file.py` and `devpro/preflight.py` where
    `install._install_managed_paths` (`devpro/install.py:613`; it lists every
    `SHIPPED_PACKAGES` row's `destination`) reaches it;
  - `devpro/profiler/hooks.py` (`devpro_executable`: the installation's wrapper first, then the
    existing search; the doctor's not-found message as harness-profiler pair 12 states). The
    wrapper's root is the repository `doctor` already resolves (`repo = git_root(cwd) or Path(cwd)`
    in `doctor`): `<repo>/.claude/skills/devpro/tools/devpro.sh`, the one file both claude launchers
    in that repository resolve — the committed `.claude/harness-profiler/hp.sh` (`HOOK_DIR`) by
    `../skills/devpro/tools/devpro.sh`, a project install's `.claude/skills/devpro/profiler/hp.sh`
    by `../tools/devpro.sh` (claude's `plugin_dir="skills/{plugin}"`, `devpro/harnesses/claude.py`).
    `devpro_executable` takes that root;
  - `tests/test_devpro_install.py`, `tests/test_devpro_profiler.py`, `tests/test_plugins.py`.
- **Facts:**
  - `git grep -l -F dicing-snippets -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` →
    `devpro/dicing-snippets/runner-snippets/devpro.just devpro/dicing-snippets/runner-snippets/devpro.mk
    devpro/install.py pyproject.toml tests/test_devpro_install.py`.
  - `git ls-files devpro/dicing-snippets` → `devpro.just` and `devpro.mk` under `runner-snippets/`.
  - `git grep -l -F devpro_executable -- ':!ACTIVE_DESIGN' ':!PROJECT_DOCS'` →
    `devpro/profiler/hooks.py`.
  - The include-line tests in `tests/test_devpro_install.py`
    (`test_the_include_line_is_appended_to_an_existing_justfile` through
    `test_the_repositorys_own_project_root_gets_no_include_line`,
    `test_a_project_install_without_the_kbase_component_writes_the_devpro_include_line_only`,
    `test_no_two_snippet_sets_name_the_same_snippet`,
    `test_the_shipped_devpro_snippets_list_the_same_five_recipes_in_both_runners`) recognize a line
    by its `runner-snippets/<snippet>` ending, which the new path keeps.
- **Not yet true at this package's end:** the snippets and the launcher still run `devpro` from
  `PATH`; P4b changes them. Harness-profiler pair 11's "the same search the launcher makes" holds
  once P4b lands. The snippets' header comments still name the retired
  `skills/docdicer/dicing-snippets/` path; P4b rewrites them.
- **Tests pinning the behavior:** the include-line tests above (their expected path becomes
  `tools/runner-snippets/`), the user-level install tests in `tests/test_devpro_install.py`
  (a user-level install now writes `tools/`), the dry-run prediction tests
  (`_assert_dry_run_predicts`), `tests/test_devpro_profiler.py`'s doctor tests; in scope.
- **New tests:**
  - A project install writes `tools/devpro/` byte-equal to the package less `_shipped`'s exclusions,
    and `tools/devpro.sh`; with no `devpro` on `PATH`, `tools/devpro.sh --version` prints the
    package's version. Defect: today no copy is installed, so an installed tree cannot run devpro
    once the system's is removed.
  - The wrapper whose recorded interpreter is gone runs under the first `python3` on `PATH` of 3.9
    or later, and with none exits non-zero naming Python 3.9. Defect: an installed tree whose
    install-time Python has been removed cannot run devpro — today no wrapper is written, so the run
    fails with no `tools/devpro.sh`.
  - Re-installing over a copy of another version reports both versions. Defect: today nothing names
    a version change.
  - A user-level install writes the tools package and no other package. Defect: today a user-level
    install writes no package.
  - An install over a tree holding an earlier install's `skills/docdicer/dicing-snippets/` leaves no
    such directory. Defect: after the move, the retired home's installed-banner files survive `prune`.

## P4b The launcher and the runner snippets run the wrapper

Agent `devpro:shell-dsl-coder`; expert.

- **Applies:** architecture-delta/harness-profiler pairs 1, 2, 10; architecture-delta/subsystem-map
  pairs 4, 6.
- **Scope:** `devpro/harnesses/resources/claude/profiler/hp.sh` (the finder's first candidate is
  the wrapper resolved from the launcher's own location: `../tools/devpro.sh` from
  `<install-dir>/profiler/hp.sh`, `../skills/devpro/tools/devpro.sh` from the committed
  `.claude/harness-profiler/hp.sh`; then the existing `PATH` search; the `--version` probe applies
  to every candidate unchanged, so a wrapper with no usable Python is absent and `capture` exits 0);
  `devpro/runner-snippets/devpro.just` and `devpro.mk` (each recipe runs the wrapper beside the
  snippet's installed directory, `../devpro.sh` relative to the snippet file's own directory — not
  the recipe's working directory, the project root — never `devpro` from `PATH`; the header comments
  say so and name `<harness-relpath>/tools/runner-snippets/`); `tests/test_devpro_profiler.py`,
  `tests/test_devpro_install.py`.
- **Facts:**
  - `devpro/harnesses/resources/claude/profiler/hp.sh:24`:
    `devpro=$(PATH="${PATH}:/opt/homebrew/bin:/usr/local/bin:${HOME}/.local/bin" command -v devpro 2>/dev/null) || devpro=`.
  - The snippets' recipes run `@devpro check-plan`, `@devpro check-design`,
    `@devpro check-design --deltas-applied`, `@devpro check-roadmap`, and `devpro-help` runs
    `@devpro --help` (`devpro/runner-snippets/devpro.just`, after P4a's move).
  - A bare `../devpro.sh` on a recipe line cannot reach the snippet's directory in either runner.
    just runs an imported recipe in the root justfile's directory ("By default, recipes run with the
    working directory set to the directory that contains the `justfile`", just 1.59.0 README,
    *Working Directory*); `source_directory()` (just 1.27.0, under the snippet's 1.33 floor) "will
    return the path and directory, respectively, of the current `import` or `mod` source file when
    called from within an import" (*Source and Source Directory*), so the just recipe runs
    `"{{source_directory()}}/../devpro.sh"`. make runs recipes from its own working directory, the
    project root; `devpro.mk` already holds `DEVPRO_SNIPPET_FILE := $(lastword $(MAKEFILE_LIST))`,
    expanded at parse, and `DEVPRO := devpro` is the one spelling its gate recipes use, so `DEVPRO`
    becomes `$(dir $(DEVPRO_SNIPPET_FILE))../devpro.sh` and `devpro-help`'s `@devpro --help` uses it.
  - `test_a_launcher_finding_an_unusable_devpro_captures_silently_and_reports_otherwise`
    (`tests/test_devpro_profiler.py`) pins the probe.
- **Tests pinning the behavior:** in `tests/test_devpro_profiler.py`,
  `test_a_launcher_finding_an_unusable_devpro_captures_silently_and_reports_otherwise`,
  `test_init_lays_down_the_launcher_and_clears_an_older_runs_files`,
  `test_doctor_reports_a_committed_launcher_that_differs_from_the_resource`; in
  `tests/test_devpro_install.py`,
  `test_the_shipped_devpro_snippets_list_the_same_five_recipes_in_both_runners`; in scope.
- **New tests:**
  - With no `devpro` on `PATH` and an installed wrapper beside the launcher, `hp.sh capture claude`
    records the call. Defect: today the launcher finds only `devpro` on `PATH` and records nothing.
  - With no `devpro` on `PATH`, `just devpro-check-plan` through an installed snippet runs the check.
    Defect: today the recipe fails with `devpro: not found`.

## P4c Session commands run the installation's wrapper

Agent `devpro:prompt-engineer`; expert (which sentences give a session a command).

- **Applies:** spec-delta/installed-tree pair 4; spec-delta/shipped-files pair 2;
  architecture-delta/subsystem-map pairs 1, 2, 3, 5.
- **Scope:** `devpro/definitions/skills/docdicer.py`, `devpro/definitions/skills/profiler.py` (P3's
  rename), `devpro/definitions/skills/guide.py`: every command they give a session to run devpro
  names `../../tools/devpro.sh`, the wrapper relative to the skill's directory, except
  `devpro install`, `devpro install-agents-file` and `devpro --version`, which keep the `devpro`
  command on `PATH`. `docdicer.py`'s recipe list drops the bare `devpro` recipe, which the snippets
  no longer define (removed in `e057582`).
- **Facts** (re-run at dispatch: P3 edits `guide.py` and the renamed skill):
  - ``git grep -n -F '`devpro ' -- devpro/definitions/skills`` → `docdicer.py:48`, `:58`;
    `guide.py:47`, `:64`, `:66`, `:68`, `:88`, `:97`, `:109`, `:114`, `:122`, `:124`, `:158`,
    `:199`, `:469`, `:472`; `show_profile.py:43` (`profiler.py` after P3). `show_profile.py:48` is
    a bare `devpro dashboard` command line in a fenced block, which the search does not match. Of
    these, `guide.py`'s install, install-agents-file and `--version` lines keep the `devpro`
    command; `guide.py:109` (`devpro profiler doctor`), `:469`, `:472` and the other skills' verbs,
    `show_profile.py:48` among them, move to the wrapper.
  - ``git grep -n -F '`devpro`' -- devpro/definitions/skills`` → `docdicer.py:2`, `:47`, `:52`,
    `:53`, `:56`; `guide.py:20`, `:45`, `:61`, `:62`, `:74`. `docdicer.py:47` ("the dicing verbs of the
    `devpro` command") and `:56` ("a direct `devpro` call for any other") move to the wrapper
    (subsystem-map pairs 1, 2); `:53` ("(`devpro`, and by name `devpro-help`,") drops the bare
    `devpro` recipe (subsystem-map pair 6's text). `guide.py:61-62` ("Every later `devpro` command
    runs as the `devpro` of that install") is scoped to the install, update and `--version`
    commands. `docdicer.py:2` (the module docstring), `:52` (the snippet set's name), `guide.py:20`
    and `:45` (the installer) and `:74` (the include line) give no command and stand.
- **Tests pinning the behavior:** none pins the commands' text; the rendering tests in
  `tests/test_devpro.py` hold unchanged.
- **New test:** none; a test of the definitions' text would be a checksum.
- **Done-line:** `just test`, `just lint`, `just dev-check-links`,
  `just dev-check-design-deltas-applied`, every pair reported landed.

## P5 README: the profiler skill and the supported platforms

Agent `devpro:tech-writer`; mechanical, step-down `comm-mechanical=haiku` through the dispatch's
`model` parameter.

- **Scope:** `README.md`, these edits only:
  - `:74` and `:80`: `show-profile` → `profiler`;
  - `:174-175`: `the \`show-profile\` skill: \`devpro:show-profile\` under claude and mage,
    \`devpro-show-profile\` under opencode.` → `the \`profiler\` skill: \`devpro:profiler\` under
    claude and mage, \`devpro-profiler\` under opencode.`;
  - `:159-160`: `native Windows is unsupported for the component.` → `native Windows is unsupported
    for the devpro plugin, the component included.`
- **Facts:** `git grep -n -F show-profile README.md` → `:74`, `:80`, `:174`, `:175`.
- **Done-line:** `just dev-check-links`; `git grep -c -F show-profile README.md` answers nothing.

## P6 Post-plan review

Reviewers, each writing its own review under `.devpro-temp/`, given the project documents and the
design, not this plan: `devpro:python-coder`, `devpro:shell-dsl-coder`, `devpro:architect`,
`devpro:prompt-engineer` (definitions, project documents) and `devpro:tech-writer` (README) — five
agents. The session synthesizes their reviews into `ACTIVE_PLAN_REVIEW.md`; this row is `landed` in
the commit that adds it.

## P7 Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
