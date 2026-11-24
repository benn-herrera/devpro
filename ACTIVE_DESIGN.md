# The profiler's stores, the plugin's model config, the scratch directory, and the stand-ins' removal

The profiler and the dashboard read each real session's store once — no copy, no doubled row. The
opencode plugin runs on the model its agents are configured with, on the host version in use. A
project install leaves the scratch directory ready for the work the hooks and the agents write into
it: created when missing, ignored by git. And the test suite holds no test whose mock vouches for
the world it copies: the pages' DOM stand-ins and the capture's stub-plugin fixtures leave with
their runners, their verification moving to the deployed surfaces — a real browser for the pages, a
live opencode host dispatch for the capture — and the sentence `clauses.TESTS_PROTECT_LOGIC` gains
names the boundary: a mock drives, never vouches. For the operator who reads traces and installs
devpro into a project, and for the agents whose work the profiler records and that the mocks misled.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md)

**As it stands:**

```
The
project's scratch directory is `.devpro-temp/` under the project root, the same name under every
harness.
```

**Becomes:**

```
The
project's scratch directory is `.devpro-temp/` under the project root: a project install creates it
when it is missing, and a `.devpro-temp/` line sits in the project's `.gitignore`, the file created
holding that line where the project has none. It carries the same name under every harness.
```

## ARCHITECTURE delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```
and both readers —
`tree`'s render, and the dashboard's profiler view, whose index and session pages read the stores per
request — walk every `.profiler-*` directory there — a dot name, so the stores group and sort at the
top of the scratch tree.
```

**Becomes:**

```
and both readers —
`tree`'s render, and the dashboard's profiler view, whose index and session pages read the stores per
request — read the stores the captures write, the directories named exactly `.profiler-<harness>`
for a harness name the profiler's own captures use (claude and opencode today) — a dot name, so the
stores group and sort at the top of the scratch tree. A directory of any other shape beside a store
is not a store and is not read.
```

**As it stands:**

```
the index of record files, every store the `.profiler-*` glob finds, one row per session
```

**Becomes:**

```
the index of record files, every store the readers read, one row per session
```

**As it stands:**

```
`traces:` the claude store `tree` reads beside the `.profiler-*`
pattern,
```

**Becomes:**

```
`traces:` the claude store `tree` reads, among the `.profiler-<harness>` stores it reads,
```

### [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md)

The leaf gains one passage, after the package copy's paragraph:

```
**The scratch directory.** A project install prepares the project's scratch directory for the work the
hooks and the agents write into it: it creates `.devpro-temp/` under the project root when it is
missing, and it adds a `.devpro-temp/` line to the project's `.gitignore`, creating the file holding
that one line where the project has none. A `.gitignore` already carrying the line is left as it
stands.
```

## Code delta

### [Opencode entry](PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md)

A fix. The leaf's *Registration* states each agent record updates the agent of that id with the
model where the record has them; at runtime on opencode 2.4.1 the host's runtime reads an agent's
model from its own store, so the registry's configured model never applies and the plugin runs on
the default model — the leaf's statement is false at runtime. The fix applies the configured model
at `Plugin.define`'s `setup`, where the 2.4.1 runtime reads it, pinned by a test. The leaf stays as
it stands.

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

A fix. `pages.TRACE_GLOB` (`devpro/profiler/values.py`) is `.profiler-*`, and every reader of it —
`pages.list_sessions` (`devpro/profiler/pages.py`, the tree's render) and `pages.store_directories`
(the index and the session pages) — takes every `.devpro-temp/` directory of that shape for a
store, so a copy of a store — or any second directory of that shape — has its sessions rendered
twice in the index, against the leaf's one-row-per-session statement; `hooks.py`'s doctor
`traces:` line prints the same glob, against the leaf's changed doctor sentence. The fix reads the
stores the leaf's changed passages name: the directories named exactly `.profiler-<harness>` for
the harness names the captures use — `claude` and `opencode` — in all three sites, and a directory
of any other shape is not a store and is not read. Pinned by a test on both readers, a copy beside
a store among the cases.

### [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md)

A fix. The leaf, as the ARCHITECTURE delta changes it, states a project install creates the
scratch directory when it is missing and adds the `.gitignore` line; the install does neither
today. The fix is that preparation, held to the changed passage.

A refactor. The clause `NEW_PROJECT_SETUP` (`devpro/clauses.py`) carries the birth-time scratch
creation the install now owns — "Also created at project birth" with the directory and the
`.gitignore` entry — and its creation mandate drops, the placement invariant it carried staying
with it: the project's scratch directory lives beside the harness directory, never inside it,
writes under the harness directory tripping the permission system's own-settings protections. The
leaf, as changed, stays true — the install's preparation is the guarantee's one code home.

### [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md)

A fix. The leaf, as the SPEC delta changes it, states the scratch directory is created when it is
missing and carries the `.gitignore` line; `devpro/harness.py`'s `scratch_rule` — the agents file's
scratch rule — tells the agent, where the scratch directory does not exist, to stop and say so,
against the create-it statement. The fix makes the rule tell the agent to create it, the
improvise-a-location prohibition unchanged. The leaf, as changed, stays true.

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

A refactor. `clauses.TESTS_PROTECT_LOGIC` (`devpro/clauses.py`) gains one sentence as its last,
after the form-is-the-contract sentence: a mock drives execution to the piece under test and is
never the oracle for what it simulates — a test asserting against a mock's own answers validates
the reading of the observation, not the system, and is not written. The leaf's statement of the
clause stays true.

### [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

A refactor. The pages' three DOM stand-in runners (`tests/profiler_browser_runner.ts`,
`tests/profiler_index_runner.ts`, `tests/profiler_page_runner.ts`, their `MutationObserver`
machinery included) and the tests driving them are removed from `tests/`, and the capture's
stub-plugin fixture runner (`tests/profiler_capture_runner.ts`) with its test — a mock that
vouches for the browser or the host verifies the reading of the observation, not the system, and
the pages and the capture are verified at the deployed surfaces instead. The two stubs the
`Opencode entry` fix's test rides — `tests/opencode_plugin_stub.ts` and
`tests/opencode_entry_runner.ts` — stay: they drive execution to the entry's registration path and
vouch for nothing the host states. The leaf's statement of `tests/` stays true: the runners were
never named there, and the suite keeps the mask, serialize and capture-contract tests and the
Python-side server and store tests. Until the browser-vision visual verification the roadmap
carries next lands, the pages' client-side rendering has no automated check — the byte-level
instruments check the rendered bytes and the server's answers, not what a browser executes.
