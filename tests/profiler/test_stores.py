"""list_sessions• read_sessions• copy-as-no-store• the claude dispatch's closing record"""

import json
import shutil
from pathlib import Path

from devpro.profiler.read import list_sessions, read_sessions, running_dispatches

from .conftest import _claude_store, _stop_at, _write_store


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


def test_a_claude_dispatch_ends_at_its_stop(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect (R1): the closing matcher reads the `SubagentStop`'s
    parent session id, so a claude dispatch's id — the opening `Agent` call's `child_agent_id` — never
    matches the ended set, and every claude dispatch shows running forever.

    A claude `Agent` call opening a child keeps the dispatch running until that child's `SubagentStop`,
    whose own `agent_id` is the child's id the call named: the stop ends it, the derivation leaving no
    claude dispatch running. Without the fix the dispatch still runs past its stop."""
    project = tmp_path / "project"
    _claude_store(
        project,
        "s-parent",
        "2026-01-01T00:00:00.000Z",
        extra={"tool": "Agent", "name": "devpro-coder", "agent_type": "devpro-coder", "child_agent_id": "a1"},
    )
    assert [dispatch.id for dispatch in running_dispatches(project)] == ["a1"]

    _stop_at(project, "s-parent", "2026-01-01T00:00:02.000Z", "a1")
    assert running_dispatches(project) == []


def test_two_claude_dispatches_close_in_opening_order(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect (R1): a claude dispatch never closes, so two of one
    session and one agent type — the case the old session-and-type match conflated — keep running past
    both their stops rather than closing at their own.

    Two `Agent` calls of one agent type open `a-first` then `a-second`, their `SubagentStops` appended
    after: both run in opening order, the palette's first and second; `a-first`'s stop leaves
    `a-second` running in its opening place, and `a-second`'s stop leaves none. Without the fix neither
    closes and the set never shrinks."""
    project = tmp_path / "project"
    store = project / ".devpro-temp" / ".profiler-claude"
    store.mkdir(parents=True)
    openings = [
        ("2026-01-01T00:00:01.000Z", "a-first"),
        ("2026-01-01T00:00:02.000Z", "a-second"),
    ]
    (store / "s-parent.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "v": 4,
                    "harness": "claude",
                    "at": at,
                    "session": "s-parent",
                    "tool": "Agent",
                    "name": "devpro-coder",
                    "agent_type": "devpro-coder",
                    "child_agent_id": child,
                    "ok": True,
                }
            )
            + "\n"
            for at, child in openings
        ),
        encoding="utf-8",
    )
    running = running_dispatches(project)
    assert [(dispatch.id, dispatch.hue) for dispatch in running] == [("a-first", 1), ("a-second", 2)]

    _stop_at(project, "s-parent", "2026-01-01T00:00:03.000Z", "a-first")
    assert [dispatch.id for dispatch in running_dispatches(project)] == ["a-second"]

    _stop_at(project, "s-parent", "2026-01-01T00:00:04.000Z", "a-second")
    assert running_dispatches(project) == []


def test_an_opencode_dispatch_whose_child_idled_last_ends_at_that_idle(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect (the killed child, found live): a child that idled with
    background work listed and never woke — the idle its store's last record — kept its dispatch
    running forever, the episode contract reading a background-listed idle as no episode's end.

    An opencode dispatch's child idles with `background: 1` as its store's last record: the idle ends
    it — the agent loop finished and nothing followed to wake it. A record after the idle (the wake)
    leaves the dispatch running, the idle no longer last, until a falsy-background idle or a final
    idle closes it."""
    project = tmp_path / "project"
    store = project / ".devpro-temp" / ".profiler-opencode"
    store.mkdir(parents=True)
    opener = {
        "v": 4,
        "harness": "opencode",
        "at": "2026-01-01T00:00:00.000Z",
        "session": "s-parent",
        "tool": "subagent",
        "name": "devpro-coder",
        "child_agent_id": "c1",
        "ok": True,
    }
    (store / "s-parent.jsonl").write_text(json.dumps(opener) + "\n", encoding="utf-8")
    idle_with_work = {
        "v": 4,
        "harness": "opencode",
        "at": "2026-01-01T00:00:02.000Z",
        "session": "c1",
        "event": "experimental.idle",
        "background": 1,
    }
    (store / "c1.jsonl").write_text(
        json.dumps(
            {
                "v": 4,
                "harness": "opencode",
                "at": "2026-01-01T00:00:01.000Z",
                "session": "c1",
                "tool": "shell",
                "ok": True,
            }
        )
        + "\n"
        + json.dumps(idle_with_work)
        + "\n",
        encoding="utf-8",
    )
    assert running_dispatches(project) == []

    (store / "c1.jsonl").open("a", encoding="utf-8").write(
        json.dumps(
            {
                "v": 4,
                "harness": "opencode",
                "at": "2026-01-01T00:00:03.000Z",
                "session": "c1",
                "tool": "shell",
                "ok": True,
            }
        )
        + "\n"
    )
    assert [dispatch.id for dispatch in running_dispatches(project)] == ["c1"]
