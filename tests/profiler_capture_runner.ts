// Runs the capture's records through the shipped hp.py's tree, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_capture_runner.ts
// Stdin: JSON {directory}: a project root whose `.devpro-temp/.profiler-opencode/` receives the records.
// Stdout: JSON {records, startedBeforeIdle, startedAfterIdle} — the records the shipped `profiler.ts`
// wrote, through the plugin context stub, for a completed call, a failed one, a skill call, a subagent
// dispatch, a remark and a call whose `execute.after` never fires; and the in-flight start map's size
// around the session's idle, which drops the never-finished call's entry.

import "./opencode_plugin_stub.ts"
import { readFileSync } from "node:fs"

type Callback = (event: unknown) => unknown
type Input = { directory: string }

const input: Input = JSON.parse(await Bun.stdin.text())
const source = new URL("../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname
// The in-flight start map is module-private; the copy the probe loads exports it, so what the test
// asserts is the map the callbacks wrote.
const patched = `${input.directory}/profiler-map-probe.ts`
await Bun.write(patched, readFileSync(source, "utf8").replace("const started = new Map<string, number>()", "export const started = new Map<string, number>()"))
const profiler = await import(patched)

const hooks = new Map<string, Callback[]>()
const add = (name: string, callback: Callback) => hooks.set(name, [...(hooks.get(name) ?? []), callback])
await profiler.default.setup({
  location: { project: { directory: input.directory } },
  tool: { hook: async (name: string, callback: Callback) => void add(name, callback) },
  session: { hook: async (name: string, callback: Callback) => void add(name, callback) },
} as never)
const fire = async (name: string, event: unknown) => {
  for (const callback of hooks.get(name) ?? []) await callback(event)
}
// opencode 2.3.2's event shapes: `execute.before`/`execute.after` carry the call's id, and a failed
// call's `error` is the host's `Tool.Error` object.
const session = "ses_capture"
const base = (id: string, tool: string, callInput: unknown) => ({ tool, sessionID: session, agent: "build", messageID: "msg_1", id, input: callInput })

await fire("execute.before", base("call_1", "shell", { command: "printf 'hi\\n'" }))
await fire("execute.after", {
  ...base("call_1", "shell", { command: "printf 'hi\\n'" }),
  status: "completed",
  result: { output: "hi\n", content: [{ type: "text", text: "hi\n" }], metadata: { exit: 0 } },
})

await fire("execute.before", base("call_2", "shell", { command: "rm -rf /" }))
await fire("execute.after", {
  ...base("call_2", "shell", { command: "rm -rf /" }),
  status: "error",
  error: Object.assign(new Error("The user rejected this tool call"), { _tag: "Tool.Error" }),
})

await fire("execute.before", base("call_3", "skill", { id: "profiler" }))
await fire("execute.after", {
  ...base("call_3", "skill", { id: "profiler" }),
  status: "completed",
  result: { content: [{ type: "text", text: "loaded" }] },
})

await fire("execute.before", base("call_4", "subagent", { agent: "devpro-python-coder", description: "port it", prompt: "port hp.py" }))
await fire("execute.after", {
  ...base("call_4", "subagent", { agent: "devpro-python-coder", description: "port it", prompt: "port hp.py" }),
  status: "completed",
  result: { output: { sessionID: "ses_child", status: "running" } },
})

// A dispatch the host reports as a fork: the response's `agentType` is the kind hp.py draws the context by.
await fire("execute.before", base("call_7", "subagent", { agent: "devpro-architect", description: "fork it", prompt: "fork" }))
await fire("execute.after", {
  ...base("call_7", "subagent", { agent: "devpro-architect", description: "fork it", prompt: "fork" }),
  status: "completed",
  result: { output: { sessionID: "ses_fork", status: "running" }, metadata: { agentType: "fork" } },
})

// The same dispatch under opencode 2.3.0's spelling of the tool, which its floor range covers.
await fire("execute.before", base("call_8", "task", { agent: "devpro-tech-writer", description: "write it", prompt: "write" }))
await fire("execute.after", {
  ...base("call_8", "task", { agent: "devpro-tech-writer", description: "write it", prompt: "write" }),
  status: "completed",
  result: { output: "ses_task" },
})

// A remark the capture skips, a call whose `execute.after` never fires, and the session's idle.
await fire("execute.before", base("call_5", "todowrite", { todos: [] }))
await fire("execute.before", base("call_6", "removed_tool", {}))
const startedBeforeIdle = profiler.started.size
await fire("experimental.idle", { sessionID: session, background: [] })
const startedAfterIdle = profiler.started.size

const file = `${input.directory}/.devpro-temp/.profiler-opencode/${session}.jsonl`
const records = (await Bun.file(file).text())
  .trim()
  .split("\n")
  .map((line) => JSON.parse(line))
console.log(JSON.stringify({ records, startedBeforeIdle, startedAfterIdle }))
