# ACTIVE PLAN REVIEW — the process self-alignment plan (P1–P13)

The post-plan review of the accepted design's landed changes (commits `1af120a8..HEAD` at
synthesis). Panel: devpro-architect, devpro-prompt-engineer, devpro-security-reviewer,
devpro-tech-writer, devpro-python-coder — each wrote independently to
`.devpro-temp/review-<seat>.md`; this document is the de-duplicated synthesis, one entry per
defect, every seat that reported it named, grouped by root cause. Severities are when-cost-lands.

## The release tag

- **R1 — Critical** (tech-writer; architect): README's pipx line names `@v0.18.1` before the
  release is cut — `git tag` reads `v0.18.0`, `git describe` agrees, so Quick Start's pipx
  reader (the path that exists for readers without Homebrew) fails to resolve the ref. The text
  is right for the release once `just tag` cuts `v0.18.1` and pushes it; until then the
  user-facing path is broken.
- **R2 — Warning** (tech-writer; architect): the hand-edit step CONVENTIONS' version leaf names
  is held by nothing — `bump-version` edits `__version__` only, `tag` reads it, no check greps
  README; P13's drift is the gap admitted. The brew update path never mentions the README tag
  while the pipx path says "the next release's tagged URL" (tech-writer F3). The bump rode
  P1's code-delta commit and the README tag landed separately, against the leaf's ordering
  (architect).

## The precedence span's wording — owner decision

- **R3 — Warning** (python-coder; prompt-engineer): the span's "no list of qualifying documents
  and no carve-out" admits two readings — no exception to the precedence itself, or no
  exceptions anywhere — and the second collides with the project's own leaves that name
  exceptions (e.g. structural-rules' value-constant exemption). Its heading ("The project's own
  documents modify the process") states a narrower rule than its body, which also governs file
  headers and settled style (prompt-engineer W7). Eleven seats that write no code carry "the
  code you change" (prompt-engineer W8). The fix is the owner's: scope the prohibition to the
  precedence, and reconcile heading, body and audience.

## The reach invariants' tests

- **R4 — Warning** (architect): no test pins the change's corpus-level invariants — that every
  agent definition carries `PROJECT_PRECEDENCE` (the clause-group check covers group members
  only), that only python-coder and ml-engineer pass `VENV_PROBE_RULE`, or the MB13 seat set.
  Grep of tests/ for the three new constants returns nothing. One small test in
  `tests/render/test_structural_rules.py` closes all three.
- **R5 — Warning** (python-coder): the uncredited-shared-paragraph check judges at paragraph
  grain, so a hard-wrapped paste of the new span is a different paragraph and passes — measured,
  not guessed. The "shared text cannot disagree" property escapes by line-wrapping.

## The reworked rules' model-facing precision

- **R6 — Warning** (prompt-engineer): the cap's two statements admit different arithmetic —
  the guide's "raise the count … past the cap" vs the skill's phrasing; the guide never names
  the term, so an agent cannot reconcile them.
- **R7 — Warning** (prompt-engineer): the drafting boundary is stated three times, byte-identical
  at two sites — and the third (the periodic-review drafting sentence) copies "a request for the
  plan is not that ask" into a context where the plan is the review's own plan, which the user's
  request *does* create; the sentence there refuses the ordinary path.
- **R8 — Warning** (prompt-engineer): the trigger rewrite deleted "the boundary is", leaving
  "coherent feature boundary" undecidable at the point it fires — the gloss lives only in this
  repository's CONVENTIONS leaf, which consuming projects never render.
- **R9 — Warning** (prompt-engineer): the agents-file alias principle obliges the model to recall
  an unbounded operator-profile list — a machine guarantee handed to a model.
- **R10 — Warning** (prompt-engineer): the drafting boundaries say "the user asks the session
  itself" without saying which seat "the session" is when the skill is loaded by another agent.
- **R11 — Warning** (prompt-engineer): the development skill now opens with a governance
  paragraph ahead of its *Route* table, burying the routing a newcomer needs first.

## The severity ladder's reach

- **R12 — Warning** (prompt-engineer): the prose-architect keeps a four-word severity ladder of
  its own (`prose_architect.py:45–46`) — a seat the MB13 unification's sweep missed.
- **R13 — Note** (security-reviewer; prompt-engineer): the shared ladder's Note has no security
  gloss mapping, the security reviewer's Critical is narrower than the span's, and the two
  Critical definitions coexist with no precedence rule between them — severity drift across
  seats is possible.
- **R14 — Note** (architect; prompt-engineer): the architect's severity line renders as a doubled
  label — "**Classify severity**: **Severity by when the cost lands**:".

## Stale artifacts and document drift

- **R15 — Note** (security-reviewer): the git-ignored stale render `rendered/agents/…` still
  carries the full retired pipeline text; an install from that directory without regeneration
  revives what MB10 retired.
- **R16 — Note** (architect): `clauses.DATA_FORMATS`' tail names the project's `CONVENTIONS.md`
  as governing — the narrower form the design's claim "no narrower CONVENTIONS-only form
  survives anywhere" says no longer survives. Recommend deleting the tail.
- **R17 — Note** (architect): subsystem-map says the development skill has "six supporting
  files" and lists seven — pre-existing, but the entry was touched in-window.
- **R18 — Note** (tech-writer): the skill names `plan-count` without saying the consuming
  project must provide the target in its own runner — a Makefile project has none.
- **R19 — Note** (tech-writer): the 0.17.x upgrade walk is restated in the guide's installing
  reference and README — linked correctly, drift-prone.

## The runner's new machinery

- **R20 — Warning** (python-coder): the surface set is hardcoded in two places —
  `devtools/tests/test_changed_map.py` pins the names `devtools/scripts/test.sh` defines, so a
  new surface needs an edit in two places.
- **R21 — Note** (python-coder): the count-target test scans the whole `## Periodic review`
  slice rather than the count bullet, and `text.index` raises instead of naming its condition.
- **R22 — Note** (python-coder): `VENV_PROBE_RULE` begins with a space — the only constant in
  `clauses.py` that does; the separator belongs in `verification_evidence()`.

## The count's naming

- **R23 — Note** (prompt-engineer): three sites, one term, three names — "count" / "number" /
  "agents running at once".
- **R24 — Note** (prompt-engineer): this repository's own CONVENTIONS still says `just
  plan-count` (The count is a target) — the naming MB3 retired survives here.
