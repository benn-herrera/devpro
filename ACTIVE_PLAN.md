# Active plan — the delta application ends verified: the development skill states the byte-check, the Toolchain paragraph names its runner target

From the accepted design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — two entries, each one passage pair:
[the Recipes Toolchain paragraph](ACTIVE_DESIGN.md#recipes) and
[the development skill's application bullet](ACTIVE_DESIGN.md#devprodefinitionsskillsdevelopmentpy).
The design is not diced; it is under the plan size limit.

Every package is **shipped**: the whole process, one commit closing each package.

Sequencing: P1, then P2, then P3. Each package leaves the tree green on every surface its work
touches; the one red surface is the `docs` surface of the checkpoint gate, below.

The checkpoint gate is `just test`, then `just sweep-python`. Its `docs` surface (`just test docs`
runs `just check-links`) is red for a reason outside this work: the installed launcher
(`.opencode/plugins/devpro/skills/docdicer/tools/docdicer`, pinned `VERSION=0.12.0` at
`devpro/docdicer-tools/docdicer:8`) pip-installs docdicer from a tag that is not published — pip's
build of `git+https://github.com/benn-herrera/docdicer@v0.12.0` fails at `git checkout -q v0.12.0`
(observed run: `error: recipe 'docdicer' failed`, exit 1; the installed venv holds 0.11.2). An
executor running the gate as bound expects exactly this failure on the `docs` surface and no other;
the hosted-clone route `just dev-check-links` covers the document checks meanwhile. P3's landing
commit adds the ROADMAP item that records the resolution: publish the docdicer `v0.12.0` tag.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | landed | mechanical | the two passage pairs applied verbatim: the skill's application bullet gains the byte-check, the Toolchain paragraph names its runner target |
| P2 | landed | expert | the review document `ACTIVE_PLAN_REVIEW.md`, and P2's Status row |
| P3 | dispatchable | expert | the burndown's fixes from the review, and the landing commit: `ACTIVE_DESIGN.md`, `ACTIVE_PLAN_REVIEW.md` and this plan deleted, and the ROADMAP item added |

## P1 — The two passage pairs applied

Implements [the Recipes entry](ACTIVE_DESIGN.md#recipes) and
[the development.py entry](ACTIVE_DESIGN.md#devprodefinitionsskillsdevelopmentpy), each as accepted:
its `becomes` block replaces its `as it stands` block byte-exact, no composition; the labels the
design's blocks carry (`**As it stands:**`, `**Becomes:**`) are not written into the target.

Scope: `devpro/definitions/skills/development.py`, `PROJECT_DOCS/ARCHITECTURE/recipes.md`.

Facts, each re-run before acting on it:

- Both deltas' from-blocks sat byte-exact in their targets before P1's application
  (`devpro/definitions/skills/development.py:149-151`, `PROJECT_DOCS/ARCHITECTURE/recipes.md:39-43`);
  no relative links to rebase. The tree now holds the becomes-text in both places; the byte-check
  fact below is the re-run that confirms it.
- The byte-check, re-run now: `just dev-check-design-deltas-applied` →
  `pairs: 2, landed: 2, pending: 0, drifted: 0, conflicting: 0, problems: 0`, exit 0. If a re-run
  disagrees — a pair pending, drifted or conflicting — the tree does not hold the design's text;
  re-apply that pair from the design's blocks before the commit.
- No test pins the confirming sentence: `git grep -n "confirms them" -- tests/` returns nothing.
- The two structural tests over the definition module passed unchanged in P1's verified run
  (`just test devpro` → 879 passed): `tests/test_devpro.py:1511`
  (`test_the_definition_modules_and_the_text_module_hold_their_structure`) and `:1516`
  (`test_development_bodies_spell_each_term_through_its_constant`). No test edit is in scope; the
  executor never decides it.
- The runner target consumers get is `docdicer-check-design-deltas-applied`
  (`devpro/docdicer-tools/runner-snippets/docdicer.just:46-48`); this repository's route is
  `just dev-check-design-deltas-applied` → `dev-dd check-design --deltas-applied`
  (`justfile:332`).

The CONVENTIONS leaf
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md` stays as
written: the skill's sentence is generic ("where the project carries it"), and the leaf's local
naming (`docdicer-check-design-deltas-applied` through `dev-check-design-deltas-applied`) and its
pin (`devpro/docdicer-tools/docdicer:8`, `VERSION=0.12.0`) remain true.

Work:

1. [done] Apply the Code delta's becomes-block over the from-block in `development.py` verbatim.
2. [done] Apply the ARCHITECTURE delta's becomes-block over the from-block in `recipes.md` verbatim.

Remaining: P1's commit, after the done-line's checks pass on a fresh run.

Done-line: `just test devpro`, then `just sweep-python`, then `just dev-check-design-deltas-applied`
→ the fact's full byte-check line, then `just dev-check-links`.

## P2 — Post-plan review

The reviewers are the agent for each domain the plan changed substantively; each gets the project
documents and the design, not the plan, and reviews the changes and their tests against the
project's standards. Each writes their own review in the scratch directory, independently; the
session synthesizes them into `ACTIVE_PLAN_REVIEW.md`, never diced, de-duplicating findings and
reconciling them into one account.

- `prompt-engineer` — `devpro/definitions/skills/development.py`: the new byte-check sentence in the
  application bullet, its fit beside the link sentence and the bullet's `*Purpose:*` clause;
- `architect` — `PROJECT_DOCS/ARCHITECTURE/recipes.md`: the Toolchain paragraph's byte-check
  sentence against the recipes the repo actually runs.

The CONVENTIONS leaf is unchanged — P1 leaves it as written — so no seat reviews it.

Done-line: `just dev-check-links`. The review document and P2's Status row land in P2's commit.

## P3 — Post-plan burndown and landing

Drafted from `ACTIVE_PLAN_REVIEW.md` (landed at `c253777`): 1 High, 6 Medium, 4 Low, one item per
root cause. Each item names the surfaces it changes and the command that shows it. P3's commit is the
landing commit, and its acts are stated here so no executor decides them unassisted.

**B1 — the skill's application bullet and the design reference it generates.** Apply the design's
corrected Code delta entry verbatim to `devpro/definitions/skills/development.py`: its
`**As it stands:**` block is lines `150-153` (first line `  confirms them; its delta check ...`, last
line `  documents as accepted, its links still resolving, with nothing left unapplied.`) — verify with
`sed -n '150,153p' devpro/definitions/skills/development.py` before editing, and stop if it differs.
It answers H1, M1, M3, M4, M6, M7.

The reference `references/design.md` is generated, not tracked: its text lives at
`development.py:779` (`path="references/design.md"`). In that body's entry-body bullet — the one
reading "Each passage, each replacement and each whole text is a fenced block." — add a clause naming
`**As it stands:**` and `**Becomes:**` as what marks a pair's from and becomes, worded in that
bullet's own sentence (M8). Edit no file under `.opencode/`, `.claude/` or `rendered/`: those are
generated copies.

No test pins the sentence (`git grep -n "confirms them" -- tests/` → nothing); the two structural
tests at `tests/test_devpro.py:1511` and `:1516` must stay green.

**B2 — `PROJECT_DOCS/ARCHITECTURE/recipes.md` and the CONVENTIONS leaf.** Apply the design's corrected
Recipes entry verbatim to `recipes.md`: its `**As it stands:**` block is lines `39-47` (first line
`(SPEC.md, Guide and README). That import is the install's own snippet,`, last line `` `.venv` ``) —
verify with `sed -n '39,47p' PROJECT_DOCS/ARCHITECTURE/recipes.md` before editing, and stop if it
differs. It answers M2, M9, L1.

In `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`, make two
corrections. Its phrase "occurs byte-exact in its target leaf" becomes the rule the check applies: each
run of whitespace read as one space, every other character exact. Its "run through
`dev-check-design-deltas-applied`" becomes the route the code has: the shipped target is the snippet
set's `docdicer-check-design-deltas-applied`, and this repository's `just dev-check-design-deltas-applied`
runs `dev-dd check-design --deltas-applied` against the hosted clone (M3, L2).

**B3 — the two sites where a done-line is written.** In `devpro/definitions/skills/development.py`,
`:296`'s "such as a link check" becomes "such as a link check or a delta check", and `:512`'s "a
link check or a document build" becomes "a link check, a delta check or a document build" (M5).
Verify both with `grep -n "such as a link check\|link check or a document build"
devpro/definitions/skills/development.py` before editing. No test pins either phrase
(`git grep -n "document build" -- tests/` → nothing).

**B4 — one CONVENTIONS rule defines how an application ends.** The leaf
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-by-searching-the-doc-set.md`
takes the heading "### A delta application is followed by a search of the doc set", and the index
lists it under `planning-and-execution/index.md` as `- [A delta application is followed by a search of
the doc set](a-delta-application-ends-by-searching-the-doc-set.md)` (L4). The second list carrying the
old title is this file's list of entries in `PROJECT_DOCS/CONVENTIONS/entry-point.md:49`, which takes
the same new text; `just dev-check-links` reads link targets, not link text, so grep both lists
(`grep -rn "A delta application ends by searching" PROJECT_DOCS/` → two hits become none). Its body
already opens with the act; only the title and the two lists change.

**B5 — the hosted clone holds the pinned version.** `docdicer-repo` clones once and never brings the
clone to the pin: the clone's newest tag is `v0.11.2` (`cd docdicer && git describe --tags --abbrev=0`)
while `devpro/docdicer-tools/docdicer:8` pins `VERSION=0.12.0` (L3). Add a step to `docdicer-repo`
that reads the pin, and where an existing clone's `git describe --tags --abbrev=0` is not that tag,
fetches tags and checks the clone out to it without discarding local work (a dirty clone is reported,
not reset). Where the tag is absent both locally and on the remote — as `v0.12.0` is today — the step
reports which tag is missing and leaves the clone alone; it never fails a clone that already holds
the pin.

The test is `devtools/tests/test_docdicer_repo.py`, and it fails on the recipe as it stands: no test in
`devtools/tests/` reads the justfile today (`grep -rln justfile devtools/tests/*.py` → nothing), so
nothing observes that the recipe leaves the clone at the pin. Its assertions: the `docdicer-repo`
recipe body reads the pin from `devpro/docdicer-tools/docdicer` rather than hard-coding a version, and
it contains the step that brings a clone whose newest tag differs to the pin's tag. `just test
dupe_sweep` runs the suite.

Declined: M8's vocabulary beyond the reference clause (the bullet and the reference would state one
fact twice), and the prompt-engineer's "Unverified" note (whether a model skips the check is not a
change to this text).

P3 is expert: B3, B4 and B5 compose, and B1's reference clause is written rather than applied.

Done-line: `just test devpro`, then `just sweep-python`, then `just test dupe_sweep`, then the
byte-check reading `just dev-check-design-deltas-applied` reporting `pairs: 2, landed: 2, pending: 0,
drifted: 0, conflicting: 0, problems: 0`, then `just dev-check-links`, then `just dev-check-plan`.
`just test`'s `docs` surface fails as the header states; every other surface passes.

The landing acts, after the burndown's work:

1. The landing commit deletes `ACTIVE_DESIGN.md` (not diced, so no tree).
2. The landing commit deletes `ACTIVE_PLAN_REVIEW.md`.
3. The landing commit deletes this plan (`ACTIVE_PLAN.md`) — no next plan exists at that time.
4. The landing commit adds the ROADMAP item recording the `docs` surface's resolution: publish the
   docdicer `v0.12.0` tag the pin at `devpro/docdicer-tools/docdicer:8` names. The item leaves
   ROADMAP when the tag is published.
