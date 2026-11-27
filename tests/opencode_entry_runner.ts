// Runs opencode's plugin entry, index.ts, under a stub plugin context, for tests/test_opencode_entry.py.
//
// Usage: bun tests/opencode_entry_runner.ts
// Stdin: JSON {entry, directory, project, writes, command, compactions, prompts}: the installed entry; the directory the
// session opened at and the project root above it, the reminder's gate reading the root rather than the opened
// directory; files ({path, text}) written one at a time, each awaited until a reload its watcher triggers
// changes what is registered; a command ({name, path, text, user}) executed with the user's text before
// and after its body file is replaced by text; the text each of two compactions of the primary
// session's context held; and the sessions to admit a prompt for, each {sessionID, skills}, the
// skills being the ids the operator's own prompt already attached.
// Stdout: JSON {id, hooks, sessionHooks, states, prompts, synthetics, attachments, log}: the plugin id, the tool and
// session hooks it registered, what it had registered after setup and after each write, the text each
// execute prompted, every synthetic message a hook injected, naming the event that fired the hook
// and the session it went to, the skills each admitted prompt carried, in the order it carried
// them, and the reports the entry wrote as it ran. The runner fires the compaction surface beside the reminder — a compaction carrying a skill's
// body records the session, and the session's next prompt, admitted after every compaction, is where
// the skill's reload attaches it, as the host admits the prompt a compaction is followed by. Every
// callback registered for an event fires, so a hook name the entry registers twice reaches both
// registrations.
// A state holds the agents store opencode keeps
// an agent in, the one its transform edits. The runner fails where an execute's prompt drops the
// invocation's session id or delivery, or where a reminder hook the entry must register is missing.
// It exits once the plugin's cleanup has run; a watcher the cleanup left open keeps it running.
//
// Run outside `bun test`: the "@opencode/plugin" stub must be registered before the entry loads.

import "./opencode_plugin_stub.ts"
import { writeFileSync } from "node:fs"

type Input = {
  entry: string
  directory: string
  project: string
  writes: { path: string; text: string }[]
  command: { name: string; path: string; text: string; user: string }
  compactions: { sessionID: string; text: string }[]
  prompts: { sessionID: string; skills: string[] }[]
}
type Command = { name: string; description?: string; execute(input: unknown): Promise<void> }
// A skill as the plugin's own transform leaves it in the domain, and as its editor lists it back.
type Skill = { id: string; name: string; path: string; content: string }
// The sessions the hooks see: a subagent's child, whose parent is the session that dispatched it,
// that parent, and the primary session a compaction lands on when the test drives one there.
const PARENT = "ses_parent"
const CHILD = "ses_child"
const PRIMARY = "ses_primary"
type Call = { tool: string; sessionID: string; status: "completed" | "error" }
// A session's idle event carries the work still running for it, one entry per running job.
type Idle = { sessionID: string; background: unknown[] }
// A compaction request: the session, and the messages the context it replaces holds. The skill's
// activation is one message's text part, `content` the part list a skill message nests its body in.
type Compact = { sessionID: string; messages: { role: string; content: { type: string; text: string }[] }[] }
// A prompt as the host admits one: the session, and the prompt draft the hook mutates, whose skills
// are the ones the operator's own prompt already carried. The draft's skills after the hook are the
// attachment a test reads.
type Prompt = { sessionID: string; prompt: { text: string; skills?: { id: string }[] } }

// A domain as opencode's State keeps one: every registered transform re-runs against a fresh
// value on each reload. `list` is the domain's own read, as the host issues it.
function domain<Value, Editor>(fresh: () => Value, editorOf: (value: Value) => Editor) {
  const callbacks: ((editor: Editor) => void)[] = []
  const d = {
    value: fresh(),
    build() {
      const value = fresh()
      for (const callback of callbacks) callback(editorOf(value))
      d.value = value
    },
    list(): Promise<{ data: Skill[] }> {
      return Promise.resolve({ data: [...(d.value as unknown as Map<string, Skill>).values()] })
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
// The store the transform edits is `agent.value`, rebuilt empty on each reload the way the host's is.
const agent = domain<Map<string, Agent>, unknown>(
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
const skill = domain<Map<string, Skill>, { add(s: { id: string; name: string; path: string; content: string }): void }>(
  () => new Map<string, Skill>(),
  (skills) => ({
    // The host brands a skill's id, name and path; the stub's strings stand for those brands.
    add: (s) => void skills.set(s.id, { id: s.id, name: s.name, path: s.path, content: s.content }),
  }),
)
const command = domain<Map<string, Command>, unknown>(
  () => new Map<string, Command>(),
  (commands) => ({ add: (c: Command) => void commands.set(c.name, c) }),
)
const mcp = domain<Map<string, unknown>, unknown>(
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
    ...built(),
  }
}

const input: Input = JSON.parse(await Bun.stdin.text())
// The entry's reports: the stderr it writes as it runs, read back so a test can weigh a report
// against what the run did rather than read the test's own command line for it.
const log: string[] = []
const reported = console.error
console.error = (...args: unknown[]) => {
  log.push(args.map(String).join(" "))
  reported(...args)
}
const prompts: string[] = []
const hooks: string[] = []
const sessionHooks: string[] = []
const synthetics: { on: string; sessionID: string; text: string; delivery: string }[] = []
const attachments: { sessionID: string; skills: string[] }[] = []
const invocation = { sessionID: "ses_1", delivery: "queue" }
// Every callback registered for an event, in registration order: one plugin registers the entry's own
// reminder and the capture's, and each is fired.
const after: ((call: Call) => void | Promise<void>)[] = []
const idles: ((event: Idle) => void | Promise<void>)[] = []
const compactions: ((event: Compact) => void | Promise<void>)[] = []
const admissions: ((event: Prompt) => void | Promise<void>)[] = []
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
      if (name === "compaction") compactions.push(callback as (event: Compact) => void | Promise<void>)
      if (name === "prompt") admissions.push(callback as (event: Prompt) => void | Promise<void>)
    },
    async get({ sessionID }: { sessionID: string }) {
      // A session with no parent carries no `parentID` field at all, as the host's `Session` omits it.
      return sessionID === CHILD ? { parentID: PARENT } : {}
    },
    async synthetic({ sessionID, text, delivery }: { sessionID: string; text: string; delivery: string }) {
      synthetics.push({ on: firing, sessionID, text, delivery })
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
// The compaction is a request the host builds before the model summary, and the messages handed
// here are the context it replaces: a message carrying the skill's body, then the user turn that
// follows. What follows it in the host is the session's next prompt, which the runner admits after
// every firing below.
const fireCompaction = async (event: Compact) => {
  if (compactions.length === 0) throw new Error("the entry registered no compaction hook")
  firing = "compaction"
  for (const callback of compactions) await callback(event)
}
// A prompt as the host admits one: the hook mutates the draft, and what the admission carries after
// the hook is what the host resolves the skill's attachment from.
const firePrompt = async (event: Prompt) => {
  if (admissions.length === 0) throw new Error("the entry registered no prompt hook")
  firing = "prompt"
  for (const callback of admissions) await callback(event)
  attachments.push({ sessionID: event.sessionID, skills: (event.prompt.skills ?? []).map((skill) => skill.id) })
}
// A compaction's context holding a skill's activation: the skill message, its body's text nested in
// `content`. The day the host nests a skill's body otherwise is the entry's read's to follow, and
// this message with it.
const skillMessage = (text: string) => ({
  role: "user",
  content: [{ type: "text", text }],
})
await fireTool({ tool: "subagent", sessionID: PARENT, status: "completed" })
await fireTool({ tool: "shell", sessionID: PARENT, status: "completed" })
await fireTool({ tool: "subagent", sessionID: PARENT, status: "error" })
await fireIdle({ sessionID: CHILD, background: [] })
await fireIdle({
  sessionID: CHILD,
  background: [{ kind: "shell", sessionID: CHILD, shellID: "sh_1", command: "sleep 60" }],
})
await fireIdle({ sessionID: PARENT, background: [] })

// The compaction surface, driven from the input so a test states what each session's context held,
// and the prompts admitted after it. Each text is one compaction of the primary session's context —
// the host builds the request, then the compacted session's next prompt is admitted, the exchange the
// reload's attachment rides. A prompt's own skills are the operator's, as the input states them. The
// primary session is a compaction's likeliest target, and the reminder, which reads only a session
// with a parent, is silent on it: the synthetic records above are the reminder's own.
const texts = [0, 1].map((i) => input.compactions[i]?.text ?? "")
for (const [index, text] of texts.entries()) {
  await fireCompaction({ sessionID: PRIMARY, messages: [skillMessage(text)] })
  const own = (input.prompts[index]?.skills ?? []).map((id) => ({ id }))
  await firePrompt({ sessionID: PRIMARY, prompt: { text: "what's next?", skills: own } })
}
// The prompts the input asks for beyond the compactions', each on the session it names: a prompt of
// a session the marker never recorded, or a second one on a session whose marker a prompt has spent.
for (const extra of input.prompts.slice(texts.length)) {
  await firePrompt({ sessionID: extra.sessionID, prompt: { text: "what's next?", skills: extra.skills.map((id) => ({ id })) } })
}

await cleanup()
console.log(JSON.stringify({ id: plugin.id, hooks, sessionHooks, states, prompts, synthetics, attachments, log }))
