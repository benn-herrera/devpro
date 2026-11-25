"""The write pass: each section's lines, links rewritten and its heading ladder re-based, into its
file under the output directory; the entry point and each section index end with a Contents block
listing what is below them.

A volume's head is the section planned at its root: the tree's own, or a head `volume_head` names for
one document of a volume tree. It holds that document's own text — its title and the text above its
first split heading — as it stands, and lists every section of the document below it."""

import os
import posixpath
from typing import TextIO

from .heads import CONTENTS, contents_line
from .linkrewrite import Linker, Tree, parent_dir, rel
from .outline import _HEADING, Outline, Section
from .textfile import fence_flags, write_lines


def contents_block(outline: Outline, section: Section) -> list[str]:
    """A volume head lists every section of its document, indented by depth; an index lists its
    children."""
    block = [CONTENTS, ""]
    if section.kind == "E":
        root = parent_dir(section.path)
        for s in outline.sections[1:]:
            indent = "  " * (outline.depth[s.id] - 1)
            block.append(contents_line(indent, text=outline.link_text(s.id), path=rel(root, s.path)))
        return block
    here = parent_dir(section.path)
    for kid in outline.children.get(section.id, []):
        block.append(contents_line("", text=outline.link_text(kid), path=rel(here, outline.sections[kid].path)))
    return block


def _rebased_level(line: str, *, delta: int, top: int | None = None) -> int:
    """The level a heading line writes at once its section's ladder has moved by `delta`: the level
    moves by the delta, so the heading's distance below the section's top is what the move keeps.
    A section's top heading, given `top`, lands at that level whatever it held."""
    return top if top is not None else _HEADING.match(line).end() - 1 + delta


def _shifted(line: str, level: int) -> str:
    """A heading line rewritten to open at `level` hashes: its heading text and number unchanged."""
    return "#" * level + line[_HEADING.match(line).end() - 1 :]


def _rebased(line: str, *, delta: int, top: int | None = None) -> str:
    """A heading line of a section whose ladder moved by `delta`, written at the re-based level."""
    return _shifted(line, _rebased_level(line, delta=delta, top=top))


def _fits(lines: list[str], s: Section, fenced: list[bool]) -> bool:
    """Whether every heading of the section's own text lands at a level 1 to 6 once re-based: one
    deeper than level 6 shifted down, or one at level 1 shifted up, has no level to write at, and
    its section is then written as the monolith has it and reported. A volume head's own text is the
    document's title and what sits above its first split heading, and no shift touches it."""
    for k in range(s.first - 1, s.last):
        if fenced[k] or not _HEADING.match(lines[k]):
            continue
        top = 1 if k == s.first - 1 else None
        if not 1 <= _rebased_level(lines[k], delta=_shift(s), top=top) <= 6:
            return False
    return True


def write_tree(sections: list[Section], lines: list[str], tree: Tree, *, err: TextIO, base: str = "") -> list[int]:
    """Write each section's own text to its file under base, the directory its paths are relative to
    (the tree's root where it is empty); returns the ids of the sections the re-base could not write,
    which are written at their monolith levels and left for the caller to fail on. Each file written
    is reported on err as `=== <kind> <path>`: `<kind>` the section's, a volume head's or a
    section's."""
    outline = Outline(sections)
    linker = Linker(outline, tree, lines)
    fenced = fence_flags(lines)
    unrebased = []
    for s in sections:
        leaf_dir = parent_dir(f"{base}/{s.path}" if base else s.path)
        if not _fits(lines, s, fenced):
            print(f"heading too deep to re-base at line {s.first} ({s.level}): written at its monolith level", file=err)
            unrebased.append(s.id)
        body = []
        for k in range(s.first - 1, s.last):
            next_line = lines[k + 1] if k + 1 < len(lines) else ""
            line = lines[k] if fenced[k] else linker.forward(lines[k], leaf_dir, next_line)
            if s.id not in unrebased and not fenced[k] and _HEADING.match(line):
                line = _rebased(line, delta=_shift(s), top=1 if k == s.first - 1 else None)
            body.append(line)
        if s.kind != "L":
            body += contents_block(outline, s)
        write_lines(os.path.join(tree.out, posixpath.join(base, s.path) if base else s.path), body)
        print(f"=== {_written_kind(s)} {posixpath.join(base, s.path) if base else s.path}", file=err)
    distinct = "".join(f" §{number}({count})" for number, count in linker.dangling.items())
    print(f"refs linked: {linker.resolved}; dangling: {len(linker.dangling)} distinct:{distinct}", file=err)
    return unrebased


def _written_kind(s: Section) -> str:
    """The kind of file a section is written as: a volume's head, or a section of the tree."""
    return "volume head" if s.kind == "E" else "section"


def _shift(s: Section) -> int:
    """The section's lines' level shift: a top heading lands at level 1, every other heading keeping
    its distance below it. A volume head's own text is the document's title and the text above its
    first split heading, and it is written as the source has it."""
    return 0 if s.kind == "E" else 1 - s.level
