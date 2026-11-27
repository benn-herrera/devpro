# Section references

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
