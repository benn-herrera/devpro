### A host version is checked against the host's declarations

A shipped resource that names a host version is type-checked against that host's published
declarations for that version, never against a devpro-owned stub for a published package. The
declarations are the authority on what the resource may call: the stub a runner registers is a
runtime stand-in for a package the runner does not install; installed beside the package, the stub
shadows the package's own types wherever the check reads the module, so the drift the check exists to
catch passes it silently.

The id the capture reads at the result's top level is the host's runtime shape, published in its
source and not in the shipped declarations; the check sees the shapes around it.

The declarations reach the check as a dev-time dependency the lint recipe installs before the checker
runs, pinned to the version the resource's header names (ARCHITECTURE.md, Recipes). `just lint` runs
the check, and a missing tool fails it, naming what is missing, rather than skipping the step.
