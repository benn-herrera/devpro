### A delta application ends verified

Applying a design entry's passage pair ends with a mechanical byte-check: each `becomes` block
of the entry, diffed against the applied region of its target leaf, must match byte-exact, and
the check runs before the application's commit. "Applied as written, with nothing left to
interpret" has no other witness: a partial application diffs clean against nothing and reads as
done until something trusts the leaf.
