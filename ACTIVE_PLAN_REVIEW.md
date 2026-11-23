# ACTIVE PLAN REVIEW — the plan's landed work, reviewed

The post-plan review of commits `4293ad5..25bc0c4` (fdef450, 3d4f058, 0bcae3a, 25bc0c4), synthesized
from five independent seat reviews written to `.devpro-temp/review-{python,typescript,browser,
architect,prompt-engineer}.md`. One entry per defect, naming every seat that reported it. The
burndown cites these IDs and groups by root cause.

Every seat verified its own claims with probes or runs; logs live in `.devpro-temp/`. All findings
stood in the landing commit; the two foreign runner-snippet test failures (the hand-added
`devpro-dashboard` recipe) are outside the range and are not findings of this review.

## Critical

**R1 — The dispatched-agents head never sorts, and three of four head assertions cannot tell it from a working head.** *(browser 1, typescript 3, architect C1, python 6)*
`draw()` sorts on `a[order.key]` (`pages.py:1087-1090`), but no feed entry carries `agents` —
`_feed_entry` writes harness, id, records, first, last, span, dispatcher only (`pages.py:816-828`).
The count lives in `draw()`'s `counted` map and the row's `data-agents` attribute, which the JS
never reads. Every comparison is `undefined < undefined` → 0: the head is a structural no-op under
an `aria-sort="ascending"` that asserts an order that is not there, against
`harness-profiler.md:99-101` and the script's own comments (`:1019-1020`, `:1108-1109`). The tests
miss it three ways: the agents press is driven only on a feed with no dispatchers (all ties,
`test_devpro_profiler.py:1139-1141`); `by_first`'s `first`-ascending and `records`-descending
expected orders are identical (`:1080-1097`); the runner's Proxy would have surfaced the phantom
read had keys been asserted after the press. Fix: give the feed entry the count (widen
`_feed_entry`, the schema comment and the keys assertion together), or make `draw()` resolve
`counted`; then drive the head over a feed where two dispatchers hold different children counts,
plus a descending press.

**R2 — The deco's rewrite destroys the `<time>` elements — the machine form and the per-instant titles the leaf promises vanish when the script runs.** *(architect W1, browser 4)*
`readMoments` writes `cell.textContent = local` (`deco.js:120`), which in a browser removes the
children: both `<time>` elements, their `datetime` attributes and their per-instant raw-UTC titles
(`pages.py` `moment()`, `:1001-1006`) are gone. `harness-profiler.md:108-110` states the machine
form stands in the `datetime` attributes and the raw UTC in the titles; after the sweep it stands
nowhere on the index. `deco.js`'s own comment (`:118-119`) states the opposite of the behavior. The
suite cannot see it: the deco runner's `Cell` stub models `textContent` as a recording write
(`profiler_deco_runner.ts:43-44`). The subline path already has the right shape — it hands each
`<time>` element itself to `readMoments`. Fix: write each `<time>`'s own text and keep the elements.

**R3 — A harness the controls do not name throws in `draw()`, mislabeled as a feed failure, and blanks the index.** *(architect W2, python 1)*
`hides()` dereferences `document.getElementById('harness-' + session.harness).checked`
(`pages.py:1067-1069`); the template carries boxes for exactly `claude`/`opencode` (`:940-941`),
while `session_harness` passes unknown store names through masked (`:767-770`). One third value
(`"mage"`, a hand-written store) makes the lookup `null`, the throw lands in the fetch's `.catch`
(`:1140-1143`), and the page reports "The traces feed could not be read" for a feed that answered —
the exact mislabeling the leaf's notice distinction exists to prevent. Verified through the shipped
runner with a `{"harness":"mage"}` entry: `rows: []` plus the false notice. Fix: a missing box
means visible; and wrap `draw()`'s body so a page defect stops being reported as a feed failure —
`notice` is the feed's failure channel (`:1126-1132`).

**R4 — `profiler.ts`'s stated floor is no longer true: on 2.3.0 the capture records no child.** *(typescript 1)*
Line 3 declares "opencode 2.3.2 plugin module (floor 2.3.0)", but `childSessionOf` now reads
`result.output.sessionID` — on 2.3.0, where the id rides `result.metadata.sessionID`, every
dispatch records `null` and the dispatcher's count and the child's row are gone. CONVENTIONS,
*A harness resource's floor is behavioral*, cites this exact file. Fix: read `output.sessionID`
first and fall back to `metadata.sessionID` (two lines, keeps the floor true), or state the
child-tie as 2.3.2-only on line 3, in the fixture's `task` comment and the test's docstring.

**R5 — The capture fixture passes for the wrong reason, and `childAgentTypeOf` has the mirror hole.** *(typescript 2)*
The fixtures carry `output` as an object, which `resultText` refuses as text; the record's
`result: None` assertion (`test_devpro_profiler.py:635`) passes on the fixture's leftover
`metadata` key, not on the host's shape — the fixture is not "the host's observed dispatch result
shape" the design names. And `childAgentTypeOf` (`profiler.ts:255-258`) reads `result.agentType` /
`result.metadata.agentType`: if the host's fork marker rides the same `output` object the session id
does, every fork records as its input's `agent`. Fix: one observed result per fixture, the runner
asserting what that result renders, the agent type read from the place the host puts it.

## Warning

**R6 — A child whose dispatcher is hidden is drawn nowhere, and takes its own children with it.** *(typescript 5)*
`tops` is `visible.filter((s) => !s.dispatcher)` (`pages.py:1086`): a child hidden for its harness,
or whose parent is a hidden child, is drawn nowhere while counts stay at the feed's — a session
reading "0 dispatched agents" and linking to a page no press reaches. The comment at `:1065-1066`
is silent on grandchildren. Fix: hide only on own-harness or (child-rows off and it has a
dispatcher), promoting orphans to their dispatcher's level.

**R7 — The session page's header stamp reads clock alone, and multi-day crossings read like one-day crossings.** *(typescript 6, browser multi-day note, prompt-engineer F4)*
`localMoment` returns the clock with no date (`deco.js:105-109`): on a page titled "Session
<id slice>" nothing says which day. And the first-to-last rule's "the next day's being obvious"
(`harness-profiler.md:111-113`) is rationale, not an observable — `2025-12-31 22:00 to 10:30` (the
test's own case) does not make the finish's day obvious, and a two-day crossing renders like a
one-day crossing. Fix: a lone moment reads with its date; the leaf states the observation, not the
reader inference.

**R8 — "One notation" rests on the host's ICU defaults, and three notations survive a script run.** *(python 4, typescript 7, prompt-engineer F1/F2)*
`momentClock` passes `[]` as locale (`deco.js:90-91`): the separator is ICU's per reader, and
`hourCycle: "h23"` is a preference, not a guarantee. Meanwhile the index's raw UTC is `HH:MM:SS`
(`pages.py:990`), the deco writes `HH:MM`, and `view.html`'s UTC stamp `HH:MM:SS` — three notations
for one instant across pages the design promises one. The test pins `TZ` but not locale. Fix: build
the clock by hand (`padStart`, as `dayOf` does) or name the locale; pin `LC_ALL` alongside `TZ` in
the test; cut "one notation" from the leaf and let the titles clause carry what titles hold.

**R9 — Nothing holds `profiler.ts` to the host it is shipped for.** *(typescript 8)*
No `package.json`, no `tsconfig.json`, no `@opencode-ai/plugin` types on disk; the stub exports
`Plugin.define` and nothing else. The commit's whole job was one key the host reports — the defect
class is exactly what no check can police. CONVENTIONS, *Harness resources are copied verbatim*,
already flags the gap. Fix: type-check the opencode resources against the host's published
declarations (vendored or installed) in a `just` recipe on the devpro surface, or vendor the two
declaration files with a test on the declared hook signatures.

**R10 — The deco runner's selectors are `deco.js`'s own strings, so the page and the sweep are one edit apart.** *(browser 5, typescript 9)*
The stub answers `querySelectorAll` by string equality (`profiler_deco_runner.ts:222-229`) on the
same literal `deco.js` queries (`:122`); a selector the live page still satisfies falls to `[]`, the
readings initialize to the served text (`:35`), and the test passes. `getComputedStyle` returns
`""` for every palette variable. Fix: read the selectors from `deco.js`'s own `MOMENTS` constant,
and make the readings' initial value distinguish "sweep ran and wrote the same text" from "sweep
never ran".

**R11 — The failure-notice test pins the runner's literal, not the page's message.** *(browser 2)*
`{fail:"boom"}` is a boolean; the runner always answers 500 (`profiler_index_runner.ts:171`), so the
assertion pins "the runner answered 500 and the page's two fixed strings joined" — the page's own
composed-message path is never the thing asserted, and nothing asserts the notice was `hidden`
before (`:1133-1139`, the gap browser note 9 names). Fix: `{fail}` carries the status and body the
server would answer; assert the notice per case and its hidden-before state.

**R12 — The no-records row does not make the distinctions the leaf states — and a third state it does not name.** *(python 2, browser 7)*
The leaf says the notice is "distinct from the no-records state *a zero-record store renders*"
(`harness-profiler.md:98-102`), but `read_sessions` filters zero-record stores out (`pages.py:764`),
so a store that recorded nothing and no store at all render the identical "run a session with the
hook installed" row. And both harness controls off draws that row over a non-empty feed
(`pages.py:1098`; verified `probe-hidden-feed.ts`). Fix: the row gains the distinction (a store was
found and held nothing ≠ no store found ≠ the controls hid everything), or the leaf drops the
clause — one side, named.

**R13 — `_report` discriminates on `isinstance` where the caller holds the discriminator.** *(python 3)*
`_report(path, *, reader)`'s `Callable[[str], Plan | Layout]` union exists only to be type-tested
(`plancheck.py:167-179`); a `Layout`-shaped document reaching the roadmap arm silently gets the
roadmap summary. Fix: pass the summary formatter beside the reader, or name the two concrete
returns in the docstring; if the union leaves the signature, `from __future__ import annotations`
(`:6`, added in fdef450 for it) goes with it.

**R14 — The sort cycle is three statements of one machine that disagree.** *(typescript 4)*
The comment says two-press (`pages.py:1107`), the code has a third press returning to feed order
with no arrow (`:1116-1118`), and `th[aria-sort]`'s `::after` rule draws nothing on the unsorted
head — the third state is indistinguishable from never-sorted, and the button carries no accessible
name for the state. Fix: the comment, the arrow and `aria-sort` say the same thing.

**R15 — The record's field list has a fifth hand-transcribed copy in the tests.** *(typescript 10)*
`profiler_serialize_runner.ts:24-44` transcribes all 22 fields by hand beside the resource's own
`CallRecord`; the commit that changes what a record carries is exactly where that list goes stale.
Fix: one source for the record's fields in the tests (shared literal from the resource's own
`callRecord`), as `_RECORD_FIELDS` already is on the Python side.

**R16 — The leaf's sentences drift from the behavior the code can hold, and the column lists drift from each other.** *(prompt-engineer F1-F6)*
"the machine form only in the `datetime` attributes" is a tirelessness guarantee prose cannot carry
(F1); "one notation" restates the titles clause and collides with the three surviving notations
(F2, with R8); the no-script branch and the first-to-last rule describe different surfaces — a
`tree --format html` file carries both (F3); the row list names five columns, the head list four,
and the dispatched-agent count is in neither row list nor column list (F5); "the time" names the
first-to-last column under a second name (F6). Fix in the leaf: name the surfaces, state the
observation, make the lists agree.

**R17 — Stale text in the leaf set: pre-existing references that do not resolve.** *(prompt-engineer F8, F9, F10, architect N1)*
"an Agent row" has no referent (`harness-profiler.md:113-116`); the unreadable store is stated
three times, the middle one weaker (`:126-129`); `repo-layout.md:45-47`'s "`dicing`'s modules" is
the only clause not at package grain; the harness-name union comment counts two spellings where
three exist (`pages.py:898-901`, `:920-921`, `:940-941`). Fix: the smallest wording in each place.

**R18 — `index.js` is named in two comments and is no file.** *(python 8, prompt-engineer B2)*
`pages.py:799, :892` name `index.js` as the index's script; the script is the `INDEX` template's
own text. Fix: drop the name from both comments.

**R19 — The span table is paired by position with a substring check.** *(python 5)*
`test_devpro_profiler.py:1054-1060` — every assertion is "somewhere in the row"; a span cell moved
columns or rows drawn in reverse still satisfies most of it. Fix: assert the row's last `<td>`
structurally.

**R20 — The opencode control hides nothing while reporting checked, and the ×-fields convention it violates is unstated.** *(prompt-engineer C2)*
With `opencode` unchecked and `claude` checked, the `opencode` control reports `checked` while
hiding nothing, and the opencode-parent rule hides a claude child `claude` checked would show. The
`claude`/`opencode` pair is convex; the dispatcher/child pair is not two boxes. Fix: name the
convention in code, and make the control state honest — or state in the leaf that the pair is the
unit of filtering.

**R21 — The deliberate `metadata.sessionID` discard is documented nowhere.** *(prompt-engineer C1)*
The commit discarded a source the host also reports; the code comments carry the mechanics, the
leaf nothing. An executor touching `childSessionOf` cannot tell a deliberate discard from an
oversight. Fix: one sentence in the leaf or the commit is not enough — the leaf states it (R4's
resolution covers it).

**R22 — Dead branches in `deco_runner` and the unreadable constant bound twice.** *(browser 6, python seen)*
`profiler_deco_runner.ts:222-229` matches `.sort` and `.controls input`, which `deco.js` never
queries; `UNREADABLE` binds in `plancheck.py:70` and `kanban/server.py:55`. Fix: delete the
branches with R10's fix; the constant is pre-existing — one home or one noted twin.

## Contract gaps (proposed CONVENTIONS leaves, not code)

**R23 — A JS stand-in models the API's real semantics.** *(python contract gap)*
The project's test doctrine says nothing about how faithful a hand-written DOM stand-in must be; R2,
R10 and R12's test-blindness all live here. Proposed leaf: "A JS runner's stand-in for a DOM API
models the API's real semantics — what it matches, what it returns null for, what it leaves out —
and no test relies on a stand-in being more permissive than the browser."

**R24 — A shipped resource naming a host version is checked against that host's declarations.** *(typescript contract gap)*
The tool, the version it pins, the recipe that runs it — the check R9 asks for becomes a rule, not
a one-off.

**R25 — A test asserting a formatted time or date pins the locale alongside `TZ`.** *(typescript contract gap)*
A locale-dependent separator is an assertion on the runner's ICU, not on the code.

## Not defects (asked and answered, or expected)

- The server's `stamp()` keeps its raw-UTC text-tree reading — the design's no-script branch.
- `aria-sort` is honest across all three presses; the nav's active-view link is unchanged; escaping
  holds on both pages (`esc` at every `innerHTML` site).
- The design's As-it-stands blocks no longer matching the amended leaves is the delta mechanism
  working; the design retires when the plan lands.
- The sweep's `_check`-wrapper candidate is the verb surface; the `UNREADABLE` twin and the
  installed-tree `dicerlib` imports are outside the range (reinstall the plugin payload at the next
  natural occasion).

## Blockers routed to their owners

- The uncommitted `devpro-dashboard` recipe in `devpro/runner-snippets/` breaking two pins — the
  session owns the call; no seat touched it.
- `index.js` (R18) — code-owned comment fix.
