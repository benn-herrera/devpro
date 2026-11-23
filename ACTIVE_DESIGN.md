# Profiler page fidelity and the absorbed packages' shape

The dashboard's profiler view tells the truth about its data: every moment renders in the reader's
clock, in one notation, with the date stated once; the index filters its rows and sorts its
columns; a failed feed names itself; and an opencode session draws the children it dispatched as a
claude session does. The check code loses its copy-paste, and the dicing package sits at one level
like every other devpro package. Consumers of the dashboard get a view they can read and drive;
agents and maintainers get a codebase without pattern breaks or duplicated bodies.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The
summary text is not to be consistency checked. The design is authoritative.

## ARCHITECTURE delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```
The index's page file is static — no row is in its text — and its script fetches the
records' feed the server answers at `/api/traces`, one JSON entry per session with the columns
above, the stores the glob finds but cannot read among them as unreadable, and renders the rows
client-side — the board's pattern, the payload consumed client-side.
```

**Becomes:**

```
The index's page file is static — no row is in its text — and its script fetches the
records' feed the server answers at `/api/traces`, one JSON entry per session with the columns
above, the stores the glob finds but cannot read among them as unreadable, and renders the rows
client-side — the board's pattern, the payload consumed client-side. The index carries simple
controls — child-record rows on and off, claude and opencode on and off separately, and column
heads sorting on the dispatched-agent count, the record count, the time and the span — and a
failed feed names itself: an in-page notice naming the feed's failure, distinct from the
no-records state a zero-record store renders.
```

**As it stands:**

```
The moments are the raw UTC where no script runs and the reader's local
time where the page's decoration script does, the raw string kept in the cell's title, and the span
is its own column.
```

**Becomes:**

```
The moments are the raw UTC where no script runs; with it, every moment the pages and their
headers show — the moments cells, the index's first-to-last line, the session page's header stamp —
reads in the reader's local time, 24-hour, one notation, the machine form only in the `<time>`
elements' `datetime` attributes and the raw UTC in the titles. A first-to-last whose ends share the
reader's day reads as two times with no date; one crossing midnight reads with the date on its
first end alone and the finish end time only, the next day's being obvious. The span is its own
column.
```

**As it stands:**

```
A `subagent` or `task` call also records the child
session it dispatched, the host's `result.metadata.sessionID` read under the host's own string
guard: that id fills the record's `child_agent_id`, where the index groups the child one level
under its dispatcher — the tree, on the session's page, drawing the dispatch as a context — and the
dispatch links to the child's page. The stores stay flat — the child's id reaches
no capture as a parent key, the hierarchy being what the parent's records state — and a dispatch
whose result carries no metadata records no child.
```

**Becomes:**

```
A `subagent` or `task` call also records the child session it dispatched, the child's session id
read from the host's result where the host reports it — opencode 2.3.2's `result.output.sessionID`
is that place: that id fills the record's `child_agent_id`, where the index groups the child one
level under its dispatcher — the tree, on the session's page, drawing the dispatch as a context —
and the dispatch links to the child's page. The stores stay flat — the child's id reaches no
capture as a parent key, the hierarchy being what the parent's records state — and a dispatch that
fails before creating a child, or whose result reports no child session, records none.
```

### [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

**As it stands:**

```
The package's modules depend one way: `kanban/` imports `doccheck/` and `dicing.dicerlib`,
`doccheck/` imports `dicing.dicerlib`, `profiler/` reads `kanban/`'s stylesheet as package data,
`dashboard/` imports the panels it serves, and none of them depends on a module that depends on it.
```

**Becomes:**

```
The package's modules depend one way: `kanban/` imports `doccheck/` and `dicing`'s modules,
`doccheck/` imports `dicing`'s, `profiler/` reads `kanban/`'s stylesheet as package data,
`dashboard/` imports the panels it serves, and none of them depends on a module that depends on it.
```

## Code delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

`profiler.ts`'s `childSessionOf` reads a dispatch's child session from `result.metadata.sessionID`
where the host reports it at `result.output.sessionID`, and every live dispatch records no child:
the read becomes the one the host makes — `result.output.sessionID`, the string guard standing,
and no child where the result reports none. The capture runner's fixture pins the host's observed
dispatch result shape, so the run whose read it drives fails on the old reading. [Harness
profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md), as the ARCHITECTURE delta amends
it, stays true.

### [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

Every module of `dicerlib/` moves up to `dicing/`, and every import that named
`dicing.dicerlib` names `dicing`'s own modules; nothing of the old name remains. [Repo
Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md), as the ARCHITECTURE delta amends its dependency
paragraph, stays true.

### [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

`doccheck/plancheck.py`'s `check_plan`, `check_design` and `check_roadmap` carry the same body
three times over beside the `_check` driver that is that body, and `_plan_report` and
`_roadmap_report` are the same function but for the reader they call: the three verbs become calls
to the one `_check`, each with its document type's reader, and the two report builders become one
taking both. `check-roadmap` appears as `doccheck/cli.py`'s `CHECK_ROADMAP` and
`devpro/definitions/skills/development.py`'s `CHECK_ROADMAP_COMMAND` — the first the check verbs'
argparse surface, the second the skills' prose. Leave both; do not import one from the other.
[Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md) stays true: `plancheck.py` the check
verbs' implementation, `cli.py` the `check-plan`, `check-design` and `check-roadmap` verbs'
argparse and dispatch.
