# ACTIVE PLAN REVIEW — the UX pass

The post-plan review of the UX plan's landed work: U1 (the phosphor identity on one shared
presentation layer, the nav, the board-first landing with the root 302, the profiler frame band and
legend's one-text mechanism, the re-style, and the layout pair's application to the record).
Landing commit `e14288d`. Four independent seats reviewed the shipped changes against the project
documents and their own criteria; the seats were not given the plan.

**Seats:** architect, prompt-engineer, python-coder, tech-writer. **Gates run during review:**
`just test devpro` (1581 passed, 1 skipped), the dashboard and profiler suites (78 passed), the
docs checks (94 documents, 0 problems), and a probe of the served pages.

What holds, per every seat: the six phosphor values exactly as recorded, one home; the legend's
one-home-two-carriers, the once pinned by tests; one guard, one reply path and the CSP including
across the redirect; the board-first root tested through to the board page; scanlines in chrome
and never on cards; production entry points only. The findings below are the defects.

## Findings

### Record and code

- **R1 — Warning.** The applied SPEC record says the server's elements — live/idle indicator and
  stop — **persist across every view** (`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:123-124`),
  and the shipped profiler view deliberately carries neither: `devpro/dashboard/server.py`'s
  `nav_html` docstring disclaims server state, the frame band holds only legend and return, and
  the executor's reasons (a static "serving" is false once the server stops; a dead stop control
  is worse than none) are recorded nowhere. The divergence needs routing: bring the code to the
  sentence, or the sentence to the code with the divergence recorded as the decision it is.
  (prompt-engineer, architect)
- **R2 — Warning.** The profiler index's **standalone output carries no presentation layer**:
  `index_html`'s `css=` substitution key (`devpro/profiler/pages.py:756`) is dead — `INDEX` holds
  no `$css` placeholder, so `/*STYLE*/` survives the fill as a literal, and the served index gets
  its CSS only from `with_frame`'s slot — contradicting the docstring (`pages.py:748`) and the
  ARCHITECTURE leaf's statement of the mechanism (`harness-profiler.md:49-51`). (architect)
- **R3 — Warning.** The nav move **broke the server elements' alignment**: `#connection`'s
  `margin-left: auto` (`board.css:150`) no longer reaches the nav's flex edge inside the plain
  `<span class="nav-server">`, the stylesheet's "in the page's header" comment is stale, and
  `.nav-server`/`.nav-stop` exist in no stylesheet. (architect)
- **R4 — Warning.** The stop button's post-`POST` focus move lands on the now
  `.visually-hidden` `#page-title` (`assets/index.html:22`) with no `:focus-visible` rule — a
  UA-dependent stray ring in the nav. (coder)
- **R5 — Warning.** `board.css`'s `body { height: 100dvh; display: flex }` reaches the profiler
  page through the inline, flexing the sequence-diagram panel inside a viewport column and
  overriding the template's own padding — the ARCHITECTURE leaf's scoping permission
  (`harness-profiler.md:41-43`) is unexercised; the fix is a board-only root class on the layout
  rules. (coder)
- **R6 — Warning.** `GET /`'s 302 carries a **bare `Location: /board/`** (`devpro/dashboard/
  server.py:182`) — relative — while the verb prints the absolute URL and `loopback()` pins the
  absolute form: the printed URL and the accepted URL are a redirect, not where the page lives.
  Absolute location, or the record and the pin moved to the redirect. (coder)
- **R7 — Warning.** `devpro/profiler/pages.py:767`: the CSS splice happens **before** the legend
  removal and the order is load-bearing — the splice re-fills the region the removal empties —
  and no comment or test states it. Order documented, or the two operations made independent.
  (coder, architect)
- **R8 — Warning.** `harness-profiler.md` still describes the pre-`6481c9e` finder and a live
  `HP_DEVPRO` (`:26-31`, `:20`), and the doctor statement (`:179-181`) says the finder probes
  `--version` where `hooks.py`'s `devpro_executable()` checks executability only — the leaf is a
  version behind the launcher's simplification. (coder)
- **R9 — Warning.** `harness-profiler.md:54` still places the board's indicator and stop **"in its
  header"** — the same landing commit moved them into the nav. (prompt-engineer)
- **R10 — Note.** "Traces panel" survives at five sites in docstrings the pass itself edited
  (`pages.py:2`, `dashboard/__init__.py:4`, `server.py:5`, `server.py:100`,
  `tests/test_devpro_profiler.py:133`), half-renamed against the profiler-view vocabulary the same
  landing introduced. (prompt-engineer)
- **R11 — Note.** `--accent-dim` is defined in both motifs and used by no rule — the banned
  second brand color, left standing in the shared layer. (prompt-engineer, architect)
- **R12 — Note.** The template-carries-no-second-copy assertion is checked on the served path
  (legend count == 1) but not the standalone path (`tests/test_devpro_profiler.py:654` asserts
  presence only). (prompt-engineer)
- **R13 — Notes on record and vocabulary.** `view.html`'s diagram color map vs. the leaf's
  "no palette of its own"; two stale "pending" notes in `ACTIVE_DESIGN.md`; the record's monogram
  sentence describing an object that does not ship; test cuts that pin form rather than behavior
  (`test_devpro_profiler.py:655`, `:673`; a duplicate at `:659`; `test_server.py:294`, `:308`
  counting words where `class="intro"` is the behavior). (architect, coder)

## Process notes

- The pass's plan carried the done-line both surfaces and the delta checks; the gaps the seats
  found are all in the code-record boundary, which no gate reads — the same class of gap the
  stage-3 review documented, now once again filled by the review round itself.
- The plan's predicted delta-gate exit-1 cause was wrong in detail (it named a stale pair; the
  standing pending pair is stage 4's attribution record, correct at this landing) — the executor's
  report corrected it and the landing commit states the true cause.
