### A devtools tool joins the tests

A module added under `devtools/` arrives with its test under `devtools/tests/` in the same change, as
`render_diff`, `clause_join_sites` and `check_deltas` do. Nothing else reaches it: the `test-changed`
surface map and `sweep-python` pass over an untested devtools module, so a tool whose failing mode is
a wrong verdict ships green and stays green.
