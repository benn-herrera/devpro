# ROADMAP – devpro

Future intent only. Not part of the contract doc set; not handed to coding dispatches.
A finished item leaves nothing. Do not mark it as done and let it persist. Just remove it.

## Bugs

### The profiler index's controls state dies at every navigation hop

The controls' state lives in the page's URL (`pages.py`'s `sync`/`restore`, landed) and survives a
reload — but nothing carries the query across the page's own links: the index's row links
(`pages.py:1028`) are `PAGE + id` with no query, and the session page's return link is
`return_to=PROFILER_PATH` bare (`pages.py:648`). Index → session → back is the reader's normal
flow, and the state dies at both hops. The fix is two lines — the row link appending
`location.search`, the session page's script echoing its query into the return link — and it
ships blind until the browser-vision loop can see it: the loop's first calibrated use, the fix
verified on the served page before it lands.

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

### Profiler pages should skip namespacing

`devpro-` preceding agent names is just consuming space. We know they are from devpro. 

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

### A shared sentence written out inside a longer paragraph is not checked for double delivery

`tests/test_devpro.py` `_double_paragraphs` compares whole prose units and never splits them into
sentences, so a sentence two outputs of one prompt both carry — each inside its own longer
paragraph — is delivered twice unseen. The fix compares sentences: each prose unit splits into
sentences the way `devtools/dupe_sweep/doc_sentences.py` splits them — hard wrap rejoined before
the split, punctuation-split, the abbreviation caveats that module states — and the repeat count
runs over the prompt's sentences instead of its units. Measured cost: the splitter's own corpus
sweep runs in 0.535s and sentence splitting is linear over the filled texts the check already
walks, so the check's cost stays flat. The false-positive surface is bounded by the check's own
scope — one prompt, being one plugin's agents file and the outputs its `@` lines load — so the
families' deliberate parallel structure across different agents stays out of it, and the shared
scaffolds one prompt co-delivers stay candidates, judged as this check's findings always are. The
sentence check inherits the fill gap the next ticket states: finer granularity checked through
one family and one harness only.

### The double-delivery check fills only the claude family under the claude harness

`tests/test_devpro.py` `_prompts` fills with `_CLAUDE_RENDER`, so family overlay text and other
harnesses' text go unchecked. The sentence check the previous ticket adds raises the stakes:
overlay text and other harnesses escape at sentence granularity, where a shared sentence is small
enough to hide inside a paragraph that differs.

### dupe_sweep reads the string literals

The sentence pass reads docstrings and comments only, so a paragraph hand-copied between two
harness renderers is equal only by care, checked by nothing: the render-level double-delivery
check sees duplication within one prompt, and the sweep never reads a plain string literal. The
calibration instance is the post-plan review's finding 4 — `devpro/harness.py`'s `scratch_rule`
and `devpro/harnesses/mage.py`'s hand-copy, equal by lockstep edits until the constant landed.
The corpus gains the f-string and `str` literals of `devpro/definitions/`, `devpro/harnesses/`
and `devpro/clauses.py` as sentence units, the candidates reporting like the rest: sorted,
byte-stable, advisory. Measured cost: the whole-corpus sweep runs in 0.535s and the literals'
sentences reach machinery that already clusters them. Live instance already in hand: the nine
coder definitions restate the scratch paragraph's location-and-examples sentence that
`NEW_PROJECT_SETUP` dropped the mandate from — delivered twice through the clauses layer, seen
by the post-plan review and invisible to every gate.

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

### The preflight's managed-directory copy drags scratch through every install

RESOLVED — the owner's ruling: `.devpro-temp` is not a managed directory. The install creates it
where missing and that is the whole story; the managed set carries the `.gitignore` file it
writes, and the comparison never reads what the project holds inside scratch. The stopgap's
`symlinks=True` landed at `6429cdc` on the way. Measured before the removal: 270 MB and 22,651
files of stale probe copies made `just agents` take 30 seconds; after the detritus went, the
same run took 0.72.
