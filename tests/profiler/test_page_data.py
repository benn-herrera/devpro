"""page data keys• deco• legend• IIFE/prefix lanes"""

import re
import subprocess
from pathlib import Path

import pytest

from devpro.components import NAME
from devpro.profiler.pages import (
    AGENT_PREFIX,
    AGENT_PREFIX_LINE,
    AGENT_PREFIX_MARK,
    DECO_INLINE,
    INDEX,
    SHARED_CSS,
    call_label,
    index_html,
)

from .conftest import (
    _PACKAGE_ROOT,
    LAYER_LINK,
    _fetch,
    _inline_script_bodies,
    _opens_an_iife,
    _run,
    _serve,
    _write_store,
)


def test_the_standalone_render_carries_the_shared_layer_and_the_legend_once(tmp_path: Path, _wrapper: Path) -> None:
    """The page `tree --format html` prints carries the presentation layer's own text, inlined whole,
    and the frame band's legend exactly once — the deco the served page carries as its own text,
    here the render's: the standalone page names no view active to a live dashboard, so its band
    heads with the legend alone, no dispatcher and no way back. A render that inlines a second layer,
    or carries the legend twice, is the reskin the shared layer forbids."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    printed = _run(_wrapper, "tree", "s-claude", "--format", "html", cwd=project)

    assert printed.returncode == 0, printed.stderr
    assert SHARED_CSS in printed.stdout
    assert printed.stdout.count("How to read this") == 1
    assert 'class="site-nav' in printed.stdout and 'class="frame-band' in printed.stdout


def test_the_standalone_render_carries_the_decoration_its_pages_script_reads(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a `tree --format html` page whose own script calls
    the deco's notation, `globalThis.devproFormat`, while the page carries neither the deco's link
    nor its text — a file cannot link a server's origin, so the page's script throws before the
    diagram and every time draw, and the page it prints is a table of nothing.

    The render inlines the deco's text where the served page links the file, and the page's script
    reads the global from it."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    printed = _run(_wrapper, "tree", "s-claude", "--format", "html", cwd=project)

    assert printed.returncode == 0, printed.stderr
    assert DECO_INLINE in printed.stdout
    assert '<script src="/profiler/deco.js"></script>' not in printed.stdout
    assert "const { localDay, clock, dur, scaled } = globalThis.devproFormat;" in printed.stdout


def test_every_page_script_wraps_its_body_in_an_iife() -> None:
    """`clauses.TEST_PRECONDITION`. The defect: `view.html`'s script stood at the page's top level,
    its helpers — `padTwo`, `localDay`, `localClock` — in the global scope classic scripts share with
    the deco's, so the next helper of one of those names would redeclare a `const` and the session
    page would draw nothing. Every script the pages run wraps its body in an IIFE; the shipped pages
    carrying an inline script are `view.html` and the `INDEX` template, and the scripts they load by
    file — the deco and the board's — are in the same shared scope and wrap theirs the same way. The
    deco is the one exception to the bare IIFE, and it is the one name the design makes public: the
    notation the pages call, `globalThis.devproFormat`."""
    pages = {
        "view.html": (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8"),
        "INDEX": INDEX,
    }
    for name, page in pages.items():
        bodies = _inline_script_bodies(page)
        assert bodies, f"{name} carries no inline script"
        assert all(_opens_an_iife(body) for body in bodies), f"{name}'s script does not open an IIFE"
    for name in ("devpro/profiler/deco.js", "devpro/kanban/assets/board.js"):
        assert _opens_an_iife((_PACKAGE_ROOT / name).read_text(encoding="utf-8")), f"{name} does not open an IIFE"
    deco = (_PACKAGE_ROOT / "devpro" / "profiler" / "deco.js").read_text(encoding="utf-8")
    assert re.findall(r"^globalThis\.(\w+)", deco, re.M) == ["devproFormat"], "the deco publishes one name"


def test_the_served_index_links_the_shared_layers_own_text(tmp_path: Path, _wrapper: Path) -> None:
    """`/profiler/` names the board's stylesheet at the path the board panel serves it: the index
    carries no copy of the layer itself, and its one stylesheet link is the board panel's link line.
    A profiler page carrying a palette of its own is the second reskin the design forbids, the board
    and the profiler showing two identities for one site; a link to a path nothing serves is a page
    styled by nothing."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    with _serve(cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        [linked] = re.findall(r'<link rel="stylesheet" href="([^"]+)">', index)

    assert LAYER_LINK == f'<link rel="stylesheet" href="{linked}">'
    assert SHARED_CSS not in index


def test_every_script_spelling_of_the_prefix_is_the_services_one(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a page's script carrying the set's prefix as its
    own literal — a re-stringed `devpro-` in `view.html`'s `shownName`, or in the index's row strip,
    beside `pages.agent_prefix_line` — so a change to the install's one name leaves the page dropping a
    prefix the set's agents no longer carry, silently, the rendering's own text still saying it does.

    The lane is the engine's reading of both scripts: each reads a name with no prefix line standing
    and fails to load, then loads beside the `AGENT_PREFIX` line and drops the Agent call's prefix
    while keeping a Bash call's name whole. The page's own spelling is the install's one name — the
    line's prefix equals `components.NAME` and `call_label` drops it. A missing `bun` fails rather
    than skips, as the pages' other engine checks do."""
    import shutil

    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the prefix's scripts cannot be read without it")
    index = index_html()
    view = (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8")
    assert AGENT_PREFIX_MARK in view

    # The pages' own spelling is the install's one name, and the label drops exactly it.
    assert AGENT_PREFIX == f"{NAME}-"
    assert call_label("Agent", f"{AGENT_PREFIX}coder") == "coder (agent)"

    # `shown` is the index's child-row name, over the row's dispatcher; `label` is a session page's
    # call label, over the two helpers it reads.
    reads = {
        "index": "const dispatched = { name: 'devpro-coder', tool: 'Agent' };\n"
        "const AGENT_TOOL = 'Agent';\n"
        + re.search(r"^    const shown = .*$", index, re.M).group(0)
        + "\nconsole.log(shown);",
        "view": "\n".join(
            re.search(pattern, view, re.M).group(0)
            for pattern in (
                r"^const shownName = .*$",
                r"^const KIND_WORDS = .*$",
                r"^const kindWord = .*$",
                r"^const label = .*$",
            )
        )
        + "\nconsole.log(label('Agent', 'devpro-coder') + ' / ' + label('Bash', 'devpro-tool'));",
    }
    bound = AGENT_PREFIX_LINE + "\n"
    for page, read in reads.items():
        (tmp_path / f"{page}-unbound.js").write_text(read, encoding="utf-8")
        (tmp_path / f"{page}-bound.js").write_text(bound + read, encoding="utf-8")

    # Each page's unbound module is the engine's `ReferenceError`; its bound one reads the name.
    for page in reads:
        unbound = subprocess.run(["bun", str(tmp_path / f"{page}-unbound.js")], capture_output=True, text=True)
        assert "ReferenceError" in unbound.stderr, unbound.stderr
    run = subprocess.run(
        ["bun", "-e", "".join(f"await import({str(tmp_path / (page + '-bound.js'))!r});\n" for page in reads)],
        capture_output=True,
        text=True,
    )

    assert run.returncode == 0, run.stderr
    assert run.stdout.split("\n")[:2] == ["coder", "coder (agent) / devpro-tool (Bash)"]


def test_the_decoration_states_durations_in_the_one_notation(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is the two notations the index and the call tree each
    carried — `1129 s` in one column and `3h 2m` in the other, and `2 ms` where a call took none —
    so one duration read two ways on two pages.

    The deco's one formatter reads a duration in milliseconds, no space between number and unit:
    `0s` at zero, `217ms` below the second, `4.2s` with one decimal below ten seconds, `48s` below
    the minute, `18m 49s` below the hour (`18m` when the seconds are zero) and `1h 2m` from the hour
    (`1h` when the minutes are zero). The file runs whole against a stub document holding no nav, so
    the deco's own body returns at its first element and the notation is what the page scope carries.
    A missing bun fails rather than skips, as the file's other engine readings do."""
    import shutil

    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the deco's notation cannot be read without it")
    deco = (_PACKAGE_ROOT / "devpro" / "profiler" / "deco.js").read_text(encoding="utf-8")
    script = tmp_path / "dur.js"
    script.write_text(
        "globalThis.document = { getElementById: () => null, querySelector: () => null };\n"
        + deco
        + "\nconsole.log([0, 217, 4200, 48000, 1129000, 1080000, 3720000, 3600000].map(devproFormat.dur).join(' '));\n",
        encoding="utf-8",
    )

    run = subprocess.run(["bun", str(script)], capture_output=True, text=True, stdin=subprocess.DEVNULL)

    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == "0s 217ms 4.2s 48s 18m 49s 18m 1h 2m 1h"


def test_a_script_naming_no_name_renders_no_word(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is `shownName` returning the name it was handed for a
    call recorded with none, so the grouped-skills label — the one site that reads the name as a
    word of its own, its fallback guarded on the string — renders `undefined` in the line a reader
    reads: `3 skills: undefined, …`.

    A call with no name renders `''`, the empty word a caller's own fallback fills, in the same
    engine reading as the prefix lane."""
    import shutil

    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the prefix's scripts cannot be read without it")
    view = (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8")
    [nameless] = re.findall(r"^const shownName = .*$", view, re.M)
    calls = "const D = { calls: [{ tool: 'Skill', name: null }, { tool: 'Skill', name: 'devpro-docdicer' }] };\n"
    names = "const names = D.calls.map((c) => shownName(c.tool, c.name) || 'skill');\n"
    (tmp_path / "nameless.js").write_text(
        f"{AGENT_PREFIX_LINE}\n{nameless}\n{calls}{names}console.log(names.join(','));\n", encoding="utf-8"
    )

    run = subprocess.run(["bun", str(tmp_path / "nameless.js")], capture_output=True, text=True)

    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == "skill,devpro-docdicer"
