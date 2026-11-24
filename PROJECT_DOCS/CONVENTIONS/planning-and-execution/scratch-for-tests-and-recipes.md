### Scratch for tests and recipes

Anything that renders or installs in a test or a recipe runs under a scratch `HOME`, or it reads the
operator's devpro settings file.

A test run writes its cache under the scratch directory, not the project root:
`[tool.pytest.ini_options]`'s `cache_dir` sits under `.devpro-temp/`, so `just test` leaves no
`.pytest_cache` at the root.

A package's scratch under `.devpro-temp/` is the session's to delete when the plan lands. This is a
practice the session keeps, not a control a tool enforces.
