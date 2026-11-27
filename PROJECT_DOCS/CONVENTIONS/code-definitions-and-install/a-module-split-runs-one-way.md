# A module split runs one way

A module split runs one way: a lower module never imports the upper one it was split from. Where the
lower module needs a value the upper derives, the upper passes it in as an argument, so the lower
module's own imports name only modules at or below it — its schema, its values, the standard library.

A function-level import from the upper module is not the way back: it defers the cycle to call time
and leaves the dependency in place. `devpro/profiler/read.py` is the worked instance — `pages.py`,
which imports it, hands it the serve path's prefix and the render's context derivation rather than
the read importing them.
