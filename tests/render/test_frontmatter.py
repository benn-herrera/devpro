"""agent/skill/command/document forms"""

import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

import pytest

from devpro.context import Render, map_spec
from devpro.definition import Definition
from devpro.errors import InputError
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.harness import HarnessFile, ShippedDefinition
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.mage import HARNESS as MAGE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.loading import load
from devpro.render import (
    agent_fields,
    filled_body,
    render_all,
    render_definition,
    render_skill_file,
    write_renders,
)
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

# One render of each harness, so the banner and tuning-table cases cover every carrier.
_RENDERS = (
    Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories)),
    Render(harness=MAGE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories)),
    _OPENCODE_RENDER,
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
    assert lines[2] == "---"
    body = "\n".join(lines[3:])
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
    assert lines[2] == "---"


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
    assert lines[2:5] == [
        "name: probe",
        'description: "Use when the user asks about the knowledge base."',
        "---",
    ]
    assert lines[5:] == ["", "Route the request to the reference it asks for.", ""]
    reference = render_skill_file(defn, defn.files[0], ctx, module="devpro.definitions.probe").split("\n")
    assert reference[0].startswith("<!-- !GENERATED! from devpro/definitions/probe.py — ")
    assert reference[0].endswith(" -->")
    assert reference[1:] == ["", "Read a claim before you cite it.", ""]


@pytest.mark.parametrize(
    "defn",
    [_security_reviewer(), _DOCUMENT, _COMMAND, _skill()],
    ids=lambda defn: defn.kind.value,
)
def test_an_opencode_definition_opens_with_the_comment_banner_and_no_frontmatter(defn: Definition) -> None:
    """Every kind opens with the banner line as an HTML comment and the blank line after it, and what
    follows is the filled body entire: the registry, not the file, carries its metadata."""
    lines = render_definition(defn, _OPENCODE_RENDER, module="devpro.definitions.probe").split("\n")
    assert lines[0].startswith("<!-- !GENERATED! from devpro/definitions/probe.py — ")
    assert lines[0].endswith(" -->")
    assert lines[1] == ""
    assert "\n".join(lines[2:]) == filled_body(defn, _OPENCODE_RENDER) + "\n"


def test_every_opencode_output_but_the_registry_holds_the_comment_banner_and_then_only_its_body() -> None:
    """Over the whole render, each definition's file opens with the comment banner line and a blank line,
    and no second banner or frontmatter fence follows; the registry is the one other output, a file
    carrying its own ownership marker rather than a banner."""
    renders = dict(render_all(_OPENCODE_RENDER))
    registry = renders.pop(PurePosixPath("registry.json"))
    assert "!GENERATED!" not in registry
    assert len(renders) > 20
    for path, text in renders.items():
        generated, blank, body = text.split("\n", 2)
        assert generated.startswith("<!-- !GENERATED! ") and generated.endswith(" -->"), path
        assert blank == "" and not body.startswith("---\n"), path
        assert not body.startswith("<!--"), path


def test_no_rendered_definition_carries_the_tuning_data() -> None:
    """The tuning data rides on no rendered file: neither the `!TUNING!` line nor the values it spelled
    — the family, the effective category map, the definition's category and member, the harness — stand
    in any definition's text; the tuning table, one per install, is their only carrier."""
    for ctx in _RENDERS:
        for path, text in render_all(ctx):
            assert "!TUNING!" not in text, path
            assert f" category-map={map_spec(ctx.category_map)}" not in text, path
            assert f" member={ctx.family.categories[CATEGORIES[0]]}" not in text, path
