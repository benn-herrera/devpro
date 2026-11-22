# Post-plan review — the attribution pass (commit `bd2fab1`)

The review's seats: Python coder (`.devpro-temp/pr-python.md`), TypeScript coder
(`.devpro-temp/pr-review-typescript.md`), architect (`.devpro-temp/pr-review-architect.md`),
prompt engineer (`.devpro-temp/pr-review-pe.md`) — each given the project documents and the design,
not the plan. One entry per defect below; seats that reported it named. The source files are the
seat-level record.

## Findings

**F1 — Critical — the zebra's tone has no light-mode counterpart; odd rows are unreadable in the stated light motif** *(architect, python coder)*
The index's odd-row rule is `background: $zebra` with `ZEBRA_MARKS = {"zebra": "#191c22"}` — a
dark-motif literal lifted from the dark-only mockup (`zebra-brands.html`), with no
`prefers-color-scheme` counterpart anywhere in the template block. The page's light motif sets
`--fg: #1d1d1f` on `--bg: #f4f4f6` (`board.css:11-40`), so every odd row and every child row renders
≈1.03:1 contrast — session link, records, moments, span, all invisible — in exactly the mode SPEC
states unconditionally (the zebra sentence and the light-mode surface both live in
`shipped-files.md`). *Fix:* the tone gets a motif-aware carrier — either a shared-layer variable
the board.css `:root`/dark pair owns (the zebra then follows the site's surfaces like every other
tone), or a second `prefers-color-scheme` block in the template's own style; the dark value keeps
the settled `#191c22`, the light value is named in the burndown (proposed: `#e7e7eb`). The zebra
test pins (`.devpro-temp/pr-python.md` finding 5: the literal declaration spelling) re-point to the
carrier — they would break under this fix anyway, and the literal spelling is not the contract.

**F2 — Warning — nested dispatch chains drop the deepest sessions, and the docs state the grouping unconditionally** *(architect)*
For a chain A→B→C, B is excluded from the top level and drawn as a one-level child of A, so C
appears nowhere, and B's dispatched count is the direct children only — while ARCHITECTURE states
"the count of the rows beneath it" and SPEC "the render groups children under their dispatching
session" with no depth limit. *Fix needs a decision the review could not settle:* either the code
walks the chain (each dispatcher's subtree, count of every row beneath), or both leaves are scoped
to one level ("a dispatch's child one level deep; deeper chains read on the session's page, whose
tree draws every dispatch as a context"). Nothing written separates the two readings — the user's
word decides; the burndown holds this item open for it.

**F3 — Warning — a session named as its own child is drawn nowhere, and the code's own docstring states the opposite** *(PE, python coder)*
`dispatches` fills `parent_of[child] = (session, name)` unconditionally; `index_html` guards the
child assignment against self-dispatch but filters top-level rows on membership alone, so a record
carrying `child_agent_id == session` drops the session from every row — while a second dispatcher
naming it still draws it as *its* child with a count. The docstring (`pages.py:820-822`) claims
such a session "keeps its own place in first-moment order." *Fix:* the exclusion is one fact —
`dispatches` drops the self-naming before returning (or the admissible children are computed once
and both the filter and the grouping derive from it) — and the docstring states what the code now
does. Also folded here (same lines, same guard): the TS relay that `render_html`'s `childPage`
guard's rationale and its field's name disagree by intent — the docstring states the claude reason
in terms of what the guard checks.

**F4 — Warning — the dispatcher band re-reads every store on every page request** *(python coder [Warning], architect [Note])*
`DashboardServer.page` calls `page_of` (a full `read_sessions`) and then reads all stores again
(`server.py:195-196`) for one lookup — every `/page/<id>` request now parses the tree twice.
Severity reconciled: real on the request path, mitigated by the small local server; the fix is
cheap, so Warning. *Fix:* one read serves both — `page_of` returns the session beside the page, or
a sibling lookup takes the sessions `page_of` already had.

**F5 — Warning — the claude half of the grouping guard is pinned by no test that could fail** *(python coder)*
"Claude records never group" and "a parent's Agent rows link to the child's page" rest entirely on
`record.get("harness") == "opencode"`, but every test's claude store carries no `child_agent_id`:
removing the guard fails nothing. A real claude record fills `child_agent_id` on every subagent
call (`capture.py:317`) with an agent id that could collide with a session id. *Fix:* one test —
a claude store whose record's `child_agent_id` equals another session's id, asserting no grouping
and no `childPage` link; and the `childPage` docstring's rationale matching the guard's shape.

**F6 — Warning — the localization path is held by nothing mechanical: no test touches `chrome.js`, and a failed parse degrades silently** *(TS coder, findings 2+4 as one root)*
~25 lines of clock arithmetic have no runner: the only pin is the pre-script raw-UTC text. The
`MOMENTS` regex is anchored on text `_moments` writes free-form (`stamp()`/`_iso()` directly), so
a format drift stops matching and leaves the raw UTC silently — a safe degradation nothing
asserts. *Fix:* the format's authority moves to where it is produced — `_moments` emits
`<time datetime="…">` elements the script reads, eliminating the regex — or, minimally, the
docstring states the fallback and one runner (or the design's Firefox-headless probe) loads
`chrome.js` against same-day and cross-day cells and asserts the rewrite and the untouched title;
the fallback test rides along either way. DST skipped: the same-day test is a calendar comparison,
not an interval.

**F7 — Warning — the capture's host fact is held only by a hand-built fixture and the commit message** *(TS coder, findings 1+5 as one root)*
The new behavior hinges on `result.metadata.sessionID`, vouched for solely by fixtures that
hand-build the shape; the real-host verification (opencode 2.3.2) lives only in the commit
message, so nothing re-checks it at the next point release — the drift the harness floor rule
exists to catch. The in-code docstring also does not state which version ships the field or that
"no metadata" is a valid state. *Fix:* a re-examinable artifact — a captured real `subagent`
`execute.after` payload kept beside the `a1-*.log` evidence — and the one-sentence docstring
(version range; no-metadata is a valid no-child state).

**F8 — Notes bundle** *(architect, TS coder, PE, python coder)*
Small, independently fixable: the "1 dispatched agents" plural cemented by its pin (architect,
python — fix to singular, re-pin); the stale "two substitution slots" comment contradicted by the
block added above it (architect); the session href built in three places, the serve-path one
bypassing the existing builder (architect); `calendar()` duplicating `dayOf()` in `chrome.js`
(TS coder, python relay); the `view.html` link's 404 behavior undocumented in-file (TS coder);
the band test helper's slice coupling to the `Return to list` label (python, recorded — a page
with neither dispatcher nor return control would read vacuously true); the plan's dangling ticket
cite and the TS gate-duplication nit resolve on their own (the plan deletes at closure; the call
site reads as intentional).

## Contract gaps

- **G1** *(the build executor)*: a command a plan states as re-runnable evidence must be
  demonstrated returning its stated output when the document is written — two of the plan's three
  host-fact `strings` commands returned empty as written (mis-sized windows). Proposed for
  `PROJECT_DOCS/CONVENTIONS/planning-and-execution/`: "Evidence commands run before they ship."
- **G2** *(TS coder)*: nothing mechanically holds the `.ts` harness resources — no tsconfig, no
  package, `just lint` is Python-only, the file ships verbatim. Proposed for CONVENTIONS: a
  sentence naming what, if anything, checks them, or stating plainly they are held only by their
  tests.
- **G3** *(python coder, "seen")*: `just test` (whole tree) fails at `check-wheel` —
  `pyproject.toml` lists `profiler/view.html` but not `profiler/chrome.js`, missing since `a7f1390`.
  Pre-existing, outside the commit; a one-line package-data fix lands in the burndown.

## Verified clean (cross-checked, no finding)

The opencode-only matching, the flat stores, the template's own style block vs the shared layer,
the serve-path band's home, the subsystem map's profiler row, nothing home-less; the SPEC
`becomes` text landed verbatim; no stale old-behavior claim survives in any comment, docstring,
or test (grep-verified by the PE); the guard/narrowing quality of the capture extraction
 TS-verified cast-free.
