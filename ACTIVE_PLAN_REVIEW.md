# ACTIVE PLAN REVIEW — stage 3, the dashboard

The post-plan review of the stage-3 plan's landed work: P1 (the dashboard verb), P1b (the
positional project directory), P2 (the one front end — the old serving verbs retire). Landing
commits `b7077d7`, `d7ad2b3`, `8ebd7b3`. Four independent seats reviewed the shipped changes
against the project documents and their own criteria; the seats were not given the plan.

**Seats:** architect, prompt-engineer, python-coder, tech-writer. **Gates run during review:**
`just test devpro` (1573 passed, 1 skipped), `just lint`, `just test docs` (352 links, 0 broken),
`just dev-check-design-deltas-applied` (76 landed, 2 pending, 0 drifted), plus a live dashboard
over a scratch project and a defect-reproduction probe (the `since` route, the move-error path).

The composition's structure is sound: no rendering copied, the retirement a real deletion, the
tests pin what the documents promise. The findings below are the defects.

## Findings

### Code

- **R1 — Critical.** `devpro/dicing/kanban/server.py:324-326`: a move's handler binds `root` on
  the same name the error branch exists to survive, so an `OSError` escaping a move raises
  `UnboundLocalError` instead of the 500 the module docstring promises; no test exercises the
  path. (coder)
- **R2 — Warning.** The board panel's long poll compares `since` against the server's version
  only: a client holding an older version waits out the 25 s poll against a board it already
  differs from. Pinned contrast: the fixed query-string route is correct; this is the payload
  comparison's own gap. (coder)
- **R3 — Warning.** The host guard is duplicated: the dashboard's guard (`devpro/dashboard/
  server.py:180-186`) runs first on every request, making the panel's own guard
  (`devpro/dicing/kanban/server.py:328-334`) dead in composition, with drifting 403 messages
  between the two. (architect)
- **R4 — Warning.** `DashboardServer.stop` (`devpro/dashboard/server.py:112-118`) has zero
  callers — a second home for the stop mechanism `POST /api/stop` already owns. (architect)
- **R5 — Warning.** A bad `--port` value prints a ~448 KB argparse choices error
  (`choices=range(0, 65536)` enumerating every legal value). (architect)
- **R6 — Warning.** The panel's spoofed `BaseServer` internals
  (`devpro/dicing/kanban/server.py:109-111`, `:142-143`) are written and read by nothing —
  pre-composition leftovers. (architect)

### SPEC and the contract documents

- **R7 — Warning.** `PROJECT_DOCS/SPEC/dicing/kanban.md:48`: the row refusing a non-directory
  `<project-dir>` with exit 2 has no implementation and no test — the check lived in the retired
  `devpro kanban` dispatch and went out with it; the dashboard path resolves a nonexistent named
  directory to itself and serves (`devpro dashboard /nonexistent-dir-xyz` verified printing a URL
  and serving). Smallest fix: delete the row, as the no-project-root row was, or carry the
  refusal into `devpro/dashboard/cli.py`. (prompt-engineer, architect)
- **R8 — Warning.** `PROJECT_DOCS/SPEC/dicing/kanban.md:50`: the cannot-listen row (exit 2)
  fails — `CannotListen` is a plain `Exception` caught nowhere on the dashboard path (traceback,
  exit 1); the `cannot read: <file>` row is likewise unformatted now. (architect)

### Human-facing texts

- **R9 — Critical.** `README.md:7-9`, `:45-53`: the user-facing mode's lead is unreachable —
  the README never gives the `devpro dashboard` command line, the board landing, the CLI-only
  start, or the stop; `dashboard` reaches the README only as a qualifier inside the profiler
  bullet, and the board screenshot's caption promises a board the root page does not serve (the
  root serves the traces index; the board-first landing is the design's deferred UX pass).
  (tech-writer)
- **R10 — Critical.** `README.md:141-146`, `devpro/definitions/skills/guide.py:468-469`,
  `PROJECT_DOCS/ARCHITECTURE/recipes.md:3-5`, `:44-47`: the "ask your agent" path hands only
  `--help`, and `dev-dashboard` is absent from the recipe list the agent would name. (tech-writer)
- **R11 — Critical.** `guide.py:468-469`, `devpro/definitions/skills/docdicer.py:58-61`: the
  dashboard is described as the board alone, and `--help` is offered as the command — the model
  routing the user asks for the dashboard cannot state its surface or its traces panel.
  (tech-writer)
- **R12 — Warning.** `guide.py:36`: the route row names a `dashboard` verb the docdicer skill's
  own description does not offer. (tech-writer)
- **R13 — Warning.** `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:49-61`: the Serving
  section omits the landing page, the `--port` default, the page stop, and the board's writes;
  a mid-sentence line break at `:52-53`; and `:100`, `:125-126` still attach "page reads" to
  `tree` where the served page reads the stores. (tech-writer, coder)
- **R14 — Warning.** `PROJECT_DOCS/ARCHITECTURE/repo-layout.md:11`, `:15`: the HTTP render still
  attributed to `devpro/profiler/pages.py`, and no `devpro/dashboard/` row exists.
  (tech-writer, coder)
- **R15 — Note.** `devpro/profiler/__init__.py:1`: the package docstring still says the profiler
  prints "a served site" — the half that was the retired `profiler serve`. (prompt-engineer)
- **R16 — Note.** The board panel's payload key `devpro_version` is undocumented in code and
  ARCHITECTURE; the panel seam (`after`, `panel_handler`) likewise. (coder)
- **R17 — Note.** An import-structure docstring credits the dashboard with a property it did not
  produce. (coder)
- **R18 — Note.** `devpro/dicing/kanban/assets/board.js:6`, `:11`: the page's static `<title>`
  and `<h1>` read the bare `kanban` where the leaf's Title-and-header contract says
  `<project> kanban`; `board.js:131` sets both dynamically, so the static text is only the
  pre-script frame. Pre-existing. (tech-writer)
- **R19 — Note.** Presentation and housekeeping: the retirement sentence in `recipes.md` is
  over-composed; a long spliced line in `README.md`; the duplicated CSP constant and `_send`
  bodies across the two servers; the dead `LOOPBACK` constant; a leftover debug print at
  `tests/dicing/test_server.py:256`; two project-root walks on either side of the panel/check
  seam; duplicated command-spawn helpers across the two test suites. (tech-writer, architect,
  coder)

## Corrections

Made during the burndown's PE usability review, each verified against the tree by the session
before the burndown's revision accepted it:

- **R1 is a phantom defect.** The `except OSError` branch (`devpro/dicing/kanban/server.py:323-326`)
  assigns `root` from `self.server.root` before any use, so no `UnboundLocalError` is reachable;
  `test_a_file_a_move_cannot_read_is_named_from_the_root` (`tests/dicing/test_server.py:401`)
  exercises exactly this path and passes, and a composed HTTP probe returned the promised
  `500 {"error": "cannot read: …"}`. The seat's evidence printed the branch's source but never
  observed the error. The original claim attributed to the seat is withdrawn.
- **R2 is a phantom defect.** `payload` (`devpro/dicing/kanban/server.py:151-155`) answers
  immediately whenever the client's `since` differs from the server's version
  (`wait_for(lambda: str(self._version) != since …)` returns at once) — a stale client is served
  the current payload without waiting. The seat misread its own probe's output. Withdrawn.
- **R18's cite is corrected**: the static `<title>` and `<h1>` are
  `devpro/dicing/kanban/assets/index.html:6` and `:11`, not `board.js:6`/`:11` (there a comment
  and a constant). The defect itself stands.

## Process notes

- The stage's done-line covered the prose it landed only by `dev-check-links`:
  `just test devpro` routes `README.md` and `PROJECT_DOCS/` to the docs surface
  (`TEST_SURFACE_MAP`), so no run in the plan checked the human-facing texts' content. The
  gap R9-R14 filled is structural: prose landed by a code package is reviewed by no gate the
  package's done-line names. (tech-writer)
- `dev-check-design`'s displaced-pair behavior required a re-anchor pass outside any done-line's
  wording until the plan's own revision added it (P2's done-line now carries it for this plan).
- The design's two remaining pending pairs are the deferred ones — the dashboard layout pair and
  the launcher pair — recorded for their own later passes, not open defects.
