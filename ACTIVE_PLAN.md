# Active plan — the plan-state reminder's gate narrows to the plan

Going straight to the plan: a design-only root gives the reminder no subject, and the design-half
of the gate buys nothing across the design→plan handoff. The reminder's sentence is unchanged: with
the gate narrowed, its conditional ("Where the active plan carries a status table…") is always
satisfied where it fires.

Every package is **shipped**. One commit closes each package.

Out of scope: the harness-profiler work (its draft and its ROADMAP ticket), the reminder sentence's
wording, the diced-design-tree question (dissolved — the gate no longer reads design files at all).

Sequencing: P1 first; P2 after P1; P3 after P2.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | landed | mechanical | the gate reads the plan alone, in both resources, their tests, and the three contract statements |
| P2 | landed | expert | Post-plan review |
| P3 | landed | expert | Post-plan burndown |

## P1 — The gate reads the plan alone

Scope: two resources, their tests, three contract statements. The gate opens on `ACTIVE_PLAN.md` —
file or, where the plan was diced, the `ACTIVE_PLAN/` tree — and on nothing else.

- `devpro/harnesses/resources/claude/hooks/state-table-reminder.sh`, the gate line (verified this
  session): `if [[ ! -f "${root}/ACTIVE_PLAN.md" && ! -f "${root}/ACTIVE_DESIGN.md" && ! -d "${root}/ACTIVE_PLAN" ]]; then`
  → `if [[ ! -f "${root}/ACTIVE_PLAN.md" && ! -d "${root}/ACTIVE_PLAN" ]]; then`. The header's gate
  sentence (lines 4-6, "a project holding `ACTIVE_PLAN.md`, `ACTIVE_DESIGN.md` or the diced
  `ACTIVE_PLAN/` tree") drops the design file, and the sentence comment at lines 50-52 ("it is true
  where only a design stands…") carries the same retired design-only rationale and drops it.
- `devpro/harnesses/resources/opencode/index.ts:96` (verified this session):
  `return ["ACTIVE_PLAN.md", "ACTIVE_DESIGN.md", "ACTIVE_PLAN"].some((name) => existsSync(join(root, name)))`
  → `["ACTIVE_PLAN.md", "ACTIVE_PLAN"]`. The comment above `planStanding` (:93-94, "a plan or a
  design") and the reminder constant's comment (:100-102, whose design-only rationale the narrowing
  retires) state the plan-only fact.
- Tests pinning the changed behavior — each updated case fails on the current code, where a
  design-only root still nudges (the defect the updates close):
  - `tests/test_guardrail.py:306-312`, `test_the_reminder_speaks_where_a_plan_a_design_or_the_diced_tree_stands_at_the_project_root`:
    the parametrization drops `ACTIVE_DESIGN.md` from the gate cases and the name/docstring state
    the plan-only fact, as does the section comment above the test (`:302-303`, "reading a plan, a
    design or the diced plan tree"); the design-only silence case lands beside the existing silence
    test, `test_the_reminder_is_silent_where_the_project_holds_no_gate_path` (`:336`).
  - `tests/test_opencode_entry.py:198-202`, `test_a_design_or_the_diced_plan_at_the_project_root_opens_the_gate`:
    the `ACTIVE_DESIGN.md` case flips to no-injection (name and docstring with it); the
    `ACTIVE_PLAN` case stays a gate case; the design-only case's assertion becomes
    `out["synthetics"] == []`, beside the gate case. The module docstring (`:5-6`) states "a plan
    file, a design file or the diced tree" and goes false.
- Three contract statements — no design stands for this change, so no design delta's `becomes`
  block pins them (`just check-deltas` is vacuous while the active design carries no delta
  sections); keep each edited paragraph's wrapping and rewrap only the lines the dropped words
  shorten:
  - `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:97-99`: "gated by `ACTIVE_PLAN.md` or
    `ACTIVE_DESIGN.md` — file or, where the plan was diced…" drops "or `ACTIVE_DESIGN.md`".
  - `PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md:22-27`: the passage beginning "which reads
    `ACTIVE_PLAN.md` or `ACTIVE_DESIGN.md` — file or…" drops "or `ACTIVE_DESIGN.md`".
  - `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md:6-9`: the passage beginning "gated by
    `ACTIVE_PLAN.md` or `ACTIVE_DESIGN.md` — file or…" drops "or `ACTIVE_DESIGN.md`".

Done-line: `just test devpro`, then `just check-links`. One commit.

## P2 — Post-plan review

The reviewers are the agent for each domain the plan changed substantively; each gets the project
documents (there is no design for this change) and reviews the changes and their tests:

- `shell-dsl-coder` — the reminder script's gate and its tests;
- `typescript-coder` — `planStanding`, the runner and `tests/test_opencode_entry.py`;
- `prompt-engineer` — the three contract statements;
- `architect` — the statements' claims about the code, and whether any document still claims the
  design opens the gate.

No python-coder seat: no Python source changes; the test flips ride the two code seats. The session
synthesizes the reviews into `ACTIVE_PLAN_REVIEW.md`, never diced.

Done-line: `just check-links`. One commit carries the review document, and its row lands with it.

## P3 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md`. One commit closes the package; the items cite their review
IDs. G4 (the version banner against the version constant, and the stale deployed copies) is the
owner's call, raised at the landing — not this package's work.

1. **The gate's parity and differential pins** (G2, G3, G7, G8): a runner case holds the entry's gate
   decision table — plan file, diced tree, design file, nothing — against the recorded injections
   (`devpro/harnesses/resources/opencode/index.ts:96`); the table's design row and the plan rows are
   one test's cases, and the design row's assertion is the differential — one project in two states:
   with `ACTIVE_PLAN.md` (injected), with the design file alone (silent) — the entry's design case
   is `tests/test_opencode_entry.py:222-240` and its boundary sibling `:170-195`, the defect being
   that an always-off gate passes today's pin; `planStanding` checks the kind the gate names — a
   file for the `.md` names — the defect being that a directory named `ACTIVE_PLAN.md/` opens
   opencode's gate and not claude's; `index.ts`'s reminder comment (:99-101) states what holds the
   sentence and the gate. G2's original defect claim (the suite stays green under the list's
   deletion) is disputed by the review's second reading — the mutation run at acceptance settles
   it: red, the pin holds; green, the table stays as consolidation and the comment states what
   holds the gate.
2. **The docstring and rewrap sweep** (G1, G5), item 3 first for the leaf it rewrites:
   `tests/test_guardrail.py:347-349` and `:337-339`
   state the parent's delivery; the module docstring (:17-20) names both silence cases;
   `tests/test_opencode_entry.py` line 8's silence list gains "a project holding only a design" and
   the stale sentence about where the session opened goes; the script header's gate sentence
   (:4-6) rewraps whole; the three doc leaves the deletion left mid-phrase rewrap
   paragraph-wide — `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:97-99`,
   `PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md:22-24`,
   `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md:8-9`, the blocks item 3 leaves; the
   runner's stdin deliberately carries the opened directory beside the project root — the tests pin
   that the entry reads only the project root — and its declaration states that fact.
3. **The leaf cites its source** (G6): `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md:6-9`
   keeps one clause of the gate statement — gated by the active plan (`ACTIVE_PLAN.md` or the diced
   `ACTIVE_PLAN/` tree; SPEC, Shipped files) — and cites
   `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:95-99` for the rest, instead of restating
   it sentence-for-sentence.
4. **The one-text rule reaches predicates** (the review's second contract gap): a clause in
   `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-sentence-two-resources-carry-is-one-text.md`
   — a predicate two resources carry is one text, held by the gate test item 1 lands, as the
   sentence is by its parity test.

Deferred to the owner's direction, recorded here: a shellcheck target beside `lint` (the host has
no shellcheck binary — a target that cannot pass locally is a ROADMAP question, not a burndown
item); a review-seat definition line stating the seat does not read the plan it reviews.

Done-line: `just test devpro`, then `just check-links`. One commit; the commit that lands the plan
follows it, deleting `ACTIVE_PLAN.md` and the review document.

Done-line: the checkpoint gate, then `just check-links`. One commit; the commit that lands the plan
follows it, deleting `ACTIVE_PLAN.md` and the review document.
