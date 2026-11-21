### A delta application ends verified

Applying a design entry's passage pair ends with a mechanical byte-check, run before the
application's commit: each `becomes` block of the entry occurs in its target leaf with each run of
whitespace read as one space and every other character exact, and where the becomes-text does not
contain it, the from-text is gone rather than surviving beside it.
"Applied as written, with nothing left to interpret" has no other witness: a partial application
diffs clean against nothing and reads as done until something trusts the leaf. The runner target
that runs this check is `just dev-check-design-deltas-applied`, which runs `python3 -m devpro
check-design --deltas-applied`, exiting non-zero naming each miss. `check-design` without the flag requires each pair's from-text still to match its target,
so it reads a design before its application and never after; the applied state is
`--deltas-applied`'s to report. It reads fences as CommonMark does — a closer is the opener's
character, at least as long — so an applied passage may quote a fenced block.
