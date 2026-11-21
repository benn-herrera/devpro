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
| P4 | in progress | expert | Post-plan burndown — drafted from the review, PE-reviewed, revised, executed |

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

Drafted from `ACTIVE_PLAN_REVIEW.md` (landed at `4a0025b`): 6 Critical (F1–F6), 18 Medium/High
(F7–F24, one per ID), 6 Low (F25–F30) — 30 findings. Thirteen items by root cause, plus two
user-decision items held out. Two findings retired in the prompt-engineer review for having no
defect at HEAD — F6 with B4 (noted before the held list), F20 with B12's first half (noted at B12) —
leaving their items one shorter. Each item names its surfaces and verification; the seat files in
`.devpro-temp/` carry the per-finding detail.

**B1 — README's install/update/mage surface returns to SPEC (F2, F3, F11, F12, F13; F1 verified
fixed).** The install-paragraph contradictions, the Updating self-contradiction, the pipx
`ensurepath` steps, the gitignore guidance, and the mage migration paragraph's SPEC absence — one
README pass reading each section against its SPEC leaf, plus the SPEC-side sentence the mage
paragraph needs. F1 (the mage install command) is already repaired at HEAD (`f0b32ab`,
`README.md:105`) and is verified only, not re-fixed. Verify: each of the five live sections names
the SPEC passage it answers to and the sentence that changed; the mage command copied and run in a
scratch project.

**B2 — the profiler's user-facing line and its discovery (F4, F10).** `README.md:45` states what
actually records per harness (claude's six events; claude-on-web's `init` requirement; mage ships
none) and the Next section routes to the show-profile skill; the guide's Route gains the same
routing. Verify: README read against `shipped-files.md`; the Route names the skill.

**B3 — the two-acts reminder description moves to the shipped sentence (F5).**
`opencode-entry.md:63-66` and `guardrail-hook.md:24-25` describe the reminder as injected —
"keep the ACTIVE_PLAN state table up to date." — the sentence both harnesses actually carry
(`index.ts:108`, `state-table-reminder.sh:52`). The same pass corrects the code comment still
asserting the retired description, at `state-table-reminder.sh:50-51`. B3 lands before B8, whose
SPEC sentence reads the corrected leaf.

**B5 — the carriers refresh (F7).** `just agents` re-installs this checkout's devpro here
(justfile:297), refreshing the installed carriers that live in every session —
`.opencode/plugins/devpro/…` and `.claude/…`; `just render` re-runs for the rendered slots. Both
carry the interval default 5 and the current step-down rendering, with B7's source correction
landed first. Verify: `grep 'default 5'` over the installed carriers reads the refreshed value
back. The recurrence is noted: a version bump's landing re-renders — the mechanism question
(auto-render at bump) is a design candidate, not a fix.

**B6 — the docdicer skill's script section states the shipped recipes (F8).** `check-design` and
`check-roadmap` recipes exist; the deltas-applied recipe is named where the development skill and
the CONVENTIONS leaf point at it.

**B7 — the guide's Getting-started and SPEC agree on the scratch step (F9).** The fix is in the
source (`guide.py:241-245`, still carrying the scratch step via `{clauses.PROJECT_TEMP_DIR}`) and
lands before B5's re-render, so no stale terminal render passes the gate.

**B8 — SPEC gains the claude reminder sentence and the opencode store (F14, F28 part).** After
B3's leaf correction, `shipped-files.md` states the claude reminder as it ships: the injected
sentence "Reminder: keep the ACTIVE_PLAN state table up to date." (`index.ts:108`,
`state-table-reminder.sh:52`) — not `guardrail-hook.md:20-27`'s two-acts wording, which B3 retires;
the opencode-profiler store joins the claude one.

**B9 — structural-rules and test_plugins lose the second-plugin premise (F15).** The sweeps' scope
reads as the one-plugin reality; the test file's companion claim matches.

**B10 — recipes.md's agents paragraph (F16) and the version wording (F24).** The one-line `agents`
recipe stated; `version-has-one-home.md` names `bump-version.sh`; the leaked `{{dot}}` placeholder
in its diagnostic fixed.

**B11 — profiler.ts's floor and field fidelity (F17, F19); the module id documented (F18).**
`SUBAGENT_TOOLS` carries both spellings — the 2.3.0-era `task` and the renamed `subagent` — and the
floor statement stays. `childAgentTypeOf` reads `call.result` into its agent-type lookup
(`profiler.ts:221-229`). The module `id`'s one rule is the registry-read convention the entry
already uses (`opencode-entry.md:21-22`: the id read synchronously from `registry.json`); the rule
lands in `opencode-entry.md`, the modules follow it, and `profiler.ts`'s `PLUGIN_ID` literal
(`:52-53`) goes.

**B12 — hp.py's encode-policy conformance (F23).** `hp.py`'s fit-check and write policies named
and aligned: it measures a line under one encode policy and writes under another (`_json`'s
`ensure_ascii=False`, `hp.py:96`). F20 is retired: `check-wheel.sh:42` has exported
`HOME="${scratch}/home"` since `32fe7da` — its seat's grep could not have run against HEAD.

**B13 — the guardrail's scratch-redirect false positive (F21).** First the failing case: the
`.devpro-temp/` redirect pattern (`echo hi > file 2>&1` writing into the scratch tree) joins
`tests/guardrail_cases.json` with a non-null reason and fails against the current guardrail — its
existing scratch cases (`echo hi > @scratch@/out.txt`, reason `null`) already mark the class
allowed. Then the code: `guardrail.ts`'s scratch free-list and redirect logic (`:15`, `:36-50`)
stops blocking it, and the case passes.

**B14 — the stale listings, citations and the Lows (F22, F28, F29, F30).**
`guide-and-readme.md`'s "holds these things" list and Usage bullet are brought back to the rendered
page's sections they govern (F22); `placeholders.md`'s `--plugin=` and the subsystem map's
`show-profile` entry (F28); the torn-tail/LINE_LIMIT contract sentences (F29) — and their code
half, in scope here: `serialize` (`profiler.ts:312-324`) cannot guarantee `LINE_LIMIT`, fixed
fields over the bound surviving with keys already emptied, so the `name`/`session` clip at the
root is code this item lands; the seat files' Notes tiers as listed (F30).

**Held for user decision (not executed by this package):**
- **F25/F26** — THESIS's building-block table gains the component kind, and the Installed-resources
  row's wording widens past "scripts". The wording is drafted when the user decides, from the seat
  file's alternative shapes (a clause, not a row — or its own kind with a row; widen the row's kinds
  or state the list as examples — `review-prompt-engineer-consistency.md:45-46,72`), and rides the
  next plan's review.
- **F27** — THESIS's adopter-audience sentence and `USER_README.md`'s status: decisions, not fixes;
  they land the same way, with the user's word, in the next plan.

Retired in the prompt-engineer review: **B4** (F6) — the seat's fact misread
`renders-and-copies.md`'s copy-list lines as a mode statement; `opencode-entry.md:7-10`,
`install.py:408-416` and `renders-and-copies.md:71-72` all state the user-level exclusion
consistently at HEAD.

The burndown is expert.

The drafted burndown gets its `devpro-prompt-engineer` usability review, then a revision here,
before its row is `dispatchable`. Execution closes the package in one commit.

Done-line: `just test`, then `just sweep-python`, then `just lint`, then
`just dev-check-design-deltas-applied` (landed: 11), then `just dev-check-links`, then
`just dev-check-plan` — all before the landing acts; the landing commit's tree carries the gate
passing.

## Landing

The plan's landing commit: it deletes `ACTIVE_PLAN_REVIEW.md` (never before — the burndown cites
it until it lands), carries the final status rows with every package `landed`, and its message
says it lands this plan. The plan is deleted with it — a landed plan left in place reads as work
still under way. The closing commits carry the attribution line and bodies, per *Commits and pull
requests*.
