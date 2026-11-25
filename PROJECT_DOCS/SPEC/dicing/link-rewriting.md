## Link rewriting

Rewriting applies to text outside fenced code and code spans only: not to lines of fenced code,
and not to text inside code spans. A code span opens at a run of backticks and closes at the next
run of the same length; an unmatched run is literal text.

### What is a link

A link is `[text](target)`: the first `]` after a `[`, immediately followed by `(`, with the target
running to the first `)`. This includes images (`![alt](target)`). No title, angle-bracket or
escape syntax is interpreted; reference-style links and autolinks are not recognised and never
rewritten.

The **plain text** of prose is that prose with each link outside code spans replaced by its text:
`[Plan Status Form](x)` reads `Plan Status Form`.

### Section references

A reference is `§` followed by digits and `.digits` groups, taken at maximal length (`§1.1.` is the
reference `§1.1`). Outside link text and code spans, each reference is handled in this order:

1. **Another document's section.** If the text just before it, on the same line, ends with
   `SPEC `, `ARCHITECTURE `, `THESIS ` or `CONVENTIONS ` (with or without `.md`), it is left as
   written and is not counted.
2. **Dangling.** If no section has that number, it is left as written and counted as dangling.
3. **Linked.** Otherwise it becomes `[§<number>](<path>)`, the path being the numbered section's
   file relative to the file the reference sits in. If the reference is directly followed by a
   space and a backticked name, and a direct child of the section has a title containing that
   backticked name, the link text extends over the name and the target is that child
   (``[§2 `beta`](...)``); with no such child only `§<number>` is linked and the name stays as
   text. The first matching child wins.

After the section pass, stderr carries one summary line:
`refs linked: <R>; dangling: <D> distinct:` followed by ` §<number>(<count>)` for each distinct
dangling number in order of first occurrence.

### Link targets

Each link's target is classified in this order:

1. **Anchor of this document** (`#frag`, where `frag` is the GitHub-style anchor of one of the
   document's headings; [anchors](#anchors)). The target becomes the file holding that heading,
   relative to the linking file; plus `#<anchor within that file>` unless the heading is the first
   line of a non-head file. A head's own headings keep their anchor.
2. **Left unchanged:** an empty target, any other `#...` target, a target opening with `/`, and a
   target opening with a scheme: one or more lowercase ASCII letters followed by `:` (`https:`,
   `mailto:`).
3. **Any other relative path** is rebased ([shared behaviors](index.md#dicing-and-checks)) to reach
   the same file from the directory of the file it now sits in, fragment kept.

### Anchors

The GitHub-style anchor of a heading (ATX, levels 1 to 6, up to three leading spaces, outside
fenced code): text with closing `#` run removed, taken as plain text
([what is a link](#what-is-a-link)), lowercased, every character that is not a letter, digit,
space, `-` or `_` deleted (letters and digits include non-ASCII ones), spaces made `-`; so
`### [Plan Status Form](x)` anchors as `plan-status-form`. The Nth repeat of an anchor in one file
takes the suffix `-<N-1>` for N>1 (`setup`, `setup-1`, `setup-2`). In the source, repeats are
counted over the whole document; in a diced file, over that file's headings alone.
