"""The committed hook's wiring: the command string and `init`.

`init` writes the profiler skill into a repository's `.claude/` and registers the capture on every
event it records, for a session that loads no plugin's hooks. An install and an `init` both apply the
stores' rename: they move the `claude-profiler` and `opencode-profiler` stores under the project's
`.devpro-temp/` to their `.profiler-*` names.

Every command here names a wrapper its writer knows — the committed hook the project's, the plugin's
the installation's — and none resolves one.

`init` writes claude's hook alone, the harness stated as the argument `capture` takes: each other
harness's capture is its own plugin's. A repository whose install is another harness's, or whose hook
entry names a command a claude `init` did not write, is refused before anything is written — a claude
entry appended there would register a second capture in one settings file.

The renderer is imported where it is used, in `profiler_skill_text`: the hook-run capture reaches this
module for `init`, and the install for `rename_stores` — from `stores`, which imports the store facts
alone — and none of those reads a rendered definition. The package's root is imported at module scope
from `install_base`, which imports nothing of the renderer's.
"""

import json
from pathlib import Path, PurePosixPath
from typing import cast

from devpro.errors import InputError
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
# A claude project install's directory in a repository, the claude plugin's: its wrapper is the one file
# the install writes there. The profiler's skill names the same wrapper as its runner.
INSTALL_WRAPPER = ".claude/skills/devpro/tools/devpro.sh"
# Each harness's committed wrapper, the path its hook entry names: the claude install's beside the skill,
# and the opencode install's plugin wrapper `init` recognizes to refuse rather than register a second
# capture in it. Literals, not derived: `Harness.project_wrapper` renders the same paths, but importing a
# profile here would put the definitions on the capture's import path, as `INSTALL_WRAPPER`'s comment
# says of the claude one.
PROJECT_WRAPPERS = {
    "claude": INSTALL_WRAPPER,
    "opencode": "devpro/plugins/devpro/tools/devpro.sh",
}

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


# The one harness `init` writes settings for: claude's hook is the only one `init` registers, and each
# other harness's capture is its own plugin's.
INIT_HARNESS = "claude"


def hook_entry(harness: str) -> Json:
    """One committed hook entry: the capture for `harness`, run out of band and bounded."""
    return {
        "matcher": "*",
        "hooks": [
            {
                "type": "command",
                "command": _hook_command(f'"$CLAUDE_PROJECT_DIR/{PROJECT_WRAPPERS[harness]}"'),
                "timeout": HOOK_TIMEOUT_S,
                "async": True,
            }
        ],
    }


def is_recognized_command(command: str | None, *, harness: str) -> bool:
    """Whether `command` is a capture this tool wrote for `harness`, under the committed wrapper."""
    return command == _hook_command(f'"$CLAUDE_PROJECT_DIR/{PROJECT_WRAPPERS[harness]}"')


def is_our_command(command: str | None) -> bool:
    """Whether `command` is one this tool wrote, under the committed wrapper."""
    return is_recognized_command(command, harness=INIT_HARNESS)


def any_ours(entry: Json, *, harness: str) -> bool:
    """Whether a hook entry is one this tool wrote for `harness`."""
    return any(is_recognized_command(hook.get("command"), harness=harness) for hook in entry.get("hooks") or [])


def foreign_hook_command(settings: Json) -> str | None:
    """The first command an existing hook entry names that a claude `init` did not write, or `None`."""
    for entries in (settings.get("hooks") or {}).values():
        for entry in entries or []:
            for hook in entry.get("hooks") or []:
                command = cast(str | None, hook.get("command"))
                if command is not None and not is_our_command(command):
                    return command
    return None


def merge_hooks(settings: Json, *, harness: str) -> Json:
    """`settings` with this tool's entries for `harness` on every captured event, in the place of the
    first one it wrote and appending nothing while another install's command stands in them."""
    merged = {**settings, "hooks": {**(settings.get("hooks") or {})}}
    if foreign_hook_command(settings) is not None:
        return merged
    for event in CAPTURED_EVENTS:
        entries = merged["hooks"].get(event) or []
        ours = [index for index, entry in enumerate(entries) if any_ours(entry, harness=harness)]
        if not ours:
            merged["hooks"][event] = [*entries, hook_entry(harness)]
        else:
            rest = [entry for index, entry in enumerate(entries) if index not in ours]
            merged["hooks"][event] = [*entries[: ours[0]], hook_entry(harness), *rest]
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
    too, as an install renames them.

    A repository whose devpro install is another harness's, or whose hook entry names a command this
    `init` did not write, is refused, with nothing written: `init claude` is claude's alone."""
    if not argv or argv[0] != INIT_HARNESS:
        raise UsageError("Usage: devpro profiler init claude")
    repo = git_root(cwd)
    if not repo:
        raise UsageError("Run devpro profiler init inside a git repository.")
    if repo.resolve() == PACKAGE_ROOT or repo.resolve().is_relative_to(PACKAGE_ROOT):
        raise UsageError(
            f"This repository's root is the running devpro package's source, {PACKAGE_ROOT}: "
            "init writes into a project, not the package running it."
        )
    other = next(
        (name for name in PROJECT_WRAPPERS if name != INIT_HARNESS and (repo / PROJECT_WRAPPERS[name]).is_file()), None
    )
    if other is not None:
        raise InputError(
            f"This project's devpro install is {other}'s ({PROJECT_WRAPPERS[other]}): `init` registers"
            " claude's hook alone, and the opencode plugin records every call itself."
        )
    settings_file = repo / ".claude" / "settings.json"
    settings = json.loads(settings_file.read_text(encoding="utf-8")) if settings_file.exists() else {}
    if not isinstance(settings, dict):
        settings = {}
    foreign = foreign_hook_command(settings)
    if foreign is not None:
        raise InputError(
            f".claude/settings.json already registers {foreign}, which `init` did not write: it will not"
            f' add "{HOOK_COMMAND}" beside it.'
        )
    skill = repo / ".claude" / PROFILER_SKILL
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(profiler_skill_text(), encoding="utf-8")
    staged = [
        Path(".claude") / PROFILER_SKILL,
        Path(".claude") / "settings.json",
    ]

    settings_file.write_text(json.dumps(merge_hooks(settings, harness=INIT_HARNESS), indent=2) + "\n", encoding="utf-8")
    return "\n".join(
        [
            "Added the profiler skill and registered its capture for the project's wrapper in"
            " .claude/settings.json.",
            *rename_stores(repo),
            "Commit them; Claude Code on the web picks the hook up in the next session:",
            "  git add " + " ".join(path.as_posix() for path in staged),
        ]
    )
