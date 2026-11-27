# The agents column

The board panel's payload carries `agents`, the running dispatches the agents column shows
(SPEC.md, Dicing and Checks, Kanban, the agents column), derived from the activity capture's
stores, `.devpro-temp/.profiler-claude/` and `.devpro-temp/.profiler-opencode/`, the directories
[the stores' rename](../../../PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-stores-and-their-rename.md#the-stores-and-their-rename) fixed. The derivation reads records only; it runs no subprocess and watches no clock.

A **dispatch** is identified by the id the capture records for the dispatched child: the child
session's id under opencode, the child agent's id — `child_agent_id` — under claude. Under opencode
the dispatch record — the
acknowledgment `execute.after` observed ([the opencode capture](../../../PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-opencode-capture.md#the-opencode-capture)) — opens it, and the child's idle record with an empty
`background` closes it. Under claude the `Agent` tool-call record whose `child_agent_id` names the
child opens it, and the `SubagentStop` event record closes it, matched by the parent session, the
agent type and the order of the records, the ids the claude capture holds: two concurrent
dispatches of one agent type in one session close in the order they opened. A dispatch whose
closing record is absent is running; one with both is done.

The panel derives the running set over the records the stores hold, orders it by the opening
record's `at`, and assigns each dispatch its color from a fixed palette in that order, stable while
the dispatch runs. A dispatch card's fields are the records': the agent's name, the model it runs,
the dispatching session, and the dispatch's identifier, which the card links to `/page/<id>` where
that identifier is a session id — under claude the card links the dispatching session's page, the
store holding the child's records.

The board's mode is the status table's: planning while no row of the active plan's status table is
`in progress` or `landed`, execution otherwise — the plan the board already reads, read once more;
a project with no active plan is in planning mode. The watched set gains the stores — the two store
directories watched as directories, not their records one by one, so the poll's cost does not grow
with the sessions' count — and the panel's poll thread, the one loop the board panel already runs
([the board panel](../../../PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md#the-board-panel)), sees a new record within its poll interval, and the long poll wakes the
open pages. A store that cannot be read is named on stderr as [live following](../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md#live-following) names an
unreadable watched file, and the board keeps its last good state until it reads again.
