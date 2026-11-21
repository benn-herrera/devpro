"""The dicing surface is offered as `devpro <verb>`: `devpro --help` lists every dicing verb.

The defect: the nine dicing verbs are the absorbed dicing surface's command-line offering, and
without them `devpro dice-doc` is refused by argparse (`invalid choice: 'dice-doc'`, exit 2) — the
offered surface does not include them. `devpro --help` lacks every verb name before the change.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from devpro.cli import DICING_VERBS

REPO_ROOT = Path(__file__).resolve().parents[2]


def _help() -> bytes:
    env = {**os.environ, "COLUMNS": "1000", "PYTHONPATH": str(REPO_ROOT)}
    return subprocess.run(
        [sys.executable, "-m", "devpro", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=True,
    ).stdout


@pytest.mark.parametrize("verb", DICING_VERBS)
def test_help_lists_each_dicing_verb(verb: str) -> None:
    assert verb.encode() in _help()
