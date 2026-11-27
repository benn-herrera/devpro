// Runs opencode's plugin entry, index.ts, under a stub plugin context, for tests/test_opencode_entry.py.
//
// Usage: bun tests/opencode_entry_runner.ts
// Stdin: JSON {entry, directory, project, writes, command, compactions, prompts, skillLoads}, each
// key the runner fires in this order:
//   entry — the installed entry
//   directory — the directory the session opened at and the project root above it, the reminder's
//     gate reading the root rather than the opened directory
//   project — the project root
//   writes — files ({path, text}) written one at a time, each awaited until a reload its watcher
//     triggers changes what is registered
//   command — ({name, path, text, user}) executed with the user's text before and after its body
//     file is replaced by text
//   compactions — the provider request messages each of two compactions of the primary session's
//     context holds
//   prompts — the sessions to admit a prompt for, each {sessionID, skills}, the skills being the ids
//     the prompt draft carries before the hook runs
//   skillLoads — {name, path} entries whose body the runner appends — banner stripped, a `# Skill:
//     <name>` heading in its place — to the Agents file's text in the false-positive session's
//     context
// Stdout: JSON {id, hooks, sessionHooks, states, prompts, synthetics, attachments, log}, each key in
// this order:
//   id — the plugin id
//   hooks — the tool hooks the entry registered
//   sessionHooks — the session hooks the entry registered
//   states — what it had registered after setup and after each write; a state holds the agents store
//     opencode keeps an agent in, the one its transform edits
//   prompts — the text each execute prompted
//   synthetics — every synthetic message a hook injected, naming the event that fired the hook and
//     the session it went to
//   attachments — the skills each admitted prompt carried, in the order it carried them
//   log — the reports the entry wrote as it ran
// Every callback registered for an event fires, so a hook name the entry registers twice reaches
// both registrations. The runner fails where an execute's prompt drops the invocation's session id
// or delivery, or where a reminder or reload hook the entry must register is missing. It exits once
// the plugin's cleanup has run; a watcher the cleanup left open keeps it running.
//
// The runner fires, in order: each reminder path — a subagent dispatch and its completion, and the
// calls the entry must ignore; then each of the two compactions of the primary session and the
// prompt admitted after it; then the false-positive session's compaction and prompt; then any prompt
// the input names beyond those. Each compaction and each prompt fires every callback registered for
// it, the capture's included.
//
// Run outside `bun test`: the "@opencode/plugin" stub must be registered before the entry loads.

import "./opencode_plugin_stub.ts"
import { readFileSync, writeFileSync } from "node:fs"
import { join } from "node:path"
import type { SessionCompaction, SessionIdle, SessionPrompt } from "@opencode/plugin/promise/session"

// The `Bun` global, for the stub the runner registers and the stdin it reads: `@types/bun` is not
// among the `package.json`'s dependencies, and the runtime the runner executes under is bun's.
declare global {
  // eslint-disable-next-line no-var -- a global declaration
  var Bun: {
    stdin: { text(): Promise<string> }
    plugin(config: {
      setup(build: { module(name: string, loader: () => { loader: string; exports: unknown }): void }): void
    }): void
  }
}

type Input = {
  entry: string
  directory: string
  project: string
  writes: { path: string; text: string }[]
  command: { name: string; path: string; text: string; user: string }
  compactions: { sessionID: string; messages: SessionCompaction["messages"] }[]
  prompts: { sessionID: string; skills: string[] }[]
  skillLoads?: { name: string; path: string }[]
}
type Command = { name: string; description?: string; execute(input: unknown): Promise<void> }
// A skill as the plugin's own transform leaves it in the domain, and as its editor lists it back.
type Skill = { id: string; name: string; path: string; content: string }
// The sessions the hooks see: a subagent's child, whose parent is the session that dispatched it,
// that parent, and the primary session a compaction lands on when the test drives one there.
const PARENT = "ses_parent"
const CHILD = "ses_child"
const PRIMARY = "ses_primary"
// The session whose context holds only the Agents file's text: the marker's false positive, R6's
// case. It is named after the defect so a record on it reads as one.
const SKILL_QUESTIONED = "ses_the_agents_file_names_the_skill"
type Call = { tool: string; sessionID: string; status: "completed" | "error" }
// A prompt as the host admits one: the session, and the prompt draft the hook mutates, whose skills
// are the ones the operator's own prompt already carried. The draft's skills after the hook are the
// attachment a test reads.
type Prompt = SessionPrompt & { prompt: { text: string; skills?: { id: string }[] } }
type Compact = SessionCompaction

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
const idles: ((event: SessionIdle) => void | Promise<void>)[] = []
const compactionHooks: ((event: Compact) => void | Promise<void>)[] = []
const admissions: ((event: Prompt) => void | Promise<void>)[] = []
// The hook whose callback is running, named in the synthetic record it produces.
let firing = ""

// A branded string the host's declarations give a maker for. The runner fabricates ids in the
// declarations' shapes so a stand-in message is one the host itself could build; a brand is a type,
// not a runtime mark, so the string passes through whole.
const brand = <T extends string>(value: string): T => value as unknown as T
// A provider request message as the host builds one, cutting its fields. A message whose required
// fields are cut to satisfy a test is one the runner cannot build; the cut is refused.
function message<T extends SessionCompaction["messages"][number]>(fields: T): T {
  return fields
}
// A job a session's idle event reports still running, in the declarations' shape.
const background = <T extends SessionIdle["background"][number]>(job: T): T => job

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
      if (name === "experimental.idle") idles.push(callback as (event: SessionIdle) => void | Promise<void>)
      if (name === "compaction") compactionHooks.push(callback as (event: Compact) => void | Promise<void>)
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
const fireIdle = async (event: SessionIdle) => {
  if (idles.length === 0) throw new Error("the entry registered no experimental.idle hook")
  firing = "experimental.idle"
  for (const callback of idles) await callback(event)
}
// The compaction is a request the host builds before the model summary, and the messages handed
// here are the context it replaces — provider request messages, built from the input. What follows
// it in the host is the session's next prompt, which the runner admits after every firing below.
const fireCompaction = async (event: Compact) => {
  firing = "compaction"
  for (const callback of compactionHooks) await callback(event)
}
// A prompt as the host admits one: the hook mutates the draft, and what the admission carries after
// the hook is what the host resolves the skill's attachment from.
const firePrompt = async (event: Prompt) => {
  firing = "prompt"
  for (const callback of admissions) await callback(event)
  attachments.push({ sessionID: event.sessionID, skills: (event.prompt.skills ?? []).map((skill) => skill.id) })
}
// A compaction's context holding a skill's activation, in the shape the host builds: the skill it
// loaded is a message as long as the session holds the skill — a `skill` tool call in the
// assistant's parts and a tool result carrying the skill's `<skill_content name="…">` body — cut
// here to the result, where the name stands. No message arrives as the stored `SessionMessage.Skill`
// kind: the host has translated the context into provider request messages
// (`@opencode/schema/dist/session-message.d.ts:540-554` gives the stored shape; observed at 2.4.2,
// `.devpro-temp/b2-probe/README.md`).
const skillActivation = (name: string) =>
  message({
    role: "tool",
    content: [
      {
        type: "tool-result",
        id: brand<"ToolCall.ID">("call_skill"),
        name: "skill",
        result: { type: "text", value: `<skill_content name="${name}">\n# Skill: ${name}\n</skill_content>` },
      },
    ],
  })
// The compaction hook's request for a session: the messages, and the fields a request carries that
// the entry does not read.
const compactionRequest = (sessionID: string, messages: SessionCompaction["messages"]): Compact => ({
  sessionID: brand(sessionID),
  model: { providerID: brand("omlx"), id: brand("test") },
  system: [],
  messages,
  options: {},
  agent: brand("build"),
  tools: {},
})
// A prompt as the host admits one: the session, and the draft the hook mutates.
const admitted = (sessionID: string, skills: { id: string }[]): Prompt => {
  const draft = { text: "what's next?", skills: skills.map(({ id }) => ({ id: brand(id) })) }
  return {
    sessionID: brand(sessionID),
    messageID: brand(`msg_${sessionID}`),
    prompt: draft as unknown as SessionPrompt["prompt"],
    delivery: brand("queue"),
  }
}
await fireTool({ tool: "subagent", sessionID: PARENT, status: "completed" })
await fireTool({ tool: "shell", sessionID: PARENT, status: "completed" })
await fireTool({ tool: "subagent", sessionID: PARENT, status: "error" })
await fireIdle({ sessionID: brand(CHILD), background: [] })
await fireIdle({
  sessionID: brand(CHILD),
  background: [background({ kind: "shell", sessionID: brand(CHILD), shellID: brand("sh_1"), command: "sleep 60" })],
})
await fireIdle({ sessionID: brand(PARENT), background: [] })

// The compaction surface, driven from the input so a test states what each session's context held,
// and the prompts admitted after it. Each input entry is one compaction of the primary session's
// context — the host builds the request, then the compacted session's next prompt is admitted, the
// exchange the reload's attachment rides. A prompt's own skills are the operator's, as the input
// states them. The primary session is a compaction's likeliest target, and the reminder, which
// reads only a session with a parent, is silent on it: the synthetic records above are the
// reminder's own.
const compactions = [0, 1].map((i) => input.compactions[i]?.messages ?? [])
for (const [index, messages] of compactions.entries()) {
  await fireCompaction(compactionRequest(PRIMARY, messages))
  const own = (input.prompts[index]?.skills ?? []).map((id) => ({ id }))
  await firePrompt(admitted(PRIMARY, own))
}
// A session whose Agents file names the skill and whose context holds no activation: its compaction
// carries no message with the skill's tool call, but its next prompt is the marker's likeliest false
// positive. The runner fires that compaction and that prompt after the input's; the Agents file is
// whatever the project's AGENTS.md holds, with each `skillLoads` entry's body appended as plain text
// the way a file's text lands in a context — no activation message beside it.
const agentsFile = (project: string): SessionCompaction["messages"] => {
  let text: string
  try {
    text = readFileSync(join(project, "AGENTS.md"), "utf8")
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code !== "ENOENT") throw err
    text = ""
  }
  const loads = (input.skillLoads ?? []).map(({ name, path }) =>
    readFileSync(path, "utf8").replace(/^(?:<!--.*-->\n)+(?:\n)?/, "").replace(/^/, `# Skill: ${name}\n\n`),
  )
  if (text === "" && loads.length === 0) return []
  return [message({ role: "system", content: [{ type: "text", text: [text, ...loads].join("\n\n") }] })]
}
await fireCompaction(compactionRequest(SKILL_QUESTIONED, agentsFile(input.project)))
await firePrompt(admitted(SKILL_QUESTIONED, []))
// The prompts the input asks for beyond the compactions', each on the session it names: a prompt of
// a session the marker never recorded, or a second one on a session whose marker a prompt has spent.
for (const extra of input.prompts.slice(compactions.length)) {
  await firePrompt(admitted(extra.sessionID, extra.skills.map((id) => ({ id }))))
}

await cleanup()
console.log(JSON.stringify({ id: plugin.id, hooks, sessionHooks, states, prompts, synthetics, attachments, log }))
