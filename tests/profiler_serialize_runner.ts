// The longest line the shipped `profiler.ts` writes, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_serialize_runner.ts
// Stdin: JSON {directory, record, sessionLength}: a scratch root, the fixture record the test reads
// and passes whole, and the session id's length. Stdout: JSON {bytes, session} — the record line's
// byte count and the session id's length after `serialize` fitted it.

import "./opencode_plugin_stub.ts"
import { readFileSync } from "node:fs"

type Input = { directory: string; record: Record<string, unknown>; sessionLength: number }

const input: Input = JSON.parse(await Bun.stdin.text())
// A missing length would silently measure an empty session; the test's whole claim is the field's fit.
if (typeof input.sessionLength !== "number") throw new Error("stdin carries no sessionLength")
const source = new URL("../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname
// `serialize` is module-private; the copy the probe loads exports it, so what the test measures is
// the function the capture appends with.
const patched = `${input.directory}/profiler-serialize-probe.ts`
await Bun.write(patched, readFileSync(source, "utf8").replace("function serialize(", "export function serialize("))
const profiler = await import(patched)

const line: string = profiler.serialize({
  ...input.record,
  // Fixed instant, so the length under measure is the fields', not the clock's.
  at: "2026-11-20T00:00:00.000Z",
  session: "s".repeat(input.sessionLength),
})
console.log(JSON.stringify({ bytes: Buffer.byteLength(line, "utf8"), session: JSON.parse(line).session.length }))
