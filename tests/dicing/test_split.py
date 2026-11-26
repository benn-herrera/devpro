"""Unit tests for the write pass's re-base: which lines of a section have no level to write at."""

import io

import pytest

from devpro.dicing.outline import plan_sections
from devpro.dicing.split import _overflow
from devpro.dicing.textfile import fence_flags


def _overflows(lines: list[str], *, deepest: int = 4) -> list[int]:
    """The offending lines of every section the document plans, in line order."""
    sections, ok = plan_sections(lines, err=io.StringIO(), deepest=deepest)
    assert ok
    fenced = fence_flags(lines)
    return [no for s in sections for no in _overflow(lines, s, fenced)]


@pytest.mark.parametrize(
    "lines, deepest, offending",
    [
        pytest.param(["# Doc", "## A", "######## Too deep"], 4, [3], id="one-level-past-the-last"),
        pytest.param(["# Doc", "## A", "###### Fine", "####### Also fine"], 4, [], id="the-last-level-is-writable"),
        pytest.param(
            ["# Doc", "## A", "######## One", "text", "######## Two"], 4, [3, 5], id="every-offender-in-a-section"
        ),
        pytest.param(
            ["# Doc", "## A", "######## One", "## B", "######## Two"],
            4,
            [3, 5],
            id="each-section-names-its-own",
        ),
        pytest.param(["# Doc", "## A", "```", "######## Fenced", "```"], 4, [], id="a-fenced-line-is-not-a-heading"),
        pytest.param(["# Doc", "## A", "######## Too deep"], 2, [3], id="split-level-2-still-refuses"),
    ],
)
def test_every_heading_with_no_level_to_write_at_is_named(lines, deepest, offending):
    """A section whose shift carries a heading past the last level has no ladder the tree can hold,
    and each such heading is named by its own monolith line. The defect: the report named the
    section's first line rather than the heading that overflows, and one id per section meant a
    second defective heading in the same section was never named."""
    assert _overflows(lines, deepest=deepest) == offending
