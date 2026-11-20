### [ARCHITECTURE.md, Why There Is No Verification Verb](../../PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md)

A slot holds one project, rendered with the component on so the baseline holds its output.

```
A slot holds one slot project per plugin
(`rendered/<slug>/devpro/`, `rendered/<slug>/kbase/`), each an install of its plugin with itself as
project root, so beside the definitions the kbase slot project holds the kb-tools package, the harness's
MCP entry and the runner include lines (the docdicer line for either plugin, the kb line for kbase; none in the mage slot, a harness-directory plugin), and each slot project
holds, where the harness ships them, its own harness resources — the whole install product of both
plugins, which is what makes a `render-diff` a comparison of both.
```
becomes
```
A slot holds one slot project
(`rendered/<slug>/devpro/`), an install of the devpro set with the kbase component on, with itself
as project root, so beside the definitions it holds the kb-tools package, the harness's
MCP entry and the runner include lines (the docdicer line always, the kb line with the component
on; none in the mage slot, a harness-directory plugin), and it
holds, where the harness ships them, its own harness resources — the whole install product, which is
what makes a `render-diff` a comparison of installs.
```

