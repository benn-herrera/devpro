"""Fixtures every test runs under, and the helpers and values more than one test module shares."""

import json
from pathlib import Path

import pytest

from devpro.components import Components

PLAIN = Components()
"""The selection with no optional component on."""
WITH_KBASE = Components(on=frozenset({"kbase"}))
"""The selection with the kbase component on."""


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
    path = tmp_path / "devpro.cfg"
    path.write_text(text, encoding="utf-8")
    return path


def page_data(page: str) -> dict:
    """The JSON a profiler page inlines at its data slot, whichever carrier served it."""
    return json.loads(page.split("const D = ", 1)[1].split(";\n", 1)[0])
