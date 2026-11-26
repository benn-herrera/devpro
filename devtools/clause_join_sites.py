"""List each definition-body unit that joins a `clauses.*` interpolation to the module's own text.

Each `body=` f-string of a definition module is composed as import composes it, with the characters
each `clauses.*` interpolation contributed marked. The composed text is split into units by
`devtools.render_diff.line_kinds`. A unit is a paragraph or a list item; a heading, thematic break,
table row or fence line is not a unit, so a clause there is never reported. A unit holding both
marked characters and the module's own is printed as `<path>:<line>: <clause> + <clause>`, its
clauses in source order, the line being that of the unit's first clause. The last line is
`sites: <count>`.

A bare harness-string constant, such as `clauses.PROJECT_HARNESS_DIR` (`@!hrn-…!@`), names a path or
file inside the module's own sentence, so its characters count as the module's own text. The same
holds for a member of `clauses.VALUE_CONSTANTS`, which carries a value rather than a clause. So does
the text of a module constant passed to a clause function: `clauses.f(frame=_FRAME)` marks only
what `f` writes around `_FRAME`. A literal argument stays clause text, a slot fill of the clause's
own sentence.

Paths name definition modules relative to the repository root. With none, every `.py` file under
`devpro/definitions/`, its subpackages walked, that `devpro.definitions.is_private` does not pass
over is read, in sorted path order.
"""

import ast
import importlib
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any, NamedTuple

from devpro import clauses
from devpro.definitions import is_private
from devpro.render import PLACEHOLDER
from devtools.render_diff import LIST_ITEM, line_kinds

DEFINITIONS_ROOT = Path("devpro/definitions")


class Clause(NamedTuple):
    lineno: int
    col_offset: int
    name: str


def _evaluated(expr: ast.expr, *, namespace: dict[str, Any], filename: str) -> str:
    """An interpolation's value, evaluated against the module's namespace: a clause function's
    return is text by contract, which the annotation states rather than proves."""
    text: str = eval(compile(ast.Expression(expr), filename, "eval"), namespace)
    return text


def _module_argument_texts(expr: ast.expr, *, namespace: dict[str, Any], filename: str) -> list[str]:
    """The text of each module constant `expr` passes to a function."""
    return [
        _evaluated(arg, namespace=namespace, filename=filename)
        for call in ast.walk(expr)
        if isinstance(call, ast.Call)
        for arg in (*call.args, *(keyword.value for keyword in call.keywords))
        if isinstance(arg, ast.Name)
    ]


def _names_a_value_constant(expr: ast.expr) -> bool:
    """Whether `expr` reads a member of `clauses.VALUE_CONSTANTS`."""
    return any(
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "clauses"
        and getattr(clauses, node.attr, None) in clauses.VALUE_CONSTANTS
        for node in ast.walk(expr)
    )


def composed_bodies(
    source: str, *, namespace: dict[str, Any], filename: str
) -> Iterator[tuple[str, list[Clause | None]]]:
    """Each `body=` f-string in `source`, composed against `namespace`, with the clause each character
    came from, or None for the module's own text."""
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.keyword) and node.arg == "body" and isinstance(node.value, ast.JoinedStr)):
            continue
        text: str = ""
        mask: list[Clause | None] = []
        for part in node.value.values:
            if isinstance(part, ast.Constant):
                if not isinstance(part.value, str):
                    continue
                text += part.value
                mask += [None] * len(part.value)
                continue
            if not isinstance(part, ast.FormattedValue):
                continue
            expr = part.value
            piece = _evaluated(expr, namespace=namespace, filename=filename)
            names = {name.id for name in ast.walk(expr) if isinstance(name, ast.Name)}
            piece_mask: list[Clause | None]
            if "clauses" not in names or PLACEHOLDER.fullmatch(piece) or _names_a_value_constant(expr):
                piece_mask = [None] * len(piece)
            else:
                clause = Clause(expr.lineno, expr.col_offset, ast.unparse(expr).split("(")[0])
                piece_mask = [clause] * len(piece)
                for own in _module_argument_texts(expr, namespace=namespace, filename=filename):
                    start = piece.find(own)
                    if start >= 0:
                        piece_mask[start : start + len(own)] = [None] * len(own)
            text += piece
            mask += piece_mask
        yield text, mask


def units(text: str) -> list[list[int]]:
    """The `[start, end)` span of each paragraph and list item of `text`, a list item's marker excluded."""
    spans: list[list[int]] = []
    current: list[int] | None = None
    pos = 0
    lines = text.split("\n")
    for line, kind in zip(lines, line_kinds([line.encode() for line in lines])):
        start = pos
        pos += len(line) + 1
        if kind in ("fence", "exact", "blank"):
            current = None
        elif kind == "item" or current is None:
            match = LIST_ITEM.match(line.encode())
            marker = match.end() if kind == "item" and match else 0
            current = [start + marker, start + len(line)]
            spans.append(current)
        else:
            current[1] = start + len(line)
    return spans


def join_sites(source: str, *, namespace: dict[str, Any], path: str) -> list[str]:
    """One `<path>:<line>: <clause> + …` line per unit of a body in `source` that joins a clause to
    the module's own text."""
    sites = []
    for text, mask in composed_bodies(source, namespace=namespace, filename=path):
        for start, end in units(text):
            clauses = sorted({clause for clause in mask[start:end] if clause is not None})
            own = "".join(text[i] for i in range(start, end) if mask[i] is None)
            if clauses and own.strip():
                sites.append(f"{path}:{clauses[0].lineno}: {' + '.join(clause.name for clause in clauses)}")
    return sites


def _definition_module_paths() -> list[Path]:
    """Every definition module's path under the repository root, its subpackages walked, in sorted
    path order."""
    return sorted(
        path for path in DEFINITIONS_ROOT.rglob("*.py") if not is_private(path.relative_to(DEFINITIONS_ROOT).parts)
    )


def main(paths: list[str]) -> int:
    total = 0
    for path in [Path(path) for path in paths] or _definition_module_paths():
        module = importlib.import_module(".".join(path.with_suffix("").parts))
        sites = join_sites(path.read_text(encoding="utf-8"), namespace=vars(module), path=str(path))
        for site in sites:
            print(site)
        total += len(sites)
    print(f"sites: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
