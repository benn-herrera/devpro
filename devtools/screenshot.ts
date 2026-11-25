// The development loop's page screenshot: a page, settled, written as a PNG so the rendered result
// can be viewed and iterated on. Run as `bun devtools/screenshot.ts <page> [options]` (justfile
// `screenshot`); never imported.
//
// The browser is the `firefox` on PATH, which the host's package manager owns; `puppeteer-core` is
// the driver, speaking WebDriver BiDi to it, so no browser is downloaded and the profile, the flags
// and the handshake are its own. Nothing here asserts anything about the pixels: the output is the
// picture, for a reader's eye.
//
// `page` is one of three forms — an `http://` or `https://` URL; a route starting with `/`, resolved
// against `--base`; a file path, opened as its `file://` URL. `--base` decides the form of a
// `/`-path, before any filesystem test: with it the path is a route, and without it the path is
// looked for on disk. Settle is in order: the load holds network idle, the fonts are ready, and the
// `--wait-for` selector appears where one is given. Each step is bounded by `--timeout`, as is the
// color scheme's check, which runs before the shot so a page shown in the wrong scheme writes no PNG.
//
// Exit codes: 0 prints the PNG's absolute path and nothing else; 2 is a usage error; 1 is a page that
// failed to load or settle, or no `firefox` on PATH, and no PNG is written. `--help` prints the usage
// and exits 0. The browser closes on every path, the failure's included.
import { accessSync, constants, existsSync, mkdirSync, statSync } from "node:fs"
import { delimiter, dirname, join, resolve } from "node:path"
import { pathToFileURL } from "node:url"
import { parseArgs } from "node:util"
import puppeteer, { type Browser, type Page } from "puppeteer-core"

// The defaults `--help` lists: the recipe passes its arguments through, and the tool holds them.
const DEFAULT_VIEWPORT = "1280x800"
const DEFAULT_COLOR_SCHEME = "light"
const DEFAULT_TIMEOUT_MS = 30_000
// Under the repository root, beside the project's other scratch.
const DEFAULT_OUT_DIR = join(import.meta.dirname, "..", ".devpro-temp", "screenshots")

const USAGE = `usage: bun devtools/screenshot.ts <page> [options]

  <page>                  an http(s) URL, a route starting with / (needs --base), or a file path
  --base <url>            the URL a route is resolved against (no default)
  --viewport <W>x<H>      the viewport (default ${DEFAULT_VIEWPORT})
  --wait-for <selector>   a selector to wait for after the load settles (no default)
  --color-scheme light|dark
                          the page's color scheme (default ${DEFAULT_COLOR_SCHEME})
  --out <png>             the file written (default .devpro-temp/screenshots/<slug>.png)
  --timeout <ms>          the bound on each settle step (default ${DEFAULT_TIMEOUT_MS})`

// A failure as the run reports it: the message printed on stderr, and the exit code that says whether
// the command line was wrong (2) or the run could not finish (1).
class ScreenshotError extends Error {
  readonly exitCode: 1 | 2

  constructor(message: string, exitCode: 1 | 2, options?: ErrorOptions) {
    super(message, options)
    this.name = "ScreenshotError"
    this.exitCode = exitCode
  }
}

function usage(message: string): ScreenshotError {
  return new ScreenshotError(`${message}\n\n${USAGE}`, 2)
}

interface Options {
  page: string
  base: string | undefined
  width: number
  height: number
  waitFor: string | undefined
  colorScheme: "light" | "dark"
  out: string | undefined
  timeoutMs: number
}

function positive(text: string | undefined, option: string): number {
  const value = Number(text)
  if (text === undefined || text.trim() === "" || !Number.isInteger(value) || value <= 0) {
    throw usage(`${option} takes a positive whole number, not ${JSON.stringify(text)}`)
  }
  return value
}

// `WxH`, both positive whole numbers.
function viewport(text: string): { width: number; height: number } {
  const match = /^(\d+)x(\d+)$/.exec(text)
  if (!match) throw usage(`--viewport takes <W>x<H>, not ${JSON.stringify(text)}`)
  const [, w, h] = match
  return { width: positive(w, "--viewport"), height: positive(h, "--viewport") }
}

// The parsed command line, or the usage text where `--help` was asked for: asking for help is not a
// usage error, so the caller prints it and exits 0.
function options(argv: string[]): Options | string {
  let parsed
  try {
    parsed = parseArgs({
      args: argv,
      allowPositionals: true,
      options: {
        base: { type: "string" },
        viewport: { type: "string", default: DEFAULT_VIEWPORT },
        "wait-for": { type: "string" },
        "color-scheme": { type: "string", default: DEFAULT_COLOR_SCHEME },
        out: { type: "string" },
        timeout: { type: "string", default: String(DEFAULT_TIMEOUT_MS) },
        help: { type: "boolean", short: "h" },
      },
    })
  } catch (err) {
    // `parseArgs` states what the command line got wrong; it rides in the usage error as written.
    throw usage(err instanceof Error ? err.message.split("\n")[0] ?? err.message : String(err))
  }
  const { values, positionals } = parsed
  if (values.help) return USAGE
  if (positionals.length !== 1) {
    throw usage(positionals.length === 0 ? "a page is required" : `one page is taken, not ${positionals.length}`)
  }
  const scheme = values["color-scheme"]
  if (scheme !== "light" && scheme !== "dark") {
    throw usage(`--color-scheme takes light or dark, not ${JSON.stringify(scheme)}`)
  }
  const { width, height } = viewport(values.viewport)
  return {
    page: positionals[0],
    base: values.base,
    width,
    height,
    waitFor: values["wait-for"],
    colorScheme: scheme,
    out: values.out,
    timeoutMs: positive(values.timeout, "--timeout"),
  }
}

// The URL a page form names: a URL as it stands, a route resolved against `--base`, a file path as
// its `file://` URL. `--base` decides a `/`-path's form before any filesystem test, because every
// route starts with `/` and an absolute path that exists on disk — `/`, the dashboard's index — would
// otherwise be read as a file.
function targetUrl(page: string, base: string | undefined): string {
  if (/^https?:\/\//.test(page)) return page
  if (page.startsWith("/")) {
    if (base === undefined) {
      const path = resolve(page)
      if (existsSync(path)) return pathToFileURL(path).href
      throw usage(`the route ${page} needs --base <url> to resolve against, and no such file: ${path}`)
    }
    let origin: URL
    try {
      origin = new URL(base)
    } catch {
      throw usage(`--base takes a URL, not ${JSON.stringify(base)}`)
    }
    return new URL(page, origin).href
  }
  const path = resolve(page)
  if (existsSync(path)) return pathToFileURL(path).href
  throw usage(`no such file: ${path} — pass an http(s) URL, a /route with --base, or a file`)
}

// The page's host and path, each run of characters outside the set replaced by `_`, and `index`
// where nothing is left. A file's path is read decoded, so `%20` spells its space.
function slug(url: string): string {
  const { host, pathname, protocol } = new URL(url)
  const path = protocol === "file:" ? decodeURIComponent(pathname) : pathname
  return `${host}${path}`.replaceAll(/[^A-Za-z0-9._-]+/g, "_") || "index"
}

// The executable `name` on PATH, as a shell's command lookup finds it: a regular file with the
// execute bit, so a directory sharing the name is not mistaken for the browser.
function onPath(name: string): string | undefined {
  for (const dir of (process.env.PATH ?? "").split(delimiter)) {
    const path = join(dir === "" ? "." : dir, name)
    try {
      accessSync(path, constants.X_OK)
      if (statSync(path).isFile()) return path
    } catch {}
  }
  return undefined
}

function isTimeout(err: unknown): boolean {
  if (!(err instanceof Error)) return false
  return err.name === "TimeoutError" || err.name === "Timeout" || /timeout/i.test(err.message)
}

// A failure's cause, one line: the driver's protocol errors carry the browser's own stack after the
// message, which names the run's problem no better than the message does.
function reason(err: unknown): string {
  if (!(err instanceof Error)) return String(err)
  return err.message.split("\n")[0] ?? err.message
}

// Rejects after `ms`, so a wait the driver does not bound can be raced against one that is.
function after(ms: number, what: string): Promise<never> {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error(`${what} did not finish within ${ms} ms`)), ms)
  })
}

// The color scheme the page is shown in. Firefox 160 over WebDriver BiDi takes no media emulation
// from the driver (`emulateMediaFeatures` asks for CDP, which the connection has none of), so the
// `prefers-color-scheme` Firefox's own preference sets at launch carries it: the page's `matchMedia`
// reports the scheme the run asked for, and a scheme it did not report fails the run rather than
// leaving a screenshot in the wrong one.
async function scheme(page: Page, opts: Options): Promise<void> {
  const ms = opts.timeoutMs
  let shown: unknown
  try {
    shown = await Promise.race([
      page.evaluate(() => globalThis.matchMedia("(prefers-color-scheme: dark)").matches),
      after(ms, "reading the page's color scheme"),
    ])
  } catch (err) {
    throw new Error(`reading the color scheme of the page failed: ${reason(err)}`, { cause: err })
  }
  const wanted = opts.colorScheme === "dark"
  if (shown !== wanted) {
    throw new Error(`the browser shows ${shown === true ? "dark" : "light"} where --color-scheme ${opts.colorScheme} was asked for`)
  }
}

// Settles the page and writes its full-page screenshot. Every failure is thrown described, so the
// caller prints one cause. The scheme is checked once the load has landed and before the shot, so a
// page shown in the wrong scheme leaves no file behind.
async function shoot(page: Page, target: string, opts: Options, out: string): Promise<void> {
  const ms = opts.timeoutMs
  try {
    await page.goto(target, { waitUntil: "networkidle0", timeout: ms })
  } catch (err) {
    const what = isTimeout(err) ? `loading ${target} did not settle within ${ms} ms` : `loading ${target} failed`
    throw new Error(`${what}: ${reason(err)}`, { cause: err })
  }
  await scheme(page, opts)
  try {
    await Promise.race([page.evaluate(() => globalThis.document.fonts.ready), after(ms, "the page's fonts")])
  } catch (err) {
    throw new Error(`the fonts of ${target} were not ready within ${ms} ms: ${reason(err)}`, { cause: err })
  }
  if (opts.waitFor !== undefined) {
    try {
      await page.waitForSelector(opts.waitFor, { timeout: ms })
    } catch (err) {
      const what = isTimeout(err)
        ? `${opts.waitFor} did not appear within ${ms} ms`
        : `waiting for ${opts.waitFor} failed`
      throw new Error(`${what}: ${reason(err)}`, { cause: err })
    }
  }
  try {
    await page.screenshot({ path: out, fullPage: true })
  } catch (err) {
    throw new Error(`writing ${out} failed: ${reason(err)}`, { cause: err })
  }
}

async function main(argv: string[]): Promise<string> {
  const opts = options(argv)
  if (typeof opts === "string") return opts
  const target = targetUrl(opts.page, opts.base)
  const executablePath = onPath("firefox")
  if (executablePath === undefined) {
    throw new ScreenshotError("error: the screenshot tool requires firefox on PATH", 1)
  }
  const out = opts.out === undefined ? join(DEFAULT_OUT_DIR, `${slug(target)}.png`) : resolve(opts.out)
  mkdirSync(dirname(out), { recursive: true })

  let browser: Browser | undefined
  try {
    try {
      browser = await puppeteer.launch({
        browser: "firefox",
        executablePath,
        headless: true,
        protocol: "webDriverBiDi",
        // Every driver call bounded by the run's own timeout, the protocol's 180 s default otherwise.
        protocolTimeout: opts.timeoutMs,
        // Firefox's preference names the scheme its content is shown in: 0 dark, 1 light, 2 the
        // system's.
        extraPrefsFirefox: { "layout.css.prefers-color-scheme.content-override": opts.colorScheme === "dark" ? 0 : 1 },
      })
    } catch (err) {
      throw new Error(`starting ${executablePath} failed: ${reason(err)}`, { cause: err })
    }
    const page = await browser.newPage()
    await page.setViewport({ width: opts.width, height: opts.height })
    await shoot(page, target, opts, out)
  } catch (err) {
    // Each step's failure is an `Error` naming its step, so it is reported as composed, never run
    // through `reason()` again: that would cut a selector the tool was given.
    if (err instanceof ScreenshotError) throw err
    throw new ScreenshotError(`error: ${err instanceof Error ? err.message : String(err)}`, 1, { cause: err })
  } finally {
    // A close that fails or hangs is the run's cleanup, not its result: it never replaces the error
    // the shot raised, and it never holds the process past the run's own bound.
    if (browser !== undefined) {
      await Promise.race([browser.close().catch(() => {}), after(opts.timeoutMs, "closing the browser").catch(() => {})])
    }
  }
  return out
}

try {
  process.stdout.write(`${await main(process.argv.slice(2))}\n`)
} catch (err) {
  process.stderr.write(`${err instanceof ScreenshotError ? err.message : `error: ${reason(err)}`}\n`)
  process.exitCode = err instanceof ScreenshotError ? err.exitCode : 1
}
