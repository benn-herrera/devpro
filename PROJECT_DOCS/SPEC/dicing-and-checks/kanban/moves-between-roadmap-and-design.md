# Moves between Roadmap and Design

Dropping a card moves its ticket between `ROADMAP.md` and the active design. A ticket moves as its
**lines**, its heading line to its last non-blank line, carried byte for byte but for their
relative links (**Links**, below).

A ticket added **at the end of a category** follows the category's last non-blank line, a blank
line parting it from the text above and, where a heading directly follows that line, a blank line
parting it from the heading. A ticket removed takes the blank lines directly above it with it; its
category's heading stays.

In a diced design, a **leaf** is a file other than a head file
([check-design](../reassembly.md)) whose directory has a head
([check-tree](../reassembly.md)), and the **full listing** is the list under the last
`Contents:` line of `entry-point.md`, where that list holds a line linking a file that is not
beside `entry-point.md` ([file content](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks)). A line added to the full listing
links the added file by its path from the directory of `entry-point.md`; it is indented two spaces
more than the line linking the head ([check-tree](../reassembly.md)) of the file's directory,
and follows that line and the lines below it indented deeper. Where no line of the full listing
links that head, it goes at the end of the full listing, indented two spaces. In the Contents lines
a move adds for a new leaf, `<text>` is the link text [file content](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks) gives
the leaf's section: for a ticket title [file names and layout](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks) reads
as numbered, `§<number> ` and the rest of the title; else the title.

**Roadmap to Design.** Dropping a roadmap card or a parked card on Design adds a ticket at the end
of the design's `## Drafts` category, the first category whose heading text is `Drafts`.
`## Drafts` is not a delta, so [check-design](../reassembly.md) reports it until the design
reaches its final form:

- *roadmap card*: the ticket's lines are removed from `ROADMAP.md` and added to the design;
- *parked card*: its link ticket ([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)) is added; the piece
  of parked work's files and `ROADMAP.md` are not touched.

| The active design | The addition |
|---|---|
| absent | `ACTIVE_DESIGN.md` is created, opening with the level-1 heading `# ACTIVE DESIGN`, then `## Drafts` and the ticket, a blank line parting each from the line above |
| a monolith | the ticket is added at the end of `## Drafts`; where there is none, `## Drafts` and the ticket are appended to the file, a blank line parting each from the text above, where there is any |
| a diced tree whose `## Drafts` heading opens an `index.md` | the ticket is a new leaf beside that `index.md`, named `<name>.md`, `<name>` being the [file names and layout](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks) name of the ticket's title; the line `- [<text>](<name>.md)` is added at the end of the list under that `index.md`'s last `Contents:` line, and a line `- [<text>](<path>)` for the leaf to the full listing, where `entry-point.md` has one |
| a diced tree with no `## Drafts` | the ticket is the new leaf `drafts/<name>.md`, named as above, the directory `drafts` beside `entry-point.md` made where it does not exist; `drafts/index.md` is created holding `## Drafts`, a blank line, `Contents:`, a blank line and the line `- [<text>](<name>.md)`; and the lines `- [Drafts](../index.md)` and `  - [<text>](drafts/<name>.md)` are added at the end of the list under the last `Contents:` line of `entry-point.md`, or in a Contents block added at its end where it has none |
| a diced tree whose `## Drafts` is elsewhere | the ticket is added at the end of `## Drafts` in the file holding it; in a head file ([check-design](../reassembly.md)), before its Contents block |

**Design to Roadmap.** Dropping on Roadmap a design card other than an entry card removes its
ticket from the design and, unless it is a link ticket, adds the ticket's lines to `ROADMAP.md`.
Where `ROADMAP.md` has categories, the ticket is added at the end of the category whose separator
is nearest above the place the drop landed, whether on a card or on a separator; at the end of the
first category where no category's separator is above that place, or where that category is no
longer on the board. The `ROADMAP_DESIGNS` separator
([columns and cards](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/columns-and-cards.md#columns-and-cards)) is not a category's. A link ticket is removed and nothing
is added; its parked card shows in Roadmap again
([columns and cards](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/columns-and-cards.md#columns-and-cards)).

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

**Links.** A move rebases each relative link target in the text ([link rewriting](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks)) of the
ticket's lines, resolved from the directory of the file the ticket leaves, to reach the same file
from the directory of the file it joins, fragment kept; targets that
[link targets](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks) step 2 leaves unchanged stay unchanged. A `#<anchor>` target
stays as written in both directions: it names a heading of the file holding it, so it keeps
reaching a heading the ticket carries. It breaks only where
[anchors](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks)' per-file repeat count gives that heading another anchor in the file
joined, or where it named a heading outside the ticket;
[check-links](../reassembly.md) reports either break. Between files in one directory, as
`ROADMAP.md` and a single-file active design are ([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)), no
link changes. A link ticket is written, not moved: its links are made for the file that holds it
([the project's files](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)).

**Refusals.** A move is refused, and nothing is written, where:

- a file the move writes, creates or deletes (`ROADMAP.md`, or a file of the design) has a content,
  existence or absence different from when the board last read it, checked for every such file
  immediately before the first write; a change after that check is not detected;
- what is dropped on Roadmap is an entry card or a separator, in a drop request the page would not
  make ([the plan columns are read-only](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-plan-columns-are-read-only.md#the-plan-columns-are-read-only)), such as one from a page
  showing a board that has since changed; refused with a message naming that cause;
- the active design is a diced tree, the move adds a leaf, and the title's
  [file names and layout](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks) name is empty (an unnumbered title with an
  empty slug), refused with a message naming that cause;
- the active design is a diced tree and a file the move creates already exists, refused with a
  message naming that cause;
- the active design is a diced tree and the move must remove a leaf's line from the Contents list
  of its directory's head and cannot find it, refused with a message naming that cause;
- the ticket dropped on Roadmap is in a diced design and runs on past its file: its text in the
  layout ([check-roadmap](../reassembly.md)) continues into the next file in document order
  ([check-design](../reassembly.md)), as a ticket whose level-4 sections were diced into
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
