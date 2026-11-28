"""text/tree render• call rows• dispatch joins• durations"""

import json
from pathlib import Path

import pytest

from devpro.profiler.pages import call_label, clock, stamp
from devpro.profiler.values import _epoch_ms
from tests.conftest import page_data
from tests.fixtures import fixture_file

from .conftest import (
    _HERE,
    _call_row,
    _claude_store,
    _dispatch_store,
    _fetch,
    _idle_store,
    _run,
    _run_ts,
    _serve,
    _stop_at,
    _write_store,
)


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
    idle's 20 s or the background-laden idle's 30 s. A background-laden idle standing as the child's
    last record ends the child — the killed child's rule: the span reads to that idle, the store's last
    word on the run, and not the placeholder the acknowledgment carried."""
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

    for session, span in (("ses_parent", 40_000), ("ses_other", 30_000)):
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
