"""package copy• resource copy• bytecode• duplicate output"""

import json
import os
import re
from collections.abc import Callable
from pathlib import Path, PurePosixPath

import pytest

from devpro.cli import main
from devpro.components import Components
from devpro.definition import Definition
from devpro.errors import InputError
from devpro.install import HARNESS_RESOURCES_SOURCE, ShippedPackage, harness_resource_copies, package_copies
from devpro.install_base import PACKAGE_ROOT
from devpro.loading import load
from devpro.render import render_all
from devpro.vocabulary import Kind
from tests.conftest import PLAIN, WITH_KBASE

from .conftest import (
    _CLAUDE_PLUGIN_RELPATH,
    _CLAUDE_RENDER,
    _DEVELOPMENT_SCRIPTS,
    _DEVPRO_PACKAGE,
    _GUARDRAIL,
    _GUARDRAIL_MATCHER,
    _KBASE_PACKAGE,
    _MAGE_RENDER,
    _NEW_BANNER,
    _OPENCODE_RENDER,
    _OPENCODE_SETTINGS_NAMES,
    _PROFILER,
    _PROFILER_COMMAND,
    _PROFILER_EVENTS,
    _PROFILER_SKILL,
    _REGISTRATION,
    _REMINDER,
    _SETTINGS,
    _TS_GUARDRAIL,
    _claude_plugin,
    _definition_install,
    _delivers_the_kbase_server,
    _files,
    _opencode_plugin,
    _plant,
)


def test_an_opencode_install_copies_the_harnesss_plugin_byte_verbatim(tmp_path: Path) -> None:
    """The opencode plugin is the harness's own file, not this repository's generated product: it lands
    under ROOT byte for byte, so a stamp anywhere in the copy would show as a difference from the
    source."""
    root = tmp_path / ".opencode"
    root.mkdir()
    _definition_install(root, _OPENCODE_RENDER, project_root=tmp_path)
    copied = _opencode_plugin(root) / _TS_GUARDRAIL
    assert copied.read_bytes() == (PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "opencode" / _TS_GUARDRAIL).read_bytes()


def test_a_fresh_claude_install_ships_the_guardrail_and_registers_it_in_the_plugin(tmp_path: Path) -> None:
    """Where the probe passes, the hook script lands byte-verbatim and executable under ROOT beside the
    plugin's one registration, which holds the guardrail's `PreToolUse` entry and the plan-state
    reminder's `PostToolUse` entry, and the project gains no settings file."""
    root = tmp_path / ".claude"
    root.mkdir()
    _definition_install(root, project_root=tmp_path)
    copied = _claude_plugin(root) / _GUARDRAIL
    assert copied.read_bytes() == (PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "claude" / _GUARDRAIL).read_bytes()
    assert os.access(copied, os.X_OK)
    assert (_claude_plugin(root) / _REMINDER).is_file()
    registration = json.loads((_claude_plugin(root) / _REGISTRATION).read_text(encoding="utf-8"))
    assert list(registration) == ["hooks"]
    hooks = registration["hooks"]
    assert [entry["matcher"] for entry in hooks["PreToolUse"]] == [_GUARDRAIL_MATCHER]
    assert "Agent" in [entry["matcher"] for entry in hooks["PostToolUse"]]
    assert not (tmp_path / _SETTINGS).exists()


def test_the_profiler_ships_the_skill_and_no_launcher(tmp_path: Path) -> None:
    """The profiler's code and page are devpro's own and ship in the wheel; the one file it adds to the
    install directory is the wrapper every install writes. Defect: the harness resources once carried a
    launcher under `profiler/`, and an install delivered it as a resource beside the hooks."""
    root = tmp_path / ".claude"
    root.mkdir()
    _definition_install(root, project_root=tmp_path)
    plugin = _claude_plugin(root)
    assert (plugin / "tools" / "devpro.sh").is_file()
    assert not (plugin / _PROFILER).exists()
    assert not (PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "claude" / _PROFILER).exists()


def test_the_claude_registration_carries_the_profiler_on_every_event_it_captures(tmp_path: Path) -> None:
    """A hooks file missing an entry ships a claude install that records no activity of that kind: each
    of the profiler's six events carries one matcher group on every call, running the capture out of
    band and short, beside the guardrail's and the reminder's entries."""
    root = tmp_path / ".claude"
    root.mkdir()
    _definition_install(root, project_root=tmp_path)
    hooks = json.loads((_claude_plugin(root) / _REGISTRATION).read_text(encoding="utf-8"))["hooks"]
    for event in _PROFILER_EVENTS:
        [profiler] = [entry for entry in hooks[event] if entry["matcher"] == "*"]
        [hook] = profiler["hooks"]
        assert hook == {"type": "command", "command": _PROFILER_COMMAND, "async": True, "timeout": 5}, event
    assert [entry["matcher"] for entry in hooks["PreToolUse"]] == [_GUARDRAIL_MATCHER]


def test_the_profile_skill_renders_under_every_harness() -> None:
    """The skill is a rendered definition, not a claude payload: a harness that ships no profiler still
    renders it, so its committed-copy fallback can be reached there."""
    for ctx in (_CLAUDE_RENDER, _OPENCODE_RENDER, _MAGE_RENDER):
        assert PurePosixPath(_PROFILER_SKILL) in dict(render_all(ctx)), ctx.harness.name


def test_a_second_install_leaves_the_copied_plugin_standing_and_prunes_only_the_stale_render(
    tmp_path: Path, capsys
) -> None:
    """The copied file is in `keep`, so a re-install neither rewrites it away nor prunes it: the one
    rendered file planted beside it is what goes."""
    root = tmp_path / ".opencode"
    root.mkdir()
    _definition_install(root, _OPENCODE_RENDER, project_root=tmp_path)
    copied = _opencode_plugin(root) / _TS_GUARDRAIL
    before = copied.read_bytes()
    stale = _opencode_plugin(root) / "agents/gone.md"
    stale.write_text(_NEW_BANNER, encoding="utf-8")
    capsys.readouterr()
    _definition_install(root, _OPENCODE_RENDER, project_root=tmp_path)
    assert copied.read_bytes() == before
    assert not stale.exists()
    out = capsys.readouterr().out
    assert f"pruned {stale}" in out
    assert f"pruned {copied}" not in out


def test_the_package_copy_stages_every_file_the_running_package_holds(tmp_path: Path, _staged) -> None:
    """The package copy takes its source tree whole, less the `__pycache__` directories no wheel
    carries: that source is the clone's own tree when the install runs from a checkout, which has no
    build to filter it. Defect: a denylist here dropped a file the tree carried, so an installed copy
    was not the package it ran."""
    _staged(
        tmp_path / "devpro",
        (
            ("tool.py", "probe\n"),
            ("tests/test_tool.py", "probe\n"),
            ("SPEC.md", "probe\n"),
            (".DS_Store", "probe\n"),
            ("a/x.py.bak", "probe\n"),
            ("README.md", "probe\n"),
            ("__pycache__/tool.cpython-311.pyc", "probe\n"),
        ),
    )
    copies = package_copies(tmp_path / "root", ShippedPackage(".", "tools/devpro", None, stamps=False))
    assert [target.relative_to(tmp_path / "root").as_posix() for _, target in copies] == sorted(
        f"tools/devpro/{relative}"
        for relative in (".DS_Store", "README.md", "SPEC.md", "a/x.py.bak", "tests/test_tool.py", "tool.py")
    )


def test_a_resource_copy_stages_every_file_the_tree_holds(tmp_path: Path, _staged) -> None:
    """The harness resource copy reads its tree as it stands, filtering nothing: a `.DS_Store` or a
    `.bak` beside a harness's own file is the source's, and no walk drops what the build or the
    checkout delivered."""
    _staged(
        tmp_path,
        (
            (f"{HARNESS_RESOURCES_SOURCE}/probe/plugins/keep.ts", "probe\n"),
            (f"{HARNESS_RESOURCES_SOURCE}/probe/plugins/.DS_Store", "probe\n"),
            (f"{HARNESS_RESOURCES_SOURCE}/probe/plugins/keep.ts.bak", "probe\n"),
        ),
    )
    root = tmp_path / ".probe"
    copies = harness_resource_copies(root, harness="probe")
    assert [target.relative_to(root).as_posix() for _, target in copies] == sorted(
        ["plugins/.DS_Store", "plugins/keep.ts", "plugins/keep.ts.bak"]
    )


def test_neither_staging_path_copies_bytecode(tmp_path: Path, _staged) -> None:
    """Bytecode is no wheel content: a `__pycache__` directory in a source tree — what a pip-compiled
    install of the wheel holds and the wheel itself does not — reaches neither the package copy nor
    the harness resource copy, at any depth. Defect: both walks took every file, so an install staged
    from a pip-installed wheel shipped a `.pyc` beside every module it copied."""
    _staged(
        tmp_path,
        (
            ("tool.py", "probe\n"),
            ("__pycache__/tool.cpython-311.pyc", "probe\n"),
            ("sub/__pycache__/deeper.cpython-311.pyc", "probe\n"),
            (f"{HARNESS_RESOURCES_SOURCE}/probe/plugins/keep.ts", "probe\n"),
            (f"{HARNESS_RESOURCES_SOURCE}/probe/__pycache__/probe.cpython-311.pyc", "probe\n"),
        ),
    )
    root = tmp_path / ".probe"
    staged = [
        *(
            target.relative_to(root).as_posix()
            for _, target in package_copies(root, ShippedPackage(".", "tools/devpro", None))
        ),
        *(target.relative_to(root).as_posix() for _, target in harness_resource_copies(root, harness="probe")),
    ]
    assert sorted(staged) == [
        "plugins/keep.ts",
        "tools/devpro/harnesses/resources/probe/plugins/keep.ts",
        "tools/devpro/tool.py",
    ]


def test_the_resources_tree_is_not_read_as_a_harness_module() -> None:
    """`resources/` holds no `__init__.py`, so `pkgutil` lists it as a tree rather than a module and
    `load` returns every harness module. A `resources` package appearing later would break that, so the
    same case pins the tree's presence: a resource tree that went missing fails here too, rather than
    the plugin copy silently landing nothing."""
    assert sorted(load("devpro.harnesses", "HARNESS")) == ["claude", "mage", "opencode"]
    assert (PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "opencode").is_dir()


def test_a_duplicate_output_is_refused_even_when_the_selection_ships_neither_definition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The duplicate check runs over what discovery found, before the selection filter: a selection
    shipping neither definition — here the kbase component's member, with the component off — would
    otherwise render past a collision another selection refuses."""
    first = Definition(name="kbase", kind=Kind.COMMAND, body="one")
    second = Definition(name="kbase", kind=Kind.COMMAND, body="two")
    monkeypatch.setattr("devpro.render.discover", lambda: [("m.a", (first,)), ("m.b", (second,))])
    assert not PLAIN.ships("kbase")
    with pytest.raises(InputError, match=re.escape("'commands/kbase.md' is produced by both m.a and m.b")):
        render_all(_CLAUDE_RENDER)


@pytest.mark.parametrize(
    "harness, root_of",
    [
        ("claude", lambda project: _claude_plugin(project / ".claude")),
        ("opencode", lambda project: _opencode_plugin(project / ".opencode")),
    ],
    ids=["claude", "opencode"],
)
@pytest.mark.parametrize(
    "components, flag", [(PLAIN, []), (WITH_KBASE, ["--components=kbase"])], ids=["plain", "with-kbase"]
)
def test_supporting_artifacts_ship_with_the_definition_that_owns_them(
    tmp_path: Path, harness: str, root_of: Callable[[Path], Path], components: Components, flag: list[str]
) -> None:
    """Both selections carry the development scripts and the runner snippets, and every project install
    writes the devpro runner include line; only with the kbase component on does the install carry the
    kbase toolchain: the kb-tools package, the kbase MCP entry and the kb runner include line, in the
    same runner file. No install writes a project's opencode settings file."""
    project = tmp_path / "project"
    project.mkdir()
    (project / "justfile").write_text("# mine\n", encoding="utf-8")
    main(["install", str(project), *flag, f"--harness={harness}"])
    root = root_of(project)
    kbase = components is WITH_KBASE
    assert (root / _DEVELOPMENT_SCRIPTS).is_file()
    assert (root / _DEVPRO_PACKAGE).is_file()
    assert (root / _KBASE_PACKAGE).is_file() is kbase
    assert _delivers_the_kbase_server(project, root) is kbase
    assert not any(path.name in _OPENCODE_SETTINGS_NAMES for path in project.rglob("*"))
    justfile = (project / "justfile").read_text(encoding="utf-8")
    assert "tools/runner-snippets/devpro.just" in justfile
    assert ("runner-snippets/kb.just" in justfile) is kbase
    assert not (project / "Makefile").exists()


def test_an_install_changes_nothing_outside_its_own_install_directory(tmp_path: Path) -> None:
    """An install directory of another tool, or of an earlier layout, sits beside this one inside the
    harness directory's `skills/`: a devpro install leaves its every file as it found them, its own
    ROOT's files beside it being the only ones it writes or prunes."""
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=claude"])
    _plant(project / ".claude/skills/earlier-layout/agents/python-coder.md", _NEW_BANNER)
    others = {
        relative: data
        for relative, data in _files(project).items()
        if relative.startswith(".claude/skills/earlier-layout/")
    }
    assert others
    main(["install", str(project), "--components=kbase", "--harness=claude"])
    after = _files(project)
    assert {relative: after.get(relative) for relative in others} == others
    assert (project / _CLAUDE_PLUGIN_RELPATH / "agents/python-coder.md").is_file()
