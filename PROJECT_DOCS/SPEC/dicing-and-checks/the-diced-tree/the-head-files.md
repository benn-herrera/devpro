# The head files

A tree's head files are fixed by convention and never configurable: a reader moving between projects
relies on finding them, and the standing project trees carry the same rule. The constant names are
`entry-point.md` for a volume's head and `index.md` for a broken-out section's
([shared behaviors](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks) names the module that holds them).

- A head's Contents block opens at its last line that is exactly `Contents:`; its lines are each
  `- [<link text>](<path>)`, indented by spaces as [file content](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/the-diced-tree/file-content.md#file-content) gives them.
- `check-tree` reads a directory's head as its `entry-point.md` where it has one, else its
  `index.md`; a tree's root must open at `entry-point.md`
  ([check-tree](../reassembly.md)).
- `undice` reads a tree's root at whichever of the two it holds, so a broken-out section undices as
  its own document ([undice](../dice.md)).
