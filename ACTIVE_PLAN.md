# Plan: land the process-consistency design in the generator source and the repo's own files

Design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — 19 entries under `## ARCHITECTURE delta` and
`## Code delta`; this plan implements each entry exactly as accepted, applying the ARCHITECTURE
delta's pair to its target verbatim; every entry is claimed by exactly one package below.

Each package states its lifetime below, and packages sharing a file run serially in the shared
tree, in the order the serial sentences after the status table state. Each package's
`just test-changed` is a delta run: it reads the uncommitted tree against the last commit, so a
package's run covers only its own changes; cumulative coverage is the checkpoint gate's job
(`just test`, `just lint`, `just sweep-python`). This plan is not a release's hardening plan and
names no release: the version bump is an ordinary commit under the version leaf
(CONVENTIONS, [Version has one home](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/version-has-one-home.md)),
`just tag` is not part of this plan, and the README hand-edit that leaf's step names is gone with
the tag itself — P13 landed it, the owner's later ruling (MB6c) removes it, B13 executes the
removal.
The untracked `SUGGESTED_MECHANICAL_FIXES.md` is the transient review the design captured and
cites nowhere: no package commits it.

**The version bump is already done.** `devpro/__init__.py` carries `__version__ = "0.18.1"`
(uncommitted; `git diff devpro/__init__.py` shows the change from `"0.18.0"`). The plan carries it
in P1, the first package that changes block content, as a named edit in P1's scope and commit.

**The one choice this plan puts to the user at approval** is P13's side of the README pipx-tag
discrepancy; the plan's recommended reading is stated there. Superseded: the owner's later
ruling (MB6c) removes the hand-kept tag outright — B13 executes the removal and supersedes
B1's guard direction.

## Status

| Package | State | Rating | Design entries |
| --- | --- | --- | --- |
| P1 | landed: c4f2d78 | mechanical | MB9 |
| P2 | landed: 52609761 | mechanical | MB13 |
| P3 | landed: 171b3a99 | mechanical | MB8, MB11 |
| P4 | landed: 848c35cf | mechanical | MB10 |
| P5 | landed: 2b19ce55 | mechanical | MB6 |
| P6 | landed: 995dc0a4 (gate batched with P6–P10) | mechanical | MB5 |
| P7 | landed: 65b406bc (gate batched with P6–P10) | mechanical | MB2, MB3 |
| P8 | landed: cb8972da (gate batched with P6–P10; the silent dispatch's work verified against the design's texts, render probe run by the session: `asks the session itself` × 3) | mechanical | MB15, MB17 |
| P9 | landed: 0569acbc (gate batched with P6–P10) | mechanical | MB4, MB1b |
| P10 | landed: 3cf25488 (gate batched with P6–P10) | mechanical | MB1a, MB7, MB14, MB16 |
| P11 | landed: f959aa54 | mechanical | MB12 |
| P12 | landed: 113b813f | mechanical | ARCH delta |
| P13 | landed: dbc05b64 — superseded by MB6c/B13: the tag it landed is removed | mechanical | the pipx decision |
| P14 | landed: 934eff29 (ACTIVE_PLAN_REVIEW.md, 24 findings) | expert | — |
| P15 | landed: 4cba2de2 (11 items drafted B1–B11, all rows drafted) | expert | — |
| B1 | landed: 8a8e8524 — superseded in part by MB6c/B13: the owner's ruling removes the hand-kept README tag the guard polices; R2's brew/no-tag statement persists in B13's rewrite | mechanical | R1, R2 |
| B2 | landed: 2210ac49 (the flag ticket under Maintenance — superseded by B12's removal, which removes it). Incident on the record: the dispatch used git stash/pop mid-task — a forbidden working-tree command — verified no data lost, corrected course; accepted with the violation named here | mechanical | R3 (flag; superseded by the owner's removal decision) |
| B3 | landed: 8ceceb77 (two invariant facts pinned — no precedence pin, per the corrected scope; B12's "drop the pin" edit will find none and no-op) | mechanical | R4; R5 closed by measurement |
| B4 | landed: 69bc4c9d (R6, R18, R23 closed; one fact for the record: the guide's term renders in `references/using.md`, not `SKILL.md` — the item's done-line grep named the wrong file, the report measured the right one) | mechanical | R6, R18, R23 |
| B5 | landed: e84e3f49 (three seat-word sites + the trigger gloss's deciding half; R7 retained for the owner; one premise note for the record — the item called two sites "byte-identical", they differ in "a plan"/"the items", the seat word applied identically and the difference left standing) | mechanical | R8, R10; R7 flagged for the owner |
| B6 | landed: 2bc7e633 (the design's MB16 "becomes" text superseded by this item's mechanical form — recorded here; the design leaves at the plan's landing) | mechanical | R9 |
| B7 | dispatchable (dissolves at B12's landing — B12's scope deletes the governance paragraph outright, the paragraph B7 was to move; R11 closes by removal, no own dispatch or commit) | mechanical | R11 |
| B8 | landed: 22cfc235 (all three fixes verbatim where drafted; conftest tuple + B3's carrier set updated in-commit; its lint citation quoted the shell/docs legs — the batched tail gate runs lint whole) | mechanical | R12, R13, R14 |
| B9 | dispatchable (fires after B12 on clauses.py) | mechanical | R15, R16, R17, R24 |
| B10 | landed: a9c52eb3 (pure deletion, verified no pins; the render-surface half of its done-line went red on B12's in-flight clauses.py state — not B10's scope — and the batched tail gate re-runs it whole after B12 lands) | mechanical | R19 |
| B11 | dispatchable (fires after B9 on clauses.py) | mechanical | R20, R21, R22 |
| B13 | landed: f8aad90a (one judgment on the record: SPEC's count moved two → three install sources — the rewrite would have self-contradicted; the release-tag URL stays a source without the `@v<version>` spelling, per MB6c) | mechanical | MB6c — supersedes B1's direction |
| B12 | in progress: dispatch ses_ddef66388ffeW5WVeZ4bTqnIGd — the owner's removal decision, corrected mid-run; the span is deleted outright, not reworded | mechanical | R3, W7, W8 — resolved by removal |

Serial order per shared file, nothing concurrent across these runs:
`devpro/definitions/skills/development.py`: P5 → P6 → P7 → P8 → P9. `guide.py`: P6 → P7 → P8.
`clauses.py`: P1 → P2 → P5 → P6. `security_reviewer.py` and `architect.py`: P2 → P4.
`harness_agents_file.py`: P5 → P10.

### P1 Carry the version bump; parameterize the evidence clause's venv sentence

Lifetime: shipped — the rendered definitions reach users.

Scope: `devpro/clauses.py` (`verification_evidence`, new constant `VENV_PROBE_RULE`),
`devpro/definitions/agents/python_coder.py`, `devpro/definitions/agents/ml_engineer.py`; plus the
version bump as an enumerated edit — `devpro/__init__.py`'s `__version__ = "0.18.1"`, already in
the working tree and verified uncommitted — is committed with this package's changes, in this
package's one commit.

Entry: [MB9](ACTIVE_DESIGN.md#structural-rules--mb9-the-venv-probe-sentence-reaches-only-the-python-probing-seats)
— it quotes the venv sentence byte for byte and states the constant, the third keyword-only
parameter `probe_rule` (default empty, composed onto the paragraph's end), and the two call sites
that pass `probe_rule=clauses.VENV_PROBE_RULE`. The other call sites stand unchanged; the
architect's call at `devpro/definitions/agents/architect.py:34–37` keeps its two custom arguments
and loses the sentence with no edit.

Reference search (signature change) — `git grep -l verification_evidence -- devpro tests` prints:

```
devpro/clauses.py
devpro/definitions/agents/android_app_expert.py
devpro/definitions/agents/architect.py
devpro/definitions/agents/c_coder.py
devpro/definitions/agents/cpp_coder.py
devpro/definitions/agents/generalist_coder.py
devpro/definitions/agents/go_coder.py
devpro/definitions/agents/ios_app_expert.py
devpro/definitions/agents/linux_app_expert.py
devpro/definitions/agents/linux_kernel_driver_expert.py
devpro/definitions/agents/lua_coder.py
devpro/definitions/agents/macos_app_expert.py
devpro/definitions/agents/ml_engineer.py
devpro/definitions/agents/python_coder.py
devpro/definitions/agents/rust_coder.py
devpro/definitions/agents/shell_dsl_coder.py
devpro/definitions/agents/typescript_coder.py
devpro/definitions/agents/web_app_expert.py
devpro/definitions/agents/windows_app_expert.py
tests/test_clause_groups.py
```

Only python-coder and ml-engineer gain an argument; `tests/test_clause_groups.py:54,115` name
`verification_evidence` as a plain entry — the name stands, so the tables stand.

Tests and fixtures pinning the changed behavior: `tests/render/test_prose.py:104` (a paragraph two
outputs carry has one source) and `tests/render/conftest.py:601` (the sentinel sweep, which reads
`VALUE_CONSTANTS`).

Done-line: `just test-changed`; `just lint` — the check that catches an unindented pasted
constant, the form this plan uses wherever a package pastes the design's constants; then the
render probe — `just render latest`, then `grep -rln "python -c"
rendered/latest/devpro/skills/devpro/agents/` reports exactly `python-coder.md` and
`ml-engineer.md`, and `grep -c "the file and line you read"
rendered/latest/devpro/skills/devpro/agents/architect.md` reports `1` (the custom evidence forms
survive, the venv sentence gone); then `git show --stat HEAD` names `devpro/__init__.py` — the
bump is in the commit.

### P2 One severity ladder across the reviewer seats

Lifetime: shipped.

Scope: `devpro/clauses.py` (`REVIEW_SEVERITY`), `devpro/definitions/agents/tech_writer.py`,
`devpro/definitions/agents/security_reviewer.py`, `devpro/definitions/agents/architect.py`.

Entry: [MB13](ACTIVE_DESIGN.md#rendering--mb13-one-severity-ladder-across-the-reviewer-seats) —
it gives the reworked constant (tie-break included) and the exact replacement bodies for the two
calibration sections (headings kept) and the architect's Review Process item 2.

Reference search — `git grep -l REVIEW_SEVERITY -- devpro tests` prints:

```
devpro/clauses.py
devpro/definitions/agents/shell_dsl_coder.py
```

shell-dsl-coder is the one direct carrier and gains the tie-break with no edit of its own; the
sixteen remaining carriers reach it through `WHEN_REVIEWING_SECTION` in the stacks.

Attestation this package runs and quotes, that the headings the "per the calibration above"
references point at stand — `grep -n "Severity Calibration"
devpro/definitions/agents/architect.py devpro/definitions/agents/tech_writer.py
devpro/definitions/agents/security_reviewer.py` prints:

```
devpro/definitions/agents/tech_writer.py:168:### Severity Calibration
devpro/definitions/agents/security_reviewer.py:99:## Severity Calibration
```

`architect.py` has no hit: its severity is the Review Process item, which needs no heading.

Tests and fixtures pinning the changed behavior: `tests/test_clause_groups.py` (the
`WHEN_REVIEWING_SECTION` plain entries) and `tests/render/test_prose.py:104`.

Done-line: `just test-changed`; `just lint`; then `just render latest`, then
`grep -rn "prefer Critical" rendered/latest/devpro/skills/devpro/agents/tech-writer.md
rendered/latest/devpro/skills/devpro/agents/security-reviewer.md` reports nothing, and
`grep -c "Severity by when the cost lands" rendered/latest/devpro/skills/devpro/agents/tech-writer.md
rendered/latest/devpro/skills/devpro/agents/security-reviewer.md` reports `1` for each.

### P3 Two agent definitions' stale text corrected

Lifetime: shipped.

Scope: `devpro/definitions/agents/prompt_engineer.py` (the description at lines 13–19, the Scope
line at line 38), `devpro/definitions/agents/generalist_coder.py` (the "Understand the task" bullet
at lines 28–30). Two entries, two files, one commit — both are standalone text corrections to one
definition each.

Entries: [MB8](ACTIVE_DESIGN.md#subsystem-map-seats--mb8-the-prompt-engineer-claims-no-plan-or-design-note-authorship)
and [MB11](ACTIVE_DESIGN.md#subsystem-map-seats--mb11-the-stale-clarifying-question-clause-is-gone)
— they give both replacement texts.

Reference searches — `git grep -n "yours to write" -- devpro` prints only
`devpro/definitions/agents/prompt_engineer.py:38`, and `git grep -n "one clarifying question" --
devpro` prints only `devpro/definitions/agents/generalist_coder.py:28`.

Done-line: `just test-changed`; then `just render latest`, then
`grep -rn "yours to write" rendered/latest/devpro/skills/devpro/agents/prompt-engineer.md` reports
nothing, and `grep -rn "one clarifying question"
rendered/latest/devpro/skills/devpro/agents/generalist-coder.md` reports nothing.

### P4 Retire the security-findings pipeline

Lifetime: shipped.

Scope: `devpro/definitions/agents/security_reviewer.py`,
`devpro/definitions/agents/architect.py`.

Entry: [MB10](ACTIVE_DESIGN.md#subsystem-map-seats--mb10-the-security-findings-pipeline-is-retired)
— it enumerates every site: the reviewer's opening reword and the "## Invocation Context" removal;
the architect's description, artifacts list, the corrected Pre-output lead sentence, the removed
synthesis paragraph, the removed Security-dimension skip condition, and the "## Integrating
Security Findings" section removed whole.

Tests and fixtures pinning the changed behavior: `tests/render/test_prose.py` (the render checks —
one source, no span twice); no test names the removed section or the handoff.

Done-line: `just test-changed`; then `just render latest`, then
`grep -rn "burn-down" rendered/latest/devpro/skills/devpro/agents/architect.md
rendered/latest/devpro/skills/devpro/agents/security-reviewer.md` reports nothing.

### P5 One precedence span, carried by every seat

Lifetime: shipped.

Scope: `devpro/clauses.py` (rename and rework to `PROJECT_PRECEDENCE`, the two stacks, the
comments naming the old constant), `devpro/definitions/skills/development.py` (the opening
sentence), `devpro/definitions/harness_agents_file.py` (the CONVENTIONS.md word), and the twelve
definitions the entry names — `architect.py`, `security_reviewer.py`, `tech_writer.py`,
`prompt_engineer.py`, `ml_engineer.py`, `applied_mathematician.py`, `biz_dev_strategist.py`,
`economic_historian.py`, `literature_scout.py`, `marketing_comms_expert.py`,
`prose_architect.py`, `theoretical_economist.py` — seven of them gaining the `clauses` import,
plus `python_coder.py`'s and `shell_dsl_coder.py`'s inline continuations.

Entry: [MB6](ACTIVE_DESIGN.md#rendering--mb6-one-precedence-span-carried-by-every-seat) — it
gives the span's text verbatim, the placement rule, the seven-import list, both continuation
settlements, the block word, and the reason the block carries no copy of the span.

Reference search (renamed constant) — `git grep -l PROJECT_CONVENTIONS_OUTRANK -- devpro tests`
prints only `devpro/clauses.py` (its definition, the two stacks, and the comments) — no definition
or test names it, so the rename touches no table.

Tests and fixtures pinning the changed behavior: `tests/test_clause_groups.py` (member lists and
plain entries — the span is reached only inside the stacks, so no plain-entry row changes),
`tests/render/test_prose.py:104` (one source) and `:143` (no prompt delivers a span twice).

Done-line: `just test-changed`; `just lint`; then the twelve-render probe — `just render latest`,
then `grep -c "The project's own documents modify the process"
rendered/latest/devpro/skills/devpro/agents/*.md` reports exactly `1` for every agent file (the
twelve placements the entry names among them), and `grep -rln "The project's own documents modify
the process" rendered/latest/devpro/AGENTS.md rendered/latest/devpro/skills/devpro/skills/`
reports only the development skill's `SKILL.md` — the block carries no copy.

### P6 A bindable concurrency cap governs fan-out

Lifetime: shipped.

Scope: `devpro/clauses.py` (`CONCURRENT_DISPATCHES_DEFAULT` joining `VALUE_CONSTANTS`),
`devpro/definitions/skills/development.py` (`CONCURRENT_DISPATCHES_TERM`, the bindable-terms
table row, the Dispatch bullet), `devpro/definitions/skills/guide.py` (the go bullet).

Entry: [MB5](ACTIVE_DESIGN.md#subsystem-map-development-skill--mb5-a-bindable-concurrency-cap-governs-fan-out)
— it gives the constant, the table row, the replacement bullet, and the guide's replacement.

Reference search — `CONCURRENT_DISPATCHES` has no references today (new names); the tuple it
joins — `git grep -l VALUE_CONSTANTS -- devpro tests` prints:

```
devpro/clauses.py
tests/render/conftest.py
```

Tests and fixtures pinning the changed behavior: `tests/render/conftest.py:601` (the sentinel
sweep, which reads `VALUE_CONSTANTS`) and the term-value test that reads `development.py` for a
term's value written literally — the table row interpolates `{CONCURRENT_DISPATCHES_TERM}`.

Done-line: the render probe — `just render latest`, then
`grep -rn "most capable model" rendered/latest/devpro/` reports nothing, and
`grep -c "concurrent dispatches" rendered/latest/devpro/skills/devpro/skills/development/SKILL.md`
reports at least `2` (the table row and the Dispatch bullet). The `just test-changed` and
`just lint` of P6–P10 run once as the batch gate, at the last of the group's landings, over the
checkpoint base (`just test-changed 1af120a8`): the user directs batching text-change tickets'
testing — one gate run for the group, and a failure's forensics read five small diffs.

### P7 The periodic review's trigger is one condition, its count target named without a runner

Lifetime: shipped.

Scope: `devpro/definitions/skills/development.py` (Periodic review section, first and second
bullets), `devpro/definitions/skills/guide.py` (the Due bullet and the bullet after it).

Entries: [MB2](ACTIVE_DESIGN.md#subsystem-map-development-skill--mb2-the-periodic-reviews-trigger-is-one-condition)
and [MB3](ACTIVE_DESIGN.md#subsystem-map-development-skill--mb3-the-count-target-is-named-without-naming-a-runner)
— they give the replacement bullets, the guide's Due and holds-up replacements, and the
`plan-count` rewording ("the `plan-count` runner target prints").

Reference search — `git grep -n "just plan-count" -- devpro` prints only:

```
devpro/definitions/skills/development.py:481:- The {PERIODIC_REVIEW_INTERVAL_TERM}'s count is what the runner target `just plan-count` prints:
```

Done-line: the render probe — `just render latest`, then
`grep -rn "just plan-count" rendered/latest/devpro/` reports nothing. The `just test-changed`
and `just lint` of P6–P10 run once as the batch gate, at the last of the group's landings, over
the checkpoint base (`just test-changed 1af120a8`): the user directs batching text-change
tickets' testing — one gate run for the group, and a failure's forensics read five small diffs.

### P8 The architect drafts the burndown items; the session drafts only on the user's ask

Lifetime: shipped.

Scope: `devpro/definitions/skills/development.py` (the Post-plan review drafting bullet, the
Plans first-draft bullet, the Periodic review drafting sentence),
`devpro/definitions/skills/guide.py` (the burndown bullet).

Entries: [MB15](ACTIVE_DESIGN.md#subsystem-map-development-skill--mb15-the-architect-drafts-the-post-plan-burndown-items)
and [MB17](ACTIVE_DESIGN.md#subsystem-map-development-skill--mb17-the-session-drafts-only-on-the-users-ask)
— they give all three replacement texts, the guide's replacement, and the statement that the
"so the session is the worker" sentence is removed with the whole-bullet rewrite.

Done-line: the render probe — `just render latest`, then
`grep -c "asks the session itself" rendered/latest/devpro/skills/devpro/skills/development/SKILL.md`
reports `3` — the three drafting rules' boundary sentence, stated in the same terms. The
`just test-changed` and `just lint` of P6–P10 run once as the batch gate, at the last of the
group's landings, over the checkpoint base (`just test-changed 1af120a8`): the user directs
batching text-change tickets' testing — one gate run for the group, and a failure's forensics
read five small diffs.

### P9 The skill cites no source path; unstaging names its index-only commands

Lifetime: shipped.

Scope: `devpro/definitions/skills/development.py` (the Dispatchability test-precondition bullet,
the Dispatch shared-tree bullet).

Entries: [MB4](ACTIVE_DESIGN.md#subsystem-map-development-skill--mb4-rendered-process-text-cites-no-devpro-source-path)
and [MB1b](ACTIVE_DESIGN.md#subsystem-map-development-skill--mb1b-the-unstaging-the-skill-requires-names-its-index-only-commands)
— the parenthetical citation is dropped from the first, and the second's middle sentence names
`git restore --staged <path>`.

Reference search — `git grep -n "devpro/clauses" -- devpro/definitions` prints only:

```
devpro/definitions/skills/development.py:312:  (`clauses.TEST_PRECONDITION` in `devpro/clauses.py`), which the coder and platform-expert
```

Done-line: the render probe — `just render latest`, then
`grep -rn "devpro/clauses" rendered/latest/devpro/` reports nothing. The `just test-changed`
and `just lint` of P6–P10 run once as the batch gate, at the last of the group's landings, over
the checkpoint base (`just test-changed 1af120a8`): the user directs batching text-change
tickets' testing — one gate run for the group, and a failure's forensics read five small diffs.

### P10 The agents-file block's rules: unstaging, escapes, boundaries, aliases

Lifetime: shipped.

Scope: `devpro/definitions/harness_agents_file.py` — the Shared working tree bullet (lines
59–63), the U+2028 bullet (133–134), the alias bullet (135–138), the stale-plan bullet (158–161);
current text as the entries state it.

Entries: [MB1a](ACTIVE_DESIGN.md#agents-file--mb1a-the-git-ban-allows-index-only-unstaging),
[MB7](ACTIVE_DESIGN.md#agents-file--mb7-the-u2028-escape-bullet-is-removed),
[MB14](ACTIVE_DESIGN.md#agents-file--mb14-the-stale-plan-revision-gets-its-boundary),
[MB16](ACTIVE_DESIGN.md#agents-file--mb16-the-command-alias-rule-states-the-principle).

Done-line: the render probe — `just render latest`, then
`grep -n "U+2028" rendered/latest/devpro/AGENTS.md` reports nothing, and
`grep -c "touches the index only" rendered/latest/devpro/AGENTS.md` reports `1`. P10's landing
runs the batch gate when it is the last of P6–P10's landings: `just test-changed 1af120a8`;
`just lint` — one gate run for the group's five commits; the user directs batching text-change
tickets' testing.

### P11 The repository's own AGENTS.md tail states the Must-see rule's coverage

Lifetime: shipped — the tail is hand-maintained, outside the rendered block.

Scope: `AGENTS.md` at the repository root, lines 183–187 (the Must-see section between the block's
closing marker and "## Contents lists"); the first bullet replaced by the two the entry gives.

Entry: [MB12](ACTIVE_DESIGN.md#agents-file--mb12-the-must-see-rule-in-the-repositorys-own-agentsmd-states-its-coverage).

Done-line: `just test-changed` and `just check-links` — a top-level `*.md` change maps to the
docs surface (`justfile:329`'s `*.md docs` row).

### P12 Apply the ARCHITECTURE delta to the Subsystem Map leaf

Lifetime: persistent — the project documents, tracked and reaching no user.

Scope: `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md`, the three pairs of the delta entry — the
`profiler`, `guide` and `development` skill modules' paths gaining their `skills/` segment. The
platform's docs surface selects the changed leaf (`justfile:329`'s `*.md docs` row).

Entry: [ARCH delta](ACTIVE_DESIGN.md#subsystem-map) — applied verbatim; the pipx discrepancy note
in that entry is this plan's P13, not this package's.

Done-line: `just dev-check-design-deltas-applied` (every pair landed); then `just test-changed`
(docs surface) and `just check-links`.

### P13 Settle the README pipx-tag discrepancy

Lifetime: shipped — README reaches users.

Scope: `README.md` line 61 (`pipx install "git+https://github.com/benn-herrera/devpro"` — no tag)
and, only on the alternative side, `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/version-has-one-home.md`.
This package owns the whole edit on whichever side the user picks; it references no other
package's outcome.

The decision the design leaves to this plan, put to the user at approval — a file-level choice:

- **Recommended: `README.md` only; the leaf stands.** README's pipx install line gains the
  hand-kept tag: `pipx install "git+https://github.com/benn-herrera/devpro@v0.18.1"` — the tag
  spelling `devpro/__init__.py`'s `__version__` (0.18.1) names. The leaf's statement that makes
  this a standing step, quoted: "A fourth carrier is hand-kept, not filled: `README.md`'s pipx
  tag, `@v<version>`; its step is the hand edit beside the `__version__` bump, before `just tag`
  cuts the release tag." — the recommended side is that standing manual step, on every release,
  not a one-time line.
- **Alternative: the leaf only; `README.md` stands.** The leaf's fourth-carrier sentence drops;
  the pipx line stays untagged.

The user picks the side at approval; approval of this plan's stated side is the quote that
authorizes the edit.

Superseded after landing: the owner's ruling (MB6c) removes the hand-kept tag outright — B13
executes the removal, and the choice above is the historical record of what P13 settled.

Done-line: `just test-changed` (docs surface, `justfile:329`'s `*.md docs` row) and
`just check-links`.

### P14 Post-plan review

Lifetime: persistent — the review's product is `ACTIVE_PLAN_REVIEW.md`.

Scope: the post-plan review over the whole plan, staffed as the development skill's *Post-plan
review* section defines — the agent for each domain the plan changed substantively, a change where
a defect would pass unseen without that seat. For this plan: the architect (structure — the shared
spans, the clause reach, the seats' texts), the prompt-engineer (model-facing text — the
development skill, the guide, the agents-file block and the definitions), the security-reviewer
(the MB10 retirement's surface), the tech-writer (README, if P13's README side wins), and the
python-coder (clauses.py and the definition modules are Python). Each reviews against the project
documents and the accepted design.

Done-line: `just dev-check-plan` over this plan's final form, and the review document written.

## Post-plan burndown

### P15 Post-plan burndown drafting

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands. The review's 24 findings,
grouped under its eight root-cause headings, close through the eleven items below — groups merged
where one fix closes them (R6/R18/R23; R8/R10; R12/R13/R14; R15/R16/R17/R24), split where the
group needs two commits. R3 is drafted as a flag, not a fix: the owner has not decided the span
reading, and no wording change to the span is authorized in any item. R7's third-site half is
flagged for the owner the same way — the usability review reversed its premise, and B5 removes no
sentence without the ruling. R5 is closed by measurement, recorded in B3's facts and rewritten in
the review document.

Serial order per shared file, nothing concurrent across these runs:
`devpro/definitions/skills/development.py`: B4 → B5 → B7. `guide.py`: B4 → B5 → B10.
`clauses.py`: B9 → B12 → B11. `README.md`: B1 → B10 → B13 — B13 is the last reader of README and
runs after all three of B4/B5/B9. B13 edits
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/version-has-one-home.md` too: B9's two
leaves stand, B13's edit of the third is its own commit, and no other item edits that leaf.
`tests/render/test_structural_rules.py`: B3 → B8 — B8 updates the `REVIEW_SEVERITY` carrier set
B3's test pins. `tests/render/conftest.py`: B8 alone — B3's test reads its helpers and edits
nothing. `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md`: B5 → B9 — B5 cites the main-session term at
:106–107, B9 edits :119's count; different lines, ordered anyway. `PROJECT_DOCS/CONVENTIONS/`: B9's
two leaves are one commit, one direction; no other item edits them. No item edits this repository's
`CONVENTIONS.md`; B4's Dispatch bullet keeps naming it as the file that binds the cap. Each item
logs its recipe runs under its own ID as the job — `.devpro-temp/B<n>-<target>.log` — so no two
items' logs collide even back to back.

items' logs collide even back to back.

The tail's four dispatches (B7, B9, B10, B11) run on the coder agent's own model, not the
step-down — the owner's direction at dispatch resolution time (the step-down host has been running
hard); their ratings stay mechanical.

The tail's testing gate is batched by the owner's direction (the P6–P10 precedent): the four tail
items B7, B9, B10, B11 are small mechanical text edits — B11 also touches the test machinery
(`test_families.py`, `test.sh`) that the batched gate then exercises — so `just test-changed` and
`just lint` run once at the last of the tail's landings, over the entire change set, not per item.
Each item's cheap verification probes (render greps, `check-links`, `check-roadmap`) still run and
are recorded at that item's landing; the heavyweight gate is the one batched run. The plan lands
when it clears.

### B1 The release's README tag is guarded and the install paths agree

Rating: mechanical. Lifetime: persistent — the guard is repository machinery; the README text
ships.

Scope: `devtools/scripts/tag.sh` — beside its existing refusals (`justfile:106`'s `tag` refuses
while `devpro/` is uncommitted or the tag exists), a refusal while `README.md`'s pipx line's tag
differs from what `python3 -m devpro --version` prints, naming README's line; the README tag stays
hand-kept, the leaf's step unchanged. `README.md` — the *Updating* section gains one sentence
stating what the tag governs (the pipx install and update URLs) and that the brew path carries no
tag.

Two calls decided here, so the executor decides nothing:

- The map row the edit pulls: `devtools/scripts/` selects the `ALL` surface (the justfile's
  `TEST_SURFACE_MAP`), so this package's `just test-changed` is the full gate, not a delta run —
  accepted explicitly: the guard sits in a script no narrower surface reaches, and the full run is
  also the only automated exercise the refusal path gets.
- The *Updating* sentence's text: "The pipx install and update URLs pin a release tag
  (`@v<version>`, hand-edited beside each version bump); brew carries no tag — `brew upgrade`
  moves to the tapped formula's current release."
- The guard stays (the keep-or-drop call): R2's gap is admitted, the check is one refusal in a
  script that already refuses two ways, and dropping it leaves the leaf's hand-edit step held by
  nothing again.

Findings: closes R2; R1 is the wait, stated here — the tag resolves when `just tag` cuts `v0.18.1`
and the release pushes it, the release step this plan names no package for (ACTIVE_PLAN.md:11–14).
This commit performs the guard, not the release.

Facts: the leaf's step the guard holds — "A fourth carrier is hand-kept, not filled: `README.md`'s
pipx tag, `@v<version>`; its step is the hand edit beside the `__version__` bump, before `just tag`
cuts the release tag" (PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/version-has-one-home.md:5–7)
— is held by nothing today. R1's fact: README.md:61 reads `pipx install
"git+https://github.com/benn-herrera/devpro@v0.18.1"`; `git tag --list 'v0.18*'` prints only
`v0.18.0`.

Tests and fixtures: none pin `tag.sh`'s refusals today; the guard's refusal run is its own pin.

Done-line: `just test-changed`; `just lint`; then the refusal probe — the tag script's check path
run against a scratch copy whose README tag is wrong refuses, naming README's line, and passes with
the tag matching. No `tag` run is part of this done-line: the tag is cut by the release, not by
this package's verification.

### B2 The precedence span's open reading is flagged for the owner

Rating: mechanical. Lifetime: persistent — the roadmap ticket.

Scope: `ROADMAP.md` — one ticket stating the open reading and the decision it needs. No other file:
`devpro/clauses.py:121` keeps the span byte for byte; no item in this section edits it.

Findings: flags R3; closes nothing — R3 stays open until the owner rules.

Facts (R3, as the corrected review states them): the span's "there is no list of qualifying
documents and no carve-out" admits two readings — no exception to the precedence itself, or no
exceptions anywhere — and the second collides with the project's own leaves that name exceptions,
the value-constant exemption among them, quoted: "A `clauses.py` constant carrying a value rather
than a clause is not counted by the first check; `clauses.VALUE_CONSTANTS` declares the set, and a
new value constant is added there." (PROJECT_DOCS/ARCHITECTURE/rendering/structural-rules.md:48–49).
The heading ("The project's own documents modify the process") states a narrower rule than the
body, which also governs file headers and settled style; eleven seats that write no code read "the
code you change". The owner has not decided the reading.

The ticket names the two readings and the decision's owner — the ruling is the owner's, and no
wording is drafted until it is made; the ticket carries the colliding leaves and the audience
facts, so the ruling starts from the record and converts to a work item when it comes.

Tests and fixtures: none — no behavior changes.

Done-line: `just dev-check-roadmap` (the skill's rule: run it after each edit to `ROADMAP.md`);
`just test-changed` (docs surface).

### B3 The reach invariants are pinned by tests

Rating: mechanical. Lifetime: persistent — the suite.

Scope: `tests/render/test_structural_rules.py` — one test asserting two corpus facts:
`clauses.VENV_PROBE_RULE` is passed at exactly `devpro/definitions/agents/python_coder.py`'s and
`ml_engineer.py`'s `verification_evidence` call sites; the definition modules whose body names
`clauses.REVIEW_SEVERITY` are exactly architect, security-reviewer, tech-writer and
shell-dsl-coder. The set grows only by a deliberate edit; B8's edit is scheduled after this test
lands (the serial sentence below states that order). The third fact the draft asserted — every
agent-kind definition renders the precedence span — is **dropped: B12 removes the span outright**
(the owner's decision, the design's MB6b entry), so no test pins it.

Findings: closes R4 — two of its three invariants survive the span's removal; records R5's
closure.

Facts: R4 measured — `grep -rn "PROJECT_PRECEDENCE|VENV_PROBE_RULE|CONCURRENT_DISPATCHES" tests/
devtools/tests/` returns nothing, and the clause-group check covers group members only
(`UNGROUPED` carries no plain entries, tests/test_clause_groups.py:122). R5 closed by measurement:
`.devpro-temp/r5-grain-probe.py`, run under `.venv/bin/python` with `PYTHONPATH=.`, composes two
fixture pairs through `_uncredited_shared_paragraphs` the way `tests/render/test_prose.py`'s own
fixtures run. Result: two pastes of the span hard-wrapped at different widths (72 and 40 columns)
are found as one shared unit — `collapsed` (devtools/render_diff.py:86–110) joins a paragraph's
hard-wrapped lines before the comparison (`tests/render/conftest.py:467` builds the units from
it) — so a wrapped paste is not a different paragraph and R5's escape does not exist. The same run
shows a single wrapped paste beside a credited interpolation is not found: one writer, the check's
designed two-writer scope, grain-independent — a scope limit the closure note records, not a
defect this plan acts on. The test holds these facts; a corpus change that breaks one fails it.

Tests: these are the tests.

Done-line: `just test-changed`; `just lint`.

### B4 The concurrency cap's statements state one arithmetic and one name

Rating: mechanical. Lifetime: shipped.

Scope: `devpro/definitions/skills/development.py` — the Dispatch bullet (:349–353) and the count
bullet (:485); `devpro/definitions/skills/guide.py` — the go bullet (:350–351). The naming call:
the term {CONCURRENT_DISPATCHES_TERM} is the one name the sites keep — the Dispatch bullet's "the
count of {CONCURRENT_DISPATCHES_TERM}", the table row's term cell, and the guide's go bullet,
which gains the term (it names the cap and never the term today — guide.py:350–351, measured);
"count" and "number" survive only as common nouns in the sentences the term anchors. With the term
at both sites an agent can reconcile the two statements' arithmetic.
R18's half: the count bullet states that the consuming project provides the `plan-count` target in
its own runner — a Makefile project spells it there — instead of assuming it exists. The arithmetic
is stated once, in the skill's Dispatch bullet; the guide's go bullet refers to it by the term, so
the two sites cannot disagree.

Findings: closes R6, R18, R23.

Facts: R6 — the guide's "a go for a dispatch that would raise the number of agents running at once
past the cap the development skill states (*Dispatch*)" versus the skill's "A dispatch that would
raise the count of {CONCURRENT_DISPATCHES_TERM} past the cap" admit different arithmetic, and the
guide never names the term. R18 — the count bullet's "The {PERIODIC_REVIEW_INTERVAL_TERM}'s count
is what the `plan-count` runner target prints:" names the target without saying the project
provides it.

Shared-constant references: `git grep -l CONCURRENT_DISPATCHES -- devpro tests` prints
`devpro/clauses.py` and `devpro/definitions/skills/development.py` — the constant's default and
text stand; no table or test change.

Tests and fixtures pinning the changed behavior: the term-value test
(tests/render/test_structural_rules.py:294) pins every mention to the constant; the count-target
test (tests/render/test_families.py:186–194) parses "`<name>` runner target" from the Periodic
review section — the R18 sentence keeps that form.

Done-line: `just test-changed`; `just lint`; then `just render latest`, then
`grep -c "concurrent dispatches" rendered/latest/devpro/skills/devpro/skills/development/SKILL.md`
reports at least `2`, and
`grep -c "concurrent dispatches" rendered/latest/devpro/skills/devpro/skills/guide/SKILL.md`
reports at least `1` — the item changes the guide's text, so this expectation is the rendered
truth after it, stated here because guide.py:351 holds no such text today.

### B5 The drafting and trigger boundaries state what they decide

Rating: mechanical. Lifetime: shipped.

Scope: `devpro/definitions/skills/development.py`. Three edits; every wording decided here:

- R10, all three boundary sites, both named: the Plans bullet (:173–174), the burndown bullet
  (:443–444) and the periodic-review drafting sentence (:502) each gain the seat's name — the main
  session. The call: the skill's own docstring (development.py:1, "the skill that carries one
  development process for the main session") and the subsystem map (:106–107) name that seat, so
  the boundary states it rather than leaving "the session" to the loading agent's guess. The two
  byte-identical boundary sentences (:173–174, :443–444) change by the seat word only, staying
  identical to each other; :502's sentence gains the same seat word and loses no sentence — the
  flag below governs that site.
- R8, the trigger bullet (:477–480): "a coherent feature boundary is reached" gains the deciding
  half it lacks — who judges. The call, sourced from the leaf the consuming projects never render
  (the-gates.md:17–22, quoted: "The periodic review runs at a coherent feature boundary, the
  user's direction: a full project review makes sense only when the project holds a coherent set
  of functionality — no incomplete work split across multiple plans, no undone pieces dangling
  from a landed plan"): the bullet states the boundary is the user's direction — the review runs
  when the user judges the project holds a coherent set of functionality — so the count says when
  the review is due and the user's judgment says when its result is worth anything.
- R7, flagged not fixed: the usability review reversed R7's third-site claim — development.py:502
  is text about a plan, and the review drafts a plan from findings by its own label, so the copied
  "a request for the plan is not that ask" is not measured a defect there. Whether that clause
  stays at :502 is the owner's ruling; this item removes no sentence and flags the reversal here,
  where the owner meets it at approval.

Findings: closes R8, R10; flags R7 for the owner — its premise is under reversal and no sentence
moves without the ruling.

Facts: R7 — the boundary is stated three times, byte-identical at two sites (:173–174, :443–444),
and the third (:502) copies the clause the review now measures as fitting its context. R8 — the
trigger rewrite deleted "the boundary is", leaving "coherent feature boundary" undecidable at the
point it fires. R10 — "the session" is unnamed.

Tests and fixtures: none pin these sentences — P8's "asks the session itself × 3" count was a
one-time render probe, not a standing test; the term-value test pins term spellings only. B3's new
test does not reach these sites.

Done-line: `just test-changed`; `just lint`; then `just render latest` and a read of the three
sites in the rendered SKILL.md — each carries the seat name, and the trigger bullet carries the
user's-direction half.

### B6 The alias rule states a mechanical form, not a recalled list

Rating: mechanical. Lifetime: shipped.

Scope: `devpro/definitions/harness_agents_file.py` (:135–139). The bullet's rule becomes one a
model follows without recalling the operator's profile: a tool command or dispatched instruction
runs every command through `command`, the profile's alias set neither enumerated nor recalled. The
keep-the-examples call: the four `command rm` / `command cp` / `command mv` / `command ls` forms
stay — they cost one clause, show the rule's most-hit cases, and the rule, not a set, is what the
bullet obliges.

Findings: closes R9.

Facts (R9, quoted): "Tool commands and dispatched instructions call any command the operator's
profile may alias through `command` — `command rm`, `command cp`, `command mv` and `command ls`
are examples, not the whole set." — the obligation requires recalling an unbounded list; a machine
guarantee handed to a model.

Tests and fixtures: none pin the bullet's text — the render checks are structural, and P10's
render probes were one-time.

Done-line: `just test-changed`; then `just render latest`, then
`grep -c "may alias" rendered/latest/devpro/AGENTS.md` reports `0` and the rendered bullet states
the `command` prefix rule.

### B7 The development skill's governance paragraph moves below its Route table

Rating: mechanical. Lifetime: shipped.

Scope: `devpro/definitions/skills/development.py` (:46–48): the `{clauses.PROJECT_PRECEDENCE}`
paragraph moves from the body's first position to the end of the *Route* section — its own
paragraph immediately before the `## Terms` heading (## Route runs :48–61, ## Terms opens :62,
measured). One interpolation, one site — the no-shared-clause-twice checks are unaffected.

Findings: closes R11.

Facts (R11, quoted): the skill "now opens with a governance paragraph ahead of its *Route* table,
burying the routing a newcomer needs first."

Shared-span references: `git grep -l PROJECT_PRECEDENCE -- devpro` prints 14 files — the span's
text once in `devpro/clauses.py:121`, twelve agent definitions, this skill. Only this skill's
placement moves; the definitions' placements (the design's "directly after the body's opening
paragraph") stand.

Tests and fixtures pinning the changed behavior: tests/render/test_prose.py:104 (one source) and
:143 (no span twice) — both unaffected, still one interpolation.

Done-line: `just test-changed`; `just lint`; then the rendered SKILL.md reads *Route* before the
governance paragraph.

### B8 The severity ladder's reach and seams close

Rating: mechanical. Lifetime: shipped.

Scope: `devpro/definitions/agents/prose_architect.py` (:45–46) — the ladder the R12 measurement
names ("Severity-tag in brackets: `[Note]` for stylistic suggestion, `[Warning]` for a real rhythm
or comprehension problem, `[Critical]` for a logical gap or error.") is replaced by
`{clauses.REVIEW_SEVERITY}` and the mapping sentence, drafted here so the executor drafts nothing:
"{clauses.REVIEW_SEVERITY} The audit's bracket tags carry these tiers: `[Note]` its Note,
`[Warning]` its Warning, `[Critical]` its Critical." — the bracket tags stay in the output format;
the ladder behind them is the shared one. `devpro/definitions/agents/architect.py` (:213) —
R14's doubled label: the item reads `2. {clauses.REVIEW_SEVERITY}` — the local
"**Classify severity**: " lead goes, the span's own label carries the line, and the Review
Process list's other items keep their labels. `devpro/definitions/agents/security_reviewer.py`
(:104–106) — R13's seams: the domain sentence gains the Note mapping and states that it *narrows*
the span's Critical for hazards, so the two definitions cannot drift apart silently.

Findings: closes R12, R13, R14.

Facts: R12 — the seat the MB13 sweep missed carries its own ladder. R13 — the shared ladder's Note
has no security gloss and the two Critical definitions coexist with no precedence rule. R14 — the
architect's line renders "**Classify severity**: **Severity by when the cost lands**:".

Shared-constant references: `git grep -l REVIEW_SEVERITY -- devpro tests` prints
`devpro/clauses.py`, `agents/architect.py`, `agents/security_reviewer.py`, `agents/shell_dsl_coder.py`,
`agents/tech_writer.py`, `tests/render/conftest.py`. The constant's text stands; prose-architect is
a new carrier. The join-site tuple (tests/render/conftest.py:356, 391, 396) gains
prose_architect's site and changes architect's — updated deliberately in this commit.

Tests and fixtures: tests/test_clause_groups.py — prose-architect is ungrouped, so no table row
changes; tests/render/conftest.py's join-site tuple above; and B3's pinned `REVIEW_SEVERITY`
carrier set gains prose-architect — updated in this commit (B3 lands first; the serial order
between them is the set's). tests/render/test_prose.py:104, :143.

Done-line: `just test-changed`; `just lint`; then `just render latest`, then
`grep -c "Severity by when the cost lands"
rendered/latest/devpro/skills/devpro/agents/prose-architect.md` reports `1`, and the architect's
rendered Review Process item 2 reads one label.

### B9 Stale text and artifacts removed

Rating: mechanical. Lifetime: mixed — the deletions are one commit; the corrected documents
persist.

Scope: `rendered/agents/` — the git-ignored stale render, populated today, removed from the
filesystem (it carries the retired pipeline text; an install from it without regeneration revives
what MB10 retired; nothing reads it back — fresh renders go to `rendered/latest/` and the
reference slots). The observation is not "deleted" — a git-ignored deletion produces no diff — it
is the before-and-after counts in the Facts, plus the render run showing nothing revives the path.
`devpro/clauses.py:323` — `DATA_FORMATS`' tail sentence "Where the project's `CONVENTIONS.md` says
more about formats, it governs." deleted; the span's general rule covers it.
`PROJECT_DOCS/ARCHITECTURE/subsystem-map.md:119` — "its six supporting files" reads "seven", the
count the entry's own list (:102–103) states.
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-count-is-a-target.md:3` and `the-gates.md:9`
— "`just plan-count`" reads "the `plan-count` runner target", the naming MB3 retired leaving this
repository's CONVENTIONS too. The replacement wordings are fixed as stated here; the executor
drafts nothing.

Findings: closes R15, R16, R17, R24.

Facts: R15's observation, repeatable today: `find rendered/agents -name '*.md' | wc -l` reports
`50`, `grep -rl "burn-down" rendered/agents | wc -l` reports `4`, and the root is git-ignored
(justfile:96–100 names the render slots' root so). The work is the filesystem deletion plus the
check-runner step that prevents revival: the render writes only its own slots, so after deletion a
fresh `just render latest` leaving `rendered/agents` absent is the repeated observation. R16's
defect line, quoted: "Where the project's `CONVENTIONS.md` says more about formats, it governs."
(devpro/clauses.py:323). R17's defect phrase, quoted: "in `SKILL.md` and its six supporting files
interpolates" (subsystem-map.md:119). R24's lines: the-count-is-a-target.md:3 and the-gates.md:9,
both reading "`just plan-count`".

Shared-constant references (R16): `git grep -l DATA_FORMATS -- devpro tests` prints
`devpro/clauses.py`, nine agent files, `tests/render/conftest.py`, `tests/test_clause_groups.py` —
the edit keeps the constant's name, so the plain-entry tables do not move; only the tail sentence
goes.

Tests and fixtures: tests/render/test_prose.py:104 (one source) — unaffected.

Done-line: `just test-changed`; `just check-links`; `just lint`; then `ls rendered/agents` fails
and `grep -rn "says more about formats" rendered/latest/devpro/` reports nothing.

### B10 The guide points at no upgrade walk that is not there

Rating: mechanical. Lifetime: shipped.

Scope: `devpro/definitions/skills/guide.py` (:98) — the installing reference's sentence is
**removed**. There is no upgrade walk: README carries one behavior paragraph about 0.17.x
upgrades (README.md:222–225, under no walk banner, one statement of behavior), and the guide's
sentence misnames it "the walk … under *Updating*" — not a walk, and not under *Updating*.
Removing the sentence closes R19 by removal: one statement of the behavior remains (README), no
restatement left to drift. The README paragraph takes no edit.

Findings: closes R19 by removal — the restatement is deleted, not homed.

Facts: guide.py:98 reads "A project installed by 0.17.x upgrades by the walk the repository's
README states under *Updating* ({clauses.REPOSITORY_URL})."; README.md:222–225 reads "A project
installed by 0.17.x upgrades in one run: an install replaces the plugin directory whole, …" —
behavior, not a walk, and the guide's pointer misnames both the shape and the section.

Tests and fixtures: none pin either text; `just check-links` verifies the repository's links are
undisturbed after the removal.
Done-line: `just test-changed`; `just check-links`; then
`grep -rn "the walk the repository's README states" rendered/latest/devpro/` reports nothing — the
sentence is gone, not relocated.

### B11 The runner's new machinery seams closed

Rating: mechanical. Lifetime: persistent — devtools and tests; the clauses.py edit ships.

Scope: `devtools/scripts/test.sh` and `devtools/tests/test_changed_map.py` (R20) — the surface
names are defined in test.sh's case statement and re-pinned in the test's `SURFACES` set
(test_changed_map.py:11); one edit adds a surface after this closes — the test reads the names
from test.sh, or test.sh derives them from the map the justfile holds, the coder picks the single
source. `tests/render/test_families.py` (:186–194, R21, restated to the measured defect) — the
vacuity assert (:194) is a block-level assert naming no path, so a failure does not say which
construction broke; and the slice starts at the `## Periodic review` section rather than the count
bullet, so the parsed targets are the section's, not the count's. The missing-heading `ValueError`
at :196 is unreachable today because :194 fires first — stated so nobody fixes a defect that
cannot fire. The fix: the test slices from the count bullet, and the guard's message names the
path it searched. `devpro/clauses.py`
(:268, R22) — the leading space moves from `VENV_PROBE_RULE` into `verification_evidence()`'s
composition, so the empty default still renders no separator and the constant reads like every
other constant; the structural rule holds — three keyword-only parameters, no call.

Findings: closes R20, R21, R22.

Facts: R20 — a new surface needs an edit in two places (measured: test_changed_map.py's `SURFACES`
set against test.sh's case arms). R21, R22 as the review states them.

Shared-constant references (R22): `git grep -l VENV_PROBE_RULE -- devpro tests` prints
`devpro/clauses.py`, `devpro/definitions/agents/ml_engineer.py`, `devpro/definitions/agents/python_coder.py`
— the call sites stand; only the constant's first character and the function's composition move.

Tests and fixtures: `test_changed_map.py` is itself the changed test; the sentinel sweep
(tests/render/conftest.py:601) reads `VALUE_CONSTANTS`, which the change does not touch.

Done-line: `just test-changed`; `just lint`; then the render probe —
`grep -c "A probe that imports" rendered/latest/devpro/skills/devpro/agents/python-coder.md`
reports `1` and the rendered paragraph's spacing is unchanged.

### B12 The precedence span is removed outright

Rating: mechanical. Lifetime: shipped.

Scope: `devpro/clauses.py` — `PROJECT_PRECEDENCE` deleted; the twelve interpolations and the two
stacks' embeddings removed; `devpro/definitions/skills/development.py` — the opening governance
paragraph deleted; `ROADMAP.md` — B2's flag ticket removed, its supersession named in this item's
commit body; `tests/render/test_structural_rules.py` — B3's precedence pin dropped (edit B3's
landed test; if B3 has not landed, note the pin's removal as owed to its landing).

Entry: [MB6b](ACTIVE_DESIGN.md#code-delta) — the owner's decision: a project can override the
process by writing its own text (the agents file, its documents, a file's own header) and can be
as explicit as it likes; granting permission ahead of time for what is in the user's power
already is machinery for nothing. The review's R3, W7, W8, R4's precedence pin, and R5's closure
note go with it.

Reference search — the span's name and text are removed everywhere: `git grep -n
PROJECT_PRECEDENCE -- devpro tests` prints the constant, the twelve interpolation sites, the two
stacks and the skill's opening before the removal, nothing after.

Tests and fixtures: `tests/render/test_prose.py`'s shared-paragraph check loses one span;
`tests/render/test_structural_rules.py`'s invariant test drops its precedence pin; the corpus
/join-site checks re-run against the stacks' shorter bodies.

Done-line: `just test render`; `just test dupe_sweep`; then `just render latest`, then
`grep -rn "PROJECT_PRECEDENCE" devpro/ tests/` reports nothing, and
`grep -rn "The project's own documents modify the process" rendered/latest/devpro/` reports
nothing, and `grep -rn "no carve-out" rendered/latest/devpro/` reports nothing.

### B13 The README's pipx line carries no version tag

Rating: mechanical. Lifetime: shipped — README and tag.sh; the SPEC and CONVENTIONS leaves persist.

Scope: `README.md` — :61's pipx install line loses `@v0.18.1` and reads
`pipx install "git+https://github.com/benn-herrera/devpro"`, unpinned; :219's sentence is
rewritten without the hand-kept tag — the brew-carries-no-tag half stands; :221's update sentence
is rewritten without "the next release's tagged URL". `devtools/scripts/tag.sh` — the README-tag
comment paragraph (:33–37) and the read-and-refuse block (:38–42) are deleted; the dirty-tree,
version-read and duplicate-tag checks stand. `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/version-has-one-home.md` —
the fourth-carrier sentence (:5–7, inside the leaf's opening paragraph — the paragraph around it
stands) is deleted, the leaf stating the version's carriers as the one constant and the three
filled render slots. `PROJECT_DOCS/SPEC/package-and-command.md` — :4–5's sources sentence gains
the unpinned git URL as the README's stated source, beside the release tag's URL and the built
wheel; the release tag's URL stays a source but loses the `@v<version>` pipx spelling in the
rewrite (the tag itself is `v<version>`, the CONVENTIONS leaf's) — the done-line's placeholder
grep expects SPEC clean of it.

Design entry: [MB6c](ACTIVE_DESIGN.md#code-delta) — the owner's decision, quoted there: the hand
edit beside each bump is rot bait; a guard can only name its failure loudly, never prevent it.

Facts: README.md:61 reads `pipx install "git+https://github.com/benn-herrera/devpro@v0.18.1"`;
:219 reads "The pipx install and update URLs pin a release tag (`@v<version>`, hand-edited beside
each version bump)…"; tag.sh's guard reads `readme_tag=…` from the pipx line and refuses a
mismatch against `__version__` (tag.sh:33–42, the region this item deletes); version-has-one-home.md:5–7
reads "A fourth carrier is hand-kept, not filled: `README.md`'s pipx tag, `@v<version>`; its step
is the hand edit beside the `__version__` bump…"; SPEC/package-and-command.md:4–5 reads "a
release tag's git URL, `git+https://github.com/benn-herrera/devpro@v<version>`, or a built wheel."

Reference searches: `git grep -n 'hand-kept\|hand-edited\|@v<' -- PROJECT_DOCS` prints six hits —
the leaf's two lines (:5–6) and four unrelated ones: renders-and-copies' managed-path list,
undice's regenerated block, the THESIS entry-point's hand-kept files, and
SPEC/package-and-command.md:5, whose `@v<version>` is the release tag's URL — the pipx spelling
this item's SPEC edit drops, so that hit goes with the edit. Only the leaf states the README tag.
`git grep -l tag.sh -- devtools tests` prints nothing — no test in either tree names the script;
B1's refusal probe was a manual run against a scratch README.

Tests and fixtures: none pin the changed behavior — the leaves are checked by the docs surface,
which the done-line runs.

Done-line: `just test-changed`; `just lint` — `devtools/scripts/` selects the `ALL` surface (B1's
accepted call), so this test-changed is the full gate, not a delta run; `just check-links` — the
one recipe that reads both
edited leaves; then `git grep -E '@v[0-9]+' -- README.md devtools` reports nothing (it is red
before the change: README:61 is its only match — the tag.sh guard's literals do not match the
pattern), `git grep -n '@v<version>' -- PROJECT_DOCS/SPEC PROJECT_DOCS/CONVENTIONS` reports
nothing — the check that sees SPEC's placeholder — and `grep -c README devtools/scripts/tag.sh`
reports `0`, the script consulting nothing hand-edited.

Findings: supersedes B1's fix direction per MB6c — the guard was landed for a carrier this
decision removes.
