# One devpro plugin with optional components; the activity profiler ships as payload

devpro installs one plugin, the devpro plugin, carrying every definition the project ships, and the
kbase plugin retires: what only it delivered rides as the optional `kbase` component, turned on per
install by a `--components` CSV or the settings file's per-harness `components` key, so a project
that opts into the knowledge-base process carries it beside the full development process, and one
that does not never sees the kbase skill, its MCP server or its tools. Every claude project install
also ships the activity profiler as payload — the harness-profiler plugin's source vendored under
its MIT licence and credited in README.md — recording skill, agent and tool activity through six
hooks and rendering it through the `show-profile` skill. Consuming projects get one install
directory, one namespace and one set of MCP tool names per harness; the project gets one membership
home, one mage directory and one slot project per render slot.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The
summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [SPEC.md, Deployed Surfaces, Plugins](PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md)

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
components, `kbase` the only one today; the default is none. A name that is neither an optional
component nor part of what every install carries is refused, naming the optional components, and a
required component — `development`, `docdicer` — is not a legal value. The first positional is the
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

### [SPEC.md, Deployed Surfaces, Surfaces and layout](PROJECT_DOCS/SPEC/deployed-surfaces/surfaces-and-layout.md)

The render usage line takes the components flag, and the install usage line states the one set.

```
produced to order into the output root an invocation names: `devpro render --out <dir>
[--plugin=NAME]` renders the plugin's definitions (Plugins) and the harness-rendered files it writes
```
becomes
```
produced to order into the output root an invocation names: `devpro render --out <dir>
[--components=CSV]` renders the plugin's definitions with the named components on (Plugins) and the
harness-rendered files it writes
```

````
It arrives by **install**,
the one distribution channel. Install delivers one plugin, `devpro` or `kbase`, and no other. Its usage:

```sh
devpro install TARGET [--plugin=NAME] [--harness=NAME] [--subdir=DIR] [--family=NAME] [--config-file=FILE] [--dry-run] [--verbose]
```

Plugins states `--plugin`'s default.
````
becomes
````
It arrives by **install**,
the one distribution channel. Install delivers the devpro plugin's set, with the components the
invocation names. Its usage:

```sh
devpro install TARGET [--components=CSV] [--harness=NAME] [--subdir=DIR] [--family=NAME] [--config-file=FILE] [--dry-run] [--verbose]
```

Plugins states the `--components` default.
````

### [SPEC.md, Deployed Surfaces, Install destination](PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md)

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

### [SPEC.md, Deployed Surfaces, Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

The packages' delivery statement names the set, the `.index/` trigger names the component, and the
leaf gains the profiler payload.

```
(Plugins). Both plugins deliver the **docdicer tools package** at its package destination under
the install directory, `skills/docdicer/tools/`: inside the `docdicer` skill's own directory. They
also deliver the **development scripts package**, `skills/development/scripts/`, inside the
`development` skill's own directory (below), under mage as under claude and opencode. The kbase
plugin also delivers the kb-tools package (below).
```
becomes
```
(Plugins). Every install delivers the **docdicer tools package** at its package destination under
the install directory, `skills/docdicer/tools/`: inside the `docdicer` skill's own directory. It
also delivers the **development scripts package**, `skills/development/scripts/`, inside the
`development` skill's own directory (below), under mage as under claude and opencode. An install
with the kbase component also delivers the kb-tools package (below).
```

```
file, which they look for on every call, so an install of the devpro plugin is never blocked by it.
```
becomes
```
file, which they look for on every call, so an install without the kbase component is never blocked
by it.
```

```
A harness shipping none copies nothing, which is not an error.
```
becomes
```
A harness shipping none copies nothing, which is not an error.

A claude project install also ships the **activity profiler** payload: the harness resources
`libexec/hp.sh`, `libexec/hp.js` and `libexec/view.html`, copied as they stand, and the
`show-profile` skill, which renders a session's recorded activity — its skill, agent and tool calls
with timings and token costs — as text or as a self-contained HTML page. Six hook entries, one per
event (`PostToolUse`, `PostToolUseFailure`, `PreCompact`, `PostCompact`, `SessionStart`,
`SubagentStop`), are written into `hooks/hooks.json` on every claude project install; each appends
one line to the project's `.harness-profile/<session-id>.jsonl`, and a capture that fails, or finds
no `node` to run under, exits 0 with no output. A claude session on the web loads no plugin's hooks
and records nothing there; the skill names the tool's `init` for committing the hook where a session
needs one. A user-level install renders the skill and copies none of the resources; no opencode or
mage install ships the resources or the hook entries.
```

### [SPEC.md, Deployed Surfaces, Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md)

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

### [SPEC.md, Agents File](PROJECT_DOCS/SPEC/agents-file.md)

The marker's plugin word is constant, the verb loses its flag, and the other-plugin case retires.

```
`<!-- vvv-devpro <plugin> <version> … devpro-vvv -->` to an end marker line
`<!-- ^^^-devpro … devpro-^^^ -->`. A file holds one block, and the plugin on the begin marker
says whose it is.
```
becomes
```
`<!-- vvv-devpro devpro <version> … devpro-vvv -->` to an end marker line
`<!-- ^^^-devpro … devpro-^^^ -->`. A file holds one block, and the plugin word on the begin marker
says whose it is.
```

```
`devpro install-agents-file DIR [--plugin=NAME] [--harness=NAME]`, the plugin defaulted as Deployed
Surfaces, Plugins states, installs that plugin's agents file into the directory the operator names —
the harness's user harness directory or a project's own — and is the only way the agents-file block
first reaches a user harness directory, or changes the plugin a global block belongs to.
```
becomes
```
`devpro install-agents-file DIR [--harness=NAME]` installs the devpro plugin's agents file into the
directory the operator names — the harness's user harness directory or a project's own — and is the
only way the agents-file block first reaches a user harness directory.
```

```
    removed and why. A block whose begin marker names no plugin is kept as the installing plugin's.
    A global block of the other plugin stays that plugin's: no install reports it, refuses on it or
    reconciles it. Only the block goes from the project: every other byte of the project's
```
becomes
```
    removed and why. A block whose begin marker names no plugin — a legacy `kbase`-stamped block
    included — is kept as the installing plugin's. Only the block goes from the project: every other
    byte of the project's
```

```
Both plugins' blocks name the `development` skill. `install-agents-file` installs no skill, so a
```
becomes
```
The block names the `development` skill. `install-agents-file` installs no skill, so a
```

### [SPEC.md, Rendering](PROJECT_DOCS/SPEC/rendering.md)

The settings section names its two keys, and the namespace and shipped-set statements lose the
two-plugin phrasing.

```
Its sections are named per harness: `[<harness>]` carries the
  harness's settings, its `install` value among them (SPEC.md, Install destination);
```
becomes
```
Its sections are named per harness: `[<harness>]` carries the
  harness's settings, its `install` (SPEC.md, Install destination) and `components` (SPEC.md,
  Deployed Surfaces, Plugins) values among them;
```

```
Apart from the plugin's name and the namespace it gives references, text differs between plugins only
by an optional reference's paragraph being present or absent.
```
becomes
```
Apart from the namespace, text differs between installs only
by an optional reference's paragraph being present or absent.
```

```
References close within the shipped set, the definitions the render's plugin carries.
```
becomes
```
References close within the shipped set, the definitions the render carries — the plugin's set with
its components on.
```

### [SPEC.md, Package and Command](PROJECT_DOCS/SPEC/package-and-command.md)

The flag statement and the checkout premise take the components flag.

```
Every command that takes a plugin takes it as `--plugin=NAME`, with the default
Deployed Surfaces, Plugins states.
```
becomes
```
Every command that takes components takes them as `--components=CSV`, with the default
Deployed Surfaces, Plugins states.
```

```
- A project install of either plugin writes its runner include lines for any project (Deployed
  Surfaces, Plugins).
```
becomes
```
- A project install writes its runner include lines for any project (Deployed
  Surfaces, Plugins).
```

### [SPEC.md, Write Safety](PROJECT_DOCS/SPEC/write-safety.md)

The up-to-date judgment names the components flag and loses the second install directory.

```
`--harness`, `--family` or the category map changes bytes, so that install proceeds. A different plugin
is a different install directory, not a change of bytes in one.
```
becomes
```
`--harness`, `--family`, the category map or `--components` changes bytes, so that install proceeds.
```

### [SPEC.md, Generated files](PROJECT_DOCS/SPEC/generated-files.md)

The registry's ownership marker names the one plugin.

```
  file that carries its marker, `"plugin": "<plugin>"`, rather than a banner (Installed tree).
```
becomes
```
  file that carries its marker, `"plugin": "devpro"`, rather than a banner (Installed tree).
```

### [SPEC.md, Plan Status Form](PROJECT_DOCS/SPEC/plan-status-form.md)

The three "both plugins'" possessives name the one skill.

```
Both plugins' `development` skill gives plans one form for package headings, status and release,
```
becomes
```
The `development` skill gives plans one form for package headings, status and release,
```

```
  plugins' `development` skill, that lays out work as work packages and records their progress.
```
becomes
```
  `development` skill, that lays out work as work packages and records their progress.
```

```
- **plan size limit** — the length past which the plugins' `development` skill dices a plan before
```
becomes
```
- **plan size limit** — the length past which the `development` skill dices a plan before
```

### [SPEC.md, Guide and README](PROJECT_DOCS/SPEC/guide-and-readme.md)

The guide's delivery statement, the mage directory and the requirements list take the one plugin,
the component and the profiler.

```
The `guide` skill is where a session starts or continues work with devpro. Both plugins ship it
under every harness (SPEC.md, Deployed Surfaces, Plugins).
```
becomes
```
The `guide` skill is where a session starts or continues work with devpro. Every install carries it
under every harness (SPEC.md, Deployed Surfaces, Plugins).
```

```
    which writes `~/Mage/Skills/<plugin>/`, and, for the kbase plugin, restarting Mage;
```
becomes
```
    which writes `~/Mage/Skills/devpro/`, and, with the kbase component, restarting Mage;
```

```
  - the requirements: `just` 1.33.0 or later where the consuming project's runner is a justfile,
    for the runner include lines; `perl` with core `JSON::PP` for the claude guardrail;
```
becomes
```
  - the requirements: `just` 1.33.0 or later where the consuming project's runner is a justfile,
    for the runner include lines; `perl` with core `JSON::PP` for the claude guardrail; `node` 18 or
    later for the claude activity profiler, whose captures stay silent without it;
```

## ARCHITECTURE delta

### [ARCHITECTURE.md, Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

The kbase bullet becomes the component's, and the both-plugins phrases name the one install.

```
- **kbase plugin + kbase** — the `kbase` skill alone: the definition the devpro plugin excludes by name
  and the kbase plugin delivers with the others SPEC.md, Deployed Surfaces, Plugins lists
  (`devpro/plugins/kbase.py`). `kbase.py` owns a directory,
```
becomes
```
- **kbase component + kbase** — the `kbase` skill alone: the definition the kbase component adds to
  the devpro set, named among the component's contents in SPEC.md, Deployed Surfaces, Plugins
  (`devpro/components.py`). `kbase.py` owns a directory,
```

```
consuming project's `kb-root/AGENTS.md`, under every harness. The kbase plugin reaches kbase, the
```
becomes
```
consuming project's `kb-root/AGENTS.md`, under every harness. The kbase component reaches kbase, the
```

```
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered with its
  tools package by both plugins.
```
becomes
```
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered with its
  tools package by every install.
```

```
  `references/installing.md` and `references/using.md`, carried as `SkillFile`s, delivered by both
  plugins under every harness.
```
becomes
```
  `references/installing.md` and `references/using.md`, carried as `SkillFile`s, delivered
  under every harness.
```

```
The `development` and `docdicer` rows name their skill
  by a plain reference (`clauses.ref`), safe because both plugins ship both.
```
becomes
```
The `development` and `docdicer` rows name their skill
  by a plain reference (`clauses.ref`), safe because every install carries both.
```

```
  - an optional reference to `kbase` (`clauses.optional_ref`), which hands installing kbase itself
    to that skill. It is kept in the kbase plugin alone.
```
becomes
```
  - an optional reference to `kbase` (`clauses.optional_ref`), which hands installing kbase itself
    to that skill. It is kept where the kbase component is on.
```

```
  `adopting.md`, `release.md`, `design.md`), carried as `SkillFile`s, delivered by both plugins under every
  harness, mage included.
```
becomes
```
  `adopting.md`, `release.md`, `design.md`), carried as `SkillFile`s, delivered under every
  harness, mage included.
```

```
  `docdicer` references are optional references (Rendering, Placeholders), and `docdicer` ships
  with both plugins, so each fills. The *Plan status* and *Roadmap tickets* sections render whole
  under every plugin; each one's
```
becomes
```
  `docdicer` references are optional references (Rendering, Placeholders), and `docdicer` ships
  with every install, so each fills. The *Plan status* and *Roadmap tickets* sections render whole
  under every install; each one's
```

### [ARCHITECTURE.md, Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

The slots hold one project, the plugin rows give way to the components module, and the resources
row names the profiler's files.

```
rendered/               gitignored build product — this repo's own rendered tree, one slot per rendering, each holding one slot project per plugin (`rendered/<slug>/devpro/`, `rendered/<slug>/kbase/`), and the four `reference*` slots, one per harness plus gemma, `render-diff` compares against (justfile RENDERED_DIR); created on demand
```
becomes
```
rendered/               gitignored build product — this repo's own rendered tree, one slot per rendering, each holding one slot project (`rendered/<slug>/devpro/`), and the four `reference*` slots, one per harness plus gemma, `render-diff` compares against (justfile RENDERED_DIR); created on demand
```

```
  plugin.py             the `Plugin` type: a name and either the definition names it ships or the ones it leaves out, with `ships(name)` (Rendering, Harnesses and families)
  plugins/              one module per plugin, each defining `PLUGIN` and nothing else — `devpro.py` and `kbase.py`; which definitions each ships is SPEC.md, Deployed Surfaces, Plugins (CONVENTIONS.md, Plugin membership has one home)
```
becomes
```
  components.py         the definition selection: the member lists of the optional components (`kbase`), the required set being every discovered definition no component names, with `ships(name)` (Rendering, Harnesses and families); which definitions ship is SPEC.md, Deployed Surfaces, Plugins (CONVENTIONS.md, Plugin membership has one home)
```

```
  kb-tools/             shipped package, owned by `kbase` and so delivered only by the kbase plugin — the runner snippets
```
becomes
```
  kb-tools/             shipped package, owned by `kbase` and so delivered only with the kbase component — the runner snippets
```

```
  docdicer-tools/       shipped package, owned by `docdicer` and so delivered by every project install of either plugin — the `docdicer` bash launcher,
```
becomes
```
  docdicer-tools/       shipped package, owned by `docdicer` and so delivered by every project install — the `docdicer` bash launcher,
```

```
  development-tools/    shipped package, owned by `development` and so delivered by every project install of either plugin — `cold-read.sh`,
```
becomes
```
  development-tools/    shipped package, owned by `development` and so delivered by every project install — `cold-read.sh`,
```

```
and `claude/hooks/guardrail.pl` and `claude/hooks/state-table-reminder.sh`, and no `__init__.py`, so `load` still reads one harness per module; mage ships none
```
becomes
```
and `claude/hooks/guardrail.pl` and `claude/hooks/state-table-reminder.sh`, and
`claude/libexec/hp.sh`, `claude/libexec/hp.js` and `claude/libexec/view.html` (the activity
profiler, Install, Harness profiler), and no `__init__.py`, so `load` still reads one harness per
module; mage ships none
```

### [ARCHITECTURE.md, Install, Plugins](PROJECT_DOCS/ARCHITECTURE/install/plugins.md)

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

### [ARCHITECTURE.md, Install, Install entry](PROJECT_DOCS/ARCHITECTURE/install/install-entry.md)

The verb takes the components CSV, detection reads component-independent values, and the mage
dependency sentence retires.

```
The verb takes TARGET, its one positional
argument, and `--plugin=NAME`, a choice among the plugins `devpro/plugins/` holds, default
`context.DEFAULT_PLUGIN` (`cli._add_plugin`); a second positional is an argument argparse does not
recognize, refused with exit 2 before anything is written.
```
becomes
```
The verb takes TARGET, its one positional
argument, and `--components=CSV`, the optional components the invocation turns on, default none
(`cli._add_plugin`); a second positional is an argument argparse does not
recognize, refused with exit 2 before anything is written.
```

```
detects the harness from values
no plugin changes (`_detected_harness`), binds that harness to the plugin, and returns the harness,
```
becomes
```
detects the harness from values
no component changes (`_detected_harness`), binds that harness to the plugin, and returns the harness,
```

```
One read of the file serves the
selection and every harness's render. Only mage's harness directory depends on the plugin, its
`project_harness_dir` being `{plugin}`. `install` uses the project root as spelled,
```
becomes
```
One read of the file serves the
selection and every harness's render. `install` uses the project root as spelled,
```

### [ARCHITECTURE.md, Install, Guardrail hook](PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md)

The signal's presence follows the component.

```
Every claude install therefore runs the guardrail script
on each file-tool call as well as each Bash call, and on an install of the devpro plugin the script finds
the kbase signal absent and lets a file-tool call through.
```
becomes
```
Every claude install therefore runs the guardrail script
on each file-tool call as well as each Bash call, and with the kbase component off the script finds
the kbase signal absent and lets a file-tool call through.
```

```
Both are
relative to the install directory, so the signal is present where the kbase plugin is installed and absent where the devpro plugin is.
```
becomes
```
Both are
relative to the install directory, so the signal is present where the kbase component is on and
absent where it is off.
```

### [ARCHITECTURE.md, Install, Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md)

The prune-walk statement keeps its reason under one install directory.

```
What moves between plugins is the install directory: under claude another plugin's install directory
(`.claude/skills/kbase/`) sits inside the harness directory's `skills/`, so a walk wider than the
install directory would delete a different plugin.
```
becomes
```
The walk is one install directory's: under claude the install directory
(`.claude/skills/devpro/`) sits inside the harness directory's `skills/` beside what the project
keeps there, so a walk wider than the install directory would delete a neighbor's.
```

### [ARCHITECTURE.md, Install, Opencode entry](PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md)

The entry is the one file.

```
Surfaces, Shipped files). It is written for opencode 2.3.2 (floor 2.3.0) and is the same file for
both plugins, and its setup registers
```
becomes
```
Surfaces, Shipped files). It is written for opencode 2.3.2 (floor 2.3.0), and its setup registers
```

### [ARCHITECTURE.md, Install, Installing this repository](PROJECT_DOCS/ARCHITECTURE/install/installing-this-repository.md)

The mage sentence names the constant directory and one install.

```
(mage, whose `project_harness_dir` is `{plugin}` and whose `user_harness_dir` is `.`): the install
skips that call there, so a mage install of either plugin writes no include line and creates no `Makefile`.
```
becomes
```
(mage, whose `project_harness_dir` is `devpro` and whose `user_harness_dir` is `.`): the install
skips that call there, so a mage install writes no include line and creates no `Makefile`.
```

### [ARCHITECTURE.md, Rendering, Harnesses and families](PROJECT_DOCS/ARCHITECTURE/rendering/harnesses-and-families.md)

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

### [ARCHITECTURE.md, Packaging](PROJECT_DOCS/ARCHITECTURE/packaging.md)

The wheel check runs one install with the component on.

```
that an install of each plugin into a scratch project equals the checkout's
  byte for byte (each exercises packages the other lacks), and that a mage install of each plugin
  writes `<plugin>/CLAUDE.md`.
```
becomes
```
that an install with the kbase component on into a scratch project equals the checkout's
  byte for byte, and that a mage install writes `devpro/CLAUDE.md`.
```

```
| `install_include_lines`: no include lines for the repository itself, written by a project install of either plugin | skips that project | stands down: writes the lines for any project |
```
becomes
```
| `install_include_lines`: no include lines for the repository itself, written by a project install | skips that project | stands down: writes the lines for any project |
```

### [ARCHITECTURE.md, Banner](PROJECT_DOCS/ARCHITECTURE/banner.md)

The harness-rendered markers name the one plugin.

```
`registry.json` carries its marker,
`"plugin": "<plugin>"`, as the plugin manifest carries `"name": "<plugin>"` and `.mcp.json` the command
`"command": "kbase"`;
```
becomes
```
`registry.json` carries its marker,
`"plugin": "devpro"`, as the plugin manifest carries `"name": "devpro"` and `.mcp.json` the command
`"command": "kbase"`;
```

### [ARCHITECTURE.md, Agents File](PROJECT_DOCS/ARCHITECTURE/agents-file.md)

The block is the one plugin's, and the marker section loses the two-plugin cases.

```
reference to `development` in its own paragraph, and both plugins ship it, so both blocks carry it.
```
becomes
```
reference to `development` in its own paragraph, and every install carries it, so the block carries it.
```

```
**The plugin on the marker.** The begin marker line reads `vvv-devpro <plugin> <version> …`: the
plugin is `@!plg-name!@` (`clauses.PLUGIN_NAME`), the version `@!agf-version!@`. A file holds one
block, because two blocks with different markers would deliver the shared rules twice to every
session that reads the file (SPEC.md, Rendering). `agents_file._block_plugin` reads the first word
after the marker's opening as a plugin name, and `_release` the word after it. A begin line whose
first word is no plugin's name is a block of no plugin, with no release. On a project install
`checked_followed_agents_file` keeps a global block current as the plugin `_held_plugin` reads from its
begin line (`install-agents-file --plugin=<plugin>` into the user harness directory is what changes it), and a
block of no plugin as the installing plugin's. The block of no plugin differs in content from the
plugin's, so it is rewritten under the existing rule for a stamp that is not a release version. Mage
writes the plugin's block into `<plugin>/CLAUDE.md` in its own directory, so no conflict arises.
```
becomes
```
**The plugin on the marker.** The begin marker line reads `vvv-devpro devpro <version> …`: the
plugin word is `@!plg-name!@` (`clauses.PLUGIN_NAME`), the version `@!agf-version!@`. A file holds one
block, because two blocks would deliver the shared rules twice to every
session that reads the file (SPEC.md, Rendering). `agents_file._block_plugin` reads the first word
after the marker's opening as a plugin name, and `_release` the word after it. A begin line whose
first word is not `devpro` is a block of no plugin, with no release — a legacy `kbase`-stamped block
reads as one. On a project install
`checked_followed_agents_file` keeps a global block current as `_held_plugin` reads it from its
begin line (`install-agents-file` into the user harness directory is what changes it), and a
block of no plugin as the installing plugin's. The block of no plugin differs in content from the
plugin's, so it is rewritten under the existing rule for a stamp that is not a release version. Mage
writes the plugin's block into `devpro/CLAUDE.md` in its own directory, so no conflict arises.
```

### [ARCHITECTURE.md, Why There Is No Verification Verb](PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md)

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

### [ARCHITECTURE.md, Recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md)

The recipes take the components flag, the slot loop is one install, and the plugin-name reader
retires.

```
`just install <target> [--plugin=NAME]`, `just agents`, `just render`,
`just retake-reference`, `just install-agents-file <dir> [--plugin=NAME] [--harness=NAME] [--dry-run]`,
```
becomes
```
`just install <target> [--components=CSV]`, `just agents`, `just render`,
`just retake-reference`, `just install-agents-file <dir> [--harness=NAME] [--dry-run]`,
```

```
and each forwards all of it as `"$@"`, so `--plugin=NAME`, `--harness=NAME` and `--dry-run` all
reach the verb, which defaults the plugin to `context.DEFAULT_PLUGIN`;
```
becomes
```
and each forwards all of it as `"$@"`, so `--components=CSV`, `--harness=NAME` and `--dry-run` all
reach the verb, which defaults the components to none;
```

```
`agents` installs the devpro plugin into this checkout once per nested harness, taking the default
plugin `context.DEFAULT_PLUGIN` names — never passing `--plugin` — so the two lines are
`--harness=claude` and `--harness=opencode`;
```
becomes
```
`agents` installs the devpro set into this checkout once per nested harness, passing no
`--components`, so the two lines are
`--harness=claude` and `--harness=opencode`;
```

```
`render` and `retake-reference` go through the private `_render-slot.sh`, which calls
`python3 -m devpro install <slot>/<plugin> --plugin=<plugin>` with `--subdir=` once per plugin,
into `<slot>/<plugin>/`, where a nested plugin's install also writes the project's `AGENTS.md` and,
```
becomes
```
`render` and `retake-reference` go through the private `_render-slot.sh`, which calls
`python3 -m devpro install <slot>/devpro --components=kbase` with `--subdir=` once,
into `<slot>/devpro/`, where a nested plugin's install also writes the project's `AGENTS.md` and,
```

```
`render-agents-file HARNESS OUT [PLUGIN]` script, which may be an
earlier revision's copy run inside that revision's worktree, where that worktree's own justfile
supplies `GEN` and the worktree holds the package `GEN` names. Its third positional, the plugin,
becomes `--plugin=<plugin>` where given and not empty; absent or empty, the script passes no
plugin and the verb's default applies, which the script does not name. A copy predating the third
positional ignores it. `tag` goes through `--version`, which
```
becomes
```
`render-agents-file HARNESS OUT` script, which may be an
earlier revision's copy run inside that revision's worktree, where that worktree's own justfile
supplies `GEN` and the worktree holds the package `GEN` names. `tag` goes through `--version`, which
```

```
Scripts read a harness's `HarnessText` values through
`python3 -m devpro harness --plugin=PLUGIN NAME KEY`
and the loaded plugins' names, one per line, through `python3 -m devpro plugins`: the maintainer
scripts' readers, both hidden from `--help` and not part of the consumer CLI. `harness` takes
`--plugin` because every plugin verb does, and the `{plugin}`-templated keys need a bound harness. `devtools/scripts/_harness-value.sh` is the one shell reader of harness
values, for `_render-slot.sh`; `devtools/scripts/_plugin-names.sh` is the one
reader of plugin names, which `_render-slot.sh` and `check-wheel.sh` loop over.
```
becomes
```
Scripts read a harness's `HarnessText` values through
`python3 -m devpro harness NAME KEY`: the maintainer
scripts' reader, hidden from `--help` and not part of the consumer CLI. The `{plugin}`-templated keys
bind to the one plugin, so `harness` takes no selection flag. `devtools/scripts/_harness-value.sh` is the one shell reader of harness
values, for `_render-slot.sh`.
```

### [ARCHITECTURE.md, entry point](PROJECT_DOCS/ARCHITECTURE/entry-point.md)

The contents list gains the profiler leaf.

```
  - [Opencode entry](install/opencode-entry.md)
  - [Installing this repository](install/installing-this-repository.md)
```
becomes
```
  - [Opencode entry](install/opencode-entry.md)
  - [Harness profiler](install/harness-profiler.md)
  - [Installing this repository](install/installing-this-repository.md)
```

### ARCHITECTURE.md, Install, Harness profiler

A new leaf, carrying the vendored payload's statements whole:

```
### Harness profiler

Every claude project install ships the activity profiler as payload, not as a companion plugin
(SPEC.md, Deployed Surfaces, Shipped files): the source of the harness-profiler plugin by Aleksandr
Furmanov (MIT, `github.com/afurmanov/harness-profiler`), taken over and modified. No version is
stamped on the vendored code and no origin constant names it: the acknowledgement in README.md
credits the source, and that is the whole mechanism.

**Resources.** Three files are vendored into `devpro/harnesses/resources/claude/libexec/`: `hp.sh`,
the POSIX-sh launcher that finds `node` (PATH, `HP_NODE`, `~/.volta`, `~/.nvm`, Homebrew);
`hp.js`, the whole tool — `capture`, `tree`, `init`, `doctor` — one file, Node 18+ standard library
only, no dependency; and `view.html`, the self-contained page template that loads nothing from the
network. Each carries the `!INSTALLED! … devpro` banner within its first ten lines, added at
vendoring — the banner rule binds every harness resource — and the files are otherwise copied as
they stand; the one-way copy rule applies. `harness_resource_copies` lands each at the path it holds
below the install directory, so the install directory gains `libexec/`.

**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `sh "${CLAUDE_PLUGIN_ROOT}/libexec/hp.sh" capture claude`. The wiring is data in the harness
module, not a new mechanism, and no entry is gated on the install-time probe. A capture appends one
line to the project's `.harness-profile/<session-id>.jsonl`, whose directory the first write adds to
`.git/info/exclude`; a capture that fails, or finds no `node`, exits 0 with no output.

**The skill.** `show-profile` ships as a rendered skill definition under `devpro/definitions/skills/`,
so it carries the generated banner and the harness's namespace (`devpro:show-profile` under claude)
and renders under every harness. Its finder's first candidate, `../../libexec/hp.sh` from the
skill's directory, resolves to `<install-dir>/libexec/hp.sh` where the payload landed; its second,
the committed `.claude/harness-profiler/hp.sh`, covers a repository where the hook was committed for
claude-on-web; where neither stands, the skill says the tool is not installed. A user-level install
renders the skill and copies no resource, so there it is the committed copy or the absence.

**Limits, stated.** The vendored `doctor` greps the name `harness-profiler` in claude's
installed-plugin records and will not recognize the vendored copy; its committed-hook and
settings-hook checks still find a committed one. The limitation is stated, not fixed. Claude Code on
the web sends the same hook data but loads no plugin's hooks, so a cloud session records nothing
until the hook is committed to the repository; the vendored `init` subcommand does that, copying
launcher, script, page and skill into the repository's `.claude/` and merging the six entries into
its `.claude/settings.json`.

**What does not exist.** No companion-plugin mechanism is built: the profiler has no namespace of its
own and no carrier but the devpro plugin. Should it become optional later, it becomes a
`--components` value. No opencode or mage payload ships: the profiler's hooks are claude's, and no
port is planned. Token counts come from claude's own transcripts under `~/.claude/projects/`, which
is claude's data, not a source the install configures.
```

## Code delta

### [ARCHITECTURE.md, Rendering, Harnesses and families](PROJECT_DOCS/ARCHITECTURE/rendering/harnesses-and-families.md)

`devpro/plugin.py` and `devpro/plugins/` (`__init__.py`, `devpro.py`, `kbase.py`) are deleted, and
`devpro/components.py` replaces them: the optional components' member lists (`kbase` enumerating the
`kbase` skill), the required set being every discovered definition no component names — the
joins-by-existing mechanism `devpro.py` embodied stays for it — with `ships(name)` read as before.
`context.py`'s `plugins()`, `plugin_named()` and `DEFAULT_PLUGIN` retire with them; `build_render`
takes the components and validates every member name against `discover()`; `Render` carries the
selection; `clauses.PLUGIN_NAME` fills the one name. `harnesses/mage.py`'s `project_harness_dir`
becomes the constant `devpro`, the `{plugin}` binding machinery in `harness.py` staying for the
markers and prefixes. The rewritten statements are the delta entries above.

### [ARCHITECTURE.md, Install, Install entry](PROJECT_DOCS/ARCHITECTURE/install/install-entry.md)

`cli.py`'s `_add_plugin` becomes the `--components` CSV parsing and validation — optional components
only, required names refused, hard override — and every `args.plugin` / `plugin=` call site across
the verbs retargets to it. The hidden `plugins` verb and its only consumer,
`devtools/scripts/_plugin-names.sh`, are deleted. `devtools/scripts/_harness-value.sh` calls
`python3 -m devpro harness NAME KEY` with no selection flag. The rewritten statements are the delta
entries above.

### [ARCHITECTURE.md, Install, Plugins](PROJECT_DOCS/ARCHITECTURE/install/plugins.md)

`install.py` takes the `SHIPPED_PACKAGES` rows whose owner the selection's `ships(name)` admits, and
`runner_file.install_include_lines` writes the lines of the sets those rows carry — the docdicer
line always, the `kb` line with the component on; `_install_managed_paths` needs no change, already
naming every destination. The `harness.mcp_json` owner and the opencode registry gate stay keyed on
the `kbase` definition shipping, which the component decides. The kb-tools snippets' header comments
(`devpro/kb-tools/runner-snippets/kb.just`, `kb.mk`) reword their spelled install paths to
`.claude/skills/devpro/skills/kbase` and `.opencode/plugins/devpro` and drop the `--plugin=kbase`
writer line. The rewritten statements are the delta entries above.

### [SPEC.md, Deployed Surfaces, Plugins](PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md)

`context.py`'s settings reader extends `[<harness>]`'s legal keys with `components`, the CSV, beside
`install`, its unknown-key refusal message naming both; `install_selected` passes each named
harness's value to that harness's install, with `--components` replacing it when given. The leaf's
new statements are the delta entry above.

### [ARCHITECTURE.md, Agents File](PROJECT_DOCS/ARCHITECTURE/agents-file.md)

`agents_file.py`'s `_block_plugin` and `_held_plugin` look the marker word up in the one plugin
name: a begin line whose first word is not `devpro` is a block of no plugin, so a legacy
`kbase`-stamped global block is replaced by the existing no-plugin rule with no migration code. The
rewritten statements are the delta entries above.

### [ARCHITECTURE.md, Why There Is No Verification Verb](PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md)

The render and wheel scripts collapse to one slot project per slot: `devtools/scripts/render.sh`
renders one slot project with `--components=kbase` and drops its `--plugin` refusal,
`_render-slot.sh` writes `rendered/<slug>/devpro/` alone, `check-wheel.sh` runs one install with the
component on and asserts `devpro/CLAUDE.md`, and `_plugin-names.sh` is deleted. The test pins
re-anchor: `tests/test_plugins.py`'s include/exclude, two-plugin-render and agents-file pins rewrite
to the components shape; `tests/test_devpro.py`'s `mcp__plugin_kbase_kbase__query` pin becomes
`mcp__plugin_devpro_kbase__query` and its KBASE-plugin render pins become component-on pins;
`tests/test_devpro_install.py`'s DEVPRO/KBASE parametrization becomes a components matrix and its
doubled-path pin spells the single path; `tests/test_install_target.py`'s `--plugin=kbase` pins
become `--components=kbase` pins; `tests/test_kbase_surface.py`, `tests/test_opencode_entry.py` and
`tests/_structure.py` re-anchor to the one install directory. Obviated pins are deleted, not parked.
The rewritten statements are the delta entries above.

### ARCHITECTURE.md, Install, Harness profiler

The three resource files land at `devpro/harnesses/resources/claude/libexec/` (`hp.sh`, `hp.js`,
`view.html`), each gaining the `!INSTALLED! … devpro` banner line within its first ten lines at
vendoring; `devpro/harnesses/claude.py`'s `_registration_hooks` gains the six profiler entries as
data; and the `show-profile` skill joins `devpro/definitions/skills/` as a rendered definition whose
finder names `../../libexec/hp.sh`. The leaf the delta above creates states them.

### [SPEC.md, Guide and README](PROJECT_DOCS/SPEC/guide-and-readme.md)

README.md's third-party acknowledgments section, which the leaf names, gains exactly this line and
nothing else records the origin — no version stamping anywhere:

```
Credit to Aleksandr Furmanov for his [harness-profiler](https://github.com/afurmanov/harness-profiler) Claude Code plugin, whose source was adapted for our own activity profiler.
```
