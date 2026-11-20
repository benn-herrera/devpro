"""The selection in the render: each selection renders under each harness with every template filled and
every reference closed, membership is decided in one module and its member lists are validated against
discovery, an out-of-set reference refuses while an optional one drops its paragraph, and the agents
file reads the same whichever components are on.
"""

from __future__ import annotations

import dataclasses
import re

import pytest

from devpro.components import Components, selection
from devpro.context import Render, build_render, harness_named
from devpro.definition import Definition
from devpro.errors import InputError
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.harness import PLUGIN_MANIFEST, Harness
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.loading import load
from devpro.render import filled_body, render_agents_file, render_all
from devpro.vocabulary import Kind, optional_reference, reference
from tests.conftest import PLAIN, WITH_KBASE

_HARNESSES = sorted(load("devpro.harnesses", "HARNESS"))


@pytest.mark.parametrize("harness", _HARNESSES)
@pytest.mark.parametrize("components", [PLAIN, WITH_KBASE], ids=["plain", "with-kbase"])
def test_every_selection_renders_under_every_harness_with_nothing_left_unfilled(
    components: Components, harness: str
) -> None:
    """A plain reference outside the shipped set refuses the render, so this is also the closure test of
    each selection: one such reference fails it, naming the citing definition."""
    ctx = build_render(harness=harness, components=",".join(sorted(components.on)), family="claude")
    texts = [text for _, text in render_all(ctx)]
    texts.append(render_agents_file(harness_named(harness), components, scope="x"))
    leaks = [match for text in texts for match in re.findall(r"\{plugin\}|@![a-z0-9.-]+!@", text)]
    assert leaks == []


def test_a_component_naming_an_undiscovered_definition_refuses_every_render(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    misspelt = {"kbase": frozenset({"kbase", "kbse"})}
    monkeypatch.setattr("devpro.components.COMPONENTS", misspelt)
    with pytest.raises(InputError, match=re.escape("component 'kbase' names no discovered definition: kbse")):
        build_render(harness="claude", components="kbase", family="claude")


@pytest.mark.parametrize("name", ["nosuch", "development", "docdicer"])
def test_a_name_that_is_no_optional_component_is_refused(name: str) -> None:
    """A required definition ships already, so naming it asks for nothing: the components are the optional
    ones alone, and a refusal names them."""
    with pytest.raises(InputError, match=re.escape(f"unknown component '{name}'")):
        Components(on=frozenset({name}))
    with pytest.raises(InputError, match=re.escape("optional components are kbase")):
        selection(name)


def test_ships_reads_the_required_set_and_the_components_turned_on() -> None:
    """Every definition no component names ships whichever components are on; a component's member ships
    only with that component on."""
    assert PLAIN.ships("python-coder") and WITH_KBASE.ships("python-coder")
    assert not PLAIN.ships("kbase") and WITH_KBASE.ships("kbase")


def test_a_render_binds_its_harness_to_the_one_name() -> None:
    ctx = Render(harness=CLAUDE, plugin=WITH_KBASE, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    assert (ctx.bound_harness.plugin_dir, ctx.bound_harness.reference_prefix) == ("skills/devpro", "devpro:")
    manifest = next(file for file in ctx.bound_harness.rendered_files if file.path == PLUGIN_MANIFEST.path)
    assert manifest.marker == '"name": "devpro"'


def test_binding_fills_the_guardrail_registration_marker_and_leaves_other_braces() -> None:
    assert CLAUDE.guardrail is not None
    registration = dataclasses.replace(CLAUDE.guardrail.registration, marker='{"plugin": "{plugin}"}')
    probe = dataclasses.replace(CLAUDE, guardrail=dataclasses.replace(CLAUDE.guardrail, registration=registration))
    bound = probe.bound(PLAIN.name).guardrail
    assert bound is not None
    assert bound.registration.marker == '{"plugin": "devpro"}'


_PLAIN_RENDER = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))


def test_a_plain_reference_outside_the_shipped_set_refuses_naming_the_site_and_the_referent() -> None:
    defn = Definition(name="probe", kind=Kind.COMMAND, body=f"Hand it to {reference('kbase')}.")
    with pytest.raises(InputError, match=re.escape("definition 'probe': references 'kbase', which")):
        filled_body(defn, _PLAIN_RENDER)


def test_an_optional_reference_fills_where_its_referent_ships_and_drops_its_paragraph_where_not() -> None:
    body = (
        f"Before.\n\nAsk {optional_reference('kbase')} first.\n\n"
        f"Then {optional_reference('tech-writer')}, and more.\n\nAfter."
    )
    defn = Definition(name="probe", kind=Kind.COMMAND, body=body)
    assert filled_body(defn, _PLAIN_RENDER) == "Before.\n\nThen devpro:tech-writer, and more.\n\nAfter."
    assert filled_body(defn, dataclasses.replace(_PLAIN_RENDER, plugin=WITH_KBASE)) == (
        "Before.\n\nAsk devpro:kbase first.\n\nThen devpro:tech-writer, and more.\n\nAfter."
    )


@pytest.mark.parametrize("harness", [CLAUDE, OPENCODE], ids=lambda harness: harness.name)
@pytest.mark.parametrize("components", [PLAIN, WITH_KBASE], ids=["plain", "with-kbase"])
def test_each_selections_agents_file_carries_the_development_bullet(harness: Harness, components: Components) -> None:
    text = render_agents_file(harness, components, scope="x")
    development = f"{harness.bound(components.name).reference_prefix}development"
    assert f"load the `{development}` skill" in text


@pytest.mark.parametrize("harness", [CLAUDE, OPENCODE], ids=lambda harness: harness.name)
def test_the_agents_file_reads_the_same_whichever_components_are_on(harness: Harness) -> None:
    """`install-agents-file` takes no component list, so the block it writes and the block a
    component-flagged install writes are one text: two would rewrite each other on every run."""
    assert render_agents_file(harness, PLAIN, scope="x") == render_agents_file(harness, WITH_KBASE, scope="x")
