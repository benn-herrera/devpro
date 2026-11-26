# Serving

## The verb and the bind

The dashboard renders in memory behind a local HTTP server: the
`devpro dashboard [<project-dir>] [--port <number>]` verb binds `127.0.0.1` on a free port —
`--port` pins one, 0 (its default) asking the system for a free one — and prints the served URL on
stdout for cmd-clicking. The bind is the rule, not a detail: the server listens on loopback only and
loads nothing from the network, so the records it renders never leave the machine. The board is the
dashboard's landing surface: its URL's root answers a `302` to `/board/`'s absolute URL — the one it
prints, `http://127.0.0.1:<port>/board/` — so opening it shows the kanban board, the project's actual
current state.

## The index

The profiler view is the second view, at `/profiler/` (trailing slash, the board panel's convention):
the index of record files, every store the readers read,
one row per session — harness,
session id, the models its calls recorded, record count, the count of the dispatched agents it
holds, first and last moments, and the span between them —
each linking to `/page/<session-id>`, which serves that session's page in
memory, the render's page carrying the same page data `tree --format html` produces. The header row
and the body's rows take their column widths from one source, so every header sits over the column it
names at every width the data produces, and the first-to-last column is wide enough that its line
never wraps. The index's page file is static — no row is in its text — and
its script renders the feed the server answers at `/api/traces`: one JSON entry per session carrying
`harness`, `id`, `models`, `records`, `agents`, `first`, `last`, `span`, and `dispatcher` where a
session was dispatched — `models` the distinct models the session's records name, in the order
they first appear, empty where none does. The script puts `harness` and `records` under their own
names, `id` in the session column, `models` in the model column, joined by `, `,
`agents` in the dispatched-agents count,
`first` and `last` in the first-to-last line, `span` in the
span column, and draws `dispatcher` in no column at all, as the child row under its dispatcher's row.
The agents cell reads the count with the postscript `agents` — `1 agent`, `3 agents`. The index's row
links and the session page's return link carry the query, so the controls' state and the sort in
force survive the page's own navigation. An agent name a page renders drops the `devpro-` prefix: the
reader knows the set's provenance already. A feed that reads every store it names and finds no
session in them is one `stores` entry naming how many stores the exact names read. A store an exact
name finds but cannot read fails the feed: the handler answers a `500` whose error body names the
raised exception's text — the dashboard is a `127.0.0.1` surface, so the text is the operator's. The
index carries simple controls — child-record
rows on and off, claude and opencode on and off separately, and column heads sorting on the
dispatched-agent count, the record count, the time and the span — and a failed feed names itself in
an in-page notice, distinct from the no-records state a zero-record store renders. The controls' state
and the sort in force live in the index page's URL, which the reader can copy, so leaving the view
and returning restores it. The session page's embedded payload is unchanged: it is, and stays, the
feed the page's script reads.

## Dispatched children

A session an opencode record names as its dispatch's child is drawn under the session that dispatched
it — a dispatch's child one level deep; deeper chains read on the session's page, whose tree draws
every dispatch as a context — that session's row carrying the count of the rows beneath it and each
child's naming, after its id and with no lead-in, the call that dispatched it — the indent, the
accent-colored border at its left edge and its tone mark it a child; the rows alternate their tone,
and each carries its harness's mark.

## The moments and their form

The pages' own scripts draw every moment local at birth — the moments cells, the
index's first-to-last line, the session page's header stamp, its diagram's and its call tree's
times — in the reader's local time, 24-hour, one
notation: the first end of a pair carries its date whole beside its time, the second its time only,
the clock's being 24-hour making a span across midnight plain by the numbers, no branch to state. The
machine form stands in the `<time>` elements' `datetime` attributes alone, and no title carries a
moment's UTC; a
page carries no moments where its script does not run, and the deco formats the moments the pages
present and reads none of them. `tree`'s text reads
its time column and its session stamps in the machine's local zone, through `values._local`, which
doctor's `newest:` line reads too. The span is its own
column, drawn from the feed's seconds in the same form the call tree's duration column takes, both
from the one formatter (`devproFormat.dur`): a duration from zero up reads `0s` at zero, `217ms`
below the second, `4.2s` with one decimal below ten seconds, `48s` below the minute, `18m 49s`
below the hour — `18m` when its seconds are zero — and `1h 2m` from the hour — `1h` when its
minutes are zero. No space stands between a number and its unit.

## The dispatcher's frame

A session's page
carries its dispatcher in the frame band, linked to that session's page, where one dispatched it, and
then names its own root context — its id still `main` — for the dispatching call's agent, the
prefix dropped, in the hue the context that call opened wears on the dispatcher's page:
`pages.dispatcher_of` reads from the dispatcher's records at render both the dispatching call's
agent and the hue, the dispatcher's own root hue from its own dispatcher's, up the chain, the
child's own records naming no parent, and the page's other contexts take hues from 1 up, skipping
the root's hue. A page nothing dispatched names
its root `main`, in hue 0. A call row whose tool is `Agent` links to the child session's page where the record names one: a
child's page the dashboard does not serve answers the 404 any unrecorded session's page answers.

## The nav and the server block

A top nav persists across both views — the `devpro` brand, then `kanban` and `profiler`, the active
view in the motif's accent and the inactive one a lifted gray, then the server block right-justified
at the nav's flex edge: the live/idle state indicator and the stop — and in the profiler view a frame
band sits under it, carrying on a session's page the how-to-read legend at its top and `Return to
list` back to `/profiler/`, and on the index neither; drill-down is ordinary page navigation, and no inner frame exists. The nav
and the band are the view's pages' own text, assembled with the page by the one strict fill; the
dashboard serves the assembled page and changes nothing in it. The nav's server block is the same on
both views: the decoration's one script polls `GET /api/state` — the endpoint every view's server
answers `{"state": "live"}` while it serves, and that a closed server answers not at all — so a page
that carries no payload of its own reads the state the board reads, and the stop posts the board
panel's `/api/stop`. No file is written for the traces.

## The models in the page

The page names the models its calls recorded: the session's in
its header line, each context's in its lifeline's header where that header holds it alone, and each
call's in its detail — a context or a call showing none where it recorded none, and a count where a
context recorded several — and shows a session's calls: a session of
nothing but tool calls renders those calls as its calls content, never an empty tree under a calls
header. The server runs until interrupted (Ctrl-C) or stopped from the page; either exits 0.

## The board panel

The dashboard's board panel is the profiler's sibling panel, `devpro.kanban.server`'s `KanbanServer`
over the dashboard's root. The seam is `panel_handler`: the dashboard reads the request, hands it to a
handler over the panel's routes, and answers it on its own connection, so the guard, the reply write
and the Content-Security-Policy the page is served under are the dashboard's one of each and travel
with the panel's answers. A client gone mid-request — a page reloaded during a long poll — is not an
error; anything else gets the default traceback. The panel serves the project's kanban board at
`/board/` and, at the board's own root paths, its payload, its moves and its stop (SPEC.md, Dicing
and Checks, Kanban): its two moves write the project's `ROADMAP.md` and the active design, and its
stop button ends the server as an interrupt does. Its payload carries `devpro_version`, the version
the board's connection indicator names, beside its `version`, `board`, `plan_columns` and `project`
keys. A board file that cannot be read, and a port that cannot be bound, refuse the verb before it
prints the URL: exit 2, and `error: ` before the message on stderr.
