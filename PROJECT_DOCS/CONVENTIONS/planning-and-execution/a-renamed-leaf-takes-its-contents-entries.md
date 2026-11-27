# A renamed leaf takes its contents entries

Renaming, retitling or re-homing a leaf moves every listing that names it — the category's index
and the volume's entry-point — in the same change. `just dev-check-links` catches a listing still
naming the old path, a dead link, and a leaf dropped from the entry-point, but not one left off its
category's index, which the tree check does not read; the listing still carrying the old title
neither check reads.
