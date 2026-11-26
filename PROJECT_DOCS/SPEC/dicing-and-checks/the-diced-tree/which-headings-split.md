# Which headings split

A heading is a line of one or more `#` at column 0 followed by a space, outside fenced code. Levels
1 to 6 are the levels a document can place; a run of seven or more is a heading still, with no
level of its own, and it is written at the level its distance below its section's top gives it
([file content](file-content.md#file-content)). A fenced
block opens at a line of at least three backticks or tildes (indentation by spaces allowed; a
backtick fence's info string holds no backtick) and closes at a line of the same character, at
least as many, followed only by spaces; an unclosed fence runs to the end of the document. No line
inside fenced code is read as a heading, table, list item or other element of any plan, design,
layout or roadmap form ([check-plan](../check-plan.md#check-plan) through
[check-roadmap](../check-roadmap.md#check-roadmap) read those forms); it is text of the part that holds it,
and its content is never read as a breach of a form.

| Level | Role |
|---|---|
| 1 | The first is the document title and stays in the entry point's text. Each later level-1 heading stays as text and is reported on stderr: `extra level-1 heading at line <N> kept as text`. |
| 2 to the deepest split level | Split into sections. |
| deeper than the deepest split level | Text. |

The **deepest split level** is the deepest heading level that splits;
[shared behaviors](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#shared-behaviors) gives the option that sets it.

A split heading's parent is the nearest preceding split heading of a lower level, or the tree's
root if none; levels may be skipped.

A section's text runs from its heading line to the line before the next split heading of any
level. The entry point's text is every line before the first split heading, or the whole document
if there is none.
