"""The dashboard's test fixtures: a project to serve, a store with a recorded session, a dashboard
under test, and the client that reads it back.

The dashboard reads its stores and its git root from the directory it runs in — the working
directory when it starts. The suite's own fixtures move the working directory around, so every
dashboard here takes its root explicitly: `DashboardServer(root=...)`, whose stores are that root's
and whose board is read from it, like a dashboard started inside the project.
"""

import http.client
import io
import json
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from email.message import Message
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from devpro.dashboard.server import DashboardServer

TIMEOUT = 10
PLAN = "# Plan\n\nRelease: 9.9.9\n\n## Status\n\n| Package | Rating | State |\n|---|---|---|\n| P1 | expert | |\n"


def project(root: Path, files: dict[str, str]) -> Path:
    """A project at root: its `.git` and the files named, at the path the file system gives it."""
    root = Path(root).resolve()
    (root / ".git").mkdir(parents=True)
    for name, text in files.items():
        write(root / name, text)
    return root


def write(path: Path, text: str) -> None:
    """Write text to path, creating its directory."""
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def record(at: str, *, tool: str = "Bash", name: str = "ls", session: str = "s-one") -> dict:
    """One schema-2 call record."""
    return {
        "v": 2,
        "harness": "claude",
        "at": at,
        "session": session,
        "tool": tool,
        "name": name,
        "duration_ms": 0,
        "ok": True,
    }


def store(root: Path, session: str, records: list[dict], *, directory: str = ".profiler-claude") -> Path:
    """A session's records in one `.profiler-*` store under root, its records one line each."""
    path = Path(root).resolve() / ".devpro-temp" / directory / f"{session}.jsonl"
    write(path, "".join(json.dumps(row) + "\n" for row in records))
    return path


class Client:
    """One server's URL, with a request's answer as the tests read it."""

    def __init__(self, url: str) -> None:
        self.url = url
        parts = urlsplit(url)
        self.host, self.port = parts.hostname or "", parts.port or 0

    def get(self, path: str) -> tuple[int, str, bytes]:
        """The status, content type and body of path, its 4xx answered rather than raised."""
        try:
            with urllib.request.urlopen(self.url + path, timeout=TIMEOUT) as response:
                return response.status, response.headers.get_content_type(), response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.headers.get_content_type(), error.read()

    def post(self, path: str, body: dict) -> tuple[int, dict]:
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(self.url + path, data, {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def raw(self, method: str, path: str, *, body: bytes = b"", host: str | None = None) -> tuple[int, Message]:
        """The status and headers of a request sent with exactly the host given, where one is."""
        headers = {"Content-Type": "application/json"}
        if host is not None:
            headers["Host"] = host
        connection = http.client.HTTPConnection(self.host, self.port, timeout=TIMEOUT)
        try:
            connection.request(method, "/" + path, body=body, headers=headers)
            response = connection.getresponse()
            response.read()
            return response.status, response.headers
        finally:
            connection.close()


def dashboard(root: Path) -> DashboardServer:
    """A dashboard of the project at root, its stores and board that project's, serving nothing yet."""
    return DashboardServer(root=Path(root).resolve(), stderr=io.StringIO())


@pytest.fixture
def serve() -> Iterator:
    """A dashboard over a project's root, serving; every one started is stopped."""
    started: list[tuple[DashboardServer, threading.Thread]] = []

    def start(root: Path) -> Client:
        server = dashboard(root)
        server.start()
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
        thread.start()
        started.append((server, thread))
        return Client(server.url)

    def stop_all() -> None:
        while started:
            server, thread = started.pop()
            server.shutdown()
            thread.join()
            server.server_close()

    start.stop_all = stop_all
    yield start
    stop_all()


@contextmanager
def serving(root: Path) -> Iterator[Client]:
    """A dashboard over root, serving for the body's length."""
    server = dashboard(root)
    server.start()
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    try:
        yield Client(server.url)
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
