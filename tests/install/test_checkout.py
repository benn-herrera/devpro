"""is_checkout• uncommitted• git refusals• the wheel's tree case"""

import subprocess
from pathlib import Path

import pytest

from devpro.errors import InputError
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.install import DEVPRO_COPY, SHIPPED_PACKAGES, package_copies, uncommitted_sources
from devpro.install_base import PACKAGE_ROOT, REPO_ROOT, checkout_root
from devpro.render import render_agents_file
from tests.conftest import PLAIN

from .conftest import _install, _plant_file

_DEVPRO_ROW = next(package for package in SHIPPED_PACKAGES if package.destination == DEVPRO_COPY)


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


def _tree_side(*paths: str) -> set[str]:
    """`check-wheel`'s tree side for `paths` — the index plus untracked-but-not-ignored files — less the
    `.py` files the comparison drops, each relative to `REPO_ROOT`, the listing the wheel's package data is
    held to."""
    listed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--cached", "--others", "--exclude-standard", "--", *paths],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.splitlines()
    return {path for path in listed if not path.endswith(".py")}


def _ignored(path: Path) -> bool:
    """Whether `path` is gitignored, read from the working tree rather than the index — `--no-index` is
    what asks the ignore rules about a path the index holds too, which a stray swept in by a glob is."""
    return (
        subprocess.run(
            ["git", "-C", str(REPO_ROOT), "check-ignore", "-q", "--no-index", str(path)],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def test_the_wheel_checks_tree_side_and_a_checkout_install_agree_on_a_stray_under_the_package(
    tmp_path: Path,
) -> None:
    """`clauses.TEST_PRECONDITION`. The real-tree case `check-wheel` lacked. The defect the survey found: no
    test hands the wheel check the tree it polices, so its wheel-versus-tree comparison is exercised over
    the recipe's fixtures alone and a stray under `devpro/` reaching one side of it reaches a passing wheel
    unseen.

    The two sides are compared over this checkout's own `devpro/`, as the check compares them: the tree
    side, the index plus untracked-but-not-ignored files, and the install side, what `package_copies` stages
    from the tree as it stands. A path `.gitignore` covers is on neither side — the tree side never lists
    it, and the walk drops `__pycache__` by its own rule — so the two agree there. One the tree holds and
    the index does not ignore is untracked but counted, so the tree side lists it and the install stages it,
    and a wheel not carrying it fails the comparison: the failure that rules out a passing wheel."""
    assert REPO_ROOT is not None
    package = PACKAGE_ROOT.name
    # A text file under `__pycache__` is on neither side by two different rules: the index's ignore rule
    # and the walk's directory name, which is what makes it the shape worth planting.
    ignored_stray = _plant_file(PACKAGE_ROOT / "__pycache__" / "zz_probe.txt", "not bytecode, ignored\n")
    stray = _plant_file(PACKAGE_ROOT / "zz_probe_stray.txt", "stray\n")
    root = tmp_path / "root"
    try:
        tree_side = _tree_side(package)
        staged = {
            f"{package}/{target.relative_to(root / DEVPRO_COPY).as_posix()}"
            for _, target in package_copies(root, _DEVPRO_ROW)
        }
        assert _ignored(ignored_stray) and not _ignored(stray)
        assert f"{package}/{ignored_stray.relative_to(PACKAGE_ROOT).as_posix()}" not in tree_side | staged
        assert f"{package}/{stray.relative_to(PACKAGE_ROOT).as_posix()}" in tree_side
        assert f"{package}/{stray.relative_to(PACKAGE_ROOT).as_posix()}" in staged
    finally:
        stray.unlink()
        ignored_stray.unlink()
