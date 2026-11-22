# the attribution pass — child sessions grouped under their dispatchers, the index's zebra and marks

Design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md#shipped-files--the-docdicer-package-retires-its-runner-shortcuts-return-the-profilers-and-dashboards-decisions-stages-2-4)
— the Shipped files entry's one pending pair (ACTIVE_DESIGN.md:507-522), whose `becomes` states the
whole decided target:

> A page attributes a child session to the session that dispatched it: the capture extracts the
> child's session id into the parent call's record, the render groups children under their
> dispatching session, links each Agent row to the child's page and heads a child page with its
> dispatcher, and the stores stay flat — the child never knows its parent at write time, the
> hierarchy being metadata the parent side builds, and claude holding no child session records at
> all. The index's rows alternate their tone — a zebra the eye reads across the columns — and each
> row's harness carries its own mark, a dot in the harness's brand colors: opencode's blue, claude's
> coral.

The pass also carries the roadmap's ticket *The index's moments read local time and the span as
data* (ROADMAP.md:55-61), which names this pass the owner of the index's rows and folds its work
in: the moments rendered in the reader's local time — the browser's, where the page renders — the
span as its own datum, human-legible ("3h 42m"), the raw UTC kept in the title attribute where a
hover wants it. The ticket leaves the roadmap when this plan lands.

The delta gate's own answer, run during planning (`just dev-check-design-deltas-applied`):
`ACTIVE_DESIGN.md:507: pending: PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md … pairs: 80,
landed: 79, pending: 1, drifted: 0, conflicting: 0, problems: 0` — the pass is that one pair, plus
the ticket's work inside it.

APPROVED: the PE review and revision round is complete, and the user approved this plan —
dispatch proceeds under that approval.

**Decision this plan lands** (strike it in approval where wrong): one package builds the pass
whole. The only candidate boundary is capture against render — the capture gains one read of the
host's payload, the render consumes the field — but they meet at the record schema both sides
already share (`CallRecord.child_agent_id` stands in the type, profiler.ts:271; the claude capture
writes the field today, capture.py:317), the render tests' fixtures already carry the payload's
shape (`tests/profiler_capture_runner.ts:64`), and a split would leave the render's grammar with
nothing to build against while the capture lands. No verb, route or file retires.

## Status

| Package | State | Rating | Lifetime | Work |
| --- | --- | --- | --- | --- |
| A1 | landed: the delta gate reports 80 landed, 0 pending | expert | shipped | the attribution pass: the opencode capture's child-session extraction, the index's grouping, zebra and brand marks, the moments in local time with the span as a datum, the child page's dispatch band, the Agent-row links, and the pending pair's application |
| PR | landed: the review document committed | expert | shipped | Post-plan review |
| PB | dispatchable: the PE review's findings revised in; B2's hold gates the dispatch | expert | shipped | Post-plan burndown |

## A1 — the attribution pass

Lifetime: shipped. One commit closes it — the capture's extraction, the render's grouping and the
SPEC leaf's application are one behavior whose record must land together.

**Scope** (files): `devpro/harnesses/resources/opencode/profiler.ts`, `devpro/profiler/pages.py`,
`devpro/dashboard/server.py` (the band builder, if the child band needs a parameter),
`devpro/profiler/chrome.js` (the moments' localization joins the nav's script — the moments bullet
below decides the home),
`devpro/profiler/view.html` (the Agent-row link drawing only),
`tests/profiler_capture_runner.ts`, `tests/test_devpro_profiler.py`,
`tests/dashboard/test_server.py`, `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

**What does not change.** The claude capture writes nothing new: `capture.py` already takes the
child's agent id from the hook payload's `tool_response.agentId` (`"child_agent_id": child_id,`
capture.py:317), and claude records subagents' calls inside the parent session's own file — claude
holds no child session records, which the entry states, not changes. The stores stay flat: no
capture gains a parent key, no store changes name or directory. The CSP, the layer link and the
chrome serving are untouched (the pair's context, landed `a7f1390`): the serve path still links
`/board/board.css` and `/profiler/chrome.js`, and no test in that seam is re-expected except where
the scope below names one.

**The capture's field — the payload's shape, verified.** For opencode's `task`/`subagent` calls,
the child's session id reaches the `execute.after` hook as a string at
`call.result.metadata.sessionID`. Three facts, each re-runnable:

- The hook's `result` is the tool's own `{output, content, metadata}` shape — the host builds it as
  `…status:"completed",result:{…output,content,…metadata}` on the `"execute.after"` trigger.
  Command and answer: `command strings /opt/homebrew/bin/opencode | command grep -o '.{180}"execute.after".{250}'`
  on the installed opencode v2.3.2 (`opencode --version` → `opencode v2.3.2`) returns that
  construction.
- The subagent tool's own `metadata` is `{sessionID: <child id>, status}` — the host returns
  `metadata:{sessionID:z.sessionID,status:z.status}` beside the job's `childSessionID:Y.id`.
  Command: `command strings /opt/homebrew/bin/opencode | command grep -o 'metadata:{sessionID:z.sessionID,status:z.status}}'`.
- The host itself reads that field with a string guard — `se.name==="subagent"&&typeof
  re?.sessionID==="string"?re.sessionID:void 0` — the guard the capture copies.
  Command: `command strings /opt/homebrew/bin/opencode | command grep -o 'typeof re?.sessionID==="string".{160}'`.

The change: `profiler.ts`'s `callRecord` (profiler.ts:282-316) fills the existing `child_agent_id`
slot (today hard-nulled at :304 under the comment :301-303 that the host's result names the child's
session) from `call.result.metadata.sessionID` under the capture's own gate — the `subagent` flag,
`raw in SUBAGENT_TOOLS` (profiler.ts:285), which admits both the `subagent` and the `task` spelling
— with the host's string guard on the value only (`typeof re?.sessionID === "string"`, the third
fact above); the host's literal tool-name check (`se.name==="subagent"`) is not the gate the
capture copies. A task-spelled dispatch fills the field by the same path when its result carries
the metadata, and the fixture's task call — whose `execute.after` carries no `metadata` — keeps
`null`; every other call, and a dispatch whose `execute.after` never fires, keeps `null`. The agent-kind
read (`childAgentTypeOf`, :242) is untouched. The repo's TS fixture already carries the host's
shape (`tests/profiler_capture_runner.ts:64` `result: { output: "ses_child", metadata: {
sessionID: "ses_child" } }`, `:72` the fork's), so the fixture needs no shape change — only the
assertion below. `serialize`'s fitting list (`name, session, result, args`, profiler.ts:341) is
unchanged: a session id is short, and `tests/profiler_serialize_runner.ts:33` already passes
`child_agent_id: null` at the bound.

**Named consequence — the tree and diagram read the field too.** `pages.py`'s `contexts_of` and
`build_forest` read `child_agent_id` as the context a call started (pages.py:255, :328). An
opencode dispatch whose record carries the child's session id now draws in the text tree and the
page diagram as the context it opened — `new context <child id>`, and `copy of <parent>` on a
`fork` — the words claude dispatches already draw for the same fields (pages.py:384-392). The
entry's grouping statement covers the pages; the tree's shift is a consequence of writing the
truthful id in the shared record, and it is pinned, not prevented: the tree test below gains the
dispatch fixture. The child's own calls stay in the child's file, where they never were in the
parent's — the profiler.ts comment's whole point (:301-303) — so the tree draws a dispatch bar of
the dispatch's own duration, which is true.

**The index's grouping — where it lands.** `index_html` and `session_row` (pages.py:723-732,
745-756) build the rows; the grouping is render-side, computed over `read_sessions`'s sessions
(pages.py:696-714). One child is an opencode session whose id appears in some other session's
opencode records' `child_agent_id`; the grouping matches only on opencode records (`harness`
`"opencode"`), so a claude record's agent-id `child_agent_id` never names a session and claude rows
never group — the entry's "claude holding no child session records". The grammar, from the entry
and the session's refinement (the mockups in `.devpro-temp/ux-pass/`, untracked scratch):

- The dispatcher's row carries its dispatched count beside its link — the index mockup's
  `<small>— 5 dispatched agents</small>` (`mock-attr-index.html` dispatcher row). The count is the
  grouped child rows rendered under that dispatcher — the same grouping that draws them — not a
  count of the parent's dispatching records nor of the distinct child ids its records name: those
  differ when a child's store is lost or one record is reused, and a count that disagrees with the
  rows beside it is a defect a reader sees at a glance.
- Each child session renders as one indented row under its dispatcher's row, an empty first cell
  carrying the accent bar and the indented cell beside it — the grammar's pair,
  `tr td:first-child.child { border-left: 3px solid var(--accent); }` and
  `tr td:first-child.child + td { padding-left: 2.4rem; }` (`mock-attr-index.html:307-308`) — its
  link followed by `↳ child — <the dispatching call's name>` (the parent record's `name`); one row
  per child, children in first-moment order.
- The rows alternate their tone across the columns — a zebra — and each row's harness cell carries
  its own mark, a dot in the harness's brand colors: opencode's blue, claude's coral
  (`zebra-brands.html:11-12`, `--harness-opencode: #4a9eea; --harness-claude: #d97757`). The zebra
  and dot rules live in the index template's own style block (the `INDEX` template, pages.py:798-811)
  — "the template's own rules are the page's alone" (PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:57).
  The zebra's rule is decided: odd rows — `tr:nth-child(odd) td { background: #191c22; }` — with the
  tone the literal `#191c22`, the stronger-contrast candidate the mockup's own comment names the
  winner (`zebra-brands.html:26-27`, "the stronger zebra"); no shared-layer variable stands behind
  it — the shared layer holds `--track`/`--card`, and the zebra reads neither. A variable tone is
  the dots' alone, and their two colors are new variables of the page's own, not the site's
  phosphor: the dots are the only brand-marked part of a row.
- The moments: rendered in the reader's local time — the browser's, where the page renders — with
  the span as its own datum ("3h 42m") and the raw UTC in the title attribute (ROADMAP.md:55-61).
  The served bytes are decided:
  - The moments cell's static text is the raw UTC string the old test pins — the exact instant
    where no script runs — and the cell's `title` attribute carries that same string, so a hover
    carries the exact instant whether or not a script ran. The script replaces only the cell's text
    with the mockup's localized form (`mock-attr-index.html:395`, `21:36 to 21:53`): the two
    instants in the reader's local time, `H:MM to H:MM` where both share the reader's calendar day,
    each carrying its date where they do not — the one case the mockup does not show, decided here
    — and the title keeps the raw UTC untouched.
  - The span is its own column, headed `span`, last, after `first to last` — the mockup predates
    the ticket and shows no span, so the moments cell keeps the mockup's exact text. The span is
    timezone-independent, computes where first/last are in hand, and renders server-side: its
    static text stands under script and no-script alike. The table's grammar moves with it:
    `unreadable_row`'s `colspan="4"` (pages.py:737) and the empty-index row's (pages.py:755)
    become `colspan="5"`. The human-legible form is the ticket's grammar in whole seconds — hours
    and minutes ("3h 42m"), minutes alone, seconds below a minute, and "0s" for a zero-length span
    — so the fixture's one-second span renders `1s`.
  - The localization joins `chrome.js`: the script the nav's poll and stop live in gains the
    moments' code, and `/profiler/chrome.js` carries it beside them. The byte-pin consequence is
    named: `tests/dashboard/test_server.py:372` compares the served bytes against `CHROME_SCRIPT` —
    the constant read from the changed source — so it keeps holding without re-expectation, as does
    the `scripts: 0` parametrize (`pytest.param("profiler/", 0, id="index")`, :327, asserted at
    :349): no second script link and no inline block land.

**The child page's dispatch band.** The served child page's frame band heads with its dispatcher —
the decided band, verbatim: `Dispatched by <link to the dispatcher's page> — <the dispatching
call's name>`, beside the existing `Return to list`. The mockup line it refines also carries a
third element, `· <strong>the U1 executor</strong>` (`mock-attr-child.html:53`); that executor
element is dropped — no field the pass writes names an executor beyond the dispatching call's own
name, which the band already carries, and the band builder's data are the dispatcher's link and
that name.
The dispatcher is resolved where all sessions are in hand: `page_of` (pages.py:827-833) reads the
other sessions' opencode records for the parent that names this session, and hands the dispatcher
to the band builder (`dashboard/server.py:101-111`'s `band_html` — one caller). The file-flow page
carries none of it: the hierarchy is metadata the parent side builds, and the file flow holds one
session — so the dispatch band is the serve path's band, chrome, and the byte pin below keeps
passing. Reference searches, with answers:

- `git grep -n "band_html" -- "*.py"` → `devpro/dashboard/server.py:101` (definition), `:111` (the
  one caller), `devpro/profiler/pages.py:773` (docstring prose only).
- `git grep -n "page_of" -- "*.py"` → `devpro/dashboard/server.py:46` (import), `:179` (the one
  caller), `devpro/profiler/pages.py:827` (definition).

**The Agent-row links.** On a parent's session page, each Agent row links to the child's page:
`render_html`'s call entries already carry `"child": record.get("child_agent_id")` (pages.py:581,
quoted) into `view.html`'s data, and the diagram gains the link where the record's harness is
`opencode` — a claude record's `child_agent_id` is an agent id, no page exists for it. Whether the
link's condition rides a shaped key in the page data or the record's harness beside it is the
executor's call; both carriers run the same render, so the byte pin holds. A page whose link names
a page the dashboard does not serve (the child's trace lost) answers the existing 404, not a
broken page.

**The SPEC leaf — the pair's application.** Target
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`. The leaf already stands at the becomes's
opening (`registers no hook entries; … and a mage install ships none of them.`, lines 150-152);
the application inserts the new sentences verbatim after that sentence, re-wrapped to the leaf's
prose, so the leaf carries the whole `becomes` text (ACTIVE_DESIGN.md:511-522) modulo line
wrapping: `A page attributes a child session to the session that dispatched it: … opencode's blue,
claude's coral.` The gate confirms: `just dev-check-design-deltas-applied` reports
`landed: 80, pending: 0`.

**The ARCHITECTURE leaf.** `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` states what the
change moves, in the same commit: the opencode capture section (:146-174) gains the extraction —
the dispatch's `result.metadata.sessionID`, the child's session, landing in the record's
`child_agent_id` under the host's own string guard — and the Serving paragraph (:85-88, "one row
per session — harness, session id, record count, first and last moments — each linking to
`/page/<session-id>`") states the grouped presentation, its row list gaining the span beside the
moments: children under their dispatchers, the
zebra and the harness marks, the moments in the reader's local time with the span its own column
and the raw UTC in the title attribute. No other ARCHITECTURE leaf states these rows: the subsystem
map's profiler row is the skill's rendering routes (PROJECT_DOCS/ARCHITECTURE/subsystem-map.md:69-75),
unchanged.

**Tests** — each naming the defect it fails on, per the test-precondition clause
(`clauses.TEST_PRECONDITION` in `devpro/clauses.py`):

- `test_the_opencode_capture_records_every_fired_call` (tests/test_devpro_profiler.py:386-418)
  gains `calls[3]["child_agent_id"] == "ses_child"` and the fork's `calls[4]["child_agent_id"] ==
  "ses_fork"`, and pins the task spelling's null: `calls[5]["child_agent_id"] is None` — the
  `task`-spelled call whose fixture `execute.after` carries no `metadata`, so the capture's gate
  fills nothing. Defect: the capture drops the child's session id from a dispatch's record — with
  that record the index cannot group children under their dispatchers and the Agent row cannot link
  to the child's page — or misreads the task spelling's bare result as an id.
- `test_the_served_index_lists_every_recorded_session` (tests/test_devpro_profiler.py:582-605) is
  re-expected and extended: the fixture gains an opencode parent with a record carrying
  `child_agent_id` and the child session it names (extending `_write_store`, :548, to inject
  records — executor's call), and the row-list assertions re-expect the rows the additions bring.
  Its two raw-UTC pins on the moments' static text (`"2026-01-01 00:00:00 UTC to
  2026-01-01T00:00:01.000Z"` at :601, the opencode row's at :603) keep holding — that string is the
  static text, and the title attribute carries it too. The new assertions pin a child row indented under its
  dispatcher with the accent bar and `↳ child — <call name>`, the dispatcher's count, the harness
  dots, the zebra alternation, the span cell's datum (`1s` on the one-second row, `0s` on the
  zero-length one) and the title attribute's raw UTC. Defects: an index that lists a child session
  as a stranger drops the dispatching relation its records state; a span cell that invents or
  misstates the duration, and a title attribute that loses the raw string, leave the hover nothing
  exact to carry.
- `test_the_served_page_is_the_html_the_file_flow_writes` (tests/test_devpro_profiler.py:650-673)
  passes unedited, and it is the plan's constraint, not a test to change: the dispatch band is
  chrome, never the file-flow page's content, and the page data's grouping keys flow through
  `render_html` so both carriers hold the same data. A change that puts dispatcher content into the
  file-flow bytes fails this test, and that failure is the defect, not an expectation to move.
- tests/dashboard/test_server.py's `test_a_session_page_carries_the_bands_legend_and_the_way_back`
  (:400) is extended, or a test beside it is added: a child session's served page's band carries
  `Dispatched by` with a link to the dispatcher's page, and the band of a page no one dispatched
  does not. Defect: a child page that names no dispatcher loses the way back to the session that
  dispatched it.
- `test_every_profiler_view_page_renders_the_way_the_file_flow_renders_it`
  (tests/dashboard/test_server.py:331-351) passes unedited: the localization joins the linked
  `chrome.js`, so its `scripts: 0` param for `profiler/` (:327, asserted at :349) keeps holding —
  no second script link and no inline block land.
- `test_a_tree_renders_an_opencode_store_beside_the_claude_capture`
  (tests/test_devpro_profiler.py:301-347) gains an opencode dispatch record in its fixture and
  pins the tree line's context words (`new context …`; `copy of …` on the fork's
  `child_agent_type`). Defect: the tree drops or misreads the context words an opencode dispatch's
  record carries — the two harnesses' dispatches drawing differently for the same fields.
- `test_the_installed_profiler_is_the_sources_bytes` (:257) keeps holding: the resource is copied,
  never stamped.

**Done-line.** `just test devpro && just lint && just dev-check-links && just test docs && just
dev-check-design-deltas-applied` — run once, at the package's end: the pytest surfaces over the
changed code and dashboard suites, the lint over them, the link check over the touched leaves and
the plan, the docs surface (its link check with its defaults), and the delta gate confirming the
pair landed.

## PR — Post-plan review

Lifetime: shipped. The reviewers are given the project documents and the design, not the plan,
and review the changes and their tests against the project's standards and fitness for purpose.

The review landed as `ACTIVE_PLAN_REVIEW.md` (commit `d63e4c5`) — four seats, one entry per
de-duplicated defect.

## PB — Post-plan burndown

Lifetime: shipped. Drafted from `ACTIVE_PLAN_REVIEW.md` (landed `d63e4c5`), grouped by root cause;
each item cites its finding's ID. The package's done-line, run once at its end:
`just test devpro && just lint && just dev-check-links && just test docs` — every item's check is
inside those runs; B5's new test's failing run is `just test devpro` (the claude-guard removal it
names is the mutation that fails it).

- **B1 (F1)** — the zebra's tone gets a motif-aware carrier: a shared-layer variable the
  board.css `:root`/dark pair owns, or a second `prefers-color-scheme` block in the template's own
  style — dark keeps `#191c22`, light takes `#e7e7eb` (proposed; strike where wrong). The zebra
  test pins stop asserting the literal declaration (F1: the literal spelling is not the contract)
  and assert the carrier's effect instead: the odd-row rule reaches the served page, and the
  harness cell carries its class.
- **B2 (F2)** — nested dispatch chains: HELD for the user's decision. If the word is *walk*:
  `index_html` draws each dispatcher's subtree and the count covers every row beneath. If the word
  is *one level*: the code stands and both leaves gain the clause "a dispatch's child one level
  deep; deeper chains read on the session's page, whose tree draws every dispatch as a context."
- **B3 (F3)** — the self-dispatch exclusion is one fact: `dispatches` drops a session named as its
  own child before returning (or the admissible children are computed once and both the filter and
  the grouping derive from them). The `index_html` docstring states what the code now does, and
  the `childPage` docstring's rationale matches its guard's shape. Observable and pinned: a
  fixture record naming its own session draws exactly one row — the test's defect: a self-naming
  record drops the session from the index or draws it twice.
- **B4 (F4)** — one read serves both the page and the dispatcher: `page_of` returns the session
  beside the page, or a sibling lookup takes the sessions in hand; `server.py`'s second full
  `read_sessions` goes.
- **B5 (F5)** — a test pins the claude guard: a claude store whose record's `child_agent_id`
  equals another session's id groups nothing and emits no `childPage` link. Defect: removing
  `record.get("harness") == "opencode"` groups a claude-named session and links a page that does
  not exist — this test is what fails under it.
- **B6 (F6)** — decided, not branched: the moments' format authority moves to `_moments`, which
  emits `<time datetime="…">` elements the script reads — the `MOMENTS` regex goes — and a runner
  test loads `chrome.js` over same-day and cross-day cells asserting the rewrite, the untouched
  title, and the unmatched-cell fallback. Defect: a moment cell whose served format drifts parses
  to nothing and keeps raw UTC silently — this test is what fails under it.
- **B7 (F7)** — the code carries what no act can produce as a file today: `childSessionOf`'s
  docstring names the version range the field holds from and states that a result with no record
  metadata is a valid no-child state. The machine-hold gap — nothing re-checks the host fact on
  the next point release — becomes a ROADMAP ticket (a captured real `subagent` payload as a
  re-examinable artifact), not a pretend file in gitignored scratch.
- **B8 (F8)** — the notes bundle, each at its site: the count reads `1 dispatched agent`
  (`session_row`, pages.py:790) and the pin re-expects singular (`test_devpro_profiler.py`);
  the older substitution-slot comment (`pages.py:891-892`) is reworded to name the row slots it
  describes; the href builder is exported and shared by `render_html`'s `childPage`,
  `dispatcher_html`, and `_session_link`; `calendar` is replaced by a `sameDay` predicate
  (`chrome.js:88`, `:97`) with `dayOf` for display only; `view.html:372-378` gains a note that the
  link's target answers the existing 404 where no child page is served; the band test helper
  `_band()` (tests/dashboard/test_server.py) names its return-label coupling in its docstring.
- **B9 (G3)** — `pyproject.toml` gains `profiler/chrome.js` as package data; `just test` (whole
  tree) green again.
- **B10 (G1)** — the proposed CONVENTIONS rule lands as
  `PROJECT_DOCS/CONVENTIONS/planning-and-execution/evidence-commands-run-before-they-ship.md`:
  "Evidence commands run before they ship. A command a plan or design states as re-runnable
  evidence is run when the document is written, and its stated output is what the run returned."
- **B11 (G2)** — the sentence lands in
  `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/harness-resources-are-copied-verbatim.md`:
  the `.ts` harness resources are held only by their tests — no type check or lint covers them.
- **B12 (new — the user's finding during the hotfix, `c11c4d9`)** — `chrome.js` is renamed
  `deco.js`: a name a reader meets in a failure path cannot tell apart from a platform-specific
  resource loaded erroneously, and the confusion is a diagnosability defect — today it cost real
  diagnostic time, and the name manufactures a question no other site answers. Sites the rename
  touches, each verified in the change: the file and the `CHROME_SCRIPT` constant and
  `/profiler/chrome.js` route in `server.py`, the board page's script reference, the byte pins
  and the new one-scope compile pin, the ARCHITECTURE leaf's statement of the script, and the
  plan's own prose. The prose term "the nav's chrome" stays where it stands: the record is the
  name's retirement, not the concept's.
