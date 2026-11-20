"""The activity profiler's contract, driven through the launcher the install copies: one capture
writes a schema-2 record, `tree --format html`'s page data carries the keys `view.html` parses, and
the installed tool is the source's bytes. It fails on the port defect that renames or drops a record
field the page data carries — the rename or drop ships green and renders an empty page.

Two records the port itself owns: `tree` renders an opencode session's store beside the claude
capture's — the split that is the capture's purpose, and whose loss the single-store read would not
show; and the opencode capture, driven by `tests/profiler_capture_runner.ts` through the shipped
`profiler.ts`, writes a record for every call it is fired for, a failed one carrying its error's text.
`test_the_two_masks_redact_alike` holds the two harnesses' masking to one sample list, since
JavaScript's `\\w` is ASCII where Python's is not.

The package is imported from the repository root, which `just test` puts on PYTHONPATH.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from devpro.install import HARNESS_RESOURCES_SOURCE
from devpro.install_base import PACKAGE_ROOT
from tests.test_devpro_install import _PROFILER, _claude_plugin, _definition_install

_HERE = Path(__file__).parent
# The samples both masking implementations are held to: the credential shapes hp.py's SECRETS are
# written for, and the same shapes holding a non-ASCII letter, where JavaScript's `\w` stops matching.
_MASK_SAMPLES = "mask_samples.txt"

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


def _launcher(tmp_path: Path) -> Path:
    """The installed launcher: the claude install into `tmp_path`, where the payload lands."""
    root = tmp_path / ".claude"
    root.mkdir()
    _definition_install(root, project_root=tmp_path)
    return _claude_plugin(root) / _PROFILER / "hp.sh"


def _run(launcher: Path, *args: str, cwd: Path, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(launcher), *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, "HP_PYTHON": sys.executable},
        check=False,
    )


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
    launcher = _launcher(tmp_path)
    capture = _run(launcher, "capture", "claude", cwd=project, stdin=_PAYLOAD)
    assert capture.returncode == 0, capture.stderr
    assert capture.stdout == "" and capture.stderr == ""
    trace = project / ".devpro-temp" / "claude-profiler" / "s-profiler.jsonl"
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


def test_the_installed_profiler_is_the_sources_bytes(tmp_path: Path) -> None:
    """The copy that ships is the copy the repository holds: no stamp or reflow lands in `hp.py` on
    its way through the package data."""
    launcher = _launcher(tmp_path)
    source = PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "claude" / "profiler" / "hp.py"
    assert (launcher.parent / "hp.py").read_bytes() == source.read_bytes()


def test_a_tree_renders_an_opencode_store_beside_the_claude_capture(tmp_path: Path) -> None:
    """A session in each harness's store under one project, and one `tree <id>` per store renders it:
    the read that walks every `*-profiler` store, whose revert to claude's alone loses the opencode
    session silently."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    launcher = _launcher(tmp_path)
    capture = _run(launcher, "capture", "claude", cwd=project, stdin=_PAYLOAD)
    assert capture.returncode == 0, capture.stderr
    # A record the opencode capture writes, holding what `tree`'s render reads: an event at start and
    # the call, which only --verbose draws.
    opencode = project / ".devpro-temp" / "opencode-profiler" / "s-opencode.jsonl"
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
    text is its `Tool.Error`'s message, the skill and subagent carry the host's own names, and the one
    call whose `execute.after` never fires drops its start at the idle."""
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
    ]
    assert calls[0]["result"] == "hi"
    assert calls[1]["ok"] is False
    assert calls[1]["result"] == "The user rejected this tool call"
    assert calls[2]["result"] == "loaded"
    assert calls[3]["result"] == "ses_child"
    assert [record["event"] for record in records if record.get("event")] == ["experimental.idle"]
    assert (out["startedBeforeIdle"], out["startedAfterIdle"]) == (1, 0)


def test_the_two_masks_redact_alike(tmp_path: Path) -> None:
    """hp.py's `mask` and the port's, over one sample list: each sample's masked text is the same on
    both sides, the non-ASCII credential included."""
    samples = (_HERE / _MASK_SAMPLES).read_text(encoding="utf-8").splitlines()
    spec = importlib.util.spec_from_file_location(
        "hp", PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / "claude" / "profiler" / "hp.py"
    )
    hp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hp)
    run = _run_ts(_HERE / "profiler_mask_runner.ts", directory=tmp_path, arg=str(_HERE / _MASK_SAMPLES))
    ported = [json.loads(line) for line in run.stdout.splitlines()]

    assert ported == [hp.mask(sample) for sample in samples]
