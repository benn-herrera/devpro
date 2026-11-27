# ACTIVE PLAN

# The Python type gate and the profiler's operational context

Written from [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), its seven entries cited per package below. Every
package's work is shipped-lifetime code; the whole process applies. Each package closes in exactly
one commit; the closing commit carries a body and the attribution line (*Commits and pull
requests*, the development skill). The checkpoint gate is `just test`, then `just lint`, then
`just sweep-python` (CONVENTIONS, The gates). Run order is serial, P1 → P2 → P3 → P4 — the packages
share the tree, and the lint gate P1 builds is what P2–P4's done-lines run.

The design's delta application is verified by `just dev-check-design-deltas-applied` (justfile:393).
The check has no subset mode: it exits 1 whenever any pair has not landed (plancheck.py:296), and
its stdout prints one state line per pair — `pending` or `landed` — at the pair's `As it stands`
label's line in ACTIVE_DESIGN.md (plancheck.py:295; a run today names all seven `pending`). The
design states seven pairs and one whole-leaf entry: :22 — SPEC [Shipped files]
(ACTIVE_DESIGN.md#shipped-files), P4 lands it; :55 — [Recipes](ACTIVE_DESIGN.md#recipes), P1; :118 —
[Harness profiler](ACTIVE_DESIGN.md#harness-profiler), P2; :135 and :158 — [Serving, The index]
(ACTIVE_DESIGN.md#serving-the-index), P3; :191 — [Serving, Dispatched children]
(ACTIVE_DESIGN.md#serving-dispatched-children), P4; :226 — [Serving, The models in the page]
(ACTIVE_DESIGN.md#serving-the-models-in-the-page), P3; and [The operational-context stamp]
(ACTIVE_DESIGN.md#the-operational-context-stamp), a whole leaf with no pair, written by P2. So
P1–P3's runs exit 1 on the pairs later packages land — that is the passing shape for those packages
— and each done-line below states the literal stdout its run must give. The whole design's delta
application is complete when P4's run exits 0.

P1 through P4 are `dispatchable`: the plan's packages have had their `devpro-prompt-engineer`
usability review and `devpro-architect` revision (*Dispatchability*). PR and PB stay `drafted`
until their subjects exist.

The user's standing direction: when this plan lands, the periodic review starts immediately — the
interval's count is met and this plan's landing is the coherent feature boundary, so the next plan
is the full review, straight to a plan with no design before it. The review rolls through the
findings collected and its plan drafted, and holds there: the user discusses the findings and the
draft plan before anything is approved or dispatched.

## Status

| Package | State | Rating |
| --- | --- | --- |
| P1 | landed | expert |
| P2 | landed | expert |
| P3 | landed | expert |
| P4 | landed | expert |
| PR | landed | expert |
| PB | in progress | expert |
| B1 | drafted | expert |
| B2 | drafted | expert |
| B3 | drafted | expert |
| B4 | drafted | expert |
| B5 | drafted | expert |
| B6 | drafted | mechanical |

## P1 — the Python type gate

Applies the design's [Recipes](ACTIVE_DESIGN.md#recipes) entry to its target
`PROJECT_DOCS/ARCHITECTURE/recipes.md`, verbatim except its relative links. Also carries the
plan's own CONVENTIONS amendment, below — a change to house rules is not one of a design's deltas.

Intended lifetime: shipped. Rating: expert — the strict-mode fixes over `devpro/` and `devtools/`
require judgment (typing decisions, where annotations are honest) and possible debugging, not
enumerated edits.

Scope, named in files and symbols:

- `pyproject.toml` — a `mypy` line in the `[dependency-groups]` `dev` group, with the
  compatible-release specifier the group's lines take (pyproject.toml:24-31: `pytest~=9.2`,
  `isort~=9.0`, `black~=26.10`, `flake8~=7.5`, `setuptools~=84.2`, `build~=1.6`), and the
  `[tool.mypy]` strict configuration.
- `justfile` — the `lint` recipe (justfile:224-227, its comment above it) gains the mypy pass, run
  through the venv's own interpreter (`{{VENV_PYTHON}} -m mypy ...`) as the recipe's other Python
  checks are; `FLAKE8_IGNORE` (justfile:212) and the recipe's other lines are untouched.
- `devtools/scripts/format-python.sh` gains no mypy line: it is the rewriting form — black and
  isort rewrite (:18-19), flake8 checks (:20) — and formatting cannot fix a type error; mypy has
  nothing to rewrite, so its pass lives only in `just lint`.
- The strict-mode fixes the gate demands over `devpro/` and `devtools/`. The set is whatever
  strict mypy reports over those paths at this package's start. If it proves too large for one
  commit, split it into packages that each need one commit and amend this plan before dispatching
  the splits.
- The design entry applied to `PROJECT_DOCS/ARCHITECTURE/recipes.md` (the [Recipes]
  (ACTIVE_DESIGN.md#recipes) pair).
- The CONVENTIONS amendment (the plan's own change):
  `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-lint-recipe-is-read-only.md` gains the
  checker in its enumeration — appended into the sentence whose enumeration clause ends "a file
  checked though it does not ship;" and whose next clause reads "`format-python` is the rewriting
  form, run to fix what `lint` reports." (leaf:8) — in the leaf's own voice: mypy in its
  strict mode over `devpro/` and `devtools/`, configured in `pyproject.toml`, whose paths are the
  gate's paths — `tests/` stays outside them — and a checker release changes what the gate reports
  only with a change to the group line, the pin being the record as the other tools' are.

Facts this package acts on (re-run any of them):

- `just lint` today (justfile:224-227) runs black, isort and flake8 over `tests devpro devtools`,
  plus `_lint-shell` (justfile:230) and `_lint-typescript` (justfile:240). `FLAKE8_IGNORE` stands
  at justfile:212.
- No Python type checker exists anywhere: `git grep -in 'mypy\|pyright' -- justfile
  pyproject.toml devtools PROJECT_DOCS` answers nothing (exit 1), so `[tool.mypy]` is new, not a
  change to an existing configuration.
- Pinning convention: `_venv` (justfile:41-93) installs the `dev` group and records its literal
  text in `.venv/tools.txt`; ARCHITECTURE packaging.md:42-45 states "move is a deliberate edit to
  `pyproject.toml`, visible in the diff. The group's text is the record" — a group edit re-triggers
  the install on the next `_venv`.
- **Design decision, not an oversight: `tests/` stays outside the gate's paths.** The design entry
  states it ("`tests/` stays outside them until a test tree's signal proves worth the quieting its
  fixture indirection asks"). This package does not add `tests/` to the mypy paths, and no later
  package in this plan does.

Done-line, run once at the package's end:

- `just lint` passes, mypy strict over `devpro/` and `devtools/` included.
- `just test` passes.
- `just dev-check-design-deltas-applied` exits 1 — the passing shape while later packages' pairs are
  unapplied — and prints no `drifted` and no `conflicting` state line. Its stdout gives seven state
  lines, in the run's document order (:22, :55, :118, :135, :158, :191, :226), naming `landed` on
  exactly :55 — this package's [Recipes] pair, per the map above — and `pending` on the other six;
  its summary line reads `pairs: 7, landed: 1, pending: 6, drifted: 0, conflicting: 0, problems: 0`.

## P2 — the stamp at capture

Applies the design's [The operational-context stamp](ACTIVE_DESIGN.md#the-operational-context-stamp)
entry — a whole-leaf entry: its application writes the leaf
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-operational-context-stamp.md` carrying the entry's
text, which has no pair for the delta check to confirm — and the
[Harness profiler](ACTIVE_DESIGN.md#harness-profiler) Contents pair to its target
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/index.md`.

Intended lifetime: shipped. Rating: expert — the stamp's once-per-session read-or-compute, the
digest and its manifest, and the opencode capture's long-lived process side each take design-in-code
decisions the entry leaves to the executor.

Scope, named in files and symbols:

- `devpro/profiler/values.py:14` — `SCHEMA_VERSION = 3` → 4.
- `devpro/profiler/capture.py` — the record construction (`build_record`, capture.py:309; the
  `"v": SCHEMA_VERSION` writes at capture.py:323 and :368) gains the stamp, taken per the design
  entry: read off the store's earliest-`at` record where the store holds one, computed fresh where
  not.
- `devpro/harnesses/resources/opencode/profiler.ts` — its own constant (profiler.ts:61) and the
  `"v": SCHEMA_VERSION` writes at both record construction sites — `callRecord` (profiler.ts:301,
  its write at :309) and `eventRecord` (:356, its write at :358) — move to 4, the stamp fields
  landing on both sites. The long-lived capture writes every record field, absent as `null`, so its
  unstamped fields are `null` where the Python capture's are left out — the invariant's source is
  the `eventRecord` comment (profiler.ts:352-355: "The record carries the signal's fields on every
  record, absent ones as `null`"), not capture.py:310, whose docstring ("absent values are left
  out") is the Python side's; the design entry states the split.
- The `.devpro-temp/.profiler-directives/` manifest the entry states. The directory's `.profiler-`
  prefix collides with no reader: the readers select stores by the `TRACE_STORES` allowlist —
  pages.py:813 iterates `for store in sorted(stores / name for name in TRACE_STORES if
  (stores / name).is_dir())` — so `.devpro-temp/.profiler-directives/` joins no feed and no store
  read, as the entry states ("the directory is not a store, and no reader of the stores reads it as
  one").
- Tests and fixtures pinning the changed behavior, all in scope to update — the pinned expectation
  moves with its requirement:
  - `tests/test_devpro_profiler.py:100` — `_RECORD_FIELDS = {"v", "harness", "at", "session",
    "tool", "name", "ok", "args", "branch"}` gains `plan` and `directives`; the pin is the
    record's shape, so the fields' arrival changes it. Its only uses are :100 and :258
    (`git grep -n '_RECORD_FIELDS' -- tests devpro devtools` → those two lines).
  - `tests/test_devpro_profiler.py:246` — the docstring "carrying schema 3"; :258 —
    `assert record["v"] == 3`; the `"v": 3` fixtures at :455, :466, :488, :669, :779, :1113.
  - `tests/profiler_contract_runner.ts` — drives the shipped `profiler.ts`'s record construction
    through a stub plugin context for tests/test_devpro_profiler.py:574. No change is expected: the
    runner asserts no key set and no `v` value — it returns the raw records for the Python test to
    assert (its stdout is `JSON.stringify({ records })`, runner:184) — so a failure in the runner
    after this package's changes is a finding, never an edit to pass.
- The two document targets above.

`tests/fixtures/profiler_serialize_record.json` is read-only in this package — leave its shape. It
is frozen input, not a pin: tests/fixtures/__init__.py:9-11 states it "is not derived from the
capture: a field the record gains, renames or drops leaves the fixture holding the old shape", and
tests/test_devpro_profiler.py:902 measures `serialize`'s clipping over the fixture's field lengths,
so bumping its `"v"` (:2) or adding fields silently changes the asserted arithmetic.

Facts this package acts on (re-run any of them):

- `git grep -n SCHEMA_VERSION -- devpro tests devtools` → devpro/profiler/values.py:14
  (`SCHEMA_VERSION = 3`), devpro/profiler/capture.py:26, :323, :368,
  devpro/harnesses/resources/opencode/profiler.ts:61, :309, :358. Every hit is in this package's
  scope; the value changes in both captures together.
- The Python capture runs one process per hook event; the opencode capture is long-lived in the
  host's process. The stamp's read-or-compute differs accordingly — the Python capture reads the
  store file it is appending to; the opencode capture holds the session's records in memory —
  the design entry's once-per-session rule governs both.
- Tests this package adds name their defect by the test-precondition clause: the defect is a
  capture that writes records without the session's stamp, or one that re-computes a stamp where
  the store already holds records to read it from, or a manifest absent where a digest's file list
  must be recoverable.

Done-line, run once at the package's end:

- `just test` passes.
- `just lint` passes — `profiler.ts` is a shipped TypeScript resource the lint's `tsc` pass checks,
  and the capture changes are Python the gate checks.
- `just dev-check-design-deltas-applied` exits 1 and prints no `drifted` and no `conflicting` state
  line. Its stdout gives the seven state lines in document order, naming `landed` on exactly :55
  and :118 — :118 is this package's [Harness profiler] pair; the [The operational-context stamp]
  entry is a whole leaf and has no pair, so no state line names it — and `pending` on the other
  five (:22, :135, :158, :191, :226, P3 and P4's pairs); its summary line reads `pairs: 7, landed:
  2, pending: 5, drifted: 0, conflicting: 0, problems: 0`.

## P3 — the stamp at read

Applies the design's [Serving, The index](ACTIVE_DESIGN.md#serving-the-index) and
[Serving, The models in the page](ACTIVE_DESIGN.md#serving-the-models-in-the-page) entries to their
target `PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md`, verbatim except relative links.

Intended lifetime: shipped. Rating: expert — the entries enumerate the feed's keys and the two
columns, but the cells' rendering (the cut length, the separator, the `null`/`title` handling) is
authored in the index template's script with no existing helper named. Mechanical requires every
edit enumerated, and these are not; the rating is expert accordingly.

Scope, named in files and symbols:

- `devpro/profiler/pages.py` — `traces_feed` (:970) and `_feed_entry` (:1002) gain the feed's
  `plan` and `directives` keys; `session_data` (:688) gains the stamp on the page data; the index's
  static page built by `index_html` (:1021) gains the two columns and their cells' rendering in its
  script.
- `devpro/profiler/view.html` — the session page's header line (the `facts` line, view.html:140,
  where the models phrase is built) gains the plan's title and the directives digest beside the
  session's models, per the entry.
- `tests/dashboard/test_server.py` — the feed's key set is pinned at :107-108
  (`SESSION_KEYS = {"harness", "id", "models", "records", "agents", "first", "last", "span"}`;
  `DISPATCHED_KEYS = SESSION_KEYS | {"dispatcher"}`) and moves with the keys; the test
  `test_the_traces_feed_answers_one_entry_per_session` (:110) pins one feed entry per session and
  keeps pinning it. Updating the pin is in scope; a test failing on behavior this package does not
  state it changes is reported as a finding, never edited to pass.
- `tests/test_devpro_profiler.py:103` — `_PAGE_KEYS = {"session", "branch", "models", "contexts",
  "markers", "calls"}`, the pinned page-data key set, gains the stamp's keys beside the feed pins
  above; the page data this package's `session_data` change adds fields to is what it pins.

Facts this package acts on (re-run any of them):

- The read boundary, `devpro/profiler/pages.py`: `child_episodes` :188, `joined_session` :208 (the
  dispatch-to-child join), `session_data` :688, `session_of` :785 (the session's start is the min
  of its records' `at`), `dispatches` :925, `dispatcher_of` :943, `traces_feed` :970,
  `_feed_entry` :1002, `index_html` :1021, the page render ~:1488-1500. The stamp rides the page
  data and the feed read off the records at the same render that reads everything else.
- `devpro/dashboard/server.py` — the feed is served at :19 (`GET /api/traces` named in the
  handler's contract comment) and :150-152 (`traces()` returns
  `json.dumps(pages.traces_feed(self.root))`, read per request). No server change is needed; the
  lines are the evidence the feed's schema is `pages.traces_feed`'s alone.
- Unstamped sessions: a session captured before the stamp carries neither field, renders unstamped,
  and no association is inferred for it (the design's stamp entry states it; the feed's `null` and
  the pages' nothing are the [Serving, The index](ACTIVE_DESIGN.md#serving-the-index) and
  [Serving, The models in the page](ACTIVE_DESIGN.md#serving-the-models-in-the-page) entries'
  statement).

Done-line, run once at the package's end:

- `just test` passes.
- `just lint` passes.
- `just dev-check-design-deltas-applied` exits 1 and prints no `drifted` and no `conflicting` state
  line. Its stdout gives the seven state lines in document order, naming `landed` on exactly :55,
  :118, :135, :158 and :226 — :135, :158 and :226 are this package's [Serving, The index] and
  [Serving, The models in the page] pairs — and `pending` on the other two (:22 and :191, P4's
  pairs); its summary line reads `pairs: 7, landed: 5, pending: 2, drifted: 0, conflicting: 0,
  problems: 0`.

## P4 — the depth-2 chain and the fan-out detector

Applies the design's [Serving, Dispatched children](ACTIVE_DESIGN.md#serving-dispatched-children)
entry to its target `PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md`, and the design's
[Shipped files](ACTIVE_DESIGN.md#shipped-files) SPEC pair to its target
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md` — with this package, the whole design's
delta application is complete.

Intended lifetime: shipped. Rating: expert — the fan-out detector's semantics (what counts as the
fan-out's first dispatch, the review seat's absence before it) and the depth-2 chain's drawing from
a second store's records take judgment the entry does not enumerate.

Scope, named in files and symbols:

- `devpro/profiler/pages.py` — the session page draws, beneath a dispatch's context, the child's
  own dispatched agents: `joined_session` (:208) is the dispatch-to-child join the depth-2 chain
  reads beside, `child_episodes` (:188), `dispatches` (:925) and `dispatcher_of` (:943) are the
  dispatch metadata the page and index already read, `session_of` (:785) is the store reader the
  chain needs — it takes a store path, not a session id, so deriving the child's store path from
  its id is part of the work — `session_data` (:688) and the page render (~:1488-1500) carry the
  drawing. The detector reads the opencode dispatch chains at the same read; its mark stands beside
  the dispatch that opened it on the session page and, after the count, in the dispatcher's index
  row's agents cell (the index script in `index_html` :1021, `_feed_entry` :1002 carrying what the
  cell's count reads).
- `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md` — the [Shipped files]
  (ACTIVE_DESIGN.md#shipped-files) pair applied.
- `PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md` — the [Serving, Dispatched children]
  (ACTIVE_DESIGN.md#serving-dispatched-children) pair applied.
- `tests/dashboard/test_server.py` — the feed and page pins this package's behavior changes (the
  `agents` cell's content, the page's depth-2 rows) are in scope to update; a test failing on
  behavior this package does not state it changes is reported as a finding, never edited to pass.

Facts this package acts on (re-run any of them):

- The stores are flat per-session JSONL under `.devpro-temp/.profiler-<harness>/`; the depth-2
  chain reads the child's store beside the join — one level deeper and no deeper; a claude
  session's nested agents stand on its page already, its subagents' records its own store holds
  (the entry states both bounds).
- The dispatch-duration join reads the child's `experimental.idle`; the depth-2 chain extends that
  join and adds no second one.
- The review seat the detector names is `devpro-prompt-engineer` (the development skill's
  post-plan-reviewers definition). The detector compares dispatch records' `name` field against
  that literal: the agent name lives in `name` on a subagent/Agent call record — opencode's
  `callRecord` sets `agent_id: null` (profiler.ts:315) and
  `name: nameOf(raw, input) ?? (subagent ? DEFAULT_AGENT : tool)` (profiler.ts:319), the context
  key and the agent's name being different fields.
- The index gains no second row level: the mark is the flat table's whole fan-out surface, and the
  count the column sorts stays the count (the entry states both).

Done-line, run once at the package's end:

- `just test` passes.
- `just lint` passes.
- `just dev-check-design-deltas-applied` passes: exit 0, its stdout giving the seven state lines in
  document order all named `landed` (:22, :55, :118, :135, :158, :191, :226), none `pending`,
  `drifted` or `conflicting`, and the summary line reading `pairs: 7, landed: 7, pending: 0,
  drifted: 0, conflicting: 0, problems: 0`. The [The operational-context stamp] entry is a whole
  leaf with no pair; with its leaf written (P2) and these seven landed, the design's delta
  application is complete.

## PR — Post-plan review

Intended lifetime: shipped (it reviews shipped work). Rating: expert.

The post-plan reviewers are the agent for each domain the plan changed substantively — here, the
coder for Python (the type gate, the captures, the render), the coder for TypeScript
(`profiler.ts`), `devpro-architect` (structure and the project documents' claims about the code
changed) and `devpro-prompt-engineer` (the project documents changed). They are given the project
documents and [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), not the plan, and review the changes and their
tests against the project's standards and fitness for purpose. Each reviewer writes their own
review in the scratch directory, independently; the session synthesizes the reviews into
`ACTIVE_PLAN_REVIEW.md`, de-duplicating findings and reconciling them into one account, without
waiting for an approval between the last report and the write-up. The review document is never
diced. This package's row is `landed` in the commit that adds the review document.

## Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` (the post-plan review: four seats, twelve findings F1–F12) —
one item per root-cause group, each closing in exactly one commit; the findings are cited by
F-number and the review document carries each one's evidence and locations. Run order is serial,
B1 → B2 → B3 → B4 → B5 → B6: B1 and B2 share `profiler.ts`'s stamp functions, and B2's binding
test runs code B1 restructures.

### PB Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review landed: items B1–B6 below, drafted
by the session from the review document, usability-reviewed together by one `devpro-prompt-engineer`
pass, revised, and set by state. This ticket's row lands with the drafting.

### B1 — the stamp is taken once, on every path

Fixes F1 and F4. After the fix, the observable the tests plant: a record written after the
session's first stamped record carries the same set of stamp keys that record carries — no key is
gained later — so a session whose plan arrives mid-session gets no `plan` key on any later record;
and no store that already holds records is ever freshly stamped. The mechanism:

- the stamp is copied wholesale from the earliest-`at` stamped record — the whole stamp, not the
  present keys of it;
- a store holding no stamped record is a legacy store and stays unstamped (the leaf's migration
  posture governs; its wording is amended in step with the design entry to state the legacy case
  plainly);
- the TS reader's window reads from the file's beginning, where the earliest records sit; the
  first stamped record within the window governs, and the window's end reached without one means
  unstamped — never a fresh stamp beside old records;
- the manifest is consulted first on the copy path; where none stands for the digest, the per-file
  digests are recomputed from the files as they stand and written, and the leaf states that such a
  manifest may postdate the digest it is keyed by;
- the read is bounded — no full parse of the store per hook.

Scope: `devpro/profiler/capture.py`, `devpro/harnesses/resources/opencode/profiler.ts`,
`ACTIVE_DESIGN.md`'s stamp entry and its applied leaf in step, tests naming the defects above.

### B2 — one digest, bound

Fixes F2 and F3. Both captures build the digest by one stated construction, byte-canonical — path
and file-digest bytes joined without JSON escaping, non-ASCII safe — over one project-wide file
set, stated and walked identically by both captures: every file beneath all of
`PROJECT_HARNESS_DIRS` carrying an installed banner or an ownership marker (the incumbent install
machinery reused, so `registry.json` and `hooks.json` reach the digest), plus the project root's
`AGENTS.md`; a `CLAUDE.md` redirect that names it carries no directive of its own and is not
hashed, and the leaf says so. File links are followed — a symlink is hashed as what it points at,
the user's ruling — and directory links are not descended: the Python walk stops treating a
symlinked harness directory as a directory to enter, as the TS side already does; the leaf states
both halves. The binding test runs both implementations over one fixture project that plants a
file in every walked directory and asserts byte-equal digests and manifests. Scope:
`devpro/profiler/directives.py`, `devpro/harnesses/resources/opencode/profiler.ts`,
`ACTIVE_DESIGN.md`'s stamp entry and its applied leaf in step, tests.

### B3 — the read side reads once and pins once

Fixes F5, F7 and F12. The rulings, stated:

- One earliest-selection reader over records; a record whose `at` is absent never governs the
  stamp's ordering (the read side's current rule), and the capture side aligns to it.
- The depth-2 draw's child records come from the sessions `read_sessions` already read — the store
  path is never rebuilt from the id, the "safe set" question dissolves, and a child absent from
  that read is absent from the draw.
- The index's column count has one home, the header-cell list; the width sum and the `colSpan`
  derive from it, and the pin asserts the span equals the header-cell count.
- The feed schema has one pin, in `tests/dashboard/test_server.py`, replacing the literal
  `SESSION_KEYS`/`DISPATCHED_KEYS` sets; serving.md's feed-key list gains `unreviewed` (design
  pair and target in step).

Scope: `devpro/profiler/pages.py`, `view.html`, `tests/dashboard/test_server.py`, the profiler
tests, `ACTIVE_DESIGN.md` and `serving.md` in step.

### B4 — the mark where the design drew it

Fixes F6 and F8. The unreviewed mark stands in the depth-2 chain row on the dispatcher's page —
after the child's agents' names in that row's call span — and in the dispatcher's index row's
agents cell, after the count. The fan-out's own header-line mark is removed, and the `view.html`
comment recording the opposite choice is edited in step. The per-child `unreviewed` key is retired
with its pin: the design puts the mark beside the dispatch and nowhere on the flat row. The
detector's boundary: the comparison reads the bare name, the prefix strip applied in one helper
beside the renderer's own, and a test plants a prefixed record and asserts the verdict. Scope:
`devpro/profiler/pages.py`, `view.html`, tests.

### B5 — terms and the leaves left behind

Fixes F9 and F10. Document work, each edit's wording in the target leaf's own voice: SPEC's
"empty where a session predates the stamp" states the `null` rendering (design pair and target in
step); serving.md's "review seat" phrase names the post-plan review's seat; the lint gate's two
statements attribute the paths to the mypy line — mypy's arguments name the gate's paths
(`devpro`, `devtools`), the recipe's other lines' arguments are not the gate's, and `tests/` stays
outside them — in `recipes.md` and the CONVENTIONS leaf together; `the-opencode-capture.md` is
amended to state what the capture now reads and writes, the manifest outside its store, in the
tree's voice; the ARCHITECTURE entry-point's listing gains the stamp leaf; the CONVENTIONS lint
leaf gains the sentence "the checker caches its analysis under the scratch directory and writes no
source" — the title stands, the recipe writes no source. Scope: documents only.

### B6 — hygiene

Fixes F11. Edits enumerated: the dead `held`/`s` alias at `linkrewrite.py:66-69` removed;
`GENERATED_MARK` moves to `install_base.py` beside `INSTALLED_BANNER`, `render.py` and
`directives.py` importing it — the import direction is `directives → install_base ← render`, and
no new test is written for it; mypy's cache moves under `.devpro-temp/` (`cache_dir` in
`[tool.mypy]`), and the promise is observable: a `lint` run leaves no `.mypy_cache` at the
repository root. Scope: `devpro/dicing/linkrewrite.py`, `devpro/install_base.py`,
`devpro/render.py`, `devpro/profiler/directives.py`, `pyproject.toml`.
