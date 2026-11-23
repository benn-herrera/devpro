# ACTIVE PLAN — an installation that runs its own devpro, and the surface and modules around it

Design: [ACTIVE_DESIGN/entry-point.md](ACTIVE_DESIGN/entry-point.md). Every package's lifetime is
**shipped**. Packages run serially in the shared tree, in the order below.

## Status

| Package | State | Rating | Agent |
|---|---|---|---|
| P1 | landed | expert | `devpro:python-coder` |
| P2 | landed | expert | `devpro:python-coder` |
| P3 | landed | expert | `devpro:python-coder` |
| P4a | landed | expert | `devpro:python-coder` |
| P4b | landed | expert | `devpro:shell-dsl-coder` |
| P4c | landed | expert | `devpro:prompt-engineer` |
| P5 | landed | mechanical | `devpro:tech-writer` |
| P6 | landed | expert | post-plan reviewers |
| P7a | in progress | expert | `devpro:python-coder` |
| P7b | dispatchable | expert | `devpro:python-coder` |
| P7c | dispatchable | expert | `devpro:shell-dsl-coder` |
| P7d | dispatchable | expert | `devpro:prompt-engineer` |
| P7e | in progress | expert | `devpro:tech-writer` |

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
`**As it stands:**` blocks. 67 pairs: 27 SPEC, 40 ARCHITECTURE. The table below assigns P1–P4c's
61; P7's table assigns the six P7 added and the two whose Becomes P7 amended.

| Design leaf | P1 | P2 | P3 | P4a | P4b | P4c |
|---|---|---|---|---|---|---|
| [spec-delta/package-and-command](ACTIVE_DESIGN/spec-delta/package-and-command.md) (2) | | | 1 | 2 | | |
| [spec-delta/surfaces-and-layout](ACTIVE_DESIGN/spec-delta/surfaces-and-layout.md) (2) | | | 1 | 2 | | |
| [spec-delta/plugins](ACTIVE_DESIGN/spec-delta/plugins.md) (9) | | | 1, 2, 3 | 4, 5, 6, 7, 8 | | |
| [spec-delta/install-destination](ACTIVE_DESIGN/spec-delta/install-destination.md) (3) | | | 2, 3 | 1 | | |
| [spec-delta/installed-tree](ACTIVE_DESIGN/spec-delta/installed-tree.md) (5) | | | | 1, 2, 3 | | 4 |
| [spec-delta/shipped-files](ACTIVE_DESIGN/spec-delta/shipped-files.md) (3) | | | 3 | 1 | | 2 |
| [spec-delta/guide-and-readme](ACTIVE_DESIGN/spec-delta/guide-and-readme.md) (2) | | | 1, 2 | | | |
| [spec-delta/write-safety](ACTIVE_DESIGN/spec-delta/write-safety.md) (1) | | | | 1 | | |
| [architecture-delta/harness-profiler](ACTIVE_DESIGN/architecture-delta/harness-profiler.md) (12) | 4, 5 | 3, 6 | 7, 8, 9 | 11, 12 | 1, 2, 10 | |
| [architecture-delta/install-entry](ACTIVE_DESIGN/architecture-delta/install-entry.md) (2) | | | 1 | | | |
| [architecture-delta/installing-this-repository](ACTIVE_DESIGN/architecture-delta/installing-this-repository.md) (1) | | | | | | |
| [architecture-delta/packaging](ACTIVE_DESIGN/architecture-delta/packaging.md) (3) | | 2 | | 1 | | |
| [architecture-delta/plugins](ACTIVE_DESIGN/architecture-delta/plugins.md) (4) | | | | 1, 2, 3, 4 | | |
| [architecture-delta/recipes](ACTIVE_DESIGN/architecture-delta/recipes.md) (2) | | | 1, 2 | | | |
| [architecture-delta/renders-and-copies](ACTIVE_DESIGN/architecture-delta/renders-and-copies.md) (4) | | | | 1, 2, 3 | | |
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
  - `tests/test_devpro_install.py`, `tests/test_devpro_profiler.py`, `tests/test_plugins.py`,
  `devtools/scripts/check-wheel.sh` (its checkout-side install runs under the venv interpreter, so
  the wrapper's recorded interpreter is the same on both sides of its comparison).
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

Agent `devpro:tech-writer`; mechanical. The step-down model was resolved at dispatch, not recorded
here — the plan's first form named `comm-mechanical=haiku`, a literal model name from a stale pin
set, no such model on the menu; the correction's record is the P5 landing commit.

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

Each item is a finding in [ACTIVE_PLAN_REVIEW.md](ACTIVE_PLAN_REVIEW.md), cited by its ID; the
finding carries its evidence and its fix, and the package applies that fix. Line numbers are at
`2369903`.

New or amended pairs, added to the design for R1, R11, R15 and U1, cited by leaf and ordinal as
*Pair assignment* cites them. An amended pair's target holds its earlier Becomes; the package
replaces that text with the pair's current Becomes.

| Design leaf | pair | package |
|---|---|---|
| spec-delta/package-and-command | 1 (its Becomes amended for R11) | P7a |
| spec-delta/shipped-files | 2 (its Becomes amended for R1) | P7a |
| spec-delta/plugins | 9 | P7a |
| architecture-delta/install-entry | 2 | P7a |
| architecture-delta/renders-and-copies | 4 | P7a |
| architecture-delta/installing-this-repository | 1 | P7a |
| architecture-delta/packaging | 3 | P7a |
| spec-delta/installed-tree | 5 | P7d |

Until P7d lands, `just dev-check-design-deltas-applied` fails only on spec-delta/installed-tree
pair 5; any other pair it reports is the package's failure.

### P7a Post-plan burndown: the install

Agent `devpro:python-coder`; expert (the wrapper's bootstrap form, within R2's bound below, and the
refusal's placement are the agent's call).

- **Items:**
  - R1 (its SPEC half is spec-delta/shipped-files pair 2, not Install destination; the refusal's
    scope is that pair's: an install run from an installation's own copy into the installation
    holding that copy);
  - R2, bounded: the bootstrap adds no installed path. SPEC Shipped files names `tools/`'s contents
    whole (`tools/devpro/`, `tools/devpro.sh`, `tools/runner-snippets/`), so what the wrapper runs
    is the wrapper itself or lives inside `tools/devpro/`;
  - R3; R8 (the `_WRAPPER_TEXT` half: its `cd`, `devpro/install.py:201`, runs with `CDPATH=`);
  - U1 (this repository's runner file gets its include lines as any project's does);
  - R11 (the SPEC pair only); R27; R28; R30 (`base_interpreter`, the `install.py` module docstring,
    the dead `pop` and reassignment in `tests/test_devpro_install.py`).
- **Applies:** the seven P7a pairs above. The two amended pairs' earlier Becomes stand in their
  targets, so each lands as an edit to that text:
  - spec-delta/package-and-command pair 1: in `PROJECT_DOCS/SPEC/package-and-command.md:9`, the
    clause "and the same arguments install the same product, byte for byte." is replaced by the
    pair's Becomes from "and the same arguments under the same Python" through "(Deployed
    Surfaces, Shipped files)."; the rest of the pair's Becomes already stands.
  - spec-delta/shipped-files pair 2: in `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:70-71`,
    the sentence "An install run from an installation's own copy, …, as the one that installs." is
    inserted after "and only an install replaces the copy."; the rest already stands.
- **Scope:** `devpro/install.py`, `devpro/install_target.py`, `devpro/install_base.py` (the
  `PACKAGE_ROOT` docstring, where R1 changes what the guard refuses), `devpro/runner_file.py`,
  `tests/test_devpro_install.py`, `tests/test_install_target.py`.
- **Facts:**
  - `git grep -n require_outside_package_source -- devpro` → `devpro/install.py:55`, `:879`;
    `devpro/install_base.py:23`; `devpro/install_target.py:89`, `:156`.
  - `git grep -n "REPO_ROOT" -- devpro/runner_file.py` → `:231`, the U1 skip.
  - `git grep -l "_WRAPPER_TEXT" -- devpro tests` → `devpro/install.py` (`:193`).
  - `git grep -l ShippedPackage -- devpro tests` → `devpro/install.py tests/test_devpro_install.py`.
  - R28's stamping exemption is `devpro/install.py:648`
    (`stamps = not target.is_relative_to(root / DEVPRO_COPY)`); R27's count line is `:670`.
- **Tests pinning the behavior** (in scope):
  - R1: `test_an_install_into_the_running_packages_own_source_tree_is_refused`
    (`tests/test_install_target.py:161`).
  - R2, R28: in `tests/test_devpro_install.py`,
    `test_a_project_install_writes_the_devpro_copy_and_a_wrapper_that_runs_it` (`:1816`, the copy
    byte-equal to the package), `test_a_wrapper_whose_recorded_python_is_gone_runs_the_first_python3_on_path_or_names_the_floor`
    (`:1836`), `test_install_writes_every_render_and_stamps_the_packages_once` (`:1941`).
  - R3: `test_a_hand_written_file_at_a_render_target_is_refused_with_nothing_written` (`:1987`),
    `test_a_directory_at_a_render_target_is_refused_with_nothing_written` (`:1998`),
    `test_every_failing_target_is_named_in_one_refusal` (`:2009`).
  - R27: none pins the count line's counts; `:2436` pins its absence on an up-to-date run.
  - U1, rewritten to pin the include line written: `:1374`
    (`test_the_repositorys_own_project_root_gets_no_include_line`), `:1381`
    (`test_the_exemption_creates_no_runner_file_in_a_project_holding_none`), `:2398`
    (`_the_repository_as_project`, used at `:2421`); and `:298`
    (`test_outside_a_checkout_a_project_at_site_packages_gets_its_include_line`), which pins the
    outside-a-checkout stand-down packaging pair 3 removes.
- **New tests, each failing before its fix:** R1, a second install whose `PACKAGE_ROOT` is the
  first install's copy leaves `tools/devpro/__init__.py` in place and exits 2; R2, the wrapper run
  from a directory holding a `devpro` package imports the copy; R3, a `tools/devpro.sh` in the
  install directory that carries no installed banner refuses the install with nothing written; U1,
  an install whose project is `REPO_ROOT` writes the `devpro` include line.
- **Done-line:** `just test`, `just lint`, `just dev-check-links`,
  `just dev-check-design-deltas-applied`.
- **After acceptance:** the session runs `just agents`, and the closing commit carries the
  include line it writes into this repository's `justfile` with the rest of that install's changes.

### P7b Post-plan burndown: the profiler and the verbs

Agent `devpro:python-coder`; expert (how doctor walks the launcher's candidates, and the
placeholder's name and namespace, are the agent's call).

- **Items:**
  - R4 (the `hooks.py` half: `devpro_executable` and `doctor`);
  - R5 (the fill only; P7d writes the wording that uses it): a placeholder, in the closed set
    `PROJECT_DOCS/ARCHITECTURE/rendering/placeholders.md` describes, filled from the bound harness
    with the path, relative to the project root, of the wrapper a project install under that
    harness writes — claude's `.claude/skills/devpro/tools/devpro.sh`. R6's derived
    `INSTALLED_WRAPPER` and this fill come from one derivation;
  - R6 (the derivation only; no test, below); R26; R29 (`CHECK_VERBS` only);
  - R30 (`hooks.py` positional insert; the duplicated assignment in `tests/test_devpro_profiler.py`).
- **Scope:** `devpro/profiler/hooks.py`, `devpro/profiler/pages.py`, `devpro/cli.py`,
  `devpro/doccheck/cli.py`; `devpro/vocabulary.py`, `devpro/harness.py`, `devpro/render.py` and
  `devpro/harnesses/` where the fill needs them; `tests/test_devpro_profiler.py`,
  `tests/dicing/test_cli_surface.py`, `tests/test_devpro.py`;
  `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` where its account of doctor or the
  wrapper's path changes, and `PROJECT_DOCS/ARCHITECTURE/rendering/placeholders.md` where its
  account of the closed set changes.
- **Facts:**
  - `git grep -n "INSTALLED_WRAPPER\|devpro_executable" -- devpro tests` →
    `devpro/profiler/hooks.py:56`, `:74`, `:78`, `:249`.
  - `git grep -n CHECK_VERBS -- devpro tests` → `devpro/cli.py:42`, `:241`;
    `tests/dicing/test_cli_surface.py:15` (the import), `:31` (the parametrize).
  - `hp.sh:34`, the launcher's candidates:
    `"${here}/../tools/devpro.sh" "${here}/../skills/devpro/tools/devpro.sh"`.
  - No placeholder reaches the plugin directory today: `git grep -n plugin_dir -- devpro/vocabulary.py`
    → nothing; `HarnessText` (`devpro/vocabulary.py:84-90`) holds seven members. `plugin_dir` is
    claude's `"skills/{plugin}"` (`devpro/harnesses/claude.py:149`), opencode's
    `"plugins/{plugin}"` (`devpro/harnesses/opencode.py:97`), `""` by default
    (`devpro/harness.py:202`). An unknown placeholder is refused at render (`devpro/render.py:188`).
  - `profiler init` writes the body a claude install renders (`profiler_skill_text`,
    `devpro/profiler/hooks.py:129-135`), so the fill reaches the skill `init` writes.
- **Tests pinning the behavior** (in scope):
  - R4: in `tests/test_devpro_profiler.py`,
    `test_doctor_reports_a_committed_launcher_that_differs_from_the_resource` (`:712`),
    `test_a_doctor_names_an_old_pattern_store_and_its_remedy` (`:1209`),
    `test_a_doctor_names_a_collided_store_as_the_operators_own_merge` (`:1232`).
  - R5's fill: in `tests/test_devpro.py`, `test_a_harness_text_placeholder_fills_with_the_harness_string`
    (`:882`), `test_an_unknown_placeholder_is_refused_at_render` (`:898`),
    `test_the_text_module_spells_each_render_placeholder_as_the_renderer_fills_it` (`:906`).
  - R26: in `tests/test_devpro_profiler.py`, `test_a_capture_writes_the_record_the_page_and_tree_read`
    (`:235`), `test_the_served_page_is_the_html_the_file_flow_writes` (`:1058`),
    `test_the_standalone_render_carries_the_shared_layer_and_the_legend_once` (`:1085`),
    `test_the_strict_fill_refuses_unknown_and_unfilled_marks_and_leaves_none_standing` (`:1250`).
  - R29: `test_help_lists_each_dicing_verb` (`tests/dicing/test_cli_surface.py:31-33`).
  - R30: `test_init_lays_down_the_launcher_and_clears_an_older_runs_files`
    (`tests/test_devpro_profiler.py:600`).
- **New tests, each failing before its fix:** R4, doctor given a launcher-relative wrapper that
  does not run reports it unusable; R5, a body carrying the fill renders
  `.claude/skills/devpro/tools/devpro.sh` under claude — today the closed set has no such
  placeholder, and the render refuses it; R26, a session whose output holds `/*DATA*/null` renders.
  R6's equality test is not written: `INSTALLED_WRAPPER` (`hooks.py:56`) already equals `hp.sh:34`'s
  second candidate taken from `HOOK_DIR`, so the test passes before the change and names no defect
  it fails on (`clauses.TEST_PRECONDITION`).
- **Done-line:** `just test`, `just lint`, `just dev-check-links`,
  `just dev-check-design-deltas-applied`.

### P7c Post-plan burndown: the shell

Agent `devpro:shell-dsl-coder`; expert (the quoting form is the agent's call).

- **Items:**
  - R7;
  - R4 (the `hp.sh` half: `hp.sh:35`'s `-x` test becomes an existence test, and the probe decides);
  - R8 (the `hp.sh` half; P7a carries `_WRAPPER_TEXT`'s), done when `find_devpro`'s `here` and
    `candidate` are `local`, its `cd` (`hp.sh:33`) runs with `CDPATH=`, and either the script sets
    `set -euo pipefail` or its header states why it does not. The choice is the agent's; either way
    `capture` still exits 0 on every path;
  - R9; R11 (the ARCHITECTURE Recipes sentence on check-wheel's checkout side).
- **Scope:** `devpro/runner-snippets/devpro.just`, `devpro/harnesses/resources/claude/profiler/hp.sh`,
  `devtools/scripts/render.sh`, `devtools/scripts/_render-slot.sh`,
  `PROJECT_DOCS/ARCHITECTURE/recipes.md`, `tests/test_devpro_install.py` (R7),
  `tests/test_devpro_profiler.py` (R4).
- **Facts:**
  - `grep -n 'source_directory()' devpro/runner-snippets/devpro.just` → `:33`, `:37`, `:41`, `:45`,
    `:49`.
  - `grep -n 'DEVPRO_DEV' devtools/scripts/*.sh` → `_harness-value.sh:7`, `_render-slot.sh:21`,
    `render.sh:40`, `render-agents-file.sh:11`; R9's are `render.sh:40` and `_render-slot.sh:21`.
- **Tests pinning the behavior** (in scope):
  - R7: in `tests/test_devpro_install.py`,
    `test_an_installed_runner_snippet_runs_the_check_through_the_wrapper_without_devpro_on_path`
    (`:1582`), `test_the_shipped_devpro_snippets_list_the_same_five_recipes_in_both_runners` (`:1502`).
  - R4, R8: in `tests/test_devpro_profiler.py`,
    `test_a_launcher_finding_an_unusable_devpro_captures_silently_and_reports_otherwise` (`:290`),
    `test_a_launcher_runs_the_wrapper_beside_it_with_no_devpro_on_path` (`:337`).
  - R9: none; `git grep -n -E 'render\.sh|_render-slot' -- tests` → nothing.
- **New tests, each failing before its fix:**
  - R7: `test_an_installed_runner_snippet_runs_the_check_through_the_wrapper_without_devpro_on_path`'s
    `just` case, run from a project directory whose name holds a space. Defect: the unquoted
    `{{source_directory()}}` path splits, and the recipe exits 127.
  - R4: a launcher whose installed wrapper exists without the execute bit, with a `devpro` on `PATH`,
    records nothing (the probe rules the wrapper unusable). Defect: today `[[ -x ]]` skips it and the
    launcher runs the `devpro` on `PATH`.
- **Done-line:** `just test`, `just lint`, `just dev-check-links`,
  `just dev-check-design-deltas-applied`.

### P7d Post-plan burndown: definitions and project documents

Agent `devpro:prompt-engineer`; expert (the wrapper clause's wording is the agent's call).

- **Items:**
  - R5 (the wording: the clause in `devpro/clauses.py`, composed into `docdicer.py`, `profiler.py`
    and `guide.py`; its second candidate, for the skill `profiler init` writes, is P7b's fill);
  - R12, R13, R14, R15, R16, R17 (`subsystem-map.md:87-88`: `guide.py:37` gives the `profiler` row
    a `clauses.ref` too; the `packaging.md` claim holds), R18 (all but README), R19 (the prose),
    R20;
  - U1's ROADMAP ticket, "devpro runner-snippets import line not installing" (`ROADMAP.md:18`),
    leaves the roadmap, accomplished by P7a;
  - U1's two tickets that record surroundings rather than the fact: "claude profiler records not
    being captured" (`ROADMAP.md:14`), whose body becomes "A claude project session writes no record
    to `.devpro-temp/.profiler-claude/`."; and "Profiler time stamps in local" (`ROADMAP.md:108`),
    whose heading becomes "Profiler pages show timestamps in UTC, not local time" and whose body
    names the surfaces, the trace list and the session page.
- **Applies:** spec-delta/installed-tree pair 5.
- **Scope:** `devpro/clauses.py`, `devpro/definitions/skills/{docdicer,profiler,guide,development}.py`,
  the PROJECT_DOCS leaves the items name,
  `PROJECT_DOCS/CONVENTIONS/adding-definitions/a-skill-omits-its-tool-s-offered-surface.md`,
  `ROADMAP.md`.
- **Facts:** `git grep -n -F '../../tools/devpro.sh' -- devpro` → `docdicer.py:48`, `:49`, `:59`;
  `profiler.py:49`; `guide.py:109`, `:469`, `:472`.
- **Done-line:** `just test`, `just lint`, `just dev-check-links`, `just dev-check-roadmap`,
  `just dev-check-design-deltas-applied`, which passes from here on.

### P7e Post-plan burndown: the README

Agent `devpro:tech-writer`; expert (R21's wording and R25's order are the agent's call).

- **Items:** R18 (the README sites), R21, R22, R23, R24, R25.
- **Scope:** `README.md`.
- **Done-line:** `just dev-check-links`; `git grep -c -i 'dicing snippets' README.md` answers
  nothing.
