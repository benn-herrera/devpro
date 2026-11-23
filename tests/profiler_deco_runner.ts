// Runs `devpro/profiler/deco.js` over a page's moments cells, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_deco_runner.ts
// Stdin: JSON {cells} or {index, feed} or {page}: the served HTML of each moments cell, in page order;
// the served `/profiler/` page and the feed its script reads, where the deco is run in the index's own
// order — the index's script drawing its rows, the deco's sweep after it; or a session page's own
// text, where the deco's sweep after the page's script reads the header stamp it wrote.
// Stdout: JSON {readings, titles, drawn, stamped}: each cell's text after the script ran, the title it
// kept, one [markup, reading] per moments cell the index's script drew — the markup it wrote and the
// text it then read, which is the pair a rewritten cell is told by — and, for a session page, its
// header stamp's [reading, title].

import { readFileSync } from "node:fs"

type Input = { cells: string[] } | { index: string; feed: object[] } | { page: string }

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
  listeners: Record<string, (() => void)[]> = {}
  // A checkbox's state, the property the page's script reads and a press switches.
  checked = false
  // The box that holds a page's diagrams and tables, as wide as the page's own: the session page's
  // sequence diagram measures it.
  parentElement: Node = this

  constructor(tag: string) {
    this.tag = tag
  }

  set textContent(text: string) {
    this.childNodes = [text]
  }

  get textContent(): string {
    return this.childNodes.map((child) => (typeof child === "string" ? child : child.textContent)).join("")
  }

  set href(href: string) {
    this.attrs.href = href
  }

  set title(title: string) {
    this.attrs.title = title
  }

  set dateTime(value: string) {
    this.attrs.datetime = value
  }

  set colSpan(span: number | string) {
    this.attrs.colspan = String(span)
  }

  clientWidth = 800

  get dataset(): Record<string, string> {
    return { sort: this.attrs["data-sort"] ?? "" }
  }

  setAttribute(name: string, value: string) {
    this.attrs[name] = value
  }

  removeAttribute(name: string) {
    delete this.attrs[name]
  }

  addEventListener(event: string, listener: () => void) {
    ;(this.listeners[event] ??= []).push(listener)
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
      .filter(([name, value]) => name !== "checked" && value !== undefined)
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

// One moment standing alone, in a subtree with no moments cell: the session page's header stamp. A
// stamp's cell is kept once per element, so the reading the deco writes is the one read back.
const stampCells = new Map<Node, Cell>()
const stampsIn = (node: Node): Cell[] =>
  (node.childNodes.filter((child) => typeof child !== "string") as Node[]).flatMap((child) => {
    if (child.tag !== "time") return stampsIn(child)
    if (!stampCells.has(child)) {
      const stamp = new Cell("")
      stamp.times = [{ getAttribute: () => child.attrs.datetime ?? "" }]
      stamp.reading = stamp.served = child.textContent
      stamp.title = child.attrs.title ?? ""
      stampCells.set(child, stamp)
    }
    return [stampCells.get(child) as Cell]
  })

let cells: Cell[] = []
const observers: (() => void)[] = []
const body = new Node("tbody")
// Each cell the index's script drew, and the markup it wrote to draw it.
const drawn = new Map<Cell, () => string>()
// What a lookup of the page's moments selector finds in a root: the cells a row holds.
const standing = (root: Node): Cell[] =>
  root.childNodes.filter((child): child is Node => typeof child !== "string").flatMap(cellsIn)
body.querySelectorAll = (selector: string): unknown[] => (selector === ".moments" ? standing(body) : [])
body.replaceChildren = (...nodes: Node[]) => {
  body.childNodes = nodes
  for (const react of observers) react()
}

// The page's static controls and column heads, built from the served markup in document order: the
// index's script binds its controls by id and its heads by `data-sort`, so a binding that reaches
// nothing here is a control no press drives.
const staticNodes = (html: string): Node[] => {
  const found: Node[] = []
  for (const [, tag, attrs] of html.matchAll(/<(input|button)\b([^>]*)>/g)) {
    const node = new Node(tag)
    for (const [, name, value] of attrs.matchAll(/([\w-]+)(?:="([^"]*)")?/g)) node.attrs[name] = value ?? ""
    if (tag === "input") node.checked = "checked" in node.attrs
    found.push(node)
  }
  return found
}
const statics = "index" in input ? staticNodes(input.index) : []
const byId = new Map(statics.filter((node) => node.attrs.id).map((node) => [node.attrs.id, node]))
// The session page's header stamp, read back after the sweep: the `<time>` the page's script wrote
// into the subline and the deco then read in the reader's own clock.
const subline = new Node("div")
subline.querySelectorAll = (selector: string): unknown[] => (selector === "time" ? stampsIn(subline) : [])
// Any other id a page's script asks for — the session page's heading, timeline, tree and panel — is
// an element standing empty, as the page's own markup says it is; an id the page's mark-up carries
// stands as the element the markup names.
const elsewhere = new Map<string, Node>()
const declared = [...input.page?.matchAll(/id="([^"]+)"/g) ?? []].map(([, id]) => id)
const elementFor = (id: string): Node => {
  if (id === "rows") return body
  if (id === "subline") return subline
  if (byId.has(id)) return byId.get(id) as Node
  if (!elsewhere.has(id)) {
    if (!declared.includes(id)) return null as unknown as Node
    const node = new Node("div")
    node.parentElement = node
    elsewhere.set(id, node)
  }
  return elsewhere.get(id) as Node
}

Object.assign(globalThis, {
  document: {
    createElement: (tag: string) => new Node(tag),
    getElementById: (id: string) => elementFor(id),
    querySelector: () => null,
    querySelectorAll: (selector: string) =>
      selector === ".sort"
        ? statics.filter((node) => node.tag === "button")
        : selector === ".controls input"
          ? statics.filter((node) => node.tag === "input")
          : selector === ".moments, #subline time"
            ? [...cells, ...stampsIn(subline)]
            : [],
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
  window: { addEventListener: () => {} },
  getComputedStyle: () => ({ getPropertyValue: () => "" }),
})

if ("cells" in input) {
  cells = input.cells.map((served) => new Cell(served))
  new Function(source)()
} else if ("index" in input) {
  // The index's own script runs first and its fetch settles after it; the deco loads before those
  // rows arrive — the served page's script order — so its sweep sees the empty body at load and each
  // drawn cell on the change its arrival makes.
  new Function([...input.index.matchAll(BLOCK)][0][1])()
  new Function(source)()
  await new Promise((resolve) => setTimeout(resolve, 0))
} else {
  // A session page: the page's own script writes its header stamp, and the deco's sweep, loaded
  // before it as the served page loads it, reads it when the page's script adds it.
  const page = [...input.page.matchAll(BLOCK)].map(([, body]) => body)
  new Function(source)()
  new Function(page[page.length - 1])()
  for (const react of observers) react()
}

console.log(
  JSON.stringify({
    readings: cells.map((cell) => cell.reading),
    titles: cells.map((cell) => cell.title),
    drawn: [...drawn].map(([cell, markup]) => [markup(), cell.reading]),
    stamped: stampsIn(subline).map((cell) => [cell.reading, cell.title]),
  }),
)
