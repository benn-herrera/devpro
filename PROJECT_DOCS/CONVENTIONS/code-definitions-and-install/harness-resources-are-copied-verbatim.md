### Harness resources are copied verbatim

The install stamps nothing on a file under `devpro/harnesses/resources/`, which never takes
the package loop. A consuming project receives what the source holds, an installed banner the file
already carries included, as the file's own text. That installed banner is required (SPEC.md, Write
Safety), and the source test enforces it for every file a harness ships. The loop beside it
stamps a file whose suffix is in `STAMPED_SUFFIXES` or whose name is in `STAMPED_NAMES`, a package's
files being this repository's own, so a change adding a resource must not reuse that loop just
because the walk is already there: the suffix or name says nothing about what a file already holds,
and a `.py` resource would gain a banner above its own. This tree is the master for what it ships — an installed copy is never edited,
and no other repository's copy is a source.

The one Python file this tree once carried, the profiler's `hp.py`, is gone: the profiler's code is
the `devpro/profiler/` package, which is a devpro module like any other and inside `just lint`'s
paths by the same rule, so adding or deleting a resource no longer changes what the lint gate covers.
The only Python under this tree is a resource nothing executes as Python, and a resource written in
Python again would pass black, isort and flake8 as well as carrying its banner — the gate it is
subject to is the module it becomes.
