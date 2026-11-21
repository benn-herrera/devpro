// The longest line the shipped `profiler.ts` writes, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_serialize_runner.ts
// Stdin: JSON {directory, sessionLength}: a scratch directory, and the length of the session id the
// record carries. Stdout: JSON {bytes, session} — the record line's byte count and the session id's
// length after `serialize` fitted it.

import "./opencode_plugin_stub.ts"
import { readFileSync } from "node:fs"

type Input = { directory: string; sessionLength: number }

const input: Input = JSON.parse(await Bun.stdin.text())
const source = new URL("../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname
// `serialize` is module-private; the copy the probe loads exports it, so what the test measures is
// the function the capture appends with.
const patched = `${input.directory}/profiler-serialize-probe.ts`
await Bun.write(patched, readFileSync(source, "utf8").replace("function serialize(", "export function serialize("))
const profiler = await import(patched)

const line: string = profiler.serialize({
  v: 2,
  harness: "opencode",
  at: "2026-11-20T00:00:00.000Z",
  session: "s".repeat(input.sessionLength),
  agent_id: null,
  agent_type: null,
  tool_use_id: null,
  tool: "shell",
  name: "ls",
  duration_ms: 1,
  ok: true,
  child_agent_id: null,
  child_agent_type: null,
  background: false,
  child_spend: null,
  tokens: null,
  context_tokens: null,
  branch: null,
  args: "ls",
  result: "x",
})
console.log(JSON.stringify({ bytes: Buffer.byteLength(line, "utf8"), session: JSON.parse(line).session.length }))
