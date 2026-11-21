"""The activity profiler: records every tool call of a coding agent session and prints the calls as a
tree, a page or a served site.

The `profiler` verb's implementation, registered by `devpro.profiler.cli.add_verbs` beside the dicing
verbs. Split by concern: `values` the schema, limits, masks and store facts every other module below
reads, `stores` those stores' rename and the names it moves from, `capture` the hook payload's parsing,
masking and record serialization, `pages` the tree, page and HTTP render, `hooks` the committed hook's
wiring — `init` and `doctor` — and `cli` the verb's dispatch and usage. Standard library only.
"""
