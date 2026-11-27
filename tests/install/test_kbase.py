"""kbase skill• mcp entry• include line• mage"""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from devpro import __version__
from devpro.cli import build_parser, main
from devpro.errors import InputError
from devpro.install import install
from devpro.install_base import PACKAGE_ROOT, REPO_ROOT
from tests._structure import kbase_skill_output_paths

from .conftest import (
    _DEVPRO_SET_LINE,
    _KBASE_CLAUDE_RENDER,
    _KBASE_MAGE_RENDER,
    _KBASE_OPENCODE_RENDER,
    _KBASE_PACKAGE,
    _MAGE_MANIFEST,
    _MAGE_RENDER,
    _MAINTAINER_VERBS,
    _claude_plugin,
    _committed,
    _definition_install,
    _files,
    _opencode_plugin,
)


def test_a_kbase_install_writes_the_kbase_skill_the_package_the_mcp_entry_and_the_include_line(
    tmp_path: Path,
) -> None:
    project = tmp_path
    root = project / ".claude"
    root.mkdir()
    (project / "justfile").write_text("# mine\n", encoding="utf-8")
    _definition_install(root, _KBASE_CLAUDE_RENDER, project_root=project)
    plugin = _claude_plugin(root)
    for relative in kbase_skill_output_paths():
        assert (plugin / relative).is_file()
    kb_just = (plugin / "skills/kbase/kb-tools/runner-snippets/kb.just").read_text(encoding="utf-8").split("\n")
    source_just = (PACKAGE_ROOT / "kb-tools/runner-snippets/kb.just").read_text(encoding="utf-8").split("\n")
    kb_mk = (plugin / "skills/kbase/kb-tools/runner-snippets/kb.mk").read_text(encoding="utf-8").split("\n")
    assert kb_just[0].startswith("# !INSTALLED! from devpro/kb-tools/runner-snippets/kb.just — ")
    assert kb_just[1:] == source_just
    assert kb_mk[0].startswith("# !INSTALLED! from devpro/kb-tools/runner-snippets/kb.mk — ")
    snippets = plugin / "tools/runner-snippets"
    for name in ("devpro.just", "devpro.mk"):
        installed = (snippets / name).read_text(encoding="utf-8").split("\n")
        source = (PACKAGE_ROOT / f"runner-snippets/{name}").read_text(encoding="utf-8").split("\n")
        assert installed[0].startswith(f"# !INSTALLED! from devpro/runner-snippets/{name} — ")
        assert installed[1:] == source
    assert json.loads((plugin / ".mcp.json").read_text(encoding="utf-8")) == {
        "mcpServers": {"kbase": {"command": "kbase", "args": ["mcp"]}}
    }
    assert not (project / ".mcp.json").exists()
    relpath = plugin.relative_to(project).as_posix()
    assert (project / "justfile").read_text(encoding="utf-8") == (
        f"# mine\n\n{_DEVPRO_SET_LINE}\n\n" f"import? '{relpath}/skills/kbase/kb-tools/runner-snippets/kb.just'\n"
    )


def test_the_version_flag_prints_the_constant_and_nothing_else(capsys) -> None:
    """A recipe parses this line to cut the tag, so it is the constant alone: no `v`, no suffix, no
    prose, one line — and the constant carries that shape, which a manifest would inherit too."""
    with pytest.raises(SystemExit) as exited:
        main(["--version"])
    assert exited.value.code == 0
    assert capsys.readouterr().out == f"{__version__}\n"
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)


def test_version_is_refused_as_a_verb(capsys) -> None:
    with pytest.raises(SystemExit) as exited:
        main(["version"])
    assert exited.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_an_operating_system_failure_is_reported_as_an_error_and_exits_2(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.setenv("DEVPRO_DEV", "1")
    out = tmp_path / "missing" / "AGENTS.md"
    with pytest.raises(SystemExit) as exited:
        main(["render-agents-file", "claude", str(out)])
    assert exited.value.code == 2
    assert capsys.readouterr().err.startswith("error: ")
    assert not out.parent.exists()


def test_the_agents_file_script_ignores_a_third_argument(tmp_path: Path) -> None:
    """A stable interface across revisions: a newer caller of an older copy passes no third argument,
    and an older caller of a newer copy passes PLUGIN, which the body accepts and ignores. Both call
    shapes write identical bytes."""
    two = tmp_path / "two.md"
    three = tmp_path / "three.md"
    script = REPO_ROOT / "devtools/scripts/render-agents-file.sh"
    env = {
        "PATH": os.environ["PATH"],
        "PROJECT_ROOT": str(REPO_ROOT),
        "PYTHONPATH": str(REPO_ROOT),
        "GEN": "devpro",
    }
    for argv in (["claude", str(two)], ["claude", str(three), "kbase"]):
        subprocess.run(["bash", str(script), *argv], env=env, check=True, capture_output=True, text=True)
    assert two.read_bytes() == three.read_bytes()


def test_the_help_usage_line_lists_every_verb(capsys) -> None:
    with pytest.raises(SystemExit):
        main(["--help"])
    usage = capsys.readouterr().out.split("\n\n")[0]
    listed = re.search(r"\{([^}]*)\}", usage)
    assert listed is not None
    verbs = next(action for action in build_parser()._actions if isinstance(action, argparse._SubParsersAction))
    assert listed.group(1).split(",") == list(verbs.choices)


@pytest.mark.parametrize("value", [None, "0"], ids=["unset", "zero"])
def test_the_maintainer_verbs_exist_only_where_devpro_dev_is_1(capsys, monkeypatch, value: str | None) -> None:
    """Without `DEVPRO_DEV=1` the maintainer verbs are absent from `--help` and refused as an invalid
    choice; before the gate `--help` listed `render` and `render-agents-file`, and `harness` ran."""
    if value is None:
        monkeypatch.delenv("DEVPRO_DEV", raising=False)
    else:
        monkeypatch.setenv("DEVPRO_DEV", value)
    with pytest.raises(SystemExit):
        main(["--help"])
    help_text = capsys.readouterr().out
    choices = re.search(r"\{([^}]*)\}", help_text)
    assert choices is not None
    listed = {*choices.group(1).split(","), *re.findall(r"^ {4}(\S+)", help_text, flags=re.MULTILINE)}
    assert listed.isdisjoint({*_MAINTAINER_VERBS, "render"})
    for verb in (*_MAINTAINER_VERBS, "render"):
        with pytest.raises(SystemExit) as exited:
            main([verb, "claude", "agents-file"])
        assert exited.value.code == 2
        assert "invalid choice" in capsys.readouterr().err, verb


def test_an_opencode_kb_install_registers_the_server_in_its_registry_and_leaves_the_projects_settings(
    tmp_path: Path,
) -> None:
    """The server's entry is a record of the plugin's own registry, in opencode's v2 shape; the project's
    settings file stays as the project wrote it, and none is created beside it."""
    project = tmp_path
    root = project / ".opencode"
    root.mkdir()
    discovered = root / "opencode.json"
    prior = json.dumps({"theme": "omlx", "mcp": {"servers": {"other": {"type": "local"}}}})
    discovered.write_text(prior, encoding="utf-8")
    _definition_install(root, _KBASE_OPENCODE_RENDER, project_root=project)
    assert discovered.read_text(encoding="utf-8") == prior
    assert not (root / "opencode.jsonc").exists() and not (project / "opencode.json").exists()
    registry = json.loads((_opencode_plugin(root) / "registry.json").read_text(encoding="utf-8"))
    assert registry["mcp"] == {"kbase": {"type": "local", "command": ["kbase", "mcp"]}}


def test_a_mage_kbase_install_renders_its_mcp_json_whole_beside_the_set_at_root(tmp_path: Path) -> None:
    """ROOT is the install's own, so `.mcp.json` there is rendered whole: a prior one of ours is replaced,
    a server beside the entry included, and the project root holds no `.mcp.json` at all. The manifest
    is still the three-key one carrying `__version__`. No runner include line is written and no
    `Makefile` created at either root: an install directory is not a repo project."""
    project = tmp_path
    root = project / "plugins/devpro"
    root.mkdir(parents=True)
    entry = {"command": "kbase", "args": ["mcp", "--project-dir-required"]}
    prior = {"mcpServers": {"kbase": {"command": "kbase", "args": ["mcp"]}, "other": {"command": "x"}}}
    (root / ".mcp.json").write_text(json.dumps(prior), encoding="utf-8")
    _definition_install(root, _KBASE_MAGE_RENDER, project_root=project)
    settings = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
    assert settings == {"mcpServers": {"kbase": entry}}
    assert not (project / ".mcp.json").exists()
    manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    assert set(manifest) == {"name", "version", "description"}
    assert manifest["version"] == __version__
    assert not (root / "Makefile").exists()
    assert not (project / "Makefile").exists()


def test_a_mage_devpro_install_ships_no_part_of_the_kbase_toolchain(tmp_path: Path) -> None:
    """Under mage too the selection decides: the plain install holds no kbase skill, no kb-tools package
    and no MCP settings file."""
    project = tmp_path
    root = project / "plugins/devpro"
    root.mkdir(parents=True)
    _definition_install(root, _MAGE_RENDER, project_root=project)
    assert not (root / ".mcp.json").exists()
    assert not (root / "skills/kbase").exists()
    assert (root / "agents/python-coder.md").is_file()


def test_a_mage_kbase_install_ships_the_kbase_toolchain(tmp_path: Path) -> None:
    """Under mage the kbase component carries its kbase skill and the kb-tools package."""
    project = tmp_path
    root = project / "plugins/devpro"
    root.mkdir(parents=True)
    _definition_install(root, _KBASE_MAGE_RENDER, project_root=project)
    assert (root / _KBASE_PACKAGE).is_file()
    assert (root / "skills/kbase").is_dir()


def test_a_mage_install_names_no_absolute_path_and_no_home_directory(tmp_path: Path) -> None:
    """Nothing the plugin writes names the directory it lands in, because that directory moves. The `~/`
    search is over the manifest and the MCP settings file alone: a definition's prose names `~/.config` in
    order to forbid hardcoding it, so a tree-wide search reports the advice rather than a path."""
    project = tmp_path
    root = project / "plugins/devpro"
    root.mkdir(parents=True)
    _definition_install(root, _KBASE_MAGE_RENDER, project_root=project)
    files = _files(root)
    ours = (_MAGE_MANIFEST, ".mcp.json")
    assert set(ours) <= set(files)
    absolute = str(root.resolve()).encode()
    assert [relative for relative, data in files.items() if absolute in data] == []
    assert [relative for relative in ours if b"~/" in files[relative]] == []


def test_a_mage_install_ships_no_hook_and_writes_no_settings_file(tmp_path: Path) -> None:
    """mage has no guardrail, so no script lands under ROOT and no guardrail settings file appears
    either beside the plugin or at the project it installs into — as an opencode install writes none."""
    project = tmp_path
    root = project / "plugins/devpro"
    root.mkdir(parents=True)
    _definition_install(root, _MAGE_RENDER, project_root=project)
    assert not (root / "hooks").exists()
    assert not (project / ".claude/settings.json").exists()
    assert not (root / ".claude/settings.json").exists()


def test_a_second_mage_install_passes_over_its_own_manifest_byte_identical(tmp_path: Path) -> None:
    """The manifest is JSON, which no generated banner rides in front of, so the marker the file states
    about itself is what makes it ours: an install over one this repository wrote is not refused and
    not pruned, and rewrites the same bytes."""
    project = tmp_path
    root = project / "plugins/devpro"
    root.mkdir(parents=True)
    _definition_install(root, _MAGE_RENDER, project_root=project)
    manifest = root / _MAGE_MANIFEST
    written = manifest.read_bytes()
    _definition_install(root, _MAGE_RENDER, project_root=project)
    assert manifest.read_bytes() == written


def test_an_operators_manifest_without_the_marker_is_refused_with_nothing_written(tmp_path: Path) -> None:
    """A plugin of another name at that path is the operator's own, so the install refuses it whole and
    names it, writing nothing — no render lands before the refusal."""
    project = tmp_path
    root = project / "plugins/devpro"
    manifest = root / _MAGE_MANIFEST
    manifest.parent.mkdir(parents=True)
    manifest.write_text('{"name": "other"}\n', encoding="utf-8")
    before = _files(tmp_path)
    with pytest.raises(InputError, match=re.escape(f"'{manifest}'")):
        _definition_install(root, _MAGE_RENDER, project_root=project)
    assert _files(tmp_path) == before


def test_a_verbose_mage_install_lists_the_manifest_as_written(tmp_path: Path, capsys) -> None:
    project = tmp_path
    root = project / "plugins/devpro"
    root.mkdir(parents=True)
    capsys.readouterr()
    install(root, _MAGE_RENDER, verbose=True, project_root=project, uncommitted=_committed)
    assert f"wrote {root / _MAGE_MANIFEST}" in capsys.readouterr().out.splitlines()
