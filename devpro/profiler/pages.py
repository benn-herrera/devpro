"""The render: the text tree, the self-contained HTML page, and the index and pages the dashboard's
profiler view serves.

The page template `view.html` is this package's own data, read through `importlib.resources`, so the
render finds it wherever devpro is installed. The stylesheet the page and the index carry is the
board's own, `devpro.dicing.kanban.assets/board.css`: the presented interface's one presentation
layer, inlined here because the standalone page must load nothing, so its palette is the board's
from the identical file. `SHARED_CSS` is that file's text, and is what the dashboard inlines too.
"""

from __future__ import annotations

import html
import json
import math
import re
import string
from importlib.resources import files
from pathlib import Path
from urllib.parse import quote

from .capture import fill_context_tokens, spent_tokens, transcript_files
from .values import (
    CONTEXT_WIDTH,
    COPY_AGENT_TYPE,
    DEFAULT_AGENT,
    DUPLICATE_EVENT_MS,
    HANDBACK,
    MAIN,
    NAME_LIMIT,
    PARENT_TOOLS,
    SESSION_WIDTH,
    TRACE_DIR,
    TRACE_GLOB,
    TREE_WIDTH,
    _epoch_ms,
    _iso,
    _json,
    _round_half_up,
    _utc,
    clip,
    mask,
    read_text,
)


class UsageError(Exception):
    """A command line or an environment this tool cannot act on."""


ANSI_COLORS = (36, 33, 35, 32, 34, 31)
DATA_SLOT = "/*DATA*/null"
CSS_SLOT = "/*STYLE*/"
LEGEND_SLOT = "<!--LEGEND-->"

# The how-to-read legend, once for the whole presented interface. The standalone render injects it
# into the page it renders, and the dashboard's frame band reads this same constant for the served
# pages — so the legend has one home and two carriers, and the template carries no second copy.
LEGEND = (
    '<details class="intro"><summary>How to read this</summary><p>A sequence diagram of the session. '
    "Each vertical bar is one <b>context</b>: a conversation history the model reads. A Skill or Agent "
    "call that opens a new context is a message to a new bar, and the dashed message back carries its "
    "result. A new context starts with its prompt only and gets a color of its own; one that starts "
    "with a copy of its parent's history says so and keeps the parent's color. Rows are in time order, "
    "not to scale. To save width, a column holds one context at a time: when a context ends, a later "
    "one can reuse its column, so five runs of the same skill one after another sit in one column as "
    "five bars. Such a column's header is an outline with one chip per context, in time order and in "
    "the color of its bar; a chip without a name repeats the name before it. Next to the top of a "
    "context's bar are the tokens it spent over all its model calls, each of which sends the whole "
    "history again: new input, input read from the prompt cache (far cheaper), and output. Hover for "
    "the exact numbers. Click a message to see the call's arguments and result.</p>\n"
    '<div class="symbols" style="margin-top:8px">\n'
    '  <span><svg width="34" height="12"><line x1="0" x2="26" y1="6" y2="6" stroke="var(--c0)" '
    'stroke-width="2"/><path d="M24 1 L34 6 L24 11 z" fill="var(--c0)"/></svg>call that starts a '
    "context</span>\n"
    '  <span><svg width="34" height="12"><line x1="0" x2="32" y1="6" y2="6" stroke="var(--c0)" '
    'stroke-width="2"/><path d="M24 1 L34 6 L24 11" fill="none" stroke="var(--c0)" stroke-width="2"/>'
    "</svg>one that runs in the background</span>\n"
    '  <span><svg width="34" height="12"><line x1="0" x2="30" y1="6" y2="6" stroke="var(--muted)" '
    'stroke-width="1.5" stroke-dasharray="5 4"/><path d="M26 1 L34 6 L26 11" fill="none" '
    'stroke="var(--muted)" stroke-width="1.5"/></svg>return with the result</span>\n'
    '  <span><svg width="14" height="14"><path d="M7 1 l6 6 l-6 6 l-6 -6 z" fill="var(--c0)"/>'
    "</svg>skill loaded inline: its text joins this context; several in a row share one diamond, click "
    "it to list them</span>\n"
    '  <span><svg width="26" height="14"><rect x="1" y="1" width="24" height="12" fill="none" '
    'stroke="var(--fg)" stroke-width="1.5"/></svg>compacted: history replaced by a summary</span>\n'
    '  <span><svg width="10" height="16"><rect x="0" y="0" width="10" height="16" rx="2" '
    'fill="var(--c0)" fill-opacity=".85"/></svg>context at work</span>\n'
    "</div></details>"
)


def shared_css() -> str:
    """The presentation layer's text: the board's own stylesheet, read where devpro ships it."""
    return (files("devpro.dicing.kanban") / "assets" / "board.css").read_text(encoding="utf-8")


SHARED_CSS = shared_css()


def strict_fill(text: str, fills: dict[str, str]) -> str:
    """One strict fill every fill the profiler's assembly makes runs through. A `$name` slot goes
    through `string.Template`'s own substitute, which raises on a `$name` the text carries with no
    key; a literal mark — a map key that is no identifier, the mark as it stands in the text — is
    replaced once by its value. A key whose placeholder the text does not carry raises — a plain
    `str.replace` silently ignored an unused key and left the mark standing — and so does a mark
    still standing in the filled output. A mark the text carries that the call names no fill for is
    not a raise: a later stage fills it through this same fill.

    substitute runs first, over the text's own `$name`s alone: it inserts each value without
    rescanning, so a mark value carrying a `$` is never read as a slot, and a call with no slot skips
    the scan, leaving a template of `${...}` script untouched."""
    slots = {name: value for name, value in fills.items() if name.isidentifier()}
    marks = {mark: value for mark, value in fills.items() if not mark.isidentifier()}
    for name in slots:
        if f"${name}" not in text:
            raise KeyError(name)
    filled = string.Template(text).substitute(slots) if slots else text
    for mark, value in marks.items():
        if mark not in filled:
            raise KeyError(mark)
        filled = filled.replace(mark, value)
        if mark in filled:
            raise KeyError(mark)
    return filled


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


def format_span(ms: int | float) -> str:
    """A span as the index shows it, in whole seconds: `3h 42m`, minutes alone, seconds below a
    minute and `0s` for a zero-length span."""
    seconds = _round_half_up(ms / 1000)
    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {seconds}s" if seconds else f"{minutes}m"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m" if minutes else f"{hours}h"


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


def _context_spend(records: list[dict]) -> dict:
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


def render_tree(records: list[dict], *, verbose: bool = False, color: bool = False) -> str:
    """The trace as the text tree."""
    contexts, markers = contexts_of(records)
    options = {
        "verbose": verbose,
        "kinds": {context["id"]: context["kind"] for context in contexts},
        "colors": ansi_colors(contexts) if color else None,
        "spend": _context_spend(records),
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
    """One self-contained page: the package's template with the presentation layer, the how-to-read
    legend and the trace inlined.

    `<` is escaped so tool output in the JSON can't close the script tag."""
    calls = unique_calls(fill_context_tokens(session["records"]))
    contexts, markers = contexts_of(session["records"])
    spend = _context_spend(session["records"])
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
                # A child's page exists only where the record's harness names a session: claude's
                # `child_agent_id` is an agent id.
                "childPage": (
                    f"/page/{quote(str(record['child_agent_id']))}"
                    if record.get("child_agent_id") and record.get("harness") == "opencode"
                    else None
                ),
                "background": record.get("background"),
                "running": record.get("running"),
            }
            for record in calls
        ],
    }
    template = (files(__package__) / "view.html").read_text(encoding="utf-8")
    return strict_fill(
        template,
        {
            DATA_SLOT: _json(data).replace("<", "\\u003c"),
            CSS_SLOT: SHARED_CSS,
            LEGEND_SLOT: LEGEND,
        },
    )


def session_of(path: Path) -> dict:
    """One trace as `list_sessions` shapes it: its records and its first and last moments."""
    records = read_trace(path)
    starts: list[int] = []
    ends: list[int] = []
    for record in records:
        end = _epoch_ms(record.get("at"))
        if end is None:
            continue
        ends.append(end)
        starts.append(end - (record.get("duration_ms") or 0))
    return {
        "id": path.name[: -len(".jsonl")],
        "path": path,
        "records": records,
        "first": min(starts, default=math.inf),
        "last": max(ends, default=-math.inf),
    }


def list_sessions(directory: Path | str) -> list[dict]:
    """Every session trace under `directory`, with its records and its first and last moments.

    Every `.profiler-*` store under `.devpro-temp/` is read, so both harnesses' sessions reach one tree,
    and a session id is unique across them."""
    traces: list[Path] = []
    for store in sorted((Path(directory) / TRACE_DIR.parent).glob(TRACE_GLOB)):
        if store.is_dir():
            traces.extend(path for path in store.iterdir() if path.name.endswith(".jsonl"))
    return [session for session in (session_of(path) for path in traces) if session["records"]]


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
        raise UsageError(
            f"No traces in {Path(directory) / TRACE_DIR.parent / TRACE_GLOB}. "
            "Run a session with the hook installed first."
        )
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


# ---------- the served index and pages ----------


def read_sessions(directory: Path | str) -> tuple[list[dict], list[str]]:
    """`list_sessions`'s sessions, and the stores it cannot read, named as such rather than raised.

    One read over all of them cannot tell an unreadable store from an empty tree: `iterdir` raises
    out of it, so the index walks the stores one at a time, building each session the shape
    `list_sessions` builds, and states the store it cannot list in place of the session it lost."""
    stores = Path(directory) / TRACE_DIR.parent
    sessions: list[dict] = []
    unreadable: list[str] = []
    for store in sorted(stores.glob(TRACE_GLOB)):
        if not store.is_dir():
            continue
        try:
            traces = [path for path in store.iterdir() if path.name.endswith(".jsonl")]
        except OSError:
            unreadable.append(store.name)
            continue
        sessions.extend(session_of(path) for path in traces)
    return [session for session in sessions if session["records"]], unreadable


def session_harness(session: dict) -> str:
    """The harness's name, as the session's own records carry it, masked and clipped like any field."""
    harness = next((record.get("harness") for record in session["records"] if record.get("harness")), "")
    return clip(mask(str(harness)), NAME_LIMIT)


def _link(href: str, text: str) -> str:
    """`text`, as a link to `href`."""
    return f'<a href="{html.escape(href)}">{html.escape(text)}</a>'


def session_href(identifier: str) -> str:
    """A session's page, at the path the dashboard serves it."""
    return PAGE_PREFIX + quote(identifier)


def _session_link(identifier: str) -> str:
    """A session id, as a link to its page."""
    return _link(session_href(identifier), identifier)


def _moments(session: dict) -> str:
    """A session's first and last moments: the raw UTC as the cell's text where no script runs, and in
    its title where a hover wants the exact instant, and each instant as a `<time>` element the
    reader's local time is written from — the data, never the cell's own text, parsed."""
    text = html.escape(f"{stamp(session)} to {_iso(_utc(session['last']))}")
    first = html.escape(_utc(session["first"]).strftime("%Y-%m-%dT%H:%M:%SZ"))
    last = html.escape(_iso(_utc(session["last"])))
    return (
        f'<span class="moments" title="{text}">'
        f'<time datetime="{first}">{html.escape(stamp(session))}</time> to '
        f'<time datetime="{last}">{last}</time></span>'
    )


def dispatches(sessions: list[dict]) -> dict[str, tuple[str, str]]:
    """child session id -> the session that dispatched it and that call's name.

    Only an opencode record names a session: its `child_agent_id` is a session id. A claude record's
    is an agent id, and claude records its subagents' calls in the parent's own file, so no claude
    session is ever a child here. A child two sessions name keeps the first in list order, and a
    session naming itself is no child: it would be dropped from the index's top level and drawn as
    its own child."""
    found: dict[str, tuple[str, str]] = {}
    for session in sessions:
        for record in session["records"]:
            child = record.get("child_agent_id")
            if record.get("harness") == "opencode" and child and str(child) != session["id"]:
                found.setdefault(str(child), (session["id"], str(record.get("name") or "")))
    return found


def _count_of(count: int) -> str:
    """How many sessions a dispatcher's row says it dispatched, in the singular where it is one."""
    return "1 dispatched agent" if count == 1 else f"{count} dispatched agents"


def _records(session: dict) -> str:
    """A session's record count, as its row states it."""
    return html.escape(f"{len(session['records'])} records")


def session_row(session: dict, *, children: list[tuple[dict, str]] = ()) -> str:
    """One index row and, under a dispatcher's, the rows of the children drawn beneath it: the
    harness with its mark, the session's link and its dispatched count, the record count, the
    moments and the span. Each child's row carries the accent bar's empty cell, its link naming the
    call that dispatched it, its own count, moments and span."""
    rows = [
        "<tr>"
        f'<td><span class="harness {html.escape(_harness_class(session_harness(session)))}">'
        f"</span>{html.escape(session_harness(session))}</td>"
        f"<td>{_session_link(session['id'])}"
        + (f" <small>— {_count_of(len(children))}</small>" if children else "")
        + f"</td><td>{_records(session)}</td>"
        f"<td>{_moments(session)}</td><td>{html.escape(format_span(session['last'] - session['first']))}</td>"
        "</tr>"
    ]
    rows.extend(
        "<tr>"
        f'<td class="child"></td><td>{_session_link(child["id"])} '
        f"<small>↳ child — {html.escape(name)}</small></td>"
        f"<td>{_records(child)}</td>"
        f"<td>{_moments(child)}</td><td>{html.escape(format_span(child['last'] - child['first']))}</td>"
        "</tr>"
        for child, name in children
    )
    return "".join(rows)


def _harness_class(harness: str) -> str:
    """A harness's name as the page's class for its mark, where the page holds one for it."""
    return harness if harness in HARNESS_MARKS else ""


def unreadable_row(store: str) -> str:
    """The index row for a store the glob found but could not read."""
    return f'<tr><td colspan="5">{html.escape(store)} is unreadable</td></tr>'


def index_html(directory: Path | str) -> str:
    """The index of record files: one row per session, and one per store that cannot be read.

    A child session is drawn under the session that dispatched it, its dispatcher's row carrying the
    count of the rows drawn beneath it; a session no other dispatched keeps its own place in
    first-moment order. A session naming itself dispatches nothing (`dispatches` drops it), so it is
    no child and keeps that place. The index carries the presentation layer and names no view of its
    own: opened on its own it stands beside no board, so the nav, the frame band and the
    decoration's script are the marks the dashboard fills when it serves the index (`with_frame`),
    and absent where nothing fills them."""
    sessions, unreadable = read_sessions(directory)
    parent_of = dispatches(sessions)
    children: dict[str, list[tuple[dict, str]]] = {}
    for session in sessions:
        dispatched = parent_of.get(session["id"])
        if dispatched:
            children.setdefault(dispatched[0], []).append((session, dispatched[1]))
    rows = "".join(
        session_row(
            session,
            children=sorted(children.get(session["id"], ()), key=lambda pair: pair[0]["first"]),
        )
        for session in sorted(
            (session for session in sessions if session["id"] not in parent_of),
            key=lambda session: session["first"],
        )
    )
    return strict_fill(
        INDEX,
        {
            "unreadable": "".join(unreadable_row(store) for store in unreadable),
            "rows": rows or '<tr><td colspan="5">No sessions recorded yet.</td></tr>',
            **ZEBRA_MARKS,
        },
    )


def with_frame(page: str, *, nav: str, band: str, script: str) -> str:
    """The rendered page as the dashboard serves it: the presentation layer **linked** — the
    dashboard's Content-Security-Policy refuses an inline stylesheet, and the one source is the
    board panel's own file, which the board page links too. The render's carrier is the inline — a
    standalone page being self-contained — so the serve path strips the render's inline copy where
    the page carries it and names the file where the style block stood; a session's page arrives
    through the render first and carries the inline copy, an index does not. The template's own
    style block stands: its rules are the page's own, served and written alike. The nav in place of
    its nav mark, band in place of its band mark, and the decoration's script named where the
    template marks it — a linked script, for the same CSP.

    The band is where the view's legend is served from, and the render injected its own copy into the
    page it rendered: that copy is removed here, at the one site holding both in hand, so the served
    page carries the legend once. The removal comes before the band's splice because the band carries
    `LEGEND` itself (`dashboard.server.band_html`), which a removal run afterwards would take out of
    the band; the link's site stands beside both, its mark disjoint from the legend's, and the mark
    the script goes into stands below them all, so no stylesheet text can be read as that mark."""
    layer_link = '<link rel="stylesheet" href="/board/board.css">'
    if SHARED_CSS in page:
        page = page.replace(SHARED_CSS, "").replace("<style>\n", f"{layer_link}<style>", 1)
    else:
        page = page.replace("<style>\n" + CSS_SLOT, f"{layer_link}<style>", 1)
    page = page.replace(LEGEND, "")
    return strict_fill(page, {NAV_MARK: nav, BAND_MARK: band, DECO_MARK: script})


PAGE_PREFIX = "/page/"
# The marks the dashboard fills on the pages it serves: the nav, the frame band, and where the
# decoration's script goes — below the templates' splices, where no stylesheet text can be read as a
# mark. The index's template carries the last two as well, and the page's all three, so one renderer
# serves both.
NAV_MARK = "<!--NAV-->"
BAND_MARK = "<!--BAND-->"
DECO_MARK = "<!--DECO-->"
# The index's own brand marks: a harness's dot, in its brand colors, and the variable each wears.
# They are the page's, not the site's — the dots are the only brand-marked part of a row — so they
# live in the template's own style block beside its other rules. `ZEBRA_MARKS` is the template's
# substitution slots: the two harness class names and the two brand colors. The zebra's tones are no
# slot: their carrier is the template's own motif pair below it, whose light value is the shared
# layer's `--column` and whose dark value is the layer's `--zebra`, standing beside it as the
# layer's pair stands.
HARNESS_MARKS = {"opencode": "#4a9eea", "claude": "#d97757"}
ZEBRA_MARKS = {
    **{f"class_{harness}": _harness_class(harness) for harness in HARNESS_MARKS},
    **HARNESS_MARKS,
}
# The index's substitution slots, named by `index_html`: the unreadable stores' rows, the session
# rows, the harness class each row's mark carries and the two brand colors — in substitution's one
# pass, so text spliced into one slot is never read as another's.
# The presentation layer is no substitution slot: `/*STYLE*/` stands in the template, as it does on a
# page, and the `CSS_SLOT` splice fills it. The three marks are the last thing before the body's own
# content, their text no stylesheet's.
INDEX = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>devpro — profiler view: sessions</title>
<style>
/*STYLE*/
main { padding: 1rem; }
h1 { font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem; }
table { border-collapse: collapse; }
th, td { text-align: left; padding: 0.4rem 1rem 0.4rem 0; border-bottom: 1px solid var(--line); }
th { font-weight: 600; color: var(--muted); font-size: 0.85rem; }
a { color: var(--fg); }
a:hover, a:focus-visible { color: var(--accent); }
tr:nth-child(odd) td { background: var(--zebra); }
@media (prefers-color-scheme: dark) { tr:nth-child(odd) td { background: var(--zebra); } }
td small { color: var(--muted); }
tr td:first-child.child { border-left: 3px solid var(--accent); }
tr td:first-child.child + td { padding-left: 2.4rem; }
.harness { width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-right: 7px; }
.harness.$class_opencode { background: $opencode; }
.harness.$class_claude { background: $claude; }
</style>
<body>
<!--NAV-->
<!--BAND-->
<!--DECO-->
<main>
<h1>Sessions</h1>
<table>
<tr><th>harness</th><th>session</th><th>records</th><th>first to last</th><th>span</th></tr>
$unreadable$rows</table>
</main>
</body>
</html>
"""


def page_of(path: str, directory: Path | str) -> str | None:
    """The page at `/page/<session-id>`, or nothing where the path names no page or no session."""
    if not path.startswith(PAGE_PREFIX):
        return None
    sessions, _ = read_sessions(directory)
    session = next((session for session in sessions if session["id"] == path[len(PAGE_PREFIX) :]), None)
    return None if session is None else render_html(session)
