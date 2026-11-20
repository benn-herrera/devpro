### [CONVENTIONS.md, Planning and execution, A delta application ends verified](../../PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-verified.md)

`devtools/check_deltas.py` reads a design's entries from the design's one source: the leaves of the
diced tree where the design was diced — each leaf one entry — and the undiced document where it was
not. A diced design keeps no monolith beside its tree: the dicer's successful exit — its reassembly
and link checks green — is the monolith's retirement, and the tree is the single source from then on.
The active design's monolith (`ACTIVE_DESIGN.md`) outlived its dice only because the byte-check could
not yet read the tree; it retires when this change lands. Decision (user): the check
reads the diced document, not a monolith kept beside it — holding both is a single-source-of-truth
violation. Both present is a failure, not an ambiguity to resolve: where a design's monolith and its
tree both exist, `check-design` and `check-plan` report it as a problem. That enforcement is
docdicer's — the pinned package the launcher installs (`devpro/docdicer-tools/docdicer`,
`git+https://github.com/benn-herrera/docdicer@v0.11.2`) — so it lands with a docdicer change and this
repository's pin bump; until then the rule above carries it.
