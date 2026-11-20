# ACTIVE DESIGN

## Drafts

### The delta-application byte-check joins the development skill

Decision (user): the byte-check policy is process, not a project idiosyncrasy — the development
skill states it, and the mechanism ships in the docdicer package (`check-design --deltas-applied`;
the RFE is under way in the docdicer session, which owns the tool side).

Facts: the policy's home today is `PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md`
— devpro's own CONVENTIONS, not the shipped skill; the check's devpro-local implementation is
`devtools/check_deltas.py` (tree-read and from-side absence checks, landed with the previous plan);
the docdicer checks reach consumers through the installed runner snippets, which now carry the
target — `docdicer-check-design-deltas-applied` ("check that ACTIVE_DESIGN pending project doc
deltas were applied") — so the runner-target question closes on the snippets' name; the skill
section closes too: the rule joins the Design section's application bullet, whose sentence already
names the link check as the application's only mechanical confirmation; the previous plan landed the
dice-lifecycle bullet in the development skill but not the byte-check rule — the gap this ticket
closes.

Open: whether `devtools/check_deltas.py` retires at docdicer parity or stays as the dev harness —
parity awaits a live probe of docdicer 0.12.0's `--deltas-applied`, which errored on the local clone
(`dev-dd` runs `PYTHONPATH=<clone> python3 -m docdicer`; the clone is v0.11.2-1 and lacks the flag);
the CONVENTIONS leaf's fate (cite the skill's rule, or keep the project instance beside it).

### The docdicer pin bumps to the release carrying --deltas-applied

Decision (user): the flag is `--deltas-applied` — not `--check-deltas-applied`, not
`--include-deltas`; the RFE is under way in the docdicer session.

Facts: the pin is `devpro/docdicer-tools/docdicer:8` — bumped, `VERSION=0.12.0`; the runner snippets
(`docdicer.just`, `docdicer.mk`) carry the new target and help; the working tree's justfile sketch
corrects to `--deltas-applied`. At the bump, the both-present enforcement the CONVENTIONS leaf
defers to ("until then the rule above carries it") activates.

Open: the live verification — `just dev-check-design-deltas-applied` errored (`docdicer:
unrecognized arguments: --deltas-applied`), because `dev-dd` runs the local clone
(`PYTHONPATH=<clone> python3 -m docdicer`), still at v0.11.2-1; the clone updates to the release in
the docdicer session, and this ticket's verification follows it. The pin bump commits when the
capability is verified live.
