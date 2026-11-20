"""`check_deltas` over designs written for the case — an undiced document and a diced tree: both
verdicts, each failure the tool names, and the fence rule that keeps a passage's own fenced example
from ending the block it belongs to."""

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


def test_a_passage_whose_from_text_survives_is_a_miss_naming_the_leaf(tmp_path: Path, capsys) -> None:
    """A leaf holding both blocks reads as applied while the replacement never happened: the deletion
    block whose becomes-text pre-existed passed before the from-side check existed."""
    design = _passage(tmp_path, "The new sentence.", leaf=f"Lead. {_REPLACED} The new sentence. Tail.\n")
    assert main([str(design)]) == 1
    out = capsys.readouterr().out
    assert "MISS" in out and "still holds the from-text" in out
    assert "1 not applied, 0 problems, 1 becomes-blocks checked" in out


def test_an_addition_whose_becomes_contains_its_from_text_passes(tmp_path: Path) -> None:
    """An entry that appends keeps its anchor sentence: the from-text inside the becomes-text is the
    applied state, not a survival."""
    applied = f"{_REPLACED}\n\nA second sentence."
    assert main([str(_passage(tmp_path, applied, leaf=f"Lead. {applied} Tail.\n"))]) == 0


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


_TARGET = "PROJECT_DOCS/ARCHITECTURE/agents-file.md"
# A tree's links are leaf-relative: from a section directory the target sits two levels up.
_TREE_LINK = f"../../{_TARGET}"


def _tree(tmp_path: Path, *, stem: str = "design", applied: str = "The new sentence.", leaf: str | None = None) -> Path:
    """A diced design at `tmp_path/stem/`, its one code-delta leaf linking `_TARGET`, and that target
    beside the tree holding `leaf` or the applied text between a lead and a tail. Returns the design
    path to check — the monolith's, retired."""
    tree = tmp_path / stem
    entry = tree / "code-delta" / "entry.md"
    entry.parent.mkdir(parents=True, exist_ok=True)
    (tree / "entry-point.md").write_text("# design\n", encoding="utf-8")
    target = tmp_path / _TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(leaf if leaf is not None else f"Lead. {applied} Tail.\n", encoding="utf-8")
    entry.write_text(
        f"{_ENTRY.format(leaf=_TREE_LINK)}\n\n```\n{_REPLACED}\n```\nbecomes\n```\n{applied}\n```\n",
        encoding="utf-8",
    )
    return tmp_path / f"{stem}.md"


def test_a_trees_entries_are_read_from_its_leaves(tmp_path: Path, capsys) -> None:
    """Tree mode reads each section leaf as one entry: a reader that opens the named path as a
    document finds no monolith beside the tree, reports `missing design`, and so never passes an
    applied pair or names a miss."""
    assert main([str(_tree(tmp_path / "applied"))]) == 0
    assert "all 1 becomes-blocks occur byte-exact in their leaves" in capsys.readouterr().out
    assert main([str(_tree(tmp_path / "missed", leaf=f"Lead. {_REPLACED} Tail.\n"))]) == 1
    out = capsys.readouterr().out
    assert "MISS" in out
    assert "1 not applied, 0 problems, 1 becomes-blocks checked" in out


def test_a_trees_link_resolves_from_the_leafs_own_directory(tmp_path: Path, capsys, monkeypatch) -> None:
    """A tree's links are leaf-relative where a document's are repository-relative: resolved from the
    invocation directory, the entry names a leaf that is not there."""
    design = _tree(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert main([str(design)]) == 0
    assert "all 1 becomes-blocks occur byte-exact in their leaves" in capsys.readouterr().out


def test_index_and_entry_point_are_not_entries(tmp_path: Path, capsys) -> None:
    """Only a section directory's leaves are entries: an `index.md` and the tree's `entry-point.md`
    carrying entry-shaped text would otherwise each report a missing leaf and count a block."""
    design = _tree(tmp_path)
    tree = design.with_suffix("")
    decoy = "### [ARCHITECTURE.md, Decoy](nowhere.md)\n\n```\nx\n```\nbecomes\n```\ny\n```\n"
    (tree / "code-delta" / "index.md").write_text(decoy, encoding="utf-8")
    (tree / "entry-point.md").write_text(decoy, encoding="utf-8")
    assert main([str(design)]) == 0
    assert "all 1 becomes-blocks occur byte-exact in their leaves" in capsys.readouterr().out


def test_a_tree_leaf_yielding_no_entry_is_a_problem_naming_the_leaf(tmp_path: Path, capsys) -> None:
    """A section leaf holding no `###` entry was dropped silently, so a leaf the parser could not read
    passed as `all 0 becomes-blocks`. One PROBLEM names the leaf."""
    design = _tree(tmp_path)
    (design.with_suffix("") / "code-delta" / "entryless.md").write_text("A paragraph, no entry.\n", encoding="utf-8")
    assert main([str(design)]) == 1
    out = capsys.readouterr().out
    assert "PROBLEM" in out and "entryless.md: no entry" in out


def test_a_documents_links_resolve_from_the_link_base_given(tmp_path: Path, capsys, monkeypatch) -> None:
    """Document-mode links resolve from the repository root, not the invocation directory: a call from
    a subdirectory passes the root as the second argument, where the cwd base named a phantom leaf."""
    (tmp_path / "leaf.md").write_text("Lead. The new sentence. Tail.\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text(
        "## ARCHITECTURE delta\n\n"
        "### [ARCHITECTURE.md, Install, Guardrail hook](leaf.md)\n\n"
        f"```\n{_REPLACED}\n```\nbecomes\n```\nThe new sentence.\n```\n",
        encoding="utf-8",
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert main([str(design), str(tmp_path)]) == 0
    assert "all 1 becomes-blocks occur byte-exact in their leaves" in capsys.readouterr().out


def test_the_tree_beside_the_named_design_path_is_the_source(tmp_path: Path, capsys, monkeypatch) -> None:
    """The default invocation resolves `ACTIVE_DESIGN.md` beside `ACTIVE_DESIGN/`: with the monolith
    retired, a reader that opens the named path reports `missing design`."""
    monkeypatch.chdir(tmp_path)
    _tree(tmp_path, stem="ACTIVE_DESIGN")
    assert main([]) == 0
    assert "all 1 becomes-blocks occur byte-exact in their leaves" in capsys.readouterr().out
