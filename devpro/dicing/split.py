"""The write pass: each section's lines, links rewritten and its heading ladder re-based, into its
file under the output directory; the entry point and each section index end with a Contents block
listing what is below them."""

from typing import TextIO

from .heads import CONTENTS, contents_line
from .linkrewrite import Linker, Tree, parent_dir, rel
from .outline import _HEADING, Outline, Section
from .textfile import fence_flags, write_lines


def contents_block(outline: Outline, section: Section) -> list[str]:
    """The entry point lists every section, indented by depth; an index lists its children."""
    block = [CONTENTS, ""]
    if section.id == 0:
        for s in outline.sections[1:]:
            indent = "  " * (outline.depth[s.id] - 1)
            block.append(contents_line(indent, text=outline.link_text(s.id), path=s.path))
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
    its section is then written as the monolith has it and reported."""
    for k in range(s.first - 1, s.last):
        if fenced[k] or not _HEADING.match(lines[k]):
            continue
        top = 1 if k == s.first - 1 else None
        if not 1 <= _rebased_level(lines[k], delta=1 - s.level, top=top) <= 6:
            return False
    return True


def write_tree(sections: list[Section], lines: list[str], tree: Tree, *, err: TextIO) -> list[int]:
    """Write each section's own text to its file; returns the ids of the sections the re-base could
    not write, which are written at their monolith levels and left for the caller to fail on."""
    outline = Outline(sections)
    linker = Linker(outline, tree, lines)
    fenced = fence_flags(lines)
    unrebased = []
    for s in sections:
        leaf_dir = parent_dir(s.path)
        if not _fits(lines, s, fenced):
            print(f"heading too deep to re-base at line {s.first} ({s.level}): written at its monolith level", file=err)
            unrebased.append(s.id)
        body = []
        for k in range(s.first - 1, s.last):
            next_line = lines[k + 1] if k + 1 < len(lines) else ""
            line = lines[k] if fenced[k] else linker.forward(lines[k], leaf_dir, next_line)
            if s.id not in unrebased and not fenced[k] and _HEADING.match(line):
                line = _rebased(line, delta=1 - s.level, top=1 if k == s.first - 1 else None)
            body.append(line)
        if s.kind != "L":
            body += contents_block(outline, s)
        write_lines(f"{tree.out}/{s.path}", body)
    distinct = "".join(f" §{number}({count})" for number, count in linker.dangling.items())
    print(f"refs linked: {linker.resolved}; dangling: {len(linker.dangling)} distinct:{distinct}", file=err)
    return unrebased
