# Active plan — the delta application ends verified: the development skill states the byte-check, the Toolchain paragraph names its runner target

From the accepted design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — two entries, each one passage pair:
[the Recipes Toolchain paragraph](ACTIVE_DESIGN.md#recipes) and
[the development skill's application bullet](ACTIVE_DESIGN.md#devprodefinitionsskillsdevelopmentpy).
The design is not diced; it is under the plan size limit.

Every package is **shipped**: the whole process, one commit closing each package.

Sequencing: P1, then P2, then P3. Each package leaves the tree green.

The `docs` surface is red for a reason outside this work: `just check-links` builds docdicer
`v0.12.0` from the remote and the tag does not exist yet (`git checkout -q v0.12.0` fails). The
plan leaves the breakage with the docdicer release — no package resolves it; the hosted-clone
route `just dev-check-links` covers the document checks meanwhile.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | drafted | mechanical | the two passage pairs applied verbatim: the skill's application bullet gains the byte-check, the Toolchain paragraph names its runner target |
| P2 | drafted | expert | Post-plan review |
| P3 | drafted | expert | Post-plan burndown |

## P1 — The two passage pairs applied

Implements [the Recipes entry](ACTIVE_DESIGN.md#recipes) and
[the development.py entry](ACTIVE_DESIGN.md#devprodefinitionsskillsdevelopmentpy), each as accepted:
its `becomes` block replaces its `as it stands` block byte-exact, no composition, no label-adding.

Scope: `devpro/definitions/skills/development.py`, `PROJECT_DOCS/ARCHITECTURE/recipes.md`.

Facts, each re-run before acting on it:

- The Code delta's from-block is byte-exact at `devpro/definitions/skills/development.py:149-151`;
  applying its becomes-block puts the byte-check sentence beside the link sentence, inside the
  bullet, with the `*Purpose:*` clause extended. (`sed -n '149,151p'
  devpro/definitions/skills/development.py`)
- The ARCHITECTURE delta's from-block is byte-exact in its target
  (`PROJECT_DOCS/ARCHITECTURE/recipes.md:39-43`); no relative links to rebase.
- No test pins the confirming sentence: `git grep -n "confirms them" -- tests/` returns nothing.
- The two structural tests over the definition module must stay green:
  `tests/test_devpro.py:1511` (`test_the_definition_modules_and_the_text_module_hold_their_structure`)
  and `:1516` (`test_development_bodies_spell_each_term_through_its_constant`). Updating them is in
  scope only where the change breaks them; the becomes-text writes out no `*_TERM` value, so the
  spelling test should pass unchanged.
- The runner target consumers get is `docdicer-check-design-deltas-applied`
  (`devpro/docdicer-tools/runner-snippets/docdicer.just:46-48`); this repository's route is
  `just dev-check-design-deltas-applied` → `dev-dd check-design --deltas-applied`
  (`justfile:332`).
- The byte-check today reports `pairs: 2, pending: 2, problems: 0`, exit 1 — both pairs unapplied,
  their from-blocks matching their targets. P1's application moves both to landed.

The CONVENTIONS leaf `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`
stays as written: it is the local instance naming the target
(`docdicer-check-design-deltas-applied` through `dev-check-design-deltas-applied`) and the pin
(`devpro/docdicer-tools/docdicer:8`, `VERSION=0.12.0`, the release the flag is live on); the
skill's sentence is generic ("where the project carries it"), so nothing in the leaf becomes false
once the skill states the rule, and the leaf's index already frames the leaves as the local rules
of the `development` skill.

Work:

1. Apply the Code delta's becomes-block over the from-block in `development.py` verbatim.
2. Apply the ARCHITECTURE delta's becomes-block over the from-block in `recipes.md` verbatim.
3. Run the byte-check: `just dev-check-design-deltas-applied` must report both pairs landed
   (`landed: 2, pending: 0, problems: 0`).

Done-line: `just test devpro`, then `just sweep-python`, then
`just dev-check-design-deltas-applied` (pending: 0), then `just dev-check-links`. One commit closes
the package.

## P2 — Post-plan review

The reviewers are the agent for each domain the plan changed substantively; each gets the project
documents and the design, not the plan, and reviews the changes and their tests against the
project's standards. Each writes their own review in the scratch directory, independently; the
session synthesizes them into `ACTIVE_PLAN_REVIEW.md`, never diced, de-duplicating findings and
reconciling them into one account.

- `prompt-engineer` — the skill's model-facing prose: the new byte-check sentence in the
  application bullet, its fit beside the link sentence and the bullet's `*Purpose:*` clause;
- `architect` — the contract documents' claims about the code: the Toolchain paragraph's
  byte-check sentence against the recipes the repo actually runs, and the CONVENTIONS leaf's
  relationship to the skill's rule.

Done-line: `just dev-check-links`. One commit carries the review document, and its row lands with
it.

## P3 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
