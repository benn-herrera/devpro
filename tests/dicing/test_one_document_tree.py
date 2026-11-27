"""Acceptance pins for the tree shapes [the model] states, which check_tree reads.

Each case is a literal tree written into a tmp_path and checked, so every expected outcome is
settled here rather than left to the CLI and the corpus harness.

- a one-document tree whose sections stand beside the root head as leaf documents — the form `dice`
  writes for a document with no level-2 section under the title;
- a one-document tree whose top-level directory opens at `index.md`: a section whichever head each
  opens at, so check_tree reports nothing.

A root opening at `index.md` is [undice](undice.md)'s to read, not check-tree's, whose root must open
at `entry-point.md` ([check-tree](check-tree.md#check-tree)); it is not a case here.
"""

import io
from pathlib import Path

import pytest

from devpro.dicing.treecheck import check_tree


def _tree(root: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")


@pytest.mark.parametrize(
    "files, documents",
    [
        pytest.param(
            {
                "entry-point.md": "# Title\n\nContents:\n\n- [One](one.md)\n",
                "one.md": "# One\n\none text\n",
            },
            2,
            id="a-section-beside-the-root-head",
        ),
        pytest.param(
            {
                "entry-point.md": "# Title\n\nContents:\n\n- [Section](section/index.md)\n",
                "section/index.md": "# Section\n\nContents:\n\n- [Sub](sub/index.md)\n",
                "section/sub/index.md": "# Sub\n\nsub text\n",
            },
            3,
            id="a-section-directory-in-a-one-document-tree",
        ),
    ],
)
def test_a_one_document_tree_passes_whichever_head_its_directories_open_at(
    tmp_path: Path, files: dict[str, str], documents: int
) -> None:
    root = tmp_path / "tree"
    _tree(root, files)
    err = io.StringIO()

    checked, problems = check_tree(str(root), err=err)

    assert (checked, problems) == (documents, 0), err.getvalue()
