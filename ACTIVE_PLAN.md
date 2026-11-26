# ACTIVE PLAN

## The post-plan run's contract gaps stated as house rules

This plan carries the four contract gaps the four-changes plan's run surfaced, which that plan's
scope did not cover, as three packages: the checkpoint gate runs the linter (G1), the settings
tables' grammar is stated once and a renamed leaf takes its contents entries (both G2), and the
amended pair is named where the application rule lives (G3). The plan has no design behind it — the
operator directed the gaps straight to a plan, and each is a process or house-rule change, which no
design's deltas carry. Every package's intended lifetime is **shipped**. Recorded here, fact and
not a package: the periodic-review count reads overdue — well past the interval of 8 since
`8ccbac74`; the exact count reads when the review is made active — and the **operator takes the
periodic review up for the next plan they run**; this plan defers it by direction. All packages are
doc-only: each done-line names document checks only.

## Status

| Package | State | Rating |
|---|---|---|
| G1 | landed: 246325b5 | mechanical |
| G2 | landed: 849558f5 | mechanical |
| G3 | landed: 8e9c5e83 | expert |
| G4 | landed: 53ee57f4 | expert |
| G5 | in progress | mechanical |
| H1 | drafted | expert |
| H2 | drafted | expert |

## G1 — The checkpoint gate runs the linter

mechanical. Scope: `PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md` — two edits,
both in this leaf: the binding line and one new paragraph after the block.
Fact, with the quoted line: the binding block (lines 4–6) reads

```
checkpoint gate: `just test`, then `just sweep-python` (A checkpoint includes the sweep)
step-down application: the dispatch's `model` parameter
periodic review interval: 8
```

The binding line becomes: ``checkpoint gate: `just test`, then `just lint`, then `just sweep-python`
(A checkpoint includes the sweep)``. The new paragraph, the landing rule, reads: "The landing rule:
a plan is landed only when the gates have been run over its last landing commit, not over each
package's own."
Ruling, stated: the landing rule stays prose in this leaf, with no check target, and G1 stays
doc-only. It is process discipline of the same shape as the binding block's own rules — nothing
checks that the gate runs once before a checkpoint commit either — not a machine guarantee; a
target would have to read history (which commit is the last landing, whether the gates ran over
it), which no cheap tree check does. It does not move to
`a-checkpoint-includes-the-sweep.md` (that leaf's subject is the sweep's cross-file reading, not
when the gates run) and does not get its own leaf: one sentence does not carry one.
The named defect: the four-changes plan's post-plan review found `just lint` red at HEAD through a
whole plan's run because no gate named lint, and proposed both the gate line and the landing
sentence.
No target pins this package: no test covers a landing invariant, and the binding line is prose —
the done-line's link check checks links only. Stated so the absence is not read as an omission.
Reference search and answer:
`git grep -n -F 'checkpoint gate' -- PROJECT_DOCS/CONVENTIONS/` names `the-gates.md:4` alone.
Done-line: `just dev-check-links`, run once at this package's end.

## G2 — Two house rules with their listings

mechanical. Scope: two new CONVENTIONS leaves —
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-top-level-key-is-a-bare-harness-name.md`
and
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-renamed-leaf-takes-its-contents-entries.md` —
and the three listing files the searches name: `code-definitions-and-install/index.md`,
`planning-and-execution/index.md`, `CONVENTIONS/entry-point.md`.

- New `a-top-level-key-is-a-bare-harness-name.md`, body: the devpro settings file's top-level key
  is a bare harness name; `[<harness>.model-map]` is that harness's nested subtable; a quoted
  dotted top-level key (`["claude.model-map"]`) names no harness's table and is refused with the
  unknown tables, naming the table and the supported harnesses; and the trap the rule answers: a
  quoted key parses and reads plausibly, so a reader meets it and re-litigates it. The behavior is
  SPEC.md, Rendering's.
- New `a-renamed-leaf-takes-its-contents-entries.md`, body: renaming, retitling or re-homing a
  leaf moves every listing that names it — the category's index and the volume's entry-point — in
  the same change. `just dev-check-links` catches the broken link; a listing still naming the old
  path is the residue the check cannot see.
- The listings, by the searches and their answers: `git grep -n -F 'Obviated code is deleted' --
  PROJECT_DOCS/CONVENTIONS/` names four sites — the obviated-code leaf itself,
  `code-definitions-and-install/index.md:25`, `CONVENTIONS/entry-point.md:35`, and
  `code-definitions-and-install/a-stand-in-models-the-api-s-real-semantics.md:7` (a cross-reference
  in another leaf's prose: it cites the rule, it does not list it, so it does not join). The
  grammar leaf joins the two listings — one entry in `code-definitions-and-install/index.md`, one
  in `CONVENTIONS/entry-point.md`. `git grep -n -F 'A checkpoint includes the sweep' --
  PROJECT_DOCS/CONVENTIONS/` names four lines — `CONVENTIONS/entry-point.md:48`, the sweep leaf
  itself, `planning-and-execution/index.md:9`, and `the-gates.md:4` (its parenthetical repeats the
  rule and is not a listing, so it does not join). The renamed-leaf rule joins the two listings —
  one entry in `planning-and-execution/index.md`, one in `CONVENTIONS/entry-point.md`.

Done-line: `just dev-check-links`, run once at this package's end.

## G3 — The amended pair is named

expert. Scope: `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`
— the leaf gains a sentence naming the amended-pair case explicitly: a pair whose target leaf a
later change retouches is amended in that change — the Becomes re-pointed to the leaf's final
wording and the As moved to what stood when the pair was written — and the amended pair must read
landed against the leaf's new text, never pending or drifted. The named defect: B6 amended a pair
whose As-text the checker still paired against the pre-amendment leaf, and `--deltas-applied` read
the pair drifted until the As moved; B4 amended three pairs the same way. The probe that shows the
case: re-pointing only the Becomes of an applied pair makes
`just dev-check-design-deltas-applied` read the pair drifted, not landed — the check matches the
pair's normalized As/Becomes text to the leaf and reports a state; it does not read the pair's two
passages as separate documents. Done-line:
`just dev-check-links`, run once at this package's end.

## G4 — Post-plan review

Scope: the changes G1–G3 landed — process and house-rule text the plan changed — read by the
post-plan reviewers against the project's standards and fitness for purpose. Ruling, stated: two
seats. `devpro-prompt-engineer` — the project documents changed, its standing trigger.
`devpro-architect` joins: G2's grammar leaf states how the settings parser behaves (the refusal,
and what its message names), a project document's claim about the code, which is the architect's
trigger. Each reviewer writes their own review to `.devpro-temp/`, independently; this session
synthesizes them into `ACTIVE_PLAN_REVIEW.md`.

Done-line: `just dev-check-links`, run once `ACTIVE_PLAN_REVIEW.md` is written.

## Post-plan burndown

The items below are drafted from [ACTIVE_PLAN_REVIEW.md](ACTIVE_PLAN_REVIEW.md) — they cite its
defect IDs; the review document is the finding of record.

### G5 — Post-plan burndown drafting

Drafted from [ACTIVE_PLAN_REVIEW.md](ACTIVE_PLAN_REVIEW.md): the two items below, each carrying
its defect IDs, scope, rating and one-commit close; one `devpro-prompt-engineer` usability review
over the drafted items together, its revision applied, then each item's row set by its state.

### H1 — The amended-pair paragraph states the checker truthfully (R1)

expert. Scope: `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`
— the amended-pair paragraph restated to the verified mechanism: the Becomes is the
drifted↔landed hinge (the check matches each passage, normalized, against the whole leaf), an
unamended As reads `landed` and nothing catches it, the As move is the application discipline no
target verifies — the residue stated, not hidden — and the probe account corrected to the
architect's probe (a re-pointed-only Becomes is not read drifted once the leaf is retouched; the
drifted reading belongs to the pre-retouch state). The named defect: the paragraph asserts the
checker polices the As move, the one edit no check verifies. Done-line: `just dev-check-links`,
run once at this package's end.

### H2 — The new leaves state what the checkers and the altitude give (R2, R3, R4)

expert. Scope, three leaves:
- `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-top-level-key-is-a-bare-harness-name.md`
  stripped to the one trap SPEC lacks — a quoted dotted key parses and reads plausibly, the reader
  meets it and re-litigates, the refusal is SPEC Rendering's — its behavior statement removed (R3).
- `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-renamed-leaf-takes-its-contents-entries.md`
  resolved against `CONVENTIONS/planning-and-execution/project-documents.md:9-13` — where the rule
  is already carried, the leaf and its two listing entries are deleted; where restating serves, the
  leaf states the true reach: the old-path listing is the dead link the check catches, the stale
  title or dropped listing is the invisible residue (R2).
- `PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md` — the landing rule's placement
  and wording per R4: inside the binding fence as a stated gate line, or worded so the observation
  it names (the gate log at the landing commit) is readable at the site (R4).
Done-line: `just dev-check-links`, run once at this package's end.
