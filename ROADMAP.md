# ROADMAP – devpro

Future intent only. Not part of the contract doc set; not handed to coding dispatches.
A finished item leaves nothing. Do not mark it as done and let it persist. Just remove it.

## Bugs

### A background dispatch's tool call times the spawn, not the child's run

Under opencode 2.4.1, a backgrounded subagent dispatch is recorded — by the capture's
`execute.before`/`execute.after` pair and by the host's own `session_part` storage alike — as a
tool call completed in single-digit milliseconds. The window is the cost of firing the dispatch,
not the child's work: durations cluster at 17–21 ms regardless of how long the child then runs,
and the completed part's own `metadata` carries `"status": "running"` for the child session it
names. Measured 2026-11-25 over twelve background dispatches in one project: tool-call durations
of 2–21 ms against child-session spans of 0.2–10.9 minutes. The hook pair is not wrong about what
it measures — it brackets the tool's execution, and a background dispatch's execution is the
firing. The capture is what presents that window as the dispatch's duration, and that is the
defect.

The ticket is the capture watching the window itself: a background dispatch's call opens on the
launch acknowledgment `execute.after` already receives — the dispatch's intent — and on the child's
own opening events, `session.agent.selected` and `session.model.selected`, which carry the
actualized run: the agent actually running and the model actually selected, where the dispatch side
names only what was asked for. The records' `child_agent_type` reads null today for exactly this
reason. The call closes on the terminal `session.execution.*` event — `succeeded`, `failed`, or
`interrupted` — naming the child's session id. The parent's inbox delivery is not the marker: an
agent that purposefully or erroneously sends no work back still terminates, and termination is the
event's guarantee, delivery's is not. Foreground calls, which no child session carries, keep the
hook pair. Under the claude harness the same dispatch's Task-tool duration already covers the
subagent's run, so the fix is also what makes the two harnesses' records compare.

## Features

### add installed agents directory to claude development skill

The claude session seat does not get path information. Render the relative path
`.claude/skills/devpro/agents/` into SKILL.md, identifying it as the path to the agents files.
This is necessary because some instructions require that the main session read the agent definition
before dispatching. The model usually finds it, but it is an awkward step and we should just
provide the information. This will be a harness-specific overlay.

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

### Legacy project comprehension skill

How a session enters a brownfield project with known and unknown issues, builds familiarity with
it, and begins repair work. The target case is projects whose debt accumulated through ungoverned
agentic development. It follows the development-process skill and should not assume that skill's
workflow is already in place.

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

### A Facts entry's evidence survives its item's commit

B7's Facts cite `.devpro-temp/b4/` as the finding's evidence directory; when B7 landed, the
directory had been cleaned, and the measurement lived only in the plan's own text — a measurement
with no artifact behind it is a claim. Scratch is scratch by design, so the fix is not "keep the
directory": a Facts entry whose evidence is a probe either records the probe's essential output
inline (the command, the runs, the exits) or the rule states where durable evidence goes. Proposed
home: CONVENTIONS, beside the dispatchability rules a Facts entry serves.

### Profiler child rows off by default

Having them on by default is not helpful. The code is also crufty.
It does not have tunable initial values for any of the controls. It has a hard default of
'checked' for the initial value of all checkboxes and only appends parameter values when a checkbox
value is false (again, hard value check)

### Eliminate profiler `repair` and `doctor`

These were one-off tools used while getting the profiler working and was never intended to persist
as user-facing code we drag behind us and test forever.

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

### Install stages through a built wheel

`devpro install` has two staging paths with opposite polarities that must match but nothing makes
them: the checkout path copies the package tree through a denylist (`EXCLUDED_DIRS`,
`EXCLUDED_NAMES`, `EXCLUDED_SUFFIX`, `_shipped()` in `devpro/install.py`), the deployed path copies
wheel content whose allowlist is `pyproject.toml`'s `[tool.setuptools.package-data]`. A built wheel
and `package_copies`' enumeration agreed exactly — 109 files each, both cross-diffs empty — but
that equality is maintained by care, not enforced by anything, and a new file outside the six
globs ships from a checkout and silently misses the wheel consumers install. The denylist's work
is dev-only: in the deployed case every exclusion is a no-op.

The rework: `just agents` builds the wheel and runs the install from the built package — unpacked
to scratch with `PYTHONPATH` pointed at it (zero runtime dependencies make that free),
`PACKAGE_ROOT` resolving into the unpacked copy — and consumers install from site-packages as
today, so both paths stage from wheel content and `.dist-info/RECORD` is the one manifest for
both. The build doubles as a gate: a tree that does not build cannot install (partial — it catches
a malformed package: the version attr's import, missing declared files, pyproject/readme/license
faults; it does not compile modules or validate the entry point, which the test suite owns).
Retires the denylist wholesale — `_shipped`'s third call site (`install.py:413`, the keep/removal
path) needs its own stated rule rather than inheriting the retirement — and the install tests
(`tests/test_devpro_install.py`) reshape around wheel-staged installs.

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

### Every test over 100ms justifies its existence

The suite's full run is ~57-60s for ~1,700 tests, and the weight has accumulated unexamined. A
pass where every test whose setup+call+teardown exceeds 100ms justifies its existence, one of four
verdicts: *earns* (pins a real defect no cheaper test pins, or exercises a real integration no
fixture can stand in for), *cheapens* (rewritten to a fixture so it drops under threshold),
*merges* (duplicate coverage with a sibling), or *goes*. Open for the design: whether a `slow`
marker (the `cold_read` pattern) is a third way for tests that earn their cost but not their place
in the default run; any target for total full-run wall time. First probe, already in
`.devpro-temp/weight-durations.txt`: pytest `--durations=100` over the full default run.

### Tests exist only with a defect they die on

A test protects only where a defect exists that it dies on while the source reads correct to its
author. It must assert behavior, not text.

The pin test — a source literal restated in the test and compared back to the source, an exact
log output check, a polyglot 'is this doing all the things' check against an multi-property 
artifact — is a coverage-mandate fossil: built to satisfy a 100%-coverage metric, not to find a
defect. It is shaped like a test while doing the metric's job. Human projects mass-produced it, the 
training data carries it, and agents reproduce it however often a rule forbids it; prohibition alone
has had modest effect against a prior fed by ten thousand coverage-gaming suites. The same holds for
a change-detector that knows it is one, a hash against a literal. Where detecting change is
load-bearing — generated files, frozen contracts — the mechanism is the regeneration check or an
integration test over the behavior. Coverage that unit tests cannot reasonably reach belongs to the
integration test, never to a pin.

The reason this category of test is an antipattern and anathema - it produces pure friction for
no benefit. It is a suit of armor with fixed joints that requires a plasma cutter and welder
for every change of pose.

Found instances. Two pin the claude family's model assignments, both in `tests/test_devpro.py`:
`test_each_family_pins_the_member_of_every_category` asserts the category map equals a hand-copied
dict of itself; `test_claude_frontmatter_holds_the_field_order_and_spelling`, whose subject is
field order and spelling, carries `model: opus` in its expected tuple. Both photograph owner
tuning: `829f7e7` changed one model entry and the gate ran red until the pins followed. The third
pins presentation text: `tests/test_devpro_profiler.py`'s index test asserts the whole
`table { … }` declaration, so a layout change the presentation layer invites — P3's column
widths — cannot land without either shaping the CSS around the pin or editing it.

Three parts:

1. **Prune the instances.** Keep the form asserts that are contract — order, spelling, quoting,
   required fields. Assert the `model:` line is present, not its value. Rework or retire the
   members mirror.
2. **Commission tests.** Wherever a test can be born, not only in plan packages, it exists only
   with its defect named and the run that fails under that defect shown — the
   `clauses.TEST_PRECONDITION` shape.
3. **Triage a test that fails on unstated behavior, at once.** The work does not state it changes
   this behavior, yet the test fails on it: the test enters the active plan immediately as an
   interrupt — its own row, closed by one commit — and the package that tripped it does not
   proceed until the row closes. Three verdicts: *axe* (the test checks nothing); *isolate* (it
   checks something, too sensitively — refactor it to depend only on its own subject); *acquit*
   (it checks something real and the work broke it — the work is the suspect *or* it was an unavoidable
   side-effect of the required change and the test needs legitimate rework). A report to the owner
   is not the mechanism; the updated plan is.
