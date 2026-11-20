# The activity profiler is devpro's own Python, writing into the project's scratch directory

The claude activity profiler ports from `hp.js` to `hp.py`, ending the install's only foreign
runtime: every devpro install has `python3` by definition, so the `node` requirement and the
launcher's node-version-manager search retire. The port makes the profiler devpro's own code — the
vendoring ends, the original author keeps the acknowledgement for the idea and design, and the
README credit line stands verbatim. The capture's output moves from `.harness-profile/` to
`.devpro-temp/harness-profile/`, the project's scratch directory, whose gitignore convention the
project itself carries; the capture's `.git/info/exclude` write retires with the move. A future
opencode capture, should one come, is recreated in the opencode plugin's TypeScript rather than
reusing this code.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```markdown
A claude project install also ships the **activity profiler** payload: the harness resources
`libexec/hp.sh`, `libexec/hp.js` and `libexec/view.html`, copied as they stand, and the
`show-profile` skill, which renders a session's recorded activity — its skill, agent and tool calls
with timings and token costs — as text or as a self-contained HTML page. Six hook entries, one per
event (`PostToolUse`, `PostToolUseFailure`, `PreCompact`, `PostCompact`, `SessionStart`,
`SubagentStop`), are written into `hooks/hooks.json` on every claude project install; each appends
one line to the project's `.harness-profile/<session-id>.jsonl`, and a capture that fails, or finds
no `node` to run under, exits 0 with no output. A claude session on the web loads no plugin's hooks
and records nothing there; the skill names the tool's `init` for committing the hook where a session
needs one. A user-level install renders the skill and copies none of the resources; no opencode or
mage install ships the resources or the hook entries.
```

**Becomes:**

```markdown
A claude project install also ships the **activity profiler** payload: the harness resources
`libexec/hp.sh`, `libexec/hp.py` and `libexec/view.html`, copied as they stand, and the
`show-profile` skill, which renders a session's recorded activity — its skill, agent and tool calls
with timings and token costs — as text or as a self-contained HTML page. Six hook entries, one per
event (`PostToolUse`, `PostToolUseFailure`, `PreCompact`, `PostCompact`, `SessionStart`,
`SubagentStop`), are written into `hooks/hooks.json` on every claude project install; each appends
one line to the project's `.devpro-temp/harness-profile/<session-id>.jsonl`, and a capture that
fails, or finds no `python3` to run under, exits 0 with no output. A claude session on the web loads
no plugin's hooks and records nothing there; the skill names the tool's `init` for committing the
hook where a session needs one. A user-level install renders the skill and copies none of the
resources; no opencode or mage install ships the resources or the hook entries.
```

## ARCHITECTURE delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```markdown
Every claude project install ships the activity profiler as payload, not as a companion plugin
(SPEC.md, Deployed Surfaces, Shipped files): the source of the harness-profiler plugin by Aleksandr
Furmanov (MIT, `github.com/afurmanov/harness-profiler`), taken over and modified. No version is
stamped on the vendored code and no origin constant names it: the acknowledgement in README.md
credits the source, and that is the whole mechanism.

**Resources.** Three files are vendored into `devpro/harnesses/resources/claude/libexec/`: `hp.sh`,
the POSIX-sh launcher that finds `node` (PATH, `HP_NODE`, `~/.volta`, `~/.nvm`, Homebrew);
`hp.js`, the whole tool — `capture`, `tree`, `init`, `doctor` — one file, Node 18+ standard library
only, no dependency; and `view.html`, the self-contained page template that loads nothing from the
network. Each carries the `!INSTALLED! … devpro` banner within its first ten lines, added at
vendoring — the banner rule binds every harness resource — and the files are otherwise copied as
they stand; the one-way copy rule applies. `harness_resource_copies` lands each at the path it holds
below the install directory, so the install directory gains `libexec/`.

**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `sh "${CLAUDE_PLUGIN_ROOT}/libexec/hp.sh" capture claude`. The wiring is data in the harness
module, not a new mechanism, and no entry is gated on the install-time probe. A capture appends one
line to the project's `.harness-profile/<session-id>.jsonl`, whose directory the first write adds to
`.git/info/exclude`; a capture that fails, or finds no `node`, exits 0 with no output.

**The skill.** `show-profile` ships as a rendered skill definition under `devpro/definitions/skills/`,
so it carries the generated banner and the harness's namespace (`devpro:show-profile` under claude)
and renders under every harness. Its finder's first candidate, `../../libexec/hp.sh` from the
skill's directory, resolves to `<install-dir>/libexec/hp.sh` where the payload landed; its second,
the committed `.claude/harness-profiler/hp.sh`, covers a repository where the hook was committed for
claude-on-web; where neither stands, the skill says the tool is not installed. A user-level install
renders the skill and copies no resource, so there it is the committed copy or the absence.

**Limits, stated.** The vendored `doctor` greps the name `harness-profiler` in claude's
installed-plugin records and will not recognize the vendored copy; its committed-hook and
settings-hook checks still find a committed one. The limitation is stated, not fixed. Claude Code on
the web sends the same hook data but loads no plugin's hooks, so a cloud session records nothing
until the hook is committed to the repository; the vendored `init` subcommand does that, copying
launcher, script, page and skill into the repository's `.claude/` and merging the six entries into
its `.claude/settings.json`.

**What does not exist.** No companion-plugin mechanism is built: the profiler has no namespace of its
own and no carrier but the devpro plugin. Should it become optional later, it becomes a
`--components` value. No opencode or mage payload ships: the profiler's hooks are claude's, and no
port is planned. Token counts come from claude's own transcripts under `~/.claude/projects/`, which
is claude's data, not a source the install configures.
```

**Becomes:**

```markdown
Every claude project install ships the activity profiler as payload, not as a companion plugin
(SPEC.md, Deployed Surfaces, Shipped files). The profiler is devpro's own code, ported from the
harness-profiler plugin by Aleksandr Furmanov (MIT, `github.com/afurmanov/harness-profiler`); the
acknowledgement in README.md credits the source of the idea and design. devpro owns the ported code
and carries no version stamp on it.

**Resources.** Three files live in `devpro/harnesses/resources/claude/libexec/`: `hp.sh`, the
POSIX-sh launcher that finds `python3` (`HP_PYTHON` overrides the search); `hp.py`, the whole tool —
`capture`, `tree`, `init`, `doctor` — one file, Python 3 standard library only, no dependency; and
`view.html`, the self-contained page template that loads nothing from the network. Each carries the
`!INSTALLED! … devpro` banner within its first ten lines — the banner rule binds every harness
resource. `harness_resource_copies` lands each at the path it holds below the install directory, so
the install directory gains `libexec/`.

**Wiring.** `harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `sh "${CLAUDE_PLUGIN_ROOT}/libexec/hp.sh" capture claude`. The wiring is data in the harness
module, not a new mechanism, and no entry is gated on the install-time probe. A capture appends one
line to the project's `.devpro-temp/harness-profile/<session-id>.jsonl` — the project's scratch
directory, which the project's own convention gitignores; a capture that fails, or finds no
`python3`, exits 0 with no output.

**The skill.** `show-profile` ships as a rendered skill definition under `devpro/definitions/skills/`,
so it carries the generated banner and the harness's namespace (`devpro:show-profile` under claude)
and renders under every harness. Its finder's first candidate, `../../libexec/hp.sh` from the
skill's directory, resolves to `<install-dir>/libexec/hp.sh` where the payload landed; its second,
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
`--components` value. No opencode or mage payload ships: the profiler's hooks are claude's, and an
opencode capture, should one come, is recreated in the opencode plugin's TypeScript rather than
reusing this code. Token counts come from claude's own transcripts under `~/.claude/projects/`, which
is claude's data, not a source the install configures.
```

## Code delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

`hp.js` ports to `hp.py` — Python 3 standard library only, the same four subcommands (`capture`,
`tree`, `init`, `doctor`) and the same capture behavior: one hook payload on stdin, one record
appended per event, exits 0 silently on a failed capture or a missing interpreter. `hp.sh` finds
`python3` (`HP_PYTHON` overrides the search) and runs `hp.py` beside it. The capture writes
`.devpro-temp/harness-profile/<session-id>.jsonl` under the project root, and the
`.git/info/exclude` write retires: the scratch directory's gitignore convention carries the
exclusion. The comment at `devpro/harnesses/claude.py:69-71` and the show-profile skill text's
trace-directory sentence move to the new path; the guide's node warning retires; the install tests'
`_PROFILER_FILES` pin becomes `("hp.py", "hp.sh", "view.html")`. The leaf, as amended by the
ARCHITECTURE delta above, stays true.
