# The plan columns are read-only

The cards in the plan columns cannot be dragged, and nothing can be dropped on a plan column. The
page shows this on sight: the plan columns, their cards and the Design column's entry cards are
visibly set apart, by form and not by colour alone, from the cards that can be dragged, which are
the Roadmap column's cards and the Design column's other cards. Neither an entry card nor a
separator can be dragged; a separator is drawn as a band, not as a card. A work package's state
changes only by an edit to the plan file, which the board shows
([live following](live-following.md#live-following)).

**Drops not accepted.** The only drops accepted are a roadmap or parked card on Design and a design
card other than an entry card on Roadmap (both
[moves between Roadmap and Design](moves-between-roadmap-and-design.md#moves-between-roadmap-and-design)). Any other drop is not
accepted and the card returns to its column. A departure from the common path, such as a plan with
no design or a skipped step, is not refused for being one (only the moves'
**Refusals** refuse a move) and never asks for confirmation.
