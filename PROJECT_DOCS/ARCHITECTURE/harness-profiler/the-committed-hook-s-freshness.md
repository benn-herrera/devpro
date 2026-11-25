# The committed hook's freshness.

`doctor`'s `update` line names a committed hook that lacks an
event, is not `async`, or runs another command than `hooks.HOOK_COMMAND` — the registered wiring is
the master, and the compare reads it without needing an install directory.

