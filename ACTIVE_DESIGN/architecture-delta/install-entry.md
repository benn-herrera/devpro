### [Install entry](../../PROJECT_DOCS/ARCHITECTURE/install/install-entry.md)

**As it stands:**

```
`just install target *args` is a one-line recipe over `python3 -m devpro install "$@"`; the
installed `devpro install` is the same verb (Packaging). The verb takes TARGET,
```

**Becomes:**

```
`devpro install` is the install's one entry, and `python3 -m devpro install` the same verb
(Packaging); no recipe of this repository's runner file stands in front of it. The verb takes
TARGET,
```

**As it stands:**

```
`install` uses the project root as spelled, and resolves it
only to compare it with this checkout (`REPO_ROOT`, `runner_file.install_include_lines`), so
two spellings of the checkout compare equal. The install directory's
```

**Becomes:**

```
`install` uses the project root as spelled. The install directory's
```

