"""holes• unknown placeholder• reference prefix"""

import dataclasses
import json
import re
from pathlib import PurePosixPath

import pytest

import devpro
import devpro.clauses
from devpro.agents_file import is_marker_line
from devpro.components import Components
from devpro.context import Render
from devpro.definition import Definition, SkillFile
from devpro.errors import InputError
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.harness import Harness
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.render import definitions, filled_text, render_agents_file, render_all, render_definition
from devpro.vocabulary import (
    ALL,
    HarnessText,
    Kind,
    OptionalHarnessText,
    PluginText,
    TuningText,
    hole,
    optional_reference,
    reference,
)
from tests.conftest import PLAIN, WITH_KBASE

from .conftest import _ALL_INHERIT, _CLAUDE_RENDER, _NAMESPACED, _PREFIXED, _skill


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
