## kanban

`devpro dashboard [<project-dir>]` serves a live board of a project's development-process files on
the local machine as the dashboard's board panel at `/board/`, for the user to open in a browser. The board shows `ROADMAP.md`'s tickets and the
parked work, the active design and the active plan's work packages as cards in columns. Its only
writes to documents are the moves of [Moves between Roadmap and Design](#moves-between-roadmap-and-design),
made by dropping a card on Design or on Roadmap: a ticket moved between `ROADMAP.md` and the
active design, after which it is in exactly one of the two documents (a move that fails partway is
described under **Writes**, [Moves between Roadmap and Design](#moves-between-roadmap-and-design));
a parked card's link ticket added to the active design; and a link ticket removed from it. The
plan columns are read-only: a work package's state changes only by an edit to the plan, which the
board then shows ([the plan columns are read-only](#the-plan-columns-are-read-only),
[live following](#live-following)). The board stores nothing
([the board stores nothing](#the-board-stores-nothing)).

The board reads the files as they are, `ROADMAP.md` in the layout
[check-roadmap](checks.md#check-roadmap) checks, a plan in the form
[check-plan](checks.md#check-plan) checks and the active design in the form
[check-design](checks.md#check-design) checks, and shows a document that holds breaches of its form
all the same. Terms of [check-plan](checks.md#check-plan) (plan, work package, state, rating,
title, status table, release line, project root, active plan), of
[check-design](checks.md#check-design) (design, delta, entry, document order) and of
[check-roadmap](checks.md#check-roadmap) (layout, category, ticket, a ticket's title) are used as
defined there.

**Start.** `<project-dir>` names a directory inside the project; without it the project is the one
the verb runs in. The project root is the nearest of that directory and its ancestors holding a
`.git` entry, that directory itself where none does; the board then reads the documents at the
paths below, a document that is absent contributing no cards. Once the server is listening it prints
the page's URL, `http://127.0.0.1:<port>/`, on a line of its own to stdout; the user opens that URL.
The server accepts connections from the local machine only (`127.0.0.1`), and refuses a request whose
`Host` header is not the server's own address (`127.0.0.1` or `localhost`, with the port), so that
a page served from elsewhere cannot drive the board. The server serves the served documents, and
no other file of the project: every `.md` file at the project root's top level, every `.md` file
beneath the project's `PROJECT_DOCS/` and `ROADMAP_DESIGNS/` directories, and the active design's
and active plan's files as the form reads them ([the project's files](#the-projects-files), a diced
tree's leaves included); each read-only, as `text/markdown`, at the URL path that is the file's
path from the project root. A served file that cannot be read is answered 404, the others still
served. It then runs until interrupted (Ctrl-C) or stopped from the page
([live following](#live-following)); either ends the process with exit 0. Which port it listens on
is not fixed by this section: the printed URL is the address. The server writes nothing per
request: stdout carries the URL line only, and stderr carries only the diagnostics named in this
section ([live following](#live-following)).

| Condition | Stream | Message | Exit |
|---|---|---|---|
| more than one argument, or an unknown option | stderr | the usage error | 2 |
| `<project-dir>` is not a directory | stderr | the usage error `no such directory: <project-dir>` | 2 |
| a document the board reads cannot be read as a file, at start | stderr | `error: cannot read: <file>`, before any URL is printed | 2 |
| a port outside 0 to 65535 | stderr | the usage error `NUMBER is not a port: 0 to 65535` | 2 |
| the port cannot be bound | stderr | `error: cannot listen: <reason>`, before any URL is printed | 2 |

### The project's files

Under the project root the files are at fixed paths; nothing relocates them.

| Document | Path |
|---|---|
| roadmap tickets ([check-roadmap](checks.md#check-roadmap)) | `ROADMAP.md` |
| **active design** | `ACTIVE_DESIGN.md`, else `ACTIVE_DESIGN/entry-point.md` |
| active plan ([check-plan](checks.md#check-plan)) | `ACTIVE_PLAN.md`, else `ACTIVE_PLAN/entry-point.md` |
| **parked-designs directory** | `ROADMAP_DESIGNS/` |
| **project-documents directory** (where present) | `PROJECT_DOCS/` |

Where both forms of the active design or the active plan exist, the board reads the monolith.
**Parked work** is each `.md` file in the parked-designs directory other than `README.md`, a
**parked file**, and each subdirectory there holding its own `entry-point.md`, a **parked tree**.
Each has a **parked name**: a parked file's name without `.md`, a parked tree's directory name. A
parked name `<topic>_DESIGN`, `<topic>_PLAN` or `<topic>_PLAN_REVIEW` makes `<topic>` a **topic**.
A parked name that is `<topic>` or opens with `<topic>_` joins that topic, the longest where it
could join more than one. The parked files and trees of one topic are one **piece of parked work**,
whose parked name is `<topic>`; each other parked file or tree is a piece of its own, keeping its
parked name. A piece's **files** are its parked files and its parked trees' `entry-point.md`, in
order of their paths. A **link ticket** is a ticket of the active design, outside any delta, for a
piece of parked work that no roadmap ticket links, whose lines are exactly `### <name>`, a blank
line, a line `[<path>](<link>)` for each of the piece's files, in order, a blank line and
`complete and update this design`, where `<name>` is the piece's parked name, each `<path>` a
file's path from the project root and its `<link>` that path relative to the directory of the file
holding the ticket. A document that is absent contributes no cards; a project with none of them
shows an empty board.

### Columns and cards

The board has six columns, left to right: Roadmap, Design, Drafted, Dispatchable, In progress,
Landed. Drafted through Landed are the **plan columns**, which are read-only
([the plan columns are read-only](#the-plan-columns-are-read-only)).

| Column | Cards |
|---|---|
| Roadmap | each category of `ROADMAP.md` as a separator; each ticket of it, one card each; each parked card (**Parked work**, below), and above those the `ROADMAP_DESIGNS` separator |
| Design | each category of the active design as a separator; each ticket of it, one card each |
| Drafted | each work package whose State cell opens with `drafted`; a State cell opening with no state word breaches [check-plan](checks.md#check-plan), and the board draws no card for its package |
| Dispatchable, In progress, Landed | as the Drafted row, for their state words |

**Roadmap cards.** The board reads `ROADMAP.md` in the layout
([check-roadmap](checks.md#check-roadmap)), in document order. A category is not a card: its
heading is a **separator** drawn in its place among the cards. Each ticket is a card titled by its
title over the ticket's text. Lines above the first category, and lines of a category before its
first ticket, are not shown.

**Parked work.** A piece of parked work that a roadmap ticket links, by a link whose path names one
of its files ([the project's files](#the-projects-files)), has no card of its own: it shows inside
the card of the ticket that links it. A link in a design ticket other than a link ticket leaves the
parked work on Roadmap. Only a roadmap ticket's link naming a piece's file links it; links inside
parked work are not followed. A piece of parked work that no roadmap ticket links, and whose link
ticket ([the project's files](#the-projects-files)) is not in the active design, gets a **parked
card**, titled by its parked name ([the project's files](#the-projects-files)). The parked cards
follow all the cards of tickets, ordered among themselves by parked name, below a separator of
their own labelled `ROADMAP_DESIGNS`, drawn where there is any parked card; the parked cards and
that separator exist only on the board. A piece of parked work whose link ticket
([the project's files](#the-projects-files)) is in the active design shows there as a Design card,
and not in Roadmap.

**Design cards.** The board reads the active design in the layout
([check-roadmap](checks.md#check-roadmap)), in document order
([check-design](checks.md#check-design)); in a diced design each heading is read from the file that
holds it. A category, a delta among them, is not a card: its heading is a separator drawn in its
place among the cards. Each ticket is a card titled by its title over the ticket's text; a link
ticket's ([the project's files](#the-projects-files)) is a link ticket's card (**Card links**). A
ticket in a delta is an **entry card**. Lines above the first category, and lines of a category
before its first ticket, are not shown. Cards and separators follow document order.

**Collapsed categories.** Double-clicking a separator band — a category's, a delta's, or the
`ROADMAP_DESIGNS` band's — collapses the cards from that band to the next separator band or the
column's end, and doing so again shows them; the band stays, its marker shows the collapsed state
in place of the expanded band's, and every card outside the range keeps its place. A band takes
keyboard focus, toggles with Enter or Space, keeps that focus across the toggle, and reports
whether it is expanded. A collapse belongs to the page and to no file
([the board stores nothing](#the-board-stores-nothing)): a redraw keeps it, a reload loses it, and
a card added to a collapsed category, by a move
([moves between Roadmap and Design](#moves-between-roadmap-and-design)) or by an edit, stays hidden
until the category expands.

**Content outside the layout.** Each breach [check-roadmap](checks.md#check-roadmap) reports in
`ROADMAP.md`, and each breach of the layout in the active design, is shown as a notice at the head
of its document's column, naming its file, as a path from the project root, its line, the text
found and the form accepted there.

**Work package cards.** A card shows the package's ID, its title, its rating word (`mechanical` or
`expert`) or that it is unrated, and its lifetime where the status table has a `Lifetime` column,
matched without regard to case. A package's title is as [check-plan](checks.md#check-plan) Terms
defines it; an untitled package shows untitled. A plan whose table has no `Rating` column is still
shown, its packages unrated. Cards in a plan column follow the status table's row order.

**Card links.** Each card other than a parked card links to the file holding its heading, with that
heading's anchor ([anchors](links.md#anchors), repeats counted over that file) as the fragment: a
ticket's card to the ticket's heading, a work package's card to the heading its title is read from
([check-plan](checks.md#check-plan)). An untitled work package's card links to the file holding its
status-table row, with no fragment. A parked card links to each of its piece's files, with no
fragment; a link ticket's card ([the project's files](#the-projects-files)), besides its heading,
links each file of the piece of parked work it links, with no fragment. Each link reaches its file
as the server serves it (**Start**, above).

**Title and header.** The page is titled `<project> kanban`, `<project>` being the name of the
project root's directory, in the browser's title and in the header. The header also shows the
active plan's release (the version of its release line, displayed as written and never
interpreted), and "hardening" where the plan's level-1 heading opens `Release hardening`. The page's
own header text is the dynamic value alone: its title carries the bare word `kanban` before the
page's script runs, and the script sets both the browser's title and the header to the title above
when it draws the board.

### Moves between Roadmap and Design

Dropping a card moves its ticket between `ROADMAP.md` and the active design. A ticket moves as its
**lines**, its heading line to its last non-blank line, carried byte for byte but for their
relative links (**Links**, below).

A ticket added **at the end of a category** follows the category's last non-blank line, a blank
line parting it from the text above and, where a heading directly follows that line, a blank line
parting it from the heading. A ticket removed takes the blank lines directly above it with it; its
category's heading stays.

In a diced design, a **leaf** is a file other than a head file
([check-design](checks.md#check-design)) whose directory has a head
([check-tree](checks.md#check-tree)), and the **full listing** is the list under the last
`Contents:` line of `entry-point.md`, where that list holds a line linking a file that is not
beside `entry-point.md` ([file content](tree.md#file-content)). A line added to the full listing
links the added file by its path from the directory of `entry-point.md`; it is indented two spaces
more than the line linking the head ([check-tree](checks.md#check-tree)) of the file's directory,
and follows that line and the lines below it indented deeper. Where no line of the full listing
links that head, it goes at the end of the full listing, indented two spaces. In the Contents lines
a move adds for a new leaf, `<text>` is the link text [file content](tree.md#file-content) gives
the leaf's section: for a ticket title [file names and layout](tree.md#file-names-and-layout) reads
as numbered, `§<number> ` and the rest of the title; else the title.

**Roadmap to Design.** Dropping a roadmap card or a parked card on Design adds a ticket at the end
of the design's `## Drafts` category, the first category whose heading text is `Drafts`.
`## Drafts` is not a delta, so [check-design](checks.md#check-design) reports it until the design
reaches its final form:

- *roadmap card*: the ticket's lines are removed from `ROADMAP.md` and added to the design;
- *parked card*: its link ticket ([the project's files](#the-projects-files)) is added; the piece
  of parked work's files and `ROADMAP.md` are not touched.

| The active design | The addition |
|---|---|
| absent | `ACTIVE_DESIGN.md` is created, opening with the level-1 heading `# ACTIVE DESIGN`, then `## Drafts` and the ticket, a blank line parting each from the line above |
| a monolith | the ticket is added at the end of `## Drafts`; where there is none, `## Drafts` and the ticket are appended to the file, a blank line parting each from the text above, where there is any |
| a diced tree whose `## Drafts` heading opens an `index.md` | the ticket is a new leaf beside that `index.md`, named `<name>.md`, `<name>` being the [file names and layout](tree.md#file-names-and-layout) name of the ticket's title; the line `- [<text>](<name>.md)` is added at the end of the list under that `index.md`'s last `Contents:` line, and a line `- [<text>](<path>)` for the leaf to the full listing, where `entry-point.md` has one |
| a diced tree with no `## Drafts` | the ticket is the new leaf `drafts/<name>.md`, named as above, the directory `drafts` beside `entry-point.md` made where it does not exist; `drafts/index.md` is created holding `## Drafts`, a blank line, `Contents:`, a blank line and the line `- [<text>](<name>.md)`; and the lines `- [Drafts](drafts/index.md)` and `  - [<text>](drafts/<name>.md)` are added at the end of the list under the last `Contents:` line of `entry-point.md`, or in a Contents block added at its end where it has none |
| a diced tree whose `## Drafts` is elsewhere | the ticket is added at the end of `## Drafts` in the file holding it; in a head file ([check-design](checks.md#check-design)), before its Contents block |

**Design to Roadmap.** Dropping on Roadmap a design card other than an entry card removes its
ticket from the design and, unless it is a link ticket, adds the ticket's lines to `ROADMAP.md`.
Where `ROADMAP.md` has categories, the ticket is added at the end of the category whose separator
is nearest above the place the drop landed, whether on a card or on a separator; at the end of the
first category where no category's separator is above that place, or where that category is no
longer on the board. The `ROADMAP_DESIGNS` separator
([columns and cards](#columns-and-cards)) is not a category's. A link ticket is removed and nothing
is added; its parked card shows in Roadmap again
([columns and cards](#columns-and-cards)).

| `ROADMAP.md` | The addition |
|---|---|
| absent | `ROADMAP.md` is created holding `# ROADMAP`, a blank line, `## General`, a blank line, then the ticket |
| no category | `## General` and the ticket are appended to it, a blank line parting each from the text above, where there is any |
| categories | the ticket is added at the end of the category the drop selects (above) |

In a diced design, a ticket that is all of a leaf, holding the ticket and only blank lines besides,
goes with the leaf: the line linking the leaf is removed from the Contents list of its directory's
head and, where that head is not `entry-point.md` and the full listing holds a line linking the
leaf, from the full listing too; then the leaf is deleted. Any other ticket is removed from the
file holding it.

**Links.** A move rebases each relative link target in the text ([link rewriting](links.md)) of the
ticket's lines, resolved from the directory of the file the ticket leaves, to reach the same file
from the directory of the file it joins, fragment kept; targets that
[link targets](links.md#link-targets) step 2 leaves unchanged stay unchanged. A `#<anchor>` target
stays as written in both directions: it names a heading of the file holding it, so it keeps
reaching a heading the ticket carries. It breaks only where
[anchors](links.md#anchors)' per-file repeat count gives that heading another anchor in the file
joined, or where it named a heading outside the ticket;
[check-links](checks.md#check-links) reports either break. Between files in one directory, as
`ROADMAP.md` and a single-file active design are ([the project's files](#the-projects-files)), no
link changes. A link ticket is written, not moved: its links are made for the file that holds it
([the project's files](#the-projects-files)).

**Refusals.** A move is refused, and nothing is written, where:

- a file the move writes, creates or deletes (`ROADMAP.md`, or a file of the design) has a content,
  existence or absence different from when the board last read it, checked for every such file
  immediately before the first write; a change after that check is not detected;
- what is dropped on Roadmap is an entry card or a separator, in a drop request the page would not
  make ([the plan columns are read-only](#the-plan-columns-are-read-only)), such as one from a page
  showing a board that has since changed; refused with a message naming that cause;
- the active design is a diced tree, the move adds a leaf, and the title's
  [file names and layout](tree.md#file-names-and-layout) name is empty (an unnumbered title with an
  empty slug), refused with a message naming that cause;
- the active design is a diced tree and a file the move creates already exists, refused with a
  message naming that cause;
- the active design is a diced tree and the move must remove a leaf's line from the Contents list
  of its directory's head and cannot find it, refused with a message naming that cause;
- the ticket dropped on Roadmap is in a diced design and runs on past its file: its text in the
  layout ([check-roadmap](checks.md#check-roadmap)) continues into the next file in document order
  ([check-design](checks.md#check-design)), as a ticket whose level-4 sections were diced into
  files of their own does; refused with a message naming that cause;
- a document the move reads cannot be read, refused with `cannot read: <file>`, `<file>` as a path
  from the project root (a move never reads the active plan); or
- the dropped card is no longer on the board, its ticket or parked work having changed or been
  removed since the page showed it.

The refusal is shown to the user and names the cause.

**Writes.** Each file is written whole. The addition is written before the removal, so that a
failure partway leaves the ticket in both documents and never in neither. A write or a deletion
that fails at the file system is reported as `cannot write: <file>`, `<file>` the file that could
not be written or deleted, and names the files already written. After a move the page shows a move
message naming the files written, a deleted leaf among them, as paths from the project root with
`/` separators.

### The plan columns are read-only

The cards in the plan columns cannot be dragged, and nothing can be dropped on a plan column. The
page shows this on sight: the plan columns, their cards and the Design column's entry cards are
visibly set apart, by form and not by colour alone, from the cards that can be dragged, which are
the Roadmap column's cards and the Design column's other cards. Neither an entry card nor a
separator can be dragged; a separator is drawn as a band, not as a card. A work package's state
changes only by an edit to the plan file, which the board shows
([live following](#live-following)).

**Drops not accepted.** The only drops accepted are a roadmap or parked card on Design and a design
card other than an entry card on Roadmap (both
[moves between Roadmap and Design](#moves-between-roadmap-and-design)). Any other drop is not
accepted and the card returns to its column. A departure from the common path, such as a plan with
no design or a skipped step, is not refused for being one (only the moves'
**Refusals** refuse a move) and never asks for confirmation.

### Live following

A change to a watched file, to its content, creation or deletion, appears on the open page without
a reload, within about a second. The watched files are `ROADMAP.md`, each parked file and each
parked tree's `entry-point.md`, and the active design and the active plan, a diced one as every
`.md` file beneath its entry point's directory.

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

### The board stores nothing

The board keeps no state beyond the page and writes no file, in the project or elsewhere, for
itself. A redraw keeps what the page holds; a reload loses it. A restarted server shows the files
as they then are, and nothing else.

### What kanban does not do

It makes no inference call, runs no subprocess, reads no git history and fetches nothing from the
network; every write is a fixed transformation of file content
([moves between Roadmap and Design](#moves-between-roadmap-and-design)). Its only state the user
sets is a band's collapse ([columns and cards](#columns-and-cards)); it has no filters, pull-downs,
search, sorting or custom drop affordances. The board is not a source of its own, so it changes
nothing that the page's own state could otherwise hold. The board's only writes are the moves
([moves between Roadmap and Design](#moves-between-roadmap-and-design)). It does not reorder
tickets, move a ticket between categories of one document, or edit any ticket's or category's
text. The project root is found by looking at the file system
([check-plan](checks.md#check-plan)).
