"""What the capture, the render and the hook wiring all read: the schema and record limits, the masks,
the stores' names and the directories the readers read, the text helpers, and the git facts a record
and a project root take without spawning git. The stores' rename and the two names it moves from are
`stores`'s, which reads this module and nothing else of the package.
"""

import json
import math
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, cast

Json = dict[str, Any]
"""A record as the capture writes it: a JSON object, its fields' values whatever the writer put there."""

SCHEMA_VERSION = 3
# The store naming's prefix every name now carries; `stores` holds the naming before the rename, and the
# two stores it renames.
NEW_STORE_PREFIX = ".profiler-"
# Each harness's capture owns one store, named exactly for the harness its records carry, and `tree`
# reads them all — a dot name, so the stores group at the top of the scratch tree. A directory of any
# other shape there is no store, so a copy of one is not read beside it.
TRACE_HARNESSES = ("claude", "opencode")
TRACE_DIR = Path(".devpro-temp") / f"{NEW_STORE_PREFIX}claude"
TRACE_STORES = tuple(f"{NEW_STORE_PREFIX}{harness}" for harness in TRACE_HARNESSES)
TOOL_EVENTS = ("PostToolUse", "PostToolUseFailure")
SESSION_EVENTS = ("PreCompact", "PostCompact", "SessionStart", "SubagentStop")
LAUNCHED = "async_launched"
CAPTURED_EVENTS = (*TOOL_EVENTS, *SESSION_EVENTS)
COPY_AGENT_TYPE = "fork"
MAIN = "main"
PROFILER_SKILL = Path("skills") / "profiler"
DUPLICATE_EVENT_MS = 5000
TRANSCRIPT_TAIL_BYTES = 512 * 1024
PARENT_TOOLS = ("Skill", "Agent")
HANDBACK = "SubagentHandback"
DEFAULT_AGENT = "general-purpose"
NAME_LIMIT = 80
ARGS_LIMIT = 200
RESULT_LIMIT = 300
LINE_LIMIT = 4096
TREE_WIDTH = 160
CONTEXT_WIDTH = 6
SESSION_WIDTH = 8
SHORT_SHA = 7
NEWLINE = " ⏎ "
ELLIPSIS = "…"
SECRETS = (
    (re.compile(r"\b(Bearer|Basic|token)\s+[\w.~+/=-]{8,}", re.IGNORECASE), r"\1 [redacted]"),
    (
        re.compile(
            r"""\b((?:api[_-]?key|access[_-]?token|token|secret|password|passwd|authorization)["']?\s*[:=]\s*["']?)[^\s"'&]+""",
            re.IGNORECASE,
        ),
        r"\1[redacted]",
    ),
    (re.compile(r"\b(?:gh[pousr]_|github_pat_|sk-|xox[abp]-)[\w-]{10,}"), "[redacted]"),
)
SECRET_KEY = re.compile(r"token|secret|password|api_?key|authorization|credential", re.IGNORECASE)


# ---------- values ----------


def _is_number(value: object) -> bool:
    """Whether `value` is a number: a bool is not one, whatever its type says."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _number(value: object) -> float | int:
    """`value` where it is a number, and zero otherwise: what an absent token count costs."""
    return cast(float | int, value) if _is_number(value) else 0


def _json(value: object) -> str:
    """`value` as compact JSON, the shape a record line and the page's data take.

    Every character outside ASCII is escaped, and a lone surrogate `json.loads` admits from a `\\ud800`
    escape is escaped too: the line is then pure ASCII, so the bytes `serialize` counts are the bytes the
    file holds, whatever the writing call's encoding or error policy does with the text."""
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def _iso(moment: datetime) -> str:
    """`moment` as ISO 8601 UTC with milliseconds, the shape a record's `at` takes."""
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def _local(ms: float) -> datetime:
    """Epoch milliseconds as an aware moment in the machine's local zone."""
    return datetime.fromtimestamp(ms / 1000).astimezone()


def _epoch_ms(value: object) -> int | None:
    """An ISO 8601 timestamp as epoch milliseconds, or nothing where it does not parse."""
    if not isinstance(value, str):
        return None
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return int(round(moment.timestamp() * 1000))


def _round_half_up(value: float) -> int:
    """`value` rounded to the nearer integer, halves going up: a duration never loses its half second."""
    return int(math.floor(value + 0.5))


# ---------- text helpers ----------


def mask(text: str) -> str:
    """`text` with what looks like a credential replaced."""
    for pattern, replacement in SECRETS:
        text = pattern.sub(replacement, text)
    return text


def clip(text: str, limit: int) -> str:
    """`text` cut to `limit` characters, its last one an ellipsis."""
    return text if len(text) <= limit else text[: max(limit - 1, 0)] + ELLIPSIS


def _lines(text: str) -> list[str]:
    """`text`'s lines, each trimmed, the blank ones dropped."""
    return [line.strip() for line in re.split(r"\r?\n", str(text)) if line.strip()]


def one_line(text: str) -> str:
    """`text`'s non-blank lines, trimmed and joined so a record stays on one line."""
    return NEWLINE.join(_lines(text))


def first_line(text: str) -> str:
    """`text`'s first non-blank line, trimmed."""
    return next(iter(_lines(text)), "")


def read_text(file: Path | str | None) -> str | None:
    """The file's text, or nothing where it cannot be read."""
    if not file:
        return None
    try:
        return Path(file).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def read_json(file: Path) -> object:
    """The file's JSON, or nothing where it cannot be read or parsed."""
    text = read_text(file)
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return None


def _without_jsonl(path: Path | str) -> Path:
    """`path` with a trailing `.jsonl` dropped: the directory a session's subagent transcripts sit in."""
    text = str(path)
    return Path(text[: -len(".jsonl")]) if text.endswith(".jsonl") else Path(text)


# ---------- git, without spawning git ----------


def git_root(start: Path | str) -> Path | None:
    """The repository `start` sits in: the nearest directory holding a `.git`."""
    directory = Path(start).resolve()
    for candidate in (directory, *directory.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def git_dir(root: Path) -> Path:
    """The repository's git directory: a worktree's `.git` is a file pointing at its own."""
    dot_git = Path(root) / ".git"
    if dot_git.is_dir():
        return dot_git
    pointer = re.search(r"^gitdir:\s*(.+)$", read_text(dot_git) or "", re.MULTILINE)
    return Path(root, pointer.group(1).strip()) if pointer else dot_git


def branch_of(start: Path | str) -> str | None:
    """The branch checked out at `start`, or its short commit where HEAD is detached."""
    try:
        root = git_root(start)
        if not root:
            return None
        head = (git_dir(root) / "HEAD").read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    ref = re.match(r"^ref:\s*refs/heads/(.+)$", head)
    return ref.group(1) if ref else head[:SHORT_SHA]


def hook_env() -> dict[str, str | None]:
    """The one variable the hook needs."""
    return {"CLAUDE_PROJECT_DIR": os.environ.get("CLAUDE_PROJECT_DIR")}


def project_dir(cwd: Path | str, env: dict[str, str | None] | None = None) -> Path:
    """The project root a trace belongs to: `CLAUDE_PROJECT_DIR` or `cwd`, taken up to the git root.

    Claude Code sets `CLAUDE_PROJECT_DIR` to the launch directory, which can sit below the git root.
    Traces go to the git root so `tree` finds them from anywhere in the repository."""
    env = hook_env() if env is None else env
    start = Path(env.get("CLAUDE_PROJECT_DIR") or cwd)
    return git_root(start) or start
