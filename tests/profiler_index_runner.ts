// Runs the served index's own row-rendering script over a feed, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_index_runner.ts
// Stdin: JSON {index, feed, actions?}: the served `/profiler/` page, the feed its script reads, and
// optionally the controls a reader drives after the feed settles — each `{toggle: <input id>}` a
// checkbox's `change`, each `{sort: <head data-sort>}` a column head's `click`, and `{fail: {status,
// body}}` a feed that answers that status instead of the feed, its body read where the status is ok.
// Stdout: JSON {rows, keys, fetches, notices, controls}: each row the script drew as its markup, the
// feed-entry keys the script read, the paths it fetched in order, the notices the page showed, and
// each control's state after the presses.
//
// The page's script is run against a document that is what the template says it is — the `#rows`
// body, the empty notice, the static controls and column heads its text carries, and the element
// factory — and a `fetch` that answers the feed the test hands it. The keys the script reads are
// recorded by wrapping each parsed entry in a proxy, so the run names the schema the script consumes
// rather than the one a reader of the script believes. The controls are read from the served page's
// own markup, so a page whose controls the script names differently from the template is a state no
// press reaches.

import { readFileSync } from "node:fs"

type Action = { toggle?: string; sort?: string; fail?: { status: number; body?: unknown } }
type Input = { index: string; feed: object[]; actions?: Action[] }

const input: Input = JSON.parse(await Bun.stdin.text())
const BLOCK = /<script>([\s\S]*?)<\/script>/g
const scripts = [...input.index.matchAll(BLOCK)].map(([, body]) => body)
if (scripts.length !== 1) throw new Error(`the page carries ${scripts.length} scripts; its rows' one is expected`)

// One element, as markup: the tag, its attributes, its text and its children in order.
class Node {
  tag: string
  attrs: Record<string, string> = {}
  childNodes: (Node | string)[] = []
  className = ""
  listeners: Record<string, (() => void)[]> = {}
  // A checkbox's state, the property the page's script reads and a press switches.
  checked = false
  // The `<th>` a column head's button stands in, where it stands in one: the cell `closest('th')`
  // finds, and the one `aria-sort` belongs on.
  cell: Node | null = null

  closest(selector: string): Node | null {
    return selector === "th" ? this.cell : null
  }

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

  set colSpan(span: number | string) {
    this.attrs.colspan = String(span)
  }

  set hidden(hidden: boolean) {
    this.attrs.hidden = String(hidden)
  }

  get hidden(): boolean {
    return this.attrs.hidden === "true"
  }

  set disabled(disabled: boolean) {
    if (disabled) this.attrs.disabled = ""
    else delete this.attrs.disabled
  }

  get dataset(): Record<string, string> {
    return { sort: this.attrs["data-sort"] ?? "" }
  }

  setAttribute(name: string, value: string) {
    this.attrs[name] = value
  }

  removeAttribute(name: string) {
    delete this.attrs[name]
  }

  getAttribute(name: string) {
    return this.attrs[name] ?? null
  }

  addEventListener(event: string, listener: () => void) {
    ;(this.listeners[event] ??= []).push(listener)
  }

  fire(event: string) {
    for (const listener of this.listeners[event] ?? []) listener()
  }

  append(...nodes: (Node | string)[]) {
    this.childNodes.push(...nodes)
  }

  replaceChildren(...nodes: Node[]) {
    this.childNodes = nodes
  }

  html(): string {
    const attrs = Object.entries({ ...this.attrs, ...(this.className ? { class: this.className } : {}) })
      .filter(([, value]) => value !== undefined)
      .map(([name, value]) => ` ${name}="${value}"`)
      .join("")
    const inner = this.childNodes.map((child) => (typeof child === "string" ? child : child.html())).join("")
    return `<${this.tag}${attrs}>${inner}</${this.tag}>`
  }
}

const body = new Node("tbody")
const notice = new Node("p")
notice.hidden = true
const keys = new Set<string>()
const fetches: string[] = []

// The page's static controls and column heads, built from the served markup in document order, so
// the ids and `data-sort` keys the script binds are the page's own. A `<th>` that holds a button
// joins it as the cell the press takes, the way the page's own `closest('th')` does.
const staticNodes = (html: string): Node[] => {
  const found: Node[] = []
  let head: Node | null = null
  for (const [, tag, attrs] of html.matchAll(/<(th|input|button)\b([^>]*)>/g)) {
    if (tag === "th") head = new Node("th")
    const node = new Node(tag)
    for (const [, name, value] of attrs.matchAll(/([\w-]+)(?:="([^"]*)")?/g)) node.attrs[name] = value ?? ""
    if (tag === "input") node.checked = "checked" in node.attrs
    if (tag === "button" && head) node.cell = head
    if (tag !== "th") found.push(node)
  }
  return found
}
const statics = staticNodes(input.index)
const byId = new Map(statics.filter((node) => node.attrs.id).map((node) => [node.attrs.id, node]))

// Every property the script reads on a feed entry, at any depth, is the key it reads.
const watched = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(watched)
  if (value === null || typeof value !== "object") return value
  return new Proxy(value, {
    get(target, property) {
      if (typeof property === "string") keys.add(property)
      return watched((target as Record<string | symbol, unknown>)[property])
    },
  })
}

let failure: { status: number; body: unknown } | null = null

Object.assign(globalThis, {
  document: {
    createElement: (tag: string) => new Node(tag),
    getElementById: (id: string) => (id === "rows" ? body : id === "notice" ? notice : (byId.get(id) ?? null)),
    querySelector: () => null,
    querySelectorAll: (selector: string) =>
      selector === ".sort"
        ? statics.filter((node) => node.tag === "button" && node.cell !== null)
        : statics.filter((node) => node.tag === "input"),
  },
  // The page's URL and its history: the state the controls and the sort carry is written back into
  // them (`sync`), and the query the page opened at is read back into the controls (`restore`). The
  // page opens at its bare path here, so the state starts as the markup serves it.
  location: { pathname: "/profiler/", search: "" },
  history: { replaceState: (_state: unknown, _title: string, _next: string) => {} },
  fetch: async (path: string) => {
    fetches.push(path)
    if (failure !== null) return { ok: failure.status < 400, status: failure.status, json: async () => watched(failure.body ?? {}) }
    return { ok: true, status: 200, json: async () => watched(input.feed) }
  },
  setInterval: () => 0,
})

// The page's script runs with a quiet console; the runner's own output restores the real one.
const running = console
globalThis.console = { warn: () => {}, log: () => {} }
const rows = () => body.childNodes.map((child) => (typeof child === "string" ? child : child.html()))
// What the page shows before any press: the notice hidden and its text empty, and no row drawn. A
// test asserting the notice a failed feed raises needs the state it was raised from, since a notice
// the page opened with is no feed's failure.
const before = { hidden: notice.hidden, text: notice.textContent, rows: rows() }
new Function(scripts[0])()
// The script's fetch is a promise chain; one turn of the microtask queue settles it.
await new Promise((resolve) => setTimeout(resolve, 0))

// The reader's own presses, in the order the test names them: a control's switch and a head's press.
// A `{fail}` re-runs the page's script against a feed answering that status, the page's notice then
// holding the message its own failure path composed.
for (const action of input.actions ?? []) {
  if (action.fail !== undefined) {
    failure = action.fail
    body.childNodes = []
    await new Function(scripts[0])()
    await new Promise((resolve) => setTimeout(resolve, 0))
  } else if (action.toggle) {
    const control = byId.get(action.toggle)
    if (!control) throw new Error(`the page carries no control ${action.toggle}`)
    control.checked = !control.checked
    control.fire("change")
  } else if (action.sort) {
    const head = statics.find((node) => node.tag === "button" && node.attrs["data-sort"] === action.sort)
    if (!head) throw new Error(`the page carries no head sorting on ${action.sort}`)
    head.fire("click")
  }
}
globalThis.console = running

// Each column head's sort state, read off the `<th>` the press marks: the cell's `aria-sort`, or
// `none` where the page does not say.
const sorts = statics
  .filter((node) => node.tag === "button" && node.cell !== null)
  .map((node) => [node.attrs["data-sort"], (node.cell as Node).attrs["aria-sort"] ?? "none"])
// Each control's state as the page leaves it: checked, and disabled where it can hide nothing.
const controls = Object.fromEntries(
  statics
    .filter((node) => node.tag === "input")
    .map((node) => [node.attrs.id, { checked: node.checked, disabled: "disabled" in node.attrs }]),
)
running.log(
  JSON.stringify({
    rows: rows(),
    keys: [...keys].sort(),
    fetches,
    sorts,
    controls,
    before,
    notices: notice.hidden ? [] : [notice.textContent],
  }),
)
