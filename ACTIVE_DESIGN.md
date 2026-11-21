# The profiler serves its pages over HTTP

opencode and claude sessions' recorded activity becomes browsable without file juggling: the
profiler's render path turns from file-out to serve-on-demand — `hp.py` renders pages in memory
behind a small HTTP server, the server's main page is the list of record files it can render, and a
runner target starts it on a free port with the URL on stdout for cmd-clicking, the way docdicer's
board serves. The records stay local: the server binds loopback only.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```markdown
`profiler/hp.sh`, `profiler/hp.py` and `profiler/view.html`, copied as they stand, and the
`show-profile` skill, which renders a session's recorded activity — its skill, agent and tool calls
with timings and token costs — as text or as a self-contained HTML page.
```

**Becomes:**

```markdown
`profiler/hp.sh`, `profiler/hp.py` and `profiler/view.html`, copied as they stand, and the
`show-profile` skill, which renders a session's recorded activity — its skill, agent and tool calls
with timings and token costs — as text, as a self-contained HTML page, or served over HTTP: the
tool's `serve` subcommand renders the record files in memory behind a local server whose main page
lists every record file it can render. The pages and the records stay local: reachable only from the
machine that runs the server.
```

## ARCHITECTURE delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```markdown
**Resources.** Three files live in `devpro/harnesses/resources/claude/profiler/`: `hp.sh`, the
POSIX-sh launcher that finds `python3` (`HP_PYTHON` overrides the search); `hp.py`, the whole tool —
`capture`, `tree`, `init`, `doctor` — one file, Python 3 standard library only, no dependency; and
```

**Becomes:**

```markdown
**Resources.** Three files live in `devpro/harnesses/resources/claude/profiler/`: `hp.sh`, the
POSIX-sh launcher that finds `python3` (`HP_PYTHON` overrides the search); `hp.py`, the whole tool —
`capture`, `tree`, `init`, `doctor`, `serve` — one file, Python 3 standard library only, no
dependency; and
```

**As it stands:**

```markdown
**The skill.** `show-profile` ships as a rendered skill definition under `devpro/definitions/skills/`,
```

**Becomes:**

```markdown
**Serving.** The `serve` subcommand renders in memory behind a local HTTP server: `hp serve` binds
`127.0.0.1` on a free port — `--port` pins one — and prints the served URL on stdout for
cmd-clicking. The bind is the rule, not a detail: the server listens on loopback only and loads
nothing from the network, so the records it renders never leave the machine. Its main page is the
index of record files: every store the `*-profiler` glob finds,
one row per session — harness, session id, record count, first and last moments — each linking to
`/page/<session-id>`, which renders that session's page in memory, the bytes `tree --format html`
produces. No file is written. A store the glob finds but cannot read appears in the index as
unreadable — the server raises nothing for it. The page shows a session's calls: a session of
nothing but tool calls renders those calls as its calls content, never an empty tree under a calls
header. The server runs until interrupted.

**The skill.** `show-profile` ships as a rendered skill definition under `devpro/definitions/skills/`,
```

## Code delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

The render flow becomes serve-first. `hp.py` gains the `serve` verb: a `ThreadingHTTPServer` bound to
`127.0.0.1` on a free port (`--port` pins one), printing the served URL on stdout; its handler
renders `/` as the index of record files inline — one row per session from `list_sessions`, linking
to `/page/<session-id>` — and `/page/<session-id>` as the page the existing builder returns, served
from memory; no file is written. The skill body's instruction changes to serve-first: run
`profiler/hp.sh serve`, hand the user the URL, with the file-redirect demoted to a one-line mention
for one-off exports. The repository's justfile gains the runner target `dev-profiler` running the
source-tree `hp.sh serve`, the way `dev-kanban` wraps docdicer's serve. The leaf, as amended, stays
true.

The page builder changes in two ways the user decided taking the design up: a session of nothing
but tool calls renders those calls as its calls content — the call tree the skill and agent calls
build stays empty there, and the page never shows an empty tree under a calls header; and an
unreadable `*-profiler` store reaches the index as a stated unreadable row rather than a raised
error, so one bad directory does not blank the page.
