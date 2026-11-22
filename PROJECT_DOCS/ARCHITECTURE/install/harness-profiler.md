### Harness profiler

Every claude project install ships the activity profiler as payload, not as a companion plugin
(SPEC.md, Deployed Surfaces, Shipped files). The profiler is devpro's own code, ported from the
harness-profiler plugin by Aleksandr Furmanov (MIT, `github.com/afurmanov/harness-profiler`); the
acknowledgement in README.md credits the source. devpro owns the ported code
and carries no version stamp on it.

**The code is devpro's.** The port is a devpro package, `devpro/profiler/`, standard library only,
no dependency: `values.py` the schema, limits, masks and store facts every other module reads,
`capture.py` the hook payload's parsing, masking and record serialization, `pages.py` the tree, page
and HTTP render, `hooks.py` the committed hook's wiring — `init` and `doctor` — and `cli.py` the
`profiler` verb's dispatch. The verb is dispatched lazily: registering it imports none of these
modules, and `cli.py` imports the one whose subcommand runs. Its subcommands are `capture`, `tree`,
`init` and `doctor`, which read exactly as they did inside `hp.py`; the records are served by the
`dashboard` verb, below.

**Resources.** One file lives in `devpro/harnesses/resources/claude/profiler/`:
`hp.sh`, the POSIX-sh launcher, which finds the `devpro` command and runs its `profiler` verb
(`HP_DEVPRO` overrides the search). It carries the `!INSTALLED! … devpro` banner within its first ten
lines — the banner rule binds every harness resource — and `harness_resource_copies` lands it at the
path it holds below the install directory, so the install directory gains `profiler/hp.sh`. The
launcher is this harness's alone: mage ships no resources, and opencode's capture is the plugin's own
TypeScript, below.

**The launcher's finder.** `command -v devpro`, then `/opt/homebrew/bin/devpro`,
`/usr/local/bin/devpro` and `~/.local/bin/devpro`, since a hook may run with a `PATH` where only the
shell's builtins are found; `HP_DEVPRO`, where set, replaces the search rather than leading it. A
candidate is the devpro when `"$candidate" --version` runs and exits 0 — the found command is the one
`profiler` runs — and the terminal line is `exec "$devpro" profiler "$@"`, the subcommand parsed
where the verb is dispatched and the launcher's own arguments passed through unchanged.

**The page template.** `view.html` is the wheel's package data, `devpro/profiler/view.html`, read by
`pages.py` through `importlib.resources` beside the module that renders it: it is a self-contained
page that loads nothing from the network, it ships in the wheel, and it is no install resource and no
committed hook file.

**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `sh "${CLAUDE_PLUGIN_ROOT}/profiler/hp.sh" capture claude`, and the hook name changes with no
other: `hp.sh` kept its name, so a committed hook written under it stays this tool's own. The wiring
is data in the harness module, not a new mechanism, and no entry is gated on the install-time probe. A
capture appends one line to the project's `.devpro-temp/.profiler-claude/<session-id>.jsonl` — one of
the per-harness stores under `.devpro-temp/`, every `.profiler-*` directory of which the `tree`
subcommand renders — the project's scratch directory, which the project's own convention gitignores; a
capture that fails, or finds no `devpro`, exits 0 with no output.

**Serving.** The dashboard renders in memory behind a local HTTP server: the `devpro dashboard
[<project-dir>] [--port <number>]` verb binds `127.0.0.1` on a free port — `--port` pins one — and
prints the served URL on stdout for cmd-clicking. The bind is the rule, not a detail: the server
listens on loopback only and loads
nothing from the network, so the records it renders never leave the machine. Its traces panel is the
index of record files: every store the `.profiler-*` glob finds,
one row per session — harness, session id, record count, first and last moments — each linking to
`/page/<session-id>`, which renders that session's page in memory, the bytes `tree --format html`
produces. No file is written. A store the glob finds but cannot read appears in the index as
unreadable — the server raises nothing for it. The page shows a session's calls: a session of
nothing but tool calls renders those calls as its calls content, never an empty tree under a calls
header. The server runs until interrupted. The dashboard's board panel is the profiler's sibling
panel, serving the project's kanban board (SPEC.md, Dicing and Checks, Kanban).

**The skill.** `show-profile` ships as a rendered skill definition under `devpro/definitions/`, so it
carries the generated banner and the harness's namespace (`devpro:show-profile` under claude) and
renders under every harness. Its finder's first candidate, `../../profiler/hp.sh` from
the skill's directory, resolves to `<install-dir>/profiler/hp.sh` where the payload landed — the
launcher that then finds `devpro` — and its second, the committed `.claude/harness-profiler/hp.sh`,
covers a repository where the hook was committed for claude-on-web; where neither stands, the skill
says the tool is not installed. A user-level install renders the skill and copies no resource, so
there it is the committed copy or the absence. `init` renders the same skill into the repository's
`.claude/skills/show-profile/SKILL.md` from the definition, beside the launcher it copies.

**Limits, stated.** The `doctor` subcommand greps the name `harness-profiler` in claude's
installed-plugin records and will not recognize the payload copy; its committed-hook and
settings-hook checks still find a committed one. The limitation is stated, not fixed. Claude Code on
the web sends the same hook data but loads no plugin's hooks, so a cloud session records nothing
until the hook is committed to the repository; the `init` subcommand does that, copying the launcher
and the skill into the repository's `.claude/` and merging the six entries into its
`.claude/settings.json`.

**What `init` copies, and what it removes.** `init claude` writes the repository's
`.claude/harness-profiler/hp.sh` — the harness resource the devpro package ships, readable as
`devpro.profiler.hooks.launcher_resource()` and marked executable — and the rendered skill, then
unlinks the files an older `init` left beside the launcher: `hp.py` and `view.html`, which no install
ships any more. A hook committed by an older `init` therefore keeps working: it runs `hp.sh`, which
finds `devpro`. `doctor`'s `update` line names a committed hook that lacks an event, is not `async`,
or differs by a byte from the launcher's resource the devpro package ships — that resource is the
master, and the compare reads it without needing an install directory.

**What does not exist.** No companion-plugin mechanism is built: the profiler has no namespace of its
own and no carrier but the devpro plugin. Should it become optional later, it becomes a
`--components` value.

**The opencode capture.** Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call (the `tool`,
`sessionID`, `status`, `input` and `result`/`error` the after-hook reports), and the idle hook appends
a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/.profiler-opencode/<session-id>.jsonl` store, `harness` `"opencode"`, which
`devpro profiler tree` and the dashboard's traces panel render beside the claude sessions', each
record read from its own `.profiler-*` store.
The model's own `todowrite` notes are not recorded: they are not activity, so the store holds one
record per tool call that did something. A capture that fails raises nothing out of the hook. `init`
and `doctor` stay claude-facing: opencode has no committed-hook concept. The install ships the
profiler's launcher under opencode too: `_CROSS_HARNESS_SOURCES` carries claude's
`claude/profiler` directory to opencode's `profiler/`, so an opencode project install holds
`profiler/hp.sh` beside the plugin's `profiler.ts`, and the show-profile skill's first finder
candidate resolves it. The payload is copied, not wired: opencode registers no hook entry, so no
committed copy arises, and the store the plugin writes is read by `devpro profiler tree` run from the
`devpro` command's `PATH`. One line holds one record, and the limits that keep it so are
`devpro/profiler/values.py`'s: `NAME_LIMIT`,
`ARGS_LIMIT` and `RESULT_LIMIT` clip a field's text as the Python capture clips it, and `LINE_LIMIT`
bounds the written line in bytes, `name` and `session` clipped at the root before `result` and `args`
gives way.
A line a killed process left torn would fuse the next record onto it, so an append finds the last
newline in the file's tail and truncates to it, renaming the whole store aside where the file holds
no newline at all. The Python capture has no such repair: it appends as it stands, and its reader
skips the torn line. An opencode record carries no token counts, so the tree's token columns are blank for
its sessions; claude's counts come from its own transcripts under `~/.claude/projects/`, which is
claude's data, not a source the install configures. An opencode record's `branch` is empty on its own
account: the capture runs in the host's process, and the hooks report no branch, so `tree --branch`
selects no opencode session.

**The stores and their rename.** Each harness's capture owns one store under the project's
`.devpro-temp/`: claude's `.profiler-claude/`, opencode's `.profiler-opencode/`, and the `tree`
and page reads walk every `.profiler-*` directory there — a dot name, so the stores group
and sort at the top of the scratch tree. The naming before the rename was `<store>-profiler`, and
both `devpro install` and `devpro profiler init claude` migrate the two stores it named:
`.devpro-temp/claude-profiler/` is renamed to `.profiler-claude` and
`.devpro-temp/opencode-profiler/` to `.profiler-opencode`, and the move is printed. A directory
under `.devpro-temp/` whose name only ends in `-profiler` is no store and is left alone. Where a
store's new name is already taken, the old one is left in place and named instead — the stores'
contents are never merged, and merging or deleting the old store is the operator's call. A second
run touches nothing. The window between the upgrade's first capture and the install that follows it
exists: captures write `.profiler-*` while an old-pattern store still holds its traces, so `tree` cannot
read that store until the migration runs. The skip-and-name case above is where the window does not
close — the old store is left standing and named, and at the migration's end one store name per
harness stands with its traces readable under it, or the operator is told which store was left behind.

**Doctor's lines.** `devpro profiler doctor` reports `devpro:` the executable the launcher's finder
would resolve — or `not found on PATH, in Homebrew or ~/.local/bin (install devpro)` — `traces:` the
claude store `tree` reads beside the `.profiler-*` pattern, `hook:` where a capture hook is
registered here (the plugin's own records, and the committed, local and user settings files) or
`not installed` with the install and `init` remedies, an `old:` line per pre-rename store it cannot
read with the remedy that renames or merges it, `update:` a stale committed hook, and `newest:` the
newest claude session's last moment or `no calls recorded yet`. Doctor is claude-facing: every line
reads claude's hook and claude's store, where `tree` reads both harnesses'.
