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

from devpro.profiler.capture import mask
from devpro.profiler.hooks import RETIRED_HOOK_FILES, launcher_resource
from tests.test_devpro_install import _PROFILER, _claude_plugin, _definition_install

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
        env={**os.environ, "HP_DEVPRO": str(_devpro_shim(cwd))},
        check=False,
    )


_SERVE_URL = re.compile(r"^http://127\.0\.0\.1:\d+/$", re.MULTILINE)


@contextmanager
def _serve(launcher: Path, *, cwd: Path, env: dict[str, str] | None = None) -> Iterator[str]:
    """The dashboard, through the launcher's `devpro`, as `_run` runs it, as a context manager
    yielding the URL its traces panel is at.

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
        env={**os.environ, "HP_DEVPRO": str(_devpro_shim(cwd)), **(env or {})},
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
def test_a_launcher_finding_no_devpro_captures_silently_and_reports_otherwise(tmp_path: Path, command: str) -> None:
    """With no devpro the finder can resolve, `capture` drains stdin and exits 0 writing nothing, and every
    other subcommand reports on stderr and exits 1: a capture that reports or exits nonzero blocks the
    tool call that fired it, under the harness hook error policy, and a tree that says nothing leaves the
    operator no line naming the one dependency to install."""
    launcher = _launcher(tmp_path / "harness")
    payload = json.dumps({"hook_event_name": "PostToolUse", "session_id": "s-none", "tool_name": "Bash"})
    project = tmp_path / "project"
    project.mkdir()
    done = subprocess.run(
        ["sh", str(launcher), command],
        input=payload,
        capture_output=True,
        text=True,
        cwd=project,
        env={**os.environ, "HP_DEVPRO": str(tmp_path / "absent")},
        check=False,
    )

    if command == "capture":
        assert (done.returncode, done.stdout, done.stderr) == (0, "", "")
    else:
        assert done.returncode == 1
        assert done.stdout == ""
        assert "HP_DEVPRO" in done.stderr
    assert not (project / ".devpro-temp").exists()


def test_a_tree_renders_an_opencode_store_beside_the_claude_capture(tmp_path: Path) -> None:
    """A session in each harness's store under one project, and one `tree <id>` per store renders it:
    the read that walks every `.profiler-*` store, whose revert to claude's alone loses the opencode
    session silently."""
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
            )
        )
        + "\n",
        encoding="utf-8",
    )

    opencode_tree = _run(launcher, "tree", "--verbose", "s-opencode", cwd=project)
    assert opencode_tree.returncode == 0, opencode_tree.stderr
    assert "make test" in opencode_tree.stdout
    claude_tree = _run(launcher, "tree", "--verbose", "s-profiler", cwd=project)
    assert claude_tree.returncode == 0, claude_tree.stderr
    assert "ls" in claude_tree.stdout


def _bun() -> str:
    if shutil.which("bun") is None:
        pytest.fail("bun is not on PATH: the opencode capture cannot run without it")
    return "bun"


def _run_ts(script: Path, *, directory: Path, arg: str | None = None) -> subprocess.CompletedProcess[str]:
    """One of the TypeScript runners under `tests/`, given the scratch directory it writes into."""
    done = subprocess.run(
        [_bun(), str(script), *([arg] if arg else [])],
        input=json.dumps({"directory": str(directory)}),
        capture_output=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    return done


def test_the_opencode_capture_records_every_fired_call(tmp_path: Path) -> None:
    """The shipped `profiler.ts` through a stub plugin context: a completed call, a failed one, a
    skill call, a subagent dispatch and the session's idle each append their record; the failed call's
    text is its `Tool.Error`'s message, the skill and subagent carry the host's own names, a dispatch
    carries the kind its response reports or else its own agent, under either of the host's spellings
    for the tool, and the one call whose `execute.after` never fires drops its start at the idle."""
    project = tmp_path / "project"
    project.mkdir()
    run = _run_ts(_HERE / "profiler_capture_runner.ts", directory=project)
    out = json.loads(run.stdout)
    records = out["records"]

    calls = [record for record in records if record.get("event") is None]
    assert [(record["tool"], record["name"]) for record in calls] == [
        ("shell", "printf 'hi\\n'"),
        ("shell", "rm -rf /"),
        ("Skill", "show-profile"),
        ("Agent", "devpro-python-coder"),
        ("Agent", "devpro-architect"),
        ("Agent", "devpro-tech-writer"),
    ]
    assert calls[0]["result"] == "hi"
    assert calls[1]["ok"] is False
    assert calls[1]["result"] == "The user rejected this tool call"
    assert calls[2]["result"] == "loaded"
    assert calls[3]["result"] == "ses_child"
    assert calls[3]["child_agent_type"] == "devpro-python-coder"
    assert calls[4]["child_agent_type"] == "fork"
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
    assert (project / ".claude" / "skills" / "show-profile" / "SKILL.md").is_file()
    assert "harness-profiler/hp.sh" in (project / ".claude" / "settings.json").read_text(encoding="utf-8")


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


def _write_store(root: Path, store: str, session: str, at: str, *, harness: str, records: int = 1) -> Path:
    """A `.profiler-*` store under `root`, holding `records` call records for one session, a second
    apart from the moment `at` names."""
    directory = root / ".devpro-temp" / store
    directory.mkdir(parents=True)
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
    served index carries a row for every recorded session, each stating the harness and count its own
    records hold and its first and last moment, and linking to that session's page; an index that
    omits a session the stores hold, or states one the store does not, drops or invents what the
    records say."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    _write_store(project, ".profiler-opencode", "s-opencode", "2026-01-01T00:00:05.000Z", harness="opencode")

    with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
        index = _fetch(url)
        page = _fetch(f"{url}page/s-claude")

    rows = re.findall(r"<tr>(?!<th>).*?</tr>", index)
    assert [re.search(r'href="[^"]*/page/([^"]+)"', row).group(1) for row in rows] == ["s-claude", "s-opencode"]
    assert "claude" in rows[0] and "2 records" in rows[0]
    assert "2026-01-01 00:00:00 UTC to 2026-01-01T00:00:01.000Z" in rows[0]
    assert "opencode" in rows[1] and "1 records" in rows[1]
    assert "2026-01-01 00:00:05 UTC to 2026-01-01T00:00:05.000Z" in rows[1]
    assert _page_data(page)["session"] == "s-claude"


def test_the_served_index_lists_its_own_project_under_a_foreign_project_dir(tmp_path: Path) -> None:
    """`CLAUDE_PROJECT_DIR` at another project, as a claude shell sets it, while the dashboard runs in
    this one: the index lists this project's sessions; an index that follows the variable serves the
    other project's stores, which for a terminal-launched server is the wrong repository."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    _write_store(project, ".profiler-claude", "s-here", "2026-01-01T00:00:00.000Z", harness="claude")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    _write_store(foreign, ".profiler-claude", "s-elsewhere", "2026-01-01T00:00:00.000Z", harness="claude")

    with _serve(_launcher(tmp_path / "harness"), cwd=project, env={"CLAUDE_PROJECT_DIR": str(foreign)}) as url:
        index = _fetch(url)

    assert "/page/s-here" in index
    assert "/page/s-elsewhere" not in index


def test_the_served_index_states_an_unreadable_store(tmp_path: Path) -> None:
    """One `.profiler-*` store the glob finds and cannot read, beside one it can: the index answers
    2xx, names the unreadable store as such, and still lists the readable store's session, and the
    unreadable store's own page is a 404 rather than a traceback; an index that lets the one bad
    directory blank the page or raise out of the handler is the defect the stated row replaces."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".devpro-temp").mkdir()
    locked = _write_store(project, ".profiler-broken", "s-broken", "2026-01-01T00:00:00.000Z", harness="claude")
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude")
    os.chmod(locked, 0o000)
    try:
        with _serve(_launcher(tmp_path / "harness"), cwd=project) as url:
            index = _fetch(url)
            with pytest.raises(urllib.error.HTTPError) as missing:
                _fetch(f"{url}page/s-broken")
    finally:
        os.chmod(locked, 0o755)

    assert ".profiler-broken is unreadable" in index
    assert "/page/s-claude" in index
    assert missing.value.code == 404


def test_the_served_page_is_the_html_the_file_flow_writes(tmp_path: Path) -> None:
    """One session's `/page/<id>` is the bytes `tree --format html` prints for it, less the one
    trailing newline `print` adds: the dashboard's traces panel shows the page the file-redirect flow
    produces, and a served page that diverges from it — rebuilt another way, or another session's —
    is the defect: the user's two routes would show two pages."""
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    launcher = _launcher(tmp_path / "harness")

    with _serve(launcher, cwd=project) as url:
        served = _fetch(f"{url}page/s-claude")

    printed = _run(launcher, "tree", "s-claude", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr
    assert served == printed.stdout.removesuffix("\n")


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
