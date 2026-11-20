### Opencode entry

`devpro/harnesses/resources/opencode/index.ts` is opencode's plugin entry (SPEC.md, Deployed
Surfaces, Shipped files). It is written for opencode 2.3.2 (floor 2.3.0), and its setup registers `ctx.tool.hook("execute.after")` filtered to `subagent` and
`ctx.session.hook("experimental.idle")` for a session whose `parentID` is set, injecting
`ctx.session.synthetic` into the parent session at agent dispatch and agent completion, gated by
the active plan (`ACTIVE_PLAN.md` or the diced `ACTIVE_PLAN/` tree; SPEC, Shipped files). The
install copies it, with `guardrail.ts`, to the install directory as a harness resource (Renders
and copies); a user-level install copies the entry alone.

The floor is a behavioral one, not an API one: every API the entry uses exists at 2.2.6, but there
the `subagent` tool defaults to the foreground, so `execute.after` fires at the child's completion,
behind the idle hook — a parent gets two completion nudges and none at the dispatch. From 2.3.0 the
call returns at once and the child runs in the background, which makes the call's return the
dispatch moment.

**The opencode API it uses.** It imports `Plugin` from `@opencode/plugin` and exports
`Plugin.define({ id, setup })`.

- `id` is the registry's `plugin`, read synchronously from `registry.json` because opencode takes the id
  before `setup` runs; an unreadable registry falls back to the install directory's name.
- `setup(ctx)` receives four registration domains, `ctx.agent`, `ctx.skill`, `ctx.command` and
  `ctx.mcp`. Each has `transform(callback)`, which hands the callback an editor: `update(id, fn)` for
  agents, `add` for skills and commands, `set(name, config)` for MCP servers. Each also has
  `reload()`, which makes opencode run its transforms again. `ctx.session.prompt` delivers a
  command's text.
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
  running. A user-level install has no `guardrail.ts`, and none runs.
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
  belongs to the execution that just ran, and its text is the sentence claude's reminder script
  emits, byte for byte, naming the status table's two acts: `in progress` when a package is
  dispatched, `landed` when its work is accepted and committed.
- *Watcher.* A recursive `fs.watch` on the install directory schedules a refresh after a 100 ms
  quiet period. Refreshes are serialized on one promise chain, so an older read never replaces a
  newer one. A refresh re-reads the registry and calls the four `reload()`s; a failure is logged and the
  next change tries again. The watcher has an error listener that logs. The cleanup clears the
  pending refresh, closes the watcher and awaits a refresh in flight.
