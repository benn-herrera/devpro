### Annotations on the floor

The floor is 3.11: an annotation evaluates as written, and a union written `X | Y` evaluates there.
`from __future__ import annotations` is cruft on this floor — do not add it, and remove it from code
you touch.

A genuine forward reference — a type named before it is defined, or a class's own name inside its
body or a self-referential field — is that single annotation quoted as a string (`x: "LaterType"`),
and only it. Quote the annotation, never make the import the fix: the import defers every
module's annotations to serve one.

A value evaluated at runtime — a type alias, an `isinstance` argument, anything that is not an
annotation — is spelled the same way, `X | Y`; the type aliases in `devpro/vocabulary.py` are the
worked case. `typing` keeps the names with no builtin or `collections.abc` form: `TextIO`,
`Protocol`, `TypeVar`, `Literal`, `NamedTuple`, `cast`, `Any`, `IO`, `NoReturn`.

The floor has one home and it is enforcement, not a statement: `requires-python`, the venv recipe
that rebuilds a venv below it, and the entry point's refusal. The SPEC's host requirement restates it
for the consumer — `PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md`'s `devpro, the generator, needs
Python 3.11 or later on the host` — a fourth site a move of the floor must carry.
