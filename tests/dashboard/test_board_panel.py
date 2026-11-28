"""Unit tests for the dashboard's board panel: the page's files, the board payload over the board
model, live following of the watched files, and the moves between Roadmap and Design.

The panel is `KanbanServer` over a `DashboardServer`, served at `/board/` and the root paths its
page calls; the tests drive the dashboard, since that is the one server the project serves. The
tests the two panels share — the board's payload over the same file, a card's move there and back —
are the dashboard suite's (`tests/dashboard/test_server.py`), and are not repeated here; the served
file's tests carry a root escape no other suite does, a request for `..%2F` reaching the project
root refused with a 404.

`_serve_the_command` here and the one in the dashboard suite both start `python -m devpro
dashboard`, and neither is the other's copy: this one ends the child by the interrupt and the stop
button, the panel's two ways to stop, so it reads the exit status and both streams; the dashboard's
brings its own arguments and working directory and reads the root a browser lands on, so it stops
the server through its API and returns what it served.
"""

import errno
import http.client
import io
import json
import os
import select
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import asdict
from email.message import Message
from importlib.resources import files
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from devpro.dashboard.server import DashboardServer
from devpro.kanban import board as board_module
from devpro.kanban import server as server_module
from devpro.kanban.board import read_board
from devpro.profiler.read import DISPATCH_HUES

from .conftest import record

_PLAN = (
    "# Plan\n\nRelease: 9.9.9\n\n## Status\n\n| Package | Rating | State |\n|---|---|---|\n"
    "| P1 | expert | |\n| P2 | expert | dispatchable |\n| P3 | mechanical | landed |\n"
)
_ROADMAP = "## Next\n\n### Search index\n\nBuild an index.\n"
_TWO = "\n### Two\n"  # a second ticket, appended to _ROADMAP
_DESIGN = "# Design\n\nText.\n"
_TIMEOUT = 10


def _project(root: Path, files_: dict[str, str]) -> str:
    (root / ".git").mkdir(parents=True)
    for name, text in files_.items():
        _create(root / name, text)
    return str(root)


def _create(path: Path, text: str) -> None:
    """Write text to path, creating its directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class _Client:
    def __init__(self, url: str) -> None:
        self.url = url

    def raw(self, method: str, path: str, *, body: bytes = b"", headers: dict[str, str]) -> tuple[int, Message]:
        """The status and headers of a request sent with exactly the headers given, Host included
        where given."""
        url = urlsplit(self.url)
        connection = http.client.HTTPConnection(url.hostname, url.port, timeout=_TIMEOUT)
        try:
            connection.request(method, "/" + path, body=body, headers=headers)
            response = connection.getresponse()
            response.read()
            return response.status, response.headers
        finally:
            connection.close()

    def get(self, path: str) -> tuple[int, str, bytes]:
        try:
            with urllib.request.urlopen(self.url + path, timeout=_TIMEOUT) as r:
                return r.status, r.headers.get_content_type(), r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get_content_type(), e.read()

    def board(self, since=None) -> dict:
        status, _, body = self.get("api/board" if since is None else f"api/board?since={since}")
        assert status == 200
        return json.loads(body)

    def post(self, path: str, body: dict) -> tuple[int, dict]:
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(self.url + path, data, {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=_TIMEOUT) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())


_SERVED_PROJECT = {
    "ACTIVE_PLAN.md": _PLAN,
    "ROADMAP.md": _ROADMAP,
    "ACTIVE_DESIGN.md": _DESIGN,
    "ROADMAP_DESIGNS/README.md": "",
}
"""The project a test that only reads the panel is served: every file the board reads, standing."""


@pytest.fixture(scope="session")
def served_project(tmp_path_factory: pytest.TempPathFactory) -> str:
    """`_SERVED_PROJECT` written once for the whole session. A test that writes under it would
    leak into the run after it, so the ones that change their files are served their own."""
    return _project(tmp_path_factory.mktemp("board-panel") / "proj", _SERVED_PROJECT)


@pytest.fixture(scope="session")
def panel(served_project: str) -> Iterator[_Client]:
    """The dashboard serving `served_project`, for every test that only reads the panel. Such a test
    pins the panel's rendering or its route, not the server, and a boot is a measured 52.9 ms of the
    run, so the read-only tests share one. A test that writes the board, follows a change to its
    files, stops the server, or expects a quiet stderr starts its own. The server's stderr is
    captured here and dropped: the capture keeps its output off the run's log."""
    err = io.StringIO()
    server = DashboardServer(served_project, stderr=err)
    server.start()
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    try:
        yield _Client(server.url)
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.fixture
def serve():
    """Start a dashboard, its board panel over a project's root; every one started is stopped."""
    started = []

    def start(root: str, *, stderr: io.StringIO | None = None) -> _Client:
        server = DashboardServer(root, stderr=stderr if stderr is not None else io.StringIO())
        server.start()
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
        thread.start()
        started.append((server, thread))
        return _Client(server.url)

    def stop_all() -> None:
        while started:
            server, thread = started.pop()
            server.shutdown()
            thread.join()
            server.server_close()

    start.stop_all = stop_all
    yield start
    stop_all()


def _json_round_trip(value):
    return json.loads(json.dumps(value))


def test_the_board_page_is_drawn_under_the_board_path(panel):
    """The board's `index.html` is served at `/board/`, the URL its link line opens: the page is the
    panel's, not a rendering of the dashboard's, and its own path reaches it."""
    client = panel

    status, _, body = client.get("board/")

    assert status == 200
    assets = files("devpro.kanban") / "assets"
    assert body == (assets / "index.html").read_text(encoding="utf-8").encode("utf-8")
    assert client.get("board/nothing.js")[0] == 404


_SERVED = {
    "ROADMAP.md": "## Next\n\n### Café\n",
    "ACTIVE_DESIGN/entry-point.md": "# Design\n",
    "ACTIVE_DESIGN/a b%.md": "## Goals\n",
    "ACTIVE_PLAN_REVIEW.md": "# Review\n",
    "PROJECT_DOCS/SPEC/arch.md": "# A leaf\n",
    "ROADMAP_DESIGNS/tree/entry-point.md": "# Tree\n",
    "ROADMAP_DESIGNS/tree/leaf.md": "## Leaf\n",
    "notes.txt": "not markdown\n",
    "docs/notes.md": "# In a directory no pattern names\n",
}


@pytest.mark.parametrize(
    "path, name",
    [
        pytest.param("ROADMAP.md", "ROADMAP.md", id="roadmap"),
        pytest.param("ACTIVE_PLAN_REVIEW.md", "ACTIVE_PLAN_REVIEW.md", id="root-document-the-board-does-not-read"),
        pytest.param("PROJECT_DOCS/SPEC/arch.md", "PROJECT_DOCS/SPEC/arch.md", id="project-docs-leaf"),
        pytest.param("ACTIVE_DESIGN/a%20b%25.md", "ACTIVE_DESIGN/a b%.md", id="percent-decoded-leaf"),
        pytest.param("ROADMAP_DESIGNS/tree/entry-point.md", "ROADMAP_DESIGNS/tree/entry-point.md", id="parked-tree"),
        pytest.param("ROADMAP_DESIGNS/tree/leaf.md", "ROADMAP_DESIGNS/tree/leaf.md", id="parked-tree-leaf"),
        pytest.param("ROADMAP_DESIGNS/a%FF.md", "ROADMAP_DESIGNS/a\udcff.md", id="parked-file-named-not-utf-8"),
    ],
)
def test_a_served_file_is_served(tmp_path, serve, path, name):
    files_ = dict(_SERVED)
    if name not in files_:
        files_[name] = "# A\n"
        try:
            _create(tmp_path / "probe" / os.path.basename(name), "")
        except OSError:
            pytest.skip("the file system refuses a name that is not UTF-8")
    root = _project(tmp_path / "proj", files_)
    client = serve(root)
    status, content_type, body = client.get(path)
    escaped = client.raw("GET", "..%2Fproj%2FROADMAP.md", headers={"Host": urlsplit(client.url).netloc})[0]

    assert (status, content_type, body) == (200, "text/markdown", files_[name].encode("utf-8"))
    assert escaped == 404


def _denied(path: Path) -> bool:
    """Whether path, its permissions just removed, now refuses this user a read."""
    try:
        path.read_text(encoding="utf-8")
    except PermissionError:
        return True
    return False


def test_an_unreadable_served_file_is_refused_alone(tmp_path, serve):
    root = _project(tmp_path / "proj", _SERVED)
    client = serve(root)
    leaf = tmp_path / "proj" / "ACTIVE_DESIGN" / "a b%.md"
    leaf.chmod(0)
    try:
        if not _denied(leaf):
            pytest.skip("chmod denies this user no read")
        assert client.get("ROADMAP.md")[0] == 200
        assert client.get("ACTIVE_DESIGN/a%20b%25.md")[0] == 404
    finally:
        leaf.chmod(0o644)


@pytest.mark.parametrize(
    "change",
    [
        pytest.param(
            lambda root: (root / "ROADMAP.md").write_text(_ROADMAP + "- Two.\n", encoding="utf-8"), id="content"
        ),
        pytest.param(lambda root: (root / "ACTIVE_DESIGN.md").write_text(_DESIGN, encoding="utf-8"), id="creation"),
        pytest.param(lambda root: (root / "ACTIVE_PLAN.md").unlink(), id="deletion"),
        pytest.param(
            lambda root: (root / "ROADMAP_DESIGNS" / "new.md").write_text("x\n", encoding="utf-8"), id="parked"
        ),
        pytest.param(
            lambda root: _create(root / "ACTIVE_DESIGN" / "entry-point.md", "## Goals\n"), id="diced-design-created"
        ),
        pytest.param(
            lambda root: _create(root / "ROADMAP_DESIGNS" / "tree" / "entry-point.md", "# Tree\n"), id="parked-tree"
        ),
    ],
)
def test_a_change_to_a_watched_file_is_followed(tmp_path, serve, change):
    root = _project(
        tmp_path / "proj", {"ACTIVE_PLAN.md": _PLAN, "ROADMAP.md": _ROADMAP, "ROADMAP_DESIGNS/README.md": ""}
    )
    client = serve(root)
    board = client.board()

    change(Path(root))
    # The change lands by the first board the poll reads after it, the registered change irrelevant:
    # the board, not the version it bumps, is what says the changed files were read.
    changed = client.board(since=board["version"])
    assert changed["board"] == _json_round_trip(asdict(read_board(root)))

    assert changed["version"] != board["version"]
    assert changed["board"] != board["board"]


def test_a_change_to_a_diced_designs_leaf_is_followed(tmp_path, serve):
    entry = "# Design\n\nContents:\n\n- [Goals](goals.md)\n"
    root = _project(tmp_path / "proj", {"ACTIVE_DESIGN/entry-point.md": entry, "ACTIVE_DESIGN/goals.md": "## Goals\n"})
    client = serve(root)
    board = client.board()

    (Path(root) / "ACTIVE_DESIGN" / "goals.md").write_text("## Goals\n\n### Fast\n\nFast.\n", encoding="utf-8")
    changed = client.board(since=board["version"])

    assert changed["board"]["design"][1]["text"] == "Fast."


def test_the_payloads_since_holds_the_answer_until_the_board_changes(tmp_path, serve):
    """`/api/board?since=<version>` holds the answer until the board changes, and the query survives
    the dashboard's route to the panel: a panel handed the path alone loses the query, so every poll
    answers at once with the unchanged board, and a page following its files then spins on it. The
    answer at close is still the board, so the wait is bounded — the version the waiter gets is the
    one it asked for, never a newer board's.

    `clauses.TEST_PRECONDITION`. The defect: the wait was bounded by `LONG_POLL_SECONDS`, which is
    the server's own poll term, while the waiter's request gives up at `_TIMEOUT`; a poll whose
    condition is never satisfied blocks until the shutdown wakes it, and a shutdown past `_TIMEOUT`
    leaves the wait under the old bound and the assertion silent. The wait is held to `_TIMEOUT`, so
    that poll fails here."""
    client = serve(_project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP}))
    version = client.board()["version"]
    answers = []
    asked = threading.Event()
    waited = []

    def wait() -> None:
        started = time.monotonic()
        asked.set()
        answers.append(client.board(since=version))
        waited.append(time.monotonic() - started)

    waiter = threading.Thread(target=wait)
    waiter.start()
    assert asked.wait(_TIMEOUT)
    time.sleep(2 * server_module.POLL_SECONDS)
    assert not answers

    serve.stop_all()
    waiter.join(_TIMEOUT)

    assert not waiter.is_alive()
    assert 0 < waited[0] < _TIMEOUT
    assert answers[0]["version"] == version


def test_an_unreadable_file_keeps_the_last_good_board_and_is_named(tmp_path):
    if os.geteuid() == 0:
        pytest.skip("root reads any file")
    root = _project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP})
    err = io.StringIO()
    server = DashboardServer(root, stderr=err)
    roadmap = Path(root) / "ROADMAP.md"
    try:
        server.start()
        before = server.board.payload(None)
        roadmap.chmod(0)
        deadline = time.monotonic() + _TIMEOUT
        while str(roadmap) not in err.getvalue() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert server.board.payload(None)["board"] == before["board"]
        roadmap.chmod(0o644)
        roadmap.write_text(_ROADMAP + _TWO, encoding="utf-8")
        after = before
        while len(after["board"]["roadmap"]) != 3 and time.monotonic() < deadline:
            after = server.board.payload(str(after["version"]))
    finally:
        roadmap.chmod(0o644)
        server.server_close()

    named = err.getvalue().splitlines()
    assert len(named) == 1 and str(roadmap) in named[0]
    assert len(after["board"]["roadmap"]) == 3


def test_a_change_to_the_stores_is_followed(tmp_path, serve):
    """`clauses.TEST_PRECONDITION`: the defect is a watched set holding the board's files alone, so a
    dispatch the capture records surfaces on no open page and the agents column stands still while work
    goes on — the stores' files never followed, an append or a new session file alike.

    The stores are watched as directories: a record appended to a session file and a newly written
    session file each change a store's digest, and the next board answers the running dispatch the
    records now hold."""
    root = _project(tmp_path / "proj", {"ACTIVE_PLAN.md": _PLAN, "ROADMAP.md": _ROADMAP})
    store = Path(root) / ".devpro-temp" / ".profiler-opencode"
    _create(store / "s-parent.jsonl", "")
    client = serve(root)
    board = client.board()

    _append(store / "s-parent.jsonl", _dispatch("2026-01-01T00:00:05.000Z", "s-child"))
    appended = client.board(since=board["version"])
    _append(store / "s-other.jsonl", _dispatch("2026-01-01T00:00:09.000Z", "s-other-child"))
    created = client.board(since=appended["version"])

    assert [a["id"] for a in appended["agents"]] == ["s-child"]
    assert [(a["id"], a["hue"]) for a in created["agents"]] == [("s-child", 1), ("s-other-child", 2)]


def test_a_running_dispatch_keeps_its_color_as_another_opens(tmp_path, serve):
    """`clauses.TEST_PRECONDITION`: the defect is a color read off the running set's place at each
    payload — every dispatch recolored as one opens or ends — where a color is the dispatch's own,
    fixed by its rank among every dispatch the stores opened, and holds while it runs.

    Two dispatches open in `at` order, the palette's first and second; a third opens later and takes
    the third, and every earlier dispatch keeps the hue it had."""
    root = _project(tmp_path / "proj", {})
    store = Path(root) / ".devpro-temp" / ".profiler-opencode"
    opened = [
        ("2026-01-01T00:00:09.000Z", "s-late"),
        ("2026-01-01T00:00:05.000Z", "s-first"),
        ("2026-01-01T00:00:07.000Z", "s-second"),
    ]
    _append(store / "s-parent.jsonl", "".join(_dispatch(at, child) for at, child in opened))
    client = serve(root)
    board = client.board()

    _append(store / "s-parent.jsonl", _dispatch("2026-01-01T00:00:11.000Z", "s-third"))
    after = client.board(since=board["version"])

    assert [(a["id"], a["hue"]) for a in board["agents"]] == [("s-first", 1), ("s-second", 2), ("s-late", 3)]
    assert [(a["id"], a["hue"]) for a in after["agents"]] == [
        ("s-first", 1),
        ("s-second", 2),
        ("s-late", 3),
        ("s-third", 4),
    ]


def test_closing_a_dispatch_leaves_the_later_hues_unchanged(tmp_path, serve):
    """`clauses.TEST_PRECONDITION`: the defect (R2) is a hue read off the dispatch's place among the
    dispatches *still running*, so closing an earlier one shifts every later one a hue down — a
    recoloring of a dispatch that is working, while the leaves say a running dispatch's color is
    stable while it runs.

    Three open in `at` order and take the palette's first three; `s-first` ends and leaves the running
    set, and `s-second` and `s-third` keep the hues they had — the closed dispatch's rank in the
    stores' history still counted, nothing pruned. Without the fix `s-second` is recolored 1 and
    `s-third` 2."""
    root = _project(tmp_path / "proj", {})
    store = Path(root) / ".devpro-temp" / ".profiler-opencode"
    opened = [("2026-01-01T00:00:01.000Z", "s-first"), ("2026-01-01T00:00:03.000Z", "s-second")]
    opened += [("2026-01-01T00:00:05.000Z", "s-third")]
    _append(store / "s-parent.jsonl", "".join(_dispatch(at, child) for at, child in opened))
    client = serve(root)
    board = client.board()

    _append(store / "s-first.jsonl", _idle("2026-01-01T00:00:07.000Z", "s-first"))
    after = client.board(since=board["version"])

    assert [(a["id"], a["hue"]) for a in board["agents"]] == [
        ("s-first", 1),
        ("s-second", 2),
        ("s-third", 3),
    ]
    assert [(a["id"], a["hue"]) for a in after["agents"]] == [("s-second", 2), ("s-third", 3)]


def test_more_running_dispatches_than_hues_share_a_color_rather_than_shift(tmp_path, serve):
    """`clauses.TEST_PRECONDITION`: the defect (R2) is a hue read off the dispatch's place among the
    dispatches still running, which shifts every hue when one of them closes; the palette is smaller
    than the set the store holds, so a hue that follows a running dispatch's count is a promise the
    leaves cannot keep however many dispatches run.

    Seven closed dispatches hold ranks 0 to 6, then nine running ones hold 7 to 15: `s-running-1`
    takes hue 8 and `s-running-2` hue 1, and `s-running-9`, whose rank wraps past the palette's size,
    takes hue 8 again — the hue `s-running-1` holds — so more running dispatches than hues share a
    color rather than start a new round. The closed dispatches' ranks still count, so `s-running-1`'s
    hue is its own rank's, not the palette's first. Read off the running set's places — the defect —
    the closed dispatches' ranks are dropped and each running dispatch is colored by the place it
    holds, so `s-running-1` takes hue 1 where its rank gives 8."""
    root = _project(tmp_path / "proj", {})
    store = Path(root) / ".devpro-temp" / ".profiler-opencode"
    closed = [("2026-01-01T00:00:00.000Z", f"s-closed-{n}") for n in range(DISPATCH_HUES - 1)]
    running = [("2026-01-01T00:01:00.000Z", f"s-running-{n}") for n in range(1, DISPATCH_HUES + 2)]
    last = ("2026-01-01T00:02:00.000Z", running[-1][1])
    _append(store / "s-parent.jsonl", "".join(_dispatch(at, child) for at, child in closed + running[:-1] + [last]))
    for _, child in closed:
        _append(store / f"{child}.jsonl", _idle("2026-01-01T00:00:30.000Z", child))
    client = serve(root)

    hues = {a["id"]: a["hue"] for a in client.board()["agents"]}

    # Ranks are enumerate's, 0-based: the closed dispatches hold 0 to 6, the running ones 7 onward.
    closed_count = len(closed)
    expected = {f"s-running-{n}": (closed_count + n - 1) % DISPATCH_HUES + 1 for n in range(1, DISPATCH_HUES + 2)}
    assert hues == expected and expected[f"s-running-{DISPATCH_HUES + 1}"] == expected["s-running-1"]


def test_an_opencode_card_names_the_model_the_childs_records_carry(tmp_path, serve):
    """`clauses.TEST_PRECONDITION`: the defect (R6) is a card's model read off the opening record —
    the *dispatching session's* model — where the child runs another, the step-down scheme making
    that routinely wrong; the child's own call records name the model it ran.

    `s-closed` runs one call naming `reaper/Qwen3.8-Flash-Next` and idles; `s-child`, dispatched
    after it, runs a call of its own and is still running. `s-closed` is gone from the running set
    once its idle closes it; `s-child`'s card shows `wafer.ai/child-model`, its own call's, never
    `wafer.ai/parent-model`, the dispatching session's the opening record names."""
    root = _project(tmp_path / "proj", {})
    store = Path(root) / ".devpro-temp" / ".profiler-opencode"
    _append(store / "s-parent.jsonl", _dispatch("2026-01-01T00:00:05.000Z", "s-closed"))
    _append(store / "s-closed.jsonl", _call("2026-01-01T00:00:06.000Z", "s-closed", "reaper/Qwen3.8-Flash-Next"))
    _append(store / "s-closed.jsonl", _idle("2026-01-01T00:00:07.000Z", "s-closed"))
    _append(store / "s-parent.jsonl", _dispatch("2026-01-01T00:00:09.000Z", "s-child"))
    _append(store / "s-child.jsonl", _call("2026-01-01T00:00:10.000Z", "s-child", "wafer.ai/child-model"))
    client = serve(root)

    models = {a["id"]: a["model"] for a in client.board()["agents"]}

    assert models == {"s-child": "wafer.ai/child-model"}


def test_a_claude_card_names_no_model_where_no_record_does(tmp_path, serve):
    """`clauses.TEST_PRECONDITION`: the defect (R6) is a card's model read off the opening record,
    whose model under claude is the dispatching session's; a claude child's own records stand in no
    store — claude holds none — so the derivation names none rather than the session's.

    An `Agent` call on `wafer.ai/parent-model` opens the dispatch and no record names the child: the
    card shows no model, and the dispatch still runs (no stop record stands)."""
    root = _project(tmp_path / "proj", {})
    store = Path(root) / ".devpro-temp" / ".profiler-claude"
    call = record("2026-01-01T00:00:05.000Z", tool="Agent", name="devpro-python-coder", session="s-claude") | {
        "child_agent_id": "a-child",
        "model": "wafer.ai/parent-model",
    }
    _append(store / "s-claude.jsonl", json.dumps(call) + "\n")
    client = serve(root)

    assert [(a["id"], a["model"]) for a in client.board()["agents"]] == [("a-child", None)]


def test_an_unreadable_store_keeps_the_last_good_board_and_is_named(tmp_path):
    """`clauses.TEST_PRECONDITION`: the defect is a store that cannot be read blanking the running set
    and the agents column with it, and the store left unnamed on stderr — the operator reading a board
    that says no agent works while the capture holds its records.

    A store the poll cannot list is named on stderr as the live-following rule names an unreadable
    watched file, and the board keeps the last running set and its version until the store reads
    again."""
    if os.geteuid() == 0:
        pytest.skip("root reads any directory")
    root = _project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP})
    store = Path(root) / ".devpro-temp" / ".profiler-opencode"
    _append(store / "s-parent.jsonl", _dispatch("2026-01-01T00:00:05.000Z", "s-child"))
    err = io.StringIO()
    server = DashboardServer(root, stderr=err)
    try:
        server.start()
        before = server.board.payload(None)
        store.chmod(0)
        deadline = time.monotonic() + _TIMEOUT
        while str(store) not in err.getvalue() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert server.board.payload(None)["agents"] == before["agents"]
        store.chmod(0o755)
        _append(store / "s-parent.jsonl", _dispatch("2026-01-01T00:00:07.000Z", "s-next"))
        after = before
        while len(after["agents"]) != 2 and time.monotonic() < deadline:
            after = server.board.payload(str(after["version"]))
    finally:
        store.chmod(0o755)
        server.server_close()

    named = err.getvalue().splitlines()
    assert len(named) == 1 and str(store) in named[0]
    assert len(after["agents"]) == 2


def _dispatch(at: str, child: str) -> str:
    """One opencode dispatch record line: the acknowledgment `execute.after` writes, its `at` the
    dispatch moment and its `child_agent_id` the child's session."""
    row = record(at, tool="Agent", name="devpro-python-coder", session="s-parent") | {
        "harness": "opencode",
        "child_agent_id": child,
        "child_agent_type": "devpro-python-coder",
        "background": True,
    }
    return json.dumps(row) + "\n"


def _idle(at: str, child: str) -> str:
    """One idle record line closing the dispatch of the child session `child`: no background work held."""
    row = record(at, session=child) | {"harness": "opencode", "event": "experimental.idle", "background": 0}
    return json.dumps(row) + "\n"


def _call(at: str, session: str, model: str) -> str:
    """One opencode call record line: a call the child session `session` ran, naming the model it ran."""
    row = record(at, session=session) | {"harness": "opencode", "model": model}
    return json.dumps(row) + "\n"


def _append(path: Path, text: str) -> None:
    """Append text to the file at path, creating its directory: a capture's own write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as trace:
        trace.write(text)


def _texts(root: str) -> dict[str, str]:
    return {name: (Path(root) / name).read_text(encoding="utf-8") for name in ("ROADMAP.md", "ACTIVE_DESIGN.md")}


def test_a_card_moves_into_a_diced_design(tmp_path, serve):
    design = {"ACTIVE_DESIGN/entry-point.md": "# Design\n", "ACTIVE_DESIGN/goals.md": "## Goals\n"}
    root = _project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP, **design})
    client = serve(root)

    status, payload = client.post("api/to-design", {"card": client.board()["board"]["roadmap"][1]})

    assert (status, payload["written"]) == (
        200,
        ["ACTIVE_DESIGN/drafts/search-index.md", "ACTIVE_DESIGN/drafts/index.md", "ACTIVE_DESIGN/entry-point.md"]
        + ["ROADMAP.md"],
    )
    assert [c["path"] for c in payload["board"]["design"] if c["title"] == "Search index"] == [
        "ACTIVE_DESIGN/drafts/search-index.md"
    ]


@pytest.mark.parametrize(
    "path, card",
    [
        pytest.param("api/to-design", {"title": "Gone", "path": "ROADMAP_DESIGNS/gone.md"}, id="to-design"),
        pytest.param(
            "api/to-roadmap",
            {"title": "Gone", "text": "", "path": "ACTIVE_DESIGN.md", "parked": None, "kind": "ticket"},
            id="to-roadmap",
        ),
    ],
)
def test_a_move_of_a_card_not_on_the_board_is_refused(tmp_path, serve, path, card):
    root = _project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP, "ACTIVE_DESIGN.md": _DESIGN})
    client = serve(root)

    status, payload = client.post(path, {"card": card, "target": None})

    assert status == 409 and payload["error"]
    assert _texts(root) == {"ROADMAP.md": _ROADMAP, "ACTIVE_DESIGN.md": _DESIGN}


def _fail_roadmap_writes(monkeypatch) -> None:
    """Make a move's every write of ROADMAP.md fail at the file system."""
    real = board_module.replace_lines

    def fail_on_roadmap(path, lines):
        if os.path.basename(path) == "ROADMAP.md":
            raise OSError("disk full")
        real(path, lines)

    monkeypatch.setattr(board_module, "replace_lines", fail_on_roadmap)


def test_a_failed_write_names_the_file_and_the_files_written(tmp_path, serve, monkeypatch):
    root = _project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP, "ACTIVE_DESIGN.md": _DESIGN})
    client = serve(root)
    _fail_roadmap_writes(monkeypatch)
    status, payload = client.post("api/to-design", {"card": client.board()["board"]["roadmap"][1]})

    assert status == 500
    assert "ROADMAP.md" in payload["error"]
    assert payload["written"] == ["ACTIVE_DESIGN.md"]


def test_a_file_a_move_cannot_read_is_named_from_the_root(tmp_path, serve):
    if os.geteuid() == 0:
        pytest.skip("root reads any file")
    root = _project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP, "ACTIVE_DESIGN.md": _DESIGN})
    client = serve(root)
    card = client.board()["board"]["roadmap"][1]
    roadmap = Path(root) / "ROADMAP.md"
    roadmap.chmod(0)
    try:
        status, payload = client.post("api/to-design", {"card": card})
    finally:
        roadmap.chmod(0o644)

    assert status == 500
    assert "ROADMAP.md" in payload["error"] and root not in payload["error"]
    assert "written" not in payload
    assert _texts(root) == {"ROADMAP.md": _ROADMAP, "ACTIVE_DESIGN.md": _DESIGN}


@pytest.mark.parametrize("write_fails", [False, True], ids=["moved", "write-failed"])
def test_a_failed_read_after_a_move_is_named_and_keeps_the_moves_answer(tmp_path, serve, monkeypatch, write_fails):
    root = _project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP, "ACTIVE_DESIGN.md": _DESIGN})
    err = io.StringIO()
    client = serve(root, stderr=err)
    card = client.board()["board"]["roadmap"][1]
    unreadable = str(Path(root) / "ACTIVE_DESIGN.md")

    def read_fails(_root):
        raise OSError(errno.EACCES, os.strerror(errno.EACCES), unreadable)

    monkeypatch.setattr(server_module, "read_board", read_fails)
    if write_fails:
        _fail_roadmap_writes(monkeypatch)
    status, payload = client.post("api/to-design", {"card": card})

    if write_fails:
        assert (status, payload["written"]) == (500, ["ACTIVE_DESIGN.md"])
    else:
        assert (status, payload["written"]) == (200, ["ACTIVE_DESIGN.md", "ROADMAP.md"])
    assert unreadable in err.getvalue()


def test_a_read_that_fails_once_is_retried_without_a_further_edit(tmp_path, serve, monkeypatch):
    root = _project(tmp_path / "proj", {"ROADMAP.md": _ROADMAP})
    client = serve(root)
    before = client.board()
    calls = []

    def fails_once(path):
        calls.append(path)
        if len(calls) == 1:
            raise OSError(errno.EIO, os.strerror(errno.EIO), str(Path(path) / "ROADMAP.md"))
        return read_board(path)

    monkeypatch.setattr(server_module, "read_board", fails_once)
    (Path(root) / "ROADMAP.md").write_text(_ROADMAP + _TWO, encoding="utf-8")
    after = client.board(since=before["version"])
    while len(after["board"]["roadmap"]) != 3:  # a poll may catch the write half done
        after = client.board(since=after["version"])

    assert len(calls) >= 2
    assert after["board"] == _json_round_trip(asdict(read_board(root)))
    assert len(after["board"]["roadmap"]) == 3


_JSON = "application/json"


@pytest.mark.parametrize(
    "path, content_type, body, length, status",
    [
        pytest.param("api/nothing", _JSON, b"{}", None, 404, id="unknown-endpoint"),
        pytest.param("api/to-design", "text/plain", b"{}", None, 415, id="not-json"),
        pytest.param("api/to-design", _JSON, b"{not json", None, 400, id="unparsable"),
        pytest.param("api/to-design", _JSON, b"[]", None, 400, id="not-an-object"),
        pytest.param("api/to-design", _JSON, b'{"card": "x"}', None, 400, id="card-not-an-object"),
        pytest.param("api/to-roadmap", _JSON, b'{"card": {}, "target": 1}', None, 400, id="target-not-an-object"),
        pytest.param("api/to-design", _JSON, b"", "x", 400, id="length-not-a-number"),
        pytest.param("api/to-design", _JSON, b"", "-1", 400, id="length-negative"),
    ],
)
def test_a_bad_request_is_refused(panel, served_project, path, content_type, body, length, status):
    """The panel's own routes refuse a request they cannot act on, and no refusal writes a file.
    Pinned over the shared served project, whose ROADMAP.md is read back after the request: a
    refusal that wrote there would show here, and would leak into every other test served it."""
    client = panel
    url = urlsplit(client.url)
    headers = {"Host": url.netloc, "Content-Type": content_type, "Content-Length": length or str(len(body))}

    assert client.raw("POST", path, body=body, headers=headers)[0] == status
    assert (Path(served_project) / "ROADMAP.md").read_text(encoding="utf-8") == _ROADMAP


def test_a_cross_origin_preflight_is_not_granted(panel):
    client = panel
    headers = {
        "Host": urlsplit(client.url).netloc,
        "Origin": "http://attacker.example",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }

    _, answer = client.raw("OPTIONS", "api/to-design", headers=headers)

    assert "Access-Control-Allow-Origin" not in answer


def test_a_client_gone_mid_request_leaves_stderr_empty(tmp_path, serve, capsys):
    root = _project(tmp_path / "proj", {"ACTIVE_PLAN.md": _PLAN})
    client = serve(root)
    version = client.board()["version"]
    url = urlsplit(client.url)
    before = set(threading.enumerate())

    with socket.create_connection((url.hostname, url.port), timeout=_TIMEOUT) as gone:
        gone.sendall(f"GET /api/board?since={version} HTTP/1.1\r\nHost: {url.netloc}\r\n\r\n".encode("ascii"))
        gone.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))  # close with a reset
    # wakes the long poll onto the closed socket
    (Path(root) / "ACTIVE_PLAN.md").write_text(_PLAN + "\nMore.\n", encoding="utf-8")
    for thread in set(threading.enumerate()) - before:
        thread.join(_TIMEOUT)
        assert not thread.is_alive()

    assert capsys.readouterr().err == ""


def test_an_error_that_is_not_a_gone_client_gets_the_default_traceback(tmp_path, capsys):
    """`clauses.TEST_PRECONDITION`: the defect is a non-`ConnectionError` reaching
    `DashboardServer.handle_error`, whose one-line delegation to the board panel's `handle_error`
    falls through to `BaseHTTPRequestHandler.handle_error` — no handler class carries it — and raises
    `AttributeError` at the call instead of the default traceback. The run that fails under it is this
    one: over a scratch root the board reads, a `ValueError` raised and made the current exception,
    then `handle_error` called on it — before the change the delegation raises `AttributeError` where
    the traceback should go; after, the base server's default writes the `ValueError`'s traceback to
    stderr and nothing raises."""
    root = _project(tmp_path / "proj", {"ACTIVE_PLAN.md": _PLAN})
    server = DashboardServer(root, stderr=io.StringIO())
    try:
        with pytest.raises(ValueError):
            try:
                raise ValueError("boom")
            except ValueError:
                server.handle_error(None, None)
                raise
    finally:
        server.server_close()
    assert "boom" in capsys.readouterr().err


def _serve_the_command(
    root: str, end: Callable[["subprocess.Popen[bytes]", _Client], None]
) -> tuple[int, bytes, bytes]:
    """Run `python -m devpro dashboard root`, fetch the board page from the URL it prints, end it with
    end, and give its status and what it wrote after the URL line. The child is given the package's
    place on `PYTHONPATH` from the running interpreter, so a test that leaves the working directory
    elsewhere still starts this checkout's devpro."""
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            [str(Path(sys.modules["devpro"].__file__).resolve().parents[1])]
            + ([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else [])
        ),
    }
    child = subprocess.Popen(
        [sys.executable, "-m", "devpro", "dashboard", root],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        ready, _, _ = select.select([child.stdout], [], [], _TIMEOUT)
        assert ready, "no URL printed"
        url = child.stdout.readline().decode("utf-8").strip()
        client = _Client(url)
        assert url.startswith("http://127.0.0.1:") and url.endswith("/")
        assert client.get("board/")[0] == 200
        end(child, client)
        out, err = child.communicate(timeout=_TIMEOUT)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
    return child.returncode, out, err


def test_the_command_prints_the_url_and_serves_until_interrupted(tmp_path):
    root = _project(tmp_path / "proj", {"ACTIVE_PLAN.md": _PLAN})
    assert _serve_the_command(root, lambda child, _: child.send_signal(signal.SIGINT)) == (0, b"", b"")


def test_the_command_serves_until_stopped_from_the_page(tmp_path):
    root = _project(tmp_path / "proj", {"ACTIVE_PLAN.md": _PLAN})
    answers = []
    assert _serve_the_command(root, lambda _, client: answers.append(client.post("api/stop", {}))) == (0, b"", b"")
    assert answers == [(200, {})]
