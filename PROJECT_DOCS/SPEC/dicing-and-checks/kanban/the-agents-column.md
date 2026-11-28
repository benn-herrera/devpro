# The agents column

The board's last column is the **agents column**, in both modes. It shows the project's running
dispatches: one card per dispatch of an agent that is working now.

A **running dispatch** is one the activity capture has recorded the start of and not the completion
of. Whether a dispatch runs is the capture's events' answer, read from the same records the
profiler view reads ([Shipped files](../../../../PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md#shipped-files)), never a measurement of time and never a poll of any
harness: the board starts no observation of its own. A change in the stores surfaces on the open
page as [live following](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md#live-following) follows any watched file.

A dispatch card shows the agent's name, the child's model where the capture's records name it, the
session that dispatched it, and a link to the dispatched work's page: one page per harness — the
child session's page under opencode, whose records name the child's session id, and the dispatching
session's page under claude, whose store holds the child's records. A running dispatch's color is a
function of the dispatch alone: its rank in the order the capture opened the dispatches of the
stores, closed ones included, counted against a fixed palette. The color is the same at every read
and stable while the dispatch runs, distinct among the concurrently running dispatches up to the
palette's size, and shared where more than the palette's size run at once.

A dispatch is **joined** where the active plan names it: the row of the package the dispatch works
under carries the dispatch's identifier as its dispatch note ([Plan Status Form](../../../../PROJECT_DOCS/SPEC/plan-status-form.md#plan-status-form)), and that package's
card carries a dot in the dispatch's color. A package several running dispatches work under carries
a dot for each. A dispatch no row names shows unjoined, and colors no dot; a note whose dispatch
runs no longer colors no dot.
