"""Confirm each design delta's `becomes` block occurs byte-exact in its target leaf.

A design's entries come from its one source. Undiced, that is the design document — the argument,
default `ACTIVE_DESIGN.md` at the repository root — carrying three `## ... delta` sections:
`## SPEC delta`, `## ARCHITECTURE delta` and `## Code delta`. Diced, it is the tree that replaced the
document — `ACTIVE_DESIGN/` beside `ACTIVE_DESIGN.md` — whose `spec-delta/`, `architecture-delta/`
and `code-delta/` directories hold one entry per `.md` leaf, every `index.md` aside. The tree is
read wherever a same-stem directory carrying `entry-point.md` sits beside the design path, and the
document otherwise; where neither is there, the design is missing.

Each entry's `###` heading names a target leaf in its markdown link: relative to the link base in a
document — the second argument, the invocation directory when it is not given; the recipe passes
the repository root — and relative to the leaf's own directory in a tree, whose links are
leaf-relative, which is why a document reader cannot read the tree verbatim. Within an entry a
fenced code block whose following non-blank line is `becomes` is a passage pair; the fenced block
after the `becomes` line is the applied text, and this checks that block's content occurs byte-exact
as a substring of the leaf.
A trailing line boundary is not required: a replaced span often sits mid-line or ends mid-sentence in
its leaf. Fences follow CommonMark, as `render_diff` pins them: an opener is three or more backticks
with an info string holding no backtick, or three or more tildes, and the closer is the same
character, at least as many, with nothing else on the line — so a passage's own fenced example stays
inside the block rather than ending it. Code delta entries carry no passage pair, so they parse as
entries and contribute none.

The block before `becomes` is the from-text: where the becomes-text does not contain it, it must be
gone, because a leaf still holding it while its becomes-text is present reads as applied while the
replacement never happened — a deletion whose becomes-text pre-existed. Both present is a MISS
naming the leaf. A becomes-text that contains its from-text is an addition, so the from-text's
survival there is the applied state.

A passage pair carrying a markdown link can never pass: the design's link resolves from the
repository root, or from the entry's own directory in a tree, and the target leaf's from the leaf's
own directory, so the applied text rebases the target and no longer occurs byte-exact. Nothing
false-fails today — no passage pair in the current design holds a link inside its fenced block.

Every becomes-block not found in its leaf is named — the file holding the entry, the entry heading,
the leaf, and the block — and a section leaf yielding no entry (a heading that is not `###`, no
heading at all), an unparseable entry (a `becomes` with no following fenced block, a `###` heading
with no link), a missing leaf or a missing design file is named too; that detection is the point of
the tool. Exits zero when every becomes-block occurs in its leaf and no from-text survives, non-zero
otherwise.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Each tree section directory with the label its entries are reported under.
SECTION_DIRS = {
    "spec-delta": "SPEC delta",
    "architecture-delta": "ARCHITECTURE delta",
    "code-delta": "Code delta",
}

_HEADING = re.compile(r"^(#{1,6})\s")
_LINK = re.compile(r"\]\(([^)]+)\)")
# `render_diff`'s two fence patterns, over text: the opener's run of backticks with an info string
# holding none, or its run of tildes; the closer the same character, at least as many, nothing else.
_FENCE_OPEN = re.compile(r" {0,3}(?:(`{3,})[^`]*|(~{3,}).*)")
_FENCE_CLOSE = re.compile(r" {0,3}(`{3,}|~{3,})[ \t]*")


@dataclass(frozen=True)
class Entry:
    section: str
    heading_line: int
    heading: str
    link: str | None
    start: int
    end: int


@dataclass(frozen=True)
class EntrySource:
    """One file holding design entries, and the directory its heading links resolve against."""

    path: Path
    link_base: Path
    lines: list[str]
    entries: list[Entry]


def _heading_level(line: str) -> int | None:
    m = _HEADING.match(line)
    return len(m.group(1)) if m else None


def _fence_opener(line: str) -> str | None:
    """The fence `line` opens, its run of backticks or tildes, or None where it opens none."""
    m = _FENCE_OPEN.fullmatch(line)
    if m is None:
        return None
    return m.group(1) or m.group(2)


def _closes_fence(line: str, opener: str) -> bool:
    """Whether `line` closes the fence `opener`: the same character, at least as many, nothing else."""
    m = _FENCE_CLOSE.fullmatch(line)
    if m is None:
        return False
    closer = m.group(1)
    return closer[:1] == opener[:1] and len(closer) >= len(opener)


def _read_fence(lines: list[str], i: int) -> tuple[list[str] | None, int | None]:
    """`lines[i]` opens a fenced block. Return its content lines and the index just past the closing
    fence, or `(None, None)` if no line closes it."""
    opener = _fence_opener(lines[i])
    if opener is None:
        return None, None
    j = i + 1
    while j < len(lines) and not _closes_fence(lines[j], opener):
        j += 1
    if j >= len(lines):
        return None, None
    return lines[i + 1 : j], j + 1


def _becomes_index(lines: list[str], after_fence: int, end: int) -> int | None:
    """The index of the first non-blank line at or after `after_fence`, if it reads `becomes`; else
    None."""
    j = after_fence
    while j < end and not lines[j].strip():
        j += 1
    if j < end and lines[j].strip() == "becomes":
        return j
    return None


def _link_target(heading: str) -> str | None:
    m = _LINK.search(heading)
    if not m:
        return None
    target = m.group(1).strip().split("#", 1)[0].strip()
    return target or None


def _parse_entries(lines: list[str], *, section: str | None = None) -> list[Entry]:
    """Each `###` entry of a tracked `## ... delta` section, with its line range in `lines`. Given
    `section`, the whole text belongs to it: a tree leaf is one entry and carries no section heading.
    """
    entries = []
    i = 0
    n = len(lines)
    current = section
    while i < n:
        if _fence_opener(lines[i]) is not None:
            _, nxt = _read_fence(lines, i)
            i = n if nxt is None else nxt
            continue
        level = _heading_level(lines[i])
        if section is None and level == 2:
            text = lines[i].strip()[2:].strip()
            current = text if text in SECTION_DIRS.values() else None
            i += 1
        elif level == 3 and current is not None:
            heading = lines[i].strip()[3:].strip()
            start = i
            j = i + 1
            while j < n:
                if _fence_opener(lines[j]) is not None:
                    _, j2 = _read_fence(lines, j)
                    j = n if j2 is None else j2
                    continue
                hl = _heading_level(lines[j])
                if hl is not None and hl <= 3:
                    break
                j += 1
            entries.append(Entry(current, start + 1, heading, _link_target(heading), start, j))
            i = j
        else:
            i += 1
    return entries


def _parse_pairs(lines: list[str], start: int, end: int) -> tuple[list[tuple[str, str, int]], list[str]]:
    """Within `lines[start:end]`, the `(from text, applied text, design line of the applied block's
    opening fence)` of each passage pair, and a list of malformation descriptions."""
    pairs: list[tuple[str, str, int]] = []
    problems: list[str] = []
    i = start
    while i < end:
        if _fence_opener(lines[i]) is None:
            i += 1
            continue
        from_lines, nxt = _read_fence(lines, i)
        if from_lines is None:
            problems.append(f"unclosed fenced block at line {i + 1}")
            break
        becomes = _becomes_index(lines, nxt, end)
        if becomes is None:
            i = nxt
            continue
        k = becomes + 1
        while k < end and _fence_opener(lines[k]) is None:
            k += 1
        if k >= end:
            problems.append(f"`becomes` at line {becomes + 1} with no following fenced block")
            i = k
            continue
        applied_lines, nxt2 = _read_fence(lines, k)
        if applied_lines is None:
            problems.append(f"unclosed applied fenced block at line {k + 1}")
            i = k + 1
            continue
        pairs.append(("\n".join(from_lines), "\n".join(applied_lines), k + 1))
        i = nxt2
    return pairs, problems


def _tree_sources(tree: Path) -> list[EntrySource]:
    """The diced tree at `tree`: each section directory's `*.md` leaves but its `index.md`, one entry
    per leaf, each heading's link resolving from the leaf's own directory."""
    sources = []
    for dirname, section in SECTION_DIRS.items():
        for leaf in sorted((tree / dirname).glob("*.md")):
            if leaf.name == "index.md":
                continue
            lines = leaf.read_text(encoding="utf-8").split("\n")
            entries = _parse_entries(lines, section=section)
            sources.append(EntrySource(leaf, leaf.parent, lines, entries))
    return sources


def _design_sources(design: Path, link_base: Path) -> tuple[Path, list[EntrySource]] | None:
    """The design's one source, as the path to report and its entry sources: the diced tree beside
    `design` where one sits there, else `design` itself, whose links resolve from `link_base`; None
    where neither is present."""
    tree = design.with_suffix("")
    if (tree / "entry-point.md").is_file():
        return tree, _tree_sources(tree)
    if design.is_file():
        lines = design.read_text(encoding="utf-8").split("\n")
        return design, [EntrySource(design, link_base, lines, _parse_entries(lines))]
    return None


def main(argv: list[str]) -> int:
    design_path = Path(argv[0]) if argv else Path("ACTIVE_DESIGN.md")
    link_base = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    resolved = _design_sources(design_path, link_base)
    if resolved is None:
        print(f"PROBLEM {design_path}: missing design")
        return 1
    source_path, sources = resolved
    checked = misses = problems = 0
    print(f"delta byte-check: {source_path}")
    for source in sources:
        if not source.entries:
            problems += 1
            print(f"PROBLEM {source.path}: no entry")
        for entry in source.entries:
            where = f"{source.path}:{entry.heading_line} [{entry.section}] {entry.heading}"
            if entry.link is None:
                problems += 1
                print(f"  PROBLEM {where}: ### entry heading with no link")
                continue
            leaf = source.link_base / entry.link
            if not leaf.is_file():
                problems += 1
                print(f"  PROBLEM {where}: missing leaf {entry.link}")
                continue
            leaf_text = leaf.read_text(encoding="utf-8")
            pairs, problems_ = _parse_pairs(source.lines, entry.start, entry.end)
            for why in problems_:
                problems += 1
                print(f"  PROBLEM {where}: {why}")
            for from_text, applied, anchor in pairs:
                checked += 1
                if applied not in leaf_text:
                    misses += 1
                    print(f"  MISS {source.path}:{anchor} [{entry.section}] {entry.heading}")
                    print(f"    leaf: {entry.link}")
                    for block_line in applied.split("\n"):
                        print(f"    {block_line}")
                elif from_text and from_text not in applied and from_text in leaf_text:
                    misses += 1
                    print(f"  MISS {source.path}:{anchor} [{entry.section}] {entry.heading}")
                    print(f"    leaf: {entry.link} still holds the from-text")
                    for block_line in from_text.split("\n"):
                        print(f"    {block_line}")

    print()
    if misses or problems:
        print(f"{misses} not applied, {problems} problems, {checked} becomes-blocks checked")
        return 1
    print(f"all {checked} becomes-blocks occur byte-exact in their leaves")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
