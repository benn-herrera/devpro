"""The TEST_SURFACE_MAP's shape: most specific first, first match wins.

The map's resolution is first match: a path takes its surfaces from the first row whose
prefix matches it, and a broader row standing below a specific one is shadowed — dead text.
The defect this suite pins: an unordered row never runs, so the surface it names goes
untested for every path it was written for. The surface names themselves carry one source,
test.sh's case statement; a row naming any other is a surface the runner has no arm for.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _surfaces() -> set[str]:
    """The surface names test.sh's case statement defines, plus the map's ALL keyword: the runner's
    arm names are the one source, so a surface is added in test.sh alone."""
    test_sh = (ROOT / "devtools/scripts/test.sh").read_text(encoding="utf-8")
    case_block = re.search(r'case "\$\{surface\}" in\n(.*?)^esac', test_sh, re.S | re.M)
    assert case_block is not None, "test.sh carries no case statement over the surface"
    arms = re.findall(r"^\s{4}([\w-]+)\)", case_block.group(1), re.M)
    assert arms, "no surface arms parsed from test.sh's case statement"
    return set(arms) | {"ALL"}


def _rows() -> list[list[str]]:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")
    block = re.search(r'TEST_SURFACE_MAP := "\n(.*?)"\n', justfile, re.S)
    assert block is not None, "the justfile carries no TEST_SURFACE_MAP block"
    return [line.split() for line in block.group(1).strip().splitlines()]


def test_a_broader_row_never_shadows_a_specific_one() -> None:
    rows = _rows()
    for i, (prefix, *_) in enumerate(rows):
        for earlier, *_ in rows[:i]:
            shadowed = (earlier.endswith("/") and prefix.startswith(earlier)) or prefix == earlier
            assert not shadowed, (
                f"row '{prefix}' is shadowed by the earlier row '{earlier}': its surface "
                "never runs — order rows most specific first"
            )


def test_every_surface_field_names_known_surfaces() -> None:
    known = _surfaces()
    for prefix, *surfaces in _rows():
        assert surfaces, f"row '{prefix}' names no surface"
        unknown = set(surfaces) - known
        assert not unknown, f"row '{prefix}' names unknown surface(s): {sorted(unknown)}"
