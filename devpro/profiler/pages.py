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

import html
import json
import math
import re
from importlib.resources import files
from pathlib import Path
from typing import NamedTuple
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
    TRACE_STORES,
    TREE_WIDTH,
    _epoch_ms,
    _json,
    _local,
    _round_half_up,
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
# The deco's carriage, the second thing the two carriers hold differently: the serve path names the
# script by file, and the render — a page opened from disk — carries its text inline.
DECO_MARK = "<!--DECO-->"
DECO_LINK = '<script src="/profiler/deco.js"></script>'

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
    '  <span><svg width="34" height="12"><line x1="0" x2="26" y1="6" y2="6" stroke="var(--accent)" '
    'stroke-width="2"/><path d="M24 1 L34 6 L24 11 z" fill="var(--accent)"/></svg>call that starts a '
    "context</span>\n"
    '  <span><svg width="34" height="12"><line x1="0" x2="32" y1="6" y2="6" stroke="var(--accent)" '
    'stroke-width="2"/><path d="M24 1 L34 6 L24 11" fill="none" stroke="var(--accent)" stroke-width="2"/>'
    "</svg>one that runs in the background</span>\n"
    '  <span><svg width="34" height="12"><line x1="0" x2="30" y1="6" y2="6" stroke="var(--muted)" '
    'stroke-width="1.5" stroke-dasharray="5 4"/><path d="M26 1 L34 6 L26 11" fill="none" '
    'stroke="var(--muted)" stroke-width="1.5"/></svg>return with the result</span>\n'
    '  <span><svg width="14" height="14"><path d="M7 1 l6 6 l-6 6 l-6 -6 z" fill="var(--accent)"/>'
    "</svg>skill loaded inline: its text joins this context; several in a row share one diamond, click "
    "it to list them</span>\n"
    '  <span><svg width="26" height="14"><rect x="1" y="1" width="24" height="12" fill="none" '
    'stroke="var(--fg)" stroke-width="1.5"/></svg>compacted: history replaced by a summary</span>\n'
    '  <span><svg width="10" height="16"><rect x="0" y="0" width="10" height="16" rx="2" '
    'fill="var(--accent)" fill-opacity=".85"/></svg>context at work</span>\n'
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
# first and the template's own rules override them. The deco's element is its text in a script block
# of its own, ahead of the page's own script, which reads the one global it publishes.
LAYER_INLINE = "<style>\n" + SHARED_CSS + "\n</style>"
DECO_INLINE = "<script>\n" + (files(__package__) / "deco.js").read_text(encoding="utf-8") + "\n</script>"


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
    """Epoch milliseconds as the tree's time column: local, to the second."""
    return _local(ms).strftime("%H:%M:%S")


def subagent_stops(records: list[dict]) -> dict[str, dict]:
    """agent id -> its last SubagentStop.

    A background subagent stops each time it has nothing to do and is woken when a child of its own
    reports, so the last stop is the one that ends it."""
    stops: dict[str, dict] = {}
    for record in records:
        if record.get("event") == "SubagentStop" and record.get("agent_id"):
            stops[record["agent_id"]] = {**stops.get(record["agent_id"], {}), **record}
    return stops


IDLE = "experimental.idle"


def child_episodes(records: list[dict]) -> dict[str, dict]:
    """session id -> its latest idle with no background work running: where that session's run ended.

    An opencode session idles each time an episode closes — the agent loop finished and nothing is
    queued — and a wake that follows its own background work, or a dispatcher's follow-up, opens
    another episode whose idle is later. An idle seen with background work listed is no episode's end,
    so it is not kept; the latest kept one is the end the join reads."""
    episodes: dict[str, dict] = {}
    for record in records:
        if record.get("event") == IDLE and record.get("session") and not record.get("background"):
            episodes[str(record["session"])] = record
    return episodes


# Traces captured before a background skill was told apart from a finished one hold Claude Code's
# launch notice as the call's result.
LAUNCH_NOTICE = re.compile(r"^Running in the background as @")


def with_stop(record: dict, stop: dict | None, handback: str | None, episode: dict | None = None) -> dict:
    """A background subagent's call, ended by its stop where one is recorded.

    Its call returns at once and it ends at its SubagentStop; its result is what it handed back. Until
    its first stop it is `running`: the duration recorded so far is the launch, not the work.

    An opencode dispatch records no stop, its child ending at the child's own empty-background idle
    (`episode`, read from the child's store): the record's agent and model become the child's, where
    the idle carries them, and its duration the span from the dispatch to that idle. A dispatch whose
    episode never came is the acknowledgment as it was written — never `running`, since the capture
    writes the launch, not the work, and its end is the child's to report."""
    launched = {key: value for key, value in record.items() if key != "result"}
    call = {**launched, "background": True} if LAUNCH_NOTICE.match(record.get("result") or "") else record
    if not stop:
        if episode:
            return {
                **call,
                "child_agent_type": episode.get("agent_type") or call.get("child_agent_type"),
                "model": episode.get("model") or call.get("model"),
                "duration_ms": max(0, (_epoch_ms(episode.get("at")) or 0) - (_epoch_ms(call.get("at")) or 0)),
            }
        return {**call, "running": True} if LAUNCH_NOTICE.match(call.get("result") or "") else call
    merged = {**call, "child_agent_type": call.get("child_agent_type") or stop.get("agent_type")}
    if not call.get("background"):
        return merged
    return {
        **merged,
        "at": stop.get("at"),
        "duration_ms": max(0, (_epoch_ms(stop.get("at")) or 0) - start_of(call)),
        "result": handback or call.get("result") or stop.get("result"),
    }


def unique_calls(records: list[dict], episodes: dict[str, dict] | None = None) -> list[dict]:
    """The calls a trace holds once each: a plugin and a committed hook on one machine record everything
    twice.

    `episodes` is `child_episodes` over every store read, where a reader joins an opencode dispatch to
    its child's end: the child's store is not `records`, so its idle is handed in, keyed by the session
    id the dispatch's `child_agent_id` names."""
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
        child = record.get("child_agent_id")
        calls.append(with_stop(record, stops.get(child), handbacks.get(child), (episodes or {}).get(str(child))))
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

# The prefix an agent set's definitions carry their names under, dropped where a page renders one: the
# stored records and the feed keep the name as recorded. It is the install's one name,
# `components.NAME`; `pages` spells it rather than importing a module the capture path may not pay
# for, and the lane test pins the spelling to `components.NAME`.
AGENT_PREFIX = "devpro-"
# Where the index script's prefix line stands in the template, `index_html` replacing it with the line
# below: a mark a carrier has filled is no unfilled one, so the strict fill lets neither stand.
AGENT_PREFIX_MARK = "/*AGENT_PREFIX*/"
# The one line of JavaScript both pages' scripts get the prefix from, beside the template scripts that
# read it: a rendering fills their `AGENT_PREFIX` mark with this text, so the four spellings — this
# constant, the index's row strip and `view.html`'s `shownName` — are one line the lane checks.
AGENT_PREFIX_LINE = f"const AGENT_PREFIX = '{AGENT_PREFIX}';"


def rendered_name(name: str | None, tool: str | None) -> str | None:
    """An Agent call's name as a page renders it: the set's prefix dropped. Every other call's name is
    as recorded — a Bash command's `devpro-check-plan` is that command, not the set's prefix."""
    return name.removeprefix(AGENT_PREFIX) if name and tool == "Agent" else name


def call_label(tool: str | None, name: str | None) -> str:
    """The name leads and the kind follows: `review (skill)`, `counter (agent)`, `wc -l a (Bash)`."""
    word = TOOL_WORDS.get(tool, tool)
    rendered = rendered_name(name, tool)
    return f"{rendered} ({word})" if rendered else word


def context_of(record: dict) -> str:
    """The context a call belongs to: the subagent's id, or main's."""
    return record.get("agent_id") or MAIN


def short_id(identifier: str) -> str:
    """An id as a tree line shows it: main's as it stands, a subagent's first few characters."""
    return MAIN if identifier == MAIN else identifier[:CONTEXT_WIDTH]


def contexts_of(
    records: list[dict],
    *,
    root_label: str = MAIN,
    root_hue: int = 0,
    episodes: dict[str, dict] | None = None,
) -> tuple[list[dict], list[dict]]:
    """The trace's contexts and markers.

    A context is one conversation history: main, or a subagent started by a forked Skill or an Agent
    call. Inline skills and compactions are markers in one. A `fork` subagent starts with a copy of its
    parent's history; every other subagent starts with its prompt only. The root keeps the id `main`,
    and takes the label and hue a child's page names it by — the call that dispatched the session,
    in the color that call's own context wears on its dispatcher's page. `episodes` is
    `unique_calls`'s: the calls joined to their children's ends."""
    calls = unique_calls(records, episodes)
    contexts: list[dict] = [{"id": MAIN, "parent": None, "kind": "root", "label": root_label}]
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

    # Color follows history: a copy keeps its parent's hue, a fresh context gets the next one — never
    # the root's, which a page's root holds whether or not a fresh context counted past it.
    hues: dict[str, int] = {}
    next_hue = 1
    for context in contexts:
        if context["id"] == MAIN:
            context["hue"] = root_hue
        elif context["kind"] == "copy" and context.get("parent") in hues:
            context["hue"] = hues[context["parent"]]
        else:
            while next_hue == root_hue:
                next_hue += 1
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


def build_forest(records: list[dict], markers: list[dict] | None = None, episodes: dict[str, dict] | None = None):
    """The tree's roots: each call under the call that started its context, in start order."""
    nodes = [
        {"record": record, "index": index, "start": start_of(record), "children": []}
        for index, record in enumerate(unique_calls(records, episodes))
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


class Dispatcher(NamedTuple):
    """A session's dispatcher, as the band and the page's root context read it: the session that
    dispatched this one, the call that did, the tool it ran as, and the hue that call's context wears
    on its dispatcher's page."""

    session: str
    name: str
    tool: str | None
    hue: int


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


def render_tree(
    records: list[dict], *, verbose: bool = False, color: bool = False, episodes: dict[str, dict] | None = None
) -> str:
    """The trace as the text tree. `episodes` is `session_data`'s: the joins an opencode dispatch takes
    to its child's end, which the one tree draws where the session has one."""
    contexts, markers = contexts_of(records, episodes=episodes)
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

    walk(build_forest(records, [marker for marker in markers if marker["kind"] == "compact"], episodes), 0)
    options["longest"] = max([0] + [(node.get("record") or {}).get("duration_ms") or 0 for node, _ in shown])
    return "\n".join([tree_header()] + [format_line(node, depth, **options) for node, depth in shown])


def session_data(
    session: dict, *, dispatcher: Dispatcher | None = None, episodes: dict[str, dict] | None = None
) -> dict:
    """The page data `view.html` inlines at its data mark: the session's calls as the file flow
    draws them, one source for the standalone render and the served page alike.

    A dispatched session's root context — its id still `main` — is named and colored by the call
    `dispatcher` names, in the hue that call's own context wears on its dispatcher's page. The models
    are the calls' own: the session's, and each context's of the calls it holds, in the order they
    first appear. The calls are the merged list the page draws, which carries the tokens
    `fill_context_tokens` fills at render where the capture left them out.

    `episodes` is `child_episodes` over every store the reader holds: an opencode dispatch's child ends
    in the child's own store, so the join reads it from there rather than from `session`."""
    calls = unique_calls(fill_context_tokens(session["records"]), episodes)
    contexts, markers = contexts_of(
        session["records"],
        root_label=(rendered_name(dispatcher.name, dispatcher.tool) or MAIN) if dispatcher else MAIN,
        root_hue=dispatcher.hue if dispatcher else 0,
        episodes=episodes,
    )
    spend = _context_spend(session["records"])
    by_context: dict[str, list[dict]] = {}
    for record in calls:
        by_context.setdefault(context_of(record), []).append(record)
    return {
        "session": session["id"],
        "branch": next((record.get("branch") for record in calls if record.get("branch")), None),
        "models": models_in(calls),
        "contexts": [
            {**context, "spent": spend.get(context["id"]), "models": models_in(by_context.get(context["id"], []))}
            for context in contexts
        ],
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
                "model": record.get("model"),
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


def _inlined_session_data(session: dict, *, dispatcher: Dispatcher | None, episodes: dict[str, dict] | None) -> str:
    """`session_data` as the JSON a page's script inlines: `<` escaped so tool output cannot close the
    script tag, and `/` escaped so it cannot spell a fill's mark — `/*DATA*/null` among them, which
    the strict fill refuses in a value."""
    data = session_data(session, dispatcher=dispatcher, episodes=episodes)
    return _json(data).replace("<", "\\u003c").replace("/", "\\/")


def _rendering(
    session: dict, *, dispatcher: Dispatcher | None, return_to: str | None, episodes: dict[str, dict] | None
) -> str:
    """The page's one rendering: the template's own text with the session's data, the band's facts and
    the prefix line filled, the layer's and the deco's marks left standing for their carriers' fills —
    `render_html` inlines both texts, a file being unable to load a server's file, and the serve path
    fills the two links (`served_page`). One rendering, two carriers."""
    template = (files(__package__) / "view.html").read_text(encoding="utf-8")
    return strict_fill(
        template,
        {
            DATA_MARK: _inlined_session_data(session, dispatcher=dispatcher, episodes=episodes),
            AGENT_PREFIX_MARK: AGENT_PREFIX_LINE,
            **band_fills(dispatcher=dispatcher, return_to=return_to, legend=True),
        },
    )


def render_html(session: dict, *, dispatcher: Dispatcher | None, episodes: dict[str, dict] | None = None) -> str:
    """One self-contained page: the package's template with the presentation layer, the deco, the
    how-to-read legend and the trace inlined, and the frame band's per-page facts the session's stores
    name — the way back to the list, and the dispatcher where one dispatched it — the same facts the
    served page fills, the layer's and the deco's carriage the differences between the carriers: a file
    links neither, so it carries both texts and the page's script finds the one notation they hold.
    `episodes` is `session_data`'s: the child-end joins the page's calls take."""
    return strict_fill(
        _rendering(session, dispatcher=dispatcher, return_to=PROFILER_PATH, episodes=episodes),
        {LAYER_MARK: LAYER_INLINE, DECO_MARK: DECO_INLINE},
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

    Every store under `.devpro-temp/` is read — the directories named exactly for a harness the
    captures write, `values.TRACE_STORES` — so both harnesses' sessions reach one tree, and a session
    id is unique across them."""
    traces: list[Path] = []
    stores = Path(directory) / TRACE_DIR.parent
    for store in sorted(stores / name for name in TRACE_STORES if (stores / name).is_dir()):
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


def stamp(ms: int | float) -> str:
    """A moment's date and clock, local, to the second."""
    return _local(ms).strftime("%Y-%m-%d %H:%M:%S")


def tree(argv: list[str], directory: Path | str, *, color: bool = False) -> str:
    """The session the arguments choose, as the text tree or as the html page."""
    options = parse_tree_args(argv)
    sessions = list_sessions(directory)
    if not sessions:
        stores = Path(directory) / TRACE_DIR.parent
        raise UsageError(
            f"No traces in {', '.join(str(stores / name) for name in TRACE_STORES)}. "
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
    episodes = child_episodes([record for session in sessions for record in session["records"]])
    if options["format"] == "html":
        if len(chosen) > 1:
            listing = "\n".join(f"  {session['id'][:SESSION_WIDTH]}  {stamp(session['first'])}" for session in chosen)
            raise UsageError(f"The html page shows one session. Pick one by id prefix:\n{listing}")
        return render_html(chosen[0], dispatcher=dispatcher_of(chosen[0]["id"], sessions), episodes=episodes)
    if not branch:
        return render_tree(chosen[0]["records"], verbose=options["verbose"], color=color, episodes=episodes)
    blocks = []
    for session in chosen:
        rendered = render_tree(session["records"], verbose=options["verbose"], color=color, episodes=episodes)
        blocks.append(f"# session {session['id']} ({stamp(session['first'])})\n{rendered}")
    return "\n\n".join(blocks)


# ---------- the served index and pages ----------


def store_directories(directory: Path | str) -> list[Path]:
    """The stores under the project's scratch directory — each named exactly for a harness the captures
    write — in the order they are read."""
    stores = Path(directory) / TRACE_DIR.parent
    return sorted(stores / name for name in TRACE_STORES if (stores / name).is_dir())


def read_sessions(directory: Path | str) -> list[dict]:
    """`list_sessions`'s sessions, the index's and the pages' one read: each store the exact names
    find, walked a session at a time so a store's own listing is the one read that fails where it
    does. A store that cannot be read raises out of it."""
    sessions: list[dict] = []
    for store in store_directories(directory):
        traces = [path for path in store.iterdir() if path.name.endswith(".jsonl")]
        sessions.extend(session_of(path) for path in traces)
    return [session for session in sessions if session["records"]]


def session_harness(session: dict) -> str:
    """The harness's name, as the session's own records carry it, masked and clipped like any field."""
    harness = next((record.get("harness") for record in session["records"] if record.get("harness")), "")
    return clip(mask(str(harness)), NAME_LIMIT)


def models_in(records: list[dict]) -> list[str]:
    """The distinct models calls name, in the order they first appear, and none where no call names one.
    An event record is no call, so a marker naming a model states none."""
    models: list[str] = []
    for record in records:
        model = record.get("model")
        if record.get("tool") and isinstance(model, str) and model and model not in models:
            models.append(model)
    return models


def dispatches(sessions: list[dict]) -> dict[str, tuple[str, str, str | None]]:
    """child session id -> the session that dispatched it, that call's name and the tool it ran as.

    Only an opencode record names a session: its `child_agent_id` is a session id. A claude record's
    is an agent id, and claude records its subagents' calls in the parent's own file, so no claude
    session is ever a child here. A child two sessions name keeps the first in list order, and a
    session naming itself is no child: it would be dropped from the index's top level and drawn as
    its own child. The tool is the call's: a page rendering the dispatcher's name drops the set's
    prefix on an Agent call and on no other."""
    found: dict[str, tuple[str, str, str | None]] = {}
    for session in sessions:
        for record in session["records"]:
            child = record.get("child_agent_id")
            if record.get("harness") == "opencode" and child and str(child) != session["id"]:
                found.setdefault(str(child), (session["id"], str(record.get("name") or ""), record.get("tool")))
    return found


def dispatcher_of(session: str, sessions: list[dict]) -> Dispatcher | None:
    """The session that dispatched `session`, the call that did, the tool it ran as and the hue that
    call opened its context in — named by the stores' other sessions. The band's per-page fact and
    the page's root context both read it: the one lookup whoever fills either runs, so the dump's
    page and the served page name the same dispatcher, and the child's root wears the color the
    dispatcher's own page draws that context in.

    The child's records name no parent, so the hue is read off the dispatcher's records: they are the
    ones `contexts_of` draws the dispatcher's page from, so the child's record is the context whose id
    is the child's session id. That page's root hue is the dispatcher's own, read from the session
    that dispatched it up the chain — 0 where nothing did, and 0 at the session where the walk meets
    one it has already visited. Nothing is written at capture: the chain is walked at each read."""
    found = dispatches([x for x in sessions if x["id"] != session]).get(session)
    if not found:
        return None
    parent, name, tool = found
    root_hue, upstream, visited = 0, parent, {session}
    while upstream not in visited:
        visited.add(upstream)
        up = dispatcher_of(upstream, sessions)
        if up is None:
            break
        root_hue, upstream = up.hue, up.session
    contexts, _ = contexts_of(next(x["records"] for x in sessions if x["id"] == parent), root_hue=root_hue)
    return Dispatcher(parent, name, tool, next(context["hue"] for context in contexts if context["id"] == session))


def traces_feed(directory: Path | str) -> list[dict]:
    """The feed `/api/traces` answers, the index's rows' one source: one JSON entry per recorded
    session, in the order the index draws them.

    A session's entry carries its harness, its id, the models its calls recorded, its record count, the
    count of the dispatched agents it holds, its first and last moments as epoch milliseconds and its
    span in seconds, and — where an opencode record names a dispatcher for it — that dispatcher's
    session id and the dispatching call's name, the two halves `dispatches` holds; an entry so
    dispatched follows its dispatcher's, so the feed is in the order the index draws the rows. A store
    the exact names find and cannot read raises out of here: the answer is the handler's failed
    request, not an entry. Where the feed holds no session, it is one `{stores: <count>}` entry: the
    stores the exact names read, none of which held a record to draw — the count a zero-record store
    renders, which no session would otherwise tell apart from a tree with no store at all. This is the
    schema's one definition: the index's own script renders the rows from exactly these keys."""
    sessions = read_sessions(directory)
    dispatched = dispatches(sessions)
    children: dict[str, list[dict]] = {}
    for session in sessions:
        if session["id"] in dispatched:
            children.setdefault(dispatched[session["id"]][0], []).append(session)
    entries = []
    for session in sorted(
        (session for session in sessions if session["id"] not in dispatched), key=lambda session: session["first"]
    ):
        entries.append(_feed_entry(session, dispatched.get(session["id"]), len(children.get(session["id"], ()))))
        for child in sorted(children.get(session["id"], ()), key=lambda session: session["first"]):
            entries.append(_feed_entry(child, dispatched.get(child["id"])))
    if not entries:
        return [{"stores": len(store_directories(directory))}]
    return entries


def _feed_entry(session: dict, dispatcher: tuple[str, str, str | None] | None, agents: int = 0) -> dict:
    """One session's entry in the feed, `agents` the count of the sessions `dispatcher` and its
    siblings name as children, and `dispatcher` itself left out where none dispatched the session."""
    entry = {
        "harness": session_harness(session),
        "id": session["id"],
        "models": models_in(session["records"]),
        "records": len(session["records"]),
        "agents": agents,
        "first": int(session["first"]),
        "last": int(session["last"]),
        "span": _round_half_up((session["last"] - session["first"]) / 1000),
    }
    if dispatcher:
        session, name, tool = dispatcher
        entry["dispatcher"] = {"session": session, "name": name, "tool": tool}
    return entry


def index_html() -> str:
    """The index of record files, static: its page file carries no row, and its script renders them
    from the feed `/api/traces` answers (`traces_feed`) — the board's pattern, the payload consumed
    client-side. The rows' order and their dispatcher grouping are the feed's.

    The index carries the presentation layer and names no view of its own: opened on its own it
    stands beside no board, so the deco — the nav, the frame band and the decoration's script, which
    holds the one notation the page's script calls — is the template's own text, the band filled with
    none of its per-page facts (the index carrying no legend, no dispatcher and no way back), and the
    two carriage marks left standing — filled by the serve path with their links (`served_page`), its
    one consumer, since no file flow writes the index.
    The script's mark is the one prefix line, `AGENT_PREFIX_LINE`, filled here."""
    return strict_fill(
        INDEX.replace(AGENT_PREFIX_MARK, AGENT_PREFIX_LINE),
        band_fills(dispatcher=None, return_to=None, legend=False),
    )


def served_page(text: str) -> str:
    """A page as the dashboard serves it: the presentation layer **linked** at its carriage mark — the
    dashboard's Content-Security-Policy refuses an inline stylesheet, and the one source is the board
    panel's own file, which the board page and the profiler's pages link alike — and the deco linked
    at its own. The render's carrier is the inline — a standalone page being self-contained — so the
    serve path fills the page's two carriage marks with the two links where the render filled their
    texts, and a mark left standing refuses."""
    return strict_fill(text, {LAYER_MARK: LAYER_LINK, DECO_MARK: DECO_LINK})


def _link(href: str, text: str) -> str:
    """`text`, as a link to `href`."""
    return f'<a href="{html.escape(href)}">{html.escape(text)}</a>'


def _session_link(identifier: str) -> str:
    """A session id, as a link to its page."""
    return _link(PAGE_PREFIX + quote(identifier), identifier)


def dispatcher_html(dispatcher: Dispatcher) -> str:
    """The frame band's dispatch line: the session that dispatched this page, linked to its page, and
    the call that dispatched it — an Agent call, its record's tool gating the prefix's drop."""
    return (
        f'<span class="dispatched"><strong>Dispatched by</strong> {_session_link(dispatcher.session)} — '
        f"{html.escape(rendered_name(dispatcher.name, dispatcher.tool) or '')}</span>"
    )


def band_fills(*, dispatcher: Dispatcher | None, return_to: str | None, legend: bool) -> dict[str, str]:
    """The frame band's per-page fills for the strict fill: the legend from its one home `LEGEND`
    where the page carries one, the dispatch line, and the way back. A fact this page carries none of
    fills its mark empty — the legend on the index, the dispatcher where none dispatched it, and the
    way back on the index, which is the list itself — and the strict fill does not raise on an empty
    value, so a page carrying none of them carries the band bare."""
    return {
        BAND_LEGEND: LEGEND if legend else "",
        DISPATCHED_MARK: dispatcher_html(dispatcher) if dispatcher else "",
        RETURN_MARK: f'<a class="return" href="{return_to}">{RETURN_LABEL}</a>' if return_to else "",
    }


PAGE_PREFIX = "/page/"
# The profiler view's own path: the way back the frame band's return control names, on a session's
# page, whatever carrier wrote it — the dump's page and the served page's alike.
PROFILER_PATH = "/profiler/"
# The frame band's fills, in the order the band reads them — the how-to-read legend from its one home
# `LEGEND`, then the dispatch line, then the way back — as marks the strict fill replaces. They sit
# inside the band both profiler templates carry as their own text, so one fill assembles the deco
# the dashboard once spliced; a mark the fill is told to leave empty comes out empty, not standing.
BAND_LEGEND = "<!--LEGEND-->"
DISPATCHED_MARK = "<!--DISPATCHED-->"
RETURN_MARK = "<!--RETURN-->"
# The index's template: static. The rows' table is the one the template's own script fills (the feed
# `/api/traces` as its payload), and that script's read of the feed is what the page's body carries;
# the script is the template's own text, as the deco is, and served under the pages' policy.
# `<!--LAYER-->` and `<!--DECO-->` stand in the template, as they do on a page, and the serve path
# fills them with their links (`served_page`) — the render's own carrier for a page being the layer's
# text, and no index being written as a file. The three band
# marks are the last thing before the body's own content, their text no stylesheet's.
# A harness's dot wears its brand color, which the layer holds as `--harness-<name>` — the site's
# color rather than the page's, the page's rule only naming the variable. The dots are the only
# brand-marked part of a row, and a dot's class is the name the feed's entry carries where the
# script's `HARNESSES` holds that harness.
INDEX = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>devpro — profiler view: sessions</title>
<!--DECO-->
<!--LAYER-->
<style>
main { padding: 1rem; }
h1 { font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem; }
main { overflow-x: auto; }
table { border-collapse: collapse; table-layout: fixed; }
th, td { text-align: left; padding: 0.4rem 1rem 0.4rem 0; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-weight: 600; color: var(--muted); font-size: 0.85rem; overflow-wrap: anywhere; }
td { overflow-wrap: anywhere; }
a { color: var(--fg); }
a:hover, a:focus-visible { color: var(--accent); }
tr:nth-child(odd) td { background: var(--zebra); }
td small { color: var(--muted); }
tr td:first-child.child { border-left: 3px solid var(--accent); }
tr td:first-child.child + td { padding-left: 2.4rem; }
/* Each column's width, declared once as a custom property on the table: the `.col-*` rules read the
   properties, and the table's floor below is their sum, so no width is written twice. The fixed layout
   gives each column its width and measures no cell's content, so header and body stand in the same
   columns; a viewport narrower than the floor overruns it and `main` scrolls the table. */
table { --w-harness: 7.5rem; --w-session: 32ch; --w-model: 12rem; --w-records: 8rem; --w-agents: 8rem; --w-one: 15rem; --w-span: 7rem;
  min-width: calc(var(--w-harness) + var(--w-session) + var(--w-model) + var(--w-records) + var(--w-agents) + var(--w-one) + var(--w-span)); }
.col-harness { width: var(--w-harness); }
.col-session { width: var(--w-session); }
.col-model { width: var(--w-model); }
.col-records { width: var(--w-records); }
.col-agents { width: var(--w-agents); }
.col-one { width: var(--w-one); }
.col-span { width: var(--w-span); }
/* A session's id and the agent that dispatched it stand on one line, the child's indent inside the
   column; the model cell's list may wrap. */
.col-session, .col-session a, .col-session small { white-space: nowrap; }
.col-session small { margin-left: 0.4rem; }
/* The first-to-last cell's line never wraps: its column is wide enough for the longest pair the data
   produces, and a narrower viewport keeps the column and lets the table overrun it, rather than
   folding the line. */
.moments { white-space: nowrap; }
.harness { width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-right: 7px; }
.harness.opencode { background: var(--harness-opencode); }
.harness.claude { background: var(--harness-claude); }
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
<main>
<h1>Sessions</h1>
<div class="controls">
<label><input type="checkbox" id="child-rows" name="child-rows" value="on"> child rows</label>
<label><input type="checkbox" id="harness-claude" name="harness" value="claude" checked> claude</label>
<label><input type="checkbox" id="harness-opencode" name="harness" value="opencode" checked> opencode</label>
</div>
<p id="notice" class="notice" role="alert" hidden></p>
<table>
<thead><tr><th class="col-harness">harness</th><th class="col-session">session</th><th class="col-model">model</th><th class="col-records" aria-sort="none"><button type="button" class="sort" data-sort="records">records</button></th><th class="col-agents" aria-sort="none"><button type="button" class="sort" data-sort="agents">dispatched agents</button></th><th class="col-one" aria-sort="none"><button type="button" class="sort" data-sort="first">first to last</button></th><th class="col-span" aria-sort="none"><button type="button" class="sort" data-sort="span">span</button></th></tr></thead>
<tbody id="rows"></tbody>
</table>
</main>
<script>
'use strict';
// The index's rows, rendered from the feed the server answers — the board's pattern, the payload
// consumed client-side. One feed entry per session, in the order the index draws them. A session
// dispatched by another is drawn under its dispatcher, its dispatcher's row carrying the count of the
// children beneath it. The moments are epoch
// milliseconds and become the row's `<time>` elements, drawn local at birth — the reader's clock,
// 24-hour. Reads the entry's own keys and nothing else: `harness`, `id`, `models`,
// `records`, `agents`, `first`, `last`, `span`, `dispatcher`, and
// `stores` on a feed that drew nothing, naming how many stores the exact names read. The page's body is
// wrapped: the controls' state and the sort in force live in the page's URL, and the helpers for
// them are the page's own.
(() => {
const FEED = '/api/traces';
const PAGE = '/page/';
/*AGENT_PREFIX*/
const AGENT_TOOL = 'Agent';
// The moments' and durations' one notation, the deco's global (`devproFormat`): this page carries no
// formatter of its own.
const { localDay, clock, dur, scaled } = globalThis.devproFormat;
// The harnesses the controls carry a box for, in the page's own order: a box's id is this name
// behind `harness-`, and a row's dot classes it where the harness is one of these — the feed's name,
// the controls' boxes and the style block's two rules changing together.
const HARNESSES = ['claude', 'opencode'];

const el = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};

// A session id, as a link to its page — the page's own query carried along, so the controls' state
// and the sort in force survive the drill-down and the reader's way back.
const link = (id) => {
  const anchor = el('a', id);
  anchor.href = PAGE + encodeURIComponent(id) + location.search;
  return anchor;
};

// A moment as the index draws one, local at birth: its text the reading this script writes — there
// is no second pass to correct it, so a page whose script does not run carries no moment — the
// machine form in the `<time>` element's `datetime`.
const moment = (ms, text) => {
  const node = el('time', text);
  node.setAttribute('datetime', new Date(ms).toISOString());
  return node;
};

// The two moments' cell: the first end carries its date whole beside its time, the second its time
// only — the clock's being 24-hour makes a span across midnight plain by the numbers, no branch to
// state.
const moments = (session) => {
  const [first, last] = [new Date(session.first), new Date(session.last)];
  const cell = el('span', undefined, 'moments');
  cell.append(
    moment(session.first, localDay(first) + ' ' + clock(first)),
    ' to ',
    moment(session.last, clock(last)),
  );
  return cell;
};

// One row: a dispatcher's carries the count of the children the feed holds in the agents column; a
// child's carries the class `child` on its first cell — the harness cell, where the rule at the row's
// left edge and the session cell's indent are drawn from — and names after its id the call that
// dispatched it, no lead-in: the indent, the rule and its tone mark it a child. Both carry the
// harness with its mark where the page holds one, their own count, moments and span. A row's sort
// keys are the entry's own: the dispatched-agent count, the record count, the first moment and the
// span.
const row = ({ session, dispatched, children = 0 }) => {
  const tr = el('tr');
  tr.setAttribute('data-records', String(session.records));
  tr.setAttribute('data-first', String(session.first));
  tr.setAttribute('data-span', String(session.span));
  const harness = el('td', undefined, dispatched ? 'col-harness child' : 'col-harness');
  const mark = HARNESSES.includes(session.harness) ? session.harness : '';
  harness.append(el('span', undefined, ('harness ' + mark).trim()), session.harness);
  const id = el('td', undefined, 'col-session');
  id.title = session.id;
  id.append(link(session.id));
  if (dispatched) {
    const shown = dispatched.tool === AGENT_TOOL ? dispatched.name.replace(AGENT_PREFIX, '') : dispatched.name;
    id.append(' ', el('small', shown));
  }
  const window = el('td', undefined, 'col-one');
  window.append(moments(session));
  const count = session.agents === 1 ? '1 agent' : session.agents + ' agents';
  tr.append(
    harness,
    id,
    el('td', session.models.join(', '), 'col-model'),
    el('td', session.records + ' records', 'col-records'),
    el('td', session.agents ? count : '', 'col-agents'),
    window,
    el('td', dur(session.span * 1000), 'col-span'),
  );
  return tr;
};

// A full-width row: a store's name where the feed could not read it, or the table's own reading where
// it draws no session.
const wideRow = (text) => {
  const cell = el('td', text);
  cell.colSpan = 7;
  const tr = el('tr');
  tr.append(cell);
  return tr;
};
// The no-records reading, which names which state the page stands in — a store held sessions and the
// controls hid them, stores stand and none held a record, or the tree holds no store at all. The
// count the feed states is the stores it found, so a tree holding stores that recorded nothing reads
// differently from one holding none.
const empty = (held_count, store_count) => {
  if (held_count) return wideRow('No sessions shown: the controls hide every session the feed holds.');
  if (store_count) return wideRow('No sessions recorded yet: the stores hold no record to draw.');
  return wideRow('No session store found yet: run a session with the hook installed.');
};

// What the page holds: every session the feed drew, in the feed's order, each with its children
// counted and the call that dispatched it where one did. The controls read this, and a control's
// change redraws the table from it rather than fetching the feed again.
let held = [];
let found = 0; // the stores the feed found, where it drew no session to say so itself

// The column the table stands sorted on, and the order it stands in, read off the head that marks it:
// the `<th>`'s `aria-sort` is where a table's sort belongs, and a sort is the page's whether a press
// set it or the URL the page opened at did.
const sorted = () => {
  for (const head of document.querySelectorAll('.sort')) {
    const cell = head.closest('th');
    const state = cell ? cell.getAttribute('aria-sort') : null;
    if (state === 'ascending' || state === 'descending') return { key: head.dataset.sort, descending: state === 'descending' };
  }
  return null;
};

// A session the page hides: the child-rows control takes every dispatched session out, and each
// harness's control its own sessions — a harness the controls carry no box for is visible, since no
// control can hide it. A dispatcher is never hidden by a control: it keeps its row, and its count
// names the agents the feed holds rather than the rows on screen. The harness pair is two boxes and
// hides by the harness alone: a claude session an opencode dispatch named as its child is the
// feed's child, which the child-rows control alone hides, and its own harness's box hides it beside.
const hides = (session) => {
  if (session.dispatcher && !document.getElementById('child-rows').checked) return true;
  if (!HARNESSES.includes(session.harness)) return false;
  return !document.getElementById('harness-' + session.harness).checked;
};

// The table from what the page holds: the feed's order, or the sorted order where a head marks the
// table sorted, each dispatcher's row followed by its own visible children. A dispatcher's count is
// the agents the feed holds beneath it, whether or not the page is showing them; an empty table
// reads as which state the page stands in (`empty`).
const draw = () => {
  const visible = held.filter((session) => !hides(session));
  const children = new Map();
  for (const session of held) {
    if (!session.dispatcher) continue;
    if (hides(session)) continue;
    const parent = session.dispatcher.session;
    if (!children.has(parent)) children.set(parent, []);
    children.get(parent).push(session);
  }
  // A session stands at the top where nothing dispatched it, or where its dispatcher is not drawn:
  // an orphan follows its dispatcher's level, never vanishing with a hidden dispatcher.
  const shown = new Set(visible.map((session) => session.id));
  const tops = visible.filter((session) => !session.dispatcher || !shown.has(session.dispatcher.session));
  const order = sorted();
  if (order) {
    const s = order.descending ? -1 : 1;
    tops.sort((a, b) => s * (a[order.key] < b[order.key] ? -1 : a[order.key] > b[order.key] ? 1 : 0));
  }
  const drawn = [];
  for (const session of tops) {
    const kids = children.get(session.id) || [];
    drawn.push(row({ session, children: session.agents }));
    for (const kid of kids) drawn.push(row({ session: kid, dispatched: kid.dispatcher }));
  }
  if (!drawn.length) drawn.push(empty(held.length, found));
  document.getElementById('rows').replaceChildren(...drawn);
};

const show = (feed) => {
  held = feed.filter((entry) => entry.stores === undefined);
  found = feed.reduce((sum, entry) => sum + (entry.stores || 0), 0);
  // A harness box the feed holds no session for is disabled: left checked it would report filtering
  // a harness the feed has none of, and left pressable it would hide nothing on every press. A box it
  // disables is checked again, so the disabled box neither hides rows nor carries an "off" the reader
  // never chose; one the feed still holds keeps whatever state the reader left it in.
  for (const harness of HARNESSES) {
    const box = document.getElementById('harness-' + harness);
    box.disabled = !held.some((session) => session.harness === harness);
    if (box.disabled) box.checked = true;
  }
  sync();
  draw();
};

// The page's state, in the page's URL: each control whose state deviates from its own default — the
// child-rows box off, each harness box on — and the head the table sorts on with the order it stands
// in. A page standing at every control's default and sorted on nothing is the page it opened on, so
// its link carries no query at all — the short URL for an untouched page, and the reader's own
// choices for one they changed. The URL the page shows is the link they copy:
// opened again it reads the same state back (`restore`).
const sync = () => {
  const params = new URLSearchParams();
  for (const control of document.querySelectorAll('.controls input')) {
    if (control.name && control.checked !== control.defaultChecked) params.append(control.name, control.value);
  }
  for (const head of document.querySelectorAll('.sort')) {
    const cell = head.closest('th');
    const state = cell ? cell.getAttribute('aria-sort') : null;
    if (state === 'ascending' || state === 'descending') {
      params.append('sort', head.dataset.sort + (state === 'descending' ? '-descending' : ''));
    }
  }
  const query = params.toString();
  history.replaceState(null, '', location.pathname + (query ? '?' + query : ''));
};

// The state the page's URL carries, read back into the page before its feed arrives: a control the
// link names reads the opposite of its own default, and a head in the order the link names, the heads
// a link names none of left as the page carries them. The link names one head — the page stands
// sorted on one — so a URL carrying more takes the first and drops the rest, and no two heads are
// ever marked sorted by a link `sync()` did not write.
const restore = () => {
  const params = new URLSearchParams(location.search);
  for (const control of document.querySelectorAll('.controls input')) {
    if (control.name) control.checked = params.getAll(control.name).includes(control.value) ? !control.defaultChecked : control.defaultChecked;
  }
  const sort = params.get('sort');
  for (const head of document.querySelectorAll('.sort')) {
    const cell = head.closest('th');
    const state = sort === head.dataset.sort ? 'ascending' : sort === head.dataset.sort + '-descending' ? 'descending' : 'none';
    if (cell) cell.setAttribute('aria-sort', state);
  }
};

// Column heads: a head's three-press cycle — its first press sorts ascending, its second descending,
// its third returns the feed's own order and the table to no sorted head at all. A head's `data-sort`
// is the feed entry's own key its column sorts on. The sort state is the column head's own —
// `aria-sort` on the `<th>`, where a table's sort belongs, `none` standing for the unsorted table as
// headers attribute it — so the button is the label and the press, and the cell announces the order.
// The arrow marks the two orders a press sets; the third press leaves `none`, with no arrow, which is
// the same head the page opened on. A press writes the page's state to its URL, as a control's change
// does, and redraws the table.
for (const label of document.querySelectorAll('.sort')) {
  label.addEventListener('click', () => {
    const cell = label.closest('th');
    const key = label.dataset.sort;
    const order = sorted();
    const next = !order || order.key !== key ? { key, descending: false } : order.descending ? null : { key, descending: true };
    for (const other of document.querySelectorAll('.sort')) other.closest('th').setAttribute('aria-sort', 'none');
    if (next && cell) cell.setAttribute('aria-sort', next.descending ? 'descending' : 'ascending');
    sync();
    draw();
  });
}
for (const control of document.querySelectorAll('.controls input')) {
  control.addEventListener('change', () => {
    sync();
    draw();
  });
}
restore();

// The feed's failure names itself in the page, in the feed's own words, and is no session's absence:
// the no-records reading stands for a feed that answered with nothing to draw.
const notice = (error) => {
  const line = document.getElementById('notice');
  line.textContent = 'The traces feed could not be read: ' + String(error.message || error) + '.';
  line.hidden = false;
};

fetch(FEED, { cache: 'no-store' })
  .then((response) => {
    // A refused feed's body names the failure — the handler's `{"error": ...}` — and that text is the
    // notice's; a response carrying none speaks for its status alone.
    if (!response.ok) {
      return response.json().then(
        (answer) => { throw new Error(answer.error || 'HTTP ' + response.status); },
        () => { throw new Error('HTTP ' + response.status); },
      );
    }
    return response.json();
  })
  .then((feed) => {
    try {
      show(feed);
    } catch (error) {
      // The page's own defect, which is no feed's absence: it warns and leaves the rows as they stand
      // rather than reaching the catch below, whose notice speaks for a feed that could not be read.
      console.warn('the index could not draw the feed: ' + String(error));
    }
  })
  .catch((error) => {
    console.warn('the traces feed could not be read: ' + String(error));
    notice(error);
  });
})();
</script>
</body>
</html>
"""


def session_for(path: str, directory: Path | str) -> dict | None:
    """The session recorded at `/page/<session-id>`'s id, or nothing where the path names no page or
    no session: the page's own read, the records the render and the band's facts both draw from."""
    if not path.startswith(PAGE_PREFIX):
        return None
    sessions = read_sessions(directory)
    return next((session for session in sessions if session["id"] == path[len(PAGE_PREFIX) :]), None)


def page_for(
    session: dict,
    *,
    return_to: str | None,
    dispatcher: Dispatcher | None,
    episodes: dict[str, dict] | None = None,
) -> str:
    """A page of the profiler view as the dashboard serves it: the view's own text — the nav, the
    frame band with its legend, the decoration's script, the presentation layer linked — the band's
    per-page facts the dashboard's own lookup names, one legend on the page and the script once. The
    layer's carriage is the serve path's own fill (`served_page`), where the render inlined the
    layer's text. `episodes` is `session_data`'s: the child-end joins the page's calls take."""
    return served_page(_rendering(session, dispatcher=dispatcher, return_to=return_to, episodes=episodes))
