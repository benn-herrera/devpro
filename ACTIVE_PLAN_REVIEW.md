# ACTIVE_PLAN_REVIEW — "The test suite earns its keep", post-plan review

Provenance: five independent reviewer seats — `devpro-python-coder`, `devpro-shell-dsl-coder`,
`devpro-typescript-coder`, `devpro-architect`, `devpro-prompt-engineer` — dispatched with the
project documents and `ACTIVE_DESIGN.md` and without the plan, over the range `bcd7cdf..f8552ac`
(P1–P9). The interrupt leaf and its contents rows landed in `f2c7e9e`, an ancestor of the stated
range; the seats whose questions reach it reviewed it anyway. Their reviews live at
`.devpro-temp/review-postplan-{python,shell,typescript,architect,prompt-engineer}.md`; this document
is the de-duplicated account: one entry per defect, naming every seat that reported it. Where seats
rated the same defect differently, the severity below is the reconciled one and the spread is noted.

Every finding below survives the tree as it stands after P9. Verified-and-clean accounts the seats
ran (surface collection counts, the single-home chain `package.json`→`bun.lock`→installed
declarations, shellcheck, link check, the marker law's reach, the merged tests' duplicate verdicts)
are not repeated here; they live in the seat files.

## Findings

### F-01 — The justfile's `test` note states the default exclusion for one marker and is silent on the other [Warning]

Seats: shell (Warning), prompt-engineer (Critical). Reconciled: the shipped behavior is correct;
the note — the human entry point to the surface machinery — states less than `test.sh` does, and
its "cold-read runs the marker's tests as its default -m" clause now has a sibling surface it does
not cover. Cost lands on the next reader and the next marker, so Warning.

Where: `justfile:199-206` against `devtools/scripts/test.sh:17-20`, `:98-103`. The no-argument
run's parenthetical names `cold_read` only; the surface list carries `slow` with no default-`-m`
statement. The grep for standing text (prompt-engineer) returns this as the one remaining drift.

Change: name both markers once each — "the cold_read and slow markers excluded by default" and
"cold-read and slow each run their own marker as default -m" — as description, not as a second
enumeration of the surface list.

### F-02 — Two records still say the TypeScript check reads "the host version their headers name" [Warning]

Seats: shell (Warning), python (Note). After P4 dropped the pin from the headers, no header names
a version, and the check reads the version `package.json` pins. `justfile:218-221` (the `lint`
note) and `PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md:47` state the old shape.
The recipes leaf and the CONVENTIONS leaf were both amended; these two were not.

Change: `justfile:220` → "against the host's published declarations, the version `package.json`
pins"; the same correction at `why-there-is-no-verification-verb.md:47`.

### F-03 — The pin-numeral removal left the records that anchored on the entry's version claim [Warning]

Seats: typescript (Warning ×1), architect (Warning ×1), python (Note, the same seam seen from the
retired test's contract). Three sites of one root cause — the design's "records that name the
header-named version move with the change" missed the anchors that were not literal restatements:

1. `devpro/harnesses/resources/opencode/index.ts:126-127` — "checked against the declarations of
   the version this file names": the file names only a floor now; the referent resolves to nothing.
2. `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-harness-resource-s-version-claims-testing.md:3,8`
   — "opencode's entry names 2.4.1, what it has been used with most": the entry's header carries no
   numeral, and the leaf's premise ("a version this project's harness resources name") no longer
   describes the headers at all.
3. The patch-level "used with most" claim itself now lives nowhere: the pin moves for the
   declarations, not for use. The python seat's change: decide where the claim lives (the leaf's
   phrasing points at `ARCHITECTURE/install/opencode-entry.md`) or retire it into the version
   observations the prose already carries.

Change: rewrite `index.ts:126-127` to name the declarations as what the check reads (the host
declarations installed at `package.json`'s pin); move or fold the CONVENTIONS leaf onto the prose
observations it still describes (profiler.ts:11's "observed working from" lines), or retire it;
settle the "used with most" claim's home. The first two are the design's order completed; the
third is a decision the owner may need to make.

### F-04 — Two resource headlines name a floor their bodies never observe [Warning]

Seat: typescript (Warning). `guardrail.ts:3` and `profiler.ts:3` carry `(floor 2.3.0)` with no
qualifying phrase and no body observation earning it — every earned floor in the tree is behavioral
and lives in `index.ts:10-14` (`:157`), and `guardrail.ts` touches no host surface beyond a type
import and `Plugin.define`. The change did not introduce the claim (it kept the numeral verbatim),
but it chose which half of each headline to keep.

Change: drop the numeral from `guardrail.ts:3`'s headline; at `profiler.ts:3`, either state the
floor where its own line records the observation (`profiler.ts:10-13`) or tie the headline's floor
to `index.ts`'s, as the CONVENTIONS leaf's rule requires.

### F-05 — The interrupt leaf needs the revision its first use will force [Warning]

Seat: prompt-engineer (three Warnings — its F2, F3, F7 — and three Notes — F4, F5, F6). One root
cause: the leaf's text was written as a design input, not as a rule an executing agent applies.
The findings, in the leaf's order:

- The catch-all's "scope finding" never states its relation to the word "finding" the shipped
  process (`devpro/definitions/skills/development.py:298-299`) uses for the same event, and the
  body never uses the title's "unstated behavior". (Warning)
- `isolate` names no marker form (`skip` with a reason vs `xfail(strict=True)` — the difference
  between an interrupt that is counted later and one that vanishes) and no witness that the
  quarantine was carried into the run. Whether the plan form can hold the record at all — no state
  or note form names it — is the architect's contract addition. (Warning)
- "Enters the active plan as an interrupt" presumes an executor who can edit the plan; the leaf
  names no act for the dispatched seat. The reader is the arbitrating session; say what the coder
  does — "the package stops, the interrupt is reported to the dispatching session with the test's
  name and the evidence for each verdict it considers". (Note)
- `axe`'s "checksum over text" is a necessary condition where the law's
  (`repo-layout.md:51`) is sufficient; the reader holding only the leaf loses the law's contract
  exception. Two words carry it: "a checksum over text, unless the text is the contract". (Note)
- `acquit`'s "or on its environment alone" is unverifiable and adds no act the first clause lacks;
  delete it, or replace it with the observable ("the same failure reproduces on the base revision,
  recorded with the command and its output"). (Warning)
- The heading is the tree's longest slug and resists the `CONVENTIONS.md, <title>` citation form.
  A shorter title that keeps the subject costs a file rename. (Note)

Change: one revision of the leaf applying these, with the plan-form question (whether the interrupt
reaches a state note, a section, or a new form element) settled by the architect before the wording
lands — the design carries no entry for it, and the shipped clause's word is still "finding".

### F-06 — The law's 30-second target sentence states a figure every run of the tree contradicts [Warning]

Seat: architect (Warning). `PROJECT_DOCS/ARCHITECTURE/repo-layout.md:58` — "The default run targets
30 seconds" — against the measured default `devpro` surface: 51-56s across the acceptance runs
(1662 passed, 1 skipped, 34 deselected). The design's own arithmetic anticipated this: the
protected install suite alone measures 17.5-19.3s, the guardrail suite's perl floor 2.0s, and the
editable remainder ~33s against the target's implied ~12.5s. The 100ms law itself is not violated —
the slowest calls are dashboard boots and install runs the law's own justification clause covers.

Change: the plan stated P10 reports, not forces, the target — so the landing either amends the
sentence to the measured state the pass reached, with the ambition moving to ROADMAP, or keeps the
figure and opens the ticket that carries it. A contract leaf carrying a number the tree never
meets is the defect; which of the two fixes is the owner's call.

### F-07 — The single-home rule's restatement is circular and its rule lives in two homes [Note]

Seats: architect (Note — `recipes.md:64` "names the floor its header already names" states
nothing), prompt-engineer (Note — the amended CONVENTIONS leaf and the recipes clause state one
rule at two strengths; the fix is a delete on one side).

Change: architect's wording — "a resource's header keeps the floor it already names and names no
version of the moment" — and one of the two homes keeps the rule's sentence, the other the
mechanism.

### F-08 — `test.sh`'s header states the `slow` machinery but not its bound or its reason [Note]

Seats: shell (two Notes), architect (Note — the same bound seen as the law's sentence outrunning
the surface). Two one-line additions to the header at `test.sh:17-20`: the `slow` surface's
directory bound ("the `slow` surface runs the `devtools/tests` cases marked `slow`" — a marked
`tests/` test is otherwise excluded from every default run and unreachable by `just test slow`),
and the reason the default refuses the marker's tests (the screenshot cases' wall time), which
today explains `cold_read` only.

### F-09 — The merged long-poll test cannot see a poll that never answers [Warning]

Seat: python (Warning; the query-survival arm was shown live by probe, the timeout arm was not —
the probe hung, which is itself the finding's shape). `tests/dashboard/test_board_panel.py:326`
bounds `waited[0]` by `LONG_POLL_SECONDS` (25.0) while the wait it observes terminates at the
fixture's `_TIMEOUT` (10): a regression that never satisfies the poll's condition makes the waiter
block until shutdown wakes it, `waited[0]` sits under 25, and the assertion passes in silence. The
merge dropped the sibling's bound.

Change: `assert 0 < waited[0] < _TIMEOUT` — and the run that plants the never-answering poll and
shows the failure, so the finding stops resting on reading.

### F-10 — Session-scoped fixtures and the scratch-HOME rule disagree on the shared tier [Warning]

Seat: python (Warning, partial evidence). `PROJECT_DOCS/CONVENTIONS/planning-and-execution/scratch-for-tests-and-recipes.md`
— "Anything that renders or installs in a test or a recipe runs under a scratch `HOME`" — is served
by `tests/conftest.py`'s `_home`, which is function-scoped and autouse; a session-scoped fixture
sets up at a point pytest chooses, outside any test's home. Whether `tests/test_devpro_profiler.py:132`'s
`_launcher` and `tests/dashboard/test_board_panel.py:116`'s fixtures run the install under a
scratch `HOME` is unstable across selection (`-k`, file arguments, cache reruns). A probe of the
board panel's path on this host does not fail; the finding is the mechanism, not an observed leak.

Change: one record beside `_home` in `tests/conftest.py` stating how a session- or module-scoped
fixture gets its scratch home (or, if the install path reads no home, the CONVENTIONS leaf's
sentence is the one that should say so), so the next shared fixture follows a stated rule.

### F-11 — The dashboard merges left two stale records and one dead surface [Note]

Seat: python (Note — the module docstring), architect (Note — the fixture's stderr half). The
module docstring at `tests/dashboard/test_board_panel.py:6-7` still says the two suites "are not
repeated here" after P7 moved the root-escape arm across them (its own text under-states what the
board panel now carries); and the session `panel` fixture (`:124-136`) yields a stderr half no
test consumes — the capture is load-bearing, the yielded second element is not.

Change: add the escape arm to the docstring's parenthetical (or drop the arm from the survivor);
yield the client alone and keep `err` local to the fixture.

### F-12 — The dupe_sweep rewrite left the corpus's error conversion untested [Note]

Seat: python (Note). `devtools/dupe_sweep/corpus.py:31-32` converts `CalledProcessError` to
`SweepError` and no test exercises it; the rewritten CLI tests mount the corpus's refusal instead.
A conversion regression would ship a wrong verdict green.

Change: one case calling `code_corpus(rev="no-such-revision")` asserting `SweepError` — a single
`git ls-tree` call, no sweep.

### F-13 — The profiler fixture's name outlived the mechanism it named [Note]

Seat: python (Note). `tests/test_devpro_profiler.py:132` names the fixture `_launcher` for a
wrapper — the word every other name in the file uses, and the word `devpro/profiler/hooks.py:40-42`
retires. Rename to `_wrapper` (and `_run`'s `launcher:` parameter to `wrapper`) in one edit.

## Seat findings recorded without an entry

- The installed plugin trees (`.opencode/plugins/devpro/`, `.claude/skills/devpro/`) and the
  `rendered/` reference renders carry the old headline numeral: installed and reference trees,
  refreshed by an install or a retake, not source (typescript seat).
- `devtools/scripts/test-changed.sh:20`'s surface list omits `cold-read` and `slow` (python seat):
  unrelated to this diff; `devpro`'s default `-m` covers the exclusion.
- `test.sh:100-103`'s restatement of the default marker string is bounded file-local duplication
  the shell seat judged not worth the change.
