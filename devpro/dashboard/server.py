"""The dashboard: the project's board and the profiler's records, one server on 127.0.0.1.

Neither panel's rendering is this module's. The board panel is `devpro.dicing.kanban.server`'s serve
surface — its page, files, payload, moves and served documents, answered by the `KanbanServer` built
over the dashboard's root — and the traces panel is `devpro.profiler.pages`' index and pages, read from
the stores as they stand. This module adds the routes that hold them apart and the one link line the
root carries.

Endpoints:

- `GET /`: the traces index (`pages.index_html`) with the board's link line before its `</html>`.
- `GET /page/<session-id>`: that session's page, the bytes `tree --format html` produces.
- `GET /board/` and `GET /board/<file>`: the board page and its files, the file resolved beside the
  page, so the page's relative asset names reach them.
- `GET /<path>.md`: a served document, as the board panel serves it.
- `GET /api/board`, `POST /api/to-design`, `POST /api/to-roadmap`, `POST /api/stop`: the board's
  payload, moves and stop, at the root paths its page calls.
"""

from __future__ import annotations

import os
import re
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional, TextIO
from urllib.parse import unquote, urlsplit

from devpro.profiler.pages import PAGE_PREFIX, index_html, page_of
from devpro.profiler.values import git_root

from ..dicing.kanban.server import HOST, CannotListen, KanbanServer

BOARD_PATH = "/board/"
BOARD_LINK = '<p><a href="/board/">Board</a> — the project\'s kanban board</p>'
# The one policy both panels' pages are served under, so a page cannot load from elsewhere and no
# page frames either.
CONTENT_SECURITY_POLICY = "default-src 'self'; frame-ancestors 'none'"
_REFUSED_HOST = '{"error": "requests must name the host the dashboard is served on"}'
_NO_SUCH_PAGE = "No such page"


def with_board_link(index: str) -> str:
    """The traces index with the board's link line immediately before the template's closing `</html>`."""
    head, closing, tail = index.rpartition("</html>")
    return f"{head}\n{BOARD_LINK}{closing}{tail}"


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

    `root` is explicit: the project whose `.profiler-*` stores and git root the traces panel reads,
    and whose files the board panel reads. The command takes it from the directory it names, or
    where it names none, from the directory it runs in; a test names it. The board panel is a
    `KanbanServer` over the same root, which reads the board on construction and raises OSError where a
    file it reads cannot be read; the port refuses with CannotListen. `start` begins the board's
    polling of its files, until server_close ends it and closes the socket."""

    daemon_threads = True

    def __init__(self, root: str, *, stderr: TextIO, port: int = 0) -> None:
        self.root = root
        self._closed = threading.Event()
        self._board_closed = threading.Event()
        try:
            super().__init__((HOST, port), _Handler)
        except OSError as e:
            raise CannotListen(e.strerror or str(e)) from e
        self.board = KanbanServer(root, stderr=stderr, after=self)

    @property
    def url(self) -> str:
        return f"http://{HOST}:{self.server_address[1]}/"

    @property
    def port(self) -> int:
        return self.server_address[1]

    def traces_index(self) -> str:
        """The index of the stores under the root, with the board's link line.

        Read per request: a session recorded a moment ago is listed by the next page loaded.
        `CLAUDE_PROJECT_DIR` is not followed — it names the outermost claude session's launch
        directory, which for a terminal-launched server is another project."""
        return with_board_link(index_html(self.root))

    def page(self, session: str) -> str | None:
        """The page at `/page/<session>`, or nothing where it names no recorded session."""
        return page_of(PAGE_PREFIX + session, self.root)

    def start(self) -> None:
        """Begin polling the board's files. Called once the server is serving, inside the try whose
        finally closes it, so a construction that fails half-way owns no running thread."""
        self.board.start()

    def stop(self) -> None:
        """Stop serving, as the board panel's `POST /api/stop` does: asked from the request's own
        thread, which `shutdown` cannot serve, so the stop waits for that answer first. The panel ends
        its polling once, here; the close that follows does not end it again."""
        self.board.server_close()
        self._board_closed.set()
        threading.Thread(target=super().shutdown, daemon=True).start()

    def handle_error(self, request: Any, client_address: Any) -> None:
        self.board.handle_error(request, client_address)

    def server_close(self) -> None:
        """Close the board panel and the socket, once each: a bind that failed half-way closes a
        server whose panel was never composed."""
        if self._closed.is_set():
            return
        self._closed.set()
        if hasattr(self, "board") and not self._board_closed.is_set():
            self._board_closed.set()
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
            self._send(HTTPStatus.OK, self.server.traces_index().encode("utf-8"), "text/html; charset=utf-8", page=True)
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
        """Refuse a request naming another host, as the board panel refuses one (DNS rebinding)."""
        port = self.server.port
        if self.headers.get("Host") in (f"{HOST}:{port}", f"localhost:{port}"):
            return True
        self._send(HTTPStatus.FORBIDDEN, _REFUSED_HOST.encode("ascii"), "application/json")
        return False

    def _send(self, status: int, body: bytes, content_type: str, *, page: bool = False) -> None:
        """Send one response; page marks an answer to a request for a page of the dashboard's own."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if page:
            self.send_header("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        self.end_headers()
        self.wfile.write(body)


def serve(directory: Optional[str], port: int) -> None:
    """Serve the dashboard of the project directory is in, or with None the project the current
    directory is in, until interrupted or stopped, the URL printed once on stdout."""
    server = DashboardServer(dashboard_root(directory), stderr=sys.stderr, port=port)
    try:
        print(server.url, flush=True)
        server.start()
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
