# File content

Each file holds, in order, exactly the source lines of its section, heading line included, with the
section's heading ladder re-based and links rewritten ([link rewriting](../index.md#dicing-and-checks)).

**The heading ladder.** A section's own text opens with its top heading, and every file of the tree
but a document's own head holds it at level 1, whatever level that heading had in the source: a
leaf's file is a document, not a fragment of one. Every other heading of the section's text moves
with it by the same shift, the top's source level minus 1, so its distance below the top is
unchanged — a `####` heading under a `##` top writes at `###`. The heading's text and its number are
not touched, so a section's file name ([file names and layout](file-names-and-layout.md#file-names-and-layout)) does not move
with the ladder. A document's own head (`entry-point.md`, or a section's `index.md`) holds its
document's title and opening text as the source has them, the title at level 1. No line inside fenced
code is a heading and none is re-based ([which headings split](which-headings-split.md#which-headings-split)).

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
  document's title ([dice](../dice.md)).
- An index lists its direct children in order, unindented, each `<path>` relative to the index's
  directory.
- A block with nothing to list is `Contents:` and a blank line.
- `<link text>` is `§<n> <title>`, where `<n>` is the number of the section itself if numbered,
  else of its nearest numbered ancestor; with no numbered section at or above, it is the title
  alone.
