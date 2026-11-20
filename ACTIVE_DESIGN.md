# ACTIVE DESIGN

## Drafts

### The delta-application byte-check joins the development skill

Decision (user): the byte-check policy is process, not a project idiosyncrasy — the development
skill states it, and the mechanism ships in the docdicer package (`check-design --deltas-applied`;
the RFE is under way in the docdicer session, which owns the tool side).

Facts: the policy's home today is `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`
— devpro's own CONVENTIONS, not the shipped skill; the check's devpro-local implementation is
`devtools/check_deltas.py` (tree-read and from-side absence checks, landed with the previous plan);
the docdicer checks reach consumers through the installed runner snippets, which carry no deltas
recipe today; the previous plan landed the dice-lifecycle bullet in the development skill but not
the byte-check rule — the gap this ticket closes.

Open: which runner target the skill text names (devpro's local `just check-deltas`, the docdicer
recipe the runner snippets gain, or both under one name); whether `devtools/check_deltas.py`
retires at docdicer parity or stays as the dev harness; the CONVENTIONS leaf's fate (cite the
skill's rule, or keep the project instance beside it); which skill section the rule joins.

### The docdicer pin bumps to the release carrying --deltas-applied

Decision (user): the flag is `--deltas-applied` — not `--check-deltas-applied`, not
`--include-deltas`; the RFE is under way in the docdicer session.

Facts: the pin is `devpro/docdicer-tools/docdicer:8` (`VERSION=0.11.2`); at the bump, the
both-present enforcement the CONVENTIONS leaf defers to ("until then the rule above carries it")
activates; the working tree's uncommitted justfile sketch (`dev-check-design-deltas-applied`) calls
the old flag name and corrects at this bump.

Open: the version number — the bump lands when the docdicer release does.
