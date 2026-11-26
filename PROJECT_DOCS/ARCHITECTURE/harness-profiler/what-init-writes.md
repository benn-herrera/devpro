# What `init` writes

`init claude` writes the repository's rendered skill and its
`.claude/settings.json`, merging the six entries through `hooks.merge_hooks`: each command runs
`profiler capture claude` on the committed wrapper, `hooks.HOOK_COMMAND`. An entry an `init` wrote
earlier is replaced in place, so a re-run picks up new hook options.
