# Link targets

Each link's target is classified in this order:

1. **Anchor of this document** (`#frag`, where `frag` is the GitHub-style anchor of one of the
   document's headings; [anchors](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/link-rewriting/anchors.md#anchors)). The target becomes the file holding that heading,
   relative to the linking file; plus `#<anchor within that file>` unless the heading is the first
   line of a non-head file. A head's own headings keep their anchor.
2. **Left unchanged:** an empty target, any other `#...` target, a target opening with `/`, and a
   target opening with a scheme: one or more lowercase ASCII letters followed by `:` (`https:`,
   `mailto:`).
3. **Any other relative path** that names a second document given to the same `dice` run becomes a
   link to that document's head: the tree path of that head, fragment dropped, wherever the file the
   link sits in stands in the tree. Any other relative path is rebased
   ([shared behaviors](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#shared-behaviors)) to reach the same file from the directory of the file it now sits in,
   fragment kept.
