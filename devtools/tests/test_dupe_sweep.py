"""Tests for the `dupe_sweep` package — the one-idea-two-places candidate sweep.

Corpus-shaped cases pass a `{path: source}` mapping straight to the extractors
rather than building a tree — the sweep reads its corpus from git, and a
filesystem is not on the path between a source file and a candidate.
"""

import ast
import io

import pytest

from devtools.dupe_sweep import (
    cli,
    clustering,
    constants,
    definition_text,
    doc_sentences,
    normalization,
    passes,
    python_corpus,
    report,
    shapes,
)
from devtools.dupe_sweep.corpus import SweepError

KNOWN_ANSWER_SENTENCE = (
    "If you cannot complete the task as scoped, report immediately rather than proceeding with assumptions."
)
NEAR_COPY = (
    "If you cannot complete the task as scoped (missing context, ambiguous requirements, file conflict"
    " risk), report this immediately rather than proceeding with assumptions."
)


def unit(text: str, *, path: str = "a.md", line: int = 1) -> clustering.Unit:
    return clustering.Unit(path, line, "", text, normalization.prose_tokens(text))


# ── the metric ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "left, right, floor, ceiling",
    [
        ("the same sentence exactly", "the same sentence exactly", 1.0, 1.0),
        # The known near-copy: an inserted parenthetical and one added word.
        (KNOWN_ANSWER_SENTENCE, NEAR_COPY, 0.90, 1.0),
        ("a sentence about parsing markdown links", "an unrelated remark concerning venv layout", 0.0, 0.4),
    ],
)
def test_containment_scores_a_restatement_high_and_a_stranger_low(left, right, floor, ceiling):
    score = clustering.containment(normalization.prose_tokens(left), normalization.prose_tokens(right))
    assert floor <= score <= ceiling


def test_containment_is_symmetric():
    long_side = normalization.prose_tokens("the rule holds at every seat and in every definition without exception")
    short_side = normalization.prose_tokens("the rule holds at every seat")
    assert clustering.containment(long_side, short_side) == clustering.containment(short_side, long_side)


# ── sentence-unit clustering (docstrings and comments) ───────────────────────


def test_seven_copies_report_as_one_candidate_with_seven_sites():
    copies = [unit(KNOWN_ANSWER_SENTENCE, path=f"t{index}.md") for index in range(7)]
    found = clustering.clusters(copies, **passes.DOC_DEFAULTS)
    assert len(found) == 1
    assert len(found[0].members) == 7


def test_the_representative_is_the_shortest_statement_of_the_shared_idea():
    short = unit("Declare the files you will modify before you start, and stay inside that set.", path="a.md")
    long = unit(
        "Declare the files you will modify before you start, and stay inside that set, because another"
        " agent may be editing one.",
        path="b.md",
    )
    found = clustering.clusters([long, short], **passes.DOC_DEFAULTS)
    assert len(found) == 1
    assert found[0].representative.path == "a.md"


def test_a_short_span_inside_a_long_one_does_not_chain_them():
    """`length_ratio`'s job. Containment alone links a fragment to everything that
    quotes it, and the cluster becomes a rope rather than a finding."""
    fragment = unit("never invoke the compiler directly when a target covers it", path="a.md")
    quoting = unit(
        "Use the project's runner targets for every build, test, lint and integration operation, and"
        " never invoke the compiler directly when a target covers it, whichever runner the project has"
        " chosen for itself and however tempting the naked command line looks.",
        path="b.md",
    )
    assert clustering.containment(fragment.tokens, quoting.tokens) == 1.0
    assert clustering.clusters([fragment, quoting], **passes.DOC_DEFAULTS) == []


def test_a_span_shorter_than_min_tokens_is_not_compared():
    pair = [unit("Stdlib-first, always.", path=f"t{index}.md") for index in range(2)]
    assert clustering.clusters(pair, **passes.DOC_DEFAULTS) == []


def test_the_same_units_in_any_order_render_the_same_report():
    units = [unit(KNOWN_ANSWER_SENTENCE, path=f"t{index}.md") for index in range(4)] + [
        unit(
            "A dependency is a permanent maintenance obligation, so justify it before you add one.", path=f"d{index}.md"
        )
        for index in range(3)
    ]

    def rendered(ordered):
        out = io.StringIO()
        report.render_clusters("t", clustering.clusters(ordered, **passes.DOC_DEFAULTS), out=out)
        return out.getvalue()

    assert rendered(units) == rendered(list(reversed(units)))


def test_the_file_pair_tally_counts_a_pair_once_per_candidate():
    units = [
        unit(KNOWN_ANSWER_SENTENCE, path="a.md"),
        unit(KNOWN_ANSWER_SENTENCE, path="b.md"),
        unit("A dependency is a permanent maintenance obligation, so justify it before you add one.", path="a.md"),
        unit("A dependency is a permanent maintenance obligation, so justify it before adding one.", path="b.md"),
    ]
    found = clustering.clusters(units, **passes.DOC_DEFAULTS)
    assert report.file_pairs(found) == [(2, "a.md", "b.md")]


def test_hard_wrapped_prose_is_rejoined_before_it_is_split():
    numbered = [(10, "A rule that spans"), (11, "two physical lines."), (12, ""), (13, "A separate block.")]
    assert list(doc_sentences.block_sentences(numbered)) == [
        (10, "A rule that spans two physical lines."),
        (13, "A separate block."),
    ]


# ── prose tokens ─────────────────────────────────────────────────────────────


def test_a_chunk_marker_is_not_prose_and_a_code_span_is():
    assert normalization.prose_tokens('@!parallel-execution variant="platform"!@ Use `NSFileCoordinator` here.') == (
        "use",
        "nsfilecoordinator",
        "here",
    )


# ── python extraction ────────────────────────────────────────────────────────


TWO_SPELLINGS_OF_ONE_LOOP = {
    "one.py": (
        "def totals(rows):\n"
        "    '''A docstring the shape does not see.'''\n"
        "    out = {}\n"
        "    for row in rows:\n"
        "        if row.kind not in out:\n"
        "            out[row.kind] = 0\n"
        "        out[row.kind] += row.weight\n"
        "    return out\n"
    ),
    "two.py": (
        "def tally(entries):\n"
        "    counts = {}\n"
        "    for entry in entries:\n"
        "        if entry.sort not in counts:\n"
        "            counts[entry.sort] = 0\n"
        "        counts[entry.sort] += entry.size\n"
        "    return counts\n"
    ),
}


def test_two_spellings_of_one_loop_are_one_candidate():
    found = clustering.clusters(
        shapes.shape_units(TWO_SPELLINGS_OF_ONE_LOOP), **{**passes.CODE_DEFAULTS, "min_tokens": 10}
    )
    assert [member.site for member, _ in found[0].members] == ["one.py:1 totals()", "two.py:1 tally()"]


def test_unlike_functions_are_not_a_candidate():
    files = {
        "one.py": TWO_SPELLINGS_OF_ONE_LOOP["one.py"],
        "two.py": "def shout(text):\n    return text.upper()\n",
    }
    assert clustering.clusters(shapes.shape_units(files), **{**passes.CODE_DEFAULTS, "min_tokens": 10}) == []


def test_a_method_is_a_unit_and_a_nested_function_is_not():
    files = {
        "one.py": (
            "class Store:\n"
            "    def put(self, key):\n"
            "        def inner(value):\n"
            "            return value\n"
            "        return inner(key)\n"
        )
    }
    assert [unit.label for unit in shapes.shape_units(files)] == ["Store.put()"]


def test_a_docstring_and_a_comment_both_state_rules():
    files = {"one.py": '"""A module rule.\n\nA second sentence.\n"""\n\n# A commented rule.\nx = 1\n'}
    units = doc_sentences.doc_units(files)
    assert [(unit.label, unit.text) for unit in units] == [
        ("module docstring", "A module rule."),
        ("module docstring", "A second sentence."),
        ("comment", "A commented rule."),
    ]


def test_a_module_that_does_not_parse_is_reported_and_skipped(caplog):
    assert shapes.shape_units({"broken.py": "def (:\n"}) == []
    assert "does not parse" in caplog.text


# ── definition-module string literals as sentence units ──────────────────────


def test_a_sentence_two_definition_modules_carry_as_a_literal_reaches_the_report(monkeypatch):
    """Defect, before the change: `doc_units` reads docstrings and comments, `constants` reads
    module-level bindings as values, so two literals stating one rule were no candidate and the
    shared prose could drift between them unseen. Mounted through the pass, because a unit source
    the pass does not read is the same defect with a module's worth of code around it."""
    sentence = "A dispatch that outlives its task is a leak the operator cannot see until the queue drains."
    files = {f"devpro/definitions/agents/{name}.py": f'BODY = """{sentence}"""\n' for name in ("one", "two")}
    monkeypatch.setattr(passes, "code_corpus", lambda *, rev: files)
    out = io.StringIO()
    passes.python_pass(rev=None, settings=passes.CODE_DEFAULTS, out=out)
    under_one_rule = out.getvalue().split("\n## one rule, two homes", 1)[1].split("\n## one word")[0]
    assert sentence in under_one_rule
    assert [line.strip() for line in under_one_rule.splitlines() if "of a" not in line and "devpro/" in line] == [
        "100%  devpro/definitions/agents/one.py:1 string literal at 1",
        "100%  devpro/definitions/agents/two.py:1 string literal at 1",
    ]


def test_a_literal_is_rejoined_across_its_hard_wrap_and_split_like_a_docstring():
    files = {"devpro/clauses.py": 'RULE = """A rule that spans\\ntwo physical lines. A second sentence."""\n'}
    units = definition_text.definition_text_units(files)
    assert [unit.text for unit in units] == ["A rule that spans two physical lines.", "A second sentence."]


def test_a_literals_later_blocks_report_at_their_own_lines_not_the_literals():
    """Defect, before numbering: `block_sentences` was handed the literal as a single numbered
    line, so the whole literal — every block in it — reported at its opening line."""
    files = {"devpro/clauses.py": 'RULE = """A rule.\n\nA second block two lines down."""\n'}
    units = definition_text.definition_text_units(files)
    assert [(unit.line, unit.text) for unit in units] == [(1, "A rule."), (3, "A second block two lines down.")]


@pytest.mark.parametrize(
    "source",
    [
        '"""A module rule."""\n',
        'class Store:\n    """A store rule."""\n',
        'def f():\n    """A function rule."""\n',
        'async def f():\n    """An async rule."""\n',
        '"""\nA rule that starts on the docstring\'s second line.\n"""\n',
        'def f():\n    """A rule."""\n    def g():\n        """A nested rule."""\n',
        'x = 1\n# not a docstring\ny = "a literal"\n',
    ],
)
def test_the_literals_read_as_docstrings_and_the_literals_skipped_as_them_are_one_set(source):
    """Defect, before the one helper: `docstring_nodes` walked for docstrings a second time, so a
    shape one walk recognized and the other did not reported a docstring against itself."""
    tree = ast.parse(source)
    read_by_doc_units = {id(literal) for literal, _, _, _ in doc_sentences.docstrings(tree)}
    skipped_as_docstring = {id(literal) for literal in definition_text._literals(tree)} & read_by_doc_units
    assert skipped_as_docstring == set()
    assert len(read_by_doc_units) == source.count('"""') // 2


@pytest.mark.parametrize(
    "path",
    [
        "devpro/definitions/agents/one.py",
        "devpro/harnesses/one.py",
        "devpro/clauses.py",
        "devtools/notes.py",  # outside the definition modules
    ],
)
def test_only_the_definition_modules_contribute_literals(path):
    files = {path: 'BODY = """A sentence held as a literal."""\n'}
    assert [unit.text for unit in definition_text.definition_text_units(files)] == (
        ["A sentence held as a literal."] if path != "devtools/notes.py" else []
    )


def test_a_docstring_is_not_also_read_as_a_literal():
    """Defect, before skipping docstrings: they are `ast.Constant`s, so each reported against
    itself as one candidate in every module carrying a docstring."""
    files = {"devpro/clauses.py": '"""A module rule stated once."""\n\n# A comment.\nX = 1\n'}
    assert [unit.text for unit in definition_text.definition_text_units(files)] == []


def test_a_literal_with_no_whitespace_is_not_prose():
    files = {"devpro/clauses.py": 'PLACEHOLDER = "@!hrn-recipe-rule!@"\nDIR = "kb-tools"\nBODY = "One word."\n'}
    assert [unit.text for unit in definition_text.definition_text_units(files)] == ["One word."]


@pytest.mark.parametrize(
    "source, expected",
    [
        ("WIDTH = 72\n", [("WIDTH", "72")]),
        ("TAG: str = 'survey'\n", [("TAG", "survey".join("''"))]),
        ("KINDS = ('clm', 'exp')\n", [("KINDS", "('clm', 'exp')")]),
        ("ENABLED = True\nEMPTY = ''\nZERO = 0\n", []),  # trivia
        ("VALUE = compute()\n", []),  # not a literal
        ("def f():\n    INNER = 4096\n", []),  # not module level
    ],
)
def test_module_level_literals_are_collected_and_trivia_is_not(source, expected):
    found = constants.constants({"one.py": source})
    assert [(constant.name, constant.value) for constant in found] == expected


def test_one_name_in_two_modules_is_a_candidate():
    found = constants.constants({"one.py": "EXCERPT_MAX_CHARS = 240\n", "two.py": "EXCERPT_MAX_CHARS = 240\n"})
    (why, sites), *rest = constants.constant_candidates(found)
    assert why == "one name bound in 2 modules: EXCERPT_MAX_CHARS"
    assert [site.path for site in sites] == ["one.py", "two.py"]
    assert rest == [], "the same sites must not be reported again as a repeated value"


def test_two_unrelated_uses_of_a_small_number_are_not_a_candidate():
    found = constants.constants({"one.py": "EXIT_USAGE = 2\n", "two.py": "EDGE_STROKE_WIDTH = 2\n"})
    assert constants.constant_candidates(found) == []


def test_one_distinctive_value_under_similar_names_is_a_candidate():
    found = constants.constants(
        {"one.py": "DEFAULT_SILENCE_SECONDS = 600\n", "two.py": "DEFAULT_SILENCE_SECONDS_LIMIT = 600\n"}
    )
    assert [why for why, _ in constants.constant_candidates(found)] == [
        "one value in 2 modules under similar names: 600"
    ]


# ── the command line ─────────────────────────────────────────────────────────


def test_a_pass_that_finds_candidates_still_exits_zero(monkeypatch):
    """`clauses.TEST_PRECONDITION`: candidates are not verdicts, so a pass that found one still
    exits 0 — a nonzero exit would be the judgment the sweep refuses to make, and would stand in
    the way of every checkpoint it runs at. The run that fails under it is this one with
    `cli.main` exiting on the report's emptiness instead of the pass's completion: a sweep whose
    mounted corpus holds no candidate exits 1 there, and a pass that found its candidate exits 0.

    The corpus is mounted: the sweep reads its own from git — the working tree, so the uncommitted
    edits it is run at are swept — and judging the exit contract of a pass that reads this tree is
    plumbing that carries no fact about the tree. What a candidate renders as is the report tests'
    subject above.
    """
    sentence = "A dispatch that outlives its task is a leak the operator cannot see until the queue drains."
    files = {f"devpro/definitions/agents/{name}.py": f'BODY = """{sentence}"""\n' for name in ("one", "two")}
    monkeypatch.setattr(passes, "code_corpus", lambda *, rev: files)
    out = io.StringIO()
    assert cli.main(["python"], out=out) == 0
    assert "candidates, not verdicts" in out.getvalue()


def test_an_unreadable_revision_exits_two_rather_than_reporting_a_clean_tree(monkeypatch):
    """`clauses.TEST_PRECONDITION`: a revision git cannot resolve is a sweep that did not run, and
    one reporting it as a tree holding no candidate tells the checkpoint it runs at that the tree
    is clean. The run that fails under it is this one with `cli.main` returning 0 where `python_pass`
    raised `SweepError` — the refusal falling through to the pass's exit status instead of the
    error's.

    The refusal is mounted at the corpus read, the one seam `SweepError` crosses: this test names
    the revision and asks the sweep to refuse it, and reading the sweep's own tree at a real
    revision is the sibling test's single run, not a second one here.
    """
    asked: list[str | None] = []

    def refuse(*, rev):
        asked.append(rev)
        raise SweepError("git ls-tree failed: unknown revision")

    monkeypatch.setattr(passes, "code_corpus", refuse)
    out = io.StringIO()
    assert cli.main(["python", "--rev", "no-such-revision"], out=out) == 2
    assert asked == ["no-such-revision"]
    assert out.getvalue() == ""


def test_an_unreadable_revision_raises_sweeperror_in_the_corpus_conversion():
    """`clauses.TEST_PRECONDITION`: `_git` turns a git `CalledProcessError` — a revision git cannot
    resolve — into `SweepError`, and that conversion is what keeps an unreadable revision from reading
    as a tree holding no candidate. A regression that let the raw error through, or returned an empty
    corpus instead, ships a wrong verdict green: the checkpoint the sweep runs at is told the tree is
    clean where it never ran. The run that fails under it is this one with `code_corpus` raising the
    `CalledProcessError` unconverted, or returning `{}` — a bad revision raises `SweepError`.

    This exercises `corpus._git`'s conversion directly, through the real `code_corpus`; the sibling
    `test_an_unreadable_revision_exits_two_rather_than_reporting_a_clean_tree` mounts the refusal at the
    corpus seam and asserts the CLI's mapping of that error to its exit status. The conversion's own
    verdict, not the CLI's handling of it, is this test's subject.
    """
    with pytest.raises(SweepError):
        python_corpus.code_corpus(rev="no-such-revision")


def test_an_unknown_pass_is_refused():
    with pytest.raises(SystemExit):
        cli.main(["structure"])
