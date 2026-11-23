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

Two more are the launcher's own: a capture whose devpro the finder cannot resolve exits 0 with no
output and no other subcommand does, and `init` lays down the launcher alone, removing the `hp.py` and
`view.html` an older init left beside it.

The stores' rename is the last group's: an install and an `init` move each `*-profiler` store under
`.devpro-temp/` to its `.profiler-*` name and name the move, and neither ever merges one store into
another; `doctor` names an old-pattern store the reader cannot see.

The package is imported from the repository root, which `just test` puts on PYTHONPATH. The launcher
runs whatever `devpro` it resolves, and no test relies on one installed on the host: each installs a
shim running this checkout into the directory it runs in and points `HP_DEVPRO` at it.
"""

from __future__ import annotations

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
from datetime import datetime, timedelta, timezone
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
    LEGEND,
    RETURN_MARK,
    SHARED_CSS,
    index_html,
)
from devpro.profiler.values import _epoch_ms
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
    return _claude_plugin(directory) / _PROFILER / "hp.sh"


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


def _run(launcher: Path, *args: str, cwd: Path, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(launcher), *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, "PATH": f"{_devpro_shim(cwd).parent}:{os.environ['PATH']}"},
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


def _without_deco(served: str) -> str:
    """A served page reduced to the file flow's page, so the served and the printed stand apart on
    the layer's carriage and nothing else: the shared layer's link stands back as the inline text the
    render writes there, and the band's per-page facts — the way back this page carries and the
    legend, which the render's own band holds in the same place — come out, leaving the band the
    render carries bare.

    The layer line is one with no other `</style>`-opening kind between it and the head; the way back
    and the legend are the band's own, the band one with no other `frame-band` div, and it runs to the
    `Return to list` link it ends with, so each region takes its own whole lines with it and nothing
    is left where the render has nothing. The band comes out bare — the render's own band, its legend
    removed in the comparison, is bare too."""
    lines = served.splitlines()
    lines[lines.index(LAYER_LINK)] = LAYER_INLINE
    page = "\n".join(lines) + "\n"
    band = page[
        page.find('<div class="frame-band') : page.find("Return to list</a></div>") + len("Return to list</a></div>")
    ]
    return page.replace(band, '<div class="frame-band scanlines"></div>')


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
    """The launcher that ships is the launcher the repository holds: no stamp or reflow lands in `hp.sh`
    on its way through the package data."""
    launcher = _launcher(tmp_path / "harness")
    assert launcher.read_bytes() == launcher_resource().read_bytes()


@pytest.mark.parametrize("command", ["capture", "tree"])
def test_a_launcher_finding_an_unusable_devpro_captures_silently_and_reports_otherwise(
    tmp_path: Path, command: str
) -> None:
    """With a `devpro` first on the finder's path that does not run, `capture` drains stdin and exits 0
    writing nothing, and every other subcommand names the unusable command on stderr and exits 1: a
    capture that reports or exits nonzero blocks the tool call that fired it, under the harness hook
    error policy, and a tree that says nothing leaves the operator no line naming the one dependency
    to fix."""
    launcher = _launcher(tmp_path / "harness")
    payload = json.dumps({"hook_event_name": "PostToolUse", "session_id": "s-none", "tool_name": "Bash"})
    project = tmp_path / "project"
    project.mkdir()
    broken = tmp_path / "broken"
    broken.mkdir()
    script = broken / "devpro"
    script.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    script.chmod(0o755)
    done = subprocess.run(
        ["sh", str(launcher), command],
        input=payload,
        capture_output=True,
        text=True,
        cwd=project,
        env={**os.environ, "PATH": f"{broken}:{os.environ['PATH']}"},
        check=False,
    )

    if command == "capture":
        assert (done.returncode, done.stdout, done.stderr) == (0, "", "")
    else:
        assert done.returncode == 1
        assert done.stdout == ""
        assert str(script) in done.stderr
    assert not (project / ".devpro-temp").exists()


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


def _run_ts(
    script: Path, *, directory: Path, arg: str | None = None, stdin: str | None = None
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
    )
    assert done.returncode == 0, done.stderr
    return done


def _moments(first: str, last: str) -> str:
    """The moments' cell as the index's script writes it from the feed's two epoch milliseconds —
    `index.js`'s `moments`, in Python: each instant an ISO UTC `<time>`, the text raw UTC to the
    second, the title's last instant with the milliseconds the instant holds.

    The script reads the feed's integers, so a whole second there carries no `.000`; the cell's last
    `<time>` keeps the milliseconds only where the instant has any, and the title stands on that
    same instant, so a title that added `.000` would be a form the page never draws."""
    moments = [datetime.fromtimestamp(_epoch_ms(stamp) / 1000, timezone.utc) for stamp in (first, last)]
    text = [f"{moment:%Y-%m-%d %H:%M:%S} UTC" for moment in moments]
    instants = [
        f"{moment:%Y-%m-%dT%H:%M:%S}" + (f".{moment.microsecond // 1000:03d}" if moment.microsecond else "") + "Z"
        for moment in moments
    ]
    return (
        f'<span class="moments" title="{text[0]} to {instants[1]}">'
        f'<time datetime="{instants[0]}">{text[0]}</time> to '
        f'<time datetime="{instants[1]}">{instants[1]}</time></span>'
    )


def test_the_decoration_script_reads_every_moments_cell_the_index_draws(tmp_path: Path) -> None:
    """`deco.js` over the moments cells the index's script writes — its `<time>` elements' datetimes
    the feed's epoch milliseconds, its text and title the raw UTC: a cell whose two instants share the
    reader's calendar day reads `H:MM to H:MM` in the reader's zone, one whose instants fall on two
    days carries each date, a second-precision instant keeps its second of it, and the cell's title
    keeps the raw UTC to the byte; a cell with no `<time>` element keeps the text it served, the
    fallback where a cell's instants cannot be read. The script parses no cell text, so a moment
    whose rendered form moves still reads: a script that parses the served text instead stops
    matching at the first format change and leaves the raw UTC with nothing saying so."""
    cells = [
        _moments("2026-01-01T00:00:01.250Z", "2026-01-01T00:00:02.500Z"),
        _moments("2026-01-01T06:00:00.000Z", "2026-01-01T18:30:00.000Z"),
        '<span class="moments" title="2026-01-01 00:00:00 UTC to 2026-01-01T00:00:01.000Z">'
        "2026-01-01 00:00:00 UTC to 2026-01-01T00:00:01.000Z</span>",
    ]
    done = subprocess.run(
        [_bun(), str(_HERE / "profiler_deco_runner.ts")],
        input=json.dumps({"cells": cells}),
        capture_output=True,
        encoding="utf-8",
        env={**os.environ, "TZ": "America/Los_Angeles"},
        timeout=120,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    readings = json.loads(done.stdout)

    assert readings["readings"] == [
        "16:00 to 16:00",
        "2025-12-31 22:00 to 2026-01-01 10:30",
        "2026-01-01 00:00:00 UTC to 2026-01-01T00:00:01.000Z",
    ]
    assert readings["titles"] == [
        "2026-01-01 00:00:01 UTC to 2026-01-01T00:00:02.500Z",
        "2026-01-01 06:00:00 UTC to 2026-01-01T18:30:00Z",
        "2026-01-01 00:00:00 UTC to 2026-01-01T00:00:01.000Z",
    ]


def test_the_opencode_capture_records_every_fired_call(tmp_path: Path) -> None:
    """The shipped `profiler.ts` through a stub plugin context: a completed call, a failed one, a
    skill call, a subagent dispatch and the session's idle each append their record; the failed call's
    text is its `Tool.Error`'s message, the skill and subagent carry the host's own names, a dispatch
    carries the kind its response reports or else its own agent, under either of the host's spellings
    for the tool, the child session its result's metadata names, and the one call whose `execute.after`
    never fires drops its start at the idle."""
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
    ]
    assert calls[0]["result"] == "hi"
    assert calls[1]["ok"] is False
    assert calls[1]["result"] == "The user rejected this tool call"
    assert calls[2]["result"] == "loaded"
    assert calls[3]["result"] == "ses_child"
    assert calls[3]["child_agent_id"] == "ses_child"
    assert calls[3]["child_agent_type"] == "devpro-python-coder"
    assert calls[4]["child_agent_id"] == "ses_fork"
    assert calls[4]["child_agent_type"] == "fork"
    # The task spelling's after-hook carries no `metadata`, so its bare `output` names no session.
    assert calls[5]["child_agent_id"] is None
    assert calls[5]["child_agent_type"] == "devpro-tech-writer"
    assert [record["event"] for record in records if record.get("event")] == ["experimental.idle"]
    assert (out["startedBeforeIdle"], out["startedAfterIdle"]) == (1, 0)


def test_a_line_over_the_bound_is_fitted_at_its_root(tmp_path: Path) -> None:
    """`serialize` holds every line to `LINE_LIMIT`, which the torn-tail read relies on: a record whose
    fixed `session` alone is longer than the bound is fitted by clipping that field too, and a line
    already inside the bound is left as it stands."""
    line_limit = 4096
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    over = json.loads(_run_ts(_HERE / "profiler_serialize_runner.ts", directory=first, arg="4090").stdout)
    assert over["bytes"] <= line_limit
    assert over["session"] < 4090
    inside = json.loads(_run_ts(_HERE / "profiler_serialize_runner.ts", directory=second, arg="200").stdout)
    assert inside == {"bytes": 338, "session": 0}


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
    """A committed hook directory holding an older `init`'s launcher, `hp.py` and `view.html`: a re-run
    writes the launcher alone and removes both retired files. A committed hook running devpro beside a
    stale `hp.py` is the half-absorbed install, and `stale_hook` would chase files no install ships."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    hook_dir = project / ".claude" / "harness-profiler"
    hook_dir.mkdir(parents=True)
    for name in ("hp.sh", *RETIRED_HOOK_FILES):
        (hook_dir / name).write_text("an older init's copy\n", encoding="utf-8")

    done = _profiler_init(project)

    assert done.returncode == 0, done.stderr
    assert [path.name for path in sorted(hook_dir.iterdir())] == ["hp.sh"]
    assert (hook_dir / "hp.sh").read_bytes() == launcher_resource().read_bytes()
    assert os.access(hook_dir / "hp.sh", os.X_OK)
    assert (project / ".claude" / "skills" / "profiler" / "SKILL.md").is_file()
    assert "harness-profiler/hp.sh" in (project / ".claude" / "settings.json").read_text(encoding="utf-8")


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

    (project / ".claude" / "harness-profiler" / "hp.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

    edited = _run(_launcher(tmp_path / "harness"), "doctor", cwd=project)

    assert edited.returncode == 0, edited.stderr
    assert "update:  the committed hook has another version of hp.sh;" in edited.stdout


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
            "first": _epoch_ms("2026-01-01T00:00:00.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:01.000Z"),
            "span": 1,
        },
        {
            "harness": "opencode",
            "id": "s-opencode",
            "records": 1,
            "first": _epoch_ms("2026-01-01T00:00:05.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:05.000Z"),
            "span": 0,
        },
        {
            "harness": "opencode",
            "id": "s-dispatcher",
            "records": 1,
            "first": _epoch_ms("2026-01-01T00:00:06.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:06.000Z"),
            "span": 0,
        },
        {
            "harness": "opencode",
            "id": "s-child",
            "records": 2,
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
    assert re.search(r"<th>harness</th><th>session</th><th>records</th><th>first to last</th><th>span</th>", index)
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
    assert 'class="child"' in drawn["rows"][3] and "↳ child — devpro-coder" in drawn["rows"][3]
    # The keys the script reads are the schema's: a session entry's six, the dispatcher pair, and an
    # unreadable store's one — no key the feed builder does not write, and none it writes unread.
    assert set(drawn["keys"]) == {
        "harness",
        "id",
        "records",
        "first",
        "last",
        "span",
        "dispatcher",
        "session",
        "name",
        "unreadable",
    }
    assert drawn["fetches"] == ["/api/traces"]

    # The deco's sweep over the rows the index drew: the index's script runs first and its fetch
    # settles after it, the deco's sweep loading before those rows arrive — the served page's own
    # script order — so a sweep that reads the cells once at load leaves every fresh one raw UTC. Each
    # moments cell the rows carry is read from its `<time>` instants, its raw text replaced by the
    # reader's clock and its title left standing.
    run = _run_ts(
        _HERE / "profiler_deco_runner.ts",
        directory=tmp_path,
        stdin=json.dumps({"index": index, "feed": json.loads(feed)}),
    )
    swept = json.loads(run.stdout)
    assert len(swept["drawn"]) == 4, swept["drawn"]
    for markup, reading in swept["drawn"]:
        assert re.search(r'title="\d{4}-\d\d-\d\d \d\d:\d\d:\d\d UTC to ', markup), markup
        assert reading and "UTC" not in reading, reading

    # The span's own rendering, at every scale the server-side span test covered — seconds below a
    # minute, minutes alone, and the hour forms — fed the runner a crafted feed so the scale is known
    # by construction; and the table's own empty reading, where the feed holds no session to draw and
    # no store to name, a full-width row that is no store's unreadable state.
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
    for entry, cell in zip(
        drawn["rows"], ("<td>59s</td>", "<td>1m 30s</td>", "<td>2m</td>", "<td>1h</td>", "<td>1h 30m</td>")
    ):
        assert cell in entry, f"{cell} not the span cell of the row drawn for its entry"
    run = _run_ts(
        _HERE / "profiler_index_runner.ts",
        directory=tmp_path,
        stdin=json.dumps({"index": index, "feed": []}),
    )
    drawn = json.loads(run.stdout)
    assert len(drawn["rows"]) == 1
    assert "No sessions recorded yet" in drawn["rows"][0] and "is unreadable" not in drawn["rows"][0]


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
            "first": _epoch_ms("2026-01-01T00:00:00.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:00.000Z"),
            "span": 0,
        },
        {"unreadable": ".profiler-broken"},
    ]
    assert missing.value.code == 404


def test_the_served_page_is_the_html_the_file_flow_writes(tmp_path: Path) -> None:
    """One session's `/page/<id>` carries the file flow's page data and that flow's page: the two
    profiler templates' own text — the nav, the frame band and the decoration's script — both carry,
    and the only difference between the served page and the printed one is the shared layer's
    carriage, the serve's the link to the board panel's own file and the print's the inlined text.
    Undo that carriage — the link stands back as the text the render inlines — and the band's
    per-page facts — the way back this page carries and the legend, which the render's band holds in
    the same place — come out, leaving `tree --format html`'s page, to the byte. A served page whose
    layer is inlined (the render's carriage, not the serve's), or whose data is not that page's, is
    the page standing apart from the one the file flow writes."""
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
    # carriers, and the page else the same to the byte.
    assert served.count(LAYER_LINK) == 1 and SHARED_CSS not in served
    assert _without_deco(served) == printed.stdout.replace(LEGEND, "").rstrip("\n") + "\n"


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
