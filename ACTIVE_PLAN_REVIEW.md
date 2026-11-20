# Post-plan review — one devpro plugin with optional components; the activity profiler ships as payload

The panel: `python-coder`, `shell-dsl-coder`, `architect`, `prompt-engineer`, `tech-writer` — each
seat independent, the project documents and the design tree in hand, the plan unread. Scope: the
run's changes, `90a3a5f..9f074e3` (P1b's tree-reading byte-check through P4's delta applications).
Each seat's full review sits in the scratch directory (`review-<seat>.md`); this document is the
de-duplicated account — one entry per defect, naming every seat that reported it, grouped by area.
The IDs are the burndown's citations. Severity is the highest across seats, reconciled.

## A. The component selection's render-family paths

**R1 — critical.** The selection's source diverges three ways from SPEC.md, Deployed Surfaces,
Plugins ("`render` takes components from its `--components` alone"):

- `render` reads the settings file's `components` when the flag is absent (`devpro/cli.py:151` →
  `_components_value`, `:127`) — reproduced: a settings file naming `kbase` turns the component on
  in a render with no flag, and the flag's "default none" help is false wherever a settings file
  exists. Seats: architect (critical), python-coder (blocker, with the reproduction, the fix —
  `components = args.components or ""` in the render branch, `_components_value` left to the
  install paths — and the missing pin: a settings file naming `kbase` plus `main(["render", …])`
  must render no `skills/kbase/SKILL.md`).
- The slot install's fixed `--components=kbase` is overridable by a forwarded flag (argparse
  last-wins; `devtools/scripts/render.sh:30-36`, `_render-slot.sh:54`), while `render.sh:32` states
  the slot is rendered with the component on — the deleted `--plugin` refusal was this class's
  guard. Seat: shell-dsl-coder (warning).
- The hidden `harness` verb binds zero components (`devtools/scripts/_harness-value.sh:9-13`), so a
  component-gated definition renders different text in the harness probe than in any install. Seat:
  shell-dsl-coder (first report).

Root cause: the selection was centralized in code but not across the render family's call sites.

## B. The applied contract leaves vs the code and the design

**R2 — critical.** SPEC.md, Deployed Surfaces, Plugins still carries "Installing both plugins in
one place gives duplicate agents under different names." (`plugins.md:80`) — the design delta
prescribed deleting it, and the applied leaf kept it, contradicting the same leaf's
one-install-directory statement and the code (one ROOT per install; mage's constant directory).
Root cause: `check_deltas` verifies a `becomes` block's presence and never a from-block's absence,
so P3 skipped the deletion block whose becomes-text pre-existed in the leaf. Seats: architect
(critical), python-coder (note), prompt-engineer (medium, the stale-vocabulary sweep). Fix: apply
the delta's end state — delete the sentence. Corollary, R7 below.

**R3 — high.** `ARCHITECTURE/rendering/harnesses-and-families.md:80-82` states the member lists are
"validated at import against `discover()`" — the validation runs in `selection()`, called by
`build_render`, as the same leaf says three paragraphs later; the "imports no … definition"
dependency-chain clause is also false. Seats: python-coder (revise), prompt-engineer (medium).

**R4 — revise.** `ARCHITECTURE/install/install-entry.md:6` names `cli._add_plugin` — the function
is now `_add_components`. Seat: python-coder.

**R5 — high.** The component-refusal sentence contradicts itself (`SPEC/deployed-surfaces/
plugins.md:5-8`). Seat: prompt-engineer (high).

**R6 — high.** `PROJECT_DOCS/entry-point.md:65` still ships "the two plugins". Seat:
prompt-engineer (high).

## C. The show-profile skill

**R7 — blocker.** The profile page is written to `${TMPDIR:-/tmp}/harness-profile.html`
(`devpro/definitions/skills/show_profile.py:36`) — the scratch invariant every session loading this
skill also carries (`/tmp` off limits; all scratch in `.devpro-temp/`), and `TMPDIR` is unset on a
stock shell. Seats: prompt-engineer (blocker), python-coder (revise). Fix:
`DONE=.devpro-temp/harness-profile.html`.

**R8 — blocker.** The delivery fallback commits to the user's branch unprompted
(`show_profile.py:45-47`: "otherwise commit it to their branch as
`harness-profile/<session id>.html`") — a read request is not authorization for a repository write,
and the name sits one letter from the git-excluded `.harness-profile/` the same paragraph discusses.
Seat: prompt-engineer (blocker). Fix: end the ladder at "give them the path"; delete the fallback.

## D. The vendored profiler

**R9 — warning.** `hp.sh:13-17`'s nvm branch keeps the lexicographically last directory: with
`v18.20.0` and `v9.11.0` installed, the launcher runs node v9 (reproduced), and because nvm is
searched before Homebrew one old nvm install outranks a current Homebrew node. `hp.js:575` uses `??`,
which no Node below 14 parses, so `capture` exits non-zero on every tool call — the outcome the
header and `claude.py:70-71` promise cannot happen. Seat: shell-dsl-coder (reproduced). Fix:
version-ordered candidates (or a run-check), or state the limit in the header and the profiler leaf.

**R10 — warning.** `hp.sh:1` opens `#!/bin/sh` with no header clause saying why the bash house style
is absent; the reason is real (`claude.py:73` invokes it as `sh`, a hook PATH may lack bash) and
lives only in ARCHITECTURE. Seat: shell-dsl-coder. Fix: one header clause; the CONVENTIONS
exemption for vendored resources is the noted alternative.

## E. `check_deltas` — the devpro-side byte-check

**R11 — high.** The check verifies a `becomes` block's presence and never a from-block's absence:
a design block whose becomes-text pre-exists elsewhere in the leaf reads as applied while its
from-text survives — R2 is the concrete case. Seats: architect (warning), shell-dsl-coder and
prompt-engineer (the same gap surfaced in the design discussions). Fix: the from-side absence check
in the devpro tool; the docdicer RFE carries the cross-project form.

**R12 — warning.** Tree mode drops a section leaf that yields no entry silently: `all 0
becomes-blocks`, exit 0 (`check_deltas.py:204,230-254`; reproduced) — the docstring claims
unparseable entries are named, and `a-delta-application-ends-verified` is this failure with the
witness off. Seat: shell-dsl-coder. Fix: an entryless leaf is one PROBLEM naming the leaf.

**R13 — warning.** Document mode resolves entry links from the invocation directory
(`check_deltas.py:226`) while the docstring and the justfile recipe say "repository root" — run from
a subdirectory, every entry reports a phantom missing leaf (reproduced). Seat: shell-dsl-coder.
Fix: name the base, or pass `PROJECT_ROOT` and resolve from it.

## F. The lifecycle rule's reach

**R14 — high.** A diced *plan*'s lifecycle is stated three incompatible ways:
`SPEC/plan-status-form.md:11-14` (the monolith form), `guide.py:313-314` (the tree), and
`docdicer.py:37-40` — the new rule (P1c) settles designs only. Seat: prompt-engineer. This is the
plan-side gap the skill-text draft flagged as B2; the owner's call is whether the plan side gets
its own rule.

**R15 — high.** The monolith-removal actor is stated two ways: "the session removes it"
(`development.py:204-207`) and "at the user's direction" (`docdicer.py:29-40`). Seat:
prompt-engineer. Fix: one actor, at the general rule.

**R16 — note.** The docdicer skill's undice bullets (`docdicer.py:23-35`) describe the tool's
conversion machinery (a re-dice to a second tree) while D1 states the design's end state — noted
outside P1c's pairs' reach by the plan's own revision. Seat: prompt-engineer (the same family as
R14/R15).

## G. SPEC and skill text mismatches

**R17 — high.** SPEC, Shipped files says the skill names the tool's `init`
(`SPEC/deployed-surfaces/shipped-files.md:102-104`); the skill never does. Seat: prompt-engineer.

**R18 — high.** SPEC, Guide and README says the guide's requirements carry `node`
(`SPEC/guide-and-readme.md:36-38`); the guide's do not (`guide.py:71-76`). Seat: prompt-engineer.

## H. README and the mage surface

**R19 — critical.** No migration step for the retired kbase plugin directory: the previous
release's install wrote `~/Mage/Skills/kbase/` (a full duplicate set — guide, development, docdicer,
agents, `.mcp.json`), the new install writes only `~/Mage/Skills/devpro/` and touches nothing beside
it, and README's Updating section says "the same install line" — a returning user ends with two
plugin directories, two agents files and two `kbase` MCP servers loading side by side (verified by
two install probes; the mage-discovery behaviour is the unverifiable half). Seat: tech-writer
(critical). Fix: the README says to remove a pre-component `~/Mage/Skills/kbase/`, or the install
detects it and the README says so.

**R20 — warning.** README says the install "runs `kbase`" where it only writes `.mcp.json`
(README.md:107-108, two probes). Seat: tech-writer.

**R21 — warning.** The mage quick start shows only `--components=kbase` and never says the
component is optional, diverging from the guide's plain `--harness=mage`. Seat: tech-writer.

**R22 — warning.** The requirements list omits node 18+ for the claude profiler, which captures
nothing without it. Seat: tech-writer.

**R23 — note.** The credit carries no licence though the vendored source is MIT. Seat:
tech-writer. (Settled separately: "our own activity profiler" is the line's only first person and is
the design's verbatim text — no change.)

## I. The devtools scripts

**R24 — warning.** `render-agents-file.sh:2-6` still spells `PLUGIN` in its version-skew header
("HARNESS OUT [PLUGIN]", "is read") while the positional was removed and nothing reads it — a newer
caller passing a third argument is silently ignored. Seat: shell-dsl-coder. Fix: reword to
`HARNESS OUT` and refuse a third argument.

**R25 — warning.** `check-wheel.sh:57` asserts the mage manifest at `devpro/CLAUDE.md`, which the
flip moved — the assertion passes for the wrong reason. Seat: shell-dsl-coder. Fix: assert the path
the manifest lands at.

**R26 — note cluster.** `RENDER-FLAGS.txt` records `"$@"` rather than the applied args (0 bytes for
a defaulted slot); `_render-slot.sh` reads only `--harness=NAME` (`--harness NAME` is forwarded but
unread — pre-existing); `_render-slot.sh:40` uses bare `rm -rf` (pre-existing); `render.sh:33-36`'s
slot-contents comment says "the kb include lines" plural where mage writes none. Seat:
shell-dsl-coder.

## J. Code-level notes

**R27 — note cluster.** The components precedence rule is written twice (`cli.py:127`,
`install.py:714`); `resolve_install_target`'s `plugin` parameter takes one value at every call site;
`render-agents-file` accepts a `--components` that cannot matter; the selection field and params are
named `plugin` while typed `Components`; turning the component off leaves `.mcp.json`, `kb-tools/`
and the `kb` include line with no report; two tests pin the same refusal; `_OPTIONAL_MEMBERS` is a
snapshot while `COMPONENTS` is read live. Seat: python-coder.

## K. Document-level notes

**R28 — note.** `ARCHITECTURE/repo-layout.md:18-21` carries a tree listing broken across four
physical lines — the one structure failure in the doc set. Seat: prompt-engineer.

**R29 — note.** `devpro.definition._check_body` refuses a Definition body with a trailing newline —
a trap that cost P2 a run; `PROJECT_DOCS/CONVENTIONS/adding-definitions/` is where the clause
belongs. Seat: python-coder (P2's report).

**R30 — note.** The `justfile` recipe claim that every copied file's `!INSTALLED!` banner is masked
holds only for `#`-comment banners (the HTML banner is a comment, the shell's is a comment, but the
claim's universal shape outruns it). Seat: shell-dsl-coder.

## Limits

Unverified by the panel, with probes named in the seat files: the profiler end-to-end run;
`show-profile` under opencode and mage; a live diced-design-to-landing session; Mage's discovery of
a sibling directory; THESIS completeness beyond grep. The from-side absence check and the
both-present enforcement are the docdicer RFE's (`docdicer/RFE_CHECK_DELTAS.md`) — the devpro-side
half of the from-side check is R11.
