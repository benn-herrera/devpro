"""Opencode's plugin entry, `index.ts`, run under `bun` against a stub plugin context over a real opencode
install of `kbase`, whose registry gains a command record, a model and a permission map: what it
registers is what the registry lists, with each body's banner stripped; an edited body and a dropped record take effect on the
reload its watcher triggers; a command reads its body when it runs; and its cleanup closes the watcher.
A project whose root holds a plan file or the diced `ACTIVE_PLAN/` tree has the
plan-state reminder injected into the parent session when a subagent call completes and when that
subagent's session goes idle with nothing running on it; a failed call, a session still holding
background work, a session with no parent and a project holding only a design inject nothing. The
two resources inject one sentence, byte for byte. A
user-level install, which ships no guardrail beside the entry, registers the same way, and with no
gate path at the project root it injects no reminder. A missing `bun` fails rather than skips, as in
`tests/test_guardrail.py`.
"""

import functools
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from devpro import cli
from devpro.components import NAME
from devpro.context import DEFAULT_FAMILY, build_render
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.render import filled_body, render_definition, rendered_definitions
from tests.test_guardrail import _run_reminder

_RUNNER = Path(__file__).parent / "opencode_entry_runner.ts"


@functools.cache
def _banner_lines() -> int:
    """How many lines the opencode render writes above a definition's body."""
    ctx = build_render(harness=OPENCODE.name, components="kbase", family=DEFAULT_FAMILY)
    module, defn = rendered_definitions(ctx)[0]
    text = render_definition(defn, ctx, module=module)
    return text[: len(text) - len(filled_body(defn, ctx) + "\n")].count("\n")


def _banner(text: str) -> str:
    return "".join(text.splitlines(keepends=True)[: _banner_lines()])


def _body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text[len(_banner(text)) :]


def _installed(target: Path, *, harness_dir: Path) -> tuple[Path, dict]:
    """A real opencode install with the kbase component on into `target`, whose harness directory is
    `harness_dir`: its install directory and its registry."""
    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the opencode entry cannot run without it")
    cli.main(["install", str(target), "--components=kbase", "--harness=opencode"])
    plugin = harness_dir / OPENCODE.bound(NAME).plugin_dir
    return plugin, json.loads((plugin / "registry.json").read_text(encoding="utf-8"))


def _add_probe_command(plugin: Path, registry: dict, *, banner: str) -> Path:
    """Plant a command body and its record in `registry`, returning the body's path."""
    command_path = plugin / "commands/probe.md"
    command_path.parent.mkdir()
    command_path.write_text(f"{banner}Old command.\n", encoding="utf-8")
    registry["commands"] = [{"id": "kbase-probe", "file": "commands/probe.md", "description": "A probe"}]
    return command_path


def _probe_entry(target: Path) -> tuple[Path, Path, str]:
    """An install of kbase into `target` with the probe command planted and its registry written back:
    the plugin directory, the command body's path, and the banner the entry's files carry."""
    plugin, registry = _installed(target, harness_dir=target / OPENCODE.project_harness_dir)
    banner = _banner((plugin / registry["agents"][0]["file"]).read_text(encoding="utf-8"))
    command_path = _add_probe_command(plugin, registry, banner=banner)
    (plugin / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
    return plugin, command_path, banner


def _run_entry(plugin: Path, *, directory: Path, project: Path, writes: list[dict], command: dict) -> dict:
    """The runner's output for the entry installed in `plugin`, for a session opened at `directory` in
    the project rooted at `project`."""
    done = subprocess.run(
        ["bun", str(_RUNNER)],
        input=json.dumps(
            {
                "entry": str(plugin / OPENCODE.entry_resource),
                "directory": str(directory),
                "project": str(project),
                "writes": writes,
                "command": command,
            }
        ),
        capture_output=True,
        encoding="utf-8",
        # A watcher the entry's cleanup left open keeps the runner from exiting.
        timeout=30,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def test_the_opencode_entry_registers_and_reloads_what_the_plugin_holds(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    plugin, registry = _installed(project, harness_dir=project / OPENCODE.project_harness_dir)
    # The plan-state reminder's gate: the reminder fires where a plan file stands at the project root,
    # here read from a session opened below it.
    (project / "ACTIVE_PLAN.md").write_text("# Active plan\n", encoding="utf-8")
    opened = project / "nested"
    opened.mkdir()
    registry_path = plugin / "registry.json"
    edited, removed, *_ = registry["agents"]
    banner = _banner((plugin / edited["file"]).read_text(encoding="utf-8"))

    command_path = _add_probe_command(plugin, registry, banner=banner)
    edited["model"] = {"providerID": "omlx", "id": "Qwen3.8-Flash-Next"}
    edited["permission"] = {"read": "allow", "shell": "deny", "subagent": "deny"}
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    without_removed = {**registry, "agents": [a for a in registry["agents"] if a["id"] != removed["id"]]}
    bodies = {record["id"]: _body(plugin / record["file"]) for record in registry["agents"] + registry["skills"]}

    out = _run_entry(
        plugin,
        directory=opened,
        project=project,
        writes=[
            {"path": str(plugin / edited["file"]), "text": f"{banner}New body.\n"},
            {"path": str(registry_path), "text": json.dumps(without_removed)},
        ],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
    )
    first, after_edit, after_removal = out["states"]

    assert out["id"] == NAME
    # Registration order follows the code: the guardrail's `execute.before`, the entry's reminder
    # `execute.after`, then the capture's pair; and the entry's idle hook, then the capture's.
    assert out["hooks"] == ["execute.before", "execute.before", "execute.after", "execute.after"]
    assert out["sessionHooks"] == ["experimental.idle", "experimental.idle"]
    assert set(first["agents"]) == {a["id"] for a in registry["agents"]}
    assert set(first["skills"]) == {s["id"] for s in registry["skills"]}
    assert first["commands"] == {"kbase-probe": "A probe"}
    assert first["mcp"] == registry["mcp"] != {}
    for record in registry["agents"]:
        assert first["agents"][record["id"]]["system"] == bodies[record["id"]]
    for record in registry["skills"]:
        registered = first["skills"][record["id"]]
        assert registered["content"] == bodies[record["id"]]
        assert registered["path"] == str(plugin / record["file"])
    assert first["agents"][edited["id"]]["model"] == {"providerID": "omlx", "id": "Qwen3.8-Flash-Next"}
    assert first["agents"][edited["id"]]["permissions"][-3:] == [
        {"action": "read", "resource": "*", "effect": "allow"},
        {"action": "shell", "resource": "*", "effect": "deny"},
        {"action": "subagent", "resource": "*", "effect": "deny"},
    ]

    assert after_edit["agents"][edited["id"]]["system"] == "New body.\n"
    assert set(after_removal["agents"]) == set(first["agents"]) - {removed["id"]}
    assert out["prompts"] == ["Old command.\n\ngo", "New command.\n\ngo"]
    # The gate holds, so the subagent's dispatch and its completion each inject once into the parent
    # session; the runner also fires a call that is not a subagent, a failed subagent call, a session
    # with no parent and a session still holding running work, and none of them injects.
    assert [(injected["on"], injected["sessionID"]) for injected in out["synthetics"]] == [
        ("execute.after", "ses_parent"),
        ("experimental.idle", "ses_parent"),
    ]


def test_a_user_level_opencode_entry_with_no_guardrail_beside_it_injects_no_reminder(tmp_path: Path) -> None:
    OPENCODE.user_dir.mkdir(parents=True)
    plugin, registry = _installed(OPENCODE.user_dir, harness_dir=OPENCODE.user_dir)
    assert not (plugin / "guardrail.ts").exists()
    banner = _banner((plugin / registry["agents"][0]["file"]).read_text(encoding="utf-8"))
    command_path = _add_probe_command(plugin, registry, banner=banner)
    (plugin / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
    )

    # The user-level install copies no capture beside the entry, so it registers the reminder's pair.
    assert out["hooks"] == ["execute.after"]
    assert out["sessionHooks"] == ["experimental.idle"]
    assert out["synthetics"] == []
    (registered,) = out["states"]
    assert set(registered["agents"]) == {a["id"] for a in registry["agents"]}
    assert set(registered["skills"]) == {s["id"] for s in registry["skills"]}
    assert registered["commands"] == {"kbase-probe": "A probe"}
    assert registered["mcp"] == registry["mcp"] != {}


def test_the_gate_is_the_plan_file_or_tree_and_silent_for_a_design_or_nothing(tmp_path: Path) -> None:
    """The entry's gate over one project and its four rows: a plan file or the diced `ACTIVE_PLAN/`
    tree at the root injects the parent (here the session opened below it), a design alone or nothing
    injects nothing. The design row is the differential — the same project that injected with the plan
    file stands silent with only the design — which an always-off gate, and one that read a directory
    named `ACTIVE_PLAN.md/` as a plan, would each fail to pin."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, command_path, banner = _probe_entry(project)
    opened = project / "nested"
    opened.mkdir()

    def run() -> dict:
        return _run_entry(
            plugin,
            directory=opened,
            project=project,
            writes=[],
            command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
        )

    def injected(out: dict) -> list[tuple[str, str]]:
        return [(i["on"], i["sessionID"]) for i in out["synthetics"]]

    gate = [("execute.after", "ses_parent"), ("experimental.idle", "ses_parent")]

    (project / "ACTIVE_PLAN.md").write_text("# Active plan\n", encoding="utf-8")
    assert injected(run()) == gate
    (project / "ACTIVE_PLAN.md").unlink()

    (project / "ACTIVE_DESIGN.md").write_text("# Active design\n", encoding="utf-8")
    assert injected(run()) == []
    (project / "ACTIVE_DESIGN.md").unlink()

    (project / "ACTIVE_PLAN").mkdir()
    assert injected(run()) == gate
    (project / "ACTIVE_PLAN").rmdir()

    assert injected(run()) == []


def test_both_harnesses_inject_one_sentence(tmp_path: Path) -> None:
    """The entry's injection is byte for byte the sentence claude's reminder script emits: one table,
    one rule at one strength, held to it here rather than by a reader comparing the two resources."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, command_path, banner = _probe_entry(project)
    (project / "ACTIVE_PLAN.md").write_text("# Active plan\n", encoding="utf-8")

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
    )
    claude = _run_reminder(json.dumps({"hook_event_name": "PostToolUse", "cwd": str(project)}), project_dir=project)
    assert claude.returncode == 0, claude.stderr
    sentence = json.loads(claude.stdout)["hookSpecificOutput"]["additionalContext"]

    assert {injected["text"] for injected in out["synthetics"]} == {sentence}
