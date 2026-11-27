# check-plan

`devpro check-plan [<plan>]` checks that a development plan is written in the form below, so that a
program reading the plan can read all of it. The verb reports what is present and unreadable, and a
post-plan review or burndown package without the other; what is otherwise absent is valid.

**Terms.**

- **plan**: a tracked markdown document that lays out work as work packages and records their
  progress. It is a monolith, one file, or a diced tree ([the diced tree](../../../PROJECT_DOCS/SPEC/dicing-and-checks/the-diced-tree/index.md#the-diced-tree)) given by its
  `entry-point.md`: a file named `entry-point.md` is read as one plan together with every other
  `.md` file beneath its directory, in **the plan's file order**, the entry point first.
- **work package**: one unit of a plan's work, a row of the plan's status table, named by the ID in
  that row's `Package` cell. A row whose `Package` cell is empty is not a work package.
- **status table**: the first table under a `## Status` heading (a level-2 heading whose text is
  `Status`; the section runs to the next heading of level 1 or 2) whose header cells include
  `Package` and `State`, matched without regard to case. In a diced plan the heading may be in any
  of its files. The table is found by those two headers alone. The form also has a `Rating` header,
  matched without regard to case; other columns are free.
- **state**: a work package's progress as its State cell records it. A cell opening with `drafted`
  (not yet ready to hand to an agent as it stands), `dispatchable` (ready to hand to an agent),
  `in progress` (dispatched, not yet landed) or `landed` (accepted and committed) states that word,
  lowercase and without markup, as a whole word; any text after it is a note.
- **rating**: a work package's kind of work as its Rating cell records it. A cell opening with
  `mechanical` (every edit enumerated, no design choice and no debugging) or `expert` (anything
  else) states that word, lowercase and without markup, as a whole word; any text after it is a
  note. A package whose Rating cell opens with neither word, an empty cell included, or whose table
  has no `Rating` column, is **unrated**.
- **release line**: a line opening with `Release:` at column 0. Its version is the text after the
  colon, surrounding spaces removed.
- **title**: in the first heading, in the plan's file order, whose text opens with a work package's
  ID — the ID followed by neither a letter, digit or `_`, nor a `.` or `-` followed by one — the
  text after the ID and after any run of characters each whitespace or one of `:` `.` `,` `;` `|`
  `/` `)` `]` `-` `–` `—`. A package with no such heading is untitled and is neither post-plan
  package kind.
- **post-plan review package**, **post-plan burndown package**: A title opens with
  `Post-plan review` (or `Post-plan burndown`) where it begins with those characters,
  case-sensitive, followed by the end of the title or a character that is not a letter or digit. A
  package whose title opens with `Post-plan review` is a **post-plan review package**; with
  `Post-plan burndown`, a **post-plan burndown package**: the drafting ticket the plan's `## Post-plan
  burndown` section holds.

**The form, as checked.** A plan with no status table, no work packages, no H1 heading, no release
line or neither post-plan package is valid. A plan has a breach where:

| Breach | Reported at | `found` text |
|---|---|---|
| a work package's ID is the ID of an earlier row | the later row | the ID and the line of the row that first holds it |
| a work package's ID holds a space | the row | the ID |
| a State cell opens with none of the four state words | the row | the cell |
| the status table has no `Rating` column | the table's header line | the header line |
| a work package's Rating cell opens with neither rating word, an empty cell included | the row | the cell |
| a release line is not the first non-blank line after the plan's H1 heading, the first level-1 heading | the line | the line |
| a release line, in that place, has no version | the line | the line |
| a post-plan review package where the plan has no post-plan burndown package, or a post-plan burndown package where it has no post-plan review package | that package's row | the ID, a space, and the title, as `P4 Post-plan review` |
| a work package with no heading, at any level, opening with its row's ID | the row | the ID |

The form also has a work package's heading, at any level, open with its row's ID and then its
title, as the table's breach holds. A heading that fails to open with the ID cannot be told from
one that only mentions it, so the breach does not try: its accepted form states both cases, each
with its remedy. The drafting ticket pairs by title alone, as the Terms define
it: a heading pairs whether or not a `## Post-plan burndown` section is present, the section the
[plan status form](../plan-status-form.md) has hold that ticket.

**The plan checked.** With `<plan>`, that plan. Without it, the active plan of the project the verb
runs in. The **project root** is the nearest ancestor of the current directory, the directory
itself included, that holds an entry named `.git`, found by looking at the file system; git is not
run. The active plan is `ACTIVE_PLAN.md` under the root, or `ACTIVE_PLAN/entry-point.md` where the
monolith is absent. Where both exist as files, the verb exits 2 before reading either, with the
message the exit table below gives for that case. The message's `<monolith>` and `<entry-point>`
are the two files' absolute paths. The active design is never read.

**Output.** One line to stderr per breach:

```text
<file>:<line>: <problem>: <found>; accepted: <accepted form>
```

`<file>` is the file holding the line (a diced plan's breach may be in any of its files), `<line>`
its 1-based number, `<problem>` names the breach, and `<found>` renders the text the table gives:
`found an empty cell` where the cell is empty; otherwise `found ` and the text in a code span that
holds its own backticks (delimited by one backtick more than the text's longest run of backticks,
padded with a space each side), so that the text ``a`b`` reads ``found `` a`b `` ``.
`<accepted form>` states what the plan may hold there, enough to correct it without the rest of
this section. The `<problem>` wording is current wording:

| Breach | `<problem>` |
|---|---|
| repeated ID | `package ID repeated in the status table` |
| ID with a space | `package ID holds a space` |
| State cell | `State cell opens with no state word` |
| no Rating column | `status table has no Rating column` |
| Rating cell | `Rating cell opens with no rating word` |
| release line placed elsewhere | `` `Release:` line is not the first non-blank line after the H1 heading `` |
| release line without a version | `` `Release:` line names no version `` |
| review without burndown | `post-plan review has no post-plan burndown package` |
| burndown without review | `post-plan burndown has no post-plan review package` |

Problems are printed in the plan's file order (the entry point first, Terms): by file, then by
line within a file.

The summary `plan checked: <plan>, work packages: <N>, problems: <P>` goes to stdout, `<N>`
counting the rows with a non-empty `Package` cell.

**Exit status.**

| Condition | Stream | Message | Exit |
|---|---|---|---|
| no breach, status table or none | stdout | the summary | 0 |
| without `<plan>`, no active plan under the root | stdout | `no active plan in <root>` | 0 |
| any breach | stderr, stdout | the breach lines, the summary | 1 |
| `<plan>` is not a file | stderr | the usage error `no such plan file: <plan> (name a plan's markdown file, or a diced plan's entry-point.md)` | 2 |
| without `<plan>`, no project root | stderr | `no project root: neither <directory> nor any directory above it holds .git; run devpro check-plan inside a project, or name the plan to check: devpro check-plan <plan>` | 2 |
| without `<plan>`, both forms of the active plan exist | stderr | `both forms of the active plan exist: <monolith> and <entry-point>: remove one` | 2 |
| a file of the plan cannot be read | stderr | `cannot read: <file>` | 2 |

A plan with an unreadable file exits 2 naming an unreadable file, and a verb without `<plan>` in a
project holding both forms of the active plan exits 2 naming both files — each before any breach
or summary is printed. A diced plan's unreadable file is any `.md` file beneath the entry point's
directory that cannot be read as a file, a dangling symbolic link among them.
