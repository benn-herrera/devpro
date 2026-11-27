# Columns and cards

The board's columns depend on its mode. In **planning** mode, left to right: Roadmap, Design,
Drafted, Dispatchable, Agents. In **execution** mode: Design, Drafted, Dispatchable, In progress,
Landed, Agents. Drafted through Landed are the **plan columns**, which are read-only
([the plan columns are read-only](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-plan-columns-are-read-only.md#the-plan-columns-are-read-only)).
The board is in planning mode while the active plan's status table holds no `in progress` and no
`landed` row, and in execution mode otherwise; a project with no active plan is in planning mode.
The last column in both modes is the agents column
([the agents column](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-agents-column.md#the-agents-column)).

| Column | Cards |
|---|---|
| Roadmap | each category of `ROADMAP.md` as a separator; each ticket of it, one card each; each parked card (**Parked work**, below), and above those the `ROADMAP_DESIGNS` separator |
| Design | each category of the active design as a separator; each ticket of it, one card each |
| Drafted | each work package whose State cell opens with `drafted`; a State cell opening with no state word breaches [check-plan](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan), and the board draws no card for its package |
| Dispatchable, In progress, Landed | as the Drafted row, for their state words |
| Agents | one card per running dispatch (the agents column) |

**Roadmap cards.** The board reads `ROADMAP.md` in the layout
([check-roadmap](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap)), in document order. A category is not a card: its
heading is a **separator** drawn in its place among the cards. Each ticket is a card titled by its
title over the ticket's text. Lines above the first category, and lines of a category before its
first ticket, are not shown.

**Parked work.** A piece of parked work that a roadmap ticket links, by a link whose path names one
of its files ([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)), has no card of its own: it shows inside
the card of the ticket that links it. A link in a design ticket other than a link ticket leaves the
parked work on Roadmap. Only a roadmap ticket's link naming a piece's file links it; links inside
parked work are not followed. A piece of parked work that no roadmap ticket links, and whose link
ticket ([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)) is not in the active design, gets a **parked
card**, titled by its parked name ([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)). The parked cards
follow all the cards of tickets, ordered among themselves by parked name, below a separator of
their own labelled `ROADMAP_DESIGNS`, drawn where there is any parked card; the parked cards and
that separator exist only on the board. A piece of parked work whose link ticket
([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)) is in the active design shows there as a Design card,
and not in Roadmap.

**Design cards.** The board reads the active design in the layout
([check-roadmap](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap)), in document order
([check-design](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-design.md#check-design)); in a diced design each heading is read from the file that
holds it. A category, a delta among them, is not a card: its heading is a separator drawn in its
place among the cards. Each ticket is a card titled by its title over the ticket's text; a link
ticket's ([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)) is a link ticket's card (**Card links**). A
ticket in a delta is an **entry card**. Lines above the first category, and lines of a category
before its first ticket, are not shown. Cards and separators follow document order.

**Collapsed categories.** Double-clicking a separator band — a category's, a delta's, or the
`ROADMAP_DESIGNS` band's — collapses the cards from that band to the next separator band or the
column's end, and doing so again shows them; the band stays, its marker shows the collapsed state
in place of the expanded band's, and every card outside the range keeps its place. A band takes
keyboard focus, toggles with Enter or Space, keeps that focus across the toggle, and reports
whether it is expanded. A collapse belongs to the page and to no file
([the board stores nothing](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-board-stores-nothing.md#the-board-stores-nothing)): a redraw keeps it, a reload loses it, and
a card added to a collapsed category, by a move
([moves between Roadmap and Design](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/moves-between-roadmap-and-design.md#moves-between-roadmap-and-design)) or by an edit, stays hidden
until the category expands.

**Content outside the layout.** Each breach [check-roadmap](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap) reports in
`ROADMAP.md`, and each breach of the layout in the active design, is shown as a notice at the head
of its document's column, naming its file, as a path from the project root, its line, the text
found and the form accepted there.

**Work package cards.** A card shows the package's ID, its title, its rating word (`mechanical` or
`expert`) or that it is unrated, and its lifetime where the status table has a `Lifetime` column,
matched without regard to case. A card carries a dot in each running dispatch's color whose
dispatch works under that package (the agents column). A package's title is as [check-plan](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan) Terms
defines it; an untitled package shows untitled. A plan whose table has no `Rating` column is still
shown, its packages unrated. Cards in a plan column follow the status table's row order.

**Card links.** Each card other than a parked card links to the file holding its heading, with that
heading's anchor ([anchors](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/link-rewriting/anchors.md#anchors), repeats counted over that file) as the fragment: a
ticket's card to the ticket's heading, a work package's card to the heading its title is read from
([check-plan](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)). An untitled work package's card links to the file holding its
status-table row, with no fragment. A parked card links to each of its piece's files, with no
fragment; a link ticket's card ([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)), besides its heading,
links each file of the piece of parked work it links, with no fragment. Each link reaches its file
as the server serves it (**Start**, above).

**Title and header.** The page is titled `<project> kanban`, `<project>` being the name of the
project root's directory, in the browser's title and in the header. The header also shows the
active plan's release (the version of its release line, displayed as written and never
interpreted), and "hardening" where the plan's level-1 heading opens `Release hardening`. The page's
own header text is the dynamic value alone: its title carries the bare word `kanban` before the
page's script runs, and the script sets both the browser's title and the header to the title above
when it draws the board.
