import pytest

from devpro.dicing.dicedoc import _placed_level
from devpro.dicing.heads import contents_cut
from devpro.dicing.reassemble import own_end, top_is_rebased
from devpro.dicing.split import _rebased


@pytest.mark.parametrize(
    "lines, cut",
    [
        pytest.param(["## A", "text", "Contents:", "", "- [b](b.md)"], 2, id="block-at-end"),
        pytest.param(["Contents:", "quoted", "Contents:", ""], 2, id="last-of-two"),
        pytest.param(["## A", "Contents:", "", "- [b](b.md)", "", "- [G](g/index.md)"], 1, id="lines-after-block"),
        pytest.param(["## A", "Contents: ", " Contents:", "contents:"], -1, id="not-exact-no-block"),
    ],
)
def test_contents_cut_is_last_exact_contents_line(lines, cut):
    assert contents_cut(lines) == cut


_WITH_CONTENTS = ["## A", "Contents:", "", "- [b](b.md)"]


@pytest.mark.parametrize(
    "path, lines, end",
    [
        pytest.param("entry-point.md", _WITH_CONTENTS, 1, id="entry-point"),
        pytest.param("g/index.md", _WITH_CONTENTS, 1, id="index"),
        pytest.param("g/v/entry-point.md", _WITH_CONTENTS, 1, id="nested-volume"),
        pytest.param("g/leaf.md", _WITH_CONTENTS, 4, id="leaf-keeps-its-contents-line"),
        pytest.param("index.md", ["## A", "text"], 2, id="head-without-block"),
    ],
)
def test_own_end_cuts_only_a_head_file_at_its_contents_block(path, lines, end):
    assert own_end(path, lines) == end


@pytest.mark.parametrize(
    "level, delta, top, written",
    [
        pytest.param(2, -1, 1, 1, id="a-level-2-section-writes-its-top-at-one"),
        pytest.param(4, -3, 1, 1, id="a-level-4-section-writes-its-top-at-one"),
        pytest.param(4, -1, None, 3, id="a-level-4-heading-in-a-level-2-section-writes-at-three"),
        pytest.param(5, -2, None, 3, id="a-level-5-heading-two-below-a-level-3-top-writes-at-three"),
        pytest.param(1, 0, 1, 1, id="the-entry-points-title-stands-still"),
        pytest.param(1, 2, 3, 3, id="a-top-the-check-puts-back-at-its-source-level"),
    ],
)
def test_a_rebased_level_moves_the_ladder_by_its_delta(level, delta, top, written):
    """The written form: a section's top lands at level 1, and every other heading moves by the same
    delta the top did, so its distance below the top is what the move keeps."""
    assert _rebased("#" * level + " T", delta=delta, top=top) == "#" * written + " T"


@pytest.mark.parametrize(
    "leaf, rebased",
    [
        pytest.param(["# 1. A", "", "text"], True, id="written-form-top-at-one"),
        pytest.param(["## 1. A", "", "text"], False, id="pre-change-top-at-two"),
        pytest.param(["### 1.1 A", "", "text"], False, id="pre-change-top-at-three"),
        pytest.param(["text"], False, id="no-heading"),
        pytest.param([], False, id="empty-file"),
    ],
)
def test_only_a_level_1_top_is_the_written_form(leaf, rebased):
    """The two forms are told apart by the top heading alone: `plan_sections` plans no level-1
    section, so a pre-change leaf's top is never level 1, and a written leaf's top always is."""
    assert top_is_rebased(leaf) is rebased


@pytest.mark.parametrize(
    "path, level",
    [
        pytest.param("2-two.md", 2, id="root-leaf"),
        pytest.param("1-one/index.md", 2, id="root-index"),
        pytest.param("1-one/1.1-sub.md", 3, id="child-of-an-index"),
        pytest.param("sec/sub.md", 3, id="child-carrying-a-deeper-heading-sits-beside-its-siblings"),
        pytest.param("a/b/c/d/e/f.md", None, id="a-placement-no-legal-heading-reaches-is-refused"),
        pytest.param("a/b/c/d/e/f/index.md", None, id="an-index-no-legal-heading-reaches-is-refused"),
    ],
)
def test_a_part_is_restored_to_the_level_its_place_in_the_tree_fixes(path, level):
    """The tree does not carry the level a re-based section came from, so a restored heading sits at
    its place's level: a directory holding a section index counts as that index's level, so a section
    index's children and a childless section at the same depth sit beside each other. A part's own
    ladder never moves it. A place deeper than the last heading level has no document to be restored
    into, and none is: the part is refused, never written at a level markdown cannot hold."""
    assert _placed_level(path) == level
