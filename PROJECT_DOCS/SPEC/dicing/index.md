## Shared behaviors

These hold for every verb of the dicing surface ([its outcome and verbs](../entry-point.md));
each leaf states its verbs' contract beside them.

Contents:

- [The diced tree](tree.md)
- [Link rewriting](links.md)
- [Dicing verbs](verbs.md)
- [The checks](checks.md)
- [The board](kanban.md)

A wrong argument count, an unknown option, or an argument fault a verb's section names, is a usage
error.

**Streams.** Results and summaries go to stdout; diagnostics, warnings and failure details go to
stderr, except where a verb's section says otherwise.

**Current directory.** Relative links in a source document, and paths in a link map or a verb's
output directory, are resolved against the directory the verb runs in, its current directory, not
the document's own directory.

**Text.** Files are read and written as UTF-8 with lines split on `\n` only. A line's other bytes,
including `\r` and bytes that are not valid UTF-8, are preserved from input to output. Every line
written is terminated by `\n`, so a file whose last line was unterminated gains a final newline.

**Split level.** `dice` and `undice` take the option `--split-level <level>`, which sets the
deepest split level ([which headings split](tree.md#which-headings-split)): `2`, `3` or `4`,
default `4`; any other value is a usage error.
