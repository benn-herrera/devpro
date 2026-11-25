# A hook contract is read, not assumed

An event's accepted output fields, and where its context lands, are the harness's statement in its
hook reference, never an inference from where the hook fires: a field accepted on one event is
ignored on another, and context lands where the reference says — at the next model request of the
session it names, not at the call that fired the hook. Read the reference for each event before
wiring one. The entry's tests run it against a stub of the surface,
`tests/opencode_plugin_stub.ts`, which holds the code to the assumptions written into the stub and
not to the harness.
