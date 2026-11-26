# check-roadmap

`devpro check-roadmap [<roadmap>]` checks that `ROADMAP.md` is written in the ticket layout below,
so that the board shows every ticket it holds ([the board](../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/index.md#kanban)).
[check-design](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-design.md#check-design) and the board read the active design in the same layout.

**Terms.** [check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)'s terms are used as defined there, with these additions:

- **category**: a level-2 heading and the lines below it, up to the next heading of level 1 or 2,
  or the end of the document.
- **ticket**: a level-3 heading inside a category, and the lines below it up to the next heading
  of level 1, 2 or 3, or the end of the document; a heading of level 4 or more inside it is part of
  its text. A ticket's **title** is the plain text ([what is a link](../../../PROJECT_DOCS/SPEC/dicing-and-checks/link-rewriting/what-is-a-link.md#what-is-a-link)) of
  its heading's text ([file names and layout](../../../PROJECT_DOCS/SPEC/dicing-and-checks/the-diced-tree/file-names-and-layout.md#file-names-and-layout)). The lines of a
  category before its first ticket are not a ticket.
- **old-form item**: a line opening at column 0 with a list marker (`-`, `*`, `+`, or digits
  followed by `.` or `)`), a space and `**`.

These terms are the **layout**; every other line is free.

**The layout, as checked.**

| Breach | Reported at | `found` text |
|---|---|---|
| a level-3 heading outside any category | the heading | the heading line |
| an old-form item outside any ticket | the line | the line |
| a ticket heading whose plain text is empty or only spaces | the heading | the heading line |

**`ROADMAP.md`, as checked.** Each breach of the layout, and:

| Breach | Reported at | `found` text |
|---|---|---|
| no category | the first level-1 heading, else line 1 | the line |

**The file checked.** With `<roadmap>`, that file, read as one file whatever its name, in place of
`ROADMAP.md`. Without it, `ROADMAP.md` under the project root ([check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)).

**Output.** One stderr line per breach, in the form [check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan) gives, in line
order. An empty `found` text renders as `found an empty line`. Current `<problem>` wording:

| Breach | `<problem>` |
|---|---|
| level-3 heading outside any category | `ticket outside a category` |
| old-form item | `list item in the old ticket form` |
| empty ticket heading | `ticket heading names nothing` |
| no category | `roadmap has no category` |

The summary `roadmap checked: <roadmap>, tickets: <N>, problems: <P>` goes to stdout.

**Exit status.** As [check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)'s table, with these changes: the row "no breach,
status table or none" is "no breach"; in the row "without `<plan>`, no active plan under the
root", the condition is that `ROADMAP.md` under the root is absent or not a file, and the message
is `no roadmap in <root>`; a `<roadmap>` that is not a file is the usage error
`no such roadmap file: <roadmap> (name a roadmap's markdown file)`; the no-project-root message
names `devpro check-roadmap` and `devpro check-roadmap <roadmap>`; a file checked that cannot be
read prints `cannot read: <roadmap>`, exit 2.
