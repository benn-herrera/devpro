# Wiring.

`harnesses/claude.py`'s `_registration_hooks` carries the profiler's six hook entries
beside the guardrail's and the reminder's: `PostToolUse`, `PostToolUseFailure`, `PreCompact`,
`PostCompact`, `SessionStart` and `SubagentStop`, each `matcher "*"`, `async: true`, `timeout: 5`,
running `"${CLAUDE_PLUGIN_ROOT}/skills/devpro/tools/devpro.sh" profiler capture claude`
(`claude.INSTALL_WRAPPER`). The wiring is data in the harness module, not a new mechanism, and no
entry is gated on the install-time probe. A capture appends one line to the project's
`.devpro-temp/.profiler-claude/<session-id>.jsonl` — one of the per-harness stores under
`.devpro-temp/`, the project's scratch directory, which a project install of a nested plugin prepares
and gitignores (a mage or user-level install prepares neither; The scratch directory, Renders and
copies). The
wrapper's `capture` subcommand
owns the never-block contract: `cli.run` reads the hook payload bounded to `PAYLOAD_LIMIT` bytes,
points stdout at the null device for the capture's duration so no child line reaches the hook's
stdout, and returns 0 on every path.

