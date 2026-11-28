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
`just tag` is not part of this plan, and the README hand-edit that leaf's step names is P13's.
The untracked `SUGGESTED_MECHANICAL_FIXES.md` is the transient review the design captured and
cites nowhere: no package commits it.

**The version bump is already done.** `devpro/__init__.py` carries `__version__ = "0.18.1"`
(uncommitted; `git diff devpro/__init__.py` shows the change from `"0.18.0"`). The plan carries it
in P1, the first package that changes block content, as a named edit in P1's scope and commit.

**The one choice this plan puts to the user at approval** is P13's side of the README pipx-tag
discrepancy; the plan's recommended reading is stated there.

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
| P13 | landed: dbc05b64 | mechanical | the pipx decision |
| P14 | dispatchable | expert | — |
| P15 | dispatchable | expert | — |

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

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
