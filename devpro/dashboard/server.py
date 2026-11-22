"""The dashboard: the project's board and the profiler's records, one server on 127.0.0.1.

Neither panel's rendering is this module's. The board panel is `devpro.dicing.kanban.server`'s serve
surface — its page, files, payload, moves and served documents, answered by the `KanbanServer` built
over the dashboard's root — and the profiler view is `devpro.profiler.pages`' index and pages, read
from the stores as they stand. This module adds the routes that hold them apart and the state
endpoint every view's deco reads; the view's deco — the top nav and the frame band — is the
templates' own text, this module adding only the band's per-page facts, the way back and the
dispatcher its lookup names.

Endpoints:

- `GET /`: a `302` to `/board/`'s absolute URL. The board is the landing surface, and it serves from
  `/board/` so its page's assets, its payload and its served documents stay under that path; the
  redirect is the one answer the root owes.
- `GET /profiler/`: the profiler view's static index — `pages.index_html` — with the nav and the band,
  the shared layer linked at `/board/board.css` and the decoration's script linked at
  `/profiler/deco.js`; its rows are rendered client-side from the feed below.
- `GET /api/traces`: the index's feed — `pages.traces_feed` — one JSON entry per recorded session and
  one per store that could not be read, the rows' one schema.
- `GET /page/<session-id>`: that session's page, with the nav, the band's legend and its return to the
  list, and the dispatcher its lookup names where one dispatched it.
- `GET /board/` and `GET /board/<file>`: the board page and its files, the file resolved beside the
  page, so the page's relative asset names reach them.
- `GET /<path>.md`: a served document, as the board panel serves it.
- `GET /api/state`: `{"state": "live"}`, answered while the server serves, which is the answer the
  shared deco's indicator reads.
- `GET /api/board`, `POST /api/to-design`, `POST /api/to-roadmap`, `POST /api/stop`: the board's
  payload, moves and stop, at the root paths its page and the deco call.
"""

from __future__ import annotations

import json
import os
import re
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from typing import Any, Optional, TextIO
from urllib.parse import unquote, urlsplit

from devpro import __version__
from devpro.profiler import pages
from devpro.profiler.pages import PAGE_PREFIX, dispatches, read_sessions
from devpro.profiler.values import git_root

from ..dicing.kanban.server import HOST, KanbanServer
from ..errors import InputError

BOARD_PATH = "/board/"
PROFILER_PATH = "/profiler/"
STATE_PATH = "/api/state"
TRACES_PATH = "/api/traces"
# The decoration's script: its one source is the shipped file, which the server answers at the
# profiler path the pages name (`/profiler/deco.js`, a link the templates carry) — the board page's
# script names it too. The one policy both panels' pages are served under, so a page cannot load from
# elsewhere and no page frames either.
DECO_SCRIPT = (files("devpro.profiler") / "deco.js").read_text(encoding="utf-8")
# The profiler path's name for that script: one file, served from the one path.
DECO_SCRIPT_PATH = "deco.js"
# The templates' own style and script blocks are inline, and the served pages carry them: the
# pages are first-party, and the render escapes every record field at source (`html.escape`, quoted
# ids, the payload's `<` script-escaped), so 'unsafe-inline' admits them while 'self' keeps
# everything else same-origin.
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'"
)
_REFUSED_HOST = '{"error": "requests must name the host the dashboard is served on"}'
_NO_SUCH_PAGE = "No such page"


def dispatcher_of(session: str, root: str) -> tuple[str, str] | None:
    """The session that dispatched `session`, and the call that did, for the band it heads.

    The page's render holds this session's records alone, so a dispatcher named among them is found
    in the stores' other sessions: the band's one fact costs a read beside the page's own."""
    sessions, _ = read_sessions(root)
    return dispatches([other for other in sessions if other["id"] != session]).get(session)


def profiler_page(session: dict, *, return_to: str | None, dispatcher: tuple[str, str] | None) -> str:
    """A page of the profiler view as the dashboard serves it: the view's own text — the nav, the
    frame band, the decoration's script, the shared layer linked — assembled by `pages`, this module
    adding the band's per-page facts, the way back and the dispatcher its lookup names."""
    return pages.profiler_page(session, return_to=return_to, dispatcher=dispatcher)


def loopback(url: str) -> bool:
    """Whether url is the URL the dashboard prints: `http://127.0.0.1:<port>/`."""
    return re.fullmatch(r"http://127\.0\.0\.1:\d+/", url) is not None


def dashboard_root(directory: Optional[str] = None) -> str:
    """The project the dashboard serves: the directory the command names, or where it names none,
    the directory the command runs in, either up to the nearest directory at or above it holding a
    `.git` entry, which is itself where there is none."""
    start = os.getcwd() if directory is None else os.path.abspath(directory)
    return str(git_root(start) or start)


class DashboardServer(ThreadingHTTPServer):
    """The dashboard serving the project at root — its stores and its board — on HOST at port, 0
    being an ephemeral one.

    `root` is explicit: the project whose `.profiler-*` stores and git root the profiler view reads,
    and whose files the board panel reads. The command takes it from the directory it names, or
    where it names none, from the directory it runs in; a test names it. The board panel is a
    `KanbanServer` over the same root, which reads the board on construction, so a board file that
    cannot be read refuses the server as InputError naming the file — `error: cannot read: <file>`.
    `start` begins the board's polling of its files, until server_close ends it and closes the
    socket."""

    daemon_threads = True

    def __init__(self, root: str, *, stderr: TextIO, port: int = 0) -> None:
        self.root = root
        self._closed = threading.Event()
        try:
            super().__init__((HOST, port), _Handler)
        except OSError as e:
            raise InputError(f"cannot listen: {e.strerror or e}") from e
        try:
            self.board = KanbanServer(root, stderr=stderr, after=self)
        except OSError as e:
            self.server_close()
            raise InputError(f"cannot read: {e.filename if e.filename is not None else root}") from e

    # The one guard and the one reply write each answer a request gets, the board panel's answers
    # included: its `_Handler` takes both from here, once this module is loaded (`KanbanServer`'s
    # `__init__`).
    handler = None

    @property
    def url(self) -> str:
        return f"http://{HOST}:{self.server_address[1]}/"

    @property
    def port(self) -> int:
        return self.server_address[1]

    def profiler_index(self) -> str:
        """The profiler view's static index, as the dashboard serves it: the page's own text under
        the nav and the band, the legend once — its rows rendered by its script from `traces`.

        `CLAUDE_PROJECT_DIR` is not followed — it names the outermost claude session's launch
        directory, which for a terminal-launched server is another project."""
        return pages.served_page(pages.index_html())

    def traces(self) -> bytes:
        """The index's feed as the JSON answer `/api/traces` serves: `pages.traces_feed`'s entries,
        read per request so a session recorded a moment ago is in the next answer."""
        return json.dumps(pages.traces_feed(self.root)).encode("utf-8")

    def page(self, session: str) -> str | None:
        """The page at `/page/<session>`, or nothing where it names no recorded session: the view's
        own text — the nav, the band, the shared layer linked — with the band's per-page facts, whose
        return control leads back to the list and whose heading names the session that dispatched it,
        where one did.

        The store read is the page's own; the dispatcher its band names is looked up beside it, once.
        The page of the session that named this one is a second render, never a second index."""
        session_record = pages.session_for(PAGE_PREFIX + session, self.root)
        if session_record is None:
            return None
        return profiler_page(session_record, return_to=PROFILER_PATH, dispatcher=dispatcher_of(session, self.root))

    def start(self) -> None:
        """Begin polling the board's files. Called once the server is serving, inside the try whose
        finally closes it, so a construction that fails half-way owns no running thread."""
        self.board.start()

    def handle_error(self, request: Any, client_address: Any) -> None:
        """A client gone mid-request (a page reloaded during a long poll) is not an error; anything
        else gets the default traceback."""
        if not isinstance(sys.exc_info()[1], ConnectionError):
            super().handle_error(request, client_address)

    def server_close(self) -> None:
        """Close the board panel and the socket, once each: a bind that failed half-way closes a
        server whose panel was never composed."""
        if self._closed.is_set():
            return
        self._closed.set()
        if hasattr(self, "board"):
            self.board.server_close()
        super().server_close()


class _Handler(BaseHTTPRequestHandler):
    server: DashboardServer

    def log_message(self, format: str, *args: Any) -> None:
        """Nothing is written per request."""

    def do_GET(self) -> None:
        if not self._local_host():
            return
        url = urlsplit(self.path)
        path = unquote(url.path)
        if path in ("", "/"):
            self._redirect(f"http://{HOST}:{self.server.port}{BOARD_PATH}")
        elif path == STATE_PATH:
            self._send(
                HTTPStatus.OK,
                json.dumps({"state": "live", "version": __version__}).encode("utf-8"),
                "application/json",
            )
        elif path == PROFILER_PATH:
            self._send(
                HTTPStatus.OK, self.server.profiler_index().encode("utf-8"), "text/html; charset=utf-8", page=True
            )
        elif path == TRACES_PATH:
            self._send(HTTPStatus.OK, self.server.traces(), "application/json", page=True)
        elif path == PROFILER_PATH + DECO_SCRIPT_PATH:
            self._send(HTTPStatus.OK, DECO_SCRIPT.encode("utf-8"), "text/javascript")
        elif path.startswith(BOARD_PATH):
            self._board(self.path[len(BOARD_PATH) - 1 :])
        elif path.startswith(PAGE_PREFIX):
            page = self.server.page(path[len(PAGE_PREFIX) :])
            if page is None:
                self.send_error(HTTPStatus.NOT_FOUND, _NO_SUCH_PAGE)
            else:
                self._send(HTTPStatus.OK, page.encode("utf-8"), "text/html; charset=utf-8", page=True)
        else:
            self._board(self.path)

    def do_POST(self) -> None:
        if self._local_host():
            self._board(urlsplit(self.path).path, method="POST")

    def _board(self, path: str, *, method: str = "GET") -> None:
        """Answer a request the board panel owns, with the panel's own handler over this request and
        onto this connection: the board's host guard and its Content-Security-Policy travel with it,
        and its routes are reached at the paths its page calls — `/board/` hands the page's assets
        over as their bare names, which resolve beside the page. path is the request's own path with
        the board prefix taken off, its query kept where it has one: the payload's `since` is the
        query, and a panel handed the path alone answers every long poll at once."""
        handler = self.server.board.panel_handler(self.request, self.client_address)
        handler.path = path
        handler.command = self.command
        handler.headers = self.headers
        handler.rfile = self.rfile
        handler.requestline = self.requestline
        handler.request_version = self.request_version
        handler.wfile = self.wfile
        (handler.do_POST if method == "POST" else handler.do_GET)()

    def _local_host(self) -> bool:
        """Refuse a request naming a host or port other than the dashboard's own (DNS rebinding)."""
        port = getattr(self.server, "dashboard", self.server).port
        if self.headers.get("Host") in (f"{HOST}:{port}", f"localhost:{port}"):
            return True
        self._send(HTTPStatus.FORBIDDEN, _REFUSED_HOST.encode("ascii"), "application/json")
        return False

    def _send(self, status: int, body: bytes, content_type: str, *, page: bool = False) -> None:
        """Send one response; page marks an answer a browser could load as a page, the dashboard's
        own and the board panel's, which carry the policy, framed or loaded from elsewhere."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if page:
            self.send_header("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        """Answer with a redirect to location, under the policy a page is served under: it is an
        answer a browser follows into a page, so it carries the page's headers as the pages do."""
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        self.end_headers()


# The board panel's handler takes its guard and its reply from here (`KanbanServer`'s `__init__`).
DashboardServer.handler = _Handler


def serve(directory: Optional[str], port: int) -> None:
    """Serve the dashboard of the project directory is in, or with None the project the current
    directory is in, until interrupted or stopped, the URL printed once on stdout. A port that
    cannot be bound and a board file that cannot be read refuse as InputError, before the URL."""
    server = DashboardServer(dashboard_root(directory), stderr=sys.stderr, port=port)
    try:
        print(server.url, flush=True)
        server.start()
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
