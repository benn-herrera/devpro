"""Shared helpers and fixtures for the profiler tests: the devpro shim, the run and serve runners, the store writers and the project install."""

import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import IO

import pytest

from devpro.dashboard.server import BOARD_PATH
from devpro.profiler.pages import COLUMNS
from tests.conftest import _dispatch_store
from tests.install.conftest import _claude_plugin, _definition_install

# Re-exported so the profiler suite's tests import the shared dispatch-store writer from its own
# conftest; the definition lives in the shared `tests/conftest.py` (see its `__all__`). Its own
# `_write_store` stays — the call-record helper its other tests import.
__all__ = ["_dispatch_store"]

LAYER_LINK = f'<link rel="stylesheet" href="{BOARD_PATH}board.css">'
_HERE = Path(__file__).parent
_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_MASK_SAMPLES = "mask_samples.txt"
_SERVE_TIMEOUT_S = 15.0
_PAYLOAD = json.dumps(
    {
        "hook_event_name": "PostToolUse",
        "session_id": "s-profiler",
        "tool_name": "Bash",
        "tool_input": {"command": "ls"},
    }
)
_RECORD_FIELDS = {"v", "harness", "at", "session", "tool", "name", "ok", "args", "branch", "plan", "directives"}
_PAGE_KEYS = {"session", "branch", "models", "plan", "directives", "contexts", "markers", "calls"}
_CALL_KEYS = {
    "ctx",
    "tool",
    "name",
    "start",
    "dur",
    "ok",
    "ctxTokens",
    "model",
    "args",
    "result",
    "child",
    "background",
    "running",
}


def _installed_wrapper(directory: Path) -> Path:
    """The installed wrapper, from a claude install into `directory`: `tools/devpro.sh` beside the
    package copy the install writes.

    `directory` is its own project root, so the install writes no `AGENTS.md` or `CLAUDE.md` beside the
    devpro shim a run places in it."""
    directory.mkdir(exist_ok=True)
    _definition_install(directory, project_root=directory)
    return _claude_plugin(directory) / "tools" / "devpro.sh"


@pytest.fixture(scope="session")
def _wrapper(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The installed wrapper one install serves every test that only reads and runs it: the tree under
    the session's own directory, none of a test's `tmp_path`.

    Its stores go where a test writes them — under the `project` it runs the wrapper in, never under this
    tree — so no test changes what another reads. A test that writes into the tree it runs takes
    `_installed_wrapper` and a directory of its own."""
    return _installed_wrapper(tmp_path_factory.mktemp("harness"))


def _devpro_shim(project: Path) -> Path:
    """A `devpro` command on `project`'s PATH: this checkout's `python3 -m devpro`, in `project`.

    A test that runs an installed wrapper directly (`dashboard`, `profiler`) gives its run one of
    these."""
    shim = project / "devpro"
    shim.write_text(
        "#!/bin/sh\nexec env " f'PYTHONPATH={_PACKAGE_ROOT} PYTHONDONTWRITEBYTECODE=1 python3 -m devpro "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    return shim


def _run(
    wrapper: Path,
    *args: str,
    cwd: Path,
    stdin: str | None = None,
    path: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Runs the installed wrapper with the `profiler` verb and `args`, a `devpro` shim of this
    checkout on PATH unless `path` is given, which sets PATH whole — a bare PATH, or one with no
    devpro. The wrapper consults PATH for one thing only, its interpreter, so a bare PATH is where a
    capture is put to the proof."""
    if path is None:
        path = f"{_devpro_shim(cwd).parent}:{os.environ['PATH']}"
    return subprocess.run(
        [str(wrapper), "profiler", *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, "PATH": path},
        check=False,
    )


_SERVE_URL = re.compile(r"^http://127\.0\.0\.1:\d+/$", re.MULTILINE)


@contextmanager
def _serve(*, cwd: Path, env: dict[str, str] | None = None) -> Iterator[str]:
    """The dashboard, run through this checkout's `devpro` shim, as a context manager yielding the
    URL its profiler view is at.

    `_run` blocks, and the dashboard never exits, so the process is started as a `Popen` and its
    stdout read by a watcher thread until the URL it prints arrives, the waiting side bounded by a
    timeout: nothing connects to a port before the server says it is listening. The process is
    killed and reaped on the way out, and a URL that never arrives leaves the process's stderr in
    the failure."""
    process = subprocess.Popen(
        [str(_devpro_shim(cwd)), "dashboard"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env={**os.environ, "PATH": f"{_devpro_shim(cwd).parent}:{os.environ['PATH']}", **(env or {})},
    )
    assert process.stdout is not None and process.stderr is not None
    urls: list[str] = []
    errors: list[str] = []

    def watch(stream: IO[bytes], into: list[str]) -> None:
        """One line at a time, until the stream closes: a whole-stream read answers only at EOF."""
        for line in iter(stream.readline, b""):
            into.append(line.decode("utf-8", "replace"))

    watchers = [
        threading.Thread(target=watch, args=(process.stdout, urls), daemon=True),
        threading.Thread(target=watch, args=(process.stderr, errors), daemon=True),
    ]
    for watcher in watchers:
        watcher.start()
    try:
        deadline = time.monotonic() + _SERVE_TIMEOUT_S
        while not urls and not errors and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        url = next((line.strip() for line in urls if _SERVE_URL.match(line)), "")
        assert url, f"the dashboard printed no URL; exited {process.poll()}: {''.join(errors)}"
        yield url
    finally:
        process.kill()
        process.wait()
        process.stdout.close()
        process.stderr.close()
        for watcher in watchers:
            watcher.join(_SERVE_TIMEOUT_S)


def index_head_classes(index: str) -> list[str]:
    """The `col-*` classes the index's header cells carry, in order."""
    head = index.split("<thead>", 1)[1].split("</thead>", 1)[0]
    return [cls for cls in re.findall(r'<th class="([^"]+)"', head) if cls.startswith("col-")]


def index_row_colspan(index: str) -> str:
    """The span the index's row script gives a full-width row, as its script's own expression: the
    header-cell count the script reads, never a literal."""
    script = index.split("<script>", 1)[1].split("</script>", 1)[0]
    return re.search(r"cell\.colSpan = (.+);", script).group(1)


def index_width_terms(index: str) -> int:
    """The terms of the table's floor — the width list's one home in its stylesheet — that the floor's
    `calc` sums."""
    floor = re.search(r"min-width: calc\((.*?)\);", index).group(1)
    return len(re.findall(r"nth\(var\(--widths\), \d+\)", floor))


def _plan(root: Path, title: str) -> None:
    """The project's active plan at `root`, its first level-1 heading `title`."""
    (root / "ACTIVE_PLAN.md").write_text(f"# {title}\n\nbody\n", encoding="utf-8")


def _bun() -> str:
    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the opencode capture cannot run without it")
    return "bun"


def _run_ts(
    script: Path,
    *,
    directory: Path,
    arg: str | None = None,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """One of the TypeScript runners under `tests/`, given the scratch directory it writes into, and
    the JSON payload it reads where it takes one: a runner given none is handed the directory."""
    done = subprocess.run(
        [_bun(), str(script), *([arg] if arg else [])],
        input=json.dumps({"directory": str(directory)}) if stdin is None else stdin,
        capture_output=True,
        encoding="utf-8",
        timeout=120,
        check=False,
        env=env,
    )
    assert done.returncode == 0, done.stderr
    return done


def _idle_store(root: Path, session: str, idles: list[tuple[str, int]]) -> Path:
    """The child's own opencode store, one idle record per `(at, background)` the child idled with: the
    event record the capture stamps, carrying the agent and model the child's last call request named."""
    directory = root / ".devpro-temp" / ".profiler-opencode"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{session}.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "v": 4,
                    "harness": "opencode",
                    "at": at,
                    "session": session,
                    "event": "experimental.idle",
                    "trigger": None,
                    "source": None,
                    "context_tokens": None,
                    "transcript": None,
                    "background": background,
                    "agent_type": "devpro-go-coder",
                    "model": "reaper/Qwen3.8-Flash-Next",
                }
            )
            + "\n"
            for at, background in idles
        ),
        encoding="utf-8",
    )
    return directory


def _claude_store(root: Path, session: str, at: str, *, extra: dict | None = None) -> Path:
    """A claude store under `root` holding one call record for `session` at `at`, carrying the fields
    in `extra` — the launch the capture wrote, the stop an event record beside it."""
    return _write_store(root, ".profiler-claude", session, at, harness="claude", extra=extra)


def _stop_at(root: Path, session: str, at: str, agent_id: str) -> None:
    """Appends a background subagent's SubagentStop at `at` to `session`'s claude store, as the capture
    writes it: an event record for `agent_id`, its `duration_ms` the stop hook's own cost. The call it
    ends wrote no `tool_use_id`, so the two are not read as one record twice."""
    path = root / ".devpro-temp" / ".profiler-claude" / f"{session}.jsonl"
    text = path.read_text(encoding="utf-8")
    with path.open("a", encoding="utf-8") as trace:
        trace.write(
            ("\n" if not text.endswith("\n") else "")
            + json.dumps(
                {
                    "v": 4,
                    "harness": "claude",
                    "at": at,
                    "session": session,
                    "agent_id": agent_id,
                    "event": "SubagentStop",
                    "ok": True,
                    "duration_ms": 5,
                }
            )
            + "\n"
        )


def _call_row(tree: str) -> tuple[str, str]:
    """A tree's call row as its time and duration columns: `"15:59:59", "500 ms"`.

    A dispatch's call is drawn after its context's placeholder, and neither is indented, so the call is
    the last row opening with a clock. Its columns are `pages.COLUMNS`', the time and duration the
    first two."""
    line = [line for line in tree.splitlines() if re.match(r"\d\d:\d\d:\d\d ", line)][-1]
    time_width, duration_width = (width for _, width, _ in COLUMNS[:2])
    return line[:time_width].strip(), line[time_width + 1 : time_width + 1 + duration_width].strip()


def _digest_runner(directory: Path, probe: Path, *, markers: bool = False) -> dict[str, object]:
    """The shipped `profiler.ts`'s stamp for a session starting at `directory`, its manifest and, where
    `markers` is asked for, the ownership markers it recognizes — each probe copy written into `probe`, never
    into `directory`, so nothing the runner writes stands in the state digested."""
    probe.mkdir()
    payload: dict[str, object] = {"directory": str(directory), "probeDirectory": str(probe)}
    if markers:
        payload["markersDirectory"] = str(probe)
    return json.loads(_run_ts(_HERE / "profiler_digest_runner.ts", directory=probe, stdin=json.dumps(payload)).stdout)


def _profiler_init(wrapper: Path, project: Path) -> subprocess.CompletedProcess[str]:
    """`profiler init claude` in `project`, through the installed wrapper `wrapper` and the test's
    devpro."""
    return _run(wrapper, "init", "claude", cwd=project)


def _write_store(
    root: Path, store: str, session: str, at: str, *, harness: str, records: int = 1, extra: dict | None = None
) -> Path:
    """A `.profiler-*` store under `root`, holding `records` call records for one session, a second
    apart from the moment `at` names, each carrying the fields in `extra`."""
    directory = root / ".devpro-temp" / store
    directory.mkdir(parents=True, exist_ok=True)
    start = datetime.fromisoformat(at.replace("Z", "+00:00"))
    (directory / f"{session}.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "v": 4,
                    "harness": harness,
                    "at": (start + timedelta(seconds=second)).strftime("%Y-%m-%dT%H:%M:%S.") + "000Z",
                    "session": session,
                    "tool": "Bash",
                    "name": "ls",
                    "duration_ms": 0,
                    "ok": True,
                    **(extra or {}),
                }
            )
            + "\n"
            for second in range(records)
        ),
        encoding="utf-8",
    )
    return directory


def _fetch(url: str) -> str:
    """The page at `url`, read as utf-8, with the request bounded by a timeout."""
    with urllib.request.urlopen(url, timeout=_SERVE_TIMEOUT_S) as response:
        return response.read().decode("utf-8")


_IIFE_OPENINGS = ("(() => {", "(function () {")


def _inline_script_bodies(page: str) -> list[str]:
    """`page`'s inline script bodies, in order: each between its `<script>` tag and its close, a tag
    naming a `src` loading a file and carrying no body."""
    return re.findall(r"<script>(.*?)</script>", page, re.DOTALL)


def _opens_an_iife(body: str) -> bool:
    """Whether `body`'s first statement is the notation's one global or opens an IIFE, a leading
    `'use strict';` directive — in either quote the shipped scripts spell it in — and the comments
    ahead of it passed over. The deco's body opens with the one deliberate global (`devproFormat`,
    the pages' notation), a single named export the other scripts live inside."""
    for line in body.splitlines():
        statement = line.strip()
        if not statement or statement.startswith("//") or statement in ("'use strict';", '"use strict";'):
            continue
        return statement in _IIFE_OPENINGS or statement == "globalThis.devproFormat = (() => {"
    return False


def _install_project(project: Path) -> subprocess.CompletedProcess[str]:
    """`devpro install` of this checkout into `project`, its claude harness detected: the CLI's own
    `main`, in a child interpreter so the run's exit status and streams are the installer's."""
    return subprocess.run(
        [sys.executable, "-m", "devpro", "install", str(project)],
        capture_output=True,
        text=True,
        cwd=project,
        stdin=subprocess.DEVNULL,
        env={
            **os.environ,
            "PYTHONPATH": str(_PACKAGE_ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            # No user-level harness directory of this machine's own: detection reads the target alone.
            "HOME": str(project.parent / "home"),
        },
        check=False,
    )


@pytest.fixture
def kolkata(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """The machine pinned to a zone four and a half hours ahead of UTC for one test, its zone back
    afterwards whether the test passed or failed."""
    monkeypatch.setenv("TZ", "Asia/Kolkata")
    time.tzset()
    yield
    time.tzset()
