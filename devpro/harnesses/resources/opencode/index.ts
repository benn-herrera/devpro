// !INSTALLED! from devpro/harnesses/resources/opencode/index.ts — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
//
// It is written for opencode (floor 2.3.0): the entry of one plugin the devpro project ships, the
// directory holding this file. Registers the plugin's agents, commands, skills and MCP servers from
// registry.json and the Markdown bodies it lists, re-reads them whenever anything in this directory
// changes, runs the guardrail beside it where one is installed, reminds a parent session to update
// the active plan's status table when it dispatches a subagent and when that subagent's session
// finishes, and re-activates the development skill on the next prompt of a session the host has
// compacted where that session's context held it.
//
// The floor is 2.3.0, where the `subagent` call stops defaulting to the foreground: from it the call
// returns at once and the child runs in the background, so `execute.after`'s return is the dispatch
// moment rather than a nudge behind the idle that reports the child's completion. The skill's reload
// stands on a surface read from the host's published declarations — the `prompt` and `compaction`
// events of `SessionHooks`, which the pinned 2.4.1 declares — and no path here checks the host's
// version: the hooks register on every install.

import { Plugin } from "@opencode/plugin"
import type { SessionRequestMessage } from "@opencode/plugin/promise/session"
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

// What a registry entry becomes once its body is read: the entry, and the text `readBody` returned.
type Bodied<E extends Entry> = { entry: E; body: string }

const here = dirname(fileURLToPath(import.meta.url))
const registryPath = join(here, "registry.json")
const guardrailPath = join(here, "guardrail.ts")
const profilerPath = join(here, "profiler.ts")

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

// The development skill's reload: the host's compaction replaces the session's context with a
// summary, which drops the skill's text, and no declared hook fires when the compacted context
// resumes. The one the host declares for a compaction, `compaction`, runs before its request; the
// event after it that can carry an activation is the session's next `prompt`, the admission the
// host resolves a prompt's attachments at. So the compaction's hook reads the skill's name off its
// pre-compaction context and records the session there, and that prompt attaches the skill. The
// marker is a set of session ids, added at a compaction and removed by the prompt that reads it, so
// a session compacted twice is reloaded twice; the name is the marker's text because the host's
// request messages carry an activation as a `skill` tool call and its `<skill_content name="…">`
// result, not as a skill-kind message, so a context holding the name only through the Agents file's
// mention of it marks too.
const skillName = "devpro-development"

// The marker's text, the skill's name without the invocation's `@`: a skill message nests its body
// under a `content` part, so a JSON-escaped copy of the request would not hold the name itself.
const skillMark = skillName

// Whether a compaction request's context still holds a skill's activation. The host records an
// activation as a `SessionMessage.Skill` whose body is a plain `text` field
// (`@opencode/schema/dist/session-message.d.ts:540-554`, no `content` part), but the messages a
// compaction's hook gets are already provider request messages, and no skill message survives into
// them as that kind: observed at 2.4.2, the activation arrives as a `skill` tool call and its
// `tool-result`, whose `<skill_content name="…">` header carries the skill's name
// (`.devpro-temp/b2-probe/README.md`).
function holdsInvocation(text: string): boolean {
  return text.includes(skillMark)
}

// The texts a compaction request's message holds: each part's `text`, and a tool result's own text
// value, which is where an executed tool's output — the skill's body among them — is carried.
function textOf(message: SessionRequestMessage): string[] {
  return message.content.flatMap((part) => {
    const texts: string[] = []
    if ("text" in part && typeof part.text === "string") texts.push(part.text)
    if ("result" in part) {
      const result = part.result as { type?: unknown; value?: unknown }
      if (result.type === "text" && typeof result.value === "string") texts.push(result.value)
    }
    return texts
  })
}

// The reminder's sentence, byte for byte what claude's state-table-reminder.sh emits, and the gate
// that opens it — the plan file or the diced tree, not a design or nothing — are both held to the
// recorded injections in tests/test_opencode_entry.py. A synthetic message is context, as a hook's
// additionalContext is, so it states the reminder as what it is.
const reminder =
  "Automated reminder: keep the ACTIVE_PLAN state table up to date."

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
  agents: Bodied<AgentEntry>[]
  commands: Entry[]
  skills: Bodied<Entry>[]
  mcp: [string, unknown][]
}

// readBodies reads every entry's body, keeping the entries whose body could be read.
const readBodies = async <E extends Entry>(entries: E[]): Promise<Bodied<E>[]> => {
  const read = await Promise.all(entries.map(async (entry) => ({ entry, body: await readBody(entry.file) })))
  return read.filter((bodied): bodied is Bodied<E> => bodied.body !== undefined)
}

// readPlugin reads the registry and the body of every agent and skill it lists, keeping what it could
// read. A command's body is read when the command runs.
async function readPlugin(): Promise<Held> {
  const registry = await readRegistry()
  if (!registry) return { agents: [], commands: [], skills: [], mcp: [] }
  return {
    agents: await readBodies(registry.agents),
    commands: registry.commands,
    skills: await readBodies(registry.skills),
    mcp: Object.entries(registry.mcp),
  }
}

// The plugin context is the host's own, so every use below is checked against the host's published
// declarations, installed at `package.json`'s pin. The opened directory is not the project root: the
// plan stands at the checkout root, which is `project.directory`. A command's body is read when the
// command runs, so
// its invocations and prompts are the host's too.
type Context = Parameters<Parameters<typeof Plugin.define>[0]["setup"]>[0]

export default Plugin.define({
  // opencode takes the id before setup runs, so it is read synchronously; setup's read logs a failure.
  id: pluginId(),
  async setup(ctx: Context) {
    // The guardrail stands beside the entry at user level as in a project, and the entry runs it where
    // it is there.
    if (existsSync(guardrailPath)) await (await import(guardrailPath)).default.setup(ctx)
    // Nor does it ship the capture, which writes its records into the project's `.devpro-temp/`.
    if (existsSync(profilerPath)) await (await import(profilerPath)).default.setup(ctx)

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

    // The development skill's reload. A compaction records the session where the context it is about
    // to replace held the skill, and sets no `result`, so the host still authors the summary. The
    // session's next prompt then carries the skill among its `skills`, the host's own attachment
    // path, so the host activates it with that exchange, its text in the same request. The marker is
    // spent by that prompt, and a second compaction records the session again, so a session compacted
    // twice is reloaded twice.
    const reloaded = new Set<string>()
    await ctx.session.hook("prompt", async (prompt) => {
      if (!reloaded.delete(prompt.sessionID)) return
      // The skill's id is read from the domain as the prompt comes in, never assumed: the domain is
      // where the transform above put the skill, and its entry is the one the host activates.
      const listed = (await ctx.skill.list()).data.find((skill) => String(skill.name) === skillName)
      if (listed === undefined) {
        log(`no skill the plugin lists is named ${skillName}`, "nothing to activate")
        return
      }
      // The prompt's own list is kept. The brands the host puts on a skill's id are made from its
      // strings, and no maker stands in the published declarations this file is checked against, so the
      // id the attachment carries is the string the domain lists for the skill.
      const id = String(listed.id)
      const attached = prompt.prompt.skills ?? []
      if (attached.some((skill) => String(skill.id) === id)) return
      prompt.prompt.skills = [...attached, { id } as { id: NonNullable<typeof attached[number]>["id"] }]
    })
    await ctx.session.hook("compaction", (compaction) => {
      if (!compaction.messages.some((message) => textOf(message).some(holdsInvocation))) return
      reloaded.add(compaction.sessionID)
    })

    // Every callback reads `held`, which only setup and the watcher replace: a callback that threw
    // would disable this plugin module's whole registration group.
    let held = await readPlugin()
    await ctx.agent.transform((editor) => {
      for (const { entry, body } of held.agents) {
        editor.update(entry.id, (agent) => {
          agent.system = body
          if (entry.description !== undefined) agent.description = entry.description
          agent.mode = entry.mode
          if (entry.hidden !== undefined) agent.hidden = entry.hidden
          if (entry.model !== undefined) agent.model = entry.model as NonNullable<typeof agent.model>
          if (entry.color !== undefined) agent.color = entry.color
          for (const [key, effect] of Object.entries(entry.permission ?? {})) {
            agent.permissions.push({ action: key, resource: "*", effect })
          }
        })
      }
    })
    await ctx.skill.transform((editor) => {
      for (const { entry, body } of held.skills) {
        // The host brands a skill's id, name and path, and its published declarations export no maker
        // for those brands: the strings handed over are the registry's own.
        editor.add({
          id: entry.id,
          name: entry.id,
          ...(entry.description === undefined ? {} : { description: entry.description }),
          path: join(here, entry.file),
          content: body,
        } as Parameters<typeof editor.add>[0])
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
      for (const [name, config] of held.mcp) {
        // The registry holds each server's config as JSON the harness rendered; the host names the
        // shape a server's config takes, which JSON cannot state.
        editor.set(name, config as Parameters<typeof editor.set>[1])
      }
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
