"""The capture: one hook payload in, one record appended to the harness's store.

The claude hook runs this through the installation's wrapper (`<wrapper> profiler capture claude`); the
opencode plugin writes the same records itself. Neither a failed capture nor a missing toolchain may
block the call that fired it, so `cli`'s capture path reads a bounded payload, silences the child's
stdout and exits 0 on every path.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from .values import (
    ARGS_LIMIT,
    CAPTURED_EVENTS,
    DEFAULT_AGENT,
    HANDBACK,
    LAUNCHED,
    LINE_LIMIT,
    MAIN,
    NAME_LIMIT,
    PARENT_TOOLS,
    RESULT_LIMIT,
    SCHEMA_VERSION,
    SECRET_KEY,
    TOOL_EVENTS,
    TRACE_DIR,
    TRANSCRIPT_TAIL_BYTES,
    _is_number,
    _iso,
    _json,
    _number,
    _without_jsonl,
    branch_of,
    clip,
    first_line,
    mask,
    one_line,
    project_dir,
    read_text,
)


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


def tool_use_facts(payload: dict) -> dict:
    """What the assistant message holding this call's tool_use states: its `context_tokens` — how full
    the calling context was when the model asked for the call — and its `model`, each present only
    where that line states it.

    The line is read from the tail of Claude Code's transcript, the subagent's where the call ran in
    one. The transcript format is Claude Code's own and undocumented, so any miss leaves the keys
    out."""
    try:
        if not payload.get("transcript_path") or not payload.get("tool_use_id"):
            return {}
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
        return {}
    for line in reversed(text.split("\n")):
        if payload["tool_use_id"] not in line:
            continue
        found = usage_by_tool_use(line).get(payload["tool_use_id"])
        if found is not None:
            return {"context_tokens": found, **_model_of(line)}
    return {}


def _model_of(line: str) -> dict:
    """The model an assistant transcript line names, masked and clipped as a record's name is, or no key
    where the line names none."""
    try:
        message = json.loads(line).get("message")
    except (ValueError, AttributeError):
        return {}
    model = message.get("model") if isinstance(message, dict) else None
    return {"model": clip(mask(model), NAME_LIMIT)} if isinstance(model, str) and model else {}


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
        **tool_use_facts(payload),
        "branch": branch_of(payload.get("cwd") or os.getcwd()),
        "args": _args_text(args) if args else None,
        "result": clip(mask(result), RESULT_LIMIT) if result else None,
    }
    return {key: value for key, value in record.items() if value is not None}


def serialize(record: dict) -> str:
    """The record's JSON line, `result` and then `args` giving way until the line fits.

    The line is what `_json` makes it — ASCII alone — so its length is the byte count `serialize` bounds
    and the bytes the file holds, one count."""
    line = _json(record)
    fitted = dict(record)
    for key in ("result", "args"):
        while len(line.encode("utf-8")) > LINE_LIMIT and fitted.get(key):
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
    """The trace file for one session under `directory`, its id made path-safe.

    The store the profiler's readers read: the claude capture's, the harness `capture` runs."""
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
