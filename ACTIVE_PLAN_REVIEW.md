# Post-plan review — the profiler pages read as devpro's, name their models and show local time

Reviewed: commits `42cb61d`, `2012fdb`, `2197d21`, `86bb3fc`, `189a468`, `52eeff1`, `d6639d7`,
`8bafc22`, against the project documents and `ACTIVE_DESIGN.md`. Seats: python (`py`), typescript
(`ts`), web (`web`), architect (`arch`), prompt-engineer (`pe`), and the owner. The seats' own
reviews and their evidence (screenshots, probes, run logs) are under `.devpro-temp/review-*`.

Held, by every seat that judged it: all 20 design pairs landed (`just dev-check-design-deltas-applied`:
landed 20, pending 0); links clean (`just check-links`: 357 links, 0 broken); every presented moment
local; one header separator; no legend on the index; main context in the accent with labels at
6.2:1 light, 7.6:1 dark; no palette hue reads as the accent; child pages named for the dispatching
agent; the model on header, lifelines, tooltips, call detail and index; the read-time join keeps
"the child never knows its parent at write time"; no "chrome" in changed text.

Severity: **C** critical, **W** warning, **N** note.

## Owner

- **R1 (W) Call durations read as raw seconds.** `devpro/profiler/view.html` `dur` prints whole
  seconds past ten seconds (`1129 s`); the index's span column has its own formatter
  (`pages.py` `span`, `3h 2m`). Owner's decision: one formatter serves both, no space between number
  and unit — `217ms`, `4.2s`, `48s`, `18m 49s`, `1h 2m`. ARCHITECTURE `install/harness-profiler.md`
  states the span form; it gains that call durations take the same form. (owner)

## Hue and color

- **R2 (C) A dispatched page's fresh contexts do not skip the root's hue.** `pages.py`
  `contexts_of` starts `next_hue` at 1 and never compares it with `root_hue`; with root hue 1 (the
  common case) the first fresh context also wears hue 1. Breaks `harness-profiler.md` "skipping the
  root's hue". The fix must have `dispatcher_of` compute the dispatcher's hues with the dispatcher's
  own root hue (walking the dispatcher chain at read time, cycle-guarded), or a grandchild's root
  disagrees with its dispatcher's page. `tests/dashboard/test_server.py:648`'s docstring describes a
  skip that does not happen; no test has a child page with its own fresh contexts. Drop the dead
  `max(next_hue, 1)`. Probes: `hue-skip-probe.txt`, `hue_skip.txt`. (py C1, web C1, arch W1, py N1,
  py N6, web N2)
- **R3 (W) Arrowheads into hue 8, 16, … wear the accent while the lifeline wears `--c0`.**
  `view.html` selects `head-${hue % PALETTE}`, and `head-0` is filled with `hueColor(0)` = accent.
  Breaks SPEC `shipped-files.md` "no other context wears a hue that reads as the accent". 39
  sessions in this tree reach it. Fix: palette markers from `var(--c${h})`, `head-main` the only
  accent marker. (web W1, arch W2)
- **R4 (W) The palette lives in `view.html`, not the shared layer the documents name.** SPEC
  `shipped-files.md` and ARCHITECTURE `harness-profiler.md` say the palette lives in the shared
  layer and the template carries none; `view.html` defines `--c0`…`--c7`, and the index's harness
  dots are literals in `INDEX`. The SPEC outcome holds the code: move the palette and the harness
  dot colors, as named variables, into `devpro/kanban/assets/board.css` beside `--accent`. Then
  `harness-profiler.md`'s twice-stated "no palette of its own" keeps one site. (arch W3, pe A1,
  pe L2)
- **R5 (N) Dark palette labels are unreadable on the new `--c4`.** White head labels on dark
  `--c4 #9aa8ba` read 2.42:1; child pages now draw their root in palette hues. Fix: dark-mode labels
  on palette hues use `--on-accent`. (web N4)
- **R6 (N) The accent-hue chip rule is dead.** `view.html` `.chip.on-accent { … !important }` does
  nothing (the inline background already resolves to the accent); `accentChip` marks heads as well
  as chips. Drop the chip rule and class; compute the child-or-context id once. (web N1, arch N3)
- **R7 (N) `dispatcher_of`'s hue-0 fallback is unreachable** and would put the accent on a
  dispatched root if reached. Delete it. (arch N4)
- **R8 (N) Light accent bar under 3:1 against the panel** (`--accent #d09020` on `#fff`, 2.73:1).
  Accepted as a brand token unless a thin `--line` stroke is wanted. (web N5)

## Index page

- **R9 (W) The index's last moment lost its day.** `pages.py` `moments` dates the first moment only;
  with the UTC title gone nothing recovers the last's day — `2026-11-20 14:46 to 03:11` over a 36h
  span. ARCHITECTURE `harness-profiler.md` states "the second its time only", so the fix changes
  that statement: the last moment carries its date where its local day differs from the first's.
  Check `.col-one` (15rem) still holds the pair on one line. (web W2)
- **R10 (W) Child rows' session ids wrap at 1280px.** `.col-session { width: 22% }` with the 2.4rem
  child indent leaves a 30-character id short by a character or two; the agent name drops a line.
  Fix: size the session column from its content and re-derive the `table { min-width }` floor; that
  floor restates the column sum by hand. (web W3, arch N5)

## Session page

- **R11 (N) Two wordings for the model count, and a redundant guard.** `modelWords` gives
  `models 3`, `modelTail` gives `· 3 models`; fold into one function the callers prefix.
  `D.models.length ? modelWords(D.models) : ''` repeats `modelWords`'s own check. (web N3, arch N2,
  web N2)
- **R12 (N) Header items break mid-item on narrow viewports** (`1` / `contexts`). Wrap each item
  `white-space: nowrap`. (web N6)
- **R13 (N) The local-time formatter has two JS homes**, `INDEX` and `view.html`; both pages link
  `deco.js`. Move it there, together with R1's one duration formatter. (arch N1)

## Tests

- **R14 (W) No test runs the page scripts.** The header misjoin (fixed in `8bafc22`) and R3 shipped
  through the gates for that reason. Proposed: one test that renders a fixture session and loads it
  headless through the `puppeteer-core` + system Firefox toolchain P1 adopted, asserting the
  rendered header separators, the root lifeline's fill against `--accent`, and each arrowhead's fill
  against its lifeline; then delete the script-source substring pins it supersedes. (web W4, arch W6)
- **R15 (W) Form pins.** `tests/test_devpro_profiler.py` regex over the whole index `<thead>`,
  widened for the model column (roadmap already names it); the harness-dot hex pins (opencode and
  claude); `tests/test_opencode_entry.py:149` pins hook registration order. Loosen to the effect or
  delete. (py W1, py W2, arch N6, ts N5)
- **R16 (W) The no-legend assertion goes vacuous on a reword.** `tests/dashboard/test_server.py:435`
  checks the phrase "How to read this"; assert `LEGEND not in index`. (py W3)
- **R17 (N) Zone reset skipped on failure.** `tests/test_devpro_profiler.py:1363-1377` calls
  `time.tzset()` only after passing assertions; move `setenv` + `tzset` into a yield fixture. Drop
  the docstring's second, signature-only "defect". (py N7)
- **R18 (N) Duplicate page-data parser** in `tests/dashboard/test_server.py:100,681` beside
  `tests/test_devpro_profiler.py` `_page_data`; share one helper. (py N5)

## Screenshot tool

- **R19 (C) A route that is also an existing path is shot as a `file://` page — `/` always is.**
  `devtools/screenshot.ts` `targetUrl` tests the filesystem before the route; `--base` is ignored.
  `just screenshot / --base http://127.0.0.1:9` exits 0 with Firefox's `file:///` listing. Fix: with
  `--base`, a `/`-path is a route. Add the test that fails today: a served page at `/`. (ts C1)
- **R20 (W) `just screenshot` prints `bun install` output before the PNG path.** `_js-deps` writes the
  install's output to stdout; send it to stderr or `--silent`. The test runs `bun` directly and
  misses it. (ts W1)
- **R21 (W) A failed color-scheme check leaves the PNG behind.** `scheme()` runs after `shoot()`
  wrote the file, against the tool's own "no PNG is written" contract. Check before
  `page.screenshot`; add a dark-scheme case. (ts W3, arch W5)
- **R22 (W) `reason()` strips every `" #"`, mangling selectors in errors** (`body #nope` reported as
  `body nope`); and `main` re-runs `reason()` over the tool's own messages. (ts W2)
- **R23 (W) The fonts wait is not bounded by `--timeout`**, though its error says it was. (ts W4,
  arch N8)
- **R24 (N) Wrapped errors drop their cause**; pass `{ cause: err }`. (ts W5)
- **R25 (N) Small items:** `--help` exits 2 to stderr; `onPath` reimplements `Bun.which`; `close()`
  in `finally` can mask the failure; two `node:fs` imports; `_js-deps` and `js-lock` repeat the bun
  guard; `screenshot.ts:25`'s comment cites a project document and misstates it. (ts N1–N4,
  arch N8, pe M3)

## Capture

- **R26 (N) Each transcript line is parsed twice** in `capture.py` `tool_use_facts`
  (`usage_by_tool_use` and `_model_of`). Parse once. (py N4, arch N9)
- **R27 (N) Quoted forward references** `"Dispatcher | None"` in `pages.py`; move the class above
  its first user. The `[]` default in `dispatcher_of`'s `next(...)` is unreachable. (py N2, py N3)

## opencode — handed to the opencode session

The owner directed opencode's problems to its own session. Recorded here, not drafted into this
burndown:

- **R28 (W) The model read takes any request kind.** `profiler.ts` stores every `model.request`
  without reading `request.kind` (`"primary" | "compaction" | "title" | "generate"`), so a title or
  compaction request can become a call's model; the contract runner fires `kind: "call"`, not a
  declared kind. (arch W4)
- **R29 (W) A rejected `model.request` registration escapes as an unhandled rejection** —
  `silently(() => { void … })` cannot catch it. (ts W6)
- **R30 (N) The opencode model is clipped but not masked**, unlike claude's. (py, outside its focus)
- **R31 (N) `providerID/modelID` in `harness-profiler.md` against `${providerID}/${id}` in code.**
  (arch N7)

## Documents

- **R32 (W) `recipes.md`'s lint passage is split and now false.** The screenshot text sits inside the
  type-check paragraph, so "The check's mandate is what ships" reads against the wrong check; and
  `just lint` now also type-checks `devtools/screenshot.ts` under `devtools/tsconfig.json`, which
  neither `recipes.md`, CONVENTIONS `a-lint-recipe-is-read-only.md` nor `repo-layout.md` (missing
  `devtools/tsconfig.json`) states. (pe H1, pe A2, arch W7)
- **R33 (W) The models sentence in `harness-profiler.md` cannot be resolved** ("where that header
  holds it alone") and, read one way, contradicts SPEC's "for each context". Rewrite one condition per
  item. (pe H2)
- **R34 (N) "hue" and "copy" are used undefined** in `harness-profiler.md`; define them where first
  used. (pe M1)
- **R35 (N) The child root's color is stated twice in SPEC `shipped-files.md`**; keep the complete
  rule, trim the other. (pe M2)
- **R36 (N) `repo-layout.md`'s screenshot row disagrees with `recipes.md`** on where the PNG lands
  and restates its mechanism. (pe M4)
- **R37 (N) "reads both" in `harness-profiler.md` has two candidate referents.** (pe M5)
- **R38 (N) Small wording:** SPEC names the `<time>`/`datetime` markup (mechanism in SPEC); "the
  accent rule" for a drawn border; "The suite needs … `firefox`" now spans two test surfaces.
  (pe L1, L3, L4)

## Decisions the burndown needs from the owner

- **R9**: the last moment carries its date where its day differs from the first's — a change to an
  ARCHITECTURE statement.
- **R14**: a headless-browser test of the page scripts in the suite.
- **R8**: accept the light accent bar's 2.73:1, or add a stroke.
