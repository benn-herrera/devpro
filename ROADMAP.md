# ROADMAP – devpro

Future intent only. Not part of the contract doc set; not handed to coding dispatches.
A finished item leaves nothing. Do not mark it as done and let it persist. Just remove it.

## Bugs

### The zebra's dark stripes are too subtle against the dark background

The landed zebra reads the shared layer's `--column` for both motifs — light `#e7e7eb` reads well,
dark `#232328` sits a shade above the dark background `#18181b`, and the operator reads the rows
as unstriped. The dark tone wants a visibly lighter step than the background's — the executor
names the value against the real dark nav, the mockup's original dark literal (`#191c22`) being
the cautionary tale: darker than the background is the failure mode that hid the odd rows
entirely.

### The board panel's error path raises AttributeError instead of handling

`devpro/dicing/kanban/server.py:140` calls `BaseHTTPRequestHandler.handle_error(...)`, which does
not exist — `handle_error` is a `BaseServer` method, and the call is made from a handler. Every
client error reaching the branch raises `AttributeError` instead of the handler's quiet
client-gone behavior. Found by the UX pass's burndown executor, pre-existing.

### The show-profile skill's verbose statement contradicts the profiler's own leaf

`devpro/definitions/skills/show_profile.py:67-69` says `sh HP tree --verbose` draws "the column
header alone"; the training-skill correction in `harness-profiler.md` states every tool call is
drawn.

### The modules' homes: kanban out of dicing, the checkers into doccheck

The user's direction: the modules' locations correspond to usage **and to the dependency
direction**, and — the boundary's principle, the user's — **kanban consumes a known-good doc set
and serves it up; the module's job is presentation, not validation**. Dicing and validation are
different jobs. The shape: `devpro.dicing.kanban` — the board, the dashboard's panel — becomes
`devpro.kanban`; **`plancheck.py` (the check verbs' implementation) and `planform.py` (the
workflow documents' model they validate against) become `devpro.doccheck`** — the validation
world — whose model `devpro.kanban` consumes. `dicing.cli`'s reverse arrow
(`.kanban.plancheck`) is what blocks the clean arrangement today. The target arrows point one way
only: `devpro.kanban` → `devpro.doccheck` → `devpro.dicing`, `devpro.dashboard` → the front
ends, nothing back; `dicerlib` flattening into `devpro.dicing` is the optional half. The CLI layer follows the same
line: **doccheck owns its commands' argparse and dispatch** (`check-plan`/`check-design`/
`check-roadmap`, lazy, the verb-entry pattern — the invariant test's exemption tuple gains it),
`devpro.dicing.cli` keeps the dicing verbs including `check-links`/`check-tree` (the dicing
operations' own verification), and `devpro/cli.py` composes the fourth `add_verbs` — the house
pattern the profiler and dashboard already follow. The generic verb-registry alternative is the
over-engineering trap the thesis's building-blocks table names; both users of this record
rejected it independently.

### The profiler pages render unstyled under the dashboard's CSP, and their chrome script never runs

The dashboard answers pages with `Content-Security-Policy: default-src 'self'`, which blocks
inline `<style>` blocks and inline scripts. The UX pass moved the profiler pages to *inlined*
shared CSS and an inlined chrome script — so every profiler page the dashboard serves renders
unstyled, the indicator poll never runs and the stop is dead, while the board renders styled (it
links `board.css` externally, which `'self'` allows). Found by rendering the served bytes from
disk: identical bytes render styled from `file://` and unstyled over HTTP. R14's serve-path
divergence diagnosis is corrected: the bytes were always identical — the CSP was eating the style,
invisible to fetch-level tests. The user folds the fix into the next pass (the attribution pass):
the shared layer and `chrome.js` served as same-origin files and linked/scripted externally — the
board's own pattern, no CSP weakening, and the recorded feed direction's "the shared layer is
linked rather than inlined."

## Features

### Codex CLI harness support

Add the ability to install as a codex plugin. Feasible with gaps
([research](ROADMAP_DESIGNS/CODEX_HARNESS_RESEARCH.md)): delegation to named agents is built in,
with a fixed model per agent. An agent cannot be denied editing or web search, so read-only seats
are unenforced; whether reviewers stay read-only is to be tried first. `AGENTS.md` has no `@`
imports and a 32 KiB cap; agents, skills, hooks and MCP live in separate places, MCP in a shared
`config.toml`; agent bodies are TOML strings; one provider per session, Responses API only.

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

### No shell lint

No recipe runs `shellcheck` over `devtools/scripts/*.sh`,
`devpro/harnesses/resources/*/hooks/*.sh`, `devpro/harnesses/resources/claude/profiler/hp.sh` or
`devpro/development-tools/cold-read.sh`. The user directs it: the sources need to be lintable,
shell included — the resources are shipped code.

### The HTML templates' slot fills are never checked

`devpro/profiler/view.html`'s placeholders (`/*STYLE*/`, `<!--LEGEND-->`, the nav and band marks)
and every Python-spliced fragment have no check that a render leaves no placeholder standing: the
UX review found a literal `${0}` in every served session page and a dead `/*STYLE*/` key —
byte-level failures no test of the splices catches, because the splices are what the tests
assert. The check the render needs: a fill that refuses an unknown or unfilled placeholder, and a
test running it over every template — the same refusal the definitions' `filled_text` already
makes.

### The pages assemble by string splices

The dashboard's and profiler's pages are assembled by Python string splices — templates with
placeholder slots filled by `replace`, fragments spliced in order-dependent sequences — and the
per-request serving changes the page under the browser: the chrome (nav, band, CSS, legend) is
spliced in at serve time. The UX review's findings (the dead `/*STYLE*/` key, the load-bearing
splice order, the serve path diverging from the file path, the literal `${0}`) are one failure
class, and the burndown's fixes make the assembly path one and pin it byte-for-byte. The user's
recorded direction beyond it: **dynamic data is data, served through a clean feed that the
served content — including its script — consumes**, the board's pattern the model (`/api/board`
and client-side DOM); the traces index becomes a data feed with client rendering, the session
pages keep their embedded payload as the feed, the shared layer is linked rather than inlined,
and the chrome ships in the page — each view's active state known statically — so the server
stops changing pages under the browser. If server-side assembly survives anywhere after that,
Python's `string.Template` is the candidate step: standard library, strict fill, unknown keys
raising instead of surviving as literals. The whole of it is the design work of the pass that
takes it.

### Browser-driven visual verification

The dashboard's served pages need a check that a page not only serves but renders. Firefox's
`--screenshot` cannot provide it: the shot is taken when the document finishes parsing, so nothing
inside the page can be settled first, and no assertion over the PNG's bytes separates a rendered
page from a blank one. A check that can settle the page, inspect its state and then capture needs a
browser driver — Firefox's Remote Agent behind a WebSocket, or an equivalent — which is a
dependency decision of its own. Open for the design work: the driver and its dependency, what the
check asserts, and which pages it covers. Rides with the UX pass, where the visual work lives.
