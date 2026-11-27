"""overlays• stock• step-down model"""

import dataclasses
import json
import re
from pathlib import Path, PurePosixPath

import pytest

import devpro
import devpro.clauses
from devpro.context import MODEL_MAP_TABLE, SETTINGS_FILE, MapSupply, Render, build_render, harnesses
from devpro.definition import Definition, SkillFile
from devpro.definitions import discover
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.family import Family
from devpro.harness import Harness
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.mage import HARNESS as MAGE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.install import INSTALL_SETTINGS
from devpro.loading import load
from devpro.render import filled_body, filled_text, render_all, render_skill_file, write_renders
from devpro.vocabulary import ALL, CATEGORIES, Kind, OptionalHarnessText, hole
from tests._structure import kbase_skill_output_paths
from tests.conftest import PLAIN, WITH_KBASE

from .conftest import (
    _ALL_INHERIT,
    _BAIT,
    _CLAUDE_RENDER,
    _INHERIT_SUPPLY,
    _LIST_OR_TABLE_LINE,
    _MAGE_MANIFEST,
    _MAGE_RENDER,
    _OMLX_SUPPLY,
    _OVERLAY,
    _SELECTIONS,
    _SKILLS_WITH_FILES,
    _STEP_DOWN_BODY,
    _TUNED,
    _TUNING_HOLES,
    Discovered,
    _baited_family_overlay,
    _baited_harness_text,
    _baited_optional_harness_text,
    _baited_scope_name,
    _baited_step_down_model,
    _clause_with_a_baited_harness_value,
    _found,
    _kbase_skill_render,
    _routed_references,
    _skill,
    _user_install_paths,
    _with_family_text,
)


def test_render_all_emits_every_file_of_a_shipped_skill_and_the_selection_drops_a_whole_definition() -> None:
    shipping = {path for path, _ in render_all(dataclasses.replace(_CLAUDE_RENDER, plugin=WITH_KBASE))}
    without = {path for path, _ in render_all(_CLAUDE_RENDER)}
    assert set(kbase_skill_output_paths()) <= shipping
    assert not any(path.parts[:2] == ("skills", "kbase") for path in without)


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


@pytest.mark.parametrize("harness", harnesses())
def test_the_installing_reference_names_the_settings_file_and_its_map_table(harness: str) -> None:
    """The page names the settings file's path and the map subtable to its reader, and the settings reader
    parses them by `SETTINGS_FILE` and `MODEL_MAP_TABLE`; the assertion is composed from those constants, so a
    rename of either that leaves the page naming a file or table the parser no longer reads fails here, not
    silently."""
    ctx = build_render(components="", harness=harness, family="claude")
    [text] = [text for path, text in render_all(ctx) if str(path).endswith("guide/references/installing.md")]
    assert f"~/{SETTINGS_FILE}" in text
    assert f"[<harness>.{MODEL_MAP_TABLE}]" in text


@pytest.mark.parametrize("harness", harnesses(), ids=lambda name: name)
def test_the_scratch_rule_names_the_one_scratch_directory(harness: str) -> None:
    """Each harness's scratch rule names the one scratch directory both guardrails allow, in the
    paragraph the clauses module carries."""
    rule = harnesses()[harness].scratch_rule
    assert f"`{devpro.clauses.PROJECT_TEMP_DIR}/`" in rule
    assert rule == devpro.clauses.SCRATCH_PARAGRAPH


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


@pytest.mark.parametrize("skill", _SKILLS_WITH_FILES, ids=lambda skill: skill.name)
def test_the_router_routes_to_every_reference_that_ships_and_no_other(skill: Definition) -> None:
    """A reference is read only when its route is reached and every route is a reference, so the two
    sets are one: a route naming a file the skill does not carry opens on nothing, and a file no route
    names is text no session ever reads."""
    routed = _routed_references(skill.body)
    assert routed == {file.path for file in skill.files}
    assert routed, "no route parsed from the table, so the comparison above would pass vacuously"


@pytest.mark.parametrize("harness", harnesses(), ids=lambda name: name)
def test_the_development_skill_names_the_target_that_counts_landed_plans(harness: str) -> None:
    """The section states a count, so it must name a recipe the runner carries: a target the skill names
    and the justfile lacks is a count its reader cannot read."""
    ctx = build_render(components="", harness=harness, family="claude")
    [text] = [text for path, text in render_all(ctx) if str(path).endswith("development/SKILL.md")]
    targets = set(re.findall(r"`just ([\w-]+)`", text))
    assert targets, "no `just` target parsed from the rendered section, so the check below would pass vacuously"
    justfile = Path(__file__).resolve().parents[2] / "justfile"
    recipes = set(re.findall(r"^([a-z][\w-]*) *[^\n:]*:", justfile.read_text(encoding="utf-8"), re.M))
    assert sorted(targets - recipes) == []


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


def test_each_family_pins_the_member_of_every_category() -> None:
    for family in load("devpro.families", "FAMILY").values():
        assert set(family.categories) == set(CATEGORIES)
