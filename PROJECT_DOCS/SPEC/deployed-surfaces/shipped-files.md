### Shipped files

A **shipped package** is plain code, never rendered and so never carrying a generated banner,
installed at its **package destination**, a fixed directory under the install directory. Its
installed copy is stamped where Installed tree says: the installed banner, not the generated
banner. A package ships with the definition it belongs to, and only where that definition ships
(Plugins). Every install delivers the **development scripts package**, `skills/development/scripts/`,
inside the `development` skill's own directory (below), and the **dicing snippets package**
(below), under mage as under claude and opencode. An
install with the kbase component also delivers the kb-tools package (below). A user-level install
delivers none (SPEC.md,
Deployed Surfaces, Install destination). No dicing code ships in a package: the dicing, check and
board verbs run as verbs of the `devpro` command (Package and Command, Dicing and Checks); the
dicing snippets package holds only their runner shortcuts.

A `.venv` directly under a package destination is not install output.

The development scripts package holds one file, `cold-read.sh`, a `bash` script, executable,
carrying the installed banner below its shebang. A **cold read** is one agent reading one brief
with no tools and none of the project's instruction files in context. The script is run as
`scripts/cold-read.sh <agent> <brief-file> [<output-file>]` from the skill's directory:
- The reply is written to the output file, by default beside the brief, named
  `<brief name without .md>-<agent, ":" as "-">.md`, and the script prints that path. Exit status 2
  is a usage error; 1 is a refusal or a failed harness run, which leaves no output file.
- The reader runs with no tools and loads none of the project's instruction files, while the
  operator's global agents file, under claude `~/.claude/CLAUDE.md`, still loads. It works in a
  fresh directory that is empty under claude and, under opencode, holds only the named agent's
  file with every tool denied, composed from that agent's record in the plugin's registry and its
  body file; the session is not added to the operator's history.
- That directory is a mode 0700 child of the directory the environment variable
  `DEVPRO_COLD_READ_DIR` names, and is removed when the script exits, on failure and on
  interruption included. The script refuses, naming the cause and creating nothing, where the
  variable is not set, does not name an existing directory, names a directory inside the project
  root, or names one with an instruction file (`CLAUDE.md`, `AGENTS.md` or another the harnesses
  load) at or above it, other than in the operator's own `~/.claude/`; it names that file.
- An agent the installed set does not hold fails the run with no output; under claude the script
  says the agent did not load and passes on the available agents claude named.
- Where the environment variable `DEVPRO_COLD_READ_MODEL` is set and not empty, the reader runs on
  that model (under claude a model name or alias, under opencode `provider/model`); otherwise on the
  model the harness gives the agent — under the unpinned defaults, the model the session runs.
  A model the harness rejects fails the run with no output.
- Under opencode a brief whose first character is `-` is refused.
- It refuses where the calling session is the other harness's, naming both and saying to run the
  calling harness's own copy of the skill, and where it sits under no harness directory named
  `.claude` or `.opencode`, so under mage and in this repository's source tree. It runs under claude
  and opencode only.

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

A **harness resource** is a file a harness ships, such as a guardrail script, opencode's plugin
entry or the plan-state reminder script, copied as it stands and never rendered. A harness also writes harness-rendered files into the
install directory — the plugin manifest `.claude-plugin/plugin.json`, one value shared by claude and
mage, version included, `.mcp.json` under claude and mage where `kbase` ships, rendered whole
with the `kbase` server alone, `registry.json` under opencode, and under claude the guardrail
registration `hooks/hooks.json` (below) — which are rendered, not copied, carry no banner, and are
replaced whole. `registry.json` is opencode's **registry**: the plugin's name and version and one record
per agent, command and skill — id, body file, description, and for an agent its mode, model, color
and permissions — and the `kbase` MCP server where `kbase` ships. An install copies the harness
resources into the install directory, except a user-level install, which copies only opencode's
entry, and save a file conditional on the install-time probe (below), so a resource lands at the
path it holds below the install directory: opencode's at `<install-dir>/index.ts`, the plugin entry,
`<install-dir>/guardrail.ts` and `<install-dir>/profiler.ts`, and, for claude and opencode alike,
`<install-dir>/profiler/hp.sh`;
claude's at `<install-dir>/hooks/guardrail.pl` and
`<install-dir>/hooks/state-table-reminder.sh` (mage ships none):
in the install directory, outside its three deployed surfaces. Each keeps its bytes and its mode:
the install stamps nothing on them. Every such file carries an installed banner
(`!INSTALLED! … devpro`) in its first ten lines — the guardrails' name this repository and forbid
edits. A harness shipping none copies nothing, which is not an error.

A claude project install also ships the **activity profiler**: its code is devpro's own, and the
hook files refer back to devpro wherever they ran the profiler's script, with the capture hook's
contract — a failed or interpreterless capture exits 0 with no output — unchanged. The page
template `view.html` the render reads is the devpro wheel's package data
(`devpro/profiler/view.html`, read by the rendering module), not an install resource; and the
`show-profile` skill, which renders a session's recorded activity — its skill, agent and tool calls
with timings and token costs — as text, as a self-contained HTML page, or served over HTTP: the
dashboard, devpro's one loopback server for the web interface, renders the record files in memory
as one panel of its site. The board is the landing surface: opening the dashboard's URL shows the
kanban board — the project's actual current state — and the traces are the second view, reached
from the nav. A simple top nav persists across every view: the `devpro` brand, then the view names
`kanban` and `profiler`, selection switching the view — intuitive, recognizable surfaces, no
invented paradigms, the dynamic behavior spent only where it counts. The nav and the views carry
the phosphor pairing, the brand's callback to amber and green screen terminals inverted from the
nav's scanlines deliberate — and the accent is the phosphor, no second brand
color. The dark mode carries the phosphor green: brand `#3cf077`, the active view `#31c260`, 80%
of the brand's brightness, the inactive view `#a6a6ad`. The light mode carries the warm phosphor:
brand `#e8a020`, the active view `#d09020`, the inactive view `#63636b`. The surfaces are the
board's own variable system — `board.css`'s `:root` and its `prefers-color-scheme` block — the
site's surfaces not inherited; the site's accent values and its two-motif accent map are. The
nav's grammar: the brand wordmark is monospace, heavier and about 15% larger than the nav items,
in the motif's brand color at full brightness; both view names sit in the same smaller size, no
underline, no visited-link styling; the active view is the brand color at 80% brightness and
heavier weight, the inactive view a lifted gray that reads available, never deactivated. The
site's own light-mode mapping (green) and its dim value are superseded: the
dashboard's light brand is the bright amber, dimmed only for the active view's smaller text.
`board.css`'s `:root` carries the nav grammar's values — the phosphor brand, the accent at 80% of
it, and the view's lifted gray — and no value of the superseded map: `--accent-dim`, the dim the
active view's text once used, is gone rather than left standing unused.
Retro colors, modern chrome: the phosphor accents and the scanline treatment are the whole retro
voice — the layout, spacing and componentry are ordinary modern web, no TUI replication — and the
scanline treatment may appear in the chrome, the nav or the frame band, never on a card surface,
its placement the pass's executor call. The server's elements persist across every view, the nav's
server block right-justified at its flex edge: a live/idle state indicator and, when live, a stop
control; starting is the CLI's alone, no served page starting its own server. In the profiler view the how-to-read legend sits at the top of the
view's frame band and persists there across drill-down, the same band carrying a return-to-list
control, its label `Return to list`, revisable at execution as a one-string change — the pass's
second executor call; drill-down is ordinary page navigation, the trace list to the session page
with
`/page/<session-id>` deep links intact and no inner-frame mechanic. One presentation layer serves
the whole presented interface: a single CSS source the board's assets and the profiler's pages
alike consume, the palette living there, the profiler page's re-style to the kanban presentation
made through that shared layer, never as a second reskin. The legend's text has one home and two
carriers, one source both read: the rendering side holds it once — the standalone render injects
it into the page it renders, the template carrying no second copy — and the dashboard's frame band
reads the same source, so the served page's legend comes from the frame. The pages and the records
stay local: reachable only from the
machine that runs the server. Six hook entries, one per
event (`PostToolUse`, `PostToolUseFailure`, `PreCompact`, `PostCompact`, `SessionStart`,
`SubagentStop`), are written into `hooks/hooks.json` on every claude project install; each appends
one line to the project's `.devpro-temp/.profiler-claude/<session-id>.jsonl`, and a capture that
fails, or finds no `devpro` to run under, exits 0 with no output. A claude session on the web loads
no plugin's hooks and records nothing there; the skill names the tool's `init` for committing the
hook where a session needs one. A user-level install renders the skill and copies none of the
resources. A project opencode install also ships the profiler's launcher — `profiler/hp.sh` — and
the capture `profiler.ts` beside the plugin entry, and
registers no hook entries; each recorded call appends one line to the project's
`.devpro-temp/.profiler-opencode/<session-id>.jsonl`, a capture that fails raises nothing out of the
hook, and a mage install ships none of them. A page attributes a child session to the session that
dispatched it: the capture extracts the child's session id into the parent call's record, the render
groups children under their dispatching session, links each Agent row to the child's page and heads
a child page with its dispatcher, and the stores stay flat — the child never knows its parent at
write time, the hierarchy being metadata the parent side builds, and claude holding no child
session records at all. The index's rows alternate their tone — a zebra the eye reads across the
columns — and each row's harness carries its own mark, a dot in the harness's brand colors:
opencode's blue, claude's coral.

A claude project install also carries the plan-state reminder in that registration: one ungated
`PostToolUse` entry matched on `Agent`, running `<install-dir>/hooks/state-table-reminder.sh`, which
reads the same gate at the project root and injects the same sentence as opencode's — `Reminder: keep
the ACTIVE_PLAN state table up to date.` That entry is written on every claude project install,
whatever the probe decides about the guardrail's, so its script runs on every project claude
install. A user-level claude install writes no registration, so the reminder never registers there.

Opencode loads the plugin directory and registers its agents, skills, commands and, where
`kbase` ships, the `kbase` MCP server under the registry's ids, and injects a plan-state reminder
into the parent session at agent dispatch and agent completion, gated by `ACTIVE_PLAN.md` — file
or, where the plan was diced, the `ACTIVE_PLAN/` tree — existing at the project root. A change to
the install directory is picked up without restarting opencode, except a change to `guardrail.ts` or
`profiler.ts`, either of which the plugin entry imports when it loads, so a changed one takes effect
at the next opencode start. The plugin entry is written for opencode 2.3.2 (floor 2.3.0) and is the
same file for both plugins; ARCHITECTURE.md, Install, Opencode entry holds how it works. A resource
may be conditional
on the probe: claude's guardrail is
delivered only when one run of the script on the installing machine succeeds within a few seconds,
and is otherwise skipped, with the reason reported and the rest of the install unaffected. The
guardrail catches common mistakes; it is not a security boundary, and does not contain an agent
that sets out to evade it. Both guardrails are to block the same calls but one spelling, which only
the claude guardrail reads: a path word of a shell command that, its surrounding quote stripped,
opens with `$CLAUDE_PROJECT_DIR` or `${CLAUDE_PROJECT_DIR}` followed by `/` or the word's end is
read as the rest of the word under the project root; where that variable is unset or empty, the word
is read literally. File-tool arguments are read literally, and no other variable is read.

Their mutation check blocks shell commands that change a file behind the edit tools, such as
in-place `sed`, `perl` or `ruby` edits, shell redirections, `tee`, `cp` or `mv` onto an existing
file, and inline scripts that write, and allows a redirect, a `tee` destination or a `cp`/`mv`
target in the scratch directory, `.devpro-temp/` under the project root. A relative
destination is judged lexically against the working directory of the call. A heredoc's body is data:
no check reads it, unless the heredoc feeds a script: a shell's (`bash`, `sh`, `zsh`) body is read
by every check, an interpreter's (`python3 -`, `perl`, `ruby`, `node`) only by the inline-script
write check. Its own command line is read like any other. This check blocks with `Blocked: <reason>` and a pointer to the edit tools.

Their `.index/` check is active only where the install directory holds the kbase skill's skill entry
file, which they look for on every call, so an install without the kbase component is never blocked
by it. It blocks a call
that reaches into `<project>/kb-root/.index/`, whose index records kbase's own tools read and
change:
- a shell command with a word naming a path there, existence checks (`stat`, and `test` or `[` with `-e`, `-d` or `-f`) excepted
- a recursive `grep`, `rg`, `find`, `ls -R` or `tree` rooted in `kb-root/` that does not exclude
  `.index`
- a file-tool call whose path lies there: Claude's Read, Write, Edit and NotebookEdit, opencode's
  read, write, edit and patch
- a Grep or Glob rooted in `kb-root/` whose file filter's last segment does not end in `.md`

A path reaches `kb-root/.index/` when it does so through `..` segments, relative to the call's
working directory (for opencode's file-tool calls, the project root). A Glob reaches it when its
`path` together with its pattern's leading literal segments does. This check blocks with `Blocked:
<reason>` alone, without the mutation check's pointer to the edit tools. Where both checks would
block a shell command, the block reported is this check's.

Claude's guardrail runs at session time and needs perl with core `JSON::PP`; an install also
registers it as a `PreToolUse` entry for Bash and the file tools (Read, Write, Edit, NotebookEdit,
Grep, Glob) in the plugin's own `hooks/hooks.json`, written beside the script and holding the guardrail's
entry only where the install-time probe succeeds; no project settings file is written to register it. The entry runs the
script only where it stands readable: where it is missing, a call reports `guardrail hook: no readable script at <path>`
on stderr and proceeds, and is not blocked. A claude guardrail that fails while running, through a
missing module or an error in the script, reports on stderr and does not block the call.
Opencode's guardrail is run by the plugin entry, which imports `guardrail.ts` from the install
directory: the install writes no settings entry for it. A user-level install copies no
`guardrail.ts`, and the plugin entry then runs none.

