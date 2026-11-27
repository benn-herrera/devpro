"""span edit• marker pairs• append• stamp"""

import re
from pathlib import Path

import pytest

from devpro import __version__
from devpro.agents_file import marker_span, scope_name
from devpro.context import Render
from devpro.definition import Definition
from devpro.errors import InputError
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.render import filled_body, render_agents_file
from devpro.vocabulary import Kind
from tests.conftest import PLAIN

from .conftest import _BEGIN, _CURRENT, _END, _STAMPED_BEGIN, _block, _files, _install, _stamped


def test_the_fresh_render_holds_the_title_and_one_marker_span() -> None:
    user_dir = Path(CLAUDE.user_harness_dir).expanduser()
    text = render_agents_file(CLAUDE, PLAIN, scope=scope_name(CLAUDE, user_dir))
    lines, begin, end = marker_span(text, where="render")
    assert (lines[0], lines[begin], lines[end]) == ("# Global info and directives", _STAMPED_BEGIN, _END)
    assert text.endswith(_END + "\n")


def test_an_agents_file_hole_in_any_other_kind_is_an_unknown_placeholder() -> None:
    defn = Definition(name="probe", kind=Kind.COMMAND, body="for @!agf-scope-name!@")
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    with pytest.raises(InputError, match=re.escape("definition 'probe': unknown placeholder @!agf-scope-name!@")):
        filled_body(defn, ctx)


def test_install_replaces_only_the_span_and_keeps_every_other_byte(tmp_path: Path, capsys) -> None:
    above = "# My rules\r\n\r\nmine above\r\n"
    below = "\nmine below\r\n\r\n  trailing  "
    begin = " <!-- vvv-devpro version[abc1234] an earlier revision's wording devpro-vvv -->"
    prior = f"{above}{begin}\r\nold block\r\n{_END}\r{below}"
    target = tmp_path / "AGENTS.md"
    target.write_bytes(prior.encode())
    _install(tmp_path)
    expected = (above + "\n".join(_block(OPENCODE)) + below).encode()
    assert target.read_bytes() == expected
    assert (tmp_path / "backup.AGENTS.md").read_bytes() == prior.encode()
    capsys.readouterr()
    _install(tmp_path)
    assert capsys.readouterr().out == f"unchanged {target}\n"
    assert target.read_bytes() == expected
    assert (tmp_path / "backup.AGENTS.md").read_bytes() == prior.encode()


@pytest.mark.parametrize(
    "prior, message",
    [
        (f"{_BEGIN}\n{_BEGIN}\n{_END}\n", "found 2 begin and 1 end"),
        (f"# mine\n{_END}\n", "found 0 begin and 1 end"),
        (f"{_END}\n{_BEGIN}\n", "found 1 begin and 1 end"),
    ],
)
def test_a_file_without_one_ordered_marker_pair_is_refused(tmp_path: Path, prior: str, message: str) -> None:
    (tmp_path / "AGENTS.md").write_text(prior, encoding="utf-8")
    with pytest.raises(InputError, match=message):
        _install(tmp_path)
    assert _files(tmp_path) == {"AGENTS.md": prior.encode()}


@pytest.mark.parametrize(
    "prior, separator",
    [
        ("", ""),
        ("# mine\r\nkeep\r\n\n", ""),
        ("# mine\r\nkeep\r\n", "\n"),
        ("# mine\r\nkeep  ", "\n\n"),
    ],
)
def test_a_file_without_marker_lines_gets_the_block_appended(
    tmp_path: Path, capsys, prior: str, separator: str
) -> None:
    target = tmp_path / "AGENTS.md"
    target.write_bytes(prior.encode())
    _install(tmp_path)
    expected = (prior + separator + "\n".join(_block(OPENCODE)) + "\n").encode()
    assert target.read_bytes() == expected
    assert (tmp_path / "backup.AGENTS.md").read_bytes() == prior.encode()
    capsys.readouterr()
    _install(tmp_path)
    assert capsys.readouterr().out == f"unchanged {target}\n"
    assert target.read_bytes() == expected


@pytest.mark.parametrize(
    "stamp, content, rewritten",
    [
        ("0.0.1", _CURRENT, False),
        ("99.0.0", _CURRENT, False),
        ("0.0.1", ["old"], True),
        (__version__, ["old"], True),
        ("99.0.0", ["old"], False),
    ],
    ids=["identical-older", "identical-newer", "older", "same", "newer"],
)
def test_the_stamp_decides_a_differing_block_and_identical_content_is_never_rewritten(
    tmp_path: Path, capsys, stamp: str, content: list[str], rewritten: bool
) -> None:
    target = tmp_path / "AGENTS.md"
    prior = _stamped(stamp, content=content)
    target.write_text(prior, encoding="utf-8")
    _install(tmp_path)
    captured = capsys.readouterr()
    if rewritten:
        assert target.read_text(encoding="utf-8") == "\n".join(["mine", *_block(OPENCODE), ""])
        assert (tmp_path / "backup.AGENTS.md").read_text(encoding="utf-8") == prior
    else:
        assert _files(tmp_path) == {"AGENTS.md": prior.encode()}
    downgrade = stamp == "99.0.0" and content != _CURRENT
    assert ("not downgraded" in captured.err and f"99.0.0, newer than this {__version__}" in captured.err) is downgrade


def test_an_unstamped_block_is_rewritten_and_stamped(tmp_path: Path) -> None:
    """The not-a-release row is the planted `version[abc1234]` fence above."""
    target = tmp_path / "AGENTS.md"
    target.write_text(f"{_BEGIN}\nold\n{_END}\n", encoding="utf-8")
    _install(tmp_path)
    assert target.read_text(encoding="utf-8") == "\n".join([*_block(OPENCODE), ""])
