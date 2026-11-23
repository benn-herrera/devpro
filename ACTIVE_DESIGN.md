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

### The index's column headers do not sit over their columns

The header row drifts out of alignment with the body's columns — "records", "dispatched agents",
"first to last" and "span" do not sit over the cells they name. The header is likely a separate
element from the body's rows (the body is drawn by script into its own `tbody`), so whatever widths
the body's cells take are not shared with the header's.

### The index's controls and sort reset when the view leaves and returns

The selector checkboxes (child rows, claude, opencode) and the column sort do not stick: going into
a session's details view and coming back brings the index back to its defaults. The controls' state
lives only in the page's script, so a re-navigation re-draws the page and reads nothing — the state
wants either persistence (the URL's query, or `sessionStorage`) or the view to survive the
round-trip.

### No TypeScript type check

`devpro/harnesses/resources/opencode/index.ts`, `guardrail.ts` and the `tests/*.ts` runners are
never type-checked: there is no `tsconfig` and no recipe. A recipe needs a declaration stub for
`@opencode/plugin`.
