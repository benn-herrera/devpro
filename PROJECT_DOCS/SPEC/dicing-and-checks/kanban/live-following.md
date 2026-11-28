# Live following

A change to a watched file, to its content, creation or deletion, appears on the open page without
a reload, within about a second. The watched files are `ROADMAP.md`, each parked file and each
parked tree's `entry-point.md`, and the active design and the active plan, a diced one as every
`.md` file beneath its entry point's directory — and the activity capture's two store directories,
`.devpro-temp/.profiler-claude/` and `.devpro-temp/.profiler-opencode/`, watched as directories
rather than their record files one by one, so a record appended or a session file created changes
what the poll reads and surfaces the agents column.

The page's header holds a **connection indicator**, which says whether the server is answering.
When three consecutive attempts of the page to reach the server fail, the indicator says the server
has stopped and to restart `devpro dashboard` and open the URL it prints, and no drag starts. The page
keeps trying; a successful attempt restores the board's live state and drags.

The connection indicator carries `devpro v<version>`, `<version>` being what `devpro --version`
prints for the running server, as its hover text; its accessible label is what it says, whether the
server is answering. Nothing else on the page shows devpro's version.

**Stop.** Beside the connection indicator the page shows a stop button. Pressing it, with no
confirmation, asks the server to exit: the server answers, then ends the process as an interrupt
does (**kanban**, above). On that answer the indicator says the server has stopped and to restart
`devpro dashboard` and open the URL it prints, no drag starts, the page makes no further attempt to
reach the server, and keyboard focus moves to the page's heading.

A watched file that cannot be read as a file while the server runs is named on stderr as
`cannot read: <file>`, and the board keeps its last good state until the file reads again.
