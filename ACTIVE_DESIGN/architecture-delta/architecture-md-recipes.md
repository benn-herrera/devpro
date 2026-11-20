### [ARCHITECTURE.md, Recipes](../../PROJECT_DOCS/ARCHITECTURE/recipes.md)

The recipes take the components flag, the slot loop is one install, and the plugin-name reader
retires.

```
`just install <target> [--plugin=NAME]`, `just agents`, `just render`,
`just retake-reference`, `just install-agents-file <dir> [--plugin=NAME] [--harness=NAME] [--dry-run]`,
```
becomes
```
`just install <target> [--components=CSV]`, `just agents`, `just render`,
`just retake-reference`, `just install-agents-file <dir> [--harness=NAME] [--dry-run]`,
```

```
and each forwards all of it as `"$@"`, so `--plugin=NAME`, `--harness=NAME` and `--dry-run` all
reach the verb, which defaults the plugin to `context.DEFAULT_PLUGIN`;
```
becomes
```
and each forwards all of it as `"$@"`, so `--components=CSV`, `--harness=NAME` and `--dry-run` all
reach the verb, which defaults the components to none;
```

```
`agents` installs the devpro plugin into this checkout once per nested harness, taking the default
plugin `context.DEFAULT_PLUGIN` names — never passing `--plugin` — so the two lines are
`--harness=claude` and `--harness=opencode`;
```
becomes
```
`agents` installs the devpro set into this checkout once per nested harness, passing no
`--components`, so the two lines are
`--harness=claude` and `--harness=opencode`;
```

```
`render` and `retake-reference` go through the private `_render-slot.sh`, which calls
`python3 -m devpro install <slot>/<plugin> --plugin=<plugin>` with `--subdir=` once per plugin,
into `<slot>/<plugin>/`, where a nested plugin's install also writes the project's `AGENTS.md` and,
```
becomes
```
`render` and `retake-reference` go through the private `_render-slot.sh`, which calls
`python3 -m devpro install <slot>/devpro --components=kbase` with `--subdir=` once,
into `<slot>/devpro/`, where a nested plugin's install also writes the project's `AGENTS.md` and,
```

```
`render-agents-file HARNESS OUT [PLUGIN]` script, which may be an
earlier revision's copy run inside that revision's worktree, where that worktree's own justfile
supplies `GEN` and the worktree holds the package `GEN` names. Its third positional, the plugin,
becomes `--plugin=<plugin>` where given and not empty; absent or empty, the script passes no
plugin and the verb's default applies, which the script does not name. A copy predating the third
positional ignores it. `tag` goes through `--version`, which
```
becomes
```
`render-agents-file HARNESS OUT` script, which may be an
earlier revision's copy run inside that revision's worktree, where that worktree's own justfile
supplies `GEN` and the worktree holds the package `GEN` names. `tag` goes through `--version`, which
```

```
Scripts read a harness's `HarnessText` values through
`python3 -m devpro harness --plugin=PLUGIN NAME KEY`
and the loaded plugins' names, one per line, through `python3 -m devpro plugins`: the maintainer
scripts' readers, both hidden from `--help` and not part of the consumer CLI. `harness` takes
`--plugin` because every plugin verb does, and the `{plugin}`-templated keys need a bound harness. `devtools/scripts/_harness-value.sh` is the one shell reader of harness
values, for `_render-slot.sh`; `devtools/scripts/_plugin-names.sh` is the one
reader of plugin names, which `_render-slot.sh` and `check-wheel.sh` loop over.
```
becomes
```
Scripts read a harness's `HarnessText` values through
`python3 -m devpro harness NAME KEY`: the maintainer
scripts' reader, hidden from `--help` and not part of the consumer CLI. The `{plugin}`-templated keys
bind to the one plugin, so `harness` takes no selection flag. `devtools/scripts/_harness-value.sh` is the one shell reader of harness
values, for `_render-slot.sh`.
```

