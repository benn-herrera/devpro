# Plan — profiler dashboard corrections and sweep granularity

Implements [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md): its [Repo Layout ARCHITECTURE
entry](ACTIVE_DESIGN.md#repo-layout), its [Harness profiler](ACTIVE_DESIGN.md#harness-profiler)
ARCHITECTURE entry (display and failed feed), and the [Code delta](ACTIVE_DESIGN.md#repo-layout-1)
([profiler half](ACTIVE_DESIGN.md#harness-profiler-1)). Every package below is **shipped**. Each
closes in one commit.

Line numbers in this plan are of-when anchors, taken as this plan was written; tests and symbols are
cited by name, and a name outranks a stale line number.

## Status

| Package | State | Rating | Scope |
| --- | --- | --- | --- |
| P1 | landed: 6854bb9 | expert | sweep reads definition string literals as sentence units; repo-layout pair 1 |
| P2 | landed: 74c5f7e | expert | double-delivery check compares sentences; scratch-name pin retired; repo-layout pair 2 |
| P3 | landed: 99f0f4d | expert | unreadable store fails the feed; `read_sessions` returns the list alone; profiler pair 1 |
| P4 | landed: e4f1edd | expert | agents cell, query-carrying links, `devpro-` prefix drop; profiler pair 2 |
| PR | landed: 4d32c66 | expert | review of what shipped, written to `ACTIVE_PLAN_REVIEW.md` |
| B0 | landed: f3e8835 | expert | Post-plan burndown drafting: the section's items from the review, then their usability review |
| B1 | landed: 8143650 | expert | sentence-grain check hardening: real-tree case, constant-form pin, marker strip |
| B2 | dispatchable | expert | the failed-feed answer: one catch-all, the notice rendered |
| B3 | landed: 7d5547c | expert | sweep line numbers, helper dedup |
| B4 | landed: 641ef80 | expert | the prefix's one source and its tool gate |
| B5 | landed: c026bcb | mechanical | document wording: repo-layout row, leaf reflow |
| B6 | dispatchable | mechanical | pin honesty: name the form pins |
| B7 | dispatchable | mechanical | CONVENTIONS lines: real-tree case, synonym search, scratch hygiene |
| B8 | dispatchable | mechanical | the cli docstrings' one home |
| B9 | drafted — blocked on the owner's choice (R18) | expert | the families' anchor prose: in the literals corpus or recorded as out |

P1–P4 and PR are `landed`. The burndown's items B1–B8 were drafted from `ACTIVE_PLAN_REVIEW.md` in
the section shape the owner directed: one ticket per root-cause group, each with its own row,
rating and one-commit close. They stay `drafted` through the burndown's `devpro-prompt-engineer`
usability review and the session's revision; B2 stays blocked on the owner's choice of outcome
regardless.

## Sequencing

- P1 → P2 → P3 → P4, in that order. P3 and P4 both edit `devpro/profiler/pages.py`: packages that
  share a build run serially in the shared tree.
- Each package that implements an ARCHITECTURE delta entry applies that entry's passage pair to its
  target leaf in its own commit (CONVENTIONS, *A delta application ends verified*), then searches the
  doc set for the replaced wording (CONVENTIONS, *A delta application is followed by a search of the
  doc set*). `just dev-check-design-deltas-applied` goes green only once every pair has landed — it is
  P4's done-line, and the plan names its expected failure on P1–P3.
- The checkpoint gate is CONVENTIONS-bound: `just test`, then `just sweep-python`, before each
  checkpoint commit.

## P1 — the sweep reads definition string literals as sentence units

Implements the [Code delta's Repo Layout entry](ACTIVE_DESIGN.md#repo-layout-1) sweep sentences and
applies the [ARCHITECTURE Repo Layout entry](ACTIVE_DESIGN.md#repo-layout)'s `dupe_sweep/` passage
pair to `PROJECT_DOCS/ARCHITECTURE/repo-layout.md`.

**Scope.** `devtools/dupe_sweep/doc_sentences.py`, `devtools/dupe_sweep/passes.py`,
`devtools/dupe_sweep/python_corpus.py` as needed; `devtools/tests/test_dupe_sweep.py`;
`PROJECT_DOCS/ARCHITECTURE/repo-layout.md` (the `dupe_sweep/` pair only).

**Facts.**

- The python pass composes its corpus and unit sources at `devtools/dupe_sweep/passes.py:35-43`
  (`code_corpus`, `shape_units`, `doc_units`, `constants`), and the doc pass's unit source is
  `doc_sentences.doc_units` (`passes.py:13,38`). Reference search
  `git grep -n -e "doc_units" -e "code_corpus" -- devtools/dupe_sweep devtools/tests` returns exactly:
  `doc_sentences.py:52` (def), `passes.py:13,36,38`, `python_corpus.py:17` (def),
  `devtools/tests/test_dupe_sweep.py:193`. No other caller — reshaping these is safe.
- The sentence splitter is `doc_sentences._split_sentences` (`doc_sentences.py:27`) reached through
  `block_sentences` (`:31`); reference search
  `git grep -n "_split_sentences" -- devtools tests` returns `doc_sentences.py:27,47` only.
- The corpus filter is `python_corpus.CODE_PREFIXES`/`CODE_UNSWEPT` (`python_corpus.py:13-14`); the
  definition modules the entry names — `devpro/definitions/`, `devpro/harnesses/`,
  `devpro/clauses.py` — are inside the swept trees already; what is new is reading their string
  literals as sentence units, which no pass does today (`constants.py` reads module-level bindings as
  values, `doc_units` reads docstrings and comments only).

**Guidance.** The literals of the three named definition-module areas join the python pass's unit
sources as sentences, split with `doc_sentences`' splitter rather than a second one; the candidates
report through the existing renderers like the rest — sorted, byte-stable, advisory, no new exit
path. How literals are gathered (ast walk, which node kinds) and which pass reports them is the
coder's call. Any added test names its defect by `clauses.TEST_PRECONDITION`: today a distinctive
sentence carried as a string literal in two definition modules is no candidate, so shared prose can
drift between two literals unseen — the test fails on that defect.

**Done-line.** `just test dupe_sweep`, then `just sweep-python` (advisory; exits zero with findings),
then `just test-changed`. `just dev-check-design-deltas-applied` is expected to fail until P4 lands
(the plan accounts for it; P4's done-line closes it).

**One commit** carries the code, the tests and the applied pair.

## P2 — the double-delivery check compares sentences

Implements the [Code delta's Repo Layout entry](ACTIVE_DESIGN.md#repo-layout-1) check sentences and
applies the [ARCHITECTURE Repo Layout entry](ACTIVE_DESIGN.md#repo-layout)'s `tests/` passage pair to
`PROJECT_DOCS/ARCHITECTURE/repo-layout.md`.

**Scope.** `tests/test_devpro.py` (`_double_paragraphs`, its fixtures' expectations, and the removal
of `test_no_rendering_names_a_retired_scratch_directory` with its rendering loop);
`devtools/dupe_sweep/doc_sentences.py` only if promoting the splitter's name is the chosen reuse;
`PROJECT_DOCS/ARCHITECTURE/repo-layout.md` (the `tests/` pair only).

**Facts.**

- Fixture drift, the after-run's comparison mechanism: `devpro.clauses.DISSENT` splits into 3
  sentences (reproduced: the collapsed constant through `doc_sentences._split_sentences` → 3), so
  `test_a_command_repeating_a_clause_the_output_it_loads_carries_is_refused`'s `_double_paragraphs`
  expectation (`tests/test_devpro.py:2270`) goes from one finding previewing the paragraph to three,
  one per sentence. `just test devpro tests/test_devpro.py -k repeating_a_clause` is the command that
  shows the three once the change lands — that passing run is the after-run's anchor, not a count
  match against the tree as it stands. No recipe stores a baseline, and the tree moves under any
  stored count, so the plan states no baseline figure beyond this expectation change. The other three
  double-delivery fixtures — `test_a_paragraph_the_agents_file_and_an_agent_both_write_is_refused`
  (`:2181`), `test_a_paragraph_one_output_writes_twice_is_refused` (`:2275`),
  `test_a_thematic_break_written_twice_is_not_a_paragraph` (`:2280`) — are single-sentence and keep
  their counts; only the preview text's source moves from unit to sentence where the two differ.
- Drift probe (run twice during planning; both runs agreed): on the rendered prompts the check walks
  (`tests/test_devpro.py`'s `_prompts` over `_definition_sources`), paragraph grain reports **0**
  findings today. The naive sentence split reports **13**, all enumeration-marker fragments, and
  every one is body-internal — a single output carrying two numbered lists whose markers collide:
  `agents/architect.md` (5: `1.`…`5.`), `skills/development/references/project-documents.md`
  (5: `1.`…`5.`), `skills/kbase/references/reading.md` (3: `1.`…`3.` — its two lists share markers
  1–3, the body-internal worst case the usability review probed). No finding comes from a cross-output
  collision; the families' parallel structure stays out, as the design states. A marker is the list's
  numbering, not prose.
- The scratch tests: `test_the_scratch_rule_names_the_one_scratch_directory` (`:770`) positively pins
  every harness's `scratch_rule` to `devpro.clauses.PROJECT_TEMP_DIR`; the negative-space pin
  `test_no_rendering_names_a_retired_scratch_directory` (`:778`) is removed whole with its rendering
  loop (design, [Code delta](ACTIVE_DESIGN.md#repo-layout-1)).

**Guidance.** `_double_paragraphs` keeps its name, scope and finding shape; each prose unit — the
joined, whitespace-collapsed text `_prose_unit_list` already walks — splits into sentences with
`doc_sentences`' splitter, and the repeat count runs over the prompt's sentences. The corpus stays
clean: the rendered prompts report zero findings at paragraph grain today, and the landed check
reports zero at sentence grain too — the 13 marker fragments are what the naive split would add, and
they are handled inside the check's own scope (an item's leading marker is dropped before the split,
or marker-only sentences are not counted — coder's call). If a test pins that rule, it names
`clauses.TEST_PRECONDITION`: the defect is the corpus run of
`test_no_prompt_delivers_a_span_twice` failing on today's clean definitions.

**Done-line.** `just test devpro`, then `just test dupe_sweep` (the splitter's surface), then
`just test-changed`. `just dev-check-design-deltas-applied` stays expected-failing until P4.

**One commit.**

## P3 — a store the feed cannot read fails the feed

Implements the [ARCHITECTURE Harness profiler entry](ACTIVE_DESIGN.md#harness-profiler) (its failed
feed pair) and the [Code delta's profiler entry](ACTIVE_DESIGN.md#harness-profiler-1) feed sentences.
Applies that entry's passage pair to `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

**Scope.** `devpro/profiler/pages.py`, `devpro/dashboard/server.py`,
`tests/dashboard/test_server.py`, `tests/test_devpro_profiler.py`, and the leaf above.

**Facts.**

- Signature: `read_sessions` returns `tuple[list[dict], list[str]]` (`pages.py:765-780`); the second
  element is always empty when nothing is unreadable. After the change it returns the session list
  alone. Reference search `git grep -n "read_sessions" -- devpro tests` returns, besides the def:
  `devpro/dashboard/server.py:45` (import), `:156` (`sessions, _ = read_sessions(...)`),
  `devpro/profiler/pages.py:828` (feed unpack), `:1326` (`session_for`'s unpack),
  `tests/dashboard/test_server.py:36` (import), `:517,529-530,547,554-555` (counting wrappers),
  `tests/test_devpro_profiler.py:58` (import), `:1169` (docstring), `:1184,1185` (tuple reads).
  Every one of these files is in scope.
- The unreadable mechanism: collection at `pages.py:772,777,780`, feed entries at `:841`, docstring
  `:822-826`; template text at `:1006` (feed-keys comment), `:1136` (renderer), `:1199` (branch),
  `:1205-1206` (filters). Reference search `git grep -n "unreadable" -- devpro tests` also returns,
  outside this package's scope: `devpro/dicing/cli.py`, `devpro/doccheck/*`, `devpro/kanban/server.py`,
  `devpro/runner_file.py`, the opencode resources' registry comments, `devtools/tests/test_dupe_sweep.py:255`
  — different mechanisms, untouched.
- Tests pinning the removed behavior: `test_an_unreadable_store_is_stated_in_the_feed_rather_than_failing_it`
  (`tests/dashboard/test_server.py:104`) removed whole;
  `test_the_traces_feed_answers_one_entry_per_session_and_names_unreadable_stores` (`:131`) loses its
  locked store, the `{"unreadable": ".profiler-claude"}` expectation (`:193`), the third key-tuple in
  the `:195` assertion, and the docstring sentence, its name dropping `names_unreadable_stores`;
  `test_the_served_feed_states_an_unreadable_store` (`tests/test_devpro_profiler.py:996`) removed
  whole. The `_denied` helper (`test_server.py:198`) goes with them; `_unreadable` (`:206`) stays —
  `test_a_board_file_that_cannot_be_read_is_refused_before_the_url` (`:802`) uses it.
- The 404 pin `test_the_served_feed_states_an_unreadable_store` alone carried — an unknown
  `/page/<id>` answering 404 rather than a traceback — is kept by a new test with no locked store.
  The pin's scope is a store-free or readable tree: with a locked store present, `read_sessions` now
  raises out of `session_for` before `None` is returned — that raising is the failed-feed behavior
  this package lands, not the unknown-id path. On a readable tree the unknown-id path reads the
  stores, finds no match and returns `None`. The test names `clauses.TEST_PRECONDITION`: the defect
  is an unrecorded session id rendering a traceback (500) instead of the 404, on a readable tree.
- `test_a_session_page_is_served_without_reading_the_stores_a_second_time` (`test_server.py:497`)
  **survives as-is**: it still measures a real second read — the server's dispatcher lookup and the
  page's own read both call `read_sessions` — and its counting wrappers forward whatever
  `read_sessions` returns; only their `tuple[...]` annotations loosen with the signature.
- Fact 3 of the design's review, stated so no package "fixes" it: the leaf's doctor `old:` line and
  the stores-and-rename paragraph (`harness-profiler.md:240-262`) speak of a *pre-rename* store the
  rename leaves standing — a different notion from the removed feed behavior. They stay.

**Guidance.** `pages.py` stops collecting unreadable stores and stops answering
`{unreadable: <store name>}`; a store the exact names find but cannot read is not converted into a
feed entry — the read's `OSError` propagates out of the feed's assembly, the handler answers by its
default failure answer, and the leaf's failed-feed notice is the reader's account of it.
`session_for`'s unknown-id guard before its unpack stays. `server.py:156`, `pages.py:828` and
`:1326` change with the signature. The doc-set search for the replaced wording hits
`harness-profiler.md`'s own doctor/rename lines — they stay, per the fact above; `opencode-entry.md:22`'s
"unreadable registry" is a third notion and stays.

**Done-line.** `just test devpro`, then `just test-changed`. `just dev-check-design-deltas-applied`
stays expected-failing until P4.

**One commit.**

## P4 — the agents cell, the query-carrying links, and the `devpro-` prefix drop

Implements the [ARCHITECTURE Harness profiler entry](ACTIVE_DESIGN.md#harness-profiler) (display) and
the display sentences of the [Code delta's profiler entry](ACTIVE_DESIGN.md#harness-profiler-1).
Applies that entry's passage pair to `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`. Runs
after P3: both packages edit `devpro/profiler/pages.py`.

**Scope.** `devpro/profiler/pages.py` (the `INDEX` template's script, `call_label`, `dispatcher_html`,
the tree render's label sites), `devpro/profiler/view.html` (the session page's script),
`tests/dashboard/test_server.py`, and the leaf above.

**Facts.**

- Cell-text sites: reference search `git grep -n "dispatched agent" -- devpro` returns the column head
  (`pages.py:994` — stays; `tests/test_devpro_profiler.py:901-902` pins it — stays) and the cell
  postscript (`pages.py:1106` — changes to `1 agent` / `3 agents`).
- Rendered-name sites (an agent name a page renders): reference search
  `git grep -n -e "call_label" -e "dispatcher_html" -- devpro tests` returns `call_label`
  (`pages.py:254`) called at `:289,307,493,519`, and `dispatcher_html` (`pages.py:896`) used at
  `:913`; the index's child row renders the feed's dispatcher name at `pages.py:1102`
  (`'↳ child — ' + dispatched.name`). The stored records and the feed keep the name as recorded; the
  drop is applied where a page renders the name.
- Tests pinning the rendered name: `tests/dashboard/test_server.py:536` and `:588` assert
  `— devpro-coder` in the served band; both update with the drop. The feed's dispatcher name is
  pinned as feed data at `test_server.py:191` and stays (the feed is not a page render).
- The links: the index's row links are built by the `INDEX` script's `link` helper
  (`pages.py:1026-1030`); the session page's return link's base `href` is server-written
  (`band_fills`, `pages.py:905-915`), with `return_to` staying `PROFILER_PATH`, passed by the
  dashboard server's `profiler_page` (`dashboard/server.py:159` as of planning). The session page's
  script — `devpro/profiler/view.html`'s `<script>` (`view.html:54` as of planning, read through
  `importlib.resources` by `_rendering`, `pages.py:632`) — is where the query is read and the return
  link's `href` is set: that script *is* the session page's script, so no `pages.py` site holds it.
  The change composes `location.search` into the session URL and sets the return link's `href` to
  the profiler path with that query, per the leaf's new sentences.
- The feed-keys comment (`pages.py:1006`) naming `unreadable` is P3's to fix: it is already free of
  `unreadable` when P4 runs, and P4 edits nothing there.
- Visual verification: the outcomes are on the served page. The fetch checks run through
  `tests/dashboard/conftest.py`'s `serve` fixture — the dashboard suite's own fetch vehicle, beside
  the in-scope `test_server.py`, and one fixture fetches the index (`profiler/`), a session page
  (`page/<id>`) and the feed — over a project holding a dispatching session: the fetched index's
  script must compose the query into the row links, the fetched session page's script must set the
  return link's `href` from the query, the agents cell must read `agents` postscript, and a rendered
  agent name must carry no `devpro-` prefix. `just dev-dashboard` blocks serving and is the human's
  route, not the agent's. A browser-eye check is the user's; the fetch checks are the repeatable run.

**Guidance.** The drop is one strip applied at every rendered-name site the search names, python side
and template-script side — not a rewrite of the names where they are stored. The agents cell postscript
is the leaf's examples verbatim. After this commit all four pairs are applied: run
`just dev-check-design-deltas-applied` and expect it green.

**Done-line.** `just test devpro` (view.html rides the devpro surface: `just test-changed` selects it
through `devpro/`), then `just dev-check-design-deltas-applied`, then `just dev-check-links`, then
the served-page verification above.

**One commit.**

## PR — Post-plan review

The post-plan reviewers — the coder for the changed language, `devpro-architect` (structure and the
project documents' claims about the code), and `devpro-prompt-engineer` (model-facing text changed:
none expected, seat included for the project documents) — are given the project documents and
[ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), not this plan, and review the changes and their tests against
the project's standards and fitness for purpose. Each writes their own review in the scratch
directory, one path per seat — `.devpro-temp/pr-review-<seat>.md` (for example
`.devpro-temp/pr-review-architect.md`) — so no two seats collide on one implied file name; the
session synthesizes them into `ACTIVE_PLAN_REVIEW.md`, de-duplicating and reconciling,
without waiting between the last report and the write-up. The review document is never diced. This
package's row goes `landed` in the commit that adds the review document.

**Done-line.** `just dev-check-links` (the review document is a root-level md), and the review
document present at `ACTIVE_PLAN_REVIEW.md`.

**One commit.**

## Post-plan burndown

Drafted from [ACTIVE_PLAN_REVIEW.md](ACTIVE_PLAN_REVIEW.md); the findings' IDs below are its. One
package per root-cause group, one commit each, per the section shape the owner directed: the
section holds the drafting ticket, and the items it drafted under it. R17's one-sentence leaf
reword — the only finding with no package — rides the session's commit that lands the plan. The
checkpoint gate —
`just test`, then `just sweep-python` — runs once, before each item's closing commit; each
done-line's final run is at that close.

### B0 — Post-plan burndown drafting

**Scope.** This section's items; the session is the worker.

**Facts.** The items below group the review's findings and contract gaps by root cause, each item
citing its IDs and carrying the quoted lines its executor acts on. B0's work: draft them, run their
`devpro-prompt-engineer` usability review, apply the session's one revision, and set each item's
row by its state: `dispatchable` where the review left nothing open; `drafted` where it did, the
note naming what blocks it — B2's note names the owner's choice (R4), B9's the owner's choice
(R18).

**Done-line.** `just devpro-check-plan` green with every B-row's State cell matching the sentence
above; each item then dispatches under its own row.

**One commit** — the one carrying the items' usability-reviewed form.

### B1 — sentence-grain check hardening

**Scope.** `tests/test_devpro.py`; `devtools/dupe_sweep/doc_sentences.py` if fixing R9 promotes the
splitter's name.

**Facts.**

- R1: no caller of `_double_paragraphs` runs it over the real renderings. Add the real-tree case:
  `assert _double_paragraphs(_definition_sources()) == []` — the review's probe measured 89
  prompts / 19,192 sentences, zero findings, on the clean tree.
- R2: the DISSENT expectation at `tests/test_devpro.py:2294-2299` is built by applying the
  production splitter to the same constant it tests — a splitter change moves both sides. Restore
  the constant form: the expected findings stated as literals.
- R3: the pin, stated as the failing observation: `_sentence_list(b"Run 2. Then stop.")` returns
  `["Run 2. Then stop."]`; before the fix it returns `["Run Then stop."]` — the strip at
  `tests/test_devpro.py:1926` is `re.sub(rb"\d+[.)] ", b"", unit, count=1)`, unanchored. Anchor it
  to `^`. (The review's "scope by kind" clause is vacuous under the current code — every prose
  unit is one kind — so the anchor is the fix.)
- R10: `_repeatable_sentence`'s empty case raises an unnamed `StopIteration` — name the defect in
  its raise.
- R9: tests reach the private `_split_sentences`; make it public or reach it through
  `block_sentences` — the choice is the coder's.

**Done-line.** `just test devpro`, then `just test dupe_sweep`, then `just test-changed`.

### B2 — the failed-feed answer

**Scope.** `devpro/dashboard/server.py`, `devpro/profiler/pages.py` as the answer requires;
`tests/dashboard/test_server.py`; `tests/test_devpro_profiler.py`.

**Facts.**

- The owner decided: one catch-all, not per-cause handling — "individual calls for all of them is
  giving those super low odds problems exactly the excessive concern that leads to continued
  fixation on them." Any exception a route doesn't anticipate answers the failure status with the
  exception's text as its error body; the dashboard is a `127.0.0.1` development surface, so the
  text is for an operator who could read the server log anyway.
- The pin that moves: `test_a_store_the_feed_cannot_read_fails_the_feed` asserts
  `pytest.raises(RemoteDisconnected)` today; under the catch-all it asserts the failure status and
  an error body naming the cause.
- The leaf's "a failed feed names itself in an in-page notice" becomes true as written — the
  page's `fetch` reads the error body and the notice renders it. No unreadable-store special case
  returns, and no leaf wording changes.
- R5: `devpro/dashboard/server.py:19-20`'s endpoint-map docstring says "one per store that could
  not be read" — reword to what the feed answers now.

**Done-line.** `just test devpro`, then `just test-changed`.

### B3 — sweep line numbers, helper dedup

**Scope.** `devtools/dupe_sweep/definition_text.py`, `devtools/dupe_sweep/doc_sentences.py`,
`devtools/tests/test_dupe_sweep.py`.

**Facts.**

- R6: multi-line literals report every sentence at the literal's opening line. Number them as
  `_docstrings` does (`doc_sentences.py:60`'s `enumerate(..., start=first_line)` pattern), and
  correct the docstring's overclaim at `definition_text.py:6-7` ("a sentence's line is the
  literal's line, which is the line the reader opens the module at").
- R11: `docstring_nodes` (`doc_sentences.py:78`) re-implements `_docstrings`' detection
  (`:68`, `ast.get_docstring(clean=True)`). One helper decides; the shape that survives is the one
  `test_a_literal_is_rejoined_across_its_hard_wrap_and_split_like_a_docstring` needs — probe the
  merge both ways if the tests disagree.

**Done-line.** `just test dupe_sweep`, then `just sweep-python` (advisory — read once, its count
move is not a done-line), then `just test-changed`.

### B4 — the prefix's one source and its tool gate

**Scope.** `devpro/profiler/pages.py`, `devpro/profiler/view.html`,
`tests/dashboard/test_server.py`, `tests/test_devpro_profiler.py`.

**Facts.**

- R15: the drop is unconditional (`rendered_name`, `pages.py:258-268`), so a Bash call whose
  recorded head carries the prefix renders misstated — gate the drop on the Agent tool. The pins
  that move: `test_a_rendered_call_label_drops_the_set_prefix`'s Bash case
  (`tests/test_devpro_profiler.py:1189`, `call_label("Bash", "devpro-tool")`) flips to
  `"devpro-tool (Bash)"`; the served band pin at `tests/dashboard/test_server.py:654` stays — it is
  an Agent call. `view.html:288`'s grouped-skills label renders raw names — render it through
  `shownName` like the other sites.
- R7: settled in revision — the equality pin, the smaller change: pin the four spellings equal
  (the sites at `tests/dashboard/test_server.py:610,612,655`, `pages.py:1031,1105`,
  `view.html:86`), rather than a render-time constant substitution.
- R13: `shownName` (`view.html:86`) returns `undefined` for a missing name — return `''`.
- R12 is struck: `view.html:90` already composes `back.pathname + location.search` — verified in
  this revision.

**Done-line.** `just test devpro`, then `just lint`, then `just test-changed`.

### B5 — document wording

**Scope.** `PROJECT_DOCS/ARCHITECTURE/repo-layout.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

**Facts.**

- R16: `repo-layout.md`'s `dupe_sweep/` row says "the string literals the trees carry" — narrow to
  the three definition areas the code reads (`definition_text.py`'s `DEFINITION_TEXT_PREFIXES`).
- R22: `harness-profiler.md`'s lines 105–110 carry ragged wrapping from P4's hand edit — reflow to
  the leaf's column. R17's rewrite is B2's; B5 reflows only what B2 leaves.

**Done-line.** `just test-changed` — the docs surface is this package's only work.

### B6 — pin honesty

**Scope.** `tests/dashboard/test_server.py`, `tests/test_devpro_profiler.py`.

**Facts.**

- R8: three inline-script substring assertions in three tests —
  `test_the_indexs_row_links_and_the_session_pages_way_back_carry_the_query`
  (`tests/dashboard/test_server.py:610,612`), `test_the_agents_cell_reads_the_count_as_agents`
  (`:626`), and `test_a_rendered_agent_name_drops_the_set_prefix` (`:655`). R14: that last test's
  docstring claims the served page while the assertion byte-matches template source. The fix is
  the naming: each docstring says plainly "a form pin — the served-page fetch checks are the
  effect witnesses, the browser-eye check the witness for the branches the probes do not
  exercise." The pins stay (house pattern).

**Done-line.** `just test devpro`, then `just test-changed`.

### B7 — CONVENTIONS lines

**Scope.** `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-by-searching-the-doc-set.md`
(edit); a new leaf under `PROJECT_DOCS/CONVENTIONS/planning-and-execution/` with its index and
entry-point lines (the new-leaf rules are in `project-documents.md`);
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/scratch-home-for-tests-and-recipes.md`
(title widened); `pyproject.toml`.

**Facts.**

- G1: the new leaf's rule — "A repository-wide check's own case set includes one run over the real
  tree it polices; a fixture-only case leaves the check unexercised on its inputs."
- G2: the search-of-doc-set leaf gains the synonym requirement — R5's stale docstring survived a
  mandated search because it said "could not be read" where the search said "unreadable".
- R20: the widened scratch leaf's rule — "a test run writes its cache under the scratch directory,
  not the project root" — is carried by the code too: `pyproject.toml`'s
  `[tool.pytest.ini_options]` sets the cache dir under `.devpro-temp/`, so `just test` stops
  leaving `.pytest_cache` at the root.
- R21: the same leaf states the cleanup practice — a package's scratch under `.devpro-temp/` is
  the session's to delete when the plan lands; a practice the session keeps, not a control a tool
  enforces.

**Done-line.** `just test` (the cache dir moves under the scratch and the suite still passes), then
`just test-changed`.

### B8 — the cli docstrings' one home

**Scope.** `devpro/profiler/cli.py`, `devpro/dashboard/cli.py`.

**Facts.** R19: the two module docstrings are 90–100% duplicated — the sweep's live candidate. The
duplicated portion is the argparse-surface sentence; its one home is `devpro/cli.py`'s own
docstring, and each module's docstring says only the verb it adds (the verbs differ — sharing one
text between the two modules is not the fix). Evidence: the sweep's report run before and after,
recorded in the commit body — the pair is gone after. Evidence, not gate.

**Done-line.** `just test devpro`, then `just test-changed`.

### B9 — the families' anchor prose: in the literals corpus or recorded as out

**Scope.** `devtools/dupe_sweep/definition_text.py` (`DEFINITION_TEXT_PREFIXES`),
`PROJECT_DOCS/ARCHITECTURE/repo-layout.md` (the `dupe_sweep/` row only, if extended).

**Facts.** R18: `devpro/families/gemma_4.py`'s anchor paragraph is rendered prose — the same kind
of text the corpus reads — outside `DEFINITION_TEXT_PREFIXES`. The owner chooses:

- (a) extend the prefixes to the families: the sweep's header scope line (`passes.py:42-45`) and
  the repo-layout row move with it;
- (b) record the hole as intended: a line on `definition_text.py`'s docstring saying the families'
  anchors are outside the corpus by decision, so the next reader does not rediscover it.

**Done-line.** `just test dupe_sweep`, then `just sweep-python` (advisory), then `just test-changed`.
