"""global block• fallback• shadow"""

from pathlib import Path

import pytest

from devpro.agents_file import marker_span
from devpro.cli import main
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.render import render_agents_file
from tests.conftest import PLAIN

from .conftest import (
    _BEGIN,
    _END,
    _HARNESS_NAMED,
    _STAMPED_BEGIN,
    _UP_TO_DATE,
    _block,
    _committed,
    _dirty,
    _dry_run_groups,
    _files,
    _global_agents_file,
    _plant,
    _project_with_a_copy,
    _state,
)


@pytest.mark.parametrize("uncommitted", [False, True], ids=["committed", "uncommitted"])
@pytest.mark.parametrize("name, redirect", [("claude", True), ("opencode", False)], ids=["claude", "opencode"])
def test_without_a_global_block_a_project_install_keeps_it_in_the_projects_agents_md(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, redirect: bool, uncommitted: bool
) -> None:
    """The global file holds no block, so its text is not touched, and the commit state is not read."""
    monkeypatch.setattr("devpro.install.uncommitted_sources", _dirty if uncommitted else _committed)
    harness = _HARNESS_NAMED[name]
    _plant(_global_agents_file(tmp_path / "home", harness), "# my global rules\n")
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), f"--harness={name}"])
    rendered = render_agents_file(harness, PLAIN, scope=project.name).encode()
    gitignore = ".gitignore"
    top = {
        path: data for path, data in _files(project).items() if "/" not in path and path not in {"Makefile", gitignore}
    }
    assert top == {"AGENTS.md": rendered, **({"CLAUDE.md": b"@AGENTS.md\n"} if redirect else {})}
    assert (project / gitignore).read_text(encoding="utf-8") == ".devpro-temp/\n"
    assert _global_agents_file(tmp_path / "home", harness).read_text(encoding="utf-8") == "# my global rules\n"


def test_on_the_fallback_a_claude_redirect_is_left_and_the_block_appended(tmp_path: Path) -> None:
    project = tmp_path / "project"
    _plant(project / "CLAUDE.md", "@AGENTS.md\n")
    _plant(project / "AGENTS.md", "# mine\n")
    main(["install", str(project), "--harness=claude"])
    assert (project / "CLAUDE.md").read_text(encoding="utf-8") == "@AGENTS.md\n"
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "\n".join(["# mine", "", *_block(CLAUDE), ""])


def test_on_the_fallback_a_claude_native_file_with_its_own_content_refuses_the_install(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    _plant(project / "CLAUDE.md", "# my own rules\n")
    before = _state(project)
    with pytest.raises(SystemExit):
        main(["install", str(project), "--harness=claude"])
    assert "CLAUDE.md holds its own content" in capsys.readouterr().err
    assert _state(project) == before


@pytest.mark.usefixtures("_no_uncommitted")
@pytest.mark.parametrize("own", ["# mine\n\n", ""], ids=["own-text", "only-the-block"])
@pytest.mark.parametrize(
    "name, native",
    [("claude", "@AGENTS.md\n"), ("claude", "# my own rules\n"), ("opencode", None)],
    ids=["claude-redirect", "claude-own-content", "opencode"],
)
def test_with_a_global_block_the_install_keeps_it_there_and_removes_the_project_copy(
    tmp_path: Path, capsys, name: str, native: str | None, own: str
) -> None:
    """The project's AGENTS.md stays, emptied or not; its native file is neither read nor refused."""
    harness = _HARNESS_NAMED[name]
    global_file = _plant(_global_agents_file(tmp_path / "home", harness), f"# my global rules\n{_BEGIN}\nold\n{_END}\n")
    global_prior = global_file.read_text(encoding="utf-8")
    project = _project_with_a_copy(tmp_path, native=native, own=own)
    project_prior = (project / "AGENTS.md").read_text(encoding="utf-8")
    capsys.readouterr()
    main(["install", str(project), f"--harness={name}"])
    out = capsys.readouterr().out
    assert global_file.read_text(encoding="utf-8") == "\n".join(["# my global rules", *_block(harness), ""])
    assert (global_file.parent / f"backup.{global_file.name}").read_text(encoding="utf-8") == global_prior
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == own
    assert (project / "backup.AGENTS.md").read_text(encoding="utf-8") == project_prior
    assert f"removed the devpro block from {project / 'AGENTS.md'}" in out
    assert (None if native is None else (project / "CLAUDE.md").read_text(encoding="utf-8")) == native
    assert native is not None or not (project / "CLAUDE.md").exists()


@pytest.mark.usefixtures("_no_uncommitted")
def test_once_the_global_file_holds_the_block_every_project_install_keeps_it_there(tmp_path: Path, capsys) -> None:
    """Sticky: a project with no agents file gets none, and a second install is up to date."""
    global_file = _plant(_global_agents_file(tmp_path / "home", CLAUDE), f"{_BEGIN}\nold\n{_END}\n")
    for project in (tmp_path / "one", tmp_path / "two"):
        project.mkdir()
        main(["install", str(project), "--harness=claude"])
        assert not (project / "AGENTS.md").exists() and not (project / "CLAUDE.md").exists()
        assert global_file.read_text(encoding="utf-8") == "\n".join([*_block(CLAUDE), ""])
        capsys.readouterr()
        main(["install", str(project), "--harness=claude"])
        assert _UP_TO_DATE in capsys.readouterr().out


@pytest.mark.usefixtures("_no_uncommitted")
def test_a_legacy_kbase_stamped_global_block_is_replaced_as_a_block_of_no_plugin(tmp_path: Path) -> None:
    """A global block an earlier release stamped with the retired kbase plugin's name is a block of no
    plugin: the project install keeps the block where it is and replaces it, stamp and all, writing no
    project block. Before `_block_plugin` read the one name, it held the block as the kbase plugin's and
    left it there."""
    kbase_begin = " <!-- vvv-devpro kbase 0.0.1 do not edit at or between marker lines. devpro-vvv -->"
    global_file = _plant(_global_agents_file(tmp_path / "home", CLAUDE), f"{kbase_begin}\nold\n{_END}\n")
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=claude"])
    lines, begin, end = marker_span(render_agents_file(CLAUDE, PLAIN, scope="x"), where="render")
    assert global_file.read_text(encoding="utf-8") == "\n".join([*lines[begin : end + 1], ""])
    assert lines[begin] == _STAMPED_BEGIN
    assert not (project / "AGENTS.md").exists() and not (project / "CLAUDE.md").exists()


def test_the_global_write_under_uncommitted_sources_is_refused_with_nothing_written(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("devpro.install.uncommitted_sources", _dirty)
    _plant(_global_agents_file(tmp_path / "home", CLAUDE), f"{_BEGIN}\nold\n{_END}\n")
    project = _project_with_a_copy(tmp_path, native="@AGENTS.md\n", own="# mine\n")
    before = {"home": _state(tmp_path / "home"), "project": _state(project)}
    with pytest.raises(SystemExit):
        main(["install", str(project), "--harness=claude"])
    assert "uncommitted changes" in capsys.readouterr().err
    assert {"home": _state(tmp_path / "home"), "project": _state(project)} == before


@pytest.mark.usefixtures("_no_uncommitted")
def test_a_dry_run_names_the_global_files_whole_and_the_projects_relative(tmp_path: Path, capsys) -> None:
    global_file = _plant(_global_agents_file(tmp_path / "home", CLAUDE), f"{_BEGIN}\nold\n{_END}\n")
    project = _project_with_a_copy(tmp_path, native=None, own="# mine\n")
    argv = ["install", str(project), "--harness=claude"]
    capsys.readouterr()
    main([*argv, "--dry-run"])
    groups = _dry_run_groups(capsys.readouterr().out)
    assert {str(global_file), "AGENTS.md"} <= groups["changed"]
    assert {str(global_file.parent / "backup.CLAUDE.md"), "backup.AGENTS.md"} <= groups["created"]
    assert not (global_file.parent / "backup.CLAUDE.md").exists() and not (project / "backup.AGENTS.md").exists()
