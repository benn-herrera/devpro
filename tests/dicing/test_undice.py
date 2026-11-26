"""Unit tests for undice's stray-file check and its walk: which `.md` files under a volume are
reported, and as what.

Each report is identified by the tree paths it carries: a file read as another section names it and
the path it would be re-diced as, a file that opens no section names it alone, an unread file names
it and its volume's entry point.
"""

import io
import re
from pathlib import Path

import pytest

from devpro.dicing.dicedoc import Volume, _reproduced, _walk
from devpro.dicing.outline import DEEPEST_SPLIT_LEVEL, plan_sections

# Planned as entry-point.md (line 1), alpha.md (lines 2-3), beta.md (line 4).
MONOLITH = ["# Doc", "## Alpha", "text", "## Beta"]
ASSIGNED = ["entry-point.md", "alpha.md", "beta.md"]


@pytest.mark.parametrize(
    "extra, reads, reports",
    [
        pytest.param([], [("alpha.md", 2), ("beta.md", 4)], [], id="all-assigned"),
        pytest.param(
            ["old.md"], [("old.md", 2), ("beta.md", 4)], [["old.md", "alpha.md"]], id="read-as-another-section"
        ),
        pytest.param(
            ["dup.md"], [("dup.md", 2), ("dup.md", 4)], [["dup.md", "alpha.md"]], id="read-twice-first-section-wins"
        ),
        pytest.param(
            ["dup.md"], [("dup.md", 3), ("dup.md", 4)], [["dup.md", "beta.md"]], id="read-twice-first-opening-wins"
        ),
        pytest.param(["extra.md"], [("alpha.md", 2), ("extra.md", 3)], [["extra.md"]], id="read-mid-section"),
        pytest.param(["empty.md"], [("empty.md", None)], [["empty.md"]], id="read-empty"),
        pytest.param(["stray.md"], [], [["stray.md", "entry-point.md"]], id="not-read"),
        pytest.param(
            ["a.md", "b.md"], [], [["a.md", "entry-point.md"], ["b.md", "entry-point.md"]], id="each-stray-reported"
        ),
        pytest.param(["sub/y.md"], [], [["sub/y.md", "entry-point.md"]], id="subdirectory-without-entry-point"),
        pytest.param(["img.png"], [], [], id="not-markdown"),
    ],
)
def test_reproduced(
    tmp_path: Path, extra: list[str], reads: list[tuple[str, int | None]], reports: list[list[str]]
) -> None:
    out = tmp_path / "out"
    for name in ASSIGNED + extra:
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        (out / name).write_text("x\n", encoding="utf-8")
    sections, ok = plan_sections(MONOLITH, err=io.StringIO())
    assert ok
    err = io.StringIO()

    passed = _reproduced(
        Volume("entry-point.md", "", "Doc"), sections, reads, out=str(out), err=err, deepest=DEEPEST_SPLIT_LEVEL
    )

    assert passed == (not reports)
    reported = [re.findall(r"\S+\.md\b", line) for line in err.getvalue().splitlines()]
    assert sorted(reported) == sorted([f"{out}/{path}" for path in report] for report in reports)


def test_a_volume_is_walked_depth_first_in_link_order_once_each(tmp_path: Path) -> None:
    """The walk reads a volume's head, then the files its Contents links reach, depth first, a file
    once however many Contents blocks link it, and gives each part's document path with the line it
    starts at. The defect: the walk's body stood twice, in `visit` and beside it in `_walk`, so a
    change to what a part is — its lines, or the line it starts at — landed in one path and not the
    other, and a head read by both was numbered by whichever ran."""
    tree = tmp_path / "tree"
    files = {
        "entry-point.md": "# Doc\n\nContents:\n\n- [One](one/index.md)\n- [Two](two.md)\n",
        "one/index.md": "# One\n\nContents:\n\n- [Child](child.md)\n- [Two](../two.md)\n",
        "one/child.md": "# Child\n\ntext\n",
        "two.md": "# Two\n\ntext\n",
    }
    for name, text in files.items():
        (tree / name).parent.mkdir(parents=True, exist_ok=True)
        (tree / name).write_text(text, encoding="utf-8")
    err = io.StringIO()

    parts, reads, all_read = _walk(str(tree), "entry-point.md", err=err)

    assert all_read and err.getvalue() == ""
    assert [path for path, _ in parts] == ["entry-point.md", "one/index.md", "one/child.md", "two.md"]
    assert reads == [("entry-point.md", 1), ("one/index.md", 3), ("one/child.md", 5), ("two.md", 8)]
