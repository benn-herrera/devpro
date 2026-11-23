"""The entry point's floor check, its position, and the wrapper that leaves the refusal to it.

The below-floor runs are synthetic: no 3.9 interpreter is needed, only one that answers a below-floor
`version_info`, so the check's own syntax and its exact first act are what is exercised. A decoy
`devpro` ahead of the installed copy raises when its `cli` is imported, so a check that ran second
reports the decoy; the refusal line is compared whole, its stderr and exit being the contract.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

from devpro import __version__
from devpro.cli import main
from devpro.components import NAME
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.install import wrapper_text
from devpro.install_base import PACKAGE_ROOT

_NO_DEVPRO_PATH = "/usr/bin:/bin"


def _plugin(project: Path) -> Path:
    return project / ".claude" / CLAUDE.bound(NAME).plugin_dir


def _run_wrapper(wrapper: Path, *, path: str, home: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(wrapper), "--version"],
        env={"PATH": path, "HOME": str(home)},
        cwd=home,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        stdin=subprocess.DEVNULL,
        timeout=60,
    )


def _first_python3() -> str:
    located = subprocess.run(
        ["python3", "-c", "import sys; print(sys.executable)"],
        env={"PATH": _NO_DEVPRO_PATH},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return located.stdout.strip()


@pytest.fixture
def installed(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    main(["install", str(project), "--harness=claude"])
    return project


def test_the_entry_point_refuses_a_below_floor_interpreter_before_importing_another_module(
    installed: Path, tmp_path: Path
) -> None:
    """The console script's entry and `-m` both reach `devpro/__init__.py` first, and it refuses there:
    a decoy package ahead of the copy raises if its `cli` is imported, so the refusal line coming back
    whole is the check having run before it. Defect: the wrapper checked the floor on the `python3`
    found on PATH and never on the interpreter it recorded, so a copy recorded under a 3.9 ran with no
    refusal."""
    copy = _plugin(installed) / "tools"
    decoy = tmp_path / "decoy"
    (decoy / "devpro").mkdir(parents=True)
    (decoy / "devpro/__init__.py").write_text("", encoding="utf-8")
    (decoy / "devpro/cli.py").write_text("raise SystemExit('the decoy ran')\n", encoding="utf-8")
    (decoy / "devpro/__main__.py").write_text("raise SystemExit('the decoy ran')\n", encoding="utf-8")
    interpreter = _first_python3()
    for entry in (
        "from devpro.cli import main\nmain()\n",
        "import runpy\nrunpy.run_module('devpro', run_name='__main__', alter_sys=True)\n",
    ):
        refused = subprocess.run(
            ["python3", "-c", f"import sys\nsys.version_info = (3, 9, 6, 'final', 0)\n{entry}", "--version"],
            cwd=copy,
            env={"PYTHONPATH": f"{decoy}:{copy}", "PATH": _NO_DEVPRO_PATH, "HOME": str(tmp_path)},
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            stdin=subprocess.DEVNULL,
            timeout=60,
        )
        assert refused.returncode == 1, refused.stderr
        assert refused.stdout == ""
        assert refused.stderr == (
            f"error: devpro needs Python 3.11 or later, running under 3.9.6 ({interpreter})\n"
        ), refused.stderr


def test_a_real_below_floor_interpreter_is_refused_by_the_entry_point() -> None:
    """The real thing where the machine has one: a `/usr/bin/python3` below the floor is refused with
    the line naming it, not the traceback an older interpreter dies with in a later module."""
    interpreter = Path("/usr/bin/python3")
    if not interpreter.exists():
        pytest.skip("no /usr/bin/python3 on this machine")
    version = subprocess.run(
        [str(interpreter), "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    ).stdout.strip()
    if tuple(int(part) for part in version.split(".")) >= (3, 11):
        pytest.skip(f"/usr/bin/python3 is {version}, not below the floor")
    refused = subprocess.run(
        [str(interpreter), "-c", "import sys; print(sys.executable)"],
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    located = refused.stdout.strip()
    failed = subprocess.run(
        [str(interpreter), "-c", "import devpro"],
        env={"PYTHONPATH": str(PACKAGE_ROOT.parent)},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        stdin=subprocess.DEVNULL,
        timeout=60,
    )
    assert failed.returncode == 1, failed.stderr
    assert failed.stderr == (
        f"error: devpro needs Python 3.11 or later, running under {version} ({located})\n"
    ), failed.stderr


def test_the_check_parses_under_every_grammar_below_the_floor() -> None:
    """The check's module is the one an interpreter below the floor reads in full, so it holds no syntax
    newer than the oldest grammar that might meet it."""
    source = (PACKAGE_ROOT / "__init__.py").read_text(encoding="utf-8")
    for grammar in ((3, 6), (3, 7), (3, 8), (3, 9), (3, 10)):
        ast.parse(source, filename="__init__.py", feature_version=grammar)


def test_the_wrapper_runs_the_copy_under_a_recorded_interpreter_that_exists(installed: Path, tmp_path: Path) -> None:
    """A recorded interpreter that exists is the one the wrapper runs the copy under."""
    wrapper = _plugin(installed) / "tools/devpro.sh"
    recorded = tmp_path / "recorded-python3"
    recorded.symlink_to(os.path.realpath(sys.executable))
    wrapper.write_text(wrapper_text(str(recorded)), encoding="utf-8")
    ran = _run_wrapper(wrapper, path=_NO_DEVPRO_PATH, home=tmp_path)
    assert (ran.returncode, ran.stdout) == (0, f"{__version__}\n"), ran.stderr


def test_the_wrapper_execs_the_first_python3_on_path_when_its_recorded_one_is_gone(
    installed: Path, tmp_path: Path
) -> None:
    """The first `python3` on PATH runs the copy, the wrapper looking no further and checking no version:
    the floor is the entry point's refusal. Defect: an installed tree whose install-time Python was
    removed could not run devpro, no wrapper being written."""
    wrapper = _plugin(installed) / "tools/devpro.sh"
    wrapper.write_text(wrapper_text(str(tmp_path / "gone" / "python3")), encoding="utf-8")
    usable = tmp_path / "usable"
    usable.mkdir()
    (usable / "python3").symlink_to(os.path.realpath(sys.executable))
    ran = _run_wrapper(wrapper, path=f"{usable}:{_NO_DEVPRO_PATH}", home=tmp_path)
    assert (ran.returncode, ran.stdout) == (0, f"{__version__}\n"), ran.stderr
