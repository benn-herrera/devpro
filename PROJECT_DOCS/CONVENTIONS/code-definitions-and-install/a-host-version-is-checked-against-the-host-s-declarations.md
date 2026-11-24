### A host version is checked against the host's declarations

A shipped resource that names a host version is type-checked against that host's published
declarations for that version, never against a devpro-owned stub for a published package. The
declarations are the authority on what the resource may call: the stub a runner registers is a
runtime stand-in for a package the runner does not install, and installed beside the package it
counts for nothing — a `declare module` naming a published package shadows the package's own types
wherever the check reads the module, so the drift the check exists to catch passes it silently.

The declarations reach the check as a dev-time dependency its runner installs before the checker
runs, pinned to the version the resource's header names, and the check reads what ships: its scope is
the resources' directory, and the host's transitive declarations are not its mandate. `just lint`
runs the check, and a missing tool fails it, naming what is missing, rather than skipping the step.
