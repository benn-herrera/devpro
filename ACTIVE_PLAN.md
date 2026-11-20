# Active plan — the opencode plugin records its sessions' activity into the profiler's trace store

From the accepted design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — four entries:
[the Shipped files entry](ACTIVE_DESIGN.md#shipped-files) and [the resources-enumeration
entry](ACTIVE_DESIGN.md#shipped-files--the-resources-enumeration) under SPEC delta, [the Harness
profiler entry](ACTIVE_DESIGN.md#harness-profiler) under ARCHITECTURE delta — three byte-pinned
passage pairs — and [the Harness profiler entry under Code
delta](ACTIVE_DESIGN.md#harness-profiler-1) (prose, no pair; P3 composes the capture from it, and
its first paragraph carries the settled home of the shipped payload). The design is not diced; it
is under the plan size limit. It is final-form, PE-reviewed and revised at `af94c7d`.

Every package's intended lifetime is **shipped** — the whole process — and one commit closes each
package: the closing commit sets its Status row to `landed` as that commit lands its work.

Sequencing: P1, then P2, then P3, then P4, then P5. P1 applies the three passage pairs; P2 makes
the install ship the payload to opencode; P3 writes the capture; P4 and P5 are the post-plan
review and burndown. P3's code ships `profiler.ts` into `resources/opencode/`, whose copy follows
the directory `harness_resource_copies` already walks — no install.py change rides in P3.

The bound terms: the checkpoint gate is `just test`, then `just sweep-python`
(`PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md:4`); the step-down application is
the dispatch's `model` parameter (`the-gates.md:5`); CONVENTIONS binds no step-down model, so the
development skill's default pair applies — the mechanical packages P1 and P2 run on
`stem-mechanical=reaper/Ornith-1.5-122B` through the `model` parameter.

The plan is written to `dispatchable` and handed back: the main session dispatches.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | dispatchable | mechanical | the three passage pairs applied verbatim: SPEC's shipped-files paragraph, SPEC's resources enumeration, ARCHITECTURE's harness-profiler leaf |
| P2 | dispatchable | mechanical | `harness_resource_copies`' opencode copy list gains the three payload files sourced from `resources/claude/libexec/`; the behavior pin updates |
| P3 | dispatchable | expert | `profiler.ts` — the capture in the plugin's TypeScript, wired from the entry; the entry's registration pin updates |
| P4 | drafted | expert | Post-plan review — dispatchable when P3's commit lands |
| P5 | drafted | expert | Post-plan burndown — dispatchable when P4's review document lands |

## P1 — The three passage pairs applied

Implements [the Shipped files entry](ACTIVE_DESIGN.md#shipped-files), [the resources-enumeration
entry](ACTIVE_DESIGN.md#shipped-files--the-resources-enumeration) and [the Harness profiler
entry](ACTIVE_DESIGN.md#harness-profiler), each as accepted: its `becomes` block replaces its
`as it stands` block, each run of whitespace read as one space, no composition; the labels the
design's blocks carry (`**As it stands:**`, `**Becomes:**`) are not written into the target.

Scope: `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

Facts, each re-run before acting on it:

- The delta check today: `just dev-check-design-deltas-applied` → `pairs: 3, landed: 0, pending: 3,
  drifted: 0, conflicting: 0, problems: 0`, exit 1. P1's application moves all three to landed.
- The from-blocks sit in their targets, every run of whitespace read as one space, verified by a
  normalized-membership check of each design pair against both target files: pair 1 and pair 2
  match only in `shipped-files.md`, pair 3 only in `harness-profiler.md`, and no `becomes` block is
  already present. Their exact sites: pair 1's from-block is
  `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:105` in full (`resources; no opencode or
  mage install ships the resources or the hook entries.`); pair 2's from-block is
  `shipped-files.md:87-88` (from `path it holds below the install directory: opencode's at` to
  `<install-dir>/hooks/guardrail.pl` and`; line 88's tail word `and` is the from-block's last
  word, so the replacement runs into line 89's `…(mage ships none):` mid-sentence — the
  becomes-block is written so the sentence continues correctly); pair 3's from-block is
  `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:56-58` (the leaf's last paragraph, first
  line `No opencode or mage payload ships: the profiler's hooks are claude's, and an`).
- No passage carries a markdown link — the `(SPEC.md, Deployed Surfaces, Shipped files)` and
  similar mentions are parenthetical text — so nothing to rebase.
- No test pins any passage's text: `git grep -n "no opencode or mage" -- tests/` → nothing;
  `git grep -n "recreated in the opencode" -- tests/ README.md devpro/` → nothing. P1 changes no
  code, so no test can break.

Work:

1. Apply pair 1's becomes-block over `shipped-files.md:105` verbatim.
2. Apply pair 2's becomes-block over `shipped-files.md:87-88` verbatim.
3. Apply pair 3's becomes-block over `harness-profiler.md:56-58` verbatim.
4. Run the delta check: it must report `landed: 3, pending: 0, problems: 0`, exit 0.

Done-line: `just dev-check-design-deltas-applied` (pending: 0), then `just dev-check-links`. One
commit closes the package.

## P2 — The install ships the payload to opencode

Implements [the Harness profiler entry under Code delta](ACTIVE_DESIGN.md#harness-profiler-1) in
its settled-home sentence: the payload keeps its one home, `resources/claude/libexec/`, and
opencode's copy list gains the three files sourced from there — no second copy of the payload in
the repository.

Scope: `devpro/install.py` (`harness_resource_copies`, its docstring included),
`tests/test_devpro_install.py:1873-1886` (the behavior pin).

Facts, each re-run before acting on it:

- The copy mechanism is one rglob per harness:
  `devpro/install.py:196` (`source = PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / harness`) and
  `:201` (`source.rglob("*")`), with `HARNESS_RESOURCES_SOURCE = "harnesses/resources"` at `:127`.
  The carve-out adds the payload's source root for opencode only — a module-level constant mapping
  the harness name to extra source roots (for example
  `_CROSS_HARNESS_SOURCES = {"opencode": ("claude/libexec",)}`), walked the same way as the
  harness's own directory; the constant's shape is the executor's call. The constraints, both from
  the settled-home sentence: one source, so no second copy of the payload exists, and mage
  unaffected — mage's copy list gains nothing.
- The docstring's invariant gains the carve-out: `install.py:185-193` states "These files are the
  harness's own"; the sentence gains that opencode's list additionally carries the render payload
  sourced from `resources/claude/libexec/`, the payload being harness-neutral.
- The user-level filter needs no change: `install.py:384-391` (`_resource_copies`) keeps, on a
  user-level install, only the target equal to the entry resource, so the payload never reaches a
  user-level opencode install; the design's "a mage install ships none of them" holds because
  mage's mapping entry does not exist.
- `Path.rglob` on a missing directory yields nothing and raises nothing:
  `python3 -c "from pathlib import Path; print(list(Path('/nonexistent').rglob('*')))"` → `[]`.
  The tests that build a synthetic `PACKAGE_ROOT` without `resources/claude/`
  (`tests/test_devpro_install.py:1429`'s fixture creates only `resources/opencode/`; `:519-531`'s
  creates only `resources/probe/`) therefore cannot crash the carve-out, and the probe-harness test
  is unaffected because its harness name is not in the mapping.
- The banner test passes unchanged: `tests/test_devpro_install.py:1781-1797` collects every
  harness's sources (`:1785`) and computes each source's origin from the source's own path
  (`:1791`), so the three payload files — listed under both claude and opencode — are each checked
  against the banner they already carry, `!INSTALLED! from
  devpro/harnesses/resources/claude/libexec/<file>` (`hp.sh:2`, and hp.py's and view.html's
  first lines), which names the file's true home in this repository and is truthful from an
  opencode install too. `assert sources` stays satisfied.
- The behavior pin to update: `tests/test_devpro_install.py:1873-1886`
  `test_no_opencode_or_mage_install_copies_the_profiler_payload_or_registers_it` asserts
  `not (root / _PROFILER).exists()` for the opencode and mage plugins alike (`:1883-1884`). The
  design changes the stated behavior for opencode, so the test moves with it: opencode's project
  install now holds `libexec/` holding exactly `_PROFILER_FILES` and registers nothing (its
  `_REGISTRATION` assertion stands); mage's holds neither, unchanged; the docstring states the new
  shape. No other test pins the opencode plugin's file set exhaustively — the opencode assertions
  in the suite are the registration/reload run, the settings absence (`:1866-1871`), this pin, and
  the user-level entry-only test (`:1429-1440`), whose synthetic fixture holds no payload to copy.
- Reference search for the changed function: `git grep -n "harness_resource_copies" -- devpro/
  tests/` → `devpro/install.py:182` (the def), `devpro/install.py:387` (the one caller,
  `_resource_copies`), `tests/test_devpro_install.py:45` (import), `:531` (harness `"probe"`),
  `:1785` (the banner test). No signature change; the one caller needs none.
- P1's landed SPEC pairs state the shipping; P2 makes the code match them.

Work:

1. Add the extra-source mapping to `devpro/install.py` and walk it inside
   `harness_resource_copies` for the harnesses it names, appending `(source, root /
   relative-target)` pairs after the harness's own.
2. Amend the function docstring's invariant sentence with the carve-out.
3. Update `tests/test_devpro_install.py:1873-1886` as the pin fact states: the opencode leg asserts
   `libexec/` holds exactly the launcher, the tool and the page and that no registration is
   written; the mage leg stays as is; the docstring follows.
4. Run the gate, then confirm the delta check still reports the three pairs landed and the link
   check passes.

Done-line: `just test`, then `just sweep-python`, then `just dev-check-design-deltas-applied`
(landed: 3), then `just dev-check-links`. One commit closes the package.

## P3 — The capture: profiler.ts beside the entry

Implements [the Harness profiler entry under Code delta](ACTIVE_DESIGN.md#harness-profiler-1),
composing the capture from its prose.

Scope: `devpro/harnesses/resources/opencode/profiler.ts` (new),
`devpro/harnesses/resources/opencode/index.ts` (the import and the registration, nothing else),
`tests/test_opencode_entry.py:140-141` (the registration pin). The scratch driver this package
observes the capture with is throwaway and lives under `.devpro-temp/`, never committed.

Facts, each re-run before acting on it:

- The wiring to copy is the guardrail's: the entry holds the path constant
  (`devpro/harnesses/resources/opencode/index.ts:82`, `const guardrailPath = join(here,
  "guardrail.ts")`) and registers with a guard and a dynamic import (`:163-164`, `if
  (existsSync(guardrailPath)) await (await import(guardrailPath)).default.setup(ctx)`). The
  registered module is `Plugin.define({ id, async setup(ctx) … })` typing its own context:
  `guardrail.ts:189-193` declares `async setup(ctx)` with no annotation and calls
  `ctx.tool.hook("execute.before", …)` from its own body (`guardrail.ts:29` types its own input).
  `profiler.ts` follows exactly — one module, its own event typing, its own `setup` — so the entry
  gains one path constant and one guarded registration, nothing else. The entry's `Context` types
  `tool.hook` for `"execute.after"` only (`index.ts:71`) and is not widened.
- The `existsSync` guard covers the user-level install, which copies no `profiler.ts` (P2's
  `_resource_copies` fact): the entry runs without the capture there, as it does without the
  guardrail.
- The hook payloads, from opencode's own source (`anomalyco/opencode`,
  `packages/plugin/src/promise/tool.ts`, interface `ToolHooks` — dev and v2 branches agree — and
  the trigger sites in `packages/core/src/tool.ts`): `execute.before` carries `tool`, `sessionID`,
  `agent`, `messageID`, `id` — the call's pairing key — and `input`; `execute.after` carries the
  same fields plus `status: "completed"` with `result`, or `status: "error"` with `error`. The
  locally installed `@opencode-ai/plugin@1.18.30` types
  (`~/.config/opencode/node_modules/@opencode-ai/plugin/dist/index.d.ts:235-258`) type only the
  `Hooks`-record form, where the pairing key is spelled `callID` and no `status` appears; they do
  not describe the `ctx.tool.hook` domain form the entry uses. The domain form above is the
  profiler's contract.
- The lifecycle event is the idle hook the entry already registers (`index.ts:192-200`); the
  capture registers its own `ctx.session.hook("experimental.idle", …)` and the record's `event`
  field carries the hook's own name, `experimental.idle`.
- The record's shape is the render contract, not a design decision: `hp.py:493-520` builds the
  tool-call record — `v` (`SCHEMA_VERSION = 2`, `hp.py:22`), `harness`, `at`, `session`,
  `agent_id`, `agent_type`, `tool_use_id`, `tool`, `name`, `duration_ms`, `ok`, `child_agent_id`,
  `child_agent_type`, `background`, `child_spend`, `tokens`, `context_tokens`, `branch`, `args`,
  `result` — and `hp.py:546-560` the event record, adding `event`, `trigger`, `source` and
  `transcript`. `tree` and the page read these fields through `.get()` guards
  (`hp.py:950-1130` reads `agent`, `agent_type`, `args`, `at`, `background`, `branch`,
  `child_agent_id`, `context_tokens`, `duration_ms`, `marker`, `name`, `ok`, `result`, `running`
  and `tool` this way), so a field the opencode hooks supply no value for renders empty; there is
  no filter on `harness` anywhere in `hp.py` — `grep -n '"harness"'` matches only the writes at
  `:508` and `:550`.
- The masking to mirror: `hp.py:125` (`mask`), `:132` (`clip`), limits `NAME_LIMIT = 80` (`:39`)
  and `RESULT_LIMIT = 300` (`:41`) — the argument and result summaries masked the way `hp.py`
  masks claude's.
- The trace destination: `.devpro-temp/harness-profile/<session-id>.jsonl` under the project root
  (`hp.py:23`, `TRACE_DIR = Path(".devpro-temp") / "harness-profile"`); the project root is
  `ctx.location.project.directory` (`index.ts:63-64`), not the opened directory. The page reads
  `view.html` from beside the script (`hp.py:1069`, `(SCRIPT_DIR / VIEW_TEMPLATE).read_text`) —
  the shipped trio stays together, which the install's relative-target copy preserves.
- The capture writes nothing inside the plugin directory, so the entry's watcher
  (`index.ts:269`, `watch(here, { recursive: true }, …)`) sees no appends and fires no reloads.
- The pin to update: `tests/test_opencode_entry.py:140-141` asserts the exact registration lists,
  `out["hooks"] == ["execute.before", "execute.after"]` and `out["sessionHooks"] ==
  ["experimental.idle"]`. The design changes what the entry registers — the profiler adds its own
  `execute.before`, `execute.after` and idle registrations — so both assertions move with it; the
  runner already records every hook by name (`tests/opencode_entry_runner.ts:126-131` for tool
  hooks, `:142` for session hooks) and its tool hook accepts any name, so no runner change is
  expected. A runner or stub failure beyond these two assertions is reported as a finding, never
  edited to pass. The suite's installs are real (`test_opencode_entry.py:57-64`), so `profiler.ts`
  stands beside the entry in every run after P2.
- The capture needs no registry entry: the registry carries agents, commands and skills only
  (`devpro/harnesses/opencode.py`, `_registry_json` — `records(Kind.AGENT, Kind.DOCUMENT)`,
  `records(Kind.COMMAND)`, `records(Kind.SKILL)`), and the show-profile skill already renders
  under opencode (`test_the_profile_skill_renders_under_every_harness`,
  `tests/test_devpro_install.py:1866-1871`; its registry file path `skills/show-profile/SKILL.md`,
  `.opencode/plugins/devpro/registry.json:399`).
- The skill's finder resolves the shipped payload: its first candidate `../../libexec/hp.sh` from
  the skill's own directory (`devpro/definitions/skills/show_profile.py:22`) resolves
  `<plugin-dir>/libexec/hp.sh` where P2 lands the payload, so the skill works under opencode
  unchanged.
- Two sentences go stale with this package and no accepted entry covers them; the plan leaves both
  to the post-plan review, whose findings route a design entry for the user to decide:
  `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:111-112` names only `guardrail.ts` as the
  change that needs an opencode restart, and P3 imports `profiler.ts` the same way;
  `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md`'s account of the entry's registrations
  becomes incomplete when the entry registers the capture too.
- Failures raise nothing out of a hook — the capture's own callbacks swallow and stay silent, the
  shape `guardrail.ts` and the entry's reminder hooks already keep (`index.ts:178-180` logs rather
  than throws; the capture stays silent per the design, logging nothing).

Work:

1. Write `profiler.ts`: TypeScript, standard-library imports only (`node:fs`, `node:path`,
   `node:url` as the entry already uses), `export default Plugin.define({ id, async setup(ctx) … })`
   with the id namespacing the entry's convention uses. It registers `execute.before` and
   `execute.after`, pairs each call's `id` to the time the before-hook took, and on the after-hook
   appends one record per completed or errored call to the session's trace file — the fields above,
   `harness` `"opencode"`, `at` ISO-8601, `duration_ms` from the paired times, `ok` from `status`,
   and the argument and result summaries masked and clipped to the limits above, every field
   `tree` and the page read present with its empty rendering where the hooks supply no value. Its
   own idle hook appends the lifecycle record, `event` carrying `experimental.idle`. A capture
   that fails is silent.
2. Wire the entry: the path constant and the guarded registration, beside the guardrail's.
3. Update `tests/test_opencode_entry.py:140-141`'s two assertions to the registration lists the
   entry now produces, in the order the wiring produces them.
4. Observe the capture where no gate executes it: in a scratch project under `.devpro-temp/`, run
   a throwaway bun driver that stubs `@opencode/plugin` the way
   `tests/opencode_plugin_stub.ts` does, loads the installed `profiler.ts`, and drives one
   synthetic before/after pair and one idle event per the payload contract above; then
   `sh <plugin-dir>/libexec/hp.sh tree` and `tree --format html` render the records — the tree
   shows the call with its duration and outcome and the page's data carries the keys `view.html`
   parses, proving the record shape `tree` and the page read survived the TypeScript capture.
5. Run the gate, then the document checks.

Done-line: `just test`, then `just sweep-python`, then `just dev-check-design-deltas-applied`
(landed: 3), then `just dev-check-links`. One commit closes the package.

## P4 — Post-plan review

The reviewers are given the project documents and the design, not the plan, and review the changes
and their tests against the project's standards and fitness for purpose. Each writes their own
review in the scratch directory, independently, at `.devpro-temp/p4-review-<seat>.md` — one file
per seat, named for it — and the session synthesizes them into `ACTIVE_PLAN_REVIEW.md`, never
diced, de-duplicating findings and reconciling them into one account.

- `devpro-typescript-coder` — `profiler.ts` and the entry's wiring against the project's coding
  standards and the hook contract;
- `devpro-python-coder` — `install.py`'s carve-out and the updated pin;
- `devpro-architect` — the landed leaves (SPEC's shipped-files, ARCHITECTURE's harness-profiler)
  against the code, SPEC.md against ARCHITECTURE.md, and the two stale sentences P3's facts name
  (`shipped-files.md:111-112`, `opencode-entry.md`);
- `devpro-prompt-engineer` — the project documents the pairs landed.

Done-line: `just dev-check-links`. The review document and P4's Status row land in P4's commit.

## P5 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.

The burndown gets `devpro-prompt-engineer` usability review, then revision, before it is
`dispatchable`.

The landing acts, after the burndown's work:

1. The landing commit deletes `ACTIVE_DESIGN.md` (not diced, so no tree).
2. The landing commit deletes `ACTIVE_PLAN_REVIEW.md`.
3. The landing commit deletes this plan (`ACTIVE_PLAN.md`) — no next plan exists at that time. The
   deletion is P5's row resolution: no Status row is set, the row dies with the plan.

Done-line: `just test`, then `just sweep-python`, then `just dev-check-design-deltas-applied`
(landed: 3), then `just dev-check-links`, then `just dev-check-plan` — all before the landing
acts; the landing commit's tree carries the gate passing.

Every commit message and pull-request description carries the attribution line the development
skill states:

```
ai assisted by [devpro](https://github.com/benn-herrera/devpro) on opencode. submitter takes full responsibility.
```
