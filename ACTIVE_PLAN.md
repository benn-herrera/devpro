# The test suite earns its keep: the plan

The plan of [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) ("The test suite earns its keep", final form).
The design is authoritative; this plan cites its entries rather than restating them. The design
holds two entries named `repo-layout` and two named `recipes`: the first pair under
`## ARCHITECTURE delta` (cited here as `#repo-layout` and `#recipes`), the second pair under
`## Code delta` (cited as `#repo-layout-1` and `#recipes-1`) — anchors deduplicated in file order.

Every package's intended lifetime is **shipped**.

**Sequencing.** P1, P2 and P3 run in parallel — disjoint paths, and each commits only its own
paths (`git commit -- <paths>`). P4 follows P3 (both edit the justfile; one file, one writer).
P4 and P5 run in parallel (disjoint paths). The pass packages P6, P7 and P8 run in parallel — they
begin only once P1 (the amended law they satisfy) and P2 (the interrupt rule) have landed, and P5
has landed before P6 begins: P5 and P6 both edit `tests/test_devpro_profiler.py`, one file, one
writer — P5 is pre-pass and lands in its own slot, P6 starts after it. P9 follows the pass
packages, its judgment needing their outcomes settled before it measures what remains. P10 is
last. The brief rules: the marker machinery and the screenshot marking belong together (P3); the
interrupt leaf lands before the pass packages begin (P2 before P6–P9); the pin removals are
independent of the marker work (P4 holds no dependency on P3 but for the justfile's file-level
exclusivity). A package whose done-line runs `just dev-check-design-deltas-applied` can pass it
only after P1 has landed — the check compares the design's fenced pairs against the targets and
fails until then; only P1 and P10 run it.

**Plan mechanics.** The status table's `Lifetime` column carries each package's intended lifetime
— `shipped` in every row; the column is the form's carrier, the `Lifetime` lines in the package
bodies repeat it for a reader of one package alone. P11 is the plan's one ticket whose body arrives
later: it stands here with its drafting line only, and once the post-plan review lands its body is
replaced by the burndown items cut from `ACTIVE_PLAN_REVIEW.md` — each item carrying a severity, a
finding, a location and guidance, one commit per item, each resulting package `shipped` and given
its own status-table row.

**Scope notes the owner ruled, and their reading.**

- No package edits `tests/test_devpro_install.py` — installation is the most fraught operation.
  The one exception is the design's own order: the retirement of
  `test_the_opencode_resources_name_the_host_version_the_check_is_pinned_to` (P4). The constraint
  bars *pass work* — perf rewrites of the suite's tests — not the design's delta entries.
- The profiler `doctor` and `repair` tests get no pass work; their operations' retirement is
  roadmap work, ticketed as *Eliminate profiler `repair` and `doctor`*. The design invests nothing
  there. A file-level fixture change that leaves their test bodies untouched is not work on them
  (P6 states its own boundary).
- No test beyond the six screenshot tests takes the `slow` marker in this work.

**Facts of record** (measured; the durations probe is `.devpro-temp/weight-durations-full.txt`):

- `just test devpro` = 54.03s, 1670 passed. `just test dupe_sweep` minus the screenshot file =
  0.67s. The six screenshot tests sum 112.26s of the ~172s no-surface pytest run. Target: the
  default run's pytest portion at 30s.
- Per-file sums from the probe: `devtools/tests/test_screenshot.py` 112.26,
  `tests/test_devpro_install.py` 17.23, `tests/test_devpro_profiler.py` 10.98,
  `tests/dicing/test_server.py` 7.55 (now `tests/dashboard/test_board_panel.py` — the probe
  predates commit 785feef's move; its `tests/dicing/test_server.py` rows read as that file),
  `tests/dicing/test_dicer.py` 4.90, `tests/dashboard/test_server.py` 4.85,
  `tests/test_devpro.py` 2.20, the rest under 1.7 each.
- The 30-second target's arithmetic, stated so no package "fixes" it wrongly: 17.23s of the
  54.03s `devpro` surface sits in `tests/test_devpro_install.py`, which the pass may not edit.
  The target is therefore reachable only if the remaining ~37s falls to ~13s; the pass's judgment
  packages aim at it, and the design itself calls the target a planning-time measurement, "not a
  check the pass runs" ([ACTIVE_DESIGN.md](ACTIVE_DESIGN.md#repo-layout-1)). P10 reports the
  measured end state against the target without manufacturing a pass.

## Status

| Package | State | Rating | Lifetime | Scope |
|---|---|---|---|---|
| P1 | landed | mechanical | shipped | PROJECT_DOCS/ARCHITECTURE deltas |
| P2 | landed | mechanical | shipped | the interrupt rule's CONVENTIONS leaf |
| P3 | landed | mechanical | shipped | the `slow` marker and the screenshot tests |
| P4 | landed | expert | shipped | the opencode pin's single home |
| P5 | landed | mechanical | shipped | retire the checksums |
| P6 | landed | expert | shipped | the profiler's shared wrapper fixture |
| P7 | landed | expert | shipped | the server-boot tier earns its keep |
| P8 | landed: judged, no edit | expert | shipped | the dicer suite earns its keep |
| P9 | landed | expert | shipped | the long tail over 100ms |
| P10 | landed | expert | shipped | post-plan review |
| P11 | dispatchable | expert | shipped | post-plan burndown |

## P1 — Apply the ARCHITECTURE deltas

**Scope.** `PROJECT_DOCS/ARCHITECTURE/repo-layout.md` and
`PROJECT_DOCS/ARCHITECTURE/recipes.md`; nothing else.

**Work.** Apply the design's two ARCHITECTURE delta entries to their target leaves, verbatim:

- [repo-layout](ACTIVE_DESIGN.md#repo-layout): the two passage pairs — the `tests/` tree lines
  gaining the `slow` marker and `slow` surface, and the test-law paragraph inserted ahead of the
  module-dependency paragraph.
- [recipes](ACTIVE_DESIGN.md#recipes): the lint paragraph's passage pair — the pin's single-home
  rule inside the sentence about the root `package.json`.

Application is byte-exact per
[A delta application ends verified](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md),
followed by the doc-set search per
[A delta application ends by searching the doc set](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-by-searching-the-doc-set.md):
a statement the application leaves false in another leaf is reported to the session, not rewritten
where it stands — the entry's scope is its target leaf, and the session schedules the stale
statement's fix for the commit that carries the change, whichever package's commit that is.

**Facts.** The passages the pairs replace stand today at `repo-layout.md:44-45` (the two `tests/`
lines) and `repo-layout.md:48-50` (the module-dependency paragraph, which stays), and
`recipes.md:62-64` ("...a root `package.json` holds it — and the check"). The design's from-blocks
quote both; `--deltas-applied` is the witness of the application.

**Done.** `just dev-check-design-deltas-applied` (this package is the one that satisfies it);
`just dev-check-links`.

**Commit.** One commit: `git commit -- PROJECT_DOCS/ARCHITECTURE/`.

**Lifetime.** Shipped.

## P2 — The interrupt rule's CONVENTIONS leaf

**Scope.** A new leaf
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-test-failing-on-unstated-behavior-is-an-interrupt.md`,
plus one contents line in `PROJECT_DOCS/CONVENTIONS/planning-and-execution/index.md` and one in
`PROJECT_DOCS/CONVENTIONS/entry-point.md` (the check-tree requires every document listed by its
parent). Nothing else.

**Work.** The design's intent names the leaf and its three verdicts
([ACTIVE_DESIGN.md](ACTIVE_DESIGN.md): "a test that fails on behavior the work does not state it
changes enters the active plan as an interrupt, its verdicts — *axe*, *isolate*, *acquit* — defined
in a CONVENTIONS leaf this design's plan writes; a project convention, not the shipped process's
law"). This plan writes the leaf; the text below is the package's input:

```
# A test failing on unstated behavior is an interrupt

A test that fails on behavior the work under way does not state it changes stops its package and
enters the active plan as an interrupt: a recorded question with its verdict, not noise inside a
package's run. One of three verdicts settles it:

- **axe** — the test asserts more than a defect needs: a checksum over text, or a seam no stated
  requirement names. The test is removed, its failure with it.
- **isolate** — the behavior the test pins is real, but this work does not state it changes: the
  test is quarantined from the default run — skipped or expected to fail, naming the reason and the
  ticket that carries the behavior — and the pass proceeds. The behavior is roadmap work, not this
  plan's.
- **acquit** — the failure is not the work's doing: the test fails the same way without the work's
  changes, or on its environment alone. The record says how that was shown, and the pass proceeds
  with the test standing.

A failure that shows the work *should* change the behavior it broke is none of these: it is a scope
finding, routed through the design like any other.
```

The heading satisfies
[Section and rule heading brevity](PROJECT_DOCS/CONVENTIONS/section-and-rule-heading-brevity.md);
the wording may be tightened to that leaf's rule, the three definitions' substance stays. The
contents lines name the leaf as its title does in the sibling lists.

**Done.** `just dev-check-links` (the new leaf listed by both its parent lists, reachable from the
entry point).

**Commit.** One commit: `git commit -- PROJECT_DOCS/CONVENTIONS/`.

**Lifetime.** Shipped.

## P3 — Register the `slow` marker and mark the screenshot tests

**Scope.** `pyproject.toml` (markers), `devtools/scripts/test.sh`, the justfile's `test` recipe
comment, and the six tests in `devtools/tests/test_screenshot.py`. Implements the fifth bullet of
[repo-layout](ACTIVE_DESIGN.md#repo-layout-1) (the code delta). The marker machinery and the
screenshot marking are one package and one commit.

**Facts.**

- `pyproject.toml:56-58` holds the marker list today, one entry:
  `"cold_read: the shipped cold-read.sh suite, one test per subprocess case — a rare manual surface
  (`just test cold-read`), excluded from the default run"`. The `slow` entry is registered beside
  it in the same shape, e.g. `"slow: a test that earns its cost but not its place in the default
  run — the screenshot suite today (`just test slow`), excluded from the default run"`.
- `devtools/scripts/test.sh:34-38` is the surface case (`"" ) dirs=(tests devtools/tests);
  full_run=1`, `devpro) dirs=(tests)`, `dupe_sweep) dirs=(devtools/tests)`,
  `cold-read) dirs=(tests)`), `test.sh:97-101` the default `-m` block
  (`cold-read) marker=(-m cold_read)`, `*) marker=(-m "not cold_read")`), and `test.sh:54` the
  error message naming the valid surfaces. The `slow` extension mirrors the `cold_read` shape and
  touches four sites: the surface table gains a `slow` row (the marked tests live in
  `devtools/tests`, so `dirs=(devtools/tests)`); the default `-m` case gains its `slow` arm
  (`marker=(-m slow)`) and its `*)` arm becomes `"not cold_read and not slow"` — which is the
  no-surface run's default too, the run reaching the marker block with `surface=""` and falling
  under `*)`; and the error message's valid-values list gains `slow`. A caller's own `-m` still
  wins everywhere.
- The six screenshot tests, `devtools/tests/test_screenshot.py:99,119,134,153,183,210`:
  `test_a_settled_page_is_shot_whole_at_the_viewport`,
  `test_a_selector_that_never_appears_fails_naming_it_and_the_timeout`,
  `test_a_route_is_resolved_against_base_before_the_filesystem`,
  `test_a_polling_page_with_a_selector_is_shot`,
  `test_a_polling_page_without_a_selector_still_shoots`,
  `test_a_page_shown_in_the_wrong_scheme_fails_and_writes_no_png`. Each takes `pytest.mark.slow`.
  Probe rows: 31.77, 31.67, 31.23, 7.67, 5.23, 4.69 seconds.
- The justfile's `test` recipe comment (justfile:199-206) names the surfaces —
  "(devpro, dupe_sweep, cold-read, docs, wheel)" — and is the record that moves with the change:
  it gains `slow` where it names the surface list. The recipe body itself needs no edit; the
  surface name reaches `test.sh` as $1.

**Behavior changed.** Every default run excludes `slow` — the no-surface run and the `devpro` and
`dupe_sweep` surfaces run `-m "not cold_read and not slow"`, the design's law's "every default run
excludes it" and its 30-second target both assuming the screenshot suite out of every default run —
and a new `slow` surface runs the marked tests. No test pins this — the surface selection is the
runner script's, checked by the runs below, not by a unit test. What the package observes at its
own end is the amended runner itself: the six `pytest.mark.slow` lines in
`devtools/tests/test_screenshot.py`, the `slow` row and marker arms in `test.sh`, and the four
runs below showing the six out of the default surfaces and in the `slow` surface. The amended
repo-layout leaf states the rule; P1's `--deltas-applied` run is the witness of the leaf, not this
package's gate, and this package runs no deltas check.

**Done.** `just test dupe_sweep` (the six deselected, the surface back to its probe weight ~0.7s);
`just test slow` (the six run, and nothing else); `just test devpro` (1670 passed, unchanged);
`just test cold-read` (the cold-read surface's behavior unchanged by the new default marker);
`just test` (the no-surface run: its pytest portion shows the six deselected — the run whose
exclusion the plan's Facts arithmetic and P10's report both assume); `just lint`.

**Commit.** One commit: `git commit -- pyproject.toml devtools/scripts/test.sh devtools/tests/test_screenshot.py justfile`.

**Lifetime.** Shipped.

## P4 — The opencode pin's single home

**Scope.** The three opencode resource headers (`devpro/harnesses/resources/opencode/index.ts`,
`guardrail.ts`, `profiler.ts`), the justfile's `_lint-typescript` comment, the retirement of the
headers-versus-lockfile test in `tests/test_devpro_install.py`, and the CONVENTIONS leaf
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-host-version-is-checked-against-the-host-s-declarations.md`.
Implements [recipes](ACTIVE_DESIGN.md#recipes-1) (the code delta). Depends on P3 only for the
justfile's file-level exclusivity.

**Facts.**

- The headers name the pin of the moment in their headlines:
  `index.ts:3` — `// Written for opencode 2.4.1 (floor 2.3.0): the entry of one plugin ...`;
  `guardrail.ts:3` and `profiler.ts:3` — `// opencode 2.4.1 plugin module (floor 2.3.0)`.
  `package.json:6` holds the pin: `"@opencode/plugin": "2.4.1"`.
- The prose's version numbers are behavior observations and stay — e.g. `index.ts:10-12` ("every
  API used here exists at 2.2.6 ... From 2.3.0"), `profiler.ts:11-12` ("`result.sessionID` on
  2.4.1, `result.output.sessionID` on 2.3.2 ...").
- The retired test, `tests/test_devpro_install.py:2251-2265`, compares each header's headline
  version against `package.json`'s pin and fails on a mismatch — the seam the single-home rule
  removes. Its `_RESOURCE_BANNER_LINES` helper stays: `test_devpro_install.py:2244` uses it in
  another test.
- The records naming the header-named version: the justfile's `_lint-typescript` comment
  (justfile:234-235) — "...`bun.lock`, which is pinned to the host version the resources name" —
  and the CONVENTIONS leaf's closing sentence
  (a-host-version-is-checked-against-the-host-s-declarations.md:13-14) — "pinned to the version the
  resource's header names (ARCHITECTURE.md, Recipes)".

**Work.** The headlines drop the pin numeral and keep the floor and the prose: `index.ts:3`
becomes `// Written for opencode (floor 2.3.0): ...`; `guardrail.ts:3` and `profiler.ts:3` become
`// opencode plugin module (floor 2.3.0)`. The wording may be adjusted to read naturally; the pin
numeral goes, the floor and the prose stay. The guard test's function is deleted whole. The
justfile comment now states the lockfile is pinned to the version `package.json` names — the pin's
one home. The leaf's closing sentence states the same single-home rule in the leaf's own voice,
citing the amended Recipes leaf; the leaf's subject — the declarations are the authority, never a
devpro-owned stub — stays. This is the package's one judgment; everything else is enumerated.

**Behavior changed.** The resources' header comments no longer restate the pin. The test that
pinned the (removed) duplication retires with the seam; no test replaces it — an absence of
duplication needs no guard, and the pin's one reader is mechanical already: the lockfile
`_js-deps` installs frozen (`bun install --frozen-lockfile`, justfile:253-254) resolves
`package.json`'s pin and fails on a lockfile that disagrees with it; `just lint` runs it. The
CONVENTIONS leaf's rewording is carried by `just dev-check-links` and by this package's commit.

**Done.** `just lint` (the tsc check runs against the declarations the frozen lockfile resolves
from `package.json`'s pin); `just test devpro` (the retired test gone, the install suite otherwise
untouched); `just dev-check-links`.

**Commit.** One commit: `git commit -- devpro/harnesses/resources/opencode/ justfile tests/test_devpro_install.py PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-host-version-is-checked-against-the-host-s-declarations.md`.

**Lifetime.** Shipped.

## P5 — Retire the checksums

**Scope.** `tests/test_devpro.py` and `tests/test_devpro_profiler.py`. No stated behavior changes —
what the package does is retire the members mirror and replace it with a keys-only assertion, and
strip the tuned values from the two frontmatter tests' comparisons; the tests' subjects stay.

**Facts.**

- The members mirror, `tests/test_devpro.py:1270-1310`: a parametrize hand-copying each family's
  category map (`claude`, `qwen3`, `gemma-4`) and comparing the loaded map against the copy —
  `test_each_family_pins_the_member_of_every_category` at line 1309,
  `assert dict(load("devpro.families", "FAMILY")[name].categories) == members`. The model already
  states the structural claim: `devpro/family.py:89` — "exactly CATEGORIES, in CATEGORIES order".
- The two frontmatter tests, `tests/test_devpro.py:426-434` and `:445-452`: full-tuple equality
  including `"model: opus"` and the color hexes `'color: "#DC2626"'` / `'color: "#3776AB"'`.
- The stylesheet-literal assertion, `tests/test_devpro_profiler.py:1200-1202`:
  `assert LAYER_LINK == ...` (structural, stays), `assert SHARED_CSS not in index` (structural,
  stays), `assert layer == SHARED_CSS` (the literal comparison, goes). The `layer` fetch at line
  1198 exists only to feed it and goes with it.

**Work.** Implements the first three bullets of [repo-layout](ACTIVE_DESIGN.md#repo-layout-1) (the
code delta).

- The members mirror is retired; the structural claim stays as an assertion over the map's keys:
  for every loaded family, its categories map's keys are exactly the category slots
  `devpro/family.py`'s `CATEGORIES` names — no slot missing, no other present. The comparison's
  form is the design's own words, keys only — `set(family.categories) == set(CATEGORIES)` — the
  set defect, not the model's ordering; `devpro/family.py:89`'s "exactly CATEGORIES, in CATEGORIES
  order" is the model's own stronger statement and is not restated here. The hand-copy parametrize
  table is deleted with the test. The assertion's defect (`clauses.TEST_PRECONDITION` shape): a
  family module whose loaded categories map drops a slot or carries one beyond the category slots
  — the structural claim the mirror over-pinned.
- The two frontmatter tests keep the contract they assert — field order, spelling, presence — and
  drop the tuned values. The decision, stated: each test's tuple comparison keeps its shape and
  order, and the two tuned slots stay in the tuple asserted value-free — the `model:` and
  `color:` lines are matched on their field name's spelling and presence, `model: ` and
  `color: ` prefixes, with no pinned value — so a retune of `model:`'s value or a recolor passes
  and a dropped or reordered field still fails. The `name`, `description` and `tools` members stay
  exact.
- The stylesheet-literal assertion and its now-dead fetch are removed; the neighboring assertions
  carry the invariant.

**Done.** `just format-python` (the edited files), `just test devpro`, `just lint`.

**Commit.** One commit: `git commit -- tests/test_devpro.py tests/test_devpro_profiler.py`.

**Lifetime.** Shipped.

## P6 — Share the profiler's wrapper fixture

**Scope.** `tests/test_devpro_profiler.py`: the `_launcher` helper (line 121) and its ~27 call
sites; the fixture machinery only, no test-body edits in the `doctor` and `repair` tests — and
those tests keep a private `_launcher` regardless of what the inspection below finds, the one way
both the scope fence and a shared fixture hold. The package writes nothing to
`tests/test_devpro_install.py`: P4's edit there removes the guard test whole and does not touch
`_definition_install` (line 74), which `_launcher` imports, so the import P6 rides is unaffected.
The first pass-work package; P2's leaf landed.

**Facts.**

- `tests/test_devpro_profiler.py:121-129`: `_launcher(directory)` runs
  `_definition_install(directory, project_root=directory)` — an in-process full definition install
  — and returns the written wrapper's path. Call sites at lines 242, 290, 320, 334, 348, 362, 416,
  439, 648, 709, 820, 833, 853, 934, 1022, 1049, 1071, 1084, 1106, 1128, 1195, 1387, 1455, 1522,
  1544, 1577, 1675 — each `tmp_path / "harness"` or similar, one install per test.
- The file's probe sum is 10.98s across ~50 tests; no single test exceeds 0.59s — the weight is the
  repeated install, not any one test.
- The wrapper tree is read-only to a test that only runs it: the stores a test writes go under its
  own `project`, never under `tmp_path / "harness"`. This is the survey's reading of the call
  sites, offered as a starting observation and not as a guarantee — the package's first step
  re-establishes it by inspecting the ~27 call sites for any test that writes into the wrapper
  tree it was handed (an edited wrapper, a planted file under the install — the `doctor` and
  `repair` tests at `:1577` and `:1675` among the sites to read, their verdict already fixed: a
  private launcher), and the sharing stands only on what that inspection finds.

**Work.** Judge first, then share: inspect the ~27 call sites for any test that writes into the
wrapper tree it was handed (an edited wrapper, a planted file under the install) — the
wrapper-failure tests are the likeliest. Tests that only read and execute the wrapper share one
session-scoped fixture (built once under `tmp_path_factory`, the same install `_launcher` runs
today); tests that write into the tree keep a private launcher. The shared fixture changes no
test's subject; any test the sharing breaks is an interrupt under P2's leaf, not a reason to
abandon the fixture. No new test is added; if one is, its docstring names the defect it dies on.

**Done.** `just format-python`, `just test devpro`, `just lint`. The package records the measured
`just test devpro` wall time before and after its change (re-measured the survey's way —
`--durations` output kept under `.devpro-temp/`) so the fixture tax's amortization is a number,
not a claim.

**Commit.** One commit: `git commit -- tests/test_devpro_profiler.py`.

**Lifetime.** Shipped.

## P7 — The server-boot tier earns its keep

**Scope.** `tests/dashboard/test_board_panel.py` (22 tests) and `tests/dashboard/test_server.py`
(38 tests). No production code changes.

**Facts.**

- Both suites boot the real server per test, in process:
  `tests/dashboard/conftest.py:16` imports `DashboardServer`, and the suites' `serve` fixture
  starts it per test against a per-test project.
- Probe sums: 7.55s under the probe's `tests/dicing/test_server.py` rows — now
  `tests/dashboard/test_board_panel.py` per 785feef's move — and 4.85s for
  `tests/dashboard/test_server.py`.
- The board wait test is already cheapened: `tests/dashboard/test_board_panel.py:291`,
  `waiter.join(0.5)` — the probe's 2.01s row for
  `test_the_payloads_since_reaches_the_board_as_a_wait` is the pre-move 2s window, not this file's
  present cost.

**Work.** Judge honestly against the amended law
([ACTIVE_DESIGN.md](ACTIVE_DESIGN.md#repo-layout)): a test whose setup, call and teardown exceed
100ms earns its place — it pins a real defect no cheaper test pins, or exercises a real integration
no fixture can stand in for — or loses the weight. The servers hold state (a served project's
board, its stores, `stop_all`), so a per-test boot is often an honest cost: these tests exercise
the real serving loop, and a shared server across tests with different projects would couple what
the tests pin separately. Merge only where two tests boot the server to pin the same defect;
cheapen only where a test's weight is an incidental wait, not the integration itself. Where a
survivor's cost is the integration, say so in the package's report and leave it standing — that is
the law's "earns its place" verdict, not a failure to act. A test that fails on unstated behavior
under this work is an interrupt under P2's leaf.

**Done.** `just test devpro`, `just lint` (any edited test file), with the package's report naming
each test judged and its verdict.

**Commit.** One commit: `git commit -- tests/dashboard/`.

**Lifetime.** Shipped.

## P8 — The dicer suite earns its keep

**Scope.** `tests/dicing/test_dicer.py` (9 tests, heavily parametrized). No production code
changes.

**Facts.**

- Probe sum 4.90s, the file's own weight; the individual `call` rows are small (0.04–0.09s each
  across the `test_cases` and `test_undice_then_dice_reproduces_the_tree` ids), so the weight sits
  in setup and fixtures — the package measures with `--durations` including setup before judging.
- The suite dices large fixtures on the CPU: the cost is the dicer's real work, not sleeps or
  subprocesses.

**Work.** Judge earn or cheapen under the amended law. A CPU-bound dicing run over large fixtures
is plausibly the real integration the law's "earns its place" names — dicing is the package's
subject and no fixture can stand in for the dicer — but if the same defect is pinned equally by a
smaller fixture set, the weight comes down. Cheapen by shrinking fixture size or merging duplicate
cases; do not mark anything `slow` (the owner's ruling: no other test takes the marker). A test
that fails on unstated behavior under this work is an interrupt under P2's leaf.

**Done.** `just test devpro`, `just lint` (if the file is edited), with the report naming the
verdict per judged test.

**Commit.** One commit: `git commit -- tests/dicing/test_dicer.py`.

**Lifetime.** Shipped.

## P9 — The long tail over 100ms

**Scope.** Every test whose setup, call and teardown sum exceeds 100ms, across `tests/` and
`devtools/tests/`, *except*: `tests/test_devpro_install.py` whole (owner's ruling), the `doctor`
and `repair` tests of `tests/test_devpro_profiler.py` (roadmap-ticketed retirement), and the six
screenshot tests (already marked, P3). Runs last: P6–P8's outcomes decide what weight remains for
this package to judge.

**Facts.**

- The amended law is the judge
  ([ACTIVE_DESIGN.md](ACTIVE_DESIGN.md#repo-layout)): every test above 100ms earns its place — a
  real defect no cheaper test pins, or a real integration no fixture can stand in for — or is
  rewritten to a fixture, merged into a sibling, retired, or marked `slow`; and no test beyond the
  six screenshot tests takes the marker in this design's work.
- The survey probe predates 785feef's file move; the package re-measures before judging (the
  survey's method: the surfaces' `--durations` output kept under `.devpro-temp/`), so its verdicts
  rest on the tree as it now stands. The threshold is per test — setup, call and teardown — never
  per file: the files whose per-file sums lead in the survey (`tests/test_devpro.py` 2.20s,
  `test_devpro_floor_check.py` ~1.36s, `test_guardrail.py` ~1.57s, `test_install_target.py`
  ~1.67s, the profiler file's remainder, and whatever P6–P8 left) enter the scope only through the
  tests over the threshold, named by the re-measure's `--durations` output.

**Work.** For each test above the threshold: name its defect and answer whether a cheaper test
pins it or a fixture can stand in; then rewrite, merge, retire, or — where the verdict is "earns"
— leave it standing with the reason recorded. Retirements here follow the same shape P5 applied
(the claim dies with the checksum, the structural claim stays where one lives beneath). Any added
or rewritten test names the defect it dies on in its docstring, with the run that fails under it
(`clauses.TEST_PRECONDITION` shape). A test that fails on unstated behavior under this work is an
interrupt under P2's leaf.

**Done.** `just format-python` (edited files), `just test devpro`, `just test dupe_sweep`,
`just lint`. The report lists each test judged, its verdict, and the run's measured end state
against the 30-second target.

**Commit.** One commit: `git commit -- <the files P9 edited>`, the list read from `git status`
before staging — the two trees are the search's range, not the commit's scope.

**Lifetime.** Shipped.

## P10 — Post-plan review

**Scope.** The whole tree, read; no edits except the status table's states and, where the review
finds a gap, the plan's own correction.

**Work.** Read [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) whole against the tree: every ARCHITECTURE
delta applied (P1), every code-delta bullet landed (P3–P5), the interrupt leaf standing where the
pass packages could reach it (P2), the pass work done and honestly reported (P6–P9), and no
constraint breached — the install suite edited only by P4's design-ordered retirement, no
`doctor`/`repair` pass work, no `slow` marker beyond the six screenshot tests. Verify the
application and the gates, and report the measured end state against the 30-second target with its
baseline named: the comparison is against the default run's pytest portion *after* P3's exclusion —
the post-P3 default run, whose pytest portion the Facts block's pre-P3 figures (54.03s surface,
112.26s screenshots) describe only as the state the pass started from — and the `slow` surface's
own run reported separately, never folded into the default figure. The design calls the target a
planning-time measurement, "not a check the pass runs"; the report states the number and the gap,
and manufactures no pass.

**Done.** `just dev-check-design-deltas-applied`; `just dev-check-links`; `just lint`;
`just test` (the default run: both pytest surfaces, then docs and wheel). Every row of the status
table that is done reads `landed`.

**Commit.** One commit: the plan's own state corrections, if any.

**Lifetime.** Shipped.

## Post-plan burndown

### P11 Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
