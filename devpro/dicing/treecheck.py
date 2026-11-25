"""The tree check: in a diced tree, every document is linked from its parent, and every document is
reachable by links from the root's entry point.

A tree has two structural patterns ([heads](heads.py)). Its root is a volume, opening at
`entry-point.md`; a direct child of the root holding an `entry-point.md` is a volume of its own; and
every other directory holding an `index.md` is a broken-out section. A top-level directory whose head
is `index.md` is neither: it is a section where the tree's own form says a volume stands, and it is
reported as one. A document's parent is its directory's head; a head's parent is its parent
directory's head; the root's own head has none.
"""

import os
from collections import deque
from typing import TextIO

from .heads import ENTRY_POINT, HEADS, INDEX
from .linkcheck import markdown_files, prose_links
from .linkrewrite import URL_SCHEME
from .textfile import read_lines


def _head(directory: str) -> str | None:
    for name in HEADS:
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            return path
    return None


def _misplaced_head(root: str) -> set[str]:
    """The top-level directories of a volume tree that open at `index.md` instead of `entry-point.md`:
    a tree whose root's head links an `entry-point.md` below it is the omnibus form, and every
    top-level directory under it is a volume's. A tree whose root links none is one document's, and
    its top-level directories are sections. Neither is misplacement; both are valid trees."""
    entry = os.path.join(root, ENTRY_POINT)
    volumes = {
        os.path.dirname(target.partition("#")[0])
        for _, target in prose_links(read_lines(entry))
        if target.partition("#")[0].endswith(f"/{ENTRY_POINT}")
    }
    if not volumes:
        return set()
    misplaced = set()
    for name in os.listdir(root):
        directory = os.path.join(root, name)
        if not os.path.isdir(directory) or name in volumes:
            continue
        if os.path.isfile(os.path.join(directory, INDEX)) and not os.path.isfile(os.path.join(directory, ENTRY_POINT)):
            misplaced.add(os.path.realpath(directory))
    return misplaced


def _links_to(path: str) -> set[str]:
    """The real paths of the files a document's relative links name, fragments dropped."""
    found = set()
    for _, target in prose_links(read_lines(path)):
        ref = target.partition("#")[0]
        if ref == "" or ref.startswith("/") or URL_SCHEME.match(ref):
            continue
        found.add(os.path.realpath(os.path.join(os.path.dirname(path), ref)))
    return found


def check_tree(root: str, *, err: TextIO) -> tuple[int, int]:
    """(documents checked, problems) for one tree, each problem reported on err."""
    entry = os.path.join(root, ENTRY_POINT)
    if not os.path.isfile(entry):
        print(f"{root}: no {ENTRY_POINT}", file=err)
        return 0, 1
    files = markdown_files([root])
    real = {os.path.realpath(f): f for f in files}
    links = {f: _links_to(f) for f in files}
    misplaced = _misplaced_head(root)
    problems = 0
    root_real = os.path.realpath(root)
    for f in files:
        directory = os.path.dirname(f)
        if os.path.realpath(f) == os.path.realpath(entry):
            continue
        own_head = _head(directory)
        is_head = own_head is not None and os.path.realpath(own_head) == os.path.realpath(f)
        if is_head and os.path.realpath(directory) in misplaced:
            print(
                f"{f}: a volume directory of this tree opens at {ENTRY_POINT}, not {INDEX}: a volume's sections sit below it",
                file=err,
            )
            problems += 1
        parent = _head(os.path.dirname(directory)) if is_head else own_head
        if parent is None or not os.path.realpath(os.path.dirname(parent)).startswith(root_real):
            print(f"{f}: no parent document (an {INDEX} or {ENTRY_POINT} beside it or above it)", file=err)
            problems += 1
            continue
        if os.path.realpath(f) not in links[parent]:
            print(f"{f}: not linked from its parent {parent}", file=err)
            problems += 1
    seen = {os.path.realpath(entry)}
    queue = deque([entry])
    while queue:
        for dest in links[queue.popleft()]:
            if dest in real and dest not in seen:
                seen.add(dest)
                queue.append(real[dest])
    for f in files:
        if os.path.realpath(f) not in seen:
            print(f"{f}: not reachable from {entry}", file=err)
            problems += 1
    return len(files), problems


def check_trees(roots: list[str], *, out: TextIO, err: TextIO) -> bool:
    checked = problems = 0
    for root in roots:
        n, p = check_tree(root, err=err)
        checked += n
        problems += p
    print(f"documents checked: {checked}, problems: {problems}", file=out)
    return problems == 0
