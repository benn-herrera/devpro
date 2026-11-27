# ACTIVE DESIGN

# The Python type gate and the profiler's operational context

The project's Python gains the mechanical vet the generate → vet → revise cycle can rely on: mypy
in strict mode over the package and the dev tool, wired into `just lint` beside the checks already
there, applied the way the ecosystem applies it. The profiler's traces gain their operational
context: every session carries, taken once at its start, the plan it worked under and a fingerprint
of the directives in force, so the dashboard's index and session pages answer what happened under
what plan and which directives — the before-and-after comparison an agent or skill tuning is judged
by. And the dashboard reads a nested fan-out as the process working — the session page drawing the
depth-2 chain the flat index stays too flat to show — or names the fan-out whose trace carries no
review chain. For the operator tuning the agent and skill definitions, and for every dispatch the
process runs under a gate that machine-checks the Python.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```
A page attributes a child session to the session that
dispatched it: the capture extracts the child's session id into the parent call's record, the render
groups a dispatch's child one level deep under the session that dispatched it — deeper chains read
on the session's page, whose tree draws every dispatch as a context — links each Agent row to the
child's page and heads a child page with its dispatcher, and the stores stay flat — the child never
knows its parent at write time, the hierarchy being metadata the parent side builds, and claude
holding no child session records at all.
```

**Becomes:**

```
A page attributes a child session to the session that
dispatched it: the capture extracts the child's session id into the parent call's record, the render
groups a dispatch's child one level deep under the session that dispatched it — deeper chains read
on the session's page, whose tree draws every dispatch as a context and, beneath a dispatch's
context, the child's own dispatched agents, marking the fan-out whose own trace records no
review-chain dispatch at or before its first — links each Agent row to the
child's page and heads a child page with its dispatcher, and the stores stay flat — the child never
knows its parent at write time, the hierarchy being metadata the parent side builds, and claude
holding no child session records at all. Every session's records carry its operational context,
taken once at its start: the plan it worked under and a digest of the directives in force. The index
names both for every session, empty where a session predates the stamp, and no association is
inferred for a session the records stamp nothing onto.
```

## ARCHITECTURE delta

### [Recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md)

**As it stands:**

```
outside it. One more pass, `bunx tsc -p devtools/tsconfig.json --noEmit`, type-checks the
repository's own `devtools/screenshot.ts` under `devtools/tsconfig.json`: a dev tool, checked though
it does not ship.
```

**Becomes:**

```
outside it. One more pass, `bunx tsc -p devtools/tsconfig.json --noEmit`, type-checks the
repository's own `devtools/screenshot.ts` under `devtools/tsconfig.json`: a dev tool, checked though
it does not ship. One more still type-checks the Python: mypy in its strict mode over `devpro/` and
`devtools/`, run through the venv's own interpreter, nothing bespoke built around it — the checker a
`dev`-group dependency like the venv's other tools, its configuration `pyproject.toml`'s, a line
with the compatible-release specifier the group's lines already take. The gate's paths are the
package and the dev tool; `tests/` stays outside them until a test tree's signal proves worth the
quieting its fixture indirection asks. A checker release changes what the gate reports only with a
change to the group line: the pin is the record, as the other tools' are.
```

### The operational-context stamp

```
# The operational-context stamp

Every record a capture writes carries the session's operational context, so the render can answer
what happened under what plan and which directives — the before-and-after comparison an agent or
skill tuning is judged by. The stamp is two fields on the record, `plan` and `directives`, taken
once per session: `plan` the active plan's title, the first level-1 heading of the project's
`ACTIVE_PLAN.md`, or of `ACTIVE_PLAN/entry-point.md` where the plan is diced; `directives` a digest
of the directives the session's harness loaded the devpro set from — the files beneath the project's
harness directory that carry an installed banner or an ownership marker (Installed tree), together
with the project's agents file, the set whatever stands at the session's start, so the digest
fingerprints state and not install history. The digest is sha256 over the sorted `(path, digest)`
pairs, each file's digest sha256 of its bytes, every path project-relative. A field the project
gives the capture nothing for — no active plan, no file carrying a banner or marker — is left out
by the Python capture and `null` by the opencode's, the absent rendering each capture's records
already take.

The stamp is taken once: where the session's store already holds records, the stamp is theirs, read
off the record whose `at` is earliest and copied onto the record being written; where the store
holds none yet, the capture reads the plan and computes the digest fresh. A digest's per-file
digests stand in `.devpro-temp/.profiler-directives/<digest>.json`, written where no manifest for
the digest stands, so a digest's file list is recoverable and two digests' difference is answerable;
the directory is not a store, and no reader of the stores reads it as one. The session's start binds
no field of its own: the store's earliest `at` is the session's start, and the stamp gives it no
second home.

The records are schema 4: `SCHEMA_VERSION` in `devpro/profiler/values.py` and the opencode
capture's own constant move together, and the tests pinning the schema and the record fields —
`tests/test_devpro_profiler.py`'s among them — move with them, the pinned expectation moving with
its requirement. The stamp rides the page data both carriers render, read off the records at the
same render that reads everything else: `tree --format html`'s page and the dashboard's session page
name the session's plan and digest alike, so the served page and the rendered one stay the same
page. A session captured before the stamp carries neither field — it renders unstamped, takes no
part in a before-and-after partition, and no association is inferred for it: the sessions are the
only observers of directive state, and a partition the records do not state is not drawn.
```

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/harness-profiler/index.md)

**As it stands:**

```
- [The opencode capture](the-opencode-capture.md)
- [The stores and their rename](the-stores-and-their-rename.md)
```

**Becomes:**

```
- [The opencode capture](the-opencode-capture.md)
- [The stores and their rename](the-stores-and-their-rename.md)
- [The operational-context stamp](the-operational-context-stamp.md)
```

### [Serving, The index](PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md#the-index)

**As it stands:**

```
the index of record files, every store the readers read,
one row per session — harness,
session id, the models its calls recorded, record count, the count of the dispatched agents it
holds, first and last moments, and the span between them —
each linking to `/page/<session-id>`, which serves that session's page in
memory, the render's page carrying the same page data `tree --format html` produces.
```

**Becomes:**

```
the index of record files, every store the readers read,
one row per session — harness,
session id, the models its calls recorded, record count, the count of the dispatched agents it
holds, first and last moments, the span between them, the plan's title and the directives digest —
two columns more, `plan` and `directives`, after the span, and neither column head sorts —
each linking to `/page/<session-id>`, which serves that session's page in
memory, the render's page carrying the same page data `tree --format html` produces.
```

**As it stands:**

```
its script renders the feed the server answers at `/api/traces`: one JSON entry per session carrying
`harness`, `id`, `models`, `records`, `agents`, `first`, `last`, `span`, and `dispatcher` where a
session was dispatched — `models` the distinct models the session's records name, in the order
they first appear, empty where none does. The script puts `harness` and `records` under their own
names, `id` in the session column, `models` in the model column, joined by `, `,
`agents` in the dispatched-agents count,
`first` and `last` in the first-to-last line, `span` in the
span column, and draws `dispatcher` in no column at all, as the child row under its dispatcher's row.
```

**Becomes:**

```
its script renders the feed the server answers at `/api/traces`: one JSON entry per session carrying
`harness`, `id`, `models`, `records`, `agents`, `first`, `last`, `span`, `plan`, `directives`, and
`dispatcher` where a
session was dispatched — `models` the distinct models the session's records name, in the order
they first appear, empty where none does, `plan` and `directives` the stamp's two fields, `null`
where the session is unstamped. The script puts `harness` and `records` under their own
names, `id` in the session column, `models` in the model column, joined by `, `,
`agents` in the dispatched-agents count,
`first` and `last` in the first-to-last line, `span` in the
span column, `plan` in the plan column — the title cut with its ellipsis where long, the whole in
the cell's `title` — and `directives` in the directives column, the digest's first twelve
characters, the whole in the cell's `title`, and draws `dispatcher` in no column at all, as the
child row under its dispatcher's row.
```

### [Serving, Dispatched children](PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md#dispatched-children)

**As it stands:**

```
A session an opencode record names as its dispatch's child is drawn under the session that dispatched
it — a dispatch's child one level deep; deeper chains read on the session's page, whose tree draws
every dispatch as a context — that session's row carrying the count of the rows beneath it and each
child's naming, after its id and with no lead-in, the call that dispatched it — the indent, the
accent-colored border at its left edge and its tone mark it a child; the rows alternate their tone,
and each carries its harness's mark.
```

**Becomes:**

```
A session an opencode record names as its dispatch's child is drawn under the session that dispatched
it — a dispatch's child one level deep; deeper chains read on the session's page, whose tree draws
every dispatch as a context — that session's row carrying the count of the rows beneath it and each
child's naming, after its id and with no lead-in, the call that dispatched it — the indent, the
accent-colored border at its left edge and its tone mark it a child; the rows alternate their tone,
and each carries its harness's mark. The session page is the depth view, and the depth-2 chain is
its newest level: beneath a dispatch's context the page draws the child's own dispatched agents,
each named after the call that dispatched it and linked to its page where the child's dispatch
record names one. The chain reads from the child's store beside the join the dispatch row's own
signals take (The opencode capture) — one level deeper and no deeper; a claude session's nested
agents stand on its page already, its subagents' records its own store holds. The detector reads the
opencode dispatch chains at the same read: a dispatched session whose records dispatch further
agents is a fan-out, and the fan-out whose own records, at or before its own first dispatch, name no
dispatch of the review seat, `devpro-prompt-engineer`, is the unreviewed fan-out. Its mark stands
beside the dispatch that opened it, on the session page, and on the dispatcher's index row in its
agents cell, after the count — the count the column sorts stays the count. The index gains no second
row level: the mark is the flat table's whole fan-out surface.
```

### [Serving, The models in the page](PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md#the-models-in-the-page)

**As it stands:**

```
The page names the models its calls recorded: the session's in
its header line, each context's in its lifeline's header where that header holds it alone, and each
call's in its detail — a context or a call showing none where it recorded none, and a count where a
context recorded several —
```

**Becomes:**

```
The page names the models its calls recorded: the session's in
its header line, each context's in its lifeline's header where that header holds it alone, and each
call's in its detail — a context or a call showing none where it recorded none, and a count where a
context recorded several —
and the header line names beside the session's models the plan's title and the directives digest,
where the records carry them and nothing where they do not.
```
