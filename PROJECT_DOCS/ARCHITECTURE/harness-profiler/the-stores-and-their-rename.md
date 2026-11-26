# The stores and their rename

Each harness's capture owns one store under the project's
`.devpro-temp/`: both readers — `tree`'s render, and the dashboard's profiler view, whose index and
session pages read the stores per request — read the stores the captures write, the directories named
exactly `.profiler-<harness>` for a harness name the profiler's own captures use (claude and opencode
today) — a dot name, so the stores group and sort at the top of the scratch tree. A directory of any
other shape beside a store is not a store and is not read. Both `devpro install` and
`devpro profiler init claude` rename the two old-pattern stores: `.devpro-temp/claude-profiler/` to `.profiler-claude` and
`.devpro-temp/opencode-profiler/` to `.profiler-opencode`, and the move is printed. A directory under
`.devpro-temp/` whose name only ends in `-profiler` is no store and is left alone. Where a store's new
name is already taken, the old one is left in place and named instead — the stores' contents are
never merged, and merging or deleting the old store is the operator's call. A second run touches
nothing. A capture writes `.profiler-*` while an old-pattern store still holds its traces, so `tree`
cannot read that store until the migration runs; a store the rename leaves standing stays unread until
the operator merges or deletes it.
