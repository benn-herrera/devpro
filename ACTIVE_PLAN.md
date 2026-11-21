# Active plan — the profiler serves its pages over HTTP

From the accepted design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — three entries: [the Shipped files
entry](ACTIVE_DESIGN.md#shipped-files) under SPEC delta, one pair; [the Harness profiler
entry](ACTIVE_DESIGN.md#harness-profiler) under ARCHITECTURE delta, two pairs; [the Harness
profiler entry under Code delta](ACTIVE_DESIGN.md#harness-profiler-1), prose with no pair — P1
through P4 compose the serve surface from it. The design is not diced; it is final-form and
accepted. Each package below applies the pair its entry carries to its target verbatim, each run
of whitespace read as one space, relative links rebased where the destination sits in another
directory — no pair block carries a relative link, so none is rebased.

Every package's intended lifetime is **shipped** — the whole of the development skill's process —
and one commit closes each package: the closing commit sets its Status row to `landed` as that
commit lands its work.

Sequencing: P1, then P2, then P3, then P4, then P5, then P6, then P7. P1 writes the serve verb and
its index, P2 the page's call tree, P3 the skill, P4 the runner target — all four are the surface
P5's document pairs describe, so the pairs land last and hold true at the commit that lands them.
P6 and P7 are the post-plan review and burndown. Packages that share a build run serially in the
shared tree.

The bound terms: the checkpoint gate is `just test`, then `just sweep-python`
(`PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md:4`); the step-down application is
the dispatch's `model` parameter (`the-gates.md:5`); CONVENTIONS binds no step-down model, so the
development skill's default pair applies — the mechanical packages P4 and P5 run on
`stem-mechanical=reaper/Ornith-1.5-122B` through the `model` parameter.

A note on verification, which is not a package: after the work lands, the user runs a live claude
session and sees the serve surface record it — that observation is out of this plan's scope by the
user's direction, and nothing here verifies a live session. P1's tests drive the serve surface
over recorded stores without one.

The plan is written to `drafted` and handed back: the main session runs the
`devpro-prompt-engineer` usability review and revises, then sets every row `dispatchable` and
dispatches.

## Status

| Package | State | Rating | Lifetime | Changes |
| --- | --- | --- | --- | --- |
| P1 | landed | expert | shipped | `hp.py` gains the `serve` verb: `ThreadingHTTPServer` on loopback, free port with `--port`, URL on stdout; `/` the index from `list_sessions` with unreadable stores stated, `/page/<session-id>` from memory; serve tests added |
| P2 | landed | expert | shipped | `view.html`'s call tree: a session of nothing but tool calls renders those calls as its calls content, never an empty tree under the calls header |
| P3 | landed | expert | shipped | `show-profile`'s body serve-first: run the launcher's `serve`, hand the user the URL; the file redirect demoted to a one-line mention |
| P4 | landed | mechanical | shipped | the justfile gains `dev-profiler`, wrapping source-tree `hp.sh serve` the way `dev-kanban` wraps docdicer's serve |
| P5 | landed | mechanical | shipped | the three delta pairs applied: one to `shipped-files.md`, two to `harness-profiler.md` |
| P6 | drafted | expert | shipped | Post-plan review — dispatchable when P5's commit lands |
| P7 | drafted | expert | shipped | Post-plan burndown — dispatchable when P6's review document lands |

## P1 — The serve verb: hp.py serves its pages over HTTP

Implements [the Harness profiler entry under Code
delta](ACTIVE_DESIGN.md#harness-profiler-1), first paragraph: the render flow becomes serve-first,
`serve` behind a `ThreadingHTTPServer` bound to `127.0.0.1` on a free port (`--port` pins one),
the URL on stdout, `/` the index of record files, `/page/<session-id>` the page the existing
builder returns, no file written, the server running until interrupted.

Scope: `devpro/harnesses/resources/claude/profiler/hp.py` (the `serve` verb: its `USAGE` line, its
branch in `main`, its handler and index code), `tests/test_devpro_profiler.py` (the new serve
tests). Nothing else in `hp.py` changes; `capture`, `tree`, `init` and `doctor` keep their
behavior.

Constraints, the whole package: Python 3 standard library only — the serve code adds only
stdlib imports; the 3.9 floor — `hp.sh:18`'s `RUNS_HP_PY` probe and the venv's own interpreter
(`justfile:87-90`: `/usr/bin/python3` 3.9.6 is the minspec) — so no syntax beyond 3.9 outside
annotations (`from __future__ import annotations` is already at `hp.py:8`); lint-clean under
`just lint`, which covers the whole `devpro/` tree (`justfile:223-225`); capture-side failures
stay silent — the `capture` branch's swallow (`hp.py:1351-1357`) is untouched.

Facts, each re-run before acting on it:

- The index's inputs: `list_sessions` (`hp.py:1083-1112`) returns every session with records from
  every `*-profiler` store — its `records`, its `first` and `last` moments (`:1103-1111`) — and
  filters out the sessions with none (`:1112`). A store the glob finds but cannot list raises out
  of `store.iterdir()` (`:1091`): that is the raised error the design replaces with a stated
  unreadable row. The handling is the index's, not `list_sessions`': `tree` (`:1146`) and `doctor`
  (`:1306`) keep today's behavior, and `list_sessions` itself is unchanged.
- The index row's fields: harness, session id, record count, first and last moments. `first`,
  `last`, `records` come from `list_sessions`; `harness` is read from a record's own field —
  `build_record` writes it (`hp.py:515`), `build_event_record` too (`:560`); every record in one
  session's trace carries the same one.
- The page: `/page/<session-id>` is the bytes `render_html(session)` returns (`hp.py:1049-1080`),
  which is exactly what `tree --format html` prints for one session (`:1173`, `return
  render_html(chosen[0])`).
- The free-port precedent, in the repository's tree but a separate project — pattern evidence,
  not a dependency: docdicer's kanban server binds `super().__init__((HOST, 0), _Handler)`
  (`docdicer/docdicer/kanban/server.py:104`), exposes the URL through its `url` property
  (`:114-115`), prints it on stdout flushed (`:341`) and serves until `KeyboardInterrupt`
  (`:342-348`). `hp.py`'s serve is its own stdlib
  implementation of the pattern; `ThreadingHTTPServer` appears nowhere in `devpro/` or `tests/`
  today (`git grep -n ThreadingHTTPServer -- devpro/ tests/ devtools/` → nothing).
- The verb's wiring: `USAGE` (`hp.py:1331-1335`) gains the serve line; `main`'s verb dispatch
  (`:1349-1368`) gains the branch.
- Masking and clip policy untouched: the serve surface renders records the capture already
  bounded — `LINE_LIMIT` bounds the written line in bytes, `name` and `session` clipped at the
  root before `result` and `args` give way (`serialize`, `hp.py:538-553`; the policy ARCHITECTURE
  states at `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:56-58`). The serve code adds no
  capture-side field and no new masking site.
- Reference search for the touched functions: `git grep -n "list_sessions" -- devpro/ tests/` →
  the def at `hp.py:1083` and the two callers at `:1146` and `:1306` (both keep today's behavior —
  the fact above); `git grep -n "render_html" -- devpro/ tests/` → the def at `hp.py:1049` and
  the one caller at `:1173`. No signature change; neither caller needs one.
- Tests pinning what P1 touches: the profiler suite runs through the launcher
  (`tests/test_devpro_profiler.py:77-86`), and
  `test_a_capture_writes_the_record_the_page_and_tree_read` (`:94-119`) pins the page-data keys
  `view.html` parses through `tree --format html` — unchanged by P1; the served page must satisfy
  the same keys, which the new /page test pins through the server. `USAGE`'s text is unpinned:
  `git grep -n "USAGE" -- tests/` → nothing.
- The serve tests' harness, stated so none is invented: a `Popen` variant of the suite's launcher
  pattern — the subprocess started the same way `_run` starts it (`tests/test_devpro_profiler.py:
  77-86`), but its stdout read incrementally until the URL line appears, each read bounded by a
  timeout, before any connecting step runs. The suite's own `_run` is `subprocess.run` and blocks;
  `serve` never exits, so a serve test that ran `_run` would hang. The launcher is the harness, not
  an in-process `main` call: `main`'s serve branch never returns, so an in-process test never
  reaches its own assertion.
- The new tests, each named by the test-precondition clause (`clauses.TEST_PRECONDITION` in
  `devpro/clauses.py`), one defect each:
  - the index test — runs `serve` through the harness above, connects to the URL it read, asserts
    one row per recorded
    session with harness, session id, record count, first and last moments, each linking to its
    `/page/<session-id>` — fails on the defect that the index omits a session the stores hold or
    renders a row that misstates what the store holds;
  - the unreadable-store test — makes one `*-profiler` store unreadable (mode `0o000`, the tests
    run unprivileged as `agent-user`; `store.is_dir()` needs only the parent's execute bit, so the
    failure surfaces at `store.iterdir()`, `hp.py:1091`) and constructs a second, readable store,
    connects to the URL it read, and asserts the response is 2xx with the index naming the
    unreadable store as such and the readable store's sessions rendered — fails on the defect that
    one bad directory blanks the index or raises out of the handler. The test restores the mode
    before returning: `tmp_path`'s teardown cannot unlink a `0o000` directory's contents and
    errors after the test has passed;
  - the page test — asserts `/page/<id>`'s bytes equal `tree --format html`'s output for the same
    session modulo the one trailing newline `print` adds (`hp.py:1361` passes `tree`'s output
    through `print`; the served bytes are `render_html`'s return) — fails on the defect that the
    served page diverges from the page the file-redirect flow produces.

Work:

1. Write the serve verb: the `USAGE` line, the `main` branch, and the handler — bind, print the
   URL once on stdout, flushed, before the serve loop (the precedent prints with `flush=True`,
   `server.py:341`), serve until interrupted; `/` the index inline from `list_sessions` with
   unreadable stores as stated rows; `/page/<session-id>` from `render_html`, no file written.
2. Add the three tests above to `tests/test_devpro_profiler.py`, docstring naming each defect.
3. Run the gate, then lint.

Done-line: `just test`, then `just sweep-python`, then `just lint`. One commit closes the package.

## P2 — The call tree never shows an empty tree under a calls header

Implements [the Harness profiler entry under Code
delta](ACTIVE_DESIGN.md#harness-profiler-1), second paragraph, first decided change: a session of
nothing but tool calls renders those calls as its calls content — the call tree the skill and
agent calls build stays empty there, and the page never shows an empty tree under a calls header.

Scope: `devpro/harnesses/resources/claude/profiler/view.html` — the call tree's default view only:
the `Call tree` section (`view.html:54-55`) and `drawTree` with its `shownCall` filter
(`view.html:337-370`). `hp.py` untouched; the page-data contract unchanged.

Facts, each re-run before acting on it:

- Today's default view: without the every-tool-call checkbox, `shownCall` shows only Skill and
  Agent calls plus compactions — `view.html:339`: `const shownCall = (c) => all || c.tool ===
  'Skill' || c.tool === 'Agent';` — so a session of nothing but tool calls draws the header row
  alone under the `Call tree` heading (`view.html:54`): an empty tree under a calls header.
- The decided behavior: that session's calls render as the call tree's rows — the content the
  every-tool-call view draws them as. The mechanism — a fallback when the filtered view yields no
  rows, or the default drawn from the data — is the coder's call; what must hold is the observable
  outcome: no session renders an empty tree under the calls header, and a session that does have
  Skill or Agent calls keeps today's default view unchanged.
- The toolbar line (`view.html:52`) states the default view's content — "Without it: skills,
  subagents and compactions, like `harness-profiler tree`". Where the fallback changes that
  content, the line stays truthful; its wording is the coder's call.
- No test pins the call tree's rendering: `git grep -n "Call tree\|drawTree\|shownCall" -- tests/`
  → nothing. The profiler tests parse the page's data only (`_page_data`,
  `tests/test_devpro_profiler.py:89-91`); no runner renders `view.html` — the TypeScript runners
  under `tests/` drive the capture, the masks and `serialize`, not the page. No test is added:
  the rendering runs in the browser, and the repo holds no DOM harness for it. The defect the
  change closes is observed on the serve surface P1 builds and in the user's live session (the
  note at the plan's opening).
- The page-data keys stay as the pin holds them (`_PAGE_KEYS`, `_CALL_KEYS`,
  `tests/test_devpro_profiler.py:52-66`): the change is rendering-only.
- The text tree is out of scope: the skill's Answer section already handles the header-alone text
  tree (`devpro/definitions/skills/show_profile.py:61-64`), and the design's decided change names
  the page.

Work:

1. Change `drawTree` so the decided behavior holds: a tool-call-only session's calls render as the
   call tree's rows; sessions with Skill or Agent calls keep today's default view; the toolbar
   line stays truthful.
2. Run the gate, then lint — the page-data pin rides `just test`.

Done-line: `just test`, then `just sweep-python`, then `just lint`. One commit closes the package.

## P3 — The show-profile skill serves first

Implements [the Harness profiler entry under Code
delta](ACTIVE_DESIGN.md#harness-profiler-1), the skill sentence: "The skill body's instruction
changes to serve-first: run `profiler/hp.sh serve`, hand the user the URL, with the file-redirect
demoted to a one-line mention for one-off exports."

Scope: `devpro/definitions/skills/show_profile.py` — `_BODY` only (`show_profile.py:15-64`);
`_DESCRIPTION` and the `Definition` record unchanged; no other definition.

Facts, each re-run before acting on it:

- The body today renders to a file and hands over a path — quoted, `show_profile.py:41-43`:
  `sh HP tree` and `sh HP tree --format html > .devpro-temp/harness-profile.html`, then
  `show_profile.py:46-50`'s deliver-the-page section: `open`, `xdg-open`, `start`, or an artifact.
  The serve-first rewrite replaces both: run the launcher's `serve`, hand the user the printed
  URL, with the file redirect demoted to a one-line mention for one-off exports. The
  deliver-the-page section's fate is the rewrite's, not left open: serve-first writes no file, so
  its opener instructions — `open`, `xdg-open`, `start`, the artifact attachment — are removed by
  the rewrite and nothing of them survives inside the one-line mention, which names the redirect
  alone.
- What pins what: `test_the_profile_skill_renders_under_every_harness`
  (`tests/test_devpro_install.py:491-495`) pins that the skill renders under every harness —
  unaffected by a body rewrite; no test pins the body's text (`git grep -n "harness-profile.html"
  -- tests/` → nothing; the one hit in `devpro/` is the body's own line). The cross-reference
  guard reads every definition body (`tests/test_cross_references.py:1-16`), so the rewritten body
  keeps other definitions' names out of its prose or spelled through the reference mechanism the
  guard accepts — the guard runs under `just test`.
- The sections the design does not name stand — Locate (`show_profile.py:19-37`), the init
  paragraph (`:32-35`), the Answer section (`:52-64`) — the deliver-the-page section excepted,
  whose fate the fact above states. Where the serve-first flow reorders the standing sections, the
  wording moves, the rules do not change; the Answer's counts still come from the tree's text.

Work:

1. Rewrite `_BODY`'s render and deliver instructions to the serve-first flow the design states,
   the file redirect demoted to a one-line mention; everything the design does not name stands.
2. Run the gate, then lint.

Done-line: `just test`, then `just sweep-python`, then `just lint`. One commit closes the package.

## P4 — The justfile gains dev-profiler

Implements [the Harness profiler entry under Code
delta](ACTIVE_DESIGN.md#harness-profiler-1): "The repository's justfile gains the runner target
`dev-profiler` running the source-tree `hp.sh serve`, the way `dev-kanban` wraps docdicer's
serve."

Scope: `justfile` — one recipe beside `dev-kanban`.

Facts, each re-run before acting on it:

- The wrapping form, quoted (`justfile:324-326`):
  ```
  [doc("serve the kanban board using hosted docdicer")]
  dev-kanban:
    @just dev-dd kanban
  ```
  `dev-profiler` wraps the source-tree launcher the same way — one recipe, a `[doc(...)]` line,
  running `devpro/harnesses/resources/claude/profiler/hp.sh serve`.
- The launcher is executable in the source tree (`git ls-files -s
  devpro/harnesses/resources/claude/profiler/hp.sh` → `100755`), so the recipe runs it directly;
  `serve` prints the URL on stdout and runs until interrupted (P1), like `dev-kanban`'s server.
- No test pins the runner recipes: `git grep -n "dev-kanban" -- tests/ devpro/` → nothing.
- A `justfile` edit selects every test surface — `justfile:266`, `justfile ALL` in
  `TEST_SURFACE_MAP` — because a change to a recipe cannot be validated by skipping the runner
  (`justfile:243-247`). That is why the done-line below runs the gate whole rather than
  `test-changed`.

Work:

1. Add the `dev-profiler` recipe beside `dev-kanban`: the `[doc(...)]` line and the one
   invocation of the source-tree launcher's `serve`.
2. Run the gate.

Done-line: `just test`, then `just sweep-python`. One commit closes the package.

## P5 — The three delta pairs applied

Implements [the Shipped files entry](ACTIVE_DESIGN.md#shipped-files) and [the Harness profiler
entry](ACTIVE_DESIGN.md#harness-profiler): each pair's `becomes` block replaces its from block in
its target, verbatim, each run of whitespace read as one space, no composition. The labels the
blocks carry (`**As it stands:**`, `**Becomes:**`) are not written into the target.

Scope: `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

Facts, each re-run before acting on it:

- The delta check today: `just dev-check-design-deltas-applied` → `pairs: 3, landed: 0, pending:
  3, drifted: 0, conflicting: 0, problems: 0`, exit 1, with the three pair lines at
  `ACTIVE_DESIGN.md:15` (target `shipped-files.md`), `:37` and `:54` (target
  `harness-profiler.md`). P5's application moves all three to landed.
- The from blocks sit in their targets today, verified by `just dev-check-design` → `entries: 3,
  problems: 0`, exit 0. Their exact sites: the SPEC pair's from is
  `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:98-100` (the profiler payload sentence,
  ending "as text or as a self-contained HTML page"); ARCH pair 1's from is
  `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:9-11` (the Resources sentence's verb
  list, ending "no dependency; and" — line 12 opens the `view.html` sentence the from block does
  not contain); ARCH pair 2's from is
  `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:25` (the one line `**The skill.**
  `show-profile` ships as a rendered skill definition under `devpro/definitions/skills/`,`, design
  line 57 — lines 26-28 continue the paragraph and are not in the from block) — its becomes block
  ends with that same line, so the application inserts the Serving paragraph before it.
- No pair block carries a relative link (checked `ACTIVE_DESIGN.md:15-31`, `:37-52`, `:54-72`), so
  nothing is rebased.
- No test pins either target's text: `git grep -n "self-contained HTML page" -- tests/ devpro/`
  → nothing. P5 changes no code, so no test can break; P1 through P4 have landed, so the
  documents' claims hold as the commit lands them.

Work:

1. Apply the SPEC pair's becomes block over `shipped-files.md:98-100` verbatim.
2. Apply ARCH pair 1's becomes block over `harness-profiler.md:9-11` verbatim.
3. Apply ARCH pair 2's becomes block over `harness-profiler.md:25` verbatim.
4. Run the delta check: it must report `landed: 3, pending: 0, problems: 0`, exit 0.

Done-line: `just dev-check-design-deltas-applied` (landed: 3), then `just dev-check-links`. One
commit closes the package.

## P6 — Post-plan review

The reviewers are given the project documents and the design, not the plan, and review the changes
and their tests against the project's standards and fitness for purpose. Each writes their own
review in the scratch directory, independently, at `.devpro-temp/p6-review-<seat>.md` — one file
per seat, named for it — and the session synthesizes them into `ACTIVE_PLAN_REVIEW.md`, never
diced, de-duplicating findings and reconciling them into one account.

- `devpro-python-coder` — `hp.py`'s serve verb and its tests, and `view.html`'s call tree, against
  the project's coding standards and the profiler's one-file, stdlib-only, 3.9-floor constraints;
- `devpro-architect` — the landed leaves (`shipped-files.md`, `harness-profiler.md`) against the
  code, SPEC.md against ARCHITECTURE.md, and the serve surface's structure;
- `devpro-prompt-engineer` — the `show-profile` skill's serve-first body, and the project documents
  the pairs landed.

Done-line: `just dev-check-links`. The review document and P6's Status row land in P6's commit.

## P7 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.

The burndown gets `devpro-prompt-engineer` usability review, then revision, before it is
`dispatchable`.

The landing acts, after the burndown's work:

1. The landing commit deletes `ACTIVE_DESIGN.md` (not diced, so no tree).
2. The landing commit deletes `ACTIVE_PLAN_REVIEW.md`.
3. The landing commit deletes this plan (`ACTIVE_PLAN.md`) — no next plan exists at that time. The
   deletion is P7's row resolution: no Status row is set, the row dies with the plan.

Done-line: `just test`, then `just sweep-python`, then `just dev-check-design-deltas-applied`
(landed: 3), then `just dev-check-links`, then `just dev-check-plan` — all before the landing
acts; the landing commit's tree carries the gate passing.

Every commit message and pull-request description carries the attribution line the development
skill states:

```
ai assisted by [devpro](https://github.com/benn-herrera/devpro) on opencode. submitter takes full responsibility.
```
