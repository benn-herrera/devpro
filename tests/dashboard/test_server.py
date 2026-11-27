"""The dashboard's serve surface: the board-first root, the profiler view at `/profiler/` and
`/page/<id>`, the board panel at `/board/` and the root paths its script calls, the served documents,
and the guards both panels carry."""

import io
import json
import os
import re
import socket
import subprocess
import sys
import threading
from dataclasses import asdict, dataclass
from importlib.resources import files
from pathlib import Path

import pytest

from devpro import __version__
from devpro.dashboard.server import (
    BOARD_PATH,
    CONTENT_SECURITY_POLICY,
    DECO_SCRIPT,
    DashboardServer,
    dashboard_root,
    loopback,
)
from devpro.kanban.board import read_board
from devpro.profiler.pages import (
    BAND_LEGEND,
    DECO_MARK,
    DISPATCHED_MARK,
    LAYER_MARK,
    LEGEND,
    RETURN_MARK,
    SHARED_CSS,
    dispatches,
    read_sessions,
)
from tests.conftest import page_data

from .conftest import PLAN, TIMEOUT, Client, project, record, store

ASSETS = Path(str(files("devpro.kanban") / "assets"))
# The serve path's carrier of the shared layer: the board panel's own file, named by the pages the
# dashboard serves in place of the inline text `SHARED_CSS` holds.
LAYER_LINK = f'<link rel="stylesheet" href="{BOARD_PATH}board.css">'


def _tool_call(session: str, at: str, name: str) -> dict:
    return record(at, tool="Bash", name=name, session=session)


def test_the_root_redirects_to_the_board_the_landing_surface(tmp_path: Path, serve) -> None:
    """The root answers `302` to the board's absolute URL — the same `http://127.0.0.1:<port>/board/`
    the verb prints — and following it shows the board: a root that serves the profiler view instead
    inverts the decided board-first landing, and one answering a bare `/board/` leaves the printed
    URL and the accepted one a redirect apart."""
    root = project(tmp_path / "proj", {"ROADMAP.md": "## Next\n\n### Two\n\nMore.\n"})
    client = serve(root)

    status, headers = client.raw("GET", "", host=f"{client.host}:{client.port}")

    assert (status, headers["Location"]) == (302, f"http://127.0.0.1:{client.port}{BOARD_PATH}")
    assert client.get("")[2] == (ASSETS / "index.html").read_text(encoding="utf-8").encode("utf-8")


def test_the_state_endpoint_answers_live_while_the_server_serves(tmp_path: Path, serve) -> None:
    """`/api/state` answers the server's state — `live`, and the version the dashboard runs, the
    hover text the indicator carries — while it serves, so the deco's poll shows the phosphor and
    names the devpro serving it. An endpoint answering without the version is an indicator whose
    hover text is empty: the operator cannot tell what is serving."""
    client = serve(project(tmp_path / "proj", {}))

    status, content_type, body = client.get("api/state")

    assert (status, content_type, json.loads(body)) == (
        200,
        "application/json",
        {"state": "live", "version": __version__},
    )


def test_the_profiler_view_serves_its_list_and_its_pages(tmp_path: Path, serve) -> None:
    """`/profiler/` is the static index — its page file carrying the rows' table and no row of its
    own — and `/api/traces` lists both stores' sessions, each once, the rows' one source:
    `/page/<id>` renders that session's own records. A view that answers its routes with an empty
    page, or another session's, has kept the routes and lost the view."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")], directory=".profiler-claude")
    store(root, "s-two", [_tool_call("s-two", "2026-01-01T00:00:05.000Z", "cat")], directory=".profiler-opencode")
    served = serve(root)

    index = served.get("profiler/")[2].decode("utf-8")
    feed = json.loads(served.get("api/traces")[2])
    status, content_type, page = served.get("page/s-one")

    assert [entry["id"] for entry in feed] == ["s-one", "s-two"]
    # The page file is static: the rows' empty table, and no session row in the text — the script's
    # own link prefix standing, a session's link being what the script writes.
    assert '<tbody id="rows"></tbody>' in index and 'href="/page/' not in index
    assert (status, content_type) == (200, "text/html")
    data = page_data(page.decode("utf-8"))
    assert (data["session"], [call["name"] for call in data["calls"]]) == ("s-one", ["ls"])


SESSION_KEYS = {
    "harness",
    "id",
    "models",
    "records",
    "agents",
    "first",
    "last",
    "span",
    "plan",
    "directives",
    "unreviewed",
}
DISPATCHED_KEYS = SESSION_KEYS | {"dispatcher"}


def test_the_traces_feed_answers_one_entry_per_session(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a static index with no rows and a `/api/traces`
    answering an empty list — which passes every test the rework began from, since each read the
    index's rows out of a page the server assembled, and this feed did not exist to be empty.

    `/api/traces` answers one entry per recorded session, each carrying exactly the keys the
    schema names — the harness the records carry, the id, the record count, the first and last
    moments as epoch milliseconds and the span in seconds — and `dispatcher`, whose two halves are
    the session that dispatched the child and the call that did, on a child's entry alone.
    A feed answering an empty list, one entry per store instead of per session, or an entry whose
    moments are strings is the index drawing nothing, or drawing what the script cannot read."""
    root = project(tmp_path / "proj", {})
    store(root, "s-claude", [_tool_call("s-claude", "2026-01-01T00:00:09.000Z", "ls")], directory=".profiler-claude")
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:05.000Z", tool="Agent", name="devpro-coder", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-child"}
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-child",
        [_tool_call("s-child", "2026-01-01T00:00:07.000Z", "cat") | {"harness": "opencode"}],
        directory=".profiler-opencode",
    )
    status, content_type, body = serve(root).get("api/traces")
    entries = json.loads(body)

    assert (status, content_type) == (200, "application/json")
    assert entries == [
        {
            "harness": "opencode",
            "id": "s-parent",
            "models": [],
            "records": 1,
            "agents": 1,
            "first": 1767225605000,
            "last": 1767225605000,
            "span": 0,
            "plan": None,
            "directives": None,
            "unreviewed": False,
        },
        {
            "harness": "opencode",
            "id": "s-child",
            "models": [],
            "records": 1,
            "agents": 0,
            "first": 1767225607000,
            "last": 1767225607000,
            "span": 0,
            "plan": None,
            "directives": None,
            "unreviewed": False,
            "dispatcher": {"session": "s-parent", "name": "devpro-coder", "tool": "Agent"},
        },
        {
            "harness": "claude",
            "id": "s-claude",
            "models": [],
            "records": 1,
            "agents": 0,
            "first": 1767225609000,
            "last": 1767225609000,
            "span": 0,
            "plan": None,
            "directives": None,
            "unreviewed": False,
        },
    ]
    assert [set(entry) for entry in entries] == [SESSION_KEYS, DISPATCHED_KEYS, SESSION_KEYS]


def test_the_feed_and_the_page_carry_each_sessions_stamp(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a read that carries the stamp of whichever session or
    record it happened to see — a later-`at` record's, or a neighbouring session's — where every
    session's entry and its page carry the stamp its own records wrote once.

    A session's stamp is its earliest-`at` stamped record's, copied onto every record after it, so
    `s-new`'s records stand newest first and each field of the answer names the earliest one's: the
    plan `at-start plan`, the digest of `b`s. Each other record here is wrong in exactly one field —
    the later record in `plan`, `s-old` in `directives` — and every session's entry and page agree,
    the stamp read off the one render that reads everything else."""
    root = project(tmp_path / "proj", {})
    store(
        root,
        "s-old",
        [_tool_call("s-old", "2026-01-01T00:00:03.000Z", "ls") | {"plan": "stale plan", "directives": "c" * 64}],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-new",
        [
            _tool_call("s-new", "2026-01-01T00:00:05.000Z", "ls") | {"plan": "at-start plan", "directives": "b" * 64},
            _tool_call("s-new", "2026-01-01T00:00:09.000Z", "ls") | {"plan": "moved plan", "directives": "b" * 64},
        ],
        directory=".profiler-opencode",
    )
    served = serve(root)

    feed = {entry["id"]: entry for entry in json.loads(served.get("api/traces")[2])}
    pages = [page_data(served.get(f"page/{session}")[2].decode("utf-8")) for session in ("s-old", "s-new")]

    assert {session: (feed[session]["plan"], feed[session]["directives"]) for session in feed} == {
        "s-old": ("stale plan", "c" * 64),
        "s-new": ("at-start plan", "b" * 64),
    }
    assert [(data["session"], data["plan"], data["directives"]) for data in pages] == [
        ("s-old", "stale plan", "c" * 64),
        ("s-new", "at-start plan", "b" * 64),
    ]


def test_a_store_the_feed_cannot_read_fails_the_feed(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a store the exact names find and cannot list answered
    as a feed entry of its own, with the other store's sessions beside it and an HTTP 200 — a feed
    that draws rows from a read it could not finish.

    A store an exact name finds and cannot read raises out of the feed's assembly to the handler's
    failure answer: the request gets a `500` whose error body names the cause — never the 200 a feed
    of entries answers over the other store's sessions, never a connection closed without an answer,
    and no entry standing in the store's place."""
    root = project(tmp_path / "proj", {})
    store(root, "s-claude", [_tool_call("s-claude", "2026-01-01T00:00:00.000Z", "ls")], directory=".profiler-claude")
    locked = store(
        root, "s-broken", [_tool_call("s-broken", "2026-01-01T00:00:00.000Z", "ls")], directory=".profiler-opencode"
    )
    locked.parent.chmod(0)
    try:
        if not _listing_denied(locked.parent):
            pytest.skip("chmod denies this user no read")
        status, content_type, body = serve(root).get("api/traces")
    finally:
        locked.parent.chmod(0o755)

    assert (status, content_type) == (500, "application/json")
    assert "/" + str(locked.parent.relative_to(root)) in json.loads(body)["error"]


def _listing_denied(path: Path) -> bool:
    try:
        os.listdir(path)
    except PermissionError:
        return True
    return False


def test_a_store_a_session_page_cannot_read_fails_the_page(tmp_path: Path, serve) -> None:
    """A session's page reads the stores like the feed does, so a store an exact name finds and cannot
    read fails it the same way: a `500` whose error body names the cause, never a page rendered over
    the other store's sessions and never a connection closed without an answer."""
    root = project(tmp_path / "proj", {})
    store(
        root,
        "s-claude",
        [_tool_call("s-claude", "2026-01-01T00:00:00.000Z", "ls")],
        directory=".profiler-claude",
    )
    locked = store(
        root, "s-broken", [_tool_call("s-broken", "2026-01-01T00:00:00.000Z", "ls")], directory=".profiler-opencode"
    )
    locked.parent.chmod(0)
    try:
        if not _listing_denied(locked.parent):
            pytest.skip("chmod denies this user no read")
        status, content_type, body = serve(root).get("page/s-claude")
    finally:
        locked.parent.chmod(0o755)

    assert (status, content_type) == (500, "application/json")
    assert "/" + str(locked.parent.relative_to(root)) in json.loads(body)["error"]


def _unreadable(path: Path) -> bool:
    """Whether path, its permissions just removed, now refuses this user a read."""
    try:
        path.read_text(encoding="utf-8")
    except PermissionError:
        return True
    return False


@pytest.mark.parametrize(
    "path, name",
    [
        pytest.param("board/", "index.html", id="page"),
        pytest.param("board/board.css", "board.css", id="stylesheet"),
        pytest.param("board/board.js", "board.js", id="script"),
    ],
)
def test_the_board_page_and_the_files_it_names_resolve_under_the_board_path(
    tmp_path: Path, serve, path: str, name: str
) -> None:
    """`/board/` serves the board's `index.html`, whose two files it names relative to itself, and
    each is served at `/board/<name>`: the board is where its page can load, which is the URL the
    dashboard's link line opens."""
    root = project(tmp_path / "proj", {"ROADMAP.md": "## Next\n\n### Two\n\nMore.\n"})
    client = serve(root)

    status, _, body = client.get(path)
    refused = client.get("board/nothing.js")[0]

    assert status == 200
    assert body == (ASSETS / name).read_text(encoding="utf-8").encode("utf-8")
    assert refused == 404


def test_the_board_payload_is_the_model(tmp_path: Path, serve) -> None:
    """`/api/board` answers the board `read_board` reads, with the plan columns, the project's name
    and devpro's version: a panel serving a second model of the files is a second board."""
    root = project(
        tmp_path / "proj",
        {"ACTIVE_PLAN.md": PLAN, "ROADMAP.md": "## Next\n\n### Two\n\nMore.\n", "ACTIVE_DESIGN.md": "# Design\n"},
    )

    payload = json.loads(serve(root).get("api/board")[2])

    assert payload["board"] == json.loads(json.dumps(asdict(read_board(str(root)))))
    assert payload["plan_columns"] == ["drafted", "dispatchable", "in progress", "landed"]
    assert payload["project"] == "proj"


def test_a_card_moves_to_the_design_and_back_at_the_paths_the_page_calls(tmp_path: Path, serve) -> None:
    """The board's script posts `/api/to-design` and `/api/to-roadmap`: each answers the board with
    the files it wrote, and the second returns the card to `ROADMAP.md`. A move at any other path
    leaves both files as they were."""
    roadmap = "## Next\n\n### Two\n\nMore.\n"
    design = "# Design\n\nText.\n"
    root = project(tmp_path / "proj", {"ROADMAP.md": roadmap, "ACTIVE_DESIGN.md": design})
    client = serve(root)
    [card] = [c for c in json.loads(client.get("api/board")[2])["board"]["roadmap"] if c["kind"] == "ticket"]

    status, payload = client.post("api/to-design", {"card": card})

    assert (status, payload["written"]) == (200, ["ACTIVE_DESIGN.md", "ROADMAP.md"])
    [moved] = [c for c in payload["board"]["design"] if c["kind"] == "ticket"]
    assert moved["title"] == "Two"
    status, payload = client.post("api/to-roadmap", {"card": moved, "target": None})
    assert (status, payload["written"]) == (200, ["ROADMAP.md", "ACTIVE_DESIGN.md"])
    assert (root / "ROADMAP.md").read_text(encoding="utf-8") == roadmap

    refused = serve(root).post("api/move", {"card": card})
    assert refused[0] == 404
    assert (root / "ROADMAP.md").read_text(encoding="utf-8") == roadmap


def test_the_stops_path_answers_and_ends_the_serving(tmp_path: Path) -> None:
    """The board's page stops the server at `/api/stop`: the answer is `{}` and the next request is
    refused — a stop answered without ending the serving is a button that does nothing."""
    server = DashboardServer(str(project(tmp_path / "proj", {"ROADMAP.md": "## Next\n"})), stderr=io.StringIO())
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    client = Client(server.url)
    try:
        assert client.post("api/stop", {}) == (200, {})
        thread.join(TIMEOUT)
        assert not thread.is_alive()
    finally:
        server.server_close()


@pytest.mark.parametrize(
    "path, name",
    [
        pytest.param("ROADMAP.md", "ROADMAP.md", id="root-document"),
        pytest.param("PROJECT_DOCS/SPEC/arch.md", "PROJECT_DOCS/SPEC/arch.md", id="project-docs-leaf"),
        pytest.param("ROADMAP_DESIGNS/a%20b.md", "ROADMAP_DESIGNS/a b.md", id="parked-file-named-with-a-space"),
    ],
)
def test_a_served_document_is_served_as_markdown(tmp_path: Path, serve, path: str, name: str) -> None:
    """A `.md` file at the root, a leaf under `PROJECT_DOCS/` and a parked design's file percent-encode
    to its path are served read-only as markdown at the path from the project root: a dashboard that
    serves them as another type, or from another path, is a document a reader cannot open."""
    files_ = {
        "ROADMAP.md": "## Next\n",
        "PROJECT_DOCS/SPEC/arch.md": "# A leaf\n",
        "ROADMAP_DESIGNS/a b.md": "## Parked\n",
    }

    status, content_type, body = serve(project(tmp_path / "proj", files_)).get(path)

    assert (status, content_type, body) == (200, "text/markdown", files_[name].encode("utf-8"))


@pytest.mark.parametrize(
    "path",
    [
        pytest.param("notes.txt", id="not-markdown"),
        pytest.param("docs/notes.md", id="markdown-in-a-directory-no-pattern-names"),
        pytest.param("../proj/ROADMAP.md", id="escaping-the-root"),
        pytest.param("%2e%2e/proj/ROADMAP.md", id="escaping-the-root-percent-encoded"),
    ],
)
def test_no_other_file_is_served(tmp_path: Path, serve, path: str) -> None:
    """A file outside the served set is a 404, an escape from the root included: a dashboard serving
    any path it is asked for publishes the repository it runs in."""
    client = serve(
        project(tmp_path / "proj", {"ROADMAP.md": "## Next\n", "notes.txt": "text\n", "docs/notes.md": "# x\n"})
    )

    assert client.raw("GET", path, host=f"{client.host}:{client.port}")[0] == 404


@pytest.mark.parametrize(
    "method, path, body, answered",
    [
        pytest.param("GET", "api/board", b"", 200, id="payload"),
        pytest.param("GET", "api/state", b"", 200, id="state"),
        pytest.param("GET", "board/", b"", 200, id="board-page"),
        pytest.param("GET", "board/board.js", b"", 200, id="board-script"),
        pytest.param("GET", "", b"", 302, id="root"),
        pytest.param("POST", "api/to-design", b"[]", 400, id="move"),
        pytest.param("POST", "api/stop", b"[]", 400, id="stop"),
    ],
)
@pytest.mark.parametrize(
    "host, accepted",
    [
        pytest.param("127.0.0.1:{port}", True, id="address"),
        pytest.param("localhost:{port}", True, id="localhost"),
        pytest.param("127.0.0.1:{other}", False, id="address-other-port"),
        pytest.param("attacker.example", False, id="other-host"),
    ],
)
def test_only_a_request_naming_the_dashboards_own_host_and_port_is_answered(
    tmp_path: Path, serve, method: str, path: str, body: bytes, answered: int, host: str, accepted: bool
) -> None:
    """Every route of both panels answers a request naming the dashboard's host and port, and 403 one
    naming another host or another port: a panel reached under the name of a page served elsewhere
    is the rebinding the guard refuses."""
    client = serve(project(tmp_path / "proj", {"ROADMAP.md": "## Next\n"}))

    status, _ = client.raw(method, path, body=body, host=host.format(port=client.port, other=client.port + 1))

    assert status == (answered if accepted else 403)


def test_every_page_answer_forbids_sniffing_and_restricts_its_sources(tmp_path: Path, serve) -> None:
    """Every answer a page could be loaded from — the dashboard's pages, the board panel's, the
    served documents and a 404 — carries `nosniff`, and each page answer the same
    Content-Security-Policy; the JSON payload carries `nosniff` alone. The board-first root answers
    `302` and carries both headers too: a browser follows it into a page. A panel that drops the
    policy from its pages, or a redirect that lands on a page without one, loses the guard the panels
    carried."""
    client = serve(project(tmp_path / "proj", {"ROADMAP.md": "## Next\n"}))
    host = f"{client.host}:{client.port}"

    for path in ("board/", "board/board.js", "profiler/", "ROADMAP.md"):
        status, headers = client.raw("GET", path, host=host)
        assert status in (200, 404), path
        assert headers["Content-Security-Policy"] == CONTENT_SECURITY_POLICY, path
        assert headers["X-Content-Type-Options"] == "nosniff", path
    for path in ("nothing.md", "nothing.js"):
        status, headers = client.raw("GET", path, host=host)
        assert status == 404, path
        assert headers["Content-Security-Policy"] == CONTENT_SECURITY_POLICY, path
        assert headers["X-Content-Type-Options"] == "nosniff", path
    status, headers = client.raw("GET", "", host=host)
    assert (status, headers["Location"]) == (302, f"http://127.0.0.1:{client.port}{BOARD_PATH}")
    assert headers["Content-Security-Policy"] == CONTENT_SECURITY_POLICY
    assert headers["X-Content-Type-Options"] == "nosniff"
    _, headers = client.raw("GET", "api/board", host=host)
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "Content-Security-Policy" not in headers


def test_the_profiler_view_carries_its_nav_and_no_legend(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is the index carrying the legend, which the view keeps
    for a session's page alone. `/profiler/` carries the frame band without it, and the nav with
    `profiler` the active view and `kanban` linking `/board/`: an index that shows the how-to-read
    spends the band on a page no diagram draws, and a nav naming no active view leaves the reader
    unable to tell which view is shown."""
    client = serve(project(tmp_path / "proj", {}))
    index = client.get("profiler/")[2].decode("utf-8")

    assert LEGEND not in index
    assert 'class="frame-band' in index
    assert re.search(r'<a class="view active" href="/profiler/" aria-current="page">profiler</a>', index)
    assert re.search(r'<a class="view" href="/board/">kanban</a>', index)


@pytest.mark.parametrize(
    "path, scripts",
    [
        pytest.param("profiler/", 1, id="index"),
        pytest.param("page/s-one", 1, id="session-page"),
    ],
)
def test_every_profiler_view_page_renders_the_way_the_file_flow_renders_it(
    tmp_path: Path, serve, path: str, scripts: int
) -> None:
    """A served page is the page the file flow writes, with the dashboard's own deco around it:
    the shared layer linked once to the board panel's own file — the CSP refuses an inline
    stylesheet, and one source serves both carriers — the nav once with the server block, the nav's
    script linked once — beside the page's own inline script, the render's on a session's page and
    the rows' on the index — and no mark the splice did not fill. A served page whose layer is
    inlined (the render's carrier, not the serve's), or which carries an unfilled mark or a second
    nav, is the page the dashboard serves standing apart from the one the render writes, and the CSP
    would strip its styling on delivery."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    page = serve(root).get(path)[2].decode("utf-8")

    assert page.count(LAYER_LINK) == 1
    assert SHARED_CSS not in page
    assert page.count('class="site-nav') == 1 and page.count('id="connection"') == 1 and page.count('id="stop"') == 1
    assert page.count("<script>") == scripts
    assert page.count('<script src="/profiler/deco.js">') == 1 and page.count("api/state") == 0
    assert not [mark for mark in (LAYER_MARK, DECO_MARK, BAND_LEGEND, DISPATCHED_MARK, RETURN_MARK) if mark in page]


def test_the_pages_csp_admits_the_pages_own_blocks(tmp_path: Path, serve) -> None:
    """The pages' Content-Security-Policy admits the templates' own inline style and script blocks —
    the pages are first-party and the render escapes every record field at source, so 'unsafe-inline'
    admits what the file flow writes while 'self' keeps everything else same-origin. A policy that
    strips a page's own blocks is the defect that left every profiler page default-styled and its
    drawing script unrun while the bytes were correct."""
    assert "style-src 'self' 'unsafe-inline'" in CONTENT_SECURITY_POLICY
    assert "script-src 'self' 'unsafe-inline'" in CONTENT_SECURITY_POLICY
    assert "frame-ancestors 'none'" in CONTENT_SECURITY_POLICY


def test_the_decoration_script_is_served_as_the_file_its_pages_name(tmp_path: Path, serve) -> None:
    """`/profiler/deco.js` answers the shipped script's bytes as JavaScript: the profiler pages name
    that file for the nav's behavior — the poll that keeps the indicator true and the stop that ends
    the server — and the CSP refuses the script inline. A page naming a file the dashboard serves
    nowhere is a nav whose stop never loads and whose indicator is idle forever."""
    served = serve(project(tmp_path / "proj", {})).get("profiler/deco.js")
    assert served[0] == 200
    assert served[2].decode("utf-8") == DECO_SCRIPT
    assert served[1] == "text/javascript"


def test_the_served_pages_link_a_shared_layer_whose_bytes_are_the_one_homes(tmp_path: Path, serve) -> None:
    """The layer the profiler pages link is the board panel's own file: the bytes `/board/board.css`
    serves are the bytes `SHARED_CSS` holds. A layer that drifts from the one home is a second
    stylesheet under another name — the page the link builds and the page the render writes diverge
    on delivery, the defect no fetch of either page alone can see."""
    served = serve(project(tmp_path / "proj", {}))
    css = served.get("board/board.css")[2].decode("utf-8")
    assert css == SHARED_CSS
    page = served.get("profiler/")[2].decode("utf-8")
    assert LAYER_LINK in page
    assert SHARED_CSS not in page


def test_the_board_page_holds_its_deco_once_and_the_nav_supplies_it(tmp_path: Path, serve) -> None:
    """`/board/` carries the nav's server block — the indicator and the stop — once, and names two
    scripts, the files the board path serves beside it: the nav's, whose text the board's own file
    holds, and its board's. A board page writing its own copy of the block is the second deco the
    one nav replaced; one naming a file the board path does not serve is a page whose stop never
    loads."""
    page = serve(project(tmp_path / "proj", {})).get("board/")[2].decode("utf-8")

    assert page.count('id="connection"') == 1 and page.count('id="stop"') == 1
    assert re.findall(r'<script src="([^"]+)"', page) == ["/profiler/deco.js", "board.js"]


def _band(page: str) -> str:
    """A session page's frame band: from the band's opening div to its close.

    The close is the band's own closing tag on its own line, never the legend's first `</div>`: the
    legend carries its symbols' div, and a band cut there holds no dispatch line and no return
    control, so every check over the band would read an empty string and assert nothing it names."""
    start = page.find('<div class="frame-band')
    return page[start : page.find("</div>\n", start) + len("</div>")] if start >= 0 else ""


def test_a_session_page_is_served_without_reading_the_stores_a_second_time(tmp_path: Path, serve, monkeypatch) -> None:
    """One `/page/<id>` request walks the stores twice — the page's own read, and the dispatcher
    lookup's — and groups the sessions without one group per render: the server's `dispatches` over
    the sessions that read holds, the lookup's own over the same tree, and the lookup's walk up the
    dispatcher chain, which groups the sessions at each ancestor it steps to rather than re-reading a
    store per step. The render's depth-2 chain reads the server's one map and groups nothing: a
    render that grouped again, or a chain that re-read a store per step, pays a read or a group for
    every ancestor a session has, and a page paying that per render has lost the cost the first read
    already paid."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-coder", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-one"}
        ],
        directory=".profiler-opencode",
    )
    served = serve(root)
    real_read, real_grouping = read_sessions, dispatches
    reads: list[str] = []
    groupings: list[int] = []

    def counted_read(directory: object) -> list[dict]:
        reads.append(str(directory))
        return real_read(directory)

    def counted_grouping(sessions: list[dict]) -> dict[str, tuple[str, str]]:
        groupings.append(len(sessions))
        return real_grouping(sessions)

    monkeypatch.setattr("devpro.profiler.pages.read_sessions", counted_read)
    monkeypatch.setattr("devpro.dashboard.server.read_sessions", counted_read)
    monkeypatch.setattr("devpro.profiler.pages.dispatches", counted_grouping)
    page = served.get("page/s-one")[2].decode("utf-8")

    assert reads == [str(root), str(root)]
    assert groupings == [2, 1, 1]
    assert re.search(r'<strong>Dispatched by</strong> <a href="/page/s-parent">s-parent</a> — coder', page)


def test_the_static_index_answers_without_reading_the_stores(tmp_path: Path, serve, monkeypatch) -> None:
    """One `/profiler/` request reads no store: the index is static — its rows are the feed's, drawn
    client-side — and every fill it carries reads a module constant, so it has no use for a session.
    A read left in a fill's neighbour walks every store the project holds for a result nothing draws,
    per page load, and that the cost lands on the index rather than the feed is the defect."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    served = serve(root)
    real_read = read_sessions
    reads: list[str] = []

    def counted_read(directory: object) -> list[dict]:
        reads.append(str(directory))
        return real_read(directory)

    monkeypatch.setattr("devpro.profiler.pages.read_sessions", counted_read)
    monkeypatch.setattr("devpro.dashboard.server.read_sessions", counted_read)
    served.get("profiler/")

    assert reads == []


def test_a_session_page_carries_the_bands_legend_and_the_way_back(tmp_path: Path, serve) -> None:
    """`/page/<id>` carries the band with the legend once and `Return to list` linking `/profiler/`,
    and its body carries no second legend: drill-down with no way back strands the reader on the
    session, and a doubled legend shows one home where the target states two carriers.

    A session an opencode record dispatched heads its band with `Dispatched by`, the dispatcher
    linked to its page and the dispatching call's name, and one nothing dispatched carries neither:
    a child page that names no dispatcher loses the way back to the session that started it."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-coder", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-one"}
        ],
        directory=".profiler-opencode",
    )
    served = serve(root)
    page = served.get("page/s-one")[2].decode("utf-8")
    undispatched = served.get("page/s-parent")[2].decode("utf-8")

    assert page.count("How to read this") == 1
    assert re.search(r'<a class="return" href="/profiler/">Return to list</a>', page)
    assert 'class="frame-band' in page
    assert re.search(r'<a class="view active" href="/profiler/" aria-current="page">profiler</a>', page)
    assert re.search(r'<strong>Dispatched by</strong> <a href="/page/s-parent">s-parent</a> — coder', page)
    assert _band(page).index("Dispatched by") < _band(page).index("Return to list")
    assert _band(page).endswith("Return to list</a></div>")
    assert "Dispatched by" not in undispatched
    assert re.search(r'<a class="return" href="/profiler/">Return to list</a>', undispatched)


def test_the_indexs_row_links_and_the_session_pages_way_back_carry_the_query(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a row link built from the session's id alone, and a
    return control whose `href` is the base `/profiler/` the band was filled with — a reader who
    narrowed the list and sorted it lands on a session and comes back to a list with neither, the
    state the page's URL carries lost at both ends of the navigation.

    This is a form pin: the two assertions that name the inline script — the index's row-link line
    and the page's return-link line — byte-match its source, not a rendered navigation. The
    served-page fetch checks are the effect witnesses, the browser-eye check the witness for the
    branches the probes do not exercise: whether the page's own script folds the query into a click
    is a render-time fact the substring probes do not run."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    served = serve(root)
    index = served.get("profiler/")[2].decode("utf-8")
    page = served.get("page/s-one")[2].decode("utf-8")

    assert "PAGE + encodeURIComponent(id) + location.search" in index
    assert re.search(r'<a class="return" href="/profiler/">Return to list</a>', page)
    assert "back.href = back.pathname + location.search" in page


def test_a_child_page_names_its_root_for_the_call_that_dispatched_it(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a child page whose root is labelled `main` in hue 0
    — before the change, `page/s-one`'s `contexts[0]` is `main`, hue 0.

    A dispatched session's page names its own root context, its id still `main`, for the dispatching
    call's agent with the set's prefix dropped, and colors it in the hue that call opened its context
    in on the dispatcher's page: `s-one` was dispatched by `devpro-coder`, whose context on
    `s-parent`'s page is fresh and takes hue 1, so `s-one`'s root is `coder` in hue 2 — 1 skipped, the
    root's own. A page nothing dispatched keeps `main` in hue 0. A root reading `main` on a child's
    page is the page naming the conversation rather than the agent it is the work of."""
    root = project(tmp_path / "proj", {})
    for session in ("s-one", "s-other"):
        store(
            root,
            session,
            [_tool_call(session, "2026-01-01T00:00:05.000Z", "ls") | {"harness": "opencode"}],
            directory=".profiler-opencode",
        )
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-architect", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-other"},
            record("2026-01-01T00:00:01.000Z", tool="Agent", name="devpro-coder", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-one"},
        ],
        directory=".profiler-opencode",
    )
    served = serve(root)

    child_root = page_data(served.get("page/s-one")[2].decode("utf-8"))["contexts"][0]
    dispatcher_root = page_data(served.get("page/s-parent")[2].decode("utf-8"))["contexts"][0]

    assert (child_root["id"], child_root["label"], child_root["hue"]) == ("main", "coder", 2)
    assert (dispatcher_root["id"], dispatcher_root["label"], dispatcher_root["hue"]) == ("main", "main", 0)


def test_a_child_pages_fresh_context_skips_the_roots_hue(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a dispatched page whose own fresh context wears its
    root's hue — before the change, `page/s-child`'s first fresh context takes hue 2 beside a root
    in hue 2, so the page draws two conversations in one color and the bar cannot tell them apart.

    A page's fresh contexts take hues from 1 up, and its root holds its own hue whether or not a
    fresh context counted past it: `s-child` is a dispatched page whose root wears hue 2, so its one
    fresh context opens in hue 1."""
    root = project(tmp_path / "proj", {})
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-architect", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-other"},
            record("2026-01-01T00:00:01.000Z", tool="Agent", name="devpro-coder", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-child"},
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-child",
        [
            record("2026-01-01T00:00:05.000Z", tool="Agent", name="devpro-tech-writer", session="s-child")
            | {"harness": "opencode", "child_agent_id": "s-grand"},
            _tool_call("s-child", "2026-01-01T00:00:06.000Z", "ls") | {"harness": "opencode"},
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-grand",
        [_tool_call("s-grand", "2026-01-01T00:00:07.000Z", "ls") | {"harness": "opencode"}],
        directory=".profiler-opencode",
    )
    page = serve(root).get("page/s-child")[2].decode("utf-8")
    contexts = page_data(page)["contexts"]

    assert [(context["id"], context["hue"]) for context in contexts] == [("main", 2), ("s-grand", 1)]


def test_a_grandchilds_root_wears_the_hue_its_dispatchers_page_draws_it_in(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a grandchild's root hue computed off a dispatcher
    whose own page is drawn with root hue 0 — before the change, `page/s-grand` opens its root in hue
    1, the hue its own first fresh context takes on `page/s-child`, where the dispatcher's page draws
    that context in hue 2.

    The hue a dispatching call's context wears is a fact of the dispatcher's page, read up the chain:
    `s-child`'s own page takes its root hue from `s-parent`'s, and `s-parent` is a page nothing
    dispatched, its root in hue 0. The contexts `s-child` opens take hues from 1 up, skipping its own
    root's: `s-grand`'s context is hue 1 there, where the root itself is hue 2, and `s-grand`'s page
    must open its root in that same hue — a grandchild's root hue read off a dispatcher page drawn at
    hue 0 disagrees with the page that actually draws it."""
    root = project(tmp_path / "proj", {})
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-architect", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-other"},
            record("2026-01-01T00:00:01.000Z", tool="Agent", name="devpro-coder", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-child"},
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-child",
        [
            record("2026-01-01T00:00:05.000Z", tool="Agent", name="devpro-tech-writer", session="s-child")
            | {"harness": "opencode", "child_agent_id": "s-grand"},
            _tool_call("s-child", "2026-01-01T00:00:06.000Z", "ls") | {"harness": "opencode"},
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-grand",
        [_tool_call("s-grand", "2026-01-01T00:00:07.000Z", "ls") | {"harness": "opencode"}],
        directory=".profiler-opencode",
    )
    served = serve(root)

    child_contexts = page_data(served.get("page/s-child")[2].decode("utf-8"))["contexts"]
    grand_root = page_data(served.get("page/s-grand")[2].decode("utf-8"))["contexts"][0]
    drawn = next(context["hue"] for context in child_contexts if context["id"] == "s-grand")

    assert (child_contexts[0]["id"], child_contexts[0]["hue"]) == ("main", 2)
    assert (grand_root["id"], grand_root["label"]) == ("main", "tech-writer")
    assert grand_root["hue"] == drawn


def test_a_session_page_draws_the_agents_its_child_dispatched(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a dispatched session's page whose payload carries no
    depth-2 chain — before the change, `page/s-parent`'s data has no `children` key at all, so the
    page stops at its child's own context and never names the agents the child dispatched.

    The session page is the depth view: beneath each dispatch the page draws the agents the child
    dispatched of its own, read from the child's own store — `s-child`'s records dispatch
    `devpro-architect` into `s-grand` and run a Bash call, so `s-parent`'s page carries `s-child`
    with that one agent, named after the call and linked to `s-grand`'s page. One level deeper and no
    deeper: `s-grand` dispatches nothing, so its entry under `s-child`'s page carries no agents, the
    depth-2 draw not following the chain a third level."""
    root = project(tmp_path / "proj", {})
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-coder", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-child"}
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-child",
        [
            record("2026-01-01T00:00:01.000Z", tool="Agent", name="devpro-architect", session="s-child")
            | {"harness": "opencode", "child_agent_id": "s-grand"},
            _tool_call("s-child", "2026-01-01T00:00:03.000Z", "ls") | {"harness": "opencode"},
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-grand",
        [_tool_call("s-grand", "2026-01-01T00:00:04.000Z", "ls") | {"harness": "opencode"}],
        directory=".profiler-opencode",
    )
    served = serve(root)

    parent = page_data(served.get("page/s-parent")[2].decode("utf-8"))
    child = page_data(served.get("page/s-child")[2].decode("utf-8"))

    assert parent["children"] == [
        {
            "id": "s-child",
            "name": "devpro-coder",
            "tool": "Agent",
            "agents": [{"name": "devpro-architect", "tool": "Agent", "childPage": "/page/s-grand"}],
            "unreviewed": True,
        }
    ]
    assert [(row["id"], row["agents"]) for row in child["children"]] == [("s-grand", [])]


def test_a_fanout_with_no_review_before_its_first_dispatch_is_marked(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a dashboard that reads a nested fan-out as the
    process working whatever its trace holds — before the change, `s-fan` dispatches agents with no
    review of them recorded, and neither its page nor its dispatcher's row says so.

    The detector reads the opencode dispatch chains: a dispatched session whose records dispatch
    further agents is a fan-out, and the fan-out whose own records, before its own first dispatch,
    name no dispatch of `devpro-prompt-engineer` is the unreviewed one. `s-fan` dispatches
    `devpro-architect` first and only then `devpro-prompt-engineer`, so its review came after its
    first dispatch and it is marked: its page's header line carries `unreviewed fan-out`, and its
    dispatcher `s-root`'s feed entry carries `unreviewed: true` with the agents count still the
    count. `s-reviewed` dispatches the review seat first, so it is a fan-out no mark names."""
    root = project(tmp_path / "proj", {})
    store(
        root,
        "s-root",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-coder", session="s-root")
            | {"harness": "opencode", "child_agent_id": "s-fan"},
            record("2026-01-01T00:00:20.000Z", tool="Agent", name="devpro-prompt-engineer", session="s-root")
            | {"harness": "opencode", "child_agent_id": "s-reviewed"},
        ],
        directory=".profiler-opencode",
    )
    # A fan-out that dispatched before any review: unreviewed.
    store(
        root,
        "s-fan",
        [
            record("2026-01-01T00:00:01.000Z", tool="Agent", name="devpro-architect", session="s-fan")
            | {"harness": "opencode", "child_agent_id": "s-leaf"},
            record("2026-01-01T00:00:05.000Z", tool="Agent", name="devpro-prompt-engineer", session="s-fan")
            | {"harness": "opencode", "child_agent_id": "s-leaf-2"},
        ],
        directory=".profiler-opencode",
    )
    # A fan-out whose first dispatch is the review seat: reviewed — the review arrives before the
    # work fans out.
    store(
        root,
        "s-reviewed",
        [
            record("2026-01-01T00:00:21.000Z", tool="Agent", name="devpro-prompt-engineer", session="s-reviewed")
            | {"harness": "opencode", "child_agent_id": "s-leaf-3"},
            record("2026-01-01T00:00:25.000Z", tool="Agent", name="devpro-coder", session="s-reviewed")
            | {"harness": "opencode", "child_agent_id": "s-leaf-4"},
        ],
        directory=".profiler-opencode",
    )
    for leaf, at in (("s-leaf", "01"), ("s-leaf-2", "06"), ("s-leaf-3", "22"), ("s-leaf-4", "26")):
        store(
            root,
            leaf,
            [_tool_call(leaf, f"2026-01-01T00:00:{at}.000Z", "ls") | {"harness": "opencode"}],
            directory=".profiler-opencode",
        )
    served = serve(root)
    feed = {entry["id"]: entry for entry in json.loads(served.get("api/traces")[2]) if "id" in entry}
    fan_page = served.get("page/s-fan")[2].decode("utf-8")
    reviewed_page = served.get("page/s-reviewed")[2].decode("utf-8")

    fan = page_data(fan_page)
    reviewed = page_data(reviewed_page)

    assert fan["unreviewed"] is True
    assert reviewed["unreviewed"] is False
    assert feed["s-root"]["agents"] == 2 and feed["s-root"]["unreviewed"] is True
    # The mark is the dispatcher's: the feed carries its child's verdict on the dispatcher's entry,
    # never on the child's own row — the index draws it in the agents cell, and the child's page
    # names it in its header line off this payload field.
    assert "unreviewed" in feed["s-fan"] and feed["s-fan"]["unreviewed"] is False


def test_the_index_marks_an_unreviewed_fanout_beside_its_count(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a flat index whose agents cell carries the count
    alone, so the reader looking at the list cannot tell a dispatcher whose child fanned out with no
    review from one whose child did not — before the change, `s-root`'s cell reads `1 agent` and its
    child's fan-out is invisible in the list.

    The mark stands in the same cell, after the count: `s-root`'s child `s-fan` dispatches an agent
    and records no review before it, so `s-root`'s feed entry carries `unreviewed` and its row's
    agents cell draws the count and the mark, not the mark in place of the count. The count the
    column sorts on is still `agents`; the index gains no second row level for the value. A
    dispatcher whose child fans out nothing carries no mark."""
    root = project(tmp_path / "proj", {})
    store(
        root,
        "s-root",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-coder", session="s-root")
            | {"harness": "opencode", "child_agent_id": "s-fan"},
            record("2026-01-01T00:00:20.000Z", tool="Agent", name="devpro-coder", session="s-root")
            | {"harness": "opencode", "child_agent_id": "s-plain"},
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-fan",
        [
            record("2026-01-01T00:00:01.000Z", tool="Agent", name="devpro-architect", session="s-fan")
            | {"harness": "opencode", "child_agent_id": "s-leaf"}
        ],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-plain",
        [_tool_call("s-plain", "2026-01-01T00:00:22.000Z", "ls") | {"harness": "opencode"}],
        directory=".profiler-opencode",
    )
    store(
        root,
        "s-leaf",
        [_tool_call("s-leaf", "2026-01-01T00:00:02.000Z", "ls") | {"harness": "opencode"}],
        directory=".profiler-opencode",
    )
    served = serve(root)
    feed = {entry["id"]: entry for entry in json.loads(served.get("api/traces")[2])}
    index = served.get("profiler/")[2].decode("utf-8")

    assert (feed["s-root"]["agents"], feed["s-root"]["unreviewed"]) == (2, True)
    # The cell draws the count and then the mark in the same cell — a `.mark` span appended to the
    # agents cell, never a row of its own: the flat table keeps its one row level.
    assert "const agents = el('td', session.agents ? count : '', 'col-agents');" in index
    assert "if (session.unreviewed) agents.append(' ', el('span', 'unreviewed fan-out', 'mark'));" in index
    assert "agents," in index


def test_the_agents_cell_reads_the_count_as_agents(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is the cell reading `1 dispatched agent` under a
    `dispatched agents` column head — the head names the column, so the cell repeating it spends a
    reader's width on what the head already said.

    This is a form pin: the single assertion byte-matches the inline script's ternary, not the cell
    the page renders. The served-page fetch checks are the effect witnesses, the browser-eye check
    the witness for the branches the probes do not exercise: which of `1 agent` and `3 agents` the
    cell shows is a render-time fact the substring probe does not run."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    index = serve(root).get("profiler/")[2].decode("utf-8")

    assert re.search(r"session\.agents === 1 \? '1 agent' : session\.agents \+ ' agents'", index)


def test_a_rendered_agent_name_drops_the_set_prefix(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a page rendering the record's name as stored —
    `devpro-coder` — in the band that heads a dispatched session, and in the index's child row,
    repeating on every row a provenance the reader reading a devpro session already knows.

    The stored name keeps its prefix — the record and the feed are as recorded — and the page drops
    it at the render: the served band names `coder` and the feed carries the name as stored. The
    index's child-row drop is a form pin — the assertion byte-matches the inline script's ternary,
    not the rendered row. The served-page fetch checks are the effect witnesses, the browser-eye
    check the witness for the branches the probes do not exercise: whether the child row shows
    `coder` is a render-time fact the substring probe does not run."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:00.000Z", tool="Agent", name="devpro-coder", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-one"}
        ],
        directory=".profiler-opencode",
    )
    served = serve(root)
    page = served.get("page/s-one")[2].decode("utf-8")
    index = served.get("profiler/")[2].decode("utf-8")
    feed = json.loads(served.get("api/traces")[2])

    assert "devpro-coder" not in page
    assert re.search(r'<strong>Dispatched by</strong> <a href="/page/s-parent">s-parent</a> — coder<', page)
    assert "dispatched.tool === AGENT_TOOL ? dispatched.name.replace(AGENT_PREFIX, '') : dispatched.name" in index
    assert {"session": "s-parent", "name": "devpro-coder", "tool": "Agent"} in [
        entry.get("dispatcher") for entry in feed
    ]


def test_a_served_dispatch_line_keeps_a_name_that_is_not_an_agents(tmp_path: Path, serve) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is the band's drop running on every dispatched session,
    so a session a Bash call recorded as its child — the recorded head `devpro-check-plan` — heads
    its page `check-plan`, the page misstating the call the store holds.

    The drop is the Agent tool's: the served band renders a Bash dispatcher's name as recorded."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    store(
        root,
        "s-parent",
        [
            record("2026-01-01T00:00:00.000Z", tool="Bash", name="devpro-check-plan", session="s-parent")
            | {"harness": "opencode", "child_agent_id": "s-one"}
        ],
        directory=".profiler-opencode",
    )
    served = serve(root)

    page = served.get("page/s-one")[2].decode("utf-8")

    assert re.search(r'<strong>Dispatched by</strong> <a href="/page/s-parent">s-parent</a> — devpro-check-plan<', page)


def test_the_decoration_and_the_pages_script_share_one_scope(tmp_path: Path, serve) -> None:
    """The decoration's script and a session page's own script are both classic scripts in the page's
    one global scope: a name both declare kills the page's script at parse — the page serves, styles,
    and draws nothing, the session content blank while the nav's own script still runs. The two
    compile together, which is the hold a render-side check cannot give: each script compiles alone.

    The one name the deco publishes is the notation the page calls, `globalThis.devproFormat`: the
    page's script reads it from this scope, so the deco's body must run before it — a global assigned
    inside a script that returned early, or one the page script re-declared as a `const`, is a page
    whose tree and header draw nothing.

    A skip without bun is the fixture's own: the compile needs an engine, and the engines a test
    environment carries are the ones the profiler's own fixtures already require."""
    import shutil

    if shutil.which("bun") is None:
        pytest.skip("bun is not installed")
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    served = serve(root)
    page = served.get("page/s-one")[2].decode("utf-8")
    blocks = re.findall(r"<script>(.*?)</script>", page, re.S)
    deco = (files("devpro.profiler") / "deco.js").read_text(encoding="utf-8")
    assert '<script src="/profiler/deco.js"></script>' in page

    script = tmp_path / "scope.js"
    script.write_text(deco + "\n" + "\n".join(blocks), encoding="utf-8")
    compile_with = subprocess.run(
        ["bun", "-e", f"new Function(require('fs').readFileSync({str(script)!r}, 'utf8'))"],
        capture_output=True,
        text=True,
    )

    assert compile_with.returncode == 0, compile_with.stderr


def test_dashboard_root_is_the_git_root_of_the_directory_it_runs_in(tmp_path: Path, monkeypatch) -> None:
    """`dashboard_root` takes the directory the command runs in up to the git root, as the profiler's
    `serve` took its project: a dashboard started in a project's subdirectory serves that project,
    and one following `CLAUDE_PROJECT_DIR` would serve the project the outermost claude session
    launched in instead."""
    root = project(tmp_path / "proj", {"ROADMAP.md": "## Next\n"})
    subdirectory = root / "PROJECT_DOCS"
    subdirectory.mkdir()
    elsewhere = project(tmp_path / "elsewhere", {})
    monkeypatch.chdir(subdirectory)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(elsewhere))

    assert dashboard_root() == str(root)


@dataclass
class Served:
    """What one run of the dashboard command printed."""

    url: str
    status: int
    rest: list[str]
    stderr: str


def _serve_the_command(cwd: Path, *arguments: str) -> Served:
    """`python -m devpro dashboard` with arguments, in cwd: its first line, its root fetched without
    following the answer, then stopped."""
    child = subprocess.Popen(
        [sys.executable, "-m", "devpro", "dashboard", "--port", "0", *arguments],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
    )
    assert child.stdout is not None and child.stderr is not None
    try:
        url = child.stdout.readline().strip()
        client = Client(url)
        status = client.raw("GET", "", host=f"{client.host}:{client.port}")[0]
        client.post("api/stop", {})
        rest, err = child.communicate(timeout=TIMEOUT)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
    return Served(url=url, status=status, rest=rest.splitlines(), stderr=err)


def test_the_command_prints_the_loopback_url_once_and_serves_the_project_it_runs_in(tmp_path: Path) -> None:
    """`devpro dashboard` in a project's subdirectory prints one `127.0.0.1` URL and nothing else, and
    serve that project at it — the root answering its redirect to the board — ending on the board's
    stop: a verb that serves another root, binds elsewhere, or reports on its stream after the URL,
    is not the loopback server the record states."""
    root = project(tmp_path / "proj", {"ROADMAP.md": "## Next\n\n### Two\n\nMore.\n"})
    subdirectory = root / "PROJECT_DOCS"
    subdirectory.mkdir()

    served = _serve_the_command(subdirectory)

    assert loopback(served.url)
    assert served.status == 302
    assert (served.rest, served.stderr) == ([], "")


def test_the_command_serves_the_project_it_names_from_a_directory_outside_it(tmp_path: Path) -> None:
    """`devpro dashboard` naming project A from inside project B serves A's stores and board, not
    B's: a server launched by another process from any working directory must reach the project it
    is told to serve. Launched inside A, a server that ignores the positional would still serve A."""
    a = project(tmp_path / "a", {"ROADMAP.md": "## Next\n"})
    b = project(tmp_path / "b", {"ROADMAP.md": "## Next\n"})
    store(a, "in-a", [_tool_call("in-a", "2026-01-01T00:00:00.000Z", "ls")])
    store(b, "in-b", [_tool_call("in-b", "2026-01-01T00:00:00.000Z", "ls")])
    child = subprocess.Popen(
        [sys.executable, "-m", "devpro", "dashboard", str(a), "--port", "0"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=b,
    )
    assert child.stdout is not None and child.stderr is not None
    try:
        client = Client(child.stdout.readline().strip())
        feed = json.loads(client.get("api/traces")[2])

        payload = json.loads(client.get("api/board")[2])
        client.post("api/stop", {})
        child.communicate(timeout=TIMEOUT)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()

    assert [entry["id"] for entry in feed] == ["in-a"]
    assert payload["project"] == "a"


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(["--port", "70000"], id="port-above-the-range"),
        pytest.param(["--port", "-1"], id="negative-port"),
        pytest.param(["--port", "eight"], id="not-a-number"),
        pytest.param(["--bogus"], id="unknown-option"),
    ],
)
def test_an_option_the_verb_cannot_take_is_refused_as_the_other_verbs_refuse_one(
    tmp_path: Path, arguments: list[str]
) -> None:
    """A port outside 0-65535, one that is not a number, and an unknown option are refused by the
    parser with exit status 2 and nothing on stdout, binding no port: the dashboard's command line
    is read as the other verbs' are, before anything serves. A port outside the range is refused by
    naming the range, not by the parser's `choices` message, which would list all 65,536 values."""
    done = subprocess.run(
        [sys.executable, "-m", "devpro", "dashboard", *arguments],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        cwd=tmp_path,
    )

    assert (done.returncode, done.stdout) == (2, "")
    assert "error:" in done.stderr
    assert len(done.stderr) < 500


@pytest.mark.parametrize(
    "arguments, message",
    [
        pytest.param(
            ["/nonexistent-dir-xyz", "--port", "0"], "no such directory: /nonexistent-dir-xyz", id="not-a-directory"
        ),
        pytest.param(["a-file.txt", "--port", "0"], "no such directory: a-file.txt", id="a-file-not-a-directory"),
    ],
)
def test_a_project_directory_that_is_not_a_directory_is_refused(
    tmp_path: Path, arguments: list[str], message: str
) -> None:
    """A named `<project-dir>` that is not a directory, an existing file among them, is refused as the
    usage error the board verb gave, exit status 2 and nothing on stdout: a dashboard that walks up
    from a name that is no directory serves whatever project the directory sits in instead, so a
    mistyped project directory does not serve the wrong one's files."""
    (tmp_path / "a-file.txt").write_text("x\n", encoding="utf-8")
    done = subprocess.run(
        [sys.executable, "-m", "devpro", "dashboard", *arguments],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        cwd=tmp_path,
    )

    assert (done.returncode, done.stdout) == (2, "")
    assert message in done.stderr


def test_a_port_already_bound_is_refused_before_the_url(tmp_path: Path) -> None:
    """A port another process holds refuses the verb as `error: cannot listen: <reason>` with exit
    status 2 and nothing on stdout: the dashboard's construction is traced back to the user, so a
    second dashboard on a taken `--port` says so instead of raising out of the command."""
    root = project(tmp_path / "proj", {"ROADMAP.md": "## Next\n"})
    with socket.socket() as taken:
        taken.bind(("127.0.0.1", 0))
        taken.listen()
        done = subprocess.run(
            [sys.executable, "-m", "devpro", "dashboard", str(root), "--port", str(taken.getsockname()[1])],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            cwd=tmp_path,
        )

    assert (done.returncode, done.stdout) == (2, "")
    assert done.stderr.startswith("error: cannot listen: ")


def test_a_board_file_that_cannot_be_read_is_refused_before_the_url(tmp_path: Path) -> None:
    """A file the board reads that cannot be read refuses the verb as `error: cannot read: <file>`
    with exit status 2 and nothing on stdout, and binds no port: the board is read on construction,
    so the refusal lands before the URL and before any request is answered."""
    root = project(tmp_path / "proj", {"ROADMAP.md": "## Next\n\n### Two\n\nMore.\n"})
    roadmap = root / "ROADMAP.md"
    roadmap.chmod(0)
    try:
        if not _unreadable(roadmap):
            pytest.skip("chmod denies this user no read")
        done = subprocess.run(
            [sys.executable, "-m", "devpro", "dashboard", str(root), "--port", "0"],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            cwd=tmp_path,
        )
    finally:
        roadmap.chmod(0o644)

    assert (done.returncode, done.stdout) == (2, "")
    assert done.stderr == f"error: cannot read: {roadmap}\n"
