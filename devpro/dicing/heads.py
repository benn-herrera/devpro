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
A head's Contents block opens at its last line that is exactly CONTENTS; contents_line spells each
line it lists.
"""

ENTRY_POINT = "entry-point.md"
INDEX = "index.md"
HEADS = (ENTRY_POINT, INDEX)
CONTENTS = "Contents:"


def contents_line(indent: str, *, text: str, path: str) -> str:
    """The one spelling of a Contents block's line: indent, then a list item linking path as text."""
    return f"{indent}- [{text}]({path})"


def volume_head(directory: str) -> str:
    """The path of the head file a volume directory opens at, beside it: ENTRY_POINT. The directory
    as given, kept as the path's prefix."""
    return f"{directory}/{ENTRY_POINT}" if directory else ENTRY_POINT


def section_head(directory: str) -> str:
    """The path of the head file a broken-out section directory opens at, beside it: INDEX. The
    directory as given, kept as the path's prefix."""
    return f"{directory}/{INDEX}" if directory else INDEX
