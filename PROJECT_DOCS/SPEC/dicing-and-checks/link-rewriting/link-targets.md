# Link targets

Each link's target is classified in this order:

1. **Anchor of this document** (`#frag`, where `frag` is the GitHub-style anchor of one of the
   document's headings; [anchors](anchors.md#anchors)). The target becomes the file holding that heading,
   relative to the linking file; plus `#<anchor within that file>` unless the heading is the first
   line of a non-head file. A head's own headings keep their anchor.
2. **Left unchanged:** an empty target, any other `#...` target, a target opening with `/`, and a
   target opening with a scheme: one or more lowercase ASCII letters followed by `:` (`https:`,
   `mailto:`).
3. **Any other relative path** is rebased ([shared behaviors](../index.md#dicing-and-checks)) to reach
   the same file from the directory of the file it now sits in, fragment kept.
