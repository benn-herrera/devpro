"""Fixtures every test runs under, and the helpers and values more than one test module shares."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from devpro.components import Components

PLAIN = Components()
"""The selection with no optional component on."""
WITH_KBASE = Components(on=frozenset({"kbase"}))
"""The selection with the kbase component on."""

# `_dispatch_store` is re-exported so a sub-suite's conftest can expose it to its tests; the
# definition lives here, at the shared `tests/conftest.py`. `_write_store` is its private backing.
__all__ = ["_dispatch_store"]


@pytest.fixture(autouse=True)
def _home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A home directory under `tmp_path`, created by the tests that use it. `HOME` names it for every
    test and every process a test starts, so nothing the suite runs reads or writes the operator's real
    home."""
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    return home


# `_home` is function-scoped and autouse, so `HOME` is scratch only while a test runs. A session- or
# module-scoped fixture is set up outside any test's home, and one that runs `devpro install` reaches
# the operator's: the install's target resolution compares the target with `Path.home()`
# (`devpro/install_target.py`), and its CLI reads the default settings file under `Path.home()`
# (`devpro/context.py`). Such a fixture points `HOME` at a scratch directory of its own first.


def settings_file(tmp_path: Path, text: str) -> Path:
    """A devpro settings file holding `text`, for the CLI to read with `--config-file`."""
    path = tmp_path / "devpro.toml"
    path.write_text(text, encoding="utf-8")
    return path


def page_data(page: str) -> dict:
    """The JSON a profiler page inlines at its data slot, whichever carrier served it."""
    return json.loads(page.split("const D = ", 1)[1].split(";\n", 1)[0])


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
                    **(extra or {}),
                }
            )
            + "\n"
            for second in range(records)
        ),
        encoding="utf-8",
    )
    return directory


def _dispatch_store(root: Path, session: str, at: str, child: str, *, records: int = 1, duration_ms: int = 500) -> Path:
    """An opencode store under `root` holding `records` dispatch records for `session`, the launch
    acknowledgment the capture writes when a `subagent` call returns, each a second apart from the
    moment `at` names, its `duration_ms` the firing cost, its `background` true, and the child's
    session id."""
    return _write_store(
        root,
        ".profiler-opencode",
        session,
        at,
        records=records,
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
