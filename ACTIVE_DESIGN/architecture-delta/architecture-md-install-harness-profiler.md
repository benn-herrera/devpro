### [ARCHITECTURE.md, Install, Harness profiler](../../PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

A new leaf, carrying the vendored payload's statements whole:

```
### Harness profiler

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

