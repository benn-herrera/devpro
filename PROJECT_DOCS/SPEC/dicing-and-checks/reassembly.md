# Reassembly

Passes when the files [file names and layout](the-diced-tree/file-names-and-layout.md#file-names-and-layout) assigns, read in
section order with each entry point's and index's Contents block dropped (from its last line that
is exactly `Contents:`) and [section references](link-rewriting/section-references.md#section-references) step 3 links undone,
equal the source lines with their other links as rewritten by
[link targets](link-rewriting/link-targets.md#link-targets). A file whose top heading reads level 1 is in the rebased
form ([file content](the-diced-tree/file-content.md#file-content)) and has its heading ladder shifted back before the
compare: its top compares at its section's source level, and every other heading gains its
section's level minus 1, fenced lines compared as they stand. A file whose top reads any other
level is the pre-change form, already at the source's levels, and compares as it stands; the
pre-change form never presents a level-1 top, since no section is planned at level 1
([which headings split](the-diced-tree/which-headings-split.md#which-headings-split)). Success prints
`reassemble ok: <N> lines` to stdout; each failure prints to the verb's error stream:

| Fault | Message |
|---|---|
| line differs | `reassemble: first difference at monolith line <N> (<file>)`, then `  want: <line>` and `  got:  <line>` |
| file unreadable | `reassemble: cannot read <file>` |
| no Contents block | `reassemble: no Contents block in <file>` |
| line count | `reassemble: leaves hold <K> lines, monolith <M>` |

The check compares lines, not final newlines ([shared behaviors](../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#shared-behaviors)). Lines
added after a Contents block are not checked.
