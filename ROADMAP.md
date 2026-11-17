# ROADMAP – devpro

Future intent only. Not part of the contract doc set; not handed to coding dispatches.
A finished item leaves nothing. Do not mark it as done and let it persist. Just remove it.

## Features

### Codex CLI harness support

Add the ability to install as a codex plugin. Feasible with gaps
([research](ROADMAP_DESIGNS/CODEX_HARNESS_RESEARCH.md)): delegation to named agents is built in,
with a fixed model per agent. An agent cannot be denied editing or web search, so read-only seats
are unenforced; whether reviewers stay read-only is to be tried first. `AGENTS.md` has no `@`
imports and a 32 KiB cap; agents, skills, hooks and MCP live in separate places, MCP in a shared
`config.toml`; agent bodies are TOML strings; one provider per session, Responses API only.

### opencode model price plugin

Add a small hook plugin that modifies the TUI sidebar showing the current 'spent' figure
to include a line below it showing the active model's $/M input/output tokens.
The cost.input / cost.output rates are available via the model catalog and should be trivial
plug in. If this turns into a side question instead of <= 100 lines of typescript re-evaluate.
possible extension: have it show the prices of all models in use (subagents)

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

### The development skill lacks a rule for a review whose commit range moves under it

A post-plan review cites a commit range; commits landing while the review runs move the range
under it, and the review's scope line rots. The `development` skill's post-plan review section
needs the rule for it: what a reviewer states when its range moves, and what the synthesis does
with the moved part.

## Maintenance

### (STICKY) Periodic load-bearing-ness pruning pass

A pass over definition clauses, across model generations: apply strip-first-observe-patch
(`devpro/family.py`, its module docstring) on a cadence, using behavioral probe sets as the
instrument. Byte-level instruments exist today — `just render-diff` between two render slots, and
the render-property assertions in `tests/test_devpro.py` (ARCHITECTURE.md, Why There Is No
Verification Verb); behavioral ones do not yet.

### Give the kbase router's not-offered branch the plugin reload remedy

Under claude the plugin's `kbase` tools appear after a fresh install only once the plugins are
reloaded. The "A path" branch of the router and `references/installing.md` (both in
`devpro/definitions/kbase.py`) say only to restart or reconnect the server. The `reload_rule` hole
names agents, not tools, so reusing it there would misdirect the model; the remedy needs a harness
hole of its own.

### Verify the opencode guardrail's tool names against the opencode runner

Which tool names reach `execute.before` is unverified: only `patch` is matched, not `apply_patch`;
a `list` tool taking `path` is not handled; the `shell` alias is accepted but never sent. Probe the
runner, accept every name the hook receives, and add a case row for each (`guardrail.ts`
`shellTools` and its tool `switch`; `tests/test_guardrail.py` `_OPENCODE_ONLY_TOOLS`).

### The guardrails hard-code kbase's private record names

The Grep/Glob judgment depends on `nodes.yaml`, `edges.yaml` and `format.yaml` (`guardrail.pl`
`@kb_records`, `guardrail.ts` `kbRecords`), so a record file a later kbase adds passes silently.
Passing a Grep/Glob rooted in `kb-root/` only when its filter's last segment ends in `.md` drops
both lists; it is a behavior change to both scripts and the case table together.

### Mage has no guardrail

`devpro/harnesses/mage.py` sets `guardrail=None` and SPEC `shipped-files.md` says mage ships none,
so a mage install's `.index/` protection rests on kbase's prose instruction alone. Check whether
mage's plugin format carries a hook; if it does not, record the gap in SPEC.

### The cold-read script is unreliable under opencode

`devpro/development-tools/cold-read.sh` runs each read in a fresh directory, and in a directory
where opencode's background service has never run a session, models a provider plugin discovers
(`opencode-models-discovery`) are reported "Model unavailable", even after `opencode models` runs
there; the run fails or falls back to opencode's free models. Whether the composed agent file's
`"*": deny` blocks every tool is therefore unconfirmed by a live run.

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

No recipe runs `shellcheck` over `devtools/scripts/*.sh` or `devpro/development-tools/cold-read.sh`.
