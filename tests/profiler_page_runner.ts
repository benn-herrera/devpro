// Runs a session page's scripts the way its carrier loads them, for tests/test_devpro_profiler.py:
// the page's own inline script, with the deco's file the page names ahead of it where the carrier
// loads that file — a file carrier loads nothing, so it runs the page's script alone — in one shared
// classic-script scope, the way the browser executes a page: a helper redeclared across the scripts
// is the error the page throws before it draws anything.
//
// Usage: bun tests/profiler_page_runner.ts
// Stdin: JSON {page, deco?}: a session page's own text — the file flow's or the served page's — and
// the deco's own source where the page's carrier loads it.
// Stdout: JSON {stamped, subline}: one [text, title, datetime] per `<time>` the page's script drew
// into the subline — the header stamp's drawn reading, the raw UTC its title keeps and the machine
// form its `datetime` carries — and the subline's markup as the scripts left it.

type Input = { page: string; deco?: string }

const input: Input = JSON.parse(await Bun.stdin.text())
const INLINE = [...input.page.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(([, body]) => body)
if (INLINE.length !== 1) throw new Error(`the page carries ${INLINE.length} inline scripts; the session page's one is expected`)

// One element, as markup: the tag, its attributes, its text and its children in order. The page's
// script draws with the browser's own names — `createElement`, `textContent`, `dateTime`, `title` —
// so the stand-in carries them, and the drawn reading is what the page's reader sees.
class Node {
  tag: string
  attrs: Record<string, string> = {}
  childNodes: (Node | string)[] = []
  className = ""
  listeners: Record<string, (() => void)[]> = {}
  // A checkbox's state, the property the page's script reads.
  checked = false
  // The box that holds the page's diagram, as wide as the page's own: the sequence diagram measures
  // it.
  parentElement: Node = this
  clientWidth = 800

  constructor(tag: string) {
    this.tag = tag
  }

  set textContent(text: string) {
    this.childNodes = [text]
  }

  get textContent(): string {
    return this.childNodes.map((child) => (typeof child === "string" ? child : child.textContent)).join("")
  }

  set title(title: string) {
    this.attrs.title = title
  }

  set dateTime(value: string) {
    this.attrs.datetime = value
  }

  getAttribute(name: string): string | null {
    return this.attrs[name] ?? null
  }

  setAttribute(name: string, value: string) {
    this.attrs[name] = value
  }

  addEventListener(event: string, listener: () => void) {
    ;(this.listeners[event] ??= []).push(listener)
  }

  append(...nodes: (Node | string)[]) {
    this.childNodes.push(...nodes)
  }

  html(): string {
    const attrs = Object.entries({ ...this.attrs, ...(this.className ? { class: this.className } : {}) })
      .map(([name, value]) => ` ${name}="${value}"`)
      .join("")
    const inner = this.childNodes.map((child) => (typeof child === "string" ? child : child.html())).join("")
    return `<${this.tag}${attrs}>${inner}</${this.tag}>`
  }

  // A subtree's elements of one kind: a selector naming a tag answers that tag, and one naming a
  // class by its dot answers the elements carrying it.
  querySelectorAll(selector: string): Node[] {
    const wanted = selector.replace(/^\./, "")
    return this.childNodes.filter((child): child is Node => typeof child !== "string").flatMap((child) => [
      ...(child.tag === wanted || (selector.startsWith(".") && child.className === wanted) ? [child] : []),
      ...child.querySelectorAll(selector),
    ])
  }
}

// The page's own controls and buttons, built from the served markup in document order, and the ids
// the page's markup declares: the script binds by id, so an id the markup names stands as the
// element it names — an empty stand-in where the script only reads or draws into it.
const statics: Node[] = []
for (const [, tag, attrs] of input.page.matchAll(/<(input|button)\b([^>]*)>/g)) {
  const node = new Node(tag)
  for (const [, name, value] of attrs.matchAll(/([\w-]+)(?:="([^"]*)")?/g)) node.attrs[name] = value ?? ""
  if (tag === "input") node.checked = "checked" in node.attrs
  statics.push(node)
}
const declared = [...input.page.matchAll(/id="([^"]+)"/g)].map(([, id]) => id)
const byId = new Map(statics.filter((node) => node.attrs.id).map((node) => [node.attrs.id, node]))

// The subline, the box the page's script draws its header stamp into. Every append there is a
// change the page's observers were registered for — the deco's, where the carrier loads it — so the
// append fires them, the way a browser delivers the mutation after the task that made it.
const observers: (() => void)[] = []
const subline = new Node("div")
subline.attrs.id = "subline"
subline.attrs.class = "sub"
subline.className = "sub"
subline.append = (...nodes: (Node | string)[]) => {
  subline.childNodes.push(...nodes)
  for (const react of observers) react()
}

const elsewhere = new Map<string, Node>()
const elementFor = (id: string): Node => {
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
    querySelectorAll: () => [],
  },
  MutationObserver: class {
    constructor(private react: () => void) {}
    observe() {
      observers.push(this.react)
    }
  },
  fetch: async () => ({ ok: false, status: 0, json: async () => ({}) }),
  setInterval: () => 0,
  window: { addEventListener: () => {} },
  getComputedStyle: () => ({ getPropertyValue: () => "" }),
})

new Function([input.deco ?? "", ...INLINE].join("\n"))()
for (const react of observers) react()

const timesIn = (node: Node): Node[] =>
  node.childNodes.filter((child): child is Node => typeof child !== "string").flatMap((child) =>
    child.tag === "time" ? [child] : timesIn(child),
  )

console.log(
  JSON.stringify({
    stamped: timesIn(subline).map((time) => [time.textContent, time.attrs.title ?? "", time.attrs.datetime ?? ""]),
    subline: subline.html(),
  }),
)
