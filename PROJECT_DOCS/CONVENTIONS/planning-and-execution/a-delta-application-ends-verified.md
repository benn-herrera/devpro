### A delta application ends verified

Applying a design entry's passage pair ends with a mechanical byte-check, run before the
application's commit: each `becomes` block of the entry occurs byte-exact in its target leaf, and
where the becomes-text does not contain it, the from-text is gone rather than surviving beside it.
"Applied as written, with nothing left to interpret" has no other witness: a partial application
diffs clean against nothing and reads as done until something trusts the leaf. The runner target
that runs this check is `just check-deltas`; it exits non-zero naming each miss. It reads fences as
CommonMark does — a closer is the opener's character, at least as long — so an applied passage may
quote a fenced block.
