"""agent/skill/command/document forms"""

import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

import pytest

from devpro.context import Render
from devpro.definition import Definition
from devpro.errors import InputError
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.harness import HarnessFile, ShippedDefinition
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.loading import load
from devpro.render import agent_fields, filled_body, render_all, render_definition, render_skill_file, write_renders
from devpro.vocabulary import CATEGORIES, HarnessText, Kind
from tests.conftest import PLAIN

from .conftest import (
    _ALL_INHERIT,
    _COMMAND,
    _DOCUMENT,
    _OPENCODE_PERMISSIONS,
    _OPENCODE_RENDER,
    _PYTHON_CODER_DESCRIPTION,
    _SECURITY_REVIEWER_DESCRIPTION,
    _claude_frontmatter,
    _python_coder,
    _security_reviewer,
    _skill,
)


@pytest.mark.parametrize(
    "package, attribute",
    [("devpro.harnesses", "HARNESS"), ("devpro.families", "FAMILY")],
)
def test_each_instance_is_named_as_its_module_loads(package: str, attribute: str) -> None:
    loaded = load(package, attribute)
    assert loaded
    assert {key: instance.name for key, instance in loaded.items()} == {key: key for key in loaded}


def test_load_refuses_a_module_without_the_attribute() -> None:
    with pytest.raises(InputError, match="'devpro.harnesses.claude' defines no FAMILY"):
        load("devpro.harnesses", "FAMILY")


def test_claude_frontmatter_holds_the_field_order_and_spelling() -> None:
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    name, description, model, color, tools = _claude_frontmatter(agent_fields(_security_reviewer(), ctx))
    assert name == "name: security-reviewer"
    assert description == _SECURITY_REVIEWER_DESCRIPTION
    assert model.startswith("model: ")
    assert color.startswith("color: ")
    assert tools == "tools: Bash, Read, Grep, Glob, Write, Edit, WebSearch, WebFetch"


def test_an_unrestricted_agent_frontmatter_matches_the_pre_1_0_render() -> None:
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    name, description, model, color = _claude_frontmatter(agent_fields(_python_coder(), ctx))
    assert name == "name: python-coder"
    assert description == _PYTHON_CODER_DESCRIPTION
    assert model.startswith("model: ")
    assert color.startswith("color: ")


@pytest.mark.parametrize(
    "defn, category_map, expected",
    [
        (
            _security_reviewer(),
            _ALL_INHERIT,
            {
                "description": _security_reviewer().description,
                "mode": "subagent",
                "color": "#DC2626",
                "permission": _OPENCODE_PERMISSIONS,
            },
        ),
        (
            _python_coder(),
            dict.fromkeys(CATEGORIES, "omlx/Qwen3.8-Flash-Next"),
            {
                "description": "Python implementation specialist.",
                "mode": "subagent",
                "model": {"providerID": "omlx", "id": "Qwen3.8-Flash-Next"},
                "color": "#3776AB",
            },
        ),
        (_DOCUMENT, _ALL_INHERIT, {"mode": "subagent", "hidden": True}),
    ],
    ids=["restricted-inherit", "unrestricted-pinned", "document"],
)
def test_an_opencode_agent_record_carries_the_pre_1_0_frontmatter_values(
    defn: Definition, category_map: dict[str, str], expected: dict[str, object]
) -> None:
    """The registry record holds what opencode's frontmatter held before the plugin render: description,
    mode, the model split into provider and id where one renders, color, and a permission per governed key
    unless every tool is allowed. A document's record is a hidden subagent's."""
    ctx = Render(harness=OPENCODE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=category_map)
    shipped = ShippedDefinition(
        name=defn.name,
        reference=f"devpro-{defn.name}",
        kind=defn.kind,
        path=str(defn.output_path),
        description=None,
        agent=agent_fields(defn, ctx) if defn.kind is Kind.AGENT else None,
    )
    registry = ctx.harness.definition_form
    assert isinstance(registry, HarnessFile)
    [record] = json.loads(registry.text("devpro", (shipped,)))["agents"]
    assert record == {"id": f"devpro-{defn.name}", "file": str(defn.output_path), **expected}


def test_a_command_renders_its_banner_straight_into_a_body_naming_the_user_harness_dir() -> None:
    """A command carries no field lines, so its closing fence is the body's own first line: a blank
    line there opens the file with an empty paragraph. The body names the user harness directory the
    definition's placeholder stands for, filled as this harness spells it."""
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    lines = render_definition(_COMMAND, ctx, module="devpro.definitions.probe").split("\n")
    assert lines[0] == "---"
    assert lines[1].startswith("# !GENERATED! from devpro/definitions/probe.py — ")
    assert lines[2] == (
        "# !TUNING! family=claude category=none member=none category-map=stem-architect=inherit,"
        "stem-expert=inherit,stem-mechanical=inherit,comm-architect=inherit,comm-expert=inherit,"
        "comm-mechanical=inherit stock=stem-architect,stem-expert,stem-mechanical,comm-architect,"
        "comm-expert,comm-mechanical harness=claude"
    )
    assert lines[3] == "---"
    body = "\n".join(lines[4:])
    assert not body.startswith("\n"), "a blank line after the closing fence opens the file with an empty paragraph"
    assert body.strip(), "the command renders no body"
    assert CLAUDE.text(HarnessText.USER_HARNESS_DIR) in body
    assert not re.search(r"@!hrn-[a-z0-9-]+!@", body), body


def test_a_document_renders_no_field_of_its_own() -> None:
    """A document declares no frontmatter value, so between the fences stands the banner alone."""
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    lines = render_definition(_DOCUMENT, ctx, module="devpro.definitions.probe").split("\n")
    assert lines[0] == "---"
    assert lines[1].startswith("# !GENERATED! from devpro/definitions/probe.py — ")
    assert " category=none member=none category-map=" in lines[2]
    assert lines[3] == "---"


@pytest.mark.skipif(shutil.which("sed") is None, reason="extraction needs sed")
def test_every_rendered_definition_extracts_frontmatter_free(tmp_path: Path) -> None:
    """The definitions' own extraction command, run over every rendered file under agents/: it exits
    0, leaves no banner, and the frontmatter block plus what it printed is the file byte for byte."""
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    write_renders(tmp_path, render_all(ctx))
    rendered = sorted((tmp_path / "agents").rglob("*.md"))
    assert len(rendered) > 20
    for path in rendered:
        done = subprocess.run(["sed", "1,/^---$/d", str(path)], capture_output=True, text=True, check=False)
        assert done.returncode == 0, done.stderr
        assert "!GENERATED!" not in done.stdout, path
        text = path.read_text(encoding="utf-8")
        between = text.removeprefix("---\n").split("\n---\n", 1)[0]
        assert text == "---\n" + between + "\n---\n" + done.stdout, path


def test_a_skill_renders_a_directory_two_fields_and_a_comment_bannered_reference() -> None:
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    defn = _skill()
    assert defn.output_path == PurePosixPath("skills/probe/SKILL.md")
    assert defn.output_paths == (
        PurePosixPath("skills/probe/SKILL.md"),
        PurePosixPath("skills/probe/references/reading.md"),
    )
    lines = render_definition(defn, ctx, module="devpro.definitions.probe").split("\n")
    assert lines[0] == "---"
    assert lines[1].startswith("# !GENERATED! from devpro/definitions/probe.py — ")
    assert " category=none member=none " in lines[2]
    assert lines[3:6] == [
        "name: probe",
        'description: "Use when the user asks about the knowledge base."',
        "---",
    ]
    assert lines[6:] == ["", "Route the request to the reference it asks for.", ""]
    reference = render_skill_file(defn, defn.files[0], ctx, module="devpro.definitions.probe").split("\n")
    assert reference[0].startswith("<!-- !GENERATED! from devpro/definitions/probe.py — ")
    assert reference[0].endswith(" -->")
    assert reference[1].startswith("<!-- !TUNING! family=")
    assert reference[1].endswith(" -->")
    assert reference[2:] == ["", "Read a claim before you cite it.", ""]


@pytest.mark.parametrize(
    "defn",
    [_security_reviewer(), _DOCUMENT, _COMMAND, _skill()],
    ids=lambda defn: defn.kind.value,
)
def test_an_opencode_definition_opens_with_the_comment_banner_and_no_frontmatter(defn: Definition) -> None:
    """Every kind opens with the two banner lines as HTML comments and the blank line after them, and
    what follows is the filled body entire: the registry, not the file, carries its metadata."""
    lines = render_definition(defn, _OPENCODE_RENDER, module="devpro.definitions.probe").split("\n")
    assert lines[0].startswith("<!-- !GENERATED! from devpro/definitions/probe.py — ")
    assert lines[0].endswith(" -->")
    assert lines[1].startswith("<!-- !TUNING! family=") and lines[1].endswith(" -->")
    assert lines[2] == ""
    assert "\n".join(lines[3:]) == filled_body(defn, _OPENCODE_RENDER) + "\n"


def test_every_opencode_output_but_the_registry_holds_the_comment_banner_and_then_only_its_body() -> None:
    """Over the whole render, each file opens with the two comment banner lines and a blank line, and
    no frontmatter fence or second banner follows; the registry is the one other output."""
    renders = dict(render_all(_OPENCODE_RENDER))
    assert renders.pop(PurePosixPath("registry.json"))
    assert len(renders) > 20
    for path, text in renders.items():
        generated, tuning, blank, body = text.split("\n", 3)
        assert generated.startswith("<!-- !GENERATED! ") and tuning.startswith("<!-- !TUNING! "), path
        assert blank == "" and not body.startswith("---\n") and "<!-- !GENERATED!" not in body, path
