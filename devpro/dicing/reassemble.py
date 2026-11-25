"""The reassembly check: the leaves, read in order with their Contents blocks dropped and section
links reverted, reproduce the monolith line for line (outside links compared in rebased form)."""

import os
from typing import TextIO

from .heads import CONTENTS, HEADS
from .linkrewrite import Linker, Tree, parent_dir
from .outline import _HEADING, Outline, Section
from .split import _rebased
from .textfile import FenceTracker, fence_flags, read_lines


def contents_cut(lines: list[str]) -> int:
    """Index of a head's Contents block: its last line that is exactly `Contents:`; -1 if none."""
    cut = len(lines) - 1
    while cut >= 0 and lines[cut] != CONTENTS:
        cut -= 1
    return cut


def own_end(path: str, lines: list[str]) -> int:
    """Where the lines of the tree file at path end as its own: at a head file's Contents block,
    else at the file's end."""
    cut = contents_cut(lines) if os.path.basename(path) in HEADS else -1
    return cut if cut >= 0 else len(lines)


def _top_is_rebased(leaf: list[str]) -> bool:
    """Whether a section's file opens at the re-based write form, its top heading at level 1. The
    pre-change form never does: no planned section is level 1 (`outline.plan_sections`). The entry
    point is not a section and its title is written as the monolith has it."""
    return bool(leaf and _HEADING.match(leaf[0]) and _HEADING.match(leaf[0]).end() == 2)


def check_reassembly(
    sections: list[Section],
    lines: list[str],
    tree: Tree,
    *,
    out: TextIO,
    err: TextIO,
    document_dir: str = "",
) -> bool:
    """Compare the tree's files with the monolith line for line, each section's path written under
    tree.out. document_dir is the directory the monolith's outside links are relative to, the tree's
    own directory where it is empty: the directory a dice read the volume's document from, or the one
    an undice wrote its document into."""
    linker = Linker(Outline(sections), tree, lines)
    fenced = fence_flags(lines)
    k = 0
    for s in sections:
        path = f"{tree.out}/{s.path}"
        try:
            leaf = read_lines(path)
        except OSError:
            print(f"reassemble: cannot read {path}", file=err)
            return False
        if s.kind != "L":
            cut = contents_cut(leaf)
            if cut < 0:
                print(f"reassemble: no Contents block in {path}", file=err)
                return False
            leaf = leaf[:cut]
        leaf_dir = parent_dir(s.path)
        fence = FenceTracker()
        # a leaf in the re-based form has its ladder shifted back for the compare; one in the
        # pre-change form is already at the monolith's levels and compares as it stands
        rebased = s.id > 0 and _top_is_rebased(leaf)
        for index, line in enumerate(leaf):
            inside = fence.inside(line)
            got = line if inside else linker.revert(line, leaf_dir)
            if rebased and not inside and _HEADING.match(got):
                # the writer moved the ladder up by 1 - s.level; the compare moves it back down
                got = _rebased(got, delta=s.level - 1, top=s.level if index == 0 else None)
            want = ""
            if k < len(lines):
                next_line = lines[k + 1] if k + 1 < len(lines) else ""
                want = lines[k] if fenced[k] else linker.written(lines[k], leaf_dir, next_line, document_dir)
            k += 1
            if got != want:
                print(
                    f"reassemble: first difference at monolith line {k} ({path})\n  want: {want}\n  got:  {got}",
                    file=err,
                )
                return False
    if k != len(lines):
        print(f"reassemble: leaves hold {k} lines, monolith {len(lines)}", file=err)
        return False
    print(f"reassemble ok: {k} lines", file=out)
    return True
