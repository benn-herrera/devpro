# Opencode entry

`devpro/harnesses/resources/opencode/index.ts` is opencode's plugin entry (SPEC.md, Deployed
Surfaces, Shipped files). It is written for opencode, and its setup registers `ctx.tool.hook("execute.after")` filtered to `subagent` and
`ctx.session.hook("experimental.idle")` for a session whose `parentID` is set, injecting
`ctx.session.synthetic` into the parent session at agent dispatch and agent completion, gated by
the active plan (`ACTIVE_PLAN.md` or the diced `ACTIVE_PLAN/` tree; SPEC, Shipped files) — and
registers the reload of the development skill a compaction drops (SPEC, Shipped files). The
compaction hook records the session when its context held the `devpro-development` skill. The
prompt hook then has the skill attached to the session's next prompt's `skills`, through the
host's own attachment path, its id resolved from the plugin's skill domain; a lookup that finds
no skill attaches nothing and logs. The hooks' names are the host's published declarations' to
give, read there at execution and never assumed (CONVENTIONS, Code, Definitions and Install, A
hook contract is read, not assumed). The
install copies it, with `guardrail.ts` and, on a project install, the capture `profiler.ts` (Harness
profiler), to the install directory as a harness resource (Renders
and copies); a user-level install copies the entry and the guardrail resource beside it.

The entry's host requirement is SPEC's (SPEC.md, Deployed Surfaces, Shipped files). The floor is a
behavioral one: the `subagent` tool defaults to the foreground below 2.3.0, so `execute.after`
fires at the child's completion, behind the idle hook — a parent gets two completion nudges and
none at the dispatch. From 2.3.0 the call returns at once and the child runs in the background,
which makes the call's return the dispatch moment.

**The opencode API it uses.** It imports `Plugin` from `@opencode/plugin` and exports
`Plugin.define({ id, setup })`.

- `id` is the plugin's: the registry's `plugin`, read synchronously from `registry.json` because
  opencode takes the id before `setup` runs; an unreadable registry falls back to the install
  directory's name. Every module of the plugin reads it that way, the entry and each module it
  awaits (`guardrail.ts`, `profiler.ts`), so a module carries no id of its own.
- `setup(ctx)` receives four registration domains, `ctx.agent`, `ctx.skill`, `ctx.command` and
  `ctx.mcp`. Each has `transform(callback)`, which hands the callback an editor: `update(id, fn)` for
  agents, `add` for skills and commands, `set(name, config)` for MCP servers. Each also has
  `reload()`, which makes opencode run its transforms again. `ctx.session.prompt` delivers a
  command's text.
- The reload's surface is the session hooks `compaction` and `prompt`, and `ctx.skill.list`, the
  domain the attachment's id is resolved from.
- The reminder's surface is `ctx.location.project.directory`, the checkout root — the opened
  directory, `ctx.location.directory`, need not be it — read for the gate; `ctx.tool.hook` and
  `ctx.session.hook` for its two events, `ctx.session.get` for a session's `parentID`, and
  `ctx.session.synthetic` for the injection.
- `setup` returns an async cleanup, which opencode calls when the plugin module goes.

The entry declares the slice of the context it reads as local types. Nothing checks them against
opencode itself: the tests run the entry under a stub of this surface
(`tests/opencode_plugin_stub.ts`, `tests/opencode_entry_runner.ts`).

**What it does.**

- *Guardrail first.* Where `guardrail.ts` stands beside it, `setup` awaits that module's `setup`
  before registering anything or starting the watcher, so a failed guardrail leaves no watcher
  running. A user-level install copies `guardrail.ts` beside the entry, and the entry runs it there as
  it does in a project.
- *The capture.* Where `profiler.ts` stands beside it, `setup` awaits that module's `setup` the same
  way, which registers the activity capture's four hooks (Harness profiler), its `experimental.idle`
  recording every session's idle, a child's included, where the reminder's is parent-scoped. A
  user-level install ships none, and nothing records.
- *Registry read.* It parses `registry.json` as the shape the opencode harness renders and validates
  nothing; the renderer is the only writer (Rendering, Harnesses and families). It reads each agent
  and skill body with async `readFile` and strips the leading comment lines, and the blank line
  after them, that carry the banner. A body or registry it cannot read is logged and left out; the
  rest registers.
- *Registration.* Each agent record updates the agent of that id: the body as its system text, the
  description, mode, hidden flag, model and color where the record has them, and each permission as
  an allow or deny rule on every resource. Each skill is added with its id as its name, its path
  and its body. Each MCP record is set under its name.
- *Commands.* A command's body is read when the command runs, banner stripped, and prepended to the
  text the operator typed; a read failure names the file. The session id and delivery mode pass
  through to `ctx.session.prompt` unchanged.
- *Reminder.* Two hooks, registered on every install and gated when they fire, so a project holding
  no gate path pays nothing: a `subagent` call that completed is the dispatch moment, and a session
  going idle with an empty `background` list is a subagent's completion, whose parent — the
  `parentID` `ctx.session.get` reports — is the one injected into. An idle session that still holds
  running work reports nothing: the wake that follows that work fires the hook again, and that idle
  is the completion. Each injection is one `ctx.session.synthetic` message delivered `steer`, so it
  belongs to the execution that just ran, and its text is the plan-state reminder's sentence, whose
  text lives in this entry — `devpro/harnesses/resources/opencode/index.ts`, its one home — and
  restates the sentence claude's `state-table-reminder.sh` emits.
- *Watcher.* A recursive `fs.watch` on the install directory schedules a refresh after a 100 ms
  quiet period. Refreshes are serialized on one promise chain, so an older read never replaces a
  newer one. A refresh re-reads the registry and calls the four `reload()`s; a failure is logged and the
  next change tries again. The watcher has an error listener that logs. The cleanup clears the
  pending refresh, closes the watcher and awaits a refresh in flight.

**The replacement under the running session.** A refresh reads `registry.json` and each body, keeps
what it could read, and then runs the four reloads on what it kept: a registry it cannot read
registers nothing, so the four stores come back empty and a later event's refresh restores them from
whatever stands then. An install's replacement is the delete pass over the whole install directory
followed by the write pass, the two together about 64 ms of a run that takes about 218 ms on the
host it was measured on, with no pause between them. What a running session holds across one was
observed on a stub context over real installs — the drivers, the raw records and the extraction in
`.devpro-temp/B25-watcher/` (gitignored; `record.py` there regenerates all of it) beside the
checkout that landed this paragraph — and their summary follows:

- The watcher's callback fires once the filesystem has been quiet for about 102 ms, then its refresh
  reads and reloads. Against the real replacement that is one callback and one refresh, after the
  run: the entry re-registers the finished tree — attributes for attributes the tree that replaced
  them — and the session's stores keep the old ones until then, never the empty read.
- Where the quiet period elapses between the passes the same watcher re-registers nothing: a
  replacement with a pause of 150 ms between the delete and the write pass left the refresh that
  fired in the pause with 0 agents, 0 skills and 0 MCP servers, and the write pass's end restored
  28, 5 and 1 (the counts of the staged install). A cold load of the entry reads the same empty
  tree then, and cannot load at all while the entry file is gone. The observed install's pass
  timing keeps the quiet period from elapsing between the passes, so the empty state is one a
  slower delete pass or a slower write pass can reach.

The observation could not drive the host's own reload of the entry's file (opencode's module loader
is not a testable surface), and `fs.watch` cannot be wrapped from outside the module that imports it
in the runtime the entry runs on; the records are the entry's own timer, refresh chain, reads and
reloads over the stub context, and a fresh module load standing in for the host's next load. What
the host does with a `reload()` — whether a session in flight re-reads its registration then or at
its next turn — is outside both. SPEC.md, Write Safety, states what a consumer may rely on.
