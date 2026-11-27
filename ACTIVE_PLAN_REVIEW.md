# ACTIVE PLAN REVIEW

The post-plan review of the plan "The Python type gate and the profiler's operational context".
Four seats ran independently against the project documents and the accepted design — the Python
coder, the TypeScript coder, the architect and the prompt-engineer — each writing to the scratch
directory; this document is the synthesized account. One entry per defect; the seats that reported
it are named. Findings F1–F3 are the burndown's substance; F4–F12 trail by severity.

## F1 — Critical: the stamp's taken-once guarantee fails on edge paths · python, typescript, prompt-engineer

Four paths break or blur "taken once", each independently reproducible:

- **Partial copy** (`capture.py:407-435`): `store_stamp` copies only the *present* keys off the
  earliest stamped record. A session that starts with no `ACTIVE_PLAN.md` and gains one mid-session
  gets `plan` stamped onto its second record — the taken-once contract and the leaf's "copied onto
  the record being written" both break (python, probe `p1.py`).
- **The 4 MB head window** (`profiler.ts` `STORE_TAIL_BYTES`): a store larger than the bound
  answers `null` and mints a fresh stamp beside its old one — the exact defect P2's own test names
  (typescript). The name says tail; the code reads the head.
- **Pre-stamp stores** (`the-operational-context-stamp.md:17-19`): "where the session's store
  already holds records" admits two readings; the executor implemented a third — a store holding
  records with neither field is stamped fresh. The leaf must state which index a legacy store
  produces (prompt-engineer H1); as written, any implementer produces a different one.
- **The manifest's copy path** (python, probe `p2.py`): the manifest is written only where the
  stamp is computed fresh — a digest copied off a store leaves no per-file manifest, so the file
  list is unrecoverable, which is the manifest's whole purpose.

## F2 — Critical: the two captures' digests are not bound to agree · typescript, architect

The design promises one digest for one directives state; nothing holds it:

- The TS side hardcodes `AGENTS.md` where a mage install writes `CLAUDE.md` — a mage-shaped
  project's two captures diverge entirely (typescript, probe `mage.ts`).
- Symlinked files are hashed by Python (`is_file()` follows) and skipped by TS (`Dirent` reports
  neither file nor directory) — an accidental policy difference; the standing rule is that a
  symlink is what it points at (typescript, probed on this repo: TS 108 files, Python 109).
- Python's `_json` (ensure_ascii) versus TS `JSON.stringify` diverge on non-ASCII paths; verified
  by probe (architect).
- The TS digest path never runs in CI, and no test binds the two implementations (typescript,
  architect).

## F3 — High: the digest's file set is not what the leaf states · architect, typescript, prompt-engineer

- Ownership markers never reach the digest: `is_installed` checks banners only, so
  `registry.json` and `hooks.json` — the marker files the Installed-tree leaf names — are excluded;
  the incumbent `_is_our_harness_file` + `harness_markers` machinery exists and was not used
  (architect W2).
- All three harness directories are walked regardless of the capturing harness, while the leaf says
  "the session's harness loaded" — one side must move (architect W3).
- `AGENTS.md` enters by existing, not by carrying the install's block, and the TS side cannot see
  it at all where CLAUDE.md is the agents file (typescript C2).
- The enumerator ("an installed banner or an ownership marker") belongs in the Installed-tree leaf;
  the stamp leaf should state the recognizers it means, and name root `AGENTS.md` (prompt-engineer
  H2/H3).

## F4 — Warning: the capture re-reads its store on every hook · python, architect

`store_stamp` full-parses the store file per tool-call hook, against the capture's never-slow-the-
session contract; the first record suffices (python W2, architect W5).

## F5 — Warning: the read side's stamp readers diverge and over-read · python, typescript

Three stamp readers select "earliest" differently (`pages` skips null `at`; capture and TS do not);
`session_store` guesses the store path instead of taking the one `read_sessions` read, fails open
on any id outside `[\w.-]`, and `child_dispatches` re-parses each child's whole store per page
request (python W3/W4, typescript W5).

## F6 — Warning: the mark's stated surface and the code's disagree · architect

serving.md says the mark stands "beside the dispatch that opened it"; the code appends it to the
fan-out's own header line (`view.html:147`) and its comment records the choice. Meanwhile
`depth_children`'s per-child `unreviewed` key is read by no template — dead data a test pins
(architect W1). One account or the other must move.

## F7 — Warning: the index's surface is over-pinned and under-stated · python, prompt-engineer

The column count has four homes (the min-width sum, the `<th>` list, `colSpan` hand-bumped 7→9,
a test pinning the literal); the feed-key list in serving.md omits `unreviewed`, which the feed
emits and the row reads — a reader of the list writes an index whose mark never draws; the feed
schema is pinned four times across the suite (python W5, prompt-engineer H11).

## F8 — Warning: the detector's field is unpinned at the boundary · typescript

`review_fanouts` compares `name` against the bare `devpro-prompt-engineer` while the renderer strips
the `devpro-` prefix; whether the host reports the prefixed or bare name where the detector reads it
is unpinned, and the failure is silent (typescript W4).

## F9 — Medium: terms and altitudes drifted · prompt-engineer, typescript

"The review seat" resolves in the corpus to the full-review panel, not the post-plan reviewer;
"the project's agents file" reads as the global agents file; SPEC says "empty where a session
predates the stamp" while the rendering is `null` cells — "empty" is the wrong word and decides
whether the index is a partition; the lint gate is stated twice at two altitudes that disagree on
who owns the paths (`pyproject.toml` sets none), and the CONVENTIONS leaf's title ("read-only") no
longer names its content (prompt-engineer H4/H12/H17/H18/H19, typescript W4).

## F10 — Medium: documents the work left behind · prompt-engineer, architect, typescript

`the-opencode-capture.md` was not amended and no longer describes the capture (it now reads two
things and writes a manifest outside its store); the new stamp leaf is absent from the
ARCHITECTURE entry-point's listing, and `check-links` checks only the parent listing, so nothing
holds the pair (prompt-engineer H21, architect, typescript).

## F11 — Low: small hygiene · python, architect

The dead `held`/`s` alias in `linkrewrite.py:66-69` (a mypy-fix leftover); `GENERATED_BANNER` in
`directives.py` is a second home for `render.GENERATED_MARK` — the same fix `INSTALLED_BANNER` got,
not applied to this one; `.mypy_cache/` lands at the repository root with no `.gitignore` entry or
convention covering it (python W6, architect W6, python notes).

## F12 — Note: pin structure to consolidate · python

The JS-source-line test pins added under `TEST_PRECONDITION` and the four-time-pinned feed schema
are candidates for one pin each at the read boundary (python notes).

## What held

The schema-bump discipline (both captures' constants and every pin moved together), the store as
the stamp's home, the digest parity test the TS runner now drives, and the gate landing as plain
ecosystem mypy with no bespoke machinery — none of it drew a finding.
