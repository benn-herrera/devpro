# The code belongs to devpro

The port is a devpro package, `devpro/profiler/`, standard library only,
no dependency: `values.py` the schema, limits, masks and store facts every other module reads,
`capture.py` the hook payload's parsing, masking and record serialization, `directives.py` the stamp's
directive walk, digest and manifest, `read.py` the stores' read and the dispatch hierarchy `Depth`
threads to the render, `pages.py` the tree and page render, `hooks.py` the committed hook's wiring —
`init` — `stores.py` the stores' rename, and `cli.py` the `profiler` verb's dispatch. The verb is dispatched
lazily: registering it imports none of these modules, and `cli.py` imports the one whose subcommand
runs. Its subcommands are `capture`, `tree` and `init`; the records are served by
the `dashboard` verb, below.
