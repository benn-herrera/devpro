"""paragraph/sentence rules• prompt double-delivery"""

from collections.abc import Callable

import pytest

import devpro
import devpro.clauses
from devpro.context import Render
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.render import filled_body
from tests._structure import body_roots, carried_clauses
from tests.conftest import PLAIN

from .conftest import (
    _ALL_INHERIT,
    _CLAUDE_RENDER,
    _CLAUSE_GRAPH,
    _FIXTURE_HEAD,
    _SELECTION_RENDERS,
    _SKILL_FIXTURE_HEAD,
    RENDERED_DEFINITION_LINE_CAP,
    Discovered,
    _chain_output,
    _definition_sources,
    _double_clause_deliveries,
    _double_paragraphs,
    _fixture_module,
    _loaded,
    _prompts,
    _repeatable_sentence,
    _sentence_list,
    _skill_fixture_module,
    _uncredited_shared_paragraphs,
)


def test_the_claude_development_skill_names_the_plugins_agents_directory(discovered: Discovered) -> None:
    """The claude session seat reading the development skill has no other statement of where the plugin's
    agent files live, so a dispatch from the skill could name the directory only by guessing; the skill's
    body carries the sentence naming it, under a project install and for the user alike, and claude
    supplies it alone. Opencode and mage give the field nothing, so the paragraph drops whole there,
    leaving no empty one behind."""
    [development] = [defn for _, defn in discovered if defn.name == "development"]
    sentence = CLAUDE.agents_path
    under_claude = filled_body(
        development, Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    )
    under_opencode = filled_body(
        development, Render(harness=OPENCODE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)
    )
    assert OPENCODE.agents_path == ""
    assert "`.claude/skills/devpro/agents/`" in sentence
    assert "`~/.claude/skills/devpro/agents/`" in sentence
    assert f"\n\n{sentence}\n\n" in under_claude
    assert sentence not in under_opencode
    assert "\n\n\n" not in under_opencode


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


@pytest.mark.parametrize(
    "body, expected",
    [
        ("Run 2. Then stop.", ["Run 2.", "Then stop."]),
        ("1. Own text.", ["Own text."]),
    ],
)
def test_a_number_inside_a_sentence_is_prose_and_an_opening_marker_is_not(body: str, expected: list[str]) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: the marker strip was unanchored, so the first `N. `
    anywhere in a unit went — and a unit reading `Run 2. Then stop.` split as `Run` and `Then stop.`,
    unlike the same sentence without its number."""
    assert _sentence_list(body) == expected


def test_a_paragraph_two_outputs_carry_has_one_source() -> None:
    sources = _definition_sources()
    found = _uncredited_shared_paragraphs(sources)
    assert found == [], "\n".join(found)


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


@pytest.mark.parametrize("check", [_double_clause_deliveries, _double_paragraphs])
def test_no_prompt_delivers_a_span_twice(check: Callable[[dict[str, str]], list[str]]) -> None:
    sources = _definition_sources()
    assert sum(prompt[0].path is None for prompt in _prompts(sources)) == len(_SELECTION_RENDERS)
    found = check(sources)
    assert found == [], "\n".join(found)


def test_the_paragraph_check_finds_nothing_in_the_real_renderings() -> None:
    """The parametrized case above reaches this check only through the real tree as one of two; on its
    own, it names the grain the renderings are judged at — the prompts' 19,192 sentences, not a
    fixture's handful."""
    assert _double_paragraphs(_definition_sources()) == []


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
    assert _double_paragraphs(sources) == [
        "commands/c.md: written twice: If you believe a directive would produce technically incorrect output, state the "
        "concern and your recommended alternativ",
        "commands/c.md: written twice: A directive whose result would break an invariant the project states, where the "
        "directive does not itself say it changes",
        "commands/c.md: written twice: An order whose result satisfies every stated requirement but whose only possible "
        "variation is form is the case to disput",
    ]


def test_a_command_repeating_a_sentence_of_an_agent_it_loads_is_refused() -> None:
    """`clauses.TEST_PRECONDITION`. The defect: the check counted a body's paragraphs, so a command
    repeating one sentence of another rendering was no finding, and shared prose could diverge
    between two outputs unseen. The sentence is read off the definitions' own text and stands in a
    list item of each output, so no paragraph holds it twice and only the sentence count sees it."""
    repeated = _repeatable_sentence()
    source = "\n".join(
        [
            f"{_FIXTURE_HEAD}from devpro.vocabulary import ALL",
            "DEFINITIONS = (",
            'Definition(name="a", kind=Kind.AGENT, description="an agent", tools=ALL, category="stem-expert", '
            f'body="- Own agent text. {repeated}"),',
            'Definition(name="c", kind=Kind.COMMAND, '
            f'body="@{devpro.clauses.PROJECT_HARNESS_DIR}/agents/a.md\\n\\n- Own command text. {repeated}"),',
            ")",
        ]
    )
    sources = {"fixture.loading": source}
    assert _double_clause_deliveries(sources) == []
    assert _double_paragraphs(sources) == [f"commands/c.md: written twice: {repeated[:120]}"]


def test_a_paragraph_one_output_writes_twice_is_refused() -> None:
    sources = {"fixture.a": _fixture_module(("a", '"Written twice.\\n\\nOwn.\\n\\nWritten twice."'))}
    assert _double_paragraphs(sources) == ["commands/a.md: written twice: Written twice."]


def test_a_thematic_break_written_twice_is_not_a_paragraph() -> None:
    sources = {"fixture.a": _fixture_module(("a", '"Own.\\n\\n---\\n\\nMore.\\n\\n---\\n\\nLast."'))}
    assert _double_paragraphs(sources) == []
