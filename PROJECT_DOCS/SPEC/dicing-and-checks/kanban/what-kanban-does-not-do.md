# What kanban does not do

It makes no inference call, runs no subprocess, reads no git history and fetches nothing from the
network; every write is a fixed transformation of file content
([moves between Roadmap and Design](moves-between-roadmap-and-design.md#moves-between-roadmap-and-design)). Its only state the user
sets is a band's collapse ([columns and cards](columns-and-cards.md#columns-and-cards)); it has no filters, pull-downs,
search, sorting or custom drop affordances. The board is not a source of its own, so it changes
nothing that the page's own state could otherwise hold. The board's only writes are the moves
([moves between Roadmap and Design](moves-between-roadmap-and-design.md#moves-between-roadmap-and-design)). It does not reorder
tickets, move a ticket between categories of one document, or edit any ticket's or category's
text. The project root is found by looking at the file system
([check-plan](../reassembly.md)).
