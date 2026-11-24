"""The profiler's stores and their one repair: the move an install and an `init` make from the store
naming before the rename, and the one-shot fill of the child ids a capture wrote before it read opencode
2.4.1's result shape. Imports the store facts alone, so the install, which renames on every run, pays for
no other module of the package.
"""

import json
import os
import re
from pathlib import Path

from .values import NEW_STORE_PREFIX, TRACE_DIR, _json

OLD_STORE_SUFFIX = "-profiler"
# The old-pattern store names an install and an `init` rename, each to its `.profiler-*` name: the
# claude and opencode captures' stores, and nothing else a project's `.devpro-temp/` holds. An
# operator's own directory can carry the suffix — Claude Code's convention is to — and a rename
# matching the shape alone takes it.
OLD_STORES = ("claude", "opencode")
# The store the repair reads: the claude capture never writes a child session id.
OPENCODE_STORE = f"{NEW_STORE_PREFIX}opencode"
# An opencode subagent call's record, in the tool's own spelling.
SUBAGENT = "Agent"
# The host's session id as a record's stored result text carries it: 2.4.1's background notice states it
# as `(sessionID: ses_…)`.
_CHILD_ID = re.compile(r"\bses_[A-Za-z0-9]+")


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


def child_id_in(result: object) -> str | None:
    """The child session id a record's stored result text names, and nothing where it names none.

    The record's `result` is the host's own text, one-lined and clipped to `RESULT_LIMIT`, so the id
    reads out of it as the host wrote it. A result clipped before the id survives names no child, and
    the record stays null."""
    text = result if isinstance(result, str) else ""
    found = _CHILD_ID.search(text)
    return found.group(0) if found is not None else None


def _record(line: str) -> dict | None:
    """The record a store's line holds, or nothing where it does not parse as one."""
    try:
        record = json.loads(line)
    except ValueError:
        return None
    return record if isinstance(record, dict) else None


def _is_subagent(record: dict | None) -> bool:
    """Whether a record is an opencode subagent call's: the one kind the repair fills and counts."""
    return record is not None and record.get("tool") == SUBAGENT and record.get("harness") == "opencode"


def repair_child_ids(directory: Path | str) -> tuple[int, int, list[Path]]:
    """Read every standing opencode record once, fill each subagent call's `child_agent_id` where its
    stored result names the child, and return the edges written, the records left null, and the files
    left as they stand.

    Run once, before the installation updates: a capture that reads opencode 2.4.1's result shape writes
    the id at the record's creation, and a record written before it carries the id only in its result
    text. A record whose id is already right stays untouched, so a second run fills nothing. A file a
    capture appends to while the repair reads it is named and left alone: the rewrite is one rename onto
    the file, so a record appended between the read and the rename would be lost, and a session that
    writes its trace during the read is the evidence that it may. The null count is every subagent
    record that names no child once the repair has run — a dispatch that failed before creating a child,
    one whose result was clipped before its id, and each record of a file left as it stands, among
    them."""
    store = Path(directory) / TRACE_DIR.parent / OPENCODE_STORE
    repaired = null = 0
    left: list[Path] = []
    for file in sorted(store.glob("*.jsonl")) if store.is_dir() else []:
        before = file.stat()
        text = file.read_text(encoding="utf-8", errors="replace")
        after = file.stat()
        changed = (before.st_ino, before.st_size) != (after.st_ino, after.st_size)
        lines = text.splitlines()
        rewritten: list[str] = []
        filled = 0
        for line in lines:
            record = _record(line)
            if _is_subagent(record):
                if not record.get("child_agent_id"):
                    child = child_id_in(record.get("result"))
                    if child is not None:
                        record = {**record, "child_agent_id": child}
                        line = _json(record)
                        filled += 1
                if not record.get("child_agent_id"):
                    null += 1
            rewritten.append(line)
        if changed:
            # Nothing is written, so the fills stay absent from the file: the records they would have
            # filled are among those left naming no child.
            left.append(file)
            null += filled
        elif rewritten != lines:
            _atomic_text(file, "\n".join(rewritten) + "\n")
            repaired += filled
    return repaired, null, left


def _atomic_text(file: Path, text: str) -> None:
    """Write `file`'s text through a sibling temp file and one rename, so a reader meets the whole text
    or the previous one, never a half-written line, and an interrupted repair leaves the store as it
    was."""
    temp = file.with_name(f".{file.name}.repair")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, file)
