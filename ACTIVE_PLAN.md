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
| PR | in progress | expert | review of what shipped, written to `ACTIVE_PLAN_REVIEW.md` |
| PB | drafted | expert | fixes drafted from the review document |

P1–P4 and PR are `dispatchable` as of the PE usability review and the architect revision that applied
it — the revision's checks clean (`check-plan`, `check-links`). PB stays `drafted`: its work list is
drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands, and gets its own usability
review before it is `dispatchable`.

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

## PB — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands. The burndown's work list
replaces this paragraph where it stands, and gets `devpro-prompt-engineer` usability review then the
session's revision before its state is set `dispatchable`.

**Done-line.** Per its drafted items, each naming the runner targets that check what it changes.

**One commit** per burndown item, each item a package of its own at drafting time.
