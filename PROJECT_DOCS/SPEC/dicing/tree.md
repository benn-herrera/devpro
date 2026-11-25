## The diced tree

File names, the files a verb writes and their content, exit statuses and the stream each message
goes to are contract. What is contract in a message is which fault or result it reports, the values
it carries, shown in `<angle brackets>` (a file, a line, a heading, a count), and the remedy it
names. The wording itself is not: the messages below give current wording, which the tests pin as
they stand.

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
| Tree root (the output directory) | `entry-point.md` |
| Has child sections | `<parent dir>/<name>/index.md` |
| No child sections | `<parent dir>/<name>.md` |

**Errors, all exit 1 with nothing written to the tree** (the output directory may be left created
and empty):

- `empty slug for heading at line <N>`: reported for the first such heading only.
- `path collision: <path> (lines <A> and <B>)`: two sections would write the same path. Every
  collision is reported, each against the previous holder of the path.

**Duplicate numbers.** Headings sharing a number are reported on stderr as
`duplicate section number <number>`, once per `dice-doc`, per `undice` and per volume
[dice-docs](verbs.md#dice-docs-and-the-manifest) dices. Dicing continues; a reference to the number
resolves to the last heading that carries it
([section references](links.md#section-references)).

### File content

Each file holds, in order, exactly the source lines of its section, heading line included, with the
section's heading ladder re-based and links rewritten ([link rewriting](links.md)).

**The heading ladder.** A section's own text opens with its top heading, and every file of the tree
but the entry point holds it at level 1, whatever level that heading had in the source: a leaf's
file is a document, not a fragment of one. Every other heading of the section's text moves with it
by the same shift, the top's source level minus 1, so its distance below the top is unchanged — a
`####` heading under a `##` top writes at `###`. The heading's text and its number are not touched,
so a section's file name ([file names and layout](#file-names-and-layout)) does not move with the
ladder. The entry point's own text is the source's, its title at its own level. No line inside
fenced code is a heading and none is re-based ([which headings split](#which-headings-split)).

A section whose text holds a heading that this shift would carry above level 1 or below level 6 has
no ladder the tree can hold: it is reported as
`heading too deep to re-base at line <N> (<level>): written at its monolith level`, written at its
source levels, and the verb exits 1.

The entry point and every index end with a **Contents block** appended directly after the section's
own lines (no separator line is added):

```markdown
Contents:

- [<link text>](<path>)
```

- The entry point lists every other section in document order, one line each, indented two spaces
  per depth below the first level, each `<path>` relative to the tree root.
- An index lists its direct children in order, unindented, each `<path>` relative to the index's
  directory.
- A block with nothing to list is `Contents:` and a blank line.
- `<link text>` is `§<n> <title>`, where `<n>` is the number of the section itself if numbered,
  else of its nearest numbered ancestor; with no numbered section at or above, it is the title
  alone.
