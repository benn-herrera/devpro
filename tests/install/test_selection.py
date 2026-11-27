"""harness detect/flag/settings• components• maps"""

from collections.abc import Callable
from pathlib import Path

import pytest

from devpro.cli import main
from tests._structure import kbase_skill_output_paths
from tests.conftest import settings_file

from .conftest import (
    _claude_plugin,
    _delivers_the_kbase_server,
    _files,
    _installs_the_kbase_skill,
    _opencode_plugin,
    _renders_the_kbase_skill,
)


@pytest.mark.parametrize(
    ("verb", "args", "ships"),
    [
        ("dev-render", ["--out", "{out}"], _renders_the_kbase_skill),
        ("install", ["{out}", "--harness=claude"], _installs_the_kbase_skill),
    ],
    ids=["dev-render", "install"],
)
def test_the_components_flag_turns_the_component_on(
    tmp_path: Path, monkeypatch, verb: str, args: list[str], ships: Callable[[Path], bool]
) -> None:
    """`--components=kbase` is the whole of turning the kbase skill on: before the flag existed argparse
    refused it as unknown and no render or install could carry the component."""
    monkeypatch.setenv("DEVPRO_DEV", "1")
    for name, flag in (("with-kbase", ["--components=kbase"]), ("plain", [])):
        out = tmp_path / name
        out.mkdir()
        main([verb, *flag, *(arg.format(out=out) for arg in args)])
        assert ships(out) is bool(flag), name


@pytest.mark.parametrize("name", ["nosuch", "development"])
def test_a_component_name_that_is_no_optional_component_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], name: str
) -> None:
    """The components are the optional ones alone, so a required definition is no legal value either;
    before the flag existed no validation existed. Nothing is written."""
    project = tmp_path / "project"
    project.mkdir()
    with pytest.raises(SystemExit) as exited:
        main(["install", str(project), f"--components={name}", "--harness=claude"])
    assert exited.value.code == 2
    err = capsys.readouterr().err
    assert f"unknown component '{name}'" in err and "optional components are kbase" in err
    assert _files(project) == {}


def test_a_component_given_as_a_positional_names_no_component(tmp_path: Path, capsys, monkeypatch) -> None:
    """The first positional is the target, so a lone `devpro install kbase` is refused where no such
    directory exists; nothing is written."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exited:
        main(["install", "kbase", "--harness=claude"])
    assert exited.value.code == 2
    assert "install target 'kbase'" in capsys.readouterr().err
    assert not (tmp_path / "kbase").exists()


@pytest.mark.usefixtures("_no_uncommitted")
def test_a_settings_files_components_value_drives_its_harness_install_and_the_flag_overrides_it(
    tmp_path: Path,
) -> None:
    """`[<harness>]`'s `components` is that harness's install selection, and `--components` given replaces
    it."""
    settings = settings_file(tmp_path, '[claude]\ncomponents = "kbase"\n')
    for name, flag, ships_kbase in (("from-settings", [], True), ("overridden", ["--components="], False)):
        project = tmp_path / name
        (project / ".claude").mkdir(parents=True)
        main(["install", str(project), *flag, f"--config-file={settings}"])
        root = _claude_plugin(project / ".claude")
        assert (root / "skills/kbase/SKILL.md").is_file() is ships_kbase, name
        assert _delivers_the_kbase_server(project, root) is ships_kbase, name


def test_the_cli_plugin_argument_installs_the_kbase_skill_files_and_the_skill_kb_tools_destination(
    tmp_path: Path,
) -> None:
    """The plugin argument reaches `install()`: driven through the CLI entry point, its own effect —
    the kbase skill's files and the runner snippets — is what appears under the plugin's ROOT."""
    root = tmp_path / ".claude"
    root.mkdir()
    main(["install", str(root), "--components=kbase", "--harness=claude"])
    plugin = _claude_plugin(root)
    assert all((plugin / relative).is_file() for relative in kbase_skill_output_paths())
    snippets = plugin / "skills/kbase/kb-tools/runner-snippets"
    assert (snippets / "kb.just").is_file() and (snippets / "kb.mk").is_file()


def test_the_settings_file_reaches_the_render(tmp_path: Path, monkeypatch) -> None:
    """Only a call through `main([...])` proves the file reaches the render: every category inherits, so
    the agent's frontmatter line reads `model: inherit`."""
    monkeypatch.setenv("DEVPRO_DEV", "1")
    out = tmp_path / "out"
    out.mkdir()
    settings = settings_file(tmp_path, '[claude.model-map]\n"*" = "inherit"\n')
    main(["dev-render", "--out", str(out), "--harness=claude", f"--config-file={settings}"])
    assert "\nmodel: inherit\n" in (out / "agents/python-coder.md").read_text(encoding="utf-8")


def test_the_settings_file_refuses_a_glob_naming_no_category(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv("DEVPRO_DEV", "1")
    out = tmp_path / "out"
    out.mkdir()
    settings = settings_file(tmp_path, '[claude.model-map]\n"nope" = "x"\n')
    with pytest.raises(SystemExit) as exited:
        main(["dev-render", "--out", str(out), "--harness=claude", f"--config-file={settings}"])
    assert exited.value.code == 2
    assert (
        f"--config-file {settings}, table '[claude.model-map]': 'nope=x' names no category" in capsys.readouterr().err
    )
    assert not any(out.iterdir())


def test_a_settings_file_installing_always_for_two_harnesses_installs_both(tmp_path: Path) -> None:
    """One invocation, one install per harness the file names, whatever the target holds."""
    project = tmp_path / "project"
    project.mkdir()
    settings = settings_file(tmp_path, '[claude]\ninstall = "always"\n\n[opencode]\ninstall = "always"\n')
    main(["install", str(project), f"--config-file={settings}"])
    assert (_claude_plugin(project / ".claude") / "agents/python-coder.md").is_file()
    assert (_opencode_plugin(project / ".opencode") / "agents/python-coder.md").is_file()


def test_a_detect_harness_whose_directory_the_target_lacks_is_skipped(tmp_path: Path) -> None:
    """`detect` is the setting the file leaves unset, judged per harness against the target."""
    project = tmp_path / "project"
    (project / ".opencode").mkdir(parents=True)
    settings = settings_file(tmp_path, "[claude]\n\n[opencode]\n")
    main(["install", str(project), f"--config-file={settings}"])
    assert (_opencode_plugin(project / ".opencode") / "agents").is_dir()
    assert not (project / ".claude").exists()


def test_a_map_section_alone_names_its_harness_and_detect_installs_it(tmp_path: Path) -> None:
    """Either table names a harness; a map table's entries reach the render it is installed with."""
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    settings = settings_file(tmp_path, '[claude.model-map]\n"*" = "inherit"\n')
    main(["install", str(project), f"--config-file={settings}"])
    agent = (_claude_plugin(project / ".claude") / "agents/python-coder.md").read_text(encoding="utf-8")
    assert "\nmodel: inherit\n" in agent


def test_a_never_harness_installs_nothing(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    settings = settings_file(tmp_path, '[claude]\ninstall = "never"\n')
    main(["install", str(project), f"--config-file={settings}"])
    assert _files(project) == {}


def test_the_harness_flag_overrides_the_selection_and_still_applies_its_map(tmp_path: Path) -> None:
    """`--harness` installs for that harness alone and the file's `install` setting is neither consulted
    nor judged — opencode's is no setting at all — while claude's own table's map still applies."""
    project = tmp_path / "project"
    project.mkdir()
    settings = settings_file(tmp_path, '[claude.model-map]\n"*" = "inherit"\n\n[opencode]\ninstall = "sometimes"\n')
    main(["install", str(project), "--harness=claude", f"--config-file={settings}"])
    agent = (_claude_plugin(project / ".claude") / "agents/python-coder.md").read_text(encoding="utf-8")
    assert "\nmodel: inherit\n" in agent
    assert not (project / ".opencode").exists()


def test_detect_judges_the_target_not_the_subdir_the_install_writes_below_it(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    settings = settings_file(tmp_path, "[claude]\n")
    main(["install", str(project), f"--config-file={settings}", "--subdir=.claude"])
    assert not (project / ".claude").exists()
    assert _files(project) == {}


def test_a_missing_target_is_refused_under_a_settings_file_as_without_one(tmp_path: Path, capsys) -> None:
    """The target's existence is refused before the file's harnesses are judged: this target holds no
    harness directory, so a `detect` setting would skip the loop and take the refusal with it."""
    settings = settings_file(tmp_path, "[claude]\n")
    missing = tmp_path / "absent"
    with pytest.raises(SystemExit) as exited:
        main(["install", str(missing), f"--config-file={settings}"])
    assert exited.value.code == 2
    assert f"install target '{missing}' is not an existing directory" in capsys.readouterr().err
    assert not missing.exists()


def test_an_escaping_subdir_is_refused_under_a_settings_file_as_without_one(tmp_path: Path, capsys) -> None:
    """The `--subdir` refusal is made before the harnesses are judged, whatever the settings say."""
    project = tmp_path / "project"
    project.mkdir()
    settings = settings_file(tmp_path, '[claude]\ninstall = "never"\n')
    with pytest.raises(SystemExit) as exited:
        main(["install", str(project), f"--config-file={settings}", "--subdir=../escape"])
    assert exited.value.code == 2
    assert "--subdir '../escape' must name a directory inside the target" in capsys.readouterr().err
    assert _files(project) == {}


def test_a_harness_the_settings_file_does_not_name_is_not_installed(tmp_path: Path) -> None:
    """The file is an expression of intent: a harness it leaves out installs nothing, though the target
    holds its harness directory."""
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    settings = settings_file(tmp_path, '[opencode]\ninstall = "always"\n')
    main(["install", str(project), f"--config-file={settings}"])
    assert (_opencode_plugin(project / ".opencode") / "agents").is_dir()
    assert _files(project / ".claude") == {}


def test_a_refusal_mid_loop_names_its_harness_and_earlier_installs_stand(tmp_path: Path, capsys) -> None:
    """The named harnesses install in name order, so claude's install stands when opencode, the
    name-later one, refuses over a file at a path it would write."""
    project = tmp_path / "project"
    project.mkdir()
    mine = _opencode_plugin(project / ".opencode") / "agents/python-coder.md"
    mine.parent.mkdir(parents=True)
    mine.write_text("---\nname: python-coder\n---\n\nmy own agent\n", encoding="utf-8")
    settings = settings_file(tmp_path, '[claude]\ninstall = "always"\n\n[opencode]\ninstall = "always"\n')
    with pytest.raises(SystemExit) as exited:
        main(["install", str(project), f"--config-file={settings}"])
    assert exited.value.code == 2
    err = capsys.readouterr().err
    assert "harness 'opencode'" in err and str(mine) in err
    assert (_claude_plugin(project / ".claude") / "agents/python-coder.md").is_file()


def test_a_map_section_naming_no_category_leaves_every_harness_uninstalled(tmp_path: Path, capsys) -> None:
    """The whole file is read before the loop writes, so a later harness's bad map refuses the early
    harness's install too."""
    project = tmp_path / "project"
    project.mkdir()
    settings = settings_file(tmp_path, '[claude]\ninstall = "always"\n\n[opencode.model-map]\n"stem-expert" = "opus"\n')
    with pytest.raises(SystemExit) as exited:
        main(["install", str(project), f"--config-file={settings}"])
    assert exited.value.code == 2
    assert "names no value for" in capsys.readouterr().err
    assert _files(project) == {}


def test_an_install_setting_outside_the_three_is_refused_before_anything_is_written(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    settings = settings_file(tmp_path, '[claude]\ninstall = "always"\n\n[opencode]\ninstall = "sometimes"\n')
    with pytest.raises(SystemExit) as exited:
        main(["install", str(project), f"--config-file={settings}"])
    assert exited.value.code == 2
    err = capsys.readouterr().err
    assert "install 'sometimes'" in err and "always, detect, never" in err
    assert str(settings) in err and "table '[opencode]'" in err
    assert _files(project) == {}


@pytest.mark.parametrize("text", ["", "# my fleet, all of it commented out\n"], ids=["empty", "comments-only"])
def test_a_settings_file_naming_no_harness_installs_nothing(tmp_path: Path, text: str, capsys) -> None:
    """A file present is an expression of intent even when it is emptied: it selects no harness, so no
    harness installs and detection does not step in — a target holding two is neither refused nor
    installed into; the run says so on stderr, naming the file, and exits 0."""
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    (project / ".opencode").mkdir()
    settings = settings_file(tmp_path, text)
    main(["install", str(project), f"--config-file={settings}"])
    err = capsys.readouterr().err
    assert "nothing installed" in err and str(settings) in err
    assert _files(project) == {}
