### [Installing this repository](../../PROJECT_DOCS/ARCHITECTURE/install/installing-this-repository.md)

**As it stands:**

```
`install_include_lines` returns without writing when the project is
`REPO_ROOT`, which is set only in a checkout (Packaging). Nor are any written for a harness-directory plugin
```

**Becomes:**

```
`install_include_lines` writes this repository's include lines as it writes any project's. None are
written for a harness-directory plugin
```
