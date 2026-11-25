# check-tree

`devpro check-tree <root>...` checks diced trees. Every root must be a directory, else exit 2
(`no such directory: <roots>`). Every `.md` file under a root must be readable as a file; before
any check, each that is not prints `cannot read: <path>` to stderr and the verb exits 2. A root
without an `entry-point.md` is one problem (`<root>: no entry-point.md`).

A directory's **head** is its `entry-point.md` if present, else its `index.md`. A document's
**parent** is the head of its directory; a head's parent is the head of the directory above. For
each `.md` file under the root other than the root's `entry-point.md`:

| Problem | Message (stderr) |
|---|---|
| no parent document inside the root | `<file>: no parent document (an index.md or entry-point.md beside it or above it)` |
| parent has no link to it | `<file>: not linked from its parent <parent>` |
| not reachable by following links from the root's `entry-point.md` | `<file>: not reachable from <entry-point>` |
| a volume directory of a volume tree opens at `index.md` | `<file>: a volume directory of this tree opens at entry-point.md, not index.md: a volume's sections sit below it` |

The last problem names a [misplaced section](../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks): a tree whose root's Contents links
an `entry-point.md` below it is the omnibus form, and every top-level directory under it is a
volume's; one opening at `index.md` stands where a volume must. A tree whose root links no such head
is one document's, and its top-level directories are sections — `dice`'s one-document form and a
project document tree such as `SPEC/` both are — so none of them is reported.

Links count as in [check-links](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-links.md#check-links). The summary
`documents checked: <N>, problems: <P>` goes to stdout, summed over roots; `<N>` counts every
`.md` file under a root, its `entry-point.md` included, and a root without `entry-point.md` counts
none. Exit 1 if any problem.
