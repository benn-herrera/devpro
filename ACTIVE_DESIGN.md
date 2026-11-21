# devpro absorbs its tooling — the dashboard server

devpro's tooling — the document dicer and the session profiler — runs as devpro code, from devpro's
install, and one dashboard server shows a project's development: what is going on actively and what
happened in the past, the kanban board and the profiler's index and pages as panels of one loopback
site. The operator installing devpro receives every utility the project ships in that one install,
with no wrapper steps, no on-demand tool installs and no hosted clone; a session or a user opens one
URL for the board and the traces; a consuming project's capture hook keeps the contract it has
today — never blocking a tool call, its capture path free of dependencies — and the profiler's
pages attribute a child session to the one that dispatched it. The work lands in five approved
stages, each its own shippable increment — 1 the dicer's absorption, 2 the profiler's, 3 the
dashboard, 4 the attribution, 5 the MCP door — one design held from the first stage's plan to the
last's, the stage boundaries moved only by the user's word.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Plan Status Form](PROJECT_DOCS/SPEC/plan-status-form.md) — designs accepted across stages

**As it stands:**
```
- The design under way stays at `ACTIVE_DESIGN.md` from before its plan is written: it is removed
  when that plan is done, and is set aside with its plan, or alone before a plan exists. The plan
  cites the design's entries rather than restating them, a requirement found while the plan runs
  is entered in the design, and the plan's post-plan review reads the design.
```
**Becomes:**
```
- The design under way stays at `ACTIVE_DESIGN.md` from before its plan is written: it is removed
  when that plan is done, and is set aside with its plan, or alone before a plan exists. A design
  accepted across stages stays until the last stage's plan is done: each stage is its own shippable
  increment with its own plan, the stage boundaries are the user's to move, and an entry the design
  holds for a later stage stays pending until that stage's work lands it, applying only the pairs
  the design marks to that stage. The plan
  cites the design's entries rather than restating them, a requirement found while the plan runs
  is entered in the design, and the plan's post-plan review reads the design.
```

### [Package and Command](PROJECT_DOCS/SPEC/package-and-command.md) — the dicing verbs are devpro's

**As it stands:**
```
The installed package provides the `devpro` command. `python3 -m devpro` is the same command:
both print the same `--help`, and the same arguments install the same product, byte for byte.
Every `devpro` command exits 0 on success and 2 on a refusal or an operating-system failure, printing `error: <message>` on
stderr. Every command that takes components takes them as `--components=CSV`, with the default
Deployed Surfaces, Plugins states.
```
**Becomes:**
```
The installed package provides the `devpro` command. `python3 -m devpro` is the same command:
both print the same `--help`, and the same arguments install the same product, byte for byte.
The install verbs — `render`, `install`, `install-agents-file`, `render-agents-file` and the
hidden `harness` — exit 0 on success and 2 on a refusal or an operating-system failure, printing
`error: <message>` on
stderr; the dicing, check and board verbs of Dicing and Checks exit 0, 1 and 2 as that section
states. Every command that
takes components takes them as `--components=CSV`, with the default
Deployed Surfaces, Plugins states.
```

**As it stands:**
```
devpro also runs from a checkout of this repository, as `PYTHONPATH=<clone> python3 -m devpro
install …` (Deployed Surfaces). The install product is the same from a checkout or from an installed package.
```
**Becomes:**
```
devpro also runs from a checkout of this repository, as `PYTHONPATH=<clone> python3 -m devpro
install …` (Deployed Surfaces). The install product is the same from a checkout or from an installed package.

The command also carries the dicing, check and board surface: `devpro dice-doc`, `devpro undice`,
`devpro dice-docs`, `devpro check-links`, `devpro check-tree`, `devpro check-plan`,
`devpro check-design`, `devpro check-roadmap` and `devpro kanban` (Dicing and Checks). The verbs
run wherever the `devpro` command runs; they are not part of the install product.
```

### Dicing and Checks — the dicing surface's section

**As it stands:**
```
```
**Becomes:**
```
## Dicing and Checks

devpro carries the dicing surface of the docdicer project: it turns large markdown documents into
trees of small linked files, checks development plans, designs and roadmaps, and shows them as a
board. The verbs and their `--help` are the offered surface; this section states the outcomes any
implementation of them is held to.

The verbs are `devpro dice-doc`, `devpro undice`, `devpro dice-docs`,
`devpro check-links`, `devpro check-tree`, `devpro check-plan`, `devpro check-design`,
`devpro check-roadmap` and `devpro kanban`. `devpro --version` prints the version; `-h`, alone or
after a verb, prints help. The verbs run where the `devpro` command runs: the devpro package on the
host is the dicing surface's prerequisite, the operator's to install.

Every verb exits 0 on success, 1 where its check or dicing failed, and 2 on a usage error or a
refusal; `kanban` serves until interrupted and exits 0 either way. Results and summaries go to
stdout, diagnostics to stderr. The round-trip check — the monolith re-diced, the tree reassembled,
the links resolved — is the dicing's own commit gate, not an offered verb.

Six outcomes hold:

- **Navigable.** Every entry point and index lists the files directly below it, so the tree's entry
  point leads to every file; `check-tree` verifies this.
- **Lossless.** Each line of the source appears in exactly one file, unaltered except for link
  rewriting; a dicing whose verification fails exits 1.
- **Linked.** Cross references in the source (`§N`, `#anchor`, relative paths) resolve in the tree;
  `check-links` verifies this.
- **Repeatable.** For every verb but `kanban`, equal inputs give equal trees and messages, and
  nothing depends on the clock, the network, or any state outside the named inputs.
- **Non-destructive.** No verb modifies a source document, except that `kanban` moves tickets
  between `ROADMAP.md` and the active design, in either direction, adds a parked card's link ticket
  to the active design, and removes a link ticket from it.
- **Reversible.** A tree `dice-doc` wrote can be written back to a document that dices to the same
  tree.

The check verbs read the forms SPEC.md, Plan Status Form states: `check-plan` the plan's status
table, `check-design` a design's final form and its delta pairs against their targets, and
`check-roadmap` the roadmap's ticket layout. Without a file argument each checks the active file
under the project root — the nearest directory at or above the current one holding a `.git` entry;
`kanban` serves that project. The full contract of each verb — the diced-tree format, link
rewriting, the link map, the manifest, the checks' reports and the board's moves — is this
section's: the stage-1 plan carries it over from the contract documents the absorbed project held,
stated in this section and its section's own leaves, and no document outside this tree holds any
verb's contract.
```

### [SPEC entry point](PROJECT_DOCS/SPEC/entry-point.md) — the new section listed

**As it stands:**
```
- [Plan Status Form](plan-status-form.md)
- [Guide and README](guide-and-readme.md)
```
**Becomes:**
```
- [Plan Status Form](plan-status-form.md)
- [Dicing and Checks](dicing-and-checks.md)
- [Guide and README](guide-and-readme.md)
```

### [Surfaces and layout](PROJECT_DOCS/SPEC/deployed-surfaces/surfaces-and-layout.md) — the docdicer tools package retires, the dicing snippets package takes its place

**As it stands:**
```
- the docdicer tools package — the launcher for docdicer, a separately published tool that dices a
  markdown document into a tree of linked files — in the `docdicer` skill's own directory;
- the development scripts package — a script that runs one agent on a brief with no tools — in the
```
**Becomes:**
```
- the development scripts package — a script that runs one agent on a brief with no tools — in the
```

**As it stands:**
```
- the development scripts package — a script that runs one agent on a brief with no tools — in the
  `development` skill's;
- the kb-tools package in the `kbase` skill's.
```
**Becomes:**
```
- the development scripts package — a script that runs one agent on a brief with no tools — in the
  `development` skill's;
- the dicing snippets package — the absorbed dicing verbs' runner shortcuts (Shipped files) — in the
  `docdicer` skill's;
- the kb-tools package in the `kbase` skill's.
```

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md) — the docdicer package retires, its runner shortcuts return; the profiler's and dashboard's decisions (stages 2-4)

**As it stands:**
```
(Plugins). Every install delivers the **docdicer tools package** at its package destination under
the install directory, `skills/docdicer/tools/`: inside the `docdicer` skill's own directory. It
also delivers the **development scripts package**, `skills/development/scripts/`, inside the
`development` skill's own directory (below), under mage as under claude and opencode. An install
with the kbase component also delivers the kb-tools package (below). A user-level install delivers none (SPEC.md,
Deployed Surfaces, Install destination). The docdicer package holds four files:
- `docdicer`, a `bash` script, executable, carrying the installed banner below its shebang
- `.gitignore`, holding `.venv/` and carrying no banner
- `runner-snippets/docdicer.just` and `runner-snippets/docdicer.mk`, runner snippets for a
  consuming project to include, each carrying the installed banner at its top. A project install of
  either plugin under claude or opencode writes the docdicer runner include line for them (Plugins).
  They define the recipes `docdicer`, `docdicer-check-plan`, `docdicer-kanban` and `docdicer-help`.
```
**Becomes:**
```
(Plugins). Every install delivers the **development scripts package**, `skills/development/scripts/`,
inside the `development` skill's own directory (below), under mage as under claude and opencode. An
install with the kbase component also delivers the kb-tools package (below). A user-level install
delivers none (SPEC.md,
Deployed Surfaces, Install destination). No dicing package ships: the dicing, check and board
verbs run as verbs of the `devpro` command (Package and Command, Dicing and Checks).
```

**As it stands:**
```
The launcher installs docdicer on demand and takes no `--install` argument. Run as
`tools/docdicer` from the skill's directory, on every run it:
- rebuilds `tools/.venv` where the venv's python is missing or does not run. Where `python3` 3.9 or
  later with its `venv` module is not on the host, it names the remedy and exits non-zero
- installs into `tools/.venv` the docdicer version the script names, where the venv's docdicer does
  not report that version; a failure exits non-zero
- sends all install output to stderr
- then passes its arguments to docdicer unchanged

The first run, and any run after the venv is lost, therefore needs the network and `git`. No install
runs the launcher. An install leaves `tools/.venv` in place; on its next run the launcher's checks
above rebuild or update it. A `.venv` directly under a package
destination is not install output.
```
**Becomes:**
```
A `.venv` directly under a package destination is not install output.
```

**As it stands:**
```
Where the project's runner includes the docdicer snippet, the `docdicer` skill directs the agent to
run docdicer through its recipes rather than through `tools/docdicer`. The skill carries no other
runner-snippet advice and no install step.
```
**Becomes:**
```
```

**As it stands:**
```
No package is a definition: a package under a
skill's directory is neither its skill entry file nor one of its supporting files, the development
scripts package and the docdicer tools package included.
```
**Becomes:**
```
No package is a definition: a package under a
skill's directory is neither its skill entry file nor one of its supporting files, the development
scripts package included.
```

(Stages 2-4: the seven pairs below wait for their stages' plans; the four pairs above are stage 1's.)

**As it stands:**
```
`<install-dir>/guardrail.ts` and `<install-dir>/profiler.ts`, and, for claude and opencode alike,
`<install-dir>/profiler/hp.sh`, `<install-dir>/profiler/hp.py` and `<install-dir>/profiler/view.html`;
claude's at `<install-dir>/hooks/guardrail.pl` and
```
**Becomes:**
```
`<install-dir>/guardrail.ts` and `<install-dir>/profiler.ts`, and, for claude and opencode alike,
`<install-dir>/profiler/hp.sh`;
claude's at `<install-dir>/hooks/guardrail.pl` and
```

**As it stands:**
```
A claude project install also ships the **activity profiler** payload: the harness resources
`profiler/hp.sh`, `profiler/hp.py` and `profiler/view.html`, copied as they stand, and the
```
**Becomes:**
```
A claude project install also ships the **activity profiler**: its code is devpro's own, and the
hook files refer back to devpro wherever they ran the profiler's script, with the capture hook's
contract — a failed or interpreterless capture exits 0 with no output — unchanged. The page
template `view.html` the render reads is the devpro wheel's package data
(`devpro/profiler/view.html`, read by the rendering module), not an install resource; and the
```

**As it stands:**
```
`show-profile` skill, which renders a session's recorded activity — its skill, agent and tool calls
with timings and token costs — as text, as a self-contained HTML page, or served over HTTP: the
tool's `serve` subcommand renders the record files in memory behind a local server whose main page
lists every record file it can render. The pages and the records stay local: reachable only from the
```
**Becomes:**
```
`show-profile` skill, which renders a session's recorded activity — its skill, agent and tool calls
with timings and token costs — as text, as a self-contained HTML page, or served over HTTP: the
dashboard, devpro's one loopback server for the web interface, renders the record files in memory
as one panel of a site whose other panel is the project's board, the how-to-read legend served once
in an outer frame, a record selection changing the inner frame only and the inner frame's top-level
view the all-records list. The pages and the records stay local: reachable only from the
```

**As it stands:**
```
resources. A project opencode install also ships the profiler's render payload — `profiler/hp.sh`,
`profiler/hp.py` and `profiler/view.html` — and the capture `profiler.ts` beside the plugin entry, and
```
**Becomes:**
```
resources. A project opencode install also ships the profiler's launcher — `profiler/hp.sh` — and
the capture `profiler.ts` beside the plugin entry, and
```

**As it stands:**
```
hook, and a mage install ships none of them.
```
**Becomes:**
```
registers no hook entries; each recorded call appends one line to the project's
`.devpro-temp/.profiler-opencode/<session-id>.jsonl`, a capture that fails raises nothing out of the
hook, and a mage install ships none of them. A page attributes a child session to the session that
dispatched it: the capture extracts the child's session id into the parent call's record, the render
groups children under their dispatching session, links each Agent row to the child's page and heads
a child page with its dispatcher, and the stores stay flat — the child never knows its parent at
write time, the hierarchy being metadata the parent side builds, and claude holding no child
session records at all.
```

**As it stands:**
```
`SubagentStop`), are written into `hooks/hooks.json` on every claude project install; each appends
one line to the project's `.devpro-temp/claude-profiler/<session-id>.jsonl`, and a capture that
```
**Becomes:**
```
`SubagentStop`), are written into `hooks/hooks.json` on every claude project install; each appends
one line to the project's `.devpro-temp/.profiler-claude/<session-id>.jsonl`, and a capture that
```

**As it stands:**
```
registers no hook entries; each recorded call appends one line to the project's
`.devpro-temp/opencode-profiler/<session-id>.jsonl`, a capture that fails raises nothing out of the
```
**Becomes:**
```
registers no hook entries; each recorded call appends one line to the project's
`.devpro-temp/.profiler-opencode/<session-id>.jsonl`, a capture that fails raises nothing out of the
```

**As it stands:**
```
(Plugins). Every install delivers the **development scripts package**, `skills/development/scripts/`,
inside the `development` skill's own directory (below), under mage as under claude and opencode. An
install with the kbase component also delivers the kb-tools package (below). A user-level install
delivers none (SPEC.md,
Deployed Surfaces, Install destination). No dicing package ships: the dicing, check and board
verbs run as verbs of the `devpro` command (Package and Command, Dicing and Checks).
```
**Becomes:**
```
(Plugins). Every install delivers the **development scripts package**, `skills/development/scripts/`,
inside the `development` skill's own directory (below), and the **dicing snippets package**
(below), under mage as under claude and opencode. An
install with the kbase component also delivers the kb-tools package (below). A user-level install
delivers none (SPEC.md,
Deployed Surfaces, Install destination). No dicing code ships in a package: the dicing, check and
board verbs run as verbs of the `devpro` command (Package and Command, Dicing and Checks); the
dicing snippets package holds only their runner shortcuts.
```

**As it stands:**
```
The kb-tools package is a shipped package installed at its own stated destination:
`skills/kbase/kb-tools/`, inside the `kbase` skill's own directory, holding only the runner
snippets, and not an importable package either, read by the consuming project through the runner
include line. The snippets run `kbase` from `PATH`. Every target the snippets define is named
`kb-<name>`. No package is a definition: a package under a
skill's directory is neither its skill entry file nor one of its supporting files, the development
scripts package included.
```
**Becomes:**
```
The kb-tools package is a shipped package installed at its own stated destination:
`skills/kbase/kb-tools/`, inside the `kbase` skill's own directory, holding only the runner
snippets, and not an importable package either, read by the consuming project through the runner
include line. The snippets run `kbase` from `PATH`. Every target the snippets define is named
`kb-<name>`. No package is a definition: a package under a
skill's directory is neither its skill entry file nor one of its supporting files, the development
scripts package included.

The dicing snippets package is a shipped package installed at its own stated destination:
`skills/docdicer/dicing-snippets/`, inside the `docdicer` skill's own directory, holding only the
runner snippets, not an importable package either, read by the consuming project through the same
runner include line. The snippets run the `devpro` command from `PATH`. They define the recipes
`devpro`, `devpro-help`, `devpro-check-plan`, `devpro-check-design`,
`devpro-check-design-deltas-applied` and `devpro-check-roadmap`: the bare `devpro` printing the
command's help, and `devpro-help` showing the commands and their doc strings. The four gates take no
argument, each checking the active file under the project root — the active plan, the active design,
the active design's applied deltas and `ROADMAP.md` — that argumentlessness being what makes them
runner-able. No `devpro-kanban` and no dicing recipes: the board is the dashboard's panel, and the
dicing shortcuts need the arguments their direct calls give them, documented in the `docdicer` skill
and Dicing and Checks. Both runners carry the set —
`devpro.just` for a justfile, `devpro.mk` for a Makefile — and `devpro-help` shows the commands and
their doc strings in either: under just from the recipes' own `[doc]` strings, under make by
parsing the snippet's own target-list comments, the approach the retired set's make snippet used and
the feature worked.
```

### [Plugins](PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md) — the snippet sets: devpro returns, the retired line cleaned up

The user directed the runner shortcuts' return after stage 1's plan landed: the absorbed dicing
verbs' check recipes come back as a new snippet set — the retired docdicer set's replacement, the
checks-only set of six recipes, `devpro` bare and five with the `devpro-` prefix where the old ones
carried `docdicer-` — and the include line is
written for every project install of a nested plugin again, not only with the kbase component. The
"served, not injected" decision named the profiler's serve surface — the dashboard's — and the
checks were never that question: their shortcuts are the process surface, and they return. The
verbs stay served by the `devpro` command; what returns is the runner surface's convenience over
them, not a second tool install. This entry and the entries with it are stage-1 surface work — the
next plan's content, the user directing it now — and stay pending until that plan lands them.

**As it stands:**
```
A supporting artifact is delivered with the definition that uses it, and only where that definition
ships. The docdicer tools package (SPEC.md, Deployed Surfaces, Shipped files) goes to its destination
inside the `docdicer` skill's own directory, and the development scripts package inside the
`development` skill's. The docdicer tools and the development scripts ship with every install, so
every project has the `kanban` board, `check-plan` and plan dicing. The kbase component also delivers
```
**Becomes:**
```
A supporting artifact is delivered with the definition that uses it, and only where that definition
ships. The development scripts package goes to its destination inside the
`development` skill's, and ships with every install. The dicing verbs — the `kanban` board,
`check-plan` and plan dicing included — ship with the `devpro` command itself (Package and Command,
Dicing and Checks). The kbase component also delivers
```

**As it stands:**
```
A **runner include line** is the line that includes one package's runner snippets in the project's
**runner file**, its `justfile` or `Makefile`. Two packages carry snippets: the docdicer tools, a
snippet set called `docdicer`, and the kb-tools, a set called `kb`. A project install
writes the line of every set whose package it ships: every install writes the `docdicer` line,
and an install with the kbase component also writes the `kb` line. Only a project install under a harness whose plugin
nests in the project (claude, opencode) writes one; a mage install writes no runner include line and
creates no `Makefile`, and nothing is written into this repository's own runner file. A line names
the snippets inside the installed tree (under claude,
`.claude/skills/devpro/skills/docdicer/tools/runner-snippets/` or
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/`; under opencode, the same below
`.opencode/plugins/devpro/`). The line does nothing where the snippets are absent: `import? '<path>'`
in a justfile, `-include <path>` in a Makefile. A project with neither runner file gets a `Makefile`
created to hold every line the install writes.
```
**Becomes:**
```
A **runner include line** is the line that includes one package's runner snippets in the project's
**runner file**, its `justfile` or `Makefile`. One package carries snippets: the kb-tools, a set
called `kb`. A project install with the kbase component writes its line. Only a project install under a harness whose plugin
nests in the project (claude, opencode) writes one; a mage install writes no runner include line and
creates no `Makefile`, and nothing is written into this repository's own runner file. A line names
the snippets inside the installed tree (under claude,
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/`; under opencode, the same below
`.opencode/plugins/devpro/`). The line does nothing where the snippets are absent: `import? '<path>'`
in a justfile, `-include <path>` in a Makefile. A project with neither runner file gets a `Makefile`
created to hold every line the install writes. The line an install wrote for the docdicer tools
package — retired with the absorbed dicing verbs — the install removes itself: a non-comment line
whose snippets path ends `runner-snippets/docdicer.just` or `runner-snippets/docdicer.mk` and whose
first path segment is the harness directory this install writes is removed, the removal named in the
install report; a docdicer line naming another harness directory's snippets is reported and left.
```

**As it stands:**
```
A supporting artifact is delivered with the definition that uses it, and only where that definition
ships. The development scripts package goes to its destination inside the
`development` skill's, and ships with every install. The dicing verbs — the `kanban` board,
`check-plan` and plan dicing included — ship with the `devpro` command itself (Package and Command,
Dicing and Checks). The kbase component also delivers
the kb-tools package (runner snippets: `justfile` and `Makefile` fragments a project includes,
inside the `kbase` skill's own directory) and the harness's `kbase` MCP entry.
```
**Becomes:**
```
A supporting artifact is delivered with the definition that uses it, and only where that definition
ships. The development scripts package goes to its destination inside the
`development` skill's, and the dicing snippets package inside the `docdicer` skill's; both ship with
every install. The dicing verbs — the `kanban` board, `check-plan` and plan dicing included — ship
with the `devpro` command itself (Package and Command, Dicing and Checks); the dicing snippets
package carries only their runner shortcuts. The kbase component also delivers
the kb-tools package (runner snippets: `justfile` and `Makefile` fragments a project includes,
inside the `kbase` skill's own directory) and the harness's `kbase` MCP entry.
```

**As it stands:**
```
A **runner include line** is the line that includes one package's runner snippets in the project's
**runner file**, its `justfile` or `Makefile`. One package carries snippets: the kb-tools, a set
called `kb`. A project install with the kbase component writes its line. Only a project install under a harness whose plugin
nests in the project (claude, opencode) writes one; a mage install writes no runner include line and
creates no `Makefile`, and nothing is written into this repository's own runner file. A line names
the snippets inside the installed tree (under claude,
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/`; under opencode, the same below
`.opencode/plugins/devpro/`). The line does nothing where the snippets are absent: `import? '<path>'`
in a justfile, `-include <path>` in a Makefile. A project with neither runner file gets a `Makefile`
created to hold every line the install writes. The line an install wrote for the docdicer tools
package — retired with the absorbed dicing verbs — the install removes itself: a non-comment line
whose snippets path ends `runner-snippets/docdicer.just` or `runner-snippets/docdicer.mk` and whose
first path segment is the harness directory this install writes is removed, the removal named in the
install report; a docdicer line naming another harness directory's snippets is reported and left.
```
**Becomes:**
```
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
```

**As it stands:**
```
devpro, the generator, needs Python 3.9 or later on the host; the kbase component's toolchain is the
`kbase` executable the operator installs, which needs no Python. The docdicer launcher needs `python3` 3.9 or later with its `venv` module,
and installing the package from its git URL needs `git` on `PATH`.
Everything else the kbase component needs (pandoc 3.12, git, a way to reach a model) is kbase's own
```
**Becomes:**
```
devpro, the generator, needs Python 3.9 or later on the host; the kbase component's toolchain is the
`kbase` executable the operator installs, which needs no Python.
Everything else the kbase component needs (pandoc 3.12, git, a way to reach a model) is kbase's own
```

### [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md) — the launcher's banner rule and the body-path example

**As it stands:**
```
written without frontmatter and carries the two lines as those comments. A copied package file of a script or
build-file type (`.py`, `.sh`, `.mk`, `.just`), and the extensionless launcher `tools/docdicer`,
carries an installed banner at its top, below its shebang where it has one. Both banners say to
```
**Becomes:**
```
written without frontmatter and carries the two lines as those comments. A copied package file of a script or
build-file type (`.py`, `.sh`, `.mk`, `.just`)
carries an installed banner at its top, below its shebang where it has one. Both banners say to
```

**As it stands:**
```
A definition body names no installed path below the harness directory for a session to run or edit. A
script inside a skill's own directory is named relative to that directory (`tools/docdicer`); the
profiler's launcher sits in the install directory's `profiler/` and is named relative to the skill's
directory too (`../../profiler/hp.sh`). The
```
**Becomes:**
```
A definition body names no installed path below the harness directory for a session to run or edit. A
script inside a skill's own directory is named relative to that directory: the
profiler's launcher sits in the install directory's `profiler/` and is named relative to the skill's
directory (`../../profiler/hp.sh`). The
```

**As it stands:**
```
the file is read. Every other copied file — `tools/.gitignore` among them — and every harness
resource is installed byte-verbatim.
```
**Becomes:**
```
the file is read. Every other copied file — a package's `.gitignore` among them — and every harness
resource is installed byte-verbatim.
```

### [Install destination](PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md) — the user-level package list

**As it stands:**
```
install-time probe or guardrail registration (Shipped files), no shipped package (none of
`kb-tools/` and the development scripts package), no runner include line and no runner file.
```
**Becomes:**
```
install-time probe or guardrail registration (Shipped files), no shipped package (none of
`kb-tools/`, the dicing snippets package and the development scripts package), no runner include
line and no runner file.
```

### [Write Safety](PROJECT_DOCS/SPEC/write-safety.md) — the docdicer package and its venv

**As it stands:**
```
destination is replaced whole, `skills/kbase/kb-tools/` included, except a `.venv` directly under it,
which stays. The development scripts package and the docdicer tools package are replaced the same way.
```
**Becomes:**
```
destination is replaced whole, `skills/kbase/kb-tools/` included, except a `.venv` directly under it,
which stays. The development scripts package is replaced the same way.
```

**As it stands:**
```
An up-to-date run reports `up to date: <harness-dir> — nothing written`, exits 0 and touches
nothing: no file
written, no mode or modification time changed, no package destination replaced and no `tools/.venv`
removed. "Nothing" is judged on the result: every file the install would
```
**Becomes:**
```
An up-to-date run reports `up to date: <harness-dir> — nothing written`, exits 0 and touches
nothing: no file
written, no mode or modification time changed, no package destination replaced and no `.venv`
removed. "Nothing" is judged on the result: every file the install would
```

**As it stands:**
```
destination is replaced whole, `skills/kbase/kb-tools/` included, except a `.venv` directly under it,
which stays. The development scripts package is replaced the same way.
```
**Becomes:**
```
destination is replaced whole, `skills/kbase/kb-tools/` included, except a `.venv` directly under it,
which stays. The development scripts and dicing snippets packages are replaced the same way.
```

### [Guide and README](PROJECT_DOCS/SPEC/guide-and-readme.md) — the just floor is the devpro line's

**As it stands:**
```
  - the requirements: `just` 1.27.0 or later, and 1.33.0 or later where the kbase component ships,
    for the kb include line; `perl` with core `JSON::PP` for the claude guardrail; and the
```
**Becomes:**
```
  - the requirements: `just` 1.27.0 or later, and 1.33.0 or later where the devpro line ships — on
    every project install of a nested plugin — for the `import?` of the include lines, the kb line
    with the kbase component riding the same floor; `perl` with core `JSON::PP` for the claude
    guardrail; and the
```

### [README](README.md) — the include-line promise states both lines

**As it stands:**
```
- `just` 1.27.0 or later, where the project's runner is a justfile, and 1.33.0 or later there where the kbase component ships: the `kb` include line an install with that component writes is an `import?`, which earlier `just` rejects. No install checks the version.
```
**Becomes:**
```
- `just` 1.27.0 or later, where the project's runner is a justfile, and 1.33.0 or later there wherever the devpro line ships: every project install of a nested plugin writes that line, an `import?`, which earlier `just` rejects; the `kb` include line an install with the kbase component also writes rides the same floor. No install checks the version.
```

**As it stands:**
```
A project install under claude or opencode adds one include line to the project's `justfile` or
`Makefile` — an `import?` or an `-include` — for the runner snippets it installs, and a project
with neither runner file gets a new `Makefile` holding it. The line is the kb-tools package's, `kb`,
written with `--components=kbase`. A line an earlier release wrote for the docdicer tools package,
retired with the absorbed dicing verbs, the install removes, naming the removal in its report. The
```
**Becomes:**
```
A project install under claude or opencode adds the include lines to the project's `justfile` or
`Makefile` — an `import?` or an `-include` — for the runner snippets it installs, and a project
with neither runner file gets a new `Makefile` holding them. One is the dicing snippets package's,
`devpro`, written on every project install of a nested plugin; another is the kb-tools package's,
`kb`, written with `--components=kbase`. A line an earlier release wrote for the docdicer tools
package — retired with the absorbed dicing verbs, and none of its snippet paths point at anything
any more — the install removes, naming the removal in its report. The
```

**As it stands:**
```
A project installed by 0.17.x upgrades in two runs. The first removes `skills/docdicer/tools/`'s own
files — the dicer, its runner snippets — along with the `docdicer` skill's files, and removes the
docdicer include line from the project's runner file, naming it in the report; a `Makefile` it
created and that line was the only content of goes with it. Then the tree is exhausted: a second
install reports nothing and leaves the same files where it left them.

What survives both runs is the launcher's `.venv` under `skills/docdicer/tools/`, with everything in
it, and the directory `skills/docdicer/` holding it. Nothing uses what is there: no definition, no
include line, and no install writes into it, the prune keeping a `VENV_DIR` entry by rule. Delete
`skills/docdicer/` once, and the upgrade is complete.
```
**Becomes:**
```
A project installed by 0.17.x upgrades in two runs. The first removes `skills/docdicer/tools/`'s own
files — the dicer, its runner snippets — along with the `docdicer` skill's earlier files, and
removes the docdicer include line from the project's runner file, naming it in the report; the
include line it writes for the new dicing snippets package lands in the same runner file. Then the
tree is exhausted: a second install reports nothing and leaves the same files where it left them.

What survives both runs is the launcher's `.venv` under `skills/docdicer/tools/`, with everything in
it, and the directory `skills/docdicer/tools/` holding it. Nothing uses what is there: no
definition, no include line, and no install writes into it, the prune keeping a `VENV_DIR` entry by
rule. Delete `skills/docdicer/tools/` once, and the upgrade is complete.
```

## ARCHITECTURE delta

### [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md) — the hosted clone and the tools package out, the dicing package and its snippets in

**As it stands:**
````
docdicer/               gitignored hosted clone — the docdicer project this repository's `just dev-dd`, `just dev-kanban` and `just dev-check-links` run in place, cloned by `docdicer-repo`; never installed and not package data
````
**Becomes:**
````
````

**As it stands:**
````
  docdicer-tools/       shipped package, owned by `docdicer` and so delivered by every project install — the `docdicer` bash launcher, which builds and runs a docdicer venv beside itself on demand, a `.gitignore` holding `.venv/`, and the runner snippets (docdicer.just, docdicer.mk) a project install writes the consuming project's include line for; nothing importable; installed under <install-dir>/skills/docdicer/tools/, inside the docdicer skill's own directory (DOCDICER_TOOLS_PACKAGE, devpro/install.py)
````
**Becomes:**
````
  dicing/               the absorbed dicing package — the docdicer project's dicer, checks and board as devpro code, run as devpro's dicing and check verbs (Dicing and Checks); importable Python, the board's assets (kanban/assets/) the package data it ships (Packaging), the absorbed project's contract documents carried into Dicing and Checks, its tests joining the devpro test surface
````

**As it stands:**
````
  dicing/               the absorbed dicing package — the docdicer project's dicer, checks and board as devpro code, run as devpro's dicing and check verbs (Dicing and Checks); importable Python, the board's assets (kanban/assets/) the package data it ships (Packaging), the absorbed project's contract documents carried into Dicing and Checks, its tests joining the devpro test surface
````
**Becomes:**
````
  dicing/               the absorbed dicing package — the docdicer project's dicer, checks and board as devpro code, run as devpro's dicing and check verbs (Dicing and Checks); importable Python, the board's assets (kanban/assets/) the package data it ships (Packaging), the absorbed project's contract documents carried into Dicing and Checks, its tests joining the devpro test surface
  dicing-snippets/      shipped package, owned by `docdicer` and so delivered by every project install — the runner snippets (devpro.just, devpro.mk) a project install writes the consuming project's include line for, which run the `devpro` command from `PATH`; nothing importable; installed under <install-dir>/skills/docdicer/dicing-snippets/, inside the docdicer skill's own directory (DICING_SNIPPETS_PACKAGE, devpro/install.py)
````

### [Packaging](PROJECT_DOCS/ARCHITECTURE/packaging.md) — the wheel's data globs and the lazy entry point

**As it stands:**
```
- **Package data.** `[tool.setuptools.package-data]` lists five patterns, `kb-tools/**/*`,
  `harnesses/resources/**/*`, `docdicer-tools/**/*`, `docdicer-tools/**/.*` and
  `development-tools/**/*`: the trees `install.py`
  reads through `PACKAGE_ROOT` (`HARNESS_RESOURCES_SOURCE` and each `SHIPPED_PACKAGES` source,
  the kb-tools, docdicer-tools and development-tools trees). The `.*` pattern exists because
  setuptools' `**/*` skips dotfiles, and the docdicer package ships a `.gitignore`. A glob sweeps in whatever sits
```
**Becomes:**
```
- **Package data.** `[tool.setuptools.package-data]` lists four patterns, `kb-tools/**/*`,
  `harnesses/resources/**/*`, `development-tools/**/*` and
  `dicing/kanban/assets/**/*`: the trees `install.py`
  reads through `PACKAGE_ROOT` (`HARNESS_RESOURCES_SOURCE` and each `SHIPPED_PACKAGES` source,
  the kb-tools and development-tools trees) and the board's assets (Repo Layout), which
  `importlib.resources` serves. A glob sweeps in whatever sits
```

**As it stands:**
```
- **Package data.** `[tool.setuptools.package-data]` lists four patterns, `kb-tools/**/*`,
  `harnesses/resources/**/*`, `development-tools/**/*` and
  `dicing/kanban/assets/**/*`: the trees `install.py`
  reads through `PACKAGE_ROOT` (`HARNESS_RESOURCES_SOURCE` and each `SHIPPED_PACKAGES` source,
  the kb-tools and development-tools trees) and the board's assets (Repo Layout), which
  `importlib.resources` serves. A glob sweeps in whatever sits
```
**Becomes:**
```
- **Package data.** `[tool.setuptools.package-data]` lists six patterns, `kb-tools/**/*`,
  `harnesses/resources/**/*`, `development-tools/**/*`, `dicing-snippets/**/*`,
  `profiler/view.html` and `dicing/kanban/assets/**/*`: the trees `install.py`
  reads through `PACKAGE_ROOT` (`HARNESS_RESOURCES_SOURCE` and each `SHIPPED_PACKAGES` source,
  the kb-tools, development-tools and dicing-snippets trees), the board's assets (Repo Layout) and
  the profiler's page template (Harness profiler), which `importlib.resources` serves. A glob
  sweeps in whatever sits
```

**As it stands:**
```
- **Console script.** `devpro = "devpro.cli:main"`. argparse's `prog` is `"devpro"`, so
  `devpro --help` and `python3 -m devpro --help` print the same text.
```
**Becomes:**
```
- **Console script.** `devpro = "devpro.cli:main"`. argparse's `prog` is `"devpro"`, so
  `devpro --help` and `python3 -m devpro --help` print the same text. The dispatch is lazy: the
  entry point imports only the verb invoked, and every verb imports no third-party dependency
  (Package and Command), so no verb pays for another verb's imports.
```

### [Recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md) — the verbs run from devpro; the consumer's floor is the devpro line's

**As it stands:**
```
**Toolchain.** This repository's justfile needs `just` 1.33.0 or later: its `import?` line is that
release's, and the `[doc]` recipe attribute it also uses arrived in 1.27.0. It runs its recipes under
`bash`. A consuming project's floor is the same 1.33.0, for the `import?` of the include line
(SPEC.md, Guide and README). That import is the install's own snippet,
`.claude/skills/devpro/skills/docdicer/tools/runner-snippets/docdicer.just`, so this checkout needs
one `just agents` run before its docdicer recipes exist: until it has run, the `docs` surface —
`just check-links`, and so `just test` and `just test-changed` on any document — fails with
`Does not contain recipe 'docdicer'`. A design's delta application is verified by
`check-design --deltas-applied`, which the snippet set exposes as
`docdicer-check-design-deltas-applied`; this repository runs it as
`just dev-check-design-deltas-applied`, through `dev-dd` against the hosted clone. The `_venv`
```
**Becomes:**
```
**Toolchain.** This repository's justfile needs `just` 1.27.0 or later, for the `[doc]` recipe
attribute; a consuming project's floor is 1.33.0 or later where the kbase component ships, for the
`import?` of the kb include line
(SPEC.md, Guide and README). It runs its recipes under
`bash`. The dicing and check verbs run through the `devpro` command — `python3 -m devpro` in the
checkout's venv — so no import or snippet stands between this checkout and its `docs` surface:
`just check-links` runs the absorbed verb directly. A design's delta application is verified by
`check-design --deltas-applied`; this repository runs it as
`just dev-check-design-deltas-applied`, over the absorbed verb. The `docdicer-repo`, `dev-dd` and
`dev-kanban` recipes, and `docdicer-repo.sh` with its test, retire with the hosted clone; the
dev-check recipes run the absorbed verbs. The `_venv`
```

**As it stands:**
```
**Toolchain.** This repository's justfile needs `just` 1.27.0 or later, for the `[doc]` recipe
attribute; a consuming project's floor is 1.33.0 or later where the kbase component ships, for the
`import?` of the kb include line
(SPEC.md, Guide and README). It runs its recipes under
```
**Becomes:**
```
**Toolchain.** This repository's justfile needs `just` 1.27.0 or later, for the `[doc]` recipe
attribute; a consuming project's floor is 1.33.0 or later where the devpro line ships — on every
project install of a nested plugin — for the `import?` of the include lines, the kb line with the
kbase component riding the same floor
(SPEC.md, Guide and README). It runs its recipes under
```

### [Plugins](PROJECT_DOCS/ARCHITECTURE/install/plugins.md) — two shipped rows with snippets, the retired line's cleanup

**As it stands:**
```
**Owners.** A supporting artifact ships iff the definition that uses it ships. Each package is a row
of `SHIPPED_PACKAGES` (`devpro/install.py`), a `ShippedPackage` of source, destination, owner and `snippets` (a `runner_file.SnippetSet`, or none):

| source in `devpro/` | destination below the install directory | owner |
|---|---|---|
| `docdicer-tools` | `skills/docdicer/tools` | `docdicer` |
| `development-tools` | `skills/development/scripts` | `development` |
| `kb-tools` | `skills/kbase/kb-tools` | `kbase` |

`install` takes the rows whose owner the selection's `ships(name)` admits, and none on a user-level
```
**Becomes:**
```
**Owners.** A supporting artifact ships iff the definition that uses it ships. Each package is a row
of `SHIPPED_PACKAGES` (`devpro/install.py`), a `ShippedPackage` of source, destination, owner and `snippets` (a `runner_file.SnippetSet`, or none):

| source in `devpro/` | destination below the install directory | owner |
|---|---|---|
| `development-tools` | `skills/development/scripts` | `development` |
| `kb-tools` | `skills/kbase/kb-tools` | `kbase` |

`install` takes the rows whose owner the selection's `ships(name)` admits, and none on a user-level
```

**As it stands:**
```
**The runner include lines**, appended to the project's justfile or Makefile, follow the shipped
packages that carry snippets: a `ShippedPackage` row's `snippets` field is a `runner_file.SnippetSet`
(label, snippets directory below the package's destination, snippet name per runner), set on the
docdicer tools row (`docdicer`) and the kb-tools row (`kb`). The lines are written where the install
ships at least one such row and is a project install of a nested plugin
(`_is_project_install_of_a_nested_plugin`), so every install writes the docdicer line and one with
the kbase component also the kb line. `ShippedPackage.installed_snippets()` joins the destination to the set's directory, and a line names the
```
**Becomes:**
```
**The runner include lines**, appended to the project's justfile or Makefile, follow the shipped
packages that carry snippets: a `ShippedPackage` row's `snippets` field is a `runner_file.SnippetSet`
(label, snippets directory below the package's destination, snippet name per runner), set on the
kb-tools row (`kb`) alone. The lines are written where the install
ships at least one such row and is a project install of a nested plugin
(`_is_project_install_of_a_nested_plugin`), so one with
the kbase component writes the kb line. `ShippedPackage.installed_snippets()` joins the destination to the set's directory, and a line names the
```

**As it stands:**
```
Mage gets no line and no `Makefile`. A line is this install's when its first path
segment equals `harness_relpath`'s, and its path token is then spliced in place. A set's line is
recognized by the path's shape, ending `<snippets directory name>/<snippet>`, so the `docdicer` and
`kb` sets never match each other's line. A set whose line is reported and left does not stop the
others. Where the project has no runner file, one `Makefile` is created holding every line.
```
**Becomes:**
```
Mage gets no line and no `Makefile`. A line is this install's when its first path
segment equals `harness_relpath`'s, and its path token is then spliced in place. A set's line is
recognized by the path's shape, ending `<snippets directory name>/<snippet>`. A set whose line is reported and left does not stop the
others. Where the project has no runner file, one `Makefile` is created holding every line.

The retired docdicer set's line is this install's to clean up: the dicing verbs are devpro's own
(Dicing and Checks), and the install removes the docdicer line as SPEC.md, Plugins, states it —
recognized by the same shape rule that recognizes its own lines (`_snippet_pattern`), removed, and
the removal named in the install report; a docdicer line naming another harness directory's
snippets is reported and left.
```

**As it stands:**
```
| source in `devpro/` | destination below the install directory | owner |
|---|---|---|
| `development-tools` | `skills/development/scripts` | `development` |
| `kb-tools` | `skills/kbase/kb-tools` | `kbase` |
```
**Becomes:**
```
| source in `devpro/` | destination below the install directory | owner |
|---|---|---|
| `development-tools` | `skills/development/scripts` | `development` |
| `dicing-snippets` | `skills/docdicer/dicing-snippets` | `docdicer` |
| `kb-tools` | `skills/kbase/kb-tools` | `kbase` |
```

**As it stands:**
```
packages that carry snippets: a `ShippedPackage` row's `snippets` field is a `runner_file.SnippetSet`
(label, snippets directory below the package's destination, snippet name per runner), set on the
kb-tools row (`kb`) alone. The lines are written where the install
ships at least one such row and is a project install of a nested plugin
(`_is_project_install_of_a_nested_plugin`), so one with
the kbase component writes the kb line. `ShippedPackage.installed_snippets()` joins the destination to the set's directory, and a line names the
installed snippets at `<harness-relpath>/<destination>/<set directory>/<snippet>`, `harness_relpath` being the install directory
relative to the project root, so under claude
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/kb.just`, and under opencode the same
below `.opencode/plugins/devpro/`. `runner_file.install_include_lines` writes them, in the
```
**Becomes:**
```
packages that carry snippets: a `ShippedPackage` row's `snippets` field is a `runner_file.SnippetSet`
(label, snippets directory below the package's destination, snippet name per runner), set on the
dicing snippets row (`devpro`) and the kb-tools row (`kb`). The lines are written where the install
ships at least one such row and is a project install of a nested plugin
(`_is_project_install_of_a_nested_plugin`), so every project install writes the devpro line and one
with the kbase component also writes the kb line. `ShippedPackage.installed_snippets()` joins the destination to the set's directory, and a line names the
installed snippets at `<harness-relpath>/<destination>/<set directory>/<snippet>`, `harness_relpath` being the install directory
relative to the project root, so under claude
`.claude/skills/devpro/skills/docdicer/dicing-snippets/runner-snippets/devpro.just` and
`.claude/skills/devpro/skills/kbase/kb-tools/runner-snippets/kb.just`, and under opencode the same
below `.opencode/plugins/devpro/`. `runner_file.install_include_lines` writes them, in the
```

**As it stands:**
```
Mage gets no line and no `Makefile`. A line is this install's when its first path
segment equals `harness_relpath`'s, and its path token is then spliced in place. A set's line is
recognized by the path's shape, ending `<snippets directory name>/<snippet>`. A set whose line is reported and left does not stop the
others. Where the project has no runner file, one `Makefile` is created holding every line.
```
**Becomes:**
```
Mage gets no line and no `Makefile`. A line is this install's when its first path
segment equals `harness_relpath`'s, and its path token is then spliced in place. A set's line is
recognized by the path's shape, ending `<snippets directory name>/<snippet>` — the devpro, kb and
retired docdicer sets share the `runner-snippets` directory name, and the snippet file name alone
tells their shapes apart, so no set's line ever matches another's. A set whose line is reported and left does not stop the
others. Where the project has no runner file, one `Makefile` is created holding every line.
```

**As it stands:**
```
The retired docdicer set's line is this install's to clean up: the dicing verbs are devpro's own
(Dicing and Checks), and the install removes the docdicer line as SPEC.md, Plugins, states it —
recognized by the same shape rule that recognizes its own lines (`_snippet_pattern`), removed, and
the removal named in the install report; a docdicer line naming another harness directory's
snippets is reported and left.
```
**Becomes:**
```
The retired docdicer set's line is still this install's to clean up, the cleanup staying as stage 1
landed it: the dicing verbs are devpro's own (Dicing and Checks), and the install removes the
docdicer line as SPEC.md, Plugins, states it — recognized by the same shape rule that recognizes
its own lines (`_snippet_pattern`), removed, and the removal named in the install report; a
docdicer line naming another harness directory's snippets is reported and left. The cleanup stands
beside the devpro line's return: the retired set's snippets are `docdicer.just` and `docdicer.mk`,
paths that point at nothing any more, and the devpro set ships `devpro.just` and `devpro.mk`, so
the cleanup never touches a line of the new set.
```

### [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md) — three package rows, no launcher naming, no tool install

**As it stands:**
```
wider than the install directory would delete a neighbor's. That walk needs no carve-out for a package
destination: the three `SHIPPED_PACKAGES` rows, the docdicer tools package, the development scripts
package and the kb-tools package, all sit inside the install directory's `skills/` —
`skills/docdicer/tools/`, `skills/development/scripts/` and `skills/kbase/kb-tools/`, each in its
skill's own directory — where every file they hold is stamped installed or left unstamped, never
generated, so every file under those trees is still either ours or untouched. A `.venv` the
docdicer script builds under its destination is outside what `_shipped` admits too, so its files
never enter the stale list. A definition of ours that this run did not write, such as one its plugin
```
**Becomes:**
```
wider than the install directory would delete a neighbor's. That walk needs no carve-out for a package
destination: the two `SHIPPED_PACKAGES` rows, the development scripts
package and the kb-tools package, both sit inside the install directory's `skills/` —
`skills/development/scripts/` and `skills/kbase/kb-tools/`, each in its
skill's own directory — where every file they hold is stamped installed or left unstamped, never
generated, so every file under those trees is still either ours or untouched. A `.venv` directly
under a package destination is outside what `_shipped` admits too, so its files
never enter the stale list. A definition of ours that this run did not write, such as one its plugin
```

**As it stands:**
```
removes nothing `_shipped` excludes, so a file outside it is never stale. A copied file takes the
installed banner when its suffix is in `STAMPED_SUFFIXES` (`.py`, `.sh`, `.mk`, `.just`) or its name
is in `STAMPED_NAMES` (`docdicer`, the one extensionless
launcher); `stamped` places the banner below a shebang. Any other file — the package's `.gitignore`
among them — is copied byte-verbatim.
```
**Becomes:**
```
removes nothing `_shipped` excludes, so a file outside it is never stale. A copied file takes the
installed banner when its suffix is in `STAMPED_SUFFIXES` (`.py`, `.sh`, `.mk`, `.just`) or its name
is in `STAMPED_NAMES`; `stamped` places the banner below a shebang. Any other file — a package's
`.gitignore`
among them — is copied byte-verbatim.
```

**As it stands:**
```
The docdicer package lands inside the `docdicer` skill's own directory, so the skill names its script
`tools/docdicer`, relative to that directory. That is the one body path not written against the
harness directory (SPEC.md, Deployed Surfaces, Installed tree), because the skill's
directory differs by harness.
```
**Becomes:**
```
```

**As it stands:**
```
**No tool install.** `install` runs no shipped package's script and takes no callable for one. The docdicer
tools package's destination is replaced like any other, and the `.venv` the launcher built beside
itself is kept. On its next run the launcher rebuilds that venv where its python does not run, and
reinstalls the docdicer it names where the venv's docdicer reports another version (SPEC.md, Deployed Surfaces, Shipped files). The install manages no dependencies across
packages, and needs no network.
```
**Becomes:**
```
**No tool install.** `install` runs no shipped package's script and takes no callable for one. The
install manages no dependencies across
packages, and needs no network.
```

**As it stands:**
```
wider than the install directory would delete a neighbor's. That walk needs no carve-out for a package
destination: the two `SHIPPED_PACKAGES` rows, the development scripts
package and the kb-tools package, both sit inside the install directory's `skills/` —
`skills/development/scripts/` and `skills/kbase/kb-tools/`, each in its
skill's own directory — where every file they hold is stamped installed or left unstamped, never
generated, so every file under those trees is still either ours or untouched. A `.venv` directly
under a package destination is outside what `_shipped` admits too, so its files
never enter the stale list. A definition of ours that this run did not write, such as one its plugin
```
**Becomes:**
```
wider than the install directory would delete a neighbor's. That walk needs no carve-out for a package
destination: the three `SHIPPED_PACKAGES` rows, the development scripts
package, the dicing snippets package and the kb-tools package, all sit inside the install directory's `skills/` —
`skills/development/scripts/`, `skills/docdicer/dicing-snippets/` and `skills/kbase/kb-tools/`, each in its
skill's own directory — where every file they hold is stamped installed or left unstamped, never
generated, so every file under those trees is still either ours or untouched. A `.venv` directly
under a package destination is outside what `_shipped` admits too, so its files
never enter the stale list. A definition of ours that this run did not write, such as one its plugin
```

### [Why There Is No Verification Verb](PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md) — the include lines in a slot

**As it stands:**
```
(`devtools/render_diff.py` states the rules). `just render <slug>` renders into `rendered/<slug>/`
and refuses a slug starting with `reference`. A slot holds one slot project
(`rendered/<slug>/devpro/`), an install of the devpro set with the kbase component on, with itself
as project root, so beside the definitions it holds the kb-tools package, the harness's
MCP entry and the runner include lines (the docdicer line always, the kb line with the component
on; none in the mage slot, a harness-directory plugin), and it
```
**Becomes:**
```
(`devtools/render_diff.py` states the rules). `just render <slug>` renders into `rendered/<slug>/`
and refuses a slug starting with `reference`. A slot holds one slot project
(`rendered/<slug>/devpro/`), an install of the devpro set with the kbase component on, with itself
as project root, so beside the definitions it holds the kb-tools package, the harness's
MCP entry and the kb runner include line with the component
on (none in the mage slot, a harness-directory plugin), and it
```

**As it stands:**
```
(`devtools/render_diff.py` states the rules). `just render <slug>` renders into `rendered/<slug>/`
and refuses a slug starting with `reference`. A slot holds one slot project
(`rendered/<slug>/devpro/`), an install of the devpro set with the kbase component on, with itself
as project root, so beside the definitions it holds the kb-tools package, the harness's
MCP entry and the kb runner include line with the component
on (none in the mage slot, a harness-directory plugin), and it
```
**Becomes:**
```
(`devtools/render_diff.py` states the rules). `just render <slug>` renders into `rendered/<slug>/`
and refuses a slug starting with `reference`. A slot holds one slot project
(`rendered/<slug>/devpro/`), an install of the devpro set with the kbase component on, with itself
as project root, so beside the definitions it holds the kb-tools package, the harness's
MCP entry and the runner include lines — the devpro line always, the kb line with the component
on (none in the mage slot, a harness-directory plugin), and it
```

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md) — the docdicer skill routes devpro's verbs

**As it stands:**
```
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered with its
  tools package by every install.
  `docdicer.py` names its script `tools/docdicer`, relative to the skill's directory, and says its
  first run installs docdicer beside it; the script's `--help` is the command list, which the skill
  does not restate in full. The skill carries no install step; its one runner instruction is that
  where the project's runner includes the docdicer snippet, docdicer is run through the recipes
  (`docdicer`, and by name `docdicer-help`, `docdicer-check-plan`, `docdicer-check-design`,
  `docdicer-check-design-deltas-applied`, `docdicer-check-roadmap` and `docdicer-kanban`), each of
  the last four checking the active plan, the active design, the active design's applied deltas and
  `ROADMAP.md`, with a path given to `docdicer` for any other.
  Its `kanban` paragraph has the session offer to run the board as a background process or hand
  over the command line, the user choosing.
  It also carries a paragraph, an optional reference to `kbase` (Rendering, Placeholders), saying
  `kb-root/` belongs to kbase and docdicer leaves it alone unless the user directs otherwise; it
  renders only where kbase ships. The docdicer version the script
  installs is written once, as `VERSION` in `devpro/docdicer-tools/docdicer`.
```
**Becomes:**
```
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered by every
  install.
  `docdicer.py` routes the session to devpro's dicing verbs — `devpro dice-doc`, `devpro undice`,
  the check verbs and `devpro kanban` — run from the command line, and does not restate their
  `--help` (CONVENTIONS.md, A skill omits its tool's offered surface). The skill carries no install
  step and no runner instruction: the recipes and snippets the docdicer tools package carried are
  retired with it (Plugins). Its `kanban` paragraph has the session offer to run the board as a
  background process or hand over the command line, the user choosing.
  It also carries a paragraph, an optional reference to `kbase` (Rendering, Placeholders), saying
  `kb-root/` belongs to kbase and docdicer leaves it alone unless the user directs otherwise; it
  renders only where kbase ships.
```

**As it stands:**
```
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered by every
  install.
  `docdicer.py` routes the session to devpro's dicing verbs — `devpro dice-doc`, `devpro undice`,
  the check verbs and `devpro kanban` — run from the command line, and does not restate their
  `--help` (CONVENTIONS.md, A skill omits its tool's offered surface). The skill carries no install
  step and no runner instruction: the recipes and snippets the docdicer tools package carried are
  retired with it (Plugins). Its `kanban` paragraph has the session offer to run the board as a
  background process or hand over the command line, the user choosing.
  It also carries a paragraph, an optional reference to `kbase` (Rendering, Placeholders), saying
  `kb-root/` belongs to kbase and docdicer leaves it alone unless the user directs otherwise; it
  renders only where kbase ships.
```
**Becomes:**
```
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered by every
  install.
  `docdicer.py` routes the session to devpro's dicing verbs — `devpro dice-doc`, `devpro undice`,
  the check verbs and `devpro kanban` — run from the command line, and does not restate their
  `--help` (CONVENTIONS.md, A skill omits its tool's offered surface). The skill carries no install
  step. Its runner instruction is back, naming the recipes of the `devpro` snippet set: where the
  project's runner includes that set, the checks run through the recipes (`devpro`, and by name
  `devpro-help`, `devpro-check-plan`, `devpro-check-design`,
  `devpro-check-design-deltas-applied` and `devpro-check-roadmap`), the four gates argumentless,
  each checking the active file under the project root — the active plan, the active design, the
  active design's applied deltas and `ROADMAP.md` — with a direct `devpro` call for any other
  (Plugins). Its
  `kanban` paragraph has the session offer to run the board as a background process or hand over
  the command line, the user choosing.
  It also carries a paragraph, an optional reference to `kbase` (Rendering, Placeholders), saying
  `kb-root/` belongs to kbase and docdicer leaves it alone unless the user directs otherwise; it
  renders only where kbase ships.
```

**As it stands:**
```
- **Guide skill** — `guide` (`definitions/guide.py`): one `SKILL.md` and two supporting files,
  `references/installing.md` and `references/using.md`, carried as `SkillFile`s, delivered
  under every harness. The description names the uses SPEC.md, Guide and README lists, and
```
**Becomes:**
```
- **Guide skill** — `guide` (`definitions/guide.py`): one `SKILL.md` and two supporting files,
  `references/installing.md` and `references/using.md`, carried as `SkillFile`s, delivered
  under every harness. Its board section routes the board through the `docdicer` skill's routing
  and names no launcher path or recipe: the launcher paths and recipes it named are retired with
  the docdicer tools package (Plugins). The description names the uses SPEC.md, Guide and README lists, and
```

**As it stands:**
```
  with every install, so each fills. The *Plan status* and *Roadmap tickets* sections render whole
  under every install; each one's `check-plan` or `check-roadmap` instruction is a paragraph of its
  own, so an optional reference that fills to nothing drops that paragraph alone. The sentence
```
**Becomes:**
```
  with every install, so each fills. The *Plan status* and *Roadmap tickets* sections render whole
  under every install; each one's `check-plan` or `check-roadmap` instruction is a paragraph of its
  own, so an optional reference that fills to nothing drops that paragraph alone. The *Design*
  section's delta-application sentence names no runner recipe: the application is verified by
  `check-design --deltas-applied`, the runner recipe it named retired with the docdicer tools
  package (Recipes). The sentence
```

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md) — the profiler stores rename to dot directories

The user renamed the profiler's stores: `.devpro-temp/claude-profiler/` and
`.devpro-temp/opencode-profiler/` become `.devpro-temp/.profiler-claude/` and
`.devpro-temp/.profiler-opencode/` — dot-directory naming, so all the profiler's stores group
together and sort to the top of the scratch tree. The rename is naming, not hierarchy: the
attribution entry's flat-store statement stands untouched. Everything that names a store moves with
it — the captures' write paths, the render side's read pattern, the skill's locate text — and the
store path the attribution pair quotes takes the new spelling with the rename, its statement
unaltered. This entry is stage-2 surface work — the next plan's content — and stays pending until
that plan lands it.

The code side moves with the pairs. `hp.py`'s `TRACE_DIR` default (`Path(".devpro-temp") /
"claude-profiler"`) and its `TRACE_GLOB` (`"*-profiler"`) take the new names: the claude capture
writes `.profiler-claude`, and the tree and page read every `.profiler-*` directory under
`.devpro-temp/`. `profiler.ts`'s `TRACE_DIR` (`join(".devpro-temp", "opencode-profiler")`) writes
`.profiler-opencode`. The `show-profile` skill's locate paragraph, which names the two store
directories, names the new ones. `tests/test_devpro_profiler.py` pins the old paths — the store
fixtures it writes (`claude-profiler`, `opencode-profiler`, `broken-profiler`) and the trace paths
it asserts — and updating those pins is the stage-2 plan's work.

**The migration of existing stores.** The boundary question stage 2 must settle: the existing
`.devpro-temp/*-profiler/` trees hold real traces — the live claude and opencode stores. The
stage-2 plan chooses between renaming the existing stores in place and reading both patterns
during a migration window, the old stores read-only while new captures write the new names. The
no-half-absorbed-state rule applies to stores too: at the choice's end one store name per harness
stands and every trace the old names held is readable under the new one — never a state where the
capture writes one name and traces sit under the other.

**As it stands:**
```
module, not a new mechanism, and no entry is gated on the install-time probe. A capture appends one line to the project's `.devpro-temp/claude-profiler/<session-id>.jsonl` — one of the per-harness stores under `.devpro-temp/`, every `*-profiler` directory of which `hp.py`'s `tree` renders — the project's scratch
```
**Becomes:**
```
module, not a new mechanism, and no entry is gated on the install-time probe. A capture appends one line to the project's `.devpro-temp/.profiler-claude/<session-id>.jsonl` — one of the per-harness stores under `.devpro-temp/`, every `.profiler-*` directory of which `hp.py`'s `tree` renders — the project's scratch
```

**As it stands:**
```
nothing from the network, so the records it renders never leave the machine. Its main page is the
index of record files: every store the `*-profiler` glob finds,
```
**Becomes:**
```
nothing from the network, so the records it renders never leave the machine. Its main page is the
index of record files: every store the `.profiler-*` glob finds,
```

**As it stands:**
```
a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/opencode-profiler/<session-id>.jsonl` store, `harness` `"opencode"`, which `hp.py`'s
tree and page render beside the claude sessions', each record read from its own `*-profiler` store.
```
**Becomes:**
```
a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/.profiler-opencode/<session-id>.jsonl` store, `harness` `"opencode"`, which `hp.py`'s
tree and page render beside the claude sessions', each record read from its own `.profiler-*` store.
```
