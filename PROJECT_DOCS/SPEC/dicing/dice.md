## dice

`devpro dice [--split-level <level>] [--section] <monolith.md>... --out <out-dir> [--map <map.tsv>]`
dices one or more documents ([the diced tree](index.md#dicing-and-checks), [link rewriting](index.md#dicing-and-checks)) at the deepest
split level `<level>` ([shared behaviors](index.md#dicing-and-checks)), using `<map.tsv>` as the link
map ([the link map](index.md#dicing-and-checks)) if given.

**The form written.** Every document named becomes a volume ([the model](index.md#dicing-and-checks)). One
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
| `--map` given and not a file | `not a file: <map.tsv>` | 2 |
| `<out-dir>` exists and is not a directory | `not a directory: <out-dir>` | 2 |
| `<out-dir>` exists and is not empty | `out-dir not empty: <out-dir>` | 2 |
| Planning fails ([file names and layout](index.md#dicing-and-checks)) | that section's message | 1 |
| A section's heading ladder cannot be re-based ([file content](index.md#dicing-and-checks)) | `heading too deep to re-base at line <N> (<level>): written at its monolith level` | 1 |
| two documents named share a base name | `volume <name>: two documents of one name` | 2 |

A refusal writes nothing: every document is planned before anything is written, and a refusal found
there leaves `<out-dir>` untouched. Otherwise `<out-dir>` is created if absent and the tree written.
Stderr receives, per document, a `=== volume head <path>` line for its head and a `=== section <path>`
line for each section file, then the `refs linked` line
([section references](index.md#dicing-and-checks)) and any warnings of [the diced tree](index.md#dicing-and-checks).
The [reassembly](reassembly.md) and [link checks](reassembly.md) then run over each
volume; their messages go to stderr and their summaries to stdout. Exit 0 only when every check
passes. Files already written remain on failure.

## undice

`devpro undice [--split-level <level>] <tree-dir> <out-dir>` writes each document a diced tree holds
into `<out-dir>`. `<level>` ([shared behaviors](index.md#dicing-and-checks)) names the deepest split
level the tree was diced at; links are restored at that level. `<out-dir>` must be absent or empty.

**Which documents it writes.** One per volume ([the model](index.md#dicing-and-checks)): for each head the
root's Contents block links below it, the document that volume holds, named for the volume's
directory — `T/A/entry-point.md` writes `<out-dir>/A.md`. A tree whose root links no head below it
holds one document, named for the tree's own directory — `SPEC/entry-point.md` writes
`<out-dir>/SPEC.md` — and a broken-out section (`<tree-dir>/index.md` at the root) writes
`<out-dir>/<tree-dir base name>.md`. An `index.md`-headed directory is never a document of its own: its
sections fold into the document of the volume above it. The omnibus root's own head is not written: it
is generator output, and the volumes are the documents the tree holds.

| Condition | stderr | Exit |
|---|---|---|
| `<tree-dir>` holds neither `entry-point.md` nor `index.md` | `not a tree: <tree-dir>` | 2 |
| `<out-dir>` exists and is not a directory | `not a directory: <out-dir>` | 2 |
| `<out-dir>` exists and is not empty | `out-dir not empty: <out-dir>` | 2 |

**Content.** A volume's head lines, then each file its Contents links reach, depth first in link
order and each once; a linked file that cannot be read prints
`undice: cannot read <tree-dir>/<target>` to stderr, is left out, and fails the verb (exit 1). From
each head file read that is named `entry-point.md` or `index.md`, the Contents block and every line
after it are dropped ([reassembly](reassembly.md)'s cut). Each other file's heading ladder is
restored before it is written: a file whose top heading reads level 1 is in the re-based form
([file content](index.md#dicing-and-checks)) and is put back at the shallowest level its place in the
tree permits — a section file sits one level below its parent's head, so a section at the
document's first level is level 2 — raised where a heading below its top would otherwise land at a
split level and split it into two sections, and a file whose top reads any other level is the
pre-change form and is written as it stands. A volume's head is its document's title and opening
text, and it writes as it stands, its title at level 1. The tree does not record the level a
re-based section came from, and no two documents with the same tree can be told apart, so the
document written is the one the tree holds: it need not be the document the tree was diced from, and
it dices back to the same tree ([undice](#undice)'s round trip). Links are restored outside fenced
code and code spans, relative to `<out-dir>`:

- A section link ([section references](index.md#dicing-and-checks), step 3) becomes its link text:
  `§<number>`, or `§<number>` and the backticked name.
- A link to a heading's place in the tree, as [link targets](index.md#dicing-and-checks) step 1 writes
  it, becomes `#<anchor>`, the heading's anchor in the document
  ([anchors](index.md#dicing-and-checks)).
- A link to a diced document the tree's link map names becomes the path the map gives, made
  relative to `<out-dir>`.
- Every other relative link is rebased from its file's directory to `<out-dir>`, fragment kept.
  Links left unchanged by [link targets](index.md#dicing-and-checks) step 2 stay unchanged.

**Round trip.** For a tree as `dice` wrote it at `<level>` without a map: move `<tree-dir>` aside,
`undice` it to `<out-dir>`, then `dice` the documents `<out-dir>` holds at `<level>`, without a map,
with `--section` where the tree is a section, from `<out-dir>` as the current directory, into
`<tree-dir>`; every file of the new tree but its link map equals the old byte for byte. The map is
generator output, keyed by the input documents' base names, which undice's own output names and
`<out-dir>` do not repeat.

**Self-check.** After writing each document, it is planned at `<level>` ([the diced tree](index.md#dicing-and-checks),
its messages to stderr as in [dice](#dice)); a planning failure exits 1 there. Otherwise the
[reassembly](reassembly.md) and [link checks](reassembly.md) run on it against its
volume, with their messages and streams as in [dice](#dice). Every `.md` file of the volume must be
one [file names and layout](index.md#dicing-and-checks) assigns. Each other prints to stderr,
naming the remedy rather than applying one:

| The file | Message |
|---|---|
| was read as a section that [file names and layout](index.md#dicing-and-checks) places at another path | `undice: <file> would be re-diced as <tree-dir>/<path>: rename the file or edit its heading to match` |
| was read, but opens no section | `undice: <file> opens no section: start it with a heading the document splits on (level 2 to <level> in the document, written at level 1), or remove it and its Contents line` |
| was not read | `undice: not reproduced: <file>: link it from <tree-dir>/entry-point.md's Contents, or remove it` |

A file was read when a link from a head's last `Contents:` line on resolves to it. It was read as a
section when its first line opens a section of its document other than the head; a file read more than
once was read as the first such section in document order. Contents blocks are not compared, so a
hand-edited block is regenerated by the round trip without a report. Exit 0 if all pass, else 1; the
documents are kept either way.
