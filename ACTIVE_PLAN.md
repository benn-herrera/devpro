# devpro absorbs its tooling — the UX pass: the dashboard's decided layout

Design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md#shipped-files--the-docdicer-package-retires-its-runner-shortcuts-return-the-profilers-and-dashboards-decisions-stages-2-4)
— the Shipped files entry's one pending pair, whose `becomes` (ACTIVE_DESIGN.md:400-448) states
the whole decided target. This plan builds what that pair states: the board-first landing, the
persistent top nav, the profiler view's frame band and legend, the one shared presentation layer,
and the profiler page's re-style to the kanban presentation. The technical base it rests on landed
(`ddf0e5f` and the stage-3 landing commits) and the phosphor-identity amendment is in the design
(`89f80b5`). DRAFT for the user's approval: nothing dispatches from this file yet — every state
below is `drafted`, and the PE review and revision round come first.

**Decision this plan lands** (strike it in approval where wrong): the dashboard keeps its two
panels and their routes; the pass re-styles what serves. The board panel stays at `/board/` —
SPEC.md's Kanban leaf pins it there
(PROJECT_DOCS/SPEC/dicing/kanban.md:3-4) and the pending pair does not move it — and the root
answers a redirect to it, so opening the dashboard's URL shows the board. The traces panel becomes
the profiler view, reached from the nav, at `/profiler/`; `/page/<session-id>` deep links are
intact. One package builds it whole: there is no staging boundary inside the pass, no verb or
surface retires, and the record lands with the code that makes it true.

## Status

| Package | State | Rating | Lifetime | Work |
| --- | --- | --- | --- | --- |
| U1 | landed | expert | shipped | the UX pass: the shared layer in `devpro/dicing/kanban/assets/board.css`, the nav, the board-first landing, the profiler view's frame band and legend, the profiler re-style, and the pending pair's application |
| PR | landed | expert | shipped | Post-plan review |
| PB | drafted: the PE review and revision of its work list remain before it is dispatchable | expert | shipped | Post-plan burndown |

## U1 — the UX pass: the decided layout, one presentation layer, the record

Lifetime: shipped. One commit closes it — the shared layer, both panels' re-style, the
band and the record are one presentation change with no shippable middle state.

**What does not change.** No verb, no route and no endpoint is added beyond the layout's own
needs — the nav's profiler link (the `/profiler/` index) and the frame band's return control,
ordinary navigation, no inner frames. The board panel is `devpro.dicing.kanban.server`'s serve
surface and the traces panel `devpro.profiler.pages`' rendering, exactly as the dashboard module
docstring states (devpro/dashboard/server.py:1-7); no rendering logic moves between the packages.
The board's payload, moves, served documents, host guard and CSP are untouched. The tests that
pin them keep passing: the board-panel suites unedited (tests/dashboard/test_server.py:123-135,
:138-159, :177-216; tests/dicing/test_server.py:138-216, :490-513), and the host guard
(tests/dashboard/test_server.py:219-249) unedited except its `id="root"` case (:225), re-expected
at `302` — its assertion pins the status only, and a `302` still answers the dashboard's own
host. Three tests the root redirect moves are not unedited; the test scope below names their
retargeting: the unreadable-store test (:63-81), the outside-it command test (:339-368), and the
CSP test (:252-272).

**The URL arrangement — the executor call, stated.** The root `/` answers `302` with
`Location: /board/`, and the traces index answers at `/profiler/` (trailing slash, the board
panel's convention). Reason: the board must keep serving from `/board/` with its assets named
relative to the page (assets/index.html:7 `<link rel="stylesheet" href="board.css">`, :22
`<script src="board.js"></script>`) and its API root-absolute (board.js:419, :422, :492, :524) —
serving the board page at `/` instead would re-path the page's asset resolution, its API and the
served documents to escape the board prefix. A redirect is the boring mechanism: one answer on the
dashboard's own root route (server.py:147-148's branch becomes the redirect; the index moves to a
`/profiler/` branch beside `/page/`), and the board panel's handler is not touched. The traces
index stays read per request (traces_index, server.py:105-111) — a session recorded a moment ago
is still listed by the next page loaded
(PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:137-138).

**The shared presentation layer — the executor call, stated.** The layer lives where the design
puts it: the board's own stylesheet, `devpro/dicing/kanban/assets/board.css`, extended with the
phosphor identity — the brand, active-view and inactive-view values in both motifs, the nav
grammar and the scanline utility — superseding the board's blue `--accent` (board.css:9, :22 — the board's stylesheet defines no
`--accent-dim`) and superseding the ux-pass mockups' light-mode dim value — `--accent-dim` lives
in `.devpro-temp/ux-pass/` (`#b795ba`), not in `board.css`
(the pair's `becomes` states the values and the grammar; this plan does not restate them). The
board's surfaces keep the board's own variable system, `board.css`'s `:root` and its
`prefers-color-scheme` block (board.css:1-25), as the design's `becomes` says; the accent values
and the two-motif accent map ride the same file.

The profiler's pages consume it by the render reading the file once and inlining its text —
`pages.py` already reads its own template through `importlib.resources` (pages.py:538), so the
render reads the shared source the same way and inlines it where the page's `<style>` sits. The
traces index (the `INDEX` template, pages.py:707-723) is inlined the same way. Reason: the
standalone render's page must stay self-contained — view.html:2, "Self-contained: no network,
works from file://" — so linking is not an option on the profiler side; inlining one source keeps
that contract, needs no new route (the board panel's asset serving at `/board/<file>` is the only
file-serving the server has), and gives the standalone page, the served page and the index the
identical palette from the identical file. A new shared file was weighed and rejected: the board
would carry two stylesheets for no third consumer, and the profiler would still inline — the
consumption modes do not change, only the count of files. The board's own component rules (#board,
.column, .card, .separator) may be scoped by the executor so their selectors cannot reach the
profiler page's DOM; the source stays one file either way.

**The legend's mechanism — the implementation site, verified.** The legend today is the template's
alone: view.html:42-50 carries the whole how-to-read block (the summary, the prose paragraph and
the symbols list), and `grep -rn "How to read" devpro tests README.md PROJECT_DOCS` returns
view.html:42 and nothing else — one copy, no pin on its text. The rendering side becomes its one
home: `devpro/profiler/pages.py` holds the legend once as a module constant (its markup
included), `view.html` carries a slot in its place — the `DATA_SLOT` pattern pages.py:49 and
:539 already uses — and `render_html` fills the slot from the constant on every call. The choice
that keeps the served page never-twice is stated here, not left an executor call: the dashboard's
`page_of` path (server.py:113-115) runs the same `render_html` with no suppressing flag, so the
rendered body carries the injected legend, and the band splice — the one site that decorates —
removes that copy from the body and carries the constant in the band instead. Two carriers, one
source: the standalone render's page carries the legend injected; the dashboard's band carries it
on the served pages. A served page never shows the legend twice because the splice is the single
place that holds both copies in hand, and it cannot leave one behind in the body.

**The frame band.** The dashboard decorates the profiler view's pages — the `/profiler/` index and
each `/page/<session-id>` page — with the band, spliced into the served page the way
`with_board_link` splices the board-link line today (server.py:38, :46-49): the nav (the `devpro`
brand, the view names `kanban` and `profiler`, the active view's name per the nav grammar), the
live/idle state indicator, the stop control when live, and — at the top of the band — the
how-to-read legend. The band persists across drill-down: the session page's band carries the
return-to-list control, its label `Return to list`, linking to `/profiler/` — the one-string
revisable change the design names as the pass's second executor call. Drill-down stays ordinary
page navigation; no inner-frame mechanic is added. The band's stop control posts the board
panel's existing `/api/stop` (tests/dashboard/test_server.py:162-174 pins the endpoint's answer);
the band's liveness source is the executor's call within one constraint — no new endpoint for it,
and no served page starts its own server. On the board view the server's elements are the board
page's existing `#connection` and `#stop` (assets/index.html:14-15, board.js:476-520), restyled
to the same grammar — the board view carries no legend.

**The board page's nav.** The nav's markup lands in `devpro/dicing/kanban/assets/index.html`,
its grammar in `board.css`; the brand wordmark monospace, heavier and about 15% larger than the
view names, the active view in the brand color at 80% brightness and heavier weight, the inactive
view a lifted gray — the pair's `becomes` states the grammar and the values. The monogram's
scanlines are deliberate, and the scanline treatment's placement (chrome, nav or frame band,
never a card surface) is the pass's executor call, as the design states. The visual reference is
the record's own: the rendered mockups in `.devpro-temp/ux-pass/` (cited by the record, their
contents not consistency-checked). The trace diagram's own content — the context palette
`--c0`…`--c7`, the sequence and tree rendering — stays the page's own: the identity restyles the
chrome, not the diagram's data colors.

**Scope — code.** Edited: `devpro/dicing/kanban/assets/board.css` (the identity, the nav grammar,
the scanline utility), `devpro/dicing/kanban/assets/index.html` (the nav markup, no behavior
change — board.js's wiring is untouched), `devpro/profiler/view.html` (the legend's slot, no
second copy), `devpro/profiler/pages.py` (the legend's home and the render's slot-filling; the
shared source read and inlined into `render_html` and `index_html`), `devpro/dashboard/server.py`
(the root redirect, the `/profiler/` route, `with_board_link` replaced wholesale by the band
splice), and the tests named below. Unchanged: the kanban server, the board model and moves, the
profiler's capture and `tree` verb, the CSP and host guard, the API routes.

**Scope — the tests that pin what changes.** The tests below state behavior the decided target
supersedes; each is updated in the same change:
- `test_the_root_is_the_traces_index_with_the_board_link_before_its_close`
  (tests/dashboard/test_server.py:30) — rewritten for the redirect and the link line's wholesale
  replacement: a root still serving the trace index inverts the decided board-first landing.
- `test_the_traces_panel_serves_its_index_and_its_pages` (:45) — retargeted to `/profiler/`.
- tests/test_devpro_profiler.py:545, :570 and :589 — the three `_serve` index tests fetch the
  root as the trace index today; each fetches `/profiler/` instead. The row and unreadable-store
  contracts they pin are untouched.
- `test_the_served_page_is_the_html_the_file_flow_writes` (tests/test_devpro_profiler.py:613) —
  rewritten: the served page's page data (`const D = …`) is the file flow's, byte for byte, the
  deep links intact, and the band is the served page's own addition; the standalone render stays
  the bytes `tree --format html` prints. The old whole-bytes pin would fail on the band the
  decided target adds — that is the stated behavior change.
- `test_every_page_answer_forbids_sniffing_and_restricts_its_sources`
  (tests/dashboard/test_server.py:252) — extended to the new pages' answers; its root fetch
  re-expects `302` in place of the `200` it pins today (:262, fetched through the no-follow
  `raw`), the redirect answer carrying the same policy headers (the executor keeps one policy
  for both panels' pages, server.py:39-41).
- `test_the_board_page_and_the_files_it_names_resolve_under_the_board_path`
  (:109) and the host-guard (its `id="root"` case excepted, re-expected above), payload, moves
  and documents tests — no edit: they compare served bytes to the assets on disk or pin panel
  behavior the pass does not touch.

**New tests, each named for its defect** (devpro/clauses.py:170 — the run that fails under the
defect, before the change):
- The `/profiler/` index carries the band: the legend's text present exactly once, the nav present
  with `profiler` active and `kanban` linking `/board/`. Defect: a band that drops the legend
  loses the view's how-to-read; one that shows it twice breaks one home, two carriers.
- The `/page/<id>` page carries the band's legend and the return control linking `/profiler/`, and
  its body carries no second legend. Defect: drill-down with no way back; a doubled legend.
- The standalone render's page carries the injected legend and no nav. Defect: the render's own
  carrier losing the legend the design assigns it.
- One-source check: the standalone render and the traces index each carry the shared source's own
  text (a substring of `board.css`'s brand values in the page's style). Defect: a second palette —
  the re-style made as a reskin the design forbids.

**Scope — the record.** The pending pair applies to
PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:99-103: the `from` region is the smallest
anchor the pair names ("the tool's `serve` subcommand renders … reachable only from the"), the
`becomes` (ACTIVE_DESIGN.md:408-447) is applied verbatim per the design application form, and the
region's continuation — "machine that runs the server. Six hook entries …" — is the anchor both
applications leave standing, the pair re-anchoring as the chain rule states (ACTIVE_DESIGN.md:40-46).
With the pair applied, the design's pending mark (ACTIVE_DESIGN.md:371) is resolved for it.
PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:53-57 — "The URL's root is the traces
panel, the landing page … a link line under the index opens the board panel" — the code this
package lands supersedes; the record updates it in the change that lands it: the root the board's
landing, the traces panel the profiler view at `/profiler/`, the band replacing the link line.
The bind, unreadable-store, calls-only-page and stop statements in the same section are untouched
— this package changes none of them.

**Facts.**
- `git log --oneline -3` as of HEAD, re-run at this revision → `d3ba2de` (this plan's own
  commit), `4cd3953` (the profiler launcher's), `89f80b5` (the phosphor identity); stage 3's
  landing `ddf0e5f` stands one below the three. The base this plan rests on.
- The pending mark: ACTIVE_DESIGN.md:371 — "the dashboard pair waits for the presentation pass,
  its layout the user's decided target — the active plan's staging boundary is the record of that
  staging." The pair's `becomes` is ACTIVE_DESIGN.md:400-448.
- The legend's only copy today: `grep -rn "How to read" devpro tests README.md PROJECT_DOCS` →
  devpro/profiler/view.html:42 alone. Nothing pins its text.
- The slot mechanism's precedent: pages.py:49 `DATA_SLOT = "/*DATA*/null"`, filled by
  `render_html` at :539; the template read at :538 through `importlib.resources`.
- The board-link line's incumbent: server.py:38 `BOARD_LINK`, spliced by `with_board_link`
  (:46-49), asserted by tests/dashboard/test_server.py:30-42 — replaced wholesale by the band.
- The board panel is the only file-serving surface: the dashboard's handler routes everything not
  `/profiler/`, `/page/` or the root to the board panel's handler (server.py:142-158), which
  resolves files beside the board page — the shared source must live in `devpro/dicing/kanban/assets/`
  to be linkable by the board and readable by the render.
- The board page's API paths: board.js:419 `/api/to-design`, :422 `/api/to-roadmap`, :492
  `/api/board`, :524 `/api/stop` — root-absolute, served by the dashboard at the root paths the
  board panel answers (server.py:16-17); the pass re-paths nothing.
- The stop endpoint's contract is pinned: `test_the_stops_path_answers_and_ends_the_serving`
  (tests/dashboard/test_server.py:162-174) — the band's stop control rides it, unedited.
- The roadmap ticket "Browser-driven visual verification" (ROADMAP.md:122-130) is not this plan's
  work: it needs a browser driver and a dependency decision of its own, and rides with the UX pass
  as a roadmap ticket. This plan's tests are fetch-level and DOM-level; the suite's fixtures are
  real recorded traces rendered through every served path, as the dashboard suite's are today.
- `TEST_PRECONDITION` (devpro/clauses.py:170) governs the new tests: each names its defect and the
  run that fails under it, as the package states above.

**Done-line.** `just test devpro`, `just lint`, `just dev-check-links`, `just test docs`, and
`just dev-check-design-deltas-applied` at landing state — run once, at the package's end, the
last over the pair this package applies.

## PR — Post-plan review

Lifetime: shipped. One commit closes it — the one that adds the review document.

The reviewers receive the project documents and the design, not this plan, and review the changes
and their tests against the project's standards and fitness for purpose: the coder seat for the
changed Python, `devpro-architect` for the structure and the project documents' claims about the
code, `devpro-tech-writer` for the human-facing pages' text, and `devpro-prompt-engineer` for the
model-facing texts — the how-to-read legend's rendered text included, it being a durable artifact
a model's page carries. The session synthesizes the reviews into `ACTIVE_PLAN_REVIEW.md` without
waiting for an approval between the last report and the write-up. The review document is deleted
in the commit that lands the plan.

**Done-line.** `just dev-check-links` — the review document is a tracked top-level markdown file
its links must resolve in; no other target checks it.

## PB — Post-plan burndown

Lifetime: shipped. One commit closes it.

Drafted from `ACTIVE_PLAN_REVIEW.md`. The findings group into five root causes; the review's IDs
are cited so no seat's report is lost.

**1. The record-code boundary, reconciled** (R1, R9, R6): the landing changed the surface's
arrangement and the records were not reconciled in the same edit. R1 the user has decided: the
profiler view's silence is a bug — the accepted design's sentence governs, and the code comes to
it. The profiler view's chrome gains the live/idle indicator and the stop, the shared nav
carrying both on every view; the mechanism for a page that does not long-poll: the shared chrome
polls a cheap state endpoint the dashboard answers (`GET /api/state`), the indicator reading the
poll's answer as the board's reads its own — true where the server is serving, idle where not —
and the stop posting the existing `/api/stop`. Pinned by tests naming their defects
(the test-precondition clause). R6 — the 302's `Location` absolute
(`devpro/dashboard/server.py:182`), matching the printed URL and the `loopback()` pin; R9 —
`harness-profiler.md:54`'s "in its header" line to the nav, which R1's answer now places on both
views.

**2. The mechanisms implemented past their statements** (R2, R7, R14): the standalone index's
`css=` substitution key is dead (`pages.py:756` — `INDEX` holds no placeholder, the served CSS
arrives only through `with_frame`'s slot) while the docstring (`:748`) and the ARCHITECTURE leaf
(`harness-profiler.md:49-51`) state the slot mechanism. The splices' one dependence is the
`LEGEND` removal preceding the **band** splice — `band_html` embeds the legend verbatim
(`server.py:74`) and the band splice is the chain's last replace (`pages.py:767`) — while the CSS
splice's target (`/*STYLE*/`) is disjoint from both, its order unobservable. Fix: the mechanism
made true or the statements rewritten — the dead key deleted and the docstring and leaf stating
the real dependence, with the legend's removal order documented or the operations made
independent; the standalone-path legend check added (R12) so the mechanism's pin covers both
carriers. And R14, the serve half of the same promise: the dashboard's session page serves CSS
differing from the file's (11,594 chars served against `SHARED_CSS`'s 8,170) with an empty
legend, while identical bytes from disk render styled — the page the dashboard serves is not the
page the file flow writes; the divergence named, closed, and pinned so the serve path and the
file path render the same page.

**3. The chrome's own defects** (R3, R4, R5, R11): the header-scoped rules that did not follow
the nav. `#connection`'s `margin-left: auto` re-homed to `.nav-server` (`board.css:150`), the
stale "in the page's header" comment out, the missing `.nav-server`/`.nav-stop` rules written;
the stop's post-`POST` focus given a `:focus-visible` home (`assets/index.html:22`); the body
layout rules scoped to the board (`board.css:111-119`) so the profiler page's template padding
and diagram panel stand; the dead `--accent-dim` deleted from both motifs.

**4. The launcher's leaf brought current** (R8): `harness-profiler.md`'s finder lines (`:20`,
`:26-31`) state the one-shot finder — extended `PATH`, one `command -v`, one probe, no
`HP_DEVPRO` — and its doctor statement (`:179-181`) matches `devpro_executable()`'s
executability check.

**5. Vocabulary and test form** (R10, R13, R15, R16, R17, R18): the half-renamed docstrings ("traces panel" at
`pages.py:2`, `dashboard/__init__.py:4`, `server.py:5`, `server.py:100`,
`tests/test_devpro_profiler.py:133`) brought to the profiler-view vocabulary; `view.html`'s
diagram color map and the leaf's "no palette of its own" reconciled; the two stale "pending"
notes in `ACTIVE_DESIGN.md:371` and `:494` corrected; the record's monogram sentence brought to
what ships; the form pins and duplicate test (`test_devpro_profiler.py:655`, `:659`, `:673`) and
the word-count assertions (`test_server.py:294`, `:308`) cut to behavior. R15 — `view.html:47`'s
literal `${0}` in every session page's toolbar out, its placeholder filled or the line removed,
pinned. R16 — the records' stale sites: `repo-layout.md:16`'s `/`-as-traces-route line,
`harness-profiler.md:138` and `:164`'s "traces panel" remnants, the layer paragraph's statement
that the board links the shared layer while the profiler pages inline it, and the checkout's
installed skill trees re-rendered by the next install. R17 — `images/kanban.webp` retaken or
re-captioned to the current `/board/` (the Firefox-headless caveat recorded: the drawn board is
script-only, the baseline shot shows its shell). R18 — `just dev-dashboard` passing `--port`
through, the nav labels mapped to the prose's "board panel"/"profiler view" at first use, and
`recipes.md:35-38`'s pre-include-line paragraph brought current.

**Done-line.** `just test devpro`, then `just lint`, then `just dev-check-links`, then `just
test docs`, then `just dev-check-design-deltas-applied` — run once, at the package's end.
