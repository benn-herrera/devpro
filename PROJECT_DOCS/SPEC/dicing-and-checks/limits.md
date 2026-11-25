# Limits

Input outside this specification is refused with a message naming what to fix, not accommodated.
Known limits:

- A source's links must be written relative to the current directory
  ([shared behaviors](index.md#dicing-and-checks)); a document run from elsewhere gets mis-rebased
  links, which the [link check](link-check.md#link-check) reports only if the result no longer resolves.
- A section's Contents link text ([file content](index.md#dicing-and-checks)) is not escaped: a title
  containing `]` or unbalanced brackets yields a malformed Contents link that no verb repairs.
  [check-tree](check-tree.md#check-tree) reports it, and [undice](dice.md) reports that section's file
  as not reproduced. The same holds for the Contents lines [the board](index.md#dicing-and-checks) writes for
  a ticket moved into a diced design
  ([moves between Roadmap and Design](index.md#dicing-and-checks)); moving such a
  ticket back to Roadmap is refused, since the head has no line linking its leaf.
- A project root with no name of its own, the file-system root `/`, gives the
  [board's](index.md#dicing-and-checks) page an empty `<project>`.
- A pair's block whose closing fence is immediately followed by another opening fence reads as one
  passage to the pair reader, not the two blocks [which headings split](index.md#dicing-and-checks)'s
  closer rule would give: the fence flags cannot tell the one block's closer from the other's
  opener. The two passages then match over text [check-design](check-design.md#check-design) does not define as
  the pair's, and its per-pair breach lines do not say so.
