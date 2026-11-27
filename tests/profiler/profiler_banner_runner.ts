// The shipped `profiler.ts`'s two banner constants and the answer its recognizer gives a file, for
// tests/profiler/test_stamp.py.
//
// Usage: bun tests/profiler/profiler_banner_runner.ts
// Stdin: JSON {directory, probeDirectory}: the project root, holding one harness directory and the file in
// it, and a scratch directory of its own for the probe copy. Nothing is fired through the hooks.
// Stdout: JSON {generatedBanner, installedBanner, recognized}: the two constants as the module holds them —
// the string whole, the pattern's ` .* ` read as the one space it separates — and whether `readStamp` lists
// the project's one file.

import "../opencode_plugin_stub.ts"
import { readFileSync } from "node:fs"
import { join } from "node:path"

type Input = { directory: string; probeDirectory: string }

const input: Input = JSON.parse(await Bun.stdin.text())
const sourcePath = new URL("../../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname

// probe loads a copy of the module with these lines rewritten to export what it holds privately, as the
// digest runner's copy exports `readStamp`: what the probe reads with is what the capture writes with.
async function probe(): Promise<Record<string, unknown>> {
  const patched = join(input.probeDirectory, `profiler-banner-probe-${crypto.randomUUID()}.ts`)
  const source = readFileSync(sourcePath, "utf8")
    .replace("const GENERATED_BANNER = ", "export const GENERATED_BANNER = ")
    .replace("const INSTALLED_BANNER = ", "export const INSTALLED_BANNER = ")
    .replace("function readStamp(", "export function readStamp(")
  await Bun.write(patched, source)
  return (await import(patched)) as Record<string, unknown>
}

const profiler = await probe()
const [, manifest] = (profiler.readStamp as (root: string) => [unknown, [string, string][]])(
  input.directory,
)
console.log(
  JSON.stringify({
    generatedBanner: profiler.GENERATED_BANNER,
    installedBanner: (profiler.INSTALLED_BANNER as RegExp).source.replace(" .* ", " "),
    recognized: manifest.length > 0,
  }),
)
