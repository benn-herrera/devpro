# Active design — the session nudge and the kanban wording

The devpro and kbase plugins nudge the session model to keep the plan's status table current at
agent dispatch and agent completion, under claude and opencode, and the docdicer and guide skills
let the session offer to run the board as a background process or hand the command line, the user
choosing. Consumers observe the nudge on every harness where the plugin ships; mage carries none.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The
summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [SPEC.md, Deployed Surfaces, Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

The harness resource listing gains the reminder script; the guardrail registration statement gains
the reminder entries; the opencode entry statement gains the runtime hooks.

```
A **harness resource** is a file a harness ships, such as a guardrail script or opencode's plugin
entry, copied as it stands and never rendered.
```
becomes
```
A **harness resource** is a file a harness ships, such as a guardrail script, opencode's plugin
entry or the plan-state reminder script, copied as it stands and never rendered.
```

```
`<install-dir>/guardrail.ts`, and claude's at `<install-dir>/hooks/guardrail.pl` (mage ships none)
```
becomes
```
`<install-dir>/guardrail.ts`, and claude's at `<install-dir>/hooks/guardrail.pl` and
`<install-dir>/hooks/state-table-reminder.sh` (mage ships none)
```

```
Opencode loads the plugin directory and registers its agents, skills, commands and, where
`kbase` ships, the `kbase` MCP server under the registry's ids.
```
becomes
```
Opencode loads the plugin directory and registers its agents, skills, commands and, where
`kbase` ships, the `kbase` MCP server under the registry's ids, and injects a plan-state reminder
into the parent session at agent dispatch and agent completion, gated by `ACTIVE_PLAN.md` or
`ACTIVE_DESIGN.md` existing at the project root.
```

### [SPEC.md, Guide and README](PROJECT_DOCS/SPEC/guide-and-readme.md)

```
  - lighter process: a step skipped at the user's direction, and work that goes straight to a
    plan;
  - the board.
```
becomes
```
  - lighter process: a step skipped at the user's direction, and work that goes straight to a
    plan;
  - the board: the session offers to run it in the background, or hands the command line, the
    user choosing.
```

## ARCHITECTURE delta

### [ARCHITECTURE.md, Install, Guardrail hook](PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md)

The registration's statement gains the reminder entries and their gating.

```
The registration holds one `PreToolUse` entry, in Claude's settings shape under a top-level
`hooks` key, whose matcher is `Bash|Read|Write|Edit|NotebookEdit|Grep|Glob` on every claude
install, as the text builder writes it.
```
becomes
```
The registration holds the guardrail's `PreToolUse` entry — matcher
`Bash|Read|Write|Edit|NotebookEdit|Grep|Glob` — where the install-time probe passes, plus two
ungated plan-state reminder entries on every claude install, each running
`<install-dir>/hooks/state-table-reminder.sh`, which reads `ACTIVE_PLAN.md` or `ACTIVE_DESIGN.md`
at the project root and emits a one-sentence `hookSpecificOutput.additionalContext` reminder to
update the plan's status table.
```

### [ARCHITECTURE.md, Install, Opencode entry](PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md)

The entry gains runtime hooks and its target version statement moves.

```
`devpro/harnesses/resources/opencode/index.ts` is opencode's plugin entry (SPEC.md, Deployed
Surfaces, Shipped files). It is written for opencode v2.2.6 and is the same file for both plugins.
```
becomes
```
`devpro/harnesses/resources/opencode/index.ts` is opencode's plugin entry (SPEC.md, Deployed
Surfaces, Shipped files). It is written for opencode 2.3.2 (floor 2.2.6) and is the same file for
both plugins, and its setup registers `ctx.tool.hook("execute.after")` filtered to `subagent` and
`ctx.session.hook("experimental.idle")` for a session whose `parentID` is set, injecting
`ctx.session.synthetic` into the parent session at agent dispatch and agent completion, gated by
`ACTIVE_PLAN.md` or `ACTIVE_DESIGN.md` existing at the project root.
```

### [ARCHITECTURE.md, Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

```
  It names `check-design` and `check-roadmap` beside `check-plan`; neither has a recipe of its
```
becomes
```
  Its `kanban` paragraph offers running the board as a background process or hands the command
  line, letting the user choose. It names `check-design` and `check-roadmap` beside `check-plan`;
  neither has a recipe of its
```

## Code delta

### [ARCHITECTURE.md, Install, Guardrail hook](PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md)

`devpro/harnesses/resources/claude/hooks/state-table-reminder.sh` ships as a claude harness
resource, and `devpro/harnesses/claude.py` writes the two reminder entries beside the guardrail's
in its rendered `hooks/hooks.json`, both ungated, so a probe failure leaves them.

### [ARCHITECTURE.md, Install, Opencode entry](PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md)

`devpro/harnesses/resources/opencode/index.ts`'s setup registers the two runtime hooks and
injects `ctx.session.synthetic` into the parent session, and its declared context slice gains the
tool and session domains; `tests/test_opencode_entry.py`'s stub carries them.

### [ARCHITECTURE.md, Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

`devpro/definitions/skills/docdicer.py`'s kanban paragraph and `devpro/definitions/skills/guide.py`'s
board bullet carry the offer-to-run wording, held to the Subsystem Map statement above and the
Guide and README board item above.