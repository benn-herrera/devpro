"""The profiler's stores: the move an install and an `init` make from the store
naming before the rename. Imports the store facts alone, so the install, which renames on every run, pays for
no other module of the package.
"""

from pathlib import Path

from .values import NEW_STORE_PREFIX, TRACE_DIR

OLD_STORE_SUFFIX = "-profiler"
# The old-pattern store names an install and an `init` rename, each to its `.profiler-*` name: the
# claude and opencode captures' stores, and nothing else a project's `.devpro-temp/` holds. An
# operator's own directory can carry the suffix — Claude Code's convention is to — and a rename
# matching the shape alone takes it.
OLD_STORES = ("claude", "opencode")


def old_store_name(store: str) -> str | None:
    """The `.profiler-*` name the old-pattern store `store` takes, or nothing where it is no old-pattern
    store's name, nor a name of the new pattern either."""
    if store.endswith(OLD_STORE_SUFFIX) and store[: -len(OLD_STORE_SUFFIX)] in OLD_STORES:
        return NEW_STORE_PREFIX + store[: -len(OLD_STORE_SUFFIX)]
    return None


def rename_stores(directory: Path | str) -> list[str]:
    """Rename the project's old-pattern stores under `directory`'s `.devpro-temp/`, each to its
    `.profiler-*` name, and return one line per store the rename leaves standing.

    A rename is reported where it happens. A store whose new name is already taken is left as it stands
    and named instead: the stores' contents are never merged, and merging or deleting the old store is
    the operator's call, not this call's. Any other name is left alone, the new pattern's own included,
    so a second run touches nothing."""
    stores = Path(directory) / TRACE_DIR.parent
    lines = []
    for old in sorted(stores.glob(f"*{OLD_STORE_SUFFIX}")) if stores.is_dir() else []:
        new = old_store_name(old.name)
        if new is None or not old.is_dir():
            continue
        if (stores / new).exists():
            lines.append(
                f"left {old} in place: {stores / new} already exists, so its traces were not merged — "
                "merge or delete the old store yourself"
            )
            continue
        old.rename(stores / new)
        lines.append(f"renamed {old} → {stores / new}")
    return lines
