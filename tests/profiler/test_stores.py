"""list_sessions• read_sessions• copy-as-no-store"""

import shutil
from pathlib import Path

from devpro.profiler.read import list_sessions, read_sessions

from .conftest import _write_store


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
