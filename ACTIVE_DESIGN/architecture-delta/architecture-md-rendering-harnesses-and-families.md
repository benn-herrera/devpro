### [ARCHITECTURE.md, Rendering, Harnesses and families](../../PROJECT_DOCS/ARCHITECTURE/rendering/harnesses-and-families.md)

The plugins paragraph is the selection's, the mage directory is constant, and the module homes lose
the plugins package.

```
The values that vary by plugin are templates over `{plugin}`: `plugin_dir`, `project_harness_dir`,
`reference_prefix`, `mcp_tool_prefix`, and each rendered file's and the registry's `marker`.
```
becomes
```
The values that vary by plugin are templates over `{plugin}`: `plugin_dir`,
`reference_prefix`, `mcp_tool_prefix`, and each rendered file's and the registry's `marker`; mage's
`project_harness_dir` is the constant `devpro`.
```

```
`Harness.bound(plugin_name)` fills them once with `str.replace`, not `str.format`, and takes the name
as a string, so a harness stays a value that knows no plugin's members and `harness.py` never
imports `plugin.py`.
```
becomes
```
`Harness.bound(plugin_name)` fills them once with `str.replace`, not `str.format`, and takes the name
as a string, so a harness stays a value that knows no member lists and `harness.py` never
imports `components.py`.
```

```
and a reader that needs a bound value reads it there. Binding again starts from the templates, so a
bound harness never holds another plugin's values.
```
becomes
```
and a reader that needs a bound value reads it there. Binding again starts from the templates, so a
bound harness never holds another binding's values.
```

```
**Plugins.** A plugin is a `Plugin` dataclass (`devpro/plugin.py`): a name and either the definition
names it ships (`include`) or the ones it leaves out (`exclude`), validated at construction, with
`ships(name)`. An instance is one module in `devpro/plugins/` defining `PLUGIN`, loaded by
`loading.load` as harnesses and families are; `devpro.py` excludes `kbase`, `kbase.py` includes
the names listed in SPEC.md, Deployed Surfaces, Plugins. A plugin is a selection of definitions and no
profile of its own. `plugin.py` imports no harness, render or definition: the dependency direction is
`vocabulary` ← `plugin` ← `context` → `harness`.
```
becomes
```
**Plugins.** The selection is one module, `devpro/components.py`: the member lists of the optional
components and the required set — every discovered definition no component names — with `ships(name)`,
validated at import against `discover()`, as a family is against its categories. It is imported by
`context` beside `harness.py` and `family.py`. The selection is a selection of definitions and no
profile of its own. `components.py` imports no harness, render or definition: the dependency
direction is `vocabulary` ← `components` ← `context` → `harness`.
```

```
instance is one module, in `devpro/harnesses/`, `devpro/families/` or `devpro/plugins/`,
defining `HARNESS`, `FAMILY` or `PLUGIN`, with no class in it. A harness, family or plugin is registered by its module existing, with no
```
becomes
```
instance is one module, in `devpro/harnesses/` or `devpro/families/`,
defining `HARNESS` or `FAMILY`, with no class in it. A harness or family is registered by its module existing, with no
```

```
The `Render` record (`devpro/context.py`) carries the harness, the plugin, the family
and the invocation's category map,
```
becomes
```
The `Render` record (`devpro/context.py`) carries the harness, the selection, the family
and the invocation's category map,
```

```
`Render.plugin` is the plugin, and `Render.bound_harness` binds the harness to it, so the bound
values a render reads are always its own plugin's and no mismatch is representable. `build_render(…, plugin=)` loads
the plugin and refuses one that names an undiscovered definition (`plugin_named`), because a misspelled
member would otherwise drop out of the contents SPEC states for that plugin and nothing else would
notice. `Plugin.ships(name)` is the one filter, called on the render's plugin.
```
becomes
```
`Render` carries the selection — the plugin and the components turned on — and `Render.bound_harness`
binds the harness to the plugin, so the bound values a render reads are always its own and no
mismatch is representable. `build_render(…, components=)` validates
every member name against `discover()`, because a misspelled
member would otherwise drop out of the contents SPEC states and nothing else would
notice. The selection's `ships(name)` is the one filter.
```

