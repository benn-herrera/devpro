## Reassembly

Passes when the files [file names and layout](tree.md#file-names-and-layout) assigns, read in
section order with each entry point's and index's Contents block dropped (from its last line that
is exactly `Contents:`) and [section references](links.md#section-references) step 3 links undone,
equal the source lines with their other links as rewritten by
[link targets](links.md#link-targets). A file whose top heading reads level 1 is in the re-based
form ([file content](tree.md#file-content)) and has its heading ladder shifted back before the
compare: its top compares at its section's source level, and every other heading gains its
section's level minus 1, fenced lines compared as they stand. A file whose top reads any other
level is the pre-change form, already at the source's levels, and compares as it stands; the
pre-change form never presents a level-1 top, since no section is planned at level 1
([which headings split](tree.md#which-headings-split)). Success prints
`reassemble ok: <N> lines` to stdout; each failure prints to the verb's error stream:

| Fault | Message |
|---|---|
| line differs | `reassemble: first difference at monolith line <N> (<file>)`, then `  want: <line>` and `  got:  <line>` |
| file unreadable | `reassemble: cannot read <file>` |
| no Contents block | `reassemble: no Contents block in <file>` |
| line count | `reassemble: leaves hold <K> lines, monolith <M>` |

The check compares lines, not final newlines ([shared behaviors](index.md#shared-behaviors)). Lines
added after a Contents block are not checked.

## Link check

Every link in the text ([link rewriting](links.md)) of every file
[file names and layout](tree.md#file-names-and-layout) assigns, taken without its `#fragment`, must
name a readable file relative to that file's directory. Skipped: empty targets (bare `#frag`),
targets opening with `/`, and targets with a URL scheme
([link targets](links.md#link-targets), step 2). Everything else is probed relative to the file and
so is dead unless it exists there; a directory is dead. An assigned file that cannot be read
contributes no links ([reassembly](#reassembly) reports it). Each dead link prints
`dead link: <file>:<line> -> <target>` to the error stream; the summary
`links checked: <N>, dead: <D>` goes to the output stream.

## check-links

`devpro check-links <root>...` checks markdown files that need not come from a dicing. A directory
root contributes every `.md` file beneath it in sorted order; a file root is checked alone; a file
reached twice is checked once. Every root must exist, else exit 2 (`no such root: <roots>`). Every
file so contributed must be readable as a file; before any link is checked, each that is not prints
`cannot read: <path>` to stderr and the verb exits 2.

In text outside fenced code and code spans, every link is checked except those with an empty
target, a target opening with `/`, or a URL scheme ([link targets](links.md#link-targets), step 2).
The target's path part (the linking file itself, if empty) must exist, else the problem is
`missing file`; given a `#fragment` it must name a markdown file with a heading whose anchor equals
the fragment ([anchors](links.md#anchors), repeats counted over the file), else `missing anchor`.
Each problem prints to stderr `<file>:<line>: <target>: <problem>`. The summary
`links checked: <N>, broken: <B>` goes to stdout. Exit 1 if any link is broken.

## check-tree

`devpro check-tree <root>...` checks diced trees. Every root must be a directory, else exit 2
(`no such directory: <roots>`). Every `.md` file under a root must be readable as a file; before
any check, each that is not prints `cannot read: <path>` to stderr and the verb exits 2. A root
without an `entry-point.md` is one problem (`<root>: no entry-point.md`).

A directory's **head** is its `entry-point.md` if present, else its `index.md`. A document's
**parent** is the head of its directory; a head's parent is the head of the directory above. For
each `.md` file under the root other than the root's `entry-point.md`:

| Problem | Message (stderr) |
|---|---|
| no parent document inside the root | `<file>: no parent document (an index.md or entry-point.md beside it or above it)` |
| parent has no link to it | `<file>: not linked from its parent <parent>` |
| not reachable by following links from the root's `entry-point.md` | `<file>: not reachable from <entry-point>` |
| a volume directory of a volume tree opens at `index.md` | `<file>: a volume directory of this tree opens at entry-point.md, not index.md: a volume's sections sit below it` |

The last problem names a [misplaced section](tree.md#the-model): a tree whose root's Contents links
an `entry-point.md` below it is the omnibus form, and every top-level directory under it is a
volume's; one opening at `index.md` stands where a volume must. A tree whose root links no such head
is one document's, and its top-level directories are sections — `dice`'s one-document form and a
project document tree such as `SPEC/` both are — so none of them is reported.

Links count as in [check-links](#check-links). The summary
`documents checked: <N>, problems: <P>` goes to stdout, summed over roots; `<N>` counts every
`.md` file under a root, its `entry-point.md` included, and a root without `entry-point.md` counts
none. Exit 1 if any problem.

## check-plan

`devpro check-plan [<plan>]` checks that a development plan is written in the form below, so that a
program reading the plan can read all of it. The verb reports what is present and unreadable, and a
post-plan review or burndown package without the other; what is otherwise absent is valid.

**Terms.**

- **plan**: a tracked markdown document that lays out work as work packages and records their
  progress. It is a monolith, one file, or a diced tree ([the diced tree](tree.md)) given by its
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
with its remedy. The post-plan burndown's drafting ticket pairs by title alone, as the Terms define
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

## check-design

`devpro check-design [--deltas-applied] [<design>]` checks that a design is in its final form,
ready to plan from: beside the form, every pair's from passage still matches its target, so a
design is accepted only against the targets it changes. With `--deltas-applied` it instead checks
that every pair has been applied: its target holds the becomes passage and no longer the from, an
addition excepted. A design still being drafted fails it in either mode.

**Terms.** [check-plan](#check-plan)'s terms, and [check-roadmap](#check-roadmap)'s (below:
layout, category, ticket, old-form item), are used as defined there, with these additions:

- **design**: a tracked markdown document, a monolith or a diced tree given by its
  `entry-point.md`. A diced design is its entry point and every other `.md` file beneath the entry
  point's directory, each read once, in **document order**:
  - the entry point;
  - the files its Contents links reach, depth first: from a **head file**, a file named
    `entry-point.md` or `index.md`, each link from its last `Contents:` line on is followed in link
    order; a linked file is read where its link is first met and, where it is a head file, its own
    links are followed there, before the next link. A Contents link to anything but a `.md` file
    beneath the entry point's directory is ignored;
  - the files those links do not reach: a directory's own files before its subdirectories', each
    level in name order.

  Each head file is read without its Contents block and what follows it.
- **H1**: the design's first level-1 heading, as for a plan ([check-plan](#check-plan)).
- **delta heading**: a level-2 heading whose text
  ([file names and layout](tree.md#file-names-and-layout): after the `#` run, surrounding spaces
  removed) is exactly `SPEC delta`, `ARCHITECTURE delta` or `Code delta`; that is their **order**.
  Its **delta** runs to the next heading of level 1 or 2, or the end of the design.
- **entry**: a ticket ([check-roadmap](#check-roadmap)) inside a delta. A delta with no entries is
  valid.
- **target**: the file an entry heading's one link names, resolved relative to the file the entry
  is in ([link rewriting](links.md)). A heading whose link is empty, opens with `#`, or opens with
  a scheme ([link targets](links.md#link-targets), step 2) gives no target; a fragment-only link's
  fragment is not resolved here, [check-links](#check-links) doing that. An entry heading that
  carries more than one link gives no target.
- **pair**: in an entry with a target, an `**As it stands:**` line — outside fenced code, alone on
  its line — and the fenced block whose opening line is the next non-blank line after it, the
  pair's **from**, then a `**Becomes:**` line — outside fenced code, alone on its line — and the
  fenced block whose opening line is the next non-blank line after it, the pair's **becomes**. An
  entry without a target has no pairs. The checks below run over an entry's pairs and its heading's
  links; its other text and unlabeled fenced blocks are not checked.

Every line outside a delta is free except a level-2 heading and what the layout
([check-roadmap](#check-roadmap)) does not admit.

**The form, as checked.** The design is read in the layout ([check-roadmap](#check-roadmap)): each
breach of the layout is a breach of the design form, reported as
[check-roadmap](#check-roadmap) reports it. The delta rules add these:

| Breach | Reported at | `found` text |
|---|---|---|
| a level-2 heading that is not a delta heading but equals one when compared without regard to case, with each run of whitespace read as one space | the heading | the heading line |
| any other level-2 heading that is not a delta heading | the heading | the heading line |
| a delta heading that repeats an earlier one | the later heading | the heading line |
| a delta heading, not a repeat, that follows a delta heading the order places after it | that heading | the heading line |
| no delta heading | the H1, else line 1 of the design's first file | the line |
| a non-blank line inside a delta before its first entry, other than one the layout reports; reported once per delta, at the first such line | the line | the line |
| an entry heading that carries more than one link and whose title is not empty once its links are reduced to their text | the heading | the heading line |
| a pair label that opens no pair | the label line | the line |
| a pair's target that cannot be read | the pair's `**As it stands:**` line | the target's path |
| a pair whose from does not match | the pair's `**As it stands:**` line | the from passage's first line |
| a pair that has drifted | the pair's `**As it stands:**` line | the from passage's first line |
| a pair that is conflicting | the pair's `**As it stands:**` line | the from passage's first line |

Each form breach's accepted form is the form the Terms give, except a pair's, whose accepted text
the delta claims give.

Whether an entry's link resolves is not checked: [check-links](#check-links) does that.

**The delta claims.** The check reads each pair's target file and matches its passages against
the target's text with each run of whitespace on either side read as one space, every other
character exact. Without `--deltas-applied`, every pair's from must match; one that does not is
a breach. With `--deltas-applied`, the matching of both passages classifies each pair: from
present and becomes absent, the pair is **pending**; from absent and becomes present, it is
**landed**; both absent, it is **drifted**; both present, it is **conflicting**. A pair whose
target cannot be read has no matching to classify and is **unreadable**. An addition is a pair
whose from passage is not empty and whose becomes passage contains it: a present becomes means
landed, a present from alone means pending, and an addition is never conflicting. A pair whose
from passage contains its becomes passage is a removal: it is conflicting while its from is
present, and landed only once its from is gone. Landed is the passing state, pending the expected
mid-execution state; a drifted or conflicting pair is a breach. Each pair breach is reported at
the pair's `**As it stands:**` line, its `accepted` text `matching in <target>`; a target that
cannot be read is a breach reported there too, its `accepted` text `a readable target file`. Where
a drifted or conflicting pair's target is also the target of a landed pair of the same design, the
breach line is followed on stderr by
`interference: <target> also holds the becomes passage of a landed pair of this design`. The
checks read their targets, never write them.

**The design checked.** With `<design>`, that design. Without it, the active design of the project
root ([check-plan](#check-plan)), at the path [the project's files](kanban.md#the-projects-files)
gives; where both exist as files, the verb exits 2 before reading either.

**Output.** One stderr line per breach, in the form [check-plan](#check-plan) gives
(`<file>:<line>: <problem>: <found>; accepted: <accepted form>`), in document order. An empty
`found` text renders as [check-roadmap](#check-roadmap) gives. Current `<problem>` wording:

| Breach | `<problem>` |
|---|---|
| misspelled delta heading | `delta heading misspelled` |
| other level-2 heading | `section is not a delta` |
| repeated delta heading | `delta heading repeated` |
| delta heading out of order | `delta heading out of order` |
| no delta heading | `design has no delta` |
| content before the first entry | `delta holds content outside an entry` |
| an entry heading that carries more than one link | `entry heading carries more than one link` |
| a pair label that opens no pair | `pair is incomplete` |
| a pair's target that cannot be read | `target cannot be read` |
| a pair whose from does not match | `from not found` |
| a pair that has drifted | `pair has drifted` |
| a pair that is conflicting | `pair is conflicting` |

The summary `design checked: <design>, entries: <N>, problems: <P>` goes to stdout. With
`--deltas-applied`, one stdout line per pair, in document order,
`<file>:<line>: <state>: <target>` — `<line>` the pair's `**As it stands:**` line's number,
`<state>` one of pending, landed, drifted, conflicting, unreadable — and the summary is
`design checked: <design>, pairs: <N>, landed: <L>, pending: <G>, drifted: <D>, conflicting: <C>,
problems: <P>`. A pair counted in no state is unreadable: its count is `<N>` less the four
states' sum.

**Exit status.** As [check-plan](#check-plan)'s table, with these changes: in the row "without
`<plan>`, no active plan under the root", the message is `no active design in <root>`; the row
"without `<plan>`, both forms of the active plan exist" applies with `design` for `plan`, and its
message is `both forms of the active design exist: <monolith> and <entry-point>: remove one`; a
named design that is not a file is the usage error `no such design file: <design> (name a design's
markdown file, or a diced design's entry-point.md)`; the no-project-root message names
`devpro check-design` and `devpro check-design <design>`. A diced design's unreadable file is as a
diced plan's ([check-plan](#check-plan)), or a `.md` file beneath the entry point's directory that
a Contents link names and that cannot be read as a file: `cannot read: <file>`, exit 2. A Contents
link to anything else is ignored (Terms). With `--deltas-applied`, the verb returns 0 where every
pair has landed and no breach stands, and 1 while any pair has not landed or a breach stands:
the summary's counts and the stderr breach lines say which pairs remain, pending being the
expected mid-execution state rather than a fault of the design.

## check-roadmap

`devpro check-roadmap [<roadmap>]` checks that `ROADMAP.md` is written in the ticket layout below,
so that the board shows every ticket it holds ([the board](kanban.md#kanban)).
[check-design](#check-design) and the board read the active design in the same layout.

**Terms.** [check-plan](#check-plan)'s terms are used as defined there, with these additions:

- **category**: a level-2 heading and the lines below it, up to the next heading of level 1 or 2,
  or the end of the document.
- **ticket**: a level-3 heading inside a category, and the lines below it up to the next heading
  of level 1, 2 or 3, or the end of the document; a heading of level 4 or more inside it is part of
  its text. A ticket's **title** is the plain text ([what is a link](links.md#what-is-a-link)) of
  its heading's text ([file names and layout](tree.md#file-names-and-layout)). The lines of a
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
`ROADMAP.md`. Without it, `ROADMAP.md` under the project root ([check-plan](#check-plan)).

**Output.** One stderr line per breach, in the form [check-plan](#check-plan) gives, in line
order. An empty `found` text renders as `found an empty line`. Current `<problem>` wording:

| Breach | `<problem>` |
|---|---|
| level-3 heading outside any category | `ticket outside a category` |
| old-form item | `list item in the old ticket form` |
| empty ticket heading | `ticket heading names nothing` |
| no category | `roadmap has no category` |

The summary `roadmap checked: <roadmap>, tickets: <N>, problems: <P>` goes to stdout.

**Exit status.** As [check-plan](#check-plan)'s table, with these changes: the row "no breach,
status table or none" is "no breach"; in the row "without `<plan>`, no active plan under the
root", the condition is that `ROADMAP.md` under the root is absent or not a file, and the message
is `no roadmap in <root>`; a `<roadmap>` that is not a file is the usage error
`no such roadmap file: <roadmap> (name a roadmap's markdown file)`; the no-project-root message
names `devpro check-roadmap` and `devpro check-roadmap <roadmap>`; a file checked that cannot be
read prints `cannot read: <roadmap>`, exit 2.

## Limits

Input outside this specification is refused with a message naming what to fix, not accommodated.
Known limits:

- A source's links must be written relative to the current directory
  ([shared behaviors](index.md#shared-behaviors)); a document run from elsewhere gets mis-rebased
  links, which the [link check](#link-check) reports only if the result no longer resolves.
- A section's Contents link text ([file content](tree.md#file-content)) is not escaped: a title
  containing `]` or unbalanced brackets yields a malformed Contents link that no verb repairs.
  [check-tree](#check-tree) reports it, and [undice](verbs.md#undice) reports that section's file
  as not reproduced. The same holds for the Contents lines [the board](kanban.md#kanban) writes for
  a ticket moved into a diced design
  ([moves between Roadmap and Design](kanban.md#moves-between-roadmap-and-design)); moving such a
  ticket back to Roadmap is refused, since the head has no line linking its leaf.
- [undice](verbs.md#undice) on a volume a link map diced is best effort: links made through a link
  map come back as the map's paths, and its self-check ([undice](verbs.md#undice)) reports what does
  not round-trip.
- A project root with no name of its own, the file-system root `/`, gives the
  [board's](kanban.md#columns-and-cards) page an empty `<project>`.
- A pair's block whose closing fence is immediately followed by another opening fence reads as one
  passage to the pair reader, not the two blocks [which headings split](tree.md#which-headings-split)'s
  closer rule would give: the fence flags cannot tell the one block's closer from the other's
  opener. The two passages then match over text [check-design](#check-design) does not define as
  the pair's, and its per-pair breach lines do not say so.
