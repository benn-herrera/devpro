# Limits

Input outside this specification is refused with a message naming what to fix, not accommodated.

Known limits:

- A source's links must be written relative to the current directory
  ([shared behaviors](../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#shared-behaviors)); a document run from elsewhere gets mis-rebased
  links, which the [link check](../../../PROJECT_DOCS/SPEC/dicing-and-checks/link-check.md#link-check) reports only if the result no longer resolves.
- A section's Contents link text ([file content](the-diced-tree/file-content.md#file-content)) is not escaped: a title
  containing `]` or unbalanced brackets yields a malformed Contents link that no verb repairs.
  [check-tree](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-tree.md#check-tree) reports it, and [undice](undice.md) reports that section's file
  as not reproduced. The same holds for the Contents lines [the board](kanban/index.md#kanban) writes for
  a ticket moved into a diced design
  ([moves between Roadmap and Design](kanban/moves-between-roadmap-and-design.md#moves-between-roadmap-and-design)); moving such a
  ticket back to Roadmap is refused, since the head has no line linking its leaf.
- A project root with no name of its own, the file-system root `/`, gives the
  [board's](../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks) page an empty `<project>`.
- A pair's block whose closing fence is immediately followed by another opening fence reads as one
  passage to the pair reader, not the two blocks [which headings split](the-diced-tree/which-headings-split.md#which-headings-split)'s
  closer rule would give: the fence flags cannot tell the one block's closer from the other's
  opener. The two passages then match over text [check-design](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-design.md#check-design) does not define as
  the pair's, and its per-pair breach lines do not say so.
