"""The dashboard's serve surface: the traces panel at the root and `/page/<id>`, the board panel at
`/board/` and the root paths its script calls, the served documents, and the guards both panels carry."""

import io
import json
import os
import subprocess
import sys
import threading
from dataclasses import asdict, dataclass
from importlib.resources import files
from pathlib import Path

import pytest

from devpro.dashboard.server import BOARD_LINK, CONTENT_SECURITY_POLICY, DashboardServer, dashboard_root, loopback
from devpro.dicing.kanban.board import read_board
from devpro.profiler.pages import index_html

from .conftest import PLAN, TIMEOUT, Client, project, record, store

ASSETS = Path(str(files("devpro.dicing.kanban") / "assets"))


def _tool_call(session: str, at: str, name: str) -> dict:
    return record(at, tool="Bash", name=name, session=session)


def test_the_root_is_the_traces_index_with_the_board_link_before_its_close(tmp_path: Path, serve) -> None:
    """The root is `index_html`'s page byte for byte with one line added before `</html>`, and no
    other change: an index rendered another way — a row dropped or invented, or the link spliced
    after the document closed — is a root that is not the traces panel plus one link."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])

    status, content_type, body = serve(root).get("")

    index = index_html(root)
    assert (status, content_type) == (200, "text/html")
    assert index.endswith("</html>\n")
    assert body == (index.rpartition("</html>")[0] + "\n" + BOARD_LINK + "</html>\n").encode("utf-8")


def test_the_traces_panel_serves_its_index_and_its_pages(tmp_path: Path, serve) -> None:
    """Two stores' sessions: the root lists both, each once, and `/page/<id>` renders that session's
    own records — a dashboard that answers the routes with an empty page, or another session's, has
    kept the routes and lost the panel."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")], directory=".profiler-claude")
    store(root, "s-two", [_tool_call("s-two", "2026-01-01T00:00:05.000Z", "cat")], directory=".profiler-opencode")
    client = serve(root)

    index = client.get("")[2].decode("utf-8")
    status, content_type, page = client.get("page/s-one")

    assert index.count('href="/page/s-one"') == 1 and index.count('href="/page/s-two"') == 1
    assert (status, content_type) == (200, "text/html")
    data = json.loads(page.decode("utf-8").split("const D = ", 1)[1].split(";\n", 1)[0])
    assert (data["session"], [call["name"] for call in data["calls"]]) == ("s-one", ["ls"])


def test_an_unreadable_store_is_stated_in_the_index_rather_than_failing_it(tmp_path: Path, serve) -> None:
    """A `.profiler-*` store the dashboard cannot list is named as unreadable in the root and the
    other store's session is still listed: the index's rule reaches the dashboard's root."""
    root = project(tmp_path / "proj", {})
    store(root, "s-one", [_tool_call("s-one", "2026-01-01T00:00:00.000Z", "ls")])
    locked = store(
        root, "s-broken", [_tool_call("s-broken", "2026-01-01T00:00:00.000Z", "ls")], directory=".profiler-broken"
    )
    os.chmod(locked.parent, 0)
    try:
        if not _denied(locked.parent):
            pytest.skip("chmod denies this user no read")
        status, _, body = serve(root).get("")
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
        pytest.param("GET", "board/", b"", 200, id="board-page"),
        pytest.param("GET", "board/board.js", b"", 200, id="board-script"),
        pytest.param("GET", "", b"", 200, id="root"),
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
    served documents and a 404 — carries `nosniff`, and each page the same Content-Security-Policy;
    the JSON payload carries `nosniff` alone. A panel that drops the board's policy, or a refusal
    a browser renders as a page without one, loses the guard the panels carried."""
    client = serve(project(tmp_path / "proj", {"ROADMAP.md": "## Next\n"}))
    host = f"{client.host}:{client.port}"

    for path in ("", "board/", "board/board.js", "ROADMAP.md"):
        status, headers = client.raw("GET", path, host=host)
        assert status == 200, path
        assert headers["Content-Security-Policy"] == CONTENT_SECURITY_POLICY, path
        assert headers["X-Content-Type-Options"] == "nosniff", path
    for path in ("nothing.md", "nothing.js"):
        status, headers = client.raw("GET", path, host=host)
        assert status == 404, path
        assert headers["Content-Security-Policy"] == CONTENT_SECURITY_POLICY, path
        assert headers["X-Content-Type-Options"] == "nosniff", path
    _, headers = client.raw("GET", "api/board", host=host)
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "Content-Security-Policy" not in headers


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


def _serve_the_command(cwd: Path) -> Served:
    """`python -m devpro dashboard --port 0` in cwd: its first line, its root fetched, then stopped."""
    child = subprocess.Popen(
        [sys.executable, "-m", "devpro", "dashboard", "--port", "0"],
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
        status = client.get("")[0]
        client.post("api/stop", {})
        rest, err = child.communicate(timeout=TIMEOUT)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
    return Served(url=url, status=status, rest=rest.splitlines(), stderr=err)


def test_the_command_prints_the_loopback_url_once_and_serves_the_project_it_runs_in(tmp_path: Path) -> None:
    """`devpro dashboard` in a project's subdirectory prints one `127.0.0.1` URL and nothing else, and
    serves that project at it, ending on the board's stop: a verb that serves another root, binds
    elsewhere, or reports on its stream after the URL, is not the loopback server the record states."""
    root = project(tmp_path / "proj", {"ROADMAP.md": "## Next\n\n### Two\n\nMore.\n"})
    subdirectory = root / "PROJECT_DOCS"
    subdirectory.mkdir()

    served = _serve_the_command(subdirectory)

    assert loopback(served.url)
    assert served.status == 200
    assert (served.rest, served.stderr) == ([], "")


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
    is read as the other verbs' are, before anything serves."""
    done = subprocess.run(
        [sys.executable, "-m", "devpro", "dashboard", *arguments],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        cwd=tmp_path,
    )

    assert (done.returncode, done.stdout) == (2, "")
    assert "error:" in done.stderr
