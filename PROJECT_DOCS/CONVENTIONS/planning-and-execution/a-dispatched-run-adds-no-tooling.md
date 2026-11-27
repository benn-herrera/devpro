# A dispatched run adds no tooling

No run adds a package manager's lock, manifest or vendor file to the repository root — no lockfile
beside the project's one, no `node_modules/` or vendor tree, no manifest for an ecosystem the root has
none of. A tool one agent's environment happens to carry is not thereby the project's: tooling the
project has not adopted waits on the owner's decision, and a reading that would be easier under it is
a finding or a request, never a root file left in place.

The root is where the stray is silent: no recipe runs from the tool that wrote it and no test reads it
back, so it outlives the run, untracked and read by nothing, and the next session finds it and
treats it as the project's.
