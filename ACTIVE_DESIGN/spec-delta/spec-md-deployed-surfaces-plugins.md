### [SPEC.md, Deployed Surfaces, Plugins](../../PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md)

The leaf states the one plugin and its optional components: the flag, the settings key, the
component's enumerated contents, and the install-directory and mage consequences.

```
An install delivers one **plugin**, a named selection of definitions: `devpro install TARGET` or
`devpro install TARGET --plugin=kbase`. Every command that takes a plugin takes it as
`--plugin=NAME`, default `devpro`. The first positional is the target, so a plugin name there is
read as a target directory (a lone `devpro install kbase` is refused where no directory `kbase`
exists: "install target 'kbase' is not an existing directory"), and a second positional is refused
before anything is written. Every harness carries every definition of its plugin.
```
becomes
```
An install delivers one **plugin**, the devpro plugin, and the optional **components** the
invocation names: `devpro install TARGET` or `devpro install TARGET --components=kbase`. Every
command that takes components takes them as `--components=CSV`, a comma-separated list of optional
components, `kbase` the only one today; the default is none. A name that is not an optional
component is refused, naming the optional components; a required definition's name — `development`,
`docdicer` — is among them and so is not a legal value. The first positional is the
target, so a component name there is read as a target directory (a lone `devpro install kbase` is
refused where no directory `kbase` exists: "install target 'kbase' is not an existing directory"),
and a second positional is refused before anything is written. Every harness carries every
definition of the plugin's set, the named components included.

The devpro settings file's `[<harness>]` section carries `components` beside `install`: the CSV of
optional components that harness's install turns on. `--components` given is a hard override — it
replaces the file's value, never adds to it — and `render` takes components from its `--components`
alone.
```

```
- **devpro** delivers every definition but `kbase`: the coding, platform and specialist agents, the
  `development`, `docdicer` and `guide` skills (SPEC.md, Guide and README) and the rest.
- **kbase** delivers fourteen definitions: the `kbase` skill, which drives kbase, a separately
  installed knowledge-base program and MCP server, with its supporting files, and `guide`,
  `development`, `docdicer`, `architect`, `python-coder`, `prompt-engineer`, `tech-writer`, `shell-dsl-coder`,
  `applied-mathematician`, `economic-historian`, `theoretical-economist`, `prose-architect` and
  `literature-scout`.
```
becomes
```
The plugin delivers every definition the repository holds: the coding, platform and specialist
agents, the `development`, `docdicer`, `guide` and `show-profile` skills (SPEC.md, Guide and README)
and the rest. The optional **kbase component** adds, and only adds:

- the `kbase` skill, which drives kbase, a separately installed knowledge-base program and MCP
  server — its skill entry file and its six supporting files (`references/reading.md`,
  `building.md`, `scoring.md`, `maintaining.md`, `scoring-system.md`, `installing.md`);
- the kb-tools package at its destination, and the runner include line for its `kb` snippet set;
- the harness's `kbase` MCP entry and the MCP tool prefixes that name its tools;
- the two harness paragraphs about it — how a kbase session locates its project under mage, and the
  reload remedy under claude;
- the two optional references to it, in the `guide` skill and the `docdicer` skill;
- the guardrail's `.index/` check, active where the skill's entry file is present.

A project with the component on carries the full process with it: the component is an addition to
the whole set, not a smaller install of it.
```

```
A plugin naming a definition that does not exist refuses every render, `render` and `install`
alike, naming the plugin and the names. Each plugin installs into its own install directory (Install
destination), so installing one never changes the other's.
```
becomes
```
A component naming a definition that does not exist refuses every render, `render` and `install`
alike, naming the component and the names. There is one install directory per harness (Install
destination); a component changes what it holds, never where it is.
```

```
`development` skill's. The docdicer tools and the development scripts ship with both plugins, so a
kbase project has the `kanban` board, `check-plan` and plan dicing. The kbase plugin also delivers
```
becomes
```
`development` skill's. The docdicer tools and the development scripts ship with every install, so
every project has the `kanban` board, `check-plan` and plan dicing. The kbase component also delivers
```

```
A project install of either
plugin writes the line of every set whose package it ships: both plugins write the `docdicer` line,
and the kbase plugin also writes the `kb` line.
```
becomes
```
A project install
writes the line of every set whose package it ships: every install writes the `docdicer` line,
and an install with the kbase component also writes the `kb` line.
```

```
A line names
the snippets inside the installed tree (under claude,
`.claude/skills/<plugin>/skills/docdicer/tools/runner-snippets/` or
`.claude/skills/kbase/skills/kbase/kb-tools/runner-snippets/`; under opencode, the same below
`.opencode/plugins/<plugin>/`).
```
becomes
```
A line names
the snippets inside the installed tree (under claude,
`.claude/skills/devpro/skills/docdicer/tools/runner-snippets/` or
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/`; under opencode, the same below
`.opencode/plugins/devpro/`).
```

```
created to hold every line the install writes, whichever plugin it installs.
```
becomes
```
created to hold every line the install writes.
```

```
A user-level
install of the kbase plugin (SPEC.md, Deployed Surfaces, Install destination) writes its
definitions and the `kbase` MCP entry, `.mcp.json` under claude and the registry's record under
opencode.
```
becomes
```
A user-level
install with the kbase component (SPEC.md, Deployed Surfaces, Install destination) writes its
definitions and the `kbase` MCP entry, `.mcp.json` under claude and the registry's record under
opencode.
```

```
Installing both plugins in one place gives duplicate agents under different names.

No install reads, rewrites or removes a file outside its own managed set.
```
becomes
```
No install reads, rewrites or removes a file outside its own managed set.
```

```
The kbase plugin is supported on macOS and Linux, where Homebrew provides kbase as
```
becomes
```
The kbase component is supported on macOS and Linux, where Homebrew provides kbase as
```

```
devpro, the generator, needs Python 3.9 or later on the host; the kbase plugin's toolchain is the
```
becomes
```
devpro, the generator, needs Python 3.9 or later on the host; the kbase component's toolchain is the
```

```
Everything else the kbase plugin needs (pandoc 3.12, git, a way to reach a model) is kbase's own
```
becomes
```
Everything else the kbase component needs (pandoc 3.12, git, a way to reach a model) is kbase's own
```

