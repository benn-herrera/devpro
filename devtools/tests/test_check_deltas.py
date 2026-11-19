"""`check_deltas` over designs written for the case: both verdicts, each failure the tool names, and
the fence rule that keeps a passage's own fenced example from ending the block it belongs to."""

from __future__ import annotations

from pathlib import Path

from devtools.check_deltas import main

_REPLACED = "The replaced sentence."
_ENTRY = "### [ARCHITECTURE.md, Install, Guardrail hook]({leaf})"
# A passage whose text holds a fenced example of its own.
_WITH_EXAMPLE = 'The sample:\n\n```json\n{"a": 1}\n```\n\nAnd the tail.'


def _passage(tmp_path: Path, applied: str, *, leaf: str | None = None, fence: str = "```") -> Path:
    """A one-entry design whose passage pair replaces `_REPLACED` with `applied`, beside a leaf holding
    `leaf` or the applied text between a lead and a tail."""
    leaf_path = tmp_path / "leaf.md"
    leaf_path.write_text(leaf if leaf is not None else f"Lead. {applied} Tail.\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text(
        "# design\n\n"
        "## ARCHITECTURE delta\n\n"
        f"{_ENTRY.format(leaf=leaf_path)}\n\n"
        f"{fence}\n{_REPLACED}\n{fence}\n"
        "becomes\n"
        f"{fence}\n{applied}\n{fence}\n",
        encoding="utf-8",
    )
    return design


def test_an_applied_passage_passes(tmp_path: Path, capsys) -> None:
    design = _passage(tmp_path, "The new sentence.")
    assert main([str(design)]) == 0
    assert "all 1 becomes-blocks occur byte-exact in their leaves" in capsys.readouterr().out


def test_a_passage_its_leaf_does_not_hold_is_a_miss_naming_the_block(tmp_path: Path, capsys) -> None:
    design = _passage(tmp_path, "The new sentence.", leaf=f"Lead. {_REPLACED} Tail.\n")
    assert main([str(design)]) == 1
    out = capsys.readouterr().out
    assert "MISS" in out
    assert "The new sentence." in out
    assert "1 not applied, 0 problems, 1 becomes-blocks checked" in out


def test_a_passage_with_its_fenced_example_applied_whole_passes(tmp_path: Path) -> None:
    """A design that wants the example's own fence kept opens the passage with a longer run, which only
    that character at that length closes: the leaf holds the whole passage."""
    assert main([str(_passage(tmp_path, _WITH_EXAMPLE, fence="````"))]) == 0


def test_a_passages_fenced_example_does_not_end_the_block_checked(tmp_path: Path, capsys) -> None:
    """The example's own fence is not a closer for a longer opener, so the block checked runs past it: a
    leaf holding the passage's first line alone is a miss, not an application."""
    design = _passage(tmp_path, _WITH_EXAMPLE, leaf="The sample:\n", fence="````")
    assert main([str(design)]) == 1
    assert "1 not applied" in capsys.readouterr().out


def test_a_heading_with_no_link_is_named(tmp_path: Path, capsys) -> None:
    design = tmp_path / "design.md"
    design.write_text("## ARCHITECTURE delta\n\n### [ARCHITECTURE.md, Install, Guardrail hook]\n", encoding="utf-8")
    assert main([str(design)]) == 1
    assert "heading with no link" in capsys.readouterr().out


def test_a_becomes_with_no_following_fence_is_named(tmp_path: Path, capsys) -> None:
    leaf = tmp_path / "leaf.md"
    leaf.write_text("Lead.\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text(
        f"## ARCHITECTURE delta\n\n{_ENTRY.format(leaf=leaf)}\n\n```\n{_REPLACED}\n```\nbecomes\n",
        encoding="utf-8",
    )
    assert main([str(design)]) == 1
    assert "no following fenced block" in capsys.readouterr().out


def test_a_missing_leaf_is_named(tmp_path: Path, capsys) -> None:
    design = _passage(tmp_path, "The new sentence.")
    (tmp_path / "leaf.md").unlink()
    assert main([str(design)]) == 1
    assert "missing leaf" in capsys.readouterr().out


def test_a_missing_design_file_is_named_rather_than_raised(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "nope.md"
    assert main([str(missing)]) == 1
    assert capsys.readouterr().out == f"PROBLEM {missing}: missing design\n"
