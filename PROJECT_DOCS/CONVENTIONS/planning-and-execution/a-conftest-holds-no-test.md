# A conftest holds no test

No function in a `conftest.py` starts with `test_`. The file carries fixtures and bare-named
helpers, and no test function: pytest collects a `conftest.py` while it walks the directories, and
collects no test from it, so a test-shaped function there never runs — `just lint` fails on one
rather than the suite run it.

A test-shaped function found there is one of three things, and each has one fix: a duplicate of a
test a `test_*.py` collects, deleted; a helper carrying a test's prefix, renamed for the job it does;
or a zombie asserting machinery the code no longer has, deleted. A test that needs fixture-only setup
keeps its body a bare-named function in the `conftest.py` and its `test_` function in the
`test_*.py`, which calls it.
