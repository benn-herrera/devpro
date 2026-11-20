#!/usr/bin/env python3
# !INSTALLED! from devpro/harnesses/resources/claude/libexec/hp.py — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
"""harness-profiler: records every tool call of a coding agent session and prints the calls as a tree.

One file, Python 3 standard library only. The command forms are the USAGE constant.
"""

from __future__ import annotations

import json
import math
import os
import platform
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

SCHEMA_VERSION = 2
TRACE_DIR = Path(".devpro-temp") / "harness-profile"
TOOL_EVENTS = ("PostToolUse", "PostToolUseFailure")
SESSION_EVENTS = ("PreCompact", "PostCompact", "SessionStart", "SubagentStop")
LAUNCHED = "async_launched"
CAPTURED_EVENTS = (*TOOL_EVENTS, *SESSION_EVENTS)
COPY_AGENT_TYPE = "fork"
MAIN = "main"
VIEW_TEMPLATE = "view.html"
SHOW_SKILL = Path("skills") / "show-profile"
DATA_SLOT = "/*DATA*/null"
DUPLICATE_EVENT_MS = 5000
TRANSCRIPT_TAIL_BYTES = 512 * 1024
ANSI_COLORS = (36, 33, 35, 32, 34, 31)
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
LAUNCHER = "hp.sh"
# Before 0.2.0 the launcher was `hp`, and a committed hook ran it by that name.
OLD_LAUNCHER = "hp"
HOOK_TIMEOUT_S = 5
HOOK_DIR = Path(".claude") / "harness-profiler"
HOOK_FILES = (LAUNCHER, "hp.py", VIEW_TEMPLATE)


def _hook_command(launcher: str) -> str:
    """The command a committed hook runs: this launcher, under the repository's `.claude/`."""
    return f'sh "$CLAUDE_PROJECT_DIR/.claude/harness-profiler/{launcher}" capture claude'


HOOK_COMMAND = _hook_command(LAUNCHER)
OLD_HOOK_COMMAND = _hook_command(OLD_LAUNCHER)


# ---------- values ----------


def _is_number(value: object) -> bool:
    """Whether `value` is a number: a bool is not one, whatever its type says."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _number(value: object) -> float | int:
    """`value` where it is a number, and zero otherwise: what an absent token count costs."""
    return value if _is_number(value) else 0


def _json(value: object) -> str:
    """`value` as compact JSON, the shape a record line and the page's data take."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _iso(moment: datetime) -> str:
    """`moment` as ISO 8601 UTC with milliseconds, the shape a record's `at` takes."""
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def _utc(ms: float) -> datetime:
    """Epoch milliseconds as an aware UTC moment."""
    return datetime.fromtimestamp(ms / 1000, timezone.utc)


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
    Traces go to the git root so `hp tree` finds them from anywhere in the repository."""
    env = hook_env() if env is None else env
    start = Path(env.get("CLAUDE_PROJECT_DIR") or cwd)
    return git_root(start) or start


# ---------- capture ----------


def tool_of(name: str) -> str:
    """The tool's kind: every MCP tool records as `mcp`, the server and tool in its name."""
    return "mcp" if name.startswith("mcp__") else name


def name_of(payload: dict) -> str | None:
    """What the call is called in a tree line: a skill's name, a subagent's kind, a command's head."""
    tool_input = payload.get("tool_input") or {}
    tool_name = payload.get("tool_name") or ""
    if tool_name == "Skill":
        return tool_input.get("skill")
    if tool_name == "Agent":
        return tool_input.get("subagent_type") or DEFAULT_AGENT
    if tool_name == "Bash":
        return re.sub(r'^cd\s+("[^"]*"|\'[^\']*\'|\S+)\s*&&\s*', "", first_line(tool_input.get("command") or ""))
    return tool_name.split("__")[-1] if tool_name.startswith("mcp__") else None


def args_of(payload: dict) -> object:
    """What the call was given: a skill's arguments, a subagent's brief, a command, or the input's JSON."""
    tool_input = payload.get("tool_input") or {}
    tool_name = payload.get("tool_name")
    if tool_name == "Skill":
        return tool_input.get("args")
    if tool_name == "Agent":
        return ": ".join(filter(None, (tool_input.get("description"), first_line(tool_input.get("prompt") or ""))))
    if tool_name == "Bash":
        return tool_input.get("command")
    if tool_name == HANDBACK:
        return None
    safe = {key: "[redacted]" if SECRET_KEY.search(key) else value for key, value in tool_input.items()}
    return _json(safe) if safe else None


def response_text(response: object) -> str:
    """A tool response's text, whatever shape the tool returned."""
    if response is None:
        return ""
    if isinstance(response, str):
        return response
    if not isinstance(response, dict):
        return ""
    if isinstance(response.get("result"), str):
        return response["result"]
    if isinstance(response.get("content"), list):
        return "\n".join(
            part.get("text") if isinstance(part, dict) and isinstance(part.get("text"), str) else ""
            for part in response["content"]
        )
    return "\n".join(value for value in (response.get("stdout"), response.get("stderr")) if isinstance(value, str))


# Claude Code may open a subagent's reply with the tools it used:
#   <tools-used-before-summary>Bash</tools-used-before-summary>\nS  => S
TOOLS_USED = re.compile(r"^\s*<tools-used-before-summary>.*?</tools-used-before-summary>", re.DOTALL)


def is_background(response: object) -> bool:
    """Whether the call was launched to run on: Claude Code's reply to a background Agent or Skill:
    {"status":"async_launched","agentId":"a1"} or {"status":"forked","background":true,...}."""
    if not isinstance(response, dict):
        return False
    return response.get("status") == LAUNCHED or response.get("background") is True


def result_of(payload: dict) -> str | None:
    """What the call returned, absent where it is still running or returned nothing.

    A background subagent reports to its caller with a SubagentHandback call, whose message is the
    result; the stop that follows has an empty last_assistant_message."""
    response = payload.get("tool_response")
    if payload.get("tool_name") == HANDBACK:
        return first_line((payload.get("tool_input") or {}).get("message") or "") or None
    if payload.get("tool_name") == "Skill" and not (isinstance(response, dict) and response.get("agentId")):
        return None
    if is_background(response):
        return None
    text = first_line(TOOLS_USED.sub("", response_text(response))) or first_line(payload.get("error") or "")
    return text or None


def usage_by_tool_use(line: str) -> dict[str, int | float]:
    """tool_use id -> context tokens, for one transcript line."""
    found: dict[str, int | float] = {}
    try:
        entry = json.loads(line)
    except ValueError:
        return found
    message = entry.get("message") if isinstance(entry, dict) else None
    if not isinstance(message, dict):
        return found
    usage = message.get("usage")
    if not usage or not isinstance(message.get("content"), list):
        return found
    total = (
        _number(usage.get("input_tokens"))
        + _number(usage.get("cache_read_input_tokens"))
        + _number(usage.get("cache_creation_input_tokens"))
    )
    for part in message["content"]:
        if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("id"):
            found[part["id"]] = total
    return found


def subagent_transcript(main: Path | str, agent_id: str) -> Path:
    """A subagent's transcript, beside its session's: `<session>/subagents/agent-<id>.jsonl`."""
    return _without_jsonl(main) / "subagents" / f"agent-{agent_id}.jsonl"


def context_tokens_of(payload: dict) -> int | float | None:
    """How full the calling context was when the model asked for this call: the usage on the assistant
    message that holds the tool_use, read from the tail of Claude Code's transcript.

    The transcript format is Claude Code's own and undocumented, so any miss leaves the field out."""
    try:
        if not payload.get("transcript_path") or not payload.get("tool_use_id"):
            return None
        file = (
            subagent_transcript(payload["transcript_path"], payload["agent_id"])
            if payload.get("agent_id")
            else Path(payload["transcript_path"])
        )
        size = file.stat().st_size
        length = min(size, TRANSCRIPT_TAIL_BYTES)
        with file.open("rb") as handle:
            handle.seek(size - length)
            text = handle.read(length).decode("utf-8", "replace")
    except (OSError, ValueError, TypeError):
        return None
    for line in reversed(text.split("\n")):
        if payload["tool_use_id"] not in line:
            continue
        found = usage_by_tool_use(line).get(payload["tool_use_id"])
        if found is not None:
            return found
    return None


def transcript_files(records: list[dict]) -> list[dict]:
    """Every transcript a trace names: main's, recorded on SessionStart, and each subagent's beside it."""
    files = []
    named: list[str] = []
    for record in records:
        name = record.get("transcript")
        if name and name not in named:
            named.append(name)
    for main in named:
        files.append({"ctx": MAIN, "file": Path(main)})
        directory = _without_jsonl(main) / "subagents"
        try:
            names = sorted(path.name for path in directory.iterdir())
        except OSError:
            names = []
        for name in names:
            agent = re.match(r"^agent-(.+)\.jsonl$", name)
            if agent:
                files.append({"ctx": agent.group(1), "file": directory / name})
    return files


def fill_context_tokens(records: list[dict]) -> list[dict]:
    """Calls recorded without `context_tokens` get them from the transcripts at render time, if those
    files still exist: an async hook can run before Claude Code flushes the transcript."""
    missing = [
        record
        for record in records
        if record.get("tool") and record.get("tool_use_id") and record.get("context_tokens") is None
    ]
    if not missing:
        return records
    found: dict[str, int | float] = {}
    for entry in transcript_files(records):
        text = read_text(entry["file"])
        if text is None:
            continue
        for line in text.split("\n"):
            if '"tool_use"' in line:
                found.update(usage_by_tool_use(line))
    return [
        (
            {**record, "context_tokens": found[record["tool_use_id"]]}
            if record.get("tool") and record.get("context_tokens") is None and record.get("tool_use_id") in found
            else record
        )
        for record in records
    ]


def spent_tokens(text: str) -> dict | None:
    """What a context spent, summed over its model calls.

    Each call sends the whole history again: what the prompt cache already held is `cached`, the rest
    (plain input and cache writes) is `new`, and the reply is `out`. They cost different amounts, so
    they stay apart. One response can span several transcript lines with the same message id."""
    seen: set[str] = set()
    spend = {"new": 0, "cached": 0, "out": 0, "calls": 0}
    for line in text.split("\n"):
        if '"usage"' not in line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict) or entry.get("type") != "assistant":
            continue
        message = entry.get("message")
        if not isinstance(message, dict) or not message.get("usage"):
            continue
        if message.get("id"):
            if message["id"] in seen:
                continue
            seen.add(message["id"])
        usage = message["usage"]
        spend["new"] += _number(usage.get("input_tokens")) + _number(usage.get("cache_creation_input_tokens"))
        spend["cached"] += _number(usage.get("cache_read_input_tokens"))
        spend["out"] += _number(usage.get("output_tokens"))
        spend["calls"] += 1
    return spend if spend["calls"] else None


def spent_by_child(payload: dict, child_id: str | None) -> dict | None:
    """What a subagent had spent when its parent's call came back, from the subagent's transcript."""
    if not payload.get("transcript_path") or not child_id:
        return None
    text = read_text(subagent_transcript(payload["transcript_path"], child_id))
    return None if text is None else spent_tokens(text)


def context_spend(records: list[dict]) -> dict:
    """context id -> {new, cached, out, calls}: from the transcripts while they exist, otherwise what
    capture recorded for each subagent."""
    spend: dict[str, dict] = {}
    for record in unique_calls(records):
        if record.get("child_agent_id") and record.get("child_spend"):
            spend[record["child_agent_id"]] = record["child_spend"]
    for stop in subagent_stops(records).values():
        if stop.get("spend"):
            spend[stop["agent_id"]] = stop["spend"]
    for entry in transcript_files(records):
        text = read_text(entry["file"])
        spent = spent_tokens(text) if text is not None else None
        if spent:
            spend[entry["ctx"]] = spent
    return spend


def _args_text(args: object) -> str:
    """`args` one-lined and clipped for a record: a string as it stands, anything else as JSON."""
    text = args if isinstance(args, str) else _json(args)
    return clip(mask(one_line(text)), ARGS_LIMIT)


def _child_agent_type(payload: dict, response: dict, child_id: str | None) -> str | None:
    """The kind of subagent a parent call started: the response's, or an `Agent` call's own input."""
    if not child_id:
        return None
    if response.get("agentType"):
        return response["agentType"]
    return (payload.get("tool_input") or {}).get("subagent_type") if payload.get("tool_name") == "Agent" else None


def build_record(payload: dict, harness: str) -> dict:
    """One tool call's record, in schema order; absent values are left out."""
    response = payload.get("tool_response") or {}
    if not isinstance(response, dict):
        response = {}
    is_parent = payload.get("tool_name") in PARENT_TOOLS
    name = name_of(payload)
    args = args_of(payload)
    result = result_of(payload)
    child_id = response.get("agentId") if is_parent else None
    # A background subagent is still at work: its end, result and spend come with its SubagentStop.
    background = is_background(response)
    spent = None if background else spent_by_child(payload, child_id)
    record = {
        "v": SCHEMA_VERSION,
        "harness": harness,
        "at": _iso(datetime.now(timezone.utc)),
        "session": payload.get("session_id"),
        "agent_id": payload.get("agent_id"),
        "agent_type": payload.get("agent_type"),
        "tool_use_id": payload.get("tool_use_id"),
        "tool": tool_of(payload.get("tool_name") or ""),
        "name": clip(mask(str(name)), NAME_LIMIT) if name else name,
        "duration_ms": payload.get("duration_ms"),
        "ok": payload.get("hook_event_name") != "PostToolUseFailure",
        "child_agent_id": child_id,
        "child_agent_type": _child_agent_type(payload, response, child_id),
        "background": background or None,
        "child_spend": spent,
        "tokens": response.get("totalTokens") if _is_number(response.get("totalTokens")) else None,
        "context_tokens": context_tokens_of(payload),
        "branch": branch_of(payload.get("cwd") or os.getcwd()),
        "args": _args_text(args) if args else None,
        "result": clip(mask(result), RESULT_LIMIT) if result else None,
    }
    return {key: value for key, value in record.items() if value is not None}


def serialize(record: dict) -> str:
    """The record's JSON line, `result` and then `args` giving way until the line fits."""
    line = _json(record)
    fitted = dict(record)
    for key in ("result", "args"):
        while len(line.encode("utf-8", "replace")) > LINE_LIMIT and fitted.get(key):
            shorter = len(fitted[key]) // 2
            if shorter < 1:
                del fitted[key]
            else:
                fitted[key] = clip(fitted[key], shorter)
            line = _json(fitted)
    return line


def build_event_record(payload: dict, harness: str) -> dict:
    """A compaction or session start's record: a marker, not a call, so it carries no `tool`."""
    record = {
        "v": SCHEMA_VERSION,
        "harness": harness,
        "at": _iso(datetime.now(timezone.utc)),
        "session": payload.get("session_id"),
        "agent_id": payload.get("agent_id"),
        "event": payload.get("hook_event_name"),
        "trigger": payload.get("trigger"),
        "source": payload.get("source"),
        "context_tokens": payload.get("context_tokens") if _is_number(payload.get("context_tokens")) else None,
        "transcript": payload.get("transcript_path") if payload.get("hook_event_name") == "SessionStart" else None,
    }
    if payload.get("hook_event_name") == "SubagentStop":
        text = read_text(payload.get("agent_transcript_path"))
        spent = spent_tokens(text) if text is not None else None
        result = first_line(TOOLS_USED.sub("", str(payload.get("last_assistant_message") or "")))
        record.update(
            {
                "agent_type": payload.get("agent_type") or None,
                "spend": spent,
                "result": clip(mask(result), RESULT_LIMIT) if result else None,
            }
        )
    return {key: value for key, value in record.items() if value is not None}


def session_file(directory: Path | str, session: object) -> Path:
    """The trace file for one session under `directory`, its id made path-safe."""
    safe = re.sub(r"[^\w.-]", "_", str(session))
    return Path(directory) / TRACE_DIR / f"{safe}.jsonl"


def capture(harness: str, text: str) -> Path | None:
    """Append one record for `text`, the hook payload, and return the file it landed in."""
    payload = json.loads(text)
    is_tool = payload.get("hook_event_name") in TOOL_EVENTS
    if payload.get("hook_event_name") not in CAPTURED_EVENTS or not payload.get("session_id"):
        return None
    if is_tool and not payload.get("tool_name"):
        return None
    directory = project_dir(payload.get("cwd") or os.getcwd())
    file = session_file(directory, payload["session_id"])
    file.parent.mkdir(parents=True, exist_ok=True)
    record = build_record(payload, harness) if is_tool else build_event_record(payload, harness)
    # One small append per record keeps concurrent hooks from interleaving.
    with file.open("a", encoding="utf-8", errors="replace") as handle:
        handle.write(serialize(record) + "\n")
    return file


# ---------- tree ----------


def read_trace(file: Path) -> list[dict]:
    """The records a trace holds: a torn line is skipped."""
    records = []
    for line in (read_text(file) or "").split("\n"):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    return records


def start_of(record: dict) -> int | float:
    """When the call started: its recorded end less its duration."""
    return (_epoch_ms(record.get("at")) or 0) - (record.get("duration_ms") or 0)


def format_duration(ms: int | float) -> str:
    """A duration as a tree column shows it."""
    if ms < 1000:
        return f"{ms} ms"
    tenths = _round_half_up(ms / 100) / 10
    return f"{tenths:.1f} s" if tenths < 10 else f"{_round_half_up(ms / 1000)} s"


def format_count(n: int | float) -> str:
    """A token count as a tree column shows it."""
    if n >= 1e6:
        return f"{n / 1e6:.1f}M"
    if n >= 1e3:
        return f"{n / 1e3:.1f}k"
    return f"{n}"


def clock(ms: int | float) -> str:
    """Epoch milliseconds as the tree's time column: UTC, to the second."""
    return _utc(ms).strftime("%H:%M:%S")


def subagent_stops(records: list[dict]) -> dict[str, dict]:
    """agent id -> its last SubagentStop.

    A background subagent stops each time it has nothing to do and is woken when a child of its own
    reports, so the last stop is the one that ends it."""
    stops: dict[str, dict] = {}
    for record in records:
        if record.get("event") == "SubagentStop" and record.get("agent_id"):
            stops[record["agent_id"]] = {**stops.get(record["agent_id"], {}), **record}
    return stops


# Traces captured before a background skill was told apart from a finished one hold Claude Code's
# launch notice as the call's result.
LAUNCH_NOTICE = re.compile(r"^Running in the background as @")


def with_stop(record: dict, stop: dict | None, handback: str | None) -> dict:
    """A background subagent's call, ended by its stop where one is recorded.

    Its call returns at once and it ends at its SubagentStop; its result is what it handed back. Until
    its first stop it is `running`: the duration recorded so far is the launch, not the work."""
    launched = {key: value for key, value in record.items() if key != "result"}
    call = {**launched, "background": True} if LAUNCH_NOTICE.match(record.get("result") or "") else record
    if not stop:
        return {**call, "running": True} if call.get("background") else call
    merged = {**call, "child_agent_type": call.get("child_agent_type") or stop.get("agent_type")}
    if not call.get("background"):
        return merged
    return {
        **merged,
        "at": stop.get("at"),
        "duration_ms": max(0, (_epoch_ms(stop.get("at")) or 0) - start_of(call)),
        "result": handback or call.get("result") or stop.get("result"),
    }


def unique_calls(records: list[dict]) -> list[dict]:
    """The calls a trace holds once each: a plugin and a committed hook on one machine record everything
    twice."""
    stops = subagent_stops(records)
    handbacks = {
        record["agent_id"]: record["result"]
        for record in records
        if record.get("tool") == HANDBACK and record.get("agent_id") and record.get("result")
    }
    seen: set[str] = set()
    calls = []
    for record in records:
        if not record.get("tool"):
            continue
        if record.get("tool_use_id"):
            if record["tool_use_id"] in seen:
                continue
            seen.add(record["tool_use_id"])
        calls.append(
            with_stop(record, stops.get(record.get("child_agent_id")), handbacks.get(record.get("child_agent_id")))
        )
    return calls


def unique_events(records: list[dict]) -> list[dict]:
    """The markers once each: the same event captured twice within a few seconds is one event."""
    kept: list[dict] = []
    for record in records:
        if record.get("tool") or not record.get("event"):
            continue
        at = _epoch_ms(record.get("at")) or 0
        twin = next(
            (
                seen
                for seen in kept
                if seen.get("event") == record.get("event")
                and seen.get("agent_id") == record.get("agent_id")
                and seen.get("trigger") == record.get("trigger")
                and seen.get("source") == record.get("source")
                and abs((_epoch_ms(seen.get("at")) or 0) - at) < DUPLICATE_EVENT_MS
            ),
            None,
        )
        if twin is None:
            kept.append(record)
    return kept


TOOL_WORDS = {"Skill": "skill", "Agent": "agent"}


def call_label(tool: str | None, name: str | None) -> str:
    """The name leads and the kind follows: `review (skill)`, `counter (agent)`, `wc -l a (Bash)`."""
    word = TOOL_WORDS.get(tool, tool)
    return f"{name} ({word})" if name else word


def context_of(record: dict) -> str:
    """The context a call belongs to: the subagent's id, or main's."""
    return record.get("agent_id") or MAIN


def short_id(identifier: str) -> str:
    """An id as a tree line shows it: main's as it stands, a subagent's first few characters."""
    return MAIN if identifier == MAIN else identifier[:CONTEXT_WIDTH]


def contexts_of(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """The trace's contexts and markers.

    A context is one conversation history: main, or a subagent started by a forked Skill or an Agent
    call. Inline skills and compactions are markers in one. A `fork` subagent starts with a copy of its
    parent's history; every other subagent starts with its prompt only."""
    calls = unique_calls(records)
    contexts: list[dict] = [{"id": MAIN, "parent": None, "kind": "root", "label": MAIN}]
    known = {MAIN}
    for record in calls:
        child = record.get("child_agent_id")
        if not child or child in known:
            continue
        known.add(child)
        contexts.append(
            {
                "id": child,
                "parent": context_of(record),
                "kind": "copy" if record.get("child_agent_type") == COPY_AGENT_TYPE else "fresh",
                "label": call_label(record.get("tool"), record.get("name")),
                "name": record.get("name"),
                "tool": record.get("tool"),
                "start": start_of(record),
                "end": _epoch_ms(record.get("at")),
            }
        )
    for record in calls:
        identifier = context_of(record)
        if identifier in known:
            continue
        known.add(identifier)
        agent_type = record.get("agent_type") or DEFAULT_AGENT
        contexts.append(
            {
                "id": identifier,
                "parent": None,
                "kind": "fresh",
                "label": call_label("Agent", agent_type),
                "name": agent_type,
                "tool": "Agent",
            }
        )

    # Calls are recorded when they end, so order by start: a caller's lifeline stays left of the
    # contexts it starts. Unrecorded parents go last.
    contexts[1:] = sorted(contexts[1:], key=lambda context: context.get("start", math.inf))

    # Color follows history: a copy keeps its parent's hue, a fresh context gets the next one.
    hues: dict[str, int] = {}
    next_hue = 0
    for context in contexts:
        if context["kind"] == "copy" and context.get("parent") in hues:
            context["hue"] = hues[context["parent"]]
        else:
            context["hue"] = next_hue
            next_hue += 1
        hues[context["id"]] = context["hue"]

    markers = [
        {"kind": "inline", "ctx": context_of(record), "at": start_of(record), "name": record.get("name")}
        for record in calls
        if record.get("tool") == "Skill" and not record.get("child_agent_id")
    ]
    open_compact: dict | None = None
    for event in unique_events(records):
        at = _epoch_ms(event.get("at")) or 0
        if event.get("event") == "PreCompact":
            open_compact = {"kind": "compact", "ctx": context_of(event), "at": at, "trigger": event.get("trigger")}
            markers.append(open_compact)
        elif event.get("event") == "PostCompact":
            if not open_compact:
                markers.append({"kind": "compact", "ctx": context_of(event), "at": at, "trigger": event.get("trigger")})
            open_compact = None
    markers.sort(key=lambda marker: marker["at"])
    return contexts, markers


def build_forest(records: list[dict], markers: list[dict] | None = None) -> list[dict]:
    """The tree's roots: each call under the call that started its context, in start order."""
    nodes = [
        {"record": record, "index": index, "start": start_of(record), "children": []}
        for index, record in enumerate(unique_calls(records))
    ]
    by_child = {node["record"]["child_agent_id"]: node for node in nodes if node["record"].get("child_agent_id")}
    placeholders: dict[str, dict] = {}
    roots: list[dict] = []

    def container(agent: str | None, start: int | float, index: int | float, agent_type: str | None = None) -> list:
        """The list a node goes in: its parent's children, or the roots where nothing started it."""
        if not agent:
            return roots
        parent = by_child.get(agent)
        if parent is None:
            parent = placeholders.get(agent)
            if parent is None:
                parent = {
                    "placeholder": True,
                    "agent": agent,
                    "agent_type": agent_type,
                    "start": start,
                    "index": index,
                    "children": [],
                }
                placeholders[agent] = parent
                roots.append(parent)
            parent["start"] = min(parent["start"], start)
        return parent["children"]

    for node in nodes:
        container(
            node["record"].get("agent_id"), node["start"], node["index"], node["record"].get("agent_type")
        ).append(node)
    for marker in markers or ():
        container(None if marker["ctx"] == MAIN else marker["ctx"], marker["at"], math.inf).append(
            {"marker": marker, "start": marker["at"], "index": math.inf, "children": []}
        )
    sort_tree(roots)
    return roots


def sort_tree(nodes: list[dict]) -> None:
    """Order the tree by start, a call that started at the same moment keeping its record order."""
    nodes.sort(key=lambda node: (node["start"], node["index"]))
    for node in nodes:
        sort_tree(node["children"])


def visible(node: dict, *, verbose: bool) -> bool:
    """Whether a node is drawn: everything under `--verbose`, and otherwise the calls that lead to
    other calls, the markers and the placeholders."""
    if verbose or node.get("placeholder") or node.get("marker"):
        return True
    return (node.get("record") or {}).get("tool") in PARENT_TOOLS


def context_words(record: dict, kinds: dict[str, str]) -> str:
    """How the call relates to contexts: `inline` for a skill that ran in its caller's context, `new
    context <id>` for one that started a subagent, plus `copy of <parent>` where that subagent began
    with the caller's history."""
    child = record.get("child_agent_id")
    if child:
        words = [f"new context {short_id(child)}"]
        if kinds.get(child) == "copy":
            words.append(f"copy of {short_id(context_of(record))}")
        if record.get("background"):
            words.append("background")
        return ", ".join(words)
    return "inline" if record.get("tool") == "Skill" else ""


def detail(record: dict, budget: int | None) -> str:
    """The `(args) -> result` tail of a tree line, clipped to `budget` characters."""
    args = record.get("args") if record.get("args") and record.get("args") != record.get("name") else None
    result = record.get("result") if record.get("tool") in PARENT_TOOLS or record.get("ok") is False else None
    if budget is not None:
        if args:
            args = clip(args, budget // 2 if result else budget)
        if result:
            result = clip(result, budget - (len(args) + 3 if args else 0) - 3)
    return " ".join(part for part in (f"({args})" if args else None, f"-> {result}" if result else None) if part)


def paint(text: str, ctx: str | None, colors: dict[str, int] | None) -> str:
    """`text` in its context's color, where the terminal takes one."""
    code = colors.get(ctx) if colors else None
    return f"\x1b[{code}m{text}\x1b[0m" if code else text


BAR_CELLS = 8
# In the duration column of a background call that has not stopped yet.
RUNNING = "running"
BAR_EIGHTHS = ("", "▏", "▎", "▍", "▌", "▋", "▊", "▉")
BAR_STEPS = len(BAR_EIGHTHS)
COLUMNS = (
    ("time", 8, "left"),
    ("duration", 8, "right"),
    ("", BAR_CELLS, "left"),
    ("new", 6, "right"),
    ("cached", 7, "right"),
    ("out", 6, "right"),
)
COLUMN_GAP = "  "


def cell(text: str, column: tuple[str, int, str]) -> str:
    """`text` padded to `column`'s width on the side its alignment names."""
    _, width, align = column
    return text.rjust(width) if align == "right" else text.ljust(width)


def columns(values: list) -> str:
    """The fixed columns a tree line opens with, a missing value left blank."""
    cells = [cell(values[index] if index < len(values) else "", column) for index, column in enumerate(COLUMNS)]
    return " ".join(cells) + COLUMN_GAP


def duration_bar(ms: int | float, longest: int | float) -> str:
    """A square-root scale: the longest call fills the bar, a call a quarter as long fills half and one a
    hundredth as long a tenth, so short calls stay visible without hiding the long ones."""
    if not longest or not ms:
        return ""
    steps = _round_half_up(math.sqrt(min(ms, longest) / longest) * BAR_CELLS * BAR_STEPS)
    return "█" * (steps // BAR_STEPS) + BAR_EIGHTHS[steps % BAR_STEPS]


def tree_header() -> str:
    """The tree's column headings."""
    return columns([name for name, _, _ in COLUMNS]) + "call"


def format_line(
    node: dict,
    depth: int,
    *,
    verbose: bool,
    kinds: dict[str, str],
    colors: dict[str, int] | None,
    spend: dict[str, dict],
    longest: int | float,
) -> str:
    """One tree line: its columns, its call with the words that place it, and its tail."""
    indent = "  " * depth
    if node.get("placeholder"):
        label = call_label("Agent", node.get("agent_type") or DEFAULT_AGENT)
        return columns([]) + paint(
            f"{indent}{label} [{short_id(node['agent'])}] parent not recorded", node.get("agent"), colors
        )
    if node.get("marker"):
        marker = node["marker"]
        return columns([clock(marker["at"])]) + paint(
            f"{indent}-- {short_id(marker['ctx'])} compacted ({marker.get('trigger') or 'unknown trigger'})",
            marker["ctx"],
            colors,
        )
    record = node["record"]
    ms = 0 if record.get("running") else record.get("duration_ms") or 0
    spent = spend.get(record["child_agent_id"]) if record.get("child_agent_id") else None
    spent_cells = [format_count(spent[key]) for key in ("new", "cached", "out")] if spent else []
    prefix = columns(
        [
            clock(node["start"]),
            RUNNING if record.get("running") else format_duration(ms),
            duration_bar(ms, longest),
            *spent_cells,
        ]
    )
    words = " ".join(
        part for part in (context_words(record, kinds), "failed" if record.get("ok") is False else "") if part
    )
    head = f"{indent}{call_label(record.get('tool'), record.get('name'))}"
    plain_head = f"{head} {words}" if words else head
    budget = None if verbose else TREE_WIDTH - len(prefix) - len(plain_head) - 2
    shown_words = words
    if words and record.get("child_agent_id"):
        shown_words = re.sub(
            r"^new context \S+", lambda found: paint(found.group(0), record["child_agent_id"], colors), words
        )
    tail = detail(record, budget)
    return prefix + " ".join(part for part in (paint(head, context_of(record), colors), shown_words, tail) if part)


def ansi_colors(contexts: list[dict]) -> dict[str, int]:
    """Each context's terminal color. Main keeps the terminal's own, and so does a copy of main."""
    return {
        context["id"]: ANSI_COLORS[(context["hue"] - 1) % len(ANSI_COLORS)]
        for context in contexts
        if context["hue"] > 0
    }


def render_tree(records: list[dict], *, verbose: bool = False, color: bool = False) -> str:
    """The trace as the text tree."""
    contexts, markers = contexts_of(records)
    options = {
        "verbose": verbose,
        "kinds": {context["id"]: context["kind"] for context in contexts},
        "colors": ansi_colors(contexts) if color else None,
        "spend": context_spend(records),
        "longest": 0,
    }
    shown: list[tuple[dict, int]] = []

    def walk(nodes: list[dict], depth: int) -> None:
        for node in nodes:
            if not visible(node, verbose=verbose):
                continue
            shown.append((node, depth))
            walk(node["children"], depth + 1)

    walk(build_forest(records, [marker for marker in markers if marker["kind"] == "compact"]), 0)
    options["longest"] = max([0] + [(node.get("record") or {}).get("duration_ms") or 0 for node, _ in shown])
    return "\n".join([tree_header()] + [format_line(node, depth, **options) for node, depth in shown])


def render_html(session: dict) -> str:
    """One self-contained page: the template from beside this file with the trace inlined.

    `<` is escaped so tool output in the JSON can't close the script tag."""
    calls = unique_calls(fill_context_tokens(session["records"]))
    contexts, markers = contexts_of(session["records"])
    spend = context_spend(session["records"])
    data = {
        "session": session["id"],
        "branch": next((record.get("branch") for record in calls if record.get("branch")), None),
        "contexts": [{**context, "spent": spend.get(context["id"])} for context in contexts],
        "markers": markers,
        "calls": [
            {
                "ctx": context_of(record),
                "tool": record.get("tool"),
                "name": record.get("name"),
                "start": start_of(record),
                "dur": record.get("duration_ms") or 0,
                "ok": record.get("ok") is not False,
                "ctxTokens": record.get("context_tokens"),
                "args": record.get("args"),
                "result": record.get("result"),
                "child": record.get("child_agent_id"),
                "background": record.get("background"),
                "running": record.get("running"),
            }
            for record in calls
        ],
    }
    template = (SCRIPT_DIR / VIEW_TEMPLATE).read_text(encoding="utf-8")
    return template.replace(DATA_SLOT, _json(data).replace("<", "\\u003c"))


def list_sessions(directory: Path | str) -> list[dict]:
    """Every session trace under `directory`, with its records and its first and last moments."""
    traces = Path(directory) / TRACE_DIR
    if not traces.is_dir():
        return []
    sessions = []
    for path in traces.iterdir():
        if not path.name.endswith(".jsonl"):
            continue
        records = read_trace(path)
        starts: list[int] = []
        ends: list[int] = []
        for record in records:
            end = _epoch_ms(record.get("at"))
            if end is None:
                continue
            ends.append(end)
            starts.append(end - (record.get("duration_ms") or 0))
        sessions.append(
            {
                "id": path.name[: -len(".jsonl")],
                "records": records,
                "first": min(starts, default=math.inf),
                "last": max(ends, default=-math.inf),
            }
        )
    return [session for session in sessions if session["records"]]


FORMATS = ("text", "html")
VALUE_FLAGS = ("--branch", "--format")


def parse_tree_args(argv: list[str]) -> dict:
    """`tree`'s options: its session prefix and its flags."""
    options: dict = {"verbose": False, "format": "text"}
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument in ("--verbose", "-v"):
            options["verbose"] = True
        elif argument in VALUE_FLAGS:
            index += 1
            options[argument[2:]] = argv[index] if index < len(argv) else None
        elif not argument.startswith("-"):
            options["prefix"] = argument
        index += 1
    if options["format"] not in FORMATS:
        raise UsageError(f"Unknown format {options['format']}; use {' or '.join(FORMATS)}.")
    return options


def stamp(session: dict) -> str:
    """A session's first call, UTC, to the second."""
    return _utc(session["first"]).strftime("%Y-%m-%d %H:%M:%S") + " UTC"


def tree(argv: list[str], directory: Path | str, *, color: bool = False) -> str:
    """The session the arguments choose, as the text tree or as the html page."""
    options = parse_tree_args(argv)
    sessions = list_sessions(directory)
    if not sessions:
        raise UsageError(f"No traces in {Path(directory) / TRACE_DIR}. Run a session with the hook installed first.")
    branch = options.get("branch")
    prefix = options.get("prefix")
    if branch:
        chosen = sorted(
            [session for session in sessions if any(record.get("branch") == branch for record in session["records"])],
            key=lambda session: session["first"],
        )
        if not chosen:
            raise UsageError(f"No session recorded on branch {branch}.")
    elif prefix:
        chosen = [session for session in sessions if str(session["id"]).startswith(prefix)]
        if len(chosen) != 1:
            raise UsageError(
                f"Session prefix {prefix} is ambiguous." if chosen else f"No session starts with {prefix}."
            )
    else:
        chosen = [max(sessions, key=lambda session: session["last"])]
    if options["format"] == "html":
        if len(chosen) > 1:
            listing = "\n".join(f"  {session['id'][:SESSION_WIDTH]}  {stamp(session)}" for session in chosen)
            raise UsageError(f"The html page shows one session. Pick one by id prefix:\n{listing}")
        return render_html(chosen[0])
    if not branch:
        return render_tree(chosen[0]["records"], verbose=options["verbose"], color=color)
    blocks = []
    for session in chosen:
        rendered = render_tree(session["records"], verbose=options["verbose"], color=color)
        blocks.append(f"# session {session['id']} ({stamp(session)})\n{rendered}")
    return "\n\n".join(blocks)


# ---------- init ----------


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


def init(argv: list[str], cwd: Path | str) -> str:
    """Commit the hook into the repository at `cwd`: the launcher, the tool, the page and the skill, and
    the six entries in its `.claude/settings.json`, for a session that loads no plugin's hooks."""
    if not argv or argv[0] != "claude":
        raise UsageError("Usage: harness-profiler init claude")
    repo = git_root(cwd)
    if not repo:
        raise UsageError("Run harness-profiler init inside a git repository.")
    target = repo / HOOK_DIR
    target.mkdir(parents=True, exist_ok=True)
    for name in HOOK_FILES:
        shutil.copyfile(SCRIPT_DIR / name, target / name)
    (target / LAUNCHER).chmod(0o755)
    (target / OLD_LAUNCHER).unlink(missing_ok=True)
    skill = repo / ".claude" / SHOW_SKILL
    skill.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SCRIPT_DIR.parent / SHOW_SKILL / "SKILL.md", skill / "SKILL.md")

    settings_file = repo / ".claude" / "settings.json"
    settings = json.loads(settings_file.read_text(encoding="utf-8")) if settings_file.exists() else {}
    if not isinstance(settings, dict):
        settings = {}
    settings_file.write_text(json.dumps(merge_hooks(settings), indent=2) + "\n", encoding="utf-8")
    return "\n".join(
        [
            f"Copied the hook to {target.relative_to(repo)}/, registered it in .claude/settings.json,"
            " and added the show-profile skill.",
            "Commit them; Claude Code on the web picks the hook up in the next session:",
            "  git add .claude/harness-profiler .claude/skills/show-profile .claude/settings.json",
        ]
    )


# ---------- doctor ----------


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
    changed = [name for name in HOOK_FILES if read_text(repo / HOOK_DIR / name) != read_text(SCRIPT_DIR / name)]
    gaps = [
        f"misses {', '.join(missing)}" if missing else "",
        "is not async" if blocking else "",
        f"has another version of {', '.join(changed)}" if changed else "",
    ]
    return " and ".join(gap for gap in gaps if gap) or None


def doctor(cwd: Path | str) -> str:
    """Whether capture works here, and why not."""
    directory = project_dir(cwd)
    sessions = list_sessions(directory)
    newest = max((session["last"] for session in sessions), default=None)
    repo = git_root(cwd) or Path(cwd)
    sources = hook_sources(repo, Path.home())
    stale = stale_hook(repo)
    installed = (
        ", ".join(sources) if sources else "not installed (install the plugin, or run harness-profiler init claude)"
    )
    lines = [
        f"python:  {sys.executable} ({platform.python_version()})",
        f"traces:  {Path(directory) / TRACE_DIR}",
        f"hook:    {installed}",
        f"update:  the committed hook {stale}; run harness-profiler init claude again and commit" if stale else None,
        f"newest:  {_iso(_utc(newest)) if newest is not None else 'no calls recorded yet'}",
    ]
    return "\n".join(line for line in lines if line)


# ---------- entry point ----------


class UsageError(Exception):
    """A command line or an environment this tool cannot act on."""


USAGE = """Usage:
  harness-profiler tree [session-id-prefix] [--branch <name>] [--verbose] [--format text|html]
  harness-profiler init claude
  harness-profiler doctor
  harness-profiler capture <harness>  (run by the hook, not by hand)"""


def read_stdin() -> str:
    """The hook payload on stdin, and nothing where it cannot be read."""
    try:
        return sys.stdin.buffer.read().decode("utf-8", "replace")
    except OSError:
        return ""


def main(argv: list[str]) -> int:
    """The subcommand's exit status."""
    sys.stdout.reconfigure(encoding="utf-8")
    command = argv[0] if argv else None
    rest = argv[1:]
    if command == "capture":
        # A profiler must never break or slow down the session it watches, so no error leaves capture.
        try:
            capture(rest[0] if rest else "unknown", read_stdin())
        except Exception:
            pass
        return 0
    try:
        if command == "tree":
            color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
            print(tree(rest, project_dir(os.getcwd()), color=color))
            return 0
        if command == "init":
            print(init(rest, Path.cwd()))
            return 0
        if command == "doctor":
            print(doctor(Path.cwd()))
            return 0
    except UsageError as error:
        print(error, file=sys.stderr)
        return 1
    print(USAGE)
    return 1 if command else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
