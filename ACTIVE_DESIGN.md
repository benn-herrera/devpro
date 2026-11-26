# Profiler dispatch timing, install re-entry, and the index page's defaults

For the operator reading the profiler, a subagent dispatch's record comes to carry the run the
child made — its span, the agent that ran and the model it ran on — rather than the cost of firing
the dispatch; and the sessions index opens with child rows off, every control's default stated in
the page, so the first view is the dispatches. For the operator maintaining an installed project,
an install run from the installation's own copy re-renders the set in place — a settings or option
change takes effect without changing the installed devpro version — passing over only the copy it
runs from. For every project the process ships, its durable records state no more specificity than
their reader needs; that fourth change is process, not a contract delta, and the plan carries it.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```
The `devpro` command on `PATH` never hands off to an installation's copy, and only an
install replaces the copy. An install run from an installation's own copy, into the installation
holding that copy, is refused with nothing written, its refusal naming the `devpro` command on
`PATH` as the one that installs.
```

**Becomes:**

```
The `devpro` command on `PATH` never hands off to an installation's copy, and only an
install replaces the copy. An install run from an installation's own copy, into the installation
holding that copy, installs: it passes over two things only — the devpro package under
`tools/devpro/` and the wrapper `tools/devpro.sh` that runs it — writing nothing at either and
reporting nothing about the pass-over, and installs everything else, each write under the overwrite
rules Write safety states.
```

*(The pair is paragraph-internal: the target's paragraph continues past the replaced run, and that
text stands.)*

## ARCHITECTURE delta

### [The index](PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md#the-index)

**As it stands:**

```
The
index carries simple controls — child-record
rows on and off, claude and opencode on and off separately, and column heads sorting on the
dispatched-agent count, the record count, the time and the span — and a failed feed names itself in
an in-page notice, distinct from the no-records state a zero-record store renders. The controls' state
and the sort in force live in the index page's URL, which the reader can copy, so leaving the view
and returning restores it.
```

**Becomes:**

```
The
index carries simple controls — child-record
rows on and off, claude and opencode on and off separately, and column heads sorting on the
dispatched-agent count, the record count, the time and the span — and a failed feed names itself in
an in-page notice, distinct from the no-records state a zero-record store renders. Child-record rows
are off by default, and the URL carries each control's state as its deviation from that control's
default — an untouched page's URL carries no query — so the controls' state and the sort in force
live in the index page's URL, which the reader can copy, and leaving the view and returning restores
it.
```

### [The capture and the hook surface](PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-opencode-capture.md#the-capture-and-the-hook-surface)

**As it stands:**

```
Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call (the `tool`,
`sessionID`, `status`, `input` and `result`/`error` the after-hook reports), and the idle hook appends
a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/.profiler-opencode/<session-id>.jsonl` store, `harness` `"opencode"`, which
`devpro profiler tree` and the dashboard's profiler view render beside the claude sessions', each
record read from its own `.profiler-*` store.
```

**Becomes:**

```
Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call that runs no child
(the `tool`, `sessionID`, `status`, `input` and `result`/`error` the after-hook reports), and the idle
hook appends a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/.profiler-opencode/<session-id>.jsonl` store, `harness` `"opencode"`, which
`devpro profiler tree` and the dashboard's profiler view render beside the claude sessions', each
record read from its own `.profiler-*` store. A call that dispatches a child — a `subagent` or
`task` call, which from 2.3.0 returns at once — is timed by the child's own events (Dispatched
children), not by the pair.
```

### [Dispatched children](PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-opencode-capture.md#dispatched-children)

**As it stands:**

```
A `subagent` or `task` call also records the child
session it dispatched: the child's id is `result.sessionID` on 2.4.1, `output.sessionID` on 2.3.2 and
`metadata.sessionID` on 2.3.0, read in that order each under the host's own string guard, and it
fills the record's `child_agent_id` — where the index groups the child one level under its dispatcher,
the tree on the session's page drawing the dispatch as a context — and the dispatch links to
that child's page.
```

**Becomes:**

```
A `subagent` or `task` call also records the child
session it dispatched: the child's id is `result.sessionID` on 2.4.1, `output.sessionID` on 2.3.2 and
`metadata.sessionID` on 2.3.0, read in that order each under the host's own string guard, and it
fills the record's `child_agent_id` — where the index groups the child one level under its dispatcher,
the tree on the session's page drawing the dispatch as a context — and the dispatch links to
that child's page. The dispatch record is written at the call's return, the launch acknowledgment:
its `at` is the dispatch moment, and its duration the window the acknowledgment's `execute.after`
observed — the cost of firing the dispatch. The child's own events then stand beside it, each
appended as its own record the moment its event reports, the dispatch record never rewritten, and
the render joins each to the dispatch at read, keyed by the session id both name — the join the
claude records' stops already take. What each event's record carries, and what it fills in the
dispatch record at the join:

| the child's event | its record carries | it fills in the dispatch record |
| --- | --- | --- |
| `session.agent.selected` | `agent_type`, the agent the child actually ran | `child_agent_type` — `null` today wherever only the acknowledgment was reported |
| `session.model.selected` | `model`, the model the child actually ran | `model` |
| `session.execution.succeeded`, `session.execution.failed` or `session.execution.interrupted` — the event name itself carries which | `at`, the child's end | the duration: until this event the row reads the firing cost, and the render then replaces it with the span from the dispatch's `at` to the event's |

Each event record is an event and no tool, its `session` the child's id, appended to the store that
id names — the child's own `.devpro-temp/.profiler-opencode/<child-session-id>.jsonl`, which the
render reads beside the dispatch's. Where the host reports none of the child's events, or a child's
terminal event never comes, the record stays as the acknowledgment wrote it.
```

### [Tokens and the model](PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-opencode-capture.md#tokens-and-the-model)

**As it stands:**

```
An opencode record carries no token counts, so the tree's token columns are blank for
its sessions; claude's counts and each claude call's `model` come from its own transcripts under
`~/.claude/projects/`, which is claude's data, not a source the install configures — the model is
that of the assistant message holding the call's tool use, the entry the capture reads the call's
context tokens from, and is recorded at capture alone. An opencode record's `model` names the model
call that issued the tool call, as `providerID/modelID`, the last one the session's `model.request`
hook reported when the record is written, and is recorded at capture alone: `null` where none has run
— a host whose plugin surface offers no such hook records none.
```

**Becomes:**

```
An opencode record carries no token counts, so the tree's token columns are blank for
its sessions; claude's counts and each claude call's `model` come from its own transcripts under
`~/.claude/projects/`, which is claude's data, not a source the install configures — the model is
that of the assistant message holding the call's tool use, the entry the capture reads the call's
context tokens from, and is recorded at capture alone. An opencode record's `model` names the model
call that issued the tool call, as `providerID/modelID`, the last one the session's `model.request`
hook reported when the record is written, and is recorded at capture alone: `null` where none has run
— a host whose plugin surface offers no such hook records none. A dispatch record's `model` is the
child's own instead, filled at the join from the child's `session.model.selected` event's record,
where the child reported one.
```

### [Opencode entry](PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md)

**As it stands:**

```
`devpro/harnesses/resources/opencode/index.ts` is opencode's plugin entry (SPEC.md, Deployed
Surfaces, Shipped files). It is written for opencode (floor 2.3.0), and its setup registers `ctx.tool.hook("execute.after")` filtered to `subagent` and
`ctx.session.hook("experimental.idle")` for a session whose `parentID` is set, injecting
`ctx.session.synthetic` into the parent session at agent dispatch and agent completion, gated by
the active plan (`ACTIVE_PLAN.md` or the diced `ACTIVE_PLAN/` tree; SPEC, Shipped files).
```

**Becomes:**

```
`devpro/harnesses/resources/opencode/index.ts` is opencode's plugin entry (SPEC.md, Deployed
Surfaces, Shipped files). It is written for opencode (floor 2.3.0), and its setup registers `ctx.tool.hook("execute.after")` filtered to `subagent` and
`ctx.session.hook` for the terminal `session.execution.succeeded`, `session.execution.failed` and
`session.execution.interrupted` events, each naming the child session whose run ended, injecting
`ctx.session.synthetic` into the parent session at agent dispatch and agent completion, gated by
the active plan (`ACTIVE_PLAN.md` or the diced `ACTIVE_PLAN/` tree; SPEC, Shipped files).
```

*(The pair is paragraph-internal: the target's paragraph continues past the replaced run, and that
text stands.)*

**As it stands:**

```
The floor is a behavioral one, not an API one: every API the entry uses exists at 2.2.6, but there
the `subagent` tool defaults to the foreground, so `execute.after` fires at the child's completion,
behind the idle hook — a parent gets two completion nudges and none at the dispatch. From 2.3.0 the
call returns at once and the child runs in the background, which makes the call's return the
dispatch moment.
```

**Becomes:**

```
The floor is a behavioral one, not an API one: every API the entry uses exists at 2.2.6, but there
the `subagent` tool defaults to the foreground, so `execute.after` fires at the child's completion.
From 2.3.0 the call returns at once and the child runs in the background, which makes the call's
return the dispatch moment. The terminal `session.execution.*` events the completion reminder reads
are observed shipped behavior of the 2.4 line, as the capture's child events are: a host whose
surface offers none fails that registration, and the completion reminder is what it loses.
```

**As it stands:**

```
- The reminder's surface is `ctx.location.project.directory`, the checkout root — the opened
  directory, `ctx.location.directory`, need not be it — read for the gate; `ctx.tool.hook` and
  `ctx.session.hook` for its two events, `ctx.session.get` for a session's `parentID`, and
  `ctx.session.synthetic` for the injection.
```

**Becomes:**

```
- The reminder's surface is `ctx.location.project.directory`, the checkout root — the opened
  directory, `ctx.location.directory`, need not be it — read for the gate; `ctx.tool.hook` and
  `ctx.session.hook` for its two events, `ctx.session.get` for the parent of the session a
  terminal event names, and `ctx.session.synthetic` for the injection.
```

**As it stands:**

```
- *Reminder.* Two hooks, registered on every install and gated when they fire, so a project holding
  no gate path pays nothing: a `subagent` call that completed is the dispatch moment, and a session
  going idle with an empty `background` list is a subagent's completion, whose parent — the
  `parentID` `ctx.session.get` reports — is the one injected into. An idle session that still holds
  running work reports nothing: the wake that follows that work fires the hook again, and that idle
  is the completion. Each injection is one `ctx.session.synthetic` message delivered `steer`, so it
  belongs to the execution that just ran, and its text is the sentence claude's reminder script
  emits, byte for byte: `Reminder: keep the ACTIVE_PLAN state table up to date.`
```

**Becomes:**

```
- *Reminder.* Two hooks, registered on every install and gated when they fire, so a project holding
  no gate path pays nothing: a `subagent` call that completed is the dispatch moment, and a child
  session's terminal `session.execution.*` event is its completion — the child the event names, and
  the parent `ctx.session.get` reports for it, the one injected into; a child's run ends once, so
  its completion reminder is one. The `experimental.idle` registration the terminal events replace
  is removed. Each injection is one `ctx.session.synthetic` message delivered `steer`, so it
  belongs to the execution that just ran, and its text is the sentence claude's reminder script
  emits, byte for byte: `Reminder: keep the ACTIVE_PLAN state table up to date.`
```
