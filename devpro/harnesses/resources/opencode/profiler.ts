// !INSTALLED! from devpro/harnesses/resources/opencode/profiler.ts — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
//
// opencode 2.3.2 plugin module (floor 2.3.0)
// The activity capture: every tool call of a session, with its duration, arguments, result and
// outcome, and the session's idle marks, appended to the project's
// `.devpro-temp/opencode-profiler/<session-id>.jsonl` — the store `hp.py`'s tree and page render beside
// the claude sessions'. The record's fields and their meanings are claude's `hp.py`'s, because the same
// render reads both, and the masking is its masking: this file is that record rebuilt against
// opencode's hook surface, which reports different things than claude's hooks do.
//
// `execute.before` carries no result, so it is where a call's start is taken; `execute.after` is where
// the record is written. A capture that fails raises nothing out of a hook and says nothing.

import { Plugin } from "@opencode/plugin"
import {
  appendFileSync,
  closeSync,
  fstatSync,
  mkdirSync,
  openSync,
  readFileSync,
  readSync,
  renameSync,
  truncateSync,
} from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

// The slice of the plugin context this module uses, declared as the entry declares its own.
type ToolInput = { [arg: string]: unknown }
// The call's pairing key: `execute.before` reports it and `execute.after` repeats it.
type Pairing = { tool: string; sessionID: string; agent?: string; messageID?: string; id: string; input: ToolInput }
// `execute.before` carries no result and no status; `execute.after` carries one or the other.
type Started = Pairing
type Finished = Pairing & { status: "completed" | "error"; result?: unknown; error?: string }
type Idle = { sessionID: string; background: readonly unknown[] }

// The callback's type is written literally at each `hook`, not through a generic alias: TypeScript
// infers an unannotated arrow's parameter from a literal callback type and not, in this position, from
// one reached through an alias.
type Context = {
  // The opened directory is not the project root: the store sits at the checkout root.
  location: { project: { directory: string } }
  tool: {
    hook(name: "execute.before", callback: (event: Started) => Promise<void> | void): Promise<unknown>
    hook(name: "execute.after", callback: (event: Finished) => Promise<void> | void): Promise<unknown>
  }
  session: {
    hook(name: "experimental.idle", callback: (event: Idle) => Promise<void> | void): Promise<unknown>
  }
}
const here = dirname(fileURLToPath(import.meta.url))

function pluginId(): string {
  try {
    return (JSON.parse(readFileSync(join(here, "registry.json"), "utf8")) as { plugin: string }).plugin
  } catch {
    // The registry is written by the install beside this file; a user-level install, which copies no
    // capture, never loads this module. The literal keeps a plugin id well-formed where it is missing.
    return "profiler-plugin"
  }
}

// hp.py's limits and spellings, so a record from either harness renders the same way.
const SCHEMA_VERSION = 2
const TRACE_DIR = join(".devpro-temp", "opencode-profiler")
const NAME_LIMIT = 80
const ARGS_LIMIT = 200
const RESULT_LIMIT = 300
const LINE_LIMIT = 4096
const ELLIPSIS = "…"
const NEWLINE = " ⏎ "
const DEFAULT_AGENT = "general-purpose"

// ---------- hp.py's text helpers ----------

const SECRETS: [RegExp, string][] = [
  [/\b(Bearer|Basic|token)\s+[\w.~+/=-]{8,}/gi, "$1 [redacted]"],
  [
    /\b((?:api[_-]?key|access[_-]?token|token|secret|password|passwd|authorization)["']?\s*[:=]\s*["']?)[^\s"'&]+/gi,
    "$1[redacted]",
  ],
  [/\b(?:gh[pousr]_|github_pat_|sk-|xox[abp]-)[\w-]{10,}/g, "[redacted]"],
]
const SECRET_KEY = /token|secret|password|api_?key|authorization|credential/i
// JSON.stringify escapes the line terminators JSON leaves raw; this does not, so a record carrying
// one stays one line and python reads it back as the same JSON.
const LINE_TERMINATOR: [string, string][] = [
  [String.fromCharCode(0x2028), "\\u2028"],
  [String.fromCharCode(0x2029), "\\u2029"],
]

// compact is a value as JSON: no spaces, and no line break left raw.
function compact(value: unknown): string {
  const text = JSON.stringify(value) ?? "null"
  return LINE_TERMINATOR.reduce((line, [raw, escaped]) => line.split(raw).join(escaped), text)
}

// mask is text with what looks like a credential replaced.
function mask(text: string): string {
  return SECRETS.reduce((masked, [pattern, replacement]) => masked.replace(pattern, replacement), text)
}

// clip is text cut to limit characters, its last one an ellipsis.
function clip(text: string, limit: number): string {
  return text.length <= limit ? text : text.slice(0, Math.max(limit - 1, 0)) + ELLIPSIS
}

// oneLine is text's non-blank lines, trimmed and joined so a record stays on one line.
function oneLine(text: string): string {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .join(NEWLINE)
}

function firstLine(text: string): string {
  const line = text.split(/\r?\n/).find((candidate) => candidate.trim())
  return line === undefined ? "" : line.trim()
}

// valueText is a tool's text, whatever the tool sent: input's string, an error's message, else the
// value as JSON.
function valueText(value: unknown): string {
  if (typeof value === "string") return value
  if (typeof value === "number" || typeof value === "boolean" || value === null) return String(value)
  return compact(value)
}

// ---------- the record's values ----------

// Remarks the model writes to itself, which opencode reports as tool calls: they carry no result and
// are not activity, so they are not recorded.
const REMARKS = new Set(["todowrite", "todoread"])
// The tools that start a subagent context, and the tool hp.py records them as: the tree draws claude's
// `Agent` call by default, so opencode's `task` must carry that name to be drawn at all.
const SUBAGENT_TOOLS: Record<string, string> = { task: "Agent", subagent: "Agent" }
const KIND_ARGS: Record<string, string[]> = {
  task: ["subagent_type", "agent"],
  subagent: ["subagent_type", "agent"],
}
// hp.py's `Skill`: the name the tree draws by default, its arguments taken from `args`.
const SKILL = "Skill"

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}

// textFrom is hp.py's `.get()` read: a string value's text, and nothing for any other.
function textFrom(value: unknown): string {
  return typeof value === "string" ? value : ""
}

// nameOf, argsOf and resultOf are hp.py's three, over opencode's tools: a skill's name and args, a
// subagent's kind and brief, a shell command's head and its text. Any other tool's name is its own
// (hp's MCP suffix rule apart), its args its input as JSON.
function nameOf(tool: string, input: Record<string, unknown>): string | undefined {
  const name =
    tool in SUBAGENT_TOOLS
      ? textFrom(input.subagent_type) || DEFAULT_AGENT
      : tool === "bash" || tool === "shell"
        ? firstLine(textFrom(input.command)).replace(/^cd\s+("[^"]*"|'[^']*'|\S+)\s+&&\s+/, "")
        : textFrom(tool === "skill" ? input.args : undefined) || tool.split("__").pop() || tool
  return clip(mask(name), NAME_LIMIT) || undefined
}

function argsOf(tool: string, input: Record<string, unknown>): string | undefined {
  // hp.py's `Agent` brief, which is a string even where it is empty.
  if (tool in SUBAGENT_TOOLS) {
    const brief = [textFrom(input.description), firstLine(textFrom(input.prompt))].filter(Boolean).join(": ")
    return clip(mask(oneLine(brief)), ARGS_LIMIT) || undefined
  }
  const given = tool === "bash" || tool === "shell" ? input.command : tool === "skill" ? input.args : undefined
  const safe =
    given === undefined || given === null
      ? Object.keys(input).length
        ? compact(
            Object.fromEntries(
              Object.entries(input).map(([key, value]) => [key, SECRET_KEY.test(key) ? "[redacted]" : value]),
            ),
          )
        : ""
      : valueText(given)
  return clip(mask(oneLine(safe)), ARGS_LIMIT) || undefined
}

// resultOf is what the call returned, or, on a failed call, why: hp.py's result is the error's text
// where the response carries none.
function resultOf(call: Finished): string | undefined {
  const textOf =
    call.status === "completed"
      ? call.result === undefined || call.result === null
        ? ""
        : valueText(call.result)
      : (call.error ?? "")
  return clip(mask(firstLine(textOf)), RESULT_LIMIT) || undefined
}

// childAgentTypeOf is the kind of subagent a parent call started: hp.py's `Agent` call names its own
// input's subagent type, opencode's `task` names its `agent`.
function childAgentTypeOf(tool: string, input: Record<string, unknown>): string | undefined {
  for (const arg of KIND_ARGS[tool] ?? []) {
    const value = input[arg]
    if (typeof value === "string" && value) return value
  }
  return undefined
}

// The record's fields are hp.py's `build_record` / `build_event_record` in their schema order, every
// one present so a reader never meets a missing key. A field a hook supplies no value for takes the
// field's empty rendering: `null` where hp.py leaves the key out, `false` where the tree reads
// truthiness, zero for a duration the tree formats as a number.
type CallRecord = {
  v: number
  harness: string
  at: string
  session: string
  agent_id: string | null
  agent_type: string | null
  tool_use_id: string | null
  tool: string
  name: string | null
  duration_ms: number
  ok: boolean
  child_agent_id: string | null
  child_agent_type: string | null
  background: boolean
  child_spend: null
  tokens: number | null
  context_tokens: null
  branch: null
  args: string | null
  result: string | null
}

function callRecord(call: Finished, start: number, end: number): CallRecord {
  const raw = call.tool
  const input = isRecord(call.input) ? call.input : {}
  const subagent = raw in SUBAGENT_TOOLS
  const tool = SUBAGENT_TOOLS[raw] ?? (raw === "skill" ? SKILL : raw)
  return {
    v: SCHEMA_VERSION,
    harness: "opencode",
    at: new Date(end).toISOString(),
    session: call.sessionID,
    // hp.py's `agent_id` keys the subagent context a call ran in, not the agent's name; opencode reports
    // that name in `agent`, and every call it hooks here runs in the session's own context.
    agent_id: null,
    agent_type: null,
    tool_use_id: null,
    tool,
    name: nameOf(raw, input) ?? (subagent ? DEFAULT_AGENT : tool),
    duration_ms: end - start,
    ok: call.status === "completed",
    // A subagent call starts its child's context; opencode names no id for the call, so the store holds
    // none to key that context by.
    child_agent_id: null,
    child_agent_type: subagent ? (childAgentTypeOf(raw, input) ?? DEFAULT_AGENT) : null,
    background: false,
    child_spend: null,
    tokens: null,
    context_tokens: null,
    branch: null,
    args: argsOf(raw, input) ?? null,
    result: resultOf(call) ?? null,
  }
}

// eventRecord marks the session's lifecycle, as hp.py's record for a SessionStart does: an event and
// no tool, so the tree draws it as a marker. `transcript` names claude's transcript file, which opencode
// has none of.
function eventRecord(session: string, event: string, at: number): Record<string, unknown> {
  return {
    v: SCHEMA_VERSION,
    harness: "opencode",
    at: new Date(at).toISOString(),
    session,
    event,
    trigger: null,
    source: null,
    context_tokens: null,
    transcript: null,
  }
}

// hp.py's `serialize`: the record's JSON line, `result` and then `args` giving way until it fits.
function serialize(record: Record<string, unknown>): string {
  let line = compact(record)
  const fitted = { ...record }
  for (const key of ["result", "args"]) {
    while (Buffer.byteLength(line, "utf8") > LINE_LIMIT && fitted[key]) {
      const shorter = Math.floor(String(fitted[key]).length / 2)
      if (shorter < 1) delete fitted[key]
      else fitted[key] = clip(String(fitted[key]), shorter)
      line = compact(fitted)
    }
  }
  return line
}

// sessionFile is the trace for one session, its id made path-safe as hp.py makes it.
function sessionFile(root: string, session: string): string {
  return join(root, TRACE_DIR, `${session.replace(/[^\w.-]/g, "_")}.jsonl`)
}

// ---------- the capture ----------

// The start of every call in flight, by its pairing key. One plugin module serves one session's
// hooks per opencode process, but a key is only unique within a call, so the session id joins it.
const started = new Map<string, number>()

function keyOf(call: Started): string {
  return `${String(call.sessionID)}.${String(call.id)}`
}

// TORN_TAIL_BYTES bounds the read that finds a torn tail: a record is at most LINE_LIMIT bytes, so a
// longer read cannot change what the last line is.
const TORN_TAIL_BYTES = 64 * 1024

// dropTornTail refuses to append onto a line a killed process left unusable, which would fuse two
// records and lose both. The file is read from its tail, not whole: an append happens on every call.
// The torn line moves aside and the file keeps the lines before it, or nothing at all happens where the
// file ends clean.
function dropTornTail(file: string): void {
  let handle: number
  try {
    handle = openSync(file, "r")
  } catch {
    return
  }
  try {
    const size = fstatSync(handle).size
    if (size === 0) return
    const length = Math.min(size, TORN_TAIL_BYTES)
    const buffer = Buffer.alloc(length)
    readSync(handle, buffer, 0, length, size - length)
    // The last newline is found in the bytes, not in a decoded string: a character index in a multibyte
    // tail is not a byte offset.
    const last = buffer.lastIndexOf(0x0a)
    const boundary = last >= 0 ? size - length + last + 1 : 0
    if (boundary === size) return
    if (boundary === 0) renameSync(file, `${file}.torn-${Date.now()}`)
    else truncateSync(file, boundary)
  } finally {
    closeSync(handle)
  }
}

// append writes one record as one line: one small append per record keeps concurrent hooks from
// interleaving.
function append(root: string, session: unknown, record: Record<string, unknown>): void {
  if (session === undefined || session === null || session === "") return
  const file = sessionFile(root, String(session))
  mkdirSync(dirname(file), { recursive: true })
  dropTornTail(file)
  appendFileSync(file, serialize(record) + "\n", "utf8")
}

// silently runs a capture step: a capture that fails raises nothing out of the hook it runs in.
function silently(step: () => void): void {
  try {
    step()
  } catch {}
}

export default Plugin.define({
  // The entry's own mechanism: the registry's plugin name where the registry is readable beside this
  // file, and this module's literal name where it is not.
  id: pluginId(),
  async setup(ctx: Context) {
    const root = ctx.location.project.directory
    await ctx.tool.hook("execute.before", (call) => {
      silently(() => {
        if (REMARKS.has(call.tool)) return
        started.set(keyOf(call), Date.now())
      })
    })
    await ctx.tool.hook("execute.after", (call) => {
      silently(() => {
        if (REMARKS.has(call.tool)) return
        const key = keyOf(call)
        const end = Date.now()
        // A call with no start recorded — one already running when the plugin loaded — is timed as its
        // end alone rather than left out.
        const start = started.get(key) ?? end
        started.delete(key)
        append(root, call.sessionID, callRecord(call, start, end))
      })
    })
    await ctx.session.hook("experimental.idle", (idle) => {
      silently(() => append(root, idle.sessionID, eventRecord(idle.sessionID, "experimental.idle", Date.now())))
    })
  },
})
