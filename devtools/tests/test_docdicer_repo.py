"""`docdicer-repo` keeps the hosted docdicer clone at the tag the shipped launcher pins.

Defect these fail on: the recipe clones `docdicer/` once and never moves it, so the clone stays at
whatever tag it was made at — `v0.11.2` while `devpro/docdicer-tools/docdicer` pins `v0.12.0` — and
`dev-dd` runs a different docdicer than the pin the installed snippet routes name. Nothing in this
directory read the runner at all, so the drift went unobserved.

The recipe's job needs the network and a real clone, so these read the runner text instead: the pin
comes from the launcher's file, and the step that follows it is there to be run.
"""

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_JUSTFILE = _ROOT / "justfile"
_LAUNCHER = "devpro/docdicer-tools/docdicer"
_VERSION = re.compile(r"\bv?\d+\.\d+\.\d+\b")
_SCRIPT = re.compile(r"devtools/scripts/[\w-]+\.sh")


def _recipe_body(name: str) -> str:
    """The recipe's body lines from the justfile, up to the next unindented line."""
    lines = _JUSTFILE.read_text(encoding="utf-8").splitlines()
    body = []
    for line in lines[lines.index(f"{name}:") + 1 :]:
        if line.strip() and not line.startswith((" ", "\t")):
            break
        body.append(line)
    return "\n".join(body)


def _script_the_recipe_runs(body: str) -> str:
    scripts = _SCRIPT.findall(body)
    assert len(scripts) == 1, f"docdicer-repo's body names these scripts, not the one step it runs: {scripts}"
    return (_ROOT / scripts[0]).read_text(encoding="utf-8")


def test_the_recipe_reads_the_pin_from_the_launcher_rather_than_carrying_one():
    body = _recipe_body("docdicer-repo")
    assert _LAUNCHER in body, f"docdicer-repo does not read its pin from {_LAUNCHER}"
    assert not _VERSION.search(body), f"docdicer-repo hard-codes a version rather than reading the pin:\n{body}"


def test_the_recipe_has_the_step_that_moves_a_clone_off_another_tag_to_the_pin():
    step = _script_the_recipe_runs(_recipe_body("docdicer-repo"))
    assert "git describe --tags --abbrev=0" in step, "the step never reads the tag the clone is at"
    assert "git fetch --tags" in step, "the step never fetches the tags the pin may be among"
    assert re.search(r"git checkout[^\n]*DOCDICER_PIN", step), "the step never checks the clone out to the pin"


def test_the_step_reports_local_changes_instead_of_resetting_them():
    step = _script_the_recipe_runs(_recipe_body("docdicer-repo"))
    assert "git status --porcelain" in step, "the step never reads whether the clone is dirty"
    assert not re.search(
        r"git (?:reset --hard|clean -\w)", step
    ), "the step discards local work instead of reporting it"
