# Installed tree

An installed tree is not for local edit: each install replaces the install directory wholesale —
the fresh tree overwrites everything that stands in it, whatever wrote it (SPEC.md, Write Safety) —
so no file in the install directory, a package destination included, is for local edit, and the
consumer's git is the record of what an install changed.

An installed tree needs no devpro installation: it runs its own copy of devpro, in the devpro tools
package (Shipped files), so removing the devpro package, or replacing it with another version,
changes nothing any installed file does, and only the next `devpro install` needs the package. That
install replaces the copy whichever of the two versions is the newer, and its report names the
version it replaces and the version it installs. The devpro set adds no machine-level dependency: beyond the harness, it runs only
what installing the devpro package already requires. What a component needs beyond that is the
operator's to install, as Plugins states for each.

A rendered definition, a copied script or build file, and a harness resource each states its origin
in a banner line; a harness-rendered file states it in its ownership marker; no other installed file
carries a banner. A rendered definition carries one banner line inside its frontmatter: the generated banner
(Generated files), which says where the file was rendered from and that it is not for local edit.
A skill's supporting file has no frontmatter, so it carries the banner as an HTML comment — its
first line, above a blank line and the body — and nothing about how the file is read depends on it.
Under opencode every rendered file is written without frontmatter and carries the banner as that
comment. The tuning data no rendered definition carries: the set records it once per install, in
the tuning table (Rendering). A copied package file of a script or build-file type (`.py`, `.sh`, `.mk`, `.just`), the devpro
copy's files excepted, carries an installed banner at its top, below its shebang where it has one. Both banners say to
request changes from the devpro project and that local needs belong in the consuming project's
CONVENTIONS.md. An installed banner names the source file it was copied from. A copied package
file lands with the mode the process umask gives a new file, plus its source's execute bits, and a
rendered file lands with the mode the process umask gives a new file. A harness resource
(Shipped files) carries its own installed banner, a `!INSTALLED! … devpro` line in its first ten
lines, as shipped: the install adds nothing to it. A harness-rendered file — the plugin manifest and
`.mcp.json` under claude and mage, `registry.json` under opencode, and under claude the guardrail
registration — carries no banner; its **ownership marker**, a fixed string in its content, states
its origin: `"name": "devpro"` in the plugin manifest, `"command": "kbase"` in `.mcp.json`,
`"plugin": "devpro"` in `registry.json`, and `no readable script at` in
`hooks/hooks.json`. No banner sits where it changes how
the file is read. Every other copied file — a package's `.gitignore` and every file of the devpro copy among them —
and every harness resource is installed byte-verbatim.

A definition body names no installed path below the harness directory for a session to run or edit. A
script the install places is named relative to the directory of the skill that names it: the
installation's wrapper sits in the install directory's `tools/` and is named relative to the skill's
directory (`../../tools/devpro.sh`; Shipped files states which commands run through it). The
project's scratch directory is `.devpro-temp/` under the project root, and it carries the same name
under every harness. A project install of a nested plugin — claude's, or opencode's — prepares it:
that install creates it when it is missing, and a `.devpro-temp/` line sits in the project's
`.gitignore`, the file created holding that line where the project has none. The preparation is
the install's, not the runner file's: an install whose runner file is already up to date still
prepares a missing scratch directory. A mage install and a
user-level install prepare neither: a mage install is no project install of a nested plugin, and a
user-level install places nothing relative to a project, so the scratch directory and its `.gitignore`
line are the work the agent's rule or the operator leaves them. A cross-definition reference renders
with the plugin's namespace — under claude and mage `<plugin>:<name>` for an agent, a command or a
skill, and under opencode `<plugin>-<name>`, the id the registry registers it under; a `kbase` MCP
tool is named `mcp__plugin_devpro_kbase__<tool>` under claude, `mcp_kbase_<tool>` under mage and
`kbase_<tool>` under opencode. A project's agents file is named `AGENTS.md` under claude and
opencode, and `CLAUDE.md` under mage (SPEC.md, Agents File).

Under claude and mage every file directly under `agents/` matching `*.md` whose definition is an
agent is a dispatchable agent definition, without exception. Its frontmatter carries the dispatch
fields the harness reads, each in that harness's spelling: `name`, `description` and, unless its
model renders empty, `model`. A document's frontmatter carries no field. A command's frontmatter
holds its banner alone. Under opencode a file has no frontmatter, and the registry
holds a record for every such file whose definition is an agent: its id, `<plugin>-<name>`, its
`description`, `mode: subagent` and, unless its model renders empty, the `model`. A document's
record is `hidden`.
