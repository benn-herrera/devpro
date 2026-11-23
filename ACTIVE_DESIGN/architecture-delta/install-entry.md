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

