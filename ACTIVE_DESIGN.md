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
keeping the program over the resources. The compiler rides unpinned — `bunx` takes the latest at run time,
and pinning it is a later decision the project has not yet needed. The check's mandate is what
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
`hp.sh`, the bash launcher, which finds a devpro — the installation's own wrapper first — and
runs its `profiler` verb (no environment variable overrides the search).
```

**Becomes:**

```
**Resources.** One file lives in `devpro/harnesses/resources/claude/profiler/`:
`profiler.sh`, the bash launcher, which runs the wrapper beside it with the `profiler` verb. Every
site spelling the launcher's file name renames with it — the hook wiring's script path, the
skill's finder and its `PROFILER` line, the init's copy and its unlinks, the doctor's compares.
```

**As it stands:**

```
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
```

**Becomes:**

```
**The launcher's finder.** The launcher resolves the wrapper beside it — `../tools/devpro.sh` from
`<install-dir>/profiler/profiler.sh`, and `../skills/devpro/tools/devpro.sh` from the committed
`.claude/harness-profiler/profiler.sh` — and runs it as a child with the `profiler` verb and the
launcher's own arguments passed through. The first candidate standing is the one that runs: there
is no probe and no `PATH` search, a foreign devpro is never run, and every failure is named by the
wrapper's own refusal — a capture whose wrapper fails drains its stdin and exits 0, never blocking
the tool call.
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

### [Why there is no verification verb](PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md)

The profiler pages' runners execute all of a page's scripts in one shared scope, the way the
browser executes a page — classic scripts share one global scope — so a redeclaration the browser
throws on, the run throws on too. The leaf's new sentence holds.
