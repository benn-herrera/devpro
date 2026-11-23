### [Packaging](../../PROJECT_DOCS/ARCHITECTURE/packaging.md)

**As it stands:**

```
`harnesses/resources/**/*`, `development-tools/**/*`, `dicing-snippets/**/*`,
  `profiler/view.html` and `dicing/kanban/assets/**/*`: the trees `install.py`
  reads through `PACKAGE_ROOT` (`HARNESS_RESOURCES_SOURCE` and each `SHIPPED_PACKAGES` source,
  the kb-tools, development-tools and dicing-snippets trees),
```

**Becomes:**

```
`harnesses/resources/**/*`, `development-tools/**/*`, `runner-snippets/**/*`,
  `profiler/view.html` and `kanban/assets/**/*`: the trees `install.py`
  reads through `PACKAGE_ROOT` (`HARNESS_RESOURCES_SOURCE` and each `SHIPPED_PACKAGES` source,
  the kb-tools, development-tools and runner-snippets trees, and the package itself, which the
  devpro tools package copies),
```

**As it stands:**

```
the verbs themselves import nothing: `devpro.cli` and the dicing verbs' `dicing/cli.py` import each
  verb's implementation where it dispatches that verb, which are their only function-level imports
  and the module-level-import house rule's one exception, the trio `tests/test_devpro.py` exempts by
  name.
```

**Becomes:**

```
the verbs themselves import nothing: `devpro.cli`, the dicing verbs' `dicing/cli.py`, the check
  verbs' `doccheck/cli.py`, `profiler/cli.py` and `dashboard/cli.py` import each verb's
  implementation where they dispatch it, which are their only function-level imports and the
  module-level-import house rule's one exception, the five `tests/test_devpro.py` exempts by name.
  `devpro/cli.py` composes each one's `add_verbs`.
```

