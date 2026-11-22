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

from devpro.dashboard.server import (
    BOARD_PATH,
    CONTENT_SECURITY_POLICY,
    DashboardServer,
    dashboard_root,
    loopback,
)
from devpro.dicing.kanban.board import read_board
from devpro.profiler.pages import BAND_MARK, CHROME_MARK, CSS_SLOT, NAV_MARK, SHARED_CSS

from .conftest import PLAN, TIMEOUT, Client, project, record, store

ASSETS = Path(str(files("devpro.dicing.kanban") / "assets"))


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
    """`/api/state` answers `{"state": "live"}` for the host it is served on: the nav's indicator
    reads that answer on every view, so an endpoint answering anything else — nothing, or a payload
    the indicator would have to dig for — leaves the profiler view's chrome reading no state."""
    client = serve(project(tmp_path / "proj", {}))

    status, content_type, body = client.get("api/state")

    assert (status, content_type, json.loads(body)) == (200, "application/json", {"state": "live"})


def test_the_profiler_view_serves_its_list_and_its_pages(tmp_path: Path, serve) -> None:
    """Two stores' sessions: `/profiler/` lists both, each once, and `/page/<id>` renders that
    session's own records — a view that answers its routes with an empty page, or another session's,
    has kept the routes and lost the view."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")], directory=".profiler-claude")
    store(root, "s-two", [_tool_call("s-two", "2026-01-01T00:00:05.000Z", "cat")], directory=".profiler-opencode")
    client = serve(root)

    index = client.get("profiler/")[2].decode("utf-8")
    status, content_type, page = client.get("page/s-one")

    assert index.count('href="/page/s-one"') == 1 and index.count('href="/page/s-two"') == 1
    assert (status, content_type) == (200, "text/html")
    data = json.loads(page.decode("utf-8").split("const D = ", 1)[1].split(";\n", 1)[0])
    assert (data["session"], [call["name"] for call in data["calls"]]) == ("s-one", ["ls"])


def test_an_unreadable_store_is_stated_in_the_index_rather_than_failing_it(tmp_path: Path, serve) -> None:
    """A `.profiler-*` store the dashboard cannot list is named as unreadable in the profiler view's
    list and the other store's session is still listed: the index's rule reaches the view's page."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    locked = store(
        root, "s-broken", [_tool_call("s-broken", "2026-01-01T00:00:00.000Z", "ls")], directory=".profiler-broken"
    )
    os.chmod(locked.parent, 0)
    try:
        if not _denied(locked.parent):
            pytest.skip("chmod denies this user no read")
        status, _, body = serve(root).get("profiler/")
    finally:
        os.chmod(locked.parent, 0o755)

    assert status == 200
    assert ".profiler-broken is unreadable" in body.decode("utf-8")
    assert "/page/s-one" in body.decode("utf-8")


def _denied(path: Path) -> bool:
    try:
        os.listdir(path)
    except PermissionError:
        return True
    return False


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

    status, _, body = serve(root).get(path)

    assert status == 200
    assert body == (ASSETS / name).read_text(encoding="utf-8").encode("utf-8")


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


def test_the_profiler_view_carries_its_nav_and_legend_once(tmp_path: Path, serve) -> None:
    """`/profiler/` carries the frame band — the how-to-read legend present exactly once — and the
    nav with `profiler` the active view and `kanban` linking `/board/`: a band that drops the legend
    loses the view's how-to-read, one that shows it twice breaks one home and two carriers, and a nav
    naming no active view leaves the reader unable to tell which view is shown."""
    client = serve(project(tmp_path / "proj", {}))
    index = client.get("profiler/")[2].decode("utf-8")

    assert index.count("How to read this") == 1
    assert 'class="frame-band' in index
    assert re.search(r'<a class="view active" href="/profiler/" aria-current="page">profiler</a>', index)
    assert re.search(r'<a class="view" href="/board/">kanban</a>', index)


@pytest.mark.parametrize(
    "path, scripts",
    [
        pytest.param("profiler/", 1, id="index"),
        pytest.param("page/s-one", 2, id="session-page"),
    ],
)
def test_every_profiler_view_page_renders_the_way_the_file_flow_renders_it(
    tmp_path: Path, serve, path: str, scripts: int
) -> None:
    """A served page is the page the file flow writes, with the dashboard's own chrome around it: the
    same stylesheet inlined once, the nav once with the server block, the nav's script once — beside
    the render's own on a session's page — and no mark the splice did not fill. A served page whose
    layer differs from the file's, or which carries an unfilled mark or a second nav, is the page the
    dashboard serves standing apart from the one the render writes."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    page = serve(root).get(path)[2].decode("utf-8")

    assert page.count(SHARED_CSS) == 1
    assert page.count('class="site-nav') == 1 and page.count('id="connection"') == 1 and page.count('id="stop"') == 1
    assert page.count("<script>") == scripts and page.count("api/state") == 1
    assert not [mark for mark in (CSS_SLOT, NAV_MARK, BAND_MARK, CHROME_MARK) if mark in page]


def test_the_board_page_holds_its_chrome_once_and_the_nav_supplies_it(tmp_path: Path, serve) -> None:
    """`/board/` carries the nav's server block — the indicator and the stop — once, and names two
    scripts, the files the board path serves beside it: the nav's, whose text the board's own file
    holds, and its board's. A board page writing its own copy of the block is the second chrome the
    one nav replaced; one naming a file the board path does not serve is a page whose stop never
    loads."""
    page = serve(project(tmp_path / "proj", {})).get("board/")[2].decode("utf-8")

    assert page.count('id="connection"') == 1 and page.count('id="stop"') == 1
    assert re.findall(r'<script src="([^"]+)"', page) == ["chrome.js", "board.js"]


def test_a_session_page_carries_the_bands_legend_and_the_way_back(tmp_path: Path, serve) -> None:
    """`/page/<id>` carries the band with the legend once and `Return to list` linking `/profiler/`,
    and its body carries no second legend: drill-down with no way back strands the reader on the
    session, and a doubled legend shows one home where the target states two carriers."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    page = serve(root).get("page/s-one")[2].decode("utf-8")

    assert page.count("How to read this") == 1
    assert re.search(r'<a class="return" href="/profiler/">Return to list</a>', page)
    assert 'class="frame-band' in page
    assert re.search(r'<a class="view active" href="/profiler/" aria-current="page">profiler</a>', page)


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
    serves that project at it — the root answering its redirect to the board — ending on the board's
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
        index = client.get("profiler/")[2].decode("utf-8")

        payload = json.loads(client.get("api/board")[2])
        client.post("api/stop", {})
        child.communicate(timeout=TIMEOUT)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()

    assert 'href="/page/in-a"' in index and 'href="/page/in-b"' not in index
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
