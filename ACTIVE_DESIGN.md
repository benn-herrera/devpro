# The opencode plugin records its sessions' activity into the profiler's trace store

opencode sessions get the same mechanical record claude sessions have: every tool call with its
duration, arguments, result and outcome, agent dispatches among them, and session lifecycle. The
capture is the opencode plugin's own TypeScript — recreated against the plugin's hook surface —
writing records into its own `.devpro-temp/opencode-profiler/` store, one of the per-harness
stores `hp.py`'s tree and page render, so the same render surface shows both harnesses' sessions. The
opencode install ships the render payload (`hp.sh`, `hp.py`, `view.html`) beside the plugin, where
the show-profile skill's existing finder already resolves it, so the skill works there unchanged.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```markdown
resources; no opencode or mage install ships the resources or the hook entries.
```

**Becomes:**

```markdown
resources. A project opencode install also ships the profiler's render payload — `profiler/hp.sh`,
`profiler/hp.py` and `profiler/view.html` — and the capture `profiler.ts` beside the plugin entry, and
registers no hook entries; a mage install ships none of them.
```

### [Shipped files — the resources enumeration](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```markdown
path it holds below the install directory: opencode's at `<install-dir>/index.ts`, the plugin entry, and
`<install-dir>/guardrail.ts`, and claude's at `<install-dir>/hooks/guardrail.pl` and
```

**Becomes:**

```markdown
path it holds below the install directory: opencode's at `<install-dir>/index.ts`, the plugin entry,
`<install-dir>/guardrail.ts`, `<install-dir>/profiler.ts` and `<install-dir>/profiler/hp.sh`,
`<install-dir>/profiler/hp.py`, `<install-dir>/profiler/view.html`, and claude's at
`<install-dir>/hooks/guardrail.pl` and
```

### [Shipped files — the trace store](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```markdown
one line to the project's `.devpro-temp/harness-profile/<session-id>.jsonl`, and a capture that
```

**Becomes:**

```markdown
one line to the project's `.devpro-temp/claude-profiler/<session-id>.jsonl`, and a capture that
```

### [Shipped files — the profiler resources](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```markdown
the harness resources
`libexec/hp.sh`, `libexec/hp.py` and `libexec/view.html`, copied as they stand, and the
```

**Becomes:**

```markdown
the harness resources
`profiler/hp.sh`, `profiler/hp.py` and `profiler/view.html`, copied as they stand, and the
```

### [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md)

**As it stands:**

```markdown
the
profiler's launcher sits in the install directory's `libexec/` and is named relative to the skill's
directory too (`../../libexec/hp.sh`). The
```

**Becomes:**

```markdown
the
profiler's launcher sits in the install directory's `profiler/` and is named relative to the skill's
directory too (`../../profiler/hp.sh`). The
```

## ARCHITECTURE delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```markdown
No opencode or mage payload ships: the profiler's hooks are claude's, and an
opencode capture, should one come, is recreated in the opencode plugin's TypeScript rather than
reusing this code.
```

**Becomes:**

```markdown
**The opencode capture.** Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call (the `tool`,
`sessionID`, `status`, `input` and `result`/`error` the after-hook reports), the idle hook marks the
session's lifecycle — and appends the records to its own
`.devpro-temp/opencode-profiler/<session-id>.jsonl` store, `harness` `"opencode"`, that `hp.py`'s
tree and page render beside the claude sessions' in `.devpro-temp/claude-profiler/` — the trace
stores split per harness, no shared directory. A
capture that fails raises nothing out of the hook. `init` and `doctor` stay claude-facing: opencode
has no committed-hook concept, and the install ships the render payload at
`<plugin-dir>/profiler/`, where the show-profile skill's first finder candidate resolves it. The
records carry no token fields the hooks do not supply.
```

### [Harness profiler — the payload directory](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```markdown
**Resources.** Three files live in `devpro/harnesses/resources/claude/libexec/`: `hp.sh`, the
POSIX-sh launcher that finds `python3` (`HP_PYTHON` overrides the search); `hp.py`, the whole tool —
`capture`, `tree`, `init`, `doctor` — one file, Python 3 standard library only, no dependency; and
`view.html`, the self-contained page template that loads nothing from the network. Each carries the
`!INSTALLED! … devpro` banner within its first ten lines — the banner rule binds every harness
resource. `harness_resource_copies` lands each at the path it holds below the install directory, so
the install directory gains `libexec/`.
```

**Becomes:**

```markdown
**Resources.** Three files live in `devpro/harnesses/resources/claude/profiler/`: `hp.sh`, the
POSIX-sh launcher that finds `python3` (`HP_PYTHON` overrides the search); `hp.py`, the whole tool —
`capture`, `tree`, `init`, `doctor` — one file, Python 3 standard library only, no dependency; and
`view.html`, the self-contained page template that loads nothing from the network. Each carries the
`!INSTALLED! … devpro` banner within its first ten lines — the banner rule binds every harness
resource. `harness_resource_copies` lands each at the path it holds below the install directory, so
the install directory gains `profiler/`.
```

### [Harness profiler — the hook command](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```markdown
running `sh "${CLAUDE_PLUGIN_ROOT}/libexec/hp.sh" capture claude`. The wiring is data in the harness
```

**Becomes:**

```markdown
running `sh "${CLAUDE_PLUGIN_ROOT}/profiler/hp.sh" capture claude`. The wiring is data in the harness
```

### [Harness profiler — the finder candidate](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```markdown
Its finder's first candidate, `../../libexec/hp.sh` from the
skill's directory, resolves to `<install-dir>/libexec/hp.sh` where the payload landed; its second,
```

**Becomes:**

```markdown
Its finder's first candidate, `../../profiler/hp.sh` from the
skill's directory, resolves to `<install-dir>/profiler/hp.sh` where the payload landed; its second,
```

### [Harness profiler — the trace store](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```markdown
A capture appends one line to the project's `.devpro-temp/harness-profile/<session-id>.jsonl` — the project's scratch
```

**Becomes:**

```markdown
A capture appends one line to the project's `.devpro-temp/claude-profiler/<session-id>.jsonl` — one of the per-harness stores under `.devpro-temp/`, every `*-profiler` directory of which `hp.py`'s `tree` renders — the project's scratch
```

### [Repo layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

**As it stands:**

```markdown
`claude/libexec/hp.sh`, `claude/libexec/hp.py` and `claude/libexec/view.html`
```

**Becomes:**

```markdown
`claude/profiler/hp.sh`, `claude/profiler/hp.py` and `claude/profiler/view.html`
```

## Code delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

The capture's shape, held to the amended leaf: `profiler.ts` beside `index.ts` in
`devpro/harnesses/resources/opencode/`, TypeScript, imported and registered from the entry the way
`guardrail.ts` is wired. The shipped render payload's one home is
`devpro/harnesses/resources/claude/profiler/` (the source directory renamed from `libexec/`), and opencode's copy list in `harness_resource_copies`
gains the three files sourced from there, so the repository holds no second copy of the payload. It hooks `execute.before` and `execute.after`, correlating each call's id
to time it; on completion it appends one record per call to
`.devpro-temp/opencode-profiler/<session-id>.jsonl` under the project root — `v` 2, `harness`
`"opencode"`, `at` ISO-8601, `session`, `tool`, `duration_ms`, `ok`, and the argument and result
summaries masked the way `hp.py` masks claude's — and every field `hp.py`'s tree and page read is
present, carrying the field's empty rendering where opencode's hooks supply no value (verified
against `tree` on a scratch trace as part of the work). The idle hook appends the lifecycle record, its event field carrying the hook's own name
(`experimental.idle`).
Failures raise nothing out of a hook: a capture that fails is silent. The record's field names and
semantics match the claude record's where the field exists, because the same `tree` and page render
both.

The trace store splits per harness, no shared `harness-profile/` directory: the claude capture
writes `.devpro-temp/claude-profiler/<session-id>.jsonl` — `hp.py`'s `TRACE_DIR` follows it — and
`tree` renders every `*-profiler` directory under `.devpro-temp/`, so the tree reads both stores;
the opencode capture writes `.devpro-temp/opencode-profiler/<session-id>.jsonl`. Traces already
under the old `harness-profile/` path are orphaned — accepted, hand-deletable. The directory
rename's satellites follow it: the show-profile finder's first candidate becomes `../../profiler/hp.sh`;
`claude.py`'s `_PROFILER_SCRIPT` and the hook command string become `profiler/hp.sh` — the hook
command is ours to spell, nothing upstream requires the old name; the trace-path assertions the
profiler tests carry (`tests/test_devpro_profiler.py`'s among them) follow the per-harness stores;
and `tests/test_devpro_install.py`'s `libexec` path references rename.

The wiring, the registration are `index.ts`'s existing mechanisms; the entry gains one import and
one registration call, nothing else.
