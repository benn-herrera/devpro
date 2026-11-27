# Plugins

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

The devpro settings file's `[<harness>]` table carries `components` beside `install`: the CSV of
optional components that harness's install turns on. `--components` given is a hard override — it
replaces the file's value, never adds to it — and `dev-render` takes components from its
`--components` alone.

The plugin delivers every definition the repository holds: the coding, platform and specialist
agents, the `development`, `docdicer`, `guide` and `profiler` skills (SPEC.md, Guide and README)
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

A component naming a definition that does not exist refuses every render, `dev-render` and
`install` alike, naming the component and the names. There is one install directory per harness (Install
destination); a component changes what it holds, never where it is.

A supporting artifact is delivered with the definition that uses it, and only where that definition
ships. The development scripts package goes to its destination inside the `development` skill's, and
ships with every project install, a user-level install's alone excepted (Install destination). The
devpro tools package — the installation's own copy of devpro, its wrapper and the runner snippets —
is the plugin's own, inside no definition's directory, and ships with every install (Shipped files).
The dicing and check verbs — `check-plan` and plan dicing
included — are verbs of the `devpro` command (Package and Command, Dicing and Checks); the runner
snippets carry only their runner shortcuts. The kbase component also delivers
the kb-tools package (runner snippets: `justfile` and `Makefile` fragments a project includes,
inside the `kbase` skill's own directory) and the harness's `kbase` MCP entry. The MCP entry is the
`.mcp.json` in the install directory under claude and mage (Install destination), and a
record in the registry `registry.json` under opencode (Write Safety states which settings files no
install writes). A user-level install delivers the devpro tools package and, under opencode, the
plugin entry and the guardrail resource beside it; beyond those it renders the definitions and the
harness-rendered files and writes no other package (Install destination).

Where the `kbase` skill ships, the `docdicer` skill states that `kb-root/` and everything under it
belongs to kbase, and that docdicer does not dice, undice or link-check it unless the user directs
that for it specifically. Where it does not ship, the skill carries no such statement.

A **runner include line** is the line that includes one package's runner snippets in the project's
**runner file**, its `justfile` or `Makefile`. Two packages carry snippets: the devpro tools
package, a set called `devpro`, and the kb-tools, a set called `kb`. Every project install of a
nested plugin writes the `devpro` line; one with the kbase component also writes the `kb` line. Only
a project install under a harness whose plugin
nests in the project (claude, opencode) writes one; a mage install writes no runner include line and
creates no `Makefile`. A line names
the snippets inside the installed tree (under claude,
`.claude/skills/devpro/tools/runner-snippets/` or
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/`; under opencode, the same below
`.opencode/plugins/devpro/`). The line does nothing where the snippets are absent: `import? '<path>'`
in a justfile, `-include <path>` in a Makefile. A project with neither runner file gets a `Makefile`
created to hold every line the install writes. No install edits a runner include line it did not
write: a line naming a set this release ships and this install writes is updated as below; a line
naming a set no install ships any more is the operator's to delete — the retired docdicer set's is
such a line — and left as written, its `import?` path missing under `just`, which refuses a missing
`import?` path rather than passing it.

Each set is judged on its own: one set's line never counts as another's. A runner file keeps at
most one line per set. A line already naming a set's snippets under this install's top-level
directory is updated in place. Updating it changes only the snippets path it names: the rest of the
line, and every line ending in the file, stay as written. A line whose first non-blank character is
`#` is not such a line. A line naming another top-level directory's snippets, or more than one line
for the same set, is reported and left, and the other sets' lines are still written. A user-level
install with the kbase component (SPEC.md, Deployed Surfaces, Install destination) writes its
definitions, the devpro tools package and the `kbase` MCP entry, `.mcp.json` under claude and the
registry's record under opencode. It writes no other package, no runner include line and no runner
file (Write Safety states which settings files no install writes).

No install reads, rewrites or removes a file outside its own managed set, and under mage the
install directory is `Mage/Skills` itself: everything directly inside it, beside `devpro/`, is inside
the install directory. A file the operator keeps there — a hand-made skill directory, a note, a
script, an earlier release's plugin directory — is removed by the next install, whatever wrote it
(Write Safety). The operator's place for such a file is outside `Mage/Skills/`. The pass-overs hold
even there: the agents file, `Mage/Skills/CLAUDE.md`, keeps its marked-block handling, and a re-entry
run's own copy under `Mage/Skills/devpro/` and its wrapper stand (Write Safety, Shipped files).

An install from a release before the kbase component was one wrote a legacy plugin directory,
`~/Mage/Skills/kbase/`, holding its own skills, `CLAUDE.md` and `.mcp.json`. No later install writes
there: the next one removes it inside the replacement, and until then Mage loads it beside
`~/Mage/Skills/devpro/`, so the operator sees two sets of skills and agents and, where the install
carries the kbase component, the `kbase` MCP server from both `.mcp.json` files. Removing it before
an install spares the second load's session; the install would have taken it anyway.

No install writes, copies, verifies or locates a `kbase` executable. The operator installs kbase
themselves, as the `kbase` skill's `references/installing.md` walks a session through, and every harness's `kbase` MCP entry names the
bare command `kbase`, resolved from `PATH`, with the argument `mcp` and no KB path; under mage the
entry keeps its `--project-dir-required` argument, and Mage gives the servers it starts access to
system tools, so `kbase` resolves there. Version 0.11.1 is the minimum kbase this product is written for, and nothing checks it.
The devpro plugin, the kbase component included, is supported on macOS and Linux, where Homebrew
provides kbase as `benn-herrera/tap/kbase`; native Windows is unsupported for it, and no install
refuses or warns on Windows.

devpro, the generator, needs Python 3.11 or later on the host; the kbase component's toolchain is the
`kbase` executable the operator installs, which needs no Python.
Kbase is installed by Homebrew, which carries the package's dependencies; the operator's requirement
is the one Homebrew states.
