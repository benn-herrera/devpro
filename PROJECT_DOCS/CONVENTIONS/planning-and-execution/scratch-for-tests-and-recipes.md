# Scratch for tests and recipes

Anything that renders or installs in a test or a recipe runs under a scratch `HOME`, or it reads the
operator's devpro settings file.

The mechanism is the suite's, not the recipe's: `tests/conftest.py`'s autouse `_home` fixture points
`HOME` at the test's `tmp_path` for every test, so a test sets nothing for a render or an install it
runs. The fixture is function-scoped, and a session- or module-scoped one is set up outside every
test's home: a fixture of that scope that runs `devpro install` or the CLI without `--config-file`
reaches the operator's — the install's target resolution compares the target with `Path.home()`,
and the CLI reads the default settings file under it. Such a fixture points `HOME` at a scratch
directory of its own first, as `tests/conftest.py` states. The recipes set no `HOME` of their own:
the fixture is what makes the suite's renders and installs scratch, and a recipe that runs devpro
outside pytest sets `HOME` or passes `--config-file` itself.

A probe a test writes — a copy of a shipped module with a line rewritten to export what it holds
privately, or any other file driven from outside the test — is scratch of its own: it stands outside
the state the test reads, and its path is unique to the run, so no path is one two runs share.

A test run writes its cache under the scratch directory, not the project root:
`[tool.pytest.ini_options]`'s `cache_dir` sits under `.devpro-temp/`, so `just test` leaves no
`.pytest_cache` at the root.

A package's scratch under `.devpro-temp/` is the session's to delete when the plan lands. This is a
practice the session keeps, not a control a tool enforces.
