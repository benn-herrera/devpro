// The shipped `profiler.ts`'s store-stamp read, driven over a store someone else wrote, for
// tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_stamp_runner.ts
// Stdin: JSON {directory, session}: a project root holding the session's `.devpro-temp/.profiler-opencode/`
// store, and the session id. Nothing is fired through the hooks. Stdout: JSON {stamp, stores} — the stamp
// the record the plugin writes for the session next carries, and every record line each store the readers
// read holds, its two stamp keys where it carries them.

import "./opencode_plugin_stub.ts"
import { readdirSync, readFileSync } from "node:fs"
import { join } from "node:path"

type Input = { directory: string; session: string }

const input: Input = JSON.parse(await Bun.stdin.text())
const source = new URL("../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname
// `sessionStamp` is module-private; the copy the probe loads exports it, as the serialize runner's copy
// exports `serialize`, so what the probe reads with is the function the capture appends with.
const patched = `${input.directory}/profiler-stamp-probe.ts`
await Bun.write(patched, readFileSync(source, "utf8").replace("function sessionStamp(", "export function sessionStamp("))
const profiler = await import(patched)

const stamp: unknown = profiler.sessionStamp(input.directory, input.session)

const stores: Record<string, ([unknown, unknown] | null)[]> = {}
for (const name of readdirSync(join(input.directory, ".devpro-temp"))) {
  // The manifest directory is named `.profiler-directives`, a prefix of a store name and no store.
  if (!name.startsWith(".profiler-")) continue
  const file = join(input.directory, ".devpro-temp", name, `${input.session}.jsonl`)
  let text: string
  try {
    text = readFileSync(file, "utf8")
  } catch {
    continue
  }
  stores[name] = text
    .split("\n")
    .filter((line) => line)
    .map((line) => {
      const record = JSON.parse(line)
      return "plan" in record || "directives" in record ? [record.plan, record.directives] : null
    })
}
console.log(JSON.stringify({ stamp, stores }))
