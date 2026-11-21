# devpro absorbs its tooling — stage 2: the profiler and the snippet surface

Design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — read whole; its stage marks are authoritative. This
plan applies only what the design marks to stage 2: the profiler's absorption (three of the five
stage-2-4 profiler/dashboard pairs) and the snippet surface (the 21 snippet-set pairs the user
directed after stage 1 landed). The design's dashboard pair and attribution pair stay pending for
stages 3 and 4, and every package below leaves them so. The stage-1 pairs are landed
(`1a81fc5`); the dicing surface is devpro's own.

The user directed the profiler stores rename — `.devpro-temp/claude-profiler/` →
`.devpro-temp/.profiler-claude/` and `.devpro-temp/opencode-profiler/` →
`.devpro-temp/.profiler-opencode/` — dot-directory naming so the stores group at the top of the
scratch tree. The design's [Harness profiler
entry](ACTIVE_DESIGN.md#harness-profiler--the-profiler-stores-rename-to-dot-directories) holds it
(landed as `16f9c44`), and this revision amends the design once more, for the stage-2 plan's
`view.html` decision: the page template leaves the install resource set for the devpro wheel's
package data (the Shipped-files profiler sentences and the Packaging pending pair). P2 answers the
entry's migration boundary question; the doc packages apply the rename's and the template's pairs
with the rest of the stage-2 set.

## Status

| Package | State | Rating | Lifetime | Work |
| --- | --- | --- | --- | --- |
| | drafted | | | Kickoff: the stage-2 plan written from the design; 29 stage-2 pairs in scope, 2 (stages 3-4) left pending |
| P1 | landed | expert | shipped | the profiler's code absorbed into `devpro/profiler/`; the launcher finds `devpro` |
| P2 | landed | expert | shipped | the store rename to `.profiler-*` and the existing-stores migration |
| P3 | landed | expert | shipped | the dicing snippets package ships; its include line on every nested-plugin project install |
| P4 | landed | mechanical | shipped | the docdicer skill's runner instruction returns |
| P5 | landed | mechanical | shipped | the SPEC delta and README pairs applied |
| P6 | in progress | mechanical | shipped | the ARCHITECTURE delta pairs applied |
| P7 | dispatchable | expert | shipped | the plan-borne house leaves (harness-profiler, repo-layout resources line, CONVENTIONS) |
| PR | dispatchable | expert | shipped | Post-plan review |
| PB | dispatchable | expert | shipped | Post-plan burndown |

## P1 — the profiler is devpro's code

Lifetime: shipped. One commit closes it.

**Scope.** New: `devpro/profiler/__init__.py`, `devpro/profiler/cli.py`, `devpro/profiler/capture.py`,
`devpro/profiler/pages.py`, `devpro/profiler/hooks.py`, and `devpro/profiler/view.html` moved from
the resources. Removed: `devpro/harnesses/resources/claude/profiler/hp.py` and
`devpro/harnesses/resources/claude/profiler/view.html`. Edited:
`devpro/harnesses/resources/claude/profiler/hp.sh`, `devpro/harnesses/resources/opencode/profiler.ts`
(comments naming hp.py only — the record schema is P2's), `devpro/cli.py` (verb registration beside
`devpro.dicing.cli.add_verbs`, `devpro/cli.py:83`), `pyproject.toml` (package data gains
`profiler/view.html`), the justfile's `dev-profiler` recipe (`justfile:308`), and the profiler tests.

**Module layout** (the plan's decision, the dicing precedent — `devpro/dicing/` holds `cli.py` plus
`dicerlib/`): one package, split by concern — `capture.py` the payload parsing, masking and record
serialization (hp.py's `capture` section, hp.py:240-611); `pages.py` the tree, page and HTTP render
(hp.py's `tree`, html and serve sections), reading `view.html` via
`importlib.resources.files("devpro.profiler")` where hp.py:1084 reads `SCRIPT_DIR / VIEW_TEMPLATE`;
`hooks.py` the hook wiring — `init`, `merge_hooks`, `hook_entry`, `is_our_command`, `hook_sources`,
`stale_hook`, `doctor` (hp.py:1355-1490); `cli.py` adding one `profiler` verb whose subcommands
`capture|tree|serve|init|doctor` pass through from the launcher unchanged. The verb is lazy like the
dicing verbs: registering it imports none of the modules (the design's Packaging entry's lazy
dispatch, [Packaging](ACTIVE_DESIGN.md#packaging--the-wheels-data-globs-and-the-lazy-entry-point),
applied in P6).

**The launcher's fate** (the design leaves this to the plan; the options it names were search for
python3 survives, replaced by finding devpro, or the launcher goes): `hp.sh` survives and its
finder is replaced by finding the `devpro` command — the launcher is the capture contract's
enforcement point, and the hook command string keeps its shape. `find_python` (hp.sh:26-34)
becomes a `find_devpro` over the same candidate list with devpro's name:
`command -v devpro`, `/opt/homebrew/bin/devpro`, `/usr/local/bin/devpro`, `~/.local/bin/devpro`;
`HP_DEVPRO` overrides where `HP_PYTHON` did. A candidate is usable when
`"$candidate" --version` runs and exits 0. The terminal exec line — hp.sh:57,
`exec "$python" "$here/hp.py" "$@"` — becomes `exec "$devpro" profiler "$@"`: the found command,
the `profiler` verb inserted before the launcher's own arguments, which pass through unchanged.
Without a usable devpro: `capture` drains stdin and exits 0 without output; every other
subcommand reports and exits 1 — hp.sh:45-50 unchanged in shape, its subject the devpro command.
The `hp.py not found beside this launcher` guard (hp.sh:51-56) is removed: its subject is a file
the install no longer ships, so it could only report an install that is not incomplete, and the
no-devpro guard above already names the launcher's one dependency and its remedy. The
`dev-profiler` recipe runs the verb directly (`just dev-devpro profiler serve`), needing no finder
in this repository.

**The hook command's fate**: unchanged. `devpro/harnesses/claude.py:74` —
`_PROFILER_COMMAND = f'sh "${{CLAUDE_PLUGIN_ROOT}}/{_PROFILER_SCRIPT}" capture claude'` — runs the
launcher, and hp.py's `_hook_command` (hp.py:77-79) writes the same shape for committed hooks;
hp.sh's name carries no rename, so `is_our_command` (hp.py:1363-1365) recognizes
`HOOK_COMMAND` and `OLD_HOOK_COMMAND` exactly as it stands.

**What `init` copies** once no hp.py ships as a copied resource: the launcher alone, read from the
harness resource the devpro package ships (`harnesses/resources/claude/profiler/hp.sh`), and the
show-profile skill rendered from its definition where hp.py:1405 copies
`SCRIPT_DIR.parent / SHOW_SKILL / "SKILL.md"`. `init` unlinks the committed `hp.py` and `view.html`
(`HOOK_FILES`' older members) the way hp.py:1402 unlinks the pre-0.2.0 launcher — the rename
precedent that names the migration shape. `HOOK_FILES` (hp.py:74) becomes `("hp.sh",)`.

**Where `stale_hook`'s byte compare lands**: on hp.sh alone, the committed
`.claude/harness-profiler/hp.sh` against the harness resource the devpro package ships — the
resource is the master (CONVENTIONS.md, Harness resources are copied verbatim), and the compare
needs no install directory to run. hp.py:1460's `HOOK_FILES` comprehension carries the new set.

**`doctor` keeps naming what is missing**: its lines keep their shape; the `python:` line
(hp.py:1484) names the devpro executable the finder resolves, and where none resolves the hook
line's "not installed" and the `update` line name the remedy as they do.

**Verbatim-rule decision — `view.html`**: it moves beside its rendering module. The page render
runs from devpro the installed package, so a template left in the install directory would be
unreachable from the render and a copy in the committed hook directory dead weight; as package data
it ships in the wheel and the render owns its one read.

**Facts.**
- `VIEW_TEMPLATE = "view.html"` — `git grep -n 'VIEW_TEMPLATE' -- devpro` → hp.py:38 only; hp.py:1084
  reads `SCRIPT_DIR / VIEW_TEMPLATE`; hp.py:74 and hp.py:1460 name it in `HOOK_FILES`.
- `git grep -l 'hp\.py'` → ACTIVE_DESIGN.md, PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md,
  PROJECT_DOCS/ARCHITECTURE/repo-layout.md, PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md,
  devpro/harnesses/resources/claude/profiler/hp.py, devpro/harnesses/resources/claude/profiler/hp.sh,
  devpro/harnesses/resources/opencode/profiler.ts, justfile, tests/profiler_capture_runner.ts,
  tests/test_devpro_install.py, tests/test_devpro_profiler.py.
- `git grep -l 'view\.html'` → ACTIVE_DESIGN.md, PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md,
  PROJECT_DOCS/ARCHITECTURE/repo-layout.md, PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md,
  devpro/harnesses/resources/claude/profiler/hp.py, devpro/harnesses/resources/claude/profiler/view.html,
  tests/test_devpro_install.py, tests/test_devpro_profiler.py.
- `git grep -l 'hp\.sh'` → the doc set, devpro/definitions/skills/show_profile.py,
  devpro/harnesses/claude.py, the profiler resources, justfile, tests/test_devpro_install.py,
  tests/test_devpro_profiler.py — hp.sh survives, so only the doc leaves and tests read it.
- pyproject.toml:25 — `devpro = ["kb-tools/**/*", "harnesses/resources/**/*", "development-tools/**/*",
  "dicing/kanban/assets/**/*"]`: the resources glob shrinks with the files removed from it;
  `profiler/view.html` joins as package data.
- `devtools/scripts/check-wheel.sh` proves the wheel's package data equals the git-tracked non-.py
  files under devpro/ — the moved template and shrunken resources enter that comparison unchanged;
  no script edit.

**Tests.** The suite that pins the hook contract is `tests/test_devpro_profiler.py` — every test
there drives the profiler through the installed launcher (`_launcher`, `_run`, test file lines
80-131), which is the contract's own path. Updating them is in scope:
- `_run` and `_serve` pass a devpro instead of `HP_PYTHON=sys.executable`: the fixture writes a
  `devpro` shim (`#!/bin/sh` + `exec python3 -m devpro "$@"` with the repository root on
  PYTHONPATH) into the test's tmp directory and points `HP_DEVPRO` at it.
- `test_the_installed_profiler_is_the_sources_bytes` (line 199) compares the installed `profiler/`
  against the resource set as it now stands: hp.sh only under claude and opencode alike.
- `tests/test_devpro_install.py`: `_PROFILER_FILES` (line 409) becomes `("hp.sh",)`;
  `test_the_profiler_resources_land_under_the_install_directorys_profiler` (line 464) and
  `test_an_opencode_install_copies_the_profiler_payload_while_a_mage_one_does_not` (line 1859)
  hold the new set; `test_the_claude_registration_carries_the_profiler_on_every_event_it_captures`
  (line 476) stands — the command string does not change.
- The TS runners (`tests/profiler_capture_runner.ts`, `profiler_mask_runner.ts`,
  `profiler_serialize_runner.ts`) keep driving `profiler.ts`; their references to hp.py's masks and
  spellings name the devpro module instead (comment and loader paths only — P2 moves their store).

**New tests, each named by its defect** (devpro/clauses.py:170, TEST_PRECONDITION):
- a capture whose devpro the finder cannot resolve drains stdin and exits 0 with empty stdout and
  empty stderr, and a non-capture subcommand under the same condition reports and exits 1 — the
  defect: a capture that reports or exits nonzero blocks a tool call under the harness's hook error
  policy, the contract [Shipped files](ACTIVE_DESIGN.md#shipped-files--the-docdicer-package-retires-its-runner-shortcuts-return-the-profilers-and-dashboards-decisions-stages-2-4)
  pins with "a failed or interpreterless capture exits 0 with no output — unchanged".
- `init` writes only the launcher into the committed hook directory and removes an older run's
  `hp.py` and `view.html` from it — the defect: a committed hook running devpro beside a stale
  `hp.py` is the half-absorbed state the migration boundary forbids, and `stale_hook`'s compare
  would chase files no longer shipped.
- `stale_hook` reports a committed launcher whose bytes differ from the resource — the defect: the
  compare reading a defunct source (the old beside-the-script copies) reports nothing, and doctor's
  `update` line loses its one job.

The show-profile skill's text stands: it names the launcher `hp.sh`, whose finder now resolves
devpro; both finder candidates keep their paths (devpro/definitions/skills/show_profile.py:24-28).
The design's show-profile entry is stage 3's and is not applied here.

**Done-line.** `just test` `just lint` `just build` `just check-wheel` — once each, at the
package's end. In scope with the commit: `just retake-reference` re-takes the four reference slots
over the changed install product, then `just render-diff` reports it clean.

## P2 — the store rename and the existing-stores migration

Lifetime: shipped. One commit closes it.

**Scope.** `devpro/profiler/` — `TRACE_DIR`/`TRACE_GLOB` (hp.py:30-31) become
`Path(".devpro-temp") / ".profiler-claude"` and `".profiler-*"`; the migration function (new, in
`hooks.py`); doctor's lines. `devpro/harnesses/resources/opencode/profiler.ts:70` —
`const TRACE_DIR = join(".devpro-temp", "opencode-profiler")` becomes
`join(".devpro-temp", ".profiler-opencode")`. `devpro/definitions/skills/show_profile.py:17-18` —
the store facts. `devpro/harnesses/claude.py:70` — the store comment. `devpro/install.py` — the
migration call. The tests below; `README.md:45`'s store sentence is P7's — the amendment's pairs
touch shipped-files and harness-profiler, not the README (verified by the deltas-applied check's
pending list).

**The migration choice** (the plan's answer to the [Harness profiler
entry](ACTIVE_DESIGN.md#harness-profiler--the-profiler-stores-rename-to-dot-directories)'s boundary
question, which the design leaves to stage 2; stated as the user's direction requires): rename
existing stores in place; the reader reads one pattern only. Rationale: reading both patterns
during a migration window keeps the second glob in every reader line — tree, index, doctor — with
no removal point: the window ends either never (two patterns forever, the duplicated-code contract)
or at an unenforced cutoff where unrevisited projects' stores silently vanish from the index. The
no-half-absorbed-state rule applied to stores lands the rename where the new reader arrives:
- `devpro install` renames every `*-profiler` directory under the project root's `.devpro-temp/`
  to its `.profiler-*` name — `claude-profiler` → `.profiler-claude`, `opencode-profiler` →
  `.profiler-opencode`, any other `<store>-profiler` → `.profiler-<store>` — naming each rename in
  the install report, resolved against the real project the way the runner include lines are
  (`real_project`, runner_file.py:210).
- `profiler init claude` performs the same rename for the committed-hook repository it writes,
  named in its output.
- doctor names any old-pattern store still standing — beside a populated new-pattern store as the
  operator's to merge or delete, otherwise with its remedy (run the install or `init` again) —
  keeping its "names what is missing" job over the renamed state.
- The schema is untouched: stores keep the schema the copies wrote — `SCHEMA_VERSION = 2`
  (hp.py:27) does not change; the rename moves directories, never contents. A directory whose name
  the mapping already gives (`.profiler-claude`) is left as it stands, so the second run touches
  nothing.
- The collision case — old-pattern and new-pattern stores both populated, the state after captures
  ran post-upgrade and before the install ran: the rename skips where the `.profiler-*` target
  already exists and names the standing old-pattern store. The installer never merges store
  contents — merging or deleting the old store is the operator's call, not the installer's; that
  boundary is the choice's statement.

**Tests.** Updated: `test_a_capture_writes_the_record_the_page_and_tree_read`,
`test_a_capture_writes_its_line_in_the_bytes_it_measured`,
`test_a_tree_renders_an_opencode_store_beside_the_claude_capture`,
`test_the_served_index_lists_every_recorded_session`,
`test_the_served_index_states_an_unreadable_store`,
`test_the_served_page_is_the_html_the_file_flow_writes` (tests/test_devpro_profiler.py — the
fixture stores take the new names), and `tests/profiler_capture_runner.ts`'s asserted store path.
New, each by its defect:
- an install renames an old-pattern store and names the rename in its report, and a second install
  reports `up to date` and touches nothing — the defect: without the rename the reader's
  `.profiler-*` glob sees no old store, and a project's recorded history vanishes from the index
  at the upgrade with nothing to say it happened.
- `init` renames the repository's old-pattern stores the same way — the defect: the committed-hook
  repository migrates nowhere and its old traces go dark while its hook records on.
- doctor names an old-pattern store with its remedy — the defect: a store the reader cannot see
  reads as "no calls recorded yet", and the operator has no line telling them why.
- an install with an old-pattern store and a populated new-pattern store skips the rename and
  names the standing old store — the defect: a rename onto the live new-pattern store destroys new
  traces or errors mid-report, and a silent skip leaves the operator without the one line that
  tells them the old store stands.

**Done-line.** `just test` — once. In scope with the commit: `just retake-reference` (the skill
text's store facts are a render product), then `just render-diff` reports clean.

## P3 — the dicing snippets package and its include line

Lifetime: shipped. One commit closes it.

**Scope.** New: `devpro/dicing-snippets/runner-snippets/devpro.just` and
`devpro/dicing-snippets/runner-snippets/devpro.mk`. Edited: `devpro/install.py`
(`SHIPPED_PACKAGES`, `RETIRED_SNIPPET_SET` stands), `pyproject.toml:25` (package data gains
`dicing-snippets/**/*`), the tests below.

**The package row** (the design's mechanism entry,
[ARCHITECTURE install Plugins](ACTIVE_DESIGN.md#plugins--two-shipped-rows-with-snippets-the-retired-lines-cleanup),
applied in P6):

```python
ShippedPackage(
    "dicing-snippets",
    "skills/docdicer/dicing-snippets",
    "docdicer",
    SnippetSet("devpro", "runner-snippets", {"just": "devpro.just", "make": "devpro.mk"}),
)
```

joining `SHIPPED_PACKAGES` (devpro/install.py:105-113) beside the kb-tools row. The include-line
mechanism needs no change: `install_include_lines` writes one line per set
(devpro/runner_file.py:204-269), the row's `snippets` field is what writes the line, and
`_is_project_install_of_a_nested_plugin` already gates it — every project install of a nested
plugin writes the devpro line, one with the kbase component also the kb line.
`RETIRED_SNIPPET_SET` (devpro/install.py:117-119) stands unchanged — the cleanup mechanism stage 1
landed keeps eating old docdicer lines, and the retired set's snippets
(`docdicer.just`/`docdicer.mk`) point at nothing, so it never matches the new set's lines.

**The six recipes**, each in both runners, running the `devpro` command from PATH:
- `devpro` — the command bare: its help.
- `devpro-help` — the commands and their doc strings: under just, the kb-help shape
  (`just --justfile "{{justfile()}}" --list` filtered to the set's recipes —
  devpro/kb-tools/runner-snippets/kb.just, the `[doc("show help on kb just recipes")]` recipe),
  reading the recipes' own `[doc]` strings; under make, parsing the snippet's own `# Targets:`
  comment block — the approach the retired set's make snippet used and the feature worked
  (devpro/kb-tools/runner-snippets/kb.mk, the block at its head).
- `devpro-check-plan`, `devpro-check-design`, `devpro-check-design-deltas-applied`,
  `devpro-check-roadmap` — the four gates, argumentless, each running its check verb on the active
  file under the project root; no `devpro-kanban` and no dicing recipes (the board is the
  dashboard's panel, the dicing shortcuts need their direct calls' arguments — the design's
  [SPEC Plugins entry](ACTIVE_DESIGN.md#plugins--the-snippet-sets-devpro-returns-the-retired-line-cleaned-up),
  applied in P5, states it).

The snippet headers state the same install-at, include-line and `import?` floor facts the kb
snippets' headers state, for the dicing set's paths. The `import?` floor (just 1.33.0) rides
SPEC's Guide and README entry, applied in P5.

**Facts.**
- devpro/runner_file.py:25-32 — `class SnippetSet(NamedTuple): label: str; directory: str;
  snippets: Mapping[str, str]` — the set's whole shape; the row above states it in full.
- `git grep -l 'SnippetSet'` → ACTIVE_DESIGN.md, PROJECT_DOCS/ARCHITECTURE/install/plugins.md,
  PROJECT_DOCS/ARCHITECTURE/subsystem-map.md, devpro/install.py, devpro/runner_file.py.
- `git grep -ln 'RETIRED_SNIPPET_SET'` → devpro/install.py, tests/test_devpro_install.py.
- `git grep -l 'SHIPPED_PACKAGES'` → ACTIVE_DESIGN.md,
  PROJECT_DOCS/ARCHITECTURE/install/plugins.md, PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md,
  PROJECT_DOCS/ARCHITECTURE/packaging.md, devpro/install.py, tests/test_devpro_install.py.
- `git grep -n 'runner-snippets/kb.just' tests/test_devpro_install.py` → lines 559, 635-640, 647,
  786, 1192, 1240 — the include-line and package-copy tests whose fixtures carry the kb line; the
  devpro line joins them (the asserted line at 1243).

**Tests.** Updated: the include-line suite
(`test_the_include_line_is_appended_to_an_existing_justfile`, `test_a_makefile_is_created_when_the_project_has_neither_runner_file`,
`test_an_include_line_for_this_harness_under_any_tree_is_rewritten_in_place`, and the shape tests,
tests/test_devpro_install.py:1186-1421) — every project install writes the devpro line beside or
instead of the kb line as the component selection says; `test_a_kbase_install_writes_the_kbase_skill_the_package_the_mcp_entry_and_the_include_line`
(line 624) and the package-copy assertions (lines 635-640) take the dicing snippets package's
files and banner. New, each by its defect:
- a project install with no kbase component writes the devpro include line and no kb line — the
  defect: the line written only with the component leaves the argumentless gates unreachable in
  the default install the user directed the line for.
- the runner file holding a devpro-set line survives the retired docdicer line's cleanup with its
  line intact — the defect: a cleanup matching the `runner-snippets/` directory name rather than
  the snippet file name deletes the new set's line the same run that restores it.
- the shipped devpro.just and devpro.mk carry the installed banner and name the same six recipes
  in both runners — the defect: a runner whose recipe list drifts from the other's writes include
  lines promising targets one runner does not define.

**Done-line.** `just test` — once. In scope with the commit: `just retake-reference` (the install
product grows the package and its line), then `just render-diff` reports clean.

## P4 — the docdicer skill's runner instruction returns

Lifetime: shipped. One commit closes it.

**Scope.** `devpro/definitions/skills/docdicer.py` — the body gains the runner-instruction
paragraph the design's
[Subsystem Map entry](ACTIVE_DESIGN.md#subsystem-map--the-docdicer-skill-routes-devpros-verbs)
(applied in P6) states: where the project's runner includes the `devpro` set, the checks run
through the recipes (`devpro`, and by name `devpro-help`, `devpro-check-plan`,
`devpro-check-design`, `devpro-check-design-deltas-applied` and `devpro-check-roadmap`), the four
gates argumentless, each checking the active file under the project root — the active plan, the
active design, the active design's applied deltas and `ROADMAP.md` — with a direct `devpro` call
for any other. The verbs paragraph and the `kanban` paragraph stand as they are.

**Facts.**
- devpro/definitions/skills/docdicer.py:47-50 — "Dice, undice and check through the dicing verbs of
  the `devpro` command … this skill does not restate it" — the paragraph P4's addition sits beside.
- The guide skill needs no change: its board section names no launcher path or recipe (the
  stage-1 pair landed it), and the design holds no stage-2 pair for it.

**Tests.** `test_devpro.py`'s render suite holds the rendered `docdicer` skill to its definition —
no new test: the paragraph's presence is the render's own output, and no defect beyond the text's
own absence is catchable (TEST_PRECONDITION bars a pin on the artifact's text alone). The
reference slots follow the changed render.

**Done-line.** `just test` — once. In scope with the commit: `just retake-reference`, then
`just render-diff` reports clean.

## P5 — the SPEC delta and README pairs

Lifetime: shipped. One commit closes it.

**Scope.** Apply the design's stage-2-marked pairs verbatim to their targets, cited by entry
(anchor links into the design; the anchors are the design's own heading anchors, computed with
`PYTHONPATH=. python3 -c "from devpro.dicing.dicerlib.anchors import heading_anchor_list; …"` over
ACTIVE_DESIGN.md). The pairs applied are the `just dev-check-design-deltas-applied` pending list's
stage-2-marked entries at run time; the line references below are authoring-time, after the
`view.html` amendment, and the check's run supersedes them:
- [Surfaces and layout](ACTIVE_DESIGN.md#surfaces-and-layout--the-docdicer-tools-package-retires-the-dicing-snippets-package-takes-its-place) — pair at design:158.
- [Shipped files](ACTIVE_DESIGN.md#shipped-files--the-docdicer-package-retires-its-runner-shortcuts-return-the-profilers-and-dashboards-decisions-stages-2-4) — pairs at design:246, :259, :290, :317, :328, :339, :360. The pairs at design:273 (dashboard) and :301 (attribution) are the design's stage-3 and stage-4 marks and stay pending; :301's accepted text carries the renamed `.profiler-opencode` spelling for stage 4 to apply.
- [Plugins](ACTIVE_DESIGN.md#plugins--the-snippet-sets-devpro-returns-the-retired-line-cleaned-up) — pairs at design:462, :484.
- [Install destination](ACTIVE_DESIGN.md#install-destination--the-user-level-package-list) — pair at design:580.
- [Write Safety](ACTIVE_DESIGN.md#write-safety--the-docdicer-package-and-its-venv) — pair at design:620.
- [Guide and README](ACTIVE_DESIGN.md#guide-and-readme--the-just-floor-is-the-devpro-lines) — pair at design:633.
- [README](ACTIVE_DESIGN.md#readme--the-include-line-promise-states-both-lines) — pairs at design:648, :657, :676.

Apply pairs in the design's order — chained pairs read one another's earlier output: the store
rename pairs (:317, :328 — the [Harness profiler
entry](ACTIVE_DESIGN.md#harness-profiler--the-profiler-stores-rename-to-dot-directories)'s
shipped-files pairs) apply the renamed spellings before the attribution pair (:301, stage 4)
reads them, and the install/plugins leaf's four chains are P6's and self-contained.

**Facts.**
- `just dev-check-design-deltas-applied` (run at this revision, after the `view.html` amendment) →
  "pairs: 64, landed: 33, pending: 31, drifted: 0, conflicting: 0, problems: 0", the pending lines
  at design:158, :246, :259, :273, :290, :301, :317, :328, :339, :360, :462, :484, :580, :620,
  :633, :648, :657, :676, :724, :755, :819, :906, :922, :950, :967, :1055, :1099, :1154, :1249,
  :1258, :1269 — the 29 stage-2 pairs above, plus :273 and :301 left pending.
- The README pairs' target is README.md at the repository root, which `just dev-check-links`
  checks.

**Done-line.** `just dev-check-design-deltas-applied` `just dev-check-links` — the check reports
the SPEC and README pairs landed, :273 and :301 pending.

## P6 — the ARCHITECTURE delta pairs

Lifetime: shipped. One commit closes it.

**Scope.** Apply the design's stage-2-marked pairs verbatim, in the design's order. The pairs
applied are the `just dev-check-design-deltas-applied` pending list's stage-2-marked entries at
run time; the line references below are authoring-time, after the `view.html` amendment, and the
check's run supersedes them:
- [Repo Layout](ACTIVE_DESIGN.md#repo-layout--the-hosted-clone-and-the-tools-package-out-the-dicing-package-and-its-snippets-in) — pair at design:724.
- [Packaging](ACTIVE_DESIGN.md#packaging--the-wheels-data-globs-and-the-lazy-entry-point) — pair at design:755, as the `view.html` amendment wrote it: six patterns, `profiler/view.html` beside the dicing assets.
- [Recipes](ACTIVE_DESIGN.md#recipes--the-verbs-run-from-devpro-the-consumers-floor-is-the-devpro-lines) — pair at design:819.
- [Plugins (install)](ACTIVE_DESIGN.md#plugins--two-shipped-rows-with-snippets-the-retired-lines-cleanup) — pairs at design:906, :922, :950, :967 (the four chained edits of the owners table, the runner-include-lines paragraph, the shape-rule paragraph and the cleanup paragraph).
- [Renders and copies](ACTIVE_DESIGN.md#renders-and-copies--three-package-rows-no-launcher-naming-no-tool-install) — pair at design:1055.
- [Why There Is No Verification Verb](ACTIVE_DESIGN.md#why-there-is-no-verification-verb--the-include-lines-in-a-slot) — pair at design:1099.
- [Subsystem Map](ACTIVE_DESIGN.md#subsystem-map--the-docdicer-skill-routes-devpros-verbs) — pair at design:1154.
- [Harness profiler](ACTIVE_DESIGN.md#harness-profiler--the-profiler-stores-rename-to-dot-directories) — the store-rename amendment's three pairs at design:1249, :1258, :1269, targeting `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`: the capture's store line and read pattern, the served index's glob, and the opencode store beside the claude sessions'. P6 applies them verbatim to the leaf as it stands; P7's absorbed-state rewrite of the same leaf lands after P6's commit and rewrites on top of the pairs' output — the leaf is rewritten twice in one direction, never to two different states.

**Facts.** The supersession clause above governs the lines; the chained pairs apply cleanly in
order (each pair's from-text is the previous pair's becomes-text).

**Done-line.** `just dev-check-design-deltas-applied` `just dev-check-links` — the check reports
every stage-2 pair landed, and the only pending pairs left are the design's stage-3 and stage-4
marks: the dashboard pair (design:273) and the attribution pair (design:301), stated as the
expected remainder.

## P7 — the plan-borne house leaves

Lifetime: shipped. One commit closes it.

**Scope.** The documents the stage-2 work invalidates that no design pair covers:
- `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` — rewritten for the absorbed state: one
  resource (`hp.sh`) beside the `devpro/profiler/` module layout P1 lands; the `profiler` verb and
  its subcommands; the launcher's devpro finder and `HP_DEVPRO`; `view.html` as package data; what
  `init` copies and what it removes; `stale_hook`'s compare against the resource; the store names
  `.profiler-claude`/`.profiler-opencode`, the `.profiler-*` glob, and the install/init migration;
  doctor's lines. The leaf's port credit and store schema statements stand. P6 lands the design's
  three store-rename pairs on this leaf first (applied verbatim); this rewrite lands in P7's
  commit and rewrites on top of their output — one direction, never two different states.
- `PROJECT_DOCS/ARCHITECTURE/repo-layout.md` — the `harnesses/resources/` line names hp.sh alone
  for the profiler and adds the `devpro/profiler/` module and `view.html` beside the dicing
  package's line (the design:724 pair's addition, applied in P6, sits beside this).
- `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md` — the show-profile bullet's store facts
  (`<store>-profiler/`, subsystem-map.md:60-65) to the renamed stores, where no amendment pair
  landed them first.
- `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/harness-resources-are-copied-verbatim.md`
  — the Python-resource lint paragraph (its last paragraph: "A harness resource written in Python
  is inside `just lint`'s paths …") retires: no Python resource remains once hp.py leaves, and the
  leaf says what took its place (the profiler module is a devpro module, lint's own paths cover
  it).
- `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-sentence-two-resources-carry-is-one-text.md`
  — the rule's scope states the masking one-text now holds between the `profiler.ts` resource and
  devpro's profiler module, held by `test_the_two_masks_redact_alike` as before; the rule's name
  and mechanism stand.

**Facts.**
- `git grep -n 'harness resource written in Python' PROJECT_DOCS/CONVENTIONS` → the verbatim leaf's
  last paragraph — the quoted line above.
- `git grep -l 'hp\.py' PROJECT_DOCS/ARCHITECTURE` → harness-profiler.md, repo-layout.md — both in
  this package's scope.

**Done-line.** `just dev-check-links` `just dev-check-design-deltas-applied` — links resolve, and
the deltas-applied check still reports the two stage-3-4 pairs pending.

## PR — Post-plan review

Lifetime: shipped. One commit closes it.

The reviewers are given the project documents and the design — not this plan — and review the
changes and their tests against the project's standards and fitness for purpose. The seats: the
coder for the changed Python and TypeScript surfaces, `devpro-architect` for the structure and the
documents' claims about the code, `devpro-tech-writer` for the human-facing guides, and
`devpro-prompt-engineer` for the model-facing text this stage changed (the docdicer skill's runner
instruction, the show-profile skill's store facts). Each writes an independent review in
`.devpro-temp/`; the session synthesizes them into `ACTIVE_PLAN_REVIEW.md`, de-duplicated and
reconciled, in the commit that adds it. Its row is `landed` in that commit.

**Done-line.** `just dev-check-links` — the review document added, its links resolving.

## PB — Post-plan burndown

Lifetime: shipped. One commit closes it.

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands. Until then this section
holds that sentence only. The burndown's work list is drafted from the review document, grouped by
root cause with one ID per defect, gets `devpro-prompt-engineer` usability review, then revision,
before it is `dispatchable`.

**Done-line.** `just dev-check-plan` `just dev-check-links` — the burndown's section holds the
work list, the plan's own form still checking.
