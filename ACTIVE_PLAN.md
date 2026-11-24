# ACTIVE PLAN — the profiler's pages read true and the toolchain checks what ships

## Lifetime

Every package is shipped.

## Design

ACTIVE_DESIGN.md — accepted. Its entries are the packages' targets, applied verbatim; the pairs'
becomes-blocks are the accepted text.

## Status

| Package | State | Rating | Scope |
|---|---|---|---|
| P1 | landed b715ab6 | expert | the shipped TypeScript resources are type-checked; R24's rule enters CONVENTIONS |
| P2 | landed 2c0563f | expert | the index's display: header widths from one source, controls state in the URL |
| P3 | landed 7a9918c, R9's note 456673f beside it | expert | the capture reads 2.4.1's shape; the one-shot child-tie repair runs before the install updates |
| P4 | landed fe14273 | expert | R17's wording halves: the Agent row's referent, the unreadable store stated once, the union comment defers |
| P5 | landed 83d1049 | expert | moments local at birth; the deco's moment pass leaves; one rendering, two carriers |
| P6 | dispatchable | expert | `profiler.sh` renames `hp.sh`; the finder runs the wrapper bare; R23's rule enters CONVENTIONS |
| P7 | drafted: dispatchable when P2 and P5 land | expert | R16's leaf catch-up, drafted from measurement after P2 and P5 land; R25's rule enters CONVENTIONS |
| R | drafted | expert | the post-plan review, five seats |
| B | drafted | expert | the post-plan burndown, drafted from the review document |

## Kickoff

The R-IDs name the findings they carry:
R9 — the opencode resources' type-check against the host source lands when the host publishes what
its runtime provides; R16 — the leaf's time-notation sentences drift from what the code holds, and
the column lists disagree; R17 — "an Agent row" has no referent, the unreadable store is stated
three times with the middle one weakest, the repo-layout paragraph's grain disagrees with its
neighbours, and the harness-union comment counts two spellings where three exist; R23 — a runner's
stand-in models the API's real semantics; R24 — a shipped resource naming a host version is checked
against that host's published declarations; R25 — a test asserting a formatted time or date pins
the locale alongside `TZ`.

Every before/after done-line measures against `6dccae1`.

The design was accepted with its six entries; the pairs' becomes-blocks are applied verbatim by the
packages below. The plan carries what design deltas do not: the R23/R24/R25 CONVENTIONS leaves
(ruled: R24 its own package — P1; R23 rides P6; R25 rides P7), R16's catch-up sequenced after this
plan's code-shaping packages land — P7, drafted from measurement — R9 deferred to the host's move
(recorded in ROADMAP.md by P3), and the repair's one-shot ordering (P3): every standing record,
once, before the installation is refreshed.

P2 and P5 land before P7 is drafted: R16's leaf catch-up is measured against the code as it lands,
not as it stands today. P3's repair runs once, before the installation is refreshed — every capture
written after P3's capture lands is correct at write time.

## P1 — the shipped TypeScript resources are type-checked

Scope: `devpro/harnesses/resources/opencode/index.ts` — type-checked against the host's published
declarations and its 11 pre-existing type errors fixed to green (`@opencode/plugin` is published;
its own types are the authority, per R24's ruling — no devpro-owned stub for a published package,
and none is built; the base commit's errors are the check's first finding); `guardrail.ts`
type-checked, clean on the base commit; `profiler.ts` in the check's scope — it ships and its drift
is this check's; a `tsconfig.json` at the repository root whose scope covers the resources'
directory only — the test runners' TypeScript is dev-time only and outside it; the declarations
reach the check through the package the resources name, installed as the dev-time toolchain's
dependency; `just lint` runs `bunx tsc --noEmit` after the shell check, where `bun` is a required
tool failing with a named error where absent, as `shellcheck` does; R24's leaf, named
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-host-version-is-checked-against-the-host-s-declarations.md`,
enters beside R24's ruling — a shipped resource naming a host version is type-checked against that
host's published declarations, never against a devpro-owned stub for a published package — and
`index.md` lists it. Scope: `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/harness-resources-are-copied-verbatim.md:27-29`
— the TypeScript sentence's first clause is false once the check lands: the leaf keeps the verbatim
rule and drops the no-type-check premise. The compiler is unpinned — `bunx` takes the latest at run time; the test
runners' TypeScript is dev-time only and outside the check. The edits to the shipped resources are
the resource's own — `harness-resources-are-copied-verbatim.md` stays true: the resource is the
master the copies follow.

Applies the design's [Recipes] pair as revised verbatim to `PROJECT_DOCS/ARCHITECTURE/recipes.md`.

Done-line: `just lint` passes with the type check live — `bunx tsc --noEmit --listFiles` reports
the resource files among its inputs, so an empty program cannot pass; `just test devpro`; the
host's declarations are what the check reads (`@opencode/plugin` resolved from the installed
package, no `declare module` present). The unpinned compiler is the ruled state — pinning is a
later decision.

## P2 — the index's display

Scope: `devpro/profiler/pages.py` (the index template's script and the deco), `tests/` pins that
draw the served index. The pairs applied: header widths from one source — every header sits over the
column it names at every width the data produces — and the controls' state with the sort in force
carried in the index page's URL query, restored on leaving and returning, the URL a copyable link.

Applies the design's [Harness profiler] pairs two and three verbatim.

Done-line: `just test devpro` — two pins, both new: `test_the_headers_sit_over_their_columns` fails
on the pre-P2 template's header cell narrower than its column at a long session id;
`test_the_url_restores_the_controls_and_sort` fails on a control toggled then the page left and
returned through its own link, reading back toggled-off — and both pass on P2's tree.

## P3 — the capture reads the host's moving shape; the one-shot repair

Scope: `devpro/harnesses/resources/opencode/profiler.ts` (`childSessionOf`: `result.sessionID`
first, then `output.sessionID`, then `metadata.sessionID`, each read through
`typeof === "string"` before the `??` chain, so a non-string at one place falls through to the
next); the one-shot repair, a `devpro profiler repair` subcommand dispatched from
`devpro/profiler/cli.py`, printing `repaired: <n> edges; null: <m> records (result clipped)`; and
the leaf pairs. The repair: run once, before the
installation is refreshed — every standing opencode record's result text read, its
`child_agent_id` filled where the host reported it, a record whose id is already right untouched.
R9's deferral is recorded in `ROADMAP.md`: the type-check of the resources against the host source
lands when the host publishes what its runtime provides.

Applies the design's [Harness profiler] capture and repair pairs verbatim.

Done-line: `just test devpro`; the live capture — one `subagent` dispatch under this host (opencode
v2.4.1), then `jq -r .child_agent_id .devpro-temp/.profiler-opencode/<session>.jsonl` on the
parent's records — returns the child's id, not null; the repair's one-shot run reports the edges
recovered and the records left null (result clipped) — the recoverable set measured, not asserted.
The repair runs after P3's capture is installed and before any further capture on this host.

## P4 — R17's wording halves

Scope: `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` — "an Agent row" becomes "a call row
whose tool is `Agent`"; the unreadable store's three statements collapse to the two the leaf keeps.
Scope: `devpro/profiler/pages.py` — the harness-union comment above the style block defers its count
to the `HARNESSES` comment's three.

## P4 — R17's wording halves

Scope: `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` — "an Agent row" becomes "a call row
whose tool is `Agent`"; the unreadable store's three statements collapse to the two the leaf keeps.
Scope: `devpro/profiler/pages.py` — the harness-union comment above the style block defers its count
to the `HARNESSES` comment's three. Scope: `PROJECT_DOCS/ARCHITECTURE/repo-layout.md` — the
dependency paragraph's grain reaches package grain, `dicing/` beside its neighbours.

Applies the design's [Harness profiler] R17 pairs, the [Repo layout] pair, and the Code delta's
harness-union comment paragraph — nothing applied to the leaf for the comment.

Done-line: `just test` — the docs surface's link check runs over the two rewritten leaves;
`just dev-check-design-deltas-applied` reports P4's pairs landed.

## P5 — moments local at birth; one rendering, two carriers

Scope: `devpro/profiler/pages.py` — the index script's moments cells draw local at birth: first end
date whole beside its time, second end time only, 24-hour, one notation — the hand-built clock R8's
fix landed; the `<time>` title keeps the raw UTC. Scope: `devpro/profiler/view.html` — the session
page's header stamp draws the same way. Scope: `devpro/profiler/deco.js` — the deco's moment pass
leaves whole: `readMoments`, the `MOMENTS` selector, both moment observers — with the double render
it served, and the deco's remaining script wraps its body in an IIFE, the design's [Harness
profiler] IIFE pair applied here. Scope: `tests/profiler_deco_runner.ts` — the runner's moment cases leave with it. One
rendering, two carriers: `render_html` and `served_page` differ only in the layer's carrier —
inlined where a file cannot link a server's origin.

Applies the design's [Harness profiler] moments pairs and the Code delta's moment paragraphs
verbatim. R23's leaf rides P6; R16's catch-up is sequenced after this package lands.

Done-line: `just test devpro` — the moments pin fails on the pre-P5 tree (UTC text) and passes on
P5's; a pin rendering one session both ways asserts the two texts differ only within
`<!--LAYER-->`'s slot and fails on the pre-P5 tree, which renders two templates; the nav's indicator
and stop pass their pins unchanged.

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
skill's `HP` line — and the leaves the rename invalidates beside the design's pairs:
`PROJECT_DOCS/ARCHITECTURE/repo-layout.md:22`, `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md:78-79`,
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/harness-resources-are-copied-verbatim.md:11`,
`PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md:43`,
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:101,163`. Scope: `devpro/profiler/hooks.py`
(`LAUNCHER = "hp.sh"` and its finder comment), `devpro/profiler/capture.py` (docstring),
`tests/test_devpro_profiler.py`, `tests/test_devpro_install.py`. R23's leaf, named
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-stand-in-models-the-api-s-real-semantics.md`,
enters beside R24's — and `index.md` lists it. The finder resolves the wrapper beside it and runs it
as a child with the `profiler` verb — no probe, no `PATH` search, no foreign devpro; every failure
named by the wrapper's own refusal; capture never blocks.

Applies the design's [Harness profiler] resources and finder pairs and the [Why there is no
verification verb] pair verbatim.

Done-line: `just test` — the docs surface runs over the six renamed leaves; the committed-hook pins
fail on the pre-P6 launcher name and pass on P6's; `devpro profiler init claude` in a repository
holding a stale committed hook renames it, and `devpro profiler doctor` no longer prints its
`update:` line; the capture on this host writes a record through the renamed launcher. The rename's
consuming-project migration is the init's, run before the install refreshes.

## P7 — R16's leaf catch-up, and R25's rule

Scope: `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` and R25's leaf, named
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-formatted-time-test-pins-the-locale.md` —
drafted from measurement against P2 and P5's landed code: the notations the scripts actually
produce, the column list the index actually draws, the locale the tests actually pin. Sequenced
last — the owner's ruling: drafted from measurement, not from this plan's expectations; this
package's measurement passages are filled at its dispatch, a later revision of this plan's changed
text only.

Done-line: `just test devpro`; `just dev-check-design-deltas-applied` reports P7's pairs landed —
the four R16 drift items, each carrying the grep or pin that produces its answer, taken on the
landed tree.

## R — the post-plan review, five seats

The post-plan review, run per the process: the changes and their tests against the project's
standards and fitness for purpose, each seat writing its own review in the scratch directory,
synthesized into the review document.

## B — the post-plan burndown

Drafted from the review document once it lands; its packages get the plan's usual states.
