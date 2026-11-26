# Surfaces and layout

The repository exposes exactly three deployed surfaces, `agents/`, `commands/` and `skills/`: the
trees of rendered definitions, and one part of the install product (below). Every definition is
produced to order into the output root an invocation names: `devpro dev-render --out <dir>
[--components=CSV]`, a maintainer verb (Package and Command), renders the plugin's definitions with the named components on (Plugins) and the
harness-rendered files it writes
(Shipped files) into `<dir>`, an existing directory, and `install` renders into its install
directory (Install destination). `agents/` holds one file per agent and per
**document**, a definition agents read but never dispatch; `commands/` holds one file per command.
The supported harnesses are `claude` (Claude Code), `opencode` and `mage` (Mage, an agent harness);
`--harness` takes these names. The supported model families are `claude`, the default, `gemma-4` and
`qwen3`; `--family` takes these names (Rendering). `skills/` holds one directory per definition of
the skill kind — `skills/<name>/SKILL.md`, the **skill entry file**, then its supporting files,
beneath that directory and nowhere else.
A project install places each skill-owned shipped package in the directory of the skill it belongs
to, where that skill ships, and the devpro tools package at the install directory's `tools/`
(Shipped files):
- the development scripts package — a script that runs one agent on a brief with no tools — in the
  `development` skill's;
- the kb-tools package in the `kbase` skill's.

None is a supporting file of its skill; what each is and where it sits is in SPEC.md, Deployed
Surfaces, Shipped files. Under claude and mage a skill entry file's frontmatter is `name` and
`description`, the two fields every harness reads; under opencode the surfaces sit inside the
plugin directory (Install destination) with no frontmatter, beside the registry `registry.json`
and `index.ts`, opencode's **plugin entry**, the file that registers it, and a skill entry file's `name` and `description` come from the registry. The
description is the whole of what a session sees before it loads the skill: it carries the conditions
under which the skill applies, so discovery needs no command of its own. A supporting file has no
frontmatter. A consuming project receives the install product — the three deployed surfaces
together with the shipped packages delivered alongside them, each at its package destination
(Shipped files), the harness resources (Shipped files), and the harness-rendered files: under claude
and mage `.claude-plugin/plugin.json`, the plugin manifest, and `.mcp.json` where `kbase` ships;
under claude `hooks/hooks.json`, the guardrail registration, written on every install with the
guardrail's entry in it only where one trial run of the guardrail at install time, the install-time
probe, succeeds; under opencode `registry.json` (Shipped
files). Each is rendered and neither a deployed surface nor a definition. It arrives by **install**,
the one distribution channel. Install delivers the devpro plugin's set, with the components the
invocation names. Its usage:

```sh
devpro install TARGET [--components=CSV] [--harness=NAME] [--subdir=DIR] [--family=NAME] [--config-file=FILE] [--dry-run] [--verbose]
```

Plugins states the `--components` default. From a checkout of this repository the same command runs as
`PYTHONPATH=<clone> python3 -m devpro install …` (Package and Command), and it stages the clone's tree
as it stands; the repository's own installs stage from the built package the build produces first
(Package and Command).
`--dry-run` previews an install without writing anything (SPEC.md, Write Safety).
