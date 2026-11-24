# The profiler reads true: stores, model config, scratch, and no mocking oracles

The design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), accepted. Each package below applies its named
entries verbatim over their targets — the pairs' from-blocks match the leaves as they stand. The
packages that apply pairs close with `just dev-check-design-deltas-applied`, which confirms each
landed. A Code entry applies to no leaf and has no pair for the check to see. The entries' code
changes are stated in the design; the packages name the files, the facts and the pins.

Every package's intended lifetime is **shipped**.

The tree is green at the plan's revision commit: `just test` passes with the `cold_read` suite
excluded from the default run (c602203) and `just test cold-read` passes on its surface. The
`rendered/reference-*` slots are stale against the profiler's landed changes; retaking them is
B7's convention, available at the owner's timing, and no package below retakes them.

Packages run serially on the shared tree, one commit per package, each closing with its done-line
run and its board row committed second. A package whose tests fail on behavior it does not state
it changes reports the failure as a finding — the test is never edited to pass.

## Status

| Package | State | Rating | Scope |
| --- | --- | --- | --- |
| P1 | landed (748c330) | expert | the plugin's configured model applies at runtime |
| P2 | landed (67d4516) | expert | the stores read true: exact names, both readers, the doctor's line |
| P3 | landed (cd50d71) | expert | the scratch guarantee's one home: install prepares, the clause drops |
| P4 | landed (f1c226a) | expert | the stand-ins' removal and the mock-as-oracle clause |
| R | landed (2c48159) | expert | Post-plan review |
| B | in progress: B1 and B2 hold for the owner's rulings; B4 continuing under the ruled extension, B3 landed, B5–B8 next | expert | Post-plan burndown |

### P1 — the plugin's configured model applies at runtime

Applies: the [Opencode entry](PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md#opencode-entry)
Code delta entry.

Scope: `devpro/harnesses/resources/opencode/index.ts`'s `setup` — the agent domain's `transform`
callback, `index.ts:180–194`, the cast at 190 — and `tests/test_opencode_entry.py:104`.

The fact the entry acts on: the *Registration* passage states each agent record updates the agent
of that id with the model where the record has them, while at runtime on opencode 2.4.1 the host
reads an agent's model from its own store — the registry's model applied through the cast at
`index.ts:190` (`if (entry.model) agent.model = entry.model as NonNullable<typeof agent.model>`)
never reaches it. The fix applies the configured model in `setup`'s agent-domain `transform`
callback, where the 2.4.1 runtime reads it. The entry leaves the mechanism's exact wiring to the
executor where the host's reading site admits more than one — the outcome is the leaf's statement
true at runtime, pinned by a test that drives `Plugin.define`'s setup with a configured model and
observes it applied. `tests/opencode_plugin_stub.ts` and `tests/opencode_entry_runner.ts` are the
drivers for that pin.

The pin: the new pin at `tests/test_opencode_entry.py:104` observes the configured model on a
second stub store standing in for the host's own-store read — a store the entry's setup populates —
and must fail at the base commit before the fix. The existing model assertion
(`tests/test_opencode_entry.py:151`) passes today only because the stub's editor is the only store
the stub has; whether the new pin replaces it or joins it is the executor's call, stated in the
report.

Type-check note: `just lint` type-checks what ships against the host's published declarations —
the fix casts at the boundary with the why-comment the resources carry.

Done-line: `just test`, `just lint`.

### P2 — the stores read true: exact names, both readers, the doctor's line

Applies: the [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md#harness-profiler)
ARCHITECTURE delta entry (three pairs) and the
[Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md#harness-profiler) Code
delta entry.

Scope: `devpro/profiler/values.py`, `devpro/profiler/pages.py`, `devpro/profiler/hooks.py`,
`tests/test_devpro_profiler.py`, `tests/dashboard/test_server.py`, the leaf.

The facts the entry acts on: `TRACE_GLOB = ".profiler-*"` (`values.py:18`); both readers glob it —
`pages.list_sessions` (`pages.py:679`, the tree's render) and `pages.store_directories`
(`pages.py:758`, the index and the session pages) — so a copy of a store, or any second
`.devpro-temp/` directory of that shape, has its sessions rendered twice in the index; the
doctor's `traces:` line prints the same glob as text (`hooks.py:257` interpolates `TRACE_GLOB`).
The fix: the two readers read the directories named exactly `.profiler-<harness>` for the harness
names the captures use (`claude` and `opencode`), and a directory of any other shape is not a store
and is not read; the doctor's `traces:` line prints the leaf's changed doctor sentence and reads no
store — its own read, `glob(f"*{OLD_STORE_SUFFIX}")` (`hooks.py:264`), is the old-store straggler
sweep and is untouched. The three pairs apply to the leaf verbatim.

Tests: the suite's tests pinning the readers' current glob behavior are named by the executor
from the tree and their update is in scope; the new pin drives both readers with a copy beside a
store among the cases and asserts one read. The pin names its defect: a store copy reads twice
(doubled rows), the served-page defect the owner triaged. The dashboard's unreadable-store fixture
writes `.profiler-broken` (`tests/dashboard/test_server.py:111`, and again at `:161`) — a name the
exact-name match will not accept — so both tests' reshaping is in scope: the unreadable case becomes
a real store name made unreadable, each test's subject — the unreadable store stated in the feed
rather than failing it — unchanged. `tests/dashboard/conftest.py`'s default (`.profiler-claude`)
is a real name and needs nothing.

Done-line: `just test`, `just lint`, `just dev-check-design-deltas-applied` reporting the three
pairs landed.

### P3 — the scratch guarantee's one home: install prepares, the clause drops

Applies: the [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md#installed-tree)
SPEC delta entry, the [Guide and readme](PROJECT_DOCS/SPEC/guide-and-readme.md#guide-and-readme)
SPEC delta entry, the [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md#renders-and-copies)
ARCHITECTURE delta entry, and the [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md#renders-and-copies)
and [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md#installed-tree) Code
delta entries.

Scope: `devpro/install.py`'s `_install_managed_paths` — the project's `.devpro-temp/` and
`.gitignore` join its managed paths, so the preflight's prediction observes the preparation —
`devpro/harness.py` (`scratch_rule`, lines 133–138), `devpro/harnesses/mage.py` (its hand-written
scratch rule, lines 41–44, taking the same create-it sentence), `devpro/clauses.py`
(`NEW_PROJECT_SETUP`), `PROJECT_DOCS/SPEC/guide-and-readme.md`, `README.md`, the touched leaves
(`PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md`,
`PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md`), and the tests pinning the touched
texts (`tests/test_devpro_install.py`, `tests/test_devpro.py`).

The facts the entries act on: the install writes no `.gitignore` and creates no scratch directory
today; `scratch_rule` tells the agent, where the scratch directory does not exist, to stop and say
so ("If it doesn't exist, stop and say so; don't improvise a location."), and mage's hand-written
rule carries the same sentence (`devpro/harnesses/mage.py:43`); `NEW_PROJECT_SETUP` carries the
birth-time creation mandate ("Also created at project birth: `.devpro-temp/`, with a
`.devpro-temp/` entry in the root `.gitignore`"). The changes: the install creates
`.devpro-temp/` when it is missing and adds the `.devpro-temp/` line to the project's
`.gitignore` — the file created holding that one line where the project has none, a `.gitignore`
already carrying the line left as it stands. The condition is the justfile's and Makefile's: a
project install of a nested plugin; a user-level install places nothing relative to a project and
creates nothing. `scratch_rule` tells the agent to create the
directory, the improvise-a-location prohibition unchanged, and mage's rule takes the same
create-it sentence; `NEW_PROJECT_SETUP`'s creation mandate
drops and its placement invariant stays — the scratch directory lives beside the harness
directory, never inside it, writes under the harness directory tripping the permission system's
own-settings protections. The SPEC pairs — the Installed tree pair and the new *The scratch
directory* passage — and the Guide-and-readme pair apply verbatim; the README's operator
instructions follow the pair: the harness lines stay the operator's, the `.devpro-temp/` line is
the install's (`README.md:87` today instructs the operator to add it by hand).

Tests: the install's preparation pinned by a test (missing directory created, line added, the
file created where none stands, a carrying `.gitignore` untouched), carrying the user-level case —
a user-level install creates nothing; the pin `tests/test_devpro.py:770`
(`test_the_scratch_rule_names_the_one_scratch_directory`, name-only, passes green) covers each
harness's rule, mage's included, and the render probes over `clauses.NEW_PROJECT_SETUP`
(`tests/test_devpro.py:1204`) update with the clause. The pin names its defect: untracked scratch
polluting a project's git status.

Done-line: `just test`, `just lint`, `just dev-check-design-deltas-applied` reporting the pairs
landed, and `just check-links`.

### P4 — the stand-ins' removal and the mock-as-oracle clause

Applies: the [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md#repo-layout) and
[Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md#subsystem-map) Code delta entries.

Scope: `tests/profiler_browser_runner.ts`, `tests/profiler_index_runner.ts`,
`tests/profiler_page_runner.ts`, `tests/profiler_capture_runner.ts` (deleted),
`tests/profiler_serialize_runner.ts` (its record source moves to a fixture the executor shapes
under `tests/`), the tests driving the deleted runners in `tests/test_devpro_profiler.py`
(removed), `devpro/clauses.py` (`TESTS_PROTECT_LOGIC`, line 169), and no other file.

The facts the entries act on: the three DOM stand-in runners (~130 lines each, the
`MutationObserver` machinery in two of them residue of the deleted deco sweep) and the capture's
stub-plugin fixture runner with its test (`test_the_opencode_capture_records_every_fired_call`,
`tests/test_devpro_profiler.py:687`) verify the reading of the observation, not the system. The
serialize runner is not deleted — the design's Repo Layout entry keeps the serialize tests — but
its record source moves: it spawns the capture runner for its record
(`tests/profiler_serialize_runner.ts:28`) and throws "the capture runner wrote no record" without
it, so its record becomes a fixture the executor shapes, and the test it serves
(`test_a_line_over_the_bound_is_fitted_at_its_root`) stays. The changes: the four runners and their
tests are removed outright — `tests/opencode_plugin_stub.ts` and `tests/opencode_entry_runner.ts`
stay (they drive execution to the entry's registration path and vouch for nothing the host
states), and the suite keeps the mask, serialize and capture-contract tests and the Python-side
server and store tests; `TESTS_PROTECT_LOGIC` gains
one sentence as its last, after the form-is-the-contract sentence: a mock drives execution to the
piece under test and is never the oracle for what it simulates — a test asserting against a
mock's own answers validates the reading of the observation, not the system, and is not written.

Consequence stated by the design: until the
[Browser-driven visual verification](ROADMAP.md#browser-driven-visual-verification) the roadmap
carries next lands, the pages' client-side rendering has no automated check — the byte-level
instruments check the rendered bytes and the server's answers, not what a browser executes.

Done-line: `just test`, `just lint`.

### R — Post-plan review

The reviewers the post-plan review seats name receive the project documents and the design — not
the plan — and review the changes and their tests against the project's standards and fitness for
purpose. Each reviewer writes their own review in the scratch directory; the session synthesizes
the reviewers' reviews into `ACTIVE_PLAN_REVIEW.md`, de-duplicating findings and reconciling them
into one account, without waiting for an approval between the last report and the write-up. The
review document is never diced. The review's row is `landed` in the commit that adds the review
document.

Done-line: `just check-links`.

### B — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` (landed at 2c48159); findings cited by their entry numbers.
Items whose subject carries an owner ruling still open state it in the item, and a `no` retires
the item as the item states; a ruling arriving changes the item before dispatch, never after.
Every item's intended lifetime is **shipped**. Each item whose done-line runs a document check
runs the dev-tree verb (`just dev-check-links`, `just dev-check-roadmap`); a package whose
done-line names `just test` also runs `just lint`.

**B1 — the model-pin remedy is redone on the evidence** *(review finding 1 — the owner's standing
order, "we are good where we are now after the fix. change nothing.", was premised on the claim
the declarations and the host source refute; this item needs the owner's ruling before it
dispatches. A `yes` is the ruling it runs under; a `no` retires the item and the plan records the
premise as held.)* The transform writes the pin as the plain object again, the resolve hook is removed
with its comment, the pin returns to store level — the stub as the driver of what the transform
writes — and `opencode-entry.md`'s Registration bullet and API-event count are true again; the
floor claim covers no experimental hook. The historical question gets one live 2.4.1 dispatch on
a cross-provider configured model, observed through the host's request surface, its outcome
recorded in the item's closing commit. Scope: `devpro/harnesses/resources/opencode/index.ts`,
`tests/opencode_entry_runner.ts`, `tests/test_opencode_entry.py`,
`PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md`.
Done-line: `just test`, `just lint`.

**B2 — the capture's record contract gets its driver back** *(review findings 2 and 3 — the
owner's P4 ruling removed the test believing it oracle-class; the review states it is
driver-class. This item also needs the owner's ruling before it dispatches. A `yes` is the ruling
it runs under; a `no` retires the item and finding 2 stays a stated gap in
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.)* A contract runner
drives the shipped `profiler.ts`'s event-record construction over the three host-shape inputs and
asserts the capture's own outputs, the boundary stated in its docstring — the shapes are inputs,
no claim in the test about what the host actually reports; the live-dispatch evidence is recorded
as a roadmap ticket again. The serialize fixture's key set is pinned to the capture's own record
construction, or the fixture's provenance is recorded and the docstring scoped. Scope:
`tests/profiler_contract_runner.ts` (new), `tests/test_devpro_profiler.py`,
`tests/fixtures/profiler_serialize_record.json`, `tests/profiler_serialize_runner.ts`, ROADMAP.md.
Done-line: `just test`, `just lint`.

**B3 — the scratch sentence is single-sourced** *(review finding 4)* One constant beside
`clauses.PROJECT_TEMP_DIR` carries the scratch paragraph; `harness.py`'s `scratch_rule` and
mage's hand-written copy (`mage.py:41–45`) take the constant; the dead `harness_dir` parameter
and `harness.py`'s "beside" docstring go — `NEW_PROJECT_SETUP`'s placement invariant stays.
Scope: `devpro/clauses.py`, `devpro/harness.py`, `devpro/harnesses/mage.py`,
`tests/test_devpro.py` (the render probes read the constant).
Done-line: `just test`, `just lint`.

**B4 — the scratch guarantee's scope is stated where it is delivered** *(review finding 5, and
finding 6's dry-run note — B4 carries the dry-run work, B5 does not)* SPEC's `installed-tree.md`
and ARCHITECTURE's scratch passage state the condition the delivery carries — claude/opencode
nested-plugin project installs, mage and user-level installs none. `devpro/install.py`'s
`_install_managed_paths` names the project's `.devpro-temp/` beside the `.gitignore` in its
managed set, so the `--dry-run` prediction prints both — `created:` lists `.gitignore` and no
directory today — and `tests/test_devpro_install.py`'s `_assert_dry_run_predicts` case for a
fresh claude project asserts the directory. Scope: `PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md`,
`PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md`, `devpro/install.py`,
`tests/test_devpro_install.py`.
Done-line: `just test`, `just lint`, `just dev-check-links`.

**B5 — the README's changed sections are finished** *(review finding 6, excluding its dry-run
note — B4 carries it)* The `.gitignore` example block carries the `.devpro-temp/` line and marks
it as the install's, so a reader copying the block sees the finished state and a hand-written
`.devpro-temp` (no slash) cannot duplicate; the profiler section states the exact-name rule and
the idle records; the Acknowledgments anchor drift is left standing (predates). Scope:
`README.md`.
Done-line: `just dev-check-links`.

**B6 — the stale glob stragglers go** *(review finding 7)* `harness-profiler.md`'s Serving
passage and its doubled store set, `pages.py`'s two docstrings and the INDEX template's comment:
the sentences name the exact-name read; the literal list drops; the negative pin and the two
dangling docstring cross-references go with them (review finding 9's related residue). Scope:
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`, `devpro/profiler/pages.py`,
`tests/test_devpro_profiler.py`.
Done-line: `just test`, `just dev-check-links`.

**B7 — the mechanical debt from the packages, decided** *(review findings 9 and 8, each
alternative picked rather than left to the executor)* One ending-aware helper replaces the CRLF
re-implementation; `rstrip()` is narrowed to the line's own ending; the one-function accessor is
inlined; the dashboard's traces-feed case gains a readable claude session beside the locked
store; the entry runner's always-empty `requests` key is dropped; `subsystem-map.md` names
`runner_file.py`'s three duties — the move to `install.py` is the roadmap's. The retired-directory
pin in `test_devpro_install.py` naming three harnesses is verified against the owner's account:
mage's per-harness temp separation predates the `.devpro-temp` unification, which forgot mage —
the third retired name's fate (leftover the install should clean, or stale pin) is decided there
with the unification's history as the record. Scope:
`devpro/runner_file.py`, `tests/conftest.py`, `tests/test_devpro_profiler.py`,
`tests/dashboard/test_server.py`, `tests/opencode_entry_runner.ts`,
`PROJECT_DOCS/ARCHITECTURE/subsystem-map.md`.
Done-line: `just test`, `just lint`.

**B8 — the double-delivery instance is folded into its ticket** *(review finding 10)* The
restated scratch sentence reaches nine coder definitions through `NEW_PROJECT_SETUP` and the
agents file's `scratch_rule` (`grep -rn "throwaway builds" devpro/definitions/agents/` returns
nothing: the sentences are delivered, not written). The roadmap's sentence-duplication ticket
gains the instance as one line naming those two sources and the nine seats; no code change in
this plan. Scope: `ROADMAP.md`.
Done-line: `just dev-check-roadmap`.

Two owner decisions ride with the findings, not as items, and neither is dispatchable until
ruled: finding 11's candidate `TESTS_PROTECT_LOGIC` sentence, and the mock sentence's provenance
beside `TEST_REVIEW`'s bullet. The candidate sentence is the doctrine B1 and B2 enact one test at
a time: ruled yes, it lands in `devpro/clauses.py` and changes B1's and B2's report line; ruled
no, B1 and B2 stand as written. Finding 11's third bullet — the design's claim that the opencode
stub "vouches for nothing" — is corrected by B2's docstring boundary for the capture and by the
`opencode_plugin_stub.ts` sentence in P4; no separate edit. A ruling lands each where the owner
says.
