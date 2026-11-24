# The profiler's pages read true and the toolchain checks what ships

The profiler's served pages show what the records hold: moments read the reader's local time in
one notation, drawn where the data is born; the index's headers sit over their columns and its
controls survive navigation; a dispatch's child edges form on the host's moving shape, and the
standing records recover theirs. The shipped TypeScript resources are type-checked against the
host's published surface — by `just lint`, which cannot pass a page the browser would reject — for
the maintainer reading the board and the traces it serves.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The
summary text is not to be consistency checked. The design is authoritative.

## ARCHITECTURE delta

### [Recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md)

**As it stands:**

```
`just lint` needs `shellcheck` on
`PATH`, and where it is absent the recipe fails, naming it, rather than skip the shell check.
```

**Becomes:**

```
`just lint` needs `shellcheck` on
`PATH`, and where it is absent the recipe fails, naming it, rather than skip the shell check.
`just lint` also type-checks what ships: the opencode harness's shipped TypeScript resources
(`index.ts`, `guardrail.ts`, `profiler.ts`) through `bunx tsc --noEmit` under a `tsconfig`, checked
against the host's published declarations — `@opencode/plugin`'s own types are the authority, no
devpro-owned stand-in for a published package shadows them. The declarations reach the check as a
dev-time dependency installed before `tsc` runs — a root `package.json` holds it — and the check
reads what ships: the host's transitive declarations are not this check's mandate, `skipLibCheck`
keeping the program over the resources. The compiler rides unpinned — `bunx` takes the latest at
run time. The check's mandate is what
ships: the test runners' TypeScript is dev-time only and outside it.
```

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```
the index of record files, every store
the `.profiler-*` glob finds, one row per session — harness, session id, record count, first and
last moments, and the span between them — each linking to `/page/<session-id>`, which serves that
session's page in memory, the render's page carrying the same page data `tree --format html`
produces.
```

**Becomes:**

```
the index of record files, every store
the `.profiler-*` glob finds, one row per session — harness, session id, record count, the count
of the dispatched agents it holds, first and last moments, and the span between them — each
linking to `/page/<session-id>`, which serves that session's page in memory, the render's page
carrying the same page data `tree --format html` produces.
```

**As it stands:**

```
The index carries simple
controls — child-record rows on and off, claude and opencode on and off separately, and column
heads sorting on the dispatched-agent count, the record count, the time and the span — and a
failed feed names itself: an in-page notice naming the feed's failure, distinct from the
no-records state a zero-record store renders.
```

**Becomes:**

```
The index carries simple
controls — child-record rows on and off, claude and opencode on and off separately, and column
heads sorting on the dispatched-agent count, the record count, the time and the span — and a
failed feed names itself: an in-page notice naming the feed's failure, distinct from the
no-records state a zero-record store renders. The controls' state and the sort in force live in
the index page's URL — its query carries what the reader chose, so leaving the view and returning
restores it — and the URL is a link the reader can copy.
```

**As it stands:**

```
A `subagent` or `task` call also records the child session it dispatched, the child's session id
read from the host's result where the host reports it — opencode 2.3.2's `result.output.sessionID`
is that place: that id fills the record's `child_agent_id`, where the index groups the child one
level under its dispatcher — the tree, on the session's page, drawing the dispatch as a context —
and the dispatch links to the child's page.
```

**Becomes:**

```
A `subagent` or `task` call also records the child session it dispatched, the child's session id
read from the host's result where the host reports it — the place moves with the host: opencode
2.4.1 reports the id at the result's top level (`result.sessionID`), 2.3.2 in `output.sessionID`
and 2.3.0 in `metadata.sessionID`, and the capture reads them in that order, each under the host's
own string guard: that id fills the record's `child_agent_id`, where the index groups the child one
level under its dispatcher — the tree, on the session's page, drawing the dispatch as a context —
and the dispatch links to the child's page.
```

**As it stands:**

```
The stores stay flat — the child's id reaches no
capture as a parent key, the hierarchy being what the parent's records state — and a dispatch that
fails before creating a child, or whose result reports no child session, records none.
```

**Becomes:**

```
The stores stay flat — the child's id reaches no
capture as a parent key, the hierarchy being what the parent's records state — and a dispatch that
fails before creating a child, or whose result reports no child session, records none. Records a
capture wrote before the capture read 2.4.1's shape carry the child's id only in their stored
result text; a one-shot repair, run before the installation updates, reads each standing subagent
record's result text and fills its `child_agent_id` where the host reported it — a record whose
id is already right stays untouched, and every edge a capture writes after the update is correct
at write time.
```

**As it stands:**

```
The deco's one script is named by the board page as
its own file, and the profiler's pages link the same file; the band's legend with its
`Return to list` control on a session's page.
```

**Becomes:**

```
The deco's one script is named by the board page as
its own file, and the profiler's pages link the same file; the band's legend with its
`Return to list` control on a session's page. Every script the pages run — the deco's and the
templates' own — wraps its body in an IIFE: its helpers are module-private, and the deliberate
surface is only what the page calls, because classic scripts share one global scope and a helper
redeclared across scripts is a page that drew nothing.
```

**As it stands:**

```
(`LAYER_MARK`), which `render_html` fills with the presentation layer's text inline — the board's
own stylesheet, `devpro/kanban/assets/board.css`, read the same way — for the standalone page,
which loads nothing from the network and so cannot link it, and which the serve path
(`served_page`) fills with a link to that stylesheet.
```

**Becomes:**

```
(`LAYER_MARK`), which fills with the presentation layer one way per carrier — the page's one
rendering, two carriers: the dashboard's serve path (`served_page`) links the board's own
stylesheet, `devpro/kanban/assets/board.css`, and `render_html` — `tree --format html`'s
carrier — fills the layer's text inline, the one difference a file cannot avoid, being unable to
link a server's origin. What the dump writes is the page the dashboard serves: one template, one
script, one band, one presentation.
```

**As it stands:**

```
The moments are the raw UTC where no script runs; with it, every moment the pages and their
headers show — the moments cells, the index's first-to-last line, the session page's header stamp —
reads in the reader's local time, 24-hour, one notation, the machine form only in the `<time>`
elements' `datetime` attributes and the raw UTC in the titles. A first-to-last whose ends share the
reader's day reads as two times with no date; one crossing midnight reads with the date on its first
end alone and the finish end time only, the next day's being obvious.
```

**Becomes:**

```
The pages' own scripts draw every moment local at birth — the moments cells, the index's
first-to-last line, the session page's header stamp — in the reader's local time, 24-hour, one
notation: the first end of a pair carries its date whole beside its time, the second its time
only, the clock's being 24-hour making a span across midnight plain by the numbers, no branch to
state. The machine form stands in the `<time>` elements' `datetime` attributes and the raw UTC in
the titles; a page carries no moments where its script does not run, and the deco reads none — the
moment sweep and its observers leave with the double render they served.
```

**As it stands:**

```
A session's page carries its dispatcher in the frame band, linked to that
session's page, where one dispatched it, and an Agent row links to the child session's page where
the record names one:
```

**Becomes:**

```
A session's page carries its dispatcher in the frame band, linked to that
session's page, where one dispatched it, and a call row whose tool is `Agent` links to the child
session's page where the record names one:
```

**As it stands:**

```
A store the glob finds but cannot read appears in the index as unreadable —
the server raises nothing for it; a store whose files the glob finds but whose trace cannot be read
is stated in the feed as unreadable, like the store that could not be read at all.
```

**Becomes:**

```
A store the glob finds but cannot read appears in the index as unreadable —
the server raises nothing for it.
```

**As it stands:**

```
**Resources.** One file lives in `devpro/harnesses/resources/claude/profiler/`:
`profiler.sh`, the bash launcher, which runs the wrapper beside it with the `profiler` verb. Every
site spelling the launcher's file name renames with it — the hook wiring's script path, the
skill's finder and its `PROFILER` line, the init's copy and its unlinks, the doctor's compares. It carries the `!INSTALLED! … devpro` banner within its
first ten lines — the banner rule binds every harness resource — and `harness_resource_copies` lands
it at the path it holds below the install directory, so the install directory gains
`profiler/profiler.sh`. Its source is claude's: mage ships no resources, and an opencode install carries
the same file, below, though opencode's capture is the plugin's own TypeScript.
```

**Becomes:**

```
**Resources.** No file lives in `devpro/harnesses/resources/claude/profiler/` — the directory is
gone. `init` removes the committed launcher it once wrote into the repository's
`.claude/harness-profiler/` beside the `hp.sh` names its machinery already carries, and the
install's copy step removes the installed tree's `profiler/profiler.sh` unconditionally, where the
pairing machinery names no replacement to pair it with.
```

The leaf's **The launcher's finder.** passage is deleted: the launcher's resolution is no longer
the leaf's subject — the wiring and the skill name their wrappers, and the never-block contract
moves to the capture subcommand.

**As it stands:**

```
**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `/bin/bash "${CLAUDE_PLUGIN_ROOT}/profiler/profiler.sh" capture claude`, and the launcher's
file name is the one change a committed hook written under its former `hp.sh` inherits: the hook stays
this tool's own, and `init`'s re-run renames it, the registered command with it. The wiring
is data in the harness module, not a new mechanism, and no entry is gated on the install-time probe. A
capture appends one line to the project's `.devpro-temp/.profiler-claude/<session-id>.jsonl` — one of
the per-harness stores under `.devpro-temp/`, every `.profiler-*` directory of which the `tree`
subcommand renders — the project's scratch directory, which the project's own convention gitignores; a
capture that fails, or finds no wrapper beside the launcher, exits 0 with nothing on the hook's
stdout, the wrapper's own failure named on stderr.
```

**Becomes:**

```
**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running the installed wrapper — `<install-dir>/tools/devpro.sh profiler capture claude`, the path
`INSTALLED_WRAPPER` holds — as the hook's command, the launcher's path and the launcher constants
gone. The wiring
is data in the harness module, not a new mechanism, and no entry is gated on the install-time probe. A
capture appends one line to the project's `.devpro-temp/.profiler-claude/<session-id>.jsonl` — one of
the per-harness stores under `.devpro-temp/`, every `.profiler-*` directory of which the `tree`
subcommand renders — the project's scratch directory, which the project's own convention gitignores.
The wrapper's
`capture` subcommand owns the never-block contract: its read of the hook payload is bounded, it
exits 0 on every path, and the capture's child runs with its stdout off the hook's stdout.
```

**As it stands:**

```
**The skill.** `profiler` ships as a rendered skill definition under `devpro/definitions/`, so it
carries the generated banner and the harness's namespace (`devpro:profiler` under claude) and
renders under every harness. Its finder's first candidate, `../../profiler/profiler.sh` from
the skill's directory, resolves to `<install-dir>/profiler/profiler.sh` where the payload landed — the
launcher that runs the wrapper beside it — and its second, the committed `.claude/harness-profiler/profiler.sh`,
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
`.claude/harness-profiler/profiler.sh` — the harness resource the devpro package ships, readable as
`devpro.profiler.hooks.launcher_resource()` and marked executable — and the rendered skill, then
unlinks the launcher an older `init` wrote under its former name, `hp.sh`, and the files an older
`init` left beside the launcher: `hp.py` and `view.html`, which no install ships any more — and the
skill an older `init` rendered under its former name,
`.claude/skills/show-profile/SKILL.md`, with its directory where that leaves it empty.
A hook committed by an older `init` therefore keeps working: it runs `hp.sh`, which still finds a
devpro; `init`'s re-run renames the hook to the launcher's current name, and the install's update
runs after that rename. `doctor`'s `update` line names a committed hook that lacks an event, is not `async`,
or differs by a byte from the launcher's resource the devpro package ships — that resource is the
master, and the compare reads it without needing an install directory.
```

**Becomes:**

```
**The skill.** `profiler` ships as a rendered skill definition under `devpro/definitions/`, so it
carries the generated banner and the harness's namespace (`devpro:profiler` under claude) and
renders under every harness. Its `Locate the profiler` block states one wrapper as the writer's
knowledge — the project's committed wrapper where `init` rendered the skill, the installation's own
where the install rendered it — and where neither rendering applies, the skill says the tool is not
installed. A user-level install renders the skill and copies no resource, so there it is the
committed wrapper or the absence. `init` renders the same skill into the repository's
`.claude/skills/profiler/SKILL.md` from the definition.

**Limits, stated.** The `doctor` subcommand greps the name `harness-profiler` in claude's
installed-plugin records and will not recognize the payload copy; its committed-hook and
settings-hook checks still find a committed one. The limitation is stated, not fixed. Claude Code on
the web sends the same hook data but loads no plugin's hooks, so a cloud session records nothing
until the hook is committed to the repository; the `init` subcommand does that, writing the rendered
skill into the repository's `.claude/` and merging the six entries into its
`.claude/settings.json`, the committed hook's command naming the project's committed wrapper.

**What `init` copies, and what it removes.** `init claude` writes the repository's rendered skill
and merges the six hook entries — each command naming the committed wrapper
`.claude/skills/devpro/tools/devpro.sh` — then unlinks the launchers an older `init` wrote into the
repository: the one under its former name, `hp.sh`, the launcher's later name,
`.claude/harness-profiler/profiler.sh`, and the files an older `init` left beside the launcher,
`hp.py` and `view.html`, which no install ships any more — and the skill an older `init` rendered
under its former name, `.claude/skills/show-profile/SKILL.md`, with its directory where that leaves
it empty. A hook committed by an older `init` therefore keeps working: its command runs the
committed wrapper from the project root. `doctor`'s `update` line names a committed hook that lacks
an event, is not `async`, or differs by a byte from the wiring the devpro package registers — the
registered wiring is the master, and the compare reads it without needing an install directory.
```

**As it stands:**

```
A capture that fails raises nothing out of the hook. `init`
and `doctor` stay claude-facing: opencode has no committed-hook concept. The install ships the
profiler's launcher under opencode too: `_CROSS_HARNESS_SOURCES` carries claude's
`claude/profiler` directory to opencode's `profiler/`, so an opencode project install holds
`profiler/profiler.sh` beside the plugin's `profiler.ts`, and the profiler skill's first finder
candidate resolves it. The payload is copied, not wired: opencode registers no hook entry, so no
committed copy arises, and the store the plugin writes is read by `profiler tree` run through the
launcher, which runs the installation's wrapper beside it.
```

**Becomes:**

```
A capture that fails raises nothing out of the hook. `init`
and `doctor` stay claude-facing: opencode has no committed-hook concept. The install ships no
launcher under opencode: `_CROSS_HARNESS_SOURCES` drops the cross-harness entry, and an opencode
project install holds only the plugin's `profiler.ts`. The payload is copied, not wired: opencode
registers no hook entry, so no committed copy arises, and the store the plugin writes is read by
`devpro profiler tree` — the wrapper's own subcommand.
```

**As it stands:**

```
**Doctor's lines.** `devpro profiler doctor` reports `devpro:` the wrapper the launcher would run —
the first candidate standing beside it, resolved as the launcher resolves it, with no probe and no
`PATH` search: a command the launcher would not run, the `devpro` on `PATH` among them, is never the
line's answer, and where no candidate stands beside a launcher the line says so, the launcher's
capture exiting 0 without recording.
It reports one such line for each launcher standing in the repository — the committed hook's
and a claude project install's, `INSTALLED_LAUNCHER` — and where none stands in the repository, one
line naming the `devpro` command on `PATH` — or `not found on PATH (install devpro)` — `traces:` the
claude store `tree` reads beside the `.profiler-*` pattern, `hook:` where a capture hook is
registered here (the plugin's own records, and the committed, local and user settings files) or
`not installed` with the install and `init` remedies, an `old:` line per pre-rename store it cannot
read with the remedy that renames or merges it, `update:` a stale committed hook, and `newest:` the
newest claude session's last moment or `no calls recorded yet`. Doctor is claude-facing: every line
reads claude's hook and claude's store, where `tree` reads both harnesses'.
```

**Becomes:**

```
**Doctor's lines.** `devpro profiler doctor` runs as the wrapper's own subcommand, and its
`devpro:` line names the wrapper that runs it — one line: `traces:` the
claude store `tree` reads beside the `.profiler-*` pattern, `hook:` where a capture hook is
registered here (the plugin's own records, and the committed, local and user settings files) or
`not installed` with the install and `init` remedies, an `old:` line per pre-rename store it cannot
read with the remedy that renames or merges it, `update:` a stale committed hook, and `newest:` the
newest claude session's last moment or `no calls recorded yet`. Doctor is claude-facing: every line
reads claude's hook and claude's store, where `tree` reads both harnesses'. The launcher's
resolution stand-ins in the profiler's tests assert the one path: the `devpro:` line names the
wrapper that runs the doctor.
```

**As it stands:**

```
The index's page file is static — no row is in its text — and its script fetches the
records' feed the server answers at `/api/traces`, one JSON entry per session with the columns
above, the stores the glob finds but cannot read among them as unreadable, and renders the rows
client-side — the board's pattern, the payload consumed client-side.
```

**Becomes:**

```
The index's page file is static — no row is in its text — and its script fetches the
records' feed the server answers at `/api/traces`, one JSON entry per session carrying its keys —
`harness`, `id`, `records`, `agents`, `first`, `last`, `span`, and `dispatcher` where a session
was dispatched — keys the index's script renders into the columns the header names: `harness` and
`records` carry their own names, `id` the session column, `agents` the dispatched-agents count,
`first` and `last` the first-to-last line, `span` the span column, and `dispatcher` no column at
all, drawing the child row under its dispatcher's row. Where the feed holds no session and no
unreadable store it is one `stores` entry naming how many stores the glob found. The stores the
glob finds but cannot read are among the entries as unreadable, and the script renders the rows
client-side — the board's pattern, the payload consumed client-side.
```

**As it stands:**

```
Its subcommands are `capture`, `tree`,
`init` and `doctor`, which read exactly as they did inside `hp.py`; the records are served by the
`dashboard` verb, below.
```

**Becomes:**

```
Its subcommands are `capture`, `tree`,
`init`, `doctor` and `repair`; the records are served by the `dashboard` verb, below.
```

**As it stands:**

```
moment sweep and its observers leave with the double render they served. The span is its own
column.
```

**Becomes:**

```
moment sweep and its observers leave with the double render they served. The span is its own
column, drawn from the feed's seconds as whole hours and minutes — `3h 2m` — minutes and seconds
below the hour — `3m 20s` — seconds below the minute, and `0s` for a zero-length span.
```

### [Why there is no verification verb](PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md)

**As it stands:**

```
(`tests/guardrail_ts_runner.ts` loads the opencode guardrail outside
`bun test`, with its package import stubbed), and asserts each implementation's reason equals the
table's.
```

**Becomes:**

```
(`tests/guardrail_ts_runner.ts` loads the opencode guardrail outside
`bun test`, with its package import stubbed), and asserts each implementation's reason equals the
table's. A runner that runs a page's scripts runs them all in one shared scope, the way the
browser executes a page — classic scripts share one global scope — so a redeclaration the browser
throws on, the run throws on too.
```

### [Repo layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

**As it stands:**

```
The package's modules depend one way: `kanban/` imports `doccheck/` and `dicing`'s modules,
`doccheck/` imports `dicing`'s, `profiler/` reads `kanban/`'s stylesheet as package data,
```

**Becomes:**

```
The package's modules depend one way: `kanban/` imports `doccheck/` and `dicing/`,
`doccheck/` imports `dicing/`, `profiler/` reads `kanban/`'s stylesheet as package data,
```

## Code delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

The harness-union comment above the index template's style block in `devpro/profiler/pages.py`
still counts the union's spellings at two — "the style block's two harness rules and that list
change together" — where the union is now spelled three ways: the feed's name, the controls' box
ids and the style rules. The comment beside `HARNESSES` already counts the three; the older
comment's counting clause leaves, deferring the union's one declaration to it — against the
leaf's statement that the index carries the harness controls, which the union's keeping-in-step
serves. Nothing is applied to the leaf.

The capture's `childSessionOf` in `devpro/harnesses/resources/opencode/profiler.ts` reads the
child's id where the host reports it — `result.sessionID` first, then `output.sessionID`, then
`metadata.sessionID`, each under the host's own string guard — matching the leaf's amended
statement. The one-shot repair is written to the scope the leaf states: every standing record,
once, before the installation updates, idempotent over a record whose id is already right; its
mechanics are the plan's.

The pages' scripts — the deco's and the templates' own — wrap their bodies in an IIFE: helpers
module-private, the deliberate surface only what the page calls. The board's and the profiler's
served pages draw as before; the leaf's new sentence holds.

The moment rendering moves to the pages' own scripts: the index script's moments cells and the
session page's header stamp (`view.html`'s script) draw local at birth — first end date whole
beside its time, second end time only, 24-hour — and the `<time>` title keeps the raw UTC. The
deco's moment pass leaves whole — `readMoments`, the `MOMENTS` selector and both moment observers —
with the double render it served; the deco's state indicator and stop are untouched. The leaf's
amended statement holds.

### [The clauses module](devpro/clauses.py)

The profiler skill's finder clause states one wrapper as the writer's knowledge — the tree's own,
filled where the skill is rendered — where the shared `WRAPPER` clause (the guide's and docdicer's)
keeps its resolution: the ruling covers the profiler's runner.

**As it stands:**

```
WRAPPER_PROFILER = f"""`DP` below is the installation's wrapper, the first of these that exists: {_WRAPPER_FROM_SKILL}, or `{PROJECT_WRAPPER}` at the project root. {_WRAPPER_RUN}"""
```

**Becomes:**

```
WRAPPER_PROFILER = f"""`DP` below is the tree's own wrapper, `{PROJECT_WRAPPER}` — filled with the wrapper's path in the tree the skill ships in. {_WRAPPER_RUN}"""
```

### [Why there is no verification verb](PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md)

The profiler pages' runners execute all of a page's scripts in one shared scope, the way the
browser executes a page — classic scripts share one global scope — so a redeclaration the browser
throws on, the run throws on too. The leaf's new sentence holds.
