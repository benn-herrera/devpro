"""The committed hook's wiring: the command string, `init`, and `doctor`.

`init` writes the profiler skill into a repository's `.claude/` and registers the capture on every
event it records, for a session that loads no plugin's hooks. `doctor` says whether capture works in
a repository, and why not. Both apply the stores' rename: an install and an `init` move the
`claude-profiler` and `opencode-profiler` stores under the project's `.devpro-temp/` to their
`.profiler-*` names.

Every command here names a wrapper its writer knows — the committed hook the project's, the plugin's
the installation's — and none resolves one.

The renderer is imported where it is used, in `profiler_skill_text`: the hook-run capture reaches this
module for `doctor` and `init`, and the install for `rename_stores` — from `stores`, which imports the
store facts alone — and none of those reads a rendered definition. The package's root is imported at
module scope from `install_base`, which imports nothing of the renderer's.
"""

import json
import sys
from pathlib import Path

from devpro.install_base import PACKAGE_ROOT

from .pages import UsageError, list_sessions, stamp
from .stores import OLD_STORE_SUFFIX, old_store_name, rename_stores
from .values import (
    CAPTURED_EVENTS,
    PROFILER_SKILL,
    TRACE_DIR,
    TRACE_STORES,
    _json,
    git_root,
    project_dir,
    read_json,
    read_text,
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
  devpro profiler doctor
  devpro profiler repair  (once, after the capture reads the host's current result shape)
  devpro profiler capture <harness>  (run by the hook, not by hand)"""


def devpro_command() -> str:
    """The `devpro` command doctor's `devpro:` line names: the tree that ran it, as
    `<python> -m devpro --from <its root>`, or the `devpro` command on PATH where the tree is not one
    this project's own sources answer for — a wheel in site-packages, which no line of this
    repository's names."""
    if PACKAGE_ROOT.parent.name in ("tools", "devpro"):
        return f"{sys.executable} -m devpro --from {PACKAGE_ROOT.parent}"
    return "devpro (on PATH)"


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


def hook_entry() -> dict:
    """One committed hook entry: the capture, run out of band and bounded."""
    return {
        "matcher": "*",
        "hooks": [{"type": "command", "command": HOOK_COMMAND, "timeout": HOOK_TIMEOUT_S, "async": True}],
    }


def is_our_command(command: str | None) -> bool:
    """Whether `command` is one this tool wrote, under the committed wrapper or an older launcher."""
    return command in (HOOK_COMMAND, *OLD_HOOK_COMMANDS)


def is_ours(entry: dict) -> bool:
    """Whether a hook entry is one this tool wrote."""
    return any(is_our_command(hook.get("command")) for hook in entry.get("hooks") or [])


def merge_hooks(settings: dict) -> dict:
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
    return dict(render_all(ctx))[PROFILER_SKILL / "SKILL.md"]


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


def hook_sources(repo: Path, home: Path) -> list[str]:
    """Where a capture hook is registered for this repository: the plugin's own records, and the three
    settings files that can carry one."""
    sources = []
    installed = read_json(home / ".claude" / "plugins" / "installed_plugins.json")
    if installed is not None:
        plugins = installed.get("plugins") if isinstance(installed, dict) else None
        if "harness-profiler" in _json(plugins if plugins else installed):
            sources.append("plugin")
    for label, file in (
        ("committed hooks", repo / ".claude" / "settings.json"),
        ("local settings hooks", repo / ".claude" / "settings.local.json"),
        ("user settings hooks", home / ".claude" / "settings.json"),
    ):
        text = read_text(file)
        if text and any(command in text for command in _OUR_COMMAND_SPELLINGS):
            sources.append(label)
    return sources


def stale_hook(repo: Path) -> str | None:
    """What a hook committed by an older `init` lacks: events added since, `async`, and the wrapper's
    command as this devpro's wiring states it."""
    settings = read_json(repo / ".claude" / "settings.json")
    hooks = (settings.get("hooks") if isinstance(settings, dict) else None) or {}

    def ours(event: str) -> list[dict]:
        return [
            hook
            for entry in hooks.get(event) or []
            if is_ours(entry)
            for hook in entry.get("hooks") or []
            if is_our_command(hook.get("command"))
        ]

    if not any(ours(event) for event in CAPTURED_EVENTS):
        return None
    missing = [event for event in CAPTURED_EVENTS if not ours(event)]
    blocking = any(any(hook.get("async") is not True for hook in ours(event)) for event in CAPTURED_EVENTS)
    replaced = any(hook.get("command") != HOOK_COMMAND for event in CAPTURED_EVENTS for hook in ours(event))
    gaps = [
        f"misses {', '.join(missing)}" if missing else "",
        "is not async" if blocking else "",
        f"runs another command than {HOOK_COMMAND}" if replaced else "",
    ]
    return " and ".join(gap for gap in gaps if gap) or None


def doctor(cwd: Path | str) -> str:
    """Whether capture works here, and why not: the `devpro` command that runs it, the store and the
    stores `tree` reads, the hook's registration, any store from before the rename, a stale committed
    hook, and the newest claude session."""
    directory = project_dir(cwd)
    # doctor is claude-facing: every other line reads claude's hook and this directory's claude sessions,
    # so `newest` is claude's store alone, named among the stores the `traces` line lists.
    claude_store = Path(directory) / TRACE_DIR
    claude_sessions = [session for session in list_sessions(directory) if session["path"].parent == claude_store]
    newest = max((session["last"] for session in claude_sessions), default=None)
    stores = Path(directory) / TRACE_DIR.parent
    reads = ", ".join(str(stores / name) for name in TRACE_STORES)
    repo = git_root(cwd) or Path(cwd)
    sources = hook_sources(repo, Path.home())
    stale = stale_hook(repo)
    installed = (
        ", ".join(sources) if sources else "not installed (install the plugin, or run devpro profiler init claude)"
    )
    lines = [
        f"devpro:  {devpro_command()}",
        f"traces:  tree reads {reads}",
        f"hook:    {installed}",
    ]
    # A store from before the rename is one `tree` cannot see, and no devpro command merges two stores:
    # where its new name stands the operator merges or deletes it, and elsewhere the `mv` or the `init`
    # renames it. The `mv` is the remedy wherever an install cannot run — this repository's own install
    # refuses its root, the package's source, so the straggler here stands until it is moved by hand.
    for store in sorted((Path(directory) / TRACE_DIR.parent).glob(f"*{OLD_STORE_SUFFIX}")):
        if store.is_dir() and (new := old_store_name(store.name)) is not None:
            target = Path(directory) / TRACE_DIR.parent / new
            remedy = (
                f"{target} already exists, and devpro never merges two stores: merge or delete the old one "
                f"yourself, by moving its files into {target} and removing this directory"
                if target.exists()
                else f"move it there yourself, mv {store} {target}, or run devpro profiler init claude, which renames it"
            )
            lines.append(f"old:     {store} is not a store tree reads; {remedy}")
    lines += [
        f"update:  the committed hook {stale}; run devpro profiler init claude again and commit" if stale else None,
        f"newest:  {stamp(newest) if newest is not None else 'no calls recorded yet'}",
    ]
    return "\n".join(line for line in lines if line)
