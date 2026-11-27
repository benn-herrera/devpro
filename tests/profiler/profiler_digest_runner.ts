// The shipped `profiler.ts`'s directives digest and the ownership markers it recognizes, for
// tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_digest_runner.ts
// Stdin: JSON {directory, markersDirectory, probeDirectory}: the project root the digest is taken over, a
// scratch directory of its own for the copy the markers are read from where they are asked for, and a
// directory outside the project for the copy the stamp is read from — so nothing written here stands
// inside the state digested, and no two runs share a probe path. Nothing is fired through the hooks.
// Stdout: JSON {stamp, manifest, markers}: the stamp fields the capture computes for a session starting
// now, the per-file digests its manifest holds, and the ownership markers the module recognizes.

import "../opencode_plugin_stub.ts"
import { readFileSync } from "node:fs"
import { join } from "node:path"

type Input = { directory: string; markersDirectory?: string | null; probeDirectory: string }

const input: Input = JSON.parse(await Bun.stdin.text())
const sourcePath = new URL("../../devpro/harnesses/resources/opencode/profiler.ts", import.meta.url).pathname

// probe loads a copy of the module with one line rewritten to export what it holds privately, as the stamp
// runner's copy exports `sessionStamp`: what the probe reads with is what the capture writes with.
async function probe(directory: string, [held, exported]: [string, string]): Promise<Record<string, unknown>> {
  const patched = join(directory, `profiler-digest-probe-${crypto.randomUUID()}.ts`)
  await Bun.write(patched, readFileSync(sourcePath, "utf8").replace(held, exported))
  return (await import(patched)) as Record<string, unknown>
}

const profiler = await probe(input.probeDirectory, ["function readStamp(", "export function readStamp("])
const [stamp, pairs]: [{ plan: string | null; directives: string | null }, [string, string][]] = profiler.readStamp(
  input.directory,
) as [{ plan: string | null; directives: string | null }, [string, string][]]
const manifest: Record<string, string> = Object.fromEntries(pairs)
let markers: string[] = []
if (typeof input.markersDirectory === "string") {
  const exported = await probe(input.markersDirectory, ["const OWNERSHIP_MARKERS = ", "export const OWNERSHIP_MARKERS = "])
  markers = exported.OWNERSHIP_MARKERS as string[]
}
console.log(JSON.stringify({ stamp, manifest, markers }))
