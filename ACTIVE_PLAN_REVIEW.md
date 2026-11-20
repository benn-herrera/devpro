# Post-plan review — the delta-application byte-check in the development skill

Findings from two seats over commit `9416f6c`, each written independently in `.devpro-temp/`:
`devpro-prompt-engineer` (`p2-review-prompt-engineer.md`, 9 findings) and `devpro-architect`
(`p2-review-architect.md`, 5 findings). One ID per defect below, naming every seat that reported it.

Severity: **High** — the designed outcome is not achieved; **Medium** — a false or overclaiming
statement, or a rule with two homes; **Low** — wording, naming, or a defect this change did not
introduce.

## H1 — The rule names the check but never makes the application finish on it

*Seats: prompt-engineer (F1).*

`development.py:149-151`. The bullet's imperatives are "applies it to its target verbatim" and the
link rebase. A reader that does both and commits has satisfied every imperative with a pair still
`pending`; nothing else in the skill surfaces that state. The two clauses that introduce a check
bind — "run `check-design` on it ... until it reports nothing", and *Dispatchability*'s "the package
is done when that run passes". This one does not, so the design's stated gap ("an agent applying a
delta reads its work as done once links resolve") is only half closed.

## M1 — The sentence names a subcommand the reader cannot run

*Seats: prompt-engineer (F2).*

`development.py:149-150`. `check-design` is not on PATH in a installing project; the agents file
installed beside the skill forbids invoking the toolchain directly. The runnable, greppable name is
the recipe `docdicer-check-design-deltas-applied`, which the CONVENTIONS leaf and `recipes.md` both
spell out. The skill is alone in naming only the inner command.

## M2 — The ARCHITECTURE paragraph scopes the check to two documents it never reads

*Seats: architect (1).*

`recipes.md:43-45`: "over a design's pending deltas, SPEC.md and ARCHITECTURE.md". The check reads the
design and the leaves its entries name; the landed pair in this design names
`devpro/definitions/skills/development.py`, a Code delta. The same commit's skill bullet states the
check unscoped — the commit ships two descriptions of one check. The skill's scope is right.

The architect seat also holds the located mechanism clauses to the Toolchain paragraph and the
process clause not.

## M3 — "byte-exact" states a guarantee the check does not give

*Seats: prompt-engineer (F3).*

`development.py:150`. docdicer matches a passage with each run of whitespace read as one space. A
rewrapped becomes block with a widened space run reports `landed`, exit 0 (probe P1 in the seat's
review). The CONVENTIONS leaf uses the same word for the same check and moves with it.

## M4 — A clean run reads as confirmation of entries the check never classifies

*Seats: prompt-engineer (F4).*

`development.py:150`. `references/design.md` allows three entry-body forms; the check classifies
pairs only. A whole-leaf or removal entry yields `pairs: 0, problems: 0`, exit 0 (probe P2). The
sentence's "confirms each `becomes` block" invites "the run passed, so the entry is applied".

## M5 — The link check stands unqualified where a reader declares done

*Seats: prompt-engineer (F5).*

`development.py:294` (*Dispatchability*: "document checks, such as a link check") and
`references/new-project.md`'s runner-step line ("a link check or a document build"). The failure the
design names is generated where the done-line is written, and the no-code consumer project reads the
second text.

## M6 — The join leaves "its" and the presence condition adrift

*Seats: prompt-engineer (F6).*

`development.py:149`. After "The project's link check", "its delta check" reads as the link check's
own; and one fact about the project's tooling is qualified twice in different words.

## M7 — The added *Purpose* element restates the clause it justifies

*Seats: prompt-engineer (F7).*

`development.py:151-152`. Three elements for two mechanisms; F1's fix carries the fact into the
sentence an agent acts from.

## M8 — `becomes` / from-text are coined; the skill's words for the pair are elsewhere

*Seats: prompt-engineer (F8).*

`references/design.md` calls them "a passage of the target and its replacement".

## M9 — The process clause crosses into CONVENTIONS

*Seats: architect (2).*

`recipes.md:43-47`. What a clean run means is project process; ARCHITECTURE states the mechanism and
the route. CONVENTIONS already states the rule.

## L1 — "the private `dev-dd`" marks a public recipe private

*Seats: architect (3).*

`justfile:315` — a `[doc]`-attributed recipe with no underscore, two lines from the paragraph's real
private `_venv`.

## L2 — The CONVENTIONS leaf's route phrasing reads as a chain the code does not have

*Seats: architect (4).*

`a-delta-application-ends-verified.md`. `just dev-check-design-deltas-applied` routes through
`dev-dd`, not through the snippet target.

## L3 — The dev route's docdicer version is uncontrolled

*Seats: architect (5, pre-existing).*

The hosted clone is made once and never pulled; the leaf's ship claim attaches to the pin.

## L4 — Two CONVENTIONS leaves each define how a delta application ends

*Seats: prompt-engineer (F9, pre-existing).*

`a-delta-application-ends-verified.md` and `a-delta-application-ends-by-searching-the-doc-set.md`.
