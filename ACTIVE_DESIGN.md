# ACTIVE DESIGN

## Drafts

### The profiler's post-plan leftovers

The items the active plan deferred as it landed, collected where a later reader finds them: R9's
type-check of the opencode resources — upstream's own packaging lags its runtime (`ctx.tool.hook`
is wider than any published or client-installed surface; the host source's `packages/plugin` has
`tool: ToolDomain`), and the check lands when the host publishes what its runtime provides, with
no devpro-owned types; R17's halves closed into the entries below at the owner's smallest-wording
call; R16's leaf catch-up is sequenced after this plan's code-shaping packages land, drafted from
measurement — the owner's call; R23/R24/R25, the three proposed CONVENTIONS leaves, ruled: R24 lands as
its own package — a shipped resource naming a host version is type-checked against that host's
published declarations, never against a devpro-owned stub for a published package, the rule
binding future resources while R9's enforcement waits for the host to publish; R23 rides the
runner-fidelity package, R25 rides R16's leaf catch-up; and the capture's third
host shape: on opencode 2.4.1 the dispatch result carries the child's id at the result's top level
(`result.sessionID`, beside an `output` array — `packages/core/src/tool/plugin/subagent.ts:19-26,47-49`),
where the capture reads `output.sessionID` first and `metadata.sessionID` beside it (2.3.2 and
2.3.0). Live records on 2.4.1 record no child, the id surviving only in the result text — R9's
type-check against the host source would have flagged the move the day it happened. And the second
instance of the runners' shared-scope blindness: B2's `pad` helper in `deco.js` redeclared the
inline scripts' `pad` — classic scripts share one global scope, so the index and session pages
threw `redeclaration` and drew nothing, invisible to runners that execute one script each. The fix
the design owns: each page script's body wrapped in an IIFE (module-private helpers, a deliberate
surface only), and the runners executing all of a page's scripts in one shared scope the way the
browser does. On the user's direction:
the forensic child-tie repair runs one last time over the profiler records written since the last
repair, before the installation is updated — the capture fix makes every edge after that correct.

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
(`index.ts`, `guardrail.ts`) through `bunx tsc --noEmit` under a `tsconfig`, with a declaration
stub for `@opencode/plugin`. The compiler rides unpinned — `bunx` takes the latest at run time,
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
the `.profiler-*` glob finds, one row per session — harness, session id, record count, first and
last moments, and the span between them — each linking to `/page/<session-id>`, which serves that
session's page in memory, the render's page carrying the same page data `tree --format html`
produces. The header row and the body's rows take their column widths from one source, so every
header sits over the column it names at every width the data produces.
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
