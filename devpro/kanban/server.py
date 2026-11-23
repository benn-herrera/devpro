"""The kanban server: the board of one project, kept live by polling the files it reads, with the moves
between Roadmap and Design. It keeps no UI state, and it binds no socket: the dashboard serves it as
its board panel, and answers the routes below onto the dashboard's connection.

Endpoints, each answering JSON but the page's files and the served documents:

- `GET /` and `GET /<file>`: the page's files, from the package's `assets/` directory.
- `GET /<path>.md`: a file `board.served_files` names — its docstring gives the set — as
  `text/markdown`, read-only; any other path is 404.
- `GET /api/board?since=<version>`: the board payload — `version`, the board as `board`'s model reads
  it, the `plan_columns` its page draws, the `project`'s name, and `devpro_version`, the version its
  connection indicator names; where `since` is the version the server
  holds, the answer waits until the board changes or `LONG_POLL_SECONDS` pass.
- `POST /api/stop` `{}`: answers `{}`, then stops the server serving the panel.
- `POST /api/to-design` `{"card": <a roadmap or parked card as served>}`: move the card's ticket into
  the active design (for a parked card, the link ticket written for it).
- `POST /api/to-roadmap` `{"card": <a design card as served>, "target": <the Roadmap separator
  nearest above the drop, as served, or null>}`: move the card's ticket out of the design into
  `ROADMAP.md`.

  Both answer the board payload with `written`, the files written relative to the project root in
  the order written; 409 with `{"error": ...}` where refused, writing nothing; 500 with `{"error":
  "cannot write: <file>", "written": [...]}` where a write fails, and with `{"error": "cannot read:
  <file>"}` where a file the move reads cannot be read.
"""

import json
import os
import threading
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler
from importlib.resources import files
from typing import Any, Callable, Optional, TextIO
from urllib.parse import parse_qs, unquote, urlsplit

from .. import __version__
from ..dicing.dicerlib.textfile import read_text
from .board import (
    PLAN_COLUMNS,
    MoveRefused,
    MoveWriteFailed,
    move_to_design,
    move_to_roadmap,
    read_board,
    root_relative,
    served_files,
    sha256,
    watched_files,
)

HOST = "127.0.0.1"
POLL_SECONDS = 0.25
LONG_POLL_SECONDS = 25.0
_CONTENT_TYPES = {".html": "text/html", ".js": "text/javascript", ".css": "text/css"}
_UNREADABLE = "unreadable"


def _snapshot(root: str) -> dict[str, Optional[str]]:
    """Each watched file's content digest; None where it is not a file, `_UNREADABLE` where it is
    one that cannot be read."""
    snapshot: dict[str, Optional[str]] = {}
    for path in watched_files(root):
        if not os.path.isfile(path):
            snapshot[path] = None
            continue
        try:
            snapshot[path] = sha256(read_text(path))
        except OSError:
            snapshot[path] = _UNREADABLE
    return snapshot


class BadRequest(Exception):
    """A request the server cannot act on; the message says why."""


def _unreadable(e: OSError, reading: str) -> str:
    """The file an OSError names, else reading, the path being read."""
    return e.filename if e.filename is not None else reading


class KanbanServer:
    """The board of the project at root, as the dashboard's board panel. Reads the board on
    construction, raising OSError where a file it reads cannot be read; `start` begins polling the
    files every POLL_SECONDS, until server_close.

    The panel binds no socket of its own: its answers are written onto the dashboard's. The dashboard
    takes a handler over the request it has read, `panel_handler`, and answers with the panel's routes
    the paths its page calls. Its own `POST /api/stop` stops the dashboard serving it."""

    def __init__(self, root: str, *, stderr: TextIO, after: Any) -> None:
        """after is the dashboard server the panel answers onto, whose address it reports, which its
        `POST /api/stop` asks to stop, which this panel's handler sends its replies through, and whose
        guard stands before either panel's routes."""
        self.root = root
        self._stderr = stderr
        self._lock = threading.Condition()
        self._stop = threading.Event()
        self._poller = threading.Thread(target=self._poll, name="kanban-poll", daemon=True)
        self._snapshot = _snapshot(root)
        self._board = read_board(root)
        self._version = 1
        self._reported: Optional[str] = None  # the unreadable file last named on stderr
        self.dashboard = after
        _Handler._local_host = type(after).handler._local_host
        _Handler._send = type(after).handler._send

    def panel_handler(self, request: Any, client_address: Any) -> BaseHTTPRequestHandler:
        """A handler over a request the dashboard has read, the board's own `do_` answering it."""
        return _Handler(request, client_address, self, read_request=False)

    def start(self) -> None:
        """Begin polling the watched files. Called once the server is serving, inside the try whose
        finally closes it, so a construction that fails half-way owns no running thread."""
        self._poller.start()

    @property
    def url(self) -> str:
        """The board's URL at the dashboard serving it."""
        return f"http://{HOST}:{self.dashboard.server_address[1]}/"

    def shutdown(self) -> None:
        """Stop the server this board's answers are written by: the dashboard's."""
        self.dashboard.shutdown()

    def server_close(self) -> None:
        """End the polling. A panel binds no socket and runs no loop of its own: there is nothing
        here to close."""
        self._stop.set()
        if self._poller.is_alive():
            self._poller.join()
        with self._lock:
            self._lock.notify_all()

    def payload(self, since: Optional[str]) -> dict[str, Any]:
        """The board payload, once its version differs from since; at most LONG_POLL_SECONDS late."""
        with self._lock:
            if since is not None:
                self._lock.wait_for(lambda: str(self._version) != since or self._stop.is_set(), LONG_POLL_SECONDS)
            return self._payload()

    def to_design(self, body: dict[str, Any]) -> dict[str, Any]:
        card = _field(body, "card", dict)
        with self._lock:
            return self._moved(lambda: move_to_design(self.root, card, read=self._board.sha256))

    def to_roadmap(self, body: dict[str, Any]) -> dict[str, Any]:
        card = _field(body, "card", dict)
        target = body.get("target")
        if target is not None and not isinstance(target, dict):
            raise BadRequest("target must be a dict or null")
        with self._lock:
            return self._moved(lambda: move_to_roadmap(self.root, card, target=target, read=self._board.sha256))

    def _moved(self, move: Callable[[], list[str]]) -> dict[str, Any]:
        """Make move, then read the board again; the payload with the files written. A write that
        fails still reads the board again, as the files written have changed. A read that fails
        in either case is named on stderr and leaves the move's result as it is."""
        try:
            written = move()
        except MoveWriteFailed:
            self._refresh_or_report()
            raise
        self._refresh_or_report()
        return {**self._payload(), "written": written}

    def _payload(self) -> dict[str, Any]:
        return {
            "version": self._version,
            "board": asdict(self._board),
            "plan_columns": list(PLAN_COLUMNS),
            "project": os.path.basename(self.root),
            "devpro_version": __version__,
        }

    def _poll(self) -> None:
        while not self._stop.wait(POLL_SECONDS):
            with self._lock:
                self._refresh_or_report()

    def _refresh_or_report(self) -> None:
        try:
            self._refresh()
        except OSError as e:
            self._report(_unreadable(e, self.root))

    def _refresh(self) -> None:
        """Read the board again where a watched file changed. Raises OSError where a file cannot
        be read, keeping the last good board and the last snapshot, so the next refresh reads again."""
        snapshot = _snapshot(self.root)
        if snapshot == self._snapshot:
            return
        self._board = read_board(self.root)
        self._snapshot = snapshot
        self._reported = None
        self._version += 1
        self._lock.notify_all()

    def _report(self, path: str) -> None:
        if path != self._reported:
            print(f"cannot read: {path}", file=self._stderr, flush=True)
            self._reported = path


def _field(body: dict[str, Any], name: str, kind: type) -> Any:
    value = body.get(name)
    if not isinstance(value, kind):
        raise BadRequest(f"{name} must be a {kind.__name__}")
    return value


def _asset(name: str) -> Optional[tuple[bytes, str]]:
    """The page file name, as served, and its content type; None where the page has no such file."""
    content_type = _CONTENT_TYPES.get(os.path.splitext(name)[1])
    if content_type is None:
        return None
    for entry in (files(__package__) / "assets").iterdir():
        if entry.name == name and entry.is_file():
            return entry.read_text(encoding="utf-8").encode("utf-8"), f"{content_type}; charset=utf-8"
    return None


def _document(root: str, url_path: str) -> Optional[tuple[bytes, str]]:
    """The served file url_path, percent-decoded (a byte that is not UTF-8 decoded as a name holds
    it), names, and its content type; None where it names none or that file cannot be read. The file
    read is the one `served_files` names, an absolute path this function never derives from
    url_path."""
    try:
        wanted = unquote(url_path[1:], errors="surrogateescape")
        path = next((p for p in served_files(root) if root_relative(root, p) == wanted), None)
        if path is None:
            return None
        text = read_text(path)
    except OSError:
        return None
    return text.encode("utf-8", "surrogateescape"), "text/markdown; charset=utf-8"


class _Handler(BaseHTTPRequestHandler):
    server: KanbanServer
    # The dashboard's guard and reply write one answer per request, its own ask answering every route
    # of either panel before either panel's handler runs; the dashboard imports this module, so it
    # binds these here once it is loaded (`KanbanServer`'s `__init__`).
    _local_host: Callable[[Any], bool]
    _send: Callable[..., None]

    def __init__(self, *args: Any, read_request: bool = True, **kwargs: Any) -> None:
        """A handler over a request the dashboard has already read when read_request is false: its
        `do_` answers onto that server's connection, and this one reads no request line again."""
        self._read_request = read_request
        super().__init__(*args, **kwargs)

    def handle_one_request(self) -> None:
        if not self._read_request:
            self.close_connection = True
            return
        super().handle_one_request()

    _ACTIONS = {
        "/api/to-design": KanbanServer.to_design,
        "/api/to-roadmap": KanbanServer.to_roadmap,
    }
    _STOP = "/api/stop"

    def log_message(self, format: str, *args: Any) -> None:
        """Nothing is written per request."""

    def do_GET(self) -> None:
        if not self._local_host():
            return
        url = urlsplit(self.path)
        if url.path == "/api/board":
            since = parse_qs(url.query).get("since")
            self._send_json(200, self.server.payload(since[0] if since else None))
            return
        asset = _asset("index.html" if url.path == "/" else url.path[1:]) or _document(self.server.root, url.path)
        if asset is None:
            self._send_json(404, {"error": f"no such file: {url.path}"}, page=True)
            return
        self._send(200, *asset, page=True)

    def do_POST(self) -> None:
        if not self._local_host():
            return
        path = urlsplit(self.path).path
        action = self._ACTIONS.get(path)
        if action is None and path != self._STOP:
            self._send_json(404, {"error": f"no such endpoint: {self.path}"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "the body must be application/json"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length < 0:
                raise BadRequest("Content-Length must not be negative")
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise BadRequest("the body must be a JSON object")
            if action is None:
                # Answered before stopping, as a move's answer cannot be: the dashboard's shutdown
                # returns once its serve_forever has ended.
                self._send_json(200, {})
                self.server.shutdown()
                return
            self._send_json(200, action(self.server, body))
        except (ValueError, BadRequest) as e:
            self._send_json(400, {"error": str(e)})
        except MoveRefused as e:
            self._send_json(409, {"error": str(e)})
        except MoveWriteFailed as e:
            self._send_json(500, {"error": str(e), "written": e.written})
        except OSError as e:
            root = self.server.root
            self._send_json(500, {"error": f"cannot read: {root_relative(root, _unreadable(e, root))}"})

    def _send_json(self, status: int, payload: dict[str, Any], *, page: bool = False) -> None:
        self._send(status, json.dumps(payload).encode("ascii"), "application/json", page=page)
