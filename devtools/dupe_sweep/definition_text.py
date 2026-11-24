"""dupe_sweep — one rule, two homes: the sentences a definition module carries as string literals.

A definition module is its rendered text with placeholders, so its prose lives in string
literals: two modules stating one rule hold it in two literals, and :mod:`doc_sentences` reads
neither. Each literal is rejoined across its hard wrap and split by
:func:`doc_sentences.block_sentences`, so a sentence means here what it means in a docstring; a
sentence's line is the literal's line, which is the line the reader opens the module at.

A literal carrying no whitespace — a placeholder, a directory name, a lone word — is not prose,
and contributes no sentence. A docstring contributes none either: it is a literal, and
:func:`doc_sentences.doc_units` already reads it.
"""

import ast
from collections.abc import Iterator

from .clustering import Unit
from .doc_sentences import block_sentences, docstring_nodes
from .normalization import prose_tokens
from .python_corpus import parse_module

#: The definition-module areas whose string literals are prose the renderings carry.
DEFINITION_TEXT_PREFIXES = ("devpro/definitions/", "devpro/harnesses/", "devpro/clauses.py")


def definition_text_units(files: dict[str, str]) -> list[Unit]:
    """Every sentence of every string literal in the definition modules among `files`."""
    units = []
    for path, text in sorted(files.items()):
        if not path.startswith(DEFINITION_TEXT_PREFIXES):
            continue
        tree = parse_module(path, text)
        if tree is None:
            continue
        for literal in _literals(tree):
            label = f"string literal at {literal.lineno}"
            for line, sentence in block_sentences([(literal.lineno, literal.value)]):
                units.append(Unit(path, line, label, sentence, prose_tokens(sentence)))
    return units


def _literals(tree: ast.Module) -> Iterator[ast.Constant]:
    """Every string literal that holds prose — text with a whitespace character in it.

    A docstring is a string literal and is skipped: :func:`~.doc_sentences.doc_units` already
    reads it, and a sentence reported against its own docstring is not two homes.
    """
    docstrings = {id(node) for node in docstring_nodes(tree)}
    for node in ast.walk(tree):
        if id(node) in docstrings or not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if any(char.isspace() for char in node.value):
            yield node
