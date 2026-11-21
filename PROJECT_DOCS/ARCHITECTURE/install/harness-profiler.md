### Harness profiler

Every claude project install ships the activity profiler as payload, not as a companion plugin
(SPEC.md, Deployed Surfaces, Shipped files). The profiler is devpro's own code, ported from the
harness-profiler plugin by Aleksandr Furmanov (MIT, `github.com/afurmanov/harness-profiler`); the
acknowledgement in README.md credits the source. devpro owns the ported code
and carries no version stamp on it.

**Resources.** Three files live in `devpro/harnesses/resources/claude/profiler/`: `hp.sh`, the
POSIX-sh launcher that finds `python3` (`HP_PYTHON` overrides the search); `hp.py`, the whole tool —
`capture`, `tree`, `init`, `doctor`, `serve` — one file, Python 3 standard library only, no
dependency; and
`view.html`, the self-contained page template that loads nothing from the network. Each carries the
`!INSTALLED! … devpro` banner within its first ten lines — the banner rule binds every harness
resource. `harness_resource_copies` lands each at the path it holds below the install directory, so
the install directory gains `profiler/`.

**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `sh "${CLAUDE_PLUGIN_ROOT}/profiler/hp.sh" capture claude`. The wiring is data in the harness
module, not a new mechanism, and no entry is gated on the install-time probe. A capture appends one line to the project's `.devpro-temp/claude-profiler/<session-id>.jsonl` — one of the per-harness stores under `.devpro-temp/`, every `*-profiler` directory of which `hp.py`'s `tree` renders — the project's scratch
directory, which the project's own convention gitignores; a capture that fails, or finds no
`python3`, exits 0 with no output.

**Serving.** The `serve` subcommand renders in memory behind a local HTTP server: `hp serve` binds
`127.0.0.1` on a free port — `--port` pins one — and prints the served URL on stdout for
cmd-clicking. The bind is the rule, not a detail: the server listens on loopback only and loads
nothing from the network, so the records it renders never leave the machine. Its main page is the
index of record files: every store the `*-profiler` glob finds,
one row per session — harness, session id, record count, first and last moments — each linking to
`/page/<session-id>`, which renders that session's page in memory, the bytes `tree --format html`
produces. No file is written. A store the glob finds but cannot read appears in the index as
unreadable — the server raises nothing for it. The page shows a session's calls: a session of
nothing but tool calls renders those calls as its calls content, never an empty tree under a calls
header. The server runs until interrupted.

**The skill.** `show-profile` ships as a rendered skill definition under `devpro/definitions/skills/`,
so it carries the generated banner and the harness's namespace (`devpro:show-profile` under claude)
and renders under every harness. Its finder's first candidate, `../../profiler/hp.sh` from the
skill's directory, resolves to `<install-dir>/profiler/hp.sh` where the payload landed; its second,
the committed `.claude/harness-profiler/hp.sh`, covers a repository where the hook was committed for
claude-on-web; where neither stands, the skill says the tool is not installed. A user-level install
renders the skill and copies no resource, so there it is the committed copy or the absence.

**Limits, stated.** The `doctor` subcommand greps the name `harness-profiler` in claude's
installed-plugin records and will not recognize the payload copy; its committed-hook and
settings-hook checks still find a committed one. The limitation is stated, not fixed. Claude Code on
the web sends the same hook data but loads no plugin's hooks, so a cloud session records nothing
until the hook is committed to the repository; the `init` subcommand does that, copying
launcher, script, page and skill into the repository's `.claude/` and merging the six entries into
its `.claude/settings.json`.

**What does not exist.** No companion-plugin mechanism is built: the profiler has no namespace of its
own and no carrier but the devpro plugin. Should it become optional later, it becomes a
`--components` value.

**The opencode capture.** Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call (the `tool`,
`sessionID`, `status`, `input` and `result`/`error` the after-hook reports), and the idle hook appends
a lifecycle record the tree does not draw — writing them to its own
`.devpro-temp/opencode-profiler/<session-id>.jsonl` store, `harness` `"opencode"`, which `hp.py`'s
tree and page render beside the claude sessions', each record read from its own `*-profiler` store.
The model's own `todowrite` notes are not recorded: they are not activity, so the store holds one
record per tool call that did something. A capture that fails raises nothing out of the hook. `init`
and `doctor` stay claude-facing: opencode has no committed-hook concept, and the install ships the
render payload at `<install-dir>/profiler/`, where the show-profile skill's first finder candidate
resolves it. One line holds one record, and the limits that keep it so are `hp.py`'s: `NAME_LIMIT`,
`ARGS_LIMIT` and `RESULT_LIMIT` clip a field's text as `hp.py` clips it, and `LINE_LIMIT` bounds the
written line in bytes, `name` and `session` clipped at the root before `result` and `args` give way.
A line a killed process left torn would fuse the next record onto it, so an append finds the last
newline in the file's tail and truncates to it, renaming the whole store aside where the file holds
no newline at all. `hp.py`'s capture has no such repair: it appends as it stands, and its reader skips
the torn line. An opencode record carries no token counts, so the tree's token columns are blank for
its sessions; claude's counts come from its own transcripts under `~/.claude/projects/`, which is
claude's data, not a source the install configures. An opencode record's `branch` is empty on its own
account: the capture runs in the host's process, and the hooks report no branch, so `tree --branch`
selects no opencode session.
