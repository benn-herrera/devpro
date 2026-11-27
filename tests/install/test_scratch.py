"""scratch directory• gitignore"""

import shutil
import stat
from pathlib import Path

import pytest

from devpro.cli import main
from devpro.components import NAME
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.install import HARNESS_RESOURCES_SOURCE, RETIRED_SNIPPET_SET, ShippedPackage, install
from devpro.install_base import PACKAGE_ROOT, utf8_text
from devpro.runner_file import install_include_lines, prepare_scratch_directory

from .conftest import (
    _CLAUDE_RENDER,
    _GUARDRAIL,
    _OPENCODE_RENDER,
    _PROFILER,
    _PROFILER_SKILL,
    _REGISTRATION,
    _RESOURCE_HEADER,
    _TS_GUARDRAIL,
    _UP_TO_DATE,
    _claude_plugin,
    _committed,
    _definition_install,
    _files,
    _opencode_plugin,
    _plant,
)


@pytest.mark.parametrize(
    ("prior", "expected"),
    [
        (None, ".devpro-temp/\n"),
        (".venv/\n", ".venv/\n\n.devpro-temp/\n"),
        (".venv/", ".venv/\n\n.devpro-temp/\n"),
    ],
    ids=["no-gitignore", "line-added", "last-line-unterminated"],
)
def test_a_project_install_prepares_the_scratch_directory_and_its_gitignore_line(
    tmp_path: Path, prior: str | None, expected: str
) -> None:
    """Defect: the install left the project's scratch directory to whoever ran the work, so a project's
    first capture or probe made it untracked and showed up in `git status`; and a project with no
    `.gitignore` got none.

    `prior` is the `.gitignore` standing before the install, None where the project has none; `expected`
    is its text after, byte for byte."""
    project = tmp_path / "project"
    project.mkdir()
    gitignore = project / ".gitignore"
    if prior is not None:
        _plant(gitignore, prior)
    main(["install", str(project), "--harness=claude"])
    assert (project / ".devpro-temp").is_dir()
    assert utf8_text(gitignore) == expected


def test_a_user_level_install_prepares_no_scratch_directory_and_writes_no_gitignore(_home: Path) -> None:
    """A user-level install places nothing relative to a project, so it reads and writes no `.gitignore`
    and creates no scratch directory, in the home directory or anywhere below it."""
    _home.mkdir()
    install(_home / ".claude", _CLAUDE_RENDER, verbose=False, project_root=_home, uncommitted=_committed)
    assert _files(_home) and ".gitignore" not in _files(_home)
    assert sorted(path.name for path in _home.rglob(".devpro-temp")) == []


def test_a_mage_install_prepares_no_scratch_directory_and_writes_no_gitignore(tmp_path: Path) -> None:
    """A harness-directory plugin's install is no project install of a nested plugin: the runner file,
    the scratch directory and the `.gitignore` line are all outside what it touches."""
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=mage", "--subdir=plugins/devpro"])
    assert not (project / ".devpro-temp").exists()
    assert not (project / ".gitignore").exists()


def test_a_project_install_that_writes_no_runner_line_still_prepares_the_scratch_directory(
    tmp_path: Path, capsys
) -> None:
    """Defect: an install whose project already held the runner-file line found nothing to write there and
    returned before the scratch preparation, so a project whose `.devpro-temp/` was deleted printed
    `up to date` and kept the directory gone. The preparation is the install's own, and its idempotence
    is what leaves a prepared `.gitignore` as it stands."""
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), "--harness=claude"]
    main(argv)
    gitignore = project / ".gitignore"
    state = gitignore.stat().st_mtime_ns
    shutil.rmtree(project / ".devpro-temp")
    capsys.readouterr()
    main(argv)
    assert (project / ".devpro-temp").is_dir()
    assert gitignore.stat().st_mtime_ns == state
    assert _UP_TO_DATE not in capsys.readouterr().out


def test_preparing_the_scratch_directory_keeps_every_other_byte_of_the_gitignore(tmp_path: Path) -> None:
    """An operator's `.gitignore` with CRLF endings, its last line unterminated and a line a prefix
    match would take for this one (`.devpro-temp-old/`): the line added after the last with the file's own
    ending, and every other byte as it stood."""
    gitignore = tmp_path / ".gitignore"
    prior = ".venv/\r\n.devpro-temp-old/\r\nnode_modules/"
    gitignore.write_text(prior, encoding="utf-8", newline="")
    prepare_scratch_directory(tmp_path)
    assert utf8_text(gitignore) == f"{prior}\r\n\r\n.devpro-temp/\r\n"


def test_the_makefile_the_installer_created_is_removed_with_its_last_line(tmp_path: Path, capsys) -> None:
    """The cleanup removes the docdicer line and leaves the file it created holding nothing. It goes with
    its last include line, reported as removed; one the consumer added targets to is theirs and is left,
    reported as holding no include line, its own line gone."""
    docdicer_mk = "-include .opencode/plugins/devpro/skills/docdicer/tools/runner-snippets/docdicer.mk\n"
    removed = tmp_path / "removed"
    removed.mkdir()
    kept = tmp_path / "kept"
    kept.mkdir()
    for project in (removed, kept):
        # The bytes a project install leaves a project with neither runner file: the banner, then the line.
        install_include_lines(project, [RETIRED_SNIPPET_SET], harness_relpath=".opencode")
    with (kept / "Makefile").open("a", encoding="utf-8") as stream:
        stream.write("\nall:\n\t@echo hi\n")
    for project in (removed, kept):
        install_include_lines(project, [], harness_relpath=".opencode", retired_set=RETIRED_SNIPPET_SET)
    assert not (removed / "Makefile").exists()
    text = (kept / "Makefile").read_text(encoding="utf-8")
    assert docdicer_mk not in text and text.endswith("\nall:\n\t@echo hi\n")
    out, err = capsys.readouterr()
    assert f"removed {removed / 'Makefile'}: the installer created it and it holds no include line" in out
    assert f"left {kept / 'Makefile'} in place holding no include line" in err


def test_a_package_destination_is_replaced_whole_from_the_staged_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _staged
) -> None:
    """The package copy stages its tree whole, so every file the wheel carries lands — a test suite and
    a project document among them, the wheel being the one filter. The shipped rows' own sources hold
    neither shape to show it, so a row over a temporary source stands in for the table."""
    package = _staged(
        tmp_path / "devpro",
        (
            ("probe_pkg/tool.py", "print('probe')\n"),
            ("probe_pkg/tests/test_tool.py", "pass\n"),
            ("probe_pkg/SPEC.md", "# probe\n"),
        ),
    )
    monkeypatch.setattr(
        "devpro.install.SHIPPED_PACKAGES", (ShippedPackage("probe_pkg", "adj-tools/probe_pkg", "python-coder"),)
    )
    project = tmp_path / "project"
    root = project / ".claude"
    install(root, _CLAUDE_RENDER, verbose=False, project_root=project, uncommitted=_committed)
    plugin = _claude_plugin(root)
    staged = [relative.removeprefix("probe_pkg/") for relative in _files(package) if relative.startswith("probe_pkg/")]
    assert sorted(_files(plugin / "adj-tools/probe_pkg")) == sorted(staged)
    assert {"SPEC.md", "tests/test_tool.py", "tool.py"} <= set(staged)


def test_a_direct_install_into_the_user_directory_is_user_level(_home: Path) -> None:
    root = _home / ".claude"
    root.mkdir(parents=True)
    install(root, _CLAUDE_RENDER, verbose=False, project_root=_home, uncommitted=_committed)
    assert (_claude_plugin(root) / "agents").is_dir()
    assert not (_claude_plugin(root) / "hooks").exists() and not (root / "settings.json").exists()


def test_a_user_level_claude_install_renders_the_profile_skill_and_copies_no_resource(_home: Path) -> None:
    """A user-level install renders every definition, so the skill is there to say the profiler is
    absent; it copies no resource, so neither the payload nor a registration reaches `~/.claude`."""
    root = _home / ".claude"
    root.mkdir(parents=True)
    install(root, _CLAUDE_RENDER, verbose=False, project_root=_home, uncommitted=_committed)
    plugin = _claude_plugin(root)
    assert (plugin / _PROFILER_SKILL).is_file()
    assert not (plugin / _PROFILER).exists()
    assert not (plugin / _REGISTRATION).exists()


def test_a_user_level_opencode_install_copies_the_entry_and_no_guardrail(_home: Path, tmp_path: Path, _staged) -> None:
    """A user-level install delivers no guardrail, but the plugin registers only through its entry, so
    the entry is the one harness resource it copies, and it reaches across no other harness's
    resources at all: the carve-out admits a project install's copy list, not this one."""
    resources = {
        name: f"{_RESOURCE_HEADER}export const {name.replace('.ts', '')} = 1\n" for name in ("index.ts", _TS_GUARDRAIL)
    }
    _staged(
        tmp_path / "repo",
        tuple((f"{HARNESS_RESOURCES_SOURCE}/opencode/{name}", text) for name, text in resources.items()),
    )
    root = _home / ".config/opencode"
    root.mkdir(parents=True)
    install(root, _OPENCODE_RENDER, verbose=False, project_root=_home, uncommitted=_committed)
    plugin = _opencode_plugin(root)
    assert (plugin / "index.ts").read_text(encoding="utf-8") == resources["index.ts"]
    assert not (plugin / _TS_GUARDRAIL).exists()
    assert not (plugin / _PROFILER).exists()


def test_a_package_copy_lands_at_the_umasks_mode_and_a_resource_at_the_shipped_one(
    tmp_path: Path, _umask_002: None, _staged
) -> None:
    """Under umask 002 a copied package file lands group-writable — 664 from a 644 source, 775 from a
    755 one, the source's execute bits carried through the umask — where a harness resource keeps
    exactly the mode its harness ships it at. The package tree is a copy with the source modes set, so
    neither assertion rides on the modes this checkout happens to hold; the development scripts package
    is the source, its one file the executable and a planted `.gitignore` the non-stamped one."""
    package = tmp_path / "package"
    shutil.copytree(PACKAGE_ROOT / "development-tools", package / "development-tools")
    shutil.copytree(PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "claude", package / HARNESS_RESOURCES_SOURCE / "claude")
    (package / "development-tools/cold-read.sh").chmod(0o755)
    gitignore = package / "development-tools/.gitignore"
    gitignore.write_text(".venv/\n", encoding="utf-8")
    gitignore.chmod(0o644)
    resource = package / HARNESS_RESOURCES_SOURCE / "claude" / _GUARDRAIL
    resource.chmod(0o755)
    _staged(package, ())
    root = tmp_path / ".claude"
    root.mkdir()
    _definition_install(root, project_root=tmp_path)
    scripts = root / CLAUDE.bound(NAME).plugin_dir / "skills/development/scripts"
    assert stat.S_IMODE((scripts / "cold-read.sh").stat().st_mode) == 0o775
    assert stat.S_IMODE((scripts / ".gitignore").stat().st_mode) == 0o664
    assert stat.S_IMODE((_claude_plugin(root) / _GUARDRAIL).stat().st_mode) == 0o755
