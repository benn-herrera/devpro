// Runs the served index's own row-rendering script over a feed, for tests/test_devpro_profiler.py.
//
// Usage: bun tests/profiler_index_runner.ts
// Stdin: JSON {index}: the served `/profiler/` page.
// Stdout: JSON {rows, keys, fetches}: each row the script drew as its markup, the feed-entry keys the
// script read, and the paths it fetched, in order.
//
// The page's script is run against a document that is what the template says it is — the `#rows`
// body and the element factory — and a `fetch` that answers the feed the test hands it. The keys the
// script reads are recorded by wrapping each parsed entry in a proxy, so the run names the schema
// the script consumes rather than the one a reader of the script believes.

import { readFileSync } from "node:fs"

type Input = { index: string; feed: object[] }

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
  }

  html(): string {
    const attrs = Object.entries({ ...this.attrs, ...(this.className ? { class: this.className } : {}) })
      .map(([name, value]) => ` ${name}="${value}"`)
      .join("")
    const inner = this.childNodes.map((child) => (typeof child === "string" ? child : child.html())).join("")
    return `<${this.tag}${attrs}>${inner}</${this.tag}>`
  }
}

const body = new Node("tbody")
const keys = new Set<string>()
const fetches: string[] = []

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

Object.assign(globalThis, {
  document: {
    createElement: (tag: string) => new Node(tag),
    getElementById: (id: string) => (id === "rows" ? body : null),
    querySelector: () => null,
    querySelectorAll: () => [],
  },
  fetch: async (path: string) => {
    fetches.push(path)
    return { ok: true, status: 200, json: async () => watched(input.feed) }
  },
  setInterval: () => 0,
})

// The page's script runs with a quiet console; the runner's own output restores the real one.
const running = console
globalThis.console = { warn: () => {}, log: () => {} }
const rows = () => body.childNodes.map((child) => (typeof child === "string" ? child : child.html()))
new Function(scripts[0])()
// The script's fetch is a promise chain; one turn of the microtask queue settles it.
await new Promise((resolve) => setTimeout(resolve, 0))
globalThis.console = running

running.log(JSON.stringify({ rows: rows(), keys: [...keys].sort(), fetches }))
