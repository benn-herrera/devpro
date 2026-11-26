# undice

`devpro undice [--split-level <level>] <tree-dir> <out-dir>` writes each document a diced tree holds
into `<out-dir>`. `<level>` ([shared behaviors](../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#shared-behaviors)) names the deepest split
level the tree was diced at; links are restored at that level. `<out-dir>` must be absent or empty.

**Which documents it writes.** One per volume ([the model](the-diced-tree/the-model.md#the-model)): for each head the
root's Contents block links below it, the document that volume holds, named for the volume's
directory — `T/A/entry-point.md` writes `<out-dir>/A.md`. A one-document tree holds one document,
named for the tree's own directory — `SPEC/entry-point.md` writes `<out-dir>/SPEC.md` — and a
broken-out section (`<tree-dir>/index.md` at the root) writes `<out-dir>/<tree-dir base name>.md`.
An `index.md`-headed directory is never a document of its own. The omnibus root's own head is not
written: it is generator output, and the volumes are the documents the tree holds.

| Condition | stderr | Exit |
|---|---|---|
| `<tree-dir>` holds neither `entry-point.md` nor `index.md` | `not a tree: <tree-dir>` | 2 |
| `<out-dir>` exists and is not a directory | `not a directory: <out-dir>` | 2 |
| `<out-dir>` exists and is not empty | `out-dir not empty: <out-dir>` | 2 |
| a head file of the tree carries text below its Contents block | `<file>: text below the Contents block at line <N>: remove it or rehome it above the Contents: line` | 2 |

One line per offending head file, `<N>` the number of the file's first line below the block.

**Content.** A volume's head lines, then each file its Contents links reach, depth first in link
order and each once; a linked file that cannot be read prints
`undice: cannot read <tree-dir>/<target>` to stderr, is left out, and fails the verb (exit 1). From
each head file read that is named `entry-point.md` or `index.md`, the Contents block is dropped
([reassembly](reassembly.md)'s cut); the head carries no text below it
([file content](the-diced-tree/file-content.md#file-content)), and text below the block is refused
before anything is written. Each other file's heading ladder is
restored before it is written: a file whose top heading reads level 1 is in the rebased form
([file content](the-diced-tree/file-content.md#file-content)) and is put back at the shallowest level its place in the
tree permits — a section file sits one level below its parent's head, so a section at the
document's first level is level 2 — and a file whose top reads any other level is the pre-change
form and is written as it stands. A place deeper than the last heading level has no document to be
restored into: the file is reported as
`undice: <document path> sits deeper than a document's last heading level`, nothing is written for
that volume, and the verb exits 1; a deeper place holds no document because level 6 is the last
heading a document has ([which headings split](the-diced-tree/which-headings-split.md#which-headings-split)). A volume's head is its document's title and opening
text, and it writes as it stands, its title at level 1. The tree does not record the level a
rebased section came from, and no two documents with the same tree can be told apart, so the
document written is the one the tree holds: it need not be the document the tree was diced from, and
it dices back to the same tree ([undice](../../../PROJECT_DOCS/SPEC/dicing-and-checks/undice.md#undice)'s round trip). Links are restored outside fenced
code and code spans, relative to `<out-dir>`:

- A section link ([section references](link-rewriting/section-references.md#section-references), step 3) becomes its link text:
  `§<number>`, or `§<number>` and the backticked name.
- A link to a heading's place in the tree, as [link targets](link-rewriting/link-targets.md#link-targets) step 1 writes
  it, becomes `#<anchor>`, the heading's anchor in the document
  ([anchors](link-rewriting/anchors.md#anchors)).
- Every other relative link is restored as [link targets](link-rewriting/link-targets.md#link-targets) step 3
  wrote it: a link to a second document becomes that document's path relative to `<out-dir>`, and
  any other path is rebased from its file's directory to `<out-dir>`, fragment kept.
  Links left unchanged by [link targets](link-rewriting/link-targets.md#link-targets) step 2 stay unchanged.

**Round trip.** For a tree as `dice` wrote it at `<level>`: move `<tree-dir>` aside, `undice` it to
`<out-dir>`, then `dice` the documents `<out-dir>` holds at `<level>`, with `--section` where the
tree is a section, from `<out-dir>` as the current directory, into `<tree-dir>`; every file of the
new tree equals the old byte for byte.

**Self-check.** After writing each document, it is planned at `<level>` ([the diced tree](the-diced-tree/index.md#the-diced-tree),
its messages to stderr as in [dice](../../../PROJECT_DOCS/SPEC/dicing-and-checks/dice.md#dice)); a planning failure exits 1 there. Otherwise the
[reassembly](reassembly.md) and [link checks](reassembly.md) run on it against its
volume, with their messages and streams as in [dice](../../../PROJECT_DOCS/SPEC/dicing-and-checks/dice.md#dice). Every `.md` file of the volume must be
one [file names and layout](the-diced-tree/file-names-and-layout.md#file-names-and-layout) assigns. Each other prints to stderr,
naming the remedy rather than applying one:

| The file | Message |
|---|---|
| was read as a section that [file names and layout](the-diced-tree/file-names-and-layout.md#file-names-and-layout) places at another path | `undice: <file> would be re-diced as <tree-dir>/<path>: rename the file or edit its heading to match` |
| was read, but opens no section | `undice: <file> opens no section: start it with a heading the document splits on (level 2 to <level> in the document, written at level 1), or remove it and its Contents line` |
| was not read | `undice: not reproduced: <file>: link it from <tree-dir>/entry-point.md's Contents, or remove it` |

A file was read when a link from a head's last `Contents:` line on resolves to it. It was read as a
section when its first line opens a section of its document other than the head; a file read more than
once was read as the first such section in document order. Contents blocks are not compared, so a
hand-edited block is regenerated by the round trip without a report. Exit 0 if all pass, else 1; the
documents are kept either way.
