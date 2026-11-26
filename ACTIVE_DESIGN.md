# ACTIVE DESIGN

## Drafts

### Profiler child rows off by default

Having them on by default is not helpful. The code is also crufty.
It does not have tunable initial values for any of the controls. It has a hard default of
'checked' for the initial value of all checkboxes and only appends parameter values when a checkbox
value is false (again, hard value check)

### Detect a re-install from embedded devpro

Right now ./<harness-dir>.../devpro.sh install . fails because it detects the self-overwrite.
what it *should* do is reinstall everything but the embedded copy (just detect and skip with no
output to stdout or stderr mentioning it - re-install in place is a normal operation).
this allows for edits to ~/.config/devpro/devpro.toml to take effect without potentially changing
devpro's installed version by using the system copy.

### A background dispatch's tool call times the spawn, not the child's run

Under opencode 2.4.1, a backgrounded subagent dispatch is recorded — by the capture's
`execute.before`/`execute.after` pair and by the host's own `session_part` storage alike — as a
tool call completed in single-digit milliseconds. The window is the cost of firing the dispatch,
not the child's work: durations cluster at 17–21 ms regardless of how long the child then runs,
and the completed part's own `metadata` carries `"status": "running"` for the child session it
names. Measured 2026-11-25 over twelve background dispatches in one project: tool-call durations
of 2–21 ms against child-session spans of 0.2–10.9 minutes. The hook pair is not wrong about what
it measures — it brackets the tool's execution, and a background dispatch's execution is the
firing. The capture is what presents that window as the dispatch's duration, and that is the
defect.

The ticket is the capture watching the window itself: a background dispatch's call opens on the
launch acknowledgment `execute.after` already receives — the dispatch's intent — and on the child's
own opening events, `session.agent.selected` and `session.model.selected`, which carry the
actualized run: the agent actually running and the model actually selected, where the dispatch side
names only what was asked for. The records' `child_agent_type` reads null today for exactly this
reason. The call closes on the terminal `session.execution.*` event — `succeeded`, `failed`, or
`interrupted` — naming the child's session id. The parent's inbox delivery is not the marker: an
agent that purposefully or erroneously sends no work back still terminates, and termination is the
event's guarantee, delivery's is not. Foreground calls, which no child session carries, keep the
hook pair. Under the claude harness the same dispatch's Task-tool duration already covers the
subagent's run, so the fix is also what makes the two harnesses' records compare.

Note: the same session.execution event is needed in index.ts for the agent completed
      board-refresh reminder injection (the idle event currently used is probably wrong)

### A minimum-specificity rule for the process's records

The recurring failure: a record carries specificity beyond what its reader needs — a measured
second, a line number, a version number of the moment — the fact it restates moves, the record
rots out of agreement with the project, and every later reader pays to reconcile it, with the stale
specificity distracting indefinitely after. The rule the process should carry: a record states the
minimum specificity needed to convey the information that lets the work carry forward. A number,
path or name belongs in a record only where its reader needs it to act and nothing more durable
states it; where a measurement matters, the record names the probe that produced it and the
measurement lives with the probe, dated; specificity whose only reader is the moment that wrote it
does not get to keep living. Lands in the development skill's definition
(`devpro/definitions/skills/development.py`), so every project's install carries it, and applies to
the process's own artifacts: plans, designs, reviews, tickets, briefs.
