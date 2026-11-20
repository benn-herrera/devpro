### [ARCHITECTURE.md, Install, Plugins](../../PROJECT_DOCS/ARCHITECTURE/install/plugins.md)

The membership statement is the selection's, the package filter reads it, and the runner lines and
paths name the one install.

```
What each plugin delivers is SPEC.md, Deployed Surfaces,
[Plugins](../../SPEC/deployed-surfaces/plugins.md); this leaf is how an install selects and ships it.
```
becomes
```
What each install delivers is SPEC.md, Deployed Surfaces,
[Plugins](../../SPEC/deployed-surfaces/plugins.md); this leaf is how an install selects and ships it.
```

```
**Membership.** A plugin is a `Plugin` (`devpro/plugin.py`), one module in `devpro/plugins/` defining
`PLUGIN`: the devpro plugin states what it leaves out (`kbase`), kbase what it ships. By
`Plugin.ships(name)` (Rendering, Harnesses and families), `render.rendered_definitions` keeps
exactly the definitions it admits, so a definition the plugin does not carry is never rendered, and
the skill's directory is never created by a run that omits it. `discover()` is the closed set
every plugin's names are checked against (`context.plugin_named`). The install filters nothing of its
own and reads no plugin's name: everything below is keyed on a definition's name, the owner.
```
becomes
```
**Membership.** The selection is one module, `devpro/components.py`: the member lists of the optional
components (`kbase`: the `kbase` skill), the required set being every discovered definition no
component names. By the selection's
`ships(name)` (Rendering, Harnesses and families), `render.rendered_definitions` keeps
exactly the definitions it admits, so a definition the selection does not carry is never rendered, and
the skill's directory is never created by a run that omits it. `discover()` is the closed set
every member name is checked against. The install filters nothing of its
own and reads no component's name: everything below is keyed on a definition's name, the owner.
```

```
`install` takes the rows whose owner `Plugin.ships(name)` admits, and none on a user-level install.
```
becomes
```
`install` takes the rows whose owner the selection's `ships(name)` admits, and none on a user-level
install.
```

```
The lines are written where the install
ships at least one such row and is a project install of a nested plugin
(`_is_project_install_of_a_nested_plugin`), so both plugins write the docdicer line and kbase also
the kb line.
```
becomes
```
The lines are written where the install
ships at least one such row and is a project install of a nested plugin
(`_is_project_install_of_a_nested_plugin`), so every install writes the docdicer line and one with
the kbase component also the kb line.
```

```
so under claude
`.claude/skills/<plugin>/skills/docdicer/tools/runner-snippets/docdicer.just` and
`.claude/skills/kbase/skills/kbase/kb-tools/runner-snippets/kb.just`, and under opencode the same
below `.opencode/plugins/<plugin>/`.
```
becomes
```
so under claude
`.claude/skills/devpro/skills/docdicer/tools/runner-snippets/docdicer.just` and
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/kb.just`, and under opencode the same
below `.opencode/plugins/devpro/`.
```

