"""Shared helpers and fixtures for the install tests: the installed tree, the agents-file render, staging, and the plugin and definition installs."""

import dataclasses
import json
import os
import re
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path, PurePosixPath

import pytest

from devpro import __version__
from devpro.agents_file import BEGIN, install_agents_file, marker_span
from devpro.cli import main
from devpro.components import NAME
from devpro.context import MapSupply, Render, build_render
from devpro.definitions import discover
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.harness import Harness
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.mage import HARNESS as MAGE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.install import SHIPPED_PACKAGES, install
from devpro.install_base import PACKAGE_ROOT
from devpro.render import render_agents_file, render_all
from devpro.vocabulary import CATEGORIES, AgentsFileText, Kind, PluginText, hole
from tests.conftest import PLAIN, WITH_KBASE

_SNIPPET_SETS = {
    package.source: snippets for package in SHIPPED_PACKAGES if (snippets := package.installed_snippets()) is not None
}
_KB_SNIPPETS = _SNIPPET_SETS["kb-tools"]
_BEGIN = " <!-- vvv-devpro do not edit at or between marker lines. devpro-vvv -->"
_END = " <!-- ^^^-devpro do not edit at or between marker lines. devpro-^^^ -->"
_AGENTS_FILE = next(defn for _, entries in discover() for defn in entries if defn.kind is Kind.AGENTS_FILE)


def _agents_file_stamp(*, plugin: str | None) -> str:
    """The begin marker line the agents-file render stamps: its body's marker line filled with this
    version, and with `plugin`'s name where a plugin names it. The rendered line alone is not the
    source: a render reads the source out of the stamp, so reading the source through the render would
    hold however the source spelled it."""
    line = next(line for line in _AGENTS_FILE.body.split("\n") if line.strip().startswith(BEGIN[0]))
    body = line.replace(hole(AgentsFileText.VERSION), __version__)
    return body.replace(hole(PluginText.NAME), plugin) if plugin is not None else body


_STAMPED_BEGIN = _agents_file_stamp(plugin=NAME)
_SNIPPET_WRAPPER_LINE = re.compile(
    r"^\s*@(?:\$\(DEVPRO\)|\{\{quote\(source_directory\(\) / \"\.\.\" / \"devpro\.sh\"\)\}\}) (.*)$"
)


def _recipe_runs(snippet: str) -> dict[str, list[str]]:
    """Each recipe the snippet defines, with the wrapper command lines it runs, in order."""
    runs: dict[str, list[str]] = {}
    current = None
    for line in snippet.splitlines():
        if match := re.fullmatch(r"(devpro(?:-[a-z]+)*):", line):
            current = runs[match.group(1)] = []
        elif current is not None and (command := _SNIPPET_WRAPPER_LINE.match(line)):
            current.append(command.group(1))
    return runs


def _snippet_recipe_runs() -> dict[str, list[str]]:
    """The recipes the shipped devpro snippet set carries and the wrapper command lines each runs, read
    from the just snippet: the make snippet defines the same names, so a runner whose list drifted from
    the other's is caught by comparing the two snippet files."""
    snippets = {
        name: (PACKAGE_ROOT / "runner-snippets" / name).read_text(encoding="utf-8")
        for name in ("devpro.just", "devpro.mk")
    }
    runs = {name: _recipe_runs(text) for name, text in snippets.items()}
    assert runs["devpro.just"] == runs["devpro.mk"]
    return runs["devpro.just"]


def _block(harness: Harness) -> list[str]:
    lines, begin, end = marker_span(render_agents_file(harness, PLAIN, scope="x"), where="render")
    return lines[begin : end + 1]


def _files(root: Path) -> dict[str, bytes]:
    """Every file under `root` with its bytes."""
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def _plant_file(path: Path, text: str = "planted\n") -> Path:
    """`path` written holding `text`, its parents created."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def _staged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Callable[[Path, tuple[tuple[str, str], ...]], Path]:
    """A source tree a run stages from, in place of this checkout: `devpro.install`'s and
    `devpro.install_target`'s `PACKAGE_ROOT` each bound it, both modules having imported the name from
    `devpro.install_base`, so a tree given to one alone leaves the other reading this checkout."""

    def stage(relative: Path, files: tuple[tuple[str, str], ...]) -> Path:
        root = relative.resolve()
        for path, text in files:
            _plant_file(root / path, text)
        for module in ("devpro.install", "devpro.install_target"):
            monkeypatch.setattr(f"{module}.PACKAGE_ROOT", root)
        return root

    return stage


def _install(directory: Path, harness: Harness = OPENCODE, uncommitted: tuple[str, ...] = ()) -> None:
    install_agents_file(directory, harness, PLAIN, uncommitted=lambda: uncommitted)


def _stamped(stamp: str, *, content: list[str]) -> str:
    """A file holding the rendered block with its begin line stamped `stamp` in place of this version
    and `content` between the marker lines."""
    begin, *_, end = _block(OPENCODE)
    return "\n".join(["mine", begin.replace(__version__, stamp), *content, end, ""])


_CURRENT = _block(OPENCODE)[1:-1]


def _non_utf8(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_bytes(b"\xff\xfe" + f"{_BEGIN}\n{_END}\n".encode())


def _redirect_chain(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("@one.md\n", encoding="utf-8")
    (tmp_path / "one.md").write_text("@two.md\n", encoding="utf-8")


def _redirect_outside(tmp_path: Path) -> None:
    (tmp_path / "inner").mkdir()
    (tmp_path / "inner" / "AGENTS.md").write_text("@../outside.md\n", encoding="utf-8")


_CLAUDE_RENDER = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
_KBASE_CLAUDE_RENDER = dataclasses.replace(_CLAUDE_RENDER, plugin=WITH_KBASE)
_MAGE_RENDER = Render(harness=MAGE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
_KBASE_MAGE_RENDER = dataclasses.replace(_MAGE_RENDER, plugin=WITH_KBASE)
_OPENCODE_RENDER = build_render(
    harness="opencode",
    components="",
    family="claude",
    supply=MapSupply(
        category_map=dict.fromkeys(CATEGORIES, "inherit"),
        supplier="--config-file devtools/reference-maps/opencode.toml, table '[opencode.model-map]'",
    ),
)
_KBASE_OPENCODE_RENDER = dataclasses.replace(_OPENCODE_RENDER, plugin=WITH_KBASE)
_NEW_BANNER = "---\n# !GENERATED! from devpro/definitions/gone.py — x\n# !TUNING! y\n---\n\nbody\n"


def _definition_install(
    root: Path,
    ctx: Render = _CLAUDE_RENDER,
    *,
    project_root: Path | None = None,
) -> None:
    """`install` of `ctx`, its selection included, into the harness directory `root`."""
    install(root, ctx, verbose=False, project_root=project_root, uncommitted=_committed)


def _committed() -> tuple[str, ...]:
    """No uncommitted sources, so a mage install's agents file does not turn on this tree's git state."""
    return ()


_TS_GUARDRAIL = "guardrail.ts"
_GUARDRAIL = "hooks/guardrail.pl"
_REMINDER = "hooks/state-table-reminder.sh"
_SETTINGS = ".claude/settings.json"
_CLAUDE_PLUGIN_RELPATH = f".claude/{CLAUDE.bound(NAME).plugin_dir}"
_DEVPRO_SET_LINE = f"import? '{_CLAUDE_PLUGIN_RELPATH}/tools/runner-snippets/devpro.just'"
_PROFILER = "profiler"
_PROFILER_EVENTS = (
    "PostToolUse",
    "PostToolUseFailure",
    "PreCompact",
    "PostCompact",
    "SessionStart",
    "SubagentStop",
)
_PROFILER_COMMAND = '"${CLAUDE_PLUGIN_ROOT}/skills/devpro/tools/devpro.sh" profiler capture claude'
_PROFILER_SKILL = "skills/profiler/SKILL.md"


def _claude_plugin(harness_dir: Path) -> Path:
    return harness_dir / CLAUDE.bound(NAME).plugin_dir


def _opencode_plugin(harness_dir: Path) -> Path:
    return harness_dir / OPENCODE.bound(NAME).plugin_dir


_REGISTRATION = "hooks/hooks.json"
_GUARDRAIL_MATCHER = "Bash|Read|Write|Edit|NotebookEdit|Grep|Glob"
_DEVELOPMENT_SCRIPTS = "skills/development/scripts/cold-read.sh"
_DEVPRO_PACKAGE = "tools/runner-snippets/devpro.just"
_KBASE_PACKAGE = "skills/kbase/kb-tools/runner-snippets/kb.just"
_OPENCODE_SETTINGS_NAMES = {"opencode.json", "opencode.jsonc"}


def _delivers_the_kbase_server(project: Path, root: Path) -> bool:
    """Whether an install delivered the `kbase` MCP server: in a `.mcp.json` anywhere in the project,
    or as a record of ROOT's registry."""
    registry = root / "registry.json"
    if registry.is_file() and json.loads(registry.read_text(encoding="utf-8"))["mcp"]:
        return True
    return any(path.name == ".mcp.json" for path in project.rglob("*"))


_MAINTAINER_VERBS = ("dev-render", "render-agents-file", "harness")


def _renders_the_kbase_skill(out: Path) -> bool:
    return (out / "skills/kbase/SKILL.md").is_file()


def _installs_the_kbase_skill(out: Path) -> bool:
    return (_claude_plugin(out / ".claude") / "skills/kbase/SKILL.md").is_file()


_MAGE_MANIFEST = ".claude-plugin/plugin.json"


@pytest.fixture
def _umask_002() -> Iterator[None]:
    """The umask a group-writable project installs under, restored so no other case's mode assertions
    see it."""
    previous = os.umask(0o002)
    try:
        yield
    finally:
        os.umask(previous)


def _plant(path: Path, text: str = "planted\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


_COLD_READ_SOURCE = PACKAGE_ROOT / "development-tools" / "cold-read.sh"


def _installed_cold_reads(base: Path) -> list[Path]:
    return sorted(base.rglob("skills/development/scripts/cold-read.sh"))


_NO_DEVPRO_PATH = "/usr/bin:/bin"


def _run_wrapper(wrapper: Path, *, path: str, home: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(wrapper), "--version"],
        env={"PATH": path, "HOME": str(home)},
        cwd=home,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        stdin=subprocess.DEVNULL,
        timeout=60,
    )


_RESOURCE_HEADER = "// !INSTALLED! from elsewhere — request changes from the devpro project\n"


def _rendered(ctx: Render, relative: str) -> str:
    """The text the renderer writes at `relative`, so a planted file that must pass is rendered output."""
    return dict(render_all(ctx))[PurePosixPath(relative)]


def _claude_root(project: Path) -> Path:
    """`project/.claude`, created."""
    root = project / ".claude"
    root.mkdir()
    return root


def _run_registered_hook(
    plugin: Path, *, project: Path, event: str, matcher: str, payload: dict[str, object]
) -> subprocess.CompletedProcess:
    """The one command the registration's `event` entry matched on `matcher` carries, run under `sh -c`
    with `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PROJECT_DIR` set and `payload` on stdin."""
    registration = json.loads((plugin / _REGISTRATION).read_text(encoding="utf-8"))
    [entry] = [element for element in registration["hooks"][event] if element["matcher"] == matcher]
    [hook] = entry["hooks"]
    return subprocess.run(
        ["sh", "-c", hook["command"]],
        input=json.dumps(payload),
        capture_output=True,
        encoding="utf-8",
        env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(plugin), "CLAUDE_PROJECT_DIR": str(project)},
        check=False,
    )


def _guardrail_result(plugin: Path, *, project: Path, command: str) -> subprocess.CompletedProcess:
    """The guardrail's entry, run on a Bash call for `command`."""
    return _run_registered_hook(
        plugin,
        project=project,
        event="PreToolUse",
        matcher=_GUARDRAIL_MATCHER,
        payload={"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(project)},
    )


_UP_TO_DATE = "up to date: "


def _state(base: Path) -> dict[str, tuple[bytes, int, int]]:
    """Every directory and file below `base`: its bytes (a directory's none), modification time and
    mode — what "touched nothing" compares."""
    state = {}
    for directory, subdirs, names in os.walk(base):
        for name in [*subdirs, *names]:
            path = Path(directory, name)
            info = path.stat()
            data = path.read_bytes() if path.is_file() else b""
            state[path.relative_to(base).as_posix()] = (data, info.st_mtime_ns, info.st_mode)
    return state


def _directories(root: Path) -> set[str]:
    """Every directory below `root`, each shown with the trailing `/` a dry run gives it."""
    return {
        f"{Path(directory, name).relative_to(root).as_posix()}/"
        for directory, subdirs, _ in os.walk(root)
        for name in subdirs
    }


def _dry_run_groups(out: str) -> dict[str, set[str]]:
    """The paths a dry run printed under each of its `created`, `changed` and `removed` headings."""
    groups: dict[str, set[str]] = {}
    current: set[str] | None = None
    for line in out.splitlines():
        if line in ("created:", "changed:", "removed:"):
            current = groups.setdefault(line[:-1], set())
        elif line.startswith("  ") and current is not None:
            current.add(line.strip())
        else:
            current = None
    return groups


@pytest.fixture
def _no_uncommitted(monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI's commit-state check standing down, so an agents-file write does not turn on this tree."""
    monkeypatch.setattr("devpro.install.uncommitted_sources", _committed)


def _fail_if_called() -> tuple[str, ...]:
    pytest.fail("the commit state was read")


@pytest.fixture
def _uncommitted_never_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI's commit-state check failing the test if it runs: an install that writes no agents file
    has no reason to read it."""
    monkeypatch.setattr("devpro.install.uncommitted_sources", _fail_if_called)


def _assert_dry_run_predicts(argv: list[str], *, project: Path, capsys) -> dict[str, set[str]]:
    """Run `argv` with `--dry-run`, then for real: the dry run touches nothing under `project`, and the
    paths it prints are exactly those the real run then creates, changes and removes — the directories
    it removes among them. Its groups."""
    files, directories, state = _files(project), _directories(project), _state(project)
    capsys.readouterr()
    main([*argv, "--dry-run"])
    groups = _dry_run_groups(capsys.readouterr().out)
    assert _state(project) == state
    main(argv)
    assert groups == _changed_since(files, directories, project=project)
    return groups


def _changed_since(files: dict[str, bytes], directories: set[str], *, project: Path) -> dict[str, set[str]]:
    """What changed under `project` since it held `files` and `directories`, as a dry run groups it,
    each group present only where it holds a path. A directory created and left holding nothing is a
    created path, shown with the trailing `/` a dry run gives it; one created to hold what the run
    wrote is those files' own, and the dry run names the files."""
    after = _files(project)
    actual = {
        "created": (set(after) - set(files)) | _empty_directories(project, also=directories),
        "changed": {path for path in set(after) & set(files) if after[path] != files[path]},
        "removed": (set(files) - set(after)) | (directories - _directories(project)),
    }
    return {group: paths for group, paths in actual.items() if paths}


def _empty_directories(project: Path, *, also: set[str]) -> set[str]:
    """Every directory under `project` the project did not hold in `also` and that holds no file, each
    with the trailing `/` a dry run gives it."""
    return {path for path in _directories(project) - also if not any((project / path).iterdir())}


def _kb_install_with_a_runner_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[list[str], Path]:
    """The settings file and the runner include line are in play: each is already what the second run
    writes."""
    project = tmp_path / "project"
    project.mkdir()
    (project / "justfile").write_text("# mine\n", encoding="utf-8")
    return ["install", str(project), "--components=kbase", "--harness=claude"], project


def _agents_file_in_a_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[list[str], Path]:
    """An agents file holding an earlier block, so the first run also writes the backup."""
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text(f"mine\n{_BEGIN}\nold\n{_END}\n", encoding="utf-8")
    return ["install-agents-file", str(project), "--harness=claude"], project


def _mage_below_its_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[list[str], Path]:
    """The plugin's own `.mcp.json` and agents file at ROOT."""
    project = tmp_path / "project"
    project.mkdir()
    return ["install", str(project), "--components=kbase", "--harness=mage", "--subdir=plugins/devpro"], project


def _user_level_plugin(home: Path) -> Path:
    """A user-level claude plugin installed under `home`: its manifest's path."""
    root = home / ".claude"
    root.mkdir(parents=True)
    install(root, _CLAUDE_RENDER, verbose=False, project_root=home, uncommitted=_committed)
    return _claude_plugin(root) / ".claude-plugin/plugin.json"


_HARNESS_NAMED = {"claude": CLAUDE, "opencode": OPENCODE}


def _global_agents_file(home: Path, harness: Harness) -> Path:
    return home / Path(harness.user_harness_dir).relative_to("~") / harness.agents_file


def _dirty() -> tuple[str, ...]:
    return ("M devpro/x.py",)


def _project_with_a_copy(tmp_path: Path, *, native: str | None, own: str) -> Path:
    """A project whose AGENTS.md holds `own` and then a stale block, and whose CLAUDE.md, where `native` is
    given, holds it."""
    project = tmp_path / "project"
    _plant(project / "AGENTS.md", f"{own}{_BEGIN}\nold\n{_END}\n")
    if native is not None:
        _plant(project / "CLAUDE.md", native)
    return project


def _run_outcome(argv: list[str], capsys, *, planted: Path) -> tuple[object, list[str], dict[str, set[str]]]:
    """What a run of `argv` does about `planted`: its exit code, the stderr lines naming it, and the
    paths a dry run prints."""
    capsys.readouterr()
    try:
        main(argv)
        code: object = 0
    except SystemExit as exc:
        code = exc.code
    printed = capsys.readouterr()
    return code, [line for line in printed.err.splitlines() if str(planted) in line], _dry_run_groups(printed.out)
