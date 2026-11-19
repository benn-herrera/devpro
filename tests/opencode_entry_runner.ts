// Runs opencode's plugin entry, index.ts, under a stub plugin context, for tests/test_opencode_entry.py.
//
// Usage: bun tests/opencode_entry_runner.ts
// Stdin: JSON {entry, directory, writes, command}: the installed entry; the project directory; files
// ({path, text}) written one at a time, each awaited until a reload its watcher triggers changes what is
// registered; and a command ({name, path, text, user}) executed with the user's text before and after
// its body file is replaced by text.
// Stdout: JSON {id, hooks, sessionHooks, states, prompts, synthetics}: the plugin id, the tool and
// session hooks it registered, what it had registered after setup and after each write, the text each
// execute prompted, and every synthetic message a hook injected, naming the event that fired the hook
// and the session it went to.
// The runner fails where an execute's prompt drops the invocation's session id or delivery, or where a
// reminder hook the entry must register is missing. It exits once the plugin's cleanup has run; a
// watcher the cleanup left open keeps it running.
//
// Run outside `bun test`: the "@opencode/plugin" stub must be registered before the entry loads.

import "./opencode_plugin_stub.ts"
import { writeFileSync } from "node:fs"

type Input = {
  entry: string
  directory: string
  writes: { path: string; text: string }[]
  command: { name: string; path: string; text: string; user: string }
}
type Command = { name: string; description?: string; execute(input: unknown): Promise<void> }
// The two sessions the reminder hooks see: a subagent's child, whose parent is the session that
// dispatched it, and that parent, which has none.
const PARENT = "ses_parent"
const CHILD = "ses_child"
type Call = { tool: string; sessionID: string; status: "completed" | "error" }

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
const agent = domain(
  () => new Map<string, Agent>(),
  (agents) => ({
    update(id: string, update: (agent: Agent) => void) {
      const current = agents.get(id) ?? {
        mode: "primary",
        hidden: false,
        permissions: [{ action: "*", resource: "*", effect: "allow" }],
      }
      update(current)
      agents.set(id, current)
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

function state() {
  return {
    agents: Object.fromEntries(agent.value),
    skills: Object.fromEntries(skill.value),
    commands: Object.fromEntries([...command.value].map(([name, c]) => [name, c.description ?? null])),
    mcp: Object.fromEntries(mcp.value),
  }
}

const input: Input = JSON.parse(await Bun.stdin.text())
const prompts: string[] = []
const hooks: string[] = []
const sessionHooks: string[] = []
const synthetics: { on: string; sessionID: string; text: string }[] = []
const invocation = { sessionID: "ses_1", delivery: "queue" }
let after: ((call: Call) => void | Promise<void>) | undefined
let idle: ((event: { sessionID: string }) => void | Promise<void>) | undefined
// The hook whose callback is running, named in the synthetic record it produces.
let firing = ""

const plugin = (await import(input.entry)).default
const cleanup = await plugin.setup({
  location: { directory: input.directory },
  tool: {
    async hook(name: string, callback: (call: Call) => void | Promise<void>) {
      hooks.push(name)
      if (name === "execute.after") after = callback
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
    async hook(name: string, callback: (event: { sessionID: string }) => void | Promise<void>) {
      sessionHooks.push(name)
      if (name === "experimental.idle") idle = callback
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

// Fire each registered reminder path: a subagent's dispatch and completion, and the two calls the
// entry must ignore — a tool that is not a subagent, and a session with no parent of its own.
const fireTool = async (call: Call) => {
  if (!after) throw new Error("the entry registered no execute.after hook")
  firing = "execute.after"
  await after(call)
}
const fireIdle = async (event: { sessionID: string }) => {
  if (!idle) throw new Error("the entry registered no experimental.idle hook")
  firing = "experimental.idle"
  await idle(event)
}
await fireTool({ tool: "subagent", sessionID: PARENT, status: "completed" })
await fireTool({ tool: "shell", sessionID: PARENT, status: "completed" })
await fireIdle({ sessionID: CHILD })
await fireIdle({ sessionID: PARENT })

await cleanup()
console.log(JSON.stringify({ id: plugin.id, hooks, sessionHooks, states, prompts, synthetics }))
