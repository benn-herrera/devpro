# The profiler pages read as devpro's, name their models and show local time

The dashboard's profiler view, for the operator reading their own sessions: every moment it shows
is in local time; a session nothing dispatched draws its own context in devpro's accent, and a child session's page is
named for, and colored as, the agent call that started it; each call names the model that
made it — claude's from its transcript, opencode's as `providerID/modelID` from its capture — on
the index and on the session page; the index keeps its first-to-last line on one line
and drops the legend and the child-row lead-in; opencode's dot wears opencode's periwinkle. For
whoever changes those pages: a development-loop tool that screenshots a page after it has settled,
so the rendered result can be viewed and iterated on.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [The profiler's shipped surface](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```
In the profiler view the how-to-read legend sits at the top of the
view's frame band and persists there across drill-down, the same band carrying a return-to-list
control,
```

**Becomes:**

```
In the profiler view the how-to-read legend sits at the top of a session page's frame band — the
index carries none — the same band carrying a return-to-list
control,
```

**As it stands:**

```
The pages and the records
stay local: reachable only from the
machine that runs the server.
```

**Becomes:**

```
The pages and the records
stay local: reachable only from the
machine that runs the server. Every presentation of a recorded moment — the pages, the index, the
text tree and `profiler doctor`'s lines — reads in the reader's local time, and none shows UTC, a
hover title included. UTC stays in what the records store and in markup no reader is shown, such
as a `<time>` element's `datetime`.
```

**As it stands:**

```
links each Agent row to the
child's page and heads a child page with its dispatcher, and the stores stay flat
```

**Becomes:**

```
links each Agent row to the
child's page and heads a child page with its dispatcher, naming the child page's own context for
the dispatching call's agent, in the color the context that call opened wears on its dispatcher's
page, and the stores stay flat
```

**As it stands:**

```
The index's rows alternate their tone
```

**Becomes:**

```
A call's record names the model that made it where its harness states it: the index names the models a session's
calls recorded, and a session's page names them for the session, for each context and for each
call, showing none where no record names one. The index's rows
alternate their tone
```

**As it stands:**

```
opencode's blue, claude's coral.
```

**Becomes:**

```
opencode's periwinkle, claude's coral. On the page of a session nothing dispatched, the session's
own context wears the motif's accent, its labels dark enough to read on it; on a dispatched
session's page it wears the color the context its dispatching call opened wears on the
dispatcher's page; and no other context wears a hue that reads as the accent in the mode shown.
```

## ARCHITECTURE delta

### [The profiler's pages and capture](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```
cannot reach the profiler page's DOM, and the template's own rules draw the sequence diagram's colours
from the palette's `--c0`…`--c7` variables, no palette of its own.
```

**Becomes:**

```
cannot reach the profiler page's DOM, and the template's own rules draw the sequence diagram's colors
from the layer, no palette of its own: hue 0 — the root context's on a page nothing dispatched, and
its copies' — the layer's `--accent`, its labels in the layer's `--on-accent`, and every other hue
the palette's `--c0`…`--c7`; no palette hue reads as the accent in the mode shown.
```

**As it stands:**

```
one row per session — harness,
session id, record count, the count of the dispatched agents it holds, first and last moments, and
the span between them —
```

**Becomes:**

```
one row per session — harness,
session id, the models its calls recorded, record count, the count of the dispatched agents it
holds, first and last moments, and the span between them —
```

**As it stands:**

```
The header row
and the body's rows take their column widths from one source, so every header sits over the column it
names at every width the data produces.
```

**Becomes:**

```
The header row
and the body's rows take their column widths from one source, so every header sits over the column it
names at every width the data produces, and the first-to-last column is wide enough that its line
never wraps.
```

**As it stands:**

```
`harness`, `id`, `records`, `agents`, `first`, `last`, `span`, and `dispatcher` where a session was
dispatched. The script puts `harness` and `records` under their own names, `id` in the session column,
`agents` in the dispatched-agents count,
```

**Becomes:**

```
`harness`, `id`, `models`, `records`, `agents`, `first`, `last`, `span`, and `dispatcher` where a
session was dispatched — `models` the distinct models the session's records name, in the order
they first appear, empty where none does. The script puts `harness` and `records` under their own
names, `id` in the session column, `models` in the model column, joined by `, `,
`agents` in the dispatched-agents count,
```

**As it stands:**

```
that session's row carrying the count of the rows beneath it and each
child's naming the call that dispatched it;
```

**Becomes:**

```
that session's row carrying the count of the rows beneath it and each
child's naming, after its id and with no lead-in, the call that dispatched it — the indent, the
accent rule at its left edge and its tone mark it a child;
```

**As it stands:**

```
The pages' own scripts draw every moment local at birth — the moments cells, the
index's first-to-last line, the session page's header stamp — in the reader's local time, 24-hour, one
notation:
```

**Becomes:**

```
The pages' own scripts draw every moment local at birth — the moments cells, the
index's first-to-last line, the session page's header stamp, its diagram's and its call tree's
times — in the reader's local time, 24-hour, one
notation:
```

**As it stands:**

```
The
machine form stands in the `<time>` elements' `datetime` attributes and the raw UTC in the titles; a
page carries no moments where its script does not run, and the deco reads none.
```

**Becomes:**

```
The
machine form stands in the `<time>` elements' `datetime` attributes alone, and no title carries a
moment's UTC; a
page carries no moments where its script does not run, and the deco reads none. `tree`'s text reads
its time column and its session stamps in the machine's local zone, through `values._local`, which
doctor's `newest:` line reads too.
```

**As it stands:**

```
A session's page
carries its dispatcher in the frame band, linked to that session's page, where one dispatched it, and
a call row whose tool is `Agent` links
```

**Becomes:**

```
A session's page
carries its dispatcher in the frame band, linked to that session's page, where one dispatched it, and
then names its own root context — its id still `main` — for the dispatching call's agent, the
prefix dropped, in the hue the context that call opened wears on the dispatcher's page:
`pages.dispatcher_of` reads both from the dispatcher's records at render, the child's own records
naming no parent, and the page's other contexts take hues from 1 up, skipping the root's hue. A page nothing dispatched names
its root `main`, in hue 0. A call row whose tool is `Agent` links
```

**As it stands:**

```
and in the profiler view a frame
band sits under it, carrying the how-to-read legend at its top and, on a session's page, `Return to
list` back to `/profiler/`;
```

**Becomes:**

```
and in the profiler view a frame
band sits under it, carrying on a session's page the how-to-read legend at its top and `Return to
list` back to `/profiler/`, and on the index neither;
```

**As it stands:**

```
No file is written for the traces. The page shows a session's calls:
```

**Becomes:**

```
No file is written for the traces. The page names the models its calls recorded — the session's in
its header line, a context's in its lifeline's header where that header holds it alone, where it
recorded one, and their count where several, a call's in its detail — and shows a session's calls:
```

**As it stands:**

```
An opencode record carries no token counts, so the tree's token columns are blank for its
sessions; claude's counts come from its own transcripts under `~/.claude/projects/`, which is
claude's data, not a source the install configures.
```

**Becomes:**

```
An opencode record carries no token counts, so the tree's token columns are blank for
its sessions; claude's counts and each claude call's `model` come from
its own transcripts under `~/.claude/projects/`, which is claude's data, not a source the install
configures — the model is that of the assistant message holding the call's tool use, the entry the
capture reads the call's context tokens from, and is recorded at capture alone. An opencode
record's `model` names the model call that issued the tool call, as `providerID/modelID`, the last
one the session's `model.request` hook reported when the record is written, and is recorded at
capture alone: `null` where none has run — a host whose plugin surface offers no such hook records
none.
```

### [The repository layout's devtools](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

**As it stands:**

```
  clause_join_sites.py  the list of definition-body units that join a `clauses.*` interpolation to the module's own text (justfile `clause-join-sites`); splits units with `render_diff.py`'s line classification, `line_kinds`
```

**Becomes:**

```
  clause_join_sites.py  the list of definition-body units that join a `clauses.*` interpolation to the module's own text (justfile `clause-join-sites`); splits units with `render_diff.py`'s line classification, `line_kinds`
  screenshot.ts         the development loop's page screenshot (justfile `screenshot`): Puppeteer driving the system Firefox headless, the page settled, a PNG written under `.devpro-temp/`; run under bun, never imported
```

**As it stands:**

```
the devtools test suite — dupe_sweep (`test_dupe_sweep` and its import-structure test), clause_join_sites and render_diff —
```

**Becomes:**

```
the devtools test suite — dupe_sweep (`test_dupe_sweep` and its import-structure test), clause_join_sites, render_diff and screenshot —
```

### [The screenshot recipe and its toolchain](PROJECT_DOCS/ARCHITECTURE/recipes.md)

**As it stands:**

```
The suite needs `bun`, `perl` and `kbase` (at least `KBASE_MIN_VERSION`) on `PATH`.
`tests/test_guardrail.py`, `tests/test_opencode_entry.py` and `tests/test_kbase_surface.py` fail
rather than skip without them, because a skip would hide drift.
```

**Becomes:**

```
The suite needs `bun`, `perl`, `firefox` and `kbase` (at least `KBASE_MIN_VERSION`) on `PATH`.
`tests/test_guardrail.py`, `tests/test_opencode_entry.py`, `tests/test_kbase_surface.py` and
`devtools/tests/test_screenshot.py` fail rather than skip without them, because a skip would hide
drift.
```

**As it stands:**

```
The compiler rides unpinned — `bunx` takes the latest at
run time.
```

**Becomes:**

```
The compiler rides unpinned — `bunx` takes the latest at
run time. `just screenshot <page> [--base <url>] [--viewport <W>x<H>] [--color-scheme light|dark]
[--wait-for <selector>] [--timeout <ms>] [--out <png>]` runs
`devtools/screenshot.ts` under bun: `puppeteer-core`, a dev dependency in the same root
`package.json`, drives the `firefox` on `PATH` headless over WebDriver BiDi — Puppeteer owning the
profile, the flags and the handshake, no browser downloaded — settles the page on network idle,
the fonts ready and the selector where one is given, and writes a PNG, by default under
`.devpro-temp/screenshots/`, printing its path. It is the development loop's view of a rendered
page and asserts nothing about the pixels. The private `_js-deps` recipe installs that
`package.json`'s dependencies from `bun.lock`, frozen, for `screenshot`, `lint` and `test`;
`just js-lock` installs them unfrozen, rewriting `bun.lock`, after a change to that
`package.json`'s dependencies.
```
