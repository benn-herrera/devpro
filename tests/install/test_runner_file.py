"""include-line rewrite• snippet sets• makefile create/remove"""

import os
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

import pytest

from devpro.cli import main
from devpro.errors import InputError
from devpro.install import RETIRED_SNIPPET_SET
from devpro.install_base import PACKAGE_ROOT
from devpro.runner_file import _named_harnesses, install_include_lines

from .conftest import (
    _CLAUDE_PLUGIN_RELPATH,
    _CLAUDE_RENDER,
    _DEVPRO_SET_LINE,
    _KB_SNIPPETS,
    _KBASE_CLAUDE_RENDER,
    _KBASE_OPENCODE_RENDER,
    _NO_DEVPRO_PATH,
    _SNIPPET_SETS,
    _claude_plugin,
    _definition_install,
    _files,
    _plant,
    _snippet_recipe_runs,
    _state,
)


def test_the_include_line_is_appended_to_an_existing_justfile(tmp_path: Path) -> None:
    root = tmp_path / ".claude"
    root.mkdir()
    (tmp_path / "justfile").write_text("default:\n  @echo hi\n", encoding="utf-8")
    _definition_install(root, _KBASE_CLAUDE_RENDER, project_root=tmp_path)
    assert (tmp_path / "justfile").read_text(encoding="utf-8") == (
        f"default:\n  @echo hi\n\n{_DEVPRO_SET_LINE}\n\n"
        f"import? '{_CLAUDE_PLUGIN_RELPATH}/skills/kbase/kb-tools/runner-snippets/kb.just'\n"
    )


def test_a_makefile_is_created_when_the_project_has_neither_runner_file(tmp_path: Path) -> None:
    """Created once, holding every set's line in `SHIPPED_PACKAGES` order."""
    root = tmp_path / ".opencode"
    root.mkdir()
    _definition_install(root, _KBASE_OPENCODE_RENDER, project_root=tmp_path)
    text = (tmp_path / "Makefile").read_text(encoding="utf-8")
    assert text.startswith("# Makefile — created by the devpro installer.\n")
    assert text.endswith("\n-include .opencode/plugins/devpro/skills/kbase/kb-tools/runner-snippets/kb.mk\n")
    assert not (tmp_path / "justfile").exists()


def test_a_second_harness_writes_no_include_line_and_reports_the_first(tmp_path: Path, capsys) -> None:
    project = tmp_path
    first = project / ".claude"
    first.mkdir()
    (project / "justfile").write_text("# mine\n", encoding="utf-8")
    _definition_install(first, _KBASE_CLAUDE_RENDER, project_root=project)
    before = (project / "justfile").read_bytes()
    second = project / ".opencode"
    second.mkdir()
    capsys.readouterr()
    _definition_install(second, _KBASE_OPENCODE_RENDER, project_root=project)
    assert (project / "justfile").read_bytes() == before
    err = capsys.readouterr().err
    assert "no include line written" in err and "'claude'" in err


@pytest.mark.parametrize(
    "snippets_path",
    [
        "custom/kb-tools/runner-snippets",
        "kb-tools/runner-snippets",
    ],
    ids=["hand-written", "short-tree"],
)
def test_an_include_line_for_this_harness_under_any_tree_is_rewritten_in_place(
    tmp_path: Path, snippets_path: str
) -> None:
    """A line naming this harness directory is this install's line whatever tree its path spells, one
    no release here wrote included, so its whole path is replaced where it stands, naming the
    plugin's snippets, and the file keeps one include line rather than gaining a second beside a dead one."""
    project = tmp_path
    root = project / ".claude"
    root.mkdir()
    (project / "justfile").write_text(f"default:\n  @echo hi\n\nimport? '.claude/{snippets_path}/kb.just'\n")
    _definition_install(root, _KBASE_CLAUDE_RENDER, project_root=project)
    text = (project / "justfile").read_text(encoding="utf-8")
    expected = f"import? '{_CLAUDE_PLUGIN_RELPATH}/skills/kbase/kb-tools/runner-snippets/kb.just'"
    assert text == f"default:\n  @echo hi\n\n{expected}\n\n{_DEVPRO_SET_LINE}\n"
    assert text.count("runner-snippets/kb.just") == 1


@pytest.mark.parametrize(
    "prior, expected",
    [
        (
            "# import? '.claude/custom/kb-tools/runner-snippets/kb.just'\n",
            "# import? '.claude/custom/kb-tools/runner-snippets/kb.just'\n"
            "\nimport? '.claude/skills/kbase/kb-tools/runner-snippets/kb.just'\n",
        ),
        (
            "import? '.claude/custom/kb-tools/runner-snippets/kb.just'  # mine\n",
            "import? '.claude/skills/kbase/kb-tools/runner-snippets/kb.just'  # mine\n",
        ),
        (
            "default:\r\n  @echo hi\r\n\r\nimport? '.claude/custom/kb-tools/runner-snippets/kb.just'\r\n",
            "default:\r\n  @echo hi\r\n\r\nimport? '.claude/skills/kbase/kb-tools/runner-snippets/kb.just'\r\n",
        ),
    ],
    ids=["commented-out", "trailing-comment", "crlf"],
)
def test_the_include_line_rewrite_touches_only_its_own_path_token(tmp_path: Path, prior: str, expected: str) -> None:
    """A commented line is not an include; a rewrite replaces the snippets path alone, keeping an
    assignment's left-hand side, a trailing comment and the file's own line endings."""
    (tmp_path / "justfile").write_bytes(prior.encode("utf-8"))
    install_include_lines(tmp_path, [_KB_SNIPPETS], harness_relpath=".claude")
    assert (tmp_path / "justfile").read_bytes() == expected.encode("utf-8")


def test_a_makefile_include_line_is_recognized_by_the_same_shape(tmp_path: Path) -> None:
    """The `-include` form is matched on the path's shape too, the Makefile's own snippet being
    `kb.mk`: a stale tree is rewritten in place and no second line lands beside it."""
    prior = "all:\n\t@echo hi\n\n-include .opencode/custom/kb-tools/runner-snippets/kb.mk\n"
    (tmp_path / "Makefile").write_text(prior, encoding="utf-8")
    install_include_lines(tmp_path, [_KB_SNIPPETS], harness_relpath=".opencode")
    text = (tmp_path / "Makefile").read_text(encoding="utf-8")
    assert text == "all:\n\t@echo hi\n\n-include .opencode/skills/kbase/kb-tools/runner-snippets/kb.mk\n"


def test_two_include_lines_are_reported_and_left(tmp_path: Path, capsys) -> None:
    """Rewriting one of two would leave the other stale, so the operator merges them by hand."""
    prior = (
        "import? '.claude/custom/kb-tools/runner-snippets/kb.just'\n"
        "import? '.claude/skills/kbase/kb-tools/runner-snippets/kb.just'\n"
    )
    (tmp_path / "justfile").write_text(prior, encoding="utf-8")
    install_include_lines(tmp_path, [_KB_SNIPPETS], harness_relpath=".claude")
    assert (tmp_path / "justfile").read_text(encoding="utf-8") == prior
    assert "names the kb snippets on lines 1, 2" in capsys.readouterr().err


def test_an_include_line_naming_no_harness_reports_its_raw_prefix() -> None:
    [match] = _named_harnesses(
        "default:\n  @echo hi\nimport? 'tools/skills/kbase/kb-tools/runner-snippets/kb.just'\n",
        _KB_SNIPPETS,
        runner="just",
    )
    assert (match.name, match.index) == ("tools", 2)


@pytest.mark.parametrize("runner, matched", [("just", True), ("make", False)], ids=["its-own", "the-others"])
def test_a_line_is_a_line_for_the_runner_whose_snippet_it_names(runner: str, matched: bool) -> None:
    """`kb.just` is the justfile's snippet and `kb.mk` the Makefile's, so one runner's snippet named in
    the other's file is not an include line that install has to rewrite."""
    text = "import? '.claude/kb-tools/runner-snippets/kb.just'\n"
    assert bool(_named_harnesses(text, _KB_SNIPPETS, runner=runner)) is matched


def test_a_non_utf8_runner_file_is_refused_before_the_first_write(tmp_path: Path) -> None:
    """The runner file is decoded with every other check: the refusal writes nothing, where a decode
    after the writes would leave a half-updated install and refuse the retry too."""
    root = tmp_path / ".claude"
    root.mkdir()
    (tmp_path / "justfile").write_bytes(b"\xff\xfe default:\n")
    before = _files(tmp_path)
    with pytest.raises(InputError, match="justfile"):
        _definition_install(root, _KBASE_CLAUDE_RENDER, project_root=tmp_path)
    assert _files(tmp_path) == before


@pytest.mark.usefixtures("_no_uncommitted")
def test_an_install_whose_project_is_this_repository_writes_the_devpro_include_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Defect: the include lines were skipped where the project is `REPO_ROOT`, so this repository's own
    justfile carried no `devpro-*` recipes."""
    project = tmp_path / "project"
    project.mkdir()
    (project / "justfile").write_text("# generator\n", encoding="utf-8")
    monkeypatch.setattr("devpro.install_base.REPO_ROOT", project.resolve())
    main(["install", str(project), "--harness=claude"])
    assert _DEVPRO_SET_LINE in (project / "justfile").read_text(encoding="utf-8").splitlines()


def test_a_retired_docdicer_line_is_removed_and_reported(tmp_path: Path, capsys) -> None:
    """`skills/docdicer/tools/` is pruned at the next install, so a line importing its snippets outlives
    the snippets it names and the recipes vanish silently. Both of this harness's lines go, each removal
    reported; a line naming another harness directory's snippets is reported and left."""
    docdicer_just = f"import? '{_CLAUDE_PLUGIN_RELPATH}/skills/docdicer/tools/runner-snippets/docdicer.just'"
    (tmp_path / "justfile").write_text(
        f"default:\n  @echo hi\n\n{docdicer_just}\n{docdicer_just}\nimport? '.opencode/plugins/devpro/skills/docdicer/tools/runner-snippets/docdicer.just'\n",
        encoding="utf-8",
    )
    install_include_lines(tmp_path, [], harness_relpath=".claude", retired_set=RETIRED_SNIPPET_SET)
    assert (tmp_path / "justfile").read_text(encoding="utf-8") == (
        "default:\n  @echo hi\n\n"
        "import? '.opencode/plugins/devpro/skills/docdicer/tools/runner-snippets/docdicer.just'\n"
    )
    out, err = capsys.readouterr()
    assert out.count("removed the retired docdicer include line from") == 2
    assert "names the retired docdicer snippets for harness 'opencode'" in err


def test_a_project_install_without_the_kbase_component_writes_the_devpro_include_line_only(
    tmp_path: Path,
) -> None:
    """The devpro line rides the devpro tools package, which every selection ships: without the kbase
    component the plain install writes it and no kb line, so the argumentless gates are reachable in the
    default install. A project with neither runner file gets a `Makefile` holding that one line."""
    root = tmp_path / ".claude"
    root.mkdir()
    _definition_install(root, _CLAUDE_RENDER, project_root=tmp_path)
    text = (tmp_path / "Makefile").read_text(encoding="utf-8")
    assert "-include .claude/skills/devpro/tools/runner-snippets/devpro.mk" in text
    assert "kb-tools/runner-snippets/kb.mk" not in text
    assert not (tmp_path / "justfile").exists()


def test_a_gitignore_already_carrying_the_line_is_left_as_it_stands(tmp_path: Path) -> None:
    """Neither its bytes nor its modification time change: an install rerun on a prepared project writes
    no `.gitignore` at all, so the preflight has nothing to report and the file is untouched."""
    project = tmp_path / "project"
    project.mkdir()
    gitignore = _plant(project / ".gitignore", ".venv/\n.devpro-temp/\n")
    state = _state(project)
    main(["install", str(project), "--harness=claude"])
    assert (gitignore.read_bytes(), gitignore.stat().st_mtime_ns) == (
        b".venv/\n.devpro-temp/\n",
        state[".gitignore"][1],
    )


def test_a_runner_file_holding_no_retired_line_is_reported_as_found_not_as_left(tmp_path: Path, capsys) -> None:
    """The removal helper runs on a file this install's write changed, which an append does as surely as
    a removal, so it reaches a consumer's own Makefile the cleanup touched nothing in. That file is left
    reported as holding no include line and nothing removed — not as left over after a removal."""
    (tmp_path / "Makefile").write_text("all:\n\t@echo hi\n", encoding="utf-8")
    install_include_lines(tmp_path, [_KB_SNIPPETS], harness_relpath=".opencode", retired_set=RETIRED_SNIPPET_SET)
    out, err = capsys.readouterr()
    assert "removed" not in out
    assert f"left {tmp_path / 'Makefile'} in place: it holds no include line, and this install removed none" in err
    assert "holding no include line: it holds content other than this install's" not in err


def test_a_devpro_set_line_survives_the_retired_docdicer_lines_cleanup(tmp_path: Path, capsys) -> None:
    """The devpro set and the retired docdicer set both sit in a `runner-snippets/` directory, so a
    cleanup matching that directory name rather than the snippet file name would take the devpro line
    for a docdicer one and delete it — and delete it in the same run's write, a line that would
    otherwise have been appended the run after. The docdicer line beside it goes; the devpro line
    stands, under whatever tree it spells, and is reported left alone where it already names the
    installed snippets."""
    devpro_just = f"import? '{_CLAUDE_PLUGIN_RELPATH}/tools/runner-snippets/devpro.just'"
    docdicer_just = f"import? '{_CLAUDE_PLUGIN_RELPATH}/skills/docdicer/tools/runner-snippets/docdicer.just'"
    (tmp_path / "justfile").write_text(f"default:\n  @echo hi\n\n{devpro_just}\n{docdicer_just}\n", encoding="utf-8")
    install_include_lines(tmp_path, [], harness_relpath=".claude", retired_set=RETIRED_SNIPPET_SET)
    assert (tmp_path / "justfile").read_text(encoding="utf-8") == f"default:\n  @echo hi\n\n{devpro_just}\n"
    out = capsys.readouterr().out
    assert out.count("removed the retired docdicer include line from") == 1


def test_the_retired_cleanup_leaves_a_devpro_set_line_alone_in_a_makefile(tmp_path: Path) -> None:
    """The `-include` form is recognized on the same shape, so the Makefile side is the same defect: a
    line ending `runner-snippets/devpro.mk` is not a retired docdicer line."""
    devpro_mk = "-include .opencode/plugins/devpro/tools/runner-snippets/devpro.mk"
    docdicer_mk = "-include .opencode/plugins/devpro/skills/docdicer/tools/runner-snippets/docdicer.mk"
    (tmp_path / "Makefile").write_text(f"all:\n\t@echo hi\n\n{devpro_mk}\n{docdicer_mk}\n", encoding="utf-8")
    install_include_lines(tmp_path, [], harness_relpath=".opencode", retired_set=RETIRED_SNIPPET_SET)
    assert (tmp_path / "Makefile").read_text(encoding="utf-8") == f"all:\n\t@echo hi\n\n{devpro_mk}\n"


def test_no_two_snippet_sets_name_the_same_snippet() -> None:
    """An include line is recognized by its snippets directory's name and snippet file alone, so a pair
    two sets shared would let one set's line count as the other's."""
    pairs = [
        (PurePosixPath(snippet_set.directory).name, snippet)
        for snippet_set in _SNIPPET_SETS.values()
        for snippet in snippet_set.snippets.values()
    ]
    assert len(pairs) == len(set(pairs))


@pytest.mark.parametrize("runner", ["just", "make"])
def test_the_shipped_devpro_snippets_list_the_same_recipes_and_every_gate_takes_no_argument(
    tmp_path: Path, runner: str
) -> None:
    """`devpro-help` lists the same recipes whichever runner includes the set, and it lists them
    from the snippet rather than a copy, naming the CLI's own help beside them — its own `devpro
    --help` is in the log below. A devpro on PATH records where a check runs and what it was
    given, so the gates prove they run the check verb argumentless with nothing else. A runner
    whose list drifted from the other's would write include lines promising targets one runner does not
    define; a gate carrying an argument would check a file the consumer did not name."""
    if shutil.which(runner) is None:
        pytest.skip(f"{runner} is not installed")
    # The recipes run the installation's wrapper, `../devpro.sh` beside the snippet file's directory —
    # `project/` here, so `../devpro.sh` is this shim — not `devpro` on PATH: the shim stands where the
    # recipe's own path resolves it, recording each invocation.
    devpro = tmp_path / "devpro.sh"
    devpro.write_text('#!/bin/sh\nprintf \'%s\\n\' "$*" >> "$PROBE_LOG"\n', encoding="utf-8")
    devpro.chmod(0o755)
    project = tmp_path / "project"
    project.mkdir()
    for name in ("devpro.just", "devpro.mk"):
        (project / name).write_text(
            (PACKAGE_ROOT / "runner-snippets" / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    line = "import? 'devpro.just'" if runner == "just" else "-include devpro.mk"
    runner_file = "justfile" if runner == "just" else "Makefile"
    body = "all:\n  @echo hi\n" if runner == "just" else "all:\n\t@echo hi\n"
    (project / runner_file).write_text(f"{body}\n{line}\n", encoding="utf-8")
    environment = {**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}", "PROBE_LOG": str(tmp_path / "log")}
    runs = _snippet_recipe_runs()
    # Each recipe runs one line, the line is the wrapper's, and the two runners agree: a name whose line
    # drifted would promise one runner a target the other never runs.
    expected = ["--help", *sorted(command for lines in runs.values() for command in lines)]
    listed = subprocess.run(
        [runner, "devpro-help"], cwd=project, env=environment, capture_output=True, text=True, check=True
    )
    names = sorted(
        match.group(1)
        for line in listed.stdout.splitlines()
        if (match := re.match(r"\s+(devpro(?:-[a-z-]+)?)[:\s]", line))
    )
    assert names == sorted(runs)
    for recipe in runs:
        subprocess.run([runner, recipe], cwd=project, env=environment, capture_output=True, check=True)
    # The devpro-help run invokes the command itself — its own `devpro --help` — before the gate
    # recipes: the log names the help surface's invocation and each gate's own line, argumentless where
    # the recipe spells it so. Run order is the snippet's, so the log is compared as a multiset.
    logged = (tmp_path / "log").read_text(encoding="utf-8").splitlines()
    assert logged[0] == "--help" and sorted(logged[1:]) == expected[1:]


def test_an_argument_after_a_devpro_recipe_is_refused_before_the_command_runs(tmp_path: Path) -> None:
    """The gates take no argument: a word after one is a recipe `just` cannot find, refused before any
    command runs — where without `set positional-arguments` a bare `help` in the recipe's line is the
    shell's command lookup and `devpro help` runs the help page instead of the check."""
    if shutil.which("just") is None:
        pytest.skip("just is not installed")
    snippet = PACKAGE_ROOT / "runner-snippets/devpro.just"
    (tmp_path / "devpro.just").write_text(snippet.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "justfile").write_text("all:\n  @echo hi\n\nimport? 'devpro.just'\n", encoding="utf-8")
    # The recipe runs the wrapper `../devpro.sh` beside the snippet, not `devpro` on PATH: the shim
    # stands where that path resolves it, so a run would log and its absence still proves no run.
    devpro = tmp_path / "devpro.sh"
    devpro.write_text('#!/bin/sh\nprintf \'%s\\n\' "$*" >> "$PROBE_LOG"\n', encoding="utf-8")
    devpro.chmod(0o755)
    environment = {**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}", "PROBE_LOG": str(tmp_path / "log")}
    for words in (["devpro-check-plan", "help"], ["devpro", "help"], ["devpro-check-design", "ACTIVE_DESIGN.md"]):
        refused = subprocess.run(
            ["just", *words], cwd=tmp_path, env=environment, capture_output=True, text=True, check=False
        )
        assert refused.returncode != 0 and "does not contain recipe" in refused.stderr
    assert not (tmp_path / "log").exists()


@pytest.mark.parametrize("entry", ["make", "just"])
def test_an_installed_runner_snippet_runs_the_check_through_the_wrapper_without_devpro_on_path(
    tmp_path: Path, entry: str
) -> None:
    """An installed runner snippet runs its check through the installation's wrapper, `../devpro.sh`
    beside the snippet file's installed directory — never `devpro` on PATH: the wrapper stands at
    `<plugin>/tools/devpro.sh`, one file above the snippet, and a bare PATH still records the check.
    Defect: before the snippets named the install, a project whose system `devpro` was removed could
    not run any of the checks its own Makefile or justfile exposed. The project's directory name holds a
    space. Defect: the just snippet interpolated the wrapper's absolute path unquoted, so the shell split
    it and every `devpro-*` recipe exited 127."""
    runner = shutil.which(entry)
    if runner is None:
        pytest.skip(f"{entry} is not installed")
    project = tmp_path / "a project"
    project.mkdir()
    if entry == "just":
        # An empty justfile is where the install writes the just include line; with neither runner
        # file present the install reaches for a Makefile, and `just` finds no justfile at all.
        (project / "justfile").touch()
    main(["install", str(project), "--harness=claude"])
    plugin = _claude_plugin(project / ".claude")
    assert (plugin / "tools" / "devpro.sh").is_file()
    snippet = plugin / ("tools/runner-snippets/devpro.mk" if entry == "make" else "tools/runner-snippets/devpro.just")
    assert snippet.is_file()
    recorded = tmp_path / "recorded"
    environment = {
        **os.environ,
        # No devpro on PATH: the wrapper is what the recipe's own path resolves, not a lookup.
        "PATH": _NO_DEVPRO_PATH,
        "HOME": str(tmp_path),
        "DEVPRO_PROBE_LOG": str(recorded),
    }
    wrapper = plugin / "tools" / "devpro.sh"
    wrapper.write_text('#!/bin/sh\nprintf \'%s\\n\' "$@" >> "$DEVPRO_PROBE_LOG"\n', encoding="utf-8")
    wrapper.chmod(0o755)
    verb = "devpro-check-plan"
    done = subprocess.run([runner, verb], cwd=project, env=environment, capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stderr
    assert recorded.read_text(encoding="utf-8").splitlines() == ["check-plan"]
