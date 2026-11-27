# ACTIVE PLAN

# The second periodic review

The whole-project review over accumulated drift, staffed per the development skill's periodic-review
section plus the test-suite audit seat the ROADMAP Maintenance ticket charters. A prior periodic
review landed at devpro 0.17.2 (commit 69eed3ee); roughly nine plan-landings have accumulated since,
against the bound interval of 8 — the count is met, and the previous plan's landing was the coherent
feature boundary. The review has no design before it and goes straight to a plan; this plan is its
tracking surface. The user's standing direction: the review rolls through the findings collected and
the burndown items drafted, and holds there — the user discusses findings, remedies and the draft
before anything is approved or dispatched.

## Status

| Package | State | Rating |
| --- | --- | --- |
| R1 | landed | expert |
| R2 | drafted | expert |

### R1 — the panel runs and the findings synthesize

Intended lifetime: shipped. Rating: expert.

Nine seats run independently, each writing its own review to the scratch directory: the architect,
prompt-engineer, tech-writer and Python-coder pairs — conformance (each seat's own criteria,
reporting departures from THESIS.md, SPEC.md, ARCHITECTURE.md or CONVENTIONS.md) and consistency
(the pairs the skill assigns: THESIS↔SPEC to the prompt-engineer, SPEC↔ARCHITECTURE to the
architect, SPEC's README coverage to the tech-writer, ARCHITECTURE↔code and CONVENTIONS↔behavior to
the coder) — plus the test-suite audit seat chartered by the ROADMAP ticket. Wave 1 (the architect
pair, the coder pair, the audit) reported; wave 2 (the prompt-engineer pair, the tech-writer pair)
is out. When all nine report, the session synthesizes the findings into `ACTIVE_PLAN_REVIEW.md` —
one entry per defect, naming every seat that reported it, grouped by root cause — and this plan's
row lands in the commit that adds the review document.

Done-line: the nine seats' reports are in; `ACTIVE_PLAN_REVIEW.md` exists, is committed, and its
entries name their seats; `just dev-check-plan` passes.

### R2 — the review's plan is drafted

Intended lifetime: shipped. Rating: expert.

The session dispatches the architect to draft the burndown items from `ACTIVE_PLAN_REVIEW.md` —
one item per root-cause group, each with its own ID, status row, rating and one-commit close —
run one `devpro-prompt-engineer` usability review over the drafted items together, apply the
revision, and set each item's row by its state. The plan then holds for the user's discussion of
findings, remedies and the draft before any item is dispatched.

Done-line: the items are drafted, reviewed, revised and dispatched-visible in the status table;
the hold is reached and stated in the plan.
