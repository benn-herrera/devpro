# ROADMAP – devpro

Future intent only. Not part of the contract doc set; not handed to coding dispatches.
A finished item leaves nothing. Do not mark it as done and let it persist. Just remove it.

## Bugs

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
placeholder slots filled by `replace`, fragments spliced in order-dependent sequences. The UX
review's findings (the dead `/*STYLE*/` key, the load-bearing splice order, the serve path
diverging from the file path, the literal `${0}`) are one failure class, and the burndown's fixes
make the assembly path one and pin it byte-for-byte. If the class keeps biting, the candidate
step is Python's `string.Template` — standard library, strict fill, unknown keys raising instead
of surviving as literals. A dependency decision for the design that takes it, not this pass.

### Browser-driven visual verification

The dashboard's served pages need a check that a page not only serves but renders. Firefox's
`--screenshot` cannot provide it: the shot is taken when the document finishes parsing, so nothing
inside the page can be settled first, and no assertion over the PNG's bytes separates a rendered
page from a blank one. A check that can settle the page, inspect its state and then capture needs a
browser driver — Firefox's Remote Agent behind a WebSocket, or an equivalent — which is a
dependency decision of its own. Open for the design work: the driver and its dependency, what the
check asserts, and which pages it covers. Rides with the UX pass, where the visual work lives.
