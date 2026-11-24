# ACTIVE PLAN — the profiler's pages read true and the toolchain checks what ships

## Lifetime

Every package is shipped.

## Design

ACTIVE_DESIGN.md — accepted. Its entries are the packages' targets, applied verbatim; the pairs'
becomes-blocks are the accepted text.

## Status

| Package | State | Rating | Scope |
|---|---|---|---|
| P1 | drafted | expert | the shipped TypeScript resources are type-checked; R24's rule enters CONVENTIONS |
| P2 | drafted | expert | the index's display: header widths from one source, controls state in the URL |
| P3 | drafted | expert | the capture reads 2.4.1's shape; the one-shot child-tie repair runs before the install updates |
| P4 | drafted | expert | R17's wording halves: the Agent row's referent, the unreadable store stated once, the union comment defers |
| P5 | drafted | expert | moments local at birth; the deco's moment pass leaves; one rendering, two carriers |
| P6 | drafted | expert | `profiler.sh` renames `hp.sh`; the finder runs the wrapper bare; R23's rule enters CONVENTIONS |
| P7 | drafted | expert | R25's rule rides R16's catch-up (this package's tail) |
| P8 | drafted | expert | R16's leaf catch-up, drafted from measurement after P2 and P5 land |
| R | drafted | expert | the post-plan review, five seats |
| B | drafted | expert | the post-plan burndown, drafted from the review document |

## Kickoff

The design was accepted with its six entries; the pairs' becomes-blocks are applied verbatim by the
packages below. The plan carries what design deltas do not: the R23/R24/R25 CONVENTIONS leaves
(ruled: R24 its own package — P1; R23 rides P6; R25 rides P8), R16's catch-up sequenced after this
plan's code-shaping packages land — P8, drafted from measurement — R9 deferred to the host's move
(recorded in ROADMAP.md by P3), and the repair's one-shot ordering (P3): every standing record,
once, before the installation updates.

P2 and P5 land before P8 is drafted: R16's leaf catch-up is measured against the code as it lands,
not as it stands today. P3's repair runs once, before the installation is refreshed — every capture
written after P3's capture lands is correct at write time.

## P1 — the shipped TypeScript resources are type-checked

Scope: `devpro/profiler/view.html`-carried scripts excluded; `devpro/harnesses/resources/opencode/index.ts`,
`guardrail.ts` type-checked; a `tsconfig.json` at the repository root; a declaration stub for
`@opencode/plugin` beside the resources; `just lint` runs `bunx tsc --noEmit` after the shell check;
R24's leaf enters `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/` — a shipped resource naming
a host version is type-checked against that host's published declarations, never against a
devpro-owned stub for a published package. The compiler is unpinned — `bunx` takes the latest at run
time; the test runners' TypeScript is dev-time only and outside the check.

Applies the design's [Recipes] pair verbatim to `PROJECT_DOCS/ARCHITECTURE/recipes.md`.

Done-line: `just lint` passes with the type check live on the two resources; `just test devpro`;
the declaration stub's import surface matches the resource's imports. The unpinned compiler is the
ruled state — pinning is a later decision.

## P2 — the index's display

Scope: `devpro/profiler/pages.py` (the index template's script and the deco), `tests/` pins that
draw the served index. The pairs applied: header widths from one source — every header sits over the
column it names at every width the data produces — and the controls' state with the sort in force
carried in the index page's URL query, restored on leaving and returning, the URL a copyable link.

Applies the design's [Harness profiler] pairs two and three verbatim.

Done-line: `just test devpro` — a pin fails on the pre-P2 template for each behavior (the header
pin on a template whose widths drift; the state pin on a re-navigation), and passes on P2's tree.
The two foreign `devpro-dashboard` recipe pins are the expected failures.

## P3 — the capture reads the host's moving shape; the one-shot repair

Scope: `devpro/harnesses/resources/opencode/profiler.ts` (`childSessionOf`: `result.sessionID`
first, then `output.sessionID`, then `metadata.sessionID`, each under the host's own string guard),
the one-shot repair over the standing stores, and the leaf pairs. The repair: run once, before the
installation is refreshed — every standing opencode record's result text read, its
`child_agent_id` filled where the host reported it, a record whose id is already right untouched.
R9's deferral is recorded in `ROADMAP.md`: the type-check of the resources against the host source
lands when the host publishes what its runtime provides.

Applies the design's [Harness profiler] capture and repair pairs verbatim.

Done-line: `just test devpro`; the live capture on this host writes `child_agent_id` for a dispatch;
the repair's one-shot run reports the edges recovered and the records left null (clip-eaten ids) —
the recoverable set measured, not asserted.

## P4 — R17's wording halves

Scope: `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` — "an Agent row" becomes "a call row
whose tool is `Agent`"; the unreadable store's three statements collapse to the two the leaf keeps.
Scope: `devpro/profiler/pages.py` — the harness-union comment above the style block defers its count
to the `HARNESSES` comment's three.

Applies the design's [Harness profiler] R17 pairs and the [Why there is no verification verb]
pair-skip: the comment fix is the Code delta's, held to the leaf.

Done-line: `just test devpro`; the leaf's amended passages are the design's becomes-blocks.

## P5 — moments local at birth; one rendering, two carriers

Scope: `devpro/profiler/pages.py` — the index script's moments cells and the session page's header
stamp draw local at birth: first end date whole beside its time, second end time only, 24-hour, one
notation — the hand-built clock R8's fix landed; the `<time>` title keeps the raw UTC. The deco's
moment pass leaves whole — `readMoments`, the `MOMENTS` selector, both moment observers — with the
double render it served. One rendering, two carriers: `render_html` and `served_page` differ only in
the layer's carrier — inlined where a file cannot link a server's origin.

Applies the design's [Harness profiler] moments pairs and the Code delta's moment paragraphs
verbatim. R23's leaf rides P6; R16's catch-up is sequenced after this package lands.

Done-line: `just test devpro` — the moments pin fails on the pre-P5 tree (UTC text) and passes on
P5's; the deco's deletion leaves the nav's indicator and stop passing their pins; the dump's page is
the served page's text, the layer its only difference — measured, not asserted.

## P6 — the launcher renames; the finder runs the wrapper bare

Scope: `profiler.sh` replaces `hp.sh` everywhere the launcher is spelled — the resource file and its
opencode cross-harness copy, the hook wiring's script path (`harnesses/claude.py`), the launchers'
finder candidates, the skill's finder, the init's copy and its unlinks, the doctor's compares, the
skill's `HP` line. The finder resolves the wrapper beside it and runs it as a child with the
`profiler` verb — no probe, no `PATH` search, no foreign devpro; every failure named by the wrapper's
own refusal; capture never blocks. R23's leaf enters CONVENTIONS beside R24's: a runner's stand-in
models the API's real semantics, and no test relies on a stand-in being more permissive than the
browser.

Applies the design's [Harness profiler] resources and finder pairs and the [Why there is no
verification verb] pair verbatim.

Done-line: `just test devpro` — the committed-hook pins fail on the pre-P6 launcher name and pass on
P6's; `doctor --update` renames the stale committed hooks it names; the capture on this host writes
a record through the renamed launcher. The rename's consuming-project migration is doctor's, run
before the install refreshes.

## P7 — R16's leaf catch-up, and R25's rule

Scope: `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` and R25's leaf — drafted from
measurement against P2 and P5's landed code: the notations the scripts actually produce, the column
list the index actually draws, the locale the tests actually pin. Sequenced last — the owner's
ruling: drafted from measurement, not from this plan's expectations.

Done-line: `just test devpro`; the leaf's amended passages are the design's becomes-blocks — the
measurements named in the package, taken on the landed tree.

## R — the post-plan review, five seats

The post-plan review, run per the process: the changes and their tests against the project's
standards and fitness for purpose, each seat writing its own review in the scratch directory,
synthesized into the review document.

## B — the post-plan burndown

Drafted from the review document once it lands; its packages get the plan's usual states.
