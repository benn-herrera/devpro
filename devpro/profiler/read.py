"""The read boundary: the stores' sessions, the record joins, the dispatch hierarchy and the fan-out
detector, and the depth-2 chain `Depth` threads to the render.

Every read of a store is here; nothing in this module renders. `pages.py` renders the sessions these
functions return, and the dashboard's server calls `dispatches`, `review_fanouts` and `Depth` directly,
reading the stores once per request.
"""

import json
import math
import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import NamedTuple
from urllib.parse import quote

from .values import (
    NAME_LIMIT,
    TRACE_DIR,
    TRACE_STORES,
    Json,
    _epoch_ms,
    clip,
    mask,
    read_text,
)


def read_trace(file: Path) -> list[Json]:
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


IDLE = "experimental.idle"


def child_episodes(sessions: list[Json]) -> dict[tuple[str | None, str], Json]:
    """A child session id -> its latest idle with no background work running: where that session's run
    ended, keyed on the store's harness with the id so a join across stores rides on neither alone.

    The episode-end contract, as `the-opencode-capture` leaf states it and the join reads it. An
    opencode session idles each time an episode closes — the agent loop finished and nothing is
    queued — and a wake that follows its own background work, or a dispatcher's follow-up, opens
    another episode whose idle is later. An idle seen with background work listed is no episode's end,
    so it is not kept; the latest kept one ends the child, and the span the join reads runs from the
    dispatch to it — including, where the child opened background work of its own, the wait for it.
    The `background` field is the capture's own: claude stamps a bool and opencode a count, and both
    read as none held where falsy — `0`, `False` and a record naming neither alike."""
    episodes: dict[tuple[str | None, str], Json] = {}
    for session in sessions:
        for record in session["records"]:
            if record.get("event") == IDLE and record.get("session") and not record.get("background"):
                episodes[(record.get("harness"), str(record["session"]))] = record
    return episodes


def joined_session(session: Json, sessions: list[Json]) -> Json:
    """A session with each opencode dispatch row joined to its child's end: the child's agent, model
    and end read from the child's own store rather than the dispatch's acknowledgment, the fill
    `with_stop` once performed for the episode. `child_episodes` is built here, once, over every store
    `sessions` holds — the read boundary — so the map is computed at the read and threaded through no
    render signature, and its key carries the harness with the id so a cross-store join rides on
    neither alone. A dispatch whose child's end never came keeps the acknowledgment as it was written."""
    episodes = child_episodes(sessions)
    records = []
    for record in session["records"]:
        child = record.get("child_agent_id")
        episode = episodes.get((record.get("harness"), str(child)), None) if child else None
        if episode is not None:
            record = {
                **record,
                "child_agent_type": episode.get("agent_type") or record.get("child_agent_type"),
                "model": episode.get("model") or record.get("model"),
                "duration_ms": max(0, (_epoch_ms(episode.get("at")) or 0) - (_epoch_ms(record.get("at")) or 0)),
            }
        records.append(record)
    return {**session, "records": records}


# The hue a running dispatch is colored with, by its place in the palette. A hue names the site's own
# color (`board.css`'s `--c0`…`--c7`, `view.html`'s `hueColor`), so nothing restyles the board to draw
# one: the board and the profiler's sequence diagram wear the same palette.
DISPATCH_HUES = 8


@dataclass
class Dispatch:
    """A running dispatch, as the board's agents column draws it, and the identifier the active plan's
    dispatch note names it by."""

    id: str  # the dispatch's identifier: the child session's id under opencode, `child_agent_id`'s under claude
    name: str | None  # the agent it runs, as the opening record names it
    model: str | None  # the model it runs, as its records name it
    session: str  # the session that dispatched it
    page: str  # the page the card links: the child's under opencode, the dispatching session's under claude
    at: str  # the opening record's `at`
    hue: int  # its color: its open-order rank over the store's dispatch history, modulo the palette


def running_dispatches(directory: Path | str) -> list[Dispatch]:
    """The running dispatches the stores under directory hold, in the order they opened, each with its
    color.

    The derivation reads records alone — no subprocess, no clock, and a change in the stores reaches it
    as `read_sessions` reads them again. Under opencode the dispatch is the acknowledgment `execute.after`
    wrote, its `child_agent_id` the child's session; the child's idle with an empty `background`
    (`child_episodes`' end contract) closes it. Under claude the `Agent` tool call whose `child_agent_id`
    names the child opens the dispatch and the `SubagentStop` event record closes it, its own `agent_id`
    the child's id the opening call named — the key the session page's stop join reads — so each stop ends
    the dispatch it names, and two dispatches of one session close at their own stops. A dispatch with no
    closing record is running.

    The color is a function of the dispatch alone: its rank in the store's full dispatch history —
    every dispatch the records open, closed ones included — ordered by the opening record's `at`,
    modulo the palette, so it is the same color at every read, holds while the dispatch runs, and is
    distinct among the concurrently running up to the palette's size. The history's order by `at`
    colors a batch of records written in one moment in that rather than its store's order, and two
    records of one moment keep the read's order among the ties. No map is carried across reads and
    nothing is pruned. A store that cannot be read raises out of this, as it does from
    `read_sessions`."""
    sessions = read_sessions(directory)
    history = _opened(sessions)
    history.sort(key=lambda dispatch: (_epoch_ms(dispatch.at) or 0))
    hues = {dispatch.id: rank % DISPATCH_HUES + 1 for rank, dispatch in enumerate(history)}
    ended = _ended(sessions)
    return [replace(dispatch, hue=hues[dispatch.id]) for dispatch in history if dispatch.id not in ended]


def _opened(sessions: list[Json]) -> list[Dispatch]:
    """Every dispatch the sessions' records open, in the order their opening records stand in the read."""
    opened: list[Dispatch] = []
    for session in sessions:
        for record in session["records"]:
            dispatch = _dispatched(record)
            if dispatch is not None:
                opened.append(dispatch)
    return opened


def _dispatched(record: Json) -> Dispatch | None:
    """The dispatch a record opens, as it stands in the store, or nothing where it opens none."""
    child = record.get("child_agent_id")
    if not child or not isinstance(record.get("at"), str):
        return None
    if record.get("harness") == "opencode":
        page = quote(str(child))
    elif record.get("harness") == "claude" and record.get("tool") == "Agent":
        page = quote(str(record.get("session")))
    else:
        return None
    return Dispatch(
        id=str(child),
        name=record.get("name"),
        model=record.get("model"),
        session=str(record.get("session")),
        page=page,
        at=record["at"],
        hue=0,
    )


def _ended(sessions: list[Json]) -> set[str]:
    """The ids of the dispatches a closing record ends: opencode's child idled with an empty
    `background`, and claude's `SubagentStop`, its `agent_id` the child's id — the opening `Agent`
    call's `child_agent_id`, the key the session page's stop join reads — so each stop ends the dispatch it names."""
    ended = {str(record["session"]) for record in child_episodes(sessions).values()}
    for session in sessions:
        for record in session["records"]:
            if record.get("harness") == "claude" and record.get("event") == "SubagentStop" and record.get("agent_id"):
                ended.add(str(record["agent_id"]))
    return ended


def dispatch_notes(notes: list[str], running: list[Dispatch]) -> list[str]:
    """The colors, in the running set's order, of the running dispatches one row's State-cell note names.

    A note names the dispatches its row is under by the identifiers it carries, read as the plan's
    reader reads them: the note split on whitespace, commas and semicolons into tokens, each compared
    exactly to a dispatch's identifier, so an identifier inside a longer word names nothing."""
    named = {token for note in notes for token in _NOTE_TOKENS.split(note) if token}
    return [str(dispatch.hue) for dispatch in running if dispatch.id in named]


_NOTE_TOKENS = re.compile(r"[\s,;]+")


TOOL_WORDS = {"Skill": "skill", "Agent": "agent"}

# The prefix an agent set's definitions carry their names under, dropped where a page renders one: the
# stored records and the feed keep the name as recorded. It is the install's one name,
# `components.NAME`; this module spells it rather than importing a module the capture path may not pay
# for, and the lane test pins the spelling to `components.NAME`.
AGENT_PREFIX = "devpro-"


def rendered_name(name: str | None, tool: str | None) -> str | None:
    """An Agent call's name as a page renders it: the set's prefix dropped. Every other call's name is
    as recorded — a Bash command's `devpro-check-plan` is that command, not the set's prefix."""
    return name.removeprefix(AGENT_PREFIX) if name and tool == "Agent" else name


def bare_agent_name(record: Json) -> str | None:
    """An opencode agent dispatch's agent by its bare name — the name the detector compares against
    `REVIEW_SEAT`: the set's prefix dropped, as `rendered_name` drops it at the render. The host may
    report the name either way; the record's `harness` is the tool here, an opencode agent call's
    `name` being the agent it loaded (`profiler.ts`'s `callRecord`)."""
    name = record.get("name")
    return rendered_name(str(name), "Agent") if name else None


def call_label(tool: str | None, name: str | None) -> str:
    """The name leads and the kind follows: `review (skill)`, `counter (agent)`, `wc -l a (Bash)`."""
    word = TOOL_WORDS.get(tool or "", tool or "")
    rendered = rendered_name(name, tool)
    return f"{rendered} ({word})" if rendered else word


# The review seat the fan-out detector names: an agent set's post-plan reviewer, the development
# skill's own definition of it. `bare_agent_name` reads a dispatch record's `name` — the agent an
# opencode agent call loaded (`profiler.ts`'s `callRecord`) — down to the bare name this holds.
REVIEW_SEAT = "prompt-engineer"


class Dispatcher(NamedTuple):
    """A session's dispatcher, as the band and the page's root context read it: the session that
    dispatched this one, the call that did, the tool it ran as, and the hue that call's context wears
    on its dispatcher's page."""

    session: str
    name: str
    tool: str | None
    hue: int


class Depth(NamedTuple):
    """What a page's depth-2 chain reads, built once at the read boundary: the sessions
    `read_sessions` read, `dispatches`' map of their hierarchy, and `review_fanouts`' verdicts.
    Threading them as one value keeps the render signatures to the session and its dispatcher, and
    the reads stay the caller's — the chain rebuilds no store path and parses no store the read did
    not, nothing being rebuilt per render."""

    sessions: list[Json]
    dispatched: dict[str, tuple[str, str, str | None]]
    verdicts: dict[str, bool]


def session_of(path: Path) -> Json:
    """One trace as `list_sessions` shapes it: its records and its first and last moments.

    It reads the store path the listing found, its id the file's name, so nothing derives a store's
    path from a session id: a page's dispatcher and its depth-2 chains read the sessions a read
    returned."""
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


def list_sessions(directory: Path | str) -> list[Json]:
    """Every session trace under `directory`, with its records and its first and last moments.

    Every store under `.devpro-temp/` is read — the directories named exactly for a harness the
    captures write, `values.TRACE_STORES` — so both harnesses' sessions reach one tree, and a session
    id is unique across them."""
    traces: list[Path] = []
    stores = Path(directory) / TRACE_DIR.parent
    for store in sorted(stores / name for name in TRACE_STORES if (stores / name).is_dir()):
        traces.extend(path for path in store.iterdir() if path.name.endswith(".jsonl"))
    return [session for session in (session_of(path) for path in traces) if session["records"]]


def store_directories(directory: Path | str) -> list[Path]:
    """The stores under the project's scratch directory — each named exactly for a harness the captures
    write — in the order they are read."""
    stores = Path(directory) / TRACE_DIR.parent
    return sorted(stores / name for name in TRACE_STORES if (stores / name).is_dir())


def read_sessions(directory: Path | str) -> list[Json]:
    """`list_sessions`'s sessions, the index's and the pages' one read: each store the exact names
    find, walked a session at a time so a store's own listing is the one read that fails where it
    does. A store that cannot be read raises out of it."""
    sessions: list[Json] = []
    for store in store_directories(directory):
        traces = [path for path in store.iterdir() if path.name.endswith(".jsonl")]
        sessions.extend(session_of(path) for path in traces)
    return [session for session in sessions if session["records"]]


def session_harness(session: Json) -> str:
    """The harness's name, as the session's own records carry it, masked and clipped like any field."""
    harness = next((record.get("harness") for record in session["records"] if record.get("harness")), "")
    return clip(mask(str(harness)), NAME_LIMIT)


def dispatches(sessions: list[Json]) -> dict[str, tuple[str, str, str | None]]:
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
            child = dispatch_child(record)
            if child is not None:
                found.setdefault(child, (session["id"], str(record.get("name") or ""), record.get("tool")))
    return found


def dispatch_child(record: Json) -> str | None:
    """The session a record dispatched, where it is one `dispatches` makes a child of: an opencode
    record naming a session, and never the session naming itself. A claude record's
    `child_agent_id` is an agent id."""
    child = record.get("child_agent_id")
    if record.get("harness") != "opencode" or not child:
        return None
    return None if str(child) == record.get("session") else str(child)


def review_fanouts(sessions: list[Json], dispatched: dict[str, tuple[str, str, str | None]]) -> dict[str, bool]:
    """session id -> whether the fan-out detector marks it unreviewed, for every dispatched session
    that dispatched agents of its own. `dispatched` is `dispatches`' map, the caller's one read of
    the stores' hierarchy — the page and the feed each hold it already, so the detector derives no
    second. Its selection is that map's, so a claude session is in no answer: it names no session,
    and its subagents stand on its page already.

    A dispatched session whose records dispatch further agents is a fan-out, and it is unreviewed
    where the records standing at or before its first dispatch name no dispatch of the review seat
    (`REVIEW_SEAT`). The name read is the record's `name`, the set's prefix dropped where it carries
    one (`bare_agent_name`): on an opencode agent call it is the agent the call loaded,
    `child_agent_id` the context it opened. A fan-out with a review, and a dispatched session that
    fans out nothing, are left out — their rows carry no mark."""
    verdicts: dict[str, bool] = {}
    for session in sessions:
        if session["id"] not in dispatched:
            continue
        records = session["records"]
        first = next((index for index, record in enumerate(records) if dispatch_child(record) is not None), None)
        if first is not None:
            reviewed = any(bare_agent_name(record) == REVIEW_SEAT for record in records[: first + 1])
            verdicts[session["id"]] = not reviewed
    return verdicts


def child_dispatches(records: list[Json], page_prefix: str) -> list[Json]:
    """The agents a dispatched session dispatched of its own, read from its records in the sessions
    `read_sessions` already read — one level deeper and no deeper.

    Each is the call that dispatched it: its name and tool, and the child session's page where its
    record names one, at `page_prefix` — the serve path's own, which the read takes rather than
    spells. A record naming a child and no session — claude's — is no agent here, its calls drawn as
    contexts on the session's page already. The stored record, for an opencode call, carries
    `agent_id: null` and the agent in `name`."""
    return [
        {"name": record.get("name"), "tool": record.get("tool"), "childPage": _child_page(record, page_prefix)}
        for record in records
        if dispatch_child(record) is not None
    ]


def _child_page(record: Json, page_prefix: str) -> str | None:
    """A record's child as a link to its page, where `dispatch_child` names a session — an opencode
    record's, never claude's agent id."""
    return page_prefix + quote(str(record["child_agent_id"])) if dispatch_child(record) is not None else None


def depth_children(depth: Depth, session: Json, page_prefix: str) -> list[Json]:
    """A session's children as its page draws them beneath its dispatches: each child's own
    dispatched agents, read from the child's records `depth`'s sessions hold. `depth` is the read
    boundary's one build of the sessions, the stores' hierarchy and the verdicts; a child's verdict is
    the row's own (`session_data`'s `unreviewed`), never the child's entry — the mark stands beside the
    dispatch that opened the fan-out.

    Every child the session dispatched is here, a child of no agents carrying none; the agents are
    one level deeper and no deeper, the child's own records and never its children's. A dispatch
    whose child the read holds no session for is absent from the draw: the store a child's id names
    is never guessed from the id."""
    sessions = {session["id"]: session["records"] for session in depth.sessions}
    return [
        {
            "id": child,
            "name": name,
            "tool": tool,
            "agents": child_dispatches(sessions.get(child, []), page_prefix),
        }
        for child, (parent, name, tool) in sorted(depth.dispatched.items())
        if parent == session["id"]
    ]


def dispatcher_of(
    session: str, sessions: list[Json], contexts_of: Callable[..., tuple[list[Json], list[Json]]]
) -> Dispatcher | None:
    """The session that dispatched `session`, the call that did, the tool it ran as and the hue that
    call opened its context in — named by the stores' other sessions. The band's per-page fact and
    the page's root context both read it: the one lookup whoever fills either runs, so the dump's
    page and the served page name the same dispatcher, and the child's root wears the color the
    dispatcher's own page draws that context in.

    The child's records name no parent, so the hue is read off the dispatcher's records: they are the
    ones `contexts_of` draws the dispatcher's page from, so the child's record is the context whose id
    is the child's session id. That page's root hue is the dispatcher's own, read from the session
    that dispatched it up the chain — 0 where nothing did, and 0 at the session where the walk meets
    one it has already visited. Nothing is written at capture: the chain is walked at each read.

    `contexts_of` is the page's derivation of that page's contexts, which the read does not build: it
    is the caller's, so `pages` — which renders the dispatcher's page — passes it and the read stays
    below the render."""
    found = dispatches([x for x in sessions if x["id"] != session]).get(session)
    if not found:
        return None
    parent, name, tool = found
    root_hue, upstream, visited = 0, parent, {session}
    while upstream not in visited:
        visited.add(upstream)
        up = dispatcher_of(upstream, sessions, contexts_of)
        if up is None:
            break
        root_hue, upstream = up.hue, up.session
    contexts, _ = contexts_of(next(x["records"] for x in sessions if x["id"] == parent), root_hue=root_hue)
    return Dispatcher(parent, name, tool, next(context["hue"] for context in contexts if context["id"] == session))
