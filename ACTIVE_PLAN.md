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
| P5 | landed 9766c02 | expert | moments local at birth; the deco's moment pass leaves; one rendering, two carriers |
| P6 | landed 57bc90e | expert | `profiler.sh` renames `hp.sh`; the finder runs the wrapper bare; R23's rule enters CONVENTIONS |
| P7 | landed 11fe544 | expert | R16's leaf catch-up applied as the design's pairs; R25's rule enters CONVENTIONS |
| R | landed: this commit adds the review document | expert | the post-plan review, five seats |
| B | landed: the work list below, at this plan's revision commit | expert | the post-plan burndown |
| B1 | landed bdb395a | expert | the time pins pin what they claim (VR1) |
| B2 | landed 613b955 | expert | the IIFE invariant holds everywhere, checked (VR2) |
| B3 | landed 9ca5c29 | expert | the type check sees the host's surface (VR3) |
| B4 | landed aff8ba0 | expert | the repair tells the truth (VR4, VR13) |
| B5a | landed 1ab0ff1 | expert | one home each (VR5) |
| B6 | landed 6641b54 | expert | the documents state the shipped code (VR7, VR8, VR14; after B8) |
| B7 | landed 4584cd5 | expert | CONVENTIONS aligns with practice (VR9) |
| B8 | landed 7ea5524 | expert | the launcher's edges and the stale installs (VR10) |
| B9 | landed bca8961 | expert | one lockfile (VR11) |
| B10 | landed a468bfb | expert | the agents column, and the residue (VR12, VR13) |
| B11 | landed 6bffe75 | expert | one path to the profiler's outcome |

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
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-formatted-time-test-pins-the-locale.md`,
entered in the CONVENTIONS index and the entry-point listings (R23's pattern). Drafted from
measurement against P2 and P5's landed code — the owner's ruling: drafted from measurement, not
from this plan's expectations. The measurement passages below were filled at this package's
dispatch, a later revision of this plan's changed text only; the design carries the corrections
as pairs P7 applies verbatim.

The four R16 drift items, each with the measurement that produces its answer, taken on the landed
tree:

1. The index row's list names five data items where the header draws six columns — the
   dispatched-agents count is missing from the list. Measured: `sed -n '/^<thead>/p'
   devpro/profiler/pages.py | grep -o '>[a-z][a-z ]*<'` answers `harness`, `session`, `records`,
   `dispatched agents`, `first to last`, `span` (the static `<thead>`, one line; four labels sit
   inside sort buttons). The design's index pair is revised to carry the list the header draws;
   P7 applies the revised pair.
2. The feed's entry keys are not "the columns above": the feed carries `harness`, `id`,
   `records`, `agents`, `first`, `last`, `span`, and `dispatcher` where a session was dispatched —
   keys the index's script renders into the header's columns. Measured: `sed -n '846,855p'
   devpro/profiler/pages.py` (`_feed_entry`), the feed's docstring above it.
3. The code paragraph's `hp.py` sentence claims outputs P2 and P5 changed: the subcommands no
   longer "read exactly as they did inside `hp.py`" — the dashboard's display is the browser-shaped
   index and pages, and the pages' scripts draw the moments local at birth. Measured: `sed -n
   '14,16p' PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` against the Serving section's
   claims; the correction drops the stale clause, the display's description living in the Serving
   section.
4. The span's drawn notation is unstated: the index's script draws the feed's seconds as whole
   hours and minutes — `3h 2m` — minutes and seconds below the hour — `3m 20s` — seconds below
   the minute, and `0s` for a zero-length span. Measured: `sed -n '1027,1035p'
   devpro/profiler/pages.py` (the span's formatter and its comment).

R25's leaf, drafted from the pin — `grep -n "locale" tests/test_devpro_profiler.py` answers at
lines 502 and 564-565: the locale is pinned beside the zone, a clock built from the date's own
fields reading the same under any locale, the runner's ICU settings held hostile to prove it:

```markdown
### A formatted time test pins the locale

A test asserting a formatted time or date pins the locale beside the time zone: a runner's ICU
settings decide locale-aware formatting as the `TZ` setting decides the zone, so a pin holding
the zone alone passes under whatever locale the runner carries. The pin is hostile to the locale:
the expected text is built from the date's own fields, reading the same under any locale, and the
runner's ICU settings are set hostile in the test's own setup, so the shape the assertion holds
is the code's, not the runner's settings'.
```

Done-line: `just test` — the docs surface's link check runs over the rewritten leaf and the new
leaf's listings; `just dev-check-design-deltas-applied` reports the design's pairs landed — P7's
three new pairs and the revised index pair among them, 17 in all.

## R — the post-plan review, five seats

The post-plan review, run per the process: the changes and their tests against the project's
standards and fitness for purpose, each seat writing its own review in the scratch directory,
synthesized into the review document.

## B — the post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` as revised; each item cites its findings' `VR` IDs there —
the kickoff's `R` IDs name ROADMAP tickets, a different namespace. VR6's item moved to ROADMAP.md's
*The DOM stand-ins' shape* — the stand-ins' shape is the browser-driven design's call, not this
plan's. The checkpoint gate runs once before each package's commit: `just test`, then `just
sweep-python` (CONVENTIONS/planning-and-execution/the-gates.md). The packages run serially in the
shared tree; B9, B10 and B11 are order-free — no two share a file. After the burndown's packages
land, the plan's landing commit deletes `ACTIVE_PLAN_REVIEW.md` and `ACTIVE_DESIGN.md` and retires
the plan.

### B1 — the time pins pin what they claim (VR1)

Scope: `tests/test_devpro_profiler.py`, `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-formatted-time-test-pins-the-locale.md`.

Facts, settled by the seats' probes: bun ignores `LC_ALL` — `LC_ALL=de_DE.UTF-8 bun` still
resolves `en-US` — so no environment holds a locale under the embedded bun, and the assertions
hold because the code builds the clock from the date's own fields. What a test pins is the zone:
the index half at `:601` runs its runner under `_MOMENT_LOCALE`'s environment and is the pattern;
the unpinned sites `:543-550` and `:618-621` take the same environment, and their asserted
`America/Los_Angeles` readings fail under `TZ=UTC` today — that is each new pin's defect. The
mechanism sentence is corrected where it is stated: the test comments at `:502-504` and
`:564-566`, and the R25 leaf — the zone is pinned with `TZ`; the locale is not holdable under the
embedded bun; the expected text is built from the date's own fields, reading the same under any
locale the runner carries. The profiler leaf's notation passage states the drawn behavior and
stands unedited.

Done-line: `just test devpro`, each new pin shown failing before its fix.

### B2 — the IIFE invariant holds everywhere, checked (VR2)

Scope: `devpro/profiler/view.html`, `tests/test_devpro_profiler.py`.

The session page's own script (`view.html:55-431`) wraps its body in an IIFE, as the leaf states
and the deco's and index's scripts already do. The helpers keep their names — the deco is
deleted, no collision exists, the IIFE is the guard against the next one. The invariant gains its
check: a test asserting every inline script body in the shipped pages begins with the IIFE form
(`view.html:57-59` shows the shape) — today's unwrapped script is the defect it fails on.

Done-line: `just test devpro`, the check shown failing on the unwrapped script first.

### B3 — the type check sees the host's surface (VR3)

Scope: `devpro/harnesses/resources/opencode/profiler.ts`,
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-host-version-is-checked-against-the-host-s-declarations.md`.

The capture's hand-written `Context` and event types (`profiler.ts:36-53`; the stale claims at
`:36` and `:45-47` drop with the change) are derived from the host's published declarations, as
`index.ts:130` derives its own. The declaration fact is settled and already recorded on the
ROADMAP ticket *The opencode resources' type-check waits on the host's runtime declarations*:
`node_modules/@opencode/schema/dist/tool.d.ts` declares `Tool.Result` as
`{output?, content?, metadata?}` — no top-level `sessionID`. The leaf is the fact's one home and
gains the sentence: *"The id the capture reads at the result's top level is the host's runtime
shape, published in its source and not in the shipped declarations; the check sees the shapes
around it."*

Done-line: `just lint`, `just test devpro`.

### B4 — the repair tells the truth (VR4, VR13)

Scope: `devpro/profiler/stores.py`, `devpro/profiler/cli.py`, `tests/test_devpro_profiler.py`,
`devpro/harnesses/resources/opencode/profiler.ts`.

The defect: `stores.py:119` increments the repaired count before `:123`'s `if changed`, so a file
the live-file guard leaves as it stands still reports its would-be fills as `repaired`, against
its own docstring. Count per file after the guard, and add the test that drives the guard. The
capture's string-guard fall-through gets its test: `profiler.ts:249-256`, the fixture
`result.sessionID: 5` with `output.sessionID: "ses_x"` — the non-string first arm falls through
to the next. The repair test's 2.3.2 fixture **leaves**: the owner's ruling — we are on 2.4.1,
and a fixture asserting a version's documented interface guards nothing this repository needs; no
replacement pin.

Done-line: `just test devpro`.

### B5a — one home each (VR5)

Scope: `devpro/profiler/pages.py`, `devpro/dashboard/server.py`, `devpro/profiler/hooks.py`,
`devpro/profiler/view.html`, `devpro/harnesses/resources/opencode/profiler.ts`.

The dispatcher lookup and the `/profiler/` constant take one home: `server.py` already imports
the profiler, so `server.py` takes `pages.py`'s (`pages.py:802-806`, `:916` →
`server.py:73-79`, `:52`), and both duplicates delete from `pages.py`; the docstring's "the one
lookup" then reads true. The reference search `git grep -l 'dispatcher_of\|PROFILER_PATH'`
answers `devpro/dashboard/server.py` and `devpro/profiler/pages.py` — every referencing file,
named. `hooks.py:211-213` reads `LAUNCHER`/`OLD_LAUNCHERS` instead of re-spelling them. The `hp`
residue leaves: `view.html:5` (the provenance banner contradicting its twin), `view.html:335`,
`profiler.ts:184`.

Done-line: `just test`, `just test devpro`.

### B6 — the documents state the shipped code (VR7, VR8, VR14; runs after B8)

Scope: `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`,
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`, `devpro/profiler/pages.py`,
`devpro/harnesses/resources/opencode/profiler.ts`, `index.ts`, `guardrail.ts`,
`devpro/definitions/skills/profiler.py`, `ROADMAP.md`, `ACTIVE_DESIGN.md`'s subcommand pair.

The corrections, named per site: the leaf's `:73` names `/bin/bash` as the code's two hook
commands and `hooks.py:97` do (measured under `/bin/dash`: four `[[: not found`, exit 127, the
capture never taken); `:20` names `PROFILER`; the subcommand list at `:14-15` gains `repair` —
the design's subcommand pair is revised, its becomes reading verbatim: *"Its subcommands are
`capture`, `tree`, `init`, `doctor` and `repair`; the records are served by the `dashboard` verb,
below."* — the pair re-pends until this package applies it, and the deltas check returns to 17
landed; the failure phrasings state what the wrapper names on stderr and where the capture path
stays silent, and SPEC's `shipped-files.md:110-111`, `:159-160` match. The CSS comment at
`pages.py:941-943` stops contradicting `table-layout: fixed`; the header test's docstring at
`tests/test_devpro_profiler.py:194-200` describes the layout the test actually pins. The skill's
`PROFILER` is introduced at its first use (`profiler.py:25`) rather than twenty-one lines later.
The three resource headers' headline versions become 2.4.1 (`profiler.ts:3`, `index.ts:3`,
`guardrail.ts:3` — the capture has read 2.4.1's shape since P3; the 2.3.0 floor and the child-id
note stay as the history they state), and a test asserts the pin and the headers agree — today's
tree is the defect it fails on. ROADMAP: the backup-glob ticket's premise corrected — the shipped
repair makes no backup, and any `.profiler-*` sibling of a store reads as a store
(`pages.py:676`), so a store directory added beside another renders twice and `tree <prefix>`
reports ambiguity; the plan labels at `:209`, `:216`, `:226`, `:266` leave, `:209` naming
`harness-profiler.md` where it pointed at a directory; the model-config ticket moves to
`## Bugs` and the one-path ticket stays under `## Maintenance`; `:266-267`'s "copies" gains its
object and destination as B8's landed install behavior states them; `:269-273` names
`devpro/doccheck/planform.py`; the one-path ticket's bounded-read sentence stated as the target
state — its retire-or-rewrite disposition **waits on the owner** and is not this package's;
`ROADMAP.md:158-163` and `:64-72` are the owner's verbatim texts and are **excluded**.

Done-line: `just test docs`, `just dev-check-links`, `just dev-check-roadmap`,
`just dev-check-design-deltas-applied` back at 17 landed.

### B7 — CONVENTIONS aligns with practice (VR9)

Scope: `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/shell-in-this-repository-is-bash.md`,
`a-host-version-is-checked-against-the-host-s-declarations.md`,
`a-stand-in-models-the-api-s-real-semantics.md`,
`harness-resources-are-copied-verbatim.md`, `PROJECT_DOCS/ARCHITECTURE/recipes.md`, `ROADMAP.md`.

The shell rule gains, after its existing sentence: *"A script whose exit contract forbids `-e` —
a hook launcher that must exit 0 on every path — states that in its header, naming the failures
`-e` or `-u` would turn into a blocking exit."* The host-version leaf cites `recipes.md:57-65`'s
mechanism instead of restating it at `:9-13`, fixes the pronoun reversal at `:6-7`, and reads
*"the lint recipe installs it before the checker runs"* at `:10`. The stand-in leaf's residue
clause cites `obviated-code-is-deleted-not-parked.md`. The verbatim leaf's `:25-27` cites the R24
leaf's wording of the declarations rule — that wording survives, the restatement leaves. The R25
leaf's mechanism sentence is B1's and is not touched here. `recipes.md:63-64`'s inline deferral
moves to a ROADMAP ticket. The verbatim leaf's `:17` reads *committed and the operator's to tune*
— the owner's ruling rejects the notion: the committed copy is `init`'s render, overwritten at
init's re-run, and the banner's *do not edit* governs both destinations; the clause is corrected
to say that, the banner itself untouched — and the correcting commit names the clause's
provenance: it entered at e19906d's stage-2 burndown, never authorized by the owner. The one-path
ticket is **retired** by the owner's
ruling, its substance moved to B11 — this package removes it from ROADMAP. The structural-claims
rule proposal is **rejected** by the owner's ruling — no license for photograph-of-the-source
tests — recorded in the review document, no leaf added. After acceptance, `just retake-reference`
runs (the reference-retakes convention).

Done-line: `just test docs`, `just dev-check-links`, `just retake-reference`.

### B8 — the launcher's edges and the stale installs (VR10)

Scope: `devpro/harnesses/resources/claude/profiler/profiler.sh`, `devpro/install.py`'s copy step,
`devpro/harnesses/resources/claude/hooks/state-table-reminder.sh`, `devpro/harnesses/claude.py`.

The capture child's stdout is silenced (`>/dev/null`): the hook's stdout carries only the host's
protocol, and SPEC's "exits 0 with no output" stops resting on the capture's silence. The
install's copy step removes the old-name copies it once wrote — no stale `hp.sh` stands beside
`profiler.sh` after an upgrade. The reminder resource's `set -euo pipefail` (`:16`) leaves where
`:13` says exit 0 is the only answer — the profiler launcher's own header reasoning is the
pattern. `claude.py:47`'s interpreter comment is corrected to match `:71`'s `/bin/bash` naming.
The drain, the `exec` and the failure-message spelling ride the one-path ticket's rewrite, not
this package.

Done-line: `just lint`, `just test`.

### B9 — one lockfile (VR11)

Scope: `justfile`, the repository's lockfile.

`justfile:238` runs `bun install --frozen-lockfile` against npm's `package-lock.json` with no
`bun.lock` committed and re-migrates every run. The direction: one lockfile, the runner's —
bun's — committed, so `--frozen-lockfile` means what it says. The read-only rule holds today:
from a scratch copy the recipe runs exit 0 across 261 packages and writes no lockfile. The
compiler rides unpinned — ROADMAP.md's *The TypeScript compiler rides unpinned* states the
exclusion; settled, no action, stated here so it travels with the package.

Done-line: `just lint`.

### B10 — the agents column, and the residue (VR12, VR13)

Scope: `devpro/profiler/pages.py`, `tests/test_devpro_profiler.py`,
`devpro/harnesses/resources/opencode/profiler.ts`, the two page runners.

Sites are anchored to symbols and greps — earlier packages shift the tree under a review-era
line number. The render is the wrong side, settled by the accepted design's mapping: the count
renders into the `col-agents` cell in `row()` — the empty `el('td', undefined, 'col-agents')`
build — and the `— n dispatched agents` span in the session cell is dropped. The residue, named
per site: the CSS-text pins duplicate the measured geometry — in the index test's layout block
(grep `table-layout: fixed` in `tests/test_devpro_profiler.py`), the six `.col-*` width regexes
delete and the `table-layout: fixed` assertion stays — the browser runner reads and measures
those exact declarations, which is what makes them redundant, while only the `fixed` assertion
pins `table-layout` itself; the attribute-order pinning — the serialized `moments`-cell
literals (grep `class="moments"` in the test file) asserting `title` before `class` — becomes
per-element assertions on text, `datetime` and `title`, the attributes' order unpinned; the
multi-sort URL hole — `restore()` applying every `sort` parameter the URL carries, so a
hand-edited `?sort=records&sort=span` marks two heads sorted while the draw honors one —
closes: `restore` takes one `sort` value, the surplus dropped at the boundary, and compares
each head to it; `sync()` stays the URL's only writer; the count's move out of the session cell
changes that cell's measured box — the browser runner's geometry test is the observation,
re-baselined where the span's drop moves a width; the capture's cast in `childSessionOf`
becomes the predicate —
`return [carried.sessionID, output.sessionID, metadata.sessionID].find((id): id is string =>
typeof id === "string")` — the `ids` array, the `find` and the cast collapsing into it; the deco
body's exercise: the two runners' `querySelector` returns null for everything, so the deco's
script body never runs under them — the runners gain the deco's own three elements
(`#connection`, `#stop`, `.nav-server`) and the assertion reads what the deco draws — `show()`'s
text in `#connection` and the `nav-live`/`nav-idle` class on the server element. The IIFE check
covers the pages' file scripts too — `devpro/profiler/deco.js` and
`devpro/kanban/assets/board.js` — one assertion each that the file's body opens the IIFE form
(B2's check reads the inline bodies alone).

Done-line: `just test devpro`.

### B11 — one path to the profiler's outcome

Scope: `devpro/harnesses/resources/claude/profiler/profiler.sh`, `devpro/harnesses/claude.py`,
`devpro/profiler/hooks.py`, `devpro/profiler/capture.py`, `devpro/install.py`, `devpro/clauses.py`,
the skill definition's finder, its module docstring and its `Locate the profiler` steps' `bash`
lines (`devpro/definitions/skills/profiler.py:25-26,42-43`),
`tests/test_devpro_profiler.py`, `tests/test_devpro_install.py`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`,
`PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md`,
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/subsystem-map.md`, `PROJECT_DOCS/ARCHITECTURE/renders-and-copies.md`,
`PROJECT_DOCS/ARCHITECTURE/repo-layout.md`, and `ACTIVE_DESIGN.md`'s harness-profiler pairs.

The ruling: one path — every runner names the wrapper from its writer's knowledge. The `profiler`
verb's subcommands — `capture`, `tree`, `init`, `doctor` — are the wrapper's own: once the launcher
is gone, every caller invokes the wrapper it knows and the verb dispatches as it does. The launcher
file and its finder retire: the committed hook's wiring invokes the project-committed wrapper
directly — the `profiler` verb, the `capture` subcommand, the harness argument (`profiler capture
claude`), one command shape every block spells the same way — the installed hook's wiring names the
installed wrapper from
`init`'s knowledge, and the plugin registration's command (`_PROFILER_COMMAND`, the six
`_PROFILER_EVENTS` entries in `devpro/harnesses/claude.py`) names the wrapper `INSTALLED_WRAPPER`
declares. The copies the writers once wrote leave: `init` unlinks the committed tree's
`.claude/harness-profiler/profiler.sh` beside the `hp.sh` names its machinery already carries,
and the install's copy step removes the installed tree's `profiler/profiler.sh` — the copy
step's mirror assumption (the "not a mirror" docstring at `install.py`'s copy machinery) is what
the change relaxes, and the removal's shape is the executor's from that freedom. The opencode install's
`profiler/` copy empties with it — `_CROSS_HARNESS_SOURCES` drops the entry (the opencode
capture is the plugin's own). The skill's finder clause is rewritten: `WRAPPER_PROFILER`'s
current text is the first-of-two-candidates resolution the ruling abolishes; its replacement
carries the wrapper's path as the writer's knowledge, and the shared `WRAPPER` clause (the
guide's and docdicer's) keeps its resolution — the ruling covers the profiler's runner. The
doctor runs as the wrapper's own subcommand: its `devpro:` line names the registered wrapper,
the launcher-compare helpers leave, and the stand-in pair asserting the launcher's resolution
moves with the semantics it served. The resources tree's `claude/profiler/` directory empties —
the install's copy machinery (`harness_resource_copies`) and the launcher's banner fixture in
`tests/test_devpro_install.py` lose it. The capture subcommand owns
the contract itself: its read of the hook payload is bounded, it exits 0 on every path, and its
child's stdout stays off the hook's stdout (the host reads hook JSON there — SPEC's "exits 0
with no output"). The launcher's remaining ride-notes land here: the success path's stdin
handling and the `exec` the before side carried. The dispatcher revised the design's harness-profiler pairs at this package's dispatch turn and
obtained the PE review; the package applies them as the other packages did — the leaf's
**Resources**, **The launcher's finder** (deleted), **Wiring**, **The skill** through **What
`init` copies**, the opencode capture's install paragraph and **Doctor's lines** passages, and
the skill's `Locate the profiler` block. The contract moves with the work: SPEC's
`installed-tree.md` names the launcher relative to the skill — its wrapper sentence stands — and
`shipped-files.md` states the hooks' launcher paths and their "finds no `devpro` to run under" —
each names the wrappers the tree runs instead. ARCHITECTURE's `subsystem-map.md` (three
sentences), `renders-and-copies.md` and `repo-layout.md` carry the launcher's copy machinery —
each states the wrappers the tree names instead. The profiler tests' launcher-resolution
stand-ins — the runner asserting the launcher's resolution — move with the semantics they
served: the tests assert one path, `doctor`'s `devpro:` line naming the wrapper's own path.

Done-line: `just test`, `just lint`; `just dev-check-design-deltas-applied` reporting the
harness-profiler pairs landed; and `git grep -n "profiler\.sh" -- devpro/definitions tests`
returning nothing — a live reference is what it guards, the definitions and the tests being where
one would hide; the project documents' leaves state the retirement by naming the path, and stay
out of the grep.
