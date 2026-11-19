# Active plan — the session nudge and the kanban wording

From [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), accepted in final form and undiced. Every package is
**shipped**. One commit closes each package; the checkpoint gate — `just test`, then
`just sweep-python` ([The gates](PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md)) —
runs once before each closing commit. A design entry's application ends with the byte-check run as
`just check-deltas`, the runner target P0 lands; [A delta application ends verified](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md)
specifies what it checks. A package whose work changes rendered output re-takes the reference slots
at its end ([Reference retakes follow acceptance](PROJECT_DOCS/CONVENTIONS/planning-and-execution/reference-retakes-follow-acceptance.md));
the slots are gitignored, so a retake is procedure, not commit content.

The design is undiced, so each entry below is cited by its heading's `#anchor` in
`ACTIVE_DESIGN.md`. Entries under `## SPEC delta` and `## ARCHITECTURE delta` are applied to their
targets verbatim; their passage pairs carry no relative links, so nothing rebases.

Facts carried in the packages cite `file:line` in this repository, or `file:line` in
`/Users/agent-user/projects/opencode` at the tag named, with the command that re-checks each.
Out of scope: the `harness-profiler plugins` ticket in ROADMAP.md's Features category
(ROADMAP.md:10) is future work, not this plan.

Sequencing: P0 first. P1 applies the Shipped-files entry, running the byte-check P0 lands. P2, P3
and P4 follow serially in the shared tree — P3 and P4 act on statements P1 lands, and P2's entries
are its own. P5 after P4; P6 after P5.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P0 | landed | mechanical | the `check-deltas` runner target and its conventions leaf |
| P1 | landed | mechanical | SPEC delta's Shipped-files entry applied |
| P2 | dispatchable | expert | board offer wording: SPEC delta's Guide-and-README entry, ARCH delta's Subsystem-Map entry, both skill definitions |
| P3 | dispatchable | expert | claude plan-state reminder: ARCH delta's Guardrail-hook entry, Code delta's Guardrail-hook entry, reminder script, registration, probe gate |
| P4 | dispatchable | expert | opencode plan-state reminder: ARCH delta's Opencode-entry entry, Code delta's Opencode-entry entry, plugin entry, entry runner and test |
| P5 | dispatchable | expert | Post-plan review |
| P6 | drafted | expert | Post-plan burndown |

## P0 — The delta byte-check target

Lands the runner target the byte-check runs as, and names it where the byte-check is specified.
This is a process mechanism the plan carries, not a design delta.

Scope:

- `devtools/check_deltas.py`, new: reads a design's `## SPEC delta`, `## ARCHITECTURE delta` and
  `## Code delta` sections; for each `###` entry heading, the target leaf is the path in the
  heading's link; for each fenced block that follows a `becomes` line, it checks the block's text
  occurs byte-exact in that leaf, and exits non-zero naming each miss. The pattern is the
  repository's devtools modules run from the justfile (`just sweep-python` at justfile:215,
  `just clause-join-sites` at justfile:262, both `python3 -m devtools.<name>`).
- `justfile`: the `check-deltas [design]` recipe, default `ACTIVE_DESIGN.md`, invoking the module.
- `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`: names the
  target as the check it specifies.

Done-line: `just check-deltas` — at this package's end its report names the design's not-yet-applied
becomes blocks and nothing malformed (an unparseable entry or a missing leaf is the defect the run
exists to catch), and the run stays non-zero until P1–P4 land, which is the breakage this plan
names and they resolve — then `just check-links`. One commit.

## P1 — Apply the SPEC delta's Shipped-files entry

Applies [SPEC.md, Deployed Surfaces, Shipped files](ACTIVE_DESIGN.md#specmd-deployed-surfaces-shipped-files)
verbatim to `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`.

Scope: that one leaf. Its three passage pairs land at, verified this session by reading the leaf:

- line 76: `A **harness resource** is a file a harness ships, such as a guardrail script or opencode's plugin entry,`
  — the span sits mid-line, ending before `, copied as it stands and never rendered.`, which stays;
- line 88: `` `<install-dir>/guardrail.ts`, and claude's at `<install-dir>/hooks/guardrail.pl` (mage ships none) `` —
  the span sits mid-line, ending before the `:` that continues `in the install directory`;
- line 95: `Opencode loads the plugin directory and registers its agents, skills, commands and, where
  `kbase` ships, the `kbase` MCP server under the registry's ids.` — the span starts on line 94 and
  ends mid-line; the sentence after (`A change to the install directory …`) stays.

The entry does not touch the sentence `The plugin entry is written for opencode v2.2.6 and is the
same file for both plugins` at shipped-files.md:97–99; it stays (see P4's note).

Done-line: `just check-deltas`, then `just check-links`. One commit.

## P2 — The board offer wording

Applies [SPEC.md, Guide and README](ACTIVE_DESIGN.md#specmd-guide-and-readme) verbatim to
`PROJECT_DOCS/SPEC/guide-and-readme.md` (target passage at lines 76–78, verified this session),
and [ARCHITECTURE.md, Subsystem Map](ACTIVE_DESIGN.md#architecturemd-subsystem-map) verbatim to
`PROJECT_DOCS/ARCHITECTURE/subsystem-map.md` — its replaced span is line 57, ending
`neither has a recipe of its`; line 58 begins `own, and each runs through …` and stays. Then
implements [ARCHITECTURE.md, Subsystem Map](ACTIVE_DESIGN.md#architecturemd-subsystem-map-1):

- `devpro/definitions/skills/docdicer.py`, the `kanban` paragraph (lines 63–65) — today it reads
  `give the user the command to run rather than running it yourself`;
- `devpro/definitions/skills/guide.py`, the board bullet (lines 454–456) — today it reads
  `The user runs it; the session gives the command and does not run it`.

Each site carries the offer-to-run wording in its own words: the session offers to run the board
as a background process, or hands the command line, the user choosing — held to the applied
Subsystem Map statement and the applied Guide and README board item. The two sites must not carry
a byte-shared paragraph: [Shared text is one constant](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/shared-text-is-one-constant.md)
has `just test` fail on a paragraph two rendered definitions carry; should the wording genuinely
want to be identical, it becomes one constant in `devpro/clauses.py` instead.

No test pins the current text: `git grep -ln 'kanban' -- tests/` and
`git grep -ln 'The board\|live board' -- tests/` both return no files (run this session).

Done-line: `just test devpro`, then `just check-deltas`, then `just check-links`. Re-takes the
reference slots at its end (rendered skill bodies change). One commit.

## P3 — The claude plan-state reminder

Applies [ARCHITECTURE.md, Install, Guardrail hook](ACTIVE_DESIGN.md#architecturemd-install-guardrail-hook)
verbatim to `PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md` (target passage at lines 17–19,
verified this session), and implements
[ARCHITECTURE.md, Install, Guardrail hook](ACTIVE_DESIGN.md#architecturemd-install-guardrail-hook-1):

- `devpro/harnesses/resources/claude/hooks/state-table-reminder.sh`, new. It reads
  `ACTIVE_PLAN.md` or `ACTIVE_DESIGN.md` at the project root and emits a one-sentence
  `hookSpecificOutput.additionalContext` reminder to update the plan's status table; where neither
  file exists it emits nothing. It ships automatically: the resources walk
  (`devpro/install.py:180–193`, `harness_resource_copies`) copies every file under
  `resources/<harness>/`, for both plugins — the harness is shared (`devpro/plugins/devpro.py`
  excludes only `kbase`; `devpro/plugins/kbase.py` includes `guide`, `development`, `docdicer`),
  and mage ships none (`devpro/harnesses/resources/` holds only `claude/` and `opencode/`,
  verified this session). It carries the installed banner —
  `test_every_shipped_resource_carries_the_header_its_reinstall_needs`
  (tests/test_devpro_install.py:1686–1699) enforces one on every shipped resource — and mode
  100755 like `guardrail.pl` (`git ls-files -s devpro/harnesses/resources/claude/hooks/guardrail.pl`
  → `100755`), which the install preserves (`devpro/install.py:539–542`, `copymode`). It needs
  nothing beyond what a claude hook process has: POSIX `sh` and the Claude Code environment, no
  new interpreter or tool dependency.
- `devpro/harnesses/claude.py`, `_guardrail_registration` (lines 57–64): the two reminder entries
  go beside the guardrail's in the rendered `hooks/hooks.json`. Matchers, from the claude hook
  contract (code.claude.com/docs/en/hooks, read this session): dispatch is `PreToolUse` on
  `Agent` (the subagent tool, named `Agent` since v2.1.63); completion is `Agent|SubagentHandback`
  on `PostToolUse` — `SubagentStop`'s additionalContext reaches the subagent, not the parent. Both
  entries run the same script.
- `devpro/install.py`, the probe gate (lines 486–495): today the registration renders only where
  the probe passes (`harness_files.append(guardrail.registration)` at :492 sits in the probe's
  `else`). The reminder entries are ungated, so the registration renders on every claude install;
  the guardrail's entry stays probe-gated — on a probe failure the registration holds the two
  reminder entries only, and the guardrail script is neither shipped nor registered (unchanged
  SPEC.md rule, shipped-files.md:137–138).

Tests pinning the changed behavior, updated in scope (each fails on the current code — the entry
count of one, and no registration under a failed probe — which is the defect the updates close):

- tests/test_devpro_install.py:439–449, `test_a_fresh_claude_install_ships_the_guardrail_and_registers_it_in_the_plugin`:
  `len(registration["hooks"]["PreToolUse"]) == 1` at :449 becomes two, with one `PostToolUse`
  entry beside them (the registration's top-level shape — one `hooks` key — stands).
- tests/test_devpro_install.py:1718–1731, `test_a_failed_probe_installs_everything_else_and_neither_ships_nor_registers_the_hook`:
  asserts `not (_claude_plugin(root) / _REGISTRATION).exists()`; now the registration exists,
  holding only the reminder entries.
- tests/test_devpro_install.py:1733–1747, `test_a_failed_probe_leaves_every_earlier_script_and_registration_and_names_them`:
  pins the registration left byte-identical; a harness-rendered file is replaced whole
  (shipped-files.md:81–82), so the registration leaves its `left` list and the script stays in it.

A test for the script itself, named after the precedent `_run_perl` (tests/test_guardrail.py:122),
which runs a claude hook on stdin JSON with `CLAUDE_PROJECT_DIR` set, with two cases: no
`ACTIVE_PLAN.md` and no `ACTIVE_DESIGN.md` at the root → the script emits nothing; a gate file
present → the reminder JSON. The script's root resolution is what such a test pins.

Reference searches (run this session):

- `git grep -l '_guardrail_registration'` → `devpro/harnesses/claude.py` (definition and use),
  `PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md` (prose), `tests/test_plugins.py:85` (the
  test's name only). The builder's `(plugin, shipped)` signature need not change; if it does,
  those are the sites to follow.
- `git grep -l '_guardrail_probe'` → `devpro/install.py` only.

Done-line: `just test devpro`, then `just check-wheel` (a new non-`.py` file under `devpro/` must
ride the wheel's package data), then `just check-deltas`, then `just check-links`. Re-takes the
reference slots at its end (rendered `hooks/hooks.json` changes). One commit.

## P4 — The opencode plan-state reminder

Applies [ARCHITECTURE.md, Install, Opencode entry](ACTIVE_DESIGN.md#architecturemd-install-opencode-entry)
verbatim to `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md` (target passage at lines 3–4,
verified this session), and implements
[ARCHITECTURE.md, Install, Opencode entry](ACTIVE_DESIGN.md#architecturemd-install-opencode-entry-1):

- `devpro/harnesses/resources/opencode/index.ts`: its setup registers
  `ctx.tool.hook("execute.after")` filtered to `subagent` and
  `ctx.session.hook("experimental.idle")` for a session whose `parentID` is set, injecting
  `ctx.session.synthetic` into the parent session, gated by `ACTIVE_PLAN.md` or
  `ACTIVE_DESIGN.md` existing at the project root. Hook registration is unconditional; the gate is
  checked when the hooks fire and decides the injection, not the registration. Its declared
  `Context` slice (index.ts:47–55) gains the tool and session domains.
- `tests/opencode_entry_runner.ts`: the stub context carries the new domains. It already records
  tool hook names (`hooks.push(name)`, :106–110) and passes `location: { directory }` into setup
  (:104–106), which is the project root's source on the declared surface;
  `tests/guardrail_ts_runner.ts:12–15` types the same shape. The runner gains the session hook and
  the synthetic record, and the means to fire the registered paths — an `execute.after` event for
  a `subagent` call and an `experimental.idle` event — so the updated test exercises dispatch,
  completion and the gate. The recording shapes are the executor's call.
- `tests/test_opencode_entry.py`: the assertions pinning what the entry registers —
  `out["hooks"] == ["execute.before"]` at :114 and `out["hooks"] == []` at :154 — update to what
  the entry now registers, and the synthetic record asserts the injection into the parent session
  where the gate holds and none where it does not. The second assertion lives in
  `test_a_user_level_opencode_entry_with_no_guardrail_beside_it_registers_and_hooks_nothing`,
  whose name and docstring the change falsifies; its name is among the updates. They fail on the
  current entry — no reminder hooks registered, no injection — which is the defect the updates
  close.

Verified facts the entry acts on (repo `/Users/agent-user/projects/opencode`; HEAD is v2.3.2,
`git describe --tags` → `v2.3.2`; re-check with `git -C ../opencode grep -n '<text>' <tag> -- <path>`):

- `execute.after` carries `tool`, `sessionID`, `agent`, `messageID`, `id`, `input`, and
  `status: completed|error` — packages/plugin/src/promise/tool.ts:53–69 at v2.3.2.
- `experimental.idle` fires when a session finishes model work with no pending input and carries
  `sessionID` and a `background` list — packages/plugin/src/promise/session.ts:185–200 at v2.3.2.
- `synthetic` is a session API — packages/plugin/src/promise/session.ts:232 at v2.3.2; an injected
  message runs in the same execution, one model call per injection.
- A subagent session is distinguished by `parentID` being set: `Session.Info` carries an optional
  `parentID` (packages/schema/src/session.ts:31–34), `session.created` carries it
  (packages/schema/src/session-event.ts:47), and the session domain exposes `get`
  (packages/plugin/src/promise/session.ts:224). How the entry retrieves the parent's id from the
  idle event's `sessionID` is this package's discovery point; the surface exists.

Floor verified — the design's floor 2.2.6 stands, no blocker: at tag v2.2.6,
`git -C ../opencode grep -n 'execute.after' v2.2.6 -- packages/plugin` hits
packages/plugin/src/effect/tool.ts:29 and packages/plugin/src/promise/tool.ts:47;
`git -C ../opencode grep -n 'experimental.idle' v2.2.6 -- packages/plugin` hits
packages/plugin/src/effect/session.ts:198; `synthetic` is at
packages/plugin/src/promise/session.ts:213; `parentID` at
packages/schema/src/session-event.ts:47 (all run this session).

Note, surfaced not blocking: SPEC's `written for opencode v2.2.6` sentence
(shipped-files.md:97–99) stays as P1 leaves it, and stays true — every API the entry uses exists at
2.2.6, verified above; ARCHITECTURE.md's applied statement names the version developed against
and the floor.

Reference searches (run this session):

- `git grep -l 'opencode_entry_runner'` → `tests/opencode_entry_runner.ts`,
  `tests/test_opencode_entry.py` (`_RUNNER`, :25),
  `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md` (:21).
- `git grep -l 'opencode_plugin_stub'` → `tests/guardrail_ts_runner.ts:10`,
  `tests/opencode_entry_runner.ts:15`. The plugin stub module is expected to stand unchanged; if
  it changes, those importers are the sites to follow.

Done-line: `just test devpro`, then `just check-deltas`, then `just check-links`. Re-takes the
reference slots at its end (the entry lands in the reference-opencode slot). One commit.

## P5 — Post-plan review

The reviewers are the agent for each domain the plan changed substantively; each gets the project
documents and `ACTIVE_DESIGN.md`, not this plan:

- `python-coder` — `claude.py`, `install.py`, `check_deltas.py`, both skill definitions, the
  Python tests;
- `typescript-coder` — `index.ts` and the entry runner;
- `shell-dsl-coder` — `state-table-reminder.sh`;
- `architect` — the structure changed (a new resource, new hook wiring, the probe gate, the
  byte-check target) and the project documents' claims about the code changed;
- `prompt-engineer` — model-facing text changed (the two skill wordings) and the project
  documents changed.

No tech-writer seat: no README or human-facing guide changes.

Done-line: `just check-links`. One commit.

## P6 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
