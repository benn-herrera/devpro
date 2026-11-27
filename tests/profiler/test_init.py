"""An opencode-shaped repository's refusal, and the store rename."""

import json
import subprocess
from pathlib import Path

import pytest

from devpro.profiler.read import read_sessions, store_directories
from devpro.profiler.values import CAPTURED_EVENTS

from .conftest import _install_project, _profiler_init, _run, _write_store


@pytest.mark.parametrize("install", ["opencode", "foreign-wrapper"], ids=["opencode-shaped", "foreign-wrapper"])
def test_init_refuses_an_opencode_shaped_repo_rather_than_register_a_second_capture(
    tmp_path: Path, _wrapper: Path, install: str
) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: `is_our_command` recognized only the `.claude/…`
    wrapper, so a re-`init` over a repository whose hook entry names the opencode plugin's
    `devpro/plugins/devpro/tools/devpro.sh` appends a second entry on every event — `merge_hooks`
    matching the command against one `.claude/…` literal, `init` registering `profiler capture
    claude` beside an opencode install's capture in the same settings.

    Two repositories the claude `init` did not write: one whose install is opencode's (its plugin
    wrapper on disk), one whose entry names a wrapper neither install wrote. `init claude` refuses
    each as `error: <message>` on stderr with status 2, naming what it found, and writes nothing —
    the settings file and the skill are as they were."""
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    command = '"$CLAUDE_PROJECT_DIR/devpro/plugins/devpro/tools/devpro.sh" profiler capture claude'
    if install == "opencode":
        opencode = project / "devpro" / "plugins" / "devpro" / "tools"
        opencode.mkdir(parents=True)
        (opencode / "devpro.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        named = "devpro/plugins/devpro/tools/devpro.sh"
    else:
        named = ".devpro-temp/their-wrapper.sh"
        command = f'"$CLAUDE_PROJECT_DIR/{named}" profiler capture claude'
    settings_file = project / ".claude" / "settings.json"
    settings_file.parent.mkdir(parents=True)
    original = {
        "hooks": {
            event: [{"matcher": "*", "hooks": [{"type": "command", "command": command, "timeout": 5, "async": True}]}]
            for event in CAPTURED_EVENTS
        }
    }
    settings_file.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")

    # The wrapper's `devpro` shim written into the project would be a directory here, beside the
    # opencode install's `devpro/`: the run gets a bare PATH instead, which the wrapper consults only for
    # its interpreter, the recorded one.
    done = _run(_wrapper, "init", "claude", cwd=project, path="/usr/bin:/bin")

    assert done.returncode == 2, done.stdout
    assert done.stderr.startswith("error: "), done.stderr
    assert named in done.stderr, done.stderr
    assert json.loads(settings_file.read_text(encoding="utf-8")) == original
    assert not (project / ".claude" / "skills" / "profiler").exists()


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
