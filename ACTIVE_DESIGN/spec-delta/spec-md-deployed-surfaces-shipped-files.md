### [SPEC.md, Deployed Surfaces, Shipped files](../../PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

The packages' delivery statement names the set, the `.index/` trigger names the component, and the
leaf gains the profiler payload.

```
(Plugins). Both plugins deliver the **docdicer tools package** at its package destination under
the install directory, `skills/docdicer/tools/`: inside the `docdicer` skill's own directory. They
also deliver the **development scripts package**, `skills/development/scripts/`, inside the
`development` skill's own directory (below), under mage as under claude and opencode. The kbase
plugin also delivers the kb-tools package (below).
```
becomes
```
(Plugins). Every install delivers the **docdicer tools package** at its package destination under
the install directory, `skills/docdicer/tools/`: inside the `docdicer` skill's own directory. It
also delivers the **development scripts package**, `skills/development/scripts/`, inside the
`development` skill's own directory (below), under mage as under claude and opencode. An install
with the kbase component also delivers the kb-tools package (below).
```

```
file, which they look for on every call, so an install of the devpro plugin is never blocked by it.
```
becomes
```
file, which they look for on every call, so an install without the kbase component is never blocked
by it.
```

```
A harness shipping none copies nothing, which is not an error.
```
becomes
```
A harness shipping none copies nothing, which is not an error.

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

