"""is_checkout• uncommitted• git refusals"""

from pathlib import Path

import pytest

from devpro.errors import InputError
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.install import uncommitted_sources
from devpro.install_base import PACKAGE_ROOT, REPO_ROOT, checkout_root
from devpro.render import render_agents_file
from tests.conftest import PLAIN

from .conftest import _install


def test_uncommitted_sources_refuse_no_install_into_a_project_directory(tmp_path: Path) -> None:
    _install(tmp_path, uncommitted=("?? devpro/x.py",))
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == render_agents_file(
        OPENCODE, PLAIN, scope=tmp_path.name
    )


@pytest.mark.parametrize("git_entry", ["directory", "file", None])
def test_a_checkout_is_a_package_parent_holding_a_git_entry(tmp_path: Path, git_entry: str | None) -> None:
    package = tmp_path / "devpro"
    package.mkdir()
    if git_entry == "directory":
        (tmp_path / ".git").mkdir()
    elif git_entry == "file":
        (tmp_path / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
    assert checkout_root(package) == (None if git_entry is None else tmp_path)


def test_this_checkout_is_one_and_its_commit_state_reads() -> None:
    assert REPO_ROOT == PACKAGE_ROOT.parent
    uncommitted_sources()


def test_outside_a_checkout_nothing_is_uncommitted_and_git_is_not_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("devpro.install_base.REPO_ROOT", None)
    monkeypatch.setenv("PATH", str(tmp_path))
    assert uncommitted_sources() == ()


def test_a_checkout_git_cannot_read_still_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".git").write_text("", encoding="utf-8")
    monkeypatch.setattr("devpro.install_base.REPO_ROOT", tmp_path)
    with pytest.raises(InputError, match="cannot read the commit state"):
        uncommitted_sources()
