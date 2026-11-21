# devpro absorbs its tooling — stage 3: the dashboard's technical substrate

Design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — read whole; its stage marks are authoritative. This
plan applies what the design marks to stage 3: the dashboard's technical substrate — one loopback
server as devpro's single HTTP front end, serving the existing profiler pages and the existing
kanban board rendering as its two panels. The stage-1 and stage-2 pairs are landed (`8ed0f88` and
the stage-1 landing); the profiler is devpro's own code reading `.profiler-*` stores. DRAFT for the
user's approval: nothing dispatches from this file yet, and nothing is committed from it.

**Decision this plan lands** (strike it in approval where wrong): the dashboard is a new `devpro
dashboard` verb — one loopback server, `--port` as the profiler's `serve` takes one — and it is
devpro's only web server: when P2 lands, `devpro profiler serve` and `devpro kanban` have retired,
their serving jobs done by the dashboard's panels. The design's accepted pending pair names it —
"the dashboard, devpro's one loopback server for the web interface" — and the landed no-`devpro-kanban`
snippet decision already treats the board as the dashboard's panel
([Shipped files](ACTIVE_DESIGN.md#shipped-files--the-docdicer-package-retires-its-runner-shortcuts-return-the-profilers-and-dashboards-decisions-stages-2-4),
PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:65). The pre-release rule has no compatibility
shim: git is the rollback. P2 retires the old verbs only after P1's evidence shows the dashboard
doing their job.

**Staging boundary — the pending pair and the frame/legend work.** The design's dashboard pair —
its `becomes` text, ACTIVE_DESIGN.md:281-287, quoted: "the dashboard, devpro's one loopback server
for the web interface, renders the record files in memory as one panel of a site whose other panel
is the project's board, the how-to-read legend served once in an outer frame, a record selection
changing the inner frame only and the inner frame's top-level view the all-records list" — is NOT
applied by this plan. Its layout clauses are the UX discussion's subject, which runs concurrently:
the outer frame's presentation, the landing surface, the navigation structure and the legend
placement are all awaiting that outcome. The pair stays pending; a later package — under a later
plan, in the design's amended text — applies it verbatim and builds the frame and legend work it
describes. This plan's note is the whole of that boundary here: no package below half-specifies the
frame. What the plan leaves knowingly broken: after P2, PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:99-103
still describes "the tool's `serve` subcommand" the code no longer has — the record the pending
pair replaces; the pair's application resolves it.

**Verification approach** (the design's decision, accepted): browser-level checks run agent-side
through Firefox headless only, `--headless --screenshot` — "the stage's visual checks screenshot
real pages with no operator involvement, no sandbox change, and no browser download: the installed
browser is the tool" (the Shipped-files entry's *dashboard's visual verification* paragraph,
ACTIVE_DESIGN.md:289-296, landed as `292c367`). Chromium stays unprovisioned. Firefox stands on this
host (Firefox.app in /Applications), so the checks run and skip nowhere else.

**Route plumbing already settled in the record** — every package preserves these as they stand:

- `/page/<session-id>` renders that session's page in memory, the bytes `tree --format html`
  produces (PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:54-55); pinned by
  `test_the_served_page_is_the_html_the_file_flow_writes` (tests/test_devpro_profiler.py:610).
- The serve index states an unreadable store rather than raising (harness-profiler.md:55-56); pinned
  by `test_the_served_index_states_an_unreadable_store` (tests/test_devpro_profiler.py:586).
- A tool-call-only session's page shows the calls, never an empty tree under a calls header
  (harness-profiler.md:57-58).
- The index lists this project's sessions under a foreign `CLAUDE_PROJECT_DIR`
  (harness-profiler.md:745's rule; pinned by `test_the_served_index_lists_its_own_project_under_a_foreign_project_dir`,
  tests/test_devpro_profiler.py:567).

## Status

| Package | State | Rating | Lifetime | Work |
| --- | --- | --- | --- | --- |
| | drafted | | | Kickoff: the stage-3 plan drafted from the design; the dashboard pair and frame/legend work left pending for the UX outcome |
| P1 | drafted | expert | shipped | the dashboard verb: one loopback server, the traces panel and the board panel, the minimal frame |
| P2 | drafted | expert | shipped | the one front end: the old serving verbs retire, the record and the snippets' routing move with them |
| PR | drafted | expert | shipped | Post-plan review |
| PB | drafted | expert | shipped | Post-plan burndown |

## P1 — the dashboard verb: one server, two panels, the minimal frame

Lifetime: shipped. One commit closes it.

**Scope.** New: `devpro/dashboard/` — `cli.py` adding the `dashboard` verb (lazy, the
profiler-verb pattern: registering it imports nothing of the package), `server.py` the loopback
server and its routes. Edited: `devpro/cli.py` (verb registration beside the dicing and profiler
verbs), `justfile` (a `dev-dashboard` recipe beside `dev-profiler` and `dev-kanban`), and the tests.
Unchanged: `devpro/profiler/pages.py`'s rendering stays the traces panel's single home — the
dashboard imports it; no rendering logic moves or is copied. The board's model and moves stay in
`devpro/dicing/kanban/` — the dashboard imports them. `git grep -il dashboard -- devpro` returns
nothing: there is no incumbent dashboard to extend; this package is new.

**What it serves.** The traces panel: the profiler's index and `/page/<session-id>` pages, from the
`.profiler-*` stores, through `pages.py`'s `read_sessions`/`index_html`/`page_of` as they stand —
the settled route plumbing above is P1's contract, and the tests that pin it are P1's to keep
passing (the four tests named above; the serve tests drive the dashboard after P2 — until then the
old `serve` still runs, unchanged). The board panel: the existing kanban rendering —
`devpro/dicing/kanban/assets/index.html`, `board.js`, `board.css` served as the board page's files,
the `/api/board` payload with its long poll, and the moves (`/api/to-design`, `/api/to-roadmap`,
`/api/stop`) — the rendering and API the existing tests pin
(`tests/dicing/test_server.py`, `serve` fixture: `test_page_and_its_files_are_served` :138,
`test_board_payload_is_the_model` :227, `test_a_card_moves_to_design_and_back` :340,
`test_every_response_forbids_sniffing_and_the_pages_restrict_their_sources` :564).

**The board page's paths are fixed by its rendering**: the page's assets are named relative
(`index.html:7` `<link rel="stylesheet" href="board.css">`, `index.html:22` `<script
src="board.js"></script>`) and its API root-absolute (`board.js:419` `moveTicket("/api/to-design",
…)`, `board.js:422` `/api/to-roadmap`, `board.js:492` `fetch("/api/board…")`, `board.js:524`
`/api/stop`). The dashboard serves the API at exactly those root paths and the assets where the
board page's own URL resolves them; the assets and `board.js` are edited by no package in this plan.

**The minimal frame.** The dashboard's root is the existing traces index as it stands, plus one
link line naming the board panel — the least the two-panel site can be. No outer frame, no legend,
no inner-frame structure, no navigation beyond the link: every one of those is the later package's,
in the design's amended text. The link line is the only frame commitment this plan makes, and the
later work replaces it wholesale.

**The loopback bind is the rule** (harness-profiler.md:49-51): `127.0.0.1` only, nothing loaded
from the network, the URL printed once on stdout for cmd-clicking. The dashboard keeps both
surfaces' existing protections: the kanban handler's host-header check and CSP
(`tests/dicing/test_server.py:552`, `:564`) travel with the board panel.

**Visual checks** (the design's verification decision). A test in `tests/` screenshots the
dashboard's real pages through Firefox headless — `--headless --screenshot`: the root with the
board link, a `/page/<session-id>` page of a fixture session, and the board page — asserting each
screenshot is produced and non-trivial in size. TEST_PRECONDITION: it fails on a dashboard whose
pages render blank or fail to load — the defect no fetch-based test catches. It skips where Firefox
is absent, naming the skip. No browser is downloaded, no windowing compositor is touched.

**Facts.**
- `git grep -il dashboard -- devpro` → no output. No existing front end to absorb; new package.
- `git grep -l IndexHandler` → devpro/profiler/pages.py only — the profiler's HTTP layer moves
  under the dashboard; its rendering functions stay put.
- `git grep -l run_kanban` → devpro/dicing/cli.py, devpro/dicing/kanban/server.py,
  tests/dicing/test_server.py. `git grep -l KanbanServer` → devpro/dicing/kanban/server.py,
  tests/dicing/test_server.py. P1 touches none of these: the old board server still runs, and its
  tests still pass, until P2.
- The profiler verb registers lazily (devpro/cli.py:45, `PROFILER_VERB`) and its subcommands parse
  at dispatch (devpro/profiler/cli.py:16-20) — the pattern the dashboard verb follows.
- The board model reads `ROADMAP.md`, the active design and plan through `read_board`
  (devpro/dicing/kanban/board.py:163) and its moves write documents (board.py's module docstring) —
  the dashboard's board panel is the same board, served; no second board model.

**Done-line.** `just test devpro`, then `just lint`, run once at the package's end. `just test
devpro` runs the whole pytest surface over `tests/` (devtools/scripts/test.sh:34, `devpro) dirs=(tests)`),
so it covers the profiler suite, the dicing suite and the new visual check.

## P2 — the one front end: the old serving verbs retire

Lifetime: shipped. One commit closes it.

**Precondition.** The design carries the technical entries the user's approval of this plan
directs — the `dashboard` verb in Package and Command, and Dicing and Checks' verb list losing
`devpro kanban` (its verbs list PROJECT_DOCS/SPEC/dicing-and-checks.md:10, its exit line :15, its
repeatable outcome :27, its non-destructive outcome :29, its serve line :39; the board's own
contract PROJECT_DOCS/SPEC/dicing/kanban.md aligned to serving as the dashboard's panel; the board
verb's line in PROJECT_DOCS/SPEC/package-and-command.md:21-23). Until those entries are in the
design and `just dev-check-design` passes, P2 is not dispatchable.

**Scope — code.** Removed: `devpro/profiler/pages.py`'s `IndexHandler`, `serve` and
`parse_serve_args` (the HTTP layer P1's server replaces; `index_html`, `page_of`, `read_sessions`
and the rendering stay); the `serve` subcommand of the profiler verb (devpro/profiler/cli.py:62-64,
its USAGE line :27); the `kanban` verb (devpro/dicing/cli.py:110-118 and its run dispatch,
devpro/cli.py:41's list) and `devpro/dicing/kanban/server.py`'s `KanbanServer` and `run_kanban`.
Edited: `justfile` — `dev-profiler` (:306) and `dev-kanban` (:310) give way to `dev-dashboard`;
`devpro/definitions/skills/docdicer.py` — the routing names the dashboard for the board (:49,
:58); `devpro/definitions/skills/guide.py` — the board rows (:36, :468) route the same way;
`devpro/definitions/skills/show_profile.py` — the "Serve the trace" section (:40-59) sends the
session to the dashboard verb instead of `sh HP serve`; `tests/test_devpro_profiler.py` — the serve
tests drive the dashboard (the `_serve` context manager :130-175 launches the verb, not `serve`);
`tests/dicing/test_server.py` — the server tests target the dashboard's board panel, behavior for
behavior. The profiler verb keeps `capture`, `tree`, `init`, `doctor`.

**Scope — the record.** PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md: the **Serving.**
section (:48-58) names the dashboard verb with the same bind, unreadable-store and calls-only-page
statements; the serve subcommand's mentions at :15, :97, :123 read the dashboard. PROJECT_DOCS/ARCHITECTURE/recipes.md:45:
the `dev-kanban` retirement sentence names the recipe's replacement. PROJECT_DOCS/ARCHITECTURE/subsystem-map.md:
the docdicer skill's routing and the guide skill's board section name the dashboard. README.md:9:
the board screenshot's caption names the dashboard. The SPEC delta pairs the design's technical
entries carry are applied verbatim per the design's application form.

**The known breakage this package leaves** is the pending pair's window, named in the staging
boundary: shipped-files.md:99-103 still describes the profiler's `serve` subcommand. Nothing else
is left.

**Facts.**
- `git grep -l run_kanban` → devpro/dicing/cli.py, devpro/dicing/kanban/server.py,
  tests/dicing/test_server.py — all three are in scope above. `git grep -l KanbanServer` → the
  server and its tests only.
- `git grep -l IndexHandler` → devpro/profiler/pages.py — removed here, after P1's evidence.
- `git grep -n "HP serve" devpro/definitions/skills/show_profile.py` → :43 — the skill's one serve
  instruction; :46 and :59 name what `serve` printed.
- `git grep -n "dev-kanban"` outside the design → PROJECT_DOCS/ARCHITECTURE/recipes.md:45 and the
  justfile's :310 — both in scope; `just dev-devpro kanban` is the recipe body the replacement
  retires.
- `git grep -n "devpro kanban" README.md devpro/definitions` → README.md:9;
  docdicer.py:49, :58; guide.py:468 — the routing and caption sites above.
- The profiler tests' serve surface: tests/test_devpro_profiler.py:138 launches `["sh",
  str(launcher), "serve"]` through the launcher; the shim at :100 runs this checkout's devpro —
  the same shim drives the dashboard verb after the change.

**Done-line.** `just test devpro`, then `just lint`, then `just dev-check-links`, then `just
dev-check-design`, then `just dev-check-design-deltas-applied` — run once, at the package's end,
the last two over the design's technical entries P2 applies.

## PR — Post-plan review

Lifetime: shipped. One commit closes it — the one that adds the review document.

The reviewers receive the project documents and the design, not this plan, and review the changes
and their tests against the project's standards and fitness for purpose: the coder seat for the
changed Python, `devpro-architect` for the structure and the project documents' claims about the
code, `devpro-tech-writer` for the README and human-facing guides, and `devpro-prompt-engineer` for
the model-facing skill texts. Each writes their review in the scratch directory; the session
synthesizes them into `ACTIVE_PLAN_REVIEW.md` without waiting for an approval between the last
report and the write-up. The review document is deleted in the commit that lands the plan.

**Done-line.** `just dev-check-links` — the review document is a tracked top-level markdown file
its links must resolve in; no other target checks it.

## PB — Post-plan burndown

Lifetime: shipped. One commit closes it.

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.

**Done-line.** `just dev-check-plan`, then `just dev-check-links`, then `just
dev-check-design-deltas-applied` — run once, at the package's end.
