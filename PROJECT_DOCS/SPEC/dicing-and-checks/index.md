# Dicing and Checks

These hold for every verb of the dicing surface ([its outcome and verbs](../../../PROJECT_DOCS/SPEC/entry-point.md));
each leaf states its verbs' contract beside them.

Contents:

- [kanban](kanban/index.md)
- [Link rewriting](link-rewriting/index.md)
- [The diced tree](the-diced-tree/index.md)
- [check-design](check-design.md)
- [check-links](check-links.md)
- [check-plan](check-plan.md)
- [check-roadmap](check-roadmap.md)
- [check-tree](check-tree.md)
- [dice](dice.md)
- [Limits](limits.md)
- [Link check](link-check.md)
- [Reassembly](reassembly.md)
- [undice](undice.md)

## Shared behaviors

A leaf of this document is a file named for its heading; a section holding sections below it is a
directory named for its heading, whose `index.md` holds the section and lists its children.

A wrong argument count, an unknown option, or an argument fault a verb's section names, is a usage
error.

**Streams.** Results and summaries go to stdout; diagnostics, warnings and failure details go to
stderr, except where a verb's section says otherwise.

**Current directory.** Relative links in a source document, and paths in a verb's output directory,
are resolved against the directory the verb runs in, its current directory, not the document's own
directory.

**Text.** Files are read and written as UTF-8 with lines split on `\n` only. A line's other bytes,
including `\r` and bytes that are not valid UTF-8, are preserved from input to output. Every line
written is terminated by `\n`, so a file whose last line was unterminated gains a final newline.

## Split level

`dice` and `undice` take the option `--split-level <level>`, which sets the
deepest split level ([which headings split](the-diced-tree/which-headings-split.md#which-headings-split)): `2`, `3` or `4`,
default `4`; any other value is a usage error.
