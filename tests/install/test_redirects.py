"""redirect chain• native-file refusal• unsafe destination"""

import dataclasses
from pathlib import Path

import pytest

from devpro.errors import InputError
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.mage import HARNESS as MAGE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.render import render_agents_file
from tests.conftest import PLAIN

from .conftest import _END, _STAMPED_BEGIN, _block, _files, _install, _non_utf8, _redirect_chain, _redirect_outside


@pytest.mark.parametrize(
    "plant, directory, message",
    [
        (_non_utf8, ".", "AGENTS.md is not UTF-8 text"),
        (_redirect_chain, ".", "which is itself a redirect"),
        (_redirect_outside, "inner", "which is outside"),
    ],
)
def test_an_unsafe_destination_is_refused_with_nothing_written(
    tmp_path: Path, plant, directory: str, message: str
) -> None:
    plant(tmp_path)
    before = _files(tmp_path)
    with pytest.raises(InputError, match=message):
        _install(tmp_path / directory)
    assert _files(tmp_path) == before


def test_a_project_directory_under_claude_writes_agents_md_and_the_redirect(tmp_path: Path) -> None:
    _install(tmp_path, CLAUDE)
    assert _files(tmp_path) == {
        "AGENTS.md": render_agents_file(CLAUDE, PLAIN, scope=tmp_path.name).encode(),
        "CLAUDE.md": b"@AGENTS.md\n",
    }
    assert render_agents_file(CLAUDE, PLAIN, scope=tmp_path.name).startswith(f"# {tmp_path.name} info and directives\n")


def test_a_claude_redirect_is_followed_and_the_text_around_the_block_kept(tmp_path: Path) -> None:
    above = "# Project rules\n\nmine above\n"
    below = "\nmine below\n"
    prior = f"{above}{_STAMPED_BEGIN}\nold block\n{_END}{below}"
    (tmp_path / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text(prior, encoding="utf-8")
    _install(tmp_path, CLAUDE)
    assert _files(tmp_path) == {
        "AGENTS.md": (above + "\n".join(_block(CLAUDE)) + below).encode(),
        "CLAUDE.md": b"@AGENTS.md\n",
        "backup.AGENTS.md": prior.encode(),
    }


def test_a_claude_native_file_holding_its_own_content_is_refused(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# my own rules\n", encoding="utf-8")
    with pytest.raises(InputError, match="CLAUDE.md holds its own content"):
        _install(tmp_path, CLAUDE)
    assert _files(tmp_path) == {"CLAUDE.md": b"# my own rules\n"}


def test_a_destination_redirect_is_followed_one_hop_into_its_target(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "AGENTS.md").write_text("@docs/rules.md\n", encoding="utf-8")
    _install(tmp_path)
    assert _files(tmp_path) == {
        "AGENTS.md": b"@docs/rules.md\n",
        "docs/rules.md": render_agents_file(OPENCODE, PLAIN, scope=tmp_path.name).encode(),
    }


def test_the_user_directory_writes_the_native_file_and_no_redirect(tmp_path: Path) -> None:
    harness = dataclasses.replace(CLAUDE, user_harness_dir=str(tmp_path))
    _install(tmp_path, harness)
    assert _files(tmp_path) == {"CLAUDE.md": render_agents_file(harness, PLAIN, scope="Global").encode()}


def test_a_relative_user_directory_is_the_destination_itself(tmp_path: Path) -> None:
    """Mage's `.` names the directory being installed into — the native file, no `AGENTS.md`
    redirect — and leaves a harness whose user directory is absolute writing `AGENTS.md` elsewhere."""
    _install(tmp_path, MAGE)
    assert _files(tmp_path) == {"CLAUDE.md": render_agents_file(MAGE, PLAIN, scope="Global").encode()}
    project = tmp_path / "project"
    project.mkdir()
    _install(project, CLAUDE)
    assert _files(project) == {
        "AGENTS.md": render_agents_file(CLAUDE, PLAIN, scope=project.name).encode(),
        "CLAUDE.md": b"@AGENTS.md\n",
    }
