# An installation that runs its own devpro, and the surface and modules around it

A devpro installation runs its own copy of devpro, untouched by the system's until the next
`devpro install`. Its surface keeps only what users reach, and its modules depend in one
direction: validation feeds the board.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The
summary text is not to be consistency checked. The design is authoritative.

Contents:

- [SPEC delta](spec-delta/index.md)
  - [Package and Command](spec-delta/package-and-command.md)
  - [Surfaces and layout](spec-delta/surfaces-and-layout.md)
  - [Plugins](spec-delta/plugins.md)
  - [Install destination](spec-delta/install-destination.md)
  - [Installed tree](spec-delta/installed-tree.md)
  - [Write Safety](spec-delta/write-safety.md)
  - [Shipped files](spec-delta/shipped-files.md)
  - [Guide and README](spec-delta/guide-and-readme.md)
- [ARCHITECTURE delta](architecture-delta/index.md)
  - [Install entry](architecture-delta/install-entry.md)
  - [Recipes](architecture-delta/recipes.md)
  - [Plugins](architecture-delta/plugins.md)
  - [Renders and copies](architecture-delta/renders-and-copies.md)
  - [Packaging](architecture-delta/packaging.md)
  - [Repo Layout](architecture-delta/repo-layout.md)
  - [Subsystem Map](architecture-delta/subsystem-map.md)
  - [Harness profiler](architecture-delta/harness-profiler.md)
  - [Structural rules](architecture-delta/structural-rules.md)
- [Code delta](code-delta/index.md)
  - [Harness profiler](code-delta/harness-profiler.md)
