// Runs opencode's plugin entry, index.ts, under a stub plugin context, for tests/test_opencode_entry.py.
//
// Usage: bun tests/opencode_entry_runner.ts
// Stdin: JSON {entry, directory, project, writes, command, modelSelects}: the installed entry; the directory the
// session opened at and the project root above it, the reminder's gate reading the root rather than the opened
// directory; files ({path, text}) written one at a time, each awaited until a reload its watcher triggers
// changes what is registered; a command ({name, path, text, user}) executed with the user's text before
// and after its body file is replaced by text; and the {sessionID, agent} pairs resolved through a request
// after everything above has run.
// Stdout: JSON {id, hooks, sessionHooks, states, prompts, synthetics}: the plugin id, the tool and
// session hooks it registered, what it had registered after setup and after each write, the text each
// execute prompted, and every synthetic message a hook injected, naming the event that fired the hook
// and the session it went to. Every callback registered for an event fires, so a hook name the
// entry registers twice reaches both registrations. A state holds the two stores opencode keeps an
// agent in: `agents`, the one its transform edits, and `requests`, the model a request for that agent
// resolves to — the two the runtime reads apart.
// The runner fails where an execute's prompt drops the invocation's session id or delivery, or where a
// reminder hook the entry must register is missing. It exits once the plugin's cleanup has run; a
// watcher the cleanup left open keeps it running.
//
// Run outside `bun test`: the "@opencode/plugin" stub must be registered before the entry loads.

import "./opencode_plugin_stub.ts"
import { writeFileSync } from "node:fs"

type Ref = { id: string; providerID: string }
type Input = {
  entry: string
  directory: string
  project: string
  writes: { path: string; text: string }[]
  command: { name: string; path: string; text: string; user: string }
  modelSelects: { sessionID: string; agent: string }[]
}
type Command = { name: string; description?: string; execute(input: unknown): Promise<void> }
// The two sessions the reminder hooks see: a subagent's child, whose parent is the session that
// dispatched it, and that parent, which has none.
const PARENT = "ses_parent"
const CHILD = "ses_child"
type Call = { tool: string; sessionID: string; status: "completed" | "error" }
// A session's idle event carries the work still running for it, one entry per running job.
type Idle = { sessionID: string; background: unknown[] }
// What a request reports to the model hooks: the Session's and the agent's own selections.
type Resolve = { sessionID: string; agent: string; model: Ref }

// A domain as opencode's State keeps one: every registered transform re-runs against a fresh
// value on each reload.
function domain<Value, Editor>(fresh: () => Value, editorOf: (value: Value) => Editor) {
  const callbacks: ((editor: Editor) => void)[] = []
  const d = {
    value: fresh(),
    build() {
      const value = fresh()
      for (const callback of callbacks) callback(editorOf(value))
      d.value = value
    },
    async transform(callback: (editor: Editor) => void) {
      callbacks.push(callback)
      d.build()
      return { dispose: async () => {} }
    },
    async reload() {
      d.build()
      onReload()
    },
  }
  return d
}

type Agent = { permissions: unknown[] } & Record<string, unknown>
// `selections` is the agent's own selection a request starts from, which no transform reaches; the
// store the transform edits is `agent.value`, rebuilt empty on each reload the way the host's is.
const selections = new Map<string, Ref>()
const agent = domain(
  () => new Map<string, Agent>(),
  (store) => ({
    update(id: string, update: (agent: Agent) => void) {
      const current = store.get(id) ?? {
        mode: "primary",
        hidden: false,
        permissions: [{ action: "*", resource: "*", effect: "allow" }],
      }
      update(current)
      store.set(id, current)
    },
  }),
)
const skill = domain(
  () => new Map<string, { id: string }>(),
  (skills) => ({ add: (s: { id: string }) => void skills.set(s.id, s) }),
)
const command = domain(
  () => new Map<string, Command>(),
  (commands) => ({ add: (c: Command) => void commands.set(c.name, c) }),
)
const mcp = domain(
  () => new Map<string, unknown>(),
  (servers) => ({ set: (name: string, config: unknown) => void servers.set(name, config) }),
)
let onReload = () => {}
// reloaded resolves at the first reload after which the registered state differs from the state at
// the call: a reload set off before a write can read the files before the write lands. A refresh
// rebuilds every domain synchronously, so by the time the promise settles all of them reflect it.
function reloaded(): Promise<void> {
  const before = JSON.stringify(state())
  return new Promise((done) => {
    onReload = () => {
      if (JSON.stringify(state()) !== before) done()
    }
  })
}

// The default a request for an agent neither the Session nor the agent's selection names falls back
// to: a model no registry record is configured with, so a resolved value equal to it is the entry's
// having set none.
const FALLBACK: Ref = { id: "fallback", providerID: "fallback" }
const resolves: ((input: Resolve) => void | Promise<void>)[] = []
async function resolved(select: { sessionID: string; agent: string }): Promise<Ref> {
  const input: Resolve = { sessionID: select.sessionID, agent: select.agent, model: selections.get(select.agent) ?? FALLBACK }
  for (const callback of resolves) await callback(input)
  return input.model
}

// The domains a reload rebuilds, and the agent store it does not: the reload's change is read here.
function built() {
  return {
    skills: Object.fromEntries(skill.value),
    commands: Object.fromEntries([...command.value].map(([name, c]) => [name, c.description ?? null])),
    mcp: Object.fromEntries(mcp.value),
  }
}

// A copy, not the store's own objects: the transform updates an entry in place, so a snapshot holding
// them would show a later reload's edits and read as unchanged.
function agentsSnapshot() {
  return JSON.parse(JSON.stringify(Object.fromEntries(agent.value)))
}

function state() {
  return {
    agents: agentsSnapshot(),
    requests: Object.fromEntries(selections),
    ...built(),
  }
}

const input: Input = JSON.parse(await Bun.stdin.text())
const prompts: string[] = []
const hooks: string[] = []
const sessionHooks: string[] = []
const synthetics: { on: string; sessionID: string; text: string }[] = []
const invocation = { sessionID: "ses_1", delivery: "queue" }
// Every callback registered for an event, in registration order: one plugin registers the entry's own
// reminder and the capture's, and each is fired.
const after: ((call: Call) => void | Promise<void>)[] = []
const idles: ((event: Idle) => void | Promise<void>)[] = []
// The hook whose callback is running, named in the synthetic record it produces.
let firing = ""

const plugin = (await import(input.entry)).default
const cleanup = await plugin.setup({
  location: { directory: input.directory, project: { directory: input.project } },
  tool: {
    async hook(name: string, callback: (call: Call) => void | Promise<void>) {
      hooks.push(name)
      if (name === "execute.after") after.push(callback)
    },
  },
  agent,
  skill,
  command,
  mcp,
  session: {
    async prompt(p: { text: string; sessionID: unknown; delivery: unknown }) {
      if (p.sessionID !== invocation.sessionID || p.delivery !== invocation.delivery) {
        throw new Error(`the prompt did not pass the invocation through: ${JSON.stringify(p)}`)
      }
      prompts.push(p.text)
    },
    async hook(name: string, callback: (event: never) => void | Promise<void>) {
      sessionHooks.push(name)
      if (name === "experimental.idle") idles.push(callback as (event: Idle) => void | Promise<void>)
      if (name === "experimental.model.resolve") resolves.push(callback as (event: Resolve) => void | Promise<void>)
    },
    async get({ sessionID }: { sessionID: string }) {
      return sessionID === CHILD ? { parentID: PARENT } : {}
    },
    async synthetic({ sessionID, text }: { sessionID: string; text: string }) {
      synthetics.push({ on: firing, sessionID, text })
    },
  },
})

const states = [state()]
for (const { path, text } of input.writes) {
  const done = reloaded()
  writeFileSync(path, text)
  await done
  states.push(state())
}

const execute = () => {
  const c = command.value.get(input.command.name)
  if (!c) throw new Error(`no command ${input.command.name} is registered`)
  return c.execute({ ...invocation, prompt: { text: input.command.user } })
}
await execute()
writeFileSync(input.command.path, input.command.text)
await execute()

// Fire each registered reminder path — a subagent's dispatch and its completion — and the calls the
// entry must ignore: a tool that is not a subagent, a subagent call that failed, a session with no
// parent of its own, and a session still holding work that runs. Every callback registered for the
// event fires, the capture's included; it appends internally whatever the payload, so these calls
// put no record in a store.
const fireTool = async (call: Call) => {
  if (after.length === 0) throw new Error("the entry registered no execute.after hook")
  firing = "execute.after"
  for (const callback of after) await callback(call)
}
const fireIdle = async (event: Idle) => {
  if (idles.length === 0) throw new Error("the entry registered no experimental.idle hook")
  firing = "experimental.idle"
  for (const callback of idles) await callback(event)
}
await fireTool({ tool: "subagent", sessionID: PARENT, status: "completed" })
await fireTool({ tool: "shell", sessionID: PARENT, status: "completed" })
await fireTool({ tool: "subagent", sessionID: PARENT, status: "error" })
await fireIdle({ sessionID: CHILD, background: [] })
await fireIdle({
  sessionID: CHILD,
  background: [{ kind: "shell", sessionID: CHILD, shellID: "sh_1", command: "sleep 60" }],
})
await fireIdle({ sessionID: PARENT, background: [] })

const models: Record<string, Ref> = {}
for (const select of input.modelSelects) models[select.sessionID] = await resolved(select)

await cleanup()
console.log(JSON.stringify({ id: plugin.id, hooks, sessionHooks, states, models, prompts, synthetics }))
