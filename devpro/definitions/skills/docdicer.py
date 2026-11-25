"""docdicer: the skill that dices markdown into trees of small linked files, and undices them, routing
to the dicing verbs of the installation's wrapper."""

from devpro import clauses
from devpro.definition import Definition
from devpro.vocabulary import Kind

DEFINITIONS = (
    Definition(
        name="docdicer",
        kind=Kind.SKILL,
        description=(
            "Use when a markdown document is to be diced into a tree of small linked files or a diced tree "
            "undiced back into its documents, when a project's contract documents are to be diced or a diced "
            "tree's links and structure checked, when a tree's volumes and broken-out sections are to be "
            "managed, when a plan or design has grown too large to read whole, "
            "when a plan's status form, a design's final form or the roadmap's ticket form is to be checked "
            "(`check-plan`, `check-design`, `check-roadmap`), or when the project's kanban board is to be shown (`dashboard`); NOT for ordinary markdown editing, a leaf of a diced tree included."
        ),
        body=f"""## When

- **Dice** a project's contract documents when the user or the project's own documents call for it,
  and a plan or design too large to read whole. A design is diced with `--split-level 3`. Name one
  document and its tree hangs below it; name several and each becomes a volume under the omnibus
  ([the tree's patterns](#the-tree-s-patterns)).
- **Undice** a diced plan, design or document for a whole-body revision, which one document serves
  more efficiently and effectively than a tree: undicing repacks the tree into documents, not
  necessarily in the original's exact formatting, so it is no stand-in for the original where exact
  formatting matters; from then on the undiced documents and their tree convert into each other
  exactly. It writes into a directory you name, which must be absent or empty. If a document was
  modified you can re-dice it back to another tree.
- **An undice that does not dice back to the same tree** names the leaves that would dice
  differently. Fix the tree, then undice again into a new directory (the failed one stays until the
  user directs its removal). A leaf holding a heading at a level the dicer splits on: make that
  heading a bold run-in title opening its paragraph, or fold it into the text around it, changing
  no wording. A leaf whose heading disagrees with its file name: edit the heading to match the name, not the
  file, which would move the path. A changed tree shape is never the accepted cost of an undice,
  because other documents cite the tree's paths and a split moves them.
- **Check a design** with `check-design`; a diced design is checked through its `entry-point.md`.
- After each operation, both versions remain, apart from the active design's own monolith: the dice's
  passing exit retires it, because the design lives in its tree from then on (the
  `{clauses.ref(name="development")}` skill, *Plans*). Removing any other one(s) no longer wanted is
  a separate step, taken at the user's direction.

`kb-root/` and everything under it belongs to the `{clauses.optional_ref(name="kbase")}` skill: do not
dice, undice or link-check any of it unless the user directs that for it specifically.

## The tree's patterns

A diced tree has two structural patterns, and every tree you make or edit is one of them.

- A **volume** is an original whole document, and its top document is `entry-point.md`. Dicing one
  document writes a volume at the tree's root; dicing several writes each as a volume directory under
  an omnibus whose own head is `T/entry-point.md`.
- A **broken-out section** is a piece diced out of a parent, and its top document is `index.md`.

A section round-trips as text without becoming a document: undice reads any directory with a head
file, so a section's directory undices to one document with its children folded, and `dice
--section` writes it back as that same section. That is how a section is revised whole.

## The omnibus head

The omnibus's own `entry-point.md` orients the reader in the content and themes or guides
navigation, and stays concise: under 100 lines, not counting the volume listing. Two misuses count
even under the bound. *Specificity that belongs in a leaf* goes to the leaf it describes.
*Covering material that belongs to one volume* goes to that volume's `entry-point.md`. Content whose
growth would require splitting the head is misplaced the same way: needing the split is the
indication of misuse, and the remedy is moving the content, never splitting the file.

## Splitting a leaf

A leaf that has outgrown its place splits one of two ways, and the growth's shape decides which.

- **Simple fission** — a leaf that has grown laterally, denser or accumulated coverage at the same
  logical level, splits into sibling leaves. This covers entry-point content too.
- **Sub-dicing** — a leaf that has grown hierarchically, subtopics getting covered of their own,
  breaks out a new subdirectory with `index.md`. At the omnibus root that sub-dicing is a new volume,
  with `entry-point.md`.

Hierarchical subtopics sub-dice; lateral accumulation fissures.

## The verbs

{clauses.WRAPPER}

Dice, undice and check through the dicing verbs, run from the command line through `DP`: `DP dice`,
`DP undice` and the check verbs (`check-links`, `check-tree`, `check-plan`, `check-design`,
`check-roadmap`). The verbs' `--help` is the command list, and this skill does not restate it.

Where the project's runner includes the `devpro` snippet set, the checks run through its recipes:
`devpro-help`, and the four gates `devpro-check-plan`, `devpro-check-design`,
`devpro-check-design-deltas-applied` and `devpro-check-roadmap`, which take no argument, each
checking the active file under the project root — the active plan, the active design, the active
design's applied deltas and `ROADMAP.md` — with a direct call through `DP` for any other.

`DP dashboard [<project-dir>] [--port <number>]` serves the project's development surface on
`127.0.0.1` and prints the URL: it opens on the board of its roadmap, design and plan, the
dashboard's board panel at `/board/` (the root answers a redirect to it), and the profiler view at
`/profiler/` lists the session records, each linking to its own page. Offer to run it as a background
process, or hand the user the command line; the
user chooses. It serves until the user asks for it to stop — Ctrl-C, or the board page's stop button
— and it never finishes, so a dispatched agent hands over the command line instead of running it.""",
    ),
)
