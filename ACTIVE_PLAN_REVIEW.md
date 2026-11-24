# Post-plan review — the burndown is a section with a drafting ticket

Seats: `devpro-prompt-engineer` (primary — the change is model-facing text), `devpro-architect`,
`devpro-python-coder`; each reviewed independently from the documents and the design, not the plan.
The session synthesized this document. Range reviewed: `287175b..90cd6cc` (P1 `67c13e3`, P2
`90cd6cc`).

## Findings

- **R1** (coder, critical; architect, warning ×2; PE): The shape's identity rules and the checker's
  title-pairing disagree in three places. (a) `checks.md:105-110`'s amended Terms no longer define
  `post-plan burndown package` — the term its own messages emit at `:74, :124, :162-163`
  (`plancheck.py:40-41`); the pairing (`planform.py:378-403`) classifies by title alone, so the
  Terms must stay title-only and the definition must keep the term, naming the drafting ticket as
  what it now covers. (b) `planform.py:393-397`'s unpaired-breach message advises
  `## <ID> Post-plan burndown`, which under the shape is the section, not the ticket — the message
  steers to the old shape. (c) The rule text requires the literal `## Post-plan burndown` section
  heading *and* a ticket title opening with ID + `Post-plan burndown`; a ticket titled bare `B0`
  breaches pairing (`_title`, `planform.py:367-375`) — the probe that shows it is in the coder
  seat's evidence. The plan carrying the change complies; nothing warns its reader off the bare
  title.
- **R2** (PE): `development.py:480-485` — *Periodic review* still teaches the old model ("its
  post-plan burndown … groups the findings by root cause, not one item per finding") directly under
  the section redefining the burndown. A model following it writes the opaque row this change
  removes. Fix: "The burndown section's items cite that ID and group the findings by root cause,
  several findings to one item."
- **R3** (PE + architect): The new bullets give items content but no identity — nowhere says an
  item *is* a work package; "the section dies when its last item lands" names no act; the
  placeholder-citation move has no stated referent; and `development.py:427-430`'s "the drafted
  items' text replaces that placeholder" carries the old in-place mechanism the shape replaces.
- **R4** (PE + architect): `guide.py`'s walkthrough — "has the items reviewed" names no reviewer
  and no revision (the skill states the PE review; the guide should align with its own "reviewed
  for usability and revised"); steps 4 and 6 keep old behavior (step 4's items don't exist at plan
  appearance; step 6's "P4 fixes its findings" — the ticket drafts, the items fix).
- **R5** (coder): The pairs' added lines run 92–99 columns against files wrapped ≤ 90 — re-wrap to
  each source file's width (whitespace-squash matching keeps the pairs landed); visible orphan at
  `guide.py:382-383`.
- **R6** (coder, note): P2's commit message cited the checkpoint gate as evidence for a plan-form
  change — the delta check reads source text only, so the gate cannot catch plan-form drift. The
  seat's `check-plan` probe over the carrying plan is the instrument; recorded here as the lesson
  R1's fix should cite.
- **R7** (PE, one line): `ROADMAP.md`'s burndown-shape Maintenance ticket is accomplished by this
  plan and leaves the roadmap at landing.

## Contract gaps

- **G1** (coder): CONVENTIONS — a design pair's text is re-wrapped to the source file's width when
  applied; whitespace-squash matching makes this safe, and un-wrapped lines are the defect R5 shows.
- **G2** (coder): CONVENTIONS — the brace rule (a literal brace in a definition body is doubled) is
  unstated anywhere a definition-module editor would look.
- **G3** (coder): a plan that changes plan-form rules runs a `check-plan` probe over a plan carrying
  the change — the probe that would have caught R1's breach scenario before landing.
- **G4** (session): the shared-index hazard the run hit — concurrent dispatches staging into one
  git index swept a rename into another package's commit; a practice line (stage and commit only
  your own paths, `git commit -- <paths>`) belongs with G1-G3's pass or the next CONVENTIONS touch.

## Dispositions

No owner decision blocks the burndown: R1's fix direction is stated by the seats' convergence (keep
the term, title-only Terms, align the messages, warn off the bare title) and the checker-code slice
is small and enumerated. The accomplished ROADMAP ticket (R7) leaves at landing.
