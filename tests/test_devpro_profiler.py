"""The activity profiler's contract, driven through the launcher the install copies: one capture
writes a schema-2 record, `tree --format html`'s page data carries the keys `view.html` parses, and the
installed launcher is the source's bytes. It fails on the port defect that renames or drops a record
field the page data carries — the rename or drop ships green and renders an empty page.

Two records the port itself owns: `tree` renders an opencode session's store beside the claude
capture's — the split that is the capture's purpose, and whose loss the single-store read would not
show; and the opencode capture, driven by `tests/profiler_capture_runner.ts` through the shipped
`profiler.ts`, writes a record for every call it is fired for, a failed one carrying its error's text.
`test_the_two_masks_redact_alike` holds the two harnesses' masking to one sample list, since
JavaScript's `\\w` is ASCII where Python's is not.

Two more are the launcher's own: a capture whose wrapper the launcher cannot resolve exits 0 with no
output and no other subcommand does, and `init` lays down the launcher alone, removing the `hp.sh`,
`hp.py` and `view.html` older inits left beside it.

The stores' rename is the last group's: an install and an `init` move each `*-profiler` store under
`.devpro-temp/` to its `.profiler-*` name and name the move, and neither ever merges one store into
another; `doctor` names an old-pattern store the reader cannot see.

The package is imported from the repository root, which `just test` puts on PYTHONPATH. The launcher
runs the wrapper the install copies beside it, and no test relies on a devpro installed on the host:
the install runs in the test's directory, so the wrapper beside the launcher runs this checkout's
code.
"""

import json
import os
import re
import shlex
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
from devpro.profiler.capture import mask
from devpro.profiler.hooks import RETIRED_HOOK_FILES, launcher_resource
from devpro.profiler.pages import (
    BAND_LEGEND,
    DATA_MARK,
    DISPATCHED_MARK,
    INDEX,
    LAYER_INLINE,
    LAYER_MARK,
    RETURN_MARK,
    SHARED_CSS,
    index_html,
)
from devpro.profiler.stores import repair_child_ids
from devpro.profiler.values import CAPTURED_EVENTS, _epoch_ms
from tests.test_devpro_install import _PROFILER, _claude_plugin, _definition_install

# The serve path's carrier of the shared layer: the one file the board panel serves, which the pages
# it serves name instead of the inline text `SHARED_CSS` holds.
LAYER_LINK = f'<link rel="stylesheet" href="{BOARD_PATH}board.css">'

_HERE = Path(__file__).parent
_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
# The samples both masking implementations are held to: the credential shapes the profiler's SECRETS are
# written for, and the same shapes holding a non-ASCII letter, where JavaScript's `\w` stops matching.
_MASK_SAMPLES = "mask_samples.txt"
# How long a dashboard's URL may take to appear, and how long one fetch may take to answer.
_SERVE_TIMEOUT_S = 15.0

# The four keys the hook's own payload carries (the guardrail's probe payload apart from the values).
_PAYLOAD = json.dumps(
    {
        "hook_event_name": "PostToolUse",
        "session_id": "s-profiler",
        "tool_name": "Bash",
        "tool_input": {"command": "ls"},
    }
)

# The fields this payload fills, in the schema `view.html` and `tree` read: a rename or a drop of
# any of them changes the record's shape.
_RECORD_FIELDS = {"v", "harness", "at", "session", "tool", "name", "ok", "args", "branch"}

# The keys `view.html` reads from the page's data and from one call row.
_PAGE_KEYS = {"session", "branch", "contexts", "markers", "calls"}
_CALL_KEYS = {
    "ctx",
    "tool",
    "name",
    "start",
    "dur",
    "ok",
    "ctxTokens",
    "args",
    "result",
    "child",
    "background",
    "running",
}


def _launcher(directory: Path) -> Path:
    """The installed launcher, from a claude install into `directory`.

    `directory` is its own project root, so the install writes no `AGENTS.md` or `CLAUDE.md` beside the
    devpro shim a run places in it."""
    directory.mkdir(exist_ok=True)
    _definition_install(directory, project_root=directory)
    return _claude_plugin(directory) / _PROFILER / "profiler.sh"


def _devpro_shim(project: Path) -> Path:
    """A `devpro` command the launcher finds: this checkout's `python3 -m devpro`, in `project`.

    The launcher runs whatever `devpro` it resolves, so a test gives it one that runs this repository's
    code: its finder, the verb's dispatch and the capture all run as the install's do."""
    shim = project / "devpro"
    shim.write_text(
        "#!/bin/sh\nexec env " f'PYTHONPATH={_PACKAGE_ROOT} PYTHONDONTWRITEBYTECODE=1 python3 -m devpro "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    return shim


def _run(
    launcher: Path,
    *args: str,
    cwd: Path,
    stdin: str | None = None,
    path: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Runs the launcher with a `devpro` shim of this checkout on PATH, unless `path` is given, which
    sets PATH whole — a bare PATH, or one with no devpro. The launcher consults PATH for nothing: the
    wrapper beside it is what runs, and a bare PATH is where that is put to the proof."""
    if path is None:
        path = f"{_devpro_shim(cwd).parent}:{os.environ['PATH']}"
    return subprocess.run(
        ["bash", str(launcher), *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, "PATH": path},
        check=False,
    )


_SERVE_URL = re.compile(r"^http://127\.0\.0\.1:\d+/$", re.MULTILINE)


@contextmanager
def _serve(launcher: Path, *, cwd: Path, env: dict[str, str] | None = None) -> Iterator[str]:
    """The dashboard, through the launcher's `devpro`, as `_run` runs it, as a context manager
    yielding the URL its profiler view is at.

    `_run` blocks, and the dashboard never exits, so the process is started as a `Popen` and its
    stdout read by a watcher thread until the URL it prints arrives, the waiting side bounded by a
    timeout: nothing connects to a port before the server says it is listening. The process is
    killed and reaped on the way out, and a URL that never arrives leaves the process's stderr in
    the failure. The launcher runs the profiler verb, so the dashboard is the found `devpro`'s,
    run beside the launcher's capture."""
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


def _page_data(page: str) -> dict:
    """The JSON the page template inlines at its data slot."""
    return json.loads(page.split("const D = ", 1)[1].split(";\n", 1)[0])


def test_a_capture_writes_the_record_the_page_and_tree_read(tmp_path: Path) -> None:
    """One well-formed hook payload appends one line to the project's trace, carrying schema 2 and
    the field names the unchanged page and tree read; the html page's data carries the keys
    `view.html` parses."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    launcher = _launcher(tmp_path / "harness")
    capture = _run(launcher, "capture", "claude", cwd=project, stdin=_PAYLOAD)
    assert capture.returncode == 0, capture.stderr
    assert capture.stdout == "" and capture.stderr == ""
    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    [record] = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line]
    assert record["v"] == 2
    assert _RECORD_FIELDS <= set(record), sorted(record)
    assert record["session"] == "s-profiler"
    assert record["tool"] == "Bash"
    assert record["ok"] is True
    assert record["args"] == "ls"
    page = _run(launcher, "tree", "--format", "html", cwd=project)
    assert page.returncode == 0, page.stderr
    data = _page_data(page.stdout)
    assert _PAGE_KEYS <= set(data), sorted(data)
    assert data["session"] == "s-profiler"
    assert _CALL_KEYS <= set(data["calls"][0]), sorted(data["calls"][0])
    assert data["calls"][0]["tool"] == "Bash"


def test_a_session_whose_trace_holds_the_data_mark_renders(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: the page's data was inlined with `/` unescaped, so a
    trace carrying the data mark's own text, `/*DATA*/null`, made the strict fill refuse a value holding
    its mark and `tree --format html` failed for that session."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    args = f"grep -n '{DATA_MARK}' view.html"
    _write_store(
        project, ".profiler-claude", "s-mark", "2026-01-01T00:00:00.000Z", harness="claude", extra={"args": args}
    )

    page = _run(_launcher(tmp_path / "harness"), "tree", "--format", "html", cwd=project)

    assert page.returncode == 0, page.stderr
    assert _page_data(page.stdout)["calls"][0]["args"] == args


def test_a_capture_writes_its_line_in_the_bytes_it_measured(tmp_path: Path) -> None:
    """A lone surrogate in a tool argument, and a non-ASCII one, measure as the bytes the store holds:
    the line is ASCII, so the length `serialize` bounds and the file's bytes are one count, and
    `read_text` reads the same JSON back on a host whose default encoding is not utf-8."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    payload = dict(json.loads(_PAYLOAD), tool_input={"command": "echo h\u00e9 \ud800"})
    launcher = _launcher(tmp_path / "harness")
    capture = _run(launcher, "capture", "claude", cwd=project, stdin=json.dumps(payload))
    assert capture.returncode == 0, capture.stderr
    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    line = trace.read_bytes().decode("ascii")
    assert json.loads(line)["args"] == "echo h\u00e9 \ud800"


def test_the_installed_profiler_is_the_sources_bytes(tmp_path: Path) -> None:
    """The launcher that ships is the launcher the repository holds: no stamp or reflow lands in
    `profiler.sh` on its way through the package data."""
    launcher = _launcher(tmp_path / "harness")
    assert launcher.read_bytes() == launcher_resource().read_bytes()


def test_a_launcher_discards_what_its_capture_child_prints(tmp_path: Path) -> None:
    """A hook's stdout is the host's protocol alone, so the capture's own output is discarded even where
    the wrapper succeeds. Defect: the launcher passed the capture child's stdout straight through, so a
    warning or a progress line a wrapper printed there reached Claude Code as its hook result."""
    launcher = _launcher(tmp_path / "harness")
    wrapper = launcher.parent / ".." / "tools" / "devpro.sh"
    wrapper.write_text("#!/bin/sh\necho 'a line the wrapper printed'\nexit 0\n", encoding="utf-8")
    wrapper.chmod(0o755)
    project = tmp_path / "project"
    project.mkdir()

    done = _run(launcher, "capture", "claude", cwd=project, stdin=_PAYLOAD, path="/usr/bin:/bin")

    assert (done.returncode, done.stdout) == (0, ""), done.stderr


@pytest.mark.parametrize("command", ["capture", "tree"])
def test_a_launcher_whose_wrapper_fails_captures_silently_and_reports_otherwise(tmp_path: Path, command: str) -> None:
    """The wrapper beside the launcher that stands but fails: `capture` drains stdin and exits 0 — the
    wrapper's own refusal on stderr is what names the failure, and a capture that exits nonzero blocks
    the tool call that fired it — and every other subcommand refuses with it. A tree that says nothing
    and fails leaves the operator no line naming the one dependency to fix."""
    launcher = _launcher(tmp_path / "harness")
    payload = json.dumps({"hook_event_name": "PostToolUse", "session_id": "s-none", "tool_name": "Bash"})
    project = tmp_path / "project"
    project.mkdir()
    wrapper = launcher.parent / ".." / "tools" / "devpro.sh"
    wrapper.write_text("#!/bin/sh\necho 'devpro.sh: this wrapper is broken' >&2\nexit 1\n", encoding="utf-8")
    wrapper.chmod(0o755)
    done = subprocess.run(
        ["bash", str(launcher), command],
        input=payload,
        capture_output=True,
        text=True,
        cwd=project,
        env={**os.environ, "PATH": "/usr/bin:/bin"},
        check=False,
    )

    assert done.returncode == (0 if command == "capture" else 1), done.stderr
    assert done.stdout == ""
    assert "devpro.sh: this wrapper is broken" in done.stderr
    assert not (project / ".devpro-temp").exists()


def test_a_launcher_with_no_wrapper_beside_it_never_runs_a_devpro_from_path(tmp_path: Path) -> None:
    """No wrapper stands beside the launcher — the launcher's whole resolution is that file: a capture
    drains stdin and exits 0 writing nothing, every other subcommand reports and exits 1, and a
    `devpro` waiting on PATH is never run, there being no PATH search and no probe. A foreign devpro
    run from a hook is the capture this tool did not write."""
    launcher = _launcher(tmp_path / "harness")
    wrapper = launcher.parent / ".." / "tools" / "devpro.sh"
    wrapper.unlink(missing_ok=True)
    on_path = tmp_path / "on-path"
    on_path.mkdir()
    foreign = on_path / "devpro"
    foreign.write_text('#!/bin/sh\nprintf \'%s\\n\' "$*" >> "$PROBE_LOG"\n', encoding="utf-8")
    foreign.chmod(0o755)
    log = tmp_path / "log"
    payload = json.dumps({"hook_event_name": "PostToolUse", "session_id": "s-none", "tool_name": "Bash"})
    project = tmp_path / "project"
    project.mkdir()
    environment = {**os.environ, "PATH": f"{on_path}:/usr/bin:/bin", "PROBE_LOG": str(log)}

    capture = subprocess.run(
        ["bash", str(launcher), "capture", "claude"],
        input=payload,
        capture_output=True,
        text=True,
        cwd=project,
        env=environment,
        check=False,
    )
    tree = subprocess.run(
        ["bash", str(launcher), "tree"],
        input="",
        capture_output=True,
        text=True,
        cwd=project,
        env=environment,
        check=False,
    )

    assert (capture.returncode, capture.stdout, capture.stderr) == (0, "", "")
    assert tree.returncode == 1 and tree.stdout == ""
    assert "no devpro wrapper beside the launcher" in tree.stderr
    assert not log.exists()
    assert not (project / ".devpro-temp").exists()


def test_a_launcher_whose_wrapper_lacks_the_execute_bit_runs_no_devpro_from_path(tmp_path: Path) -> None:
    """A wrapper that exists without its execute bit still stands: the launcher runs it, the shell
    refuses it, and a capture drains stdin and exits 0 — a `devpro` on PATH is never reached, there
    being no PATH search. Defect: the finder tested `-x`, skipped the wrapper, and ran the `devpro`
    on PATH."""
    launcher = _launcher(tmp_path / "harness")
    (launcher.parent / ".." / "tools" / "devpro.sh").chmod(0o644)
    on_path = tmp_path / "on-path"
    on_path.mkdir()
    foreign = on_path / "devpro"
    foreign.write_text('#!/bin/sh\nprintf \'%s\\n\' "$*" >> "$PROBE_LOG"\n', encoding="utf-8")
    foreign.chmod(0o755)
    log = tmp_path / "log"
    project = tmp_path / "project"
    project.mkdir()
    done = subprocess.run(
        ["bash", str(launcher), "capture", "claude"],
        input=_PAYLOAD,
        capture_output=True,
        text=True,
        cwd=project,
        env={**os.environ, "PATH": f"{on_path}:/usr/bin:/bin", "PROBE_LOG": str(log)},
        check=False,
    )
    assert done.returncode == 0 and done.stdout == ""
    assert done.stderr != ""
    assert not log.exists()
    assert not (project / ".devpro-temp").exists()


def test_a_launcher_runs_the_wrapper_beside_it_with_no_devpro_on_path(tmp_path: Path) -> None:
    """The launcher's whole resolution is the wrapper beside it: a capture through it writes the
    record, with no `devpro` on PATH at all. Defect: before the launcher named its own installation,
    a hook run with a bare PATH found no devpro and the capture wrote nothing, though the install's
    copy stood one file away."""
    launcher = _launcher(tmp_path / "harness")
    assert (launcher.parent / ".." / "tools" / "devpro.sh").is_file(), "the install writes the wrapper"
    project = tmp_path / "project"
    project.mkdir()
    done = _run(launcher, "capture", "claude", cwd=project, stdin=_PAYLOAD, path="/usr/bin:/bin")
    assert done.returncode == 0, done.stderr
    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    [record] = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line]
    assert record["tool"] == "Bash" and record["args"] == "ls"


def test_a_tree_renders_an_opencode_store_beside_the_claude_capture(tmp_path: Path) -> None:
    """A session in each harness's store under one project, and one `tree <id>` per store renders it:
    the read that walks every `.profiler-*` store, whose revert to claude's alone loses the opencode
    session silently.

    The opencode dispatch's record draws the context words claude's dispatch draws for the same
    fields — `new context <id>`, and `copy of <caller>` on the host's `fork` kind. A tree reading the
    context a call started from claude's `agent_id` alone draws the opencode dispatch with no child
    context, the two harnesses' dispatches differing on records that state one fact."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    launcher = _launcher(tmp_path / "harness")
    capture = _run(launcher, "capture", "claude", cwd=project, stdin=_PAYLOAD)
    assert capture.returncode == 0, capture.stderr
    # A record the opencode capture writes, holding what `tree`'s render reads: an event at start and
    # the call, which only --verbose draws.
    opencode = project / ".devpro-temp" / ".profiler-opencode" / "s-opencode.jsonl"
    opencode.parent.mkdir()
    opencode.write_text(
        "\n".join(
            json.dumps(record)
            for record in (
                {
                    "v": 2,
                    "harness": "opencode",
                    "at": "2026-01-01T00:00:00.000Z",
                    "session": "s-opencode",
                    "event": "experimental.idle",
                    "trigger": None,
                    "source": None,
                    "context_tokens": None,
                    "transcript": None,
                },
                {
                    "v": 2,
                    "harness": "opencode",
                    "at": "2026-01-01T00:00:01.000Z",
                    "session": "s-opencode",
                    "agent_id": None,
                    "agent_type": None,
                    "tool_use_id": None,
                    "tool": "shell",
                    "name": "make test",
                    "duration_ms": 1000,
                    "ok": True,
                    "child_agent_id": None,
                    "child_agent_type": None,
                    "background": False,
                    "child_spend": None,
                    "tokens": None,
                    "context_tokens": None,
                    "branch": None,
                    "args": "make test",
                    "result": "ok",
                },
                {
                    "v": 2,
                    "harness": "opencode",
                    "at": "2026-01-01T00:00:02.000Z",
                    "session": "s-opencode",
                    "agent_id": None,
                    "agent_type": None,
                    "tool_use_id": None,
                    "tool": "Agent",
                    "name": "devpro-architect",
                    "duration_ms": 500,
                    "ok": True,
                    "child_agent_id": "ses_fork",
                    "child_agent_type": "fork",
                    "background": False,
                    "child_spend": None,
                    "tokens": None,
                    "context_tokens": None,
                    "branch": None,
                    "args": "fork it",
                    "result": "done",
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )

    opencode_tree = _run(launcher, "tree", "--verbose", "s-opencode", cwd=project)
    assert opencode_tree.returncode == 0, opencode_tree.stderr
    assert "make test" in opencode_tree.stdout
    # The dispatch draws the context words the same fields draw under claude: the host's `fork` kind
    # makes the child a copy of its caller's history.
    assert "new context ses_fo, copy of main" in opencode_tree.stdout
    claude_tree = _run(launcher, "tree", "--verbose", "s-profiler", cwd=project)
    assert claude_tree.returncode == 0, claude_tree.stderr
    assert "ls" in claude_tree.stdout


def _bun() -> str:
    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the opencode capture cannot run without it")
    return "bun"


# A moment's reading is pinned on the reader's zone with `TZ`: the zone decides which day and clock a
# date draws into, so a pin holding no zone asserts on whatever the runner carries. The locale is not
# holdable under the embedded bun — `LC_ALL=de_DE.UTF-8 bun` still resolves `en-US` — so the expected
# text is built from the date's own fields, reading the same under whatever locale the runner carries;
# `LC_ALL` rides along although bun ignores it.
_MOMENT_LOCALE = {"TZ": "America/Los_Angeles", "LC_ALL": "de_DE.UTF-8"}

# The crafted feed's four instants, as epoch milliseconds: a pair whose ends share the reader's day
# (2026-01-01T00:00:01.250Z and T02:00:00Z — LA, 2025-12-31 16:00 and 18:00) and a pair whose span
# crosses the reader's midnight (T06:00:00Z and T08:00:00.500Z — LA, 2025-12-31 22:00 and 2026-01-01
# 00:00).
_SAME_DAY_FIRST = 1767225601250
_SAME_DAY_LAST = 1767232800000
_MIDNIGHT_FIRST = 1767247200000
_MIDNIGHT_LAST = 1767254400500


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


_PAGE_RUNNER = _HERE / "profiler_page_runner.ts"


def _page_runner(tmp_path: Path, page: str, deco: str = "") -> dict:
    """A session page in a browser's own shape (`profiler_page_runner.ts`): the page's own scripts,
    with the deco's file the page names ahead of them where the carrier loads that file — a file
    carrier loads nothing, so it runs the page's script alone — in one shared classic-script scope,
    the way the browser executes a page. The runner reports the header stamp the page drew and the
    subline's markup as the scripts left it."""
    run = _run_ts(
        _PAGE_RUNNER,
        directory=tmp_path,
        stdin=json.dumps({"page": page, "deco": deco}),
        env={**os.environ, **_MOMENT_LOCALE},
    )
    return json.loads(run.stdout)


def test_the_pages_draw_their_moments_local_at_birth(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect this package replaces is the double render — the
    pages' own scripts writing the raw UTC and the deco's sweep rewriting it in the reader's clock —
    so the page a file carrier serves, where the deco the page names cannot load, reads UTC, and a
    pin reading a swept page cannot fail on it. The run that fails under it is this one: each page's
    own script alone draws its moments, and the drawn text is the reader's local time.

    The index's moments cell carries the first end's date whole beside its time and the second end's
    time only, 24-hour, one notation whether the ends share the reader's day or cross its midnight —
    the hand-built clock, its separator and digits the page's own — and the session page's header
    stamp reads with its date, the page's title naming no day. The machine form stands in the
    `datetime` attributes and the raw UTC in the titles. The zone is pinned with `TZ`; the locale is
    not holdable under the embedded bun, so a clock built from the date's own fields reads the same
    under whatever locale the runner carries."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")
    launcher = _launcher(tmp_path / "harness")

    with _serve(launcher, cwd=project) as url:
        index = _fetch(f"{url}profiler/")
    # The feed crafted, so the instants are known by construction: one pair whose ends share the
    # reader's day and one whose span crosses the reader's midnight (PST, UTC-8 in January).
    feed = [
        {
            "harness": "claude",
            "id": "s-same-day",
            "records": 1,
            "agents": 0,
            "first": _SAME_DAY_FIRST,
            "last": _SAME_DAY_LAST,
            "span": 7199,
        },
        {
            "harness": "claude",
            "id": "s-midnight",
            "records": 1,
            "agents": 0,
            "first": _MIDNIGHT_FIRST,
            "last": _MIDNIGHT_LAST,
            "span": 7200,
        },
    ]
    run = _run_ts(
        _HERE / "profiler_index_runner.ts",
        directory=tmp_path,
        stdin=json.dumps({"index": index, "feed": feed}),
        env={**os.environ, **_MOMENT_LOCALE},
    )
    cells = [
        re.search(r'<span\b[^>]*class="moments"[^>]*>.*?</span>', row).group(0)
        for row in json.loads(run.stdout)["rows"]
    ]
    assert cells == [
        '<span title="2026-01-01 00:00:01 UTC to 2026-01-01T02:00:00Z" class="moments">'
        '<time datetime="2026-01-01T00:00:01.250Z" title="2026-01-01 00:00:01 UTC">2025-12-31 16:00</time> to '
        '<time datetime="2026-01-01T02:00:00Z" title="2026-01-01 02:00:00 UTC">18:00</time></span>',
        '<span title="2026-01-01 06:00:00 UTC to 2026-01-01T08:00:00.500Z" class="moments">'
        '<time datetime="2026-01-01T06:00:00Z" title="2026-01-01 06:00:00 UTC">2025-12-31 22:00</time> to '
        '<time datetime="2026-01-01T08:00:00.500Z" title="2026-01-01 08:00:00 UTC">00:00</time></span>',
    ]

    # The session page's header stamp, drawn by the page's own script alone — the file carrier's
    # `tree --format html` page, whose script the page names and a file cannot load.
    printed = _run(launcher, "tree", "s-claude", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr
    stamped = _page_runner(tmp_path, printed.stdout)["stamped"]
    assert stamped == [["2025-12-31 16:00", "2026-01-01 00:00 UTC", "2026-01-01T00:00:00.000Z"]], stamped


def test_the_pages_two_carriers_differ_in_the_layers_slot_alone(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect the one rendering replaces is the page assembled twice
    — the file flow's page carrying no band facts and no dispatcher where the served page carried
    them, the moments drawn twice besides — so the two carriers' full texts differed beyond the
    layer's slot, and a pin holding them to the layer's slot alone failed on that tree. The run that
    fails under it is this one.

    One session, both carriers — a session the stores name as a dispatch's child, so the band's
    dispatcher fact is filled, beside the way back every session page carries: the page `tree
    --format html` writes and the page the dashboard serves. The two texts differ within the
    `<!--LAYER-->`'s slot alone — one template, one script, one band, one presentation — and the
    scripts each carrier loads draw the same moments: the file carrier's own script alone (a file
    cannot link the server's origin, so the deco the page names never loads there), the served
    carrier's own script and the deco in the order the page names them, the deco reading none."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    _write_store(
        project,
        ".profiler-opencode",
        "s-parent",
        "2026-01-01T00:00:00.000Z",
        harness="opencode",
        extra={"tool": "Agent", "name": "devpro-coder", "child_agent_id": "s-child"},
    )
    _write_store(project, ".profiler-opencode", "s-child", "2026-01-01T00:00:01.000Z", harness="opencode", records=2)
    launcher = _launcher(tmp_path / "harness")

    with _serve(launcher, cwd=project) as url:
        served = _fetch(f"{url}page/s-child")
    printed = _run(launcher, "tree", "s-child", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr

    # The band's per-page facts are the dump's too: the way back, and the dispatcher the stores name.
    assert "Dispatched by" in served and "Return to list" in served
    # The dump's page is the served page's text, the layer its only difference: the serve's link,
    # stood back as the render's inline text, is the dump's page — print's own newline aside.
    assert served.replace(LAYER_LINK, LAYER_INLINE) + "\n" == printed.stdout

    # And the scripts the carriers load draw the same page: the file carrier's script alone — a file
    # cannot link the server's origin — and the served carrier's own script with the deco it names,
    # in the order the page loads them.
    deco = (_PACKAGE_ROOT / "devpro" / "profiler" / "deco.js").read_text(encoding="utf-8")
    file_drawn = _page_runner(tmp_path, printed.stdout)
    serve_drawn = _page_runner(tmp_path, served, deco=deco)
    assert file_drawn["stamped"] == serve_drawn["stamped"], (file_drawn["stamped"], serve_drawn["stamped"])
    assert file_drawn["subline"] == serve_drawn["subline"]


def test_the_opencode_capture_records_every_fired_call(tmp_path: Path) -> None:
    """The shipped `profiler.ts` through a stub plugin context: a completed call, a failed one, a
    skill call, subagent dispatches and the session's idle each append their record; the failed call's
    text is its `Tool.Error`'s message, the skill and subagent carry the host's own names, a dispatch
    carries the kind its response reports or else its own agent, under either of the host's spellings
    for the tool, the child session its result names — in the metadata 2.3.0 reported, in the output
    2.3.2 reported, and at the result's top level 2.4.1 reports, each of which the floor covers — a
    top-level id that is not a string refused, the read falling through to the output's id — and the
    one call whose `execute.after` never fires drops its start at the idle."""
    project = tmp_path / "project"
    project.mkdir()
    run = _run_ts(_HERE / "profiler_capture_runner.ts", directory=project)
    out = json.loads(run.stdout)
    records = out["records"]

    calls = [record for record in records if record.get("event") is None]
    assert [(record["tool"], record["name"]) for record in calls] == [
        ("shell", "printf 'hi\\n'"),
        ("shell", "rm -rf /"),
        ("Skill", "profiler"),
        ("Agent", "devpro-python-coder"),
        ("Agent", "devpro-architect"),
        ("Agent", "devpro-tech-writer"),
        ("Agent", "devpro-go-coder"),
        ("Agent", "devpro-rust-coder"),
        ("Agent", "devpro-typescript-coder"),
    ]
    assert calls[0]["result"] == "hi"
    assert calls[1]["ok"] is False
    assert calls[1]["result"] == "The user rejected this tool call"
    assert calls[2]["result"] == "loaded"
    assert calls[3]["result"] is None
    assert calls[3]["child_agent_id"] == "ses_child"
    assert calls[3]["child_agent_type"] == "devpro-python-coder"
    assert calls[4]["child_agent_id"] == "ses_fork"
    assert calls[4]["child_agent_type"] == "devpro-architect"
    assert calls[5]["child_agent_id"] == "ses_task"
    assert calls[5]["child_agent_type"] == "devpro-tech-writer"
    # opencode 2.3.0's shape, the floor's: the id rides the result's metadata and a bare `output` string
    # refuses the preferred read, so the fallback is what names this child.
    assert calls[6]["result"] == "ses_floor"
    assert calls[6]["child_agent_id"] == "ses_floor"
    assert calls[6]["child_agent_type"] == "devpro-go-coder"
    # opencode 2.4.1's shape: the id at the result's top level alone, `output` a bare string carrying
    # no id. A read that stops at the output records `null` here, which is the defect this case pins.
    assert calls[7]["child_agent_id"] == "ses_top"
    assert calls[7]["child_agent_type"] == "devpro-rust-coder"
    # The top-level id is not a string: the guard refuses it and the read falls through to the
    # output's id. A read that takes the first arm on its presence alone records `null` here.
    assert calls[8]["child_agent_id"] == "ses_guard"
    assert calls[8]["child_agent_type"] == "devpro-typescript-coder"
    assert [record["event"] for record in records if record.get("event")] == ["experimental.idle"]
    assert (out["startedBeforeIdle"], out["startedAfterIdle"]) == (1, 0)


def test_a_line_over_the_bound_is_fitted_at_its_root(tmp_path: Path) -> None:
    """`serialize` holds every line to `LINE_LIMIT`, which the torn-tail read relies on: a record whose
    fixed `session` alone is longer than the bound is fitted by clipping that field too, and a line
    already inside the bound is left as it stands. The record measured is one the capture wrote, so the
    two bounds are the dispatch record's own field lengths."""
    line_limit = 4096
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    over = json.loads(
        _run_ts(
            _HERE / "profiler_serialize_runner.ts",
            directory=first,
            stdin=json.dumps({"directory": str(first), "sessionLength": 4090}),
        ).stdout
    )
    assert over["bytes"] <= line_limit
    assert over["session"] < 4090
    inside = json.loads(
        _run_ts(
            _HERE / "profiler_serialize_runner.ts",
            directory=second,
            stdin=json.dumps({"directory": str(second), "sessionLength": 200}),
        ).stdout
    )
    # A line inside the bound keeps its session whole: the field the over case clips is untouched here,
    # which is what says the runner measured the length it was given.
    assert inside["session"] == 200
    assert inside["bytes"] <= line_limit


def test_the_two_masks_redact_alike(tmp_path: Path) -> None:
    """The profiler's `mask` and the port's, over one sample list: each sample's masked text is the same on
    both sides, the non-ASCII credential included."""
    samples = (_HERE / _MASK_SAMPLES).read_text(encoding="utf-8").splitlines()
    run = _run_ts(_HERE / "profiler_mask_runner.ts", directory=tmp_path, arg=str(_HERE / _MASK_SAMPLES))
    ported = [json.loads(line) for line in run.stdout.splitlines()]

    assert ported == [mask(sample) for sample in samples]


def _profiler_init(project: Path) -> subprocess.CompletedProcess[str]:
    """`profiler init claude` in `project`, through its installed launcher and the test's devpro."""
    return _run(_launcher(project.parent / "harness"), "init", "claude", cwd=project)


def test_init_lays_down_the_launcher_and_clears_an_older_runs_files(tmp_path: Path) -> None:
    """A committed hook directory holding an older `init`'s launcher `hp.sh` beside `hp.py` and
    `view.html`: a re-run writes the launcher alone and removes the older names. A committed hook
    running devpro beside a stale `hp.py` is the half-absorbed install, and `stale_hook` would chase
    files no install ships."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    hook_dir = project / ".claude" / "harness-profiler"
    hook_dir.mkdir(parents=True)
    for name in ("hp.sh", *RETIRED_HOOK_FILES):
        (hook_dir / name).write_text("an older init's copy\n", encoding="utf-8")

    done = _profiler_init(project)

    assert done.returncode == 0, done.stderr
    assert [path.name for path in sorted(hook_dir.iterdir())] == ["profiler.sh"]
    assert (hook_dir / "profiler.sh").read_bytes() == launcher_resource().read_bytes()
    assert os.access(hook_dir / "profiler.sh", os.X_OK)
    assert (project / ".claude" / "skills" / "profiler" / "SKILL.md").is_file()
    assert "harness-profiler/profiler.sh" in (project / ".claude" / "settings.json").read_text(encoding="utf-8")


def test_init_renames_a_committed_hook_written_under_the_former_launcher_name(tmp_path: Path) -> None:
    """A repository whose committed hook spells the launcher's former name — the file `hp.sh` and the
    registered command running it: `init` renames both, the file unlinked and the current launcher
    written in its place, the command re-registered under the current name, and `doctor` no longer
    reports the hook as stale. The rename's consuming-project migration is the `init`'s, run before
    the install refreshes."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    hook_dir = project / ".claude" / "harness-profiler"
    hook_dir.mkdir(parents=True)
    (hook_dir / "hp.sh").write_text("an older init's copy\n", encoding="utf-8")
    settings_file = project / ".claude" / "settings.json"
    old_entry = {
        "hooks": {
            event: [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": '/bin/bash "$CLAUDE_PROJECT_DIR/.claude/harness-profiler/hp.sh" capture claude',
                            "timeout": 5,
                            "async": True,
                        }
                    ],
                }
            ]
            for event in CAPTURED_EVENTS
        }
    }
    settings_file.write_text(json.dumps(old_entry, indent=2) + "\n", encoding="utf-8")

    done = _profiler_init(project)
    doctor = _run(_launcher(tmp_path / "harness"), "doctor", cwd=project)

    assert done.returncode == 0, done.stderr
    assert [path.name for path in sorted(hook_dir.iterdir())] == ["profiler.sh"]
    settings = settings_file.read_text(encoding="utf-8")
    assert "harness-profiler/profiler.sh" in settings
    assert "harness-profiler/hp.sh" not in settings
    assert doctor.returncode == 0, doctor.stderr
    assert "update:" not in doctor.stdout
    assert "committed hooks" in doctor.stdout


@pytest.mark.parametrize("beside", [[], ["notes.md"]], ids=["alone", "beside-a-file"])
def test_init_removes_the_skill_an_older_init_rendered_under_its_former_name(tmp_path: Path, beside: list[str]) -> None:
    """A repository holding a committed `.claude/skills/show-profile/SKILL.md`, the skill under its name
    before `profiler`: a re-run removes it, and its directory where nothing else is left in it, and the
    `git add` line it prints stages that removal. Without the unlink the older skill stands beside the
    renamed one, two skills answering the same request; without the path in the printed line, following
    it commits the new skill and leaves the old one in the repository."""
    project = tmp_path / "project"
    project.mkdir()
    git = ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false"]
    subprocess.run([*git, "init", "-q"], cwd=project, check=True)
    retired = project / ".claude" / "skills" / "show-profile"
    retired.mkdir(parents=True)
    for name in ("SKILL.md", *beside):
        (retired / name).write_text("an older init's copy\n", encoding="utf-8")
    subprocess.run([*git, "add", "."], cwd=project, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "an older init"], cwd=project, check=True)

    done = _profiler_init(project)

    assert done.returncode == 0, done.stderr
    assert not (retired / "SKILL.md").exists()
    assert retired.is_dir() is bool(beside)
    assert all((retired / name).is_file() for name in beside)
    assert (project / ".claude" / "skills" / "profiler" / "SKILL.md").is_file()
    add_line = next(line.strip() for line in done.stdout.splitlines() if line.strip().startswith("git add "))
    subprocess.run(shlex.split(add_line), cwd=project, check=True)
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-status"], cwd=project, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    assert "D\t.claude/skills/show-profile/SKILL.md" in staged


def test_a_rename_leaves_a_directory_that_is_no_profiler_store_alone(tmp_path: Path) -> None:
    """A project holding `.devpro-temp/notes-profiler/`, a directory named after an operator's own tool:
    the install leaves it where it stands, its contents and all. Claude Code's own convention puts a
    `-profiler` suffix on a directory, so a rename reading the suffix alone takes an operator's directory
    for a store."""
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    their_own = project / ".devpro-temp" / "notes-profiler"
    their_own.mkdir(parents=True)
    (their_own / "readme.txt").write_text("an operator's own notes\n", encoding="utf-8")

    installed = _install_project(project)

    assert installed.returncode == 0, installed.stderr
    assert sorted(path.name for path in (project / ".devpro-temp").iterdir()) == ["notes-profiler"]
    assert (their_own / "readme.txt").read_text(encoding="utf-8") == "an operator's own notes\n"


def test_a_plain_install_renames_the_stores_once_with_no_wrapper(tmp_path: Path) -> None:
    """`devpro install` on its one-harness branch — `install` called straight, no preflight and no stored
    migration passed: its own call renames the project's old-pattern store and names the move, and a
    second install of the same project renames nothing. A plain call renaming on every run renames on
    every run, and a caller passing no wrapper reaches the operator's directories unguarded — the
    incident this rule exists for."""
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    claude = _write_store(project, "claude-profiler", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    first, second = _install_project(project), _install_project(project)

    stores = project / ".devpro-temp"
    assert sorted(path.name for path in stores.iterdir()) == [".profiler-claude"]
    assert f"renamed {claude} → {stores / '.profiler-claude'}" in first.stdout
    assert "renamed " not in second.stdout + second.stderr


def test_init_renames_the_repositorys_old_pattern_stores(tmp_path: Path) -> None:
    """A repository holding `.devpro-temp/claude-profiler/` and `.devpro-temp/opencode-profiler/`:
    `init` moves each to its `.profiler-*` name and names it, the same migration an install runs. A
    committed-hook repository that migrates nowhere goes dark the moment its hook records on."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    claude = _write_store(project, "claude-profiler", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")
    opencode = _write_store(project, "opencode-profiler", "s-opencode", "2026-01-01T00:00:00.000Z", harness="opencode")

    done = _profiler_init(project)

    assert done.returncode == 0, done.stderr
    stores = project / ".devpro-temp"
    assert sorted(path.name for path in stores.iterdir()) == [".profiler-claude", ".profiler-opencode"]
    assert f"renamed {claude} → {stores / '.profiler-claude'}" in done.stdout
    assert f"renamed {opencode} → {stores / '.profiler-opencode'}" in done.stdout
    assert sorted(path.name for path in (stores / ".profiler-opencode").iterdir()) == ["s-opencode.jsonl"]


def test_doctor_reports_a_committed_launcher_that_differs_from_the_resource(tmp_path: Path) -> None:
    """A committed hook this devpro's `init` wrote, its launcher then edited: `doctor` says the hook has
    another version of it. A compare reading a source no install ships reports nothing, and the `update`
    line loses its one job."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    assert _profiler_init(project).returncode == 0
    current = _run(_launcher(tmp_path / "harness"), "doctor", cwd=project)
    assert current.returncode == 0, current.stderr
    assert "update:" not in current.stdout

    (project / ".claude" / "harness-profiler" / "profiler.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

    edited = _run(_launcher(tmp_path / "harness"), "doctor", cwd=project)

    assert edited.returncode == 0, edited.stderr
    assert "update:  the committed hook has another version of profiler.sh;" in edited.stdout


@pytest.mark.parametrize("wrapper", [".claude/tools/devpro.sh", ".claude/skills/devpro/tools/devpro.sh"])
def test_doctor_names_the_wrapper_the_launcher_would_run(tmp_path: Path, wrapper: str) -> None:
    """`clauses.TEST_PRECONDITION`. Doctor's `devpro:` line models the launcher's own resolution: the
    first wrapper candidate standing beside the launcher, named without running it — whether the
    wrapper runs is the wrapper's own refusal to name at hook time, there being no probe. The defect
    the stand-in's rule guards: a line naming a devpro the launcher does not run."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    assert _profiler_init(project).returncode == 0
    broken = project / wrapper
    broken.parent.mkdir(parents=True, exist_ok=True)
    broken.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    broken.chmod(0o755)

    reported = _run(_launcher(tmp_path / "harness"), "doctor", cwd=project)

    assert reported.returncode == 0, reported.stderr
    [line] = [line for line in reported.stdout.splitlines() if line.startswith("devpro:")]
    assert str(broken) in line
    assert "does not run" not in line


def test_doctor_names_no_devpro_the_launcher_would_not_run(tmp_path: Path) -> None:
    """No wrapper stands beside either launcher, and a `devpro` waits on PATH: doctor's line names the
    absence — the launcher's capture exits 0 without recording — never the PATH command, there being
    no PATH search for the stand-in to model."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    assert _profiler_init(project).returncode == 0
    for wrapper in (
        project / ".claude" / "tools" / "devpro.sh",
        project / ".claude" / "skills" / "devpro" / "tools" / "devpro.sh",
    ):
        wrapper.unlink(missing_ok=True)
    on_path = tmp_path / "on-path"
    on_path.mkdir()
    foreign = on_path / "devpro"
    foreign.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    foreign.chmod(0o755)

    reported = _run(_launcher(tmp_path / "harness"), "doctor", cwd=project, path=f"{on_path}:/usr/bin:/bin")

    assert reported.returncode == 0, reported.stderr
    [line] = [line for line in reported.stdout.splitlines() if line.startswith("devpro:")]
    assert str(foreign) not in reported.stdout
    assert "no wrapper beside it" in line


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
                    "v": 2,
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


def test_the_served_index_lists_every_recorded_session(tmp_path: Path) -> None:
    """A store in each harness's directory and a session of several records under one project: the
    served index's feed carries an entry for every recorded session, each stating the harness and the
    count its own records hold and its first and last moment as epoch milliseconds, and its span in
    seconds; a feed that omits a session the stores hold, or states one the store does not, drops or
    invents what the records say.

    A session whose opencode record names a child session is its dispatcher: the child's entry
    carries `dispatcher`, the dispatching session's id and the dispatching call's name, and follows
    its dispatcher's in the feed — the order the index draws the rows in, a child under its
    dispatcher. The index's page file is static: no row is in its text, and its script renders them
    from this feed, which `test_the_index_renders_the_rows_the_feed_answers` drives."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    _write_store(project, ".profiler-opencode", "s-opencode", "2026-01-01T00:00:05.000Z", harness="opencode")
    _write_store(
        project,
        ".profiler-opencode",
        "s-dispatcher",
        "2026-01-01T00:00:06.000Z",
        harness="opencode",
        records=1,
        extra={"tool": "Agent", "name": "devpro-coder", "child_agent_id": "s-child"},
    )
    _write_store(project, ".profiler-opencode", "s-child", "2026-01-01T00:00:07.000Z", harness="opencode", records=2)

    with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        feed = json.loads(_fetch(f"{url}api/traces"))
        page = _fetch(f"{url}page/s-claude")

    assert feed == [
        {
            "harness": "claude",
            "id": "s-claude",
            "records": 2,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:00.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:01.000Z"),
            "span": 1,
        },
        {
            "harness": "opencode",
            "id": "s-opencode",
            "records": 1,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:05.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:05.000Z"),
            "span": 0,
        },
        {
            "harness": "opencode",
            "id": "s-dispatcher",
            "records": 1,
            "agents": 1,
            "first": _epoch_ms("2026-01-01T00:00:06.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:06.000Z"),
            "span": 0,
        },
        {
            "harness": "opencode",
            "id": "s-child",
            "records": 2,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:07.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:08.000Z"),
            "span": 1,
            "dispatcher": {"session": "s-dispatcher", "name": "devpro-coder"},
        },
    ]
    # The page file is static: the rows' empty table, no session's row, and every column heading a
    # row states, each harness's mark, and the zebra's one rule — the layer's `--zebra`, which the
    # layer switches with the color scheme itself, so the template carries no second rule for it.
    assert '<tbody id="rows"></tbody>' in index and 'href="/page/' not in index
    assert re.search(
        r'<th class="col-harness">harness</th><th class="col-session">session</th>'
        r'<th class="col-records" aria-sort="none"><button type="button" class="sort" data-sort="records">'
        r'records</button></th><th class="col-agents" aria-sort="none"><button type="button" class="sort" '
        r'data-sort="agents">dispatched agents</button></th><th class="col-one" aria-sort="none">'
        r'<button type="button" class="sort" data-sort="first">first to last</button></th>'
        r'<th class="col-span" aria-sort="none"><button type="button" class="sort" data-sort="span">'
        r"span</button></th>",
        index,
    )
    # Each column's share of the table comes from the page's own stylesheet, beside the header's class,
    # and the table's layout is the fixed one that gives that share to header and body alike.
    assert re.search(r"table \{ border-collapse: collapse; table-layout: fixed; \}", index)
    for column in ("col-harness", "col-session", "col-records", "col-agents", "col-one", "col-span"):
        assert re.search(rf"\.{column} \{{ width: [\d.]+(?:rem|%); \}}", index), column
    # The controls: a box for the child rows and one per harness, each checked so the page opens on
    # every row, and the notice a failed feed names itself in, standing empty and hidden.
    for control in ('id="child-rows"', 'id="harness-claude"', 'id="harness-opencode"'):
        assert re.search(rf'<input type="checkbox" {control} [^>]*checked>', index), control
    assert re.search(r'<p id="notice" class="notice" role="alert" hidden></p>', index)
    assert re.search(r"tr:nth-child\(odd\) td \{ background: var\(--zebra\); \}", index)
    assert "prefers-color-scheme: dark" not in index.split("<style>", 1)[1].split("</style>", 1)[0]
    assert re.search(r"\.harness\.opencode \{ background: #4a9eea; \}", index)
    assert re.search(r"\.harness\.claude \{ background: #d97757; \}", index)
    assert _page_data(page)["session"] == "s-claude"


def test_the_index_renders_the_rows_the_feed_answers(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a static index with no rows and a `/api/traces`
    answering an empty list, which passes every test the rework began from — each read the rows out of
    a page the server assembled. The run that fails under it is this one: the served page's script,
    over the feed's JSON, draws the same `<tr>` order the server-assembled index had — each session
    once, in first-moment order, a dispatched child under its dispatcher — and reads exactly the
    schema's keys, those the feed builder's entry carries and no others. A script reading a second
    shape, or a feed answering one, is a row drawn from a key nothing states."""
    project = tmp_path / "project"
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    _write_store(project, ".profiler-opencode", "s-p1", "2026-01-01T00:00:05.000Z", harness="opencode")
    _write_store(
        project,
        ".profiler-opencode",
        "s-p2",
        "2026-01-01T00:00:06.000Z",
        harness="opencode",
        extra={"tool": "Agent", "name": "devpro-coder", "child_agent_id": "s-child"},
    )
    _write_store(project, ".profiler-opencode", "s-child", "2026-01-01T00:00:07.000Z", harness="opencode", records=2)

    with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        feed = _fetch(f"{url}api/traces")
    run = _run_ts(
        _HERE / "profiler_index_runner.ts",
        directory=tmp_path,
        stdin=json.dumps({"index": index, "feed": json.loads(feed)}),
    )
    drawn = json.loads(run.stdout)

    assert [re.search(r'href="/page/([^"]+)"', row).group(1) for row in drawn["rows"]] == [
        "s-claude",
        "s-p1",
        "s-p2",
        "s-child",
    ]
    assert "claude" in drawn["rows"][0] and "2 records" in drawn["rows"][0]
    assert "1 dispatched agent" in drawn["rows"][2]
    assert 'class="col-session child"' in drawn["rows"][3] and "↳ child — devpro-coder" in drawn["rows"][3]
    # The dispatched-agent count is the entry's own, and the row carries no second copy of it: a
    # `data-agents` attribute beside the feed's key is the one the script's sort would read had the
    # entry not carried it.
    assert "data-agents" not in "".join(drawn["rows"])
    # The keys the script reads are the schema's: a session entry's seven, the dispatcher pair, an
    # unreadable store's one, and the `{stores}` marker's one — no key the feed builder does not
    # write, and none it writes unread.
    assert set(drawn["keys"]) == {
        "harness",
        "id",
        "records",
        "agents",
        "first",
        "last",
        "span",
        "dispatcher",
        "session",
        "name",
        "unreadable",
        "stores",
    }
    assert drawn["fetches"] == ["/api/traces"]

    # The span's own rendering, at every scale the server-side span test covered — seconds below a
    # minute, minutes alone, and the hour forms — fed the runner a crafted feed so the scale is known
    # by construction; the table's own empty reading is asserted below, where its three distinctions
    # are driven.
    crafted = [
        {"harness": "claude", "id": "s-59", "records": 1, "first": 0, "last": 0, "span": 59},
        {"harness": "claude", "id": "s-90", "records": 1, "first": 0, "last": 0, "span": 90},
        {"harness": "claude", "id": "s-120", "records": 1, "first": 0, "last": 0, "span": 120},
        {"harness": "claude", "id": "s-3600", "records": 1, "first": 0, "last": 0, "span": 3600},
        {"harness": "claude", "id": "s-5400", "records": 1, "first": 0, "last": 0, "span": 5400},
    ]
    run = _run_ts(
        _HERE / "profiler_index_runner.ts",
        directory=tmp_path,
        stdin=json.dumps({"index": index, "feed": crafted}),
    )
    drawn = json.loads(run.stdout)
    # Every crafted entry draws a row: a zip that silently paired fewer rows would pass with the
    # scale never checked, so the count is stated before the pairing, and each row's span is asserted
    # where the table puts it — the row's last cell — so a span cell moved a column or a row drawn out
    # of order fails rather than satisfying a substring's somewhere.
    assert len(drawn["rows"]) == len(crafted)
    for row, reading in zip(drawn["rows"], ("59s", "1m 30s", "2m", "1h", "1h 30m")):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        assert cells[-1] == reading, f"{reading!r} not the last cell of {row}"

    # The table's own empty reading makes three distinctions: a feed holding sessions the controls
    # hid, a feed whose stores stand but hold no record to draw, and a feed from a tree with no store
    # at all — an empty feed being no store found, since a store the server reads answers a session
    # entry or an `{unreadable}` one, and the stores it finds but holds no record for answer neither.
    def empty_reading(feed_in: list[dict], actions: list[dict]) -> str:
        run = _run_ts(
            _HERE / "profiler_index_runner.ts",
            directory=tmp_path,
            stdin=json.dumps({"index": index, "feed": feed_in, "actions": actions}),
        )
        rows = json.loads(run.stdout)["rows"]
        assert len(rows) == 1, rows
        return rows[0]

    assert "No session store found yet" in empty_reading([{"stores": 0}], [])
    assert "No sessions recorded yet" in empty_reading([{"stores": 2}], [])
    pair = [
        {"harness": "opencode", "id": "s-p", "records": 1, "agents": 1, "first": 0, "last": 0, "span": 0},
        {
            "harness": "opencode",
            "id": "s-kid",
            "records": 1,
            "agents": 0,
            "first": 0,
            "last": 0,
            "span": 0,
            "dispatcher": {"session": "s-p", "name": "x"},
        },
    ]
    assert "No sessions shown" in empty_reading(pair, [{"toggle": "child-rows"}, {"toggle": "harness-opencode"}])
    # The feed a served tree with stores but no record answers is one `{stores: <count>}` entry, and
    # the key it reads is the schema's own.
    served_empty = json.loads(
        _run_ts(
            _HERE / "profiler_index_runner.ts",
            directory=tmp_path,
            stdin=json.dumps({"index": index, "feed": [{"stores": 2}]}),
        ).stdout
    )
    assert served_empty["keys"] == ["stores", "unreadable"] and "No sessions recorded yet" in served_empty["rows"][0]

    # The controls, driven over the same served page: the child-rows box takes the dispatched rows out
    # and leaves their dispatcher, naming the agents the feed holds; a harness's box takes its own
    # sessions out; and a column head sorts the rows on its column — ascending on the first press and
    # descending on the second — the dispatcher's children following it as they always do.

    def driven(feed_in: list[dict], actions: list[dict]) -> list[str]:
        run = _run_ts(
            _HERE / "profiler_index_runner.ts",
            directory=tmp_path,
            stdin=json.dumps({"index": index, "feed": feed_in, "actions": actions}),
        )
        return json.loads(run.stdout)["rows"]

    # A row's session id, in the order the rows stand; a full-width store row carries no link.
    def ids(rows: list[str]) -> list[str]:
        return [match.group(1) for row in rows if (match := re.search(r'href="/page/([^"]+)"', row))]

    hidden_children = driven(json.loads(feed), [{"toggle": "child-rows"}])
    assert ids(hidden_children) == ["s-claude", "s-p1", "s-p2"]
    assert any("1 dispatched agent" in row for row in hidden_children)
    assert ids(driven(json.loads(feed), [{"toggle": "harness-opencode"}])) == ["s-claude"]
    assert ids(driven(json.loads(feed), [{"toggle": "harness-claude"}])) == ["s-p1", "s-p2", "s-child"]
    # A harness the controls carry no box for — a hand-written store's name — is drawn, and the page
    # reports no failure: a feed that answered is not reported as one that could not be read, and a
    # box other than the feed's own harnesses hides nothing.
    stranger = [
        {"harness": "mage", "id": "s-mage", "records": 1, "agents": 0, "first": 0, "last": 0, "span": 0},
        {"harness": "claude", "id": "s-claude", "records": 1, "agents": 0, "first": 1, "last": 1, "span": 0},
    ]
    run = _run_ts(
        _HERE / "profiler_index_runner.ts",
        directory=tmp_path,
        stdin=json.dumps({"index": index, "feed": stranger}),
    )
    unboxed = json.loads(run.stdout)
    assert ids(unboxed["rows"]) == ["s-mage", "s-claude"] and unboxed["notices"] == []
    # The control state is honest for the pair that hides nothing: the feed holds no opencode session,
    # so its box is disabled rather than checked while filtering nothing.
    assert unboxed["controls"] == {
        "child-rows": {"checked": True, "disabled": False},
        "harness-claude": {"checked": True, "disabled": False},
        "harness-opencode": {"checked": True, "disabled": True},
    }
    # R6: a child whose dispatcher its harness's box hides is drawn at its dispatcher's level — an
    # orphan promoted, not a row drawn nowhere. An opencode dispatch records a claude child; with
    # opencode off the dispatcher is hidden, and its claude child, whose own box is on, stands.
    orphan = [
        {"harness": "opencode", "id": "s-parent", "records": 1, "agents": 1, "first": 0, "last": 0, "span": 0},
        {
            "harness": "claude",
            "id": "s-orphan",
            "records": 1,
            "agents": 0,
            "first": 1,
            "last": 1,
            "span": 0,
            "dispatcher": {"session": "s-parent", "name": "x"},
        },
    ]
    assert ids(driven(orphan, [])) == ["s-parent", "s-orphan"]
    assert ids(driven(orphan, [{"toggle": "harness-opencode"}])) == ["s-orphan"]
    # One feed in a known first-moment order, drawn in it: the records, the first moment and the span
    # each order the rows differently, so a sort that reads no key leaves the feed's own order.
    by_first = [
        {"harness": "opencode", "id": "s-late", "records": 3, "first": 30, "last": 40, "span": 10},
        {"harness": "claude", "id": "s-early", "records": 1, "first": 10, "last": 20, "span": 40},
        {"harness": "opencode", "id": "s-mid", "records": 2, "first": 20, "last": 30, "span": 20},
    ]
    assert ids(driven(by_first, [])) == ["s-late", "s-early", "s-mid"]
    assert ids(driven(by_first, [{"sort": "records"}])) == ["s-early", "s-mid", "s-late"]
    assert ids(driven(by_first, [{"sort": "records"}, {"sort": "records"}])) == ["s-late", "s-mid", "s-early"]
    assert ids(driven(by_first, [{"sort": "first"}])) == ["s-early", "s-mid", "s-late"]
    assert ids(driven(by_first, [{"sort": "span"}])) == ["s-late", "s-mid", "s-early"]
    # The arrow the reader sees is the head's `aria-sort`: ascending on the first press, descending on
    # the second, and every other head back to none, so the table says which order it stands in.

    def sorts_state(actions: list[dict]) -> list[list[str]]:
        run = _run_ts(
            _HERE / "profiler_index_runner.ts",
            directory=tmp_path,
            stdin=json.dumps({"index": index, "feed": by_first, "actions": actions}),
        )
        return json.loads(run.stdout)["sorts"]

    assert sorts_state([]) == [["records", "none"], ["agents", "none"], ["first", "none"], ["span", "none"]]
    assert sorts_state([{"sort": "span"}]) == [
        ["records", "none"],
        ["agents", "none"],
        ["first", "none"],
        ["span", "ascending"],
    ]
    assert sorts_state([{"sort": "span"}, {"sort": "span"}]) == [
        ["records", "none"],
        ["agents", "none"],
        ["first", "none"],
        ["span", "descending"],
    ]
    # The dispatched-agent count sorts on the entry's own `agents`, the count of the children the feed
    # holds: two dispatchers of different counts order the rows by it, the feed's order being neither
    # the ascending nor the descending one, so a head reading a key no entry carries leaves the order
    # it opened in. `by_first` holds no dispatcher, so its ties are the all-zero sort's own case.
    by_agents = [
        {"harness": "opencode", "id": "s-two", "records": 1, "agents": 2, "first": 30, "last": 40, "span": 10},
        {"harness": "opencode", "id": "s-none", "records": 1, "agents": 0, "first": 10, "last": 20, "span": 10},
        {"harness": "opencode", "id": "s-five", "records": 1, "agents": 5, "first": 20, "last": 30, "span": 10},
    ]
    assert ids(driven(by_agents, [])) == ["s-two", "s-none", "s-five"]
    assert ids(driven(by_agents, [{"sort": "agents"}])) == ["s-none", "s-two", "s-five"]
    assert ids(driven(by_agents, [{"sort": "agents"}, {"sort": "agents"}])) == ["s-five", "s-two", "s-none"]

    # The dispatched-agent count sorts on a dispatcher's children, which `by_first` holds none of: the
    # head sorts, and its ties keep the feed's order.
    assert ids(driven(by_first, [{"sort": "agents"}])) == ["s-late", "s-early", "s-mid"]

    # A feed that fails names itself: the page's own composed message, from the feed's status, and
    # draws no row — the no-records reading standing for a feed that answered with nothing to draw,
    # not one that answered nothing at all. The notice is hidden and empty before the failure, so the
    # notice the reader sees is the one this failure raised.
    run = _run_ts(
        _HERE / "profiler_index_runner.ts",
        directory=tmp_path,
        stdin=json.dumps({"index": index, "feed": [], "actions": [{"fail": {"status": 503}}]}),
    )
    failed = json.loads(run.stdout)
    assert failed["before"] == {"hidden": True, "text": "", "rows": []}
    assert failed["rows"] == []
    assert failed["notices"] == ["The traces feed could not be read: HTTP 503."]
    run = _run_ts(
        _HERE / "profiler_index_runner.ts",
        directory=tmp_path,
        stdin=json.dumps({"index": index, "feed": [], "actions": [{"fail": {"status": 200, "body": [{"stores": 0}]}}]}),
    )
    failed = json.loads(run.stdout)
    assert failed["notices"] == [] and "No session store found yet" in failed["rows"][0]


def test_a_session_naming_itself_as_a_child_is_drawn_once_in_its_own_place(tmp_path: Path) -> None:
    """A session whose own opencode record carries its own id as `child_agent_id`: the feed draws it
    once, top-level, its entry carrying no `dispatcher`. A grouping that reads the self-naming as a
    dispatch drops the session from the index's top level and draws it under itself, its count
    naming a row for a session that dispatched nothing."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(
        project,
        ".profiler-opencode",
        "s-self",
        "2026-01-01T00:00:00.000Z",
        harness="opencode",
        records=1,
        extra={"tool": "Agent", "name": "devpro-coder", "child_agent_id": "s-self"},
    )

    with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
        feed = json.loads(_fetch(f"{url}api/traces"))

    assert [entry["id"] for entry in feed] == ["s-self"]
    assert "dispatcher" not in feed[0]


def test_a_claude_child_agent_id_groups_no_session(tmp_path: Path) -> None:
    """A claude store whose record's `child_agent_id` equals another session's id: the feed draws that
    session as a stranger, top-level, its entry carrying no `dispatcher`, and the claude page's call
    renders its name with no child-page link. Claude's `child_agent_id` is an agent id, and claude
    records its subagents' calls in the parent's file — grouping on it draws a page no session stands
    behind."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(
        project,
        ".profiler-claude",
        "s-claude",
        "2026-01-01T00:00:00.000Z",
        harness="claude",
        records=1,
        extra={"tool": "Agent", "name": "devpro-coder", "child_agent_id": "s-named"},
    )
    _write_store(project, ".profiler-claude", "s-named", "2026-01-01T00:00:05.000Z", harness="claude")

    with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
        feed = json.loads(_fetch(f"{url}api/traces"))
        page = _fetch(f"{url}page/s-claude")

    assert [entry["id"] for entry in feed] == ["s-claude", "s-named"]
    assert not any("dispatcher" in entry for entry in feed)
    assert _page_data(page)["calls"][0]["child"] == "s-named"
    assert _page_data(page)["calls"][0]["childPage"] is None


def test_the_served_index_lists_its_own_project_under_a_foreign_project_dir(tmp_path: Path) -> None:
    """`CLAUDE_PROJECT_DIR` at another project, as a claude shell sets it, while the dashboard runs in
    this one: the feed lists this project's sessions; a feed that follows the variable serves the
    other project's stores, which for a terminal-launched server is the wrong repository."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-here", "2026-01-01T00:00:00.000Z", harness="claude")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    _write_store(foreign, ".profiler-claude", "s-elsewhere", "2026-01-01T00:00:00.000Z", harness="claude")

    with _serve(_launcher(tmp_path / "harness"), cwd=project, env={"CLAUDE_PROJECT_DIR": str(foreign)}) as url:
        feed = json.loads(_fetch(f"{url}api/traces"))

    assert [entry["id"] for entry in feed] == ["s-here"]


def test_the_served_feed_states_an_unreadable_store(tmp_path: Path) -> None:
    """One `.profiler-*` store the glob finds and cannot read, beside one it can: the feed answers
    2xx, names the unreadable store as such, and still lists the readable store's session, and the
    unreadable store's own page is a 404 rather than a traceback; a feed that lets the one bad
    directory blank it or raise out of the handler is the defect the stated entry replaces."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    locked = _write_store(project, ".profiler-broken", "s-broken", "2026-01-01T00:00:00.000Z", harness="claude")
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")
    os.chmod(locked, 0o000)
    try:
        with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
            feed = json.loads(_fetch(f"{url}api/traces"))
            with pytest.raises(urllib.error.HTTPError) as missing:
                _fetch(f"{url}page/s-broken")
    finally:
        os.chmod(locked, 0o755)

    assert feed == [
        {
            "harness": "claude",
            "id": "s-claude",
            "records": 1,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:00.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:00.000Z"),
            "span": 0,
        },
        {"unreadable": ".profiler-broken"},
    ]
    assert missing.value.code == 404


def test_the_served_page_is_the_html_the_file_flow_writes(tmp_path: Path) -> None:
    """One session's `/page/<id>` carries the file flow's page data: the JSON the page template
    inlines at its data slot is the payload `tree --format html` inlines, and the served page names
    the shared layer's one file where the render inlines its text — the two carriers' one difference,
    which the one-rendering pin holds to (`test_the_pages_two_carriers_differ_in_the_layers_slot_alone`,
    where the band's per-page facts and the drawn moments bite too)."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    launcher = _launcher(tmp_path / "harness")

    with _serve(launcher, cwd=project) as url:
        served = _fetch(f"{url}page/s-claude")

    printed = _run(launcher, "tree", "s-claude", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr
    assert _page_data(served) == _page_data(printed.stdout)
    # The serve path names the layer's one file where the file flow inlines its text: one source, two
    # carriers.
    assert served.count(LAYER_LINK) == 1 and SHARED_CSS not in served


def test_the_standalone_render_carries_the_shared_layer_and_the_legend_once(tmp_path: Path) -> None:
    """The page `tree --format html` prints carries the presentation layer's own text, inlined whole,
    and the frame band's legend exactly once — the deco the served page carries as its own text,
    here the render's: the standalone page names no view active to a live dashboard, so its band
    heads with the legend alone, no dispatcher and no way back. A render that inlines a second layer,
    or carries the legend twice, is the reskin the shared layer forbids."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")
    launcher = _launcher(tmp_path / "harness")

    printed = _run(launcher, "tree", "s-claude", "--format", "html", cwd=project)

    assert printed.returncode == 0, printed.stderr
    assert SHARED_CSS in printed.stdout
    assert printed.stdout.count("How to read this") == 1
    assert 'class="site-nav' in printed.stdout and 'class="frame-band' in printed.stdout


# The form a page script's body opens with: an IIFE, its body inside and its helpers private to it —
# the arrow the index's script and the deco use, the `function` spelling an equivalent.
_IIFE_OPENINGS = ("(() => {", "(function () {")


def _inline_script_bodies(page: str) -> list[str]:
    """`page`'s inline script bodies, in order: each between its `<script>` tag and its close, a tag
    naming a `src` loading a file and carrying no body."""
    return re.findall(r"<script>(.*?)</script>", page, re.DOTALL)


def _opens_an_iife(body: str) -> bool:
    """Whether `body`'s first statement opens an IIFE, a leading `'use strict';` directive and the
    comments ahead of it passed over."""
    for line in body.splitlines():
        statement = line.strip()
        if not statement or statement.startswith("//") or statement == "'use strict';":
            continue
        return statement in _IIFE_OPENINGS
    return False


def test_every_page_script_wraps_its_body_in_an_iife() -> None:
    """`clauses.TEST_PRECONDITION`. The defect: `view.html`'s script stood at the page's top level,
    its helpers — `padTwo`, `localDay`, `localClock` — in the global scope classic scripts share with
    the deco's, so the next helper of one of those names would redeclare a `const` and the session
    page would draw nothing. Every script the pages run wraps its body in an IIFE; the shipped pages
    carrying an inline script are `view.html` and the `INDEX` template."""
    pages = {
        "view.html": (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8"),
        "INDEX": INDEX,
    }
    for name, page in pages.items():
        bodies = _inline_script_bodies(page)
        assert bodies, f"{name} carries no inline script"
        assert all(_opens_an_iife(body) for body in bodies), f"{name}'s script does not open an IIFE"


# A session id as a host records one — opencode's own is about this long, and an id this wide is a
# column the page's header must cover.
_LONG_SESSION = "ses_60a1b2c3d4e5f60718293a4b5c6d7e8f0a1b2c3d4e5f60718293a4b5c6d7e8f"


def _browser(tmp_path: Path, index: str, feed: list[dict], actions: list[dict]) -> dict:
    """The served index in a browser's own shape (`profiler_browser_runner.ts`): its scripts run over a
    document at `index`'s own markup, laid out the way a browser lays a table out, with the reader's
    presses and visits in order."""
    run = _run_ts(
        _HERE / "profiler_browser_runner.ts",
        directory=tmp_path,
        stdin=json.dumps(
            {
                "index": index,
                "deco": (_PACKAGE_ROOT / "devpro" / "profiler" / "deco.js").read_text(encoding="utf-8"),
                "feed": feed,
                "actions": actions,
            }
        ),
    )
    return json.loads(run.stdout)


def test_the_headers_sit_over_their_columns(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: a page whose header row does not share its columns' widths is a
    header over the wrong column, and no test that reads the markup alone can fail on it.

    The served index, drawn over a session id as long as a host's own: the table is laid out fixed,
    one width per column, and a column's width is the one the stylesheet declares for the class its
    header cell and its body's cells carry. The header row and the body's rows take their widths from
    that one source, so the session id's column — the table's widest — stands as wide as its rule
    declares and the header over it stands in it. On a template that leaves a header's column
    undeclared, the header falls back to its own label's width while the body's cell takes its
    class's, and the reader looking down that column reads the header of the column beside it."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(
        project, ".profiler-opencode", _LONG_SESSION, "2026-01-01T00:00:00.000Z", harness="opencode", records=2
    )
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:05.000Z", harness="claude")

    with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        feed = json.loads(_fetch(f"{url}api/traces"))

    drawn = _browser(tmp_path, index, feed, [])
    assert len(drawn["headers"]) == 6, drawn["headers"]
    assert _LONG_SESSION in drawn["sessionCells"], drawn["sessionCells"]
    # A session id is wide: its column is the widest in the table. The header row and the body's rows
    # take their widths from the class each cell carries, one declared rule per column, so every
    # header's box is its column's box. A header whose class declares no width falls back to its own
    # label while the cell beneath takes its class's, and the reader following the header down lands
    # one column off the ids.
    headers = {label: (column, header) for label, column, header in drawn["headers"]}
    for label, (column, header) in headers.items():
        assert header == column, f"{label!r}'s header is {header} over a column of {column}"


def test_the_url_restores_the_controls_and_sort(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a page that keeps its controls' state and its sort in
    the document alone, so the state a reader chose is gone the moment they leave the view and come
    back through the page's own link — a page that cannot be bookmarked or shared in the reading it
    shows. The run that fails under it is this one: a control toggled off and a column head pressed
    leave the page's URL naming them, and the page opened again at that URL — the link a reader copies
    — reads back with the control off and the head sorted, the rows drawn in the order the sort
    names."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")
    _write_store(project, ".profiler-opencode", "s-p1", "2026-01-01T00:00:05.000Z", harness="opencode")
    _write_store(
        project,
        ".profiler-opencode",
        "s-p2",
        "2026-01-01T00:00:06.000Z",
        harness="opencode",
        extra={"tool": "Agent", "name": "devpro-coder", "child_agent_id": "s-child"},
    )
    _write_store(project, ".profiler-opencode", "s-child", "2026-01-01T00:00:07.000Z", harness="opencode", records=2)

    with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        feed = json.loads(_fetch(f"{url}api/traces"))

    # The closed state is no query at all: the page opens on every row, in the feed's order, and its
    # link carries nothing a reader did not choose.
    opened = _browser(tmp_path, index, feed, [])
    assert opened["visits"][0]["url"] == "http://127.0.0.1:0/profiler/"

    toggled = _browser(tmp_path, index, feed, [{"toggle": "child-rows"}])
    # The URL carries what the reader chose: leaving the view and returning through the page's own
    # link reads the control back off, where a page keeping its state in the document alone returns it
    # on.
    assert toggled["visits"][-1]["url"] != opened["visits"][-1]["url"], toggled["visits"][-1]["url"]
    assert toggled["visits"][-1]["controls"]["child-rows"] is False
    # A control toggled twice is the page it opened on, and its URL says so.
    twice = _browser(tmp_path, index, feed, [{"toggle": "child-rows"}, {"toggle": "child-rows"}])
    assert twice["visits"][-1]["url"] == "http://127.0.0.1:0/profiler/"

    sorted_once = _browser(tmp_path, index, feed, [{"sort": "records"}])
    assert ["records", "ascending"] in sorted_once["visits"][-1]["sorts"]

    # Leaving the view and returning through the page's own link: the visit reads the state the page
    # left, from the URL alone.
    returned = _browser(tmp_path, index, feed, [{"toggle": "child-rows"}, {"navigate": True}])
    assert returned["visits"][-1]["controls"]["child-rows"] is False
    assert returned["visits"][-1]["url"] == toggled["visits"][-1]["url"]

    sorted_and_returned = _browser(tmp_path, index, feed, [{"sort": "records"}, {"navigate": True}])
    assert sorted_and_returned["visits"][-1]["sorts"] == sorted_once["visits"][-1]["sorts"]


def test_the_served_index_links_the_shared_layers_own_text(tmp_path: Path) -> None:
    """`/profiler/` names the board's stylesheet at the path the board panel serves it, and the bytes
    that path answers are the layer's own text: the index carries no copy of the layer itself, its
    one link names one file, and the file it names serves `SHARED_CSS`'s bytes. A profiler page
    carrying a palette of its own is the second reskin the design forbids, the board and the
    profiler showing two identities for one site; a link to a path nothing serves, or to a path
    serving other text, is a page styled by nothing."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        [linked] = re.findall(r'<link rel="stylesheet" href="([^"]+)">', index)
        layer = _fetch(f"{url}{linked.removeprefix('/')}")

    assert LAYER_LINK == f'<link rel="stylesheet" href="{linked}">'
    assert SHARED_CSS not in index
    assert layer == SHARED_CSS


# ---------- the stores' rename, and an install's migration of them ----------


def _devpro(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """The `devpro` command this checkout's shim runs, as the installer is invoked."""
    return subprocess.run(
        [str(_devpro_shim(cwd)), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        check=False,
    )


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


def test_an_install_renames_an_old_pattern_store_and_a_second_install_touches_nothing(tmp_path: Path) -> None:
    """A project holding `.devpro-temp/claude-profiler/`: the install moves it to `.profiler-claude/`,
    contents and all, naming the rename in its report, and a second install reports the target up to
    date and leaves the store alone. A rename left undone leaves the store outside the reader's
    `.profiler-*` glob, so the project's recorded history vanishes from the index at the upgrade with
    nothing saying it happened."""
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    store = _write_store(project, "claude-profiler", "s-old", "2026-01-01T00:00:00.000Z", harness="claude")

    installed = _install_project(project)

    assert installed.returncode == 0, installed.stderr
    renamed = project / ".devpro-temp" / ".profiler-claude"
    assert f"renamed {store} → {renamed}" in installed.stdout
    assert not store.exists()
    assert sorted(path.name for path in renamed.iterdir()) == ["s-old.jsonl"]
    assert (_run(_launcher(tmp_path / "harness"), "tree", "s-old", cwd=project)).returncode == 0

    again = _install_project(project)

    assert again.returncode == 0, again.stderr
    assert "up to date" in again.stdout
    assert "renamed " not in again.stdout + again.stderr
    assert sorted(path.name for path in (project / ".devpro-temp").iterdir()) == [".profiler-claude"]


def test_an_install_skips_an_old_pattern_store_whose_new_name_already_stands(tmp_path: Path) -> None:
    """Both a `.devpro-temp/claude-profiler/` and a populated `.profiler-claude/`, the state after a
    capture ran post-upgrade and before the install: the install leaves the old store exactly where it
    stands and names it, never merging or deleting it. A rename onto the live store destroys the traces
    recorded since the upgrade, and a silent skip leaves the operator without the one line saying the
    old store stands."""
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    old = _write_store(project, "claude-profiler", "s-old", "2026-01-01T00:00:00.000Z", harness="claude")
    live = _write_store(project, ".profiler-claude", "s-new", "2026-01-02T00:00:00.000Z", harness="claude")

    installed = _install_project(project)

    assert installed.returncode == 0, installed.stderr
    assert f"left {old} in place" in installed.stdout
    assert sorted(path.name for path in old.iterdir()) == ["s-old.jsonl"]
    assert sorted(path.name for path in live.iterdir()) == ["s-new.jsonl"]


def test_a_doctor_names_an_old_pattern_store_and_its_remedy(tmp_path: Path) -> None:
    """A project whose only store is `.devpro-temp/claude-profiler/`: `doctor` names it as one `tree`
    does not read, with the `mv` that moves it — the remedy where an install cannot run, this
    repository's own among them — and `init`, which renames it where the repository takes a committed
    hook. A store the reader cannot see reads as "no calls recorded yet", and the operator has no line
    telling them why; a remedy naming only `install` names a command that will not run here."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    store = _write_store(project, "claude-profiler", "s-old", "2026-01-01T00:00:00.000Z", harness="claude")

    reported = _run(_launcher(tmp_path / "harness"), "doctor", cwd=project)

    assert reported.returncode == 0, reported.stderr
    target = project / ".devpro-temp" / ".profiler-claude"
    assert f"old:     {store} is not a store tree reads; move it there yourself, mv {store} {target}," in (
        reported.stdout
    )
    assert "or run devpro profiler init claude, which renames it" in reported.stdout
    assert "devpro install" not in reported.stdout
    assert "no calls recorded yet" in reported.stdout


def test_a_doctor_names_a_collided_store_as_the_operators_own_merge(tmp_path: Path) -> None:
    """An old store standing where its `.profiler-*` name already exists: `doctor` names both and says
    devpro never merges two stores, so the merge or deletion is the operator's. Sending them to a
    command that refuses on the same collision is a remedy that cannot do what it says."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    old = _write_store(project, "claude-profiler", "s-old", "2026-01-01T00:00:00.000Z", harness="claude")
    live = _write_store(project, ".profiler-claude", "s-new", "2026-01-02T00:00:00.000Z", harness="claude")

    reported = _run(_launcher(tmp_path / "harness"), "doctor", cwd=project)

    assert reported.returncode == 0, reported.stderr
    assert f"old:     {old} is not a store tree reads; {live} already exists" in reported.stdout
    assert "devpro never merges two stores: merge or delete the old one yourself" in reported.stdout
    assert "profiler init claude and" not in reported.stdout


def test_repair_fills_the_child_ids_a_capture_that_missed_2_4_1_left_null(tmp_path: Path) -> None:
    """`devpro profiler repair`, through the launcher's `devpro`, over a store holding what a capture that
    read the host's result for `output.sessionID` alone wrote: a dispatch whose result names the child
    in 2.4.1's background notice, a failed dispatch that created no child, and a dispatch already tied
    to its child. The repair fills the first and leaves the other two, reports the edge filled and the
    record still null, and a second run fills nothing — the record it already filled, and the one that
    names no child, stay as they stand."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    store = project / ".devpro-temp" / ".profiler-opencode"
    store.mkdir(parents=True)
    notice = "The subagent is working in the background (sessionID: ses_notice). You will receive a <background-result"
    records = [
        {"tool": "Agent", "name": "devpro-python-coder", "ok": True, "child_agent_id": None, "result": notice},
        {"tool": "Agent", "name": "devpro-c-coder", "ok": False, "child_agent_id": None, "result": "Invalid arguments"},
        {"tool": "Agent", "name": "devpro-rust-coder", "ok": True, "child_agent_id": "ses_right", "result": notice},
        {"tool": "read", "name": "read", "ok": True},
    ]
    (store / "ses_parent.jsonl").write_text(
        "".join(
            json.dumps({"v": 2, "harness": "opencode", "session": "ses_parent", **record}) + "\n" for record in records
        ),
        encoding="utf-8",
    )
    launcher = _launcher(tmp_path / "harness")

    repaired = _run(launcher, "repair", cwd=project)

    assert repaired.returncode == 0, repaired.stderr
    assert repaired.stdout.strip() == "repaired: 1 edges; null: 1 records (no child id)"
    written = [json.loads(line) for line in (store / "ses_parent.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [record.get("child_agent_id") for record in written] == [
        "ses_notice",
        None,
        "ses_right",
        None,
    ]

    again = _run(launcher, "repair", cwd=project)

    assert again.stdout.strip() == "repaired: 0 edges; null: 1 records (no child id)"


def test_the_repair_counts_only_the_edges_it_writes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`clauses.TEST_PRECONDITION`: a test a package adds is written for a named defect and the run
    that fails under it before the change. The defect is the repair's count incremented before its
    live-file guard: a store file a capture appends to while the repair reads it is left as it stands,
    yet its would-be fill is reported as an edge repaired, against the verb's own docstring. The run
    fails before the count moves, reading `repaired` 1 for a file nothing wrote.

    The append is made by the read itself, between the read and the guard's second stat — the write a
    live session makes, made deterministically. The file is then named as left, its one subagent
    record still counts null, and no edge is counted repaired; the file holds the record plus the
    append, the record's `child_agent_id` still absent."""
    project = tmp_path / "project"
    store = project / ".devpro-temp" / ".profiler-opencode"
    store.mkdir(parents=True)
    file = store / "ses_parent.jsonl"
    notice = "The subagent is working in the background (sessionID: ses_notice). You will receive a <background-result"
    record = {
        "v": 2,
        "harness": "opencode",
        "session": "ses_parent",
        "tool": "Agent",
        "name": "devpro-python-coder",
        "ok": True,
        "child_agent_id": None,
        "result": notice,
    }
    appended = {"v": 2, "harness": "opencode", "session": "ses_parent", "tool": "read", "name": "read", "ok": True}
    original = json.dumps(record) + "\n"
    file.write_text(original, encoding="utf-8")
    real_read_text = Path.read_text

    def read_while_the_capture_appends(self: Path, encoding: str | None = None, errors: str | None = None) -> str:
        text = real_read_text(self, encoding=encoding, errors=errors)
        if self == file:
            with file.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(appended) + "\n")
        return text

    monkeypatch.setattr(Path, "read_text", read_while_the_capture_appends)

    repaired, null, left = repair_child_ids(project)

    assert (repaired, null, left) == (0, 1, [file])
    assert real_read_text(file, encoding="utf-8") == original + json.dumps(appended) + "\n"


def test_the_strict_fill_refuses_unknown_and_unfilled_marks_and_leaves_none_standing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`clauses.TEST_PRECONDITION`: a test a package adds is written for a named defect and the run
    that fails under it before the change. The defect is the render's silent no-op `str.replace` — a
    mark the fill is told to fill but the text no longer carries, left unfilled without a word — and
    the run fails before the strict fill exists to raise on it.

    The strict fill every profiler fill now runs through refuses a placeholder it is told to fill
    that the text no longer carries, and leaves no mark it filled standing. `index_html`, fed an
    `INDEX` whose legend mark the text no longer carries yet still told to fill it, raises;
    `strict_fill` on `view.html` with a mark removed, still told to fill it, raises the same. A rendered session page
    and the served page and index then carry no mark the fill was handed standing. The `INDEX` swap
    is for this check alone: `monkeypatch` reverts at the end and the serve below runs in a child
    process that reads `INDEX` from disk, so nothing after it sees the swap."""
    # (a) `index_html`: an `INDEX` whose legend mark the text no longer carries, still told to fill it.
    monkeypatch.setattr("devpro.profiler.pages.INDEX", INDEX.replace(BAND_LEGEND, ""))
    with pytest.raises(KeyError):
        index_html()
    # (a) the fill itself: `view.html` with a mark removed, still told to fill it.
    from devpro.profiler.pages import strict_fill

    view_text = (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8")
    fills = {DATA_MARK: "data", LAYER_MARK: "layer", BAND_LEGEND: "legend"}
    with pytest.raises(KeyError):
        strict_fill(view_text.replace(BAND_LEGEND, ""), fills)
    # (a) the fill's own strictness: a value carrying its mark leaves it standing — refused.
    with pytest.raises(KeyError):
        strict_fill(BAND_LEGEND, {BAND_LEGEND: BAND_LEGEND})
    # (b) nothing the fill was handed is left standing, standalone or served.
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    launcher = _launcher(tmp_path / "harness")
    printed = _run(launcher, "tree", "s-claude", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr
    for mark in (LAYER_MARK, DATA_MARK, BAND_LEGEND, DISPATCHED_MARK, RETURN_MARK):
        assert mark not in printed.stdout, f"{mark} left standing in the rendered page"
    with _serve(launcher, cwd=project) as url:
        page = _fetch(f"{url}page/s-claude")
        index = _fetch(f"{url}profiler/")
    for mark in (LAYER_MARK, DATA_MARK, BAND_LEGEND, DISPATCHED_MARK, RETURN_MARK):
        assert mark not in page, f"{mark} left standing in the served page"
        assert mark not in index, f"{mark} left standing in the served index"
    assert "$rows" not in index


def test_the_strict_fill_refuses_a_value_carrying_another_marks_mark() -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a fill that refuses a value carrying its own mark
    only, so a value carrying a later mark is read as that mark and filled. A value is inserted as
    it stands, never read for a mark of the same fill, so such a value is refused, not filled."""
    from devpro.profiler.pages import strict_fill

    with pytest.raises(KeyError):
        strict_fill(f"{BAND_LEGEND}{RETURN_MARK}", {BAND_LEGEND: RETURN_MARK, RETURN_MARK: "back"})
