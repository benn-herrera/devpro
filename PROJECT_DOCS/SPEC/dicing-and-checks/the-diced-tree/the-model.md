# The model

A diced tree has two structural patterns and no third.

- A **volume** is an original whole document, and its top document is `entry-point.md`. The tree's
  root is a volume, and so is each directory directly under the root that holds an
  `entry-point.md` — the omnibus form `dice A.md B.md T/` writes. Each volume's `entry-point.md`
  holds its document's title at level 1 and the document's own text above its first split heading.
- A **broken-out section** is a piece diced out of a parent, and its top document is `index.md`.
  Every other directory holding a head is one: a section that has child sections writes
  `<name>/index.md`, and the directory holds its children.

Which pattern a directory is follows from the tree, never from the file. A one-document tree — the
form `dice` writes for one document, and the form of a project document tree such as `SPEC/` — has
no volume directory: its root's `entry-point.md` holds its document and its sections sit beneath it,
the top-level ones among them being sections, not misplaced volumes. A volume tree's top-level
directories are volumes; one opening at `index.md` is a section in a volume's place, and
[check-tree](../check-tree.md#check-tree) reports it.

`undice` reads any directory with a head file, so a broken-out section round-trips as text without
becoming a document: its `index.md` and its children fold back into the document of the volume above
it, and `dice --section` states the identity on the way back.

No nested subvolumes: a joining document becomes a top-level volume or is subsumed and loses
separate-document identity.
