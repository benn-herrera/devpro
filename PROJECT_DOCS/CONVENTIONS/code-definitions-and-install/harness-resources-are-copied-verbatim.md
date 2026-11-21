### Harness resources are copied verbatim

The install stamps nothing on a file under `devpro/harnesses/resources/`, which never takes
the package loop. A consuming project receives what the source holds, an installed banner the file
already carries included, as the file's own text. That installed banner is required (SPEC.md, Write
Safety), and the source test enforces it for every file a harness ships. The loop beside it
stamps a file whose suffix is in `STAMPED_SUFFIXES` or whose name is in `STAMPED_NAMES`, a package's
files being this repository's own, so a change adding a resource must not reuse that loop just
because the walk is already there: the suffix or name says nothing about what a file already holds,
and a `.py` resource would gain a banner above its own. This tree is the master for what it ships — an installed copy is never edited,
and no other repository's copy is a source. The profiler's launcher, `claude/profiler/hp.sh`, is the
one file here `profiler init` also copies, by `launcher_resource()`, into a repository's committed
hook directory; every other file reaches a consumer through the install's copy list alone.

The two destinations differ in what the banner means: the install's copy is an installed tree's, where
`!INSTALLED!` tells the operator the source is elsewhere, while `profiler init` writes the same bytes
into a repository's own `.claude/harness-profiler/`, committed and the operator's to tune — so a future
resource copied to both must state at its banner which copy the reader holds, the installed or the
committed one.

No Python file stands under this tree: the one it carried, the profiler's `hp.py`, is gone, and the
profiler's code is the `devpro/profiler/` package, which is a devpro module like any other and inside
`just lint`'s paths by the same rule, so adding or deleting a resource no longer changes what the
lint gate covers. A resource written in Python again would pass black, isort and flake8 as well as
carrying its banner — the gate it is subject to is the module it becomes.
