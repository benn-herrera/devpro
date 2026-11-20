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
| P3 | drafted | expert | the burndown's fixes from the review, and the landing commit: `ACTIVE_DESIGN.md`, `ACTIVE_PLAN_REVIEW.md` and this plan deleted, and the ROADMAP item added |

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

**B1 — the skill's application bullet and `references/design.md`.** Apply the design's corrected Code
delta entry verbatim to `devpro/definitions/skills/development.py`, replacing its `**As it stands:**`
block at `149-152` with its `**Becomes:**` block (`just dev-check-design` passes on the design;
`just dev-check-design-deltas-applied` reports `pending: 2`). It answers H1, M1, M3, M4, M6, M7. In
`references/design.md`'s entry-body bullet, add a clause naming `**As it stands:**` and `**Becomes:**`
as what marks a pair's from and becomes (M8). No test pins the sentence
(`git grep -n "confirms them" -- tests/` → nothing); the two structural tests at
`tests/test_devpro.py:1511` and `:1516` must stay green.

**B2 — `PROJECT_DOCS/ARCHITECTURE/recipes.md` and the CONVENTIONS leaf.** Apply the design's corrected
Recipes entry verbatim to `recipes.md`, replacing its `**As it stands:**` block at `43-47` with its
`**Becomes:**` block (M2, M9, L1). In
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`, replace
"byte-exact in its target leaf" with the whitespace-run statement the check applies, and state the
routes the code has — `just dev-check-design-deltas-applied` runs `dev-dd check-design
--deltas-applied` against the hosted clone, and the shipped target is the snippet set's (M3, L2).

**B3 — the two sites where a done-line is written.** `devpro/definitions/skills/development.py:295`
"such as a link check" gains "or a delta check"; `development.py:511-512` "a link check or a document
build" gains "a delta check" (M5). No test pins either phrase (`git grep -n "document build" --
tests/` → nothing).

**B4 — one CONVENTIONS rule defines how an application ends.**
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-by-searching-the-doc-set.md`
takes the title "A delta application is followed by a search of the doc set" and opens with that act;
update its entry in `PROJECT_DOCS/CONVENTIONS/planning-and-execution/index.md` (L4).

**B5 — the hosted clone holds the pinned version.** `docdicer-repo` clones once and never brings the
clone to the pin: the clone's newest tag is `v0.11.2` (`cd docdicer && git describe --tags
--abbrev=0`) while `devpro/docdicer-tools/docdicer:8` pins `VERSION=0.12.0`, so `dev-dd` runs a
different docdicer than the routes name (L3). Add a step to `docdicer-repo` that brings an existing
clone to the pinned tag without discarding local work, and a test under `devtools/tests/` that fails
on the recipe as it stands — the defect is a clone whose HEAD is not the pinned tag with no step that
corrects it. `just test dupe_sweep` runs that suite.

Declined: M8's vocabulary beyond the reference clause (the bullet and `references/design.md` would
state one fact twice), and the prompt-engineer's "Unverified" note (whether a model skips the check
is not a change to this text).

The burndown's work is mechanical where an item applies text already written (B1, B2), and expert
where it composes (B3, B4, B5): a package holding both runs expert.

The landing acts, after the burndown's work:

1. The landing commit deletes `ACTIVE_DESIGN.md` (not diced, so no tree).
2. The landing commit deletes `ACTIVE_PLAN_REVIEW.md`.
3. The landing commit deletes this plan (`ACTIVE_PLAN.md`) — no next plan exists at that time.
4. The landing commit adds the ROADMAP item recording the `docs` surface's resolution: publish the
   docdicer `v0.12.0` tag the pin at `devpro/docdicer-tools/docdicer:8` names. The item leaves
   ROADMAP when the tag is published.
