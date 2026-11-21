"""docdicer: the skill that dices markdown into trees of small linked files, and undices them, routing
to the dicing verbs of the `devpro` command."""

from devpro import clauses
from devpro.definition import Definition
from devpro.vocabulary import Kind

DEFINITIONS = (
    Definition(
        name="docdicer",
        kind=Kind.SKILL,
        description=(
            "Use when a markdown document is to be diced into a tree of small linked files or a diced tree "
            "undiced back into one document, when a project's contract documents are to be diced or a diced "
            "tree's links and structure checked, when a plan or design has grown too large to read whole, "
            "when a plan's status form, a design's final form or the roadmap's ticket form is to be checked "
            "(`check-plan`, `check-design`, `check-roadmap`), or when the project's kanban board is to be shown (`kanban`); NOT for ordinary markdown editing, a leaf of a diced tree included."
        ),
        body=f"""## When

- **Dice** a project's contract documents when the user or the project's own documents call for it,
  and a plan or design too large to read whole. A design is diced with `--split-level 3`.
- **Undice** a diced plan, design or document for a whole-body revision, which one document serves
  more efficiently and effectively than a tree: undicing repacks the tree into one monolith document,
  not necessarily in the original's exact formatting, so it is no stand-in for the original where
  exact formatting matters; from then on the undiced document and its tree convert into each other
  exactly. General process: undice to a new monolithic document (it will not overwrite an existing one).
  If the monolith was modified you can re-dice it back to another doc tree.
- **An undice that does not dice back to the same tree** names the leaves that would dice
  differently. Fix the tree, then undice again to a new monolith name (the failed one stays until
  the user directs its removal). A leaf holding a heading at a level the dicer splits on: make that
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

## The verbs

Dice, undice and check through the dicing verbs of the `devpro` command, run from the command line:
`devpro dice-doc`, `devpro undice`, the check verbs (`check-links`, `check-tree`, `check-plan`,
`check-design`, `check-roadmap`) and `devpro kanban`. The verbs' `--help` is the command list, and
this skill does not restate it.

`kanban` serves a live board of the project's roadmap, design and plan. Offer to run it as a
background process, or hand the user the command line; the user chooses. It serves until the user
asks for it to stop, and it never finishes, so a dispatched agent hands over the command line
instead of running it.""",
    ),
)
