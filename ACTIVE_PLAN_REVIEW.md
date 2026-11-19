# ACTIVE_PLAN_REVIEW — the reminder gate reads the plan alone

The post-plan review of commit `e660f90`. Four seats reviewed independently — `shell-dsl-coder`,
`typescript-coder`, `prompt-engineer`, `architect` — each given the project documents (no design
stands for this change), writing their own review to `.devpro-temp/review-gate-<seat>.md`. This
document is the session's synthesis: one ID per defect however many seats reported it, seats named.

Verified green before review: `just test` (876), `just lint`, `just check-links` (157/0 — the count
moves with the active plan's own links), `just check-deltas` (vacuous: the standing design carries
no delta sections).

## Findings

### G1 — two test docstrings misstate where the sentence lands
Seats: shell-dsl-coder (W), prompt-engineer (F1). `tests/test_guardrail.py:347-349` says the
sentence would land "in the context of every subagent a dispatch there starts"; delivery is to the
parent's next model request — the same wrong clause repeats at `:337-339`. Against the
hook-contract convention the burndown just landed. Fix: state the parent's next request, or end at
"the reminder's subject is the plan."

### G2 — the gate predicate is machine-held on claude and not on the entry
Seats: typescript-coder (W1), shell-dsl-coder (seen). The two resources' gates are the same
predicate, but only the sentence has a cross-resource test: delete `ACTIVE_PLAN.md` from
`planStanding`'s list and `just test devpro` stays green. Fix: one runner case over the decision
table (plan file, diced tree, design file, nothing) or a test holding the list to the script's
gate — the shape the sentence's parity test already uses.

### G3 — the design-only silence case pins the wrong depth
Seat: typescript-coder (W2). `test_a_design_at_the_project_root_injects_no_reminder` asserts
`synthetics == []`, which an always-off gate also satisfies. The differential — the same project
with `ACTIVE_PLAN.md` injected and with only the design not — is the pin that fails before the
change and passes after (demonstrated by hand). Fix: one test over one project holding both states;
the bare silence case stays as the boundary case.

### G4 — the version banner and the version constant disagree, and the deployed copies are stale
Seats: architect (W1, N1), prompt-engineer (F2). `AGENTS.md:3` claims devpro 0.17.6;
`devpro/__init__.py:51` reads 0.17.5; `dist/` stops at 0.17.5; no commit ever carried 0.17.6 — the
banner's version is filled from that constant, so an install ran mid-bump. The repo's deployed
copies (`.claude/…/state-table-reminder.sh`, `.opencode/plugins/devpro/index.ts`) still carry the
three-path gate; one `just install` converges them (the gitignored products, not source). Fix: the
owner's call — reinstall at 0.17.5 or land the 0.17.6 bump in a release commit; the install is
procedure, not commit content.

### G5 — text and rewrap sweep
Seats: shell-dsl-coder (2 Notes), typescript-coder (N1, N2), prompt-engineer (F4).
- The script header's gate sentence (lines 4-6) splits mid-clause; rewrap.
- `tests/test_guardrail.py` module docstring (:17-20) enumerates one silence case; there are two.
- `tests/test_opencode_entry.py:8-9` half-updated: :5-6 states the plan-only gate, the sentence
  about where the session opened is stale beside it.
- Four doc blocks left mid-phrase by the deletion — `guardrail-hook.md:22-24` worst ("at the
  project / root"); rewrap.
- The runner's stdin `project` shape (`opened` vs root) is declared and never varied; the
  below-root case lives only in the registration test.

### G6 — the opencode-entry leaf restates SPEC nearly verbatim
Seat: prompt-engineer (F3). `ARCHITECTURE/install/opencode-entry.md:6-9` repeats
`shipped-files.md:96-99` sentence-for-sentence; cite SPEC instead of restating it.

### G7 — the reminder comment's pointer names one hold where G2 lands two
Seat: typescript-coder (N3). `index.ts:99-101` says the sentence is held by
`tests/test_opencode_entry.py`; after G2's fix the comment names both holds. Rides G2.

## Carried, not this review's to fix
- SPEC states the opencode reminder only (no claude sentence) — the user's open call from the
  previous plan; unchanged by this work.
- Contract gaps for the definition/project owners: a shellcheck target beside `lint`; the
  one-text rule extended to a predicate two resources carry; the review-seat definition stating
  that the seat does not read the plan it reviews.

## Strengths to preserve
Both harnesses agree on the gate and each design-only root is asserted silent; the flipped tests
fail on the prior code (demonstrated by two seats); a doc-wide search found no statement still
claiming the design-half; no dead remainder in source.
