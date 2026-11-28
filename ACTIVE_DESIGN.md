# The board's running agents, the lifetime scale's durability, and the tuning data's new home

The kanban board shows the agents working now: an agents column carrying a card per running
dispatch, and a colored dot on each package card a running dispatch works under, both driven by the
activity capture's events alone, so the operator reads who is working on what from the board
itself, a card's link carrying them to the detail. The package lifetime scale names durability — shipped reaches a user, persistent is tracked
and does not, transient never commits — so the process a package owes is priced by what the package
will cost to keep. The rendered definitions carry no tuning data; the set records it once per
install in a tuning table under the install directory, beside the rendered definitions, and the
coordinator reads what it
needs per agent from the dispatch fields it already reads. For the operator watching the board, the
sessions dispatching under the process, and the agents reading the rendered definitions.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Columns and cards](PROJECT_DOCS/SPEC/dicing-and-checks/kanban/columns-and-cards.md#columns-and-cards)

**As it stands:**

```
The board has six columns, left to right: Roadmap, Design, Drafted, Dispatchable, In progress,
Landed. Drafted through Landed are the **plan columns**, which are read-only
([the plan columns are read-only](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-plan-columns-are-read-only.md#the-plan-columns-are-read-only)).
```

**Becomes:**

```
The board's columns depend on its mode. In **planning** mode, left to right: Roadmap, Design,
Drafted, Dispatchable, Agents. In **execution** mode: Design, Drafted, Dispatchable, In progress,
Landed, Agents. Drafted through Landed are the **plan columns**, which are read-only
([the plan columns are read-only](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-plan-columns-are-read-only.md#the-plan-columns-are-read-only)).
The board is in planning mode while the active plan's status table holds no `in progress` and no
`landed` row, and in execution mode otherwise; a project with no active plan is in planning mode.
The last column in both modes is the agents column
([the agents column](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-agents-column.md#the-agents-column)).
```

**As it stands:**

```
| Dispatchable, In progress, Landed | as the Drafted row, for their state words |
```

**Becomes:**

```
| Dispatchable, In progress, Landed | as the Drafted row, for their state words |
| Agents | one card per running dispatch (the agents column) |
```

**As it stands:**

```
**Work package cards.** A card shows the package's ID, its title, its rating word (`mechanical` or
`expert`) or that it is unrated, and its lifetime where the status table has a `Lifetime` column,
matched without regard to case.
```

**Becomes:**

```
**Work package cards.** A card shows the package's ID, its title, its rating word (`mechanical` or
`expert`) or that it is unrated, and its lifetime where the status table has a `Lifetime` column,
matched without regard to case. A card carries a dot in each running dispatch's color whose
dispatch works under that package (the agents column).
```

### the agents column

The whole text of the new leaf
`PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-agents-column.md`:

```
# The agents column

The board's last column is the **agents column**, in both modes. It shows the project's running
dispatches: one card per dispatch of an agent that is working now.

A **running dispatch** is one the activity capture has recorded the start of and not the completion
of. Whether a dispatch runs is the capture's events' answer, read from the same records the
profiler view reads ([Shipped files](../../../../PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md#shipped-files)), never a measurement of time and never a poll of any
harness: the board starts no observation of its own. A change in the stores surfaces on the open
page as [live following](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md#live-following) follows any watched file.

A dispatch card shows the agent's name, the model it runs, the session that dispatched it, and a
link to the dispatched work's page where the capture records a session id for it — the child
session's page under opencode, the dispatching session's page under claude, whose store holds the
child's records. A running dispatch's color is a function of the dispatch alone: its rank in the
order the capture opened the dispatches of the stores, closed ones included, counted against a fixed
palette. The color is the same at every read and stable while the dispatch runs, distinct among the
concurrently running dispatches up to the palette's size, and shared where more than the palette's
size run at once.

A dispatch is **joined** where the active plan names it: the row of the package the dispatch works
under carries the dispatch's identifier as its dispatch note ([Plan Status Form](../../../../PROJECT_DOCS/SPEC/plan-status-form.md#plan-status-form)), and that package's
card carries a dot in the dispatch's color. A package several running dispatches work under carries
a dot for each. A dispatch no row names shows unjoined, and colors no dot; a note whose dispatch
runs no longer colors no dot.
```

### [Live following](PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md#live-following)

**As it stands:**

```
A change to a watched file, to its content, creation or deletion, appears on the open page without
a reload, within about a second. The watched files are `ROADMAP.md`, each parked file and each
parked tree's `entry-point.md`, and the active design and the active plan, a diced one as every
`.md` file beneath its entry point's directory.
```

**Becomes:**

```
A change to a watched file, to its content, creation or deletion, appears on the open page without
a reload, within about a second. The watched files are `ROADMAP.md`, each parked file and each
parked tree's `entry-point.md`, and the active design and the active plan, a diced one as every
`.md` file beneath its entry point's directory — and every record file beneath the activity
capture's stores, `.devpro-temp/.profiler-claude/` and `.devpro-temp/.profiler-opencode/`, whose
changes surface the agents column (the agents column).
```

### [Plan Status Form](PROJECT_DOCS/SPEC/plan-status-form.md#plan-status-form)

**As it stands:**

```
- **rating** — a work package's rating as its plan's status table records it: `mechanical`,
  `expert`, or unrated.
```

**Becomes:**

```
- **rating** — a work package's rating as its plan's status table records it: `mechanical`,
  `expert`, or unrated.
- **dispatch note** — the identifier of the dispatched agent run a package is under, as the
  activity capture records it, written into the package's row when the dispatch returns. The row's
  State cell's note carries it; the form gives it no cell of its own.
```

**As it stands:**

```
- A rating cell opens with one of two words: `mechanical`, every edit enumerated, no design choice
  and no debugging; `expert`, anything else. Anything after the word is a note.
```

**Becomes:**

```
- A rating cell opens with one of two words: `mechanical`, every edit enumerated, no design choice
  and no debugging; `expert`, anything else. Anything after the word is a note.
- A dispatch note is written when the dispatch returns, into the row of the package the dispatch
  works under, and is never inferred from brief or message text.
```

**As it stands:**

```
- Reads a plan as done only when its post-plan review row and its post-plan burndown row, each
  where it has one, are `landed`.
```

**Becomes:**

```
- Reads a plan as done only when its post-plan review row and its post-plan burndown row, each
  where it has one, are `landed`.
- Reads the identifiers a row's State cell's note carries as the dispatch notes naming the
  dispatches the package is under.
```

### [Rendering](PROJECT_DOCS/SPEC/rendering.md#rendering)

**As it stands:**

```
- **Tuning by category, recorded in the rendered definition.** Every agent definition declares a
```

**Becomes:**

```
- **Tuning by category, recorded once per install.** Every agent definition declares a
```

**As it stands:**

```
Every rendered definition's tuning line, its `!TUNING!` line, records the family's name, the
definition's category and that category's member (each `none` for a definition that declares no
category), the effective category map, the categories whose member the family has no member-scoped
tuning text for (as `stock=`), and the harness it was rendered for, so what it is tuned for and
what it dispatches on are readable from the definition alone.
```

**Becomes:**

```
The rendered set's tuning table, one per install under the install directory, beside the rendered definitions, records the
family's name, the effective category map, the full category list in `CATEGORIES` order,
comma-joined, `none` when empty (as `stock=`), and the harness it was rendered for, so what the set
is tuned for and what it dispatches on is readable from the set alone. A definition's category and
member appear nowhere in the rendered output: the member is the model the definition renders with,
which the dispatch fields the coordinator reads already carry, and the category map is recorded in
the tuning table, once per install, rather than in any definition.
```

### [Generated files](PROJECT_DOCS/SPEC/generated-files.md#generated-files)

**As it stands:**

```
- Under opencode a rendered definition carries its banner as the comment lines a supporting file
  opens with and has no frontmatter; its metadata is in the registry `registry.json`, a harness-rendered
  file that carries its marker, `"plugin": "devpro"`, rather than a banner (Installed tree).
```

**Becomes:**

```
- Under opencode a rendered definition carries its generated banner as the comment a supporting file
  opens with and has no frontmatter; its metadata is in the registry `registry.json`, a harness-rendered
  file that carries its marker, `"plugin": "devpro"`, rather than a banner (Installed tree).
```

### [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md#installed-tree)

**As it stands:**

```
A rendered definition, a copied script or build file, and a harness resource each states its origin
in banner lines; a harness-rendered file states it in its ownership marker; no other installed file
carries a banner.
```

**Becomes:**

```
A rendered definition, a copied script or build file, and a harness resource each states its origin
in a banner line; a harness-rendered file states it in its ownership marker; no other installed file
carries a banner.
```

**As it stands:**

```
A rendered definition carries two banner lines inside its frontmatter: the generated banner
(Generated files), which says where the file was rendered from and that it is not for local edit,
and the tuning line (Rendering). A skill's supporting file has no frontmatter, so it carries the
same two lines as HTML comments — its first two lines, above a blank line and the body — and
nothing about how the file is read depends on them. Under opencode every rendered file is written
without frontmatter and carries the two lines as those comments.
```

**Becomes:**

```
A rendered definition carries one banner line inside its frontmatter: the generated banner
(Generated files), which says where the file was rendered from and that it is not for local edit.
A skill's supporting file has no frontmatter, so it carries the banner as an HTML comment — its
first line, above a blank line and the body — and nothing about how the file is read depends on it.
Under opencode every rendered file is written without frontmatter and carries the banner as that
comment. The tuning data no rendered definition carries: the set records it once per install, in
the tuning table (Rendering).
```

**As it stands:**

```
A command's frontmatter holds its banner lines alone.
```

**Becomes:**

```
A command's frontmatter holds its banner alone.
```

## ARCHITECTURE delta

### [Banner](PROJECT_DOCS/ARCHITECTURE/banner.md#banner)

**As it stands:**

```
Under claude and mage a rendered definition other than a supporting file carries two banner lines in
its frontmatter, the generated banner and `# !TUNING!`, the tuning line (SPEC.md, Rendering).
`render.GENERATED_MARK` and `GENERATED_NOTICE` spell the generated banner, and `install.stamped`
writes the installed one. Those lines are YAML comments inside the frontmatter, so the opening `---`
is still the file's first line — the one thing a harness requires to read a frontmatter at all —
and the frontmatter's field lines follow the banner. A supporting file carries the pair as
`<!-- !GENERATED! … -->` and `<!-- !TUNING! … -->` followed by a blank line. The banners are
written, never read back: what stands in the install directory is decided by the wholesale
replacement (Renders and copies), not by any file's carrier. Under opencode every rendered file
takes that comment carrier (`render._comment_banner`), a definition's own included, because the
body file holds no frontmatter; the entry strips the leading comment lines and the blank line after
them when it registers the body.
```

**Becomes:**

```
Under claude and mage a rendered definition other than a supporting file carries the generated
banner as one banner line in its frontmatter (SPEC.md, Rendering). `render.GENERATED_MARK` and
`GENERATED_NOTICE` spell the generated banner, and `install.stamped` writes the installed one. That
line is a YAML comment inside the frontmatter, so the opening `---` is still the file's first line
— the one thing a harness requires to read a frontmatter at all — and the frontmatter's field lines
follow the banner. A supporting file carries the banner as `<!-- !GENERATED! … -->` followed by a
blank line. The banner is written, never read back: what stands in the install directory is decided
by the wholesale replacement (Renders and copies), not by any file's carrier. Under opencode every
rendered file takes that comment carrier (`render._comment_banner`), a definition's own included,
because the body file holds no frontmatter; the entry strips the leading comment lines and the
blank line after them when it registers the body.
The tuning data rides on no rendered file. The set's one carrier is the **tuning table**,
written once per install under the install directory, beside the rendered definitions, as `tuning.md` and replaced wholesale
with the rest of the install (Renders and copies); it records the family, the harness, the
effective category map and the stock list (SPEC.md, Rendering). No per-definition tuning line
exists, and `render.tuning_text` and `tuning_line` are gone with it.
```

### the agents column

The whole text of the new leaf
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-agents-column.md`:

```
# The agents column

The board panel's payload carries `agents`, the running dispatches the agents column shows
(SPEC.md, Dicing and Checks, Kanban, the agents column), derived from the activity capture's
stores, `.devpro-temp/.profiler-claude/` and `.devpro-temp/.profiler-opencode/`, the directories
[the stores' rename](../../../../PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-stores-and-their-rename.md#the-stores-and-their-rename) fixed. The derivation reads records only; it runs no subprocess and watches no clock.

A **dispatch** is identified by the id the capture records for the dispatched child: the child
session's id under opencode, the child agent's id — `child_agent_id` — under claude. Under opencode
the dispatch record — the
acknowledgment `execute.after` observed ([the opencode capture](../../../../PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-opencode-capture.md#the-opencode-capture)) — opens it, and the child's idle record with an empty
`background` closes it. Under claude the `Agent` tool-call record whose `child_agent_id` names the
child opens it, and the `SubagentStop` event record closes it, matched by the parent session, the
agent type and the order of the records, the ids the claude capture holds: two concurrent
dispatches of one agent type in one session close in the order they opened. A dispatch whose
closing record is absent is running; one with both is done.

The panel derives the running set over the records the stores hold and orders it by the opening
record's `at`. Each dispatch's color is read from a fixed palette by its open-order rank over every
dispatch the stores' records open, closed ones included, modulo the palette's size: the same color at
every read and stable while the dispatch runs, distinct among the concurrently running dispatches up
to the palette's size and shared beyond it. A dispatch card's fields are the records': the agent's
name, the model it runs, the dispatching session, and the dispatch's identifier, which the card links
to `/page/<id>` where that identifier is a session id — under claude the card links the dispatching
session's page, the store holding the child's records.

The board's mode is the status table's: planning while no row of the active plan's status table is
`in progress` or `landed`, execution otherwise — the plan the board already reads, read once more;
a project with no active plan is in planning mode. The watched set gains the stores — the two store
directories watched as directories, not their records one by one, so the poll's cost does not grow
with the sessions' count — and the panel's poll thread, the one loop the board panel already runs
([the board panel](../../../../PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md#the-board-panel)), sees a new record within its poll interval, and the long poll wakes the
open pages. A store that cannot be read is named on stderr as [live following](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md#live-following) names an
unreadable watched file, and the board keeps its last good state until it reads again.
```

### the package lifetime scale

The whole text of the new leaf `PROJECT_DOCS/ARCHITECTURE/the-package-lifetime-scale.md`:

```
# The package lifetime scale

The development skill's process scales with a package's **lifetime**, which names the code's
durability — where it will live — and nothing else. The scale has three values, stated in the
development skill's *Plans* section and in the guide's *Lifetime* bullet:

- **shipped** — the package reaches a user. It buys the whole process: design, plan, dispatch,
  review, the post-plan review included.
- **persistent** — the package is tracked in the repository and reaches no user: tests, the project
  documents, `ROADMAP.md`, CI and configuration. It buys the done-line and the checkpoint gate, and
  no post-plan review: its tests verify by running and its documents by their checks.
- **transient** — the package lives in the scratch directory only and is never committed.

The scale is held in the definition sources alone — `devpro/definitions/skills/development.py` and
`devpro/definitions/skills/guide.py`; no SPEC leaf states it, the skill being its own statement. A
release's plans carry shipped packages only: a persistent package taken into a release is re-rated
shipped before the hardening plan runs. An experiment kept becomes persistent; one discarded is
transient.
```

## Code delta

### [Plan Status Form](PROJECT_DOCS/SPEC/plan-status-form.md#plan-status-form) — the dispatch note's writer

The dispatch-note rule the leaf above gains is written by the dispatching session, and the
development skill's *Dispatch* section is where that duty is stated. In
`devpro/definitions/skills/development.py` (*Dispatch*), the bullet reading "Before the agents go, a
dispatch of a plan package names the package and sets its `State` cell; the value is the state *Plan
status* defines for a dispatch." comes to read: "At the dispatch's return, a dispatch of a plan
package names the package, sets its `State` cell — the value the state *Plan status* defines for a
dispatch — and writes its dispatch note into the row: the capture's record of the dispatch is the
identifier's source — never inferred; the writer is the dispatching session, whose row it is; the
child never writes it." The bullet's *Purpose* sentence stands unchanged.

### the package lifetime scale — the definition sources

The scale the new ARCHITECTURE leaf states is written in three definition-source texts, each
replacing its current wording; no other text in the two sources names the scale's values.

In `devpro/definitions/skills/development.py` (*Plans*), the scale bullet reading "Rigor scales with
the code's intended lifetime (*Skipping a step*). … **shipped** → the whole of this skill;
**exploratory** → the done-line and the {CHECKPOINT_GATE_TERM}, no post-plan review; **throwaway**
→ the {SCRATCH_TERM} only, never committed. …" comes to read "Rigor scales with the code's
durability (*Skipping a step*)." and to state the scale as: **shipped** — reaches a user — the whole
of this skill; **persistent** — tracked in the repository, never reaches a user: tests, the project
documents, ROADMAP.md, CI, configuration — the done-line and the {CHECKPOINT_GATE_TERM}, no
post-plan review; **transient** — the {SCRATCH_TERM} only, never committed. The bullet's opening
about the plan stating each package's lifetime, its closing about code that outlives its stated
lifetime, and its *Purpose* sentence stand unchanged.

In `devpro/definitions/skills/development.py` (*Scope*), the release rule's "exploratory work is
re-rated when its plan is taken into the release." comes to read "persistent work is re-rated when
its plan is taken into the release."; the rest of the bullet stands unchanged.

In `devpro/definitions/skills/guide.py` (*The plan*), the Lifetime bullet comes to read:
**shipped**, reaches a user — the whole process (the default); **persistent**, tracked in the
repository and reaching no user (tests, the project documents, ROADMAP.md, CI, configuration) — its
done-line and the checkpoint gate, no post-plan review; **transient**, in the scratch directory only
and never committed.

In `devpro/definitions/skills/guide.py`, the examples naming the retired values come to name the
scale's: "Make this plan exploratory." becomes "Make this plan persistent."; "Throwaway: don't commit
it." becomes "Transient: don't commit it."; "the lightest path is straight to an exploratory plan"
becomes "the lightest path is straight to a persistent plan."

