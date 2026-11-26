"""The head-file names of a diced tree, fixed by convention and never configurable: a reader moving
between projects relies on finding them, and the standing project trees carry the same rule.

A tree has two structural patterns and no third. A **volume** is an original whole document, and its
top document is ENTRY_POINT: the tree's root carries one, and so does every direct child of the root
that is a volume of its own — the omnibus form `dice A.md B.md T/` writes. A **broken-out section**
is a piece diced out of a parent, and its top document is INDEX: every other directory holding a head
is one. Which pattern a directory is follows from the tree and not from the file alone: a direct
child of the root is a volume's directory and opens at ENTRY_POINT, and a directory below that opens
at INDEX. A one-document tree has no volume directory, so its top-level directories are sections;
its root's own head is a volume's whichever of the two it opens at, INDEX under `dice --section`.

volume_head gives a volume directory's head file's path and section_head a broken-out section's.
contents_cut is where a head's Contents block stands, and heads_of reads the block's lines for the
volume roots a root head declares; a directory of a one-document tree is a section, its head link or
not. contents_line spells each line a block lists.
"""

import os

from .linkscan import link_targets
from .textfile import read_lines

ENTRY_POINT = "entry-point.md"
INDEX = "index.md"
HEADS = (ENTRY_POINT, INDEX)
CONTENTS = "Contents:"


def contents_line(indent: str, *, text: str, path: str) -> str:
    """The one spelling of a Contents block's line: indent, then a list item linking path as text."""
    return f"{indent}- [{text}]({path})"


def contents_cut(lines: list[str]) -> int:
    """Index of the last line that is exactly CONTENTS: where a head's Contents block opens, -1
    where the lines hold none."""
    cut = len(lines) - 1
    while cut >= 0 and lines[cut] != CONTENTS:
        cut -= 1
    return cut


def heads_of(head: str) -> set[str]:
    """The directories a root head's Contents block declares volume roots: the directory of every
    `entry-point.md` the block's lines link, as the link names it. A link in the head's own prose
    declares nothing, however it is spelled, so the block's lines alone are read. Empty for a root
    opening at `index.md` and for a block that links no `entry-point.md` below the root — a
    one-document tree, whose directories are sections."""
    if os.path.basename(head) != ENTRY_POINT:
        return set()
    lines = read_lines(head)
    start = contents_cut(lines)
    if start < 0:
        return set()
    block = lines[start:]
    while block and not block[-1].lstrip().startswith("- "):
        block.pop()  # the block runs to its last list item; text after it is the head's own
    directories = set()
    for line in block:
        for target in link_targets(line):
            path = target.partition("#")[0]
            if path.endswith(f"/{ENTRY_POINT}"):
                directories.add(os.path.dirname(path))
    return directories


def volume_head(directory: str) -> str:
    """The path of the head file a volume directory opens at, beside it: ENTRY_POINT. The directory
    as given, kept as the path's prefix."""
    return f"{directory}/{ENTRY_POINT}" if directory else ENTRY_POINT


def section_head(directory: str) -> str:
    """The path of the head file a broken-out section directory opens at, beside it: INDEX. The
    directory as given, kept as the path's prefix."""
    return f"{directory}/{INDEX}" if directory else INDEX
