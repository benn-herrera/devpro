"""The render: the text tree, the self-contained HTML page, and the index and pages the dashboard's
profiler view serves.

The page template `view.html` is this package's own data, read through `importlib.resources`, so the
render finds it wherever devpro is installed. The stylesheet the page and the index carry is the
board's own, `devpro.kanban.assets/board.css`: the presented interface's one presentation
layer, carried by the two flows each its own way. The standalone render inlines the layer —
`SHARED_CSS`, that file's text — because the standalone page must load nothing, so its palette is
the board's from the identical file; the dashboard serves the pages with the layer linked to the
same file the board panel serves.
"""

from __future__ import annotations

import html
import json
import math
import re
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
DATA_MARK = "/*DATA*/null"
# The shared layer's carriage, the one thing the standalone page and the served page hold differently:
# the render fills it with the layer's text, the serve path with the link to the board panel's own file.
LAYER_MARK = "<!--LAYER-->"
LAYER_LINK = '<link rel="stylesheet" href="/board/board.css">'

# The how-to-read legend, once for the whole presented interface. Its one home, filled by the strict
# fill into the frame band both profiler templates carry — the standalone render's and the served
# page's alike — so the template carries no second copy.
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
# The frame band's way-back control label, and the dispatcher line's lead — the band's own text.
RETURN_LABEL = "Return to list"


def shared_css() -> str:
    """The presentation layer's text: the board's own stylesheet, read where devpro ships it."""
    return (files("devpro.kanban") / "assets" / "board.css").read_text(encoding="utf-8")


SHARED_CSS = shared_css()
# The standalone page's own layer element: the shared layer's text in a style block of its own,
# placed where the mark stands — before the template's own style block, so the layer's rules cascade
# first and the template's own rules override them.
LAYER_INLINE = "<style>\n" + SHARED_CSS + "\n</style>"


def strict_fill(text: str, fills: dict[str, str]) -> str:
    """One strict fill every fill the profiler's assembly makes runs through. Each key is a literal
    mark — text inert in its host language, `<!--NAME-->` in HTML or `/*NAME*/` in CSS or JS, as it
    stands in the text — and every place it stands is replaced by its value, in one pass that never
    reads a value for a mark. A mark the text does not carry raises, and so does a value carrying any
    mark of the same fill, its own included, which would otherwise stand in the output or be read as
    the mark it carries."""
    for mark, value in fills.items():
        if mark not in text:
            raise KeyError(mark)
        if carried := next((other for other in fills if other in value), None):
            raise KeyError(carried)
    if not fills:
        return text
    # Longest first, so a mark that contains another is matched whole.
    pattern = "|".join(re.escape(mark) for mark in sorted(fills, key=len, reverse=True))
    return re.sub(pattern, lambda match: fills[match.group()], text)


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


def session_data(session: dict) -> dict:
    """The page data `view.html` inlines at its data mark: the session's calls as the file flow
    draws them, one source for the standalone render and the served page alike."""
    calls = unique_calls(fill_context_tokens(session["records"]))
    contexts, markers = contexts_of(session["records"])
    spend = _context_spend(session["records"])
    return {
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


def _inlined_session_data(session: dict) -> str:
    """`session_data` as the JSON a page's script inlines: `<` escaped so tool output cannot close the
    script tag, and `/` escaped so it cannot spell a fill's mark — `/*DATA*/null` among them, which
    the strict fill refuses in a value."""
    return _json(session_data(session)).replace("<", "\\u003c").replace("/", "\\/")


def render_html(session: dict) -> str:
    """One self-contained page: the package's template with the presentation layer, the how-to-read
    legend and the trace inlined, the frame band's facts this page carries none of left empty."""
    template = (files(__package__) / "view.html").read_text(encoding="utf-8")
    return strict_fill(
        template,
        {
            DATA_MARK: _inlined_session_data(session),
            LAYER_MARK: LAYER_INLINE,
            **band_fills(dispatcher=None, return_to=None),
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


def traces_feed(directory: Path | str) -> list[dict]:
    """The feed `/api/traces` answers, the index's rows' one source: one JSON entry per recorded
    session, in the order the index draws them, then one per store the glob found but could not read.

    A session's entry carries its harness, its id, its record count, its first and last moments as
    epoch milliseconds and its span in seconds, and — where an opencode record names a dispatcher for
    it — that dispatcher's session id and the dispatching call's name, the two halves `dispatches`
    holds; an entry so dispatched follows its dispatcher's, so the feed is in the order the index
    draws the rows. An unreadable store's entry is `{unreadable: <store name>}` and carries no other
    key. This is the schema's one definition: `index.js` renders the rows from exactly these keys."""
    sessions, unreadable = read_sessions(directory)
    dispatched = dispatches(sessions)
    children: dict[str, list[dict]] = {}
    for session in sessions:
        if session["id"] in dispatched:
            children.setdefault(dispatched[session["id"]][0], []).append(session)
    entries = []
    for session in sorted(
        (session for session in sessions if session["id"] not in dispatched), key=lambda session: session["first"]
    ):
        entries.append(_feed_entry(session, dispatched.get(session["id"])))
        for child in sorted(children.get(session["id"], ()), key=lambda session: session["first"]):
            entries.append(_feed_entry(child, dispatched.get(child["id"])))
    return entries + [{"unreadable": store} for store in unreadable]


def _feed_entry(session: dict, dispatcher: tuple[str, str] | None) -> dict:
    """One session's entry in the feed, `dispatcher` left out where none dispatched it."""
    entry = {
        "harness": session_harness(session),
        "id": session["id"],
        "records": len(session["records"]),
        "first": int(session["first"]),
        "last": int(session["last"]),
        "span": _round_half_up((session["last"] - session["first"]) / 1000),
    }
    if dispatcher:
        entry["dispatcher"] = {"session": dispatcher[0], "name": dispatcher[1]}
    return entry


def index_html() -> str:
    """The index of record files, static: its page file carries no row, and its script renders them
    from the feed `/api/traces` answers (`traces_feed`) — the board's pattern, the payload consumed
    client-side. The rows' order and their dispatcher grouping are the feed's.

    The index carries the presentation layer and names no view of its own: opened on its own it
    stands beside no board, so the deco — the nav, the frame band and the decoration's script — is
    the template's own text, the band's legend filled here from its one home (the index carrying no
    dispatcher and no way back), and the layer's carriage left at its mark — filled by the serve path
    with its link (`served_page`), its one consumer, since no file flow writes the index."""
    return strict_fill(INDEX, band_fills(dispatcher=None, return_to=None))


def served_page(text: str) -> str:
    """A page as the dashboard serves it: the presentation layer **linked** at its carriage mark — the
    dashboard's Content-Security-Policy refuses an inline stylesheet, and the one source is the board
    panel's own file, which the board page and the profiler's pages link alike. The render's carrier is
    the inline — a standalone page being self-contained — so the serve path fills the page's carriage
    mark with the link where the render filled the layer's text, and a mark left standing refuses."""
    return strict_fill(text, {LAYER_MARK: LAYER_LINK})


def _link(href: str, text: str) -> str:
    """`text`, as a link to `href`."""
    return f'<a href="{html.escape(href)}">{html.escape(text)}</a>'


def _session_link(identifier: str) -> str:
    """A session id, as a link to its page."""
    return _link(PAGE_PREFIX + quote(identifier), identifier)


def dispatcher_html(dispatcher: tuple[str, str]) -> str:
    """The frame band's dispatch line: the session that dispatched this page, linked to its page, and
    the call that dispatched it."""
    session, name = dispatcher
    return (
        f'<span class="dispatched"><strong>Dispatched by</strong> {_session_link(session)} — {html.escape(name)}</span>'
    )


def band_fills(*, dispatcher: tuple[str, str] | None, return_to: str | None) -> dict[str, str]:
    """The frame band's per-page fills for the strict fill: the legend from its one home `LEGEND`,
    the dispatch line, and the way back. A fact this page carries none of fills its mark empty — the
    dispatcher where none dispatched it, the way back where there is no list to return to — and the
    strict fill does not raise on an empty value, so a page with neither carries the band bare."""
    return {
        BAND_LEGEND: LEGEND,
        DISPATCHED_MARK: dispatcher_html(dispatcher) if dispatcher else "",
        RETURN_MARK: f'<a class="return" href="{return_to}">{RETURN_LABEL}</a>' if return_to else "",
    }


PAGE_PREFIX = "/page/"
# The frame band's fills, in the order the band reads them — the how-to-read legend from its one home
# `LEGEND`, then the dispatch line, then the way back — as marks the strict fill replaces. They sit
# inside the band both profiler templates carry as their own text, so one fill assembles the deco
# the dashboard once spliced; a mark the fill is told to leave empty comes out empty, not standing.
BAND_LEGEND = "<!--LEGEND-->"
DISPATCHED_MARK = "<!--DISPATCHED-->"
RETURN_MARK = "<!--RETURN-->"
# The index's template: static. The rows' table is the one the script fills (`index.js`, the feed
# `/api/traces` as its payload), and its script's read of the feed is what the page's body carries;
# the script is the template's own text, as the deco is, and served under the pages' policy.
# `<!--LAYER-->` stands in the template, as it does on a page, and the serve path fills it with the
# link (`served_page`) — the render's own carrier for a page being the layer's text. The three band
# marks are the last thing before the body's own content, their text no stylesheet's.
# A harness's dot wears its brand color, the page's own rule rather than the site's — the dots are
# the only brand-marked part of a row — and its class is the name the feed's entry carries where the
# script's `HARNESS_MARKS` holds a dot for it, so the style block's harness names and that list
# change together.
INDEX = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>devpro — profiler view: sessions</title>
<!--LAYER-->
<style>
main { padding: 1rem; }
h1 { font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem; }
table { border-collapse: collapse; }
th, td { text-align: left; padding: 0.4rem 1rem 0.4rem 0; border-bottom: 1px solid var(--line); }
th { font-weight: 600; color: var(--muted); font-size: 0.85rem; }
a { color: var(--fg); }
a:hover, a:focus-visible { color: var(--accent); }
tr:nth-child(odd) td { background: var(--zebra); }
td small { color: var(--muted); }
tr td:first-child.child { border-left: 3px solid var(--accent); }
tr td:first-child.child + td { padding-left: 2.4rem; }
.harness { width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-right: 7px; }
.harness.opencode { background: #4a9eea; }
.harness.claude { background: #d97757; }
.controls { display: flex; gap: 1rem; margin: 0 0 0.6rem; font-size: 0.9rem; color: var(--muted); }
.sort { font: inherit; padding: 0; border: 0; background: none; color: inherit; cursor: pointer; }
.sort:hover, .sort:focus-visible { color: var(--accent); }
th[aria-sort="ascending"] .sort::after { content: " ▲"; }
th[aria-sort="descending"] .sort::after { content: " ▼"; }
.notice { color: var(--fg); border-left: 3px solid var(--c0); padding: 0.3rem 0 0.3rem 0.6rem; margin: 0 0 0.6rem; }
</style>
<nav class="site-nav scanlines"><span class="brand">devpro</span><span class="views"><a class="view" href="/board/">kanban</a><a class="view active" href="/profiler/" aria-current="page">profiler</a></span><span class="nav-server">
  <span class="dot"></span>
  <span id="connection" role="status" aria-labelledby="connection"></span>
  <button id="stop" class="nav-stop" type="button">Stop</button>
</span></nav>
<div class="frame-band scanlines"><!--LEGEND--><!--DISPATCHED--><!--RETURN--></div>
<script src="/profiler/deco.js"></script>
<main>
<h1>Sessions</h1>
<div class="controls">
<label><input type="checkbox" id="child-rows" checked> child rows</label>
<label><input type="checkbox" id="harness-claude" checked> claude</label>
<label><input type="checkbox" id="harness-opencode" checked> opencode</label>
</div>
<p id="notice" class="notice" role="alert" hidden></p>
<table>
<thead><tr><th>harness</th><th>session</th><th aria-sort="none"><button type="button" class="sort" data-sort="records">records</button></th><th aria-sort="none"><button type="button" class="sort" data-sort="agents">dispatched agents</button></th><th aria-sort="none"><button type="button" class="sort" data-sort="first">first to last</button></th><th aria-sort="none"><button type="button" class="sort" data-sort="span">span</button></th></tr></thead>
<tbody id="rows"></tbody>
</table>
</main>
<script>
'use strict';
// The index's rows, rendered from the feed the server answers — the board's pattern, the payload
// consumed client-side. One feed entry per session, in the order the index draws them, and one per
// store the feed could not read. A session dispatched by another is drawn under its dispatcher, its
// dispatcher's row carrying the count of the children beneath it. The moments are epoch
// milliseconds and become the row's `<time>` elements, whose local reading the deco writes and whose
// titles keep the raw UTC for a hover. Reads the entry's own keys and nothing else: `harness`, `id`,
// `records`, `first`, `last`, `span`, `dispatcher`, and `unreadable` on a store's entry.
const FEED = '/api/traces';
const PAGE = '/page/';
const HARNESS_MARKS = ['opencode', 'claude'];

const el = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};

// A session id, as a link to its page.
const link = (id) => {
  const anchor = el('a', id);
  anchor.href = PAGE + encodeURIComponent(id);
  return anchor;
};

const pad = (n) => String(n).padStart(2, '0');
// A span in whole seconds, as the index states it: hours and minutes, minutes alone, seconds below
// a minute and `0s` for a zero-length span.
const span = (seconds) => {
  if (seconds < 60) return String(seconds) + 's';
  const [minutes, rest] = [Math.floor(seconds / 60), seconds % 60];
  if (minutes < 60) return rest ? minutes + 'm ' + rest + 's' : minutes + 'm';
  const [hours, left] = [Math.floor(minutes / 60), minutes % 60];
  return left ? hours + 'h ' + left + 'm' : hours + 'h';
};

// A moment's UTC reading, the one a row states: the first to the second, the last with its
// milliseconds — `2026-01-01 00:00:00 UTC` and `2026-01-01T00:00:05.000Z`.
const day = (d) => d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
const clock = (d) => pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()) + ':' + pad(d.getUTCSeconds());
const utcStamp = (ms) => day(new Date(ms)) + ' ' + clock(new Date(ms)) + ' UTC';
const isoStamp = (ms) => {
  const d = new Date(ms);
  const fraction = d.getUTCMilliseconds() ? '.' + String(d.getUTCMilliseconds()).padStart(3, '0') : '';
  return day(d) + 'T' + clock(d) + fraction + 'Z';
};

// A moment as the index draws one: the machine form in the `<time>` element's `datetime`, the raw UTC
// in its title and — where no script runs — its text. The deco finds a moment by this tag, wherever
// it stands: a moments cell's two ends and the index's first-to-last line are the same element.
const moment = (ms) => {
  const node = el('time', utcStamp(ms));
  node.setAttribute('datetime', isoStamp(ms));
  node.title = utcStamp(ms);
  return node;
};

// The two moments' cell. The first to the second and the last with its milliseconds are the moments'
// raw UTC reading, the one the cell's text serves and its title states.
const moments = (session) => {
  const cell = el('span', undefined, 'moments');
  cell.title = utcStamp(session.first) + ' to ' + isoStamp(session.last);
  cell.append(moment(session.first), ' to ', moment(session.last));
  return cell;
};

// One row: a dispatcher's carries the count of the children drawn beneath it; a child's carries the
// accent bar's empty cell and names the call that dispatched it. Both carry the harness with its
// mark where the page holds one, their own count, moments and span. A row's sort keys are the
// entry's own: the dispatcher's children count, its record count, its first moment and its span.
const row = ({ session, dispatched, children = 0 }) => {
  const tr = el('tr');
  tr.setAttribute('data-agents', String(children));
  tr.setAttribute('data-records', String(session.records));
  tr.setAttribute('data-first', String(session.first));
  tr.setAttribute('data-span', String(session.span));
  const harness = el('td');
  const mark = HARNESS_MARKS.includes(session.harness) ? session.harness : '';
  harness.append(el('span', undefined, ('harness ' + mark).trim()), session.harness);
  const id = el('td', undefined, dispatched ? 'child' : undefined);
  id.append(link(session.id));
  if (dispatched) {
    id.append(' ', el('small', '↳ child — ' + dispatched.name));
  } else if (children) {
    const count = children === 1 ? '1 dispatched agent' : children + ' dispatched agents';
    id.append(' ', el('small', '— ' + count));
  }
  const window = el('td');
  window.append(moments(session));
  tr.append(harness, id, el('td', session.records + ' records'), window, el('td', span(session.span)));
  return tr;
};

// A full-width row: a store's name where the feed could not read it, the table's own empty reading
// where the feed holds no session to draw.
const wideRow = (text) => {
  const cell = el('td', text);
  cell.colSpan = 6;
  const tr = el('tr');
  tr.append(cell);
  return tr;
};
const empty = () => wideRow('No sessions recorded yet: run a session with the hook installed.');
const unreadable = (store) => wideRow(store + ' is unreadable');

// What the page holds: every session the feed drew, in the feed's order, each with its children
// counted and the call that dispatched it where one did — and every store the feed could not read.
// The controls read this, and a control's change redraws the table from it rather than fetching the
// feed again. No control hides a store: a store that could not be read is named wherever it stands.
let held = [];
let stores = [];
let order = null; // the column the heads were last sorted on, and now ascending or descending

// A session the page hides: the child-rows control takes every dispatched session out, and each
// harness's control its own sessions. A dispatcher whose children are hidden keeps its row, and its
// count names the agents the feed holds rather than the rows on screen.
const hides = (session) =>
  (!document.getElementById('child-rows').checked && session.dispatcher) ||
  !document.getElementById('harness-' + session.harness).checked;

// The table from what the page holds: the feed's order, or the sorted order where a head was chosen,
// each dispatcher's row followed by its own visible children, and each unread store beside them. A
// dispatcher's count is the agents the feed holds beneath it, whether or not the page is showing them.
const draw = () => {
  const visible = held.filter((session) => !hides(session));
  const counted = new Map();
  const children = new Map();
  for (const session of held) {
    if (!session.dispatcher) continue;
    const parent = session.dispatcher.session;
    counted.set(parent, (counted.get(parent) || 0) + 1);
    if (hides(session)) continue;
    if (!children.has(parent)) children.set(parent, []);
    children.get(parent).push(session);
  }
  const tops = visible.filter((session) => !session.dispatcher);
  if (order) {
    const s = order.descending ? -1 : 1;
    tops.sort((a, b) => s * (a[order.key] < b[order.key] ? -1 : a[order.key] > b[order.key] ? 1 : 0));
  }
  const drawn = [];
  for (const session of tops) {
    const kids = children.get(session.id) || [];
    drawn.push(row({ session, children: counted.get(session.id) || 0 }));
    for (const kid of kids) drawn.push(row({ session: kid, dispatched: kid.dispatcher }));
  }
  for (const store of stores) drawn.push(unreadable(store));
  document.getElementById('rows').replaceChildren(...(drawn.length ? drawn : [empty()]));
};

const show = (feed) => {
  held = feed.filter((entry) => !entry.unreadable);
  stores = feed.filter((entry) => entry.unreadable).map((entry) => entry.unreadable);
  draw();
};

// Column heads: a head's first press sorts ascending, its next descending, the arrow on the head
// saying which, and a third press on the same head returns the feed's own order. A head's `data-sort`
// is the feed entry's own key its column sorts on. The sort state is the column head's own —
// `aria-sort` on the `<th>`, where a table's sort belongs — so the button is the label and the
// press, and the cell announces the order.
for (const label of document.querySelectorAll('.sort')) {
  label.addEventListener('click', () => {
    const cell = label.closest('th');
    const key = label.dataset.sort;
    if (order === null || order.key !== key) order = { key, descending: false };
    else if (!order.descending) order = { key, descending: true };
    else order = null;
    for (const other of document.querySelectorAll('.sort')) other.closest('th').setAttribute('aria-sort', 'none');
    if (order) cell.setAttribute('aria-sort', order.descending ? 'descending' : 'ascending');
    draw();
  });
}
for (const control of document.querySelectorAll('.controls input')) control.addEventListener('change', draw);

// The feed's failure names itself in the page, in the feed's own words, and is no session's absence:
// the no-records reading stands for a feed that answered with nothing to draw.
const notice = (error) => {
  const line = document.getElementById('notice');
  line.textContent = 'The traces feed could not be read: ' + String(error.message || error) + '.';
  line.hidden = false;
};

fetch(FEED, { cache: 'no-store' })
  .then((response) => {
    if (!response.ok) throw new Error('HTTP ' + response.status);
    return response.json();
  })
  .then(show)
  .catch((error) => {
    console.warn('the traces feed could not be read: ' + String(error));
    notice(error);
  });
</script>
</body>
</html>
"""


def session_for(path: str, directory: Path | str) -> dict | None:
    """The session recorded at `/page/<session-id>`'s id, or nothing where the path names no page or
    no session: the page's own read, the records the render and the band's facts both draw from."""
    if not path.startswith(PAGE_PREFIX):
        return None
    sessions, _ = read_sessions(directory)
    return next((session for session in sessions if session["id"] == path[len(PAGE_PREFIX) :]), None)


def page_for(session: dict, *, return_to: str | None, dispatcher: tuple[str, str] | None) -> str:
    """A page of the profiler view as the dashboard serves it: the view's own text — the nav, the
    frame band with its legend, the decoration's script, the presentation layer linked — the band's
    per-page facts the dashboard's own lookup names, one legend on the page and the script once."""
    return strict_fill(
        (files(__package__) / "view.html").read_text(encoding="utf-8"),
        {
            DATA_MARK: _inlined_session_data(session),
            LAYER_MARK: LAYER_LINK,
            **band_fills(dispatcher=dispatcher, return_to=return_to),
        },
    )
