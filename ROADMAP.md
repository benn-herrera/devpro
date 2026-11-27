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
modes decide which: planning uses roadmap, design, drafted, dispatchable (beside the design column),
execution uses design, dispatchable, in-progress, landed. The roadmap column is not needed during execution —
nothing drags from the roadmap to a running design — so the board renders the columns its mode
uses, and the running-agents column is the fifth in both modes. In execution mode the
in-progress column and the running-agents column are a visibly grouped pair — the agents beside
the tasks their session-id join names, the group on the right of the working columns — with
`landed` still the board's far right. The card's data is the capture's:
the dispatching session, the agent, the model, and the link to the session's page; the join is
the session id the plan's dispatch note carries, written at dispatch time, never inferred from
brief text — agents with no package show unjoined.

UPDATE:

- live use showed that 'drafted' is useful for discovered issues mid-plan that belong
in the current sprint. 'roadmap' still goes away during execution, though, leaving room for
the agents column.

- additionally, the split progress/agents column view isn't going to work.
  proposal b: active agents column with different colors for each active agent/model listed
  and then colored dots on the cards when a model is acting on it.
  i.e. when a drafted item is getting a PE review, there's a colored dot in the corner of the
  ticket that matches the running PE color. when getting revised, the revising agent's color
  is used. same treatment for tickets in the 'in progress' column. the reason the previous 2-column
  proposal doesn't work is that agents can be working on tickets in more columns than just 'in-progress'

### Antigravity TUI harness support

Add the ability to install as a plugin to Google's antigravity under `.agents/`

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

Decided — the category map populates the model pins, and once that is done its job is over: the
pin is the delivered model configuration, and the mechanism for changing it is re-running install
after changing the config file. Reading the config file to dynamically override a model pin is an
entirely new category of behavior with zero language specifying or implying it — out of the
scheme's scope however it expands.

### Dashboard doc state indicator

When roadmap, design, or plan are not kanban compliant an indication should show on the kanban
board or in the nav area - maybe an 'errors' top level nav

### Auto-reload devpro development skill after compaction

compaction hook to record a marker, context hook to inject the `@devpro-development` command.
note: only necessary for opencode. claude code automatically reloads active skills after a compaction (verify that)

### An introduction to the process

The development skill's references serve an agent mid-process; a person arriving cold asks what
the dealio is, how to use it, and why it is shaped as it is, and no leaf answers them. Add
`references/introduction.md` to the development skill: what the process is for, the route through
its references, and the why its Purpose lines only hint at — the process encodes the occasions
(the periodic review's count, the seats, the burndown) while the discipline that acts on them
stays human: the willingness to spend a dispatch proving one's own work wrong, and the restraint
to fix what that proves before the next feature. The skill definition's `## Route` table
(`devpro/definitions/skills/development.py`) gains the row at its top — the newcomer is routed
before any other row is reached — joining the references the table lists.

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

## Maintenance

### The periodic review's panel gains the test-suite audit seat

The next periodic review (and each after, while the finding holds) staffs one more seat: a
test-suite audit. Three lenses, in the user's framing:

The seat is test-driven, not yet a fixture: this review's run was its first, and its full work —
the inventory and the behavioral probes below — runs once more on this repository after the
review's burndown lands and the repository is quiescent. The `development` skill's *Periodic
review* section gains the seat as its default panel's ninth only if that drive earns it; until
the drive is ruled on, the seat is chartered here and named nowhere in the definition.

- **Shotgun versus deliberate.** Sort parametrized and generated tests by whether each case could
  fail differently — a property or oracle stated, counterexamples minimized — or whether the family
  iterates an input space proving one trivial fact. Collapse the shotgun kind to the envelope of
  distinct failure modes; the count drops as a side effect, never as a goal.
- **Tier balance.** Classify the suite by what it exercises — unit, contract/integration,
  end-to-end — and read the unit layer's marginal tests against what the integration tier holds.
  Reading rule: past roughly eighty percent unit coverage, the marginal tests are prime suspects
  for form-over-function; where no coverage metric exists, distinguish organic bloat from
  metric-chasing.
- **Gap by mechanism.** A coverage gap is never the finding by itself; name the mechanism the gap
  needs — unit for algorithmic behavior, integration or contract instruments for wiring and seams,
  structural comparison and behavioral probes for structural logic — and propose that mechanism.
- **Deliverable, named ahead of the review:** a reorganization item for the accumulated test
  monoliths — `tests/test_devpro_profiler.py`-scale files — collecting tests by subject and splitting
  along the package's seams, the layout `tests/dashboard/` and `tests/dicing/` already model. The
  review's burndown drafts the split from the audit's inventory, with no behavior change riding it.

### (STICKY) Periodic load-bearing-ness pruning pass

A pass over definition clauses, across model generations: apply strip-first-observe-patch
(`devpro/family.py`, its module docstring) on a cadence, using behavioral probe sets as the
instrument. Byte-level instruments exist today — `just render-diff` between two render slots, and
the render-property assertions in `tests/test_devpro.py` (ARCHITECTURE.md, Why There Is No
Verification Verb); behavioral ones do not yet.

### Git Flow light: publish the rework history

Move development from squash-style landing to Git Flow light — work branches with granular
history, landed by merge commit, branches public — because the rework record is data: the
catch-rate and escape metrics for the review process read it, and public rework history is part
of the transparency the project exercises. Tonight's losses motivate it: a squashed correction, a
README amend, and a recalled branch left only reflog archaeology where the measurement wants plain
history.

The process consequence: the "one commit closes a package" rule was written for squash landing —
its purpose survives (a package's row names the commit that carries its work; a merge commit can
be that commit), its form changes, and the rule lives in the process skill and the agent
definitions, so the change is a definitions-and-CONVENTIONS amendment, not a habit.

### The cold-read script is unreliable under opencode

`devpro/development-tools/cold-read.sh` runs each read in a fresh directory, and in a directory
where opencode's background service has never run a session, models a provider plugin discovers
(`opencode-models-discovery`) are reported "Model unavailable", even after `opencode models` runs
there; the run fails or falls back to opencode's free models. Whether the composed agent file's
`"*": deny` blocks every tool is therefore unconfirmed by a live run.

### The TypeScript compiler rides unpinned

`just lint`'s type check runs `bunx tsc`, which takes the latest compiler at run time, so a compiler
release can change what the check reports with no change here. A pin in the root `package.json`,
beside `@opencode/plugin`, would hold it.

currently vetoed because bun gets updated and if we break under a new bun that is a finding.
mind may change about this later.

### The install's fully-owned wipe semantics

The user's ruling: devpro is exclusively a harness plugin, and a harness plugin's directory is
100% its own — the loose-files-into-shared-locations era is history. The install therefore
replaces the plugin directory wholesale: wipe the tree, copy fresh, no banner recognition, no
foreign-file refusal, no stale list, no prune's per-file judgment, no `.bak` carve-out, no
`RETIRED_*` inventory — the retirement question dissolves with the wipe. Two exceptions stand:
the re-entry run passes over the copy it runs from (and keeps its symlinked-copy refusal), and
the shared files outside the directory keep their handling — the agents file's block and the
hook entries in the settings file. The managed-directories notion is past the Pieces table's
"is not" barrier: the thesis's entry for it names the wipe.

The work is a design before it is a plan — SPEC's write-safety and deployed-surfaces, the
THESIS Pieces entry, ARCHITECTURE's install leaves and the `install.py` rewrite — drafted once
the periodic review's burndown lands and the repository is quiescent. B16's document-only
carve-out retirement is subsumed by the write-safety rewrite either way.

## Testing

### The opencode capture's host-shape reads are verified by live dispatch alone

`devpro/harnesses/resources/opencode/profiler.ts` reads a dispatch's child session from three places
in the result — `result.metadata.sessionID` on 2.3.0, `result.output.sessionID` on 2.3.2 and the
result's top-level `sessionID` on 2.4.1 — and the code's own comment calls these reads observed,
shipped behavior: the host's published declarations are narrower than what its runtime reports.
Since the capture's stand-in runner was retired (`f1c226a`), that observation has been the reads'
only evidence, and nothing holds it. `tests/profiler_contract_runner.ts` drives the record
construction over the three shapes, but its shapes are inputs it authors: it pins what the capture
builds from a given result and says nothing about what the host reports, so a release that moves a
read's location, or drops it, leaves the capture failing live with the runner green.

The ticket is the live evidence, restored as a recurring understanding rather than a one-time record:
an opencode dispatch on each covered release that fires a subagent call, the child's id observed in
the result the hook receives, and the observation dated and recorded where the harness-profiler
leaf's account of the capture cites it. Which of the three the current releases still report, and
whether the floor's range still needs all three, is what the dispatch answers.

### The double-delivery check fills only the claude family under the claude harness

`tests/test_devpro.py` `_prompts` fills with `_CLAUDE_RENDER`, so family overlay text and other
harnesses' text go unchecked. The sentence check the previous ticket adds raises the stakes:
overlay text and other harnesses escape at sentence granularity, where a shared sentence is small
enough to hide inside a paragraph that differs.
