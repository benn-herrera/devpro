### Harness profiler

Every claude project install ships the activity profiler as payload, not as a companion plugin
(SPEC.md, Deployed Surfaces, Shipped files). The profiler is devpro's own code, ported from the
harness-profiler plugin by Aleksandr Furmanov (MIT, `github.com/afurmanov/harness-profiler`); the
acknowledgement in README.md credits the source. devpro owns the ported code
and carries no version stamp on it.

**The code is devpro's.** The port is a devpro package, `devpro/profiler/`, standard library only,
no dependency: `values.py` the schema, limits, masks and store facts every other module reads,
`capture.py` the hook payload's parsing, masking and record serialization, `pages.py` the tree and
page render, `hooks.py` the committed hook's wiring — `init` and `doctor` — and `cli.py` the
`profiler` verb's dispatch. The verb is dispatched lazily: registering it imports none of these
modules, and `cli.py` imports the one whose subcommand runs. Its subcommands are `capture`, `tree`,
`init` and `doctor`, which read exactly as they did inside `hp.py`; the records are served by the
`dashboard` verb, below.

**Resources.** One file lives in `devpro/harnesses/resources/claude/profiler/`:
`hp.sh`, the bash launcher, which finds a devpro — the installation's own wrapper first — and
runs its `profiler` verb (no environment variable overrides the search). It carries the `!INSTALLED! … devpro` banner within its
first ten lines — the banner rule binds every harness resource — and `harness_resource_copies` lands
it at the path it holds below the install directory, so the install directory gains
`profiler/hp.sh`. Its source is claude's: mage ships no resources, and an opencode install carries
the same file, below, though opencode's capture is the plugin's own TypeScript.

**The launcher's finder.** Its first candidate is the installation's wrapper (SPEC.md, Deployed
Surfaces, Shipped files), resolved from the launcher's own location: `../tools/devpro.sh` from
`<install-dir>/profiler/hp.sh`, and `../skills/devpro/tools/devpro.sh` from the committed
`.claude/harness-profiler/hp.sh`. Its fallback extends `PATH` with `/opt/homebrew/bin`,
`/usr/local/bin` and `~/.local/bin`, since a hook may run with a `PATH` where only the shell's
builtins are found, and runs one `command -v` over the whole of it. A candidate, the wrapper as any
other, is the devpro when it runs and exits 0 on `--version`, so a wrapper that finds no usable
Python is treated as absent and the capture still exits 0 with no output — the found command is the
one `profiler` runs — and the terminal line is
`exec "$devpro" profiler "$@"`, the subcommand parsed where the verb is dispatched and the launcher's
own arguments passed through unchanged. The one-shot finder replaced the per-candidate probe and the
`HP_DEVPRO` override: there is no variable to set, and a found command that does not run is reported
and treated as absent.

**The page template and its presentation layer.** `view.html` is the wheel's package data,
`devpro/profiler/view.html`, read by `pages.py` through `importlib.resources` beside the module that
renders it: it is a self-contained page that loads nothing from the network, it ships in the wheel,
and it is no install resource and no committed hook file. It carries no palette of its own: its head carries the layer's mark, `<!--LAYER-->`
(`LAYER_MARK`), which `render_html` fills with the presentation layer's text inline — the board's
own stylesheet, `devpro/kanban/assets/board.css`, read the same way — for the standalone page,
which loads nothing from the network and so cannot link it, and which the serve path
(`served_page`) fills with a link to that stylesheet. One CSS
source serves both views, and `pages.SHARED_CSS` is that text: the board serves the file at
`/board/board.css`, the render inlines it into the page it prints, and the dashboard links the same
file into the pages it serves, the layer fetched from the server's own origin, which the site's
content-security policy allows. The board's
component rules may be scoped so their selectors cannot reach the profiler page's DOM; the source
stays one file, and the template keeps its own rules — the sequence diagram's colours come from the
palette's `--c0`…`--c7` variables, no palette of its own. The frame band's `<!--LEGEND-->` mark is where the how-to-read legend goes: `pages.LEGEND` holds the legend once — its prose and its symbol key —
and `render_html` fills it into the page it renders, so the standalone page carries the legend and
no second copy exists in the template. The legend has one home and two carriers: the standalone
render's filled copy, and the dashboard's frame band, which reads the same constant. Every fill is
strict: a fill that finds an unknown or unfilled placeholder in the template's text refuses —
raises — instead of leaving the mark standing, one fill through which every fill the profiler's
assembly makes runs, and a test walks what that fill is handed — `view.html` and the `INDEX`
template — so no page, rendered or served, carries a placeholder standing. The index's `INDEX` template carries the same `<!--LAYER-->` mark, and the deco is the templates' own text:
the brand, the two view names and, right-justified at the nav's flex edge on every view, the server
block — the live/idle indicator and the stop — is template text with each view's active state known
statically, the standalone render and the served page alike carrying what the template holds; the
template's own rules are the page's alone: the layer clears the body's margin and sets the page's
colours, and the template pads its `main`. The deco's one script is named by the board page as
its own file, and the profiler's pages link the same file; the band's legend with its `Return to
list` control on a session's page. The board
page carries the same nav grammar, written in its own `index.html`, with the same server block in
the nav; it carries no legend.

**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `sh "${CLAUDE_PLUGIN_ROOT}/profiler/hp.sh" capture claude`, and the hook name changes with no
other: `hp.sh` kept its name, so a committed hook written under it stays this tool's own. The wiring
is data in the harness module, not a new mechanism, and no entry is gated on the install-time probe. A
capture appends one line to the project's `.devpro-temp/.profiler-claude/<session-id>.jsonl` — one of
the per-harness stores under `.devpro-temp/`, every `.profiler-*` directory of which the `tree`
subcommand renders — the project's scratch directory, which the project's own convention gitignores; a
capture that fails, or finds no `devpro`, exits 0 with no output.

**Serving.** The dashboard renders in memory behind a local HTTP server: the `devpro dashboard
[<project-dir>] [--port <number>]` verb binds `127.0.0.1` on a free port — `--port` pins one, 0
(its default) asking the system for a free one — and prints the served URL on stdout for
cmd-clicking. The bind is the rule, not a detail: the server listens on loopback only and loads
nothing from the network, so the records it renders never leave the machine. The board is the
dashboard's landing surface: its URL's root answers a `302` to `/board/`'s absolute URL — the one it
prints, `http://127.0.0.1:<port>/board/` — so opening it shows the kanban board, the project's actual
current state. The profiler view is the second view, at
`/profiler/` (trailing slash, the board panel's convention): the index of record files, every store
the `.profiler-*` glob finds, one row per session — harness, session id, record count, first and
last moments, and the span between them — each linking to `/page/<session-id>`, which serves that
session's page in memory, the render's page carrying the same page data `tree --format html`
produces. The index's page file is static — no row is in its text — and its script fetches the
records' feed the server answers at `/api/traces`, one JSON entry per session with the columns
above, the stores the glob finds but cannot read among them as unreadable, and renders the rows
client-side — the board's pattern, the payload consumed client-side. The index carries simple
controls — child-record rows on and off, claude and opencode on and off separately, and column
heads sorting on the dispatched-agent count, the record count, the time and the span — and a
failed feed names itself: an in-page notice naming the feed's failure, distinct from the
no-records state a zero-record store renders. The session page's embedded
payload is unchanged: it is, and stays, the feed the page's script reads. A session an opencode record names as its dispatch's child is drawn under the session that
dispatched it — a dispatch's child one level deep; deeper chains read on the session's page, whose
tree draws every dispatch as a context — that session's row carrying the count of the rows beneath
it and each child's naming the call that dispatched it; the rows alternate their tone, and each
carries its harness's mark. The moments are the raw UTC where no script runs; with it, every moment the pages and their
headers show — the moments cells, the index's first-to-last line, the session page's header stamp —
reads in the reader's local time, 24-hour, one notation, the machine form only in the `<time>`
elements' `datetime` attributes and the raw UTC in the titles. A first-to-last whose ends share the
reader's day reads as two times with no date; one crossing midnight reads with the date on its
first end alone and the finish end time only, the next day's being obvious. The span is its own
column. A session's page carries its dispatcher in the frame band, linked to that session's page,
where one dispatched it, and a call row whose tool is `Agent` links to the child session's page
where the record names one: a child's page the dashboard does not serve answers the 404 any unrecorded
session's page answers. A top nav persists across both views — the `devpro` brand, then `kanban` and
`profiler`, the active view in the motif's accent and the inactive one a lifted gray, then the
server block right-justified at the nav's flex edge: the live/idle state indicator and the stop —
and in the profiler view a frame band sits under it, carrying the how-to-read legend at its top and,
on a session's page, `Return to list` back to `/profiler/`; drill-down is ordinary page navigation,
and no inner frame exists. The nav and the band are the view's pages' own text, assembled with the page by the one strict
fill; the dashboard serves the assembled page and changes nothing in it. The nav's server block is the same on both views: the decoration's
one script polls `GET /api/state` — the endpoint every view's server answers `{"state": "live"}`
while it serves, and that a closed server answers not at all — so a page that carries no payload of
its own reads the state the board reads, and the stop posts the board panel's `/api/stop`. No file is
written for the traces. A store the glob finds but cannot read appears in the index as unreadable —
the server raises nothing for it. The page shows a session's calls: a session of nothing but tool
calls renders those calls as its calls content, never an empty tree under a calls header. The server
runs until interrupted (Ctrl-C) or stopped from the page; either exits 0. The dashboard's board
panel is the profiler's
sibling panel, `devpro.kanban.server`'s `KanbanServer` over the dashboard's root. The seam is
`panel_handler`: the dashboard reads the request, hands it to a handler over the panel's routes, and
answers it on its own connection, so the guard, the reply write and the Content-Security-Policy the
page is served under are the dashboard's one of each and travel with the panel's answers. A client
gone mid-request — a page reloaded during a long poll — is not an error; anything else gets the
default traceback. The panel
serves the project's kanban board at `/board/` and, at the board's own root paths, its payload, its
moves and its stop (SPEC.md, Dicing and Checks, Kanban): its two moves write the project's
`ROADMAP.md` and the active design, and its stop button ends the server as an interrupt does. Its
payload carries `devpro_version`, the version the board's connection indicator names, beside its
`version`, `board`, `plan_columns` and `project` keys. A board file that cannot be read, and a port
that cannot be bound, refuse the verb before it prints the URL: exit 2, and `error: ` before the
message on stderr.

**The skill.** `profiler` ships as a rendered skill definition under `devpro/definitions/`, so it
carries the generated banner and the harness's namespace (`devpro:profiler` under claude) and
renders under every harness. Its finder's first candidate, `../../profiler/hp.sh` from
the skill's directory, resolves to `<install-dir>/profiler/hp.sh` where the payload landed — the
launcher that then finds `devpro` — and its second, the committed `.claude/harness-profiler/hp.sh`,
covers a repository where the hook was committed for claude-on-web; where neither stands, the skill
says the tool is not installed. A user-level install renders the skill and copies no resource, so
there it is the committed copy or the absence. `init` renders the same skill into the repository's
`.claude/skills/profiler/SKILL.md` from the definition, beside the launcher it copies.

**Limits, stated.** The `doctor` subcommand greps the name `harness-profiler` in claude's
installed-plugin records and will not recognize the payload copy; its committed-hook and
settings-hook checks still find a committed one. The limitation is stated, not fixed. Claude Code on
the web sends the same hook data but loads no plugin's hooks, so a cloud session records nothing
until the hook is committed to the repository; the `init` subcommand does that, copying the launcher
and the skill into the repository's `.claude/` and merging the six entries into its
`.claude/settings.json`.

**What `init` copies, and what it removes.** `init claude` writes the repository's
`.claude/harness-profiler/hp.sh` — the harness resource the devpro package ships, readable as
`devpro.profiler.hooks.launcher_resource()` and marked executable — and the rendered skill, then
unlinks the files an older `init` left beside the launcher: `hp.py` and `view.html`, which no install
ships any more — and the skill an older `init` rendered under its former name,
`.claude/skills/show-profile/SKILL.md`, with its directory where that leaves it empty.
A hook committed by an older `init` therefore keeps working: it runs `hp.sh`, which finds `devpro`. `doctor`'s `update` line names a committed hook that lacks an event, is not `async`,
or differs by a byte from the launcher's resource the devpro package ships — that resource is the
master, and the compare reads it without needing an install directory.

**What does not exist.** No companion-plugin mechanism is built: the profiler has no namespace of its
own and no carrier but the devpro plugin. Should it become optional later, it becomes a
`--components` value.

**The opencode capture.** Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call (the `tool`,
`sessionID`, `status`, `input` and `result`/`error` the after-hook reports), and the idle hook appends
a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/.profiler-opencode/<session-id>.jsonl` store, `harness` `"opencode"`, which
`devpro profiler tree` and the dashboard's profiler view render beside the claude sessions', each
record read from its own `.profiler-*` store. A `subagent` or `task` call also records the child session it dispatched, the child's session id
read from the host's result where the host reports it — the place moves with the host: opencode
2.4.1 reports the id at the result's top level (`result.sessionID`), 2.3.2 in `output.sessionID`
and 2.3.0 in `metadata.sessionID`, and the capture reads them in that order, each under the host's
own string guard: that id fills the record's `child_agent_id`, where the index groups the child one
level under its dispatcher — the tree, on the session's page, drawing the dispatch as a context —
and the dispatch links to the child's page. The stores stay flat — the child's id reaches no
capture as a parent key, the hierarchy being what the parent's records state — and a dispatch that
fails before creating a child, or whose result reports no child session, records none. Records a
capture wrote before the capture read 2.4.1's shape carry the child's id only in their stored
result text; a one-shot repair, run before the installation updates, reads each standing subagent
record's result text and fills its `child_agent_id` where the host reported it — a record whose
id is already right stays untouched, and every edge a capture writes after the update is correct
at write time. The repair is `devpro profiler repair`, run once from the project's root: it reports
`repaired: <n> edges; null: <m> records (result clipped)` — the edges it filled and the subagent
records left naming no child, their result text clipped before the id survived — and a file a
capture appends to while the repair reads it is named on stderr and left as it stands, never
rewritten under a session's own write.
The model's own `todowrite` notes are not recorded: they are not activity, so the store holds one
record per tool call that did something. A capture that fails raises nothing out of the hook. `init`
and `doctor` stay claude-facing: opencode has no committed-hook concept. The install ships the
profiler's launcher under opencode too: `_CROSS_HARNESS_SOURCES` carries claude's
`claude/profiler` directory to opencode's `profiler/`, so an opencode project install holds
`profiler/hp.sh` beside the plugin's `profiler.ts`, and the profiler skill's first finder
candidate resolves it. The payload is copied, not wired: opencode registers no hook entry, so no
committed copy arises, and the store the plugin writes is read by `profiler tree` run through the
launcher, whose finder takes the installation's wrapper first. One line holds one record, and the limits that keep it so are
`devpro/profiler/values.py`'s: `NAME_LIMIT`,
`ARGS_LIMIT` and `RESULT_LIMIT` clip a field's text as the Python capture clips it, and `LINE_LIMIT`
bounds the written line in bytes, `name` and `session` clipped at the root before `result` and `args`
gives way.
A line a killed process left torn would fuse the next record onto it, so an append finds the last
newline in the file's tail and truncates to it, renaming the whole store aside where the file holds
no newline at all. The Python capture has no such repair: it appends as it stands, and its reader
skips the torn line. An opencode record carries no token counts, so the tree's token columns are blank for
its sessions; claude's counts come from its own transcripts under `~/.claude/projects/`, which is
claude's data, not a source the install configures. An opencode record's `branch` is empty on its own
account: the capture runs in the host's process, and the hooks report no branch, so `tree --branch`
selects no opencode session.

**The stores and their rename.** Each harness's capture owns one store under the project's
`.devpro-temp/`: claude's `.profiler-claude/`, opencode's `.profiler-opencode/`, and both readers —
`tree`'s render, and the dashboard's profiler view, whose index and session pages read the stores per
request — walk every `.profiler-*` directory there — a dot name, so the stores group
and sort at the top of the scratch tree. The naming before the rename was `<store>-profiler`, and
both `devpro install` and `devpro profiler init claude` migrate the two stores it named:
`.devpro-temp/claude-profiler/` is renamed to `.profiler-claude` and
`.devpro-temp/opencode-profiler/` to `.profiler-opencode`, and the move is printed. A directory
under `.devpro-temp/` whose name only ends in `-profiler` is no store and is left alone. Where a
store's new name is already taken, the old one is left in place and named instead — the stores'
contents are never merged, and merging or deleting the old store is the operator's call. A second
run touches nothing. The window between the upgrade's first capture and the install that follows it
exists: captures write `.profiler-*` while an old-pattern store still holds its traces, so `tree`
cannot read that store until the migration runs. The skip-and-name case above is where the window
does not close — the old store is left standing and named, and at the migration's end one store name
per harness stands with its traces readable under it, or the operator is told which store was left
behind.

**Doctor's lines.** `devpro profiler doctor` reports `devpro:` the executable the launcher's finder
would resolve, by the search the launcher makes — the installation's wrapper first, found by
existing alone, and then the one `command -v` — and probes the command found with `--version`, as
the launcher probes it, naming it `unusable: "<path>" does not run` where the probe fails.
It reports one such line for each launcher standing in the repository — the committed hook's
and a claude project install's, `INSTALLED_LAUNCHER` — each walking that launcher's own wrapper
candidates, and where none stands one line from the `command -v` search alone — or `not found in the installation, on PATH, in Homebrew or ~/.local/bin (install devpro)` — `traces:` the
claude store `tree` reads beside the `.profiler-*` pattern, `hook:` where a capture hook is
registered here (the plugin's own records, and the committed, local and user settings files) or
`not installed` with the install and `init` remedies, an `old:` line per pre-rename store it cannot
read with the remedy that renames or merges it, `update:` a stale committed hook, and `newest:` the
newest claude session's last moment or `no calls recorded yet`. Doctor is claude-facing: every line
reads claude's hook and claude's store, where `tree` reads both harnesses'.
