### [SPEC.md, Deployed Surfaces, Installed tree](../../PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md)

The dependency statement, the ownership markers and the MCP tool names take the one plugin, and the
body-path rule covers the profiler's launcher.

```
The devpro plugin adds no machine-level dependency: beyond the harness, it runs only
what installing the devpro package already requires. What a plugin needs beyond that is the
operator's to install, as Plugins states for each.
```
becomes
```
The devpro set adds no machine-level dependency: beyond the harness, it runs only
what installing the devpro package already requires. What a component needs beyond that is the
operator's to install, as Plugins states for each.
```

```
its origin: `"name": "<plugin>"` in the plugin manifest, `"command": "kbase"` in `.mcp.json`,
`"plugin": "<plugin>"` in `registry.json`, and `no readable script at` in
```
becomes
```
its origin: `"name": "devpro"` in the plugin manifest, `"command": "kbase"` in `.mcp.json`,
`"plugin": "devpro"` in `registry.json`, and `no readable script at` in
```

```
A
script inside a skill's own directory is named relative to that directory (`tools/docdicer`).
```
becomes
```
A
script inside a skill's own directory is named relative to that directory (`tools/docdicer`); the
profiler's launcher sits in the install directory's `libexec/` and is named relative to the skill's
directory too (`../../libexec/hp.sh`).
```

```
a `kbase` MCP
tool is named `mcp__plugin_kbase_kbase__<tool>` under claude, `mcp_kbase_<tool>` under mage and
`kbase_<tool>` under opencode.
```
becomes
```
a `kbase` MCP
tool is named `mcp__plugin_devpro_kbase__<tool>` under claude, `mcp_kbase_<tool>` under mage and
`kbase_<tool>` under opencode.
```

