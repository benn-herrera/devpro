# Plan — the profiler pages read as devpro's, name their models and show local time

Implements [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md): its [SPEC delta](ACTIVE_DESIGN.md#spec-delta) and
[ARCHITECTURE delta](ACTIVE_DESIGN.md#architecture-delta) in full. Every package below is
**shipped**. Each closes in one commit.

## Facts the packages rely on

- The pairs. Each package applies the pairs it names, verbatim, numbered in the order they stand in
  their entry. The pair counts are [the profiler's shipped surface](ACTIVE_DESIGN.md#the-profilers-shipped-surface)
  (SPEC) 5, [the profiler's pages and capture](ACTIVE_DESIGN.md#the-profilers-pages-and-capture)
  (ARCH) 11, [the repository layout's devtools](ACTIVE_DESIGN.md#the-repository-layouts-devtools) 2,
  [the screenshot recipe and its toolchain](ACTIVE_DESIGN.md#the-screenshot-recipe-and-its-toolchain)
  2, which makes 20.
- Each application ends with `just dev-check-design-deltas-applied` (CONVENTIONS, *A delta
  application ends verified*) and is followed by the package's doc-set search (CONVENTIONS, *A delta
  application is followed by a search of the doc set*). A hit the application leaves false is
  reported to the session. A hit still true is recorded, with the reason it stands, in the
  package's commit message.
- The checkpoint gate is `just test`, then `just sweep-python` (CONVENTIONS, *The gates*).
- Packages P2–P6 share `devpro/profiler/pages.py` and `devpro/profiler/view.html`, and every
  package shares the build, so all of them run serially in the order of the status table.
- The development loop. P3–P6 view their pages through P1's `just screenshot`, against
  `just dev-devpro dashboard [<project-dir>]` running in the background. That command prints the
  URL. This repository's own stores serve as data: `.devpro-temp/.profiler-opencode/`, dispatch
  records with `child_agent_id` among them, and `.devpro-temp/.profiler-claude/`. The PNGs go under
  `.devpro-temp/`. The loop is the package's own verification. The plan takes no
  screenshot as evidence and asserts nothing about the pixels.
- Times rule: records stay UTC on disk (`capture.py:306,351`, `profiler.ts:296,330`); only
  presentations change. P6's edits to `profiler.ts` leave those `at` writes as they are.
- Terminology: the nav, the frame band and the decoration script are the deco.

## Status

| Package | State | Rating | Agent | Scope |
| --- | --- | --- | --- | --- |
| P1 | landed | expert | `devpro:typescript-coder` | `just screenshot`: the development loop's page screenshot |
| P2 | landed | expert: re-rated after three step-down dispatches went idle without completing or reporting | `devpro:python-coder` | every presented moment local; the header line's one separator |
| P3 | landed | expert | `devpro:web-app-expert` | index: no legend, narrower agents column, one-line first-to-last, no child lead-in |
| P4 | landed | expert | `devpro:web-app-expert` | main context in devpro's accent; palette clear of it; opencode's dot |
| P5 | dispatchable | expert | `devpro:python-coder` | a child page names its root for the dispatching agent, in that call's hue |
| P6 | dispatchable | expert | `devpro:python-coder` | claude and opencode calls record their model; index and page show it |
| P7 | drafted | expert | session | Post-plan review of what shipped, to `ACTIVE_PLAN_REVIEW.md` |
| B0 | drafted | expert | session | Post-plan burndown drafting |

## P1 — `just screenshot`, the development loop's page screenshot

Applies pairs 1–2 of [the repository layout's devtools](ACTIVE_DESIGN.md#the-repository-layouts-devtools)
and pairs 1–2 of [the screenshot recipe and its toolchain](ACTIVE_DESIGN.md#the-screenshot-recipe-and-its-toolchain).

**Scope.** `devtools/screenshot.ts` (new); `devtools/tests/test_screenshot.py` (new); `justfile`;
`package.json`; `bun.lock`; `PROJECT_DOCS/ARCHITECTURE/repo-layout.md`;
`PROJECT_DOCS/ARCHITECTURE/recipes.md`.

**Facts.**

- The dependency is `puppeteer-core`, measured 2026-11-24 with these commands:
  - `npm view puppeteer-core version license engines` gives `25.18.1`, `Apache-2.0` and
    `node >=22.12.0`. `npm view puppeteer-core time --json` dates 25.18.1 at
    `2026-11-17T16:28:28Z`. `npm view puppeteer-core deprecated` prints nothing.
  - `curl -s https://api.npmjs.org/downloads/point/last-week/puppeteer-core` gives 34,946,533
    downloads for 2026-11-17 to 2026-11-23.
  - `npm install --package-lock-only --ignore-scripts puppeteer-core@25.18.1`, run in a scratch
    directory that already holds its own `package.json`, writes a lockfile listing 25 packages:
    MIT 16, Apache-2.0 4, ISC 4, BSD-3-Clause 1. All are compatible with the project's MIT
    `LICENSE`. Without that `package.json`, npm walks up to the repository root and writes there.
  - It is `puppeteer` without the browser download, which is the requirement here.
- `firefox` on `PATH` is `/opt/homebrew/bin/firefox`, a wrapper that execs
  `/Applications/Firefox.app/Contents/MacOS/firefox`. `firefox --version` gives
  `Mozilla Firefox 160.0.1`. `bun` is on `PATH`.
- Headless Firefox runs under this sandboxed user. As `agent-user`,
  `firefox --headless --profile <tmp> --no-remote --window-size 400,300 --screenshot <out> file://<page>`
  exits 0 and writes a 1758-byte PNG showing the page rendered; the probe's files are in
  `.devpro-temp/ffprobe/`.
- `git diff --quiet package.json` exits 0. `package.json` has no `dependencies` block; its
  `devDependencies` are `@opencode/plugin` `2.4.1` and `@types/node` `^26.6.6`. There is no root
  `package-lock.json`. The repository's lockfile is `bun.lock`.
- `_lint-typescript` (`justfile`, under `lint`) checks for `bun` and then runs
  `bun install --frozen-lockfile`. `TEST_SURFACE_MAP` maps `devtools/ dupe_sweep`, so
  `devtools/screenshot.ts` and its test fall under the `dupe_sweep` surface. No row maps
  `package.json` or `bun.lock`.
- CONVENTIONS, *A devtools tool joins the tests*: the tool arrives with its test under
  `devtools/tests/`. CONVENTIONS, *Recipe notes go above the recipe*: the recipe's notes are
  comments above it. Recipe bodies longer than a line or two are scripts (*Long recipe bodies are
  scripts*).

**Guidance.**

1. `package.json`: add `puppeteer-core` `^25.18.1` under `devDependencies`. `description` becomes
   `"Dev-time only, nothing here ships: the declarations the shipped opencode TypeScript resources
   are checked against, and the browser driver the page-screenshot tool runs."` Regenerate
   `bun.lock` with `just js-lock` (step 3) once that recipe exists.
2. `devtools/screenshot.ts`, run as `bun devtools/screenshot.ts <page> [options]`:
   - `<page>` is one of three forms:
     - an `http://` or `https://` URL;
     - a route starting with `/`, resolved against `--base <url>`. A route without `--base` is a
       usage error;
     - a file path, opened as its `file://` URL.
   - `--viewport <W>x<H>` defaults to `1280x800`.
   - `--wait-for <selector>` takes no default.
   - `--color-scheme light|dark` defaults to `light`. The mechanism is your call: Puppeteer's media
     emulation, or Firefox's `layout.css.prefers-color-scheme.content-override` pref at launch.
   - `--out <png>` defaults to `.devpro-temp/screenshots/<slug>.png` under the repository root.
     The slug is the page's host and path, with each run of characters outside `[A-Za-z0-9._-]`
     replaced by `_`, and `index` where that leaves nothing.
   - `--timeout <ms>` defaults to `30000` and bounds each settle step.
   - Settle, in order: `goto` with `waitUntil: 'networkidle0'`, then `document.fonts.ready`, then
     `waitForSelector(<selector>)` where one is given. Then take a full-page screenshot.
   - The deco polls `/api/state` every 2000 ms (`devpro/profiler/deco.js:20`, `EVERY_MS`), so
     `networkidle0`'s 500 ms quiet window is reached between polls; if it is not, report the
     observed behavior as a finding rather than changing the settle order.
   - Exit codes: 0 prints the PNG's absolute path and nothing else. 2 is a usage error. 1 means the
     page failed to load or settle, or Firefox is absent from `PATH`; the run names the cause (the
     selector, and the timeout, where it timed out) and writes no PNG.
   - The browser closes on every path.
3. `justfile`:
   - Add a private `_js-deps` recipe: `command -v bun` failing with
     `error: this recipe requires bun on PATH`, then `bun install --frozen-lockfile` from the
     project root. The note's first two sentences above `_lint-typescript` (`justfile:235-237`)
     move above `_js-deps`, with "fails the lint" becoming "fails the recipe that needs it"; the
     `tsconfig.json` sentence stays above `_lint-typescript`, which depends on `_js-deps` and keeps
     only `bunx tsc --noEmit`.
   - Add `js-lock` with `[doc("[dev] install the root package.json's dependencies, rewriting
     bun.lock to match")]`: the same `command -v bun` check, then `bun install` (not frozen) from
     the project root. Its note above it: run it after changing `package.json`'s dependencies;
     every other recipe installs frozen and fails on a stale `bun.lock`.
   - Add `screenshot *args: _js-deps` with `[doc("[dev] screenshot a page after it settles, for
     viewing")]`, running `bun devtools/screenshot.ts "$@"` from the project root. Its note goes
     above it.
   - `test` gains `_js-deps` after `_venv`.
   - `TEST_SURFACE_MAP` gains the rows `package.json dupe_sweep` and `bun.lock dupe_sweep`.
4. `devtools/tests/test_screenshot.py` runs the tool with `bun` on a static HTML file under
   `tmp_path`. The page's script, 300 ms after load, adds `<p id="ready">` and sets
   `document.body.style.height` to `1200px`; until then the page is shorter than the viewport. Two
   cases:
   - `--wait-for '#ready' --viewport 400x300 --out <tmp_path>/shot.png` exits 0 and prints that
     path. The file opens with the PNG signature; its IHDR width is 400 and its height at least
     1200. A shot taken before the page settled is 300 high, and one that ignores the viewport is
     not 400 wide.
   - `--wait-for '#never' --timeout 2000 --out <tmp_path>/never.png` exits 1, its stderr names
     `#never` and `2000`, and `<tmp_path>/never.png` does not exist.

   The docstring opens with `clauses.TEST_PRECONDITION`: the defect is a shot taken before the page
   settled, or one that ignores the viewport. Where `bun` or `firefox` is missing the test fails,
   naming what is missing, and never skips (recipes.md, as the pair restates it).
5. Apply the four pairs.

**Doc-set search.** `git grep -n -e "bun\`, \`perl\`" -e 'package.json' -e 'clause_join_sites and render_diff' -- PROJECT_DOCS`.

**Done-line.** Run `just test-changed`, which selects every surface because the justfile changed,
and `just lint`. Then run `just dev-check-design-deltas-applied`, which exits 1 with
`pairs: 20, landed: 4, pending: 16`: the four landed are this package's, and no other line is
`drifted` or `conflicting`.

## P2 — every presented moment local; the header line's one separator

Applies pairs 2 of the SPEC entry and 6–7 of the ARCH entry. The header line's one separator is a
fix no document records.

**Scope.** `devpro/profiler/values.py`, `devpro/profiler/pages.py`, `devpro/profiler/hooks.py`,
`devpro/profiler/view.html`, `tests/test_devpro_profiler.py`,
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

**Facts.**

- `values.py:87-89` defines `_utc(ms)`. `git grep -n '_utc' -- devpro tests devtools` finds it
  imported and called at `pages.py:38,163,732` and `hooks.py:33,278` only.
- `pages.py:161-163` `clock()` returns `_utc(ms).strftime("%H:%M:%S")`. `pages.py:730-732`
  `stamp(session)` returns the same moment's `"%Y-%m-%d %H:%M:%S"` plus `" UTC"`.
  `git grep -n 'stamp(' -- devpro/profiler` finds its callers at `pages.py:764,772`.
- `hooks.py:278` reads `f"newest:  {_iso(_utc(newest)) ...}"`. `_iso` is imported at
  `hooks.py:31` and used nowhere else in `hooks.py`.
- `view.html:76` defines `const clock = (t) => new Date(t).toISOString().slice(11, 19);`.
- `view.html:125` defines `moment.title = at.toISOString().slice(0, 16).replace('T', ' ') +
  ' UTC';`. The comment at `:115-118` describes it.
- `view.html:128` is the header line: `head.append([head.childNodes.length ? ' · ' : '', …].filter(Boolean).join(' · '))`.
- In the `INDEX` script, `pages.py:1062-1071` defines `day`, `clock`, `utcStamp` and `isoStamp`.
  `moment()` at `:1082-1087` sets the `datetime` attribute from `isoStamp` and the title from
  `utcStamp`. `moments()` sets `cell.title` at `:1095`. The comments at `:1019-1021`,
  `:1079-1081` and `:1089-1091` describe the UTC titles.
- No test pins a UTC reading: `git grep -n -E 'UTC|newest' -- tests devtools/tests` returns
  nothing.

**Guidance.**

1. In `values.py`, replace `_utc` with
   `_local(ms: float) -> datetime: datetime.fromtimestamp(ms / 1000).astimezone()`. Its docstring
   reads "Epoch milliseconds as an aware moment in the machine's local zone."
2. In `pages.py`:
   - `clock` becomes `_local(ms).strftime("%H:%M:%S")`, with the docstring "Epoch milliseconds as
     the tree's time column: local, to the second."
   - `stamp` becomes `stamp(ms: int | float) -> str`, returning
     `_local(ms).strftime("%Y-%m-%d %H:%M:%S")` with no zone suffix, with the docstring "A moment's
     date and clock, local, to the second." Its two callers pass `session["first"]`.
3. In `hooks.py`, the `newest:` line uses `stamp(newest)`, imported from `.pages` beside
   `UsageError`. Drop the `_iso` and `_utc` imports.
4. In `view.html`:
   - `clock` reads local fields: `${localClock(d)}:${padTwo(d.getSeconds())}`. Define it after
     `localClock`.
   - Delete the title line at `:125`. In the `:115-118` comment, "the machine form its `datetime`
     and the raw UTC its title, as on every moment" becomes "the machine form its `datetime`, as on
     every moment".
   - The header line puts one `' · '` before the joined items, where a stamp stands, and none
     inside the list.
5. In the `INDEX` script:
   - Delete `day`, `clock`, `utcStamp` and `isoStamp`.
   - `moment()` sets `datetime` to `new Date(ms).toISOString()` and sets no title.
   - `moments()` sets no title.
   - The three comments lose their UTC-title clauses: at `:1019-1021`, delete " — their titles
     keeping the raw UTC for a hover"; at `:1079-1081`, ", the raw UTC in its title" goes and the
     sentence ends "the machine form in the `<time>` element's `datetime`."; at `:1089-1091`, delete
     the sentence "The cell's title keeps the pair's raw UTC for a hover."
6. Add a test to `tests/test_devpro_profiler.py`. It pins `TZ=Asia/Kolkata` with
   `monkeypatch.setenv` and `time.tzset()`, and restores the zone after. It asserts:
   - `clock(_epoch_ms("2026-01-01T00:00:00.000Z")) == "05:30:00"`;
   - `stamp(<same>) == "2026-01-01 05:30:00"`.

   The docstring opens with `clauses.TEST_PRECONDITION`: the defect is the text tree's time column
   and session stamps reading UTC (CONVENTIONS, *A formatted time test pins the locale*). Before
   the change it fails: `clock` returns `00:00:00`, and `stamp` reads its argument as a session and
   raises.
7. Apply the three pairs.

**Doc-set search.** `git grep -n -i -e 'UTC' -e 'raw UTC' -- PROJECT_DOCS`.

**Done-line.** Run `just test-changed`. Then run `just dev-check-design-deltas-applied`, which
exits 1 with `pairs: 20, landed: 7, pending: 13`.

## P3 — the index: no legend, narrower agents column, one-line first-to-last, no child lead-in

Applies pairs 1 of the SPEC entry and 3, 5 and 9 of the ARCH entry.

**Scope.** `devpro/profiler/pages.py`, `devpro/dashboard/server.py` (docstring only),
`tests/dashboard/test_server.py`, `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

**Facts.**

- `pages.py:921-931` defines `band_fills(*, dispatcher, return_to)`, which always fills
  `BAND_LEGEND: LEGEND`. Its callers are `index_html` at `:889`, with
  `band_fills(dispatcher=None, return_to=None)`, and `_rendering` at `:658`
  (`git grep -n band_fills -- devpro tests`).
- `index_html`'s docstring (`:883-888`) says "the band's legend filled here from its one home".
  `server.py` `profiler_index`'s docstring says "the legend once".
- Column widths live in the `INDEX` style, at `pages.py:978-983`: `.col-agents { width: 12rem; }`
  and `.col-one { width: 8rem; }`. The moments cell is `<span class="moments">`, set at `:1094`.
- `pages.py:1122` reads `id.append(' ', el('small', '↳ child — ' + shown));`. No test pins
  `↳ child`: `git grep -n 'child —' -- tests` returns nothing.
- The tests pinning the legend:
  - `tests/dashboard/test_server.py:423-434`
    `test_the_profiler_view_carries_its_nav_and_legend_once` asserts
    `index.count("How to read this") == 1`;
  - `test_server.py:588-619` asserts the session page carries it once;
  - `tests/test_devpro_profiler.py:1021-1037` asserts the standalone render carries it once.

  The last two stay as they are.

**Guidance.**

1. `band_fills` gains the keyword `legend: bool`, and fills `BAND_LEGEND` with `LEGEND` where it
   is true and with `""` where it is false. `index_html` passes `legend=False`; `_rendering` passes
   `legend=True`. Update `index_html`'s docstring (`:883-888`, "the band's legend filled here"),
   `band_fills`'s, and `server.py` `profiler_index`'s ("the legend once").
2. Set the widths to `.col-agents { width: 6rem; }` and `.col-one { width: 15rem; }`, and add
   `.moments { white-space: nowrap; }`.
3. The child row's cell becomes `el('small', shown)`.
4. Replace `test_the_profiler_view_carries_its_nav_and_legend_once` with
   `test_the_profiler_view_carries_its_nav_and_no_legend`, which asserts
   `"How to read this" not in index` and that the band and nav are present. The docstring opens
   with `clauses.TEST_PRECONDITION`: the defect is the index carrying the legend; before the change
   `index.count("How to read this")` is 1.
5. Development loop: screenshot `/profiler/` at `1280x800` and `1024x768`, light and dark, with
   `--wait-for 'tbody#rows tr'`. Check that the first-to-last cell holds one line, that no column
   overruns its neighbor, and that the child row reads as a child by its indent, rule and tone.
   Where a given width fails that check, change it and report the value you set.
6. Apply the four pairs.

**Doc-set search.** `git grep -n -e 'legend' -e 'child —' -e 'naming the call that dispatched' -- PROJECT_DOCS`.

**Done-line.** Run `just test-changed`. Then run `just dev-check-design-deltas-applied`, which
exits 1 with `pairs: 20, landed: 11, pending: 9`.

## P4 — main context in devpro's accent; palette clear of it; opencode's dot

Applies pairs 5 of the SPEC entry and 1 of the ARCH entry.

**Scope.** `devpro/kanban/assets/board.css`, `devpro/profiler/view.html`,
`devpro/profiler/pages.py`, `tests/test_devpro_profiler.py`,
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

**Facts.**

- The accent is defined once, in `board.css`: `--accent: #d09020` at `:21` and `--accent: #31c260`
  at `:38`, in the dark block. Both page carriers take it: the served page links the file and the
  standalone render inlines it.
- `view.html:100` gives every hue's color:
  `` const color = (id) => `var(--c${(byId.get(id) ? byId.get(id).hue : 0) % PALETTE})`; ``.
  Main is hue 0, so it wears `--c0`.
- The arrowheads are keyed `head-${h}` and `head-open-${h}` for `h` in `0..7` (`:335-336`). A call
  picks `child.hue % PALETTE` (`:328`).
- Header labels are white: `svg .head { fill:#fff; … }` at `:23`.
- Two palette hues read as the accent. In light mode it is `--c2:#b07d1f`, amber (`:8`); in dark
  mode it is `--c4:#6cc07a`, green (`:11`).
- The opencode dot is `.harness.opencode { background: #4a9eea; }` at `pages.py:985`. It is pinned
  by `tests/test_devpro_profiler.py:923`.

**Guidance.**

1. `board.css` gains the token `--on-accent`, after `--accent`: `#1d1d1f` in `:root` and
   `#18181b` in the dark block. The file's header comment gains the clause "--on-accent the text
   that reads on the accent". `--brand` and `--accent` are unchanged.
2. In `view.html`, one function maps a hue to its color:
   `hueColor(h)` returns `'var(--accent)'` for `h === 0` and `` `var(--c${h % PALETTE})` ``
   otherwise.
   - `color(id)` and every arrowhead go through it.
   - Add `head-main` and `head-open-main` markers in `var(--accent)`. A call selects
     `h === 0 ? 'main' : h % PALETTE`.
   - A header or chip whose context has hue 0 carries the class `on-accent`, and
     `svg .head.on-accent { fill: var(--on-accent); }`.
3. Palette: light `--c2` becomes `#5d6d7e` and dark `--c4` becomes `#9aa8ba`. Check in the loop
   whether light `--c7:#8a6a4f` reads as the accent. If it does, change it and report the value.
4. The legend's swatches in `LEGEND` (`pages.py:73-82`), drawn in `var(--c0)`, become
   `var(--accent)`, the color main's own calls wear.
5. `pages.py:985` becomes `#7b7bf0`. Update the regex at `test_devpro_profiler.py:923` to match.
6. Development loop: screenshot a claude session page and an opencode dispatcher's page, light and
   dark. Check that main's lifeline, header and arrows wear the accent with a readable label, and
   that no other context's color reads as it.
7. Apply the two pairs.

**Doc-set search.** `git grep -n -e "opencode's blue" -e 'palette' -e '--c0' -- PROJECT_DOCS`.

**Done-line.** Run `just test-changed`. Then run `just dev-check-design-deltas-applied`, which
exits 1 with `pairs: 20, landed: 13, pending: 7`.

## P5 — a child page names its root for the dispatching agent, in that call's hue

Applies pairs 3 of the SPEC entry and 8 of the ARCH entry.

**Scope.** `devpro/profiler/pages.py`, `devpro/dashboard/server.py`, `devpro/profiler/view.html`,
`tests/dashboard/test_server.py`, `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

**Facts.**

- `pages.py:821-825` defines `dispatcher_of(session, sessions)`, which returns
  `(session, name, tool)`, the dispatcher's three facts, or `None`. Its callers are
  `server.py:159` and `pages.py:766`.
- `git grep -n 'tuple\[str, str, str | None\]' -- devpro` finds that type at `pages.py:647, 663,
  803, 821, 860, 911, 921, 1352` and `server.py:74`. The `dispatches()` and `_feed_entry` sites,
  `:803` and `:860`, keep the 3-tuple.
- `dispatcher_html` (`:914`) unpacks `session, name, tool = dispatcher`.
- `contexts_of` (`:290-364`) gives the root `{"id": MAIN, … "label": MAIN}` at `:297`. It assigns
  hues from `next_hue = 0` at `:337-346`, so the root takes 0 and the first fresh context 1.
  `git grep -n -e 'contexts_of(' -e 'session_data(' -- devpro tests` finds `pages.py:290,580,602,606,644`
  only: the two definitions, `contexts_of`'s callers `render_tree` (`:580`) and `session_data`
  (`:606`), and `session_data`'s caller `_inlined_session_data` (`:644`).
- Hue numbers are unbounded; `view.html` wraps them by `PALETTE = 8` (`:58`, `:100`), so on any
  page with more than eight fresh contexts two of them already share a color.
- In the dispatcher's own `contexts_of`, an opencode child is the context whose id is the child's
  session id, because its record's `child_agent_id` is that id (`:300-315`).
- `view.html:96` defines `short(id)`, which returns `'main'` for id `main`. It is the text in
  "copy of main" (`:109`) and in the compaction row (`:393`). The id checks at `:175`, `:179`,
  `:214`, `:224`, `:263-264`, `:270`, `:321`, `:347` and `:357` test the id and stay as they are.
- `test_server.py:524-563` pins `groupings == [1]`, one `dispatches()` call per page, and
  `reads == [root, root]`.

**Guidance.**

1. In `pages.py`, `class Dispatcher(NamedTuple)` holds `session: str`, `name: str`,
   `tool: str | None` and `hue: int`.
   - `dispatcher_of` keeps its one `dispatches()` call. It finds the dispatcher's session in
     `sessions` and runs `contexts_of` over its records. `hue` is the hue of the context whose id
     is `session`, or 0 where none is.
   - Every annotation listed above except `:803` and `:860` becomes `Dispatcher | None`.
   - `dispatcher_html` reads the fields by name.
2. `contexts_of(records, *, root_label: str = MAIN, root_hue: int = 0)`. The root takes both. A
   fresh context takes the next hue counting from 1, skipping the number `root_hue`, and copies keep
   their parent's hue as now. This changes nothing where the defaults stand. A hue that wraps onto
   the root's color past the palette (root hue 10, a fresh context's hue 2) is accepted: it is the
   wrap every page past eight contexts already shows, and skipping by `% 8` would copy `PALETTE`
   into Python.
3. `session_data(session, *, dispatcher: Dispatcher | None = None)` passes
   `root_label=rendered_name(dispatcher.name, dispatcher.tool) or MAIN` and
   `root_hue=dispatcher.hue` where a dispatcher is given. `_inlined_session_data` and `_rendering`
   pass the dispatcher through, so the served page and `tree --format html` agree.
4. In `view.html`, `short('main')` returns `byId.get('main').label`. The header sub `main context`
   stays.
5. Add a test to `tests/dashboard/test_server.py`. An opencode `s-parent` holds two Agent records:
   `devpro-architect` → `s-other` at `00:00:00`, then `devpro-coder` → `s-one` at `00:00:01`. Store
   `s-one` and `s-other` as well. Assert:
   - `page/s-one`'s data `contexts[0]` has label `coder` and hue 2;
   - `page/s-parent`'s `contexts[0]` has label `main` and hue 0.

   The docstring opens with `clauses.TEST_PRECONDITION`: the defect is a child page whose root is
   labelled `main` in hue 0. Before the change it fails: `page/s-one`'s `contexts[0]` is `main`,
   hue 0.
6. Development loop: screenshot a child page from the opencode store and its dispatcher's page.
   Check that the root's header names the agent in the color the context its call opened wears on
   the dispatcher's page.
7. Apply the two pairs.

**Doc-set search.** `git grep -n -e 'heads a child page' -e 'dispatcher_of' -e "names its root" -- PROJECT_DOCS`.

**Done-line.** Run `just test-changed`. Then run `just dev-check-design-deltas-applied`, which
exits 1 with `pairs: 20, landed: 15, pending: 5`.

## P6 — claude calls record their model; index and page show it

Applies pairs 4 of the SPEC entry and 2, 4, 10 and 11 of the ARCH entry. The opencode capture
records its model too: `profiler.ts` joins the scope. An opencode record still carries no
`context_tokens`, and its sessions must render cleanly with none.

**Scope.** `devpro/profiler/capture.py`, `devpro/harnesses/resources/opencode/profiler.ts`,
`devpro/profiler/pages.py`, `devpro/profiler/view.html`,
`tests/profiler_contract_runner.ts`, `tests/test_devpro_profiler.py`,
`tests/dashboard/test_server.py`,
`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.

**Facts.**

- `capture.py:156-182` defines `context_tokens_of(payload)`. It reads the transcript tail, the
  subagent's where `agent_id` is set, and finds the line naming `tool_use_id`. `usage_by_tool_use`
  (`:127-148`) parses that line's `message.usage`, and the same entry carries `message.model`.
  `git grep -n context_tokens_of -- devpro tests` finds it at `capture.py:156,320` only.
- `build_record` (`:290-325`) is in schema order and drops `None` values.
- opencode's model read. `ctx.session.hook("model.request", ...)` is declared on the plugin's
  session domain (`@opencode/plugin` 2.4.1, `dist/promise/session.d.ts`,
  `SessionHooks["model.request"]`), the parameter `SessionModelRequest` carrying `sessionID`,
  `agent`, `kind` and `model: Model.Ref` — `{ id, providerID, variant? }` (`@opencode/schema/model`,
  `Ref`). The agent loop is sequential per session: the request fires before its assistant message
  is built, the message's tool calls then run, then the next request — so the last `model.request`
  a session reported is the model that issued the call `execute.after` captures. `profiler.ts` runs
  to an opencode 2.3.0 floor, and the hook is not part of any surface guaranteed there; the
  registration goes through the capture's silent step (`profiler.ts:427-431`), and a host offering
  no such hook records `model: null`.
- The opencode pins. The contract test `tests/test_devpro_profiler.py:492` drives the shipped
  `profiler.ts` through `tests/profiler_contract_runner.ts`'s stub plugin context, which already
  registers `session.hook` (`:30`), so the runner needs only the fired events. The fixture records
  under `tests/fixtures/` predate the field and stay as captured; `CallRecord` (`profiler.ts:263-284`)
  carries every field present, nulls where absent, and gains `model: string | null`.
- The feed entry is `_feed_entry` (`pages.py:860-875`).
  - Its exact pins are `tests/test_devpro_profiler.py:860-898` and
    `tests/dashboard/test_server.py:139-170`.
  - `SESSION_KEYS` at `test_server.py:104` is the key set.
  - `_PAGE_KEYS` and `_CALL_KEYS` at `test_devpro_profiler.py:97-111` are subset checks.
- The page data is `session_data` (`pages.py:602-637`).
- The index header is `pages.py:1010`, and its regex pin is `test_devpro_profiler.py:903-912`. The
  row builder is `row()` (`:1109-1136`), and `wideRow` sets `colSpan = 6` (`:1142`).
- The session page's header line is `view.html:128`, after P2. The lifeline header's sub-line is at
  `:223-225`, unclipped, and `tipOf` is at `:214`. The call detail is at `:410-414`.

**Guidance.**

1. In `capture.py`, `context_tokens_of` becomes `tool_use_facts(payload) -> dict`. It does the same
   read and returns `context_tokens` and `model`, each only where found. `model` is the matching
   entry's `message.model` where that is a non-empty string, `clip(mask(...), NAME_LIMIT)`.
   `build_record` spreads it in place of the `context_tokens` line, and `model` follows
   `context_tokens`. The model is recorded at capture alone: `fill_context_tokens` keeps filling
   `context_tokens` only, so a record whose transcript the capture could not read shows its tokens
   filled at render and no model. `usage_by_tool_use` and `fill_context_tokens` are unchanged;
   `tool_use_facts` reads `model` from
   the same line it takes the usage line's id match from, parsing that line itself
   (`git grep -n usage_by_tool_use -- devpro tests` → `capture.py:127,179,224`). `SCHEMA_VERSION`
   stays `2` (`values.py:14`, `profiler.ts:61`): `model` is an optional key, absent where unknown,
   as `context_tokens` is.
2. In `devpro/harnesses/resources/opencode/profiler.ts`:
   - A module-level `const models = new Map<string, string>()`, keyed by session id.
   - In `setup`, a `model.request` hook registered as the other hooks are, its callback's body
     inside `silently`: the ref is read under a guard —
     `request.model ? clip(\`${request.model.providerID}/${request.model.id}\`, NAME_LIMIT) : null` —
     and the map takes the string where there is one, nothing where there is not. The `variant` is
     ignored, and no mask is applied — a model ref names no credential.
   - `callRecord` gains `model: models.get(call.sessionID) ?? null`, after `context_tokens`, the
     slot claude's `model` takes in `build_record`. It stays `null` where the session has run no
     request the hook reported.
   - The map is bounded like `started`: a session's entry goes at its idle, beside the
     started-keys sweep (`:457-464`). A new request precedes any call a new turn makes, so
     clearing there loses nothing.
3. `tests/profiler_contract_runner.ts`: fire `model.request` for `ses_capture` before `call_1`'s
   `execute.before`, and add one completed shell call in a second session, `ses_modelless`, with no
   request fired for it. The stub's `session.hook` registration already collects the callbacks.
4. `pages.py` gains `models_in(records) -> list[str]`, the distinct non-empty `model` values in
   record order.
   - `_feed_entry` adds `"models"` after `"id"`.
   - `session_data` adds a top-level `"models"` (of `calls`), `"models"` on each context (its own
     calls, by `context_of`), and `"model": record.get("model")` on each call.
   - Update `traces_feed`'s docstring key list and the `INDEX` script's key comment.
5. In `INDEX`:
   - Add `<th class="col-model">model</th>` after the session header.
   - Add `.col-model { width: 12rem; }`.
   - Add the cell `el('td', session.models.join(', '), 'col-model')` after the session cell.
   - `wideRow`'s `colSpan` becomes 7.
6. In `view.html`:
   - The header line gains the last item `model <m>`, or `models <a>, <b>` where there are
     several, and nothing where `D.models` is empty.
   - The solid header's sub-line where it holds one context (`list.length === 1`,
     `view.html:223-225`) gains ` · <model>` where the context recorded one
     and ` · <n> models` where it recorded several. The sub-line is clipped with `fits(colW - 30)`.
     `tipOf` lists several models.
   - The call detail gains `<b>model</b><m>` after `context` where the call has one.
7. Tests:
   - Add `"models"` to `_PAGE_KEYS`, `"model"` to `_CALL_KEYS`, and `"models"` to `SESSION_KEYS`.
   - The exact feed pins gain `"models"`. In `test_devpro_profiler.py:842`, the `s-claude` store
     takes `extra={"model": "claude-opus-4-5"}` and its entry pins `["claude-opus-4-5"]`. Every
     other entry, the opencode ones included, pins `[]`: the fixture records predate the field.
   - Add `"<th class="col-model">model</th>"` to the header regex.
   - Add a test to `tests/test_devpro_profiler.py`. A transcript under `tmp_path` holds one
     assistant entry with `message.model` `"claude-opus-4-5"`, `usage.input_tokens` 10 and
     `content` `[{"type": "tool_use", "id": "toolu_1"}]`. The payload is `_PAYLOAD`'s keys plus
     `transcript_path` and `tool_use_id: "toolu_1"`. Assert:
     - the record's `model` is `"claude-opus-4-5"` and its `context_tokens` is 10;
     - the `tree --format html` data has `calls[0]["model"]`, `contexts[0]["models"]` and
       `models` naming it.

     The docstring opens with `clauses.TEST_PRECONDITION`: the defect is a capture that leaves out
     the model its transcript names. Before the change it fails: the record has `context_tokens`
     10 and no `model`.
   - The contract test (`test_the_capture_builds_its_record_over_host_shape_inputs`) gains the
     model asserts: every `ses_capture` record carries
     `model: "wafer.ai/GLM-5.3-Flash"` — the string the runner's fired request names — and the
     `ses_modelless` call's record carries `model: null`. The docstring gains the clause: the
     defect is an opencode record that names no model where its session's request named one, or
     one that names a model no request reported.
8. Development loop: in `.devpro-temp/p6-project/` (a `git init`ed directory), pipe a payload of
   the new test's shape, with that directory as its `cwd`, to
   `env -u CLAUDE_PROJECT_DIR just dev-devpro profiler capture claude` (the capture's store follows
   `CLAUDE_PROJECT_DIR` before `cwd`, `values.py:204-211`). Confirm the record landed in
   `.devpro-temp/p6-project/.devpro-temp/.profiler-claude/`, serve it with
   `just dev-devpro dashboard .devpro-temp/p6-project`, and screenshot the index and the page. Then
   copy this repository's `.devpro-temp/.profiler-opencode/` beside that claude store, append one
   contract-shaped record carrying `"model": "wafer.ai/GLM-5.3-Flash"` into it, and screenshot the
   index and a page again: the model-bearing session's row and header line show it, and the
   older, model-less records around it show none and no empty separator.
9. Apply the five pairs.

**Doc-set search.** `git grep -n -e 'carries no token counts' -e '`records`, `agents`' -e 'record count, the count' -- PROJECT_DOCS`.

**Done-line.** Run `just test-changed`. Then run `just dev-check-design-deltas-applied`, which
exits 0 with all 20 pairs landed.

## P7 — Post-plan review

The post-plan reviewers review what P1–P6 shipped, and get the project documents and
`ACTIVE_DESIGN.md`, not this plan:

- `devpro:python-coder`, for the profiler Python and its tests;
- `devpro:typescript-coder`, for `devtools/screenshot.ts` and
  `devpro/harnesses/resources/opencode/profiler.ts`;
- `devpro:web-app-expert`, for `view.html` and the `INDEX` page;
- `devpro:shell-dsl-coder`, for the justfile changes;
- `devpro:architect`, for the structure and the documents' claims about the code;
- `devpro:prompt-engineer`, for the project documents.

Each writes a review under `.devpro-temp/`. The session synthesizes them into
`ACTIVE_PLAN_REVIEW.md`. The row is `landed` in the commit that adds that file.

**Done-line.** `just dev-check-links` passes over the tree holding `ACTIVE_PLAN_REVIEW.md`.

## Post-plan burndown

### B0 — Post-plan burndown drafting

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
