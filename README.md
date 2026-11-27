# devpro

AI is a tremendous lever for engineering capability, but unsupervised agents write code that rots quietly
and fails suddenly. devpro installs a collaborative AI development process into Claude Code, opencode, or
Mage that lets you build to last: you work with the agents to design, plan, build, review, and deliver.

![devpro main dashboard view](images/dashboard.webp)
*Main dashboard*

![devpro harness profiler sessions list](images/profiler-sessions.webp)
*Harness profiler sessions list*

![devpro harness profiler session details](images/profiler-graph.webp)
*Harness profiler session graph*

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

- Platforms: macOS and Linux. Native Windows is unsupported; no install refuses it.
- Harness: claude, opencode, or mage; `--harness` takes these three names.
- Homebrew or pipx to install

## Quick Start Guide

### Installation

```sh
brew tap benn-herrera/tap
brew trust benn-herrera/tap
brew install devpro
```
or
```sh
pipx install "git+https://github.com/benn-herrera/devpro"
pipx ensurepath
```
then open a new shell, so `devpro` is on your `PATH`.

Author identity: <https://keyoxide.org/wkd/benn@bennherrera.dev>

### Claude Code and opencode

Install devpro, then run its install from the project root:

```sh
devpro install .
```

The install reads the harness from the `.claude/` or `.opencode/` directory the target holds; where it
holds neither, or holds both, pass `--harness=claude` or `--harness=opencode`. A devpro settings file
that names harnesses installs for each of them instead, one install apiece.

Add the installed tree and the agents file's backup to the project's `.gitignore`, listing the lines of
the harness you installed: each install replaces the plugin directory whole, so the tree is output,
not source, and keeping it out of git keeps the diff to what you wrote. The install writes the
`.devpro-temp/` line itself, once, to the one directory of that name; leave it to the install, and run
the install again if you write it by hand in another form:

```text
# the install wrote:
.devpro-temp/
# claude
.claude/
# opencode: .opencode/ instead
# the agents file's rolling backup
backup.AGENTS.md
```

A project install under claude or opencode adds the include lines to the project's `justfile` or
`Makefile` — an `import?` or an `-include` — for the runner snippets it installs, and a project
with neither runner file gets a new `Makefile` holding them. One is the devpro tools package's,
`devpro`, written on every project install of a nested plugin; another is the kb-tools package's,
`kb`, written with `--components=kbase`. A line an earlier release wrote for the docdicer tools
package — retired with the absorbed dicing verbs, and none of its snippet paths point at anything
any more — is left where it stands: no install edits a line it did not write, so deleting it is yours.

The install gives the project its own copy of devpro, `tools/devpro/` in the install directory,
and a wrapper, `tools/devpro.sh`, that runs it; the recipes, hooks and session commands run that
copy, not the `devpro` on your `PATH`. So the project's devpro does not change when the global one
does: a `brew upgrade` changes no project's checks. Only an install run from the global devpro
replaces the copy (Updating, below); one run from the project's own copy, as the wrapper runs it,
passes over that copy and the wrapper that runs it — writing everything else — so the copy is the
one its last global install wrote. The wrapper's interpreter lookup and what the copy holds are in
[SPEC Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md).

Each install replaces the plugin directory whole before it writes: renders, hand-written files and
scratch copies alike go, and nothing in it is yours to keep. `devpro install . --dry-run` writes
nothing and lists what the install would create, change and remove — a hand-written file or a safety
copy inside the directory among the removals — so a file you mean to keep lives outside it. The
`.devpro-temp/` stores beside the project, the agents file's backup and your runner file's include
lines all sit outside it.

The install also writes the devpro block into the project's `AGENTS.md`, created with it where absent —
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
`kbase` executable from. No devpro install writes, copies, verifies or locates that executable:
install it with `brew install benn-herrera/tap/kbase` (0.11.1 or later, on macOS or Linux; a native
Windows install has none). kbase needs more than the executable: pandoc 3.12, git and a way to reach
a model are kbase's own requirements, which the operator meets (SPEC.md, Deployed Surfaces,
Plugins). Restart Mage after installing or upgrading kbase, so it starts the server.

## Next: ask your agent

Start your coding harness, or, if a session was already open during the install, reload it: run
`/reload-plugins` or restart under Claude Code, restart under opencode, and, after installing with
the kbase component on, restart Mage. Then ask the session agent to load the `guide` skill:
`devpro:guide` under claude and mage, `devpro-guide` under opencode. It starts a design, explains how
the development process runs, tells you where your work stands, and shows the board — it runs
`devpro dashboard`, or gives you that command line where you would rather run it yourself. It also
installs, updates, inspects or changes what you just installed. To see what the session did — its
profile, trace or call tree — ask for the `profiler` skill: `devpro:profiler` under claude and
mage, `devpro-profiler` under opencode.

Where the guide's setup step covers a project with nothing yet, it creates that project's documents
in the directory the session runs in. A mage install reaches no project, so after one, install into
the project the work runs in as the claude and opencode section above shows, and ask for the guide
in a session started there.

## The dashboard

`devpro dashboard [<project-dir>] [--port <number>]` serves the project in a browser on the local
machine and prints the URL it is served at:

```sh
devpro dashboard
```

It serves the project the command runs in, up to the nearest directory holding a `.git` entry;
`<project-dir>` names another directory inside the project to serve from anywhere. The port is
loopback only, `127.0.0.1`, and the system picks a free one unless `--port` names one. The URL opens
on the board — its root answers a redirect to `/board/` — and the profiler view is the second view,
at `/profiler/`. Its index lists the session records the activity profiler captured, one row per
session, each linking to that session's page; the index shows or hides the sessions a session
dispatched and either harness's records, and sorts on the agent count, record count, last moment or
span. A session that dispatched agents which ran without dispatching the post-plan review first is
marked unreviewed, on its dispatcher's row and beside the dispatch on the session's page. Recorded
moments and spans show in your own local time, never UTC, and the pages open only from the machine
that runs the server — the URL is not one to share. A top nav switches between the two:
its `kanban` link is the board panel at `/board/`, its `profiler` link the profiler view at
`/profiler/`, and at the nav's right edge sit the server's live/idle indicator and its stop.

The board is the project's roadmap, its active design and its active plan as a set of columns of
cards, live: an edit to a watched file shows on the open page within about a second. Dropping a
card moves its ticket between `ROADMAP.md` and the active design. Those moves are the board's only
writes; the plan's columns are read-only. The stop in the nav ends the server, as Ctrl-C does, from
either view. Only the command line starts it: no served page starts its own server.

## The activity profiler

A claude or opencode project install ships an activity profiler. It records the session's activity
to the project's own store under `.devpro-temp/` at the project root: `.profiler-claude/` under
claude, one line per hook event, and `.profiler-opencode/` under opencode, one per record — a tool
call, or an idle marker where the session's work settles. `devpro profiler tree` reads the stores
named exactly `.profiler-claude/` and `.profiler-opencode/`, whichever the project holds; a
directory under `.devpro-temp/` by any other name is not a store and is not read. The `profiler`
skill hands a session to you as text or as an HTML page, and `devpro dashboard` serves the records as
its profiler view (The dashboard, above). What the install copies and registers for it is in
[SPEC Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md).

Under mage, `profiler` ships with no launcher and no capture, so a mage session records nothing. A
claude session on the web loads no plugin's hooks and records nothing there until `init` commits the
hook; the skill names that `init`.

## Updating

To update, run `brew upgrade devpro`, then the same install line with `--dry-run` added to preview
it, then without to apply it. The upgrade alone reaches no project: each project keeps the copy of
devpro its last install wrote, and only an install run from the global devpro replaces it. An
install run from the project's own wrapper, `tools/devpro.sh install .`, writes everything an
install writes except that copy and the wrapper that runs it: it passes both over, reporting
nothing about them, so the project keeps the version its global install delivered.

Installed with pipx, update with `pipx install --force` of the next release's tagged URL, then `pipx
ensurepath` and a new shell, then the same install line.

A project installed by 0.17.x upgrades in one run: an install replaces the plugin directory whole,
so the dicing snippets package's retired home, `skills/docdicer/dicing-snippets/`, and the `docdicer`
skill's earlier files go with the tree, and the include line it writes for the devpro tools package
lands in your runner file. The docdicer include line in that runner file stays until you delete it:
no install edits a line it did not write.

A line already in your `justfile` or `Makefile` that names this install's snippets is rewritten in
place, not appended beside: the install rewrites only the snippets path that line names, keeping the
rest of it, an assignment's left-hand side and a trailing comment among them, and every line ending
in the file.

A project that recorded sessions before this release keeps them: the profiler's stores were named
`claude-profiler/` and `opencode-profiler/` under `.devpro-temp/`, and the install renames each such
store it finds to its `.profiler-claude/` or `.profiler-opencode/` in place, printing
`renamed <old> → <new>`. An old
store stands only where the new name already holds a store too, and the install names it instead of
moving it: the two are never merged, and merging or deleting the old one is yours.

Under Mage, an install from before the kbase component wrote a second plugin directory,
`~/Mage/Skills/kbase/`, holding its own duplicate skills, agents file and `.mcp.json`. No install
writes there or removes it, and Mage loads it beside `~/Mage/Skills/devpro/` — two sets of skills
and agents, and, with the kbase component on, a `kbase` MCP server from each `.mcp.json` — until
you remove `~/Mage/Skills/kbase/` once, before or after the install, which stops the second load.

## Acknowledgments

Credit to [Jason Coleman](https://github.com/sangrail) for the kanban-from-markdown idea

Credit to Aleksandr Furmanov for his [harness-profiler](https://github.com/afurmanov/harness-profiler)
Claude Code plugin, whose source was adapted for our own activity profiler.

- [pytest](https://github.com/pytest-dev/pytest) (the pytest developers, MIT): Python test runner
- [black](https://github.com/psf/black) (Łukasz Langa and contributors, MIT): Python formatter
- [isort](https://github.com/pycqa/isort) (Timothy Crosley and contributors, MIT): Python import sorter
- [flake8](https://github.com/PyCQA/flake8-import-order) (Tarek Ziadé and contributors, Python Code Quality Authority, MIT): Python linter
- [kbase](https://github.com/benn-herrera/kbase) (Benn Herrera, MIT): the knowledge-base program and MCP server the kbase component drives
