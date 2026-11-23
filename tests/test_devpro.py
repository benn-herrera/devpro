"""The devpro package's own logic, each case checked against values the renderer did not compute: the
map's grammar and the settings file that supplies one, the rendered model text, the three families'
pins, the CLI's Render refusals, the frontmatter of each kind — an agent's and a skill's against
literal lines of the pre-1.0 render, a command's and a document's as bare fixtures pinned to their
render's shape — every rendered definition extracting frontmatter-free, placeholder filling and
refusal, overlay resolution and stock, Definition refusals, the loader's refusal, the description's
one line and balanced code spans, the line cap, and the package's source invariants as walks of its
syntax trees.

The package is imported from the repository root, which `just test` puts on PYTHONPATH.
"""

from __future__ import annotations

import ast
import dataclasses
import importlib.util
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import types
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import pytest

import devpro
import devpro.clauses
from devpro.agents_file import is_marker_line
from devpro.cli import main
from devpro.components import Components
from devpro.context import MapSupply, Render, build_render, harnesses, parse_category_map, read_settings
from devpro.definition import Definition, SkillFile
from devpro.definitions import definitions_of, discover
from devpro.errors import InputError
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.family import Family, Overlay
from devpro.harness import AgentFields, FrontmatterForm, Harness, HarnessFile, ShippedDefinition
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.mage import HARNESS as MAGE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.install import INSTALL_SETTINGS
from devpro.loading import load
from devpro.render import (
    agent_fields,
    definitions,
    filled_body,
    filled_text,
    keyed_by_path,
    render_agents_file,
    render_all,
    render_definition,
    render_skill_file,
    write_renders,
)
from devpro.vocabulary import (
    ALL,
    CATEGORIES,
    AgentsFileText,
    Anchor,
    HarnessText,
    Kind,
    OptionalHarnessText,
    PluginText,
    Tool,
    TuningText,
    hole,
    optional_reference,
    reference,
)
from devtools import clause_join_sites, render_diff
from tests._structure import (
    ARGUMENT_RULE,
    ASSIGNMENT_RULE,
    BODY_RULE,
    CALL_RULE,
    DEFINITION_CALL_RULE,
    DEFINITION_TOP_RULE,
    FILES_RULE,
    FOLDER_KIND_RULE,
    FUNCTION_RULE,
    IMPORT_RULE,
    TEXT_TOP_RULE,
    ClauseRoot,
    body_roots,
    carried_clauses,
    check_source,
    check_structure,
    clause_graph,
    definition_paths,
    kbase_skill_output_paths,
    repeated_clause_reaches,
)
from tests.conftest import PLAIN, WITH_KBASE, settings_file

_ALL_INHERIT = dict.fromkeys(CATEGORIES, "inherit")
_SELECTIONS = (PLAIN, WITH_KBASE)
_PACKAGE = Path(devpro.__file__).parent
_SUPPLIER = "--config-file /home/me/.config/devpro/devpro.cfg, section '[claude-model-map]'"
"""A settings-file supply's provenance, as its section names it."""


@pytest.mark.parametrize(
    "spec, expected",
    [
        (
            "stem-architect=a,stem-expert=b,stem-mechanical=c,comm-architect=d,comm-expert=e,comm-mechanical=f",
            {
                "stem-architect": "a",
                "stem-expert": "b",
                "stem-mechanical": "c",
                "comm-architect": "d",
                "comm-expert": "e",
                "comm-mechanical": "f",
            },
        ),
        (
            "comm-mechanical=f,comm-expert=e,comm-architect=d,stem-mechanical=c,stem-expert=b,stem-architect=a",
            {
                "stem-architect": "a",
                "stem-expert": "b",
                "stem-mechanical": "c",
                "comm-architect": "d",
                "comm-expert": "e",
                "comm-mechanical": "f",
            },
        ),
        (
            "*=haiku,stem-expert=opus",
            {
                "stem-architect": "haiku",
                "stem-expert": "opus",
                "stem-mechanical": "haiku",
                "comm-architect": "haiku",
                "comm-expert": "haiku",
                "comm-mechanical": "haiku",
            },
        ),
        (
            "stem-expert=opus,*=haiku",
            dict.fromkeys(CATEGORIES, "haiku"),
        ),
    ],
)
def test_parse_category_map_is_total_in_category_order(spec: str, expected: dict[str, str]) -> None:
    parsed = parse_category_map(spec, supplier=_SUPPLIER)
    assert parsed == expected
    assert list(parsed) == list(CATEGORIES)


@pytest.mark.parametrize(
    "spec, message",
    [
        (
            "stem-expert=opus",
            "names no value for stem-architect, stem-mechanical, comm-architect, comm-expert, comm-mechanical",
        ),
        ("*=x,middle=y", "'middle=y' names no category"),
        ("*-architect=y", "names no value for stem-expert, stem-mechanical, comm-expert, comm-mechanical"),
        ("*=x,stem-expert", "'stem-expert' is not a <glob>=<model> entry"),
        ("*=x,stem-expert=a=b", "'stem-expert=a=b' is not a <glob>=<model> entry"),
        ("*=x,stem-expert=two words", "contains whitespace inside a glob or a model"),
        ("*=x,", "'' is not a <glob>=<model> entry"),
    ],
)
def test_parse_category_map_refusals(spec: str, message: str) -> None:
    with pytest.raises(InputError, match=re.escape(f"{_SUPPLIER}: ")) as caught:
        parse_category_map(spec, supplier=_SUPPLIER)
    assert message in str(caught.value)


def test_the_settings_file_names_its_harnesses_in_name_order_with_their_install_and_map(tmp_path: Path) -> None:
    """A section names its harness, either section; `install` arrives as written or absent; a map
    section's entries join in file order, so a later entry overwrites an earlier one."""
    path = settings_file(tmp_path, "[opencode]\ninstall = always\n\n[claude-model-map]\n*=haiku\nstem-expert=opus\n")
    settings, _ = read_settings(str(path))
    assert list(settings) == ["claude", "opencode"]
    assert settings["opencode"].install == "always"
    assert settings["opencode"].supply is None
    assert settings["claude"].install is None
    assert settings["claude"].supply == MapSupply(
        category_map={**dict.fromkeys(CATEGORIES, "haiku"), "stem-expert": "opus"},
        supplier=f"--config-file {path}, section '[claude-model-map]'",
    )


def test_a_settings_file_naming_no_harness_names_nothing_but_is_not_no_file(tmp_path: Path) -> None:
    """A file that exists and names no harness reads as an empty mapping: the file is there, and it
    names nothing. Only the absence of every file reads as None."""
    settings, _ = read_settings(str(settings_file(tmp_path, "")))
    assert settings == {}
    assert settings is not None


def test_a_render_takes_its_components_from_the_flag_alone(tmp_path: Path, monkeypatch) -> None:
    """`components` is the install's selection: a flagless render that read the file's value turned the
    component on and made the flag's "default none" help false wherever a settings file existed."""
    monkeypatch.setenv("DEVPRO_DEV", "1")
    settings = settings_file(tmp_path, "[claude]\ncomponents = kbase\n")
    from_file = tmp_path / "from-file"
    from_file.mkdir()
    main(["dev-render", "--out", str(from_file), "--harness=claude", f"--config-file={settings}"])
    assert not (from_file / "skills/kbase/SKILL.md").exists()
    from_flag = tmp_path / "from-flag"
    from_flag.mkdir()
    main(["dev-render", "--out", str(from_flag), "--components=kbase", "--harness=claude"])
    assert (from_flag / "skills/kbase/SKILL.md").is_file()


def test_a_missing_default_settings_file_is_no_config(_home: Path) -> None:
    settings, path = read_settings(None)
    assert settings is None and path is None


def test_the_default_settings_file_is_read_from_the_home_directory(_home: Path) -> None:
    """The default path is consulted with no flag given, under the home directory the environment names."""
    path = _home / ".config/devpro/devpro.cfg"
    path.parent.mkdir(parents=True)
    path.write_text("[claude]\ninstall = never\n", encoding="utf-8")
    settings, _ = read_settings(None)
    assert settings["claude"].install == "never"


@pytest.mark.parametrize("config_file", ["~/devpro.cfg", "devpro-absent.cfg"], ids=["tilde", "relative"])
def test_a_named_settings_file_that_does_not_exist_is_refused_naming_the_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, config_file: str
) -> None:
    """The path is taken as given: no expansion, no search."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(InputError, match=re.escape(f"--config-file '{config_file}' names no file")):
        read_settings(config_file)


@pytest.mark.parametrize(
    "section",
    ["[claude-code]", "[nonesuch-model-map]", "[DEFAULT]\ninstall = always"],
    ids=["settings", "map", "default"],
)
def test_a_settings_file_section_no_harness_names_is_refused(tmp_path: Path, section: str) -> None:
    path = settings_file(tmp_path, f"{section}\n")
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert section.split()[0] in message
    assert "claude, mage, opencode" in message


def test_a_settings_sections_components_key_is_read_and_its_unknown_keys_name_both_keys(tmp_path: Path) -> None:
    """`components` is a harness's second setting, read beside `install`; before it existed the key was
    refused as unknown. A key that is no setting still names both keys it could be."""
    path = settings_file(tmp_path, "[claude]\ninstall = always\ncomponents = kbase\n")
    settings, _ = read_settings(str(path))
    assert settings["claude"].components == "kbase"
    path = settings_file(tmp_path, "[claude]\ncomponents = kbase\nbogus = 1\n")
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert "'bogus'" in message and "install, components" in message and "'[claude-model-map]'" in message


def test_a_settings_section_key_that_is_no_setting_is_refused_naming_the_map_section(tmp_path: Path) -> None:
    path = settings_file(tmp_path, "[claude]\n*=haiku\n")
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert "'*'" in message and "'[claude-model-map]'" in message


@pytest.mark.parametrize(
    "text",
    ["[claude]\nthis is not an entry\n", "[claude]\ninstall = always\ninstall = never\n"],
    ids=["unparseable", "duplicate-key"],
)
def test_a_settings_file_that_does_not_parse_is_refused_naming_the_file_and_the_line(tmp_path: Path, text: str) -> None:
    path = settings_file(tmp_path, text)
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert str(path) in message and "line" in message


def test_opencode_with_no_category_spec_uses_its_default() -> None:
    ctx = build_render(components="", harness="opencode", family="claude")
    assert dict(ctx.category_map) == dict.fromkeys(CATEGORIES, "default")
    assert ctx.model("stem-mechanical") == ""


def test_mage_with_no_category_spec_pins_inherit() -> None:
    ctx = build_render(components="", harness="mage", family="claude")
    assert dict(ctx.category_map) == dict.fromkeys(CATEGORIES, "inherit")
    assert ctx.model("stem-mechanical") == "inherit"


@pytest.mark.parametrize(
    "harness, spec, message",
    [
        (CLAUDE, "default", "'default' is not a <glob>=<model> entry"),
        (OPENCODE, "default,stem-expert=omlx/X", "'default' is not a <glob>=<model> entry"),
        (OPENCODE, "", "'' is not a <glob>=<model> entry"),
    ],
    ids=["claude", "opencode-after-a-comma", "opencode-empty"],
)
def test_a_harness_default_that_names_no_category_is_refused_leading_with_the_harness(
    harness: Harness, spec: str, message: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The remaining home of the bare value: a harness default the harness does not read as one."""
    defaulted = dataclasses.replace(harness, default_category_spec=spec)
    monkeypatch.setattr("devpro.context.harnesses", lambda: {**harnesses(), defaulted.name: defaulted})
    with pytest.raises(InputError) as caught:
        build_render(components="", harness=defaulted.name, family="claude")
    assert str(caught.value).startswith(f"the harness '{defaulted.name}' default category spec: ")
    assert message in str(caught.value)


@pytest.mark.parametrize(
    "harness, family, supply, supplier",
    [
        ("claude", "gemma-4", None, "the family 'gemma-4' categories (--family)"),
        (
            "claude",
            "claude",
            MapSupply(category_map=dict.fromkeys(CATEGORIES, "gemma-4-31B-it"), supplier=_SUPPLIER),
            _SUPPLIER,
        ),
    ],
    ids=["family", "settings-file"],
)
def test_build_render_refuses_a_model_outside_the_harness_shape(
    harness: str, family: str, supply: MapSupply | None, supplier: str
) -> None:
    with pytest.raises(InputError) as caught:
        build_render(components="", harness=harness, family=family, supply=supply)
    message = str(caught.value)
    assert "model 'gemma-4-31B-it' at category stem-architect" in message
    assert f"supplied by {supplier}" in message


@pytest.mark.parametrize(
    "harness, text, expected",
    [(CLAUDE, "inherit", "inherit"), (OPENCODE, "inherit", ""), (OPENCODE, "default", "")],
)
def test_model_inherit_and_its_synonyms_render_the_harness_text(harness: Harness, text: str, expected: str) -> None:
    ctx = Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict.fromkeys(_ALL_INHERIT, text))
    assert ctx.model("stem-mechanical") == expected


def test_build_render_refuses_a_model_the_harness_default_supplies(monkeypatch: pytest.MonkeyPatch) -> None:
    """The third supplier the refusal names: no shipped harness's default spec names a model its own shape
    refuses, so the harness loaded is claude with a default claude's shape does not accept."""
    defaulted = dataclasses.replace(CLAUDE, default_category_spec="*=gpt-4")
    monkeypatch.setattr("devpro.context.harnesses", lambda: {**harnesses(), defaulted.name: defaulted})
    with pytest.raises(InputError) as caught:
        build_render(components="", harness=defaulted.name, family="claude")
    message = str(caught.value)
    assert "model 'gpt-4' at category stem-architect" in message
    assert f"supplied by the harness '{defaulted.name}' default category spec" in message


def test_render_refuses_a_category_outside_the_vocabulary() -> None:
    with pytest.raises(InputError, match="category 'bogus' is not one of stem-architect"):
        Render(
            harness=CLAUDE,
            plugin=PLAIN,
            family=CLAUDE_FAMILY,
            category_map=dict(CLAUDE_FAMILY.categories),
            category="bogus",
        )


@pytest.mark.parametrize("family", ["nonesuch", "templates/family/qwen3.toml", "qwen3.toml", "gemma_4"])
def test_build_render_refuses_a_family_that_is_not_a_name(family: str) -> None:
    with pytest.raises(InputError, match=re.escape("claude, gemma-4, qwen3")):
        build_render(components="", harness="claude", family=family)


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


def _security_reviewer() -> Definition:
    return Definition(
        name="security-reviewer",
        kind=Kind.AGENT,
        description=(
            "Adversarial security review of code and designs. Identifies hazards, attack vectors, and the "
            "specific conditions that must hold to prevent exploitation. Does not prescribe design solutions — "
            "that is the architect's job. Review only, never modifies files."
        ),
        tools=(Tool.BASH, Tool.READ, Tool.GREP, Tool.GLOB, Tool.WRITE, Tool.EDIT, Tool.WEBSEARCH, Tool.WEBFETCH),
        category="stem-architect",
        body="body",
        color="#DC2626",
    )


_SECURITY_REVIEWER_DESCRIPTION = (
    'description: "Adversarial security review of code and designs. Identifies hazards, attack vectors, and '
    "the specific conditions that must hold to prevent exploitation. Does not prescribe design solutions — "
    "that is the architect's job. Review only, never modifies files.\""
)


def _claude_frontmatter(fields: AgentFields) -> tuple[str, ...]:
    form = CLAUDE.definition_form
    assert isinstance(form, FrontmatterForm)
    return form.agent(fields)


def test_claude_frontmatter_holds_the_field_order_and_spelling() -> None:
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    assert _claude_frontmatter(agent_fields(_security_reviewer(), ctx)) == (
        "name: security-reviewer",
        _SECURITY_REVIEWER_DESCRIPTION,
        "model: fable",
        'color: "#DC2626"',
        "tools: Bash, Read, Grep, Glob, Write, Edit, WebSearch, WebFetch",
    )


_PYTHON_CODER_DESCRIPTION = 'description: "Python implementation specialist."'


def _python_coder() -> Definition:
    [defn] = [defn for _, defn in definitions() if defn.name == "python-coder"]
    return defn


def test_an_unrestricted_agent_frontmatter_matches_the_pre_1_0_render() -> None:
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    assert _claude_frontmatter(agent_fields(_python_coder(), ctx)) == (
        "name: python-coder",
        _PYTHON_CODER_DESCRIPTION,
        "model: opus",
        'color: "#3776AB"',
    )


_OPENCODE_PERMISSIONS = {
    "read": "allow",
    "grep": "allow",
    "glob": "allow",
    "list": "allow",
    "edit": "allow",
    "shell": "allow",
    "webfetch": "allow",
    "websearch": "allow",
    "subagent": "deny",
}

# A command and a document take no frontmatter value of their own, so each fixture is the least a
# definition of its kind can be: a name, a kind and a body. Each body does one thing — names the user
# harness directory — so that the placeholder fill is observable.
_COMMAND = Definition(
    name="probe",
    kind=Kind.COMMAND,
    body=f"Read the operator's notes under {hole(HarnessText.USER_HARNESS_DIR)}.",
)
_DOCUMENT = Definition(
    name="note",
    kind=Kind.DOCUMENT,
    body=f"Read the operator's conventions under {hole(HarnessText.USER_HARNESS_DIR)}.",
)


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


Discovered = tuple[tuple[str, Definition], ...]


@pytest.fixture(scope="module")
def discovered() -> Discovered:
    """Every definition the package discovers, with its module."""
    return definitions()


def _found(discovered: Discovered, path: str) -> tuple[str, Definition]:
    [found] = [(module, defn) for module, defn in discovered if defn.output_path == PurePosixPath(path)]
    return found


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


def _skill(**changes: object) -> Definition:
    """A skill named `probe` with one reference, its required description filled, overridable."""
    fields = {
        "name": "probe",
        "kind": Kind.SKILL,
        "description": "Use when the user asks about the knowledge base.",
        "body": "Route the request to the reference it asks for.",
        "files": (SkillFile(path="references/reading.md", body="Read a claim before you cite it."),),
    }
    return Definition(**{**fields, **changes})


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


_OPENCODE_RENDER = Render(harness=OPENCODE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)


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


@pytest.mark.parametrize("components, servers", [(PLAIN, set()), (WITH_KBASE, {"kbase"})], ids=["plain", "with-kbase"])
def test_the_opencode_registry_matches_the_render(components: Components, servers: set[str]) -> None:
    """`registry.json`'s agent, command and skill records are exactly the definitions the render ships, each
    id the one name, a hyphen and the definition's name, each file one the render writes; its MCP server is
    present only where kbase ships."""
    ctx = Render(harness=OPENCODE, plugin=components, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    renders = dict(render_all(ctx))
    registry = json.loads(renders[PurePosixPath("registry.json")])
    records = [*registry["agents"], *registry["commands"], *registry["skills"]]
    shipped = {defn.name: str(defn.output_path) for _, defn in definitions() if components.ships(defn.name)}
    assert sorted((record["id"], record["file"]) for record in records) == sorted(
        (f"{components.name}-{name}", path) for name, path in shipped.items()
    )
    assert all(PurePosixPath(record["file"]) in renders for record in records)
    assert registry["plugin"] == components.name and registry["version"] == devpro.__version__
    assert set(registry["mcp"]) == servers


def test_render_all_emits_every_file_of_a_shipped_skill_and_the_selection_drops_a_whole_definition() -> None:
    shipping = {path for path, _ in render_all(dataclasses.replace(_CLAUDE_RENDER, plugin=WITH_KBASE))}
    without = {path for path, _ in render_all(_CLAUDE_RENDER)}
    assert set(kbase_skill_output_paths()) <= shipping
    assert not any(path.parts[:2] == ("skills", "kbase") for path in without)


# mage's output is a Claude Code plugin directory: claude's vocabulary and one file of its own, the
# manifest.
_MAGE_RENDER = Render(
    harness=MAGE, plugin=WITH_KBASE, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories)
)
_MAGE_MANIFEST = PurePosixPath(".claude-plugin/plugin.json")


def test_a_mage_render_writes_the_plugin_tree_straight_into_the_root(tmp_path: Path) -> None:
    """The installed directory is the plugin itself, so its manifest and its surfaces sit at the root:
    one grown under another directory is a tree Claude Code does not read."""
    written = {path.relative_to(tmp_path).as_posix() for path in write_renders(tmp_path, render_all(_MAGE_RENDER))}
    assert {"agents/python-coder.md", "skills/kbase/SKILL.md", str(_MAGE_MANIFEST)} <= written


def test_a_mage_render_leaves_every_agent_on_the_session_model() -> None:
    """mage's default category spec pins no model, and the one it renders for an unpinned category is the
    inherit text the harness spells: every agent it renders carries `model: inherit`."""
    ctx = build_render(components="", harness="mage", family="claude")
    agents = {path: text for path, text in render_all(ctx) if path.parts[0] == "agents"}
    assert agents
    for path, text in agents.items():
        assert "model: inherit" in text.split("\n---\n", 1)[0].split("\n"), path


def test_the_manifest_is_the_three_key_object_carrying_the_version() -> None:
    """The marketplace reads these three keys and nothing else, its version being the release's."""
    parsed = json.loads(dict(render_all(_MAGE_RENDER))[_MAGE_MANIFEST])
    assert parsed == {
        "name": "devpro",
        "version": devpro.__version__,
        "description": "Skills, agents, and MCP tools from the devpro project",
    }


def test_the_manifest_is_the_only_render_of_a_mage_plugin_carrying_the_version() -> None:
    """A bump republishes the manifest alone: a version in a definition or a skill file would churn a
    render slot on every release and say nothing a plugin manifest does not."""
    carriers = [
        path for path, text in render_all(_MAGE_RENDER) if path != _MAGE_MANIFEST and devpro.__version__ in text
    ]
    assert carriers == []


@pytest.mark.parametrize(
    "harness, tool_name",
    [(CLAUDE, "mcp__plugin_devpro_kbase__query"), (MAGE, "mcp_kbase_query"), (OPENCODE, "kbase_query")],
)
def test_the_kb_reading_reference_names_the_harness_mcp_tool(harness: Harness, tool_name: str) -> None:
    """The rendered instruction must name the callable the selected host actually exposes."""
    ctx = Render(harness=harness, plugin=WITH_KBASE, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    reference = dict(render_all(ctx))[PurePosixPath("skills/kbase/references/reading.md")]
    assert f"`{tool_name}`" in reference


def _user_install_paths() -> set[str]:
    """Each loaded harness's user plugin directory as the guide spells it, and the directory mage's plugin
    parent names, read from the profiles."""
    paths = set()
    for harness in harnesses().values():
        if harness.plugin_dir:
            paths.add(f"{harness.user_harness_dir}/{harness.plugin_dir.replace('{plugin}', '<plugin>')}/")
        if harness.plugin_parent_dir:
            paths.add(f"~/{harness.plugin_parent_dir}/")
    return paths


@pytest.mark.parametrize("harness", harnesses())
def test_the_guide_names_every_harness_install_path_under_every_harness(harness: str) -> None:
    ctx = build_render(components="", harness=harness, family="claude")
    [text] = [text for path, text in render_all(ctx) if str(path).endswith("guide/references/installing.md")]
    assert [path for path in sorted(_user_install_paths()) if path not in text] == []


@pytest.mark.parametrize("harness", harnesses())
def test_the_installing_reference_names_every_install_setting(harness: str) -> None:
    """The page's reader learns the setting's values from the page, and `install` accepts exactly the
    values `INSTALL_SETTINGS` holds: one the page leaves out is one the operator cannot learn from it."""
    ctx = build_render(components="", harness=harness, family="claude")
    [text] = [text for path, text in render_all(ctx) if str(path).endswith("guide/references/installing.md")]
    assert [setting for setting in INSTALL_SETTINGS if setting not in text] == []


@pytest.mark.parametrize("harness", [CLAUDE, MAGE, OPENCODE], ids=lambda harness: harness.name)
def test_the_scratch_rule_names_the_one_scratch_directory(harness: Harness) -> None:
    """Each harness's scratch rule names the one scratch directory both guardrails allow."""
    assert f"`{devpro.clauses.PROJECT_TEMP_DIR}/`" in harness.scratch_rule


def test_no_rendering_names_a_retired_scratch_directory() -> None:
    """The scratch directory is one name under every harness, so every rendering under each of them
    carries that name and no retired one."""
    texts = []
    for harness in (CLAUDE, MAGE, OPENCODE):
        for components in _SELECTIONS:
            ctx = Render(
                harness=harness, plugin=components, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories)
            )
            texts += [text for _, text in render_all(ctx)]
            texts.append(render_agents_file(harness, components, scope="x"))
    retired = [".claude-temp", ".opencode-temp", ".mage-temp"]
    assert [(name, text) for name in retired for text in texts if name in text] == []


def test_no_rendered_agent_body_names_a_clauses_symbol() -> None:
    """An agent body is read by a seat with no `devpro` module in front of it, so a clauses constant
    spelled there is a symbol nothing resolves: the body says in words what the clause means. A
    skill's text may name one as the handle of a file an operator with the repository open reads."""
    symbols = re.compile(
        r"\bclauses\.[A-Za-z_]\w*"
        rf"|\b(?:{'|'.join(sorted(name for name in vars(devpro.clauses) if name.upper() == name))})\b"
    )
    found = []
    for harness in (CLAUDE, MAGE, OPENCODE):
        for components in _SELECTIONS:
            ctx = Render(
                harness=harness, plugin=components, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories)
            )
            for path, text in render_all(ctx):
                if path.parts[0] == "agents":
                    found += [
                        f"{path}:{number}: {line.strip()}"
                        for number, line in enumerate(text.split("\n"), start=1)
                        if symbols.search(line)
                    ]
    assert found == [], "\n".join(found)


def _routed_references(router: str) -> set[str]:
    """The reference paths the router's tables route to, read off the table cells themselves."""
    routed = set()
    for line in router.split("\n"):
        if not line.startswith("|"):
            continue
        for cell in line.strip("|").split("|"):
            path = cell.strip().strip("`")
            if path.startswith("references/"):
                routed.add(path)
    return routed


_SKILLS_WITH_FILES = [defn for _, defn in definitions() if defn.kind is Kind.SKILL and defn.files]


@pytest.mark.parametrize("skill", _SKILLS_WITH_FILES, ids=lambda skill: skill.name)
def test_the_router_routes_to_every_reference_that_ships_and_no_other(skill: Definition) -> None:
    """A reference is read only when its route is reached and every route is a reference, so the two
    sets are one: a route naming a file the skill does not carry opens on nothing, and a file no route
    names is text no session ever reads."""
    routed = _routed_references(skill.body)
    assert routed == {file.path for file in skill.files}
    assert routed, "no route parsed from the table, so the comparison above would pass vacuously"


def test_filled_text_names_the_file_an_unknown_placeholder_stands_in() -> None:
    ctx = _CLAUDE_RENDER
    with pytest.raises(
        InputError,
        match=re.escape("skills/probe/references/reading.md: unknown placeholder @!hrn-nonesuch!@"),
    ):
        filled_text("before @!hrn-nonesuch!@ after", _skill(), ctx, where="skills/probe/references/reading.md")


@pytest.mark.parametrize(
    "path",
    ["references/Reading.md", "SKILL.md", "references/reading.markdown", "../reading.md", "references/"],
)
def test_a_skill_file_path_outside_its_contract_is_refused(path: str) -> None:
    with pytest.raises(InputError, match=re.escape(f"skill file '{path}': path is not kebab")):
        SkillFile(path=path, body="text")


def test_a_skill_file_body_follows_the_definition_body_rule() -> None:
    for body in ("", "  \n", "text\n", "\ntext"):
        with pytest.raises(InputError, match="body must be non-empty text with no leading or trailing newline"):
            SkillFile(path="references/reading.md", body=body)


@pytest.mark.parametrize(
    "part, harness, expected",
    [
        (HarnessText.AGENTS_FILE, CLAUDE, "CLAUDE.md"),
        (HarnessText.AGENTS_FILE, OPENCODE, "AGENTS.md"),
        (HarnessText.PROJECT_HARNESS_DIR, CLAUDE, ".claude"),
        (HarnessText.PROJECT_HARNESS_DIR, OPENCODE, ".opencode"),
        (HarnessText.DISPLAY_NAME, CLAUDE, "claude code"),
        (HarnessText.DISPLAY_NAME, OPENCODE, "opencode"),
        (HarnessText.DISPLAY_NAME, MAGE, "mage"),
        (HarnessText.USER_HARNESS_DIR, CLAUDE, "~/.claude"),
        (HarnessText.USER_HARNESS_DIR, OPENCODE, "~/.config/opencode"),
        (HarnessText.MCP_TOOL_PREFIX, CLAUDE, "mcp__plugin_devpro_kbase__"),
        (HarnessText.MCP_TOOL_PREFIX, OPENCODE, "kbase_"),
    ],
)
def test_a_harness_text_placeholder_fills_with_the_harness_string(
    part: HarnessText, harness: Harness, expected: str
) -> None:
    defn = Definition(name="probe", kind=Kind.COMMAND, body=f"see {hole(part)}/x")
    ctx = Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    assert filled_body(defn, ctx) == f"see {expected}/x"


def test_a_harness_display_name_that_is_not_lowercase_is_refused() -> None:
    with pytest.raises(InputError, match=re.escape("harness 'claude': display_name is not lowercase")):
        dataclasses.replace(CLAUDE, display_name="Claude Code")


@pytest.mark.parametrize(
    "placeholder", ["@!hrn.agents-file!@", "@!hrn-nonesuch!@", "@!fam-gap!@", "@!ask-vs-stipulate!@"]
)
def test_an_unknown_placeholder_is_refused_at_render(placeholder: str) -> None:
    defn = Definition(name="probe", kind=Kind.COMMAND, body=f"before {placeholder} after")
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    with pytest.raises(InputError, match=re.escape(f"definition 'probe': unknown placeholder {placeholder}")):
        filled_body(defn, ctx)


@pytest.mark.parametrize("part", [*HarnessText, *OptionalHarnessText, *TuningText], ids=lambda part: part.name)
def test_the_text_module_spells_each_render_placeholder_as_the_renderer_fills_it(
    part: HarnessText | OptionalHarnessText | TuningText,
) -> None:
    assert getattr(devpro.clauses, part.name) == hole(part)


def test_the_text_module_spells_the_plugin_name_as_the_renderer_fills_it() -> None:
    assert devpro.clauses.PLUGIN_NAME == hole(PluginText.NAME)


def test_the_text_module_spells_a_reference_as_the_renderer_fills_it() -> None:
    assert devpro.clauses.ref(name="python-coder") == reference("python-coder")
    assert devpro.clauses.optional_ref(name="python-coder") == optional_reference("python-coder")


_PREFIXED = [CLAUDE, dataclasses.replace(CLAUDE, reference_prefix="x:")]


@pytest.mark.parametrize("harness", _PREFIXED, ids=["bare", "prefixed"])
def test_a_reference_in_a_body_and_a_description_fills_with_the_prefix_and_name(harness: Harness) -> None:
    ctx = Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    named = f"{ctx.bound_harness.reference_prefix}python-coder"
    agent = Definition(
        name="probe",
        kind=Kind.AGENT,
        description=f"Prefer over {reference('python-coder')}.",
        tools=ALL,
        category="stem-expert",
        body=f"Hand it to `{reference('python-coder')}`.",
    )
    skill = _skill(description=f"Prefer over {reference('python-coder')}.")
    agent_text = render_definition(agent, ctx, module="devpro.definitions.probe")
    assert f'description: "Prefer over {named}."' in agent_text.split("\n")
    assert agent_text.endswith(f"Hand it to `{named}`.\n")
    assert f'description: "Prefer over {named}."' in render_definition(skill, ctx, module="m").split("\n")


@pytest.mark.parametrize("harness", _PREFIXED, ids=["bare", "prefixed"])
@pytest.mark.parametrize("field", ["body", "description"])
def test_a_reference_to_an_undiscovered_name_is_refused_naming_the_definition(harness: Harness, field: str) -> None:
    hole_text = reference("nonesuch")
    defn = Definition(
        name="probe", kind=Kind.AGENT, description="a probe", tools=ALL, category="stem-expert", body="Own."
    )
    defn = dataclasses.replace(defn, **{field: f"see {hole_text}"})
    ctx = Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    with pytest.raises(InputError, match=re.escape("definition 'probe'")) as refused:
        render_definition(defn, ctx, module="m")
    assert f"unknown placeholder {hole_text}" in str(refused.value)


_NAMESPACED = [harness for harness in (CLAUDE, MAGE, OPENCODE) if harness.reference_prefix]


@pytest.mark.parametrize("harness", _NAMESPACED, ids=lambda harness: harness.name)
def test_a_reference_prefix_changes_nothing_but_the_reference_sites(harness: Harness) -> None:
    """Every rendered file, the agents file included, read with each reference's prefix removed is the
    render of the same harness with the prefix empty, and that bare render spells no reference: a prefix
    reaches no text but the references it is put before. A reference is the prefix put before a
    definition's name; the prefix is not searched for on its own, since text that names no definition
    may hold it (`devpro-` within `.devpro-temp`)."""
    bare = dataclasses.replace(harness, reference_prefix="")
    prefix = harness.bound(PLAIN.name).reference_prefix
    sites = tuple(f"{prefix}{defn.name}" for _, defn in definitions())

    def rendered(each: Harness) -> dict[PurePosixPath, str]:
        ctx = Render(harness=each, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
        return {**dict(render_all(ctx)), PurePosixPath("<agents file>"): render_agents_file(each, PLAIN, scope="x")}

    # The agents-file marker lines spell the project's name, which can equal the plugin's and so hold the
    # prefix without being a reference site.
    def off_marker(text: str) -> list[str]:
        return [line for line in text.split("\n") if not is_marker_line(line)]

    def without_sites(line: str) -> str:
        for site in sites:
            line = line.replace(site, site[len(prefix) :])
        return line

    def unprefixed(text: str) -> str:
        return "\n".join(line if is_marker_line(line) else without_sites(line) for line in text.split("\n"))

    def site_lines(text: str) -> list[str]:
        return [line for line in off_marker(text) if any(site in line for site in sites)]

    prefixed, plain = rendered(harness), rendered(bare)
    assert prefixed.keys() == plain.keys()
    assert {path: unprefixed(text) for path, text in prefixed.items()} == plain
    assert [path for path, text in plain.items() if site_lines(text)] == []
    assert any(site_lines(text) for text in prefixed.values())


_STEP_DOWN_BODY = f"before\n\nDefault: `{devpro.clauses.STEP_DOWN_MODEL}`, unless bound.\n\nafter"
_OMLX_SUPPLY = MapSupply(category_map=dict.fromkeys(CATEGORIES, "omlx/Qwen3.8-Flash-Next"), supplier=_SUPPLIER)
_INHERIT_SUPPLY = MapSupply(category_map=_ALL_INHERIT, supplier=_SUPPLIER)


@pytest.mark.parametrize(
    "harness, supply, rendered",
    [
        ("claude", None, "before\n\nDefault: `stem-mechanical=sonnet, comm-mechanical=haiku`, unless bound.\n\nafter"),
        ("opencode", None, "before\n\nafter"),
        (
            "opencode",
            _OMLX_SUPPLY,
            "before\n\nDefault: `stem-mechanical=omlx/Qwen3.8-Flash-Next, comm-mechanical=omlx/Qwen3.8-Flash-Next`, "
            "unless bound.\n\nafter",
        ),
        ("mage", None, "before\n\nafter"),
        ("claude", _INHERIT_SUPPLY, "before\n\nafter"),
    ],
)
def test_the_step_down_paragraph_names_the_mechanical_pair_or_drops_whole(
    harness: str, supply: MapSupply | None, rendered: str
) -> None:
    """A skill declares no category, so the paragraph carries both disciplines' mechanical members; where
    a member renders as the harness's inherit text there is nothing to step down to, and where both do
    the paragraph goes with its other text."""
    ctx = build_render(components="", harness=harness, family="claude", supply=supply)
    assert filled_text(_STEP_DOWN_BODY, _skill(), ctx, where="skills/probe/SKILL.md") == rendered


@pytest.mark.parametrize(
    "category, rendered",
    [
        ("stem-architect", "before\n\nDefault: `sonnet`, unless bound.\n\nafter"),
        ("comm-expert", "before\n\nDefault: `haiku`, unless bound.\n\nafter"),
    ],
    ids=["stem", "comm"],
)
def test_an_agent_steps_down_to_its_own_disciplines_mechanical_member(category: str, rendered: str) -> None:
    """An agent's step-down model is its own discipline's mechanical member, not the pair."""
    ctx = build_render(components="", harness="claude", family="claude")
    agent = Definition(
        name="probe", kind=Kind.AGENT, description="a probe", tools=ALL, category=category, body=_STEP_DOWN_BODY
    )
    assert filled_text(_STEP_DOWN_BODY, agent, ctx, where="agents/probe.md") == rendered


def test_the_step_down_model_fills_a_skill_supporting_file_as_it_fills_skill_md() -> None:
    line = f"Step down to {devpro.clauses.STEP_DOWN_MODEL}."
    defn = _skill(body=line, files=(SkillFile(path="references/reading.md", body=line),))
    ctx = build_render(components="", harness="claude", family="claude")
    rendered = render_skill_file(defn, defn.files[0], ctx, module="devpro.definitions.probe")
    assert rendered.endswith("\n\nStep down to stem-mechanical=sonnet, comm-mechanical=haiku.\n")


# A paragraph a tuning hole stands in is dropped whole where the value fills to nothing; a list or table
# in that paragraph would go with it.
_TUNING_HOLES = re.compile("|".join(re.escape(hole(part)) for part in TuningText))
_LIST_OR_TABLE_LINE = re.compile(r"^\s*(?:[-*] |\d+\. |\|)", re.MULTILINE)


def test_no_tuning_hole_shares_a_paragraph_with_a_list_or_table() -> None:
    every = [defn for _, entries in discover() for defn in entries]
    bodies = [(defn.name, defn.body) for defn in every]
    bodies += [(f"{defn.name}/{file.path}", file.body) for defn in every for file in defn.files]
    found = [
        f"{label}: {paragraph[:120]}"
        for label, body in bodies
        for paragraph in body.split("\n\n")
        if _TUNING_HOLES.search(paragraph) and _LIST_OR_TABLE_LINE.search(paragraph)
    ]
    assert found == [], "\n".join(found)


@pytest.mark.parametrize("path", ["agents/python-coder.md", "agents/web-app-expert.md"])
def test_a_coder_and_a_platform_expert_render_the_recipe_rule_under_claude_and_drop_it_under_opencode(
    discovered: Discovered, path: str
) -> None:
    """The paragraph is the harness's own: where the harness supplies one it stands as its own paragraph,
    and where it supplies none the paragraph goes whole, leaving no empty one behind."""
    _, coder = _found(discovered, path)
    paragraph = CLAUDE.recipe_rule
    under_claude = filled_body(
        coder, Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    )
    under_opencode = filled_body(
        coder, Render(harness=OPENCODE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    )
    assert OPENCODE.recipe_rule == ""
    assert f"\n\n{paragraph}\n\n" in under_claude
    assert paragraph not in under_opencode
    assert "\n\n\n" not in under_opencode


def test_the_kbase_project_rule_paragraph_renders_under_mage_and_drops_under_claude() -> None:
    body = f"before\n\n{hole(OptionalHarnessText.KBASE_PROJECT_RULE)}\n\nafter"
    defn = Definition(name="probe", kind=Kind.COMMAND, body=body)
    under_mage = filled_body(defn, Render(harness=MAGE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT))
    under_claude = filled_body(
        defn, Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    )
    assert MAGE.kbase_project_rule
    assert under_mage == f"before\n\n{MAGE.kbase_project_rule}\n\nafter"
    assert under_claude == "before\n\nafter"


def test_a_paragraph_holding_an_optional_harness_text_the_harness_supplies_nothing_for_drops_whole() -> None:
    body = f"before\n\nThe rule is: {hole(OptionalHarnessText.RELOAD_RULE)}\n\nafter"
    defn = Definition(name="probe", kind=Kind.COMMAND, body=body)
    under_claude = filled_body(
        defn, Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    )
    under_mage = filled_body(defn, Render(harness=MAGE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT))
    assert MAGE.reload_rule == ""
    assert CLAUDE.reload_rule
    assert under_claude == f"before\n\nThe rule is: {CLAUDE.reload_rule}\n\nafter"
    assert under_mage == "before\n\nafter"


def _kbase_skill_render(harness: Harness) -> dict[PurePosixPath, str]:
    """Every file of `harness`'s render of the kbase skill, keyed by its output path."""
    ctx = Render(harness=harness, plugin=WITH_KBASE, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    return dict(render_all(ctx))


def test_the_kbase_tools_reload_rule_renders_under_claude_at_both_fill_sites_and_drops_elsewhere() -> None:
    """The router's not-offered branch and installing.md's restart section each carry the reload rule as a
    harness-conditional paragraph: claude supplies the sentence at both, opencode and mage supply none, so
    the paragraph drops whole at both there."""
    router = PurePosixPath("skills/kbase/SKILL.md")
    restart = PurePosixPath("skills/kbase/references/installing.md")
    sentence = CLAUDE.tools_reload_rule
    assert sentence in _kbase_skill_render(CLAUDE)[router]
    assert sentence in _kbase_skill_render(CLAUDE)[restart]
    for harness in (OPENCODE, MAGE):
        assert harness.tools_reload_rule == ""
        assert sentence not in _kbase_skill_render(harness)[router]
        assert sentence not in _kbase_skill_render(harness)[restart]


_TUNED = Family(
    "tuned",
    {
        "stem-architect": "big",
        "stem-expert": "big",
        "stem-mechanical": "mid",
        "comm-architect": "big",
        "comm-expert": "big",
        "comm-mechanical": "mid",
    },
    overlays={Anchor.ASK_VS_STIPULATE: Overlay(text="family-wide", members={"mid": "for mid"})},
)


def _with_family_text(*, family: Family, category: str, body: str) -> str:
    defn = Definition(name="probe", kind=Kind.AGENT, description="a probe", tools=ALL, category=category, body=body)
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=family, category_map=dict(family.categories))
    return render_definition(defn, ctx, module="devpro.definitions.probe").split("---\n\n", 1)[1]


_OVERLAY = hole(Anchor.ASK_VS_STIPULATE)


@pytest.mark.parametrize(
    "family, category, body, rendered",
    [
        (_TUNED, "stem-mechanical", f"before\n\n{_OVERLAY}\n\nafter", "before\n\nfor mid\n\nafter\n"),
        (_TUNED, "stem-expert", f"before\n\n{_OVERLAY}\n\nafter", "before\n\nfamily-wide\n\nafter\n"),
        (CLAUDE_FAMILY, "stem-mechanical", f"before\n\n{_OVERLAY}\n\nafter", "before\n\nafter\n"),
        (CLAUDE_FAMILY, "stem-mechanical", f"{_OVERLAY}\n\nafter", "after\n"),
        (CLAUDE_FAMILY, "stem-mechanical", f"before\n\n{_OVERLAY}", "before\n"),
    ],
)
def test_family_text_renders_the_seats_overlay_or_leaves_no_empty_paragraph(
    family: Family, category: str, body: str, rendered: str
) -> None:
    assert _with_family_text(family=family, category=category, body=body) == rendered


# Filled text is literal: what a fill puts into a body is never filled again. Each value below carries a
# hole the fill expands — to the harness's agents file name — so any second pass over filled text
# changes the output.
_BAIT = hole(HarnessText.AGENTS_FILE)
_BAITED_FAMILY = Family(
    "baited",
    {
        "stem-architect": "big",
        "stem-expert": "big",
        "stem-mechanical": f"mid{_BAIT}",
        "comm-architect": "big",
        "comm-expert": "big",
        "comm-mechanical": "small",
    },
    overlays={Anchor.ASK_VS_STIPULATE: Overlay(text=f"overlay {_BAIT}")},
)


def _clause_with_a_baited_harness_value() -> tuple[Definition, Render, str]:
    """A clause constant's own holes are filled once; the value one fills to stays as it is."""
    harness = dataclasses.replace(CLAUDE, project_harness_dir=f"temp{_BAIT}")
    clause = devpro.clauses.NEW_PROJECT_SETUP
    expected = clause.replace(hole(HarnessText.PROJECT_HARNESS_DIR), f"temp{_BAIT}")
    defn = Definition(name="probe", kind=Kind.COMMAND, body=clause)
    return defn, Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT), expected


def _baited_harness_text() -> tuple[Definition, Render, str]:
    harness = dataclasses.replace(CLAUDE, user_harness_dir=f"~/home{_BAIT}")
    defn = Definition(name="probe", kind=Kind.COMMAND, body=f"see {hole(HarnessText.USER_HARNESS_DIR)}")
    return (
        defn,
        Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT),
        f"see ~/home{_BAIT}",
    )


def _baited_optional_harness_text() -> tuple[Definition, Render, str]:
    harness = dataclasses.replace(CLAUDE, recipe_rule=f"rule {_BAIT}")
    defn = Definition(name="probe", kind=Kind.COMMAND, body=hole(OptionalHarnessText.RECIPE_RULE))
    return (
        defn,
        Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT),
        f"rule {_BAIT}",
    )


def _baited_family_overlay() -> tuple[Definition, Render, str]:
    defn = Definition(
        name="probe", kind=Kind.AGENT, description="a probe", tools=ALL, category="stem-expert", body=_OVERLAY
    )
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=_BAITED_FAMILY, category_map=dict(_BAITED_FAMILY.categories))
    return defn, ctx, f"overlay {_BAIT}"


def _baited_scope_name() -> tuple[Definition, Render, str]:
    defn = Definition(name="probe", kind=Kind.AGENTS_FILE, body=f"# {hole(AgentsFileText.SCOPE_NAME)}")
    return (
        defn,
        Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT, scope=f"s{_BAIT}"),
        f"# s{_BAIT}",
    )


def _baited_step_down_model() -> tuple[Definition, Render, str]:
    """The family member a mechanical side pins carries the hole."""
    defn = _skill(body=f"use {hole(TuningText.STEP_DOWN_MODEL)}")
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=_BAITED_FAMILY, category_map=dict(_BAITED_FAMILY.categories))
    return defn, ctx, f"use stem-mechanical=mid{_BAIT}, comm-mechanical=small"


@pytest.mark.parametrize(
    "case",
    [
        _clause_with_a_baited_harness_value,
        _baited_harness_text,
        _baited_optional_harness_text,
        _baited_family_overlay,
        _baited_scope_name,
        _baited_step_down_model,
    ],
    ids=["clause", "harness-text", "optional-harness-text", "family-overlay", "scope-name", "step-down-model"],
)
def test_a_filled_value_carrying_a_hole_reaches_the_body_literally(case) -> None:
    defn, ctx, expected = case()
    filled = filled_body(defn, ctx)
    assert filled == expected
    assert _BAIT in filled


def test_stock_excludes_the_overridden_category() -> None:
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=_TUNED, category_map=dict(_TUNED.categories))
    assert ctx.stock == ("stem-architect", "stem-expert", "comm-architect", "comm-expert")


# The members each family ships. No harness's model shape accepts a gemma or qwen member, so a family
# renders only behind a member override that replaces these, and no rendered file records them: this
# table is their only record.
@pytest.mark.parametrize(
    "name, members",
    [
        (
            "claude",
            {
                "stem-architect": "fable",
                "stem-expert": "opus",
                "stem-mechanical": "sonnet",
                "comm-architect": "sonnet",
                "comm-expert": "sonnet",
                "comm-mechanical": "haiku",
            },
        ),
        (
            "qwen3",
            {
                "stem-architect": "Qwen3.8-Flash-Next",
                "stem-expert": "Qwen3.8-Flash-Next",
                "stem-mechanical": "Qwen3.8-27B",
                "comm-architect": "Qwen3.8-Flash-Next",
                "comm-expert": "Qwen3.8-Flash-Next",
                "comm-mechanical": "Qwen3.8-27B",
            },
        ),
        (
            "gemma-4",
            {
                "stem-architect": "gemma-4-31B-it",
                "stem-expert": "gemma-4-31B-it",
                "stem-mechanical": "gemma-4-12B-it",
                "comm-architect": "gemma-4-31B-it",
                "comm-expert": "gemma-4-31B-it",
                "comm-mechanical": "gemma-4-12B-it",
            },
        ),
    ],
    ids=["claude", "qwen3", "gemma-4"],
)
def test_each_family_pins_the_member_of_every_category(name: str, members: dict[str, str]) -> None:
    assert dict(load("devpro.families", "FAMILY")[name].categories) == members


_REFERENCE = SkillFile(path="references/reading.md", body="Read it.")


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"tools": ()}, "tools must be ALL"),
        ({"body": ""}, "body must be"),
        ({"body": "edge newline\n"}, "body must be"),
        ({"description": 'holds a "quote"'}, "description must be"),
        ({"category": None}, "an agent requires category"),
        ({"kind": Kind.DOCUMENT}, "a document takes no description, tools, category"),
        (
            {"kind": Kind.COMMAND, "description": None, "tools": None, "category": None, "color": "#000000"},
            "takes no color",
        ),
        ({"folder": "nested/Design"}, "folder 'nested/Design'"),
        ({"kind": Kind.SKILL, "description": None}, "a skill requires description"),
        (
            {"kind": Kind.SKILL, "description": "a probe", "tools": ALL, "category": None},
            "a skill takes no tools",
        ),
        (
            {"kind": Kind.SKILL, "description": "a probe", "tools": None, "category": None, "color": "#000000"},
            "a skill takes no color",
        ),
        (
            {"kind": Kind.SKILL, "description": "a probe", "tools": None, "category": None, "folder": "sub"},
            "a skill takes no folder",
        ),
        (
            {
                "kind": Kind.SKILL,
                "description": "a probe",
                "tools": None,
                "category": None,
                "files": (_REFERENCE, _REFERENCE),
            },
            "files names a path twice",
        ),
        (
            {"kind": Kind.COMMAND, "description": None, "tools": None, "category": None, "files": (_REFERENCE,)},
            "a command takes no files",
        ),
    ],
)
def test_definition_refusals(changes: dict, message: str) -> None:
    fields = {
        "name": "probe",
        "kind": Kind.AGENT,
        "description": "a probe",
        "tools": ALL,
        "category": "stem-expert",
        "body": "ok",
    }
    with pytest.raises(InputError, match="definition 'probe'") as caught:
        Definition(**{**fields, **changes})
    assert message in str(caught.value)


def test_output_paths_not_names_are_unique() -> None:
    command = Definition(name="probe", kind=Kind.COMMAND, body="x")
    document = Definition(name="probe", kind=Kind.DOCUMENT, folder="nested", body="x")
    paths = [defn.output_path for _, defn in keyed_by_path([("m.a", (command,)), ("m.b", (document,))])]
    assert paths == [PurePosixPath("agents/nested/probe.md"), PurePosixPath("commands/probe.md")]
    with pytest.raises(InputError, match=re.escape("'commands/probe.md' is produced by both m.a and m.b")):
        keyed_by_path([("m.a", (command,)), ("m.b", (command,))])


def test_an_agents_file_has_no_output_path() -> None:
    defn = Definition(name="probe", kind=Kind.AGENTS_FILE, body="x")
    with pytest.raises(InputError, match="definition 'probe': an agents file has no output path"):
        defn.output_path


def test_discovery_refuses_a_module_without_definitions() -> None:
    with pytest.raises(InputError, match="'devpro.definitions.probe' defines no DEFINITIONS"):
        definitions_of("devpro.definitions.probe", None)


def test_discovery_raises_where_a_subpackage_does_not_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A subpackage that does not import takes every definition under it out of the set — silently,
    since nothing else reads the folder — and an install then prunes their files. Discovery raises
    the failure instead of reporting a shorter set."""
    package = tmp_path / "planted"
    package.mkdir()
    (package / "__init__.py").write_text("raise ImportError('planted does not import')\n", encoding="utf-8")
    (package / "child.py").write_text("X = 1\n", encoding="utf-8")
    monkeypatch.setattr("devpro.definitions.__path__", [str(tmp_path)])
    with pytest.raises(ImportError, match=re.escape("devpro.definitions.planted")):
        discover()


# Source invariants, over every module of the package.


def _walked(root: Path) -> list[Path]:
    """Each module under a root, a directory or one file, a hidden directory's files left out: a
    launcher's `.venv` beside its tools is not package source."""
    paths = [root] if root.is_file() else root.rglob("*.py")
    return [path for path in paths if not any(part.startswith(".") for part in path.relative_to(root).parts)]


def _modules(*subpaths: str) -> list[tuple[str, ast.Module]]:
    """Every module under each subpath of the package (a directory or one file), or the whole package."""
    roots = [_PACKAGE.joinpath(*sub.split("/")) for sub in subpaths] or [_PACKAGE]
    files = sorted({path for root in roots for path in _walked(root)})
    return [
        (path.relative_to(_PACKAGE.parent).as_posix(), ast.parse(path.read_text(encoding="utf-8"))) for path in files
    ]


def test_module_walk_skips_hidden_directories(tmp_path: Path) -> None:
    hidden = tmp_path / ".venv"
    hidden.mkdir()
    (hidden / "planted.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "mod.py").write_text("x = 1\n", encoding="utf-8")
    assert {path.name for path in _walked(tmp_path)} == {"mod.py"}


def _imported(tree: ast.Module) -> list[str]:
    """Every module an import statement names, a relative import as under devpro, and each name a
    from-import takes as a possible submodule (`from devpro import clauses` names `devpro.clauses`)."""
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = f"devpro.{node.module}" if node.level else node.module
            names += [module, *(f"{module}.{alias.name}" for alias in node.names)]
    return names


def test_definitions_and_text_reach_nothing_outside_their_arguments() -> None:
    banned = {"os", "sys", "subprocess", "time", "random"}
    offenders = []
    for path, tree in _modules("definitions", "clauses.py"):
        offenders += [f"{path} imports {name}" for name in _imported(tree) if name.split(".")[0] in banned]
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                called = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", None)
                if called == "open":
                    offenders.append(f"{path}:{node.lineno} calls open")
    assert offenders == []


_HOOK_WIRING = "devpro/profiler/hooks.py"
# The renderer's imports the hook wiring may hold inside a function, and the functions that hold them.
_HOOK_WIRING_IMPORTS = ("from devpro.context import build_render", "from devpro.render import render_all")


def _hook_wiring_imports(tree: ast.Module) -> set[tuple[str, str]]:
    """The `(path, statement)` pairs the hook wiring's carve-out admits: the renderer's two imports, held
    inside `profiler_skill_text`, the function that renders the skill a hook writes. `tree` is the module's
    own, so the carve-out is read against the file it exempts and admits nothing the file does not hold
    there."""
    held = {
        ast.unparse(stmt)
        for function in tree.body
        if isinstance(function, ast.FunctionDef) and function.name == "profiler_skill_text"
        for stmt in function.body
        if isinstance(stmt, (ast.Import, ast.ImportFrom))
    }
    return {(_HOOK_WIRING, stmt) for stmt in held & set(_HOOK_WIRING_IMPORTS)}


def test_the_hook_wiring_carve_out_admits_only_its_two_imports_in_the_writer() -> None:
    """The carve-out is not a hole: the renderer's two imports are admitted where `profiler_skill_text` holds
    them, and neither is admitted anywhere else — a third import in the writer, or either import in
    another function, reads as the offender it is."""
    source = (
        "def profiler_skill_text():\n"
        "    from devpro.render import render_all\n"
        "    from devpro.context import build_render\n"
        "    import json\n"
        "\n"
        "def launcher_resource():\n"
        "    from devpro.render import render_all\n"
    )
    admitted = _hook_wiring_imports(ast.parse(source))
    assert admitted == {
        (_HOOK_WIRING, "from devpro.render import render_all"),
        (_HOOK_WIRING, "from devpro.context import build_render"),
    }


def test_every_import_is_at_module_level() -> None:
    # The entry point is the one exception: its dispatch is lazy, importing each verb's module at dispatch
    # time so no verb pays for another's imports, so its function-level imports are the deliberate
    # exception and are not walked here. The house rule holds for every other module of the package.
    # The absorbed dicing verbs' entry point carries the same exception, for the same reason: its `run`
    # imports each verb's implementation where it dispatches that verb. The profiler's entry point is
    # the third: its verb is one remainder the dispatch resolves, and its `run` imports the subcommands'
    # modules so the `devpro --help` build pays for none of them. The dashboard's entry point is the
    # fourth, for the same reason: its `run` imports the server where it dispatches. The check verbs'
    # entry point is the fifth: its `run` imports the checks' implementation where it dispatches each.
    # The profiler's hook wiring is the one other module, and the same reason one level down: the
    # hook-run capture imports it, so the renderer's imports live in `profiler_skill_text`, the function that
    # renders the skill a hook writes, rather than at module scope, and the renderer never reaches the
    # every-tool-call capture path. `_hook_wiring_imports` reads them from the module, so an import
    # moved back to module scope leaves nothing carved out and reads as the offender it would be.
    offenders = [
        f"{path}:{node.lineno}"
        for path, tree in _modules()
        if path
        not in (
            "devpro/cli.py",
            "devpro/dicing/cli.py",
            "devpro/doccheck/cli.py",
            "devpro/profiler/cli.py",
            "devpro/dashboard/cli.py",
        )
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and node not in tree.body
        and (path, ast.unparse(node)) not in _hook_wiring_imports(tree)
    ]
    assert offenders == []


def _is_stdlib(module: str) -> bool:
    """Whether the top-level module resolves into the running interpreter's
    standard library: built in, frozen, or a file under its stdlib directory
    outside any site-packages."""
    spec = importlib.util.find_spec(module)
    if spec is None or spec.origin is None:
        return False
    if spec.origin in ("built-in", "frozen"):
        return True
    stdlib = Path(sysconfig.get_paths()["stdlib"]).resolve()
    origin = Path(spec.origin).resolve()
    return stdlib in origin.parents and "site-packages" not in origin.relative_to(stdlib).parts


@pytest.mark.parametrize(
    ("module", "expected"),
    [
        ("__future__", True),
        ("ast", True),
        ("_thread", True),
        ("json", True),
        ("pytest", False),
        ("devpro", False),
        ("no_such_module_anywhere", False),
    ],
)
def test_is_stdlib_tells_the_standard_library_from_everything_else(module: str, expected: bool) -> None:
    assert _is_stdlib(module) is expected


def test_every_import_is_stdlib_or_the_package() -> None:
    offenders = [
        f"{path} imports {name}"
        for path, tree in _modules()
        for name in _imported(tree)
        if name.split(".")[0] != "devpro" and not _is_stdlib(name.split(".")[0])
    ]
    assert offenders == []


def test_importing_the_entry_point_imports_no_verb_module() -> None:
    """The dispatch is lazy: building the parser and choosing no verb imports no verb's module, so `--help`
    and every verb pay for no other's imports. Before the change the parser build imported every verb's
    implementation — all nine, the kanban server among them — so this same parser build showed
    `devpro.install` and the dicing verbs' modules in `sys.modules`. The dicing registration chain is the
    pair of the package and its verb surface; no other `devpro.dicing` module is imported by it, the
    board's server among them. The dashboard's own pair is the same: its registration chain loads the
    package, its verb surface and the cli's own imports, and the server it serves from is imported where
    the verb dispatches."""
    probe = (
        "import sys\n"
        "import devpro.cli\n"
        "devpro.cli.build_parser()\n"
        "banned = ('devpro.install', 'devpro.render', 'devpro.agents_file')\n"
        "present = [name for name in banned if name in sys.modules]\n"
        "for package, surface in (('devpro.dicing', 'devpro.dicing.cli'),\n"
        "                         ('devpro.doccheck', 'devpro.doccheck.cli'),\n"
        "                         ('devpro.dashboard', 'devpro.dashboard.cli')):\n"
        "    loaded = {\n"
        "        name for name in sys.modules if name == package or name.startswith(package + '.')\n"
        "    }\n"
        "    present += sorted(loaded - {package, surface})\n"
        "assert not present, present\n"
    )
    env = {**os.environ, "PYTHONPATH": str(_PACKAGE.parent)}
    result = subprocess.run([sys.executable, "-c", probe], env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def test_importing_the_profiler_hook_wiring_never_reaches_the_renderer() -> None:
    """The capture path pays for nothing it does not run: the hook-run capture imports the profiler's hook
    wiring for its two names, and the install imports it for the stores' rename, so neither may pull the
    renderer in — seventeen devpro submodules for the rename alone, the renderer's import on the
    every-tool-call capture path. The modules that register the profiler verb are the only others the
    chain may name."""
    probe = (
        "import sys\n"
        "import devpro.profiler.hooks\n"
        "banned = ('devpro.render', 'devpro.context', 'devpro.definitions', 'devpro.loading', 'devpro.family')\n"
        "present = [name for name in banned if name in sys.modules]\n"
        "assert not present, present\n"
    )
    env = {**os.environ, "PYTHONPATH": str(_PACKAGE.parent)}
    result = subprocess.run([sys.executable, "-c", probe], env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def test_the_definition_modules_and_the_text_module_hold_their_structure() -> None:
    violations = check_structure([*definition_paths(), _PACKAGE / "clauses.py"])
    assert violations == [], "\n".join(violations)


def test_development_bodies_spell_each_term_through_its_constant() -> None:
    """A project binds a term by its exact spelling, so a body writing one out literally drifts from the
    constant every other mention renders from."""
    tree = ast.parse((_PACKAGE / "definitions" / "skills" / "development.py").read_text(encoding="utf-8"))
    terms = {
        node.targets[0].id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign) and node.targets[0].id.endswith("_TERM")
    }
    assert terms, "no *_TERM constant found, so the check below would pass vacuously"
    literals = [
        node
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        for keyword in call.keywords
        if keyword.arg == "body"
        for node in ast.walk(keyword.value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    found = [
        f"a development.py body writes out {term} as {value!r}"
        for node in literals
        for term, value in terms.items()
        if value in node.value
    ]
    assert found == [], "\n".join(found)


_CORPUS_JOIN_SITES = (
    "devpro/definitions/agents/android_app_expert.py: clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/android_app_expert.py: clauses.PROJECT_SETUP_PLATFORM + clauses.STDLIB_FIRST_ALWAYS",
    "devpro/definitions/agents/architect.py: clauses.MACHINE_GUARANTEES",
    "devpro/definitions/agents/architect.py: clauses.PROVE_REPLACEMENT_RULE",
    "devpro/definitions/agents/architect.py: clauses.SEPARATION_OF_CONCERNS",
    "devpro/definitions/agents/c_coder.py: clauses.DATA_FORMATS_SCOPE",
    "devpro/definitions/agents/c_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/c_coder.py: clauses.data_race_frame + clauses.TSAN_VISIBILITY",
    "devpro/definitions/agents/cpp_coder.py: clauses.DATA_FORMATS_SCOPE",
    "devpro/definitions/agents/cpp_coder.py: clauses.DEPENDENCIES_LEAD_PACKAGES + clauses.ISSUE_TRACKER_HEALTH + clauses.manual_over_large_dependency",
    "devpro/definitions/agents/cpp_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/cpp_coder.py: clauses.data_race_frame + clauses.TSAN_VISIBILITY",
    "devpro/definitions/agents/generalist_coder.py: clauses.SHELL_HOUSE_STYLE",
    "devpro/definitions/agents/generalist_coder.py: clauses.heavy_logging_framework + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/generalist_coder.py: clauses.unit_test_scope_coder + clauses.COVERAGE_METRIC + clauses.MOCKING_THRESHOLD_GENERAL",
    "devpro/definitions/agents/go_coder.py: clauses.build_system_lead",
    "devpro/definitions/agents/go_coder.py: clauses.heavy_logging_framework + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/ios_app_expert.py: clauses.OSLOG_LOGGING_LEAD + clauses.logging_backend_seam + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/linux_app_expert.py: clauses.PROJECT_SETUP_PLATFORM + clauses.STDLIB_FIRST_ALWAYS",
    "devpro/definitions/agents/linux_app_expert.py: clauses.logging_backend_seam + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/linux_kernel_driver_expert.py: clauses.PROJECT_SETUP_PLATFORM + clauses.STDLIB_FIRST_ALWAYS",
    "devpro/definitions/agents/linux_kernel_driver_expert.py: clauses.logging_backend_seam + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/lua_coder.py: clauses.DATA_FORMATS",
    "devpro/definitions/agents/lua_coder.py: clauses.DEPENDENCIES_LEAD_PACKAGES + clauses.ISSUE_TRACKER_HEALTH + clauses.manual_over_large_dependency",
    "devpro/definitions/agents/lua_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/lua_coder.py: clauses.NEW_PROJECT_SETUP + clauses.new_project_runner_recipes",
    "devpro/definitions/agents/lua_coder.py: clauses.boundary_checks_lead + clauses.boundary_check_coder_body + clauses.BOUNDARY_CHECK_CONSUMERS_CODER",
    "devpro/definitions/agents/lua_coder.py: clauses.build_system_lead",
    "devpro/definitions/agents/macos_app_expert.py: clauses.OSLOG_LOGGING_LEAD + clauses.logging_backend_seam + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/prompt_engineer.py: clauses.machine_guarantees",
    "devpro/definitions/agents/prompt_engineer.py: clauses.pe_declare_bullet",
    "devpro/definitions/agents/python_coder.py: clauses.CODE_PRINCIPLES_CODER",
    "devpro/definitions/agents/python_coder.py: clauses.DATA_FORMATS",
    "devpro/definitions/agents/rust_coder.py: clauses.DATA_FORMATS",
    "devpro/definitions/agents/rust_coder.py: clauses.DEPENDENCIES_LEAD_CRATES + clauses.ISSUE_TRACKER_HEALTH + clauses.manual_over_large_dependency",
    "devpro/definitions/agents/rust_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/rust_coder.py: clauses.boundary_checks_lead + clauses.boundary_check_coder_body + clauses.BOUNDARY_CHECK_CONSUMERS_CODER",
    "devpro/definitions/agents/rust_coder.py: clauses.build_system_lead",
    "devpro/definitions/agents/shell_dsl_coder.py: clauses.CODE_PRINCIPLES_CODER",
    "devpro/definitions/agents/shell_dsl_coder.py: clauses.DEPENDENCIES_LEAD_PACKAGES + clauses.ISSUE_TRACKER_HEALTH + clauses.manual_over_large_dependency",
    "devpro/definitions/agents/shell_dsl_coder.py: clauses.boundary_checks_lead + clauses.CHEAP_OVER_THOROUGH + clauses.BOUNDARY_CHECK_CONSUMERS_CODER",
    "devpro/definitions/agents/shell_dsl_coder.py: clauses.unit_test_scope_coder + clauses.COVERAGE_METRIC + clauses.MOCKING_THRESHOLD_GENERAL",
    "devpro/definitions/agents/typescript_coder.py: clauses.DATA_FORMATS",
    "devpro/definitions/agents/typescript_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/typescript_coder.py: clauses.NEW_PROJECT_SETUP + clauses.new_project_runner_recipes",
    "devpro/definitions/agents/typescript_coder.py: clauses.boundary_checks_lead + clauses.boundary_check_coder_body + clauses.BOUNDARY_CHECK_CONSUMERS_CODER",
    "devpro/definitions/agents/typescript_coder.py: clauses.build_system_lead",
    "devpro/definitions/agents/web_app_expert.py: clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/windows_app_expert.py: clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/skills/kbase.py: clauses.kb_orientation_docs",
)


def test_the_join_sites_are_the_ones_the_corpus_holds(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The clause-paragraph rule's judgment is manual, so the corpus's join sites are pinned: a new
    site fails until the tuple is updated deliberately, and a moved line, whose site's line number
    the key drops, does not."""
    monkeypatch.chdir(_PACKAGE.parent)
    clause_join_sites.main([])
    lines = capsys.readouterr().out.splitlines()
    assert lines[-1].startswith("sites: ")
    keys = []
    for line in lines[:-1]:
        match = re.fullmatch(r"(.+?):\d+: (.+)", line)
        assert match is not None, f"not a join-site line: {line}"
        keys.append(f"{match[1]}: {match[2]}")
    assert sorted(keys) == sorted(_CORPUS_JOIN_SITES)


_DEFINITION_HEAD = "from devpro import clauses\nfrom devpro.definition import Definition\n"


def _definitions_of_body(body: str, *, head: str = "") -> str:
    """A definition-module source whose one Definition has `body` as its body= source text."""
    return f'{_DEFINITION_HEAD}{head}DEFINITIONS = (Definition(name="p", kind=Kind.COMMAND, body={body}),)\n'


def _definitions_of_files(files: str) -> str:
    """A definition-module source whose one skill has `files` as its files= source text."""
    return f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", kind=Kind.SKILL, files={files}),)\n'


@pytest.mark.parametrize(
    "source, line, rule",
    [
        (f'{_DEFINITION_HEAD}_N = len("x")\n', 3, ASSIGNMENT_RULE),
        (f'{_DEFINITION_HEAD}_D = {{"a": "b"}}\n', 3, ASSIGNMENT_RULE),
        (f'{_DEFINITION_HEAD}_T = ("a", _X)\n', 3, ASSIGNMENT_RULE),
        (f'{_DEFINITION_HEAD}_C = "".join(x for x in "ab")\n', 3, ASSIGNMENT_RULE),
        (f'{_DEFINITION_HEAD}_F = f"{{clauses.DISSENT}}"\n', 3, ASSIGNMENT_RULE),
        (_definitions_of_body('f"{clauses.dissent(x=clauses.other())}"'), 3, ARGUMENT_RULE),
        (_definitions_of_body('f"{_S.format(x=_V)}"', head='_S = "{x}"\n_V = f"{_S}"\n'), 5, ""),
        (_definitions_of_body("f\"{_F.format(x='a')}\"", head='_A = "a"\n_F = f"{_A} {{x}}"\n'), 5, CALL_RULE),
        (_definitions_of_body('f"{len(_S)}"', head='_S = "s"\n'), 4, CALL_RULE),
        (_definitions_of_body('f"{_S.upper()}"', head='_S = "s"\n'), 4, CALL_RULE),
        (_definitions_of_body('f"{clauses.x(**_K)}"'), 3, ARGUMENT_RULE),
        (_definitions_of_body('f"{_S if _S else _S}"', head='_S = "s"\n'), 4, BODY_RULE),
        (_definitions_of_files('(SkillFile(path="references/r.md", body="b"),)'), 3, ""),
        (_definitions_of_files('(SkillFile(path="references/r.md", body=f"{clauses.dissent()}"),)'), 3, ""),
        (_definitions_of_files('(SkillFile(path=clauses.f(), body="b"),)'), 3, FILES_RULE),
        (_definitions_of_files("(SkillFile(path=_P, body='b'),)"), 3, FILES_RULE),
        (_definitions_of_files("(clauses.f(),)"), 3, CALL_RULE),
        (_definitions_of_files('(SkillFile(path="references/r.md", body=f"{len(_S)}"),)'), 3, CALL_RULE),
        (
            f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", description=f"{{clauses.ref(name=\'x\')}}", body="b"),)\n',
            3,
            "",
        ),
        (
            f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", description=f"{{len(_S)}}", body="b"),)\n',
            3,
            CALL_RULE,
        ),
        (f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", tools=clauses.f(), body="b"),)\n', 3, CALL_RULE),
        (f'{_DEFINITION_HEAD}DEFINITIONS = (Definition("p", "b", kind=Kind.AGENT),)\n', 3, DEFINITION_CALL_RULE),
        (f"{_DEFINITION_HEAD}def helper():\n    pass\n", 3, DEFINITION_TOP_RULE),
        (f"{_DEFINITION_HEAD}DEFINITIONS = (_ONE,)\n", 3, DEFINITION_TOP_RULE),
        ("from devpro.clauses import X\n", 1, IMPORT_RULE),
        ("from devpro import clauses as c\n", 1, IMPORT_RULE),
        ("import devpro.clauses\n", 1, IMPORT_RULE),
    ],
)
def test_check_structure_refuses_a_definition_module_off_its_rules(source: str, line: int, rule: str) -> None:
    expected = [f"m.py:{line}: {rule}"] if rule else []
    assert check_source(source, where="m.py", text_module=False) == expected


@pytest.mark.parametrize(
    "source, rule",
    [
        ('_X = "a"\nY = f"{_X}"\ndef f(*, a, b="x", c=_X) -> str:\n    """doc"""\n    return f"{a}{b}{c}{Y}"\n', ""),
        ("from devpro.vocabulary import hole\n", TEXT_TOP_RULE),
        ("class C:\n    pass\n", TEXT_TOP_RULE),
        ('X = hole("a")\n', ASSIGNMENT_RULE),
        ('X = f"{g()}"\n', ASSIGNMENT_RULE),
        ('X = Y\nY = "y"\n', ASSIGNMENT_RULE),
        ('X = (Y,)\nY = "y"\n', ""),
        ("X = (a,)\n", ASSIGNMENT_RULE),
        ('def f(a):\n    return f"{a}"\n', FUNCTION_RULE),
        ('def f(*, a, b, c, d):\n    return f"{a}{b}{c}{d}"\n', FUNCTION_RULE),
        ('def f(*args):\n    return "x"\n', FUNCTION_RULE),
        ("def f(*, a):\n    return g(a=a)\n", FUNCTION_RULE),
        ('def f(*, a):\n    return f"{g(a=a)}"\n', FUNCTION_RULE),
        ('def f(*, a):\n    b = a\n    return f"{b}"\n', FUNCTION_RULE),
        ('def f(*, a=g()):\n    return f"{a}"\n', FUNCTION_RULE),
        ('def f(*, a):\n    return f"{a!r}"\n', FUNCTION_RULE),
    ],
)
def test_check_structure_refuses_a_text_module_off_its_rules(source: str, rule: str) -> None:
    expected = [f"clauses.py:1: {rule}"] if rule else []
    assert check_source(source, where="clauses.py", text_module=True) == expected


@pytest.mark.parametrize(
    ("folder", "kind", "violates"),
    [
        ("agents", "AGENT", False),
        ("skills", "SKILL", False),
        ("definitions", "AGENTS_FILE", False),
        ("agents", "SKILL", True),
        ("skills", "AGENT", True),
        ("definitions", "AGENT", True),
        ("definitions", "SKILL", True),
    ],
)
def test_check_structure_holds_a_definition_module_to_its_folder(
    tmp_path: Path, folder: str, kind: str, violates: bool
) -> None:
    """The folder a module sits in is the kind it renders: a module under `agents/` declares
    Kind.AGENT, under `skills/` Kind.SKILL, and one at the package's top neither."""
    directory = tmp_path / folder
    directory.mkdir()
    path = directory / "m.py"
    path.write_text(
        f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", kind=Kind.{kind}, body="b"),)\n', encoding="utf-8"
    )
    assert check_structure([path]) == ([f"{path}:3: {FOLDER_KIND_RULE}"] if violates else [])


# Shared text has one source: a paragraph two outputs carry is not written out in either.

_CLAUDE_RENDER = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
# The sweeps below read each selection as it ships: its definitions and its agents file, under claude.
_SELECTION_RENDERS = tuple(
    Render(harness=CLAUDE, plugin=components, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    for components in _SELECTIONS
)
RENDERED_DEFINITION_LINE_CAP = 500  # a runaway guard, not a target; the 100-column wrap makes lines a fair size


def test_no_rendered_definition_exceeds_the_line_cap(discovered: Discovered) -> None:
    """A definition's own rendered body is capped whatever its kind; a supporting file is carried beside
    it, not its own output, and is not counted."""
    over = [
        f"{defn.output_path} renders at {count} lines after the banner; the cap is {RENDERED_DEFINITION_LINE_CAP}"
        for _, defn in discovered
        if (count := len(filled_body(defn, _CLAUDE_RENDER).splitlines())) > RENDERED_DEFINITION_LINE_CAP
    ]
    assert over == []


def test_every_description_is_one_line_with_balanced_code_spans(discovered: Discovered) -> None:
    """A description emits as `description: "…"` on one line, so a newline breaks the frontmatter block
    and an odd backtick count opens a code span that never closes, swallowing the rest of the line. The
    double quote is not checked here: `Definition` already refuses one at construction, which
    `test_definition_refusals` pins."""
    offenders = []
    for _, defn in discovered:
        description = defn.description
        if description is None:
            continue
        if "\n" in description:
            offenders.append(f"{defn.name}: description holds a newline")
        if description.count("`") % 2:
            offenders.append(f"{defn.name}: description has an unclosed code span")
    assert offenders == []


def _credited_text() -> types.SimpleNamespace:
    """The clauses module with every constant and function standing as a sentinel naming it; a
    constant that is a bare placeholder keeps its value, so prose around it is not credited to it."""
    standing: dict[str, object] = {}
    for name, value in vars(devpro.clauses).items():
        if isinstance(value, str) and not devpro.render.PLACEHOLDER.fullmatch(value):
            standing[name] = f"<<devpro.clauses.{name}>>"
        elif isinstance(value, str):
            standing[name] = value
        elif inspect.isfunction(value) and value.__module__ == devpro.clauses.__name__:
            standing[name] = lambda _sentinel=f"<<devpro.clauses.{name}()>>", **_: _sentinel
    return types.SimpleNamespace(**standing)


def _source_definitions(source: str, *, module: str, credited: bool) -> tuple[Definition, ...]:
    """DEFINITIONS as the module's source builds them; credited, with each of the module's string
    constants and everything it reaches through `clauses` standing as a sentinel naming it."""
    tree = ast.parse(source)
    namespace: dict[str, object] = {"__name__": module}
    if credited:
        namespace["clauses"] = _credited_text()
        body = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and any(alias.name == "clauses" for alias in node.names):
                continue
            target = node.targets[0].id if isinstance(node, ast.Assign) else ""
            if target and target != "DEFINITIONS":
                node = ast.copy_location(ast.Assign(targets=node.targets, value=ast.Constant(f"<<{target}>>")), node)
            body.append(node)
        tree.body = body
        ast.fix_missing_locations(tree)
    exec(compile(tree, module, "exec"), namespace)
    return namespace["DEFINITIONS"]


def _prose_unit_list(body: str) -> list[bytes]:
    """The paragraphs and list items of a body in order, each as devtools.render_diff collapses it; a
    heading, a table row and a line of a fenced block are not prose."""
    lines = render_diff.collapsed(body.encode("utf-8")).split(b"\n")
    return [line for line, kind in zip(lines, render_diff.line_kinds(lines)) if kind in ("item", "text")]


def _prose_units(body: str) -> set[bytes]:
    return set(_prose_unit_list(body))


def _outputs(defn: Definition, sentinel: Definition) -> list[tuple[str, str, str]]:
    """(label, the definition's own text, its credited twin's) for every file it renders: its output
    first, labeled by the path it renders to, then each supporting file."""
    if defn.kind is Kind.AGENTS_FILE:
        return [(defn.name, defn.body, sentinel.body)]
    pairs = [(str(defn.output_path), defn.body, sentinel.body)]
    assert len(defn.files) == len(sentinel.files)
    pairs += [
        (str(defn.file_output_path(file)), file.body, twin.body) for file, twin in zip(defn.files, sentinel.files)
    ]
    return pairs


def _in_selection(defn: Definition, ctx: Render) -> bool:
    """Whether `ctx`'s selection carries `defn`: a definition it ships, or the agents file every selection
    has."""
    return defn.kind is Kind.AGENTS_FILE or ctx.plugin.ships(defn.name)


def _definition_sources() -> dict[str, str]:
    """Each definition module's dotted name, mapped to its source text."""
    return {
        ".".join(path.relative_to(_PACKAGE.parent).with_suffix("").parts): path.read_text(encoding="utf-8")
        for path in definition_paths()
    }


def _uncredited_shared_paragraphs(sources: dict[str, str]) -> list[str]:
    """Every prose unit two or more outputs of one plugin write out rather than take from a constant, a
    slot constant or a text function: the unit survives each one's credited render unchanged."""
    found: dict[str, None] = {}
    for ctx in _SELECTION_RENDERS:
        written: dict[bytes, list[str]] = {}
        for module, source in sources.items():
            rendered = _source_definitions(source, module=module, credited=False)
            credited = _source_definitions(source, module=module, credited=True)
            assert len(rendered) == len(credited)
            for defn, sentinel in zip(rendered, credited):
                if not _in_selection(defn, ctx):
                    continue
                for label, literal_body, credited_body in _outputs(defn, sentinel):
                    literal = _prose_units(filled_text(literal_body, defn, ctx, where=label)) & _prose_units(
                        filled_text(credited_body, sentinel, ctx, where=label)
                    )
                    for unit in literal:
                        written.setdefault(unit, []).append(label)
        found.update(
            (f"written out in {', '.join(written[unit])}: {unit.decode()[:120]}", None)
            for unit in sorted(written)
            if len(written[unit]) > 1
        )
    return list(found)


def test_a_paragraph_two_outputs_carry_has_one_source() -> None:
    sources = _definition_sources()
    found = _uncredited_shared_paragraphs(sources)
    assert found == [], "\n".join(found)


_FIXTURE_HEAD = (
    "from devpro import clauses\nfrom devpro.definition import Definition\nfrom devpro.vocabulary import Kind\n"
)
_SKILL_FIXTURE_HEAD = (
    "from devpro import clauses\nfrom devpro.definition import Definition, SkillFile\n"
    "from devpro.vocabulary import Kind\n"
)


def _fixture_module(*bodies: tuple[str, str], head: str = "") -> str:
    """A definition-module source of one command per (name, body source text)."""
    entries = "".join(f'Definition(name="{name}", kind=Kind.COMMAND, body={body}),' for name, body in bodies)
    return f"{_FIXTURE_HEAD}{head}DEFINITIONS = ({entries})\n"


def _skill_fixture_module(*file_bodies: str) -> str:
    """A definition-module source of one skill whose supporting files carry `file_bodies`."""
    names = ("one", "two", "three")
    entries = "".join(
        f'SkillFile(path="references/{names[index]}.md", body={body}),' for index, body in enumerate(file_bodies)
    )
    return (
        f'{_SKILL_FIXTURE_HEAD}DEFINITIONS = (Definition(name="s", kind=Kind.SKILL, description="a skill", '
        f'body="Own router.", files=({entries})),)\n'
    )


def test_a_paragraph_written_out_in_two_outputs_is_found_and_a_constant_is_not() -> None:
    sources = {
        "fixture.a": _fixture_module(("a", 'f"Own a.\\n\\nWritten out twice.\\n\\n{clauses.DISSENT}"')),
        "fixture.b": _fixture_module(("b", 'f"Written out twice.\\n\\n{clauses.DISSENT}\\n\\nOwn b."')),
        "fixture.group": _fixture_module(
            ("c", "f\"{_SHARED}\\n\\n{_SLOT.format(word='one')}\""),
            ("d", "f\"{_SLOT.format(word='one')}\\n\\n{_SHARED}\""),
            ("e", '"Written out in one module twice."'),
            ("f", '"Written out in one module twice."'),
            head='_SHARED = "Shared through a constant."\n_SLOT = "A slot holding {word}."\n',
        ),
    }
    assert _uncredited_shared_paragraphs(sources) == [
        "written out in commands/e.md, commands/f.md: Written out in one module twice.",
        "written out in commands/a.md, commands/b.md: Written out twice.",
    ]


def test_a_paragraph_two_supporting_files_write_out_is_found() -> None:
    """A skill's references are outputs too: one of them pasting a paragraph another holds is the same
    defect, named by the path it renders to."""
    sources = {
        "fixture.skill": _skill_fixture_module(
            '"Written out twice."',
            'f"{clauses.DISSENT}\\n\\nWritten out twice."',
        )
    }
    assert _uncredited_shared_paragraphs(sources) == [
        "written out in skills/s/references/one.md, skills/s/references/two.md: Written out twice."
    ]


# A prompt delivers each shared span once: no clause reached twice, no paragraph written twice.

_CLAUSE_GRAPH = clause_graph((_PACKAGE / "clauses.py").read_text(encoding="utf-8"))
_HARNESS_STRINGS = {hole(part) for part in (*HarnessText, *PluginText)}
# A reference names one definition, like the scratch directory's name names one directory and the plugin
# name one plugin: a sentence's word, not a span a prompt could deliver twice.
_SENTENCE_HOLES = (
    frozenset(
        name for name, value in vars(devpro.clauses).items() if isinstance(value, str) and value in _HARNESS_STRINGS
    )
    | {devpro.clauses.ref.__name__, devpro.clauses.optional_ref.__name__}
    | {
        name
        for name, value in vars(devpro.clauses).items()
        if isinstance(value, str) and value in set(devpro.clauses.VALUE_CONSTANTS)
    }
)


@dataclass(frozen=True)
class _PromptOutput:
    """One rendered file: its label, its text filled under the claude render, and the clause roots its
    body names. `loads` marks a command's or skill's own body, whose `@` lines can load another
    output; `path` is None for the agents file, which no `@` line can name."""

    label: str
    path: PurePosixPath | None
    text: str
    roots: tuple[ClauseRoot, ...]
    loads: bool


def _prompts(sources: dict[str, str]) -> list[list[_PromptOutput]]:
    """Every prompt of every plugin: an output with that plugin's installed agents file, and for a command
    or skill body each output of the plugin an `@` line of it names, transitively; the agents file's own
    output is a prompt alone."""
    prompts = []
    for ctx in _SELECTION_RENDERS:
        outputs = []
        for module, source in sources.items():
            roots = body_roots(source, _CLAUSE_GRAPH)
            for defn in _source_definitions(source, module=module, credited=False):
                if not _in_selection(defn, ctx):
                    continue
                keys = (None, *(file.path for file in defn.files))
                defn_outputs = _outputs(defn, defn)
                assert len(keys) == len(defn_outputs)
                for key, (label, body, _) in zip(keys, defn_outputs):
                    outputs.append(
                        _PromptOutput(
                            label=label,
                            path=None if defn.kind is Kind.AGENTS_FILE else PurePosixPath(label),
                            text=filled_text(body, defn, ctx, where=label),
                            roots=roots[defn.name, key],
                            loads=key is None and defn.kind in (Kind.COMMAND, Kind.SKILL),
                        )
                    )
        agents_file = [output for output in outputs if output.path is None]
        prompts += [
            [output, *(_loaded(output, outputs) if output.loads else ()), *(agents_file if output.path else ())]
            for output in outputs
        ]
    return prompts


def _loaded(output: _PromptOutput, outputs: list[_PromptOutput]) -> list[_PromptOutput]:
    """The outputs `output`'s `@` lines name, and those named by the `@` lines of each such output that
    loads, transitively, each once in first-reached order and never `output` itself. A line names an
    output when its path ends in the output's."""
    reached: list[_PromptOutput] = []
    pending = [output]
    while pending:
        current = pending.pop(0)
        named = [PurePosixPath(line[1:].strip()).parts for line in current.text.splitlines() if line.startswith("@")]
        for parts in named:
            for target in outputs:
                if target.path is None or parts[-len(target.path.parts) :] != target.path.parts:
                    continue
                if target is output or target in reached:
                    continue
                reached.append(target)
                if target.loads:
                    pending.append(target)
    return reached


def _double_clause_deliveries(sources: dict[str, str]) -> list[str]:
    """Each clause a prompt reaches twice, named with the prompt and both chains that reach it, each finding
    once however many selections deliver the prompt."""
    found = []
    for prompt in _prompts(sources):
        rooted = [(output.label, output.roots) for output in prompt]
        for node, *reaches in repeated_clause_reaches(_CLAUSE_GRAPH, rooted, uncounted=_SENTENCE_HOLES):
            paths = " | ".join(f"{label}: {' → '.join(chain)}" for label, chain in reaches)
            found.append(f"{prompt[0].label}: {node} reached twice — {paths}")
    return list(dict.fromkeys(found))


def _double_paragraphs(sources: dict[str, str]) -> list[str]:
    """Each prose unit a prompt carries twice, named with the prompt, each finding once however many
    selections deliver the prompt."""
    found = []
    for prompt in _prompts(sources):
        counts = Counter(unit for output in prompt for unit in _prose_unit_list(output.text))
        found += [
            f"{prompt[0].label}: written twice: {unit.decode()[:120]}" for unit, count in counts.items() if count > 1
        ]
    return list(dict.fromkeys(found))


@pytest.mark.parametrize("check", [_double_clause_deliveries, _double_paragraphs])
def test_no_prompt_delivers_a_span_twice(check: Callable[[dict[str, str]], list[str]]) -> None:
    sources = _definition_sources()
    assert sum(prompt[0].path is None for prompt in _prompts(sources)) == len(_SELECTION_RENDERS)
    found = check(sources)
    assert found == [], "\n".join(found)


def test_a_paragraph_the_agents_file_and_an_agent_both_write_is_refused() -> None:
    source = (
        f"{_FIXTURE_HEAD}from devpro.vocabulary import ALL\n"
        "DEFINITIONS = (\n"
        'Definition(name="f", kind=Kind.AGENTS_FILE, body="Written in both.\\n\\nOwn file text."),\n'
        'Definition(name="a", kind=Kind.AGENT, description="an agent", tools=ALL, category="stem-expert", '
        'body="Own agent text.\\n\\nWritten in both."),\n'
        ")\n"
    )
    assert _double_paragraphs({"fixture.both": source}) == ["agents/a.md: written twice: Written in both."]


def _chain_output(name: str, *loads: str) -> _PromptOutput:
    text = "\n".join(f"@commands/{target}.md" for target in loads)
    return _PromptOutput(
        label=f"commands/{name}.md", path=PurePosixPath(f"commands/{name}.md"), text=text, roots=(), loads=True
    )


def test_loaded_follows_at_lines_transitively() -> None:
    a, b, c = _chain_output("a", "b"), _chain_output("b", "c"), _chain_output("c")
    assert _loaded(a, [a, b, c]) == [b, c]


def test_loaded_terminates_on_a_cycle() -> None:
    a, b = _chain_output("a", "b"), _chain_output("b", "a")
    assert _loaded(a, [a, b]) == [b]


def test_a_clause_a_composite_already_delivers_is_refused_with_both_paths() -> None:
    sources = {
        "fixture.a": _fixture_module(("a", 'f"{clauses.CODE_PRINCIPLES_CODER}\\n\\n{clauses.MACHINE_GUARANTEES}"'))
    }
    assert _double_clause_deliveries(sources) == [
        "commands/a.md: MACHINE_GUARANTEES reached twice — "
        "commands/a.md: CODE_PRINCIPLES_CODER → MACHINE_GUARANTEES_CODER → MACHINE_GUARANTEES | "
        "commands/a.md: MACHINE_GUARANTEES"
    ]


def test_a_clause_passed_to_a_parameter_interpolated_twice_is_refused() -> None:
    sources = {"fixture.a": _fixture_module(("a", 'f"{clauses.kb_orientation_docs(when=clauses.DISSENT)}"'))}
    assert _double_clause_deliveries(sources) == [
        "commands/a.md: DISSENT reached twice — commands/a.md: DISSENT | commands/a.md: DISSENT"
    ]


def test_carried_clauses_maps_each_definition_to_the_clauses_its_call_names() -> None:
    source = (
        f"{_SKILL_FIXTURE_HEAD}DEFINITIONS = ("
        'Definition(name="c", kind=Kind.COMMAND, body=f"{clauses.kb_orientation_docs(when=clauses.DISSENT)}"),'
        'Definition(name="s", kind=Kind.SKILL, description="a skill", body="Own router.", '
        'files=(SkillFile(path="references/one.md", body=clauses.MACHINE_GUARANTEES),)),'
        ")\n"
    )
    assert carried_clauses(source) == {"c": {"kb_orientation_docs", "DISSENT"}, "s": {"MACHINE_GUARANTEES"}}


@pytest.mark.parametrize("walk", [carried_clauses, lambda source: body_roots(source, _CLAUSE_GRAPH)])
def test_a_definition_name_that_is_not_a_literal_is_refused_alike(walk: Callable[[str], object]) -> None:
    source = f'{_FIXTURE_HEAD}_NAME = "a"\nDEFINITIONS = (Definition(name=_NAME, kind=Kind.COMMAND, body="Own."),)\n'
    with pytest.raises(ValueError, match="name= is not a string literal"):
        walk(source)


@pytest.mark.parametrize(
    "call, expected",
    [
        (
            "clauses.machine_guarantees()",
            [
                "commands/a.md: MACHINE_GUARANTEES_FRAME reached twice — "
                "commands/a.md: machine_guarantees → MACHINE_GUARANTEES_FRAME | "
                "commands/a.md: MACHINE_GUARANTEES_FRAME"
            ],
        ),
        ("clauses.machine_guarantees(frame=clauses.DISSENT)", []),
    ],
)
def test_a_default_delivers_its_constant_only_where_the_call_passes_none(call: str, expected: list[str]) -> None:
    sources = {"fixture.a": _fixture_module(("a", f'f"{{{call}}}\\n\\n{{clauses.MACHINE_GUARANTEES_FRAME}}"'))}
    assert _double_clause_deliveries(sources) == expected


def test_a_command_repeating_a_clause_the_output_it_loads_carries_is_refused() -> None:
    source = (
        f"{_FIXTURE_HEAD}from devpro.vocabulary import ALL\n"
        "DEFINITIONS = (\n"
        'Definition(name="a", kind=Kind.AGENT, description="an agent", tools=ALL, category="stem-expert", '
        'body=f"Own agent text.\\n\\n{clauses.DISSENT}"),\n'
        'Definition(name="c", kind=Kind.COMMAND, '
        'body=f"@{clauses.PROJECT_HARNESS_DIR}/agents/a.md\\n\\n{clauses.DISSENT}"),\n'
        ")\n"
    )
    sources = {"fixture.loading": source}
    assert _double_clause_deliveries(sources) == [
        "commands/c.md: DISSENT reached twice — commands/c.md: DISSENT | agents/a.md: DISSENT"
    ]
    assert _double_paragraphs(sources) == [f"commands/c.md: written twice: {devpro.clauses.DISSENT[:120]}"]


def test_a_paragraph_one_output_writes_twice_is_refused() -> None:
    sources = {"fixture.a": _fixture_module(("a", '"Written twice.\\n\\nOwn.\\n\\nWritten twice."'))}
    assert _double_paragraphs(sources) == ["commands/a.md: written twice: Written twice."]


def test_a_thematic_break_written_twice_is_not_a_paragraph() -> None:
    sources = {"fixture.a": _fixture_module(("a", '"Own.\\n\\n---\\n\\nMore.\\n\\n---\\n\\nLast."'))}
    assert _double_paragraphs(sources) == []


def test_the_import_graph_is_acyclic() -> None:
    def module_name(path: str) -> str:
        parts = PurePosixPath(path).with_suffix("").parts
        return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)

    graph = {
        module_name(path): {name for name in _imported(tree) if name.startswith("devpro")} for path, tree in _modules()
    }
    done: set[str] = set()

    def visit(module: str, trail: tuple[str, ...]) -> None:
        assert module not in trail, f"import cycle: {' -> '.join((*trail, module))}"
        if module not in done:
            for target in sorted(graph.get(module, ())):
                visit(target, (*trail, module))
            done.add(module)

    for module in sorted(graph):
        visit(module, ())
