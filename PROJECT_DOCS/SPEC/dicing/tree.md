## The diced tree

File names, the files a verb writes and their content, exit statuses and the stream each message
goes to are contract. What is contract in a message is which fault or result it reports, the values
it carries, shown in `<angle brackets>` (a file, a line, a heading, a count), and the remedy it
names. The wording itself is not: the messages below give current wording, which the tests pin as
they stand.

### The model

A diced tree has two structural patterns and no third.

- A **volume** is an original whole document, and its top document is `entry-point.md`. The tree's
  root is a volume, and so is each directory directly under the root that holds an
  `entry-point.md` — the omnibus form `dice A.md B.md T/` writes. Each volume's `entry-point.md`
  holds its document's title at level 1 and the document's own text above its first split heading.
- A **broken-out section** is a piece diced out of a parent, and its top document is `index.md`.
  Every other directory holding a head is one: a section that has child sections writes
  `<name>/index.md`, and the directory holds its children.

Which pattern a directory is follows from the tree, never from the file. A one-document tree — the
form `dice` writes for one document, and the form of a project document tree such as `SPEC/` — has
no volume directory: its root's `entry-point.md` holds its document and its sections sit beneath it,
the top-level ones among them being sections, not misplaced volumes. A volume tree's top-level
directories are volumes; one opening at `index.md` is a section in a volume's place, and
[check-tree](checks.md#check-tree) reports it.

`undice` reads any directory with a head file, so a broken-out section round-trips as text without
becoming a document: its `index.md` and its children fold back into the document of the volume above
it, and `dice --section` states the identity on the way back.

No nested subvolumes: a joining document becomes a top-level volume or is subsumed and loses
separate-document identity.

### The head files

A tree's head files are fixed by convention and never configurable: a reader moving between projects
relies on finding them, and the standing project trees carry the same rule. The constant names are
`entry-point.md` for a volume's head and `index.md` for a broken-out section's
([shared behaviors](index.md#shared-behaviors) names the module that holds them).

- A head's Contents block opens at its last line that is exactly `Contents:`; its lines are each
  `- [<link text>](<path>)`, indented by spaces as [file content](#file-content) gives them.
- `check-tree` reads a directory's head as its `entry-point.md` where it has one, else its
  `index.md`; a tree's root must open at `entry-point.md`
  ([check-tree](checks.md#check-tree)).
- `undice` reads a tree's root at whichever of the two it holds, so a broken-out section undices as
  its own document ([undice](verbs.md#undice)).

### Which headings split

A heading is a line of 1 to 6 `#` at column 0 followed by a space, outside fenced code. A fenced
block opens at a line of at least three backticks or tildes (indentation by spaces allowed; a
backtick fence's info string holds no backtick) and closes at a line of the same character, at
least as many, followed only by spaces; an unclosed fence runs to the end of the document. No line
inside fenced code is read as a heading, table, list item or other element of any plan, design,
layout or roadmap form ([check-plan](checks.md#check-plan) through
[check-roadmap](checks.md#check-roadmap) read those forms); it is text of the part that holds it,
and its content is never read as a breach of a form.

| Level | Role |
|---|---|
| 1 | The first is the document title and stays in the entry point's text. Each later level-1 heading stays as text and is reported on stderr: `extra level-1 heading at line <N> kept as text`. |
| 2 to the deepest split level | Split into sections. |
| deeper than the deepest split level | Text. |

The **deepest split level** is the deepest heading level that splits;
[shared behaviors](index.md#shared-behaviors) gives the option that sets it.

A split heading's parent is the nearest preceding split heading of a lower level, or the tree's
root if none; levels may be skipped.

A section's text runs from its heading line to the line before the next split heading of any
level. The entry point's text is every line before the first split heading, or the whole document
if there is none.

### File names and layout

The heading text is what follows the `#` run, with leading and trailing spaces removed. A heading
is **numbered** when the plain text ([what is a link](links.md#what-is-a-link)) of its heading text
opens with digits optionally followed by `.digits` groups, an optional `.`, and a space (`1.`, `2 `,
`1.1.1.`). Its **number** is that prefix without the trailing `.`; its **title** is the rest. An
unnumbered heading's title is its whole plain text: `### [Plan Status Form](x)` is titled
`Plan Status Form`.

The **slug** of a title: ASCII uppercase lowered, backticks deleted, every maximal run of
characters outside `a-z0-9` replaced by one `-`, leading and trailing `-` removed. Non-ASCII
letters are separators, not transliterated.

The **name** of a section: `<number>-<slug>` when numbered with a non-empty slug; `<number>` when
numbered with an empty slug; `<slug>` when unnumbered. An unnumbered heading with an empty slug is
an error.

| Section | Path |
|---|---|
| Tree root (the output directory) | `entry-point.md`; `index.md` where `--section` writes it |
| Has child sections | `<parent dir>/<name>/index.md` |
| No child sections | `<parent dir>/<name>.md` |
| A volume directory (`dice` with several documents) | `<out dir>/<document base name>/entry-point.md` |

**Errors, all exit 1 with nothing written to the tree** (the output directory may be left created
and empty):

- `empty slug for heading at line <N>`: reported for the first such heading only.
- `path collision: <path> (lines <A> and <B>)`: two sections would write the same path. Every
  collision is reported, each against the previous holder of the path.

**Duplicate numbers.** Headings sharing a number are reported on stderr as
`duplicate section number <number>`, once per document `dice` dices and per document `undice`
writes. Dicing continues; a reference to the number resolves to the last heading that carries it
([section references](links.md#section-references)).

### File content

Each file holds, in order, exactly the source lines of its section, heading line included, with the
section's heading ladder re-based and links rewritten ([link rewriting](links.md)).

**The heading ladder.** A section's own text opens with its top heading, and every file of the tree
but a document's own head holds it at level 1, whatever level that heading had in the source: a
leaf's file is a document, not a fragment of one. Every other heading of the section's text moves
with it by the same shift, the top's source level minus 1, so its distance below the top is
unchanged — a `####` heading under a `##` top writes at `###`. The heading's text and its number are
not touched, so a section's file name ([file names and layout](#file-names-and-layout)) does not move
with the ladder. A document's own head (`entry-point.md`, or a section's `index.md`) holds its
document's title and opening text as the source has them, the title at level 1. No line inside fenced
code is a heading and none is re-based ([which headings split](#which-headings-split)).

A section whose text holds a heading that this shift would carry above level 1 or below level 6 has
no ladder the tree can hold: it is reported as
`heading too deep to re-base at line <N> (<level>): written at its monolith level`, written at its
source levels, and the verb exits 1.

The head and every index end with a **Contents block** appended directly after the section's
own lines (no separator line is added):

```markdown
Contents:

- [<link text>](<path>)
```

- A document's head lists every other section of its document in document order, one line each,
  indented two spaces per depth below the first level, each `<path>` relative to the head's
  directory. The omnibus's own head lists each volume's `entry-point.md`, its link text the volume
  document's title ([dice](verbs.md#dice)).
- An index lists its direct children in order, unindented, each `<path>` relative to the index's
  directory.
- A block with nothing to list is `Contents:` and a blank line.
- `<link text>` is `§<n> <title>`, where `<n>` is the number of the section itself if numbered,
  else of its nearest numbered ancestor; with no numbered section at or above, it is the title
  alone.
