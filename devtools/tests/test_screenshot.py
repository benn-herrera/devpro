"""`devtools/screenshot.ts`, run under bun the way the `screenshot` recipe runs it.

The page is a static file whose own script, 300 ms after load, adds the `#ready` element and makes the
body 1200px tall; until then it is shorter than the viewport. The shot is read from its PNG header,
which carries the width and height the image was taken at.
"""

import shutil
import struct
import subprocess
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
