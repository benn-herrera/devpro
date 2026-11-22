# The pages assemble once: plan

Cut from [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — *The pages assemble once: the layer linked, the deco
in the page*. The plan cites the design's entries and does not restate them. No release: this is not
release work; what ships is each package's own landing — a package that lands leaves its behavior in
the working tree, in the served pages and the rendered definitions, with no version to cut.

Entries cited, each by its heading anchor:

- [Install — Harness profiler](ACTIVE_DESIGN.md#install--harness-profiler) under the design's
  `## ARCHITECTURE delta` — six passage pairs on `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.
- [Subsystem Map](ACTIVE_DESIGN.md#subsystem-map) under `## ARCHITECTURE delta` — the tree's drawing
  stated as the code's rule, on `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md`.
- [Deployed surfaces — Shipped files](ACTIVE_DESIGN.md#deployed-surfaces--shipped-files) under
  `## Code delta` — the zebra fix held to the SPEC zebra sentence.
- [Install — Harness profiler](ACTIVE_DESIGN.md#install--harness-profiler) under the design's
  `## Code delta` — the assembly rework and the client-gone error-path fix.
- [Subsystem Map](ACTIVE_DESIGN.md#subsystem-map) under `## Code delta` — the show-profile `_BODY`
  correction.

Every code fact the design states was verified this session and is quoted where a package acts on it.

## Sequencing

Packages land in the order below. The dependencies that order them:

- `strict-fill` precedes `deco-into-templates`: the strict fill is the mechanism the reworked
  assembly runs through, and the template deco's byte pin is the evidence the design names for
  retiring `with_frame` — the retirement follows the evidence, never before it.
- `deco-into-templates` precedes `traces-feed`: the feed rework rebuilds the index whose template
  deco the earlier package settles, so the index is edited once, not twice.
- `quiet-client-gone` and `plain-tree-skill` are independent of `strict-fill`–`traces-feed` and may
  land at any point before `apply-arch-deltas`; they are placed last-before-docs so the leaves as
  amended are true when the deltas are applied.
- `apply-arch-deltas` is last: both ARCHITECTURE passage pairs are applied only when the code they
  describe stands, and `just dev-check-design-deltas-applied` verifies them byte-exact.

Each package closes in exactly one commit. Every landing commit is a checkpoint and runs the
checkpoint gate: bound at [the-gates.md](PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md)
as `just test`, then `just sweep-python`, with the sweep's list read and its pairs named per
[a-checkpoint-includes-the-sweep.md](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-checkpoint-includes-the-sweep.md).
Where a package's own done-line names a narrower target, the checkpoint gate runs at the commit as
well — the done-line is the package's check, the gate is the commit's.

Rating sets the dispatch's `model` per the-gates.md's step-down application; `mechanical` packages
run at the step-down model.

Every package below is **shipped**: intended lifetime, lands and stays.

## Packages

Each package's report states the done-line's result as
`<recipe> < /dev/null > .devpro-temp/<package>-<target>.log 2>&1`, quotes the first failure from the
log on failure, and leaves the log unread on pass.

### zebra-variable — the zebra's own tone in the shared layer

Cites [Deployed surfaces — Shipped files](ACTIVE_DESIGN.md#deployed-surfaces--shipped-files) under
`## Code delta`. Lifetime: shipped.

**Scope.** Two files:

- `devpro/dicing/kanban/assets/board.css`: add one variable, `--zebra`, defined as `#e7e7eb` in
  `:root` (the layer's own light `--column` value, `board.css:16` — `--column: #e7e7eb;`) and
  `#2e2e35` in the dark block. `--column` is untouched — the dark `--column: #232328;`
  (`board.css:32`) stays, as does `--card: #2e2e34` (`board.css:33`): the board's deco — frame
  band, columns — keeps `#232328`, so the cards' surface distinction is untouched.
- `devpro/profiler/pages.py`: the index template's two zebra rules reference `var(--zebra)` —
  line 934 `tr:nth-child(odd) td { background: var(--column); }` becomes
  `var(--zebra)`, and line 935 `@media (prefers-color-scheme: dark) { tr:nth-child(odd) td { background: #191c22; } }`
  becomes `var(--zebra)`; the dark literal `#191c22` retires. The standalone index carries no layer
  and is not this package's to carry; `--zebra` reaches the served page through the link `with_frame`
  writes. The template's own comment block at `pages.py:906-911` — the zebra's tones no slot, their
  carrier the template's motif pair — is updated by this package: its dark-value statement reads
  `--zebra` after it.

**Facts and searches.** `git grep -n "191c22" -- devpro tests` returns two hits:
`devpro/profiler/pages.py:935` and `tests/test_devpro_profiler.py:724` — the literal and its pin.
The dark values' distance — the user's criterion of twice the standing chromatic distance — is the
design's `## Code delta` entry's, cited above and not restated here.

**Tests.** `tests/test_devpro_profiler.py:722-725` pins the template's zebra lines, the dark rule by
the literal regex `background: #191c22` — updating that assertion to `var\(--zebra\)` is in this
package's scope. No other test or fixture pins the zebra (`git grep -n "zebra" -- tests` finds the
pin and no other).

**Done-line.** `just test devpro tests/test_devpro_profiler.py` — the pin and the suite around it,
run once at the package's end.

### strict-fill — one strict fill through which every fill runs

Cites [Install — Harness profiler](ACTIVE_DESIGN.md#install--harness-profiler) under
`## ARCHITECTURE delta` (the strict-fill passage pair) and under `## Code delta`. Lifetime: shipped.

**Scope.** `devpro/profiler/pages.py`: one strict fill — `strict_fill(text, fills)` — one function
every fill the profiler's assembly makes runs through, handed every template `pages.py` reads and
fills, `view.html` and the `INDEX` template. Its construction, both shapes the templates carry:

- `$name`-shaped slots run through `string.Template.substitute`, which raises on a `$name` the text
  carries with no key. `index_html` already runs through `string.Template.substitute`
  (`pages.py:863-867`); routing it through the strict fill renames its slots — `unreadable`, `rows`
  and `ZEBRA_MARKS`' four (`class_opencode`, `class_claude`, `opencode`, `claude`) — to the fill's
  vocabulary; the rename is in this package's scope.
- the literal marks go through an exact-mark map keyed by mark constant: the render's three —
  `DATA_SLOT` (`/*DATA*/null`), `CSS_SLOT` (`/*STYLE*/`), `LEGEND_SLOT` (`<!--LEGEND-->`,
  `pages.py:52-54`) — and, at this package, the serve marks `with_frame` fills — `NAV_MARK`,
  `BAND_MARK`, `DECO_MARK` (`pages.py:901-903`) — which retire with `with_frame` in
  `deco-into-templates`. Each mapping key's mark is replaced once by its value.

The fill raises — `KeyError`-family — where a mark is unknown to the mapping or stands in the
output: a `$name` the text carries with no key (`substitute`'s own raise); a fills key whose mark
the text does not carry — plain `substitute` would silently ignore an unused key, and the silent
no-op `str.replace` at `pages.py:609-610` is the defect this closes; a filled mark still standing in
the filled output. A literal mark the text carries that the call's mapping does not fill is not a
raise — the assembly's later stage fills it through the same strict fill (the index's `/*STYLE*/`
stands until `with_frame` fills it at serve time); the checks read the mapping's keys.

The fills routed through it at this package: `render_html`'s three replaces at `pages.py:609-610`
become the map's `DATA_SLOT`, `CSS_SLOT` and `LEGEND_SLOT` entries; `index_html`'s
`string.Template(INDEX).substitute(...)` at `pages.py:863-867` becomes `strict_fill(INDEX, ...)`;
`with_frame`'s three serve-mark replaces at `pages.py:893` become the map's `NAV_MARK`, `BAND_MARK`
and `DECO_MARK` entries — its layer-carriage swap (`:887-891`) and legend removal (`:892`) are text
surgery, not mark fills, and stand as they are until `deco-into-templates` retires the mechanism.
`git grep -n "string.Template" -- devpro tests` returns one hit: `pages.py:863`.

**Refactor discipline.** At this package the fill is a refactor: the byte pins
(`tests/test_devpro_profiler.py:854-916`, `tests/dashboard/test_server.py:331-351`) and the
unreadable-row path (`tests/dashboard/test_server.py:91-109`, in the run) stay green untouched —
that run is the observation of the unchanged output — at this package, before
`deco-into-templates` edits the deco those assertions count.

**Test added.** A test in `tests/test_devpro_profiler.py`,
`test_the_strict_fill_refuses_unknown_and_unfilled_marks_and_leaves_none_standing`, walks what the
fill is handed — `view.html` and the `INDEX` template — and asserts: (a) `strict_fill(view_text,
fills)` and `index_html(root)` both raise where a mark is removed from the text under test; (b) the
rendered session page carries no `/*STYLE*/`, `<!--LEGEND-->` or `/*DATA*/null` standing, and the
served page and served index carry no `/*STYLE*/`, `<!--NAV-->`, `<!--BAND-->`, `<!--DECO-->` or
`$rows` standing — the serve marks standing in the standalone render are `with_frame`'s to fill
through the same strict fill, and no assertion stands on them here. Defect it fails on before the
change: a template whose text no longer names a mark the fill is told to fill leaves the old mark
standing in the rendered page — the silent no-op `str.replace` at `pages.py:609-610`. The run that
fails before and passes after:
`just test devpro tests/test_devpro_profiler.py::test_the_strict_fill_refuses_unknown_and_unfilled_marks_and_leaves_none_standing`
— first against the pre-change tree (expected: the raise-assertion fails, the replace path returning
the page with the mark standing), then against the change.

**Done-line.** `just test devpro tests/test_devpro_profiler.py` and
`just test devpro tests/dashboard/test_server.py` — both suites, run once, byte pins untouched.

### deco-into-templates — the deco in the page, the layer linked, with_frame retired

Cites [Install — Harness profiler](ACTIVE_DESIGN.md#install--harness-profiler) under
`## ARCHITECTURE delta` (the layer-link, deco-as-template-text and splice-replacement pairs) and
under `## Code delta`. Lifetime: shipped.

**Scope.** Three files:

- `devpro/profiler/view.html` and the `INDEX` template in `devpro/profiler/pages.py`: the deco —
  nav, frame band, server block — is the templates' own text, each view's active state known
  statically (the profiler view's template carries `profiler` active), the standalone render and the
  served page alike carrying what the template holds; the deco's one script is named by the board
  page as its own file, and the profiler's pages link the same file — the
  `<script src="/profiler/deco.js"></script>` tag the templates carry directly, `NAV_MARK`,
  `BAND_MARK` and `DECO_MARK` retiring. The board page's nav is unchanged; the two profiler
  templates each carry the same nav text with `profiler` active and `kanban` not. The band's
  per-page facts — the `Return to list` control on a session's page, and the dispatcher line where
  the record names one — are filled by the strict fill from the dashboard's own lookup
  (`dispatcher_of`, `dashboard/server.py:107-113`): the dispatcher line is an empty slot the fill
  leaves empty where `dispatcher_of` returns nothing and fills otherwise; the strict fill does not
  raise on an empty value.
- `devpro/profiler/pages.py`: `render_html` fills the layer into the standalone page alone
  (`CSS_SLOT`); the layer link in the served page is the template's own text, the carriage the
  layer-carriage difference alone. The legend's one carrier is the band; `render_html` no longer
  fills `LEGEND_SLOT` and `LEGEND_SLOT` retires with it. `with_frame` (`pages.py:870-893`) and its
  legend-removal mechanism retire.
- `devpro/dashboard/server.py`: the dashboard serves the assembled page and changes nothing in it —
  `profiler_page` (`server.py:130-133`, the `with_frame` call site) and its `with_frame` import
  (`server.py:52`) retire with the mechanism; `nav_html`, `band_html` and `deco_script`
  (`server.py:68-127`) retire with the deco they built once the templates carry it. The
  Content-Security-Policy is untouched — `tests/dashboard/test_server.py:354-362` pins
  `script-src 'self' 'unsafe-inline'`; no cleanup of the `'unsafe-inline'` allowance in this
  package.

**Reference searches.** `git grep -n "with_frame" -- devpro tests` → `dashboard/server.py:52,133`;
`pages.py:844,870`; no test imports it. `git grep -n "NAV_MARK|BAND_MARK|DECO_MARK|CSS_SLOT" -- tests`
→ `tests/dashboard/test_server.py:29,351`; `tests/test_devpro_profiler.py:49,210` — both are
updaters in this package. `git grep -n "deco_script|NAV_SERVER|band_html|nav_html|profiler_page" -- devpro tests`
→ only `dashboard/server.py` and a `pages.py:884` docstring mention; no test imports any.

**The byte pin, stated once.** The test is `tests/test_devpro_profiler.py`'s
`test_the_served_page_is_the_html_the_file_flow_writes` (`:854-876`), whose `_without_deco`
reconstruction (`:191-211`) — marks spliced back in, deco stripped out — is replaced. The one fact
the rewrite asserts: the rendered and served pages both carry the template deco — the deco the
same in both pages at the same place; the served page's layer is the link, the render's is the text.
The rewritten assertion: the served page with its layer line — `<link rel="stylesheet"
href="/board/board.css"><style>` — replaced by `<style>` followed by the layer's text equals the
render's page to the byte, the legends cancelling (the band carries the served legend; the render's
inline copy is removed in the comparison) — that difference and no other. The design's
`## Code delta` entry states the property and its difference set; this package does not restate it.

**Tests updated in scope.** `tests/test_devpro_profiler.py:879-894`
(`test_the_standalone_render_carries_the_shared_layer_and_the_legend_once` — the standalone render
now carries the template deco) and `tests/dashboard/test_server.py:331-351`
(`test_every_profiler_view_page_renders_the_way_the_file_flow_renders_it` — no marks stand; the
script tag is template text, so the per-page `<script>` counts change). Two more in the behavior's
blast radius join them: `tests/dashboard/test_server.py:310-330`
(`test_the_profiler_view_carries_its_nav_and_legend_once` — the nav and band are template text now;
its active-view assertions at `:320-321` read the template's own text) and
`tests/dashboard/test_server.py:410-448`
(`test_a_session_page_is_served_without_reading_the_stores_a_second_time` — its `:445` assertion
pins the dispatcher line `<strong>Dispatched by</strong> <a href="/page/s-parent">s-parent</a> —
devpro-coder` in the served page, a band text the strict fill must produce).

**Precondition and evidence.** The strict fill demonstrably does the job before `with_frame` is
removed: the difference-set assertion is added and green with `with_frame` still in place, then the
removal and the assertion's rewrite land in the package's one commit, in that order.

**Done-line.** `just test-changed` — `devpro` (which reaches the install tests under `tests/`),
`wheel` and `docs` — run before the commit; the commit's gate is Sequencing's.

### traces-feed — the static index and the `/api/traces` feed

Cites [Install — Harness profiler](ACTIVE_DESIGN.md#install--harness-profiler) under
`## ARCHITECTURE delta` (the traces-index pair) and under `## Code delta`. Lifetime: shipped.

**Scope.** `devpro/profiler/pages.py` and `devpro/dashboard/server.py`: the index's page file is
static — no row in its text — and its script fetches the records' feed the server answers at
`/api/traces`, rendering the rows client-side, the board's pattern (`board.js` fetching
`/api/board`). The session pages' embedded payload is unchanged: it is, and stays, the feed the
page's script reads — `render_html`'s data (`pages.py:578-607`) is out of this package's scope;
neither the session page's data nor `render_html`'s fills change here, and a failure there is a
finding, not an edit.

**The schema, named once.** One JSON entry per session, in the server's feed builder's one shape:
`{harness, id, records, first, last, span, dispatcher?}` — `harness` masked and clipped as
`session_harness` holds it, `id` the session id, `records` the record count, `first` and `last` the
moments as epoch ms integers, `span` seconds — and, where the record names a dispatcher for the
child-session grouping the SPEC keeps
(`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:152-158`), `dispatcher` holding that
dispatcher's session id and the dispatching call's name — the two halves of what `dispatches`
(`pages.py:772-786`) returns. Where the record names none the entry omits `dispatcher`, and the row
renders without the dispatcher line — the band's empty slot the same case, in
`deco-into-templates`' scope. The moments' only form in the feed is epoch ms: the index's script
renders each row's `<time>` and its title from them — the raw UTC string today's `<time>` elements
carry as the title retires with the server-assembled rows. One entry per store the glob finds but
cannot read, `{unreadable: <store name>}`, beside the sessions — no other entry carries that key.
The feed's schema is defined in one place — the server's feed builder — and the index's script
consumes it; no coder invents a second shape, and the two tests added below observe that one place:
the dashboard test asserts the entry's key set, the bun runner test asserts the script reads
exactly those keys.

**Facts and searches.** `git grep -n "api/traces" -- .` returns no matches: a new surface.
`read_sessions` (`pages.py:716-734`) and `dispatches` are the facts the feed serves; both are
already imported by the dashboard (`server.py:47-51`).

**Tests updated in scope.** The tests that assert on the served index's rows become tests on the
feed and the static page: `tests/dashboard/test_server.py:73-88`
(`test_the_profiler_view_serves_its_list_and_its_pages`), `:91-109`
(`test_an_unreadable_store_is_stated_in_the_index_rather_than_failing_it`), and
`tests/test_devpro_profiler.py`'s `test_the_served_index_lists_every_recorded_session` (`:664` —
its `:711-731` moments and span assertions move to the feed test with the rows),
`test_a_session_naming_itself_as_a_child_is_drawn_once_in_its_own_place` (`:735-759`),
`test_a_claude_child_agent_id_groups_no_session` (`:762-802`).
`tests/dashboard/test_server.py:410-448`
(`test_a_session_page_is_served_without_reading_the_stores_a_second_time`) pins a behavior this
package does not change — the band text it reads was updated in `deco-into-templates`; a test
failing on it here is a finding, not an edit.

**Tests added.** The defect a static index with no rows and a `/api/traces` answering an empty list
passes every current test; two tests fail on it. A dashboard test,
`test_the_traces_feed_answers_one_entry_per_session_and_names_unreadable_stores`, fetches
`/api/traces` and asserts one entry per store, the unreadable entry's `{unreadable: <store name>}`
discriminator, and the entry's key set. A profiler test,
`test_the_index_renders_the_rows_the_feed_answers`, drives a bun runner over the index's
row-rendering script (`_run_ts`, the `profiler_*_runner.ts` shape) fed the feed's JSON, and finds
the same `<tr>` order the old index had — the script's read of the schema's keys asserted there.

**Done-line.** `just test-changed` — run before the commit; the commit's gate is Sequencing's.

### quiet-client-gone — the board panel's error path quieted

Cites [Install — Harness profiler](ACTIVE_DESIGN.md#install--harness-profiler) under
`## ARCHITECTURE delta` (the client-gone pair) and under `## Code delta`. Lifetime: shipped.

**Scope.** Two files:

- `devpro/dashboard/server.py`: `DashboardServer.handle_error` (`:215-216`) — today the one-line
  delegation `self.board.handle_error(request, client_address)` — becomes the guard: `if not
  isinstance(sys.exc_info()[1], ConnectionError): super().handle_error(request, client_address)`.
  `DashboardServer` is a `ThreadingHTTPServer` (`server.py:149`), so `super().handle_error` is
  `socketserver.BaseServer.handle_error` — the base server's default, the traceback to `sys.stderr`,
  then return. `BaseHTTPRequestHandler` carries no `handle_error`:
  `python3 -c "import http.server; http.server.BaseHTTPRequestHandler.handle_error"` exits 1 with
  `AttributeError: type object 'BaseHTTPRequestHandler' has no attribute 'handle_error'. Did you
  mean: 'send_error'?` (run this session). A client gone mid-request (a page reloaded during a long
  poll) is not an error: the `ConnectionError` branch calls nothing.
- `devpro/dicing/kanban/server.py`: `KanbanServer.handle_error` (`:136-140`) is deleted — the guard
  lives at the dashboard's handler, the delegation's own site. `git grep -n "handle_error" -- devpro
  tests` names the delegation and the panel's method alone (run against the current tree): no third
  caller survives the deletion. Before the change a non-`ConnectionError` reaching the dashboard's
  handler delegates to `KanbanServer.handle_error`, whose fall-through calls
  `BaseHTTPRequestHandler.handle_error` and raises `AttributeError` instead of the default
  traceback; after, the guard's `super().handle_error` produces the traceback in its place.

**Reference searches.** `git grep -n "handle_error" -- devpro tests` →
`dashboard/server.py:215-216`, `kanban/server.py:136-140`; no test references it.
`git grep -n "ConnectionError" -- devpro tests` → `kanban/server.py:139` alone.

**Test added.** Defect: a non-`ConnectionError` reaching `DashboardServer.handle_error` raises
`AttributeError` at the delegation instead of producing the traceback. The run that fails before and
passes after: a test in `tests/dicing/test_server.py`,
`test_an_error_that_is_not_a_gone_client_gets_the_default_traceback`, beside
`test_a_client_gone_mid_request_leaves_stderr_empty` (`:518`, which pins the quiet branch). Over a
scratch root whose board reads — the suite's own `_project` helper — construct
`DashboardServer(str(root), stderr=io.StringIO())`; inside
`with pytest.raises(ValueError): raise ValueError("boom")` call `server.handle_error(None, None)` —
before the change the delegation raises `AttributeError`; after, the traceback is written to stderr
(`capsys` reads it) and nothing raises.

**Done-line.** `just test devpro tests/dashboard/test_server.py`,
`just test devpro tests/test_devpro_profiler.py` and `just test devpro tests/dicing/test_server.py`
— the server suites the panel's error path runs under, the dicing suite pinning the client-gone
branch.

### plain-tree-skill — the show-profile skill restated on the plain tree

Cites [Subsystem Map](ACTIVE_DESIGN.md#subsystem-map) under `## Code delta`. Lifetime: shipped.

**Scope.** One file: `devpro/definitions/skills/show_profile.py` — the definition source only. The
rendered copies under `rendered/` are `just render`'s; anything written into a project's
`.opencode/` or `.claude/` is `just agents`'s. Editing one of the copies edits a generated file and
leaves the defect standing at the source — the failure this package forbids.

**Facts.** The `_BODY` sentence at lines 61-62 — *read from `sh HP tree --verbose`: the plain tree
draws only the skills, agents and compactions, so a session of plain tool calls prints the column
header alone* — attributes the column-header-alone case to `--verbose`; under `--verbose` every node
is drawn (`devpro/profiler/pages.py:385-390`), and the column-header-alone case is the plain tree's
and is exact there — a session of plain tool calls has no `Skill` or `Agent` (`PARENT_TOOLS =
("Skill", "Agent")`, `devpro/profiler/values.py:33`), so it prints the column header alone. The
correction, the exact text the `_BODY` carries after this package:

- lines 61-62, from *read from `sh HP tree --verbose`:* through *column header alone* —
  *read from `sh HP tree --verbose`, which draws every node of the session; the plain tree draws the
  placeholder and marker nodes and the calls whose tool is in `PARENT_TOOLS` — the skills, agents
  and compactions — so a session of plain tool calls prints the column header alone on the plain
  tree.*
- line 66 opens *Where the plain tree prints the column header alone, nothing was recorded: say so,
  …* — `verbose` reads `plain`, and the sentence's remainder stands as it is.

**Reference searches.** `git grep -n "column header alone" -- devpro tests` →
`devpro/definitions/skills/show_profile.py:62` and `:66` alone; no test pins the sentence
(`git grep -n "column header alone" -- tests` finds nothing). The render tests that touch
show-profile (`tests/test_devpro_install.py:423,1578,1993`) assert the file exists, not its text.

**Reference retakes.** The definition's text is the reference slots' source: after this change is
verified, `just retake-reference` re-takes `rendered/reference-*` so `just render-diff` compares
against the corrected skill. The design's acceptance is the acceptance this retake requires; the
retake runs in this package's commit, per
[reference-retakes-follow-acceptance.md](PROJECT_DOCS/CONVENTIONS/planning-and-execution/reference-retakes-follow-acceptance.md).
The retake's `rendered/` change selects no surface in `just test-changed`; it is the reference, not
the test.

**Done-line.** `just test-changed` — the `devpro` and `wheel` surfaces the definition's edit
selects — then `just retake-reference`, then `just render-diff reference-claude latest`,
`just render-diff reference-opencode latest`, `just render-diff reference-gemma latest` and
`just render-diff reference-mage latest` — each of the four refreshed references diffed against
`latest`, each diff's output read and stated clean in the report; `render-diff` exits 0 on a
difference, so the exit status is not the observation.

### apply-arch-deltas — the ARCHITECTURE leaves as amended

Cites both `## ARCHITECTURE delta` entries:
[Install — Harness profiler](ACTIVE_DESIGN.md#install--harness-profiler) and
[Subsystem Map](ACTIVE_DESIGN.md#subsystem-map). Lifetime: shipped.

**Scope.** Two leaves, each passage pair applied as the design's `Becomes` block states it:

- `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` — the six passage pairs.
- `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md` — the one passage pair.

Nothing is paraphrased: application is the `Becomes` text landing verbatim, each run of whitespace
read as one space and every other character exact, and the from-text gone rather than surviving
beside it
([a-delta-application-ends-verified.md](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md)).
The application is followed by the doc-set search for the replaced wording
(`git grep -l '<the from-text's distinctive phrase>' -- PROJECT_DOCS`, the search word chosen from
the from-text, not the becomes, each hit read), stale statements reported, not rewritten
([a-delta-application-ends-by-searching-the-doc-set.md](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-by-searching-the-doc-set.md)).

**Precondition.** Every code package above has landed: the leaves as amended describe the code as
it then stands. The run of `just dev-check-design-deltas-applied` excludes no pair; a package that
has not landed is a Blocking finding reported, not an inserted passage.

**Done-line.** `just dev-check-design-deltas-applied` — the byte-check the delta application is
verified by; expected after application: `pairs: 7, landed: 7, pending: 0, drifted: 0, conflicting:
0, problems: 0`, exit 0 — any other line is the finding — then `just dev-check-links` over the
edited leaves.

## Status

| Package | State | Rating |
|---|---|---|
| zebra-variable | landed: commit `7941698`, three files; gate `just test` (1665 passed, 1 skipped) then `just sweep-python` clean | mechanical |
| strict-fill | landed: commit `af43ee7`, two files; gate `just test` (1666 passed, 1 skipped) then `just sweep-python` clean | mechanical |
| deco-into-templates | landed: commit `8a6762e`, five files; audited extra-thorough in the main session (two findings fixed before commit: the no-mark-standing checks carried to the band's marks, `link_layer`'s dead else branch deleted); gate `just test` (1666 passed, 1 skipped) then `just sweep-python` clean | expert |
| traces-feed | landed: commit `5bf027c`, five files incl. the new `tests/profiler_index_runner.ts`; audited in the main session (three findings fixed before commit: the empty index's own full-width row with the default text restored and covered, the span's every-scale rendering pinned in the runner test, the dead `format_span` deleted); gate `just test` (1661 passed, 1 skipped) then `just sweep-python` clean | expert |
| quiet-client-gone | landed: commit `96bddb0`, three files; audited in the main session (one finding fixed before commit: the orphaned `from html import escape` — a residue of the `deco-into-templates` landing, not pre-existing as reported — deleted, `just lint` green again); gate `just test` (1662 passed, 1 skipped) then `just sweep-python` clean | mechanical |
| plain-tree-skill | landed: commit `877b7fe`, the definition source (the retake's `rendered/` is gitignored — the plan's "runs in this package's commit" written against a tree that does not exist, a finding for the post-plan review); audited in the main session: the re-taken reference differs from the stale `latest` by exactly the two corrected sentences, the four diffs' differences being the slots' own pinned tuning identities — the plan's "stated clean" observation unachievable as written, a second finding; gate `just test` (1662 passed, 1 skipped) then `just sweep-python` clean | mechanical |
| apply-arch-deltas | landed: commit `b441303`, two leaves; checker `pairs: 7, landed: 7, pending: 0`; doc-set searches read clean; gate `just test` (1662 passed, 1 skipped) then `just sweep-python` clean | mechanical |
| post-plan-review | landed: commit `f74df6e`, the synthesis of three independent seat reviews (`REVIEW-{coder,architect,prompt-engineer}.md` in scratch); one blocker (R1, the subsystem-map leaf's stranded `— and`, source the design's own `Becomes` block) and seventeen findings R2-R18, each naming its seats | expert |
| post-plan-burndown | drafted — the work list is in place (W1-W7, grouped by root cause from `ACTIVE_PLAN_REVIEW.md`'s R1-R18); the `devpro-prompt-engineer` usability review of this section, then the session's revision, before it is `dispatchable` | expert |

### Post-plan review — read the design against the landed work

A review of the landed packages against [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), its findings recorded
at `ACTIVE_PLAN_REVIEW.md`: the byte pin's difference set, the feed's schema, the quieting and the
applied leaves each read against what stands. No runner target checks the review document; the
checkpoint gate runs at its commit.

### Post-plan burndown

The review's findings, grouped by root cause — one item per cause, the IDs
[`ACTIVE_PLAN_REVIEW.md`](ACTIVE_PLAN_REVIEW.md) names.

**W1 — the layer's carriage is still a silent fill** *(R4, R15)*. `link_layer`'s global
`SHARED_CSS` strip and whitespace-keyed `<style>` replace route outside the strict fill, and the
`INDEX` template's dark zebra rule is a no-op duplicate beside a comment describing a motif pair
the template does not carry. Edit `pages.py` and the `INDEX` template: the layer splice runs
through `strict_fill` (its `CSS_SLOT` mark the splice's one site), the dead dark rule and the stale
comment go. The ARCHITECTURE claim (`harness-profiler.md:52-56`) becomes true by the edit, not by
a doc change. Test: the byte pin stays green.

**W2 — the feed and the index pay for work the static index does not need** *(R2, R3)*. The feed
answers without the `page=True` policy flag, and every `/profiler/` request reads and parses every
store and discards the result. Edit `dashboard/server.py` (one keyword on the feed branch) and
`pages.py` (`index_html` reads nothing per request — the band's fills read module constants; drop
the false docstring sentence). Test: `tests/dashboard/test_server.py`'s CSP pin stays green; the
profiler index answers without a store read.

**W3 — false confidence in the read-count test** *(R9)*. The test pins one store read per
`/page/` request; the code performs two and the monkeypatch counts one binding. Edit the test to
count both bindings (or the code to read once — the design does not name the count, the test's
property does): the pinned property must hold because it is true, not because the counter missed a
binding.

**W4 — the skill's unreachable and unobservable paths** *(R11, R12, R13)*. The `No traces in …`
fallback reads stderr the model was told to read stdout for; the record count asks the model to
count with no tool carrying it; the mage slot's skill always stops at its finder. Edit
`show_profile.py`'s `_BODY`: the fallback names stderr and the failing exit; the count sentence
names what to ask for (or drops it); the mage case is stated as the finder's stop. The rendered
references re-take after.

**W5 — the retired carriage claims survive in comments and headers** *(R8, R7, R18)*. `deco.js`'s
header still says the dashboard inlines it (R8); the moments sweep races the index's fetch with no
test pinning the ordering (R7); the row-rendering script's `console.warn` logs an object (R18).
Edit `deco.js`'s comment, re-order or observe the sweep's trigger in the runner test, make the
warn a string.

**W6 — assembly-internals hygiene** *(R5, R6)*. `profiler_page` is declared twice, the dashboard's
copy a bare delegation; `strict_fill`'s internals carry an unreachable check with a misleading
`KeyError`, duplicated existence walks, a nonexistent "later stage" sentence, and `isidentifier()`
admitting Unicode ids `string.Template` rejects. Edit `pages.py` and `server.py`: one
`profiler_page`, the strict fill's checks collapsed to the ones that can fire, the docstring
truthful, the slot test `name.isidentifier() and name.isascii()` or the Template-equivalent.

**W7 — the review's document-side defects** *(R1, R10, R14, R16, R17, R13's mage statement)*. The
blocker first: the subsystem-map leaf's stranded `— and` clause reads as the plain tree finding the
profiler's launcher — fix the leaf (and the design's `Becomes` block while it survives). The plan's
Code-delta anchors get `-1` fragments; the Sequencing count reads seven; `view.html`'s
"works from file://" narrows to what the page survives; the leaf's store-level unreadable case
gains the file-level one or names it; the mage statement lands with W4's finder fix.

Each work item lands in its own commit under the checkpoint gate (`just test`, then
`just sweep-python`); the item's tests are the ones it changes, plus the byte pin where the
assembly is touched.
