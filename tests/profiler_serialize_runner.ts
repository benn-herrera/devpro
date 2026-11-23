// The longest line the shipped `profiler.ts` writes, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_serialize_runner.ts
// Stdin: JSON {directory, sessionLength}: a scratch root — the capture runner writes its record under
// `<directory>/capture/` — and the length of the session id the record carries. Stdout: JSON {bytes,
// session} — the record line's byte count and the session id's length after `serialize` fitted it.

import "./opencode_plugin_stub.ts"
import { readFileSync } from "node:fs"

type Input = { directory: string; sessionLength: number }

const input: Input = JSON.parse(await Bun.stdin.text())
// A missing length would silently measure an empty session; the test's whole claim is the field's fit.
if (typeof input.sessionLength !== "number") throw new Error("stdin carries no sessionLength")
const source = new URL("../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname
// `serialize` is module-private; the copy the probe loads exports it, so what the test measures is
// the function the capture appends with.
const patched = `${input.directory}/profiler-serialize-probe.ts`
await Bun.write(patched, readFileSync(source, "utf8").replace("function serialize(", "export function serialize("))
const profiler = await import(patched)

// The record under measure is one the capture wrote, taken by running the capture runner in this same
// scratch root: its fields are the record's, not a list restated here that goes stale as the record
// changes. The runner is a process, not an import, because its top-level awaits read stdin and print
// their records — an import would have it consume this runner's stdin and write over its stdout.
const capture = Bun.spawnSync({
  cmd: [process.execPath, new URL("./profiler_capture_runner.ts", import.meta.url).pathname],
  stdin: new TextEncoder().encode(JSON.stringify({ directory: `${input.directory}/capture` })),
})
if (capture.exitCode !== 0) throw new Error(`the capture runner wrote no record: ${capture.stderr.toString()}`)
const records = (JSON.parse(capture.stdout.toString()) as { records: Record<string, unknown>[] }).records
// The measured record: the dispatch whose child the result's output names, a dispatch's being a record
// with no text to fit but its short brief.
const record = records.find((candidate) => candidate.tool === "Agent" && candidate.child_agent_id === "ses_child")
if (record === undefined) throw new Error("the capture runner wrote no dispatch record")
const line: string = profiler.serialize({
  ...record,
  // Fixed instant, so the length under measure is the fields', not the clock's.
  at: "2026-11-20T00:00:00.000Z",
  session: "s".repeat(input.sessionLength),
})
console.log(JSON.stringify({ bytes: Buffer.byteLength(line, "utf8"), session: JSON.parse(line).session.length }))
