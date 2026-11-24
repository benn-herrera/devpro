# ROADMAP – devpro

Future intent only. Not part of the contract doc set; not handed to coding dispatches.
A finished item leaves nothing. Do not mark it as done and let it persist. Just remove it.

## Bugs

## Features

### A child session's page names itself for the agent and wears that call's color

Owner's notes: a child session's page top context is named `main`, not for the agent whose call
created it, and it carries no color. It should (1) be named for the agent — the dispatch record
already names it, and the parent's index row shows the same name — and (2) wear the color that
agent call carries in the parent context, so the child page reads as *that* agent's session at a
glance. Open for the design: where the binding lives (the dispatch record's name and the call's
color at capture, or a join at read time); what a page shows when the agent name is absent or the
call's color is not in the palette.

### The profiler's primary color theme is devpro green, not claude orange

Owner's note: the primary color theme should not be claude orange — it should be devpro green.
The harness dots keep their per-harness colors; the theme in question is the profiler's own accent
(harnesses' orange reads as claude's brand, not devpro's). Open for the design: which surfaces
carry the primary accent and where its token lives, so the change is one home's edit rather than a
sweep.

### The profiler surfaces the model name each session and agent used

Owner's note: the records already carry the model name used in each session and agent — the
capture stores it — and the profiler surfaces it nowhere, neither on the index nor on a session
page. Open for the design: where it surfaces (an index column, the session page's band or detail,
per-agent rows); what "the model" means for a session whose records name several (a session's
own model beside each dispatched agent's); and how it reads beside the dispatched-agents count
the index already renders. The capture's records are the data source; no capture changes are
implied.

### The index spends less width on the dispatched-agents column and the child-row prefix

Owner's notes from live use (screenshot in session, 2026-11-24): the first-to-last column needs to
be widened — its dates and times are the wrapping the reader sees, and they belong on one line;
the dispatched-agents column can be narrowed further to fund that width (the cells read
`102 agents` and the column still takes more width than its content needs); and the child row's
`↳ child —` prefix before the agent name can be eliminated to save horizontal space — the child
row's indent and tone already signal what it is, and the session id beside it carries the identity.
Open for the design: what marks a child row once the prefix is gone (indent alone, or the row's
tone carrying it); whether the agents cell or its column definition narrows, and how the freed
width reaches first-to-last (column definition, not just cell text).

### Group traces with plans — the operational-context stamp

Sessions recorded by the profiler carry their operational context, so the dashboard can answer
what happened under what set of operational directives and when — before-and-after comparison for
an agent or skill tuning being the use the whole forensic layer serves. The stamp binds three
things to each trace group at capture time: the plan the session worked under; the directives
state in effect — a fingerprint of the installed agent and skill definitions and the agents file,
taken once per session start, so two sessions under the same plan but different definitions are
distinguishable; and the session's start time, which orders the fingerprint transitions: before
and after a tuning change are defined by observed transitions in session order — the sessions
through the last carrying the old fingerprint are before it, those from the first carrying the new
one are after it — the change moment bounded by the sessions either side, not exact. A change no
session straddles is invisible and no defect: the sessions are the only observers of directive
state, and the comparison needs the partition, not the moment. Open decisions for the pass's own
design work: the fingerprint's exact scope and mechanism, how association renders in the
dashboard's index, and whether pre-stamping traces get inference-based association marked as
inferred. Rides after the attribution pass: capability layers land in order, each on the clean
foundation the previous layer left.

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

### Detect a re-install from embedded devpro

Right now ./<harness-dir>.../devpro.sh install . fails because it detects the self-overwrite.
what it *should* do is reinstall everything but the embedded copy (just detect and skip).
this allows for edits to ~/.config/devpro/devpro.cfg to take effect without potentially changing
devpro's installed version by using the system copy.

### Consider changing devpro config format

It's currently .cfg but .toml allows for nesting (which we are faking with <harness>-model-map group)
The upgrade to python 3.11 makes toml available without a dependency.

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

### Every test over 100ms justifies its existence

The suite's full run is ~57-60s for ~1,700 tests, and the weight has accumulated unexamined. A
pass where every test whose setup+call+teardown exceeds 100ms justifies its existence, one of four
verdicts: *earns* (pins a real defect no cheaper test pins, or exercises a real integration no
fixture can stand in for), *cheapens* (rewritten to a fixture so it drops under threshold),
*merges* (duplicate coverage with a sibling), or *goes*. Open for the design: whether a `slow`
marker (the `cold_read` pattern) is a third way for tests that earn their cost but not their place
in the default run; any target for total full-run wall time. First probe, already in
`.devpro-temp/weight-durations.txt`: pytest `--durations=100` over the full default run.

### Legacy project comprehension skill

How a session enters a brownfield project with known and unknown issues, builds familiarity with
it, and begins repair work. The target case is projects whose debt accumulated through ungoverned
agentic development. It follows the development-process skill and should not assume that skill's
workflow is already in place.

### The burndown is a section with a drafting ticket, not one package

A plan's post-plan burndown is today one package whose drafted items hide beneath it: one row
saying `in progress` conceals several dispatches, and no item carries its own rating, so the
mechanical ones cannot visibly step down. The change, to the `development` skill's source
(`devpro/definitions/skills/development.py`, *Post-plan review*): at plan authoring the burndown is
an `## Post-plan burndown` section holding exactly one ticket — the drafting ticket — whose job is
to fill out the section once the plan's main pass is complete and the review document has landed:
converting the review's findings into tickets under the section, one per root-cause group, each
with its own ID, row, rating and one-commit close, moving through the states individually. The
plan-status form already permits packages at any heading level, so no SPEC change is expected —
the design confirms or corrects that. The section dies when its last ticket lands.

The use beyond board honesty: individual items quantify post-process work — burndown tickets per
plan — giving the before-and-after data tuning the process reads. Count is sensitive to grouping
granularity, so the metric is paired: findings per review document (the denominator) against
burndown tickets per plan (the numerator). Both numbers fall out of bookkeeping the process already
keeps; the operational-context stamp supplies the before/after boundary.

Next up on the agenda: a solo plan, taken as soon as the current plan lands — its design starts
from this ticket and the quantification use.

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

## Maintenance

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

### The TypeScript compiler rides unpinned

`just lint`'s type check runs `bunx tsc`, which takes the latest compiler at run time, so a compiler
release can change what the check reports with no change here. A pin in the root `package.json`,
beside `@opencode/plugin`, would hold it.

currently vetoed because bun gets updated and if we break under a new bun that is a finding.
mind may change about this later.

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

### Browser-driven visual verification

The dashboard's served pages need a check that a page not only serves but renders. Firefox's
`--screenshot` cannot provide it: the shot is taken when the document finishes parsing, so nothing
inside the page can be settled first, and no assertion over the PNG's bytes separates a rendered
page from a blank one.

Decided — the driver and its dependency: Puppeteer driving the system's Firefox over WebDriver
BiDi, the binary from `PATH` (`executablePath`), Puppeteer owning the plumbing — throwaway profile,
flags, the BiDi handshake — no browser download, no second Firefox. The lightest way first: if the
combination fails or shows a hole the check cannot live with, the upgrade is Puppeteer's own
hermetic Firefox build. BiDi is the standard protocol, so the system binary's version skew surfaces
as `UnsupportedOperation` — named, not silent.

Still open for the design work: what the check asserts and which pages it covers. Screenshot-byte
comparison is out of it — a pin on pixels is the photograph antipattern, the class of test this
project eliminates. The primary first use is the development loop, not a hard test: the model
working on the pages sees what it rendered and iterates toward what it intends, and the
assertion set distills second, from what that loop shows matters. Rides with the UX
pass, where the visual work lives.

### The double-delivery check fills only the claude family under the claude harness

`tests/test_devpro.py` `_prompts` fills with `_CLAUDE_RENDER`, so family overlay text and other
harnesses' text go unchecked. The sentence check the previous ticket adds raises the stakes:
overlay text and other harnesses escape at sentence granularity, where a shared sentence is small
enough to hide inside a paragraph that differs.
