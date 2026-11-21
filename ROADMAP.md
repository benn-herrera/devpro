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

### Group traces with plans

Sessions recorded by the profiler become groupable by the plan they worked under, so the
dashboard's trace index shows which work a session served. The association mechanism is an open
decision — capture-time stamping of the plan's identity (robust, no retroactive coverage),
render-time inference from the plan file's history (covers old traces, misattributes silently),
or stamp going forward with inference marked as inferred for old traces. Rides after the
attribution pass: capability layers land in order, each on the clean foundation the previous
layer left.

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
`devpro/harnesses/resources/*/hooks/*.sh` or `devpro/development-tools/cold-read.sh`.
