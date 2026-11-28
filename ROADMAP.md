# ROADMAP – devpro

Future intent only. Not part of the contract doc set; not handed to coding dispatches.
A finished item leaves nothing. Do not mark it as done and let it persist. Just remove it.

## Bugs

### The install tests' stray-file probe races parallel workers

`tests/install/test_checkout.py` plants a probe file (`zz_probe_stray.txt`) in the real `devpro/`
tree and unlinks it in a `finally`; under parallel pytest workers another test's preflight walk
(`tests/install/test_dry_run.py`) can see the file mid-flight and fail. Observed 2026-11-27: a
docs-change run of `just test-changed` failed `test_dry_run.py[opencode]` with
`FileNotFoundError: devpro/zz_probe_stray.txt`, passed in isolation, and passed on re-run. The
defect is the probe's shared-tree placement, not either test: the probe belongs in an isolated
tree, or the walk reads only the tree it owns. `just test-changed` compounds it under concurrency:
it selects surfaces from *all* uncommitted paths, so co-dispatched packages run each other's
surfaces — a package's "only its own changes" coverage holds only serially.

### test-changed's granularity is the directory, not the test

`TEST_SURFACE_MAP` maps changed files to whole surfaces: any edit under `devpro/` selects the
devpro surface — all ~1700 of the suite's tests — so a one-line text edit in one definition module
pays the full suite, and the dispatch discipline that runs many small packages pays it per
package. The correspondence the target promises (changed files → the tests that exercise the
functions they touch and their outputs) stops at the surface boundary. The concrete case: a
definition-module edit selects the dashboard's 25-second board-panel test, which cannot observe
a definition's text — selection is by directory prefix, and both files share it. The repair:
within-surface selection — map the changed module to the test files that exercise it; the test
tree's layout already names the seams (`tests/render/`, `tests/install/`, `tests/dicing/`,
`tests/profiler/`, the dashboard's board panel against `devpro/kanban/`), and the surface whole
remains the fallback where no finer mapping exists. Iteration speed is the design constraint:
selection granularity is iteration speed, and one directory is no granularity.

### A shared-constant removal mid-run reddens every render gate

The render surface walks every definition module, so a `clauses.py` constant removal that is in
flight — constant deleted, callers not yet reconciled — fails the import of the whole definition
tree and turns every concurrently running item's render gate red, including items scoped to files
the constant never touches. Observed 2026-11-28: B10 (`guide.py`, no shared constant) could not
re-render while B12's `PROJECT_PRECEDENCE` removal was mid-turn in `clauses.py` with three callers
unreconciled; the render surface died at conftest import. The convention's serial sentences order
agents on a shared file, but no gate-scoping rule orders the *gates*, whose blast radius is the
whole tree. Fix: state in CONVENTIONS.md that an item whose done-line walks definitions cannot
pass while any shared constant's removal is mid-flight, and that the reconciliation commit — the
constant's deletion and its callers' unwinding — is one commit, never a half (or batch the
render-walking gate over the run's change set where the owner directs batching).

### A resumed dispatch's store ends in its earlier close

A follow-up to an idle child continues the same session id, and the opencode capture writes no
record of the reopened run: the child's store ends in the `experimental.idle` that closed the
earlier run, and `running_dispatches` (`devpro/profiler/read.py`) reads a dispatch whose store's
tail is a closing idle as closed. Observed 2026-11-27: a devpro-architect follow-up dispatched
from the main session — the dispatch-start record with the child's id present in the main store —
never appeared in the board's agents column, because the child's store had gone silent at its
first run's close. The fix is the killed-child rule's dual: a resumed run writes an opening record
to the child's store (or opens a store of its own), so the running set tracks it. The activity-dots
ticket reads the same running set, so this blocks its whole-document case as well.

The flip side, same root cause, observed 2026-11-27: when the child's store *does* hold records —
a follow-up to a live child — the main store's second `Agent` record opens a second `Dispatch`
with the same id, and `running_dispatches` returns both, so the board draws **two cards for one
live agent** (measured: `duplicated ids: {ses_…: 2}` while one agent ran). The repair is one
mechanism for both faces: the capture models a *run*, not a session — a resumed run opens the
dispatch it resumes (or the reader collapses a history holding one id twice to its last opening,
keeping one running dispatch and its rank in the palette).


## Features

### Antigravity TUI harness support

Add the ability to install as a plugin to Google's antigravity under `.agents/`

### Codex CLI harness support

Add the ability to install as a codex plugin. Feasible with gaps
([research](ROADMAP_DESIGNS/CODEX_HARNESS_RESEARCH.md)): delegation to named agents is built in,
with a fixed model per agent. An agent cannot be denied editing or web search, so read-only seats
are unenforced; whether reviewers stay read-only is to be tried first. `AGENTS.md` has no `@`
imports and a 32 KiB cap; agents, skills, hooks and MCP live in separate places, MCP in a shared
`config.toml`; agent bodies are TOML strings; one provider per session, Responses API only.

### Auto-reload kbase skill after compaction

When kbase skill is installed (and maybe when a kb-root is present?) auto-load the kbase skill
after a compaction.

ideally: we could tell which of development and/or kbase skills were active at the time the compaction
started and then automatically reload it/them.

### Direct agent model pinning

Expand the model category map assignment scheme to allow specifying a specific model
to a specific agent. Allow globbing for agent names, e.g. *-coder

Decided — the category map populates the model pins, and once that is done its job is over: the
pin is the delivered model configuration, and the mechanism for changing it is re-running install
after changing the config file. Reading the config file to dynamically override a model pin is an
entirely new category of behavior with zero language specifying or implying it — out of the
scheme's scope however it expands.

note: my lean is to add a new section `[<provider>.agent-pins]`

### Dashboard doc state indicator

When roadmap, design, or plan are not kanban compliant an indication should show on the kanban
board or in the nav area - maybe an 'errors' top level nav

### Activity dots on the board

- **Column headers for Design and Drafted can also receive dots**
  - When their content (design or plan) is getting dispatched agent attention (review or revision)
  - The dots will appear right justified in the column header cell.
- **Dot coloring** — the dispatch hue the board already uses: one hue per running
  dispatch, the same dot naming the dispatch on its agents-column card and on every package card
  it attends. The hue is the dispatch's place in the running set, not the agent's definition
  `color`.
  - Fully unsaturated colors are to be replaced in the agent color options - they can resemble colors
    for 'disabled element', 'inactive', or look like glyph typos too easily.
  - The dispatch dot's hue on the board is the top color of that agent's data row in the profile view. 
    The palette is already shared (`--c0`…`--c7`), but the derivations differ — the board's hue is
    the dispatch's rank in the running history, the profiler's is per-call context. One derivation carried
    by both surfaces.  
- **The open design question** — the header dots' match rule: what in a running dispatch's note
  or record names whole-document activity (an agent active on a whole design or plan, which
  today appears on no card)
  - ANSWER: for now it is only Drafted and Dispatchable columns
  - Only when the entire ACTIVE_DESIGN or ACTIVE_PLAN is receiving agent attention, which is
  - dispatched prompt engineer review, dispatched architect drafting or revision

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

### The install sources move under devpro/install/

`devpro/install.py`, `devpro/install_base.py` and `devpro/install_target.py` are the only command
sources sitting loose at the package root, and their tests already name the verb's home:
`tests/install/`. Move the three under `devpro/install/` as a package — renaming nothing — and
re-point every importer (the reference search runs at execution). CONVENTIONS' one-way module
split governs the import layer the subsystem map's install entry states: `install_base` imports
no other install module, `preflight` imports `install_base`, `agents_file` imports `install_base`
and its dependents, `install` imports all of them. TEST_SURFACE_MAP needs no new row — the
`devpro/` fallback covers the subtree.

### The TypeScript compiler rides unpinned

`just lint`'s type check runs `bunx tsc`, which takes the latest compiler at run time, so a compiler
release can change what the check reports with no change here. A pin in the root `package.json`,
beside `@opencode/plugin`, would hold it.

currently vetoed because bun gets updated and if we break under a new bun that is a finding.
mind may change about this later.

### The cold-read script is unreliable under opencode

`devpro/development-tools/cold-read.sh` runs each read in a fresh directory, and in a directory
where opencode's background service has never run a session, models a provider plugin discovers
(`opencode-models-discovery`) are reported "Model unavailable", even after `opencode models` runs
there; the run fails or falls back to opencode's free models. Whether the composed agent file's
`"*": deny` blocks every tool is therefore unconfirmed by a live run.

### The precedence span's reading awaits the owner's ruling

`clauses.PROJECT_PRECEDENCE` (`devpro/clauses.py`) opens "The project's own documents modify the
process" and closes "there is no list of qualifying documents and no carve-out." That last phrase
admits two readings, and the owner has not chosen between them. Flagged from the post-plan review
(R3); no wording to the span is drafted here, and `devpro/clauses.py` is untouched.

The two readings of "no list of qualifying documents and no carve-out": either no exception to the
precedence itself — any project document governs where it departs, and the check keeps no whitelist
— or no exceptions anywhere — nothing at all may override the general approach. The second collides
with the project's own leaves that name exceptions. The value-constant exemption is the concrete
one: `PROJECT_DOCS/ARCHITECTURE/rendering/structural-rules.md` states that a `clauses.py` constant
carrying a value rather than a clause is not counted by the shared-paragraph check,
`clauses.VALUE_CONSTANTS` declaring the set, and the same leaf's `EXEMPTIONS` map admits a clause
group member's omission of one plain entry — both exceptions the "no exceptions anywhere" reading
leaves no room for.

The reading is load-bearing on its audience: the span's heading states a narrower rule than its
body, which also governs file headers and settled style, and eleven seats that write no code read
the body's "the code you change" — a rule scoped to code they do not write.

The decision is the owner's — which reading the span states, or a third wording that separates the
two. No rewording is drafted until the ruling; it starts from this record and becomes a work item —
the span's rewording — when it comes.

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
