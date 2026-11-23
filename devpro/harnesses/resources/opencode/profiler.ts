// !INSTALLED! from devpro/harnesses/resources/opencode/profiler.ts — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
//
// opencode 2.3.2 plugin module (floor 2.3.0)
// The activity capture: every tool call of a session, with its duration, arguments, result and
// outcome, and the session's idle marks, appended to the project's
// `.devpro-temp/.profiler-opencode/<session-id>.jsonl` — the store `devpro profiler tree` renders
// beside the claude sessions'. The record's fields and their meanings are `devpro/profiler/capture.py`'s,
// because the same render reads both, and the masking is its masking: this file is that record rebuilt
// against opencode's hook surface, which reports different things than claude's hooks do.
// The floor is behavioral: the child's session id, which the dispatch's tie to its child is read from,
// is `result.output.sessionID` on 2.3.2 and `result.metadata.sessionID` on 2.3.0, and the read covers both.
//
// `execute.before` carries no result, so it is where a call's start is taken; `execute.after` is where
// the record is written. A capture that fails raises nothing out of a hook and says nothing, save the
// store's own repair: an append onto a line a killed process left torn cuts that line off the file —
// truncating to the newline before it — and renames the whole file aside where it holds no newline.
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
import { basename, dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const here = dirname(fileURLToPath(import.meta.url))
const registryPath = join(here, "registry.json")

// The slice of the plugin context this module uses, declared as the entry declares its own.
type ToolInput = { [arg: string]: unknown }
// The call's pairing key: `execute.before` reports it and `execute.after` repeats it.
type Pairing = { tool: string; sessionID: string; agent?: string; messageID?: string; id: string; input: ToolInput }
// `execute.before` carries no result and no status; `execute.after` carries one or the other, and
// on a failed call its `error` is the host's `Tool.Error` object rather than a string.
type Started = Pairing
type Finished = Pairing & { status: "completed" | "error"; result?: unknown; error?: unknown }
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

// The module's id, as `guardrail.ts` and this file take it: the plugin's, read synchronously from
// `registry.json` because opencode takes an id before `setup` runs, and the install directory's name where
// the registry is unreadable.
function pluginId(): string {
  try {
    return (JSON.parse(readFileSync(registryPath, "utf8")) as { plugin: string }).plugin
  } catch {
    return basename(here)
  }
}

// `devpro/profiler/capture.py`'s limits and spellings, so a record from either harness renders the same way.
const SCHEMA_VERSION = 2
const TRACE_DIR = join(".devpro-temp", ".profiler-opencode")
const NAME_LIMIT = 80
const ARGS_LIMIT = 200
const RESULT_LIMIT = 300
const LINE_LIMIT = 4096
const ELLIPSIS = "…"
const NEWLINE = " ⏎ "
const DEFAULT_AGENT = "general-purpose"
// A start whose `execute.after` never fires — a denied or interrupted call — is dropped once its
// session has gone idle, and at the latest once this many starts are held.
const MAX_STARTED = 1024

// ---------- `devpro/profiler/values.py`'s text helpers ----------

const SECRETS: [RegExp, string][] = [
  [/\b(Bearer|Basic|token)\s+[\p{L}\p{N}_.~+/=-]{8,}/giu, "$1 [redacted]"],
  [
    /\b((?:api[_-]?key|access[_-]?token|token|secret|password|passwd|authorization)["']?\s*[:=]\s*["']?)[^\s"'&]+/giu,
    "$1[redacted]",
  ],
  [/(?<![\p{L}\p{N}_])(?:gh[pousr]_|github_pat_|sk-|xox[abp]-)[\p{L}\p{N}_-]{10,}/gu, "[redacted]"],
]
// `devpro/profiler/values.py` states the same three as `[\w]` with Unicode semantics; JavaScript's `\w` is ASCII, and the
// `\p{L}\p{N}` classes above are what make a credential holding a non-ASCII letter mask alike. The
// lookbehind is that `\w` boundary written for the same classes, since `\b` would not take them.
// `test_devpro_profiler.py` holds the two implementations to one sample list.
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

// clip is text cut to limit code points, its last one an ellipsis: `devpro/profiler/values.py`'s limit is a count of
// characters, and a UTF-16 index would cut an astral character in half.
function clip(text: string, limit: number): string {
  const points = [...text]
  return points.length <= limit ? text : points.slice(0, Math.max(limit - 1, 0)).join("") + ELLIPSIS
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

// errorText is a failed call's reason: the host reports a `Tool.Error` object carrying `.message`
// where a string spelling of it would be expected.
function errorText(error: unknown): string {
  if (typeof error === "string") return error
  return isRecord(error) ? textFrom(error.message) : ""
}

// ---------- the record's values ----------

// Remarks the model writes to itself, which opencode reports as tool calls: they carry no result and
// are not activity, so they are not recorded.
const REMARKS = new Set(["todowrite"])
// The tools that start a subagent context, and the tool the devpro profiler records them as: the tree draws claude's
// `Agent` call by default, so opencode's subagent dispatch must carry that name to be drawn at all.
// Both of the host's spellings are here: `task` is the name opencode 2.3.0's floor still uses, and
// `subagent` the one it is renamed to later in the 2.3 line.
const SUBAGENT_TOOLS: Record<string, string> = { task: "Agent", subagent: "Agent" }
const KIND_ARGS: Record<string, string[]> = {
  task: ["subagent_type", "agent"],
  subagent: ["subagent_type", "agent"],
}
// `devpro/profiler/capture.py`'s `Skill`: the name the tree draws by default, its name the host's skill id.
const SKILL = "Skill"

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}

// textFrom is the devpro profiler's `.get()` read: a string value's text, and nothing for any other.
function textFrom(value: unknown): string {
  return typeof value === "string" ? value : ""
}

// nameOf, argsOf and resultOf are `devpro/profiler/capture.py`'s three, over opencode's tools: a skill's name, a subagent's
// kind and brief, a shell command's head and its text. The host names a subagent dispatch by its
// `agent` and a skill call by its `id`; neither is a tool name, so neither falls through to the tool
// itself. Any other tool's name is its own (hp's MCP suffix rule apart), its args its input as JSON.
function nameOf(tool: string, input: Record<string, unknown>): string | undefined {
  const name =
    tool in SUBAGENT_TOOLS
      ? textFrom(input.agent) || textFrom(input.subagent_type) || DEFAULT_AGENT
      : tool === "bash" || tool === "shell"
        ? firstLine(textFrom(input.command)).replace(/^cd\s+("[^"]*"|'[^']*'|\S+)\s+&&\s+/, "")
        : textFrom(tool === "skill" ? input.id : undefined) || tool.split("__").pop() || tool
  return clip(mask(name), NAME_LIMIT) || undefined
}

function argsOf(tool: string, input: Record<string, unknown>): string | undefined {
  // `devpro/profiler/capture.py`'s `Agent` brief, which is a string even where it is empty.
  if (tool in SUBAGENT_TOOLS) {
    const brief = [textFrom(input.description), firstLine(textFrom(input.prompt))].filter(Boolean).join(": ")
    return clip(mask(oneLine(brief)), ARGS_LIMIT) || undefined
  }
  // A skill call is given nothing: its `id` is its name.
  const given = tool === "bash" || tool === "shell" ? input.command : undefined
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

// resultText is a completed call's text: the devpro profiler's `response_text` unwrapping — the `content` parts'
// text, then a string `output`, then `stdout` and `stderr` — and, where the result carries none of
// those, its `metadata` as JSON.
function resultText(result: unknown): string {
  if (!isRecord(result)) return valueText(result)
  const { content, output } = result
  if (Array.isArray(content)) {
    return content.map((part) => (isRecord(part) ? textFrom(part.text) : "")).join("\n")
  }
  if (typeof output === "string") return output
  const streams = [result.stdout, result.stderr].filter((value) => typeof value === "string")
  if (streams.length) return streams.join("\n")
  return result.metadata === undefined || result.metadata === null ? "" : valueText(result.metadata)
}

// resultOf is what the call returned, or, on a failed call, why: the devpro profiler's result is the error's text
// where the response carries none.
function resultOf(call: Finished): string | undefined {
  const textOf =
    call.status === "completed"
      ? call.result === undefined || call.result === null
        ? ""
        : resultText(call.result)
      : errorText(call.error)
  return clip(mask(firstLine(textOf)), RESULT_LIMIT) || undefined
}

// childSessionOf is the session a subagent call dispatched: the host's `result.output.sessionID` first,
// then opencode 2.3.0's `result.metadata.sessionID`, which the floor still covers, each read under the
// host's own string guard. Each opencode session owns its own trace file, so this id names the child's
// page and its row in the index, never a context in the parent's file.
// opencode 2.3.2 reports the dispatched child's session id in the output and 2.3.0 reported it in the
// metadata; a result carrying neither — a bare output string among them, and a result with none — is a
// valid no-child state, and the record keeps `null`.
function childSessionOf(call: Finished): string | undefined {
  const { output, metadata } = isRecord(call.result) ? call.result : {}
  const id = (isRecord(output) ? output.sessionID : undefined) ?? (isRecord(metadata) ? metadata.sessionID : undefined)
  return typeof id === "string" ? id : undefined
}

// childAgentTypeOf is the kind of subagent a parent call started, the response's `agentType` first as
// the devpro profiler reads it — where a forked child's `fork` appears — then the call's own input, opencode's `agent`.
// The two places here are the ones the host was observed reporting a kind in. The mirror of
// `childSessionOf`: a kind the host reports elsewhere — beside the child's session id in `output` —
// would record as the call's own input, and no live observation has shown it there.
function childAgentTypeOf(tool: string, input: Record<string, unknown>, call: Finished): string | undefined {
  const { result, metadata } = isRecord(call.result) ? call.result : {}
  const kind =
    (isRecord(result) ? textFrom(result.agentType) : "") ||
    (isRecord(metadata) ? textFrom(metadata.agentType) : "")
  if (kind) return kind
  for (const arg of KIND_ARGS[tool] ?? []) {
    const value = input[arg]
    if (typeof value === "string" && value) return value
  }
  return undefined
}

// The record's fields are `devpro/profiler/capture.py`'s `build_record` / `build_event_record` in their schema order, every
// one present so a reader never meets a missing key. A field a hook supplies no value for takes the
// field's empty rendering: `null` where the devpro profiler leaves the key out, `false` where the tree reads
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
    // the devpro profiler's `agent_id` keys the subagent context a call ran in, not the agent's name; opencode reports
    // that name in `agent`, and every call it hooks here runs in the session's own context.
    agent_id: null,
    agent_type: null,
    tool_use_id: null,
    tool,
    name: nameOf(raw, input) ?? (subagent ? DEFAULT_AGENT : tool),
    duration_ms: end - start,
    ok: call.status === "completed",
    // A subagent call starts its child's context, and the host names that child's session in the
    // result's output, or in 2.3.0's metadata: the id goes in the slot the render groups children by.
    child_agent_id: subagent ? (childSessionOf(call) ?? null) : null,
    child_agent_type: subagent ? (childAgentTypeOf(raw, input, call) ?? DEFAULT_AGENT) : null,
    background: false,
    child_spend: null,
    tokens: null,
    context_tokens: null,
    // A branch is the checkout's, which the devpro profiler reads beside the capture it runs; the capture here runs
    // in the host's process, and opencode's hooks report no branch.
    branch: null,
    args: argsOf(raw, input) ?? null,
    result: resultOf(call) ?? null,
  }
}

// eventRecord marks the session's lifecycle, as the devpro profiler's record for a SessionStart does: an event and
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

// `devpro/profiler/capture.py`'s `serialize`: the record's JSON line, `name` then `session` then `result` and `args` giving way
// until it fits. `name` and `session` are clipped first, because they are the fixed fields a record cannot
// drop and a long session id alone could hold the line over LINE_LIMIT with nothing left to shrink.
function serialize(record: Record<string, unknown>): string {
  let line = compact(record)
  const fitted: Record<string, unknown> = { ...record }
  for (const key of ["name", "session", "result", "args"]) {
    while (Buffer.byteLength(line, "utf8") > LINE_LIMIT && fitted[key]) {
      const shorter = Math.floor(String(fitted[key]).length / 2)
      if (shorter < 1) delete fitted[key]
      else fitted[key] = clip(String(fitted[key]), shorter)
      line = compact(fitted)
    }
  }
  return line
}

// sessionFile is the trace for one session, its id made path-safe as `devpro/profiler/capture.py` makes it.
function sessionFile(root: string, session: string): string {
  return join(root, TRACE_DIR, `${session.replace(/[^\w.-]/g, "_")}.jsonl`)
}

// ---------- the capture ----------

// The start of every call in flight, by its pairing key. One plugin module serves one session's
// hooks per opencode process, but a key is only unique within a call, so the session id joins it.
// A call whose `execute.after` never fires — denied, interrupted, or a plugin's failing before-hook —
// leaves its key behind, so the map is bounded: a session's keys go at its idle, and the oldest goes
// once MAX_STARTED is held.
const started = new Map<string, number>()

function keyOf(call: Started): string {
  return `${String(call.sessionID)}.${String(call.id)}`
}

function boundStarted(): void {
  for (const key of started.keys()) {
    if (started.size <= MAX_STARTED) return
    started.delete(key)
  }
}

// TORN_TAIL_BYTES bounds the read that finds a torn tail: a record is at most LINE_LIMIT bytes, so a
// longer read cannot change what the last line is.
const TORN_TAIL_BYTES = 64 * 1024

// dropTornTail refuses to append onto a line a killed process left unusable, which would fuse two
// records and lose both. The file is read from its tail, not whole: an append happens on every call.
// The torn line moves aside and the file keeps the lines before it, or nothing at all happens where the
// file ends clean. The devpro profiler has no such repair — it tolerates a torn line on read, and nothing repairs a
// claude store on write.
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
  id: pluginId(),
  async setup(ctx: Context) {
    const root = ctx.location.project.directory
    await ctx.tool.hook("execute.before", (call) => {
      silently(() => {
        if (REMARKS.has(call.tool)) return
        started.set(keyOf(call), Date.now())
        boundStarted()
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
      silently(() => {
        const prefix = `${String(idle.sessionID)}.`
        for (const key of started.keys()) {
          if (key.startsWith(prefix)) started.delete(key)
        }
        append(root, idle.sessionID, eventRecord(idle.sessionID, "experimental.idle", Date.now()))
      })
    })
  },
})
