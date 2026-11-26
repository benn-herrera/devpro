"""dupe_sweep — the ``python`` pass: it reads its corpus, compares, and reports.

``python`` answers three questions — one concept, two implementations; one constant, two
definitions; one rule, two homes — and prints :data:`UNANSWERED` for the fourth, one word with two
meanings: nothing in the source tells a term's referents apart, so it is reported as unanswered
rather than approximated.

A rule's two homes are read from docstrings, comments and, in the rendered-prose modules, string
literals: a rendering's prose is a literal, so it is a sentence unit beside the other two.

Every stage sorts its output, so the same tree yields the same report, byte for byte.
"""

from typing import TextIO, TypedDict

from .clustering import clusters
from .constants import constant_candidates, constants
from .definition_text import definition_text_units
from .doc_sentences import doc_units
from .python_corpus import CODE_PREFIXES, CODE_UNSWEPT, code_corpus
from .report import render_clusters, render_constants, render_header
from .shapes import shape_units


class ClusteringSettings(TypedDict):
    """The keyword parameters `clusters` takes, which a pass's defaults supply whole."""

    min_tokens: int
    coverage: float
    width: int
    length_ratio: float
    probes: int | None


#: Defaults, tuned on this tree for a list short enough to read. Thirty AST nodes is roughly ten
#: lines, and a structural clone is worth a reader's time only when it is near-exact, hence the
#: high containment bar and the tight length window on code.
CODE_DEFAULTS: ClusteringSettings = {
    "min_tokens": 30,
    "coverage": 0.90,
    "width": 5,
    "length_ratio": 0.7,
    "probes": 8,
}
DOC_DEFAULTS: ClusteringSettings = {
    "min_tokens": 12,
    "coverage": 0.85,
    "width": 4,
    "length_ratio": 0.6,
    "probes": None,
}

#: Printed in place of the fourth question's findings.
UNANSWERED = (
    "    No mechanical proxy for a term's referent survives contact with this tree.\n"
    '    The instance this was calibrated against is "row", used for a steps.Step and\n'
    "    for a line of a plan table — and every proxy for it (a name bound to two\n"
    "    types, a word appearing in two modules) fires on every common name here.\n"
    "    What would answer it is a glossary naming each project term and the one\n"
    "    thing it may refer to; the check is mechanical after that, guesswork before."
)


def python_pass(*, rev: str | None, settings: ClusteringSettings, out: TextIO) -> None:
    files = code_corpus(rev=rev)
    shapes = shape_units(files)
    docs = doc_units(files) + definition_text_units(files)
    compared = ", ".join(f"{prefix}/" for prefix in CODE_PREFIXES)
    scope = f"{compared} less {', '.join(CODE_UNSWEPT)}, the rendered-prose modules' literals among its sentence units"
    render_header("python", rev, scope, f"{len(shapes) + len(docs)} spans", out)
    render_clusters("one concept, two implementations", clusters(shapes, **settings), out=out)
    render_constants(constant_candidates(constants(files)), out=out)
    render_clusters("one rule, two homes", clusters(docs, **DOC_DEFAULTS), out=out)
    print("\n## one word, two meanings — UNANSWERED, not zero candidates", file=out)
    print(UNANSWERED, file=out)
