"""record• payload• bytes• model"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from devpro.profiler.pages import DATA_MARK
from tests.conftest import page_data

from .conftest import (
    _CALL_KEYS,
    _HERE,
    _PACKAGE_ROOT,
    _PAGE_KEYS,
    _PAYLOAD,
    _RECORD_FIELDS,
    _installed_wrapper,
    _plan,
    _run,
    _run_ts,
    _write_store,
)


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


def test_a_capture_copies_the_whole_stamp_off_the_sessions_store(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: the copy off the store carried only the stamp keys the
    earliest record happened to hold, so a session that started with no plan gained a `plan` key the
    moment one arrived — the taken-once contract broken on the second record.

    A store already holding two records of the session, both stamped with one digest and no plan,
    and a project whose plan and directive stand now: the record the capture appends next carries that
    digest and still no `plan`, and the digest gains a manifest whose per-file digests are recomputed
    from the files as they stand — the state the store's digest was taken from, as a manifest may
    postdate the digest it is keyed by."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    digest = "0" * 64
    directory = project / ".devpro-temp" / ".profiler-claude"
    directory.mkdir(parents=True)
    stored = [
        {
            "v": 4,
            "harness": "claude",
            "at": f"2026-01-01T00:00:0{k}.000Z",
            "session": "s-profiler",
            "directives": digest,
        }
        for k in range(2)
    ]
    (directory / "s-profiler.jsonl").write_text(
        "".join(f"{json.dumps(record)}\n" for record in stored), encoding="utf-8"
    )
    _plan(project, "a plan that arrived late")
    definition = project / ".opencode" / "plugins" / "devpro" / "agents" / "coder.md"
    definition.parent.mkdir(parents=True)
    definition.write_text("<!-- !GENERATED! from devpro/definitions/agents/coder.py -->\nbody\n", encoding="utf-8")

    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD)

    assert capture.returncode == 0, capture.stderr
    records = [json.loads(line) for line in (directory / "s-profiler.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(record.get("plan"), record["directives"]) for record in records] == [(None, digest)] * 3
    expected = hashlib.sha256(
        json.dumps(
            sorted(
                {
                    ".opencode/plugins/devpro/agents/coder.md": hashlib.sha256(definition.read_bytes()).hexdigest()
                }.items()
            ),
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()
    manifest = project / ".devpro-temp" / ".profiler-directives" / f"{expected}.json"
    assert sorted(json.loads(manifest.read_text(encoding="utf-8"))) == [".opencode/plugins/devpro/agents/coder.md"]


def test_a_capture_leaves_a_store_of_unstamped_records_unstamped(tmp_path: Path, _wrapper: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: a store holding records with neither stamp field was
    stamped fresh on the next record, so one session's records disagreed on the context they ran
    under while the leaf named a store holding no stamped record legacy and left unstamped.

    A store already holding a record with neither field, and a project whose plan and directive stand
    now: the record the capture appends next carries neither field — it writes no fresh stamp beside
    records the store already holds — and the fresh digest's manifest stands beside them, as a
    manifest may postdate the digest it is keyed by."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    _plan(project, "a plan")
    definition = project / ".opencode" / "plugins" / "devpro" / "agents" / "coder.md"
    definition.parent.mkdir(parents=True)
    definition.write_text("<!-- !GENERATED! from devpro/definitions/agents/coder.py -->\nbody\n", encoding="utf-8")
    directory = project / ".devpro-temp" / ".profiler-claude"
    directory.mkdir(parents=True)
    legacy = {"v": 1, "harness": "claude", "at": "2026-01-01T00:00:00.000Z", "session": "s-profiler", "tool": "Bash"}
    (directory / "s-profiler.jsonl").write_text(f"{json.dumps(legacy)}\n", encoding="utf-8")

    capture = _run(_wrapper, "capture", "claude", cwd=project, stdin=_PAYLOAD)

    assert capture.returncode == 0, capture.stderr
    records = [json.loads(line) for line in (directory / "s-profiler.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [{"plan", "directives"} & set(record) for record in records] == [set(), set()]
    [manifest] = (project / ".devpro-temp" / ".profiler-directives").iterdir()
    assert sorted(json.loads(manifest.read_text(encoding="utf-8"))) == [".opencode/plugins/devpro/agents/coder.md"]


def test_the_opencode_capture_reads_the_store_it_opens_after_an_unstamped_one(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: a store holding records with neither stamp field —
    what opencode wrote before this capture stamped anything — was read as holding no stamp, and the
    plugin minted a fresh one beside those records, so one process's records disagreed on the context
    they ran under. This session's store follows the plugin's own in the directory, so a read that
    starts at the first of the two cannot open the session's.

    A project whose plan and installed definition stand now: the stamp the plugin's next record for
    the session carries is unstamped — the window read no stamped record, so no fresh digest is taken
    beside the records it holds — and the session's records keep the state they were written under,
    the fresh digest's manifest written beside them as a manifest may postdate the digest it is keyed
    by."""
    project = tmp_path / "project"
    project.mkdir()
    _plan(project, "a plan")
    definition = project / ".opencode" / "plugins" / "devpro" / "agents" / "coder.md"
    definition.parent.mkdir(parents=True)
    definition.write_text("<!-- !GENERATED! from devpro/definitions/agents/coder.py -->\nbody\n", encoding="utf-8")
    legacy = {"v": 1, "harness": "opencode", "at": "2026-01-01T00:00:00.000Z", "session": "ses_stamp", "tool": "shell"}
    store = project / ".devpro-temp" / ".profiler-opencode"
    store.mkdir(parents=True)
    (store / "ses_stamp.jsonl").write_text(f"{json.dumps(legacy)}\n", encoding="utf-8")
    # The plugin's store holds a record of another session too: this session's store follows it, and a
    # read that starts at the first of the two holds a record the session's is not.
    (store / "ses_first.jsonl").write_text(
        f"{json.dumps({'v': 1, 'harness': 'opencode', 'at': '2026-01-01T00:00:00.000Z', 'session': 'ses_first'})}\n",
        encoding="utf-8",
    )
    for name in ("ses_first.jsonl", "ses_stamp.jsonl"):
        os.utime(store / name, (0, 0))

    out = json.loads(
        _run_ts(
            _HERE / "profiler_stamp_runner.ts",
            directory=project,
            stdin=json.dumps({"directory": str(project), "session": "ses_stamp"}),
        ).stdout
    )

    assert out["stamp"] == {"plan": None, "directives": None}
    assert out["stores"][".profiler-opencode"] == [None]
    [manifest] = (project / ".devpro-temp" / ".profiler-directives").iterdir()
    assert sorted(json.loads(manifest.read_text(encoding="utf-8"))) == [".opencode/plugins/devpro/agents/coder.md"]


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
