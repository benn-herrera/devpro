### Harness profiler

Every claude project install ships the activity profiler as payload, not as a companion plugin
(SPEC.md, Deployed Surfaces, Shipped files). The profiler is devpro's own port of the harness-profiler
plugin by Aleksandr Furmanov (MIT, `github.com/afurmanov/harness-profiler`), credited in README.md,
and carries no version stamp on it.

**The code is devpro's.** The port is a devpro package, `devpro/profiler/`, standard library only,
no dependency: `values.py` the schema, limits, masks and store facts every other module reads,
`capture.py` the hook payload's parsing, masking and record serialization, `pages.py` the tree and
page render, `hooks.py` the committed hook's wiring — `init` and `doctor` — `stores.py` the stores'
rename and their one repair, and `cli.py` the `profiler` verb's dispatch. The verb is dispatched
lazily: registering it imports none of these modules, and `cli.py` imports the one whose subcommand
runs. Its subcommands are `capture`, `tree`, `init`, `doctor` and `repair`; the records are served by
the `dashboard` verb, below.

**One path to the capture.** Each hook names the wrapper its writer knows; none resolves one. The
committed hook runs `"$CLAUDE_PROJECT_DIR/.claude/skills/devpro/tools/devpro.sh" profiler capture
claude` (`hooks.HOOK_COMMAND`, built from `hooks.INSTALL_WRAPPER`), and the installed hook names the
installed wrapper in the same shape. No launcher stands between either and the wrapper.

**The page template and its presentation layer.** `view.html` is the wheel's package data,
`devpro/profiler/view.html`, read by `pages.py` through `importlib.resources` beside the module that
renders it: a self-contained page that loads nothing from the network, no install resource and no
committed hook file. It carries no palette of its own: its head carries the layer's mark,
`<!--LAYER-->` (`LAYER_MARK`),
which fills with the presentation layer one way per carrier — the page's one rendering, two carriers:
the dashboard's serve path (`served_page`) links the board's own stylesheet,
`devpro/kanban/assets/board.css`, and `render_html` — `tree --format html`'s carrier — fills the
layer's text inline, the one difference a file cannot avoid, being unable to link a server's origin.
What the dump writes is the page the dashboard serves: one template, one script, one band, one
presentation. One CSS source serves both views, and `pages.SHARED_CSS` is that text: the board serves
the file at `/board/board.css`, the render inlines it into the page it prints, and the dashboard links
the same file into the pages it serves, the layer fetched from the server's own origin, which the
site's content-security policy allows. The board's component rules may be scoped so their selectors
cannot reach the profiler page's DOM, and the template's own rules draw the sequence diagram's colours
from the palette's `--c0`…`--c7` variables, no palette of its own.

The frame band's `<!--LEGEND-->` mark is where the how-to-read legend goes: `pages.LEGEND` holds the
legend once — its prose and its symbol key — its two carriers the standalone render's filled copy and
the dashboard's frame band, which reads the same constant, no second copy in the template. Every fill
is strict: a fill that finds an unknown or unfilled placeholder in the template's text refuses —
raises — instead of leaving the mark standing, one fill through which every fill the profiler's
assembly makes runs, and a test walks what that fill is handed — `view.html` and the `INDEX` template
— so no page, rendered or served, carries a placeholder standing.

The index's `INDEX` template carries the same `<!--LAYER-->` mark, and the deco is the templates' own
text: the brand, the two view names and, right-justified at the nav's flex edge on every view, the
server block — the live/idle indicator and the stop — with each view's active state known statically,
the standalone render and the served page alike carrying what the template holds. The template's own
rules are the page's alone: the layer clears the body's margin and sets the page's colours, and the
template pads its `main`. The deco's one script is named by the board page as its own file, and the
profiler's pages link the same file; the band's legend carries the `Return to list` control on a
session's page. Every script the pages run — the deco's and the templates' own — wraps its body in an
IIFE: its helpers are module-private, and the deliberate surface is only what the page calls, because
classic scripts share one global scope and a helper redeclared across scripts is a page that drew
nothing. The board page carries the same nav grammar, written in its own `index.html`, with the same
server block in the nav; it carries no legend.

**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `"${CLAUDE_PLUGIN_ROOT}/skills/devpro/tools/devpro.sh" profiler capture claude`
(`claude.INSTALL_WRAPPER`). The wiring is data in the harness module, not a new mechanism, and no
entry is gated on the install-time probe. A capture appends one line to the project's
`.devpro-temp/.profiler-claude/<session-id>.jsonl` — one of the per-harness stores under
`.devpro-temp/`, the project's scratch directory, which a project install of a nested plugin prepares
and gitignores (a mage or user-level install prepares neither; The scratch directory, Renders and
copies). The
wrapper's `capture` subcommand
owns the never-block contract: `cli.run` reads the hook payload bounded to `PAYLOAD_LIMIT` bytes,
points stdout at the null device for the capture's duration so no child line reaches the hook's
stdout, and returns 0 on every path.

**The install renders and copies.** A claude project install writes the plugin's rendered
files and `hooks/hooks.json`, whose profiler entries are the wiring above. It copies the harness's
resources byte-verbatim — `harnesses/resources/claude/` holds `hooks/` alone, nothing under
`profiler/` — and writes the wrapper at `skills/devpro/tools/devpro.sh`. What it removes is *What
removes the retired path*, below.

**Serving.** The dashboard renders in memory behind a local HTTP server: the
`devpro dashboard [<project-dir>] [--port <number>]` verb binds `127.0.0.1` on a free port —
`--port` pins one, 0 (its default) asking the system for a free one — and prints the served URL on
stdout for cmd-clicking. The bind is the rule, not a detail: the server listens on loopback only and
loads nothing from the network, so the records it renders never leave the machine. The board is the
dashboard's landing surface: its URL's root answers a `302` to `/board/`'s absolute URL — the one it
prints, `http://127.0.0.1:<port>/board/` — so opening it shows the kanban board, the project's actual
current state.

The profiler view is the second view, at `/profiler/` (trailing slash, the board panel's convention):
the index of record files, every store the readers read, one row per session — harness,
session id, record count, the count of the dispatched agents it holds, first and last moments, and
the span between them — each linking to `/page/<session-id>`, which serves that session's page in
memory, the render's page carrying the same page data `tree --format html` produces. The header row
and the body's rows take their column widths from one source, so every header sits over the column it
names at every width the data produces. The index's page file is static — no row is in its text — and
its script renders the feed the server answers at `/api/traces`: one JSON entry per session carrying
`harness`, `id`, `records`, `agents`, `first`, `last`, `span`, and `dispatcher` where a session was
dispatched. The script puts `harness` and `records` under their own names, `id` in the session column,
`agents` in the dispatched-agents count, `first` and `last` in the first-to-last line, `span` in the
span column, and draws `dispatcher` in no column at all, as the child row under its dispatcher's row.
A feed with no session and no unreadable store is one `stores` entry naming how many stores the glob
found; a store the glob finds but cannot read is an entry among them, marked unreadable, and the
server raises nothing for it. The index carries simple controls — child-record rows on and off, claude
and opencode on and off separately, and column heads sorting on the dispatched-agent count, the record
count, the time and the span — and a failed feed names itself in an in-page notice, distinct from the
no-records state a zero-record store renders. The controls' state and the sort in force live in the
index page's URL, which the reader can copy, so leaving the view and returning restores it. The
session page's embedded payload is unchanged: it is, and stays, the feed the page's script reads.

A session an opencode record names as its dispatch's child is drawn under the session that dispatched
it — a dispatch's child one level deep; deeper chains read on the session's page, whose tree draws
every dispatch as a context — that session's row carrying the count of the rows beneath it and each
child's naming the call that dispatched it; the rows alternate their tone, and each carries its
harness's mark. The pages' own scripts draw every moment local at birth — the moments cells, the
index's first-to-last line, the session page's header stamp — in the reader's local time, 24-hour, one
notation: the first end of a pair carries its date whole beside its time, the second its time only,
the clock's being 24-hour making a span across midnight plain by the numbers, no branch to state. The
machine form stands in the `<time>` elements' `datetime` attributes and the raw UTC in the titles; a
page carries no moments where its script does not run, and the deco reads none. The span is its own
column, drawn from the feed's seconds as whole hours and minutes — `3h 2m` — minutes and seconds below
the hour — `3m 20s` — seconds below the minute, and `0s` for a zero-length span. A session's page
carries its dispatcher in the frame band, linked to that session's page, where one dispatched it, and
a call row whose tool is `Agent` links to the child session's page where the record names one: a
child's page the dashboard does not serve answers the 404 any unrecorded session's page answers.

A top nav persists across both views — the `devpro` brand, then `kanban` and `profiler`, the active
view in the motif's accent and the inactive one a lifted gray, then the server block right-justified
at the nav's flex edge: the live/idle state indicator and the stop — and in the profiler view a frame
band sits under it, carrying the how-to-read legend at its top and, on a session's page, `Return to
list` back to `/profiler/`; drill-down is ordinary page navigation, and no inner frame exists. The nav
and the band are the view's pages' own text, assembled with the page by the one strict fill; the
dashboard serves the assembled page and changes nothing in it. The nav's server block is the same on
both views: the decoration's one script polls `GET /api/state` — the endpoint every view's server
answers `{"state": "live"}` while it serves, and that a closed server answers not at all — so a page
that carries no payload of its own reads the state the board reads, and the stop posts the board
panel's `/api/stop`. No file is written for the traces. The page shows a session's calls: a session of
nothing but tool calls renders those calls as its calls content, never an empty tree under a calls
header. The server runs until interrupted (Ctrl-C) or stopped from the page; either exits 0.

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

**The skill.** `profiler` ships as a rendered skill definition under `devpro/definitions/`, so it
carries the generated banner and the harness's namespace (`devpro:profiler` under claude) and renders
under every harness. Its `Locate the profiler` block states one wrapper as the writer's knowledge —
the project's committed wrapper where `init` rendered the skill, the installation's own where the
install rendered it — and where that file does not stand the skill says the tool is not installed. A
user-level install renders the skill and copies no resource, so there it is the committed wrapper or
the absence. `init` renders the same skill into the repository's `.claude/skills/profiler/SKILL.md`
from the definition.

**Limits, stated.** The `doctor` subcommand greps the name `harness-profiler` in claude's
installed-plugin records and will not recognize the payload copy; its committed-hook and
settings-hook checks still find a committed one. The limitation is stated, not fixed. Claude Code on
the web sends the same hook data but loads no plugin's hooks, so a cloud session records nothing until
the hook is committed to the repository, as *What `init` writes* below describes.

**What `init` writes.** `init claude` writes the repository's rendered skill and its
`.claude/settings.json`, merging the six entries through `hooks.merge_hooks`: each command runs
`profiler capture claude` on the committed wrapper, `hooks.HOOK_COMMAND`. An entry an `init` wrote
earlier is replaced in place, so a re-run picks up new hook options.

**What removes the retired path.** `init` unlinks, in the repository, the retired launcher
`profiler.sh` and the names it carried before it — `hp.sh`, `hp` — with `hp.py` and `view.html` beside
them, then removes `.claude/harness-profiler/` where that leaves it empty (`hooks.init`, over
`RETIRED_LAUNCHERS` and `RETIRED_HOOK_FILES`). It unlinks `.claude/skills/show-profile/SKILL.md`,
the skill under its former name, with its directory where that leaves it empty. `install`'s copy step
removes, on every install, the retired launcher files standing in the install directory —
`RETIRED_RESOURCE_FILES`: `profiler/profiler.sh` and `profiler/hp.sh` — where each carries this
repository's installed header, then removes `profiler/` where that leaves it empty
(`RETIRED_RESOURCE_DIRS`). `install` deletes only a file carrying the header it stamps; `init`
deletes by name, under `.claude/` in the repository it targets. The preflight predicts both from the
same lists. A hook command spelling a retired launcher stays this tool's: `hooks.is_our_command`
recognizes it, and an `init` re-run replaces it.

**The committed hook's freshness.** `doctor`'s `update` line names a committed hook that lacks an
event, is not `async`, or runs another command than `hooks.HOOK_COMMAND` — the registered wiring is
the master, and the compare reads it without needing an install directory.

**What does not exist.** The profiler ships no launcher resource: `harnesses/resources/claude/` holds
nothing under `profiler/`. No companion-plugin mechanism is built, so the profiler has no namespace of
its own and no carrier but the devpro plugin. Should it become optional later, it becomes a
`--components` value.

**The opencode capture.** Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call (the `tool`,
`sessionID`, `status`, `input` and `result`/`error` the after-hook reports), and the idle hook appends
a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/.profiler-opencode/<session-id>.jsonl` store, `harness` `"opencode"`, which
`devpro profiler tree` and the dashboard's profiler view render beside the claude sessions', each
record read from its own `.profiler-*` store. A `subagent` or `task` call also records the child
session it dispatched: the child's id is `result.sessionID` on 2.4.1, `output.sessionID` on 2.3.2 and
`metadata.sessionID` on 2.3.0, read in that order each under the host's own string guard, and it
fills the record's `child_agent_id` — where the index groups the child one level under its dispatcher,
the tree on the session's page drawing the dispatch as a context — and the dispatch links to the
child's page. The stores stay flat — the child's id reaches no capture as a parent key, the hierarchy
being what the parent's records state — and a dispatch that fails before creating a child, or whose
result reports no child session, records none. A capture written before it read 2.4.1's shape carries
the child's id only in its stored result text; *The repair* below fills it.

The model's own `todowrite` notes are not recorded: they are not activity, so the store holds one
record per tool call that did something. A capture that fails raises nothing out of the hook. `init`
and `doctor` stay claude-facing: opencode has no committed-hook concept. Opencode's install copies the
plugin's `profiler.ts` alone, no launcher and no hook entry beside it, and the store the plugin writes
is read by `devpro profiler tree` — the wrapper's own subcommand. One line holds one record, and the
limits that keep it so are `devpro/profiler/values.py`'s: `NAME_LIMIT`, `ARGS_LIMIT` and
`RESULT_LIMIT` clip a field's text as the Python capture clips it, and `LINE_LIMIT` bounds the written
line in bytes, `name` and `session` clipped at the root before `result` and `args` gives way. A line
a killed process left torn would fuse the next record onto it, so an append finds the last newline in
the file's tail and truncates to it, renaming the whole store aside where the file holds no newline at
all. The Python capture has no such repair: it appends as it stands, and its reader skips the torn
line. An opencode record carries no token counts, so the tree's token columns are blank for its
sessions; claude's counts come from its own transcripts under `~/.claude/projects/`, which is
claude's data, not a source the install configures. An opencode record's `branch` is empty on its own
account: the capture runs in the host's process, and the hooks report no branch, so `tree --branch`
selects no opencode session.

**The repair.** `devpro profiler repair`, run once from the project's root, reads each standing
opencode subagent record's result text and fills its `child_agent_id` where the host reported it — a
record whose id is already right stays untouched, so a second run fills nothing, and every edge a
capture writes after the update is correct at write time. It prints `repaired: <n> edges; null: <m>
records (no child id)` — the edges it filled and the subagent records left naming no child, among them
a dispatch that failed before creating one, a result clipped before the id survived, and each record
of a file left as it stands — and a file a capture appends to while the repair reads it is named on
stderr and left as it stands, never rewritten under a session's own write.

**The stores and their rename.** Each harness's capture owns one store under the project's
`.devpro-temp/`: claude's `.profiler-claude/`, opencode's `.profiler-opencode/`, and both readers —
`tree`'s render, and the dashboard's profiler view, whose index and session pages read the stores per
request — read the stores the captures write, the directories named exactly `.profiler-<harness>`
for a harness name the profiler's own captures use (claude and opencode today) — a dot name, so the
stores group and sort at the top of the scratch tree. A directory of any other shape beside a store
is not a store and is not read. Both `devpro install` and `devpro profiler init claude` rename the two
old-pattern stores: `.devpro-temp/claude-profiler/` to `.profiler-claude` and
`.devpro-temp/opencode-profiler/` to `.profiler-opencode`, and the move is printed. A directory under
`.devpro-temp/` whose name only ends in `-profiler` is no store and is left alone. Where a store's new
name is already taken, the old one is left in place and named instead — the stores' contents are
never merged, and merging or deleting the old store is the operator's call. A second run touches
nothing. A capture writes `.profiler-*` while an old-pattern store still holds its traces, so `tree`
cannot read that store until the migration runs; a store the rename leaves standing stays unread until
the operator merges or deletes it.

**Doctor's lines.** `devpro profiler doctor` runs as the wrapper's own subcommand, and its `devpro:`
line names the wrapper's own path — `INSTALLED_WRAPPER`'s where the install stands, the invoking
tree's devpro otherwise — one line: `traces:` the claude store `tree` reads, among the
`.profiler-<harness>` stores it reads, `hook:` where a capture hook is registered here (the plugin's own
records, and the committed,
local and user settings files) or `not installed` with the install and `init` remedies, an `old:` line
per pre-rename store it cannot read with the remedy that renames or merges it, `update:` a stale
committed hook, and `newest:` the newest claude session's last moment or `no calls recorded yet`.
Doctor is claude-facing: every line reads claude's hook and claude's store, where `tree` reads both
harnesses'.
