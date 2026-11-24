// Runs `devpro/profiler/deco.js` over a page's moments cells, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_deco_runner.ts
// Stdin: JSON {cells} or {index, feed} or {page}: the served HTML of each moments cell, in page order;
// the served `/profiler/` page and the feed its script reads, where the deco is run in the index's own
// order — the index's script drawing its rows, the deco's sweep after it; or a session page's own
// text, where the deco's sweep loaded before the page's script reads the header stamp's arrival.
// Stdout: JSON {readings, titles, markup, drawn, stamped}: each cell's text after the script ran, the
// title it kept, its markup as the sweep left it — each `<time>` still at its `datetime` beside the text
// now in it — one [markup, reading] per moments cell the index's script drew, and, for a session page,
// its header stamp's [reading, title].
//
// The stand-in is the browser's where the sweep touches it: a cell's `<time>` elements are elements of
// their own, and writing one's `textContent` replaces that element's text alone — its `datetime` and
// its siblings stand. A cell's text is its own text around them, as a browser reads it, so a sweep that
// never ran leaves the served text where one that ran replaced it.

import { readFileSync } from "node:fs"

type Input = { cells: string[] } | { index: string; feed: object[] } | { page: string }

const input: Input = JSON.parse(await Bun.stdin.text())
const source = readFileSync(new URL("../devpro/profiler/deco.js", import.meta.url).pathname, "utf8")
// The selectors the deco queries, read from its own `MOMENTS` constant: the sweep's document lookup
// answers the string the shipped script carries, so the stand-in and the page cannot drift apart.
const SCAN = source.match(/^const MOMENTS = ("[^"]*");$/m)
if (!SCAN) throw new Error('deco.js carries no `const MOMENTS = "...";` the sweep is scanned by')
const MOMENTS = JSON.parse(SCAN[1]) as string
const TIMES = /<time\b([^>]*)>([^<]*)<\/time>/g
const BLOCK = /<script>([\s\S]*?)<\/script>/g

// One `<time>` element: its `datetime`, the text the page served it, and the text written into it
// since — `null` until one is. The `datetime` is never written, which is what the machine form's
// surviving a sweep is asserted on.
class Time {
  datetime: string
  served: string
  written: string | null = null

  constructor(datetime: string, served: string) {
    this.datetime = datetime
    this.served = served
  }

  getAttribute(name: string): string | null {
    return name === "datetime" ? this.datetime : null
  }

  get textContent(): string {
    return this.written ?? this.served
  }

  set textContent(text: string) {
    this.written = text
  }
}

// A moments cell or a lone stamp: its title, the text the page served, and the `<time>` elements that
// text stands around. `textContent` is a prototype getter alone — a field or a setter of that name
// declared beside it would be the property instead, and the deco's comparison would read `undefined`.
class Cell {
  title: string
  served: string
  times: Time[]

  constructor(served: string, title = "") {
    this.title = title || /^<span class="moments"[^>]*\btitle="([^"]*)"/.exec(served)?.[1] || ""
    this.served = served.replace(/^<span class="moments"[^>]*>/, "").replace(/<\/span>$/, "")
    this.times = [...served.matchAll(TIMES)].map(([, attrs, text]) => new Time(/datetime="([^"]*)"/.exec(attrs)?.[1] ?? "", text))
  }

  // The deco's own lookup into a cell: its `<time>` elements, as a browser's returns them.
  querySelectorAll(selector: string): unknown[] {
    return selector === "time" ? this.times : []
  }

  // The cell's text as a browser reads it: the served text with each `<time>`'s current text where the
  // element stood. A sweep arranges for the whole to read what it wrote; a cell it never reached keeps
  // what the page served, which is what makes a sweep-over-nothing distinguishable from one that ran
  // and wrote the same text.
  get textContent(): string {
    const served = this.served.match(new RegExp(TIMES.source, "g")) ?? []
    return served.reduce((text, element, index) => text.replace(element, this.times[index].textContent), this.served)
  }

  // The cell's markup as the sweep leaves it: each `<time>` at its `datetime`, its text now the reading.
  html(): string {
    return `<span class="moments" title="${this.title}">${this.served.replace(
      new RegExp(TIMES.source, "g"),
      (_, attrs, text) => `<time${attrs}>${this.times.filter((time) => time.served === text).shift()?.textContent ?? text}</time>`,
    )}</span>`
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

  getAttribute(name: string): string | null {
    return this.attrs[name] ?? null
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

// The moments cell an element the index's script built stands for: its `<time>` children are the
// instants, its own text between them what the page wrote, and each child is the element the sweep
// writes into, so the cell reads the node's state whenever it is read.
const cellOf = (node: Node): Cell => {
  const cell = new Cell("", node.attrs.title ?? "")
  cell.served = node.childNodes.map((child) => (typeof child === "string" ? child : child.html())).join("")
  cell.times = node.childNodes
    .filter((child): child is Node => typeof child !== "string" && child.tag === "time")
    .map((child) => new Time(child.attrs.datetime ?? "", child.childNodes.join("")))
  return cell
}

// The cell of a lone stamp — a `<time>` standing on its own, as the session page's header is. The
// element is the cell: its one instant is the element's own `datetime` and text, and the deco writes
// into the element's own text, which every later read of it sees.
const stampCell = (node: Node): Cell => {
  const cell = new Cell("", node.attrs.title ?? "")
  cell.served = node.childNodes.join("")
  const time = new Time(node.attrs.datetime ?? "", cell.served)
  Object.defineProperty(time, "written", {
    get: () => node.childNodes.join(""),
    set: (text: string) => (node.childNodes = [text]),
  })
  cell.times = [time]
  return cell
}

// Every moments cell the index's script drew, keyed by the node it drew into: one cell per element,
// so the sweep's write and the test's read are the same cell.
const drawn = new Map<Node, Cell>()

// The moments cell an element at the class stands for, built once and kept.
const cellFor = (node: Node): Cell => {
  if (!drawn.has(node)) drawn.set(node, cellOf(node))
  return drawn.get(node) as Cell
}

// Every cell a subtree carries: the class's elements and the cell each stands for.
const cellsIn = (node: Node): Cell[] =>
  (node.childNodes.filter((child) => typeof child !== "string") as Node[]).flatMap((child) =>
    child.className === "moments" ? [cellFor(child)] : cellsIn(child),
  )

// Every lone stamp in a subtree, built afresh from the elements as they now stand: a stamp the page's
// script writes after an earlier read is a new cell, never a stale copy of one.
const stampsIn = (node: Node): Cell[] =>
  (node.childNodes.filter((child) => typeof child !== "string") as Node[]).flatMap((child) =>
    child.tag === "time" ? [stampCell(child)] : stampsIn(child),
  )

let cells: Cell[] = []
const observers: (() => void)[] = []
const body = new Node("tbody")
// The session page's subline: the box the page's script writes its header stamp into.
const subline = new Node("div")
// The document's root: the subtree holding the body and the subline, so the deco's own selector
// reaches what the page serves.
const page = new Node("html")
subline.attrs.id = "subline"
subline.attrs.class = "sub"
subline.className = "sub"
// The page's script appends to the subline, and the deco's observer on it is what carries the stamp
// in: every append there is a change the sweep was registered for.
subline.append = (...nodes: (Node | string)[]) => {
  subline.childNodes.push(...nodes)
  for (const react of observers) react()
}
subline.querySelectorAll = (selector: string): unknown[] => (selector === "time" ? stampsIn(subline) : [])
body.querySelectorAll = (selector: string): unknown[] => (selector === ".moments" ? cellsIn(body) : [])
body.replaceChildren = (...nodes: Node[]) => {
  body.childNodes = nodes
  for (const react of observers) react()
}
page.childNodes.push(subline, body)

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
    querySelectorAll: (selector: string) => {
      if (selector !== MOMENTS) return []
      // The deco's own selector, split on its commas: `.moments` is the cells this run holds and
      // `#subline time` the header stamp. A part this stand-in does not model is a failure, never a
      // quiet miss that a test reads as a sweep with nothing to do.
      return MOMENTS.split(",").flatMap((part) => {
        const [narrowed, target] = part.trim().split(/\s+/)
        if (narrowed === "#subline" && target === "time") return stampsIn(subline)
        if (target || narrowed !== ".moments") {
          throw new Error(`the stand-in answers no ${part.trim()}: the deco's MOMENTS grew a form it does not model`)
        }
        // The cells this run holds, or the ones the page carries — the rows' own, each built once
        // and kept in the ledger so a cell drawn and swept is the cell the test reads back.
        return cells.length ? cells : cellsIn(body)
      })
    },
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
  // The index's own script reads the URL's state back into the controls and writes it there again;
  // this run opens the page at its bare path, so the markup's own states are the page's.
  location: { pathname: "/profiler/", search: "" },
  history: { replaceState: () => {} },
})

if ("cells" in input) {
  cells = input.cells.map((served) => new Cell(served, ""))
  new Function(source)()
} else if ("index" in input) {
  // The index's own script runs first and its fetch settles after it; the deco loads before those
  // rows arrive — the served page's script order — so its sweep sees the empty body at load and each
  // drawn cell on the change its arrival makes.
  const scripts = [...input.index.matchAll(BLOCK)]
  new Function(scripts[0][1])()
  new Function(source)()
  await new Promise((resolve) => setTimeout(resolve, 0))
  for (const react of observers) react()
} else {
  // A session page is the reverse: the deco loads before the page's script, and the stamp's arrival
  // in the subline is the change its observer carries in.
  new Function(source)()
  new Function([...input.page.matchAll(BLOCK)][0][1])()
  for (const react of observers) react()
}


console.log(
  JSON.stringify({
    readings: cells.map((cell) => cell.textContent),
    titles: cells.map((cell) => cell.title),
    markup: cells.map((cell) => cell.html()),
    drawn: [...drawn].map(([node, cell]) => [node.html(), cell.textContent]),
    stamped: stampsIn(subline).map((cell) => [cell.textContent, cell.title]),
  }),
)
