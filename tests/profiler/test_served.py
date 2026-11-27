"""index feed• /page• host guard• 404"""

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from devpro.profiler.pages import SHARED_CSS
from devpro.profiler.values import _epoch_ms
from tests.conftest import page_data

from .conftest import (
    LAYER_LINK,
    _fetch,
    _run,
    _serve,
    _write_store,
    index_head_classes,
    index_row_colspan,
    index_width_terms,
)


def test_the_served_index_lists_every_recorded_session(tmp_path: Path) -> None:
    """A store in each harness's directory and a session of several records under one project: the
    served index's feed carries an entry for every recorded session, each stating the harness and the
    count its own records hold and its first and last moment as epoch milliseconds, and its span in
    seconds; a feed that omits a session the stores hold, or states one the store does not, drops or
    invents what the records say.

    A session whose opencode record names a child session is its dispatcher: the child's entry
    carries `dispatcher`, the dispatching session's id and the dispatching call's name, and follows
    its dispatcher's in the feed — the order the index draws the rows in, a child under its
    dispatcher. The index's page file is static: no row is in its text, and its script renders them
    from this feed."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(
        project,
        ".profiler-claude",
        "s-claude",
        "2026-01-01T00:00:00.000Z",
        harness="claude",
        records=2,
        extra={"model": "claude-opus-4-5"},
    )
    _write_store(project, ".profiler-opencode", "s-opencode", "2026-01-01T00:00:05.000Z", harness="opencode")
    _write_store(
        project,
        ".profiler-opencode",
        "s-dispatcher",
        "2026-01-01T00:00:06.000Z",
        harness="opencode",
        records=1,
        extra={"tool": "Agent", "name": "devpro-coder", "child_agent_id": "s-child"},
    )
    _write_store(project, ".profiler-opencode", "s-child", "2026-01-01T00:00:07.000Z", harness="opencode", records=2)

    with _serve(cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        feed = json.loads(_fetch(f"{url}api/traces"))
        page = _fetch(f"{url}page/s-claude")

    assert feed == [
        {
            "harness": "claude",
            "id": "s-claude",
            "models": ["claude-opus-4-5"],
            "records": 2,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:00.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:01.000Z"),
            "span": 1,
            "plan": None,
            "directives": None,
            "unreviewed": False,
        },
        {
            "harness": "opencode",
            "id": "s-opencode",
            "models": [],
            "records": 1,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:05.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:05.000Z"),
            "span": 0,
            "plan": None,
            "directives": None,
            "unreviewed": False,
        },
        {
            "harness": "opencode",
            "id": "s-dispatcher",
            "models": [],
            "records": 1,
            "agents": 1,
            "first": _epoch_ms("2026-01-01T00:00:06.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:06.000Z"),
            "span": 0,
            "plan": None,
            "directives": None,
            "unreviewed": False,
        },
        {
            "harness": "opencode",
            "id": "s-child",
            "models": [],
            "records": 2,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:07.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:08.000Z"),
            "span": 1,
            "plan": None,
            "directives": None,
            "unreviewed": False,
            "dispatcher": {"session": "s-dispatcher", "name": "devpro-coder", "tool": "Agent"},
        },
    ]
    # The page file is static: the rows' empty table, no session's row, and every column heading a
    # row states — the layer's `--zebra`, which the layer switches with the color scheme itself, so
    # the template carries no second rule for it.
    assert '<tbody id="rows"></tbody>' in index and 'href="/page/' not in index
    # The table's column count has one home — the header's cells. The row script's full-width span is
    # the header-cell count it reads rather than a literal, and the stylesheet's floor sums one width
    # per header cell: a column added to the head and not to the widths overruns the table, and a span
    # pinned as a literal is the count written twice, drifting on the next column.
    head_classes = index_head_classes(index)
    assert len(head_classes) == len(set(head_classes))
    assert index_row_colspan(index) == "document.querySelectorAll('table thead th').length"
    assert index_width_terms(index) == len(head_classes)
    # Each column's share of the table comes from the page's own stylesheet, beside the header's class,
    # and the table's layout is the fixed one that gives that share to header and body alike.
    assert re.search(r"table \{ border-collapse: collapse; table-layout: fixed; \}", index)
    # The controls: a box for the child rows and one per harness — child rows off by default, so the
    # child-rows box ships without `checked` while the two harness boxes stay checked, the page
    # opening on the dispatches — and the notice a failed feed names itself in, standing empty and hidden.
    assert re.search(r'<input type="checkbox" id="child-rows" name="child-rows" value="on">', index)
    for control in ('id="harness-claude"', 'id="harness-opencode"'):
        assert re.search(rf'<input type="checkbox" {control} [^>]*checked>', index), control
    assert re.search(r'<p id="notice" class="notice" role="alert" hidden></p>', index)
    assert re.search(r"tr:nth-child\(odd\) td \{ background: var\(--zebra\); \}", index)
    assert "prefers-color-scheme: dark" not in index.split("<style>", 1)[1].split("</style>", 1)[0]
    assert page_data(page)["session"] == "s-claude"


def test_a_session_naming_itself_as_a_child_is_drawn_once_in_its_own_place(tmp_path: Path, _wrapper: Path) -> None:
    """A session whose own opencode record carries its own id as `child_agent_id`: the feed draws it
    once, top-level, its entry carrying no `dispatcher`. A grouping that reads the self-naming as a
    dispatch drops the session from the index's top level and draws it under itself, its count
    naming a row for a session that dispatched nothing."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(
        project,
        ".profiler-opencode",
        "s-self",
        "2026-01-01T00:00:00.000Z",
        harness="opencode",
        records=1,
        extra={"tool": "Agent", "name": "devpro-coder", "child_agent_id": "s-self"},
    )

    with _serve(cwd=project) as url:
        feed = json.loads(_fetch(f"{url}api/traces"))

    assert [entry["id"] for entry in feed] == ["s-self"]
    assert "dispatcher" not in feed[0]


def test_the_served_index_lists_its_own_project_under_a_foreign_project_dir(tmp_path: Path, _wrapper: Path) -> None:
    """`CLAUDE_PROJECT_DIR` at another project, as a claude shell sets it, while the dashboard runs in
    this one: the feed lists this project's sessions; a feed that follows the variable serves the
    other project's stores, which for a terminal-launched server is the wrong repository."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-here", "2026-01-01T00:00:00.000Z", harness="claude")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    _write_store(foreign, ".profiler-claude", "s-elsewhere", "2026-01-01T00:00:00.000Z", harness="claude")

    with _serve(cwd=project, env={"CLAUDE_PROJECT_DIR": str(foreign)}) as url:
        feed = json.loads(_fetch(f"{url}api/traces"))

    assert [entry["id"] for entry in feed] == ["s-here"]


def test_the_served_page_is_the_html_the_file_flow_writes(tmp_path: Path, _wrapper: Path) -> None:
    """One session's `/page/<id>` carries the file flow's page data: the JSON the page template
    inlines at its data slot is the payload `tree --format html` inlines, and the served page names
    the shared layer's one file where the render inlines its text — the two carriers' one difference."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    with _serve(cwd=project) as url:
        served = _fetch(f"{url}page/s-claude")

    printed = _run(_wrapper, "tree", "s-claude", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr
    assert page_data(served) == page_data(printed.stdout)
    # The serve path names the layer's one file where the file flow inlines its text: one source, two
    # carriers.
    assert served.count(LAYER_LINK) == 1 and SHARED_CSS not in served


def test_an_unrecorded_session_id_is_a_404_and_no_traceback(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is `/page/<id>` for an id no store records answering
    HTTP 500 from the handler's traceback instead of the 404 the view answers a page it does not
    serve — on a tree whose stores are readable, the read that finds no match returns `None`.

    The tree holds one recorded session, readable, and no locked store: the unknown id's page is a
    404, as the recorded session's page is a 200."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    with _serve(cwd=project) as url:
        assert _fetch(f"{url}page/s-claude")
        with pytest.raises(urllib.error.HTTPError) as missing:
            _fetch(f"{url}page/s-unrecorded")

    assert missing.value.code == 404
