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
| P2 | dispatchable | mechanical | applies the guide.py pairs and the SPEC delta's two pairs |
| PR | dispatchable | expert | review of what shipped, written to `ACTIVE_PLAN_REVIEW.md` |
| B0 | drafted | expert | Post-plan burndown drafting: the section's items from the review, then their usability review |

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
