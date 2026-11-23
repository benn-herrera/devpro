### [Plugins](../../PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md)

**As it stands:**

```
replaces the file's value, never adds to it — and `render` takes components from its `--components`
alone.
```

**Becomes:**

```
replaces the file's value, never adds to it — and `dev-render` takes components from its
`--components` alone.
```

**As it stands:**

```
agents, the `development`, `docdicer`, `guide` and `show-profile` skills (SPEC.md, Guide and README)
```

**Becomes:**

```
agents, the `development`, `docdicer`, `guide` and `profiler` skills (SPEC.md, Guide and README)
```

**As it stands:**

```
A component naming a definition that does not exist refuses every render, `render` and `install`
alike,
```

**Becomes:**

```
A component naming a definition that does not exist refuses every render, `dev-render` and
`install` alike,
```

**As it stands:**

```
A supporting artifact is delivered with the definition that uses it, and only where that definition
ships. The development scripts package goes to its destination inside the
`development` skill's, and the dicing snippets package inside the `docdicer` skill's; both ship with
every install. The dicing verbs — the `kanban` board, `check-plan` and plan dicing included — ship
with the `devpro` command itself (Package and Command, Dicing and Checks); the dicing snippets
package carries only their runner shortcuts.
```

**Becomes:**

```
A supporting artifact is delivered with the definition that uses it, and only where that definition
ships. The development scripts package goes to its destination inside the `development` skill's,
and ships with every install. The devpro tools package — the installation's own copy of devpro, its
wrapper and the runner snippets — is the plugin's own, inside no definition's directory, and ships
with every install (Shipped files). The dicing and check verbs — `check-plan` and plan dicing
included — are verbs of the `devpro` command (Package and Command, Dicing and Checks); the runner
snippets carry only their runner shortcuts.
```

**As it stands:**

```
record in the registry `registry.json` under opencode (Write Safety states which settings files no
install writes). A user-level install delivers no package.
```

**Becomes:**

```
record in the registry `registry.json` under opencode (Write Safety states which settings files no
install writes). A user-level install delivers the devpro tools package alone.
```

**As it stands:**

```
**runner file**, its `justfile` or `Makefile`. Two packages carry snippets: the dicing snippets
package, a set called `devpro`, and the kb-tools, a set called `kb`.
```

**Becomes:**

```
**runner file**, its `justfile` or `Makefile`. Two packages carry snippets: the devpro tools
package, a set called `devpro`, and the kb-tools, a set called `kb`.
```

**As it stands:**

```
`.claude/skills/devpro/skills/docdicer/dicing-snippets/runner-snippets/` or
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/`;
```

**Becomes:**

```
`.claude/skills/devpro/tools/runner-snippets/` or
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/`;
```

**As it stands:**

```
The kbase component is supported on macOS and Linux, where Homebrew provides kbase as
`benn-herrera/tap/kbase`; native Windows is unsupported for it, and no install refuses or warns on
Windows.
```

**Becomes:**

```
The devpro plugin, the kbase component included, is supported on macOS and Linux, where Homebrew
provides kbase as `benn-herrera/tap/kbase`; native Windows is unsupported for it, and no install
refuses or warns on Windows.
```

