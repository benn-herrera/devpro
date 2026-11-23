# ACTIVE DESIGN

## Drafts

### The profiler's post-plan leftovers

The items the active plan deferred as it landed, collected where a later reader finds them: R9's
type-check of the opencode resources — upstream's own packaging lags its runtime (`ctx.tool.hook`
is wider than any published or client-installed surface; the host source's `packages/plugin` has
`tool: ToolDomain`), and the check lands when the host publishes what its runtime provides, with
no devpro-owned types; the leaf amendments R16 and R17's leaf halves — a design revision, the
user's; the three proposed CONVENTIONS leaves R23/R24/R25 — a JS stand-in models the API's real
semantics, a shipped resource is checked against the host's declarations, a formatted-time test
pins the locale beside `TZ`; the `UNREADABLE` twin (`plancheck.py` / `kanban/server.py`); the
installed plugin payload's `dicerlib` imports, cleared by a reinstall; and the capture's third
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
