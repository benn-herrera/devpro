### [Recipes](../../PROJECT_DOCS/ARCHITECTURE/recipes.md)

**As it stands:**

```
`just install <target> [--components=CSV]`, `just agents`, `just render`,
`just retake-reference`, `just install-agents-file <dir> [--harness=NAME] [--dry-run]`,
`just tag`, `just check-wheel` and `just dev-dashboard` reach `python3 -m devpro`: `install`,
`agents` and `install-agents-file` each run the verb directly in
one line; `install` takes `target *args` and `install-agents-file` takes `dir *args`,
and each forwards all of it as `"$@"`, so `--components=CSV`, `--harness=NAME` and `--dry-run` all
reach the verb, which defaults the components to none;
`agents` installs the devpro set into this checkout in one line
```

**Becomes:**

```
`just agents`, `just render`, `just retake-reference`, `just tag`, `just check-wheel` and
`just dev-dashboard` reach `python3 -m devpro`; no recipe stands in front of `install` or
`install-agents-file`, which are reached as verbs of the command alone (Install, Install entry).
`agents` installs the devpro set into this checkout in one line
```

**As it stands:**

```
Scripts read a harness's `HarnessText` values through
`python3 -m devpro harness NAME KEY`: the maintainer
scripts' reader, hidden from `--help` and not part of the consumer CLI.
```

**Becomes:**

```
Scripts read a harness's `HarnessText` values through `python3 -m devpro harness NAME KEY`: the
maintainer scripts' reader, and not part of the consumer CLI. It, `dev-render` and
`render-agents-file` are registered at parser build only where `DEVPRO_DEV` is `1` (SPEC.md,
Package and Command); each script that runs one of them — `render.sh`, `_render-slot.sh`,
`render-agents-file.sh`, `_harness-value.sh` — exports `DEVPRO_DEV=1` once.
```

