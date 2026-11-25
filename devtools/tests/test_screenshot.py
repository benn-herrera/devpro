"""`devtools/screenshot.ts`, run under bun the way the `screenshot` recipe runs it.

The page is a static file whose own script, 300 ms after load, adds the `#ready` element and makes the
body 1200px tall; until then it is shorter than the viewport. The shot is read from its PNG header,
which carries the width and height the image was taken at. The route case serves its page from a local
`http.server`, which is the page form `--base` exists for.
"""

import functools
import shutil
import struct
import subprocess
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "screenshot.ts"
PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>shot</title></head>
<body style="margin:0"><p>short</p>
<script>
setTimeout(() => {
  const ready = document.createElement('p');
  ready.id = 'ready';
  document.body.append(ready);
  document.body.style.height = '1200px';
}, 300);
</script></body></html>
"""
# A page that re-fetches every 300 ms, so its network never quiets for the driver's 500 ms idle window:
# the page the settle exists to shoot, and the one a mandatory idle wait fails. The marker is present
# from load.
POLLER_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>poller</title></head>
<body style="margin:0"><p id="marker">polling</p>
<script>
setInterval(() => { fetch('poller.html?t=' + Date.now()).catch(() => {}); }, 300);
</script></body></html>
"""
# A page that reports the dark scheme whatever it is shown in, so a `--color-scheme light` run's check
# can fail against a real page.
DARK_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>dark</title></head>
<body><p id="ready">redefined</p>
<script>
window.matchMedia = () => ({ matches: true });
</script></body></html>
"""


class _QuietHandler(SimpleHTTPRequestHandler):
    """The static file server, silent: its request log is the server's, not the test's output."""

    def log_message(self, format: str, *args: object) -> None:
        pass


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bun", str(TOOL), *args],
        capture_output=True,
        text=True,
        timeout=180,
        stdin=subprocess.DEVNULL,
    )


def _png_size(path: Path) -> tuple[int, int]:
    """The width and height a PNG's IHDR header states."""
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path} does not open with the PNG signature"
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def _tools() -> None:
    """Names every missing tool at once; a missing one fails the case rather than skipping it."""
    missing = [name for name in ("bun", "firefox") if shutil.which(name) is None]
    assert not missing, f"the screenshot test needs {', '.join(missing)} on PATH"


@contextmanager
def _served(root: Path) -> Iterator[int]:
    """Serves `root` over HTTP on a free local port, and stops the server on the way out."""
    handler = functools.partial(_QuietHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_a_settled_page_is_shot_whole_at_the_viewport(tmp_path: Path) -> None:
    """The defect is a shot taken before the page settled, or one that ignores the viewport.

    A shot taken before `#ready` appears is the viewport's own height, 300; one that ignores
    `--viewport` is not 400 wide.
    """
    _tools()
    page = tmp_path / "page.html"
    page.write_text(PAGE, encoding="utf-8")
    shot = tmp_path / "shot.png"

    result = _run(str(page), "--wait-for", "#ready", "--viewport", "400x300", "--out", str(shot))

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{shot}\n"
    width, height = _png_size(shot)
    assert width == 400
    assert height >= 1200


def test_a_selector_that_never_appears_fails_naming_it_and_the_timeout(tmp_path: Path) -> None:
    """The defect is a run that reports success for a page it never saw settle, or leaves a file behind."""
    _tools()
    page = tmp_path / "page.html"
    page.write_text(PAGE, encoding="utf-8")
    shot = tmp_path / "never.png"

    result = _run(str(page), "--wait-for", "#never", "--timeout", "2000", "--out", str(shot))

    assert result.returncode == 1, result.stderr
    assert "#never" in result.stderr
    assert "2000" in result.stderr
    assert not shot.exists()


def test_a_route_is_resolved_against_base_before_the_filesystem(tmp_path: Path) -> None:
    """The defect is a route that names an existing path on disk read as a `file://` page.

    `/` is such a route and always exists, so the tool shot the filesystem's root listing instead of
    the served page and exited 0; `#ready` exists on the served page alone. Before the change the run
    exited 1 with `#ready` never appearing.
    """
    _tools()
    (tmp_path / "index.html").write_text(PAGE, encoding="utf-8")
    shot = tmp_path / "route.png"

    with _served(tmp_path) as port:
        result = _run("/", "--base", f"http://127.0.0.1:{port}", "--wait-for", "#ready", "--out", str(shot))

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{shot}\n"
    assert shot.exists()


def test_a_polling_page_with_a_selector_is_shot(tmp_path: Path) -> None:
    """The defect is a settle whose idle wait is mandatory: a polling page never quiets, so the run
    fails and the tool cannot shoot the pages it exists for.

    Before the change the load waited on `networkidle0`, which a 300 ms poller never reaches: the
    run exited 1 on a navigation timeout. The selector is given and appears, so the run settles on
    it and exits 0 inside `--timeout`.
    """
    _tools()
    (tmp_path / "poller.html").write_text(POLLER_PAGE, encoding="utf-8")
    shot = tmp_path / "poll.png"

    with _served(tmp_path) as port:
        result = _run(
            "/poller.html",
            "--base",
            f"http://127.0.0.1:{port}",
            "--wait-for",
            "#marker",
            "--timeout",
            "3000",
            "--out",
            str(shot),
        )

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{shot}\n"
    assert shot.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_a_polling_page_without_a_selector_still_shoots(tmp_path: Path) -> None:
    """The defect is a mandatory idle wait: with no `--wait-for`, the polling page's idle wait must
    be bounded and advisory, never a failure.

    Before the change the load's `networkidle0` expired at `--timeout` and exited 1. After it, the
    idle wait expires inside its own bound, is swallowed, and the PNG is written.
    """
    _tools()
    (tmp_path / "poller.html").write_text(POLLER_PAGE, encoding="utf-8")
    shot = tmp_path / "idle.png"

    with _served(tmp_path) as port:
        result = _run(
            "/poller.html",
            "--base",
            f"http://127.0.0.1:{port}",
            "--timeout",
            "3000",
            "--out",
            str(shot),
        )

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{shot}\n"
    assert shot.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_a_page_shown_in_the_wrong_scheme_fails_and_writes_no_png(tmp_path: Path) -> None:
    """The defect is a failed color-scheme check that leaves its PNG behind, having already written it.

    The page reports dark from its own script, so `--color-scheme light` must fail the run; before the
    change `scheme()` ran after the shot, so the run exited 1 with the wrong-scheme PNG at `--out`.
    """
    _tools()
    page = tmp_path / "dark.html"
    page.write_text(DARK_PAGE, encoding="utf-8")
    shot = tmp_path / "x.png"

    result = _run(str(page), "--color-scheme", "light", "--out", str(shot))

    assert result.returncode == 1, result.stderr
    assert "dark" in result.stderr
    assert not shot.exists()
