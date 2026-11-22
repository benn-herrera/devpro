// Runs `devpro/profiler/deco.js` over a page's moments cells, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_deco_runner.ts
// Stdin: JSON {cells}: the served HTML of each moments cell, in page order.
// Stdout: JSON {readings, titles}: each cell's text after the script ran, and the title it kept, so a
// cell whose text was rewritten is told from one the script left as it served.

import { readFileSync } from "node:fs"

type Input = { cells: string[] }

const input: Input = JSON.parse(await Bun.stdin.text())
const source = readFileSync(new URL("../devpro/profiler/deco.js", import.meta.url).pathname, "utf8")
const OPEN = /^<span class="moments" title="([^"]*)">/
const TIMES = /<time datetime="([^"]*)"/g

// One moments cell: the title it serves, the instants its text holds, and the text the script sets.
class Cell {
  title: string
  times: { getAttribute: () => string }[]
  reading: string

  constructor(served: string) {
    this.title = OPEN.exec(served)?.[1] ?? ""
    this.times = Array.from(served.matchAll(TIMES), ([, datetime]) => ({ getAttribute: () => datetime }))
    this.reading = served.replace(OPEN, "").slice(0, -"</span>".length)
  }

  querySelectorAll(selector: string): unknown[] {
    return selector === "time" ? this.times : []
  }

  set textContent(reading: string) {
    this.reading = reading
  }
}

const cells = input.cells.map((served) => new Cell(served))
// The moments the page holds' selector; the nav's elements are absent, as on an index served without
// its frame.
Object.assign(globalThis, {
  document: {
    getElementById: () => null,
    querySelector: () => null,
    querySelectorAll: (selector: string) => (selector === "td .moments" ? cells : []),
  },
  fetch: async () => {
    throw new Error("no server")
  },
  setInterval: () => 0,
})

new Function(source)()
console.log(JSON.stringify({ readings: cells.map((cell) => cell.reading), titles: cells.map((cell) => cell.title) }))
