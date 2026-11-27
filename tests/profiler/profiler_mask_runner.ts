// Masks a sample per line through the shipped profiler.ts's masking, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_mask_runner.ts <samples file>
// Stdin: JSON {directory}: a scratch directory the copy the runner loads is written into.
// Stdout: each sample's masked text as a JSON string, one per line.

import "../opencode_plugin_stub.ts"
import { readFileSync } from "node:fs"

const [samples] = process.argv.slice(2)
const input: { directory: string } = JSON.parse(await Bun.stdin.text())
const source = new URL("../../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname
// `mask` is module-private; the copy the runner loads exports it.
const patched = `${input.directory}/profiler-mask-probe.ts`
await Bun.write(patched, readFileSync(source, "utf8").replace("function mask(", "export function mask("))
const { mask } = await import(patched)
const lines = readFileSync(samples, "utf8").split("\n").filter((line) => line.length > 0)
console.log(lines.map((line) => JSON.stringify(mask(line))).join("\n"))
