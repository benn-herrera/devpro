# ROADMAP – devpro

Future intent only. Not part of the contract doc set; not handed to coding dispatches.
A finished item leaves nothing. Do not mark it as done and let it persist. Just remove it.

## Bugs

## Features

### A live agents panel on the dashboard

A starting refinement, not a design: the placement, grouping and join below are the requester's
noodlings, and the design's session is welcome to input during the ticket's final design phase —
what stands here is intent, and the design owns the decisions.

The hooks capture activity as it happens and the dashboard reads the stores per request, so the
profiler view can answer what agents are active now: sessions whose latest record is fresh, per
harness, refreshed on the live state the nav's indicator already polls. What "fresh" means, the
panel's surface and its place among the views are the design's questions.

The user's placement: on the kanban board, as a running-agents column. The board's plan columns
are the four states (`PLAN_COLUMNS = STATE_WORDS`), and only four carry cards at a time — and the
modes decide which: planning uses roadmap → drafted → dispatchable (beside the design column),
execution uses design + dispatchable → landed. The roadmap column is not needed during execution —
nothing drags from the roadmap to a running design — so the board renders the columns its mode
uses, and the running-agents column is the fifth in both modes. In execution mode the
in-progress column and the running-agents column are a visibly grouped pair — the agents beside
the tasks their session-id join names, the group on the right of the working columns — with
`landed` still the board's far right. The card's data is the capture's:
the dispatching session, the agent, the model, and the link to the session's page; the join is
the session id the plan's dispatch note carries, written at dispatch time, never inferred from
brief text — agents with no package show unjoined.

### Codex CLI harness support

Add the ability to install as a codex plugin. Feasible with gaps
([research](ROADMAP_DESIGNS/CODEX_HARNESS_RESEARCH.md)): delegation to named agents is built in,
with a fixed model per agent. An agent cannot be denied editing or web search, so read-only seats
are unenforced; whether reviewers stay read-only is to be tried first. `AGENTS.md` has no `@`
imports and a 32 KiB cap; agents, skills, hooks and MCP live in separate places, MCP in a shared
`config.toml`; agent bodies are TOML strings; one provider per session, Responses API only.

### Direct agent model pinning

Expand the model category map assignment scheme to allow specifying a specific model
to a specific agent. Allow globbing for agent names, e.g. *-coder

### Dashboard doc state indicator

When roadmap, design, or plan are not kanban compliant an indication should show on the kanban
board or in the nav area - maybe an 'errors' top level nav

### Dashboard config editor

Settings top nav for letting you edit the supported config fields (some design needed around the globbable keys)

### Change-case analysis process

A skill, or an addition to the `development` skill, that performs change-case analysis in the SAAM
tradition: enumerate plausible future changes to a system, trace each through the design to every
module and contract it touches, and judge the architecture by how far those changes spread. 

Uses:

- periodic re-review of a long-lived project
- evaluation of a brownfield project
- evaluation of a large new architecture. 

Performed by people, the method consumed senior engineering attention and found little where those
engineers had already designed against the failures it detects. Agents make it cheaper to run, and
their designs produce those failures: an agent tends to build each piece as the typical form of
something it resembles, then extend it toward a full implementation of that thing, which the project
does not want, and the weaknesses of the aggregate are the ones change-case analysis exposes.

The process may still be heavy, and it asks for speculation about future change, which agents
do poorly; partially implementing a change case, so the trace runs through code that exists rather than
predicted code, is one possible workaround. Brownfield evaluation overlaps the legacy project comprehension
skill item above, which this would serve rather than absorb. Separate skill or `development` addition
is undecided.

### Legacy project comprehension skill

How a session enters a brownfield project with known and unknown issues, builds familiarity with
it, and begins repair work. The target case is projects whose debt accumulated through ungoverned
agentic development. It follows the development-process skill and should not assume that skill's
workflow is already in place.

### Documentation-only planned workflow

Right now only code-facing changes are handled by the design->plan->burndown workflow.
Doc-only changes for README or project docs are currently only handled by ad-hoc processes
and are not well-represented in the current workflow definition.

### Nested agent fan-outs read as the process, or the detector names them

The one-level dispatch shape the process keeps — every agent-facing brief crossing the
main session's reviewable chain (draft, PE review, revise, dispatch with a named package and a
state cell) — holds while agents are dispatched directly from the main session. Nested fan-outs
(an executor dispatching its own reviewers and workers) can be legitimate exactly when the trace
reads as the process working: the executor drafts its brief, dispatches its own PE review,
revises, and only then dispatches the worker — every step a named agent call the profiler's
capture already records. Two halves, one ticket: a detector that walks the flat profiler stores
for any Agent row whose child session dispatched further agents, reporting one whose trace
carries no review chain beside it (the unreviewed fan-out — today caught by nothing), and the
attribution render showing the depth-2 chain itself, so the board reader sees the process
working rather than that something ran. The index stays one level deep (the flat table of
sessions); the session page is the depth view. Rides after the attribution pass, whose
grouping and child pages this extends.

### Group traces with plans — the operational-context stamp

Sessions recorded by the profiler carry their operational context, so the dashboard can answer
what happened under what set of operational directives and when — before-and-after comparison for
an agent or skill tuning being the use the whole forensic layer serves. The stamp binds three
things to each trace group at capture time: the plan the session worked under; the directives
state in effect — a fingerprint of the installed agent and skill definitions and the agents file,
taken once per session start, so two sessions under the same plan but different definitions are
distinguishable; and the session's time against directive-state changes, so before and after a
tuning change are defined by the change, not inferred. Open decisions for the pass's own design
work: the fingerprint's exact scope and mechanism, how association renders in the dashboard's
index, and whether pre-stamping traces get inference-based association marked as inferred. Rides
after the attribution pass: capability layers land in order, each on the clean foundation the
previous layer left.

## Maintenance

### Bump python req to >=3.11

Simplifies a bunch of code. Probably saves on hook startup time.
Brew installation eliminates the bulk of the 'breadth of usability' problem that <=3.9 was addressing.

### (STICKY) Periodic load-bearing-ness pruning pass

A pass over definition clauses, across model generations: apply strip-first-observe-patch
(`devpro/family.py`, its module docstring) on a cadence, using behavioral probe sets as the
instrument. Byte-level instruments exist today — `just render-diff` between two render slots, and
the render-property assertions in `tests/test_devpro.py` (ARCHITECTURE.md, Why There Is No
Verification Verb); behavioral ones do not yet.

### The cold-read script is unreliable under opencode

`devpro/development-tools/cold-read.sh` runs each read in a fresh directory, and in a directory
where opencode's background service has never run a session, models a provider plugin discovers
(`opencode-models-discovery`) are reported "Model unavailable", even after `opencode models` runs
there; the run fails or falls back to opencode's free models. Whether the composed agent file's
`"*": deny` blocks every tool is therefore unconfirmed by a live run.

### Agents-file block churns under alternating harness installs

Installing one harness after another into the same project rewrites the agents-file block and its
rolling backup on every run — each harness's block names its own reference spelling, global
agents-file path and file-name examples — so the install never reports up to date and rewrites the
whole rendered tree with it. Single-harness installs converge and are pinned by tests
(`tests/test_devpro_install.py`). A fix would render the block byte-identical across harnesses
(plugin references with a space separator, no harness-named paths) or scope the up-to-date decision
per harness.

## Testing

### A shared sentence written out inside a longer paragraph is not checked for double delivery

`tests/test_devpro.py` `_double_paragraphs` compares whole prose units and never splits them into
sentences.

### The double-delivery check fills only the claude family under the claude harness

`tests/test_devpro.py` `_prompts` fills with `_CLAUDE_RENDER`, so family overlay text and other
harnesses' text go unchecked.

### No TypeScript type check

`devpro/harnesses/resources/opencode/index.ts`, `guardrail.ts` and the `tests/*.ts` runners are
never type-checked: there is no `tsconfig` and no recipe. A recipe needs a declaration stub for
`@opencode/plugin`.

### Browser-driven visual verification

The dashboard's served pages need a check that a page not only serves but renders. Firefox's
`--screenshot` cannot provide it: the shot is taken when the document finishes parsing, so nothing
inside the page can be settled first, and no assertion over the PNG's bytes separates a rendered
page from a blank one. A check that can settle the page, inspect its state and then capture needs a
browser driver — Firefox's Remote Agent behind a WebSocket, or an equivalent — which is a
dependency decision of its own. Open for the design work: the driver and its dependency, what the
check asserts, and which pages it covers. Rides with the UX pass, where the visual work lives.
