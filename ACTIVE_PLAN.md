# Plan — profiler dispatch timing, install re-entry, index defaults, and the process's specificity rule

The plan runs from [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), accepted in final form. Each package applies the
design entries it implements to their target leaves verbatim (the pairs carry no relative links to rebase),
and lands the code and tests that make them true. Every package is a shipped product change: full process,
one commit each. Packages run serially in the shared tree, in ID order — P1 and P3 both touch
`devpro/profiler/pages.py` and `tests/test_devpro_profiler.py`, and P3/P4 share the plugin stub, so no two
run concurrently.

## Status

| Package | State | Rating | Lifetime | Depends on |
| --- | --- | --- | --- | --- |
| P1 | landed | mechanical | shipped | — |
| P2 | landed | mechanical | shipped | — |
| P3 | dispatchable | expert | shipped | P1 |
| P4 | dispatchable | expert | shipped | — |
| P5 | landed | mechanical | shipped | — |
| P6 | dispatchable | expert | shipped | P1–P5 |
| P7 | dispatchable | expert | shipped | P6 |

## P1: The sessions index opens on its defaults

Applies [The index](ACTIVE_DESIGN.md#the-index) to its target
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md`, section "The index".

Lifetime: shipped. The index page opens with child-record rows off, and the URL carries each control's
state as its deviation from that control's default — an untouched page's URL carries no query. No config
file, no old-URL compatibility (settled in the design; the URL is written and read by the same page).

Scope: `devpro/profiler/pages.py` — the `INDEX` template's controls block, `sync`, `restore`, and the two
comments stating the encoding — and `tests/test_devpro_profiler.py`.

Facts:

- `devpro/profiler/pages.py:1096`:
  `<label><input type="checkbox" id="child-rows" name="child-rows" value="on" checked> child rows</label>`
  — the child-rows box ships `checked` today.
- `devpro/profiler/pages.py:1312` (inside `sync`, :1309–1323):
  `if (control.name && !control.checked) params.append(control.name, control.value);` — the hard
  `!control.checked` test the design's change replaces: it encodes only "off", which is the deviation
  only while every control's default is on.
- `devpro/profiler/pages.py:1333` (inside `restore`, :1330–1341):
  `if (control.name) control.checked = !params.getAll(control.name).includes(control.value);` — presence in
  the query reads back as "off", the inverse of the same all-on default.
- `devpro/profiler/pages.py:1298`: `if (box.disabled) box.checked = true;` — a harness box the feed
  disables is re-checked; under deviation encoding a re-checked box equals its default and writes nothing,
  so this line stands unchanged.
- `devpro/profiler/pages.py:1250` (inside `hides`, its comments at :1243 and :1248):
  `if (session.dispatcher && !document.getElementById('child-rows').checked) return true;` — the control's
  one runtime reader besides `sync` and `restore`. It stands unchanged under the flip: it reads the
  control's state, not its default, so the off default flows through it, and its comments state the hiding
  rule, not the default.
- `git grep -ln "child-rows"` → `devpro/profiler/pages.py`, `tests/test_devpro_profiler.py`. Nothing else
  references the controls.
- The pin that changes, `tests/test_devpro_profiler.py:945–948`: "The controls: a box for the child rows
  and one per harness, each checked so the page opens on every row" —
  `assert re.search(rf'<input type="checkbox" {control} [^>]*checked>', index)` over all three ids.

Edits (enumerated):

1. Drop `checked` from the child-rows input (:1096); the two harness boxes keep theirs.
2. `sync`: append a control's param when its state deviates from its own default — compare
   `control.checked !== control.defaultChecked` — replacing the `!control.checked` test. The harness boxes'
   URLs are unchanged for untouched boxes; a checked child-rows now writes `child-rows=on`.
3. `restore`: a control the URL names reads the opposite of its own default —
   `control.checked = params.getAll(control.name).includes(control.value) ? !control.defaultChecked : control.defaultChecked`.
4. Update the two comments (:1304–1308 and :1325–1329) to state the off default and the deviation encoding.
   `hides()` (:1250) and its comments (:1243, :1248) stand unchanged — they read the control's state, not
   its default. No other template text changes; the sort encoding is untouched.

Tests: the pin at :945–948 is updated in this package — child-rows ships no `checked`, the two harness
boxes keep it. No DOM test harness exists in this repository (`git grep -ln "jsdom|happy-dom" -- tests
devtools` → nothing; `tests/dashboard` holds server tests only), so the browser-side encoding is verified by the review's two-tab/URL probe, run by hand and recorded in
the package's report, its shape fixed so a later reviewer re-runs it string for string: serve with
`just dev-dashboard`, open `/profiler/`, and compare the URL each state writes exactly — a child-rows box
turned on writes `?child-rows=on`, the opencode box turned off writes `?harness=opencode`, a sorted head
beside an off claude box writes `?sort=records&harness=claude` — each URL opened in a second tab restores
the state that wrote it, and an untouched page's URL carries no query.

Done-line: `just test devpro`, `just lint`, `just dev-check-links` (the target leaf changed), and
`just dev-check-design-deltas-applied`, expected to fail only on the eight pairs P2–P4 apply (the
shipped-files pair, the three capture pairs, the four opencode-entry pairs) and on nothing else. One commit.

## P2: An install from an installation's own copy re-enters

Applies [Shipped files](ACTIVE_DESIGN.md#shipped-files) to its target
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`. The pair is paragraph-internal: the target's
paragraph continues past the replaced run, and that continuation stands.

An install run from an installation's own copy into the installation holding that copy proceeds, passing
over exactly two paths — the devpro package under `tools/devpro/` and the wrapper `tools/devpro.sh` —
silently (no stdout/stderr mention of the pass-over), everything else installing under Write safety's
rules as they stand. Intent: config/option changes take effect via the embedded copy without changing the
installed version.

Scope: `devpro/install.py`. `devpro/install_target.py` changes nothing —
`tests/test_install_target.py:162` (`test_an_install_into_the_running_packages_own_source_tree_is_refused`)
pins the separate source-tree boundary, `require_outside_package_source` (:87–95), which this package does
not touch and which stays green. `devpro/install_base.py` changes nothing — its `TOOLS_DIR`/`WRAPPER`
constants (:31–32) already name both passed-over paths.

Facts:

- `devpro/install.py:535–543`, `_require_not_the_running_copy`, the refusal this change replaces:
  `raise InputError(f"install would replace {copy}, the copy of devpro running it — run the \`devpro\`
  command on PATH to install here; nothing written")` where `copy = root / DEVPRO_COPY` and
  `copy.resolve() == PACKAGE_ROOT`.
- `git grep -n "_require_not_the_running_copy"` → install.py:535 (def) and :616 (its sole call site,
  `real_root = (harness_dir if real_harness_dir is None else real_harness_dir) / ctx.bound_harness.plugin_dir`).
- The two paths' names: `DEVPRO_COPY = f"{TOOLS_DIR}/devpro"` (install.py:122), the shipped row
  `ShippedPackage(".", DEVPRO_COPY, None, stamps=False)` (install.py:137), and `WRAPPER`
  (install_base.py:32), written at install.py:691–692.
- The writes a pass-over skips: the destination clear `_clear_package_destination(root /
  package.destination)` over `packages` (:684–685) — clearing the copy's destination would empty the
  package the run executes from; the package-file writes (:686–690); the wrapper write (:691–692).
- `wrapper` is also in `_refuse_foreign_targets`' resource targets (:656) and in `copied` (:665). The
  refusal stays untouched: on a re-entry run the wrapper is the installation's own stamped file and the
  check passes as it does for any reinstall. `prune(root, keep={*written, *copied})` runs at :713 — the
  passed-over paths must remain in the `keep` set, or prune deletes the running copy.
- The version report: `replaced_version = _installed_version(root / DEVPRO_COPY / "__init__.py")` (:683),
  printed at :718 — the plain `else:` of :716's `if replaced_version is None:` — as
  `devpro {replaced_version} replaced by devpro {__version__} → {copy_dir}`; the :716 branch prints the
  installed-only sentence and is untouched. On a re-entry run the copy is not replaced, and the :718
  sentence is a statement about the pass-over — the re-entry run prints neither it nor any pass-over
  mention. The `installed:` line (:714) counts what the run wrote.
- The pin's mechanism: `tests/test_devpro_install.py:143–157`, `_staged`'s docstring — "`devpro.install`'s
  and `devpro.install_target`'s `PACKAGE_ROOT` each bound it, both modules having imported the name from
  `devpro.install_base`" — the monkeypatch that makes `copy.resolve() == PACKAGE_ROOT` (install.py:539)
  true while the checkout's `main()` runs in-process: the copy is the running package by rebinding, not by
  process.
- `git grep -n "DEVPRO_COPY" -- devpro` → install.py:122, :137, :538, :683, :715 and the clauses/comment
  sites read none of them behaviorally; the profiler and claude modules' `INSTALL_WRAPPER` constants name
  the claude wrapper path, not this one.

Edits (enumerated):

1. Turn `_require_not_the_running_copy` (:535–543) into the question its call site answers — it returns
   whether `real_root`'s copy is the running package instead of raising — and rename it to state that
   (`is_the_running_copy`; its only two sites are :535 and :616 per the search above). The call site at
   :616 captures the answer.
2. On a re-entry run: drop the devpro-copy package row from `packages`/`package_files` and the wrapper
   from the write list, so neither is cleared nor written; keep both in the `keep` set prune reads.
3. On a re-entry run: suppress the version-replacement sentence at :718 (the `else:` branch). Nothing
   about the pass-over is printed, on stdout or stderr.
4. Everything else — every other shipped package, harness resource, render, agents file, prune, include
   line, migration — installs exactly as any install runs, under the Write safety rules as they stand.

Tests: `tests/test_devpro_install.py:2037–2050`
(`test_an_install_run_from_an_installations_copy_into_that_installation_is_refused`) pins the refusal and
is rewritten in this package into the re-entry case, keeping its mechanism: the first in-process
`main(["install", str(project), "--harness=claude"])` writes a real copy; `_staged(copy, ())` (:2044)
rebinds `devpro.install.PACKAGE_ROOT` to that copy — the mechanism that makes `copy.resolve() ==
PACKAGE_ROOT` true while the checkout's `main()` runs the second call in-process — and the copy is a full
staging tree, the shipped packages' sources being directories inside the `devpro` package it carries
(`devpro/development-tools/`, `devpro/runner-snippets/`, `devpro/kb-tools/`). The rewritten assertions:
the second run, `main(["install", str(project), "--harness=claude", "--components=kbase"])`, exits 0; the
copy's files and the wrapper are byte-identical before and after; the kbase component's files, absent
before, are written — the intent's config change taking effect through the pass-over; nothing in stdout or
stderr names the pass-over; and the pass-over is exactly two paths — a staged foreign file at another
shipped destination (the runner-snippets directory) is still overwritten. Its TEST_PRECONDITION defect: an
install run from an installation's own copy into the installation holding that copy refuses, or rewrites
the copy it runs from, or passes over a path other than the two named.
`test_reinstalling_over_a_copy_of_another_version_reports_both_versions` (:2053) stays green — its run is
from the checkout, not the copy.

Done-line: `just test devpro`, `just lint`, and `just dev-check-design-deltas-applied`, expected to fail
only on the seven pairs P3 and P4 apply (the three capture pairs, the four opencode-entry pairs) and on
nothing else. One commit.

## P3: The opencode capture records the child's run; the render joins it

Applies three entries to their targets in
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-opencode-capture.md`:
[The capture and the hook surface](ACTIVE_DESIGN.md#the-capture-and-the-hook-surface) (the capture side),
[Dispatched children](ACTIVE_DESIGN.md#dispatched-children) and
[Tokens and the model](ACTIVE_DESIGN.md#tokens-and-the-model) (the join side).

Lifetime: shipped. Two coupled pieces in one package and one commit: the capture writes a child's events
as their own records the moment each reports, and the render joins each to its dispatch record at read.
No held state, no close-time pairing, no rewrite of the dispatch record.

Scope: `devpro/harnesses/resources/opencode/profiler.ts`, `devpro/profiler/values.py`,
`devpro/profiler/pages.py`, `tests/profiler_contract_runner.ts`, `tests/test_devpro_profiler.py`,
`tests/fixtures/profiler_serialize_record.json`.

Facts:

- `profiler.ts:152` `const SUBAGENT_TOOLS: Record<string, string> = { task: "Agent", subagent: "Agent" }`
  — the two tool names a dispatch rides. `profiler.ts:294–333`, `callRecord`: the record the
  `execute.after` acknowledgment writes already has the launch-acknowledgment shape — `at` the call's end,
  `duration_ms` the call's window (:313) — which is the dispatch moment and the firing cost the design
  states; what changes for a dispatch is only what `background` and the join make of it.
- `profiler.ts:319`: `background: false,` — hardcoded false on every record, dispatches included.
- `profiler.ts:338–350`, `eventRecord`: the event record's shape (`v`, `harness`, `at`, `session`,
  `event`, `trigger`, `source`, `context_tokens`, `transcript`); the new records carry these fields plus
  what their event reports.
- The capture's session hooks today: `model.request` (:474) and `experimental.idle` (:486), each guarded
  so a host refusing one cannot kill `setup` (:473's `silently`, and the idle hook's own `silently` body).
  The child-event registrations join them under the same guard. The idle **lifecycle record stays**: the
  design removes the entry's idle *reminder registration* only, and the capture leaf's sentence about the
  idle record stands.
- The join the claude records already take: `devpro/profiler/pages.py:173–182` `subagent_stops` reads
  stop records out of the same session's records before the call filter; `:190–207` `with_stop` merges and
  replaces — quote :199: `merged = {**call, "child_agent_type": call.get("child_agent_type") or
  stop.get("agent_type")}`; `:210–231` `unique_calls` applies it, its filter `if not
  record.get("tool"): continue` (:222–223) skipping event records. `read_sessions` (:830–838) reads every
  store's sessions in one pass, and `dispatches` (:858–873) already maps child session id → dispatcher
  across stores — the cross-session keying the join rides.
- The consuming sites of the fields the join fills (`git grep -n "child_agent_id\|background" --
  devpro/profiler/pages.py` → 32 hits; the render's: :443–451 `context_words` (the background word),
  :540/:590–591 the child spend, :667–675 `session_data`'s page/feed fields, :858–873 `dispatches`).
- Schema: `devpro/profiler/values.py:14` `SCHEMA_VERSION = 2`; `profiler.ts:61`
  `const SCHEMA_VERSION = 2`; the claude capture takes it at `capture.py:323` and `:368`. No reader reads
  `v` (`git grep -n 'record.get("v")' -- devpro/profiler` → no hits); the pins are all in tests.
- Reference searches: `git grep -l "with_stop"` → `devpro/profiler/pages.py` (sole file). 
  `git grep -n "SCHEMA_VERSION"` → values.py:14, capture.py:26/:323/:368, profiler.ts:61. 
  `git grep -l "opencode_plugin_stub"` → the stub's importers are tests/guardrail_ts_runner.ts,
  tests/opencode_entry_runner.ts, tests/profiler_contract_runner.ts, tests/profiler_mask_runner.ts,
  tests/profiler_serialize_runner.ts (plus prose mentions in
  `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-hook-contract-is-read-not-assumed.md` and
  `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md`) — this package changes no stub content: the
  contract runner feeds host-shape events as inputs through the stub's generic `session.hook` collector
  (profiler_contract_runner.ts:28–32), so the other four runners are untouched.

Decisions this plan states:

- **Schema bump.** `SCHEMA_VERSION` goes 2 → 3, both constants in this commit. The record vocabulary
  changes — event records gain `agent_type` and `model`, and the terminal `session.execution.*` names
  arrive — and the version field is the record's one marker of what a reader may assume. Stores are
  scratch data: no migration; the render's tolerant `.get()` reads carry old lines beside new.
- **`background` on a dispatch record is `true`.** From the 2.3.0 floor every `subagent`/`task` call
  returns at once and the child runs in the background, which is what the field means; the hardcoded
  `false` at :319 misreports every dispatch today. The render already consumes the field
  (`context_words`' background word, the feed's field) — but see the failure mode below.
- **Field policy at the join.** The event's `agent_type` replaces the dispatch record's
  `child_agent_type` — it is the agent the child actually ran, the acknowledgment's input-derived guess
  standing only where no event came. The `model` replaces the parent-side model the acknowledgment
  recorded. The duration at the join becomes the span from the dispatch record's `at` to the terminal
  event's `at`; the record's `at` stays the dispatch moment. The stored records are never rewritten —
  every fill happens at read.
- **Degrade.** A child reporting none of the events, or no terminal event, renders exactly today's
  record: the acknowledgment's shape, the firing cost as duration — and **not** marked running.

Failure mode this package must not ship: `with_stop` marks a background call with no stop as
`running` (:197–198), and `subagent_stops` finds no stop in an opencode store — an opencode dispatch
record carrying `background: true` through `with_stop` as it stands would render every opencode dispatch
as running. The join extends `with_stop`'s pattern with the opencode event map and a degrade that leaves
the record as captured; one join mechanism, one home (extend `with_stop` or a sibling it delegates to —
its sole referencing file is pages.py per the search above), never a second join beside it.

Tests: the schema pins update in this package — `tests/test_devpro_profiler.py:256`
(`assert record["v"] == 2`), the inline fixtures at :454/:465/:487/:824, and
`tests/fixtures/profiler_serialize_record.json` (verified: `grep -o '"v": *[0-9]*'` → `"v": 2`).
`profiler_contract_runner.ts` fires the three event kinds for a dispatched child — host-shape inputs, the
event names and payload fields the design's table states — and the test asserts the records written to the
child's own store. New tests, each with its defect: the join fills `child_agent_type`, `model` and the
duration from the child's events (defect, TEST_PRECONDITION: a dispatch row reads the firing cost as the
child's span, or names a model the child never ran, or names an agent the child did not run); the degrade
(defect: a child whose events never came renders as nothing, raises, or is marked running). The index feed
test (:849) stays green — the feed's shape is unchanged.

Done-line: `just test devpro`, `just lint` (the shipped TypeScript is type-checked against the host's
pinned declarations), and `just dev-check-design-deltas-applied`, expected to fail only on the four pairs
P4 applies and on nothing else. One commit.

## P4: The opencode entry's completion trigger

Applies [Opencode entry](ACTIVE_DESIGN.md#opencode-entry) to its target
`PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md` — four pairs. The first pair is paragraph-internal
(the design notes it; the paragraph continues past the replaced run). No fallback: a host without the
terminal events loses the completion reminder, the plugin otherwise intact — decided in the design.

Scope: `devpro/harnesses/resources/opencode/index.ts`, `tests/opencode_plugin_stub.ts`,
`tests/opencode_entry_runner.ts`, `tests/test_opencode_entry.py`.

Facts:

- `index.ts:161–164` — the dispatch `execute.after`, filtered to a completed `subagent` call; stays.
- `index.ts:168–176` — the idle registration this change removes; quote :168–169:
  `await ctx.session.hook("experimental.idle", async (idle) => {` /
  `if (idle.background.length > 0) return`.
- `index.ts:71–72` — the reminder constant, byte for byte
  `Reminder: keep the ACTIVE_PLAN state table up to date.` — untouched; the byte-for-byte pin survives
  through `tests/test_opencode_entry.py:277–300`
  (`test_both_harnesses_inject_one_sentence`, held to claude's reminder script's output).
- The pins that change: `tests/test_opencode_entry.py:148–149`
  (`assert out["sessionHooks"] == ["model.request", "experimental.idle", "experimental.idle"]`),
  :172–175 (the synthetics' `on` values, one of which is `experimental.idle`), :226–227 (the user-level
  `sessionHooks == ["experimental.idle"]`).
- `git grep -l "opencode_plugin_stub"` → tests/guardrail_ts_runner.ts, tests/opencode_entry_runner.ts,
  tests/profiler_contract_runner.ts, tests/profiler_mask_runner.ts, tests/profiler_serialize_runner.ts —
  a stub change must keep the guardrail runner green, which the change does not touch behaviorally.
- Host surface: the terminal `session.execution.succeeded`, `.failed` and `.interrupted` events are
  observed shipped behavior of the 2.4 line (the design's floor paragraph states the 2.3.0 loss: a host
  whose surface offers none fails that registration, and the completion reminder is what it loses). Per
  CONVENTIONS, [A hook contract is read, not assumed](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-hook-contract-is-read-not-assumed.md),
  the host's hook reference is read for each event before wiring, and the stub models what the reference
  states (A stand-in models the API's real semantics).

Edits:

1. The completion reminder's second registration moves from `experimental.idle` to the three terminal
   `session.execution.*` events: each names the child session whose run ended, `ctx.session.get` reads
   that child's parent, and the parent is the one injected into. The idle registration is removed; the
   `experimental.idle` capture record in `profiler.ts` is not this package's.
2. The new registrations are guarded so a failure cannot kill `setup` — the guard the capture's
   registrations use (`silently`, profiler.ts:439), reporting through the entry's `log` helper
   (index.ts:49–51) rather than silently.
3. The dispatch-side reminder (`execute.after`, a completed `subagent` call) stands as it stands.
4. The stub gains the terminal events with the semantics the reference states, and the runner fires them.

Tests: the three pins update to these values, stated so the executor supplies them rather than invents
them. The terminal registrations are the entry's own and register on every install — not gated to project
installs as the capture is. The user-level pin (:226–227, the comment above it included) becomes
`assert out["sessionHooks"] == ["session.execution.succeeded", "session.execution.failed",
"session.execution.interrupted"]`, in the entry's registration order. The project-level pin (:148–149)
becomes `assert out["sessionHooks"] == ["model.request", "experimental.idle",
"session.execution.succeeded", "session.execution.failed", "session.execution.interrupted"]` — the
capture's `model.request` and idle (the capture's idle lifecycle record stays), then the entry's three.
The synthetics pin (:172–175) keeps its two rows, and its second `on` becomes
`session.execution.succeeded` — the terminal event the runner fires; the dispatch-moment row's
`execute.after` stands. `test_both_harnesses_inject_one_sentence` (:277) runs the user-level shape: its
runner fires a terminal event for a child whose parent holds the gate, the one injected sentence reads off
that synthetic, and the byte-for-byte text assertion survives unchanged. New test — the review's
one-reminder-per-completion probe, mechanically testable here: fire a terminal event for a child whose
parent holds the gate, then fire a second terminal event for the same child; the parent receives exactly
one injection (defect, TEST_PRECONDITION: a parent is reminded twice for one child's run, or not at all
for the terminal event).

Done-line: `just test devpro`, `just lint`, `just dev-check-links`, and
`just dev-check-design-deltas-applied`, which by this package reports every one of the design's nine pairs
landed and so passes clean. One commit.

## P5: The process's minimum-specificity rule

No design pair carries this change: it is the intent paragraph's fourth sentence
([ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), "For every project the process ships, its durable records state no
more specificity than their reader needs"), which the design states the plan carries, and the final-form
review's D8 note flags as the one obligation no pair confirms. Settled: prose-only — no mechanical check
anywhere; scope is strictly the durable documents; lightest touch — one bullet.

Lifetime: shipped (this is the process's own shipped definition code). The rule lands in
`devpro/definitions/skills/development.py`, in the body of the `references/project-documents.md`
SkillFile — the reference that governs how the project documents are written and kept right — in its
"What the documents leave out" list (:626–643), inserted after the "A check earns its place" bullet
(:632–633). The proposed full text, applied verbatim:

```
- Specificity past the reader's need: a project document states each subject at the exactness its
  reader needs to act on it or check it, and no finer. Where the code states a fact in its own text —
  a signature, a field list, a value's spelling — the document names the fact and leaves the exact
  form to the code it names, never transcribes it: a transcription is a second home for a statement
  only the code's changes move. The rule holds the durable documents; a plan or a design is
  short-lived and states whatever its work needs.
```

Facts: `git grep -c "durable" -- devpro/definitions/skills/development.py` → one hit (:172, the
reference-durability rule) — the word is free to use here. `git grep -ln "project-documents" -- tests`
→ nothing: no test pins the reference's content. The rendered copies under `.opencode/plugins/` are
untracked installs (`git ls-files .opencode` → empty), refreshed by `just agents` at the operator's hand,
not by this commit.

Edits: the one bullet above, in the one file. Nothing else — no check, no second statement of the rule in
SKILL.md's own body; the reference is the rule's one home.

Done-line: `just test devpro` (the render-closure tests over the references),
`just lint`. One commit.

## P6: Post-plan review

Lifetime: shipped (process, not product — its product is the review document). The reviewers are the
agents for each domain the plan changed substantively: the TypeScript coder (the two plugin resources),
the Python coder (`install.py`, `pages.py`, `values.py`, `development.py`), `devpro-architect` (the
render's read path and the install's flow changed structurally), and `devpro-prompt-engineer` (the
project documents and the development skill's reference changed). Each is given the project documents and
ACTIVE_DESIGN.md — not the plan — and writes their own review in the scratch directory, independently;
the session synthesizes the reviews into `ACTIVE_PLAN_REVIEW.md` at the repository root, de-duplicating
findings and reconciling them into one account, without waiting for an approval between the last report
and the write-up. The review document is never diced, and is deleted in the commit that lands the plan.

Done-line: `just dev-check-links` (the review document is a top-level `*.md` the check reads), run once,
at the package's end; the package is done when the run passes and the review document is committed. One
commit (the one that adds `ACTIVE_PLAN_REVIEW.md`).

## Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.

### P7: Post-plan burndown

Lifetime: shipped.

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
