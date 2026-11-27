# What `init` writes

`init claude` writes the repository's rendered skill and its
`.claude/settings.json`, merging the six entries through `hooks.merge_hooks`: each command runs
`profiler capture claude` on the committed wrapper, `hooks.HOOK_COMMAND`. An entry an `init` wrote
earlier is replaced in place, so a re-run picks up new hook options.

The verb is claude's alone, the harness stated as the argument `capture` takes. `init` registers
only claude's hook, because each other harness's capture is its own plugin's — opencode's records
every call with no settings `init` could write. `init claude` therefore refuses, writing nothing and
exiting 2 with `error: ` before the message, where the project's devpro install is another
harness's, or where the existing `.claude/settings.json` names a hook command an `init` did not
write: it names what it found. A claude entry appended beside that other install's would register a
second capture in one settings file, and `merge_hooks` appends nothing there.

Claude Code on the web sends the same hook data but loads no plugin's hooks, so a cloud session
records nothing until the hook is committed to the repository, as this leaf describes.
