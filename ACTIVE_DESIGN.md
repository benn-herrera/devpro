# The burndown is a section with a drafting ticket

The plan's post-plan burndown becomes a `##` section holding one drafting ticket, and the review's
findings become individually-rowed item packages under it — so the board shows the burndown's real
dispatches, each with its own rating, instead of one opaque row. For whom: the operator reading the
board, the sessions running plans, and the process's tuning, which gains burndown items per plan as
recorded data.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [The post-plan packages rule](PROJECT_DOCS/SPEC/plan-status-form.md)

The section shape moves the burndown out of the status table: the review keeps its row, the
burndown becomes a section whose drafting ticket holds the row. The form's post-plan bullet states
the old shape and goes stale with the change.

**As it stands:**

```
- The post-plan review and the post-plan burndown are work packages, each with its own ID and row.
  The review's title opens with `Post-plan review` and the burndown's with `Post-plan burndown`; the
  rest of each title is free. A plan has a post-plan review row only with a post-plan burndown row,
  and a burndown row only with a review row.
```

**Becomes:**

```
- The post-plan review is a work package whose title opens with `Post-plan review`. The post-plan
  burndown is a `## Post-plan burndown` section holding its drafting ticket, a work package whose
  title opens with its ID and then `Post-plan burndown`; the rest of each title is free. A plan has
  a post-plan review row only with a post-plan burndown row, and a burndown row only with a review
  row.
```

### [The post-plan package kinds](PROJECT_DOCS/SPEC/dicing/checks.md)

The checker's kind definitions name a post-plan burndown package outright; under the section shape
the titled package is the drafting ticket the burndown section holds. The term
`post-plan burndown package` stays — the pairing rules and breach messages that use it keep reading
the ticket — and its definition gains what it now names.

**As it stands:**

```
- **post-plan review package**, **post-plan burndown package**: A title opens with
  `Post-plan review` (or `Post-plan burndown`) where it begins with those characters,
  case-sensitive, followed by the end of the title or a character that is not a letter or digit. A
  package whose title opens with `Post-plan review` is a **post-plan review package**; with
  `Post-plan burndown`, a **post-plan burndown package**.
```

**Becomes:**

```
- **post-plan review package**, **post-plan burndown package**: A title opens with
  `Post-plan review` (or `Post-plan burndown`) where it begins with those characters,
  case-sensitive, followed by the end of the title or a character that is not a letter or digit. A
  package whose title opens with `Post-plan review` is a **post-plan review package**; with
  `Post-plan burndown`, a package is the **post-plan burndown's drafting ticket**, the work package
  a plan's `## Post-plan burndown` section holds.
```

## Code delta

### [The development skill's burndown shape](devpro/definitions/skills/development.py)

The change replaces the *Plans* section's burndown sentence and the *Post-plan review* section's
burndown bullets with the section shape the landed plan's run proved, keeping the section's
placeholder and clause style. Three pairs, quoted from the source:

**As it stands:**

```
- The post-plan review and the post-plan burndown (*Post-plan review*) are packages, each with its
  own ID and row; the review's title opens with `Post-plan review`, the burndown's with
  `Post-plan burndown`.
```

**Becomes:**

```
- The post-plan review is a package whose title opens with `Post-plan review`; the post-plan
  burndown is a `## Post-plan burndown` section holding its drafting ticket, whose title opens with
  its ID and then `Post-plan burndown` (*Post-plan review*).
```

**As it stands:**

```
- Every plan holding a shipped package ends with two packages: the post-plan review, then the
  post-plan burndown. *Purpose:* review and its fixes are planned work, not a step dropped when the
  plan lands.
```

**Becomes:**

```
- Every plan holding a shipped package ends with the post-plan review package, then the burndown
  section and its drafting ticket. *Purpose:* review and its fixes are planned work, not a step
  dropped when the plan lands.
- The drafting ticket's work: draft the section's items from the {REVIEW_DOCUMENT_TERM} — one
  package per root-cause group, each with its own ID, status-table row, rating and one-commit close
  — run one `{clauses.ref(name="prompt-engineer")}` usability review over the drafted items
  together, apply the revision, and set each item's row by its state. Drafting the items edits the
  plan, so the session is the worker; the ticket's row still moves through the states.
  *Purpose:* the burndown's real dispatches are visible on the board, each with its own rating.
- The items move through the states individually, and the section dies when its last item lands.
  Where the review finds nothing needing a fix, the drafting ticket lands having drafted no items,
  and the plan ends — a normal landing. *Purpose:* the count of burndown items per plan is recorded
  data the process's tuning reads.
```

**As it stands:**

```
- Until the review lands, the burndown's section holds only: "Drafted from `ACTIVE_PLAN_REVIEW.md`
  once the post-plan review lands." Then you draft the burndown's work list from the
  {REVIEW_DOCUMENT_TERM}; it replaces that text where the section is, in the plan or in its leaf.
- The burndown gets `{clauses.ref(name="prompt-engineer")}` usability review, then your revision, before it is
  `dispatchable`. *Purpose:* the agents that execute from it can act on each item without inventing
  what it leaves open.
```

**Becomes:**

```
- Until the review lands, the drafting ticket's body holds only: "Drafted from
  `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands." The drafted items' text replaces that
  placeholder in the section, and the citation of the {REVIEW_DOCUMENT_TERM} moves to the section's
  opening.
```

The section's remaining bullets — the reviewers, the independent writes, the synthesis, the
{REVIEW_DOCUMENT_TERM}'s deletion at landing, the release's user-flow audit — stand unchanged. The
rendered skill text changes with the source. The guide's burndown account moves with it — the next
entry — and the two SPEC passages the shape leaves stale move with it too, under the SPEC delta
above. No checker changes: the checker already reads the section shape, as the landed plan's own
form — a `## Post-plan burndown` section with the drafting ticket B0 — passes `check-plan` today.

### [The guide's burndown account](devpro/definitions/skills/guide.py)

The guide tells a plan's human reader the plan ends in two more packages; under the section shape
it ends in the review package and the burndown section. Three pairs, quoted from the source:

**As it stands:**

```
  scope in files and its done-line: the runner targets whose passing run shows it done. A plan with
  shipped work ends in two more packages, *Post-plan review* and *Post-plan burndown*. A plan longer
```

**Becomes:**

```
  scope in files and its done-line: the runner targets whose passing run shows it done. A plan with
  shipped work ends in the *Post-plan review* package, then the `## Post-plan burndown` section
  holding its drafting ticket. A plan longer
```

**As it stands:**

```
- **The burndown:** the session drafts the fix list from `ACTIVE_PLAN_REVIEW.md` into the burndown
  package, has it reviewed, and runs it like any package. Every finding that cites a written rule is
```

**Becomes:**

```
- **The burndown:** a `## Post-plan burndown` section holding its drafting ticket; the session
  drafts the fix list from `ACTIVE_PLAN_REVIEW.md` into the section — one package per root-cause
  group, each with its own row and rating — has the items reviewed, and runs them like any package.
  Every finding that cites a written rule is
```

**As it stands:**

```
4. `ACTIVE_PLAN.md` appears: P1 applies the two entries, P2 writes the export and its tests, P3 the
   post-plan review, P4 the post-plan burndown, all shipped. "The plan is approved. Run it."
```

**Becomes:**

```
4. `ACTIVE_PLAN.md` appears: P1 applies the two entries, P2 writes the export and its tests, P3 the
   post-plan review, then the burndown section's drafting ticket drafting its item packages, all
   shipped. "The plan is approved. Run it."
```
