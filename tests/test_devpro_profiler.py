"""The activity profiler's contract, driven through the wrapper the install writes: one capture
writes a schema-4 record, `tree --format html`'s page data carries the keys `view.html` parses, and the
installed wrapper is the wrapper the install wrote. It fails on the port defect that renames or drops a
record field the page data carries — the rename or drop ships green and renders an empty page.

One record the port itself owns: `tree` renders an opencode session's store beside the claude
capture's — the split that is the capture's purpose, and whose loss the single-store read would not
show. `test_the_two_masks_redact_alike` holds the two harnesses' masking to one sample list, since
JavaScript's `\\w` is ASCII where Python's is not, and
`test_the_capture_builds_its_record_over_host_shape_inputs` holds the capture's own record
construction to the child session its result names under each host shape the floor covers.

One more is `init`'s: `init` writes the skill and the committed hook's one command, removing the
launchers and files older inits left in the hook directory.

The stores' rename is the last group's: an install and an `init` move each `*-profiler` store under
`.devpro-temp/` to its `.profiler-*` name and name the move, and neither ever merges one store into
another.

The package is imported from the repository root, which `just test` puts on PYTHONPATH. The tests run
the wrapper the install writes — `tools/devpro.sh` beside this package's copy in the installed tree —
and no test relies on a devpro installed on the host: the install runs in the test's directory, so the
wrapper runs this checkout's code.
"""

import hashlib
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

from devpro.components import NAME
from devpro.dashboard.server import BOARD_PATH
from devpro.profiler.capture import mask
from devpro.profiler.hooks import RETIRED_HOOK_FILES, RETIRED_LAUNCHERS
from devpro.profiler.pages import (
    AGENT_PREFIX,
    AGENT_PREFIX_LINE,
    AGENT_PREFIX_MARK,
    BAND_LEGEND,
    COLUMNS,
    DATA_MARK,
    DECO_INLINE,
    DECO_MARK,
    DISPATCHED_MARK,
    INDEX,
    LAYER_MARK,
    RETURN_MARK,
    SHARED_CSS,
    call_label,
    clock,
    index_html,
    list_sessions,
    read_sessions,
    stamp,
    store_directories,
)
from devpro.profiler.values import CAPTURED_EVENTS, _epoch_ms
from tests.conftest import page_data
from tests.fixtures import fixture_file
from tests.test_devpro_install import _claude_plugin, _definition_install

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
_RECORD_FIELDS = {"v", "harness", "at", "session", "tool", "name", "ok", "args", "branch", "plan", "directives"}

# The keys `view.html` reads from the page's data and from one call row. The stamp's two are read off
# the records alike, `null` for a session that carries none.
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

    A test that runs the wrapper directly (`dashboard`, `profiler`) gives its run one of these."""
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


def index_row_colspan(index: str) -> int:
    """The span the index's row script gives a full-width row — the table's column count as its own
    script states it."""
    script = index.split("<script>", 1)[1].split("</script>", 1)[0]
    return int(re.search(r"cell\.colSpan = (\d+);", script).group(1))


def _plan(root: Path, title: str) -> None:
    """The project's active plan at `root`, its first level-1 heading `title`."""
    (root / "ACTIVE_PLAN.md").write_text(f"# {title}\n\nbody\n", encoding="utf-8")


def test_a_capture_writes_the_record_the_page_and_tree_read(tmp_path: Path, _wrapper: Path) -> None:
    """One well-formed hook payload appends one line to the project's trace, carrying schema 4 and
    the field names the unchanged page and tree read; the html page's data carries the keys
    `view.html` parses."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    _plan(project, "a plan")
    definition = project / ".claude" / "skills" / "devpro" / "agents" / "coder.md"
    definition.parent.mkdir(parents=True)
    definition.write_text("<!-- !GENERATED! from devpro/definitions/agents/coder.py -->\nbody\n", encoding="utf-8")
    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD)
    assert capture.returncode == 0, capture.stderr
    assert capture.stdout == "" and capture.stderr == ""
    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    [record] = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line]
    assert record["v"] == 4
    assert _RECORD_FIELDS <= set(record), sorted(record)
    assert record["session"] == "s-profiler"
    assert record["tool"] == "Bash"
    assert record["ok"] is True
    assert record["args"] == "ls"
    page = _run(_wrapper, "tree", "--format", "html", cwd=project)
    assert page.returncode == 0, page.stderr
    data = page_data(page.stdout)
    assert _PAGE_KEYS <= set(data), sorted(data)
    assert data["session"] == "s-profiler"
    assert _CALL_KEYS <= set(data["calls"][0]), sorted(data["calls"][0])
    assert data["calls"][0]["tool"] == "Bash"


def test_a_capture_records_the_model_its_transcript_names(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect is a capture that leaves out the model its transcript
    names: before the change the record has `context_tokens` 10 and no `model`, so a claude session's
    calls show which model spent the tokens and never which model itself.

    A transcript holding the assistant message that made the call — its `model` and its `usage`, its
    `tool_use` carrying the call's id — gives the record both facts from that one line, and the page's
    data names the model for the call, for the context that made it and for the session."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps(
            {
                "type": "assistant",
                "message": {
                    "model": "claude-opus-4-5",
                    "usage": {"input_tokens": 10},
                    "content": [{"type": "tool_use", "id": "toolu_1"}],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    payload = {**json.loads(_PAYLOAD), "transcript_path": str(transcript), "tool_use_id": "toolu_1"}
    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=json.dumps(payload))
    assert capture.returncode == 0, capture.stderr

    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    [record] = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line]
    page = _run(_wrapper, "tree", "--format", "html", cwd=project)

    assert (record["model"], record["context_tokens"]) == ("claude-opus-4-5", 10)
    assert page.returncode == 0, page.stderr
    data = page_data(page.stdout)
    assert (data["calls"][0]["model"], data["contexts"][0]["models"], data["models"]) == (
        "claude-opus-4-5",
        ["claude-opus-4-5"],
        ["claude-opus-4-5"],
    )


def test_a_session_whose_trace_holds_the_data_mark_renders(tmp_path: Path, _wrapper: Path) -> None:
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

    page = _run(_wrapper, "tree", "--format", "html", cwd=project)

    assert page.returncode == 0, page.stderr
    assert page_data(page.stdout)["calls"][0]["args"] == args


def test_a_capture_writes_its_line_in_the_bytes_it_measured(tmp_path: Path, _wrapper: Path) -> None:
    """A lone surrogate in a tool argument, and a non-ASCII one, measure as the bytes the store holds:
    the line is ASCII, so the length `serialize` bounds and the file's bytes are one count, and
    `read_text` reads the same JSON back on a host whose default encoding is not utf-8."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    payload = dict(json.loads(_PAYLOAD), tool_input={"command": "echo h\u00e9 \ud800"})
    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=json.dumps(payload))
    assert capture.returncode == 0, capture.stderr
    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    line = trace.read_bytes().decode("ascii")
    assert json.loads(line)["args"] == "echo h\u00e9 \ud800"


def test_a_capture_stamps_every_record_with_the_sessions_operational_context(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: a capture wrote records with no operational context, so
    the render had no plan and no directives to answer what a session ran under.

    A project holding an installed-looking definition under a harness directory, its `AGENTS.md` and a
    plan: the first record's `plan` is the plan's first level-1 heading, and its `directives` the digest
    the harness files and the agents file hash to, with that digest's manifest holding each file's own.
    A directive and the plan then change, and the session's later records keep the stamp it started
    under — taken once, not re-read per record."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    _plan(project, "the plan as it started")
    definition = project / ".opencode" / "plugins" / "devpro" / "agents" / "coder.md"
    definition.parent.mkdir(parents=True)
    definition.write_text("<!-- !GENERATED! from devpro/definitions/agents/coder.py -->\nbody\n", encoding="utf-8")
    agents_file = project / "AGENTS.md"
    agents_file.write_text("# agents\n", encoding="utf-8")
    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD)
    assert capture.returncode == 0, capture.stderr
    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    [first] = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line]

    expected = hashlib.sha256(
        json.dumps(
            sorted(
                {
                    "AGENTS.md": hashlib.sha256(agents_file.read_bytes()).hexdigest(),
                    ".opencode/plugins/devpro/agents/coder.md": hashlib.sha256(definition.read_bytes()).hexdigest(),
                }.items()
            ),
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()
    assert (first["plan"], first["directives"]) == ("the plan as it started", expected)
    manifest = project / ".devpro-temp" / ".profiler-directives" / f"{expected}.json"
    assert sorted(json.loads(manifest.read_text(encoding="utf-8"))) == [
        ".opencode/plugins/devpro/agents/coder.md",
        "AGENTS.md",
    ]

    agents_file.write_text("# agents, edited\n", encoding="utf-8")
    _plan(project, "the plan as it moved")
    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD)
    assert capture.returncode == 0, capture.stderr
    records = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line]
    assert [(record["plan"], record["directives"]) for record in records] == [(first["plan"], expected)] * 2


def test_a_capture_leaves_out_the_stamp_fields_a_project_gives_it_nothing_for(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: a capture wrote a stamp field for a project that gives it
    nothing — no plan, no file carrying an installed banner — so a record stated a context the project
    never had.

    A project holding neither a plan nor an installed file: the record carries neither `plan` nor
    `directives`, and no manifest stands."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD)
    assert capture.returncode == 0, capture.stderr
    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    [record] = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line]

    assert "plan" not in record and "directives" not in record
    assert not (project / ".devpro-temp" / ".profiler-directives").exists()


def test_the_capture_keeps_its_childs_output_off_the_hooks_stdout(tmp_path: Path, _wrapper: Path) -> None:
    """A hook's stdout is the host's protocol alone, so the capture's own output never reaches it. The
    defect: the capture printed the record's path through `sys.stdout`, so a line it wrote there
    reached Claude Code as its hook result."""
    project = tmp_path / "project"
    project.mkdir()

    done = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD)

    assert (done.returncode, done.stdout) == (0, ""), done.stderr
    assert (project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl").is_file()


@pytest.mark.parametrize("command", ["capture", "tree"])
def test_a_wrapper_whose_run_fails_reports_its_failure(tmp_path: Path, command: str) -> None:
    """The installed wrapper whose own run fails — a deleted copy of devpro, a broken interpreter
    record — exits nonzero with the failure named on stderr, stdout silent, for every subcommand.
    Defect: the retired launcher answered the capture's failure with exit 0 and a drained stdin, so a
    wrapper that could not run at all reported a capture it never made as a success."""
    launcher = _installed_wrapper(tmp_path / "harness")
    payload = json.dumps({"hook_event_name": "PostToolUse", "session_id": "s-none", "tool_name": "Bash"})
    project = tmp_path / "project"
    project.mkdir()
    launcher.write_text("#!/bin/sh\necho 'devpro.sh: this wrapper is broken' >&2\nexit 1\n", encoding="utf-8")
    launcher.chmod(0o755)
    done = subprocess.run(
        [str(launcher), "profiler", command],
        input=payload,
        capture_output=True,
        text=True,
        cwd=project,
        env={**os.environ, "PATH": "/usr/bin:/bin"},
        check=False,
    )

    assert done.returncode == 1, done.stderr
    assert done.stdout == ""
    assert "devpro.sh: this wrapper is broken" in done.stderr
    assert not (project / ".devpro-temp").exists()


def test_the_capture_with_no_wrapper_and_no_payload_exits_0_writing_nothing(tmp_path: Path) -> None:
    """The capture subcommand run where the wrapper does not stand and the payload cannot be read: it
    exits 0 with nothing on stdout, and writes no store. Defect: with no launcher draining stdin, a
    capture whose wrapper is missing or whose payload is empty exits nonzero and blocks the tool call
    that fired it."""
    project = tmp_path / "project"
    project.mkdir()
    environment = {
        **os.environ,
        "PYTHONPATH": str(_PACKAGE_ROOT),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PATH": "/usr/bin:/bin",
    }

    for payload in ("", "not json"):
        done = subprocess.run(
            [sys.executable, "-m", "devpro", "profiler", "capture", "claude"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project,
            env=environment,
            check=False,
        )
        assert (done.returncode, done.stdout) == (0, ""), (payload, done.stderr)
    assert not (project / ".devpro-temp").exists()


def test_the_wrapper_the_install_writes_captures_with_no_devpro_on_path(tmp_path: Path, _wrapper: Path) -> None:
    """The wrapper the install writes is the one the hook runs: a capture through it writes the record,
    with no `devpro` on PATH at all — the wrapper names its own copy of devpro, so a bare PATH is where
    that is put to the proof."""
    assert (_wrapper.parent / "devpro").is_dir(), "the install writes its copy of devpro in tools/"
    project = tmp_path / "project"
    project.mkdir()
    done = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD, path="/usr/bin:/bin")
    assert done.returncode == 0, done.stderr
    trace = project / ".devpro-temp" / ".profiler-claude" / "s-profiler.jsonl"
    [record] = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line]
    assert record["tool"] == "Bash" and record["args"] == "ls"


def test_a_tree_renders_an_opencode_store_beside_the_claude_capture(tmp_path: Path, _wrapper: Path) -> None:
    """A session in each harness's store under one project, and one `tree <id>` per store renders it:
    the read that walks both harnesses' stores, whose revert to claude's alone loses the opencode
    session silently.

    The opencode dispatch's record draws the context words claude's dispatch draws for the same
    fields — `new context <id>`, and `copy of <caller>` on the host's `fork` kind. A tree reading the
    context a call started from claude's `agent_id` alone draws the opencode dispatch with no child
    context, the two harnesses' dispatches differing on records that state one fact."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD)
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
                    "v": 4,
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
                    "v": 4,
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
                    "v": 4,
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

    opencode_tree = _run(_wrapper, "tree", "--verbose", "s-opencode", cwd=project)
    assert opencode_tree.returncode == 0, opencode_tree.stderr
    assert "make test" in opencode_tree.stdout
    # The dispatch draws the context words the same fields draw under claude: the host's `fork` kind
    # makes the child a copy of its caller's history.
    assert "new context ses_fo, copy of main" in opencode_tree.stdout
    claude_tree = _run(_wrapper, "tree", "--verbose", "s-profiler", cwd=project)
    assert claude_tree.returncode == 0, claude_tree.stderr
    assert "ls" in claude_tree.stdout


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


def test_the_capture_builds_its_record_over_host_shape_inputs(tmp_path: Path) -> None:
    """The shipped `profiler.ts` through a stub plugin context: a completed call, a failed one, a
    skill call and subagent dispatches each append their record. The failed call's text is its
    `Tool.Error`'s message, the skill and subagent carry the host's own names, and a dispatch's child
    session is the one its result names — in the output 2.3.2 reports, in the metadata 2.3.0
    reports, and at the result's top level 2.4.1 reports, each of which the floor covers — with a
    top-level id that is not a string refused, the read falling through to the output's id. Each
    session's idle appends its lifecycle record, the signal's keys on it whether or not the host named
    them; a dispatch's return carries `background: true`, every other call `false`.

    `clauses.TEST_PRECONDITION`. The defect: an opencode record that names no model where its
    session's request named one, or one that names a model no request reported. Each `ses_capture`
    call carries the model the one fired `model.request` named, and a call in a session that fired
    none carries `null`. The idle stamp's own defects are the same paragraph's second half above.

    The host shapes and the plugin context are inputs, both shaped here: nothing the test asserts is a
    claim about what the host reports, only about what the capture builds from them."""
    project = tmp_path / "project"
    project.mkdir()
    out = json.loads(_run_ts(_HERE / "profiler_contract_runner.ts", directory=project).stdout)
    records = out["records"]

    calls = [record for record in records if record.get("event") is None and record["session"] == "ses_capture"]
    assert [(record["tool"], record["name"]) for record in calls] == [
        ("shell", "printf 'hi\\n'"),
        ("shell", "rm -rf /"),
        ("Skill", "profiler"),
        ("Agent", "devpro-python-coder"),
        ("Agent", "devpro-go-coder"),
        ("Agent", "devpro-rust-coder"),
        ("Agent", "devpro-typescript-coder"),
    ]
    # The completed and failed texts, the failure's being the host's error object's message.
    assert calls[0]["result"] == "hi"
    assert (calls[1]["ok"], calls[1]["result"]) == (False, "The user rejected this tool call")
    assert calls[2]["result"] == "loaded"
    # A subagent dispatch: the child's id the result names, and the kind its input names.
    assert (calls[3]["child_agent_id"], calls[3]["child_agent_type"]) == ("ses_output", "devpro-python-coder")
    # 2.3.0's shape: the id rides the result's metadata, so the metadata is what names this child.
    assert (calls[4]["child_agent_id"], calls[4]["child_agent_type"]) == ("ses_floor", "devpro-go-coder")
    # 2.4.1's shape: the id at the result's top level alone, `output` a bare string carrying none.
    assert (calls[5]["child_agent_id"], calls[5]["child_agent_type"]) == ("ses_top", "devpro-rust-coder")
    # The top-level id is not a string: the guard refuses it and the read falls through to the output.
    assert (calls[6]["child_agent_id"], calls[6]["child_agent_type"]) == ("ses_guard", "devpro-typescript-coder")
    # A dispatch returns at once and its child runs in the background; any other call runs in its own
    # session's foreground. The dispatch rows carry no joined field: the join is the render's, at read.
    assert [record["background"] for record in calls] == [False, False, False, True, True, True, True]
    assert {record["event"] for record in records if record.get("event")} == {"experimental.idle"}
    # The model: the one request `ses_capture` fired, `providerID/id`, on every call the session made
    # after it; `null` on a call in a session that fired none.
    fired = "wafer.ai/GLM-5.3-Flash"
    assert [record["model"] for record in calls] == [fired] * 7
    [modelless] = [record for record in records if record.get("session") == "ses_modelless"]
    assert modelless["model"] is None
    # The child's own idles: the agent and the model its call request named are stamped on each, and
    # each states the background work it was seen with — the first one's shell, the end signal's none.
    [first, end] = [record for record in records if record.get("session") == "ses_child"]
    stamp = {"agent_type": "devpro-go-coder", "model": "reaper/Qwen3.8-Flash-Next"}
    assert ({key: first[key] for key in stamp}, first["background"]) == (stamp, 1)
    assert ({key: end[key] for key in stamp}, end["background"]) == (stamp, 0)

    # `clauses.TEST_PRECONDITION`. The defect (R4): the idle record's stamp grew `background`,
    # `agent_type` and `model` only where a signal carried them, so a record could arrive missing keys;
    # a payload naming no agent persisted the text `"undefined"`; and a title request's agent and model
    # were stamped as the run's. Every event record carries the signal's three keys, `null` where the
    # host reported none, and only a `call` request's fields are the session's.
    events = [record for record in records if record.get("event") is not None]
    idle_keys = {"v", "harness", "at", "session", "event", "trigger", "source", "context_tokens", "transcript"}
    assert [{key for key in record if key not in idle_keys} for record in events] == [
        {"background", "agent_type", "model", "plan", "directives"}
    ] * len(events)
    # The session whose only request was the host's own title request: it names no model or agent, and
    # the call the session made after it names neither, as a claude record with no transcript does.
    worker = [record for record in records if record.get("session") == "ses_worker"]
    [titled] = [record for record in worker if record.get("event") is not None]
    [untitled] = [record for record in worker if record.get("event") is None]
    assert (titled["agent_type"], titled["model"]) == (None, None)
    assert untitled["model"] is None
    # A call request naming no agent: the model stands, the agent is `null` and never `"undefined"`.
    [anonymous] = [record for record in events if record["session"] == "ses_anonymous"]
    assert (anonymous["agent_type"], anonymous["model"]) == (None, "reaper/Qwen3.8-Flash-Next")


def _dispatch_store(root: Path, session: str, at: str, child: str, *, duration_ms: int = 500) -> Path:
    """An opencode store under `root` holding one dispatch record for `session`: the launch
    acknowledgment the capture writes when a `subagent` call returns, its `at` the dispatch moment,
    its `duration_ms` the firing cost, its `background` true, and the child's session id."""
    return _write_store(
        root,
        ".profiler-opencode",
        session,
        at,
        harness="opencode",
        extra={
            "tool": "Agent",
            "name": "devpro-python-coder",
            "duration_ms": duration_ms,
            "child_agent_id": child,
            "child_agent_type": "devpro-python-coder",
            "background": True,
            "model": "wafer.ai/parent-model",
        },
    )


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


def test_a_dispatch_row_reads_the_childs_own_end_and_run(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: a dispatch row reads the firing cost as the child's
    span, or names a model the child never ran, or names an agent the child did not run.

    A parent's dispatch record and its child's store, whose empty-background idle comes 50 s after the
    dispatch: the page's call row takes the child's span, the agent its request named and the child's
    own model, in place of the acknowledgment's 500 ms, its input-derived kind and the parent's model.
    The dispatch record the store holds is unchanged — every fill is the read's."""
    project = tmp_path / "project"
    project.mkdir()
    _dispatch_store(project, "ses_parent", "2026-01-01T00:00:00.000Z", "ses_child")
    _idle_store(project, "ses_child", [("2026-01-01T00:00:50.000Z", 0)])
    dispatch = project / ".devpro-temp" / ".profiler-opencode" / "ses_parent.jsonl"
    before = dispatch.read_text(encoding="utf-8")

    page = _run(_wrapper, "tree", "ses_parent", "--format", "html", cwd=project)

    assert page.returncode == 0, page.stderr
    [call] = page_data(page.stdout)["calls"]
    assert (call["dur"], call["model"], call["running"]) == (50_000, "reaper/Qwen3.8-Flash-Next", None)
    assert dispatch.read_text(encoding="utf-8") == before


def test_an_intermediate_idle_fills_nothing(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: an intermediate idle truncates the child's span.

    A child that idles with a shell still running and idles again 20 s later with none: the join reads
    the latest empty-background idle, so the row's span is the 40 s to that last idle and not the first
    idle's 20 s or the background-laden idle's 30 s, and an idle with background work standing alone
    fills nothing — a parent's row whose child's store holds only such an idle keeps the firing cost."""
    project = tmp_path / "project"
    project.mkdir()
    _dispatch_store(project, "ses_parent", "2026-01-01T00:00:00.000Z", "ses_child")
    _dispatch_store(project, "ses_other", "2026-01-01T00:00:00.000Z", "ses_busy")
    _idle_store(
        project,
        "ses_child",
        [("2026-01-01T00:00:20.000Z", 0), ("2026-01-01T00:00:30.000Z", 1), ("2026-01-01T00:00:40.000Z", 0)],
    )
    _idle_store(project, "ses_busy", [("2026-01-01T00:00:30.000Z", 1)])

    for session, span in (("ses_parent", 40_000), ("ses_other", 500)):
        page = _run(_wrapper, "tree", session, "--format", "html", cwd=project)
        assert page.returncode == 0, page.stderr
        [call] = page_data(page.stdout)["calls"]
        assert (session, call["dur"]) == (session, span)


def test_a_dispatch_whose_child_never_ended_is_not_running(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: a child whose idle never came renders as nothing,
    raises, or is marked running.

    A dispatch record carrying the capture's `background: true` and a child store holding no idle — the
    child killed, or a host delivering none: the page renders the row as the acknowledgment wrote it,
    not `running` — the mark claude's stop join gives a background call that never stopped — and the
    tree's duration column states the firing cost rather than the mark."""
    project = tmp_path / "project"
    project.mkdir()
    _dispatch_store(project, "ses_parent", "2026-01-01T00:00:00.000Z", "ses_killed")
    _idle_store(project, "ses_killed", [])

    page = _run(_wrapper, "tree", "ses_parent", "--format", "html", cwd=project)
    tree = _run(_wrapper, "tree", "--verbose", "ses_parent", cwd=project)

    assert page.returncode == 0, page.stderr
    [call] = page_data(page.stdout)["calls"]
    assert (call["dur"], call["running"], call["model"]) == (500, None, "wafer.ai/parent-model")
    assert tree.returncode == 0, tree.stderr
    assert "500 ms" in tree.stdout


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


def test_a_claude_background_launch_still_running_renders_running(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect (R1): `with_stop`'s `running` branch re-tests the launch
    notice against the result-stripped `call`, which never carries it, and the `async_launched` JSON
    the capture records never matched the notice string either — so a claude background dispatch still
    at work renders as finished, with the launch cost as its duration.

    A launch record as the capture writes it — an `Agent` dispatch begun at its `at`, `background`
    true, its duration the launch cost, `result` the `async_launched` reply, no stop recorded —
    renders `running` in the page's call row and in the tree's duration column, and the launch cost
    never stands as its duration. The test fails on the page's `running` before the fix."""
    project = tmp_path / "project"
    project.mkdir()
    _claude_store(
        project,
        "s-claude",
        "2026-01-01T00:00:00.000Z",
        extra={
            "tool": "Agent",
            "background": True,
            "duration_ms": 1000,
            "result": '{"status":"async_launched","agentId":"a1"}',
        },
    )

    page = _run(_wrapper, "tree", "s-claude", "--format", "html", cwd=project)
    tree = _run(_wrapper, "tree", "s-claude", cwd=project)

    assert page.returncode == 0, page.stderr
    [call] = page_data(page.stdout)["calls"]
    assert (call["background"], call["running"], call["dur"]) == (True, True, 1000)
    assert tree.returncode == 0, tree.stderr
    time, duration = _call_row(tree.stdout)
    assert (len(time.split(":")), duration) == (3, "running")


def test_a_stopped_claude_background_launch_ends_its_running_state(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect (R2): the stop merge keeps the launch record's
    `background` and never ends the running state the launch began, so once a launch renders `running`
    a stopped subagent keeps the mark.

    The same dispatch, its SubagentStop recorded 2.5 s on with `background` still true and no handback:
    the row is not `running`, its `background` stays true as the launch wrote it, and its duration is
    the span from the call's start to the stop, 3 s — not the launch cost and not the stop hook's own
    5 ms. The running mark is the one R1's fix begins putting on an unstopped launch, so this test
    holds the stop path to ending it: with the fix in place, a stop that did not end the mark fails it."""
    project = tmp_path / "project"
    project.mkdir()
    _claude_store(
        project,
        "s-claude",
        "2026-01-01T00:00:00.000Z",
        extra={
            "agent_id": "main",
            "tool": "Agent",
            "child_agent_id": "a1",
            "background": True,
            "duration_ms": 500,
            "result": '{"status":"async_launched","agentId":"a1"}',
            "tool_use_id": "tu-launch",
        },
    )
    _stop_at(project, "s-claude", "2026-01-01T00:00:02.500Z", "a1")

    page = _run(_wrapper, "tree", "s-claude", "--format", "html", cwd=project)
    tree = _run(_wrapper, "tree", "s-claude", cwd=project)

    assert page.returncode == 0, page.stderr
    [call] = page_data(page.stdout)["calls"]
    assert (call["child"], call["background"], call["running"], call["dur"]) == ("a1", True, None, 3000)
    assert tree.returncode == 0, tree.stderr
    time, duration = _call_row(tree.stdout)
    assert (len(time.split(":")), duration) == (3, "3.0 s")


def test_an_opencode_dispatch_is_never_running(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect (R1): an opencode dispatch — its acknowledgment carrying
    `background` true and no stop — reaches the running mark claude's launches get.

    An unjoined opencode dispatch renders the acknowledgement it was written as: `background` true,
    no running mark, its duration the firing cost."""
    project = tmp_path / "project"
    project.mkdir()
    _dispatch_store(project, "ses_parent", "2026-01-01T00:00:00.000Z", "ses_child")

    page = _run(_wrapper, "tree", "ses_parent", "--format", "html", cwd=project)

    assert page.returncode == 0, page.stderr
    [call] = page_data(page.stdout)["calls"]
    assert (call["background"], call["running"], call["dur"]) == (True, None, 500)


def test_a_line_over_the_bound_is_fitted_at_its_root(tmp_path: Path) -> None:
    """`serialize` holds every line to `LINE_LIMIT`, which the torn-tail read relies on: a record whose
    fixed `session` alone is longer than the bound is fitted by clipping that field too, and a line
    already inside the bound is left as it stands. The record measured is the fixture
    `profiler_serialize_record.json` — a dispatch the capture wrote, frozen — so the two bounds are
    that fixture's field lengths."""
    line_limit = 4096
    record = json.loads(fixture_file("profiler_serialize_record.json").read_text(encoding="utf-8"))
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    over = json.loads(
        _run_ts(
            _HERE / "profiler_serialize_runner.ts",
            directory=first,
            stdin=json.dumps({"directory": str(first), "record": record, "sessionLength": 4090}),
        ).stdout
    )
    assert over["bytes"] <= line_limit
    assert over["session"] < 4090
    inside = json.loads(
        _run_ts(
            _HERE / "profiler_serialize_runner.ts",
            directory=second,
            stdin=json.dumps({"directory": str(second), "record": record, "sessionLength": 200}),
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


def _profiler_init(wrapper: Path, project: Path) -> subprocess.CompletedProcess[str]:
    """`profiler init claude` in `project`, through the installed wrapper `wrapper` and the test's
    devpro."""
    return _run(wrapper, "init", "claude", cwd=project)


@pytest.mark.parametrize("launcher", RETIRED_LAUNCHERS)
def test_init_clears_an_older_runs_launcher_and_files(tmp_path: Path, _wrapper: Path, launcher: str) -> None:
    """A committed hook directory holding an older `init`'s launcher — under any name it wrote, the one
    this release retired included — beside `hp.py` and `view.html`: a re-run removes every one of
    them, writes the skill, registers the project's wrapper's command, and leaves no hook directory
    where nothing else stands in it. A committed hook running devpro beside a stale `hp.py` is the
    half-absorbed install."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    hook_dir = project / ".claude" / "harness-profiler"
    hook_dir.mkdir(parents=True)
    for name in (launcher, *RETIRED_HOOK_FILES):
        (hook_dir / name).write_text("an older init's copy\n", encoding="utf-8")

    done = _profiler_init(_wrapper, project)

    assert done.returncode == 0, done.stderr
    assert not hook_dir.exists()
    assert (project / ".claude" / "skills" / "profiler" / "SKILL.md").is_file()
    settings = (project / ".claude" / "settings.json").read_text(encoding="utf-8")
    assert ".claude/skills/devpro/tools/devpro.sh" in settings
    assert "harness-profiler" not in settings


def test_init_renames_a_committed_hook_written_under_a_launcher_name(tmp_path: Path, _wrapper: Path) -> None:
    """A repository whose committed hook spells a launcher name — the file `hp.sh` and the registered
    command running it: `init` removes the file and re-registers the command on the project's committed
    wrapper. The consuming-project migration is the `init`'s, run before the install refreshes."""
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

    done = _profiler_init(_wrapper, project)

    assert done.returncode == 0, done.stderr
    assert not hook_dir.exists()
    settings = settings_file.read_text(encoding="utf-8")
    assert ".claude/skills/devpro/tools/devpro.sh" in settings
    assert "harness-profiler" not in settings


@pytest.mark.parametrize("beside", [[], ["notes.md"]], ids=["alone", "beside-a-file"])
def test_init_removes_the_skill_an_older_init_rendered_under_its_former_name(
    tmp_path: Path, _wrapper: Path, beside: list[str]
) -> None:
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

    done = _profiler_init(_wrapper, project)

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


def test_init_renames_the_repositorys_old_pattern_stores(tmp_path: Path, _wrapper: Path) -> None:
    """A repository holding `.devpro-temp/claude-profiler/` and `.devpro-temp/opencode-profiler/`:
    `init` moves each to its `.profiler-*` name and names it, the same migration an install runs. A
    committed-hook repository that migrates nowhere goes dark the moment its hook records on."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    claude = _write_store(project, "claude-profiler", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")
    opencode = _write_store(project, "opencode-profiler", "s-opencode", "2026-01-01T00:00:00.000Z", harness="opencode")

    done = _profiler_init(_wrapper, project)

    assert done.returncode == 0, done.stderr
    stores = project / ".devpro-temp"
    assert sorted(path.name for path in stores.iterdir()) == [".profiler-claude", ".profiler-opencode"]
    assert f"renamed {claude} → {stores / '.profiler-claude'}" in done.stdout
    assert f"renamed {opencode} → {stores / '.profiler-opencode'}" in done.stdout
    assert sorted(path.name for path in (stores / ".profiler-opencode").iterdir()) == ["s-opencode.jsonl"]


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
    from this feed."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(
        project,
        ".profiler-claude",
        "s-claude",
        "2026-01-01T00:00:00.000Z",
        harness="claude",
        records=2,
        extra={"model": "claude-opus-4-5"},
    )
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

    with _serve(cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        feed = json.loads(_fetch(f"{url}api/traces"))
        page = _fetch(f"{url}page/s-claude")

    assert feed == [
        {
            "harness": "claude",
            "id": "s-claude",
            "models": ["claude-opus-4-5"],
            "records": 2,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:00.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:01.000Z"),
            "span": 1,
            "plan": None,
            "directives": None,
            "unreviewed": False,
        },
        {
            "harness": "opencode",
            "id": "s-opencode",
            "models": [],
            "records": 1,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:05.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:05.000Z"),
            "span": 0,
            "plan": None,
            "directives": None,
            "unreviewed": False,
        },
        {
            "harness": "opencode",
            "id": "s-dispatcher",
            "models": [],
            "records": 1,
            "agents": 1,
            "first": _epoch_ms("2026-01-01T00:00:06.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:06.000Z"),
            "span": 0,
            "plan": None,
            "directives": None,
            "unreviewed": False,
        },
        {
            "harness": "opencode",
            "id": "s-child",
            "models": [],
            "records": 2,
            "agents": 0,
            "first": _epoch_ms("2026-01-01T00:00:07.000Z"),
            "last": _epoch_ms("2026-01-01T00:00:08.000Z"),
            "span": 1,
            "plan": None,
            "directives": None,
            "unreviewed": False,
            "dispatcher": {"session": "s-dispatcher", "name": "devpro-coder", "tool": "Agent"},
        },
    ]
    # The page file is static: the rows' empty table, no session's row, and every column heading a
    # row states — the layer's `--zebra`, which the layer switches with the color scheme itself, so
    # the template carries no second rule for it.
    assert '<tbody id="rows"></tbody>' in index and 'href="/page/' not in index
    # The header and the row script agree on the table's columns: every head carries a `col-*` class of
    # its own, and the span the script gives a full-width row is that many. A column added to the head
    # and not to the script's span, or to neither the head nor the widths, overruns the table.
    head_classes = index_head_classes(index)
    assert len(head_classes) == len(set(head_classes)) == index_row_colspan(index)
    # Each column's share of the table comes from the page's own stylesheet, beside the header's class,
    # and the table's layout is the fixed one that gives that share to header and body alike.
    assert re.search(r"table \{ border-collapse: collapse; table-layout: fixed; \}", index)
    # The controls: a box for the child rows and one per harness — child rows off by default, so the
    # child-rows box ships without `checked` while the two harness boxes stay checked, the page
    # opening on the dispatches — and the notice a failed feed names itself in, standing empty and hidden.
    assert re.search(r'<input type="checkbox" id="child-rows" name="child-rows" value="on">', index)
    for control in ('id="harness-claude"', 'id="harness-opencode"'):
        assert re.search(rf'<input type="checkbox" {control} [^>]*checked>', index), control
    assert re.search(r'<p id="notice" class="notice" role="alert" hidden></p>', index)
    assert re.search(r"tr:nth-child\(odd\) td \{ background: var\(--zebra\); \}", index)
    assert "prefers-color-scheme: dark" not in index.split("<style>", 1)[1].split("</style>", 1)[0]
    assert page_data(page)["session"] == "s-claude"


def test_a_session_naming_itself_as_a_child_is_drawn_once_in_its_own_place(tmp_path: Path, _wrapper: Path) -> None:
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

    with _serve(cwd=project) as url:
        feed = json.loads(_fetch(f"{url}api/traces"))

    assert [entry["id"] for entry in feed] == ["s-self"]
    assert "dispatcher" not in feed[0]


def test_a_claude_child_agent_id_groups_no_session(tmp_path: Path, _wrapper: Path) -> None:
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

    with _serve(cwd=project) as url:
        feed = json.loads(_fetch(f"{url}api/traces"))
        page = _fetch(f"{url}page/s-claude")

    assert [entry["id"] for entry in feed] == ["s-claude", "s-named"]
    assert not any("dispatcher" in entry for entry in feed)
    assert page_data(page)["calls"][0]["child"] == "s-named"
    assert page_data(page)["calls"][0]["childPage"] is None


def test_the_served_index_lists_its_own_project_under_a_foreign_project_dir(tmp_path: Path, _wrapper: Path) -> None:
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

    with _serve(cwd=project, env={"CLAUDE_PROJECT_DIR": str(foreign)}) as url:
        feed = json.loads(_fetch(f"{url}api/traces"))

    assert [entry["id"] for entry in feed] == ["s-here"]


def test_the_served_page_is_the_html_the_file_flow_writes(tmp_path: Path, _wrapper: Path) -> None:
    """One session's `/page/<id>` carries the file flow's page data: the JSON the page template
    inlines at its data slot is the payload `tree --format html` inlines, and the served page names
    the shared layer's one file where the render inlines its text — the two carriers' one difference."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    with _serve(cwd=project) as url:
        served = _fetch(f"{url}page/s-claude")

    printed = _run(_wrapper, "tree", "s-claude", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr
    assert page_data(served) == page_data(printed.stdout)
    # The serve path names the layer's one file where the file flow inlines its text: one source, two
    # carriers.
    assert served.count(LAYER_LINK) == 1 and SHARED_CSS not in served


def test_the_standalone_render_carries_the_shared_layer_and_the_legend_once(tmp_path: Path, _wrapper: Path) -> None:
    """The page `tree --format html` prints carries the presentation layer's own text, inlined whole,
    and the frame band's legend exactly once — the deco the served page carries as its own text,
    here the render's: the standalone page names no view active to a live dashboard, so its band
    heads with the legend alone, no dispatcher and no way back. A render that inlines a second layer,
    or carries the legend twice, is the reskin the shared layer forbids."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    printed = _run(_wrapper, "tree", "s-claude", "--format", "html", cwd=project)

    assert printed.returncode == 0, printed.stderr
    assert SHARED_CSS in printed.stdout
    assert printed.stdout.count("How to read this") == 1
    assert 'class="site-nav' in printed.stdout and 'class="frame-band' in printed.stdout


def test_the_standalone_render_carries_the_decoration_its_pages_script_reads(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a `tree --format html` page whose own script calls
    the deco's notation, `globalThis.devproFormat`, while the page carries neither the deco's link
    nor its text — a file cannot link a server's origin, so the page's script throws before the
    diagram and every time draw, and the page it prints is a table of nothing.

    The render inlines the deco's text where the served page links the file, and the page's script
    reads the global from it."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    printed = _run(_wrapper, "tree", "s-claude", "--format", "html", cwd=project)

    assert printed.returncode == 0, printed.stderr
    assert DECO_INLINE in printed.stdout
    assert '<script src="/profiler/deco.js"></script>' not in printed.stdout
    assert "const { localDay, clock, dur, scaled } = globalThis.devproFormat;" in printed.stdout


# The form a page script's body opens with: an IIFE, its body inside and its helpers private to it —
# the arrow the index's script and the deco use, the `function` spelling an equivalent.
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


def test_every_page_script_wraps_its_body_in_an_iife() -> None:
    """`clauses.TEST_PRECONDITION`. The defect: `view.html`'s script stood at the page's top level,
    its helpers — `padTwo`, `localDay`, `localClock` — in the global scope classic scripts share with
    the deco's, so the next helper of one of those names would redeclare a `const` and the session
    page would draw nothing. Every script the pages run wraps its body in an IIFE; the shipped pages
    carrying an inline script are `view.html` and the `INDEX` template, and the scripts they load by
    file — the deco and the board's — are in the same shared scope and wrap theirs the same way. The
    deco is the one exception to the bare IIFE, and it is the one name the design makes public: the
    notation the pages call, `globalThis.devproFormat`."""
    pages = {
        "view.html": (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8"),
        "INDEX": INDEX,
    }
    for name, page in pages.items():
        bodies = _inline_script_bodies(page)
        assert bodies, f"{name} carries no inline script"
        assert all(_opens_an_iife(body) for body in bodies), f"{name}'s script does not open an IIFE"
    for name in ("devpro/profiler/deco.js", "devpro/kanban/assets/board.js"):
        assert _opens_an_iife((_PACKAGE_ROOT / name).read_text(encoding="utf-8")), f"{name} does not open an IIFE"
    deco = (_PACKAGE_ROOT / "devpro" / "profiler" / "deco.js").read_text(encoding="utf-8")
    assert re.findall(r"^globalThis\.(\w+)", deco, re.M) == ["devproFormat"], "the deco publishes one name"


def test_the_served_index_links_the_shared_layers_own_text(tmp_path: Path, _wrapper: Path) -> None:
    """`/profiler/` names the board's stylesheet at the path the board panel serves it: the index
    carries no copy of the layer itself, and its one stylesheet link is the board panel's link line.
    A profiler page carrying a palette of its own is the second reskin the design forbids, the board
    and the profiler showing two identities for one site; a link to a path nothing serves is a page
    styled by nothing."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    with _serve(cwd=project) as url:
        index = _fetch(f"{url}profiler/")
        [linked] = re.findall(r'<link rel="stylesheet" href="([^"]+)">', index)

    assert LAYER_LINK == f'<link rel="stylesheet" href="{linked}">'
    assert SHARED_CSS not in index


def test_every_script_spelling_of_the_prefix_is_the_services_one(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a page's script carrying the set's prefix as its
    own literal — a re-stringed `devpro-` in `view.html`'s `shownName`, or in the index's row strip,
    beside `pages.agent_prefix_line` — so a change to the install's one name leaves the page dropping a
    prefix the set's agents no longer carry, silently, the rendering's own text still saying it does.

    The lane is the engine's reading of both scripts: each reads a name with no prefix line standing
    and fails to load, then loads beside the `AGENT_PREFIX` line and drops the Agent call's prefix
    while keeping a Bash call's name whole. The page's own spelling is the install's one name — the
    line's prefix equals `components.NAME` and `call_label` drops it. A missing `bun` fails rather
    than skips, as the pages' other engine checks do."""
    import shutil

    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the prefix's scripts cannot be read without it")
    index = index_html()
    view = (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8")
    assert AGENT_PREFIX_MARK in view

    # The pages' own spelling is the install's one name, and the label drops exactly it.
    assert AGENT_PREFIX == f"{NAME}-"
    assert call_label("Agent", f"{AGENT_PREFIX}coder") == "coder (agent)"

    # `shown` is the index's child-row name, over the row's dispatcher; `label` is a session page's
    # call label, over the two helpers it reads.
    reads = {
        "index": "const dispatched = { name: 'devpro-coder', tool: 'Agent' };\n"
        "const AGENT_TOOL = 'Agent';\n"
        + re.search(r"^    const shown = .*$", index, re.M).group(0)
        + "\nconsole.log(shown);",
        "view": "\n".join(
            re.search(pattern, view, re.M).group(0)
            for pattern in (
                r"^const shownName = .*$",
                r"^const KIND_WORDS = .*$",
                r"^const kindWord = .*$",
                r"^const label = .*$",
            )
        )
        + "\nconsole.log(label('Agent', 'devpro-coder') + ' / ' + label('Bash', 'devpro-tool'));",
    }
    bound = AGENT_PREFIX_LINE + "\n"
    for page, read in reads.items():
        (tmp_path / f"{page}-unbound.js").write_text(read, encoding="utf-8")
        (tmp_path / f"{page}-bound.js").write_text(bound + read, encoding="utf-8")

    # Each page's unbound module is the engine's `ReferenceError`; its bound one reads the name.
    for page in reads:
        unbound = subprocess.run(["bun", str(tmp_path / f"{page}-unbound.js")], capture_output=True, text=True)
        assert "ReferenceError" in unbound.stderr, unbound.stderr
    run = subprocess.run(
        ["bun", "-e", "".join(f"await import({str(tmp_path / (page + '-bound.js'))!r});\n" for page in reads)],
        capture_output=True,
        text=True,
    )

    assert run.returncode == 0, run.stderr
    assert run.stdout.split("\n")[:2] == ["coder", "coder (agent) / devpro-tool (Bash)"]


def test_the_decoration_states_durations_in_the_one_notation(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is the two notations the index and the call tree each
    carried — `1129 s` in one column and `3h 2m` in the other, and `2 ms` where a call took none —
    so one duration read two ways on two pages.

    The deco's one formatter reads a duration in milliseconds, no space between number and unit:
    `0s` at zero, `217ms` below the second, `4.2s` with one decimal below ten seconds, `48s` below
    the minute, `18m 49s` below the hour (`18m` when the seconds are zero) and `1h 2m` from the hour
    (`1h` when the minutes are zero). The file runs whole against a stub document holding no nav, so
    the deco's own body returns at its first element and the notation is what the page scope carries.
    A missing bun fails rather than skips, as the file's other engine readings do."""
    import shutil

    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the deco's notation cannot be read without it")
    deco = (_PACKAGE_ROOT / "devpro" / "profiler" / "deco.js").read_text(encoding="utf-8")
    script = tmp_path / "dur.js"
    script.write_text(
        "globalThis.document = { getElementById: () => null, querySelector: () => null };\n"
        + deco
        + "\nconsole.log([0, 217, 4200, 48000, 1129000, 1080000, 3720000, 3600000].map(devproFormat.dur).join(' '));\n",
        encoding="utf-8",
    )

    run = subprocess.run(["bun", str(script)], capture_output=True, text=True, stdin=subprocess.DEVNULL)

    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == "0s 217ms 4.2s 48s 18m 49s 18m 1h 2m 1h"


def test_a_script_naming_no_name_renders_no_word(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is `shownName` returning the name it was handed for a
    call recorded with none, so the grouped-skills label — the one site that reads the name as a
    word of its own, its fallback guarded on the string — renders `undefined` in the line a reader
    reads: `3 skills: undefined, …`.

    A call with no name renders `''`, the empty word a caller's own fallback fills, in the same
    engine reading as the prefix lane."""
    import shutil

    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the prefix's scripts cannot be read without it")
    view = (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8")
    [nameless] = re.findall(r"^const shownName = .*$", view, re.M)
    calls = "const D = { calls: [{ tool: 'Skill', name: null }, { tool: 'Skill', name: 'devpro-docdicer' }] };\n"
    names = "const names = D.calls.map((c) => shownName(c.tool, c.name) || 'skill');\n"
    (tmp_path / "nameless.js").write_text(
        f"{AGENT_PREFIX_LINE}\n{nameless}\n{calls}{names}console.log(names.join(','));\n", encoding="utf-8"
    )

    run = subprocess.run(["bun", str(tmp_path / "nameless.js")], capture_output=True, text=True)

    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == "skill,devpro-docdicer"


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


def test_the_readers_read_a_copy_of_a_store_as_no_store_at_all(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`: a copy of a store beside it reads twice — both of the profiler's
    readers, `list_sessions` and `read_sessions`, listing the one recorded session once per store the
    `.profiler-*` glob matched, which is the doubled rows the served index drew.

    A store and a copy of it under one project, then a directory of no store's name beside them: each
    reader reads the session once, names the copied directory unreadable to neither, and a directory
    nothing wrote is read by neither — a name is a store only where it is exactly the one a harness's
    capture writes."""
    project = tmp_path / "project"
    project.mkdir()
    store = _write_store(project, ".profiler-claude", "s-only", "2026-01-01T00:00:00.000Z", harness="claude")
    shutil.copytree(store, project / ".devpro-temp" / ".profiler-claude-copy")
    (project / ".devpro-temp" / ".profiler-claude-old").mkdir()
    (project / ".devpro-temp" / ".profiler-broken").mkdir()

    assert [session["id"] for session in list_sessions(project)] == ["s-only"]
    assert [session["id"] for session in read_sessions(project)] == ["s-only"]


def test_an_unrecorded_session_id_is_a_404_and_no_traceback(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is `/page/<id>` for an id no store records answering
    HTTP 500 from the handler's traceback instead of the 404 the view answers a page it does not
    serve — on a tree whose stores are readable, the read that finds no match returns `None`.

    The tree holds one recorded session, readable, and no locked store: the unknown id's page is a
    404, as the recorded session's page is a 200."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")

    with _serve(cwd=project) as url:
        assert _fetch(f"{url}page/s-claude")
        with pytest.raises(urllib.error.HTTPError) as missing:
            _fetch(f"{url}page/s-unrecorded")

    assert missing.value.code == 404


@pytest.mark.parametrize(
    "name, shown",
    [
        pytest.param("devpro-coder", "coder (agent)", id="set-prefix"),
        pytest.param("reviewer", "reviewer (agent)", id="plain"),
        pytest.param("devpro-", "agent", id="prefix-alone"),
    ],
)
def test_a_rendered_call_label_drops_the_set_prefix(name: str, shown: str) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a tree line rendering the record's name as stored,
    `devpro-coder (agent)`, repeating the set's prefix on every dispatch a reader already knows is
    the devpro set's.

    The label drops `devpro-` at the render of an Agent call and keeps every other name as recorded; a
    name that is the prefix alone renders as no name, which is the call's kind."""
    assert call_label("Agent", name) == shown


def test_a_call_that_is_not_an_agent_keeps_its_recorded_name() -> None:
    """`clauses.TEST_PRECONDITION`: the defect is an unconditional drop, a Bash command recorded as
    `devpro-check-plan` rendering as `check-plan (Bash)` — the page misstating the command that ran,
    whose name merely begins the way the set's agent names do.

    The drop is the Agent tool's: every other tool's name is rendered as recorded."""
    assert call_label("Bash", "devpro-tool") == "devpro-tool (Bash)"
    assert call_label("Skill", "devpro-docdicer") == "devpro-docdicer (skill)"


@pytest.fixture
def kolkata(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """The machine pinned to a zone four and a half hours ahead of UTC for one test, its zone back
    afterwards whether the test passed or failed."""
    monkeypatch.setenv("TZ", "Asia/Kolkata")
    time.tzset()
    yield
    time.tzset()


def test_the_text_tree_draws_a_moment_in_the_machines_zone(kolkata: None) -> None:
    """`clauses.TEST_PRECONDITION`: the defect is the text tree's time column and session stamps
    reading UTC — a reader four and a half hours ahead sees a call at midnight as `18:30:00` of the
    day before.

    The zone is pinned with `TZ` and read through `time.tzset`, the machine's zone being whatever the
    runner carries; Asia/Kolkata's half-hour offset also fails a formatter that drops the minutes."""
    midnight = _epoch_ms("2026-01-01T00:00:00.000Z")
    assert midnight is not None
    assert clock(midnight) == "05:30:00"
    assert stamp(midnight) == "2026-01-01 05:30:00"


def test_an_install_renames_an_old_pattern_store_and_a_second_install_touches_nothing(tmp_path: Path) -> None:
    """A project holding `.devpro-temp/claude-profiler/`: the install moves it to `.profiler-claude/`,
    contents and all, naming the rename in its report, and a second install reports the target up to
    date and leaves the store alone. A rename left undone leaves the store outside the readers'
    stores, so the project's recorded history vanishes from the index at the upgrade with nothing
    saying it happened."""
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
    assert renamed in store_directories(project)
    assert [session["id"] for session in read_sessions(project)] == ["s-old"]

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
    launcher = _installed_wrapper(tmp_path / "harness")
    printed = _run(launcher, "tree", "s-claude", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr
    for mark in (LAYER_MARK, DECO_MARK, DATA_MARK, BAND_LEGEND, DISPATCHED_MARK, RETURN_MARK):
        assert mark not in printed.stdout, f"{mark} left standing in the rendered page"
    with _serve(cwd=project) as url:
        page = _fetch(f"{url}page/s-claude")
        index = _fetch(f"{url}profiler/")
    for mark in (LAYER_MARK, DECO_MARK, DATA_MARK, BAND_LEGEND, DISPATCHED_MARK, RETURN_MARK):
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
