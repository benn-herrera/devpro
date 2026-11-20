### [SPEC.md, Deployed Surfaces, Install destination](../../PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md)

The mage rows take the constant directory, and the user-level statements name the set.

```
| a harness directory (mage: `Mage/Skills`) | the target (mage: `<target>/<plugin>`) | the target's parent (mage: the target) |
```
becomes
```
| a harness directory (mage: `Mage/Skills`) | the target (mage: `<target>/devpro`) | the target's parent (mage: the target) |
```

```
The project harness directory is `.claude/` by default, `.opencode/` for `opencode`, and `<plugin>/`
for mage, so a `Mage/Skills` target gives `<target>/<plugin>`.
```
becomes
```
The project harness directory is `.claude/` by default, `.opencode/` for `opencode`, and `devpro/`
for mage, so a `Mage/Skills` target gives `<target>/devpro`.
```

```
An install is **user-level** when its harness directory is the harness's user harness directory,
however the target reached it, and is per plugin: `~/.claude/skills/<plugin>/` or
`~/.config/opencode/plugins/<plugin>/`. A user-level install renders the definitions its plugin
carries and the harness-rendered files (the plugin manifest and `.mcp.json` where `kbase` ships, or
the registry `registry.json`), prunes as any install does, and writes nothing else but, under opencode,
```
becomes
```
An install is **user-level** when its harness directory is the harness's user harness directory,
however the target reached it, and names the plugin's directory: `~/.claude/skills/devpro/` or
`~/.config/opencode/plugins/devpro/`. A user-level install renders the definitions the install
carries — the plugin's set with its components on — and the harness-rendered files (the plugin
manifest and `.mcp.json` where `kbase` ships, or
the registry `registry.json`), prunes as any install does, and writes nothing else but, under opencode,
```

```
no runner include line and no runner file. A user-level install of the kbase
plugin under opencode registers the `kbase` MCP server through the registry ([Plugins](plugins.md)).
```
becomes
```
no runner include line and no runner file. A user-level install with the kbase
component under opencode registers the `kbase` MCP server through the registry ([Plugins](plugins.md)).
```

