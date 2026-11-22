"""The dashboard: devpro's one loopback server, serving the profiler's records and the project's board.

`cli` holds the `dashboard` verb's argparse surface and dispatch; `server` the loopback server and its
routes. The rendering is not this package's: the profiler view serves `devpro.profiler.pages`' index and
pages as they stand, and the board panel the board `devpro.dicing.kanban` models and serves.
"""
