"""dry-run predictions"""

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

import pytest

from devpro import __version__
from devpro.cli import main
from devpro.harness import Harness
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.install import (
    HARNESS_RESOURCES_SOURCE,
    SHIPPED_PACKAGES,
    harness_resource_copies,
    install,
)
from devpro.install_base import PACKAGE_ROOT
from devpro.loading import load

from .conftest import (
    _BEGIN,
    _CLAUDE_PLUGIN_RELPATH,
    _CLAUDE_RENDER,
    _COLD_READ_SOURCE,
    _END,
    _GUARDRAIL,
    _GUARDRAIL_MATCHER,
    _KBASE_CLAUDE_RENDER,
    _MAGE_RENDER,
    _NEW_BANNER,
    _NO_DEVPRO_PATH,
    _OPENCODE_RENDER,
    _PROFILER,
    _PROFILER_SKILL,
    _REGISTRATION,
    _REMINDER,
    _RESOURCE_HEADER,
    _SETTINGS,
    _TS_GUARDRAIL,
    _UP_TO_DATE,
    _agents_file_in_a_project,
    _assert_dry_run_predicts,
    _block,
    _changed_since,
    _claude_plugin,
    _claude_root,
    _committed,
    _definition_install,
    _directories,
    _dry_run_groups,
    _files,
    _guardrail_result,
    _installed_cold_reads,
    _kb_install_with_a_runner_file,
    _mage_below_its_project,
    _opencode_plugin,
    _plant,
    _rendered,
    _run_outcome,
    _run_registered_hook,
    _run_wrapper,
    _state,
    _user_level_plugin,
)


@pytest.mark.parametrize(
    "harness_args",
    [["--harness=claude"], ["--harness=opencode"], ["--harness=mage", "--subdir=plugins/devpro"]],
    ids=["claude", "opencode", "mage"],
)
def test_a_project_install_ships_the_cold_read_script_stamped_and_executable(
    tmp_path: Path, harness_args: list[str]
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), *harness_args])
    (script,) = _installed_cold_reads(project)
    lines = script.read_text(encoding="utf-8").split("\n")
    source_lines = _COLD_READ_SOURCE.read_text(encoding="utf-8").split("\n")
    assert lines[0] == source_lines[0] and lines[0].startswith("#!")
    assert lines[1].startswith("# !INSTALLED! from devpro/development-tools/cold-read.sh")
    assert lines[2:] == source_lines[1:]
    assert os.access(script, os.X_OK)


def test_a_user_level_install_ships_no_cold_read_script(_home: Path) -> None:
    root = _home / ".claude"
    install(root, _CLAUDE_RENDER, verbose=False, project_root=_home, uncommitted=_committed)
    assert _installed_cold_reads(_home) == []


def test_a_project_install_writes_the_devpro_copy_and_a_wrapper_that_runs_it(tmp_path: Path) -> None:
    """The copy is the package content the run stages from, byte for byte, and the wrapper runs it with
    no devpro on PATH, under an interpreter outside any virtual environment. Defect: before the devpro
    tools package no copy was installed, so an installed tree could not run devpro once the system's was
    removed."""
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=claude"])
    tools = _claude_plugin(project / ".claude") / "tools"
    expected = {
        relative: data for relative, data in _files(PACKAGE_ROOT).items() if "__pycache__" not in Path(relative).parts
    }
    assert _files(tools / "devpro") == expected
    wrapper = tools / "devpro.sh"
    recorded = re.search(r"^recorded=(.*)$", wrapper.read_text(encoding="utf-8"), re.MULTILINE)
    assert recorded is not None
    in_a_venv = sys.prefix != sys.base_prefix
    assert not (in_a_venv and Path(shlex.split(recorded.group(1))[0]).is_relative_to(sys.prefix))
    ran = _run_wrapper(wrapper, path=_NO_DEVPRO_PATH, home=tmp_path)
    assert (ran.returncode, ran.stdout) == (0, f"{__version__}\n"), ran.stderr


def test_a_wrapper_run_from_a_directory_holding_a_devpro_package_runs_the_copy(tmp_path: Path) -> None:
    """Defect: `python -m devpro` put the working directory ahead of the copy on `sys.path`, so a `devpro`
    package there — this repository's root among them — ran in the copy's place."""
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=claude"])
    impostor = tmp_path / "impostor"
    _plant(impostor / "devpro/__init__.py", "")
    _plant(impostor / "devpro/__main__.py", "print('impostor')\n")
    ran = _run_wrapper(_claude_plugin(project / ".claude") / "tools/devpro.sh", path=_NO_DEVPRO_PATH, home=impostor)
    assert (ran.returncode, ran.stdout) == (0, f"{__version__}\n"), ran.stderr


def test_an_install_run_from_an_installations_copy_into_that_installation_reenters(
    tmp_path: Path, _staged, capsys
) -> None:
    """An install run from an installation's own copy into the installation holding that copy passes over
    the copy and the wrapper — writing nothing at either and reporting nothing about the pass-over — and
    installs everything else, the added kbase component among them. The copy is the running package by
    `_staged`'s `PACKAGE_ROOT` rebinding — its row populated, so the kept-file branch of the replacement
    is the one that runs, with a stale `.pyc` beside the row file the row does not ship. Defect
    (TEST_PRECONDITION): such a run refuses, rewrites the copy's row file or drops it, keeps the stale
    `.pyc`, or passes over a path other than the two named."""
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=claude"])
    plugin = _claude_plugin(project / ".claude")
    copy = plugin / "tools/devpro"
    wrapper = plugin / "tools/devpro.sh"
    _staged(copy, (("tool.py", "probe\n"),))
    shipped_file = copy / "tool.py"
    expected = _files(copy)
    stale = _plant(copy / "tool.cpython-311.pyc", "bytecode\n")
    wrapper_before = wrapper.read_bytes()
    plugin_before = _files(plugin)
    foreign = _plant(plugin / "tools/runner-snippets/foreign.just", "foreign\n")
    capsys.readouterr()
    # Exit 0: a re-entry run returns from `main` rather than raising SystemExit, as the refused run once did.
    main(["install", str(project), "--harness=claude", "--components=kbase"])
    captured = capsys.readouterr()
    assert "tools/devpro" not in captured.out
    assert "tools/devpro" not in captured.err
    assert shipped_file.read_bytes() == b"probe\n"
    assert not stale.exists()
    assert _files(copy) == expected
    assert wrapper.read_bytes() == wrapper_before
    added = set(_files(plugin)) - set(plugin_before)
    assert any(relative.startswith("skills/kbase/") for relative in added)
    assert not foreign.exists()


def test_a_symlinked_copy_destination_is_refused(tmp_path: Path, capsys) -> None:
    """`is_the_running_copy` and the replacement's pass-over both read the copy destination resolved, so
    a link planted there sends the pass-over and the copy through the link into whatever it names. The
    install refuses, naming the link, and leaves the link's target untouched. Defect
    (TEST_PRECONDITION): such a run clears and writes through the link, or refuses without naming the path."""
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=claude"])
    copy = _claude_plugin(project / ".claude") / "tools/devpro"
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    sensitive = foreign / "keep.txt"
    sensitive.write_text("do not delete\n", encoding="utf-8")
    shutil.rmtree(copy)
    copy.symlink_to(foreign, target_is_directory=True)
    capsys.readouterr()
    with pytest.raises(SystemExit) as exit_info:
        main(["install", str(project), "--harness=claude"])
    assert exit_info.value.code == 2
    assert f"'{copy}'" in capsys.readouterr().err
    assert sensitive.read_text(encoding="utf-8") == "do not delete\n"


def test_a_user_level_reentry_reports_up_to_date_and_passes_over_its_wrapper(
    _home: Path, tmp_path: Path, _staged, capsys
) -> None:
    """A re-entry run from a user-level installation's own copy into that installation passes over the
    copy and the wrapper that runs it. Nothing else changes, so the preflight reports the user harness
    directory up to date — the user-level report's own shape, its `is user-level` line on stderr with it
    — and the wrapper a non-re-entry run would rewrite is left as it stands. Defect (TEST_PRECONDITION):
    such a run refuses, reports the pass-over, or rewrites the copy or wrapper it runs from instead of
    passing over them and reporting up to date."""
    root = _home / ".claude"
    root.mkdir(parents=True)
    main(["install", str(root), "--harness=claude"])
    plugin = _claude_plugin(root)
    copy = plugin / "tools/devpro"
    _staged(copy, ())
    wrapper = plugin / "tools/devpro.sh"
    # A non-shipped byte a non-re-entry run would overwrite by rewriting the wrapper; a re-entry run
    # passes over it, and the replacement removes nothing around it.
    wrapper.write_bytes(wrapper.read_bytes() + b"\n# re-entry left this\n")
    wrapper_before = wrapper.read_bytes()
    plugin_before = _files(plugin)
    capsys.readouterr()
    main(["install", str(root), "--harness=claude"])
    captured = capsys.readouterr()
    up_to_date = [line for line in captured.out.splitlines() if line.startswith(_UP_TO_DATE)]
    assert up_to_date and str(root) in up_to_date[0]
    assert "is user-level" in captured.err
    assert "tools/devpro" not in captured.out
    assert "tools/devpro" not in captured.err
    assert _files(plugin) == plugin_before
    assert wrapper.read_bytes() == wrapper_before


def test_a_reinstall_over_an_older_copy_reports_the_version_it_replaces(tmp_path: Path, capsys) -> None:
    """The install replaces the copy whichever of the two versions is the newer, and its report names the
    version it replaces and the version it installs. Defect: an older copy is replaced without the
    version it held being named, so the operator reads a run that changed what it ran as no change."""
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), "--harness=claude"]
    main(argv)
    init = _claude_plugin(project / ".claude") / "tools/devpro/__init__.py"
    init.write_text(
        init.read_text(encoding="utf-8").replace(f'__version__ = "{__version__}"', '__version__ = "0.0.1"'),
        encoding="utf-8",
    )
    capsys.readouterr()
    main(argv)
    replaced = [line for line in capsys.readouterr().out.splitlines() if __version__ in line]
    assert replaced == [f"devpro 0.0.1 replaced by devpro {__version__} → {init.parent}"]


def test_a_reinstall_over_a_newer_copy_reports_the_version_it_replaces_and_the_one_it_installs(
    tmp_path: Path, capsys
) -> None:
    """The direction the first case cannot show: a copy holding a version newer than this release is
    replaced too — the install writes its own regardless of which is newer — and the report names the
    newer version being replaced by this one. Defect: a run over a newer copy reports the install of this
    version without naming the version it holds, reads the newer copy as up to date, or names the two the
    other way round."""
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), "--harness=claude"]
    main(argv)
    init = _claude_plugin(project / ".claude") / "tools/devpro/__init__.py"
    newer = f"{int(__version__.split('.')[0]) + 1}.0.0"
    init.write_text(
        init.read_text(encoding="utf-8").replace(f'__version__ = "{__version__}"', f'__version__ = "{newer}"'),
        encoding="utf-8",
    )
    capsys.readouterr()
    main(argv)
    out = capsys.readouterr().out
    assert [line for line in out.splitlines() if newer in line] == [
        f"devpro {newer} replaced by devpro {__version__} → {init.parent}"
    ]
    assert _UP_TO_DATE not in out
    assert f'__version__ = "{__version__}"' in init.read_text(encoding="utf-8")


def test_a_user_level_install_writes_the_devpro_tools_package_and_no_other(_home: Path) -> None:
    """Defect: before the devpro tools package a user-level install wrote no package."""
    root = _home / ".claude"
    install(root, _KBASE_CLAUDE_RENDER, verbose=False, project_root=_home, uncommitted=_committed)
    plugin = _claude_plugin(root)
    for package in SHIPPED_PACKAGES:
        assert (plugin / package.destination).is_dir() is (package.owner is None), package.destination
    assert os.access(plugin / "tools/devpro.sh", os.X_OK)


def test_a_foreign_file_inside_the_install_directory_is_removed_and_named_in_the_dry_run(
    tmp_path: Path, capsys
) -> None:
    """Nothing inside the install directory is read to decide its fate: a file the consumer left there —
    hand-written, carrying no banner — goes with the tree, and the dry run names it in its removed
    group before the run that removes it. Defect: a file that is not ours survives a changing install,
    or the dry run omits its removal while the run makes it."""
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), "--harness=claude"]
    main(argv)
    plugin = _claude_plugin(project / ".claude")
    foreign = _plant(plugin / "agents/mine.md", "---\nname: mine\n---\n")
    my_directory = _plant(plugin / "notes/keep.txt", "mine\n").parent
    groups = _assert_dry_run_predicts(argv, project=project, capsys=capsys)
    assert not foreign.exists() and not my_directory.exists()
    removed = {foreign.relative_to(project).as_posix(), f"{my_directory.relative_to(project).as_posix()}/"}
    assert removed <= groups["removed"]


def test_a_symlink_inside_the_install_directory_is_removed_not_followed(tmp_path: Path, capsys) -> None:
    """A link inside the install directory is unlinked as the link it is: whatever it names, outside the
    install directory, keeps every file. Defect: the wipe follows the link out of the install
    directory, removing what it names."""
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), "--harness=claude"]
    main(argv)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    keep = _plant(elsewhere / "keep.txt", "keep\n")
    link = _claude_plugin(project / ".claude") / "linked"
    link.symlink_to(elsewhere)
    groups = _assert_dry_run_predicts(argv, project=project, capsys=capsys)
    assert keep.read_text(encoding="utf-8") == "keep\n"
    assert not link.exists()
    assert f"{link.relative_to(project).as_posix()}/" in groups["removed"]


def test_a_stale_pyc_under_the_re_entry_copy_is_absent_and_the_copy_byte_identical(
    tmp_path: Path, _staged, capsys
) -> None:
    """A re-entry run passes over the copy's own files by path and removes everything else inside the
    copy's tree, a stale bytecode file included, and rewrites none of the copy it runs from. Defect:
    the pass-over preserves junk, or the replacement rewrites the copy the run executes from."""
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=claude"])
    copy = _claude_plugin(project / ".claude") / "tools/devpro"
    _staged(copy, ())
    copy_before = _files(copy)
    stale = _plant(copy / "tool.cpython-311.pyc", "bytecode\n")
    capsys.readouterr()
    main(["install", str(project), "--harness=claude"])
    assert not stale.exists()
    assert _files(copy) == copy_before


def test_the_cold_read_script_installed_under_mage_refuses(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=mage", "--subdir=plugins/devpro"])
    (script,) = _installed_cold_reads(project)
    brief = tmp_path / "brief.md"
    brief.write_text("brief\n", encoding="utf-8")
    result = subprocess.run(
        [str(script), "devpro:ghost", str(brief)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        stdin=subprocess.DEVNULL,
        timeout=30,
    )
    assert result.returncode == 1
    assert "claude and opencode only" in result.stderr


def test_a_reinstall_overwrites_its_own_renders_kb_skill_files_included(tmp_path: Path) -> None:
    """A local edit that keeps the banner is still ours: the frontmatter carrier and a supporting
    file's comment carrier each pass, and the render replaces the edit."""
    root = tmp_path / ".claude"
    root.mkdir()
    _definition_install(root, _KBASE_CLAUDE_RENDER, project_root=tmp_path)
    plugin = _claude_plugin(root)
    edited = ("agents/python-coder.md", "skills/kbase/references/reading.md")
    for relative in edited:
        with (plugin / relative).open("a", encoding="utf-8") as handle:
            handle.write("a local edit\n")
    _definition_install(root, _KBASE_CLAUDE_RENDER, project_root=tmp_path)
    for relative in edited:
        assert (plugin / relative).read_text(encoding="utf-8") == _rendered(_KBASE_CLAUDE_RENDER, relative)


@pytest.mark.parametrize(
    "head",
    ["", "// filler\n" * 9 + _RESOURCE_HEADER, "// filler\n" * 10 + _RESOURCE_HEADER],
    ids=["no-header", "header-on-line-10", "header-on-line-11"],
)
def test_a_resource_destination_is_replaced_whatever_stands_there(tmp_path: Path, head: str) -> None:
    """The replacement reads no header at a destination: a file standing at a harness resource's path is
    overwritten with the resource as this release ships it, wherever a banner would have sat. Defect: a
    header gate refusing the install over a file without it."""
    root = tmp_path / ".opencode"
    guardrail = _opencode_plugin(root) / _TS_GUARDRAIL
    guardrail.parent.mkdir(parents=True)
    guardrail.write_text(f"{head}export const mine = 1\n", encoding="utf-8")
    source = (PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "opencode" / _TS_GUARDRAIL).read_bytes()
    _definition_install(root, _OPENCODE_RENDER, project_root=tmp_path)
    assert guardrail.read_bytes() == source


def test_a_prior_installs_resource_is_overwritten(tmp_path: Path) -> None:
    root = tmp_path / ".opencode"
    root.mkdir()
    _definition_install(root, _OPENCODE_RENDER, project_root=tmp_path)
    guardrail = _opencode_plugin(root) / _TS_GUARDRAIL
    with guardrail.open("a", encoding="utf-8") as handle:
        handle.write("// a local edit\n")
    _definition_install(root, _OPENCODE_RENDER, project_root=tmp_path)
    assert guardrail.read_bytes() == (PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "opencode" / _TS_GUARDRAIL).read_bytes()


def test_every_shipped_resource_carries_its_installed_banner_as_shipped(tmp_path: Path) -> None:
    """The banner a reader finds in an installed tree names the file it came from and where a local need
    goes. The install copies the file as it stands — it stamps nothing on a resource — so the banner is
    shipped text the source test holds for every file a harness ships, required by nothing an install
    reads back."""
    harnesses = load("devpro.harnesses", "HARNESS")
    sources = [source for name in harnesses for source, _ in harness_resource_copies(tmp_path, harness=name)]
    assert sources
    for source in sources:
        origin = f"{PACKAGE_ROOT.name}/{source.relative_to(PACKAGE_ROOT).as_posix()}"
        head = source.read_text(encoding="utf-8").splitlines()[:10]
        banner = next((line for line in head if "!INSTALLED!" in line), "")
        assert f"!INSTALLED! from {origin} — " in banner, source
        assert "request changes from the devpro project" in banner, source
        assert "local needs belong in your CONVENTIONS.md" in banner, source


@pytest.mark.parametrize(
    "interpreter, reason",
    [("devpro-no-such-perl", "'devpro-no-such-perl' could not be run: "), ("false", "'false ")],
    ids=["missing-interpreter", "failing-run"],
)
def test_a_failed_probe_installs_everything_else_and_neither_ships_nor_registers_the_hook(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch, interpreter: str, reason: str
) -> None:
    monkeypatch.setattr("devpro.install.GUARDRAIL_INTERPRETER", interpreter)
    root = _claude_root(tmp_path)
    capsys.readouterr()
    _definition_install(root, project_root=tmp_path)
    assert (_claude_plugin(root) / "agents/python-coder.md").is_file()
    assert not (_claude_plugin(root) / _GUARDRAIL).exists()
    assert (_claude_plugin(root) / _REMINDER).is_file()
    hooks = json.loads((_claude_plugin(root) / _REGISTRATION).read_text(encoding="utf-8"))["hooks"]
    assert "PreToolUse" not in hooks
    assert "Agent" in [entry["matcher"] for entry in hooks["PostToolUse"]]
    assert not (tmp_path / _SETTINGS).exists()
    [skipped] = [line for line in capsys.readouterr().err.splitlines() if line.startswith("guardrail hook skipped")]
    assert reason in skipped and "left in place" not in skipped


def test_a_probe_that_fails_and_then_passes_registers_the_guardrail_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The registration a failed probe writes holds the reminder entry alone, and a later install has
    to read it as this repository's own before it may replace it: the marker it states is the phrase
    both commands' reports carry, so a marker only the guardrail's entry carries would refuse."""
    root = _claude_root(tmp_path)
    _definition_install(root, project_root=tmp_path)
    monkeypatch.setattr("devpro.install.GUARDRAIL_INTERPRETER", "devpro-no-such-perl")
    _definition_install(root, project_root=tmp_path)
    monkeypatch.undo()
    _definition_install(root, project_root=tmp_path)
    hooks = json.loads((_claude_plugin(root) / _REGISTRATION).read_text(encoding="utf-8"))["hooks"]
    assert [entry["matcher"] for entry in hooks["PreToolUse"]] == [_GUARDRAIL_MATCHER]
    assert "Agent" in [entry["matcher"] for entry in hooks["PostToolUse"]]


def test_an_opencode_install_writes_no_claude_settings_file(tmp_path: Path) -> None:
    root = tmp_path / ".opencode"
    root.mkdir()
    _definition_install(root, _OPENCODE_RENDER, project_root=tmp_path)
    assert not (tmp_path / ".claude").exists()
    assert not (root / _GUARDRAIL).exists()


def test_an_opencode_install_copies_no_profiler_payload(tmp_path: Path) -> None:
    """The profiler's hooks are claude's, and opencode's capture is its plugin's own, so opencode's copy
    list carries no profiler resource: its project install holds no `profiler/` and registers nothing,
    and mage's holds no `profiler/` either. Defect: `_CROSS_HARNESS_SOURCES` carried claude's launcher
    directory across, so an opencode install delivered a bash launcher beside a TypeScript capture. Both
    carry the profiler skill."""
    opencode = tmp_path / "opencode"
    (opencode / ".opencode").mkdir(parents=True)
    _definition_install(opencode / ".opencode", _OPENCODE_RENDER, project_root=opencode)
    opencode_plugin = _opencode_plugin(opencode / ".opencode")
    mage = tmp_path / "mage"
    (mage / "plugins/devpro").mkdir(parents=True)
    _definition_install(mage / "plugins/devpro", _MAGE_RENDER, project_root=mage)
    mage_plugin = mage / "plugins/devpro"
    for plugin in (opencode_plugin, mage_plugin):
        assert not (plugin / _PROFILER).exists()
        assert not (plugin / _REGISTRATION).exists()
        assert (plugin / _PROFILER_SKILL).is_file()


@pytest.mark.parametrize("subdir", ["tools/agents", ".", 'a"b $c'], ids=["subdir", "project-root", "shell-syntax"])
def test_the_registered_command_runs_the_script_the_install_wrote(tmp_path: Path, subdir: str) -> None:
    """The command the plugin registers, run as Claude Code runs it, reaches the script under ROOT
    wherever ROOT sits, a directory name a shell reads as syntax included: it blocks an in-place edit and
    allows a plain command."""
    root = tmp_path / subdir
    root.mkdir(parents=True, exist_ok=True)
    _definition_install(root, project_root=tmp_path)
    assert (_claude_plugin(root) / _GUARDRAIL).is_file()
    assert _guardrail_result(_claude_plugin(root), project=tmp_path, command="sed -i x f").returncode == 2
    assert _guardrail_result(_claude_plugin(root), project=tmp_path, command="echo hi").returncode == 0


def test_a_missing_script_does_not_block_and_names_the_path(tmp_path: Path) -> None:
    """Perl exits 2 on a script it cannot open, which Claude Code reads as a block, so a plugin left
    without its script would block every call the matcher names. The registered command instead exits 1
    and names the missing script."""
    root = _claude_root(tmp_path)
    _definition_install(root, project_root=tmp_path)
    script = _claude_plugin(root) / _GUARDRAIL
    script.unlink()
    result = _guardrail_result(_claude_plugin(root), project=tmp_path, command="sed -i x f")
    assert result.returncode == 1
    assert result.stderr.count("\n") == 1 and str(script) in result.stderr


def test_the_registered_reminder_runs_the_script_the_install_wrote(tmp_path: Path) -> None:
    """The reminder entry's command, run as Claude Code runs it, reaches the installed script and
    answers with the reminder JSON: a wrong script path or interpreter there would leave every install
    answering `no readable script at …` on stderr, and the suite green."""
    root = _claude_root(tmp_path)
    _definition_install(root, project_root=tmp_path)
    (tmp_path / "ACTIVE_PLAN.md").write_text("# under way\n", encoding="utf-8")
    result = _run_registered_hook(
        _claude_plugin(root),
        project=tmp_path,
        event="PostToolUse",
        matcher="Agent",
        payload={"hook_event_name": "PostToolUse", "tool_name": "Agent", "cwd": str(tmp_path)},
    )
    assert (result.returncode, result.stderr) == (0, "")
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PostToolUse"
    assert "state table" in output["additionalContext"]


def test_a_failed_probe_names_no_script_an_install_did_not_write(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _claude_root(tmp_path)
    _plant(_claude_plugin(root) / _GUARDRAIL, "print 'mine';\n")
    monkeypatch.setattr("devpro.install.GUARDRAIL_INTERPRETER", "devpro-no-such-perl")
    capsys.readouterr()
    _definition_install(root, project_root=tmp_path)
    [skipped] = [line for line in capsys.readouterr().err.splitlines() if line.startswith("guardrail hook skipped")]
    assert "left in place" not in skipped


def test_a_probe_that_hangs_fails_within_its_timeout(tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    slow = tmp_path / "slow-perl"
    slow.write_text("#!/usr/bin/env bash\nexec sleep 30\n", encoding="utf-8")
    slow.chmod(0o755)
    monkeypatch.setattr("devpro.install.GUARDRAIL_INTERPRETER", str(slow))
    monkeypatch.setattr("devpro.install.GUARDRAIL_PROBE_SECONDS", 0.5)
    project = tmp_path / "project"
    project.mkdir()
    root = _claude_root(project)
    capsys.readouterr()
    _definition_install(root, project_root=project)
    assert not (project / _SETTINGS).exists()
    [skipped] = [line for line in capsys.readouterr().err.splitlines() if line.startswith("guardrail hook skipped")]
    assert "did not exit within 0.5 seconds" in skipped


@pytest.mark.usefixtures("_no_uncommitted")
@pytest.mark.parametrize(
    "setup",
    [
        _kb_install_with_a_runner_file,
        _agents_file_in_a_project,
        _mage_below_its_project,
    ],
    ids=["kb-runner-file", "agents-file", "mage-subdir"],
)
def test_a_second_identical_run_whose_decisions_read_the_real_location_is_up_to_date(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch, setup
) -> None:
    """Nothing under the target changes, a modification time included."""
    argv, base = setup(tmp_path, monkeypatch)
    main(argv)
    state = _state(base)
    capsys.readouterr()
    main(argv)
    out = capsys.readouterr().out
    assert _UP_TO_DATE in out and "installed:" not in out
    assert _state(base) == state


def test_a_changed_component_installs(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    argv = [str(project), "--harness=claude"]
    main(["install", *argv])
    files = _files(project)
    capsys.readouterr()
    main(["install", *argv, "--components=kbase"])
    assert _UP_TO_DATE not in capsys.readouterr().out
    assert _files(project) != files


@pytest.mark.usefixtures("_no_uncommitted")
@pytest.mark.parametrize(
    ("changing",),
    [(["--components=kbase"],), ([],)],
    ids=["added-component", "plain"],
)
def test_a_changing_mage_install_passes_over_the_agents_file_it_does_not_rewrite(
    tmp_path: Path, capsys, changing: list[str]
) -> None:
    """Mage's install directory is the harness directory `--subdir` names, so the plugin's `CLAUDE.md`
    sits there at ROOT's root — naming neither the directory the preflight makes for the run nor the
    one the harness directory sits in. The replacement must pass the file over by path, so the
    operator's text above and below the block and the block the earlier run wrote stand, the backup the
    rewrite makes holds the whole prior file, and a dry run lists nothing at or below the file. Defect
    (TEST_PRECONDITION): a run that does not pass the agents file over removes it before
    `write_agents_file` rewrites it — the operator's text with it — and writes the backup from the run's
    own render; a dry run names the file or its directory among the removals."""
    argv, project = _mage_below_its_project(tmp_path, pytest.MonkeyPatch())
    main(argv)
    mage = project / "plugins/devpro"
    agents = mage / "CLAUDE.md"
    above, below = "# My rules\n\nkeep this above\n", "\nkeep this below\n"
    earlier = "earlier block\n"
    prior = f"{above} {_BEGIN}\n{earlier}{_END}{below}"
    agents.write_text(prior, encoding="utf-8")
    capsys.readouterr()
    main([*argv, *changing])
    block = "\n".join(_block(CLAUDE))
    assert agents.read_text(encoding="utf-8") == f"{above}{block}{below}"
    assert (mage / "backup.CLAUDE.md").read_text(encoding="utf-8") == prior
    capsys.readouterr()
    main([*argv, *changing, "--dry-run"])
    printed = _dry_run_groups(capsys.readouterr().out)
    assert not any(
        PurePosixPath(path).name in ("CLAUDE.md", "backup.CLAUDE.md") for paths in printed.values() for path in paths
    )
    assert agents.read_text(encoding="utf-8") == f"{above}{block}{below}"


@pytest.mark.usefixtures("_no_uncommitted")
@pytest.mark.parametrize("components", ["", "kbase"], ids=["plain", "with-kbase"])
@pytest.mark.parametrize(
    "harness_args",
    [
        ["--harness=claude"],
        ["--harness=opencode"],
        ["--harness=mage", "--subdir=plugins/devpro"],
    ],
    ids=["claude", "opencode", "mage-subdir"],
)
def test_a_dry_run_on_a_fresh_target_lists_as_created_what_the_install_creates(
    tmp_path: Path, capsys, harness_args: list[str], components: str
) -> None:
    """The project's runner file is in play too: with the kbase component on it gains the kb include line,
    so it is listed as changed."""
    project = tmp_path / "project"
    project.mkdir()
    (project / "justfile").write_text("# mine\n", encoding="utf-8")
    groups = _assert_dry_run_predicts(
        ["install", str(project), f"--components={components}", *harness_args], project=project, capsys=capsys
    )
    assert groups["created"]
    # The `.gitignore` line a project install of a nested plugin prepares is predicted; the scratch
    # directory's creation is named by the install's own conditional where the real tree lacks it — a
    # mage install prepares neither file.
    nested = "--harness=mage" not in harness_args
    assert (".devpro-temp/" in groups["created"]) is nested
    assert (".gitignore" in groups["created"]) is nested


@pytest.mark.usefixtures("_uncommitted_never_read")
@pytest.mark.parametrize(
    ("harness", "ships_kbase"),
    [(CLAUDE, True), (OPENCODE, False)],
    ids=["claude", "opencode"],
)
def test_a_dry_run_of_a_user_level_kbase_install_predicts_the_install(
    tmp_path: Path, capsys, harness: Harness, ships_kbase: bool
) -> None:
    """A user-level kbase install renders `.mcp.json` where the harness renders one: claude's, beside its
    plugin's manifest; opencode carries the entry in its registry instead."""
    home = tmp_path / "home"
    harness.user_dir.mkdir(parents=True)
    argv = ["install", str(home), "--components=kbase", f"--harness={harness.name}"]
    groups = _assert_dry_run_predicts(argv, project=home, capsys=capsys)
    assert any(PurePosixPath(path).name == ".mcp.json" for path in groups["created"]) is ships_kbase


def test_a_dry_run_after_a_family_change_lists_the_renders_as_changed(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), "--harness=opencode"]
    main([*argv, "--family=gemma-4"])
    groups = _assert_dry_run_predicts([*argv, "--family=qwen3"], project=project, capsys=capsys)
    assert groups["changed"] and set(groups) == {"changed"}


def test_a_dry_run_lists_a_stale_render_as_removed(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    root = project / ".claude"
    root.mkdir(parents=True)
    argv = ["install", str(project), "--harness=claude"]
    main(argv)
    (_claude_plugin(root) / "agents/gone.md").write_text(_NEW_BANNER, encoding="utf-8")
    groups = _assert_dry_run_predicts(argv, project=project, capsys=capsys)
    assert groups == {"removed": {f"{_CLAUDE_PLUGIN_RELPATH}/agents/gone.md"}}


def test_a_dry_run_lists_a_renamed_profiler_store_as_a_path_removed_and_a_path_created(tmp_path: Path, capsys) -> None:
    """A project up to date, then given a `.devpro-temp/claude-profiler/`: the dry run names the old store
    removed and `.devpro-temp/.profiler-claude/` created, and neither its files nor a store's contents as
    changed. A preflight that cannot read the rename reports the target up to date and promises a dry run
    that omits the one change the run makes."""
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), "--harness=claude"]
    main(argv)
    store = project / ".devpro-temp" / "claude-profiler"
    store.mkdir(parents=True)
    (store / "s-old.jsonl").write_text('{"v": 2}\n', encoding="utf-8")
    state = _state(project)
    capsys.readouterr()

    main([*argv, "--dry-run"])
    groups = _dry_run_groups(capsys.readouterr().out)
    assert groups == {
        "created": {".devpro-temp/.profiler-claude/s-old.jsonl"},
        "removed": {".devpro-temp/claude-profiler/"},
    }
    assert _state(project) == state

    main(argv)
    assert sorted(path.name for path in (project / ".devpro-temp").iterdir()) == [".profiler-claude"]


@pytest.mark.usefixtures("_no_uncommitted")
@pytest.mark.parametrize(
    "argv",
    [
        ["install", "{project}", "--harness=claude"],
        ["install-agents-file", "{project}", "--harness=claude"],
    ],
    ids=["install", "install-agents-file"],
)
def test_a_dry_run_on_an_up_to_date_target_says_so(tmp_path: Path, capsys, argv: list[str]) -> None:
    project = tmp_path / "project"
    project.mkdir()
    argv = [part.format(project=project) for part in argv]
    main(argv)
    state = _state(project)
    capsys.readouterr()
    main([*argv, "--dry-run"])
    out = capsys.readouterr().out
    assert _UP_TO_DATE in out and _dry_run_groups(out) == {}
    assert _state(project) == state


@pytest.mark.usefixtures("_no_uncommitted")
def test_an_agents_file_dry_run_names_the_files_and_writes_nothing(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    groups = _assert_dry_run_predicts(
        ["install-agents-file", str(project), "--harness=claude"], project=project, capsys=capsys
    )
    assert groups == {"created": {"AGENTS.md", "CLAUDE.md"}}


def test_no_printed_path_or_refusal_names_the_scratch_copy(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A refusal the copy run raises names the real link; the scratch copy is gone afterwards."""
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr("tempfile.tempdir", str(scratch))
    project = tmp_path / "project"
    root = project / ".claude"
    root.mkdir(parents=True)
    main(["install", str(project), "--harness=claude"])
    printed = capsys.readouterr().out
    link = _claude_plugin(root)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    shutil.rmtree(link)
    link.symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(SystemExit) as exit_info:
        main(["install", str(project), "--harness=claude"])
    assert exit_info.value.code == 2
    refusal = capsys.readouterr().err
    assert f"'{link}'" in refusal
    assert str(scratch) not in printed + refusal
    assert list(scratch.iterdir()) == []


def test_a_project_plugin_a_user_level_one_shadows_is_reported_on_every_run(
    tmp_path: Path, _home: Path, capsys
) -> None:
    """The report reads the real home, so an up-to-date run and a dry run make it too."""
    _user_level_plugin(_home)
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), "--harness=claude"]
    shadowed = f"{_claude_plugin(project / '.claude')} is shadowed by {_claude_plugin(_home / '.claude')}"
    for run in (argv, argv, [*argv, "--dry-run"]):
        capsys.readouterr()
        main(run)
        assert shadowed in capsys.readouterr().err


def test_no_shadow_is_reported_without_a_user_level_plugin(tmp_path: Path, _home: Path, capsys) -> None:
    """A user-level manifest that is not ours shadows nothing this install can name."""
    _plant(_claude_plugin(_home / ".claude") / ".claude-plugin/plugin.json", '{"name": "other"}\n')
    project = tmp_path / "project"
    project.mkdir()
    capsys.readouterr()
    main(["install", str(project), "--harness=claude"])
    assert "shadowed" not in capsys.readouterr().err


def test_a_user_level_plugin_reports_that_it_shadows_every_projects(_home: Path, capsys) -> None:
    capsys.readouterr()
    _user_level_plugin(_home)
    assert f"{_claude_plugin(_home / '.claude')} is user-level" in capsys.readouterr().err


@pytest.mark.parametrize("harness, printed", [("claude", True), ("opencode", False)], ids=["claude", "opencode"])
def test_the_reload_rule_is_printed_after_an_install_that_writes_and_not_when_up_to_date(
    tmp_path: Path, capsys, harness: str, printed: bool
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    argv = ["install", str(project), f"--harness={harness}"]
    capsys.readouterr()
    main(argv)
    assert (CLAUDE.reload_rule in capsys.readouterr().out) is printed
    main(argv)
    out = capsys.readouterr().out
    assert _UP_TO_DATE in out and CLAUDE.reload_rule not in out


@pytest.mark.parametrize(
    "components, harness_args, planted",
    [
        ("", ["--harness=claude"], f"{_CLAUDE_PLUGIN_RELPATH}/agents"),
        ("kbase", ["--harness=opencode", "--subdir=tools"], "tools/plugins/devpro/registry.json"),
        ("", ["--harness=claude"], _CLAUDE_PLUGIN_RELPATH),
    ],
    ids=["render-target", "registry-target", "install-directory"],
)
def test_a_dry_run_foresees_a_file_on_the_way(
    tmp_path: Path, capsys, components: str, harness_args: list[str], planted: str
) -> None:
    project = tmp_path / "project"
    (project / "tools").mkdir(parents=True)
    path = _plant(project / planted, "mine\n")
    argv = ["install", str(project), f"--components={components}", *harness_args]
    files, directories = _files(project), _directories(project)
    dry_code, dry_lines, groups = _run_outcome([*argv, "--dry-run"], capsys, planted=path)
    real_code, real_lines, _ = _run_outcome(argv, capsys, planted=path)
    assert (dry_code, dry_lines) == (real_code, real_lines)
    assert groups == _changed_since(files, directories, project=project)
