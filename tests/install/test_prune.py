"""stale renders• retired names"""

from pathlib import Path

import pytest

from devpro.definition import Definition
from devpro.render import render_definition
from devpro.vocabulary import Kind
from tests._structure import kbase_skill_output_paths

from .conftest import (
    _CLAUDE_RENDER,
    _COMMENT_BANNER,
    _KBASE_CLAUDE_RENDER,
    _NEW_BANNER,
    _claude_plugin,
    _definition_install,
)


def test_a_run_prunes_a_stale_definition_of_ours_its_plugin_does_not_ship(tmp_path: Path, capsys) -> None:
    root = tmp_path / ".claude"
    plugin = _claude_plugin(root)
    (plugin / "agents").mkdir(parents=True)
    (plugin / "agents/kb-maintainer.md").write_text(_NEW_BANNER, encoding="utf-8")
    capsys.readouterr()
    _definition_install(root, project_root=tmp_path)
    assert not (plugin / "agents/kb-maintainer.md").exists()
    assert f"pruned {plugin / 'agents/kb-maintainer.md'}" in capsys.readouterr().out


def test_a_kbase_install_prunes_a_stale_reference_and_keeps_a_user_file(tmp_path: Path, capsys) -> None:
    """A supporting file is ours by its own first line, so prune needs no rule keyed on the skill."""
    root = tmp_path / ".claude"
    plugin = _claude_plugin(root)
    references = plugin / "skills/kbase/references"
    references.mkdir(parents=True)
    stale = references / "gone.md"
    stale.write_text(f"{_COMMENT_BANNER}\n\nold text\n", encoding="utf-8")
    mine = plugin / "skills/kbase/notes.md"
    mine.write_text("---\nmine\n---\n", encoding="utf-8")
    capsys.readouterr()
    _definition_install(root, _KBASE_CLAUDE_RENDER, project_root=tmp_path)
    assert not stale.exists()
    assert mine.read_text(encoding="utf-8") == "---\nmine\n---\n"
    assert all((plugin / relative).is_file() for relative in kbase_skill_output_paths())
    assert f"pruned {stale}" in capsys.readouterr().out


def test_prune_recognizes_the_banner_the_renderer_writes(tmp_path: Path, capsys) -> None:
    """The recognizer reads what `render_definition` emits, not a prefix typed into the test."""
    root = tmp_path / ".claude"
    (_claude_plugin(root) / "commands").mkdir(parents=True)
    stale = _claude_plugin(root) / "commands/stale.md"
    stale.write_text(
        render_definition(
            Definition(name="stale", kind=Kind.COMMAND, body="body"),
            _CLAUDE_RENDER,
            module="devpro.definitions.probe",
        ),
        encoding="utf-8",
    )
    capsys.readouterr()
    _definition_install(root, project_root=tmp_path)
    assert not stale.exists()
    assert f"pruned {stale}" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("beside", "kept", "removed"),
    [
        ("agents/sub/mine.md", ["agents/sub", "agents/sub/mine.md"], ["agents/sub/gone.md"]),
        ("agents/empty/", ["agents/empty", "."], ["agents/sub"]),
    ],
    ids=["beside-a-user-file", "beside-an-empty-directory"],
)
def test_the_prune_removes_only_the_directories_it_empties(
    tmp_path: Path, beside: str, kept: list[str], removed: list[str]
) -> None:
    """The upward walk stops at a directory still holding something; one that was already empty, and the
    install directory, stay."""
    root = tmp_path / ".claude"
    plugin = _claude_plugin(root)
    (plugin / "agents/sub").mkdir(parents=True)
    (plugin / "agents/sub/gone.md").write_text(_NEW_BANNER, encoding="utf-8")
    if beside.endswith("/"):
        (plugin / beside).mkdir()
    else:
        (plugin / beside).write_text("mine\n", encoding="utf-8")
    _definition_install(root, project_root=tmp_path)
    assert all((plugin / path).exists() for path in kept)
    assert not any((plugin / path).exists() for path in removed)


def test_a_banner_naming_a_foreign_module_is_not_ours(tmp_path: Path) -> None:
    """The payload has to name a module path this repository writes; the bare mark is not enough."""
    root = tmp_path / ".claude"
    (_claude_plugin(root) / "skills/probe/references").mkdir(parents=True)
    mine = _claude_plugin(root) / "skills/probe/references/mine.md"
    text = "<!-- !GENERATED! from someone/else.md — x -->\n<!-- !TUNING! y -->\n\nbody\n"
    mine.write_text(text, encoding="utf-8")
    _definition_install(root, project_root=tmp_path)
    assert mine.read_text(encoding="utf-8") == text
