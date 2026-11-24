# Post-plan review — the profiler cycle

The five seats' findings, synthesized into one account: one entry per defect, every seat that
reported it named. The seats' own reviews live in `.devpro-temp/review-{python,typescript,shell,architect,prompt-engineer}-seat.md`; this document cites their findings by seat and line. The
plan's work spans `6dccae1..HEAD`; reviewers were given the project documents and the design, not
the plan.

**What held** (architect's walk): the rename sweep complete at every enumerated site; doctor's
stand-in mirrors the launcher exactly; the strict fill and its test walk mechanical; the moments'
double render deleted at the root; the column-width single source real; the feed schema pinned by
proxy.

## Findings

### R1 — The time pins pin neither zone nor locale, and the stated mechanism is inert
Reported by: python (must-fix, `tests/test_devpro_profiler.py:543-550`, `:618-621`; verified
failing under `TZ=UTC`), typescript (must-fix, `:620`), architect (must-fix, same sites), prompt-engineer (must-fix — the R25 leaf's mechanism, probed: `LC_ALL=de_DE.UTF-8 bun` still resolves
`en-US`; blocker — the test comments at `:502-505`, `:564-565` carry the same claim).

The convention the plan itself landed (`a-formatted-time-test-pins-the-locale.md`) is not
satisfied by the tests that motivated it: three assertion sites run their runners with the host's
environment, and the "ICU settings held hostile" mechanism stated in the leaf and the test
comments does not move bun's resolver. The index half at `:601` pins TZ and locale correctly —
it is the pattern. Fix direction: pin the environment on every runner invocation; establish what
actually holds a locale under bun and state that in the leaf, the test comments and the R25 leaf.

### R2 — `view.html`'s script is not IIFE-wrapped, and nothing checks the invariant
Reported by: python (should-fix, `view.html:55-431`), architect (must-fix, same site).

The leaf says every script the pages run wraps its body in an IIFE; the deco's and the index's do,
the session page's own script — the largest — does not, and its helpers carry the names the removed
deco sweep held (`padTwo`, `localDay`, `localClock`), the collision the IIFE exists to prevent. Fix:
wrap it; add the check the invariant lacks (a runner assertion or a static pin).

### R3 — Hand-written types blind the type check to the host's surface moves
Reported by: typescript (must-fix, `profiler.ts:36-53`, proven: a declaration rename leaves the
check at exit 0 while a derived context errors), architect (should-fix, `profiler.ts:36-59`).

The capture keeps hand-written `Context`/event types where the host's published declarations are
the authority (R24's own rule: no dev-owned stand-in shadows a published package). Open with it:
the typescript seat's probe says 2.4.1's top-level `sessionID` has no declaration in the published
types — the fact P3 settled from the host source, not its types; if so, the check cannot see the
one field the capture exists to read, and that is R9's deferral's territory. Fix direction: derive
the context as `index.ts:130` does; settle the declaration question; the leaf's rule gains the
caveat or the ticket gains the fact.

### R4 — The repair verb reports edges it did not write, on fixtures that cannot occur
Reported by: python (should-fix ×2 — `stores.py:104-126` counts a guard-left file's would-be fills
as `repaired` against its own docstring, branch untested; the 2.3.2 fixture at
`test_devpro_profiler.py:1824` is stored text the shipped capture never writes, hiding that a
2.3.2 record's id is unrecoverable), architect (should-fix — the `(result clipped)` label narrower
than the count's semantics), typescript (question — fixture provenance).

Fix direction: the verb reports only written fills; the fixture becomes realizable or the
2.3.2-unrecoverable truth gets its own pin; label and gloss match the count.

### R5 — Second homes for values the plan centralized
Reported by: python (should-fix — `pages.py:802-806`, `:916` duplicate `dashboard/server.py:73-79`,
`:52` while the docstring claims "the one lookup"; `hooks.py:211-213` re-spells launcher literals
beside `LAUNCHER`/`OLD_LAUNCHERS`), shell (should-fix — the candidates spelled twice in
`profiler.sh`, loop and message), architect (should-fix — `hp` residue at `view.html:5` where the
provenance banner contradicts its twin, `view.html:335`, `profiler.ts:184`).

Fix direction: one home each; the launcher's double spelling rides the one-path ticket's rewrite.

### R6 — The runners' DOM stand-in exists in three copies
Reported by: architect (should-fix — `profiler_browser_runner.ts:38-180` re-implements
`profiler_index_runner.ts:31-124`, a third copy in `profiler_page_runner.ts`, ~130 lines each; the
geometry/URL tests are the browser runner's unique value).

Fix direction: one stand-in module; the runners keep their carriers.

### R7 — The leaves and SPEC state what the code does not
Reported by: shell (should-fix — `harness-profiler.md:73` says `sh`, the code runs `/bin/bash`;
`:20` says the skill's "`HP` line" where the skill spells `PROFILER`; the "named by the wrapper's
own refusal"/"no output" phrasing overclaims at the edges), architect (must-fix — the subcommand
list at `:14-15` omits `repair`, which `cli.py:69-74` dispatches and the leaf's own `:212-216`
names; the leaf contradicts itself), python (question — same list; SPEC `shipped-files.md:110-111`,
`:159-160` say a failing capture "exits 0 with no output" while the launcher names failures on
stderr in its non-capture path).

The subcommand-list defect entered with P7's own applied pair — the session's drafting miss, the
PE review missed it too. Fix direction: the doc corrections, named per site.

### R8 — ROADMAP's tickets carry false premises and plan-labeled history
Reported by: prompt-engineer (must-fix — the backup-glob ticket's `-pre-repair-<n>` renames never
shipped; the shipped repair makes no backup — the directories came from a scratch probe; plan
labels P1/P3/P6 survive in a doc that outlives the plan; ":209 points at a directory, not the
leaf"; ":266 — copies what, where?"), architect (should-fix — the same ticket; its one-path ticket
states the bounded read in the present tense where it is the target state).

Fix direction: rewrite the affected tickets to the real surface, de-plan-label them, fix the
Testing-category placement (two non-testing tickets under `## Testing`, `## Bugs` empty).

### R9 — CONVENTIONS' statements diverge from practice and from each other
Reported by: shell (should-fix — the shell rule states `set -euo pipefail` unconditionally with no
exception for a hook launcher whose exit contract forbids `-e`, proposed wording in the seat's
report; question — the banner's "do not edit here" vs the committed copy being "the operator's to
tune"), prompt-engineer (must-fix — `a-host-version…md:9-13` restates `recipes.md:57-65`'s
mechanism where it should cite; should-fix — the pronoun reversal at `:6-7`; the stand-in leaf's
residue clause restates `obviated-code-is-deleted-not-parked.md`; the verbatim leaf carries a
third wording of the declarations rule; "runner" names two referents across R24/R25/R23;
blocker — `recipes.md:63-64` carries a deferral inline in a contract doc; reference slots not
re-taken).

Fix direction: cite where the mechanism lives, state each rule once, take the shell rule's
exception, resolve the banner question as the owner's.

### R10 — The launcher's runtime edges
Reported by: shell (should-fix — the capture child's stdout is left on the hook's stdout where the
host reads hook JSON, measured; the success path's stdin can go undrained where a child exits
before reading; the `exec` the before side carried is dropped; the failure message spells both
candidates where naming the directory would do).

The stdout leak is a code fix; the rest ride the one-path ticket's rewrite. The shell seat also
reports outside its file: claude.py carries two interpreter policies; stale installed `hp.sh`
copies stand beside `profiler.sh` (the install renames forward, never removes — prompt-engineer
blocker concurs); the sibling reminder resource runs `set -euo pipefail` under an exit-0 contract.

### R11 — Build tooling
Reported by: typescript (should-fix — `justfile:238` runs `bun install --frozen-lockfile` against
npm's `package-lock.json` with no `bun.lock` committed, re-migrating every run; questions —
`tsconfig.json:12`'s include depth, `@types/node` vs the host's Bun, dynamic imports typed `any`,
brand casts), architect (question — whether the frozen-lockfile run writes a lockfile against the
lint recipe's read-only rule).

Settled, reopened and recorded: the compiler rides unpinned by the design's explicit text — no
action. The lockfile mismatch is the finding.

### R12 — The index's dispatched-agents column renders empty
Reported by: python (question — `pages.py:1106`: `<td class="col-agents"></td>` empty on every
row, the count sitting in the session cell, while the design's mapping states `agents` renders
into that column).

Either the render's defect or the mapping's misread; one of the two is wrong. Fix direction:
establish which, fix it, and the pair's text follows the truth.

### R13 — Test-discipline residue
Reported by: python (notes — the CSS comment contradicting `table-layout: fixed`; form pins in
the index test; attribute-order pinning; a multi-sort URL hole; the string-guard fall-through
untested), typescript (should-fix — a `find` type predicate where a cast stands; the deco body
unexercised, both runners' `querySelector` null).

Fix direction: per site, in the burndown's grouping.

## Open questions for the owner

- The banner's "do not edit here" against the committed copy's tune-rights (shell F5) — which
  authority wins?
- The 2.4.1 `notice` fixture vs the capture runner's text disagree about the host's wording
  (python Q8) — which is the host's?
- The pre-P6-launcher ticket describes a launcher that no longer ships (prompt-engineer) — retire
  or rewrite?
- `ROADMAP.md:158-163` overlaps `NEW_PROJECT_SETUP`, and names a generated file (prompt-engineer).
- `ROADMAP.md:64-72` — owner's verbatim text, unchanged by this review.
