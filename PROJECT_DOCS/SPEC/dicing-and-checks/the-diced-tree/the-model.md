# The model

A diced tree has two structural patterns and no third.

- A **volume** is an original whole document, and its top document is `entry-point.md`: the tree's
  root is one, and so is each top-level directory of the omnibus form, which `dice A.md B.md T/`
  writes. Each volume's `entry-point.md` holds its document's title at level 1 and the document's
  own text above its first split heading.
- A **broken-out section** is a piece diced out of a parent, and its top document is `index.md`.
  Every other directory holding a head is one: a section that has child sections writes
  `<name>/index.md`, and the directory holds its children.

The tree's form its root head's `Contents:` block decides: the directories whose `entry-point.md`
that block links are the tree's volumes, and a root head linking none — one opening at `index.md`
included — holds a **one-document tree**, whose top-level directories are sections, whichever head
each opens at. A link in the head's prose declares nothing. Not every one-document tree is the
form `dice` writes for one document: a project document tree such as `SPEC/` is one too.

A one-document tree's sections sit below the root head, and the top-level ones among them may be
leaf documents beside it: a section with no child sections is a leaf file named for its heading,
and one with child sections a directory holding its `index.md`. Such a tree passes
[check-tree](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-tree.md#check-tree) as any other does.

A top-level directory of a volume tree is a volume's, so one opening at `index.md` stands in a
volume's place: [check-tree](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-tree.md#check-tree) reports it.

`undice` reads any directory with a head file, so a broken-out section round-trips as text without
becoming a document: its `index.md` and its children fold back into the document of the volume above
it, and `dice --section` states the identity on the way back.

No nested subvolumes: a joining document becomes a top-level volume or is subsumed and loses
separate-document identity.
