"""Fixtures every test runs under, and the helpers more than one test module shares."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A home directory under `tmp_path`, created by the tests that use it. `HOME` names it for every
    test and every process a test starts, so nothing the suite runs reads or writes the operator's real
    home."""
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    return home


def settings_file(tmp_path: Path, text: str) -> Path:
    """A devpro settings file holding `text`, for the CLI to read with `--config-file`."""
    path = tmp_path / "devpro.cfg"
    path.write_text(text, encoding="utf-8")
    return path
