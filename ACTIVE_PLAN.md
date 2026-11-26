# ACTIVE PLAN

## Four changes: wheel-staged installs, TOML settings, profiler verb removal, claude agents-path overlay

This plan comes from [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), accepted `2026-11-25`. Every package's
intended lifetime is **shipped**, and each package closes in one commit. Run order is `P2`, `P1`,
`P3`, `P4`: `P2` before `P1` because both reshape `tests/test_devpro_install.py`, and the settings
fixture `P2` converts is what `P1`'s reshaped tests read. `P4` after `P1` because both change
`tests/test_devpro.py` — `P1` retexts its settings-driven tests, `P4` adds its pinning test to the
file as `P1` leaves it. `P3` shares no file with the others. The landing commit runs
`just dev-check-design-deltas-applied` once every entry of the design is applied.

## Status

| Package | State | Rating |
|---|---|---|
| P2 | landed: 75bb1ddd | expert |
| P1 | landed: 2cae7fe4 | expert |
| P3 | in progress | mechanical |
| P4 | dispatchable | mechanical |
| P5 | dispatchable | expert |
| P6 | dispatchable | mechanical |

## P2 — The devpro settings file is TOML

Scope: `devpro/context.py` (`SETTINGS_FILE`, `MODEL_MAP_SECTION_SUFFIX`, `read_settings`,
`_settings_parser`, `_settings_values`, `_section_names`, `_harness_of`, and the refusal in
`_settings_file` naming the default `~/.config/devpro/devpro.cfg`), `devpro/cli.py` (the
`--config-file` help text, whose wording names `[<harness>]`, `[<harness>-model-map]` and the
`devpro.cfg` default), `devpro/family.py` (the module docstring naming `[<harness>-model-map]`),
`devtools/reference-maps/claude.cfg` and `devtools/reference-maps/opencode.cfg` (converted to
`.toml` and renamed), the `retake-reference` justfile target's paths to them, `tests/conftest.py`
(`settings_file`, which today writes `devpro.cfg`: it writes `devpro.toml` instead, and every test
that reads the fixture reads TOML text), `tests/test_devpro.py`, and
`tests/test_devpro_install.py`'s settings use.

The format: the file is TOML read with `tomllib`. `[<harness>]` tables carry `install` and
`components`; the model map is the dotted subtable `[<harness>.model-map]`, its keys quoted globs,
its values models. Each refusal keeps its place in the rework: the unknown-table refusal stays in
`read_settings`'s scan over `_section_names`/`_harness_of`; the unknown-key refusal stays in
`_settings_values`, which `read_settings` calls only where the harness's settings table exists; the
unparseable-file refusal is `_settings_parser`'s, which catches `tomllib.TOMLDecodeError` and names
the file and the line — `tomllib`'s message carries the position (`tomllib.loads('[claude]\nthis is
not an entry\n')` refuses with `Expected '=' after a key in a key/value pair (at line 2, column 6)`),
so naming the file and the line is implementable. Refusal semantics as SPEC states: a table named
for no supported harness is refused naming the table and the supported harnesses; a key in a
settings table that is no setting is refused naming the model-map table it belongs in; an
unparseable file is refused before anything is written. A repeated glob key is tomllib's own parse
error.

Facts, with their checks:
- The live converted file is `~/.config/devpro/devpro.toml` — `cat ~/.config/devpro/devpro.toml`
  shows `[opencode]` with `install = "detect"`, `[opencode.model-map]` with quoted glob keys, and
  `[claude]` with `install = "always"`; `ls ~/.config/devpro` today shows `devpro.cfg` beside it,
  the INI the code still reads.
- Glob order is file order: `python3 -c` over `tomllib.loads` of a `[c.model-map]` table holding
  `"*-architect"`, `"*-expert"`, `"stem-mechanical"`, `"*"` in that order prints the keys in that
  order (insertion order, dict-preserved). "Later entries silently overwriting earlier ones" is
  preserved.
- A `[DEFAULT]` table parses as an ordinary table (`{'DEFAULT': {'x': 1}}`), so the general
  unknown-table refusal covers it; configparser's special case has no successor.

Reference searches and answers:
- `git grep -l 'devpro\.cfg'` → `PROJECT_DOCS/SPEC/guide-and-readme.md`, `PROJECT_DOCS/SPEC/rendering.md`,
  `ROADMAP.md`, `devpro/cli.py`, `devpro/context.py`, `devpro/definitions/skills/guide.py`,
  `tests/conftest.py`, `tests/test_devpro.py`. The two SPEC leaves are design entries this package
  applies; `ROADMAP.md`'s mention is this ticket's source text, left as the roadmap stands;
  `guide.py`'s installation reference names the location — its text is updated here.
- `git grep -l 'model-map'` → the same leaves plus
  `PROJECT_DOCS/ARCHITECTURE/rendering/harnesses-and-families.md` (design entry),
  `PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md` (design entry),
  `ROADMAP_DESIGNS/CODEX_HARNESS_RESEARCH.md` (set-aside research, untouched), `devpro/family.py`,
  `devtools/reference-maps/*.cfg` (converted here), the tests.

Tests and fixtures pinning the behavior this package changes, updating them in scope:
`tests/test_devpro.py` — `_SUPPLIER` (:105, retexted to the TOML provenance: `devpro.toml` and the
dotted subtable; it feeds `test_parse_category_map_is_total_in_category_order`,
`test_parse_category_map_refusals` and the render supplies built from it) and the settings tests
`test_the_settings_file_names_its_harnesses_in_name_order_with_their_install_and_map` (this one also
pins the supplier string `read_settings` builds),
`test_a_settings_file_naming_no_harness_names_nothing_but_is_not_no_file`,
`test_a_render_takes_its_components_from_the_flag_alone`,
`test_a_missing_default_settings_file_is_no_config`,
`test_the_default_settings_file_is_read_from_the_home_directory`,
`test_a_named_settings_file_that_does_not_exist_is_refused_naming_the_path`,
`test_a_settings_file_section_no_harness_names_is_refused`,
`test_a_settings_sections_components_key_is_read_and_its_unknown_keys_name_both_keys`,
`test_a_settings_section_key_that_is_no_setting_is_refused_naming_the_map_section`,
`test_a_settings_file_that_does_not_parse_is_refused_naming_the_file_and_the_line` — all retexted to
TOML, `[<harness>.model-map]` and `devpro.toml`; `tests/test_devpro_install.py`'s settings-driven
installs (the case at 408 and the block at 845–1036).

Done-line: `just test devpro`, then `just dev-check-links`, run once at this package's end.

## P1 — Installs stage from the built wheel

Scope: `devpro/install.py` (the denylist — `EXCLUDED_DIRS`, `EXCLUDED_NAMES`, `EXCLUDED_SUFFIX` —
and `_shipped` retire with the copies they serve; `_shipped`'s call site feeding the stale list is
restated as prune's own guard: a file below a `.venv` directory (`VENV_DIR`) directly under a
package destination, and a safety copy (a `.bak` suffix), never enters the stale list), the justfile
`agents` recipe (build the wheel, unpack it beside it into `dist/`, run the plain install verb from
the unpacked package with `PYTHONPATH` pointed at it), `devtools/scripts/check-wheel.sh` (its
install comparison target), the CONVENTIONS leaf
`code-definitions-and-install/install-sources-are-filtered.md` (retired with the denylist —
its rule becomes the wheel's: the built package is the one filter, and a new copy source that
stages from anything else ships what the wheel never declared), `tests/test_devpro_install.py`, and
`tests/test_devpro.py`'s settings-driven install tests. P1 applies the first *Shipped files* pair
(the `tools/devpro/` one); that leaf's second pair is P3's. This package runs after `P2`: the
`settings_file` fixture its tests read then writes `devpro.toml`, and the settings text this
package's tests write is TOML — `[<harness>]` tables and `[<harness>.model-map]` subtables with
quoted glob keys.

The one manifest: the package copy copies the files the running package holds — its content, once
built, is the wheel's, `.dist-info/RECORD` the one manifest — and the harness resource copy reads
`resources/<harness>/` as the wheel carries it. A dev-loop install runs from the unpacked wheel in
`dist/`, whose parent holds no `.git` entry, so `PACKAGE_ROOT` resolves outside any checkout and no
`git` check answers for this repository.

Facts, with their checks:
- The build targets exist: the `build` recipe writes the wheel and sdist to `dist/`; the
  `check-wheel` recipe runs `./devtools/scripts/check-wheel.sh` (both justfile recipes).
- `PACKAGE_ROOT`, checked: `git grep -n 'PACKAGE_ROOT' -- devpro/` shows the definition once at
  `devpro/install_base.py:20` and reads as per-module bindings imported from `devpro/install_base`
  (`devpro/install.py:52`, `devpro/install_target.py:26`, `devpro/profiler/hooks.py:22`); no dotted
  read sits outside `install_base.py` itself (a docstring at `install_target.py:14` names it). The
  wheel-staged resolution is a change to the one definition; no read site moves. Tests monkeypatch
  `devpro.install.PACKAGE_ROOT` — the module-level binding the import at `devpro/install.py:52`
  creates — in the install tests listed below.

Reference searches and answers:
- `git grep -l '_shipped'` → `PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md` (design
  entry), `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/install-sources-are-filtered.md`
  (this package), `devpro/install.py`, `tests/test_devpro_install.py`, and two false positives —
  test functions whose own names contain "shipped" and assert nothing on the retired `_shipped`:
  `test_render_all_emits_every_file_of_a_shipped_skill_and_the_selection_drops_a_whole_definition`
  (`tests/test_devpro.py:678`) and
  `test_a_plain_reference_outside_the_shipped_set_refuses_naming_the_site_and_the_referent`
  (`tests/test_plugins.py:88`) — untouched.
- `git grep -l 'EXCLUDED_'` → `devpro/install.py` alone.

Tests and fixtures pinning the behavior this package changes, updating them in scope:
`test_a_resource_copy_skips_the_unshipped_vocabulary` (denylist on the resource walk),
`test_a_shipped_package_leaves_its_tests_and_documents_behind` (denylist on the package copy),
`test_a_project_install_writes_the_devpro_copy_and_a_wrapper_that_runs_it` (checkout-copy staging
through `_shipped`),
`test_an_install_run_from_an_installations_copy_into_that_installation_is_refused`
(monkeypatched `PACKAGE_ROOT`),
`test_reinstalling_over_a_copy_of_another_version_reports_both_versions`,
`test_a_second_mage_install_passes_over_its_own_manifest_byte_identical`,
`test_an_opencode_install_copies_the_harnesss_plugin_byte_verbatim`,
`test_a_user_level_install_writes_the_devpro_tools_package_and_no_other`,
`test_install_writes_every_render_and_stamps_the_packages_once` (banner origin path) — all in
`tests/test_devpro_install.py`.
The denylist tests reshape around wheel-staged installs: a tree that does not build cannot install.

Done-line: `just test devpro`, then `just test wheel`, then `just dev-check-links`, run once at
this package's end.

## P3 — The profiler's `doctor` and `repair` verbs are removed

Scope: `devpro/profiler/cli.py` (the verb list at lines 28–32 and the `doctor`/`repair` dispatch
arms in `run`, lines 53–96), `devpro/profiler/hooks.py` (`doctor` at 237–278, the `USAGE` lines
naming the verbs at 53–58), `devpro/profiler/stores.py` (`repair_child_ids` at 87–132; the module
docstring's "their one repair"), `devpro/profiler/__init__.py:8` (the docstring naming `doctor`),
`devpro/definitions/skills/profiler.py` (the "`init` and `doctor` are claude's alone" sentence at
37–38 and the two `doctor` instructions in the tree-troubleshooting paragraph at 65–70),
`devpro/definitions/skills/guide.py` (the `WRAPPER` clause at 109 and the
"`DP profiler doctor` names a store" line at 111 — the `DP` introduction drops with them),
`README.md` (the sentence "`devpro profiler doctor` names such a store with the move to make." at
line 231, dropped without replacement — the install's own `renamed <old> → <new>` report is the
signal; the README is the devpro-tech-writer's file, and the design's Code delta entry for this
change is the authorizing text for the edit), and every design entry of the profiler change.

The shared clause — ruled: the `{clauses.WRAPPER}` interpolation drops at
`devpro/definitions/skills/guide.py:109` only, with the doctor line at 111; nothing wider.
`devpro/clauses.py` is untouched — `WRAPPER` stays defined for `docdicer.py:84`'s interpolation and
`WRAPPER_PROFILER` for `profiler.py:40`'s, and no clause text changes. The guide body's only `DP`
consumer is line 111 itself (checked: `grep -n 'DP' devpro/definitions/skills/guide.py` matches
line 111 alone), so the introduction at 109 has no reader left after the deletion.

Reference searches and answers:
- `git grep -l 'repair_child_ids'` → `devpro/profiler/cli.py`, `devpro/profiler/stores.py`,
  `tests/test_devpro_profiler.py`.
- `git grep -l 'profiler doctor'` → `PROJECT_DOCS/ARCHITECTURE/harness-profiler/doctor-lines.md`
  (leaf removed by design entry), `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md` (design entry),
  `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md` (design entry),
  `devpro/definitions/skills/guide.py`, `devpro/profiler/hooks.py`.
- `git grep -ln 'doctor' -- devpro/profiler devpro/definitions` → the five files above plus
  `devpro/definitions/skills/profiler.py` and `devpro/profiler/__init__.py`.

Tests and fixtures pinning the behavior this package removes, deleting them in scope: the seven
tests of `tests/test_devpro_profiler.py` — `test_doctor_reports_a_committed_hook_that_differs_from_the_registered_one`
(:818), `test_doctor_names_the_wrapper_this_tree_runs` (:847),
`test_the_doctor_names_the_stores_the_readers_read` (:1448),
`test_a_doctor_names_an_old_pattern_store_and_its_remedy` (:1513),
`test_a_doctor_names_a_collided_store_as_the_operators_own_merge` (:1536),
`test_repair_fills_the_child_ids_a_capture_that_missed_2_4_1_left_null` (:1554),
`test_the_repair_counts_only_the_edges_it_writes` (:1598) — plus `tests/test_devpro_profiler.py`'s
module docstring, rewritten not deleted: the rename group's sentence stays and its `doctor` clause
("`doctor` names an old-pattern store the reader cannot see", line 18) drops; and the `doctor`
assertions in `test_init_renames_a_committed_hook_written_under_a_launcher_name` (:681; lines
714–723, which keep their `init` assertions and drop the `doctor` ones).

Done-line: `just test devpro`, then `just dev-check-links`, run once at this package's end.

## P4 — The development skill states the agents directory under claude

Scope: `devpro/vocabulary.py` (`OptionalHarnessText` gains the member `AGENTS_PATH = "agents_path"`),
`devpro/harness.py` (`Harness` gains the field `agents_path: str = ""`, in the optional tail —
`reload_rule: str = ""` is the pattern — so opencode and mage supply nothing and need no edit: ""
drops the paragraph),
`devpro/harnesses/claude.py` (supplies it under claude alone, the sentence a module constant:
"The plugin's agents files sit in `.claude/skills/devpro/agents/`." — the literal path, the same
path `devpro/profiler/hooks.py` holds as `INSTALL_WRAPPER`), `devpro/clauses.py` (gains
`AGENTS_PATH = "@!hrn-agents-path!@"`; `hole()` maps the member value `agents_path` to
`@!hrn-agents-path!@`), `devpro/definitions/skills/development.py` (a standalone paragraph directly
under the `## Dispatch` heading, carrying `{clauses.AGENTS_PATH}` — standalone so the paragraph
drops whole under the harnesses that supply nothing, leaving the section's bullets untouched), and
a new pinning test. The wiring, stated so no choice remains: the sentence is a constant in
`devpro/harnesses/claude.py` bound to the new `Harness.agents_path` field; `devpro/render.py` fills
each hole from the bound harness (`values = {hole(part): ctx.bound_harness.text(part) …}`) and
drops the paragraph an empty optional stands in; `development.py`'s body carries the
`clauses.AGENTS_PATH` placeholder. `harness.py`'s validation and `render.py`'s filling consume
members generically — no change there beyond the field.

The test: `tests/test_devpro.py::test_the_development_skill_names_the_agents_directory_under_claude_and_drops_the_paragraph_under_opencode`,
in the shape of
`test_a_coder_and_a_platform_expert_render_the_recipe_rule_under_claude_and_drop_it_under_opencode`
(:1066): the claude render of the `development` skill carries the sentence naming
`.claude/skills/devpro/agents/`, and the opencode render carries neither the sentence nor an empty
paragraph where it stood. It lives in `tests/test_devpro.py`, which the done-line's
`just test devpro` runs. The named defect: the claude session seat reading the skill has no
statement of where the agents files live, so the model improvises a path at dispatch time — the
test fails while the sentence is absent from the claude render.

Reference searches and answers:
- `git grep -l 'OptionalHarnessText'` →
  `PROJECT_DOCS/ARCHITECTURE/rendering/harnesses-and-families.md` (design entry),
  `PROJECT_DOCS/ARCHITECTURE/rendering/placeholders.md`, `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md`,
  `devpro/harness.py`, `devpro/render.py`, `devpro/vocabulary.py`, `tests/test_devpro.py`.
  The two ARCHITECTURE leaves describe the mechanism and need no change for a seventh member;
  `devpro/harness.py` and `devpro/render.py` consume members generically.
- The member-list test `test_the_text_module_spells_each_render_placeholder_as_the_renderer_fills_it`
  (the `@pytest.mark.parametrize` over `*HarnessText, *OptionalHarnessText, *TuningText` in
  `tests/test_devpro.py`, near :898) asserts `getattr(devpro.clauses, part.name) == hole(part)` for
  every member. It needs no new case: the new member is covered by the parametrization once
  `clauses.AGENTS_PATH` exists, and fails without it — which is why the clauses constant is in
  scope.

Done-line: `just test devpro`, then `just dev-check-links`, run once at this package's end.

## P5 — Post-plan review

Scope: the changes and tests `P1`–`P4` landed, reviewed by the post-plan reviewers — the coder seat
for each changed language, `devpro-architect` for the structure, `devpro-prompt-engineer` for the
model-facing text the plan changed. Each reviewer receives the project documents and
[ACTIVE_DESIGN.md](ACTIVE_DESIGN.md). Output: each reviewer writes their own review to
`.devpro-temp/`, one file named for its seat; this session synthesizes them into
`ACTIVE_PLAN_REVIEW.md`.

Done-line: `just dev-check-links`, run once `ACTIVE_PLAN_REVIEW.md` is written.

## Post-plan burndown

### P6 — Post-plan burndown drafting

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands: every finding enters as an
item carrying its severity, the files and functions it names, and the guidance that closes it. This
section holds nothing until then.
