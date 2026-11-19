"""Confirm each design delta's `becomes` block occurs byte-exact in its target leaf.

The design (default `ACTIVE_DESIGN.md` at the repository root) carries three `## ... delta`
sections — `## SPEC delta`, `## ARCHITECTURE delta`, `## Code delta`. Each `###` heading names a
target leaf in its markdown link, relative to the repository root. Within an entry a fenced code
block whose following non-blank line is `becomes` is a passage pair; the fenced block after the
`becomes` line is the applied text, and this checks that block's content occurs byte-exact as a
substring of the leaf. A trailing line boundary is not required: a replaced span often sits mid-line
or ends mid-sentence in its leaf. The `## Code delta` entries carry no fenced blocks, so they parse
as entries and contribute none.

Every becomes-block not found in its leaf is named — the design, the entry heading, the leaf, and
the block — and an unparseable entry (a `becomes` with no following fenced block, a `###` heading
with no link) or a missing leaf is named too; that detection is the point of the tool. Exits zero
when every becomes-block occurs in its leaf, non-zero otherwise.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

SECTIONS = ("SPEC delta", "ARCHITECTURE delta", "Code delta")

_HEADING = re.compile(r"^(#{1,6})\s")
_LINK = re.compile(r"\]\(([^)]+)\)")


@dataclass(frozen=True)
class Entry:
    section: str
    heading_line: int
    heading: str
    link: str | None
    start: int
    end: int


def _heading_level(line: str) -> int | None:
    m = _HEADING.match(line)
    return len(m.group(1)) if m else None


def _is_fence(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def _read_fence(lines: list[str], i: int) -> tuple[list[str] | None, int | None]:
    """`lines[i]` opens a fenced block. Return its content lines and the index just past the closing
    fence, or `(None, None)` if the block is never closed."""
    j = i + 1
    while j < len(lines) and not _is_fence(lines[j]):
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


def _parse_entries(lines: list[str]) -> list[Entry]:
    """Each `###` entry of a tracked `## ... delta` section, with its line range in `lines`."""
    entries = []
    i = 0
    n = len(lines)
    section = None
    while i < n:
        if _is_fence(lines[i]):
            _, nxt = _read_fence(lines, i)
            i = n if nxt is None else nxt
            continue
        level = _heading_level(lines[i])
        if level == 2:
            text = lines[i].strip()[2:].strip()
            section = text if text in SECTIONS else None
            i += 1
        elif level == 3 and section is not None:
            heading = lines[i].strip()[3:].strip()
            start = i
            j = i + 1
            while j < n:
                if _is_fence(lines[j]):
                    _, j2 = _read_fence(lines, j)
                    j = n if j2 is None else j2
                    continue
                hl = _heading_level(lines[j])
                if hl is not None and hl <= 3:
                    break
                j += 1
            entries.append(Entry(section, start + 1, heading, _link_target(heading), start, j))
            i = j
        else:
            i += 1
    return entries


def _parse_pairs(lines: list[str], start: int, end: int) -> tuple[list[tuple[str, int]], list[str]]:
    """Within `lines[start:end]`, the `(applied text, design line of its opening fence)` of each
    passage pair, and a list of malformation descriptions."""
    pairs: list[tuple[str, int]] = []
    problems: list[str] = []
    i = start
    while i < end:
        if not _is_fence(lines[i]):
            i += 1
            continue
        content, nxt = _read_fence(lines, i)
        if content is None:
            problems.append(f"unclosed fenced block at line {i + 1}")
            break
        becomes = _becomes_index(lines, nxt, end)
        if becomes is None:
            i = nxt
            continue
        k = becomes + 1
        while k < end and not _is_fence(lines[k]):
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
        pairs.append(("\n".join(applied_lines), k + 1))
        i = nxt2
    return pairs, problems


def main(argv: list[str]) -> int:
    design_path = Path(argv[0]) if argv else Path("ACTIVE_DESIGN.md")
    lines = design_path.read_text(encoding="utf-8").split("\n")
    checked = misses = problems = 0
    print(f"delta byte-check: {design_path}")
    for entry in _parse_entries(lines):
        if entry.link is None:
            problems += 1
            print(
                f"  PROBLEM {design_path}:{entry.heading_line} [{entry.section}] {entry.heading}: "
                "### entry heading with no link"
            )
            continue
        leaf = Path(entry.link)
        if not leaf.is_file():
            problems += 1
            print(
                f"  PROBLEM {design_path}:{entry.heading_line} [{entry.section}] {entry.heading}: "
                f"missing leaf {entry.link}"
            )
            continue
        leaf_text = leaf.read_text(encoding="utf-8")
        pairs, problems_ = _parse_pairs(lines, entry.start, entry.end)
        for why in problems_:
            problems += 1
            print(
                f"  PROBLEM {design_path}:{entry.heading_line} [{entry.section}] {entry.heading}: {why}"
            )
        for applied, anchor in pairs:
            checked += 1
            if applied not in leaf_text:
                misses += 1
                print(f"  MISS {design_path}:{anchor} [{entry.section}] {entry.heading}")
                print(f"    leaf: {entry.link}")
                for block_line in applied.split("\n"):
                    print(f"    {block_line}")

    print()
    if misses or problems:
        print(f"{misses} not applied, {problems} problems, {checked} becomes-blocks checked")
        return 1
    print(f"all {checked} becomes-blocks occur byte-exact in their leaves")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
