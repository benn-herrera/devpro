### Plugins

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

A component naming a definition that does not exist refuses every render, `render` and `install`
alike, naming the component and the names. There is one install directory per harness (Install
destination); a component changes what it holds, never where it is.

A supporting artifact is delivered with the definition that uses it, and only where that definition
ships. The development scripts package goes to its destination inside the
`development` skill's, and the dicing snippets package inside the `docdicer` skill's; both ship with
every install. The dicing verbs — the `kanban` board, `check-plan` and plan dicing included — ship
with the `devpro` command itself (Package and Command, Dicing and Checks); the dicing snippets
package carries only their runner shortcuts. The kbase component also delivers
the kb-tools package (runner snippets: `justfile` and `Makefile` fragments a project includes,
inside the `kbase` skill's own directory) and the harness's `kbase` MCP entry. The MCP entry is the
`.mcp.json` in the install directory under claude and mage (Install destination), and a
record in the registry `registry.json` under opencode (Write Safety states which settings files no
install writes). A user-level install delivers no package.

Where the `kbase` skill ships, the `docdicer` skill states that `kb-root/` and everything under it
belongs to kbase, and that docdicer does not dice, undice or link-check it unless the user directs
that for it specifically. Where it does not ship, the skill carries no such statement.

A **runner include line** is the line that includes one package's runner snippets in the project's
**runner file**, its `justfile` or `Makefile`. Two packages carry snippets: the dicing snippets
package, a set called `devpro`, and the kb-tools, a set called `kb`. Every project install of a
nested plugin writes the `devpro` line; one with the kbase component also writes the `kb` line. Only
a project install under a harness whose plugin
nests in the project (claude, opencode) writes one; a mage install writes no runner include line and
creates no `Makefile`, and nothing is written into this repository's own runner file. A line names
the snippets inside the installed tree (under claude,
`.claude/skills/devpro/skills/docdicer/dicing-snippets/runner-snippets/` or
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/`; under opencode, the same below
`.opencode/plugins/devpro/`). The line does nothing where the snippets are absent: `import? '<path>'`
in a justfile, `-include <path>` in a Makefile. A project with neither runner file gets a `Makefile`
created to hold every line the install writes. The line an install wrote for the docdicer tools
package — retired with the absorbed dicing verbs, and none of its snippet paths point at anything
any more — the install removes itself: a non-comment line
whose snippets path ends `runner-snippets/docdicer.just` or `runner-snippets/docdicer.mk` and whose
first path segment is the harness directory this install writes is removed, the removal named in the
install report; a docdicer line naming another harness directory's snippets is reported and left.

Each set is judged on its own: one set's line never counts as another's. A runner file keeps at
most one line per set. A line already naming a set's snippets under this install's top-level
directory is updated in place. Updating it changes only the snippets path it names: the rest of the
line, and every line ending in the file, stay as written. A line whose first non-blank character is
`#` is not such a line. A line naming another top-level directory's snippets, or more than one line
for the same set, is reported and left, and the other sets' lines are still written. A user-level
install with the kbase component (SPEC.md, Deployed Surfaces, Install destination) writes its
definitions and the `kbase` MCP entry, `.mcp.json` under claude and the registry's record under
opencode. It writes no package, no runner include line and no runner file (Write Safety states
which settings files no install writes).

No install reads, rewrites or removes a file outside its own managed set. Under mage that leaves a
legacy plugin directory where one exists: an install from a release before the kbase component was
one wrote `~/Mage/Skills/kbase/`, holding its own skills, `CLAUDE.md` and `.mcp.json`, and no
install writes there or removes it. Mage loads the plugin directories below `~/Mage/Skills`, so it
loads both until the operator removes `~/Mage/Skills/kbase/` once: two sets of skills and agents,
and, where the install carries the kbase component, the `kbase` MCP server from both `.mcp.json`
files, the current install's rendered only with that component on. Removing the legacy directory,
before or after the install, stops the second load.

No install writes, copies, verifies or locates a `kbase` executable. The operator installs kbase
themselves, as the `kbase` skill's `references/installing.md` walks a session through, and every harness's `kbase` MCP entry names the
bare command `kbase`, resolved from `PATH`, with the argument `mcp` and no KB path; under mage the
entry keeps its `--project-dir-required` argument, and Mage gives the servers it starts access to
system tools, so `kbase` resolves there. Version 0.11.1 is the minimum kbase this product is written for, and nothing checks it.
The kbase component is supported on macOS and Linux, where Homebrew provides kbase as
`benn-herrera/tap/kbase`; native Windows is unsupported for it, and no install refuses or warns on
Windows.

devpro, the generator, needs Python 3.9 or later on the host; the kbase component's toolchain is the
`kbase` executable the operator installs, which needs no Python.
Everything else the kbase component needs (pandoc 3.12, git, a way to reach a model) is kbase's own
requirement, which the operator meets.
