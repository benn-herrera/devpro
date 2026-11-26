"""The committed hook's wiring: the command string and `init`.

`init` writes the profiler skill into a repository's `.claude/` and registers the capture on every
event it records, for a session that loads no plugin's hooks. An install and an `init` both apply the
stores' rename: they move the `claude-profiler` and `opencode-profiler` stores under the project's
`.devpro-temp/` to their `.profiler-*` names.

Every command here names a wrapper its writer knows — the committed hook the project's, the plugin's
the installation's — and none resolves one.

The renderer is imported where it is used, in `profiler_skill_text`: the hook-run capture reaches this
module for `init`, and the install for `rename_stores` — from `stores`, which imports the store facts
alone — and none of those reads a rendered definition. The package's root is imported at module scope
from `install_base`, which imports nothing of the renderer's.
"""

import json
from pathlib import Path, PurePosixPath

from devpro.install_base import PACKAGE_ROOT

from .pages import UsageError
from .stores import rename_stores
from .values import (
    CAPTURED_EVENTS,
    PROFILER_SKILL,
    Json,
    git_root,
)

HOOK_TIMEOUT_S = 5
HOOK_DIR = Path(".claude") / "harness-profiler"
# The launchers an older `init` wrote into the hook directory, under the names they had before the file
# was retired: an `init` unlinks them, and a hook command spelling one stays this tool's.
RETIRED_LAUNCHERS = ("hp.sh", "hp", "profiler.sh")
# The files an older `init` copied into the hook directory beside the launcher, which no install ships.
RETIRED_HOOK_FILES = ("hp.py", "view.html")
# The skill directory an older `init` rendered, under the skill's name before `profiler`.
RETIRED_SKILL = Path("skills") / "show-profile"
# A claude project install's directory in a repository, the claude plugin's: its wrapper is the one file
# the install writes there. A literal, not derived: the claude harness profile's `project_wrapper`
# renders the same path, but importing the profile bound to the install's name here would put the
# definitions on the capture's import path. The profiler's skill names the same wrapper as its runner.
INSTALL_WRAPPER = ".claude/skills/devpro/tools/devpro.sh"

USAGE = """Usage:
  devpro profiler tree [session-id-prefix] [--branch <name>] [--verbose] [--format text|html]
  devpro profiler init claude
  devpro profiler capture <harness>  (run by the hook, not by hand)"""


def _hook_command(wrapper: str) -> str:
    """The command a hook runs: `wrapper`, then the capture's one shape."""
    return f"{wrapper} profiler capture claude"


# The committed hook's command: the project's committed wrapper, which `init` renders the skill beside,
# named from the project root the hook is run from.
HOOK_COMMAND = _hook_command(f'"$CLAUDE_PROJECT_DIR/{INSTALL_WRAPPER}"')
# The commands an older `init` wrote: a launcher under the hook directory, in each name it had, run
# under `/bin/bash`. A hook spelling one stays this tool's, and an `init` re-run replaces it.
OLD_HOOK_COMMANDS = tuple(
    f'/bin/bash "$CLAUDE_PROJECT_DIR/{HOOK_DIR.as_posix()}/{name}" capture claude' for name in RETIRED_LAUNCHERS
)
# The spellings a settings file holds for one of those commands, the file read as text for them: a
# registration is found there whatever JSON shape it takes.
_OUR_COMMAND_SPELLINGS = (
    *(f"{HOOK_DIR.as_posix()}/{name}" for name in RETIRED_LAUNCHERS),
    *(INSTALL_WRAPPER.rsplit("/", count)[0] for count in range(len(INSTALL_WRAPPER.split("/")) - 1, 0, -1)),
    *OLD_HOOK_COMMANDS,
)


def hook_entry() -> Json:
    """One committed hook entry: the capture, run out of band and bounded."""
    return {
        "matcher": "*",
        "hooks": [{"type": "command", "command": HOOK_COMMAND, "timeout": HOOK_TIMEOUT_S, "async": True}],
    }


def is_our_command(command: str | None) -> bool:
    """Whether `command` is one this tool wrote, under the committed wrapper or an older launcher."""
    return command in (HOOK_COMMAND, *OLD_HOOK_COMMANDS)


def is_ours(entry: Json) -> bool:
    """Whether a hook entry is one this tool wrote."""
    return any(is_our_command(hook.get("command")) for hook in entry.get("hooks") or [])


def merge_hooks(settings: Json) -> Json:
    """`settings` with this tool's entry on every captured event.

    An entry an older `init` wrote is replaced in place, so a re-run picks up new hook options."""
    merged = {**settings, "hooks": {**(settings.get("hooks") or {})}}
    for event in CAPTURED_EVENTS:
        entries = merged["hooks"].get(event) or []
        at = next((index for index, entry in enumerate(entries) if is_ours(entry)), None)
        if at is None:
            merged["hooks"][event] = [*entries, hook_entry()]
        else:
            rest = [entry for entry in entries[at + 1 :] if not is_ours(entry)]
            merged["hooks"][event] = [*entries[:at], hook_entry(), *rest]
    return merged


def profiler_skill_text() -> str:
    """The profiler skill as a claude project install renders it."""
    from devpro.context import build_render
    from devpro.render import render_all

    ctx = build_render(harness="claude", components="", family="claude", supply=None)
    return dict(render_all(ctx))[PurePosixPath((PROFILER_SKILL / "SKILL.md").as_posix())]


def init(argv: list[str], cwd: Path | str) -> str:
    """Commit the hook into the repository at `cwd`: the skill, and the six entries in its
    `.claude/settings.json`, for a session that loads no plugin's hooks, run through the project's
    committed wrapper. The repository's stores from before the `.profiler-*` rename are renamed here
    too, as an install renames them."""
    if not argv or argv[0] != "claude":
        raise UsageError("Usage: devpro profiler init claude")
    repo = git_root(cwd)
    if not repo:
        raise UsageError("Run devpro profiler init inside a git repository.")
    if repo.resolve() == PACKAGE_ROOT or repo.resolve().is_relative_to(PACKAGE_ROOT):
        raise UsageError(
            f"This repository's root is the running devpro package's source, {PACKAGE_ROOT}: "
            "init writes into a project, not the package running it."
        )
    skill = repo / ".claude" / PROFILER_SKILL
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(profiler_skill_text(), encoding="utf-8")
    target = repo / HOOK_DIR
    retired = [path for path in (target / name for name in (*RETIRED_LAUNCHERS, *RETIRED_HOOK_FILES)) if path.exists()]
    for path in retired:
        path.unlink()
    if target.is_dir() and not any(target.iterdir()):
        target.rmdir()
    retired_skill = repo / ".claude" / RETIRED_SKILL
    removed_retired_skill = (retired_skill / "SKILL.md").is_file()
    (retired_skill / "SKILL.md").unlink(missing_ok=True)
    if retired_skill.is_dir() and not any(retired_skill.iterdir()):
        retired_skill.rmdir()
    retired_dirs = [Path(".claude") / RETIRED_SKILL] if removed_retired_skill else []
    staged = [
        Path(".claude") / PROFILER_SKILL,
        *retired_dirs,
        *(path.relative_to(repo) for path in retired),
        Path(".claude") / "settings.json",
    ]

    settings_file = repo / ".claude" / "settings.json"
    settings = json.loads(settings_file.read_text(encoding="utf-8")) if settings_file.exists() else {}
    if not isinstance(settings, dict):
        settings = {}
    settings_file.write_text(json.dumps(merge_hooks(settings), indent=2) + "\n", encoding="utf-8")
    return "\n".join(
        [
            "Added the profiler skill and registered its capture for the project's wrapper in"
            " .claude/settings.json.",
            *rename_stores(repo),
            "Commit them; Claude Code on the web picks the hook up in the next session:",
            "  git add " + " ".join(path.as_posix() for path in staged),
        ]
    )
