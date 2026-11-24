// Runs the served index in a browser's own shape, for tests/test_devpro_profiler.py: the page's
// scripts — the deco's file and the index template's own, in the order the page loads them — in one
// shared classic-script scope, over a document laid out the way a browser lays a table out, so what
// is measured is what a reader sees.
//
// Usage: bun tests/profiler_browser_runner.ts
// Stdin: JSON {index, deco, feed, actions?}: the served `/profiler/` page, the deco's own source, the
// feed the page's script fetches, and the reader's presses and visits in order — each `{toggle: <input
// id>}` a checkbox's `change`, each `{sort: <head data-sort>}` a column head's `click`, each
// `{navigate: <query | true>}` a visit to the page's own URL at that query — the string a hand-edited
// link carries, `true` the state the page stands at, `""` the page's closed state.
// Stdout: JSON {headers, sessionCells, rows, visits}: for the page as first drawn, each column's
// `[label, columnWidth, headerWidth]` — the widest cell of the column and the `<th>`'s own box over it,
// both in CSS pixels — each row's session cell as the page wrote it, the rows' markup, and, for every
// visit, the URL the page stands at, whether its scripts ran, each control's state and each head's
// sort.

type Action = { toggle?: string; sort?: string; navigate?: true | string }
type Input = { index: string; deco: string; feed: object[]; actions?: Action[] }
type Page = {
  url: string
  drawn: boolean
  error?: string
  controls: Record<string, boolean>
  sorts: [string, string][]
}

const input: Input = JSON.parse(await Bun.stdin.text())
const INLINE = [...input.index.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(([, body]) => body)
if (INLINE.length !== 1) throw new Error(`the page carries ${INLINE.length} inline scripts; its rows' one is expected`)

// A cell's text in the page's default font, a table cell's padding and border: fixed, so a run is the
// same everywhere, and never narrower than a browser's rendering of the same text.
const CHAR = 7.2
const PADDING = 16
const BORDER = 2

class Node {
  tag: string
  attrs: Record<string, string> = {}
  childNodes: (Node | string)[] = []
  className = ""
  listeners: Record<string, (() => void)[]> = {}
  checked = false
  // The `<th>` a column head's button stands in, where it stands in one.
  cell: Node | null = null
  // What a checkbox carries into the page's state, when it is checked.
  name = ""
  value = "on"
  private written: string | null = null

  constructor(tag: string) {
    this.tag = tag
  }

  closest(selector: string): Node | null {
    return selector === "th" ? this.cell : null
  }

  // The element's text as a browser reads it: what was written into it whole where the scripts wrote
  // one, otherwise its children's texts in order. The getter stands before its setter: a field of the
  // same name declared between them would be the property instead, and the page's writes lost.
  get textContent(): string {
    if (this.written !== null) return this.written
    return this.childNodes.map((child) => (typeof child === "string" ? child : child.textContent)).join("")
  }

  set textContent(text: string) {
    this.written = String(text)
    this.childNodes = []
  }

  set href(href: string) {
    this.attrs.href = href
  }

  set title(title: string) {
    this.attrs.title = title
  }

  set colSpan(span: string | number) {
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

  get disabled(): boolean {
    return "disabled" in this.attrs
  }

  set dateTime(value: string) {
    this.attrs.datetime = value
  }

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

  fire(event: string) {
    for (const listener of this.listeners[event] ?? []) listener()
  }

  // A subtree's elements of one kind: a selector naming a tag answers that tag, and one naming a
  // class by its dot answers the elements carrying it — the two forms the pages' scripts use.
  querySelectorAll(selector: string): Node[] {
    const wanted = selector.replace(/^\./, "")
    return elements(this).flatMap((child) => [
      ...(child.tag === wanted || (selector.startsWith(".") && child.className === wanted) ? [child] : []),
      ...child.querySelectorAll(selector),
    ])
  }

  // A cell's own text as a browser reads it: its text nodes' texts, with each element's own. The
  // nodes are the page's — an element the page built holds the text it was given.
  get ownText(): string {
    return this.childNodes.map((child) => (typeof child === "string" ? child : child.textContent)).join("")
  }

  // A subtree's markup as a browser parses it, for a cell the page carried: an element's opening tag,
  // its text and its closing tag, nested where the markup nests them.
  appendMarkup(markup: string) {
    const open = /^<(\w+)([^>]*)>([\s\S]*)<\/\1>$/.exec(markup)
    if (!open) {
      this.childNodes.push(markup)
      return
    }
    const node = new Node(open[1])
    for (const [, name, value] of open[2].matchAll(/([\w-]+)(?:="([^"]*)")?/g)) node.attrs[name] = value ?? ""
    node.className = node.attrs.class ?? ""
    if (node.tag === "button") node.cell = this.tag === "th" ? this : null
    node.appendMarkup(open[3])
    this.append(node)
  }

  append(...nodes: (Node | string)[]) {
    this.written = null
    this.childNodes.push(...nodes)
  }

  replaceChildren(...nodes: Node[]) {
    this.written = null
    this.childNodes = nodes
  }

  // The subtree's markup as it stands, for the test's own view of the rows.
  html(): string {
    const attrs = Object.entries(this.attrs)
      .map(([name, value]) => ` ${name}="${value}"`)
      .join("")
    const inner = elements(this).map((child) => child.html()).join("") || this.textContent
    return `<${this.tag}${attrs}>${inner}</${this.tag}>`
  }
}

const elements = (node: Node): Node[] => node.childNodes.filter((child): child is Node => typeof child !== "string")
const cellsIn = (row: Node): Node[] => elements(row).filter((cell) => cell.tag === "td")
// A body row as the table draws it — a row that spans the table belongs to no column.
const rowsOf = (): Node[] => elements(body).filter((row) => row.tag === "tr" && cellsIn(row).length > 1)
// A cell's own box: its longest line at the cell's font, plus the cell's padding and its border — the
// width a browser keeps the cell's text at on one line. A header's font is the page's own 0.85rem.
const boxOf = (cell: Node): number =>
  Math.max(...[0, ...cell.textContent.split("\n").map((line) => [...line].length)]) * CHAR * (cell.tag === "th" ? 0.85 : 1) +
  PADDING +
  BORDER
// The table's columns as a browser lays them out. A column's width is the one the page's stylesheet
// declares for it — the table's `table-layout: fixed` shares it with header and body alike — and
// otherwise the widest cell of the column, the browser's own rule for a table laid out by content.
const REM = 16
const VIEWPORT = 1024
const declared = new Map<string, string>()
for (const [, rule, size] of input.index.matchAll(/\.(col-[\w-]+)\s*\{\s*width:\s*([\d.]+(?:rem|%))/g)) {
  declared.set(rule, size)
}
// The width a class declares, in pixels: `rem` against the page's own root size, `%` against the
// viewport the table is laid out at.
const widthOf = (size: string): number =>
  size.endsWith("%") ? (Number(size.slice(0, -1)) / 100) * VIEWPORT : Number(size.slice(0, -3)) * REM
// The box a cell resolves to: the width its class declares, where it declares one, and otherwise its
// own text's width with its padding and border.
const boxFor = (cell: Node): number => {
  const classes = `${cell.className} ${cell.attrs.class ?? ""}`.split(" ")
  const size = declared.get(classes.find((name) => declared.has(name)) ?? "")
  return size === undefined ? boxOf(cell) : widthOf(size)
}
// Each column's header box and the box of the widest cell under it.
const layout = (): [string, number, number][] => {
  const rows = rowsOf()
  return heads.map((head, index) => {
    const cells = rows.map((row) => cellsIn(row)[index]).filter((cell): cell is Node => cell !== undefined)
    return [head.textContent, Math.max(...cells.map(boxFor)), boxFor(head)]
  })
}

// The page's static parts: the header row the template carries, the controls it carries, and the two
// elements its own script asks for by id.
const body = new Node("tbody")
body.attrs.id = "rows"
const notice = new Node("p")
notice.attrs.id = "notice"
notice.hidden = true
const headRow = new Node("tr")
const controls: Node[] = []
const byId = new Map<string, Node>([
  ["rows", body],
  ["notice", notice],
])
for (const [, markup] of input.index.matchAll(/<thead>([\s\S]*?)<\/thead>/g)) {
  for (const [, attrs, inner] of markup.matchAll(/<th\b([^>]*)>([\s\S]*?)<\/th>/g)) {
    const head = new Node("th")
    for (const [, name, value] of attrs.matchAll(/([\w-]+)(?:="([^"]*)")?/g)) head.attrs[name] = value ?? ""
    head.className = head.attrs.class ?? ""
    head.appendMarkup(inner)
    headRow.append(head)
  }
}
for (const [, attrs] of input.index.matchAll(/<input\b([^>]*)>/g)) {
  const control = new Node("input")
  for (const [, name, value] of attrs.matchAll(/([\w-]+)(?:="([^"]*)")?/g)) control.attrs[name] = value ?? ""
  control.checked = "checked" in control.attrs
  control.name = control.attrs.name ?? ""
  control.value = control.attrs.value ?? "on"
  controls.push(control)
  if (control.attrs.id) byId.set(control.attrs.id, control)
}
const heads = elements(headRow)
const buttonOf = (head: Node): Node | undefined => elements(head)[0]

// The page's state as its URL carries it: the controls the reader left checked, by their own names and
// values, and the head the table sorts on with the order it stands in.
const state = (): string => {
  const params = new URLSearchParams()
  for (const control of controls) if (control.name && !control.checked) params.append(control.name, control.value)
  for (const head of heads) {
    const order = head.attrs["aria-sort"] ?? "none"
    const button = buttonOf(head)
    if (button && order !== "none") {
      params.append("sort", button.attrs["data-sort"] + (order === "descending" ? "-descending" : ""))
    }
  }
  const query = params.toString()
  return query ? "?" + query : ""
}

// One visit: a document of its own at the query the visit carries, the page's scripts run over it in
// the order the markup loads them — sharing one global scope, as a page's classic scripts do, so a
// helper the second script declares a second time is the error the page throws before it draws
// anything — and the feed's answer waited for.
const visit = async (query: string): Promise<Page> => {
  const here = "http://127.0.0.1:0/profiler/" + query
  let url = here
  let drawn = false
  let error: string | undefined
  // A document of its own: the controls and the heads as the markup serves them, the page's script
  // reading the URL's state back into them.
  for (const control of controls) control.checked = "checked" in control.attrs
  for (const head of heads) head.attrs["aria-sort"] = head.attrs["aria-sort"] ?? "none"
  const observers: (() => void)[] = []
  body.replaceChildren = (...nodes: Node[]) => {
    body.childNodes = nodes
    for (const react of observers) react()
  }
  Object.assign(globalThis, {
    location: { pathname: "/profiler/", search: query, href: here },
    history: {
      replaceState: (_state: unknown, _title: string, next: string) => {
        url = new URL(next, here).href
      },
    },
    document: {
      createElement: (tag: string) => new Node(tag),
      getElementById: (id: string) => byId.get(id) ?? null,
      querySelector: () => null,
      querySelectorAll: (selector: string) =>
        selector === ".sort" ? heads.flatMap((head) => (buttonOf(head) ? [buttonOf(head)] : [])) : controls,
    },
    MutationObserver: class {
      constructor(private react: () => void) {}
      observe() {
        observers.push(this.react)
      }
    },
    fetch: async (path: string) => ({
      ok: true,
      status: 200,
      json: async () => (path.startsWith("/api/traces") ? input.feed : { state: "live" }),
    }),
    setInterval: () => 0,
    getComputedStyle: () => ({ getPropertyValue: () => "" }),
  })
  try {
    new Function([input.deco, ...INLINE].join("\n"))()
    drawn = true
  } catch (thrown) {
    error = String(thrown)
  }
  await new Promise((resolve) => setTimeout(resolve, 0))
  return {
    url,
    drawn,
    ...(error ? { error } : {}),
    controls: Object.fromEntries(controls.map((control) => [control.attrs.id, control.checked])),
    sorts: heads.map((head) => [buttonOf(head)?.attrs["data-sort"] ?? "", head.attrs["aria-sort"] ?? "none"]),
  }
}

const visits: Page[] = [await visit(state())]
const headers = layout()
const sessions = rowsOf().map((row) => (cellsIn(row)[1]?.textContent ?? "").split("\n")[0])
for (const action of input.actions ?? []) {
  if (action.navigate !== undefined) {
    // `true` is the page's own link — the state it stands at — and a string is the query itself, a
    // hand-edited one a reader can carry in.
    visits.push(await visit(action.navigate === true ? state() : String(action.navigate)))
    continue
  }
  if (action.toggle) {
    const control = byId.get(action.toggle)
    if (!control) throw new Error(`the page carries no control ${action.toggle}`)
    control.checked = !control.checked
    control.fire("change")
  }
  if (action.sort) {
    const head = heads.find((candidate) => buttonOf(candidate)?.attrs["data-sort"] === action.sort)
    if (!head) throw new Error(`the page carries no head sorting on ${action.sort}`)
    buttonOf(head)?.fire("click")
  }
  // The page as the press leaves it, read back: its URL, its controls and its heads.
  visits.push(await visit(state()))
}
console.log(JSON.stringify({ headers, sessionCells: sessions, rows: elements(body).map((row) => row.html()), visits }))
