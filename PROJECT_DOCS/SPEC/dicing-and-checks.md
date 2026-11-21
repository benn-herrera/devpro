## Dicing and Checks

devpro carries the dicing surface of the docdicer project: it turns large markdown documents into
trees of small linked files, checks development plans, designs and roadmaps, and shows them as a
board. The verbs and their `--help` are the offered surface; this section states the outcomes any
implementation of them is held to.

The verbs are `devpro dice-doc`, `devpro undice`, `devpro dice-docs`,
`devpro check-links`, `devpro check-tree`, `devpro check-plan`, `devpro check-design`,
`devpro check-roadmap` and `devpro kanban`. `devpro --version` prints the version; `-h`, alone or
after a verb, prints help. The verbs run where the `devpro` command runs: the devpro package on the
host is the dicing surface's prerequisite, the operator's to install.

Every verb exits 0 on success, 1 where its check or dicing failed, and 2 on a usage error or a
refusal; `kanban` serves until interrupted and exits 0 either way. Results and summaries go to
stdout, diagnostics to stderr. The round-trip check — the monolith re-diced, the tree reassembled,
the links resolved — is the dicing's own commit gate, not an offered verb.

Six outcomes hold:

- **Navigable.** Every entry point and index lists the files directly below it, so the tree's entry
  point leads to every file; `check-tree` verifies this.
- **Lossless.** Each line of the source appears in exactly one file, unaltered except for link
  rewriting; a dicing whose verification fails exits 1.
- **Linked.** Cross references in the source (`§N`, `#anchor`, relative paths) resolve in the tree;
  `check-links` verifies this.
- **Repeatable.** For every verb but `kanban`, equal inputs give equal trees and messages, and
  nothing depends on the clock, the network, or any state outside the named inputs.
- **Non-destructive.** No verb modifies a source document, except that `kanban` moves tickets
  between `ROADMAP.md` and the active design, in either direction, adds a parked card's link ticket
  to the active design, and removes a link ticket from it.
- **Reversible.** A tree `dice-doc` wrote can be written back to a document that dices to the same
  tree.

The check verbs read the forms SPEC.md, Plan Status Form states: `check-plan` the plan's status
table, `check-design` a design's final form and its delta pairs against their targets, and
`check-roadmap` the roadmap's ticket layout. Without a file argument each checks the active file
under the project root — the nearest directory at or above the current one holding a `.git` entry;
`kanban` serves that project. The full contract of each verb — the diced-tree format, link
rewriting, the link map, the manifest, the checks' reports and the board's moves — is this
section's: the stage-1 plan carries it over from the contract documents the absorbed project held,
stated in this section and its section's own leaves, and no document outside this tree holds any
verb's contract.

Contents:

- [Shared behaviors and the leaves](dicing/index.md)
- [The diced tree](dicing/tree.md)
- [Link rewriting](dicing/links.md)
- [Dicing verbs](dicing/verbs.md)
- [The checks](dicing/checks.md)
- [The board](dicing/kanban.md)
