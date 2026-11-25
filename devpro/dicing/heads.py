"""The head-file names of a diced tree, fixed by convention and never configurable: a reader moving
between projects relies on finding them, and the standing project trees carry the same rule.

A tree's root — the root-head area beside `SPEC/`, `CONVENTIONS/` or `ARCHITECTURE/` when the tree
is one of a project's documents — opens at ENTRY_POINT; every directory inside the tree opens at
INDEX, the tree's own volumes included. directory_head gives a directory's head file's path. A
head's Contents block opens at its last line that is exactly CONTENTS; contents_line spells each
line it lists.
"""

ENTRY_POINT = "entry-point.md"
INDEX = "index.md"
HEADS = (ENTRY_POINT, INDEX)
CONTENTS = "Contents:"


def contents_line(indent: str, *, text: str, path: str) -> str:
    """The one spelling of a Contents block's line: indent, then a list item linking path as text."""
    return f"{indent}- [{text}]({path})"


def directory_head(directory: str, *, tree_root: bool) -> str:
    """The path of the head file a directory opens at, beside it: ENTRY_POINT where tree_root, the
    directory being a tree's root or a diced volume; INDEX otherwise. The caller states which, since
    a head being written does not exist yet for the answer to be read from. The directory as given,
    kept as the path's prefix."""
    name = ENTRY_POINT if tree_root else INDEX
    return f"{directory}/{name}" if directory else name
