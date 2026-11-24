// The shipped `profiler.ts`'s record construction, driven over host-shape inputs, for
// tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_contract_runner.ts
// Stdin: JSON {directory}: a project root whose `.devpro-temp/.profiler-opencode/` receives the store.
// Stdout: JSON {records} — the records the shipped `profiler.ts` wrote through a stub plugin context:
// a completed call, a failed one, a skill call, a subagent dispatch in each of opencode 2.3.0's,
// 2.3.2's and 2.4.1's result shapes, one whose top-level id is not a string, and the session's idle.
//
// The host shapes below are inputs, and the test claims nothing about what the host reports: the
// events are shaped as the three releases' results are said to ride, and each shape's own home is
// the harness-profiler leaf's account of the capture. The plugin context under them is a stub, which
// gets execution to the record's construction and vouches for no host behavior. What is under
// measure is the capture: what its construction writes for these inputs.

import "./opencode_plugin_stub.ts"

type Callback = (event: unknown) => unknown
type Input = { directory: string }

const input: Input = JSON.parse(await Bun.stdin.text())
const source = new URL("../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname
const profiler = await import(source)

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

const session = "ses_capture"
const call = (id: string, tool: string, callInput: unknown) => ({
  tool,
  sessionID: session,
  agent: "build",
  messageID: "msg_1",
  id,
  input: callInput,
})
// A subagent dispatch's input: the host's `agent` is the kind, and the description and prompt are the
// brief the record's `args` carries.
const dispatch = (agent: string) => ({ agent, description: "port it", prompt: "port hp.py" })

await fire("execute.before", call("call_1", "shell", { command: "printf 'hi\\n'" }))
await fire("execute.after", {
  ...call("call_1", "shell", { command: "printf 'hi\\n'" }),
  status: "completed",
  result: { output: "hi\n", content: [{ type: "text", text: "hi\n" }], metadata: { exit: 0 } },
})

// A failed call: the host reports its reason as a `Tool.Error` object rather than a string.
await fire("execute.before", call("call_2", "shell", { command: "rm -rf /" }))
await fire("execute.after", {
  ...call("call_2", "shell", { command: "rm -rf /" }),
  status: "error",
  error: Object.assign(new Error("The user rejected this tool call"), { _tag: "Tool.Error" }),
})

// A skill call, which the host names by its `id`.
await fire("execute.before", call("call_3", "skill", { id: "profiler" }))
await fire("execute.after", {
  ...call("call_3", "skill", { id: "profiler" }),
  status: "completed",
  result: { content: [{ type: "text", text: "loaded" }] },
})

// opencode 2.3.2's shape: the child's id is `output.sessionID`, and nowhere else.
await fire("execute.before", call("call_4", "subagent", dispatch("devpro-python-coder")))
await fire("execute.after", {
  ...call("call_4", "subagent", dispatch("devpro-python-coder")),
  status: "completed",
  result: { output: { sessionID: "ses_output", status: "running" } },
})

// opencode 2.3.0's shape: the id rides `metadata.sessionID`, a bare `output` string refusing the
// output's read.
await fire("execute.before", call("call_5", "subagent", dispatch("devpro-go-coder")))
await fire("execute.after", {
  ...call("call_5", "subagent", dispatch("devpro-go-coder")),
  status: "completed",
  result: { output: "ses_floor", metadata: { sessionID: "ses_floor" } },
})

// opencode 2.4.1's shape: the id at the result's top level, `output` a bare string carrying none.
await fire("execute.before", call("call_6", "subagent", dispatch("devpro-rust-coder")))
await fire("execute.after", {
  ...call("call_6", "subagent", dispatch("devpro-rust-coder")),
  status: "completed",
  result: { sessionID: "ses_top", status: "running", output: "The subagent is working..." },
})

// A top-level id the host did not report as a string: the guard refuses it, and the read falls
// through to the output's id, the next place the host reports one.
await fire("execute.before", call("call_7", "subagent", dispatch("devpro-typescript-coder")))
await fire("execute.after", {
  ...call("call_7", "subagent", dispatch("devpro-typescript-coder")),
  status: "completed",
  result: { sessionID: 5, output: { sessionID: "ses_guard", status: "running" } },
})

await fire("experimental.idle", { sessionID: session, background: [] })

const file = `${input.directory}/.devpro-temp/.profiler-opencode/${session}.jsonl`
const records = (await Bun.file(file).text())
  .trim()
  .split("\n")
  .map((line: string) => JSON.parse(line))
console.log(JSON.stringify({ records }))
