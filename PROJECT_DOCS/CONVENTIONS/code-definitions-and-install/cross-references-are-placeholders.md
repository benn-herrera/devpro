# Cross-references are placeholders

Definition text names another definition only through `clauses.ref(name="python-coder")`, which
spells the reference placeholder `@!ref-python-coder!@` (ARCHITECTURE.md, Rendering, Placeholders).
Write the call inside the body's or description's f-string, as any clause is composed; a description
that holds one is an f-string.
- **A plain reference must resolve in the install's shipped set.** References close within the
  shipped set — every definition no component leaves out, the turned-on components' members included
  — so a plain reference to a definition outside it refuses the render. Where the text does not need
  the not-shipped name, state the role instead of the name ("a security review's findings"), so the
  text reads the same with the component off.
- **An optional reference** is `clauses.optional_ref(name="development")`. It fills as a plain one
  does where the referent ships and drops its whole paragraph where it does not, so it stands in a
  paragraph of its own: a sentence or bullet that goes with the reference, holding nothing the render
  keeps with the component off.
- **Tuning text cannot carry one.** Filled text is never rescanned (Composed text is never
  rescanned), so tuning text names no definition at all.

`tests/test_cross_references.py` fails on a definition name spelled outside a placeholder; its
docstring lists what counts as a reference and what stays bare. A new definition is covered from the
commit that adds it.
