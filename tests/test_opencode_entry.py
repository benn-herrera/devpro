"""Opencode's plugin entry, `index.ts`, run under `bun` against a stub plugin context over a real opencode
install of `kbase`, whose registry gains a command record, a model and a permission map: what it
registers is what the registry lists, with each body's banner stripped; an edited body and a dropped record take effect on the
reload its watcher triggers; a command reads its body when it runs; and its cleanup closes the watcher.
A record's model is written onto the agent the transform edits, as the object the record states, and
onto no other. A project whose root holds a plan file or the diced `ACTIVE_PLAN/` tree has the
plan-state reminder injected into the parent session when a subagent call completes and when that
subagent's session goes idle with nothing running on it; a failed call, a session still holding
background work, a session with no parent and a project holding only a design inject nothing. The
two resources inject one sentence, byte for byte. A
user-level install copies the guardrail beside the entry, so the entry runs it there and registers the
same way, while with no capture beside it and no gate path at the project root it injects no reminder. A
missing `bun` fails rather than skips, as in `tests/test_guardrail.py`.
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


_SKILL = "devpro-development"


def _activation(name: str) -> list[dict]:
    """The messages a compaction request's context holds where the skill `name` was loaded: the run
    the host builds from a skill activation, a `skill` tool call and its `tool-result` carrying the
    skill's body under its `<skill_content name="…">` header."""
    return [
        {
            "role": "tool",
            "content": [
                {
                    "type": "tool-result",
                    "id": "call_skill",
                    "name": "skill",
                    "result": {
                        "type": "text",
                        "value": f'<skill_content name="{name}">\n# Skill: {name}\n</skill_content>',
                    },
                },
            ],
        }
    ]


def _run_entry(
    plugin: Path,
    *,
    directory: Path,
    project: Path,
    writes: list[dict],
    command: dict,
    compactions: tuple[list[dict], list[dict]] | None = None,
    prompts: list[dict] | None = None,
    skill_loads: list[dict] | None = None,
) -> dict:
    """The runner's output for the entry installed in `plugin`, for a session opened at `directory` in
    the project rooted at `project`, for the two compactions of the primary session's context the
    runner fires at its end, each handed the messages it held — the skill's activation both times
    unless `compactions` states otherwise — and for the prompts the runner admits: the one after each
    compaction, on the primary session, carrying no skill of its own unless `prompts` names them,
    then each remaining prompt of `prompts` in the order given. Beyond the compactions, the runner
    fires a compaction of a session whose context holds only the project's Agents file, each of
    `skill_loads`' bodies appended to it as plain text."""
    if compactions is None:
        compactions = (_activation(_SKILL), _activation(_SKILL))
    done = subprocess.run(
        ["bun", str(_RUNNER)],
        input=json.dumps(
            {
                "entry": str(plugin / OPENCODE.entry_resource),
                "directory": str(directory),
                "project": str(project),
                "writes": writes,
                "command": command,
                "compactions": [{"sessionID": "ses_primary", "messages": messages} for messages in compactions],
                "prompts": prompts or [{"sessionID": "ses_primary", "skills": []} for _ in compactions],
                "skillLoads": skill_loads,
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
    # `execute.after`, then the capture's pair. The capture's setup runs before the entry's own
    # registrations, so its `model.request` and its idle hook precede the entry's idle and the
    # skill's reload, whose prompt hook stands beside its compaction hook.
    assert out["hooks"] == ["execute.before", "execute.before", "execute.after", "execute.after"]
    assert out["sessionHooks"] == [
        "model.request",
        "experimental.idle",
        "experimental.idle",
        "prompt",
        "compaction",
    ]
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
    # with no parent and a session still holding running work, and none of them injects. The record's
    # two compactions carry the skill's activation, so the reload attaches the skill at each prompt
    # after them, and the project's Agents file names the skill with no activation beside it, so the
    # false positive's session attaches nothing: three attachments, not one. Neither compaction idle
    # is the reminder's: its two records are the gate's own.
    assert [(injected["on"], injected["sessionID"]) for injected in out["synthetics"]] == [
        ("execute.after", "ses_parent"),
        ("experimental.idle", "ses_parent"),
    ]


def test_a_record_model_is_the_one_the_transform_writes(tmp_path: Path) -> None:
    """The agents store carries each record's model, as the object the record states, for the agents
    the registry configures one for and for no other: the transform's model write is what the host
    reads a plugin agent's model from. The two rows are the differential — a write that served every
    agent one record's model, or none, each fails it."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, registry = _installed(project, harness_dir=project / OPENCODE.project_harness_dir)
    configured, unconfigured, *_ = registry["agents"]
    banner = _banner((plugin / configured["file"]).read_text(encoding="utf-8"))
    command_path = _add_probe_command(plugin, registry, banner=banner)
    configured["model"] = {"providerID": "omlx", "id": "Qwen3.8-Flash-Next"}
    (plugin / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
    assert "model" not in unconfigured

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
    )

    (registered,) = out["states"]
    assert registered["agents"][configured["id"]]["model"] == configured["model"]
    assert "model" not in registered["agents"][unconfigured["id"]]


def test_a_user_level_opencode_entry_runs_the_guardrail_beside_it_and_injects_no_reminder(
    tmp_path: Path,
) -> None:
    OPENCODE.user_dir.mkdir(parents=True)
    plugin, registry = _installed(OPENCODE.user_dir, harness_dir=OPENCODE.user_dir)
    # A user-level install copies the guardrail resource beside the entry, and the entry runs it there.
    assert (plugin / "guardrail.ts").exists()
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

    # The capture, which a user-level install does not copy, registers none of its own, so the
    # reminder's idle hook stands alone and the skill's reload registers its prompt and compaction
    # hooks; the project root holds no gate path, so no synthetic message is injected. The record's
    # own compactions carry the skill's activation and the skill is attached at each prompt after
    # them; the false positive's session holds the skill's name in no context at all (a user-level
    # install copies no agents file), so it attaches nothing.
    assert out["hooks"] == ["execute.before", "execute.after"]
    assert out["sessionHooks"] == ["experimental.idle", "prompt", "compaction"]
    assert out["synthetics"] == []
    assert out["attachments"] == [
        {"sessionID": "ses_primary", "skills": [_SKILL]},
        {"sessionID": "ses_primary", "skills": [_SKILL]},
        {"sessionID": "ses_the_agents_file_names_the_skill", "skills": []},
    ]
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
    one rule at one strength, held to it here rather than by a reader comparing the two resources. The
    compactions the runner fires carried the skill, and their reload rides the next prompt's skills
    rather than a message — nothing it carries can read as the reminder's, which is what this test
    weighs against claude's."""
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
        compactions=(_activation(_SKILL), _activation(_SKILL)),
    )
    claude = _run_reminder(json.dumps({"hook_event_name": "PostToolUse", "cwd": str(project)}), project_dir=project)
    assert claude.returncode == 0, claude.stderr
    sentence = json.loads(claude.stdout)["hookSpecificOutput"]["additionalContext"]

    assert {injected["text"] for injected in out["synthetics"]} == {sentence}


def test_the_agents_file_name_attaches_the_skill_where_no_activation_did(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a marker narrowed to the skill's kind alone — the
    host's request messages carry no skill-kind message (`.devpro-temp/b2-probe/README.md`), so a
    kind matcher would leave every session whose context really held the skill unmarked and never
    reload it. The marker is the skill's name in the compaction request's text, so a session whose
    context holds only the Agents file — the file every project carries names the skill — marks at
    its compaction and has the skill attached at the prompt after it, though no activation ever
    ran."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, command_path, banner = _probe_entry(project)
    registry = json.loads((plugin / "registry.json").read_text(encoding="utf-8"))
    skill_path = plugin / next(record["file"] for record in registry["skills"] if record["id"] == _SKILL)
    # The project's Agents file names no skill, so the skill's body is appended as its text would
    # land in a context the model never asked to load it into — the name, and no activation message.
    assert _SKILL not in (project / "AGENTS.md").read_text(encoding="utf-8")

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
        skill_loads=[{"name": _SKILL, "path": str(skill_path)}],
    )

    assert out["attachments"][-1] == {"sessionID": "ses_the_agents_file_names_the_skill", "skills": [_SKILL]}


def test_a_compacted_context_that_held_the_skill_attaches_it_to_the_next_prompt(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a prompt hook that attaches to a prompt of a
    session the marker never recorded, or to every prompt, the session continuing without the
    development process. A session whose context held the development skill's activation states the
    marker at the compaction, and the prompt admitted after it carries the development skill among
    its `skills` — the one skill, and no other where the prompt carried none — while a compaction
    whose context held no text at all attaches nothing at the prompt after it."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, command_path, banner = _probe_entry(project)

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
        compactions=(_activation(_SKILL), []),
    )

    assert out["attachments"][:2] == [
        {"sessionID": "ses_primary", "skills": [_SKILL]},
        {"sessionID": "ses_primary", "skills": []},
    ]


def test_a_compacted_context_that_held_no_skill_attaches_nothing(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is an attachment keyed to every prompt. A compaction
    of a context that held neither the skill's body nor its name marks no session, and the prompts
    after it carry what they carried: the skill is never forced on a session that never carried it."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, command_path, banner = _probe_entry(project)

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
        compactions=([], []),
    )

    assert out["attachments"][:2] == [
        {"sessionID": "ses_primary", "skills": []},
        {"sessionID": "ses_primary", "skills": []},
    ]
    assert out["synthetics"] == []


def test_a_second_compaction_attaches_again_while_the_marker_is_spent_by_one_prompt(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a marker that latches the first delivery and
    silences every later one — the session's second compaction would leave it running without the
    development process, though its context held the skill at it — or one that delivers again on
    every prompt, forcing the skill on an exchange that was not the compaction's. The same session
    compacts twice, its context holding the skill both times, and the prompt after each compaction
    attaches it; a second prompt after that attaches nothing, the marker having been spent by the
    first."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, command_path, banner = _probe_entry(project)

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
        compactions=(_activation(_SKILL), _activation(_SKILL)),
        prompts=[
            {"sessionID": "ses_primary", "skills": []},
            {"sessionID": "ses_primary", "skills": []},
            {"sessionID": "ses_primary", "skills": []},
        ],
    )

    assert [
        (attachment["sessionID"], attachment["skills"])
        for attachment in out["attachments"]
        if attachment["sessionID"] == "ses_primary"
    ] == [
        ("ses_primary", [_SKILL]),
        ("ses_primary", [_SKILL]),
        ("ses_primary", []),
    ]


def test_the_attachment_names_the_skill_the_domain_lists(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is an attachment whose id names no skill the domain
    lists: the host has nothing to activate, and refuses the prompt. The attachment's id is the skill
    domain's own entry for the development skill — the id the entry's transform registers — not a
    string the attachment invented, and the prompt's own attachment is kept beside it where the
    operator invoked another skill."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, command_path, banner = _probe_entry(project)
    registry = json.loads((plugin / "registry.json").read_text(encoding="utf-8"))
    listed = {record["id"] for record in registry["skills"]}

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
        compactions=(_activation(_SKILL), []),
        prompts=[{"sessionID": "ses_primary", "skills": ["kbase"]}, {"sessionID": "ses_primary", "skills": []}],
    )

    (registered,) = out["states"]
    assert set(registered["skills"]) == listed
    assert _SKILL in listed
    assert out["attachments"][:2] == [
        {"sessionID": "ses_primary", "skills": ["kbase", _SKILL]},
        {"sessionID": "ses_primary", "skills": []},
    ]
    assert [log for log in out["log"] if "no skill the plugin lists" in log] == []


def test_a_skill_the_domain_does_not_list_attaches_nothing_and_reports(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is an attachment appended after a failed lookup: the
    host has nothing to activate, and refuses the prompt. An install whose registry carries no
    development skill attaches nothing at the prompt after a compaction and says so on stderr,
    naming the skill."""
    project = tmp_path / "project"
    project.mkdir()
    plugin, command_path, banner = _probe_entry(project)
    registry = json.loads((plugin / "registry.json").read_text(encoding="utf-8"))
    assert any(record["id"] == "devpro-development" for record in registry["skills"])
    registry["skills"] = [record for record in registry["skills"] if record["id"] != "devpro-development"]
    (plugin / "registry.json").write_text(json.dumps(registry), encoding="utf-8")

    out = _run_entry(
        plugin,
        directory=project,
        project=project,
        writes=[],
        command={"name": "kbase-probe", "path": str(command_path), "text": f"{banner}New command.\n", "user": "go"},
        compactions=(_activation(_SKILL), []),
        prompts=[{"sessionID": "ses_primary", "skills": []}, {"sessionID": "ses_primary", "skills": []}],
    )

    assert _SKILL not in out["states"][0]["skills"]
    assert out["attachments"][:2] == [
        {"sessionID": "ses_primary", "skills": []},
        {"sessionID": "ses_primary", "skills": []},
    ]
    reports = [log for log in out["log"] if "nothing to activate" in log]
    assert len(reports) == 1
    assert "devpro-development" in reports[0]
