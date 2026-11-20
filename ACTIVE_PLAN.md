# Active plan — the periodic review over the accumulated work since 69eed3e

This is the project's periodic review. It has no design: it delivers findings, not a contract
delta, so it goes straight to a plan, and this plan is what the user approves. Its material is
everything landed since `69eed3e` (devpro 0.17.2) — seven landed plans — weighted toward the most
recent profiler work. Its members' findings are its post-plan review, written to
`ACTIVE_PLAN_REVIEW.md`, and are fixed in its post-plan burndown, outside any release's hardening.

Trigger, checked: the periodic review interval is bound at 5
(`git grep -n 'periodic review interval' -- 'PROJECT_DOCS/CONVENTIONS/*'` →
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md:6: periodic review interval: 5`,
committed at `b68d4a7` by user direction). Seven plans have landed since the last periodic review
at `69eed3e` — overdue under either the binding's five or the skill's default three. The review is
made active now, before any other plan.

The review's interval is timely but its discipline is not optional: each member judges only what
changed since it last ran (its last run is the previous periodic review, landed at `69eed3e`), and
reopens nothing settled.

## Facts, each with the command and its answer

- **The range's plan landings and the version span.** `git log 69eed3e..HEAD --format='%h %s'` →
  seven plan-landing commits, oldest first: `f6e50c6` (devpro 0.17.3, lands the scratch-directory
  plan), `be431e5` (lands the session nudge and the kanban wording), `50d99a2` (lands the reminder
  gate reading the plan alone), `613cc7c` (lands the plugin-family consolidation), `5bc0204` (lands
  the byte-check reaching the development skill), `7016420` (devpro 0.18.0, lands the profiler
  port), `cec0a46` (lands the opencode profiler plan). The version span is 0.17.2 → 0.18.0:
  `git grep -n '__version__' -- devpro/__init__.py` → `devpro/__init__.py:51: __version__ =
  "0.18.0"`.
- **The project documents' shape.** `PROJECT_DOCS/entry-point.md` is the THESIS (titled `THESIS -
  devpro`); the root `THESIS.md`, `SPEC.md`, `ARCHITECTURE.md` and `CONVENTIONS.md` are pointer
  stubs (`THESIS.md:3` — "The THESIS now lives in the `PROJECT_DOCS/` tree"). The diced trees:
  `find PROJECT_DOCS/SPEC -name '*.md' | wc -l` → 15 leaves; `ARCHITECTURE` → 23; `CONVENTIONS` →
  49. A seat reads a document whole by reading every leaf in its entry point's order.
- **The languages' surfaces.** `just lint` → `101 files would be left unchanged.` — the lint
  surface is 101 files, of which `find devpro -name '*.py' | wc -l` → 65 live in `devpro/` (the
  rest are tests and devtools). The TypeScript surface is three files,
  `devpro/harnesses/resources/opencode/{guardrail.ts,index.ts,profiler.ts}`, with no type check —
  `grep -n 'No TypeScript type check' ROADMAP.md` → `108:### No TypeScript type check` (the known
  gap, not reopened here).
- **The profiler is shipped and in use.** `ls .devpro-temp/opencode-profiler` → live session JSONL
  captures. `.devpro-temp/claude-profiler/` does not exist (`ls` → No such file or directory): the
  claude capture's trace directory is code-created on first use
  (`devpro/harnesses/resources/claude/profiler/hp.py:25` — `TRACE_DIR =
  Path(".devpro-temp") / "claude-profiler"`), and no claude session has captured here. The review
  treats the opencode profiler as live and the claude path as shipped.
- **The routing facts.** Source: the session's standing directive — cloud dispatches route via the
  wafer provider; coder seats `wafer.ai/DeepSeek-V4.1-Flash-1017`, architect and prompt-engineer
  seats `wafer.ai/GLM-5.3-Flash`. By that directive the architect and prompt-engineer seats route
  to GLM and the coder seats to DeepSeek. The tech-writer is unnamed in it; its rendered definition
  carries `member=wafer/DeepSeek-V4.1-Flash-1017` (rendered from
  `devpro/definitions/agents/tech_writer.py:18` — `category="comm-expert"`; banner at
  `.opencode/plugins/devpro/agents/tech-writer.md:2`), so the tech-writer seat routes to DeepSeek
  under the same directive. Both models are on the wafer provider, so the local-inference
  concurrency limit does not apply to this fan-out.

## Bound terms

- **Checkpoint gate:** `just test`, then `just sweep-python` (A checkpoint includes the sweep)
  (`PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md:4`).
- **Step-down application:** the dispatch's `model` parameter (`the-gates.md:5`). Unused here:
  every package of this plan is expert.
- **Plan size limit:** CONVENTIONS binds none; the skill's default of 800 lines applies
  (`git grep -n -F 'plan size limit:' -- '*CONVENTIONS*'` → no hit). This plan is under it.
- **Step-down model:** CONVENTIONS binds none. No package is mechanical, so none is needed.

## The panel

The default eight seats, two for each of `devpro-architect`, `devpro-prompt-engineer`,
`devpro-tech-writer` and the project's coder agent: a **conformance** seat and a **consistency**
seat per agent.

| Seat | Agent | Question | Model |
| --- | --- | --- | --- |
| architect / conformance | `devpro-architect` | judges with its own review criteria; reports departures from THESIS.md, SPEC.md, ARCHITECTURE.md, CONVENTIONS.md | `wafer.ai/GLM-5.3-Flash` |
| prompt-engineer / conformance | `devpro-prompt-engineer` | same, for the model-facing text it reviews | `wafer.ai/GLM-5.3-Flash` |
| tech-writer / conformance | `devpro-tech-writer` | same, for README.md and the human-facing guides | `wafer.ai/DeepSeek-V4.1-Flash-1017` |
| coder / conformance | `devpro-python-coder` | same, for the code | `wafer.ai/DeepSeek-V4.1-Flash-1017` |
| prompt-engineer / consistency | `devpro-prompt-engineer` | — its pair is named in P2 | `wafer.ai/GLM-5.3-Flash` |
| architect / consistency | `devpro-architect` | — its pair is named in P2 | `wafer.ai/GLM-5.3-Flash` |
| tech-writer / consistency | `devpro-tech-writer` | — its pair is named in P2 | `wafer.ai/DeepSeek-V4.1-Flash-1017` |
| coder / consistency | `devpro-python-coder` | — its pair is named in P2 | `wafer.ai/DeepSeek-V4.1-Flash-1017` |

**The language split — stated call: one seat naming both.** The project's coder agent is
`devpro-python-coder` (the primary language; 65 of the lint surface's files), and both coder
briefs name the TypeScript resources — `profiler.ts`, `index.ts`, `guardrail.ts` — as in-scope
alongside `devpro/` and `tests/`. A separate typescript-coder pair would exceed the default
eight-seat panel for a three-file surface; the split is surfaced here and in the briefs instead.

Every consistency seat reads both sides whole — every leaf of each diced tree in its entry point's
order, and the THESIS in `PROJECT_DOCS/entry-point.md`. Each seat's brief carries the project
documents and the material's facts above, never this plan: the members judge what shipped, not the
plan's account of itself. Each seat writes its own review to `.devpro-temp/review/<agent>-<seat>.md`,
one finding per departure, marked with what changed since `69eed3e` it rests on.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | in progress | expert | Panel — the four conformance seats (4 agents, parallel) |
| P2 | in progress | expert | Panel — the four consistency seats (4 agents, parallel with P1) |
| P3 | landed | expert | Post-plan review — the seats synthesized into `ACTIVE_PLAN_REVIEW.md` |
| P4 | dispatchable | expert | Post-plan burndown — drafted from the review, PE-reviewed, revised, executed |

The plan's packages go out `drafted`; the plan's one `devpro-prompt-engineer` usability review and
one architect revision set P1 and P2 `dispatchable`. P3 becomes `dispatchable` when P1 and P2 are
landed; P4's row is set from the review document's landing, per the placeholder in its section.

## P1 — Panel: the four conformance seats

Dispatches four expert agents, one per seat type, each with the project documents and the facts
above (the seven landings weighted toward `7016420` and `cec0a46`), reporting every departure from
THESIS.md, SPEC.md, ARCHITECTURE.md or CONVENTIONS.md its own review criteria surface.

- `devpro-architect` — scope: the changed structure — `devpro/harnesses/resources/claude/profiler/`,
  `devpro/harnesses/resources/opencode/`, `devpro/definitions/`, the justfile's new targets — read
  against the documents above it.
- `devpro-prompt-engineer` — scope: the model-facing text that changed — the development skill's
  byte-check rule and delta-check reading, the reminder-gate sentence, the profiler definitions
  and hooks.
- `devpro-tech-writer` — scope: README.md and the human-facing guides' changed passages — the
  install and quick-start rework, the plugin-family consolidation's user-facing text.
- `devpro-python-coder` — scope: the Python package and the three TypeScript resources above;
  both languages named in the brief.

Scope of the package: the four briefs (session-drafted, in the scratch directory) and the four
scratch reviews. The package changes no tracked file, so no runner target applies to its
done-line: done is the four reports present in `.devpro-temp/review/`, their facts spot-checked
against the tree under *Acceptance* before P3 reads them.

## P2 — Panel: the four consistency seats

Dispatches the other four expert agents, in parallel with P1 — eight agents at once, four on
`wafer.ai/GLM-5.3-Flash` and four on `wafer.ai/DeepSeek-V4.1-Flash-1017`; the approval of this plan
is the go that names that count. Each consistency seat owns its pairs and reads both sides whole:

- `devpro-prompt-engineer`: THESIS.md (`PROJECT_DOCS/entry-point.md`) against SPEC.md;
- `devpro-architect`: SPEC.md against ARCHITECTURE.md;
- `devpro-tech-writer`: SPEC.md's coverage of README.md and the human-facing guides against those
  texts;
- `devpro-python-coder`: ARCHITECTURE.md against the code (both languages), and each CONVENTIONS.md
  rule against how the repository behaves — the 49-leaf tree read against the repo, its runner and
  its rendered output.

Each seat reports every inconsistency it finds — whether the texts assert one thing, and whether
the code does what ARCHITECTURE.md says — to its own scratch review. Scope and done-line as P1's:
the four briefs and four scratch reviews, no tracked file changes.

## P3 — Post-plan review: the seats synthesized

The session synthesizes the eight seat reviews into `ACTIVE_PLAN_REVIEW.md`, de-duplicating:
**one ID per defect** (`R1`, `R2`, …), one entry per defect naming every seat that reported it,
the findings reconciled into one account. The review document is never diced.

Scope: `ACTIVE_PLAN_REVIEW.md` (new, at the root); reads `.devpro-temp/review/*.md`. The review
lands in its own commit, whose row flips to `landed` as that commit lands.

Done-line: `just dev-check-links` — the review document's links must resolve
(the check covers `*.md` at the root), run once, at the package's end.

## P4 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands. Until then this section
holds only that.

When drafted: the burndown's work list cites the review IDs and **groups the findings by root
cause** — not one item per finding — and sequences the fixes by the full review's order
(vocabulary, then novelty language, then contradictions — each checked against the code before the
user decides — then undefined terms and requirements sent to another document, then mechanism in
the wrong document, then a piece pushed past its "is not", where the user decides whether the
document or THESIS.md moves). The fixes are outside any release's hardening.

The drafted burndown gets its `devpro-prompt-engineer` usability review, then a revision here,
before its row is `dispatchable`. Execution closes the package in one commit — if the findings'
scope would need more, the session splits the package before dispatch and updates the status table.

Scope: the burndown's fixes, named per item when this section is drafted (likely `PROJECT_DOCS/**`,
the definitions and skills text, and the code the findings name). Each item lists the
types/signatures it changes with the reference search and its answer, and names the tests and
fixtures pinning any behavior it moves.

Done-line: the checkpoint gate — `just test`, then `just sweep-python` — and
`just dev-check-links` for the document fixes, run once, at the package's end.

## Landing

The plan's landing commit: it deletes `ACTIVE_PLAN_REVIEW.md` (never before — the burndown cites
it until it lands), carries the final status rows with every package `landed`, and its message
says it lands this plan. The plan is deleted with it — a landed plan left in place reads as work
still under way. The closing commits carry the attribution line and bodies, per *Commits and pull
requests*.
