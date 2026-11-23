# ACTIVE PLAN — the profiler's pages read true and the packages lose their pattern breaks

Design: [Profiler page fidelity and the absorbed packages' shape](ACTIVE_DESIGN.md) — accepted.
Its entries are cited below by anchor. Every package's intended lifetime is **shipped**.

Packages run serially in the shared tree, in the order P1, P2, P3, P4.

## Status

| Package | State | Rating |
| --- | --- | --- |
| P1 | landed: commit fdef450; gate red only on the foreign runner-snippets pins, P1's surface 37/37 | mechanical |
| P2 | landed: commit 3d4f058; done-lines green but for the two foreign runner-snippet pins | mechanical |
| P3 | landed: commit 0bcae3a; third pair reads landed in deltas-applied | mechanical |
| P4 | landed: commit 25bc0c4; all three done-lines green but for the two foreign runner-snippet pins | expert |
| P5 | landed: the five seats' synthesis | expert |
| P6 | in progress: drafting the burndown from ACTIVE_PLAN_REVIEW.md | expert |

### P1 — one check body and one report builder in doccheck

Rating: mechanical. Implements [the Code delta's doccheck entry](ACTIVE_DESIGN.md#repo-layout-2).

Scope, by symbol: `devpro/doccheck/plancheck.py`'s `check_plan`, `check_design`, `check_roadmap`
(`:295`, `:313`, `:338`), their shared driver `_check` (`:107-156`), and the report builders
`_plan_report` (`:159`) and `_roadmap_report` (`:168`).

Facts, each with its answer: the three verb functions' bodies are identical but for the reader and
report they use — `sed -n '295,340p' devpro/doccheck/plancheck.py` shows the three; the two report
builders differ only in `read_plan`/`read_roadmap` and an f-string — `sed -n '159,176p'
devpro/doccheck/plancheck.py`. `_design_report` keeps its `deltas_applied` branch untouched.

The work: the three verbs become calls to `_check`, each with its document type's reader; the two
report builders become one taking both. `check-roadmap` stays two constants —
`doccheck/cli.py`'s `CHECK_ROADMAP` (the argparse surface) and
`devpro/definitions/skills/development.py:35`'s `CHECK_ROADMAP_COMMAND` (the skills' prose) — and
neither imports the other.

Done when: `just test devpro` passes.

### P2 — dicing at one level

Rating: mechanical. Implements [the Repo Layout ARCHITECTURE entry](ACTIVE_DESIGN.md#repo-layout)
and [the Code delta's flattening entry](ACTIVE_DESIGN.md#repo-layout-1).

Scope, by path: the 12 modules of `devpro/dicing/dicerlib/` plus its `__init__.py` move up to
`devpro/dicing/` — `dicerlib/__init__.py`'s docstring is deleted with the package, and
`devpro/dicing/__init__.py`'s own docstring survives it — `dicerlib/` is deleted, and the imports
naming it are rewritten.

Reference search and its answer — `git grep -l dicerlib` (17 files):
`devpro/dicing/cli.py` (6 sites), `devpro/doccheck/plancheck.py` (1), `devpro/doccheck/planform.py`
(7), `devpro/kanban/board.py` (7), `devpro/kanban/server.py` (1), and 11 test files —
`tests/dicing/test_anchors.py`, `test_board.py`, `test_linkrewrite.py`, `test_linkscan.py`,
`test_manifest.py`, `test_outline.py`, `test_reassemble.py` (1), `test_split.py` (2),
`test_textfile.py` (2), `test_treecheck.py` (1), `test_undice.py` (2) — and
`PROJECT_DOCS/ARCHITECTURE/repo-layout.md:45-46`, the ARCHITECTURE entry's pair, applied to its
target verbatim by this package.

Done when: `just test devpro` passes, `just check-links` passes over the doc change, and
`git grep -l dicerlib -- devpro tests` returns nothing — the design's "nothing of the old name
remains"; the name survives only in this plan and the design until they retire. The package
verifies its pair's application in `just dev-check-design-deltas-applied`'s output: its repo-layout
pair reads `landed` there.

### P3 — the opencode capture reads where the host reports

Rating: mechanical. Implements [the Harness profiler ARCHITECTURE entry](ACTIVE_DESIGN.md#harness-profiler)
(third pair) and [the Code delta's capture entry](ACTIVE_DESIGN.md#harness-profiler-1).

Scope, by symbol: `devpro/harnesses/resources/opencode/profiler.ts`'s `childSessionOf`
(`:247-251`), the capture runner's two dispatch fixtures `tests/profiler_capture_runner.ts:61-75` —
`ses_child` at `:61-65` and `ses_fork` at `:71-75`, both pinning the result shape — and the
application of the ARCHITECTURE entry's third pair to
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`, verbatim.

Facts, each with its answer: opencode 2.3.2 reports the dispatched child's session id at
`result.output.sessionID` — `grep -h '"tool":"Agent"' .devpro-temp/.profiler-opencode/*.jsonl`
showed 169 of 169 live dispatch records with the id only there (the forensic scripts
`.devpro-temp/forensic-edges.py` and `.devpro-temp/repair-edges.py` in this checkout's scratch, the
pre-repair store at `.devpro-temp/.profiler-opencode-pre-repair-1795424915`); the fixture today
reports `result: { output: "ses_child", metadata: { sessionID: "ses_child" } }`, a shape no host
showed. The extant stores in this checkout are already repaired; no other project's store is.

The work: `childSessionOf` reads `result.output.sessionID`, the string guard standing, and records
no child where the result reports none. Both fixtures move the id into `output`, so the run whose
read they drive fails on the old reading.

Tests and fixtures pinning the changed behavior, updated in scope:
`test_the_opencode_capture_records_every_fired_call` — its `:603-606` assertions — and both
runner fixtures.

Done when: `just test devpro` passes, `just check-links` passes over the applied pair, and
`just dev-check-design-deltas-applied`'s output reads the harness-profiler third pair `landed`
there — the run exits 1 until P4 lands the remaining pairs.

### P4 — the profiler's pages read true

Rating: expert. Implements [the Harness profiler ARCHITECTURE entry](ACTIVE_DESIGN.md#harness-profiler)
(first and second pairs), and carries one executing-agent's call the design named without an
entry: the span-scale presence guard.

Scope, by symbol: `devpro/profiler/pages.py`'s index template script and `moments` cell —
`utcStamp`, `isoStamp` (`:979-984`), the no-records line (`:1032`), the failed-fetch block
(`:1059-1063`) — `devpro/profiler/view.html:99-101`, the session page's header stamp: client-side
today as a bare `toISOString` string, under the new rule a `<time>` element with the machine form
in its `datetime` reading local; `pages.py`'s `stamp()` (`:698`), whose text-tree stamp keeps its
raw-UTC reading under the design's no-script branch; `devpro/profiler/deco.js`'s `momentClock` and
`dayOf` (`:89-93`), `localMoments` (`:96-100`) and the sweep (`:105-115`); the application of the
ARCHITECTURE entry's first and second pairs to
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`, verbatim;
`tests/test_devpro_profiler.py`.

The work, by the design's statements: every moment the pages and their headers show reads in the
reader's local time, 24-hour, one notation — the machine form only in `datetime` attributes, raw
UTC in titles; same-day first-to-last reads as two times with no date, midnight-crossing reads
with the date on its first end alone. The index carries the controls — child rows on/off, claude
and opencode on/off, sortable column heads on dispatched-agent count, record count, time, span —
and a failed feed names itself with a notice distinct from the no-records state. The guard: `assert
len(drawn["rows"]) == len(crafted)` above the zip loop at `:1006` of
`test_the_index_renders_the_rows_the_feed_answers`.

Tests and fixtures pinning the changed behavior, updated in scope:
`test_the_decoration_script_reads_every_moments_cell_the_index_draws` — its cross-day expectation
`2025-12-31 22:00 to 2026-01-01 10:30` becomes first-end-date-only, its same-day
`16:00 to 16:00` stands, and its titles assertion (`:569-573`, the raw UTC kept in titles) stands
untouched — and `test_the_index_renders_the_rows_the_feed_answers`, which extends to drive the
controls and the failure notice over the served page and feed.

Done when: `just test devpro` passes, `just check-links` passes over the applied pairs, and
`just dev-check-design-deltas-applied` passes — P4 is the last work package, so all three pairs of
the ARCHITECTURE entry are landed and the run exits 0.

### P5 — Post-plan review

Rating: expert. The reviewers, given the project documents and the accepted design, not this plan:
`devpro-python-coder`, `devpro-typescript-coder` and `devpro-web-app-expert` (the changed
languages and the browser surfaces, conformance and consistency seats), `devpro-architect`
(structure), `devpro-prompt-engineer` (the contract documents' changes). Each writes their own review in `.devpro-temp/`, independently; the session
synthesizes `ACTIVE_PLAN_REVIEW.md` from them, de-duplicated. This package's row is `landed` in
the commit that adds the review document.

Done when: `ACTIVE_PLAN_REVIEW.md` exists with every seat's findings reconciled.

### P6 — Post-plan burndown

Rating: expert throughout; B5 relabelled expert by its usability review. The work list is drafted
from `ACTIVE_PLAN_REVIEW.md` (landed at `56899a2`); findings are cited by that document's IDs.
Packages run serially, shared tree, B1 → B2 → B3 → B4 → B5; B4 consumes B2's hand-built clock;
B5's `:799` edit follows B1's landed widening of the same docstring.

Deferred to the user, not packaged: the leaf-wording amendments (R16, and R17's leaf halves —
"an Agent row", the unreadable statement, `repo-layout.md`'s grain, and B1's R12 leaf branch).
They amend the accepted design's landed pairs, and the machine check `dev-check-design-deltas-applied`
holds those pairs; amending accepted text is the user's decision. B1 and B4 take the code side
only and their done-lines assert the pairs stand untouched.

| Package | State | Rating |
| --- | --- | --- |
| B1 | landed: commit dc8b6b1; test_server.py widening accepted as the schema change's consequence | expert |
| B2 | landed: the deco keeps what the leaf promises; deco.js, the deco runner and its tests | expert |
| B3 | dispatchable | expert |
| B4 | dispatchable | expert |
| B5 | dispatchable | expert |

#### B1 — the index reads true

Rating: expert. Findings: R1, R3, R6, R11, R12 (code side), R14, R19, R20, R17's union comment.

Scope, by symbol: `devpro/profiler/pages.py`'s index script — the sort (`:1086-1090`), `hides()`
(`:1067-1069`), `tops` (`:1086`), the no-records row (`:1092-1098`), the notice (`:1128-1132`),
the sort-cycle machine (`:1107-1120`), the harness-union comment (`:898-901`); the controls'
markup (`:940-941`); the feed entry `_feed_entry` (`:816-828`) and the schema comment at `:799`;
`tests/test_devpro_profiler.py` and `tests/profiler_index_runner.ts`.

The work: the feed entry carries the dispatched-agent count, the schema comment at `:799` and the
runner's `keys` assertion widen with it, and the `data-agents` second copy is deleted (R1); the
driven test gets a feed where two dispatchers hold different children counts, a descending press,
and the keys assertion after the press (R1). A missing harness box means visible, and `draw()`'s
body is wrapped so a page defect stops reporting as a feed failure (R3). A session is hidden only
on its own harness or (child-rows off and it has a dispatcher), orphans promoted (R6). The notice
test drives the page's composed message with real failure shapes — the runner's `{fail}` carries
the status and body — and asserts hidden-before (R11). The no-records row makes the three
distinctions in code — zero-record store, no store, controls-hidden (R12's code side). The sort
cycle's comment states the three-press machine the code implements; the arrow's absence on
`aria-sort="none"` is correct and stands (R14). The span table asserts the row's last `<td>`
structurally (R19). The control state is honest for a harness pair that hides nothing (R20). The
harness-union comment counts its three spellings (R17's `pages.py` half).

Done when: `just test devpro` passes, `just dev-check-design-deltas-applied` passes — the pairs
stand untouched — and the two pre-existing foreign pins (`devpro-dashboard` in
`devpro/runner-snippets/devpro.just` and `devpro.mk`) are the only other failures; any other
failure is this package's.

#### B2 — the deco keeps what the leaf promises

Rating: expert. Findings: R2, R8, R10, R22.

Scope, by symbol: `devpro/profiler/deco.js`'s `readMoments` (`:115-121`), `momentClock`/`dayOf`
(`:90-93`), the selectors (`:122`); `tests/profiler_deco_runner.ts` (`:35`, `:174`, `:222-229`).

The work: the local reading is written into each `<time>`'s own text, the elements kept (R2); the
clock is built by hand — `padStart`, as `dayOf` writes it — not inherited from the reader's
locale, and the deco tests pin the locale alongside `TZ` (R8); the deco runner reads its selectors
from `deco.js`'s own `MOMENTS` constant, the readings initialize to something a sweep-over-nothing
is distinguishable from, and the deco runner's dead `.sort`/`.controls input` branches go with it
(R10, R22 — the runner's branches; the index page's own `.controls input` query stays).

Done when: `just test devpro` passes, `just dev-check-design-deltas-applied` passes — the pairs
stand untouched — and the two pre-existing foreign pins are the only other failures.

#### B3 — the capture honors its floor

Rating: expert. Findings: R4 (first branch), R5, R9, R15, R21.

Scope, by symbol: `devpro/harnesses/resources/opencode/profiler.ts`'s `childSessionOf`
(`:250-254`), `childAgentTypeOf` (`:256-265`), line 3's floor statement;
`tests/profiler_capture_runner.ts`, `tests/profiler_serialize_runner.ts`.

The work: B3 takes R4's first branch — `childSessionOf` reads `output.sessionID` first and falls
back to `metadata.sessionID`, keeping the 2.3.0 floor true; the floor statement and the comments
say the fallback covers 2.3.0's metadata shape, and no leaf edit is needed — R21 resolves there
(R4, R21). One observed result per fixture, the record's `result` and the agent type read from
where the host puts them (R5). The opencode resources type-check against the host's published
declarations — vendored or installed — through a new `just` recipe joined to the devpro surface;
the recipe carries no runner-snippet copy, so no third pin arises (R9). The record's fields have
one home in the tests: the serialize runner imports the record the capture runner wrote — one run,
both inputs — as `_RECORD_FIELDS` already does on the Python side (R15).

Done when: `just test devpro` passes, `just dev-check-design-deltas-applied` passes — the pairs
stand untouched — and the two pre-existing foreign pins are the only other failures.

#### B4 — the pages' lone stamps

Rating: expert. Findings: R7, R8's lone-stamp side.

Scope, by symbol: `devpro/profiler/view.html`'s header stamp and `deco.js`'s `localMoment`
(`:106-109`).

The work: a lone moment reads with its date, using B2's hand-built clock — a `toLocaleTimeString`
must not leak back into `localMoment` (R7). B4 edits no leaf: the wording amendments R16 and
R17's leaf halves need are deferred to the user above.

Done when: `just test devpro` passes, `just dev-check-design-deltas-applied` passes — the pairs
stand untouched — and the two pre-existing foreign pins are the only other failures.

#### B5 — the python surface's stale text and one discriminator

Rating: expert (relabeled by the usability review: R13 is a signature change).

Scope, by symbol: `devpro/doccheck/plancheck.py`'s `_report` (`:163-179`) and the `from __future__`
import (`:6`); `devpro/profiler/pages.py`'s comments (`:799`, `:892`) — the `:799` edit follows
B1's landed widening of that docstring.

The work: `_report` takes the summary formatter beside the reader — or names its two concrete
returns in the docstring — and the annotations import goes with the union if it leaves; the
`index.js` name leaves both comments.

Done when: `just test devpro` passes, `just dev-check-design-deltas-applied` passes — the pairs
stand untouched — and the two pre-existing foreign pins are the only other failures.

Tracked, not packaged: the `UNREADABLE` twin (`plancheck.py:70`, `kanban/server.py:55`) is
pre-existing; the three proposed CONVENTIONS leaves (R23, R24, R25 — the JS stand-in's fidelity,
the shipped resource's host check, the locale pin) go to the next design when one opens; the
installed plugin payload's `dicerlib` imports are cleared by a reinstall, not a commit; the
leaf-wording amendments R16 and R17's leaf halves wait for the user. On the user's direction: once
the plan lands and before the installation is updated, the forensic child-tie repair runs one last
time over the profiler records the still-old installed plugin wrote since the last repair — the
capture fix makes every edge after that written correctly.
