# devpro

AI is a tremendous lever for engineering capability, but unsupervised agents write code that rots quietly
and fails suddenly. devpro installs a collaborative AI development process into Claude Code, opencode, or
Mage that lets you build to last: you work with the agents to design, plan, build, review, and deliver.

![kanban screenshot](images/kanban.webp)

*Work packages on the board `devpro dashboard` serves*

## What it asks of you

This process does not run itself, and it does not claim to be a 10X everyone-is-now-an-engineer super suit.
You collaborate on design, architecture, mechanisms, and standards. You have to know what good and bad look
like and you will need to exercise that judgment frequently.

## What it gets you

The installed skills, agents, tools, and AGENTS.md have been coordinated and tuned
to maximize leverage for human attention, minimize decision fatigue, and provide visibility of and
correction steps for the stepwise drift that is unavoidable in agentic coding processes.

My ballpark estimate is a 3X gain over unassisted engineering. It's not the much-hyped 10X of the
ad campaigns, but it is dead real and the output is production-grade. For evidence, look at the git
history of not only this project, but also:

- [linux-kernel-driver-sandbox](https://github.com/benn-herrera/linux-kernel-driver-sandbox)
- [go-inference-lab-bench](https://github.com/benn-herrera/go-inference-lab-bench)
- [kbase](https://github.com/benn-herrera/kbase)
- [docdicer](https://github.com/benn-herrera/docdicer)

I was able to stand up the kernel driver sandbox in a day to learn how to hand-code Linux
kernel device drivers. And the sandbox's learning harness was not sloppy garbage. It was designed
to be efficient, reusable, and transferable. The go-inference-lab-bench project went from a cold
start to a scratch inference engine in Go with proven llama.cpp equivalence and data-driven support
for multiple architectures and multiple loading formats in a little over a month. It does all of that
in just over 16K lines of runtime code, including vision tower support and an OpenAI-compatible HTTP server.

## Requirements and Supported Platforms

- Harness: claude, opencode, or mage; `--harness` takes these three names.
- Homebrew (macOS or Linux), or pipx on a machine without it, to install devpro.
- `just` 1.27.0 or later, where the project's runner is a justfile, and 1.33.0 or later there wherever the devpro line ships: every project install of a nested plugin writes that line, an `import?`, which earlier `just` rejects; the `kb` include line an install with the kbase component also writes rides the same floor. No install checks the version.
- `perl` with core `JSON::PP` for the claude guardrail: without them the install skips the hook, says so in one line, and installs everything else.
- An activity profiler, shipped with a claude or opencode project install: the session's activity is
  recorded to the project's own store under `.devpro-temp/` at the project root — `.profiler-claude/`
  under claude, one line per hook event, and `.profiler-opencode/` under opencode, one per tool call.
  The `tree` subcommand of the `devpro profiler` verb reads every `.profiler-*` store
  there, and the `show-profile` skill hands a session to the user as text, an HTML page or a served
  page, the serving the `devpro dashboard` verb's traces panel. The claude install copies the launcher `profiler/hp.sh` and registers six hook entries in the
  plugin's `hooks/hooks.json`; the opencode install copies the launcher and the capture `profiler.ts`
  beside the plugin entry and registers no hook entries. The page template `view.html` is the devpro
  wheel's own package data, not an install resource.
- Under mage, `show-profile` ships with no launcher and no capture, so a mage session records nothing
  and has no trace to read. A claude session on the web loads no plugin's hooks and records nothing
  there until `init` commits the hook; the skill names that `init`.

## Quick Start Guide

### Installation

```sh
brew tap benn-herrera/tap
brew trust benn-herrera/tap
brew install devpro
```
or
```sh
pipx install "git+https://github.com/benn-herrera/devpro@v0.17.5"
pipx ensurepath
```
then open a new shell, so `devpro` is on your `PATH`.

The pipx line names the newest release tag. Nothing checks it: the release plan re-stamps it, by hand,
in the release that publishes a version.

Author identity: <https://keyoxide.org/wkd/benn@bennherrera.dev>

### Claude Code and opencode

Install devpro, then run its install from the project root:

```sh
devpro install .
```

The install reads the harness from the `.claude/` or `.opencode/` directory the target holds; where it
holds neither, or holds both, pass `--harness=claude` or `--harness=opencode`. A devpro settings file
that names harnesses installs for each of them instead, one install apiece.

Add the installed tree, the agent scratch space and the agents file's backup to the project's
`.gitignore`, listing the lines of the harness you installed:

```text
# claude
.claude/
# opencode: .opencode/ instead
.devpro-temp/
# the agents file's rolling backup
backup.AGENTS.md
```

A project install under claude or opencode adds the include lines to the project's `justfile` or
`Makefile` — an `import?` or an `-include` — for the runner snippets it installs, and a project
with neither runner file gets a new `Makefile` holding them. One is the dicing snippets package's,
`devpro`, written on every project install of a nested plugin; another is the kb-tools package's,
`kb`, written with `--components=kbase`. A line an earlier release wrote for the docdicer tools
package — retired with the absorbed dicing verbs, and none of its snippet paths point at anything
any more — the install removes, naming the removal in its report. The
install also writes the devpro block into the project's `AGENTS.md`, created with it where absent —
unless `~/.claude/CLAUDE.md` or `~/.config/opencode/AGENTS.md` already holds an agents-file block,
which the install keeps current there instead and writes no project agents file. Where the
project's `AGENTS.md` takes the block, claude also gets the project's `CLAUDE.md` as the one-line
`@AGENTS.md` redirect, created when absent.

Under claude, a hand-written `CLAUDE.md` refuses the install with exit 2 and nothing written: moving its content
into `AGENTS.md` is yours to do.

### Mage

Install devpro, then run its install into Mage's skills directory:

```sh
mkdir -p ~/Mage/Skills
devpro install ~/Mage/Skills --harness=mage
```

This writes `~/Mage/Skills/devpro/` and that plugin's `CLAUDE.md`, holding the agents file. It
reaches no project: a mage session works with the skills where Mage opens it. To run the process in
a project, install into that project as above, under claude or opencode. The kbase component is
optional: `--components=kbase` adds the `kbase` skill and the `.mcp.json` entry Mage starts the
`kbase` executable from. No devpro install provides, runs or checks that executable: on macOS and
Linux, install it with `brew install benn-herrera/tap/kbase` (0.11.1 or later); native Windows is
unsupported for the component. Restart Mage after installing or upgrading kbase, so it starts the
server.

## Next: ask your agent

Start your coding harness, or, if a session was already open during the install, reload it: run
`/reload-plugins` or restart under Claude Code, restart under opencode, and, after installing with
the kbase component on, restart Mage. Then ask the session agent to load the `guide` skill:
`devpro:guide` under claude and mage, `devpro-guide` under opencode. It starts a design, explains how
the development process runs, tells you where your work stands, and shows the board. It also
installs, updates, inspects or changes what you just installed. To see what the session did — its
profile, trace or call tree — ask for the `show-profile` skill: `devpro:show-profile` under claude and
mage, `devpro-show-profile` under opencode.

Where the guide's setup step covers a project with nothing yet, it creates that project's documents
in the directory the session runs in. A mage install reaches no project, so after one, install into
the project the work runs in as the claude and opencode section above shows, and ask for the guide
in a session started there.

## Updating

To update, run `brew upgrade devpro`, then the same install line with `--dry-run` added to preview
it, then without to apply it.

Installed with pipx, update with `pipx install --force` of the next release's tagged URL, then `pipx
ensurepath` and a new shell, then the same install line.

A project installed by 0.17.x upgrades in two runs. The first removes `skills/docdicer/tools/`'s own
files — the dicer, its runner snippets — along with the `docdicer` skill's earlier files, and
removes the docdicer include line from the project's runner file, naming it in the report; the
include line it writes for the new dicing snippets package lands in the same runner file. Then the
tree is exhausted: a second install reports nothing and leaves the same files where it left them.

A line already in your `justfile` or `Makefile` that names this install's snippets is rewritten in
place, not appended beside: the install rewrites only the snippets path that line names, keeping the
rest of it, an assignment's left-hand side and a trailing comment among them, and every line ending
in the file.

What survives both runs is the launcher's `.venv` under `skills/docdicer/tools/`, with everything in
it, and the directory `skills/docdicer/tools/` holding it. Nothing uses what is there: no
definition, no include line, and no install writes into it, the prune keeping a `VENV_DIR` entry by
rule. Delete `skills/docdicer/tools/` once, and the upgrade is complete.

A project that recorded sessions before this release keeps them: the profiler's stores were named
`claude-profiler/` and `opencode-profiler/` under `.devpro-temp/`, and the install renames each to
its `.profiler-claude/` or `.profiler-opencode/` in place, printing `renamed <old> → <new>`. An old
store stands only where the new name already holds a store too, and the install names it instead of
moving it: the two are never merged, and merging or deleting the old one is yours. `devpro profiler
doctor` names such a store with the move to make.

Under Mage, an install from before the kbase component wrote a second plugin directory,
`~/Mage/Skills/kbase/`, holding its own duplicate skills, agents file and `.mcp.json`. No install
writes there or removes it, and Mage loads it beside `~/Mage/Skills/devpro/` — two sets of skills
and agents, and, with the kbase component on, a `kbase` MCP server from each `.mcp.json` — until
you remove `~/Mage/Skills/kbase/` once, before or after the install, which stops the second load.

## Third Party Acknowledgments

Credit to Jason Coleman (https://github.com/sangrail) for the kanban-from-markdown idea

Credit to Aleksandr Furmanov for his [harness-profiler](https://github.com/afurmanov/harness-profiler) Claude Code plugin, whose source was adapted for our own activity profiler.

- **pytest** (the pytest developers, MIT): Python test runner
- **black** (Łukasz Langa and contributors, MIT): Python formatter
- **isort** (Timothy Crosley and contributors, MIT): Python import sorter
- **flake8** (Tarek Ziadé and contributors, Python Code Quality Authority, MIT): Python linter
- **docdicer** (Benn Herrera, MIT): the source the dicer, the checks and the kanban board were ported
  from; they are devpro's own code under `devpro/dicing`, and the package itself is no longer installed
- **kbase** (Benn Herrera, MIT): the knowledge-base program and MCP server the kbase component drives
