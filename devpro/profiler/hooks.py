"""The committed hook's wiring: the command string, `init`, and `doctor`.

`init` writes the launcher and the show-profile skill into a repository's `.claude/` and registers the
capture on every event it records, for a session that loads no plugin's hooks. `doctor` says whether
capture works in a repository, and why not. Both apply the stores' rename: an install and an `init` move
the `claude-profiler` and `opencode-profiler` stores under the project's `.devpro-temp/` to their
`.profiler-*` names.

The renderer and the package's root are imported where they are used, in `show_skill_text` and
`launcher_resource`: the hook-run capture reaches this module for `doctor` and `init`, and the install
for `rename_stores` — from `stores`, which imports the store facts alone — and none of those reads a
rendered definition or a package path.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from devpro.install_base import PACKAGE_ROOT

from .pages import UsageError, list_sessions
from .stores import OLD_STORE_SUFFIX, old_store_name, rename_stores
from .values import (
    CAPTURED_EVENTS,
    SHOW_SKILL,
    TRACE_DIR,
    TRACE_GLOB,
    _iso,
    _json,
    _utc,
    git_root,
    project_dir,
    read_json,
    read_text,
)

LAUNCHER = "hp.sh"
# Before 0.2.0 the launcher was `hp`, and a committed hook ran it by that name.
OLD_LAUNCHER = "hp"
HOOK_TIMEOUT_S = 5
HOOK_DIR = Path(".claude") / "harness-profiler"
HOOK_FILES = (LAUNCHER,)
# The files an older `init` copied beside the launcher, which no install ships any more.
RETIRED_HOOK_FILES = ("hp.py", "view.html")
# The harness resource the launcher is the master of: the install copies it, and `init` copies it again
# into the repository's committed hook directory.
HARNESS_RESOURCES = Path("harnesses") / "resources" / "claude" / "profiler"
# The candidates the launcher's finder searches after `PATH`, in its order. `HP_DEVPRO`, where set,
# replaces the search rather than leading it; doctor lists them here so its line names what the launcher
# would resolve.
DEVPRO_CANDIDATES = ("/opt/homebrew/bin/devpro", "/usr/local/bin/devpro")

USAGE = """Usage:
  devpro profiler tree [session-id-prefix] [--branch <name>] [--verbose] [--format text|html]
  devpro profiler init claude
  devpro profiler doctor
  devpro profiler capture <harness>  (run by the hook, not by hand)"""


def launcher_resource() -> Path:
    """The launcher as the devpro package ships it."""
    return PACKAGE_ROOT / HARNESS_RESOURCES / LAUNCHER


def devpro_executable() -> str | None:
    """The devpro command the launcher's finder would resolve here, or nothing where none is usable."""
    override = os.environ.get("HP_DEVPRO")
    if override is not None:
        return override if os.access(override, os.X_OK) else None
    found = shutil.which("devpro")
    candidates = (found, *DEVPRO_CANDIDATES, str(Path.home() / ".local" / "bin" / "devpro"))
    return next((candidate for candidate in candidates if candidate and os.access(candidate, os.X_OK)), None)


def _hook_command(launcher: str) -> str:
    """The command a committed hook runs: this launcher, under the repository's `.claude/`."""
    return f'/bin/bash "$CLAUDE_PROJECT_DIR/.claude/harness-profiler/{launcher}" capture claude'


HOOK_COMMAND = _hook_command(LAUNCHER)
OLD_HOOK_COMMAND = _hook_command(OLD_LAUNCHER)


def hook_entry() -> dict:
    """One committed hook entry: the capture, run out of band and bounded."""
    return {
        "matcher": "*",
        "hooks": [{"type": "command", "command": HOOK_COMMAND, "timeout": HOOK_TIMEOUT_S, "async": True}],
    }


def is_our_command(command: str | None) -> bool:
    """Whether `command` is one this tool wrote, under this launcher's name or the one before 0.2.0."""
    return command in (HOOK_COMMAND, OLD_HOOK_COMMAND)


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


def show_skill_text() -> str:
    """The show-profile skill as a claude project install renders it."""
    from devpro.context import build_render
    from devpro.render import render_all

    ctx = build_render(harness="claude", components="", family="claude", supply=None)
    return dict(render_all(ctx))[SHOW_SKILL / "SKILL.md"]


def init(argv: list[str], cwd: Path | str) -> str:
    """Commit the hook into the repository at `cwd`: the launcher and the skill, and the six entries in
    its `.claude/settings.json`, for a session that loads no plugin's hooks. The repository's stores
    from before the `.profiler-*` rename are renamed here too, as an install renames them."""
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
    target = repo / HOOK_DIR
    target.mkdir(parents=True, exist_ok=True)
    for name in HOOK_FILES:
        shutil.copyfile(launcher_resource().parent / name, target / name)
    (target / LAUNCHER).chmod(0o755)
    for name in (OLD_LAUNCHER, *RETIRED_HOOK_FILES):
        (target / name).unlink(missing_ok=True)
    skill = repo / ".claude" / SHOW_SKILL
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(show_skill_text(), encoding="utf-8")

    settings_file = repo / ".claude" / "settings.json"
    settings = json.loads(settings_file.read_text(encoding="utf-8")) if settings_file.exists() else {}
    if not isinstance(settings, dict):
        settings = {}
    settings_file.write_text(json.dumps(merge_hooks(settings), indent=2) + "\n", encoding="utf-8")
    return "\n".join(
        [
            f"Copied the hook to {target.relative_to(repo)}/, registered it in .claude/settings.json,"
            " and added the show-profile skill.",
            *rename_stores(repo),
            "Commit them; Claude Code on the web picks the hook up in the next session:",
            "  git add .claude/harness-profiler .claude/skills/show-profile .claude/settings.json",
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
        settings = read_json(file)
        hooks = settings.get("hooks") if isinstance(settings, dict) else None
        if settings and "harness-profiler/hp" in _json(hooks or {}):
            sources.append(label)
    return sources


def stale_hook(repo: Path) -> str | None:
    """What a hook committed by an older `init` lacks: events added since, `async`, and the files as
    this copy has them."""
    settings = read_json(repo / ".claude" / "settings.json")
    hooks = (settings.get("hooks") if isinstance(settings, dict) else None) or {}

    def ours(event: str) -> list[dict]:
        entries = [entry for entry in hooks.get(event) or [] if is_ours(entry)]
        return [hook for entry in entries for hook in entry.get("hooks") or [] if is_our_command(hook.get("command"))]

    if not any(ours(event) for event in CAPTURED_EVENTS):
        return None
    missing = [event for event in CAPTURED_EVENTS if not ours(event)]
    blocking = any(any(hook.get("async") is not True for hook in ours(event)) for event in CAPTURED_EVENTS)
    resource = launcher_resource().parent
    changed = [name for name in HOOK_FILES if read_text(repo / HOOK_DIR / name) != read_text(resource / name)]
    gaps = [
        f"misses {', '.join(missing)}" if missing else "",
        "is not async" if blocking else "",
        f"has another version of {', '.join(changed)}" if changed else "",
    ]
    return " and ".join(gap for gap in gaps if gap) or None


def doctor(cwd: Path | str) -> str:
    """Whether capture works here, and why not: the toolchain, the store and the pattern `tree` reads,
    the hook's registration, any store from before the rename, a stale committed hook, and the newest
    claude session."""
    directory = project_dir(cwd)
    # doctor is claude-facing: every other line reads claude's hook and this directory's claude sessions,
    # so `newest` is claude's store alone, and the `traces` line names it beside what `tree` reads.
    claude_store = Path(directory) / TRACE_DIR
    claude_sessions = [session for session in list_sessions(directory) if session["path"].parent == claude_store]
    newest = max((session["last"] for session in claude_sessions), default=None)
    repo = git_root(cwd) or Path(cwd)
    sources = hook_sources(repo, Path.home())
    stale = stale_hook(repo)
    installed = (
        ", ".join(sources) if sources else "not installed (install the plugin, or run devpro profiler init claude)"
    )
    devpro = devpro_executable() or "not found on PATH, in Homebrew or ~/.local/bin (install devpro)"
    lines = [
        f"devpro:  {devpro}",
        f"traces:  {claude_store} (tree reads {Path(directory) / TRACE_DIR.parent / TRACE_GLOB})",
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
        f"newest:  {_iso(_utc(newest)) if newest is not None else 'no calls recorded yet'}",
    ]
    return "\n".join(line for line in lines if line)
