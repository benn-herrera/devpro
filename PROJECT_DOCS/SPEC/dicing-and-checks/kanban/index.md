# kanban

`devpro dashboard [<project-dir>]` serves a live board of a project's development-process files on
the local machine as the dashboard's board panel at `/board/`, for the user to open in a browser. The board shows `ROADMAP.md`'s tickets and the
parked work, the active design and the active plan's work packages as cards in columns. Its only
writes to documents are the moves of [Moves between Roadmap and Design](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/moves-between-roadmap-and-design.md#moves-between-roadmap-and-design),
made by dropping a card on Design or on Roadmap: a ticket moved between `ROADMAP.md` and the
active design, after which it is in exactly one of the two documents (a move that fails partway is
described under **Writes**, [Moves between Roadmap and Design](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/moves-between-roadmap-and-design.md#moves-between-roadmap-and-design));
a parked card's link ticket added to the active design; and a link ticket removed from it. The
plan columns are read-only: a work package's state changes only by an edit to the plan, which the
board then shows ([the plan columns are read-only](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-plan-columns-are-read-only.md#the-plan-columns-are-read-only),
[live following](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md#live-following)). The board stores nothing
([the board stores nothing](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-board-stores-nothing.md#the-board-stores-nothing)).

The board reads the files as they are, `ROADMAP.md` in the layout
[check-roadmap](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap) checks, a plan in the form
[check-plan](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan) checks and the active design in the form
[check-design](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-design.md#check-design) checks, and shows a document that holds breaches of its form
all the same. Terms of [check-plan](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan) (plan, work package, state, rating,
title, status table, release line, project root, active plan), of
[check-design](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-design.md#check-design) (design, delta, entry, document order) and of
[check-roadmap](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap) (layout, category, ticket, a ticket's title) are used as
defined there.

**Start.** `<project-dir>` names a directory inside the project; without it the project is the one
the verb runs in. The project root is the nearest of that directory and its ancestors holding a
`.git` entry, that directory itself where none does; the board then reads the documents at the
paths below, a document that is absent contributing no cards. Once the server is listening it prints
the page's URL, `http://127.0.0.1:<port>/`, on a line of its own to stdout; the user opens that URL.
That URL is the dashboard's root, which answers a redirect to the board panel at `/board/`, the
landing surface, so opening the URL shows the board. The server accepts connections from the local machine only (`127.0.0.1`), and refuses a request whose
`Host` header is not the server's own address (`127.0.0.1` or `localhost`, with the port), so that
a page served from elsewhere cannot drive the board. The server serves the served documents, and
no other file of the project: every `.md` file at the project root's top level, every `.md` file
beneath the project's `PROJECT_DOCS/` and `ROADMAP_DESIGNS/` directories, and the active design's
and active plan's files as the form reads them ([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files), a diced
tree's leaves included); each read-only, as `text/markdown`, at the URL path that is the file's
path from the project root. A served file that cannot be read is answered 404, the others still
served. It then runs until interrupted (Ctrl-C) or stopped from the page
([live following](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md#live-following)); either ends the process with exit 0. Which port it listens on
is not fixed by this section: the printed URL is the address. The server writes nothing per
request: stdout carries the URL line only, and stderr carries only the diagnostics named in this
section ([live following](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/live-following.md#live-following)).

| Condition | Stream | Message | Exit |
|---|---|---|---|
| more than one argument, or an unknown option | stderr | the usage error | 2 |
| `<project-dir>` is not a directory | stderr | the usage error `no such directory: <project-dir>` | 2 |
| a document the board reads cannot be read as a file, at start | stderr | `error: cannot read: <file>`, before any URL is printed | 2 |
| a port outside 0 to 65535 | stderr | the usage error `NUMBER is not a port: 0 to 65535` | 2 |
| the port cannot be bound | stderr | `error: cannot listen: <reason>`, before any URL is printed | 2 |

Contents:

- [The project's files](the-project-s-files.md)
- [Columns and cards](columns-and-cards.md)
- [The agents column](the-agents-column.md)
- [Moves between Roadmap and Design](moves-between-roadmap-and-design.md)
- [The plan columns are read-only](the-plan-columns-are-read-only.md)
- [Live following](live-following.md)
- [The board stores nothing](the-board-stores-nothing.md)
- [What kanban does not do](what-kanban-does-not-do.md)
