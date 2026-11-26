# The opencode capture

## The capture and the hook surface

Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call (the `tool`,
`sessionID`, `status`, `input` and `result`/`error` the after-hook reports), and the idle hook appends
a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/.profiler-opencode/<session-id>.jsonl` store, `harness` `"opencode"`, which
`devpro profiler tree` and the dashboard's profiler view render beside the claude sessions', each
record read from its own `.profiler-*` store.

## Dispatched children

A `subagent` or `task` call also records the child
session it dispatched: the child's id is `result.sessionID` on 2.4.1, `output.sessionID` on 2.3.2 and
`metadata.sessionID` on 2.3.0, read in that order each under the host's own string guard, and it
fills the record's `child_agent_id` — where the index groups the child one level under its dispatcher,
the tree on the session's page drawing the dispatch as a context — and the dispatch links to
that child's page.

## The stores stay flat

The stores stay flat — the child's id reaches no capture as a parent key, the hierarchy
being what the parent's records state — and a dispatch that fails before creating a child, or whose
result reports no child session, records none. A capture written before it read 2.4.1's shape carries
the child's id only in its stored result text; *The repair* below fills it.

## What is not recorded, and what a failure does

The model's own `todowrite` notes are not recorded: they are not activity, so the store holds one
record per tool call that did something. A capture that fails raises nothing out of the hook.

## Init and doctor stay claude-facing

`init` and `doctor` stay claude-facing: opencode has no committed-hook concept. Opencode's install
copies the plugin's `profiler.ts` alone, no launcher and no hook entry beside it, and the store the
plugin writes is read by `devpro profiler tree` — the wrapper's own subcommand.

## The line's limits and the torn line

One line holds one record, and the limits that keep it so are `devpro/profiler/values.py`'s:
`NAME_LIMIT`, `ARGS_LIMIT` and `RESULT_LIMIT` clip a field's text as the Python capture clips it, and
`LINE_LIMIT` bounds the written line in bytes, `name` and `session` clipped at the root before
`result` and `args` gives way. A line a killed process left torn would fuse the next record onto it,
so an append finds the last newline in the file's tail and truncates to it, renaming the whole store
aside where the file holds no newline at all. The Python capture has no such repair: it appends as it
stands, and its reader skips the torn line.

## Tokens and the model

An opencode record carries no token counts, so the tree's token columns are blank for
its sessions; claude's counts and each claude call's `model` come from its own transcripts under
`~/.claude/projects/`, which is claude's data, not a source the install configures — the model is
that of the assistant message holding the call's tool use, the entry the capture reads the call's
context tokens from, and is recorded at capture alone. An opencode record's `model` names the model
call that issued the tool call, as `providerID/modelID`, the last one the session's `model.request`
hook reported when the record is written, and is recorded at capture alone: `null` where none has run
— a host whose plugin surface offers no such hook records none.

## The empty branch

An opencode record's `branch` is empty on its own account: the capture runs in the host's process,
and the hooks report no branch, so `tree --branch` selects no opencode session.
