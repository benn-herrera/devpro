"""build_render• family• category• model"""

import dataclasses
import re
from pathlib import Path

import pytest

from devpro.cli import main
from devpro.context import MapSupply, Render, build_render, harnesses
from devpro.definition import Definition
from devpro.errors import InputError
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.harness import Harness
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.mage import HARNESS as MAGE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.render import filled_body
from devpro.vocabulary import CATEGORIES, HarnessText, Kind, PluginText, hole
from tests.conftest import PLAIN, settings_file

from .conftest import _ALL_INHERIT, _SUPPLIER


def test_a_render_takes_its_components_from_the_flag_alone(tmp_path: Path, monkeypatch) -> None:
    """`components` is the install's selection: a flagless render that read the file's value turned the
    component on and made the flag's "default none" help false wherever a settings file existed."""
    monkeypatch.setenv("DEVPRO_DEV", "1")
    settings = settings_file(tmp_path, '[claude]\ncomponents = "kbase"\n')
    from_file = tmp_path / "from-file"
    from_file.mkdir()
    main(["dev-render", "--out", str(from_file), "--harness=claude", f"--config-file={settings}"])
    assert not (from_file / "skills/kbase/SKILL.md").exists()
    from_flag = tmp_path / "from-flag"
    from_flag.mkdir()
    main(["dev-render", "--out", str(from_flag), "--components=kbase", "--harness=claude"])
    assert (from_flag / "skills/kbase/SKILL.md").is_file()


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


def test_the_project_wrapper_placeholder_fills_with_the_wrapper_a_claude_project_install_writes() -> None:
    """`clauses.TEST_PRECONDITION`. The defect: the closed set held no placeholder for the wrapper's
    path, so a body naming the wrapper a project install writes could not render it."""
    defn = Definition(name="probe", kind=Kind.COMMAND, body=f"run {hole(PluginText.PROJECT_WRAPPER)} here")
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    assert filled_body(defn, ctx) == "run .claude/skills/devpro/tools/devpro.sh here"


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
