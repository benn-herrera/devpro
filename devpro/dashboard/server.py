"""The dashboard: the project's board and the profiler's records, one server on 127.0.0.1.

Neither panel's rendering is this module's. The board panel is `devpro.dicing.kanban.server`'s serve
surface — its page, files, payload, moves and served documents, answered by the `KanbanServer` built
over the dashboard's root — and the profiler view is `devpro.profiler.pages`' index and pages, read
from the stores as they stand. This module adds the routes that hold them apart, the chrome the
profiler view's pages are served with — the top nav and the frame band — and the state endpoint
every view's chrome reads.

Endpoints:

- `GET /`: a `302` to `/board/`'s absolute URL. The board is the landing surface, and it serves from
  `/board/` so its page's assets, its payload and its served documents stay under that path; the
  redirect is the one answer the root owes.
- `GET /profiler/`: the profiler view's index — `pages.index_html` — with the nav and the band.
- `GET /page/<session-id>`: that session's page, the render's, with the nav, the band's legend and its
  return to the list.
- `GET /board/` and `GET /board/<file>`: the board page and its files, the file resolved beside the
  page, so the page's relative asset names reach them.
- `GET /<path>.md`: a served document, as the board panel serves it.
- `GET /api/state`: `{"state": "live"}`, answered while the server serves, which is the answer the
  shared chrome's indicator reads.
- `GET /api/board`, `POST /api/to-design`, `POST /api/to-roadmap`, `POST /api/stop`: the board's
  payload, moves and stop, at the root paths its page and the chrome call.
"""

from __future__ import annotations

import os
import re
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from typing import Any, Optional, TextIO
from urllib.parse import unquote, urlsplit

from devpro.profiler.pages import (
    LEGEND,
    PAGE_PREFIX,
    index_html,
    page_of,
    with_frame,
)
from devpro.profiler.values import git_root

from ..dicing.kanban.server import HOST, KanbanServer
from ..errors import InputError

BOARD_PATH = "/board/"
PROFILER_PATH = "/profiler/"
STATE_PATH = "/api/state"
RETURN_LABEL = "Return to list"
# The chrome every view carries after its view names: the live/idle indicator and the stop, and the
# script that gives them their behavior. That script ships as `devpro/profiler/chrome.js` and is
# inlined where it goes — the board page's script names it instead — because the server answers no
# static file of its own, and a page's script loads under the policy every page is served with. The
# markup is one text both carriers substitute, so an id or a class cannot drift between the views.
CHROME = """<span class="nav-server">
  <span id="connection" role="status" aria-labelledby="connection"></span>
  <button id="stop" class="nav-stop" type="button">Stop</button>
</span>"""
CHROME_SCRIPT = (files("devpro.profiler") / "chrome.js").read_text(encoding="utf-8")
CHROME_MARK = "<!--CHROME-->"
# The one policy both panels' pages are served under, so a page cannot load from elsewhere and no
# page frames either.
CONTENT_SECURITY_POLICY = "default-src 'self'; frame-ancestors 'none'"
_REFUSED_HOST = '{"error": "requests must name the host the dashboard is served on"}'
_NO_SUCH_PAGE = "No such page"


def nav_html(active: str) -> str:
    """The top nav, with active — `kanban` or `profiler` — the view the page shows. The view names
    link the routes; the chrome after them, the live/idle indicator and the stop, is on both views."""
    views = "".join(
        f'<a class="view{" active" if view == active else ""}" href="{href}"'
        + (' aria-current="page"' if view == active else "")
        + f">{view}</a>"
        for view, href in (("kanban", BOARD_PATH), ("profiler", PROFILER_PATH))
    )
    return f'<nav class="site-nav scanlines"><span class="brand">devpro</span><span class="views">{views}</span>{CHROME}</nav>'


def chrome_script() -> str:
    """The nav's one script, as the page inlines it: the server answers no static file of its own, so
    the board page's script names its own asset and a page served in memory carries the text."""
    return f"<script>{CHROME_SCRIPT}</script>"


def band_html(return_to: str | None) -> str:
    """The profiler view's frame band: the how-to-read legend at its top, and, on a session's page,
    the control back to the list."""
    back = f'<a class="return" href="{return_to}">{RETURN_LABEL}</a>' if return_to else ""
    return f'<div class="frame-band scanlines">{LEGEND}{back}</div>'


def profiler_page(page: str, *, return_to: str | None) -> str:
    """A page of the profiler view as the dashboard serves it: the nav, the band and the view's own
    content, one legend on the page, and the nav's script once."""
    return with_frame(page, nav=nav_html("profiler"), band=band_html(return_to), script=chrome_script())


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
        """The profiler view's index, as the dashboard serves it: the store rows under the nav and the
        band, the legend once.

        Read per request: a session recorded a moment ago is listed by the next page loaded.
        `CLAUDE_PROJECT_DIR` is not followed — it names the outermost claude session's launch
        directory, which for a terminal-launched server is another project."""
        return profiler_page(index_html(self.root), return_to=None)

    def page(self, session: str) -> str | None:
        """The page at `/page/<session>`, or nothing where it names no recorded session: the render's
        page under the nav and the band, whose return control leads back to the list."""
        page = page_of(PAGE_PREFIX + session, self.root)
        return None if page is None else profiler_page(page, return_to=PROFILER_PATH)

    def start(self) -> None:
        """Begin polling the board's files. Called once the server is serving, inside the try whose
        finally closes it, so a construction that fails half-way owns no running thread."""
        self.board.start()

    def handle_error(self, request: Any, client_address: Any) -> None:
        self.board.handle_error(request, client_address)

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
            self._send(HTTPStatus.OK, b'{"state": "live"}', "application/json")
        elif path == PROFILER_PATH:
            self._send(
                HTTPStatus.OK, self.server.profiler_index().encode("utf-8"), "text/html; charset=utf-8", page=True
            )
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
