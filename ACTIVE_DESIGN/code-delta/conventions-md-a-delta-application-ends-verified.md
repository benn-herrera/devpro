### [CONVENTIONS.md, Planning and execution, A delta application ends verified](../../PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md)

`devtools/check_deltas.py` reads a design's entries from the design's one source: the leaves of the
diced tree where the design was diced — each leaf one entry — and the undiced document where it was
not. A diced design keeps no monolith beside its tree: the tree is the single source, and the active
design's monolith (`ACTIVE_DESIGN.md`) retires when this change lands. Decision (user): the check
reads the diced document, not a monolith kept beside it — holding both is a single-source-of-truth
violation.
