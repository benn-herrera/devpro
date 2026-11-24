# The profiler reads true: stores, model config, scratch, and no mocking oracles

The design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), accepted. Each package below applies its named
entries verbatim over their targets — the pairs' from-blocks match the leaves as they stand, and
`just dev-check-design-deltas-applied` confirms each pair landed. The entries' code changes are
stated in the design; the packages name the files, the facts and the pins.

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
| P1 | drafted | expert | the plugin's configured model applies at runtime |
| P2 | drafted | expert | the stores read true: exact names, both readers, the doctor's line |
| P3 | drafted | expert | the scratch guarantee's one home: install prepares, the clause drops |
| P4 | drafted | expert | the stand-ins' removal and the mock-as-oracle clause |
| R | drafted | expert | Post-plan review |
| B | drafted | expert | Post-plan burndown |

### P1 — the plugin's configured model applies at runtime

Applies: the [Opencode entry](PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md) Code delta
entry.

Scope: `devpro/harnesses/resources/opencode/index.ts`, the test that pins the fix.

The fact the entry acts on: the *Registration* passage states each agent record updates the agent
of that id with the model where the record has them, while at runtime on opencode 2.4.1 the host
reads an agent's model from its own store — the registry's model applied through the cast at
`index.ts:190` (`if (entry.model) agent.model = entry.model as NonNullable<typeof agent.model>`)
never reaches it. The fix applies the configured model at `Plugin.define`'s `setup`, where the
2.4.1 runtime reads it. The entry leaves the mechanism's exact wiring to the executor where the
host's reading site admits more than one — the outcome is the leaf's statement true at runtime,
pinned by a test that drives `Plugin.define`'s setup with a configured model and observes it
applied. `tests/opencode_plugin_stub.ts` and `tests/opencode_entry_runner.ts` are the drivers for
that pin and stay.

Type-check note: `just lint` type-checks what ships against the host's published declarations —
a fix the declarations' shapes cannot state reads where the runtime reads, cast at the boundary
with the why-comment the resources carry.

Done-line: `just test`, `just lint`.

### P2 — the stores read true: exact names, both readers, the doctor's line

Applies: the [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md) ARCHITECTURE
delta entry (three pairs) and the [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)
Code delta entry.

Scope: `devpro/profiler/values.py`, `devpro/profiler/pages.py`, `devpro/profiler/hooks.py`,
`tests/test_devpro_profiler.py`, the leaf.

The facts the entry acts on: `TRACE_GLOB = ".profiler-*"` (`values.py:18`); both readers glob it —
`pages.list_sessions` (`pages.py:679`, the tree's render) and `pages.store_directories`
(`pages.py:758`, the index and the session pages) — so a copy of a store, or any second
`.devpro-temp/` directory of that shape, has its sessions rendered twice in the index; the
doctor's `traces:` line (`hooks.py:257`) prints the same glob. The fix: the three sites read the
directories named exactly `.profiler-<harness>` for the harness names the captures use (`claude`
and `opencode`), and a directory of any other shape is not a store and is not read. The three
pairs apply to the leaf verbatim.

Tests: the suite's tests pinning the readers' current glob behavior are named by the executor
from the tree and their update is in scope; the new pin drives both readers with a copy beside a
store among the cases and asserts one read. The pin names its defect: a store copy reads twice
(doubled rows), the served-page defect the owner triaged.

Done-line: `just test`, `just lint`, `just dev-check-design-deltas-applied` reporting the three
pairs landed.

### P3 — the scratch guarantee's one home: install prepares, the clause drops

Applies: the [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md) SPEC delta
entry, the [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md)
ARCHITECTURE delta entry, and the [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md)
and [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md) Code delta entries.

Scope: `devpro/install.py` (the preparation beside the copy machinery), `devpro/harness.py`
(`scratch_rule`, lines 133–138), `devpro/clauses.py` (`NEW_PROJECT_SETUP`), the two leaves, and
the tests pinning the touched texts (`tests/test_devpro_install.py`, `tests/test_devpro.py`).

The facts the entries act on: the install writes no `.gitignore` and creates no scratch directory
today; `scratch_rule` tells the agent, where the scratch directory does not exist, to stop and say
so ("If it doesn't exist, stop and say so; don't improvise a location."); `NEW_PROJECT_SETUP`
carries the birth-time creation mandate ("Also created at project birth: `.devpro-temp/`, with a
`.devpro-temp/` entry in the root `.gitignore`"). The changes: the install creates
`.devpro-temp/` when it is missing and adds the `.devpro-temp/` line to the project's
`.gitignore` — the file created holding that one line where the project has none, a `.gitignore`
already carrying the line left as it stands; `scratch_rule` tells the agent to create the
directory, the improvise-a-location prohibition unchanged; `NEW_PROJECT_SETUP`'s creation mandate
drops and its placement invariant stays — the scratch directory lives beside the harness
directory, never inside it, writes under the harness directory tripping the permission system's
own-settings protections. The SPEC pair and the new *The scratch directory* passage apply
verbatim.

Tests: the install's preparation pinned by a test (missing directory created, line added, the
file created where none stands, a carrying `.gitignore` untouched); the agents-file tests pinning
`scratch_rule`'s sentence update with the rule. The pin names its defect: untracked scratch
polluting a project's git status.

Done-line: `just test`, `just lint`, `just dev-check-design-deltas-applied` reporting the pairs
landed, and `just check-links`.

### P4 — the stand-ins' removal and the mock-as-oracle clause

Applies: the [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md) and
[Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md) Code delta entries.

Scope: `tests/profiler_browser_runner.ts`, `tests/profiler_index_runner.ts`,
`tests/profiler_page_runner.ts`, `tests/profiler_capture_runner.ts` (deleted), the tests driving
them in `tests/test_devpro_profiler.py` (removed), `devpro/clauses.py` (`TESTS_PROTECT_LOGIC`,
line 169), and no other file.

The facts the entries act on: the three DOM stand-in runners (~130 lines each, the
`MutationObserver` machinery in two of them residue of the deleted deco sweep) and the capture's
stub-plugin fixture runner with its test (`test_the_opencode_capture_records_every_fired_call`,
`tests/test_devpro_profiler.py:687`) verify the reading of the observation, not the system. The
changes: the four runners and their tests are removed outright — `tests/opencode_plugin_stub.ts`
and `tests/opencode_entry_runner.ts` stay (they drive execution to the entry's registration path
and vouch for nothing the host states), and the suite keeps the mask, serialize and
capture-contract tests and the Python-side server and store tests; `TESTS_PROTECT_LOGIC` gains
one sentence as its last, after the form-is-the-contract sentence: a mock drives execution to the
piece under test and is never the oracle for what it simulates — a test asserting against a
mock's own answers validates the reading of the observation, not the system, and is not written.

Consequence stated by the design: until the browser-vision visual verification the roadmap
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

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
