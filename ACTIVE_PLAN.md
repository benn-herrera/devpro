# The board's running agents, the lifetime scale's durability, and the tuning data's new home

The plan from the accepted design `ACTIVE_DESIGN.md` (repository root, final form, accepted
2026-11-27; `just dev-check-design` passes over it — 12 entries, 0 problems). Its three changes:
the kanban board's agents column, the package lifetime scale renamed to durability
(shipped/persistent/transient), and the `!TUNING!` per-definition comment deleted with its data
re-homed to one `tuning.md` per install. No release is under way, so this plan names none.

Out of scope throughout: capturing board screenshots — the owner stages those separately; no
package adds code for it.

## Status

| Package | State | Rating | Lifetime | Notes |
|---|---|---|---|---|
| P1 | landed | mechanical | shipped | |
| P2 | landed | expert | shipped | |
| P3 | dispatchable | expert | shipped | |
| P4 | in progress | mechanical | persistent | parallel with code packages |
| P5 | dispatchable | mechanical | transient | no closing commit: untracked output |
| P6 | drafted | expert | persistent | dispatched when P1–P5 are `landed` |
| P7 | drafted | mechanical | persistent | drafting ticket |

## Sequencing

- P1, P2 and P3 share the working tree and its build: they run serially in that order. P4 touches
  only `PROJECT_DOCS/` paths and may run in parallel with any code package; it stages and commits
  only its own paths (`git commit -- <paths>`).
- P5 runs only after P1, P2 and P3 are accepted: it overwrites the reference slots
  `just render-diff` compares against (`reference retakes follow acceptance`), and all three change
  what the slots hold (P1 and P2 the rendered definitions, P3 the copied board assets).
- The checkpoint gate (CONVENTIONS, the gates): `just test`, then `just lint`, then
  `just sweep-python`, once before each checkpoint commit, never between edits.
- P6 is dispatched once every other package's row is `landed`; P7 is the burndown section's
  drafting ticket.

## Packages

### P1 The definition sources carry the durability scale

Applies the design's Code delta entry `the package lifetime scale — the definition sources`
verbatim: its quoted replacement texts are the edits, whole.

**Scope**

- `devpro/definitions/skills/development.py` — the *Plans* scale bullet (lines 181–187) and the
  *Scope* release rule (line 817).
- `devpro/definitions/skills/guide.py` — the *Lifetime* bullet (lines 328–330) and the
  *Lighter process* examples naming the retired values (lines 395 and 409: the quoted bullet, then
  the "lightest path is straight to an exploratory plan" line).
- The `{CHECKPOINT_GATE_TERM}` and `{SCRATCH_TERM}` placeholders stand where they stood.

**Facts** (run 2026-11-27)

- `git grep -n "exploratory\|throwaway" -- devpro devtools justfile PROJECT_DOCS tests README.md`
  returns the four lifetime-value sites in scope above plus eight more hits, each not a lifetime
  value and outside scope: `devpro/clauses.py:23` (the scratch paragraph's "throwaway builds" —
  rendered model-facing scratch-rule text, not a scale value), `devpro/clauses.py:305`
  (NEW_PROJECT_SETUP's "throwaway builds" — the same scratch rule in another clause), 
  `devtools/scripts/check-wheel.sh:3` and `justfile:119` and
  `PROJECT_DOCS/ARCHITECTURE/packaging.md:49` and `PROJECT_DOCS/ARCHITECTURE/recipes.md:33,36`
  (each a "throwaway venv" — the wheel check's disposable install venv, not a package lifetime).
- Quoted line, `devpro/definitions/skills/development.py:817`: `- Every package in the release's
  plans is shipped (SKILL.md, *Plans*): exploratory work is re-rated` — the *Scope* rule's retired
  half.

**Notes**

- The rendered definitions change, so the reference slots go stale until P5; `just render-diff`
  reporting that difference before then is expected, not a failure.
- No test pins the skill's scale wording (the search above); no fixture update follows.

**Done-line:** `just test devpro`, then `just lint`.

### P2 The tuning data rides on no rendered file

Applies the design's Rendering, Generated files and Installed tree deltas in code: the
`!TUNING!` banner line is deleted from every rendered file and the data moves to the tuning table.

**Scope**

- `devpro/render.py` — `tuning_text` (lines 97–107) and `tuning_line` (lines 109–111) are deleted;
  their calls in `_frontmatter` (line 129) and `_comment_banner` (line 135) drop the second banner
  line, and the docstrings that describe two banner lines (lines 125 and 133) name one.
- `devpro/install.py` — the install writes the tuning table at the install destination's root as
  `tuning.md`, once per install, replaced wholesale with the rest of the install. The write site is
  exact: the table is appended to the `renders` list as `(PurePosixPath("tuning.md"), text)` beside
  the guardrail registration, and `write_renders` (`devpro/render.py:316-327`) writes it verbatim —
  no harness form, no banner — at `root`, `harness_dir / ctx.bound_harness.plugin_dir`
  (`devpro/install.py:522`): `<project>/.claude/skills/devpro/tuning.md` under claude,
  `.opencode/plugins/devpro/tuning.md` under opencode, `skills/devpro/tuning.md` under mage. It is
  not in the replacement's pass-overs, so `_replaced` clears any earlier install's copy and the new
  one is written with the renders. Its content is the design's fields: the family's name, the
  effective category map, the stock list (`ctx.stock`, `none` when empty) and the harness, the same
  values `tuning_text` spelled — read from the `Render` the install already holds. The opencode
  entry's `stripBanner` (`index.ts:58`) strips leading `<!-- -->` comment lines only from the body
  files it registers; the tuning table is registered by nothing, so it survives byte-exact whether
  it carries comments or not, and it carries none.
- `devtools/render_diff.py` — `BANNER` and `COMMENT` (lines 37–38) become one line each
  (`b"# !GENERATED! from "`, `b"<!-- !GENERATED! from "`), and the module docblock's shape
  description names one banner line.
- `justfile` — the `render-diff` doc block (lines 182–198) quotes the one-line comment shape.
- `devtools/tests/test_render_diff.py`, `tests/render/test_frontmatter.py` (the banner-shape
  assertions at lines 129–219), `tests/install/conftest.py` (`_NEW_BANNER`, line 156) — updated to
  the one-banner shape; updating them is in scope.
- Comment-only touch-ups where the text describes the second banner line:
  `devpro/profiler/directives.py` lines 31–32 and `devpro/harnesses/resources/opencode/profiler.ts`
  lines 436–439. `GENERATED_BANNER_HEAD` stays `2` and the reason: the opencode comment carrier's
  banner is line 1 — within the head-2 search — and the claude/mage frontmatter carrier's banner is
  line 2 behind the opening `---` — exactly the head-2 search — so with the tuning line gone the
  `!GENERATED!` line still stands inside the first two lines of either carrier, and the constant
  needs no lowering.
- Out of scope: the tuning-*text*-at-anchors mechanism and its hole model (`TuningText`,
  `tests/render/conftest.py:185`) — the design deletes the tuning *line*, not the tuning text.

**Facts** (run 2026-11-27)

- `git grep -l "tuning_line"` → `devpro/render.py` only. `git grep -l "tuning_text"` →
  `devpro/render.py` only. No other module imports either name.
- `git grep -l "TUNING" -- justfile devpro devtools tests PROJECT_DOCS README.md` → ten files, each
  one side of this package's scope line:
  - In scope: `PROJECT_DOCS/ARCHITECTURE/banner.md` and `PROJECT_DOCS/SPEC/rendering.md` (P4's
    targets — the pairs delete the wording there), `devpro/render.py` (the deleted functions and
    their calls), `devtools/render_diff.py` (the shape tuples and docblock), 
    `devtools/tests/test_render_diff.py` (the banner fixtures, updated to one line),
    `tests/render/test_frontmatter.py` (the banner-shape assertions), `tests/install/conftest.py`
    (`_NEW_BANNER`), `justfile` (the `render-diff` doc block).
  - Stand: `tests/render/conftest.py` and `tests/render/test_families.py` — their hits are the
    tuning-*text* hole model (`TuningText`, `_TUNING_HOLES`, the anchor-filling clauses), which the
    design keeps; touching them would break the hole model, leaving them keeps the grep red for a
    reason this line states.
- `git grep -l "GENERATED_BANNER_HEAD"` → `devpro/harnesses/resources/opencode/profiler.ts` and
  `devpro/profiler/directives.py`; both keep the constant.
- The opencode entry's banner strip is generic over comment lines
  (`devpro/harnesses/resources/opencode/index.ts:58`, `stripBanner`) and needs no change.
- The stores the board's poll reads are named by `devpro/profiler/values.py` `TRACE_STORES`
  (`.profiler-claude`, `.profiler-opencode`) — recorded here for P3, not this package.

**Tests pinning the changed behavior** — the banner-shape assertions in
`tests/render/test_frontmatter.py`, the `_NEW_BANNER` fixture in `tests/install/conftest.py` and
the banner fixtures in `devtools/tests/test_render_diff.py`: updated in scope. A failing test on
behavior this package does not state it changes is reported as a finding, never edited to pass.

**Done-line:** `just test devpro`, then `just test dupe_sweep`, then `just lint`.

### P3 The board panel's agents column

Applies the design's Columns and cards, the agents column and Live following deltas in the board
panel, and the Code delta `Plan Status Form — the dispatch note's writer`.

**Scope**

- `devpro/profiler/read.py` — the running-dispatch derivation. Every read of a store stays in this
  module (its own docstring's rule, lines 1–7); the panel calls it and renders nothing here. The
  derivation reads records only: opencode's dispatch is opened by the `execute.after`
  acknowledgment and closed by the child's idle record with an empty `background`
  (`child_episodes`, lines 44–61, holds that end contract); claude's is opened by the `Agent`
  tool-call record naming `child_agent_id` and closed by the `SubagentStop` record, matched by the
  parent session, the agent type and the order of the records. The per-dispatch color is computed
  here, in the derivation — the fixed palette lives with it, assigned in opening-`at` order and
  stable while the dispatch runs — and each `agents` payload entry carries its `color`; the page
  reads the color, it does not compute it.
- `devpro/kanban/board.py` — the watched set gains the two store directories as two entries, not
  their records one by one (`watched_files`, lines 179–189): the watch list holds the two store
  paths, and the snapshot digests each store as one entry computed from its `os.scandir` stat data
  (each session file's name, `mtime_ns` and `size`), reading no record's bytes — an append to a
  session file or a new one changes that store's stat data and its digest, and the per-poll cost is
  one directory listing per store, never a read per record. The board's mode is read from the
  active plan's status table, the plan `read_board` already reads (lines 172–177).
- `devpro/kanban/server.py` — the payload gains `agents`, `mode` and, on package cards,
  `dispatch_colors` (`plan_columns` keeps its meaning, below). `plan_columns` becomes the mode's
  state words — `["drafted", "dispatchable"]` in planning, all four in execution — and `mode` is
  the mode's one home (`"planning"` | `"execution"`); the page prepends its fixed `roadmap`/`design`
  keys by mode and appends the `agents` column itself (lines 137–176; `POLL_SECONDS = 0.25` and
  `LONG_POLL_SECONDS = 25.0`, lines 54–55, stand). The dispatch-note join is server-side, where the
  plan form's reader rule lives: each card's `dispatch_colors` lists, in the running set's order,
  the colors of the running dispatches the row's State-cell note names — the note is read as
  identifiers by splitting it on whitespace, commas and semicolons into tokens, each token compared
  exactly to a dispatch's identifier; a substring or inflected match names nothing. An unreadable
  store is named on stderr as live following names an unreadable watched file (`_report`,
  lines 201–204).
- `devpro/kanban/assets/board.js` and `board.css` — the agents column last in both modes, one card
  per running dispatch linking `/page/<id>` where the identifier is a session id, and the dots on
  package cards drawn from the card's `dispatch_colors`; the column keys come from the payload's
  columns by mode.
- `devpro/definitions/skills/development.py` — the *Dispatch* bullet (lines 350–351) rewritten to
  the design's writer wording: the dispatch writes its dispatch note into the row, the dispatch's
  identifier as the capture records it, at the dispatch, never inferred.
- Tests: `tests/dashboard/test_server.py` (`test_the_board_payload_is_the_model` pins the payload,
  line 333: its assertions are per-key — the `payload["board"]` equality at line 343 survives the
  new keys untouched — while its pinned `plan_columns` assertion, line 344, is updated to
  `["drafted", "dispatchable"]`, the mode's state words for the fixture, whose one row's State cell
  opens with no state word, so no row is `in progress` or `landed` and the board is in planning
  mode; new assertions pin `mode` as `planning`, `agents` as empty for the fixture's project, and
  `dispatch_colors` on a fixture row naming a dispatched session id),
  `tests/dashboard/test_board_panel.py` (the watched-file following and unreadable-file cases),
  `tests/dicing/test_board.py` (`test_plan_columns`, line 98) — updated in scope; each new test
  names its defect by `clauses.TEST_PRECONDITION` (`devpro/clauses.py`). A failing test on
  behavior this package does not state it changes is reported as a finding, never edited to pass.

**Facts** (run 2026-11-27)

- The board panel's data acquisition is a 0.25 s server-side poll over watched files plus a 25 s
  client long poll: `devpro/kanban/server.py:54-55` quotes `POLL_SECONDS = 0.25` and
  `LONG_POLL_SECONDS = 25.0` above.
- The stores hold this checkout's own records: `ls .devpro-temp/.profiler-claude/` lists
  `s1.jsonl` and three `ses_de*.jsonl` files, and `ls .devpro-temp/.profiler-opencode/` lists
  three `ses_de*.jsonl` files (run 2026-11-27).
- `git grep -l "PLAN_COLUMNS"` → `devpro/kanban/board.py` (its definition, line 54), 
  `devpro/kanban/server.py` (its import and use). The page reads the payload's `plan_columns`
  (`devpro/kanban/assets/board.js:150-158`), and `tests/dashboard/test_server.py:344` pins it.
- `git grep -l "watched_files"` → `devpro/kanban/board.py` and `devpro/kanban/server.py`.
- `git grep -l "child_agent_id" -- devpro tests devtools` → `devpro/profiler/capture.py`,
  `devpro/profiler/read.py`, `devpro/profiler/pages.py`,
  `devpro/harnesses/resources/opencode/profiler.ts`, `tests/dashboard/test_server.py`,
  `tests/fixtures/profiler_serialize_record.json`, `tests/profiler/conftest.py`,
  `tests/profiler/test_capture.py`, `tests/profiler/test_served.py`,
  `tests/profiler/test_tree.py`. None of these signatures changes: the derivation is new code over
  the records they already write and read.
- The State cell's note already reaches the payload: `WorkPackage.note` is the State cell after
  its state word (`devpro/doccheck/planform.py:114-115`), and `_package_card` carries the package's
  fields whole (`devpro/kanban/board.py:416-418`). No planform change follows.
- The board assets have no DOM test — no test runs the page's script in a browser. What exists: the
  assets are served byte-identically to the tree's (`tests/dashboard/test_server.py:313` the script
  asset, `:456` the page answer), the page names its scripts (`:650`), and the script's own text is
  read in the nav-slot cases (`:631-669`). The drawn column and the dots are accepted on the
  payload the Python tests pin; the served-asset cases prove the bytes the page loads are the
  tree's.

**Done-line:** `just test devpro`, then `just lint`.

### P4 The project documents carry the accepted deltas

Applies every design entry to its target verbatim, links rebased to each destination's directory,
the three new leaves written whole.

**Scope**

- Targets edited: `PROJECT_DOCS/SPEC/dicing-and-checks/kanban/columns-and-cards.md`,
  `PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md`,
  `PROJECT_DOCS/SPEC/plan-status-form.md`, `PROJECT_DOCS/SPEC/rendering.md`,
  `PROJECT_DOCS/SPEC/generated-files.md`,
  `PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md`,
  `PROJECT_DOCS/ARCHITECTURE/banner.md`.
- New leaves: `PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-agents-column.md`,
  `PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-agents-column.md`,
  `PROJECT_DOCS/ARCHITECTURE/the-package-lifetime-scale.md` — each with the Contents entry its
  tree's listing requires.
- This package commits only `PROJECT_DOCS/` paths.

**Discipline**

- The application ends verified: `just dev-check-design-deltas-applied` reporting every pair
  landed (`a delta application ends verified`), then the replaced-wording search —
  `git grep -ln "!TUNING\|tuning line\|two banner" -- PROJECT_DOCS` — with each hit read; a stale
  statement is reported to the session, not rewritten (`a delta application ends by searching the
  doc set`).

**Facts** (run 2026-11-27)

- All seven target leaves exist as named; the `Renders and copies` leaf
  (`PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md`) states no banner-line count, so the
  search above finds nothing stale there — reported, not edited, if it does.

**Done-line:** `just dev-check-design-deltas-applied`, then `just dev-check-links`.

### P5 The reference slots re-taken

Transient: the slots are untracked output (`rendered/` is gitignored, `.gitignore:14`), so this
package's work is never committed and closes on its passing run, not on a commit.

**Scope**

- The four reference slots under `rendered/` (`reference-claude`, `reference-opencode`,
  `reference-gemma`, `reference-mage`), re-taken from the current generator with their fixed flags.

**Discipline**

- Runs only after P1, P2 and P3 are accepted (`reference retakes follow acceptance`): earlier it
  would erase the change from the next comparison.

**Done-line:** `just retake-reference`, then `just render-diff`, whose reported output — read and
pasted into the return report — shows no pairs; the target reports and never gates, so the
observable is the pasted output, not an exit status.

### P6 Post-plan review

The reviewers, given the project documents and `ACTIVE_DESIGN.md`, not the plan: the project's
python coder (`devpro-python-coder` — the definitions, render, install and board panel are Python),
`devpro-architect` (the board panel's structure and the install's file set changed) and
`devpro-prompt-engineer` (the model-facing definition texts changed). No README or human-facing
guide changed, so `devpro-tech-writer` has no seat. Each reviewer writes independently in the
scratch directory; the session synthesizes `ACTIVE_PLAN_REVIEW.md` from their reports without
waiting between the last report and the write-up. This package's row is `landed` in the commit that
adds the review document.

**Done-line:** the review document is written and committed; its acceptance is the review landing,
no runner target checks it. Where the reviewers name checks, the session runs them before the
commit.

### P7 Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
