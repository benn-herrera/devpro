# Harness resources are copied verbatim

The install stamps nothing on a file under `devpro/harnesses/resources/`, which never takes
the package loop. A consuming project receives what the source holds, an installed banner the file
already carries included, as the file's own text. That installed banner is required (SPEC.md, Write
Safety), and the source test enforces it for every file a harness ships. The loop beside it
stamps a file whose suffix is in `STAMPED_SUFFIXES` or whose name is in `STAMPED_NAMES`, a package's
files being this repository's own, so a change adding a resource must not reuse that loop just
because the walk is already there: the suffix or name says nothing about what a file already holds,
and a `.py` resource would gain a banner above its own. This tree is the master for what it ships — an installed copy is never edited,
and no other repository's copy is a source. Every file here reaches a consumer through the install's
copy list alone, and the installed copy carries the banner that says so: `!INSTALLED!` tells the
operator the source is elsewhere, and the *do not edit* it states is the copy's, so the copy is never
the operator's to tune.

No Python file stands under this tree: the one it carried, the profiler's `hp.py`, is gone, and the
profiler's code is the `devpro/profiler/` package, which is a devpro module like any other. A resource written in Python again would pass black, isort and flake8 as well as
carrying its banner — the gate it is subject to is the module it becomes.

A resource written in TypeScript, `opencode/profiler.ts` among them, is held by its tests and by the
type check `just lint` runs over the opencode harness's resources: it ships verbatim, and what the
shipped text does is held to the host's own declarations ([A host version is checked against the
host's declarations](a-host-version-is-checked-against-the-host-s-declarations.md)).
