// !INSTALLED! from devpro/harnesses/resources/opencode/index.ts — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
//
// Written for opencode 2.3.2 (floor 2.3.0): the entry of one plugin the devpro project ships, the
// directory holding this file. Registers the plugin's agents, commands, skills and MCP servers from
// registry.json and the Markdown bodies it lists, re-reads them whenever anything in this directory
// changes, runs the guardrail beside it where one is installed, and reminds a parent session to
// update the active plan's status table when it dispatches a subagent and when that subagent's
// session finishes.
//
// The floor is a behavioral one, not an API one: every API used here exists at 2.2.6, but there the
// `subagent` tool defaults to the foreground, so `execute.after` fires at the child's completion,
// behind the idle hook — a parent gets two completion nudges and none at the dispatch. From 2.3.0
// the call returns at once and the child runs in the background, which makes the call's return the
// dispatch moment.

import { Plugin } from "@opencode/plugin"
import { existsSync, readFileSync, statSync, watch } from "node:fs"
import { readFile } from "node:fs/promises"
import { basename, dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

// registry.json as devpro's opencode harness renders it. Only that renderer writes it, so it is read
// as this shape without validation.
type Effect = "allow" | "deny"
type Entry = { id: string; file: string; description?: string }
type AgentEntry = Entry & {
  mode: "subagent"
  hidden?: boolean
  model?: { providerID: string; id: string }
  color?: string
  permission?: Record<string, Effect>
}
type Registry = {
  plugin: string
  agents: AgentEntry[]
  commands: Entry[]
  skills: Entry[]
  mcp: Record<string, unknown>
}

// The slice of opencode's plugin context this entry uses.
type Rule = { action: string; resource: string; effect: Effect }
type AgentInfo = {
  system?: string
  description?: string
  mode: string
  hidden: boolean
  model?: { providerID: string; id: string }
  color?: string
  permissions: Rule[]
}
type Prompt = { text: string }
type Invocation = { sessionID: string; prompt: Prompt; delivery: unknown }
// A finished tool call, as `execute.after` reports one, and a session that has gone idle, with the
// work still running on it.
type ToolCall = { tool: string; sessionID: string; status: "completed" | "error" }
type Idle = { sessionID: string; background: readonly unknown[] }
type SessionInfo = { parentID?: string }
type Hook<Event> = (callback: (event: Event) => Promise<void> | void) => Promise<unknown>
type Domain<Editor> = { transform(callback: (editor: Editor) => void): Promise<unknown>; reload(): Promise<void> }
type Context = {
  // The opened directory is not the project root: the plan stands at the checkout root, which is
  // `project.directory`.
  location: { project: { directory: string } }
  agent: Domain<{ update(id: string, update: (agent: AgentInfo) => void): void }>
  skill: Domain<{ add(skill: { id: string; name: string; description?: string; path: string; content: string }): void }>
  command: Domain<{
    add(command: { name: string; description?: string; execute(input: Invocation): Promise<void> }): void
  }>
  mcp: Domain<{ set(name: string, config: unknown): void }>
  tool: { hook(name: "execute.after", callback: Hook<ToolCall>): Promise<unknown> }
  session: {
    prompt(input: Prompt & { sessionID: string; delivery: unknown }): Promise<unknown>
    hook(name: "experimental.idle", callback: Hook<Idle>): Promise<unknown>
    get(input: { sessionID: string }): Promise<SessionInfo>
    synthetic(input: { sessionID: string; text: string; delivery: "steer" | "queue" }): Promise<unknown>
  }
}

const here = dirname(fileURLToPath(import.meta.url))
const registryPath = join(here, "registry.json")
const guardrailPath = join(here, "guardrail.ts")

function log(message: string, err: unknown): void {
  console.error(`devpro: plugin ${basename(here)}: ${message}:`, err)
}

// stripBanner removes a body's leading comment lines and the blank line after them.
function stripBanner(text: string): string {
  return text.replace(/^(?:<!--.*-->\n)+\n?/, "")
}

// planStanding reports whether the project root holds a plan — the `ACTIVE_PLAN.md` file, or where
// the plan was diced, the `ACTIVE_PLAN/` tree — the reminder's gate. Each is the kind claude's gate
// reads it as: the `.md` name a file, not a directory of that name, the tree a directory.
function planStanding(root: string): boolean {
  const file = join(root, "ACTIVE_PLAN.md")
  const tree = join(root, "ACTIVE_PLAN")
  return (existsSync(file) && statSync(file).isFile()) || (existsSync(tree) && statSync(tree).isDirectory())
}

// The reminder's sentence, byte for byte what claude's state-table-reminder.sh emits, and the gate
// that opens it — the plan file or the diced tree, not a design or nothing — are both held to the
// recorded injections in tests/test_opencode_entry.py. A synthetic message is context, as a hook's
// additionalContext is, so it states the reminder as what it is.
const reminder =
  "Reminder: keep the ACTIVE_PLAN state table up to date."

async function readRegistry(): Promise<Registry | undefined> {
  try {
    return JSON.parse(await readFile(registryPath, "utf8"))
  } catch (err) {
    log(`cannot read ${registryPath}`, err)
    return undefined
  }
}

function pluginId(): string {
  try {
    return (JSON.parse(readFileSync(registryPath, "utf8")) as Registry).plugin
  } catch {
    return basename(here)
  }
}

async function readBody(file: string): Promise<string | undefined> {
  try {
    return stripBanner(await readFile(join(here, file), "utf8"))
  } catch (err) {
    log(`cannot read ${file}`, err)
    return undefined
  }
}

type Held = {
  agents: (AgentEntry & { body: string })[]
  commands: Entry[]
  skills: (Entry & { body: string })[]
  mcp: [string, unknown][]
}

// readPlugin reads the registry and the body of every agent and skill it lists, keeping what it could
// read. A command's body is read when the command runs.
async function readPlugin(): Promise<Held> {
  const registry = await readRegistry()
  if (!registry) return { agents: [], commands: [], skills: [], mcp: [] }
  const withBodies = async <E extends Entry>(entries: E[]) =>
    (await Promise.all(entries.map(async (entry) => ({ ...entry, body: await readBody(entry.file) })))).filter(
      (entry): entry is E & { body: string } => entry.body !== undefined,
    )
  return {
    agents: await withBodies(registry.agents),
    commands: registry.commands,
    skills: await withBodies(registry.skills),
    mcp: Object.entries(registry.mcp),
  }
}

export default Plugin.define({
  // opencode takes the id before setup runs, so it is read synchronously; setup's read logs a failure.
  id: pluginId(),
  async setup(ctx: Context) {
    // A user-level install ships no guardrail.
    if (existsSync(guardrailPath)) await (await import(guardrailPath)).default.setup(ctx)

    // The reminder is registered on every install: the gate paths at the project root are read when
    // a hook fires, and a project holding none of them pays nothing. An injection is one model call.
    const injectReminder = async (sessionID: string) => {
      if (!planStanding(ctx.location.project.directory)) return
      try {
        await ctx.session.synthetic({
          sessionID,
          text: reminder,
          // A synthetic message steers by default: passed here because the reminder belongs to the
          // execution that just ran, which is where the parent reads it.
          delivery: "steer",
        })
      } catch (err) {
        log(`cannot remind the session ${sessionID}`, err)
      }
    }
    // A subagent call returns as soon as its child session starts — always, from 2.3.0 — so a
    // completed one is the dispatch moment, and the call's session is the parent that holds the
    // work; a failed or denied call dispatched nothing.
    await ctx.tool.hook("execute.after", (call) => {
      if (call.tool !== "subagent" || call.status !== "completed") return
      return injectReminder(call.sessionID)
    })
    // A session that has gone idle is a subagent's completion, and its parent is the one to remind —
    // unless work still runs on it: a shell or a grandchild it launched wakes it and fires this hook
    // again, and that later idle is the completion.
    await ctx.session.hook("experimental.idle", async (idle) => {
      if (idle.background.length > 0) return
      const session = await ctx.session.get({ sessionID: idle.sessionID }).catch((err: unknown) => {
        log(`cannot read the session ${idle.sessionID}`, err)
        return undefined
      })
      if (session?.parentID === undefined) return
      await injectReminder(session.parentID)
    })

    // Every callback reads `held`, which only setup and the watcher replace: a callback that threw
    // would disable this plugin module's whole registration group.
    let held = await readPlugin()
    await ctx.agent.transform((editor) => {
      for (const entry of held.agents) {
        editor.update(entry.id, (agent) => {
          agent.system = entry.body
          if (entry.description !== undefined) agent.description = entry.description
          agent.mode = entry.mode
          if (entry.hidden !== undefined) agent.hidden = entry.hidden
          if (entry.model) agent.model = entry.model
          if (entry.color !== undefined) agent.color = entry.color
          for (const [key, effect] of Object.entries(entry.permission ?? {})) {
            agent.permissions.push({ action: key, resource: "*", effect })
          }
        })
      }
    })
    await ctx.skill.transform((editor) => {
      for (const entry of held.skills) {
        editor.add({
          id: entry.id,
          name: entry.id,
          ...(entry.description === undefined ? {} : { description: entry.description }),
          path: join(here, entry.file),
          content: entry.body,
        })
      }
    })
    await ctx.command.transform((editor) => {
      for (const entry of held.commands) {
        editor.add({
          name: entry.id,
          ...(entry.description === undefined ? {} : { description: entry.description }),
          async execute(input) {
            const raw = await readFile(join(here, entry.file), "utf8").catch((cause: unknown) => {
              throw new Error(`cannot read ${entry.file}`, { cause })
            })
            const body = stripBanner(raw).trimEnd()
            const text = input.prompt.text.trim()
            await ctx.session.prompt({
              ...input.prompt,
              sessionID: input.sessionID,
              text: text ? `${body}\n\n${text}` : body,
              delivery: input.delivery,
            })
          },
        })
      }
    })
    await ctx.mcp.transform((editor) => {
      for (const [name, config] of held.mcp) editor.set(name, config)
    })

    // A second transform would register beside the first, so a change re-reads the files and asks
    // opencode to re-run the transforms above. Refreshes run one at a time, so an older read never
    // replaces a newer one.
    let refreshing = Promise.resolve()
    let pending: ReturnType<typeof setTimeout> | undefined
    const refresh = () => {
      refreshing = refreshing
        .then(async () => {
          held = await readPlugin()
          await Promise.all([ctx.agent.reload(), ctx.skill.reload(), ctx.command.reload(), ctx.mcp.reload()])
        })
        .catch((err: unknown) => log("reload failed", err))
    }
    const watcher = watch(here, { recursive: true }, () => {
      clearTimeout(pending)
      pending = setTimeout(refresh, 100)
    })
    watcher.on("error", (err) => log("watch failed", err))

    return async () => {
      clearTimeout(pending)
      watcher.close()
      await refreshing
    }
  },
})
