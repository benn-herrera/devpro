# Post-plan review — the profiler cycle

The five seats' findings, synthesized into one account: one entry per defect, every seat that
reported it named. Finding IDs are `VR1`… — the plan's kickoff legend binds `R9`/`R16`/`R17`/
`R23`/`R24`/`R25` to ROADMAP tickets, a different namespace; this document's IDs never collide
with it. The seats' own reviews live in
`.devpro-temp/review-{python,typescript,shell,architect,prompt-engineer}-seat.md`; this document
carries forward the facts a tracked document needs, since the seats' reports are scratch. The
plan's work spans `6dccae1..HEAD`; reviewers were given the project documents and the design, not
the plan.

**What held** (architect's walk): the rename sweep complete at every enumerated site; doctor's
stand-in mirrors the launcher exactly; the strict fill and its test walk mechanical; the moments'
double render deleted at the root; the column-width single source real; the feed schema pinned by
proxy.

## Findings

### VR1 — The time pins pin neither zone nor locale, and the stated mechanism is inert
Reported by: python (must-fix, `tests/test_devpro_profiler.py:543-550`, `:618-621`; verified
failing under `TZ=UTC`), typescript (must-fix, `:620`), architect (must-fix, same sites),
prompt-engineer (must-fix — the R25 leaf's mechanism, probed; blocker — the test comments carry
the same claim).

The convention the plan itself landed (`a-formatted-time-test-pins-the-locale.md`) is not
satisfied by the tests that motivated it. Settled by the prompt-engineer seat's probe: **bun
ignores `LC_ALL`** (`LC_ALL=de_DE.UTF-8 bun` still resolves `en-US`) — no environment holds a
locale under the embedded bun; the assertions hold because the code builds the clock from the
date's own fields, locale-independent by construction. What a test can and must pin is the zone
(`TZ`), which the index half at `:601` does with `_MOMENT_LOCALE`'s environment — the pattern the
other sites lack. Corrected mechanism, for the leaf, the R25 leaf and the test comments: the zone
is pinned with `TZ`; the locale cannot be held hostile under the embedded bun, so the expected
text is built from the date's own fields, reading the same under any locale the runner carries.

### VR2 — `view.html`'s script is not IIFE-wrapped, and nothing checks the invariant
Reported by: python (should-fix, `view.html:55-431`), architect (must-fix, same site).

The leaf says every script the pages run wraps its body in an IIFE; the deco's and the index's do,
the session page's own script — the largest — does not. Its helpers (`padTwo`, `localDay`,
`localClock`, `view.html:80-82`) and the index script's (`pages.py:1051-1052`) are the names the
removed deco sweep held — no live collision today, the IIFE being the guard against the next one.
The python seat supplies the executable check: every inline script body in the shipped pages
begins with an IIFE form (`view.html:57-59` shows the shape); today's unwrapped script is the
defect it fails on.

### VR3 — Hand-written types blind the type check to the host's surface moves
Reported by: typescript (must-fix, `profiler.ts:36-53`, proven: a declaration rename leaves the
check at exit 0 while a derived context errors), architect (should-fix, `profiler.ts:36-59`,
whose stale claims at `:36` and `:45-47` the change drops).

The capture keeps hand-written `Context`/event types where the host's published declarations are
the authority (R24's rule: no dev-owned stand-in shadows a published package). The declaration
question is settled by the seat's read of `node_modules/@opencode/schema/dist/tool.d.ts`: a
`Tool.Result` of `{output?, content?, metadata?}` — **no top-level `sessionID` is declared**, so
the field the capture exists to read is invisible to the check; the fact is already recorded on
the ROADMAP ticket *The opencode resources' type-check waits on the host's runtime declarations*.
Fix direction: derive the context as `index.ts:130` does; the R24 leaf gains the caveat sentence
naming the one field the declarations do not carry.

### VR4 — The repair verb reports edges it did not write, on fixtures that cannot occur
Reported by: python (should-fix ×2 — `stores.py:104-126`: `:119` increments before `:123`'s
`if changed`, so a file the live-file guard leaves as it stands still reports its would-be fills
as `repaired`, against its own docstring, the branch untested; the 2.3.2 fixture at
`test_devpro_profiler.py:1824` is stored text the shipped capture never writes, hiding that a
2.3.2 record's id is unrecoverable), architect (should-fix — the `(result clipped)` label
narrower than the count's semantics), typescript (question — fixture provenance).

Fix direction: count per file after the guard, the driving test added; the fixture question waits
on the owner (below); label and gloss match the count.

### VR5 — Second homes for values the plan centralized
Reported by: python (should-fix — `pages.py:802-806`, `:916` duplicate `dashboard/server.py:73-79`,
`:52` while the docstring claims "the one lookup"; `hooks.py:211-213` re-spells launcher literals
beside `LAUNCHER`/`OLD_LAUNCHERS`), shell (should-fix — the candidates spelled twice in
`profiler.sh`, loop and message), architect (should-fix — `hp` residue at `view.html:5` where the
provenance banner contradicts its twin, `view.html:335`, `profiler.ts:184`).

The dependency direction is settled by the seat: `server.py` already imports the profiler, so
`server.py` takes `pages.py`'s lookup and route constant and both duplicates in `pages.py` delete.
`git grep -l 'dispatcher_of\|PROFILER_PATH'` answers `devpro/dashboard/server.py` and
`devpro/profiler/pages.py` — the only two referencing files. The launcher's double spelling rides
the one-path ticket's rewrite.

### VR6 — The runners' DOM stand-in exists in three copies, with residue
Reported by: architect (should-fix — `profiler_browser_runner.ts:38-180` re-implements
`profiler_index_runner.ts:31-124`, a third copy in `profiler_page_runner.ts`, ~130 lines each;
the browser runner's geometry/URL tests are its unique value and are retained), typescript
(should-fix — `MutationObserver` machinery in both runners at
`profiler_page_runner.ts:103-116,137-141,150` and `profiler_browser_runner.ts:284-288,303-307`
is residue of the deleted deco sweep — R23's rule: the residue leaves with the semantics it
served).

Fix direction: one stand-in module (`tests/dom_stub.ts` is the seat's suggested home) the three
runners share; the observer machinery leaves in the same change.

### VR7 — The leaves, the SPEC and the skill state what the code does not
Reported by: shell (should-fix — `harness-profiler.md:73` says `sh`, the code runs `/bin/bash`;
`:20` says the skill's "`HP` line" where the skill spells `PROFILER`; the "named by the wrapper's
own refusal"/"no output" phrasing overclaims at the edges), architect (must-fix — the subcommand
list at `:14-15` omits `repair`, which `cli.py:69-74` dispatches and the leaf's own `:212-216`
names — the leaf contradicts itself), python (question — same list; SPEC `shipped-files.md:110-111`,
`:159-160` say a failing capture "exits 0 with no output" while the launcher names failures on
stderr in its non-capture path; notes — the CSS comment at `pages.py:941-943` contradicts
`table-layout: fixed`; the header test's docstring at `tests/test_devpro_profiler.py:194-200`
describes automatic layout), prompt-engineer (should-fix — the skill's `PROFILER` shorthand is
used at `profiler.py:25` twenty-one lines before `:46` introduces it).

The subcommand-list defect entered with P7's own applied pair — the session's drafting miss, the
PE review missed it too. Fix direction: the doc corrections, named per site.

### VR8 — ROADMAP's tickets carry false premises and plan-labeled history
Reported by: prompt-engineer (must-fix — the backup-glob ticket's `-pre-repair-<n>` renames never
shipped: the shipped repair makes no backup, and any `.profiler-*` sibling of a store reads as a
store (`pages.py:676`) — the directories came from a scratch probe; plan labels P1/P3/P6 survive
at `:209,216,226,266` in a doc that outlives the plan, and `:209` points at a directory where the
leaf name belongs; `:266-267` says "unlinks the old launcher names and copies" with no object or
destination; the Testing category holds two non-testing tickets while `## Bugs` is empty;
`:269-273` should name `devpro/doccheck/planform.py`), architect (should-fix — the same ticket;
the one-path ticket states the bounded read in the present tense where it is the target state).

Fix direction: rewrite the affected tickets to the real surface, de-plan-label them, move the
model-config ticket to `## Bugs` and keep the one-path ticket under `## Maintenance`, name the
module.

### VR9 — CONVENTIONS' statements diverge from practice and from each other
Reported by: shell (should-fix — the shell rule
(`code-definitions-and-install/shell-in-this-repository-is-bash.md`) states `set -euo pipefail`
unconditionally with no exception for a hook launcher whose exit contract forbids `-e`; proposed
wording, after the existing sentence: *"A script whose exit contract forbids `-e` — a hook
launcher that must exit 0 on every path — states that in its header, naming the failures `-e` or
`-u` would turn into a blocking exit."*; question — the banner's "do not edit here" vs the
committed copy being "the operator's to tune"), prompt-engineer (must-fix —
`a-host-version-is-checked-against-the-host-s-declarations.md:9-13` restates
`recipes.md:57-65`'s mechanism where it should cite; should-fix — the pronoun reversal at `:6-7`;
the stand-in leaf's residue clause restates `obviated-code-is-deleted-not-parked.md:3-4`;
`harness-resources-are-copied-verbatim.md:25-27` carries a third wording of the declarations rule
— the R24 leaf's survives, the verbatim leaf cites it; "runner" names two referents — in the R24
leaf it means the lint recipe (*"the lint recipe installs it before the checker runs"*), in the
R25 and stand-in leaves the JavaScript test runner (*"the JavaScript runtime's ICU settings"*);
blocker — `recipes.md:63-64` carries a deferral inline in a contract doc, moving to ROADMAP;
reference slots not re-taken), python (proposal, not a finding against this plan's changes —
CONVENTIONS carries no rule that a *structural* claim an ARCHITECTURE leaf makes about the shipped
pages is carried by a test; proposed leaf wording in the seat's report; owner's call below).

Fix direction: cite where the mechanism lives, state each rule once, take the shell rule's
exception, run the reference retake after acceptance.

### VR10 — The launcher's runtime edges, the stale installs, and the sibling resources
Reported by: shell (should-fix — the capture child's stdout is left on the hook's stdout where the
host reads hook JSON, measured; the success path's stdin can go undrained where a child exits
before reading; the `exec` the before side carried is dropped; the failure message spells both
candidates where naming the directory would do), prompt-engineer (blocker — the install left
stale `hp.sh` copies beside `profiler.sh`: the copy step renames forward and never removes), shell
(outside its file — `devpro/harnesses/resources/claude/hooks/state-table-reminder.sh:13` says
exit 0 is the only answer while `:16` sets `set -euo pipefail`, the same contract the profiler's
launcher reasons out; `devpro/harnesses/claude.py:47` says the interpreter is "named on PATH,
never by absolute path" while `:71` names `/bin/bash`).

The stdout leak, the stale installs, the reminder script's flags and the `claude.py` comment are
code and comment fixes; the drain, the `exec` and the message spelling ride the one-path ticket's
rewrite.

### VR11 — Build tooling: one lockfile
Reported by: typescript (should-fix — `justfile:238` runs `bun install --frozen-lockfile` against
npm's `package-lock.json` with no `bun.lock` committed, re-migrating every run; questions —
`tsconfig.json:12`'s include depth, `@types/node` vs the host's Bun, dynamic imports typed `any`,
brand casts), architect (question — whether the frozen-lockfile run writes a lockfile against the
lint recipe's read-only rule), prompt-engineer (evidence — from a scratch copy the recipe runs
exit 0 across 261 packages and writes no lockfile; the read-only rule holds today).

The direction: one lockfile, the runner's — bun's — committed, so `--frozen-lockfile` means what
it says. Settled and recorded, no action: the compiler rides unpinned by the design's explicit
text.

### VR12 — The index's dispatched-agents column renders empty
Reported by: python (question — `pages.py:1106`: `<td class="col-agents"></td>` empty on every
row, the count rendered as a `— n dispatched agents` span in the session cell at `:1097-1098`).

Settled by the accepted design's mapping (`ACTIVE_DESIGN.md`, the feed-keys pair): `agents` is
"the dispatched-agents count" rendered into the columns the header names — the render is the
wrong side. Fix: the count renders into `col-agents`; the session-cell span is dropped.

### VR13 — Test-discipline residue
Reported by: python (notes — the form pins at `tests/test_devpro_profiler.py:1121-1125`;
attribute-order pinning at `:607-614`; the multi-sort URL hole at `pages.py:1240-1249`), typescript
(should-fix — the `find` type predicate where a cast stands, `profiler.ts:254-255`, replacement:
`return [result.sessionID, output.sessionID, metadata.sessionID].find((id): id is string =>
typeof id === "string")`; the deco body unexercised — both runners' `querySelector` returns null,
so the deco's script body never runs under them; the capture runner exercises three dispatches
against five).

Fix direction: per site, in the burndown's grouping.

### VR14 — The version-pin chain holds nothing to anything
Reported by: typescript (must-fix — `package.json:6` pins `@opencode/plugin` 2.4.1; the three
resource headers name 2.3.2 at `profiler.ts:3`, `index.ts:3`, `guardrail.ts:3`), architect
(should-fix — same sites; the headers are the stale side), prompt-engineer (finding 6 — the leaf's
"pinned to the version the resource's header names" resolves to no version, and nothing holds the
pin to one: the headers carry three versions — 2.3.2 headline, 2.3.0 floor, 2.4.1 in the child-id
note — and no test reads `package.json`).

The headers are the stale side: the capture has read 2.4.1's shape since P3. Fix: the headers'
headline versions become 2.4.1 (the floor and the child-id note stay as the history they state),
and a test asserts the pin and the headers agree — today's tree is the defect it fails on.

## The owner's rulings on the open questions

All seven answered as the burndown's revision landed:

- The banner rules; the committed copy is `init`'s render, overwritten at re-run — the
  "operator's to tune" notion is rejected, and the verbatim leaf's `:17` clause is corrected (B7).
  The banner itself is untouched.
- The 2.3.2 fixture leaves — we are on 2.4.1, and a fixture asserting a version's documented
  interface guards nothing this repository needs; no replacement pin (B4).
- The one-path ticket is retired; its substance folds into the burndown as B11.
- `ROADMAP.md:158-163` is left as it stands; the stale roadmap is revised after the work's final
  shape lands.
- `ROADMAP.md:64-72` is fine as it stands — and was never a question; this record corrects the
  list.
- The profiler skill carries no `repair`: the one-shot is a dev-time one-off, not operator
  surface; the leaf's own description is the record.
- The structural-claims rule proposal is rejected: no license for photograph-of-the-source tests.
