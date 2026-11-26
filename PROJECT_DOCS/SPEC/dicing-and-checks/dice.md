# dice

`devpro dice [--split-level <level>] [--section] <monolith.md>... --out <out-dir>`
dices one or more documents ([the diced tree](the-diced-tree/index.md#the-diced-tree), [link rewriting](link-rewriting/index.md#link-rewriting)) at the deepest
split level `<level>` ([shared behaviors](../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#shared-behaviors)).

**The form written.** Every document named becomes a volume ([the model](the-diced-tree/the-model.md#the-model)). One
document is written at the output root, its head `<out-dir>/entry-point.md`: this is the one-document
form. Several documents each get a
directory at the output root named for the document's base name without `.md`, holding that
volume's `entry-point.md` and its section children, and the root's `entry-point.md` is then the
omnibus's own head. With `--section` the tree is a broken-out section's: one document, its head
`<out-dir>/index.md`, and no omnibus above it.

**The omnibus's head** is a level-1 title, `# Omnibus`, and a Contents block whose every line links
a volume's `entry-point.md`, its link text the volume document's title — the plain text of its
opening level-1 heading, without its number. It carries no other line and no per-volume text: a
Contents link ends at its target, so a volume's purpose has no place there.

Order of effects and failures:

| Condition | stderr | Exit |
|---|---|---|
| a `<monolith.md>` is not a file | `not a file: <monolith.md>` | 2 |
| `<out-dir>` exists and is not a directory | `not a directory: <out-dir>` | 2 |
| `<out-dir>` exists and is not empty | `out-dir not empty: <out-dir>` | 2 |
| a document opens no level-1 heading, so its volume has no title | `volume <name>: no opening level-1 heading` | 2 |
| Planning fails ([file names and layout](the-diced-tree/file-names-and-layout.md#file-names-and-layout)) | that section's message | 1 |
| A section's heading ladder cannot be rebased ([file content](the-diced-tree/file-content.md#file-content)) | `heading too deep to rebase at line <N>: written at its monolith level`, once per offending heading | 1 |
| two documents named share a base name | `volume <name>: two documents of one name` | 2 |

A refusal writes nothing: every document is planned before anything is written, and a refusal found
there leaves `<out-dir>` untouched. Otherwise `<out-dir>` is created if absent and the tree written.
Stderr receives, per document, a `=== volume head <path>` line for its head and a `=== section <path>`
line for each section file, then the `refs linked` line
([section references](link-rewriting/section-references.md#section-references)) and any warnings of [the diced tree](the-diced-tree/index.md#the-diced-tree).
The [reassembly](reassembly.md) and [link checks](reassembly.md) then run over each
volume; their messages go to stderr and their summaries to stdout. Exit 0 only when every check
passes. Files already written remain on failure.
