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
its `becomes` text, ACTIVE_DESIGN.md:376-396, stating the user's decided layout: the board as the
landing surface, the persistent top nav with the `devpro` brand and the view names, the persistent
server elements, the profiler view's frame band carrying the how-to-read legend and the
return-to-list control, ordinary drill-down navigation and the one shared presentation layer — is
NOT applied by this plan. Those layout clauses are the design's accepted target state, and the pass
that builds them is a later pass's own plan, drafted when the user directs it after this plan's
technical base has landed — not a package of this plan, and none of this plan's packages
half-specifies the frame. The pair stays pending until that pass applies it verbatim. What the plan
leaves knowingly broken: after P2, PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:99-103
still describes "the tool's `serve` subcommand" the code no longer has — the record the pending
pair replaces; the pass's application resolves it.

**Verification approach** (the design's decision, accepted): browser-level checks run agent-side
through Firefox headless only — the installed browser is the tool; no browser is downloaded, no
windowing compositor touched, Chromium stays unprovisioned. Firefox stands on this host
(Firefox.app in /Applications), so such a check runs and skips nowhere else. P1 itself performs no
browser-level check: its verification is the fetch-level suite, and browser-driven visual
verification — which needs a page that can be settled and judged rendered, more than
`--screenshot` can assert — is the roadmap ticket taken up with the UX pass, not an ad-hoc check
slotted into this plan.

**Route plumbing already settled in the record** — every package preserves these as they stand:

- `/page/<session-id>` renders that session's page in memory, the bytes `tree --format html`
  produces (PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:54-55); pinned by
  `test_the_served_page_is_the_html_the_file_flow_writes` (tests/test_devpro_profiler.py:610).
- The serve index states an unreadable store rather than raising (harness-profiler.md:55-56); pinned
  by `test_the_served_index_states_an_unreadable_store` (tests/test_devpro_profiler.py:586).
- A tool-call-only session's page shows the calls, never an empty tree under a calls header
  (harness-profiler.md:57-58).
- The index lists this project's sessions under a foreign `CLAUDE_PROJECT_DIR`: the rule is stated
  where it lives, the pinning test's own docstring (tests/test_devpro_profiler.py:567-570) —
  "`CLAUDE_PROJECT_DIR` at another project, as a claude shell sets it, while `serve` runs in this
  one: the index lists this project's sessions; an index that follows the variable serves the other
  project's stores, which for a terminal-launched server is the wrong repository" — pinned by
  `test_the_served_index_lists_its_own_project_under_a_foreign_project_dir` (:567).
- A tool-call-only session's page shows the calls (bullet 3) has no pinning test today —
  `git grep -n "empty tree" tests/test_devpro_profiler.py` returns nothing — so P1 adds one, named
  under *Visual checks and the calls-only pin* below.

## Status

| Package | State | Rating | Lifetime | Work |
| --- | --- | --- | --- | --- |
| | drafted | | | Kickoff: the stage-3 plan drafted from the design; the dashboard pair and frame/legend work left pending for the UX outcome |
| P1 | landed | expert | shipped | the dashboard verb: one loopback server, the traces panel and the board panel, the minimal frame |
| P1b | dispatchable | expert | shipped | the dashboard verb takes a positional project directory |
| P2 | drafted: dispatchable once P1b lands — the design entries it applies are in the design, and its kanban.md pair's becomes names the signature P1b builds | expert | shipped | the one front end: the old serving verbs retire, the record and the snippets' routing move with them |
| PR | dispatchable | expert | shipped | Post-plan review |
| PB | dispatchable | expert | shipped | Post-plan burndown |

## P1 — the dashboard verb: one server, two panels, the minimal frame

Lifetime: shipped. One commit closes it.

**Scope.** New: `devpro/dashboard/` — `cli.py` adding the `dashboard` verb (lazy, the
profiler-verb pattern: registering it imports nothing of the package), `server.py` the loopback
server and its routes. Edited: `devpro/cli.py` (verb registration beside the dicing and profiler
verbs), `justfile` (a `dev-dashboard` recipe beside `dev-profiler` and `dev-kanban`), and the tests:
the dashboard's own suite, and the import-placement invariant's exemption tuple
(`tests/test_devpro.py:1503` `test_every_import_is_at_module_level`) gaining
`devpro/dashboard/cli.py` as the fourth entry-point exception — the tuple exists for exactly this
pattern, and the lazy-dispatch test (:1568) requires the function-level import the tuple exempts.
Unchanged: `devpro/profiler/pages.py`'s rendering stays the traces panel's single home — the
dashboard imports it; no rendering logic moves or is copied. The board's model and moves stay in
`devpro/dicing/kanban/` — the dashboard imports them. `git grep -il dashboard -- devpro` returns
nothing: there is no incumbent dashboard to extend; this package is new.

**What it serves.** The traces panel: the profiler's index and `/page/<session-id>` pages, from the
`.profiler-*` stores, through `pages.py`'s `read_sessions`/`index_html`/`page_of` as they stand —
the settled route plumbing above is P1's contract, and the tests that pin it are P1's to keep
passing (the four bullets: the page-bytes test :610, the unreadable-store test :586, the
calls-only coverage the dashboard suite's fixtures carry, the foreign-project test :567). Until P2, the old `serve` still runs
alongside, unchanged. The board panel is the kanban server's serve surface whole, behavior for
behavior — so P2's retarget is a whole-surface move, never a re-implementation: the board page's
files (`devpro/dicing/kanban/assets/index.html`, `board.js`, `board.css`), the `/api/board` payload
with its long poll, the moves (`/api/to-design`, `/api/to-roadmap`, `/api/stop`), and the served
documents — every `.md` file at the project root's top level, every `.md` file beneath the
project's `PROJECT_DOCS/` and `ROADMAP_DESIGNS/` directories, and the active design's and active
plan's files as the form reads them, each read-only as `text/markdown` at the URL path that is the
file's path from the project root, an unreadable one answered 404 with the others still served, and
no other file of the project (PROJECT_DOCS/SPEC/dicing/kanban.md:32-38, quoted in its essentials).
The behaviors the existing tests pin: the page and its files
(`test_page_and_its_files_are_served`, tests/dicing/test_server.py:138), the served documents and
no other file (`test_a_served_file_is_served` :177, `test_no_other_file_is_served` :199,
`test_an_unreadable_served_file_is_refused_alone` :213), the payload
(`test_board_payload_is_the_model` :227), the moves (`test_a_card_moves_to_design_and_back` :340),
the host and CSP guards (`:552`, `:564`).

**The board page's paths are fixed by its rendering, and P1 fixes its URL**: the board page is
served at `/board/`, the trailing slash included, and its assets are named relative
(`index.html:7` `<link rel="stylesheet" href="board.css">`, `index.html:22` `<script
src="board.js"></script>`) while its API is root-absolute (`board.js:419` `moveTicket("/api/to-design",
…)`, `board.js:422` `/api/to-roadmap`, `board.js:492` `fetch("/api/board…")`, `board.js:524`
`/api/stop`). The dashboard serves the API at exactly those root paths and the assets at
`/board/board.css` and `/board/board.js`, where `/board/` resolves them. With the URL stated, the
resolution rule is mechanical; the assets and `board.js` are edited by no package in this plan.

**The minimal frame, stated to the byte.** The dashboard's root is the existing traces index as it
stands, plus one link line: the dashboard's handler appends, to the index page's body, the literal
line `<p><a href="/board/">Board</a> — the project's kanban board</p>` immediately before the
template's closing `</html>` (pages.py:711-727's `INDEX` ends with `</table>` then `</html>`), and
serves that page at `/` as it serves it today. No outer frame, no legend, no inner-frame structure,
no navigation beyond that line: every one of those is the later package's, in the design's amended
text, and the line is replaced wholesale there.

**The loopback bind is the rule** (harness-profiler.md:49-51): `127.0.0.1` only, nothing loaded
from the network, the URL printed once on stdout for cmd-clicking. The dashboard keeps both
surfaces' existing protections: the kanban handler's host-header check and CSP
(`tests/dicing/test_server.py:552`, `:564`) travel with the board panel.

**Verification.** The dashboard's verification is its fetch-level suite (`tests/dashboard/`):
every served path — the root with the board link, `/page/<session-id>`, `/board/` and its assets,
the API endpoints, the served documents — is fetched and asserted against fixtures, so a page that
fails to serve fails the suite. No browser-level visual check is in this plan's scope; the
roadmap's browser-driven visual verification ticket carries that work, taken up with the UX pass.

**The calls-only composition.** The suite's fixtures are tool-call-only sessions rendered through
every served path — index, `/page/<session-id>`, the API payload
(`tests/dashboard/test_server.py:25-50`) — so the calls-only render is covered where the earlier
draft's separate test would have duplicated it; no dedicated test is added, and the suite's
page-bytes pin (`test_the_served_page_is_the_html_the_file_flow_writes`,
tests/test_devpro_profiler.py:610) holds the served page to what the file flow writes.

**Facts.**
- `git grep -il dashboard -- devpro` → no output. No existing front end to absorb; new package.
- `git grep -l IndexHandler -- devpro tests` → devpro/profiler/pages.py only — the profiler's HTTP
  layer moves under the dashboard; its rendering functions stay put.
- `git grep -l run_kanban -- devpro tests` → devpro/dicing/cli.py, devpro/dicing/kanban/server.py,
  tests/dicing/test_server.py. `git grep -l KanbanServer -- devpro tests` →
  devpro/dicing/kanban/server.py, tests/dicing/test_server.py. P1 touches none of these: the old
  board server still runs, and its tests still pass, until P2.
- The profiler verb registers lazily (devpro/cli.py:45, `PROFILER_VERB`) and its subcommands parse
  at dispatch (devpro/profiler/cli.py:16-20) — the pattern the dashboard verb follows.
- The board model reads `ROADMAP.md`, the active design and plan through `read_board`
  (devpro/dicing/kanban/board.py:163) and its moves write documents (board.py's module docstring) —
  the dashboard's board panel is the same board, served; no second board model.

**Done-line.** `just test devpro`, then `just lint`, run once at the package's end. `just test
devpro` runs the whole pytest surface over `tests/` (devtools/scripts/test.sh:34, `devpro) dirs=(tests)`),
so it covers the profiler suite, the dicing suite and the dashboard suite.

## P1b — the dashboard verb takes a positional project directory

Lifetime: shipped. One commit closes it.

**Scope.** Edited: `devpro/dashboard/cli.py` — the verb's positional, optional, following the
verb's argparse conventions; `devpro kanban [<project-dir>]`'s positional is the pattern
(`devpro/dicing/cli.py:110-120`:
`board.add_argument("project_dir", nargs="?", metavar="project-dir", …)`), so the dashboard's is
declared the same way; `devpro/dashboard/server.py` — `serve` takes the directory and passes it to
`dashboard_root(directory)`, which already accepts one; and the tests. Unchanged: the resolution
rule itself — the positional, when given, is resolved by the same `git_root` walk `dashboard_root`
uses; the board panel and the traces panel both read the resolved root, no panel re-resolving.

**Facts.**
- `git grep -n "def serve" -- devpro/dashboard/server.py` → `devpro/dashboard/server.py:195: def
  serve(port: int) -> None:` — the current signature takes the port alone. Its caller:
  `git grep -n "serve(args" -- devpro` → `devpro/dashboard/cli.py:36:    serve(args.port)`, the
  verb's `run` dispatch — the one caller: every other `serve(` hit in `git grep -n "serve(" --
  devpro tests` is the profiler's own serve (its verb call at devpro/profiler/cli.py:63 and its
  definition at pages.py:777, retired at P2), a test fixture named `serve`, or its call sites —
  none this function's caller.
- `git grep -n "def dashboard_root" -- devpro/dashboard/server.py` → `devpro/dashboard/server.py:56:
  def dashboard_root(directory: Optional[str] = None) -> str:` — the directory parameter exists
  already; the change passes the verb's positional to it, and the `git_root` walk it does
  (server.py:59) resolves the named directory by the same rule the cwd walk uses today.
- The kanban verb's positional declaration, the pattern the dashboard's follows:
  `devpro/dicing/cli.py:110-120` — `subparsers.add_parser("kanban", …)` then
  `board.add_argument("project_dir", nargs="?", metavar="project-dir", …)`.

**Tests.** A test serving a *named* directory's project — fixture projects A and B (the `project`
helper, tests/dashboard/conftest.py:31), the verb run with A named through `_serve_the_command`'s
subprocess pattern (tests/dashboard/test_server.py:290) with that subprocess's cwd outside A — B,
or any directory outside A, since launched inside A a server that ignores the positional still
serves A and the test passes vacuously — and the served index shows A's sessions and
not B's — TEST_PRECONDITION (devpro/clauses.py:170): it fails on a server that ignores the
positional and serves the cwd's project instead — the defect named: a `run` dispatch that passes
nothing to `serve`, so a server launched by another process from any CWD serves the wrong project.
The cwd-default behavior keeps its pins
(`test_dashboard_root_is_the_git_root_of_the_directory_it_runs_in`, tests/dashboard/test_server.py:265;
`test_the_command_prints_the_loopback_url_once_and_serves_the_project_it_runs_in`, :314).

**Sequencing.** P2 applies the kanban.md pair whose `becomes` names `devpro dashboard
[<project-dir>]` (the design's Kanban leaf alignment entry), so P1b lands before P2 dispatches.

**Done-line.** `just test devpro`, then `just lint`, run once at the package's end.

## P2 — the one front end: the old serving verbs retire

Lifetime: shipped. One commit closes it.

**Precondition.** The design carries the technical entries the user's approval of this plan
directs — the `dashboard` verb in Package and Command, and Dicing and Checks' verb list losing
`devpro kanban` (its verbs list PROJECT_DOCS/SPEC/dicing-and-checks.md:10, its exit line :15, its
repeatable outcome :27, its non-destructive outcome :29, its serve line :39; the board verb's line
in PROJECT_DOCS/SPEC/package-and-command.md:21-23), and the routing entries in the Subsystem Map
and Recipes moving the board's and the records' routing to the dashboard. The board's
own contract is aligned in the design as of this amendment — the Kanban leaf's entry
(`ACTIVE_DESIGN.md`, the `devpro dashboard [<project-dir>]` pair) — and P2 applies it with the
entries named above. Until those entries are applied and `just dev-check-design-deltas-applied`
passes for them, P2 is not done; P1b lands the code the entries name first.

**Scope — code.** Removed: `devpro/profiler/pages.py`'s `IndexHandler`, `serve` and
`parse_serve_args` (the HTTP layer P1's server replaces; `index_html`, `page_of`, `read_sessions`
and the rendering stay); the `serve` subcommand of the profiler verb (devpro/profiler/cli.py:62-64,
its USAGE line :27); the `kanban` verb (devpro/dicing/cli.py:110-118 and its run dispatch,
devpro/cli.py:41's list) and `devpro/dicing/kanban/server.py`'s `KanbanServer` and `run_kanban`.
Edited, text-in-code and printed surfaces included: `justfile` — `dev-profiler` (:306) and
`dev-kanban` (:310) give way to `dev-dashboard`;
`devpro/definitions/skills/docdicer.py` — the description's `(`kanban`)` clause (:17), the verb
list (:49) and the board paragraph (:58) all name the dashboard for the board;
`devpro/definitions/skills/guide.py` — the board rows (:36, :468) route the same way;
`devpro/definitions/skills/show_profile.py` — its module docstring's `serve` sentence (:4) and
both named sections, "## Serve the trace" (:40-51, the `sh HP serve` block and the flow it
describes) and "## Answer" (:52-60, whose :59 line reads "the URL `serve` printed"), send the
session to the dashboard verb;
`devpro/profiler/hooks.py` — `USAGE` (:56-62) is a string the bare `devpro profiler` call prints
(devpro/profiler/cli.py:74 `print(USAGE)`), so its `devpro profiler serve [--port <number>]` line
comes out and the change is text-in-code, not a format;
`devpro/dicing/__init__.py` — the module docstring's "and serve a board" (:2) reads the dashboard;
`tests/test_devpro_profiler.py` — the serve tests drive the dashboard (the `_serve` context
manager :130-175 launches the verb, not `serve`); `tests/dicing/test_server.py` — the server tests
target the dashboard's board panel, behavior for behavior. The profiler verb keeps `capture`,
`tree`, `init`, `doctor`.

**Scope — the record.** PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md: the **Serving.**
section (:48-58) names the dashboard verb with the same bind, unreadable-store and calls-only-page
statements; the serve subcommand's mentions at :15, :97, :123 read the dashboard.
PROJECT_DOCS/ARCHITECTURE/repo-layout.md:15: the `profiler/` row's subcommand list drops `serve`.
PROJECT_DOCS/ARCHITECTURE/recipes.md:45:
the `dev-kanban` retirement sentence names the recipe's replacement. PROJECT_DOCS/ARCHITECTURE/subsystem-map.md:
the docdicer skill's routing and the guide skill's board section name the dashboard. README.md:9:
the board screenshot's caption names the dashboard; README.md:48-49: the paragraph naming "The
`tree` and `serve` subcommands" reads `tree` and the dashboard. The SPEC delta pairs the design's
technical entries carry are applied verbatim per the design's application form.

**The known breakage this package leaves** is the pending pair's window, named in the staging
boundary: shipped-files.md:99-103 still describes the profiler's `serve` subcommand. **The
completeness sweep** backing every retirement site above:
`git grep -nP '\bserve\b' -- README.md PROJECT_DOCS devpro tests ':(exclude)*.pyc'`. Its hits,
filtered of the ordinary-English `serve` prose that names no retired surface (repo-layout.md:43
"no copy to serve from", guide.py:234, clauses.py:182, the agent-definition prose), are: the
harness-profiler.md :15/:97/:123 mentions, repo-layout.md:15, README.md:48, show_profile.py :4,
:43, :59, dicing/__init__.py:2, dicing/cli.py:112, profiler/cli.py :27/:43/:62-63, hooks.py:58,
pages.py :645/:777 and the two test files' serve surfaces — every one in the scope above. After
P2's edits the same sweep returns only the named breakage's line and that ordinary-English
remainder: nothing else is left.

**Facts.**
- `git grep -l run_kanban -- devpro tests` → devpro/dicing/cli.py, devpro/dicing/kanban/server.py,
  tests/dicing/test_server.py — all three are in scope above. `git grep -l KanbanServer -- devpro
  tests` → the server and its tests only.
- `git grep -l IndexHandler -- devpro tests` → devpro/profiler/pages.py — removed here, after P1's
  evidence.
- `git grep -n "HP serve" devpro/definitions/skills/show_profile.py` → :43 — the skill's one serve
  instruction; :46 and :59 name what `serve` printed.
- `git grep -n "dev-kanban"` outside the design → PROJECT_DOCS/ARCHITECTURE/recipes.md:45 and the
  justfile's :310 — both in scope; `just dev-devpro kanban` is the recipe body the replacement
  retires.
- The verb-phrase search and the bare-name search are separate facts: `git grep -n "devpro kanban"
  README.md devpro/definitions` → README.md:9, docdicer.py:49, guide.py:468 — the routing and
  caption sites above; `git grep -n kanban devpro/definitions/skills/docdicer.py` → :17, :49, :58 —
  the :58 line quoted: "`kanban` serves a live board of the project's roadmap, design and plan.
  Offer to run it as a background process, or hand the user the command line; the user chooses."
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
