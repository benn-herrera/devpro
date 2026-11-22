// Runs `devpro/profiler/deco.js` over a page's moments cells, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_deco_runner.ts
// Stdin: JSON {cells} or {index, feed}: the served HTML of each moments cell, in page order; or the
// served `/profiler/` page and the feed its script reads, where the deco is run in the index's own
// order — the index's script drawing its rows, the deco's sweep after it.
// Stdout: JSON {readings, titles, drawn}: each cell's text after the script ran, the title it kept,
// and one [markup, reading] per moments cell the index's script drew — the markup it wrote and the
// text it then read, which is the pair a rewritten cell is told by.

import { readFileSync } from "node:fs"

type Input = { cells: string[] } | { index: string; feed: object[] }

const input: Input = JSON.parse(await Bun.stdin.text())
const source = readFileSync(new URL("../devpro/profiler/deco.js", import.meta.url).pathname, "utf8")
const OPEN = /^<span class="moments" title="([^"]*)">/
const TIMES = /<time datetime="([^"]*)"/g
const BLOCK = /<script>([\s\S]*?)<\/script>/g

// One moments cell: the title it serves, the instants its text holds, and the text the script sets.
// `textContent` is a prototype accessor alone: a field declared beside it is initialized to
// `undefined` on the instance and shadows it, swallowing every reading the deco writes.
class Cell {
  title: string
  served: string
  times: { getAttribute: () => string }[]
  reading: string

  constructor(served: string, title = OPEN.exec(served)?.[1] ?? "") {
    this.title = title
    this.served = served.replace(OPEN, "").slice(0, -"</span>".length)
    this.reading = this.served
    this.times = Array.from(served.matchAll(TIMES), ([, datetime]) => ({ getAttribute: () => datetime }))
  }

  querySelectorAll(selector: string): unknown[] {
    return selector === "time" ? this.times : []
  }

  set textContent(reading: string) {
    this.reading = reading
  }
}

// One element, as markup: the tag, its attributes, its text and its children in order.
class Node {
  tag: string
  attrs: Record<string, string> = {}
  childNodes: (Node | string)[] = []
  className = ""

  constructor(tag: string) {
    this.tag = tag
  }

  set textContent(text: string) {
    this.childNodes = [text]
  }

  set href(href: string) {
    this.attrs.href = href
  }

  set title(title: string) {
    this.attrs.title = title
  }

  set colSpan(span: number | string) {
    this.attrs.colspan = String(span)
  }

  setAttribute(name: string, value: string) {
    this.attrs[name] = value
  }

  append(...nodes: (Node | string)[]) {
    this.childNodes.push(...nodes)
  }

  replaceChildren(...nodes: Node[]) {
    this.childNodes = nodes
    if (this === body) for (const react of observers) react()
  }

  html(): string {
    const attrs = Object.entries({ ...this.attrs, ...(this.className ? { class: this.className } : {}) })
      .map(([name, value]) => ` ${name}="${value}"`)
      .join("")
    const inner = this.childNodes.map((child) => (typeof child === "string" ? child : child.html())).join("")
    return `<${this.tag}${attrs}>${inner}</${this.tag}>`
  }
}

// The cell a row carries, read from the node the index's script built: every `<time>` in it is an
// instant, and the text the page wrote is what the deco's sweep rewrites.
const asCell = (node: Node): Cell => {
  const cell = new Cell("", node.attrs.title ?? "")
  cell.times = (node.childNodes.filter((child) => typeof child !== "string") as Node[])
    .filter((child) => child.tag === "time")
    .map((child) => ({ getAttribute: () => child.attrs.datetime ?? "" }))
  cell.served = node.childNodes
    .map((child) => (typeof child === "string" ? child : (child.childNodes[0] as string) ?? ""))
    .join("")
  cell.reading = cell.served
  return cell
}

// Every moments cell in a subtree, wherever it sits, each kept in the ledger of what the index drew
// with its markup as the script wrote it.
const cellsIn = (node: Node): Cell[] =>
  (node.childNodes.filter((child) => typeof child !== "string") as Node[]).flatMap((child) => {
    if (child.className !== "moments") return cellsIn(child)
    const cell = asCell(child)
    drawn.set(cell, () => child.html())
    return [cell]
  })

let cells: Cell[] = []
const observers: (() => void)[] = []
const body = new Node("tbody")
// Each cell the index's script drew, and the markup it wrote to draw it.
const drawn = new Map<Cell, () => string>()
// What a lookup of the page's moments selector finds in a root: the cells a row holds.
const standing = (root: Node): Cell[] =>
  root.childNodes.filter((child): child is Node => typeof child !== "string").flatMap(cellsIn)
body.querySelectorAll = (selector: string): unknown[] => (selector === "td .moments" ? standing(body) : [])
body.replaceChildren = (...nodes: Node[]) => {
  body.childNodes = nodes
  for (const react of observers) react()
}

Object.assign(globalThis, {
  document: {
    createElement: (tag: string) => new Node(tag),
    getElementById: (id: string) => (id === "rows" ? body : null),
    querySelector: () => null,
    querySelectorAll: (selector: string) => (selector === "td .moments" ? cells : []),
  },
  MutationObserver: class {
    constructor(private react: () => void) {}
    observe() {
      observers.push(this.react)
    }
  },
  fetch: async () => {
    if (!("index" in input)) throw new Error("no server")
    return { ok: true, status: 200, json: async () => input.feed }
  },
  setInterval: () => 0,
})

if ("cells" in input) {
  cells = input.cells.map((served) => new Cell(served))
  new Function(source)()
} else {
  // The index's own script runs first and its fetch settles after it; the deco loads before those
  // rows arrive — the served page's script order — so its sweep sees the empty body at load and each
  // drawn cell on the change its arrival makes.
  new Function([...input.index.matchAll(BLOCK)][0][1])()
  new Function(source)()
  await new Promise((resolve) => setTimeout(resolve, 0))
}

console.log(
  JSON.stringify({
    readings: cells.map((cell) => cell.reading),
    titles: cells.map((cell) => cell.title),
    drawn: [...drawn].map(([cell, markup]) => [markup(), cell.reading]),
  }),
)
