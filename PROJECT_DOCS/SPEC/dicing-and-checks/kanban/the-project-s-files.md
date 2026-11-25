# The project's files

Under the project root the files are at fixed paths; nothing relocates them.

| Document | Path |
|---|---|
| roadmap tickets ([check-roadmap](../reassembly.md)) | `ROADMAP.md` |
| **active design** | `ACTIVE_DESIGN.md`, else `ACTIVE_DESIGN/entry-point.md` |
| active plan ([check-plan](../reassembly.md)) | `ACTIVE_PLAN.md`, else `ACTIVE_PLAN/entry-point.md` |
| **parked-designs directory** | `ROADMAP_DESIGNS/` |
| **project-documents directory** (where present) | `PROJECT_DOCS/` |

Where both forms of the active design or the active plan exist, the board reads the monolith.
**Parked work** is each `.md` file in the parked-designs directory other than `README.md`, a
**parked file**, and each subdirectory there holding its own `entry-point.md`, a **parked tree**.
Each has a **parked name**: a parked file's name without `.md`, a parked tree's directory name. A
parked name `<topic>_DESIGN`, `<topic>_PLAN` or `<topic>_PLAN_REVIEW` makes `<topic>` a **topic**.
A parked name that is `<topic>` or opens with `<topic>_` joins that topic, the longest where it
could join more than one. The parked files and trees of one topic are one **piece of parked work**,
whose parked name is `<topic>`; each other parked file or tree is a piece of its own, keeping its
parked name. A piece's **files** are its parked files and its parked trees' `entry-point.md`, in
order of their paths. A **link ticket** is a ticket of the active design, outside any delta, for a
piece of parked work that no roadmap ticket links, whose lines are exactly `### <name>`, a blank
line, a line `[<path>](<link>)` for each of the piece's files, in order, a blank line and
`complete and update this design`, where `<name>` is the piece's parked name, each `<path>` a
file's path from the project root and its `<link>` that path relative to the directory of the file
holding the ticket. A document that is absent contributes no cards; a project with none of them
shows an empty board.
