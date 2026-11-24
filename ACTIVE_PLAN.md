# Plan — the burndown is a section with a drafting ticket

Implements [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md): its [SPEC delta](ACTIVE_DESIGN.md#spec-delta) —
[the post-plan packages rule](ACTIVE_DESIGN.md#the-post-plan-packages-rule) and
[the post-plan package kinds](ACTIVE_DESIGN.md#the-post-plan-package-kinds) — and its
[Code delta](ACTIVE_DESIGN.md#code-delta) in full:
[the development skill's burndown shape](ACTIVE_DESIGN.md#the-development-skills-burndown-shape) and
[the guide's burndown account](ACTIVE_DESIGN.md#the-guides-burndown-account). Every package below
is **shipped**. Each closes in one commit.

The shape this plan installs is the shape this plan itself follows: its own burndown is already a
`## Post-plan burndown` section holding the drafting ticket B0, drafted from the landed plan's run
(`git show c45641a:ACTIVE_PLAN.md`, the section and its B0–B9 items; landing summarized in
`git show 287175b`). The plan's own form is the standard the packages below write into the skill
source and the SPEC.

## Facts the packages rely on

- Definition modules hold only constants; the pairs quote source text containing placeholders
  (`{REVIEW_DOCUMENT_TERM}`, `{clauses.ref(name="...")}`) that must land byte-exact as source, not
  as rendered output (CONVENTIONS, *Definition modules hold only constants*). `just test` fails on
  any other top-level statement, so a mangled constant surfaces at the gate.
- Installed copies under `.opencode/` are rendered artifacts. Prior definition-body commits
  (8838000, 6cec5f4) changed only the source and left the install to the next install run; no
  package here re-renders or re-installs. `just dev-check-design-deltas-applied` reads the source
  tree, not the install.
- The pairs apply verbatim with whitespace-squash matching, verified by
  `just dev-check-design-deltas-applied` before each application's commit (CONVENTIONS, *A delta
  application ends verified*). The check resolves each pair's target from the design entry heading's
  one link, so a green or failing run's numbers are the application's witness.
- Each application is followed by a search of the doc set for the wording the application replaced
  (CONVENTIONS, *A delta application is followed by a search of the doc set*). The command, run
  after each package's pairs are applied:

  `git grep -n -e 'ends with two packages' -e 'ends in two more packages' -e 'the post-plan burndown are work packages' -e 'a **post-plan burndown package**' -e 'burndown package' -e 'two more packages' -- PROJECT_DOCS`

  For each hit: a statement the application leaves false is reported to the session for the commit
  that carries the change, never rewritten inside the applying package; a statement still true is
  recorded in that package's commit message — the commit message is the record — with the hit and
  the reason it stands. The expected hits are `PROJECT_DOCS/SPEC/plan-status-form.md:59-62` and
  `PROJECT_DOCS/SPEC/dicing/checks.md:103-109`, both false under the shape until P2 applies the
  SPEC delta's pairs; a hit anywhere else is read before it is judged.
- The checkpoint gate is CONVENTIONS-bound: `just test`, then `just sweep-python`, before each
  checkpoint commit.
- The design states the skill section's remaining bullets stand unchanged and the checker changes
  not at all — it already reads the section shape, as the landed plan's own form passing
  `check-plan` proves. The only document edits in this plan are the SPEC delta's own pairs, which
  belong to P2.

## Status

| Package | State | Rating | Scope |
| --- | --- | --- | --- |
| P1 | landed: 67c13e3 | mechanical | applies the development.py pairs |
| P2 | landed: 90cd6cc | mechanical | applies the guide.py pairs and the SPEC delta's two pairs |
| PR | landed: 2846a42 | expert | review of what shipped, written to `ACTIVE_PLAN_REVIEW.md` |
| B0 | landed: 80b1518 | expert | Post-plan burndown drafting: the section's items from the review, then their usability review |
| B1 | landed: 278d229 | expert | the pairing identity: the checker's terms, messages, and the rule's heading requirement |
| B2 | landed: 09c934a | mechanical | the development skill's reworded sentences: Periodic review, items' identity, re-wrap |
| B3 | dispatchable | mechanical | the guide's walkthrough: reviewer/revision named, steps 4 and 6, re-wrap |
| B4 | dispatchable | mechanical | the CONVENTIONS lines the run earned: width-prohibition trap, staging practice note |
| B5 | dispatchable | mechanical | the staging rule joins the skill's Dispatch section (the design's fourth pair) |

## Sequencing

- P1 → P2, in that order. The two code entries are one product surface — the rendered skill and
  guide text — but the delta check reads every pair at once, so the applications land serially:
  each package's application, check run, and doc-set search stay attached to their own commit.
- P2 carries the SPEC pairs with the guide pairs because they are one motion: the SPEC's plan-form
  language goes stale the moment the shape is real, and the guide is what tells the shape's
  readers. The delta check goes green only here.
- PR follows the code packages. B0 follows PR, per the section shape.

## P1 — the development skill's burndown shape

Applies [the development skill's burndown shape](ACTIVE_DESIGN.md#the-development-skills-burndown-shape):
all three pairs, verbatim, to `devpro/definitions/skills/development.py`.

**Scope.** `devpro/definitions/skills/development.py` — nothing else.

**Facts.**

- The three pairs are quoted in full in the design entry; the middle pair replaces one bullet with
  three. All placeholder syntax lands as written in source.
- The entry's closing paragraph is the boundary: the section's remaining bullets (the reviewers,
  the independent writes, the synthesis, the review document's deletion at landing, the release's
  user-flow audit) stand unchanged. Any drift beyond the quoted text is outside the pair and wrong.

**Guidance.** Apply by exact match; `just dev-check-design-deltas-applied` is the judge, not the
eye. After this commit the check still fails — the guide.py and SPEC pairs are unapplied — and that
is the expected result, not a defect.

**Done-line.** `just dev-check-design-deltas-applied` exits 1 with `pairs: 8, landed: 3, pending:
5`, and every `pending` line names `devpro/definitions/skills/guide.py`,
`PROJECT_DOCS/SPEC/plan-status-form.md`, or `PROJECT_DOCS/SPEC/dicing/checks.md`; any `drifted` or
`conflicting` line, or any `pending` line naming `devpro/definitions/skills/development.py`, is a
failure of this package. `just test-changed` passes. The doc-set search has run and its verdicts
are in the commit message.

**One commit.**

## P2 — the guide's burndown account and the SPEC's plan-form language

Applies [the guide's burndown account](ACTIVE_DESIGN.md#the-guides-burndown-account) — all three
pairs, verbatim, to `devpro/definitions/skills/guide.py` — and the SPEC delta's two pairs to
`PROJECT_DOCS/SPEC/plan-status-form.md` and `PROJECT_DOCS/SPEC/dicing/checks.md`.

**Scope.** `devpro/definitions/skills/guide.py`; `PROJECT_DOCS/SPEC/plan-status-form.md`;
`PROJECT_DOCS/SPEC/dicing/checks.md` — nothing else.

**Facts.**

- The guide's third pair sits inside a numbered walkthrough; its replacement keeps the number and
  the surrounding lines untouched.
- The SPEC pairs quote-verify against their targets as the source pairs do: each `as it stands`
  block matches its leaf today, each `becomes` block must match after application, whitespace
  squashed.
- After this commit all eight pairs are applied.

**Guidance.** Same as P1: exact application, the check as judge. The search matters most here —
"two more packages" is the phrase a human reader of plans was told, and other doc text describing
a plan's ending may carry the same claim in other words. Read every hit; report what the
application leaves false.

**Done-line.** `just test-changed` passes, then `just dev-check-design-deltas-applied` exits 0
green — `pairs: 8, landed: 8` — then `just dev-check-links` reports no break beyond
`ACTIVE_PLAN_REVIEW.md`, which PR creates. The doc-set search has run and its verdicts are in the
commit message.

**One commit.**

## PR — Post-plan review

The post-plan reviewers — the coder for the changed language, `devpro-prompt-engineer` (model-facing
text changed: this is the whole change — the rendered skill and guide text and the SPEC's plan-form
language — so this seat is the primary one), and `devpro-architect` (structure and the project
documents' claims about the code) — are given the project documents and
[ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), not this plan, and review the changes and their tests against
the project's standards and fitness for purpose. Each writes their own review in the scratch
directory, one path per seat — `.devpro-temp/pr-review-<seat>.md` (for example
`.devpro-temp/pr-review-prompt-engineer.md`) — so no two seats collide on one implied file name; the
session synthesizes them into `ACTIVE_PLAN_REVIEW.md`, de-duplicating and reconciling, without
waiting between the last report and the write-up. The review document is never diced. This
package's row goes `landed` in the commit that adds the review document.

**Done-line.** `just dev-check-links` clean, and the review document present at
`ACTIVE_PLAN_REVIEW.md`.

**One commit.**

## Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands; the findings' IDs below are
its. One package per root-cause group, one commit each, per the section shape this plan itself
follows: the section holds the drafting ticket, and the items it drafted under it. The checkpoint
gate —
`just test`, then `just sweep-python` — runs once, before each item's closing commit; each
done-line's final run is at that close.

### B0 — Post-plan burndown drafting

**Scope.** This section's items; the session is the worker.

**Facts.** The items below group the review's findings and contract gaps by root cause, each item
citing its IDs and carrying the quoted lines its executor acts on. B0's work: draft them, run their
`devpro-prompt-engineer` usability review, apply the session's one revision, and set each item's
row by its state: `dispatchable` where the review left nothing open; `drafted` where it did, the
note naming what blocks it.

**Done-line.** `just devpro-check-plan` green with every B-row's State cell matching the sentence
above; each item then dispatches under its own row.

**One commit** — the one carrying the items' usability-reviewed form.

### B1 — the pairing identity: the checker's terms, messages, and the rule's heading requirement

**Scope.** `PROJECT_DOCS/SPEC/dicing/checks.md` (the Terms definition, the form note at :126-130,
and the breach-message table), `devpro/doccheck/planform.py`, `devpro/doccheck/plancheck.py`,
`devpro/definitions/skills/development.py` (the rule's section-heading sentence only),
`PROJECT_DOCS/SPEC/plan-status-form.md` (the amended bullet — the title-only ruling touches it;
cite the architect seat's K2 correction when it does).

**Facts.**

- R1(a): `checks.md:105-110`'s amended Terms no longer define `post-plan burndown package` — the
  term its own messages emit at `:74, :124, :162-163` (`plancheck.py:40-41`). The pairing
  (`planform.py:378-403`) classifies by title alone; the Terms stay title-only and the definition
  keeps the term, naming the drafting ticket as what it now covers.
- R1(b): `planform.py:393-397`'s unpaired-breach message advises `## <ID> Post-plan burndown` — the
  section, not the ticket. The message states the ticket's title shape instead.
- R1(c): the rule text requires the literal `## Post-plan burndown` section heading *and* a ticket
  title opening with ID + `Post-plan burndown`; a ticket titled bare `B0` breaches pairing
  (`_title`, `planform.py:367-375` — the coder seat's probe). The rule's sentence says which title
  pairs and that the section heading is not a package title.
- The checks.md form note (:126-130) is the leaf's statement of title-only pairing — it must not
  re-assert the heading requirement in a form the rule's sentence contradicts.
- Session-level residue, reported not fixed: `_title` matches any heading opening with the ID, so
  "heading fails to open with the ID" is indistinguishable from "mentions it" — the obligation to
  keep section and ticket headings distinguishable survives as a silent violation; report to
  `devpro-architect` for the roadmap.

**Done-line.** `just test devpro`, then `just test-changed`, then `just dev-check-links`; then the
probe, twice: `PYTHONPATH=. .venv/bin/python .devpro-temp/pr-review-checkplan-probe.py` (clean) and
a second probe of the same shape whose unpaired plan prints the amended `accepted` text — both
results and the `accepted` string verbatim in the commit body. G3's normative sentence — the way to
verify a plan-form change is a `check-plan` run over a plan holding the new form — lands in
`checks.md` (the plan-form verifier's own leaf) in this package.

### B2 — the development skill's reworded sentences

**Scope.** `devpro/definitions/skills/development.py`.

**Facts.**

- R2: *Periodic review* still teaches the old model — the seat's quoted fix: "The burndown
  section's items cite that ID and group the findings by root cause, several findings to one item."
  (`development.py:482-485`.)
- R3: the items' identity and the placeholder mechanism. The mechanism is settled by the landed
  plan's own shape (`git show c45641a:ACTIVE_PLAN.md`): the items are sibling packages under the
  section; the placeholder text becomes the section-opening citation. The identity sentence — an
  item is a work package — comes from the seat's F2 (`pr-review-prompt-engineer.md:100-123`, which
  parts this package takes and drops are stated there); the section-dies act is stated per F2's
  third part. The architect seat's K3 (`pr-review-architect.md:113-114`) is the alternative wording
  the landed plan's shape supersedes.
- R5 (development.py side): the pairs' added lines (`:404-430`, `:480-485` — all exceed 90) re-wrap
  to the file's ≤ 90 columns; whitespace-squash keeps the pairs landed — verify with the delta
  check. Reachability note: the test corpus may carry the shipped sentence in an assertion; if a
  reword turns one red, that assertion moves with this package.

**Done-line.** `just test devpro`, then `just test-changed`, then the delta check:
`just dev-check-design-deltas-applied` exits 1 with `pairs: 9, landed: 3, pending: 1, drifted: 5`
— the `drifted` lines naming development.py's pairs 2 and 3 (this package's rewords superseded
their text) and the three pairs B1's title-only improvements superseded; the `pending` line naming
the staging pair (B5's). Any `conflicting` line, or any other `drifted` or `pending` line, fails
the package.

### B3 — the guide's walkthrough

**Scope.** `devpro/definitions/skills/guide.py`.

**Facts.**

- R4: the reviewer reading is settled — the guide's sentence follows the skill's exception verbatim
  (`development.py:407-411`): the items' review is the PE usability review and the session's
  revision. The regions and their rewords: the architect seat's K1 (`pr-review-architect.md:88-90`,
  two lines, both required) over `guide.py:322-332` and `:507-514`; the PE seat's F5
  (`pr-review-prompt-engineer.md`) for step 6. Do not paste a paraphrase where the skill's sentence
  is the shared text — cite it.

**Done-line.** `just test devpro`, then `just test-changed`, then
`just dev-check-design-deltas-applied` green.

### B4 — the CONVENTIONS lines the run earned

**Scope.** `PROJECT_DOCS/CONVENTIONS/planning-and-execution/` (G4's neighbour leaves:
`a-delta-application-ends-verified.md`, `a-delta-application-ends-by-searching-the-doc-set.md`).

**Facts.**

- The owner's ruling, recorded as the trap it is: source line width is not enforced in this
  project — the review's R5/G1 re-wrap finding is declined, and a review finding about source
  line width is declined by default. The pattern was killed once before as too expensive: agents
  obsess over widths, manually reflow, or write ad-hoc reflow tools. This CONVENTIONS line is the
  prohibition's home, so the next reviewer does not rebirth it.
- G4: promoted to the skill body at the owner's ruling — "general good behavior and collision
  prevention" binds every project the process ships to, not only this repo. The new pair on the
  skill's *Dispatch* section (the design's fourth development.py pair) is applied by B5; nothing
  here duplicates it.
- G2 is dropped at the owner's ruling: the brace-knowledge is self-evidencing (the render fails
  loudly on a mangled placeholder), and a pinned rule over prose is golden-master friction. If it
  bites again, the fix is one sentence in the constants leaf at that moment.
- Addressee note: G3's rule sentence — the `check-plan` probe over a plan-form change — landed in
  the skill's `check-plan` paragraph in B1 (where a plan-form editor reads); nothing here
  duplicates it.

**Done-line.** `just dev-check-links` (the tree and link check is the only one that sees new
leaves), then `just test-changed`.

### B5 — the staging rule joins the skill's Dispatch section

**Scope.** `devpro/definitions/skills/development.py` — the design's fourth development.py pair
only (the *Dispatch* section's staging bullet). Runs after B2: same file.

**Facts.**

- The pair is quoted in [the design's development.py entry](ACTIVE_DESIGN.md#the-development-skills-burndown-shape):
  the *Dispatch* section's "share a build run serially" bullet gains the staging bullet — a
  concurrent package stages and commits only its own paths, and where the index holds a path
  another package staged, that path is unstaged before the commit, or the commit waits.
- Applied verbatim; the delta check is the witness of the application.

**Done-line.** `just test devpro`, then `just test-changed`, then the delta check:
`just dev-check-design-deltas-applied` exits 1 with `pairs: 9, landed: 6, pending: 0, drifted: 3`
— every `pending` line gone; the three `drifted` lines are the pairs B1's title-only improvements
superseded (the development.py first pair and the two SPEC pairs), named as expected; any other
`drifted` or `conflicting` line, or any `pending` line, fails the package.
