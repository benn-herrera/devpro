# The code is devpro's.

The port is a devpro package, `devpro/profiler/`, standard library only,
no dependency: `values.py` the schema, limits, masks and store facts every other module reads,
`capture.py` the hook payload's parsing, masking and record serialization, `pages.py` the tree and
page render, `hooks.py` the committed hook's wiring — `init` and `doctor` — `stores.py` the stores'
rename and their one repair, and `cli.py` the `profiler` verb's dispatch. The verb is dispatched
lazily: registering it imports none of these modules, and `cli.py` imports the one whose subcommand
runs. Its subcommands are `capture`, `tree`, `init`, `doctor` and `repair`; the records are served by
the `dashboard` verb, below.

