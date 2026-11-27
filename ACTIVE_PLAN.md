# ACTIVE PLAN

# The second periodic review

The whole-project review over accumulated drift, staffed per the development skill's periodic-review
section plus the test-suite audit seat the ROADMAP Maintenance ticket charters. A prior periodic
review landed at devpro 0.17.2 (commit 69eed3ee); roughly nine plan-landings have accumulated since,
against the bound interval of 8 — the count is met, and the previous plan's landing was the coherent
feature boundary. The review has no design before it and goes straight to a plan; this plan is its
tracking surface. The user's standing direction: the review rolls through the findings collected and
the burndown items drafted, and holds there — the user discusses findings, remedies and the draft
before anything is approved or dispatched.

## Status

| Package | State | Rating |
| --- | --- | --- |
| R1 | landed | expert |
| R2 | landed | expert |
| B1 | landed | expert |
| B2 | landed | expert |
| B3 | drafted: retired before dispatch | expert |
| B4 | landed | expert |
| B5 | landed | expert |
| B6 | landed | expert |
| B7 | landed | expert |
| B8 | in progress | expert |
| B9 | dispatchable | expert |
| B10 | dispatchable | expert |
| B11 | dispatchable | expert |
| B12 | dispatchable | expert |
| B13 | dispatchable | expert |
| B14 | dispatchable | mechanical |
| B15 | dispatchable | expert |
| B16 | dispatchable | expert |

### R1 — the panel runs and the findings synthesize

Intended lifetime: shipped. Rating: expert.

Nine seats run independently, each writing its own review to the scratch directory: the architect,
prompt-engineer, tech-writer and Python-coder pairs — conformance (each seat's own criteria,
reporting departures from THESIS.md, SPEC.md, ARCHITECTURE.md or CONVENTIONS.md) and consistency
(the pairs the skill assigns: THESIS↔SPEC to the prompt-engineer, SPEC↔ARCHITECTURE to the
architect, SPEC's README coverage to the tech-writer, ARCHITECTURE↔code and CONVENTIONS↔behavior to
the coder) — plus the test-suite audit seat chartered by the ROADMAP ticket. Wave 1 (the architect
pair, the coder pair, the audit) reported; wave 2 (the prompt-engineer pair, the tech-writer pair)
is out. When all nine report, the session synthesizes the findings into `ACTIVE_PLAN_REVIEW.md` —
one entry per defect, naming every seat that reported it, grouped by root cause — and this plan's
row lands in the commit that adds the review document.

Done-line: the nine seats' reports are in; `ACTIVE_PLAN_REVIEW.md` exists, is committed, and its
entries name their seats; `just dev-check-plan` passes.

### R2 — the review's plan is drafted

Intended lifetime: shipped. Rating: expert.

The session dispatches the architect to draft the burndown items from `ACTIVE_PLAN_REVIEW.md` —
one item per root-cause group, each with its own ID, status row, rating and one-commit close —
run one `devpro-prompt-engineer` usability review over the drafted items together, apply the
revision, and set each item's row by its state. The plan then holds for the user's discussion of
findings, remedies and the draft before any item is dispatched.

Done-line: the items are drafted, reviewed, revised and dispatched-visible in the status table;
the hold is reached and stated in the plan.

## Burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` — the nine seats' findings F1–F19, with per-seat detail in
`.devpro-temp/review-periodic-*.md`. One item per root-cause group; each cites the F-numbers it
fixes and closes in one commit. The hold was reached and the user's rulings applied: B4, B5, B6
and B16 are reshaped and, with the rest, `dispatchable` — the roll proceeds in the stated serial
order. Behavioral-probe work the audit located (clause strip-and-observe, rendered-definition
smoke, live-host entry) stays with the ROADMAP Maintenance ticket that charters it — no burndown
item carries it.

**Serial order where files are shared.** B8 before B14 — both cut the profiler surface, and the
test layout maps onto the module seams B8 settles (`tests/test_devpro_profiler.py:53` imports the
`pages` symbols the split moves). B9 before B14 — the REVIEW_SEAT pin's home is the profiler test file
B14 splits; the pin lands before the split and moves with it. B7 before B13 — the README
re-entry sentence B13 lands restates the ARCHITECTURE statement B7 lands. B7 before B16 — both
touch `ARCHITECTURE/install/renders-and-copies.md`. B2 before B15 — both touch
`PROJECT_DOCS/entry-point.md`. B5, B13 and B15 may each touch `README.md`: those three run
serially in ID order.

**For the hold — the synthesis's coverage.** F1–F19 do not carry every defect the nine seats
reported; the per-seat files name further findings with no synthesized entry. The hold decides
which join the burndown as items and which are retired. The `.venv` carve-out (architect-
consistency's W3) is carried now as F19 → B16, and the served-behaviors' home (its W5) is folded
into F15 → B13. Still uncovered by any F-entry: architect-consistency W4 (the printed URL), N1,
N5; architect-conformance W1 (the stamp-manifest claim the code does not keep) and its N4's code
half; pe-consistency F2, F3, F4 (the blocks table's "is not" columns, the plan-form/category-map
naming) and F5 (the category-map sentence); pe-conformance A1, A5–A7, B3, B4, C1–C5, D1, D3,
E2–E7, F2; coder-conformance W1–W3, W5–W7, N1, N3; tw-consistency W1, W5, N1–N4; tw-conformance
F2–F5, F7–F8, F10–F17.

### B1 — the agents-file marker's SPEC statement is rewritten to the code's form

Intended lifetime: shipped. Rating: expert. Fixes F1 (settled: SPEC is the stale side; the code
and ARCHITECTURE stand).

Scope: `PROJECT_DOCS/SPEC/agents-file.md` — the block-recognition paragraphs at :9-12, :25-28 and
:57-59. Fact (re-run): `devpro/definitions/harness_agents_file.py:14` renders
`<!-- vvv-devpro @!agf-version!@ do not edit at or between marker lines. devpro-vvv -->` — no
plugin word; `devpro/agents_file.py:95` calls `vvv-devpro <version>` the harness-neutral marker.
Rewrite around the harness-neutral marker: legacy spellings (`vvv-devpro devpro <version>`,
`vvv-devpro kbase <version>`) are recognized marker lines whose first word names a present or
retired plugin; restate the release-word rule as the outcome; retire the "names no plugin"
wording, which matches no block the current release writes.

In-scope tests: the agents-file install cases in `tests/test_devpro_install.py` — the code's
behavior is unchanged, so a test failing on the rewritten wording is reported as a finding, never
edited to pass. Done-line: `just dev-check-plan`, `just check-links`.

### B2 — THESIS's "What is new" names the absorbed engine

Intended lifetime: shipped. Rating: expert. Fixes F2 (settled: retitle, drop "and only these",
name the absorption).

Scope: `PROJECT_DOCS/entry-point.md`, "What is new" (:45-48) with the process paragraph (:63-73)
cross-checked. Fact (re-run): :47 reads "Two things, and only these." The change carries one
decision: the absorption sentence also names the plan-status form and the category map with the
dicing engine (one sentence, not two — pe-consistency's F4 choice), citing
`ARCHITECTURE/repo-layout.md:17`'s "the absorbed dicing package… as devpro code".

In-scope tests: none — document only. Done-line: `just check-links`.

### B3 — retired, not executed

The user retired B3 before dispatch: F3's evidence compared the new source against old
point-in-time render runs (`agents`, `pe-postplan`, `pr-pe-review`, mtimes predating the source
edit), not living copies — `latest` and the `reference-*` slots were and are byte-identical to
the package tree, and the user re-rendered the stale snapshots the same day. The item's map
rows were no-ops (`TEST_SURFACE_MAP`'s `devpro/ devpro` and `devpro/ wheel` prefix rows already
select every file under `devpro/`, the three assets included — proved with the
`test-changed.sh` selector's own matching rule), and the mandated TEST_PRECONDITION test would
have passed on HEAD. No code change; F3 is closed by the evidence. The serial note "B3 before
B9" is spent with it — B9 needs no ordering constraint beyond B14's.

### B4 — `profiler init claude`: the verb is harness-scoped

Intended lifetime: shipped. Rating: expert. Fixes F4.

The ruling: `init` is claude-shaped because claude is the only harness it slots to — opencode's
capture is the plugin the install ships and wires, with no python-side init — and the contract
becomes explicit: the verb is `profiler init claude`, the harness stated as the argument the
`capture` verb already takes.

Scope: `devpro/profiler/hooks.py` (`INSTALL_WRAPPER` :44, `_hook_command` :52-54, `is_our_command`
:82-84, `merge_hooks` :92-105, `init` :117-134), `devpro/profiler/cli.py` (the verb's
registration), `PROJECT_DOCS/ARCHITECTURE/harness-profiler/what-init-writes.md`, and the profiler
skill's text where it names the verb. Fact (re-run): with `PYTHONPATH=.`,
`hooks.is_our_command('"$CLAUDE_PROJECT_DIR/devpro/plugins/devpro/tools/devpro.sh" profiler
capture claude')` → `False`, while `HOOK_COMMAND` names the `.claude/skills/devpro/tools/devpro.sh`
wrapper — a re-`init` over an opencode-shaped repo appends a duplicate registration. The fix:
`init claude` refuses — exit 2, `error: ` before a message naming it — where the project's devpro
install is opencode-shaped or the existing entry names a wrapper it does not recognize, and
`merge_hooks` appends nothing in that case. Rendered outputs are build products and are never
edited; the rendered copies' newer text-scan `merge_hooks` is context the fix closes.

In-scope tests: the init migration and merge-hooks cases in `tests/test_devpro_profiler.py`; a new
test names the refusal's defect — the duplicate a re-`init` over an opencode-shaped repo appends.
Done-line: `just test`, `just lint`.

### B5 — README's install line carries no version pin

Intended lifetime: shipped. Rating: expert. Fixes F5, F6.

The ruling: the version number leaves the README — text that needs constant attention or rot; the
installed version is discoverable on the machine without it. The pipx line installs unpinned from
the repository; the "names the newest release tag" sentence and its manual restamp go; the `just`
floor is stated once — 1.33.0 for every project install of a nested plugin — matching the guide.

Scope: `README.md` (:50 the floor sentence, :64 the tag, :69-70 the newest-release sentence),
`PROJECT_DOCS/SPEC/guide-and-readme.md` (:37-39), `devpro/definitions/skills/guide.py` (its
*Requirements* is the survivor). Facts (re-run): README:50 carries the two-number lead with a
colon clause ("every project install of a nested plugin writes that line, an `import?`");
README:64-70 states the pipx line "names the newest release tag. Nothing checks it: the release
plan re-stamps it, by hand"; the SPEC leaf repeats both numbers while the guide states 1.33.0
alone.

In-scope tests: none — the enforcement hole dissolves with the pin. Done-line: `just test`,
`just check-links`.

### B6 — the dashboard's stop answers any shape

Intended lifetime: shipped. Rating: expert. Fixes F7's stop half.

The ruling: the stop-shape defect is worth its few lines — `GET /api/stop` answers the stop and a
POST answers it whatever the body or content type, the panel's `{}` body contract being the page's
choice, not the endpoint's requirement; no body is required and none is parsed, and the page's own
stop keeps working unchanged. The exit-contract half is dropped as ruled: a natural
`serve_forever` return on a loopback surface is a theoretical end, not worth the stop-flag
machinery it would take to distinguish.

Scope: `devpro/kanban/server.py` (:292-294 the 415, :309-310 the 400, :302-307 the stop).
`devpro/dashboard/server.py` and `devpro/dashboard/cli.py` leave this item's scope — the exit
half is ruled out. In-scope tests: the stop-route cases in `tests/dashboard/test_server.py` gain
the GET and the no-body cases, and the test pinning the retired stop contract —
`tests/dashboard/test_board_panel.py:525`
`test_a_stop_request_that_is_not_json_is_refused_and_the_board_still_answers`, whose text/plain
→ 415 premise the ruling retires — is deleted, its subject carried positively by the new cases.
Done-line: `just test`, `just lint`.

### B7 — the install's ARCHITECTURE statements catch up

Intended lifetime: shipped. Rating: expert. Fixes F8.

Scope: `PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md`. Facts (verified at HEAD):
`devpro/install.py:849-857` adds every project-relative `checked_followed_agents_file` path (the
project's `AGENTS.md` and mage's `CLAUDE.md`) to the writes the managed set omits; `install.py:154`
`RETIRED_PACKAGE_DIR = "skills/docdicer/dicing-snippets"`, removed at :724, is named in SPEC's
write-safety but in no ARCHITECTURE leaf (`git grep -r "dicing-snippets" PROJECT_DOCS/ARCHITECTURE`
→ nothing); the re-entry run drops the devpro-copy row (`:640-644`) so its destination is never
cleared, and SPEC's pass-over (`deployed-surfaces/shipped-files.md:71-76`) is stated nowhere in
ARCHITECTURE.

In-scope tests: none — document only. Done-line: `just check-links`.

### B8 — the profiler's read boundary gets its module

Intended lifetime: shipped. Rating: expert. Fixes F9.

Scope: new `devpro/profiler/read.py` owning the read-side symbols the seat names — `read_sessions`,
`session_of`, `list_sessions`, `store_directories`, `dispatches`, `review_fanouts`,
`dispatcher_of`, `child_dispatches`, `depth_children`, `joined_session`, `child_episodes`,
`Depth` and the trace read — with `devpro/profiler/pages.py` importing from it; the referencing modules updated —
`devpro/dashboard/server.py`, `devpro/profiler/cli.py` and `devpro/profiler/hooks.py`;
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-code-belongs-to-devpro.md` names the module and
adds `directives.py` to the module list with its job (the stamp's directive walk, digest and
manifest). Reference search (re-run): `git grep -n "pages\.(dispatches|review_fanouts|session_for|Depth|read_sessions|dispatcher_of)" -- devpro/ tests/` →
`devpro/dashboard/server.py:46-47,79,164-179`; `tests/dashboard/test_server.py:29,625,627,650`;
`tests/test_devpro_profiler.py:53,2108,2139`. Second search, the import form the first misses:
`git grep -n "\.pages import|profiler import pages" -- devpro/ tests/` →
`devpro/dashboard/server.py:46-47`; `devpro/profiler/cli.py:59`; `devpro/profiler/hooks.py:22`
(which takes only `UsageError` — the strict-fill error stays in `pages.py`, so its import stands);
`tests/dashboard/test_server.py:29`; `tests/test_devpro_profiler.py:53,2108,2139` — every
referencing file is in scope.

In-scope tests: `tests/test_devpro_profiler.py`, `tests/dashboard/test_server.py` — behavior
unchanged; import-path updates ride the same commit. Done-line: `just test`, `just lint`.

### B9 — the CONVENTIONS layer's rules, bindings and open verifications catch up

Intended lifetime: shipped. Rating: expert. Fixes F10, F14, F18 (the convention statements half).

Scope: `PROJECT_DOCS/CONVENTIONS/**` and one pin test. Facts (re-run): the dangling cite —
`planning-and-execution/a-narrowed-format-names-the-inputs-it-refuses.md:8` cites
"(`ACTIVE_PLAN.md` §B3)", a file the landing `6b22eecc` deleted, and the CONVENTIONS leaf that
repeats it with; `american-english-spellings.md:12` pins `tests/test_plugins.py:47` and `:48`,
where :48 is not the symbol's line — the catalog is held by symbol or drops the numbers;
`pages.py:1139` `REVIEW_SEAT = "prompt-engineer"` has no pin while its file-mate `AGENT_PREFIX` is
pinned (`tests/test_devpro_profiler.py:1796` asserts it against `devpro.components`). The work:
one CONVENTIONS line naming the digest's recognizer case (the plugin-agnostic marker derivation
lives in `install_base.py:48-51`, the port copies it, the byte-equality digest test is the pin)
and the probe-copy sentence for `Scratch for tests and recipes`; the `REVIEW_SEAT` pin test —
a test reading the definition set's bare post-plan-reviewer name and failing on divergence, no
import on the capture path — its home today `tests/test_devpro_profiler.py`, wherever the
profiler tests land after B14's split (hence B9 before B14; the pin moves with it); the
scratch-HOME mechanism stated or the exception named; and F18's
verifications closed or retired: the hook-contract stub shapes against
`tests/opencode_plugin_stub.ts`, the real-tree case set, `devtools/scripts/check-wheel.sh:48`'s
evidence. A verification that closes as a new defect is reported as a finding, never edited to
pass.

In-scope tests: the new `REVIEW_SEAT` pin — TEST_PRECONDITION: the silent rename F10 states (a
rotten unreviewed mark on every consumer install). Done-line: `just test`, `just lint`,
`just check-links`.

### B10 — the periodic review's count is computed and its panel is one enumeration

Intended lifetime: shipped. Rating: expert. Fixes F11 (the remaining half — the process shape
landed at `eb49837b`).

Scope: `devpro/definitions/skills/development.py` (*Periodic review*), `devpro/definitions/skills/guide.py`
(the merge sentence), a count target in `justfile`, `PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md`
if the mechanism is stated beside the interval binding. Fact: no target reads the messages, so
the interval's count is a machine guarantee left in prose. The counting commands, whose answers
at execution are the count — never a literal this plan pins:
`git log --format=%s 69eed3ee..HEAD | wc -l` and `git log --format=%s 69eed3ee..HEAD |
grep -icE "lands? a plan|plan lands"` (at drafting, 956 and 13; the target's output at execution
is the number). Decision carried: the count becomes a runner target's output
(the machine's half) and the landing commit's message claims the landing (the author's half); the
seat enumeration states in one sentence that each kind's conformance seat judges to its own
criteria and owns no pair, so a seat can learn its own seat from the section.

In-scope tests: the rendered-definition structural tests over the skill bodies
(`tests/test_devpro.py`). Done-line: `just test`, `just lint`, `just dev-check-plan`.

### B11 — SPEC's design form states the entry form the skill produces

Intended lifetime: shipped. Rating: expert. Fixes F12.

Scope: `PROJECT_DOCS/SPEC/plan-status-form.md` (:85-95 the stages paragraph; :104-107 the fixed
summary line). Facts (re-run): :88-90 carries stages, `pending` entries and stage-scoped pairs;
`devpro/definitions/skills/development.py:157-165` states the design is deleted in the commit that
lands the plan, and the entry form holds no pending state or stage marker;
`development.py:30-33` `DESIGN_SUMMARY_LINE_TERM` is a private constant the SPEC leaf spells
verbatim, with no check pairing the two.

**The decision the item carries, flagged for the hold:** the stages paragraph is retired — the
skill's lifecycle is the survivor, no commit in the interval grew the skill's stage rule — and the
summary line becomes a cite of the skill's term rather than a second unchecked spelling (or a
check, if the pairing is load-bearing).

In-scope tests: none — document-only as drafted; if the hold's ruling picks the check path for
the summary-line pairing, the close amends to carry that test. Done-line: `just check-links`,
`just dev-check-plan`.

### B12 — routes and terms name one thing

Intended lifetime: shipped. Rating: expert. Fixes F13.

Scope: `PROJECT_DOCS/SPEC/guide-and-readme.md` (:17-21), `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`
(:178), the `dicing-and-checks/kanban/` leaf titles if the directory renames,
`devpro/definitions/skills/guide.py`, `devpro/definitions/skills/docdicer.py`. Survivors carried
(verified): `dashboard` names the route — SPEC:21 reads "the `docdicer` skill's `kanban`" while
`guide.py:36` routes it to the skill's `dashboard` and the verb and recipe say so; `board` names
the served part; the guide's grammar names one source (SPEC:35-39's sentence names the survivor);
"post-plan burndown" splits into *the burndown section*, *the drafting ticket*, *the burndown
items*; "review-chain dispatch" is defined where SPEC uses it (`shipped-files.md:178` marks it
undefined; the concrete reading lives only at `serving.md:74-75`).

In-scope tests: the rendered-skill structural tests (`tests/test_devpro.py`) — a rename that
moves links is checked by the link check, not the suite. Done-line: `just check-links`, `just
test`, `just lint`.

### B13 — README and SPEC state the dashboard's and re-entry's face

Intended lifetime: shipped. Rating: expert. Fixes F15.

Scope: `README.md` (the dashboard section :159-181, Updating :109-114 and :199-203, the kbase
paragraph :137-140), `PROJECT_DOCS/SPEC/dicing-and-checks/kanban/index.md`,
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`. Facts (re-run):
README:171-172 states the root answers a redirect to `/board/` — the redirect is in
`server.py:301-310` and the docdicer skill; no SPEC leaf states it, so an implementation could
404 `/` and pass; `shipped-files.md:156-161` states the local-time and loopback-only rules and the
README's dashboard section omits both for the profiler view; README:112-114's "Only rerunning the
project's install replaces the copy" reads as if a rerun always replaces it, where the re-entry
pass-over (SPEC `shipped-files.md:71-76`) writes everything but the copy; README:137-140's
"platforms as under Requirements" resolves to devpro's platforms, not kbase's own prerequisites
(SPEC `plugins.md:101-108`).

In-scope tests: none — document only. Done-line: `just check-links`.

Folded into this coverage work by the F19 entry: the profiler view's user-facing behaviors —
index controls and sorting, the unreviewed mark, the duration notation — are asserted only in
ARCHITECTURE, a boundary breach its entry-point forbids. Decision carried: the durable outcomes
are promoted into SPEC's shipped-files leaf; the exact strings and route/JSON shapes stay in
ARCHITECTURE.

### B14 — the test suite's layout splits along package seams

Intended lifetime: shipped. Rating: mechanical. Fixes F16.

Scope: the audit's layout, verbatim — `tests/install/` (from `tests/test_devpro_install.py`),
`tests/render/` (from `tests/test_devpro.py`), `tests/profiler/` (from
`tests/test_devpro_profiler.py`), each directory one package seam with the per-module subject
lists and per-directory `conftest.py` the audit's proposal names, bite-ordered profiler → install
→ render. `tests/test_guardrail.py` and `tests/dicing/test_dicer.py` are not split — their size
is the case data, not interleaved subjects.

Acceptance: `just test devpro` passes with the same collected item count, and `git diff --stat`
shows test files only — the acceptance test the sticky ticket's claim needed, run and recorded.
No behavior change rides it; no §2 collapse and no probe joins the commit.

In-scope tests: the suite itself. Serial: after B8 (shared profiler surface — the layout maps
tests onto the seams B8 settles). Done-line: `just test`, `just lint`.

### B15 — the accumulated text defects

Intended lifetime: shipped. Rating: expert. Fixes F17.

Scope, each fix enumerated (verified at HEAD): `ARCHITECTURE/harness-profiler/serving.md:132-134`
— the fused sentences, a subject restored or the clause cut; the stale
`devpro/definitions/skills/__pycache__/show_profile.cpython-311.pyc` — deleted, its module absent;
`devpro/definitions/skills/profiler.py:52-63` — the *Answer* section's one binding for `PROFILER`
and bullets for the four required items; `devpro/definitions/skills/guide.py:98-102` — the 0.17.x
walk cut to the release it applies to or moved to README's Updating, its dead
`skills/docdicer/tools/` path gone; `PROJECT_DOCS/entry-point.md` :13-19 — one sentence naming
the absorbed tooling surface; `devpro/__init__.py:9-40` — the docstring lists the absorbed
modules `repo-layout.md:11` claims it lists; the `.mypy_cache` convention stated where the lint
rule is read; `PROJECT_DOCS/SPEC/write-safety.md` — the `.bak` carve-out ARCHITECTURE
`renders-and-copies.md:21-22` states added, and the packaging-table row
(`ARCHITECTURE/packaging.md:69`) naming both refused writes.

In-scope tests: none — text only. Serial: after B2 (shared file `PROJECT_DOCS/entry-point.md`).
Done-line: `just check-links`, `just test`, `just lint`.

### B16 — the `.venv` carve-out is retired

Intended lifetime: shipped. Rating: expert. Fixes F19.

The ruling: the carve-out is stale — leftovers from when docdicer was a separate tool with its own
`.venv` — and the code's removal behavior stands; SPEC's promise goes.

Scope: `PROJECT_DOCS/SPEC/write-safety.md` (:18-19 the carve-out, :43-44 the comparison exclusion)
loses the exception; `PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md` (:22) keeps its "no
venv is ever delivered" statement; `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md:139`'s `VENV_DIR`
line — a constant the package does not define — is corrected or dropped. No code change:
`install.py:525`'s clear already removes everything under the destination.

In-scope tests: none — document only. Done-line: `just check-links`.
Serial: after B7 (shared file `renders-and-copies.md`).

**The hold.** The plan stops here: the items above are drafted, not approved. The user discusses
the findings, the remedies and the decisions the items carry — named in B4, B5, B6, B11, B16 and
the coverage note above — before any row leaves `drafted`.
