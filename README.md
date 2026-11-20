# devpro

AI is a tremendous lever for engineering capability, but unsupervised agents write code that rots quietly
and fails suddenly. devpro installs a collaborative AI development process into Claude Code, opencode, or
Mage that lets you build to last: you work with the agents to design, plan, build, review, and deliver.

![kanban screenshot](images/kanban.webp)

*Work packages on the board `docdicer kanban` serves*

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
- `just` 1.33.0 or later, where the project's runner is a justfile: the include line the install writes is an `import?`, which earlier `just` rejects, and no install checks your version.
- `perl` with core `JSON::PP` for the claude guardrail: without them the install skips the hook, says so in one line, and installs everything else.
- An activity profiler for Claude Code: each tool call of a session is recorded to `.devpro-temp/harness-profile/` at the project root, and the `show-profile` skill renders the trace as a page.

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
```

Author identity: <https://keyoxide.org/wkd/benn@bennherrera.dev>

### Claude Code and opencode

Install devpro, then run its install from the project root:

```sh
devpro install .
```

The install command takes the harness from the `.claude/` or `.opencode/` directory inside the target.
Where the project holds neither, or holds both, it refuses and writes nothing; `--harness=claude`
or `--harness=opencode` on the install line settles either case.

Add the installed tree, the agent scratch space and the agents file's backup to the project's
`.gitignore`:

```text
.claude/
# agent scratch space
.devpro-temp/
# the agents file's rolling backup
backup.AGENTS.md
```

For opencode, use `.opencode/` in place of `.claude/`.

The install also adds include lines to the project's `justfile` or `Makefile` (a project with
neither gets a new `Makefile`) for the runner files it installs, and settles the project's agents
file in one of three ways:

- `AGENTS.md`, holding the devpro block;
- under claude, `AGENTS.md` and the one-line `CLAUDE.md` redirect to it;
- nothing, where the global agents file already holds the block.

Under claude, a hand-written `CLAUDE.md` refuses the install with exit 2 and nothing written: moving its content
into `AGENTS.md` is yours to do.

### Mage

Install devpro, then run its install into Mage's skills directory:

```sh
mkdir -p ~/Mage/Skills
devpro install ~/Mage/Skills --harness=mage
```

This writes `~/Mage/Skills/devpro/`. The kbase component is optional: `--components=kbase` adds the
`kbase` skill and the `.mcp.json` entry Mage starts the `kbase` executable from. No devpro install
provides, runs or checks that executable: on macOS and Linux, install it with
`brew install benn-herrera/tap/kbase` (0.11.1 or later); native Windows is unsupported for the
component. Restart Mage after an install with the component on, or after installing or upgrading
kbase, so it starts the server.

## Next: ask your agent

Start your coding harness, or, if a session was already open during the install, reload it: run
`/reload-plugins` or restart under Claude Code, restart under opencode, and, after installing with
the kbase component on, restart Mage. Then ask the session agent to load the `guide` skill:
`devpro:guide` under claude and mage, `devpro-guide` under opencode. It starts a design, explains how
the development process runs, tells you where your work stands, and shows the board. It also
installs, updates, inspects or changes what you just installed.

## Updating

To update, run `brew upgrade devpro`, then the same install line with `--dry-run` added to preview
it, then without to apply it.

Under Mage, an install from before the kbase component wrote a second plugin directory,
`~/Mage/Skills/kbase/`, holding its own duplicate skills, agents file and `.mcp.json`. The current
install writes only `~/Mage/Skills/devpro/` and leaves that directory alone, so remove
`~/Mage/Skills/kbase/` once, before or after the install: Mage otherwise loads two sets of skills,
agents and `kbase` MCP servers side by side.

Installed with pipx, update with `pipx install --force` of the next release's tagged URL, then the
same install line.

## Third Party Acknowledgments

Credit to Jason Coleman (https://github.com/sangrail) for the kanban-from-markdown idea

Credit to Aleksandr Furmanov for his [harness-profiler](https://github.com/afurmanov/harness-profiler) Claude Code plugin, whose source was adapted for our own activity profiler.

- **pytest** (the pytest developers, MIT): Python test runner
- **black** (Łukasz Langa and contributors, MIT): Python formatter
- **isort** (Timothy Crosley and contributors, MIT): Python import sorter
- **flake8** (Tarek Ziadé and contributors, Python Code Quality Authority, MIT): Python linter
- **docdicer** (Benn Herrera, MIT): context-saving reformatter and kanban server
- **kbase** (Benn Herrera, MIT): the knowledge-base program and MCP server the kbase component drives
