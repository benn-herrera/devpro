# ACTIVE PLAN

## The post-plan run's contract gaps stated as house rules

This plan carries the four contract gaps the four-changes plan's run surfaced, which that plan's
scope did not cover: the checkpoint gate runs the linter, the settings tables' grammar is stated
once, the amended pair is named where the application rule lives, and a renamed leaf takes its
contents entries. The plan has no design behind it — the operator directed the gaps straight to a
plan, and each is a process or house-rule change, which no design's deltas carry. Every package's
intended lifetime is **shipped**. Recorded here: the periodic-review count reads overdue (~15 plan
landings since `8ccbac74`, interval 8) and the **operator takes the periodic review up for the
next plan they run** — this plan defers it by direction. All packages are doc-only: each done-line
names document checks only.

## Status

| Package | State | Rating |
|---|---|---|
| G1 | drafted | mechanical |
| G2 | drafted | mechanical |
| G3 | drafted | mechanical |
| G4 | drafted | expert |
| G5 | drafted | mechanical |

## G1 — The checkpoint gate runs the linter

mechanical. Scope: `PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md` — two edits.
Fact, with the quoted line: the binding block (lines 3–5) reads

```
checkpoint gate: `just test`, then `just sweep-python` (A checkpoint includes the sweep)
step-down application: the dispatch's `model` parameter
periodic review interval: 8
```

The binding line becomes: ``checkpoint gate: `just test`, then `just lint`, then `just sweep-python`
(A checkpoint includes the sweep)``. A new paragraph after the block: "A plan is landed when the
gates have been run on the last landing commit, not on each package's own; the checkpoint gate
binds what those runs are." The named defect: R2's `just lint` was red at HEAD through a whole
plan's run because no gate names lint (ACTIVE_PLAN_REVIEW.md R2, coder C1; the review's contract
gap carries both sentences' wording). Reference search and answer:
`git grep -n -F 'checkpoint gate' -- PROJECT_DOCS/CONVENTIONS/` names `the-gates.md:4` alone.
Done-line: `just dev-check-links`, run once at this package's end.

## G2 — Two house rules with their listings

mechanical. Scope: two new CONVENTIONS leaves and every listing that names a leaf of their
categories.

- New `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-top-level-key-is-a-bare-harness-name.md`:
  the devpro settings file's top-level key is a bare harness name; `[<harness>.model-map]` is that
  harness's nested subtable; a quoted dotted top-level key (`["claude.model-map"]`) names no
  harness's table and is refused with the unknown tables, naming the table and the supported
  harnesses. The behavior is SPEC.md, Rendering's; the rule is the trap: a quoted key parses and
  reads plausibly, so a reader meets it and re-litigates — the ruling's home is here, stated once.
- New `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-renamed-leaf-takes-its-contents-entries.md`:
  renaming, retitling or re-homing a leaf moves every listing that names it — the category's index
  and the volume's entry-point — in the same change. `just dev-check-links` catches the broken
  link; a listing still naming the old path is the residue the check cannot see.
- The listings, by the searches and their answers: `git grep -n -F 'Obviated code is deleted' --
  PROJECT_DOCS/CONVENTIONS/` names a code-definitions leaf's three sites (the leaf,
  `code-definitions-and-install/index.md:25`, `entry-point.md:35`); `git grep -n -F 'A checkpoint
  includes the sweep' -- PROJECT_DOCS/CONVENTIONS/` names a planning leaf's three sites
  (`entry-point.md:48`, the leaf, `planning-and-execution/index.md:9`). The grammar leaf joins
  `code-definitions-and-install/index.md` and `entry-point.md`; the renamed-leaf rule joins
  `planning-and-execution/index.md` and `entry-point.md`.

Done-line: `just dev-check-links`, run once at this package's end.

## G3 — The amended pair is named

mechanical. Scope: `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`
— the leaf gains a sentence naming the amended-pair case explicitly: a pair whose target leaf a
later change retouches is amended in that change — the Becomes re-pointed to the leaf's final
wording and the As moved to what stood when the pair was written — and the check reads both
passages of the amended pair. The named defect: B6 amended a pair whose As-text the checker still
paired against the pre-amendment leaf, and `--deltas-applied` read the pair drifted until the As
moved (the six-changes plan's B6 run; the same rule's shape as B4's three-pair amendment). Done-line:
`just dev-check-links`, run once at this package's end.

## G4 — Post-plan review

Scope: the changes G1–G3 landed — process and house-rule text the plan changed, read by the
post-plan reviewer for the project documents, `devpro-prompt-engineer` — against the project's
standards and fitness for purpose. The reviewer writes their own review to `.devpro-temp/`; this
session synthesizes it into `ACTIVE_PLAN_REVIEW.md`.

Done-line: `just dev-check-links`, run once `ACTIVE_PLAN_REVIEW.md` is written.

## Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.

### G5 — Post-plan burndown drafting

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
