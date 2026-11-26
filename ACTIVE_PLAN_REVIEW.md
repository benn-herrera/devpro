# ACTIVE PLAN REVIEW

The post-plan review of the house-rule plan (G1–G3, commits `246325b5`, `849558f5`, `8e9c5e83`) —
two seats reviewed independently (prompt-engineer, architect; the architect joined per the plan's
revision ruling); this is the session's synthesis, one entry per defect with every seat that
reported it named. The burndown cites these IDs.

## R1 — Critical: the amended-pair paragraph states a checker behavior the checker does not implement
*Reported by: architect (C1, with a rerunnable probe at `.devpro-temp/g3-probe/`), prompt-engineer (F4).*

`a-delta-application-ends-verified.md`'s new paragraph says a re-pointed-only Becomes leaves the
check reading the pair `drifted`, and that the amended pair "must then read `landed`". The
checker's actual hinge (`devpro/doccheck/plancheck.py:202–220`, `_pair_state`) is the **Becomes's
presence in the leaf** — it never verifies the As's content. The architect's probe: a pair with a
stale, unamended As reads **landed** (case A); the drifted reading exists only pre-retouch, and
there the As move yields `pending`, not `landed` (the prompt-engineer's probe agrees). The leaf
therefore asserts the checker polices the As move — the one edit no check verifies — creating the
false confidence that would let the four-changes plan's B4/B6 defect recur silently. Answer: the
paragraph states what the check does police (the Becomes is the drifted↔landed hinge; an
unamended As reads `landed` and nothing catches it) and names the As move as the application
discipline no target verifies — the residue stated, not hidden.

## R2 — Critical: the renamed-leaf leaf's checker claim is inverted, and it may duplicate an existing rule
*Reported by: architect (C2, probe included), prompt-engineer (F2).*

`a-renamed-leaf-takes-its-contents-entries.md` claims "a listing still naming the old path is the
residue the check cannot see" — inverted: an old-path listing is the dead link `just
dev-check-links` **does** catch (`missing file`, exit 1, probed); the invisible residue is the
**stale title or the listing dropped** (exit 0). The prompt-engineer adds that the rule is already
carried at `PROJECT_DOCS/CONVENTIONS/project-documents.md:9-13` — duplicated at lower
altitude — and that the leaf cites `just dev-check-links` where the volume's own leaf cites `just
check-links`. Answer: either restate the leaf to the true reach (the caught link, the invisible
stale-title residue) after resolving the duplication against the existing leaf, or delete the leaf
and its two listing entries.

## R3 — High: the grammar leaf designs SPEC's behavior under CONVENTIONS, on a false TOML premise
*Reported by: prompt-engineer (F1).*

`a-top-level-key-is-a-bare-harness-name.md:3-10` states the settings parser's behavior — which the
CONVENTIONS entry-point forbids ("No user-facing behaviors… that belongs to SPEC") — and its
premise is false as written: a quoted dotted key does not fail by being unparseable; it **parses**
to one top-level table `claude.model-map`, which SPEC Rendering's existing clause ("a table that
is neither a supported harness's…") refuses. The leaf's own last sentence conceding "the behavior
is SPEC.md, Rendering's" is the tell. Answer: strip the leaf to the one trap SPEC lacks — a quoted
key parses and reads plausibly, so a reader meets it and re-litigates, while the refusal is SPEC's
— or delete the leaf and its two listing entries.

## R4 — Note: the landing rule reads advisory where it stands, and its predicate names no observation
*Reported by: prompt-engineer (F3, F5).*

The landing rule sits outside `the-gates.md`'s binding fence, where a reader treats the block as
binding and the prose as advisory, and "the gates have been run" names no observation a reader can
check. The architect's ruling kept it prose in this leaf; the answer is placement and wording only
— e.g. moving the sentence inside the fence as a stated gate line, or worded so its observation
(the gate log at the landing commit) is named. Low; rides whichever package retouches the leaf.

## Verified as correct (recorded so they are not re-opened)

- The grammar leaf's refusal behavior is true of `devpro/context.py` as landed (architect, checked
  against `context.py:192-226`).
- G1's gate line and landing rule verified against the justfile and the leaf as shipped
  (architect).
- The amended-pair rule's *rule itself* — amend in the change, the Becomes to the final wording —
  is sound; R1 is about the checker's claims, not the discipline. (session)

## Contract gaps

- A probe of `just dev-check-design-deltas-applied` assumes a live `ACTIVE_DESIGN.md`; absent one
  the check exits 0 having checked nothing (G3's run). Candidate CONVENTIONS wording, parked with
  the operator.
