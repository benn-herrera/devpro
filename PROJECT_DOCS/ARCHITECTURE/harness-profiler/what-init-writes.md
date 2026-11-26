# What `init` writes

`init claude` writes the repository's rendered skill and its
`.claude/settings.json`, merging the six entries through `hooks.merge_hooks`: each command runs
`profiler capture claude` on the committed wrapper, `hooks.HOOK_COMMAND`. An entry an `init` wrote
earlier is replaced in place, so a re-run picks up new hook options. Claude Code on the web sends
the same hook data but loads no plugin's hooks, so a cloud session records nothing until the hook
is committed to the repository, as this leaf describes.
