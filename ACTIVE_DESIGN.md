# The opencode plugin records its sessions' activity into the profiler's trace store

opencode sessions get the same mechanical record claude sessions have: every tool call with its
duration, arguments, result and outcome, agent dispatches among them, and session lifecycle. The
capture is the opencode plugin's own TypeScript — recreated against the plugin's hook surface, per
the ported design's ruling — writing records into the same `.devpro-temp/harness-profile/` store
the ported design moved to, so `hp.py`'s tree and page render both harnesses' sessions. The opencode
install ships the render payload (`hp.sh`, `hp.py`, `view.html`) beside the plugin, where the
show-profile skill's existing finder already resolves it, so the skill works there unchanged.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```markdown
resources; no opencode or mage install ships the resources or the hook entries.
```

**Becomes:**

```markdown
resources. An opencode install also ships the profiler's render payload — `libexec/hp.sh`,
`libexec/hp.py` and `libexec/view.html` — and the capture `profiler.ts` beside the plugin entry, and
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
`<install-dir>/guardrail.ts`, `<install-dir>/profiler.ts` and `<install-dir>/libexec/hp.sh`,
`<install-dir>/libexec/hp.py`, `<install-dir>/view.html`, and claude's at
`<install-dir>/hooks/guardrail.pl` and
```

## ARCHITECTURE delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```markdown
**What does not exist.** No companion-plugin mechanism is built: the profiler has no namespace of its
own and no carrier but the devpro plugin. Should it become optional later, it becomes a
`--components` value. No opencode or mage payload ships: the profiler's hooks are claude's, and an
opencode capture, should one come, is recreated in the opencode plugin's TypeScript rather than
reusing this code. Token counts come from claude's own transcripts under `~/.claude/projects/`, which
is claude's data, not a source the install configures.
```

**Becomes:**

```markdown
**The opencode capture.** Under opencode the plugin itself records: `profiler.ts` beside the entry
carries the capture, recreated in the plugin's TypeScript against the plugin's hook surface —
`execute.before` and `execute.after` paired on the call's id time every tool call (the `tool`,
`sessionID`, `status`, `input` and `result`/`error` the after-hook reports), the idle hook marks the
session's lifecycle — and appends the records to the same `.devpro-temp/harness-profile/<session-id>.jsonl`
store, `harness` `"opencode"`, that `hp.py`'s tree and page render beside the claude sessions'. A
capture that fails raises nothing out of the hook. `init` and `doctor` stay claude-facing: opencode
has no committed-hook concept, and the install ships the render payload at
`<plugin-dir>/libexec/`, where the show-profile skill's first finder candidate resolves it.
Token counts come from claude's own transcripts under `~/.claude/projects/`, which is claude's data,
not a source the install configures; under opencode the records carry no token fields the hooks do
not supply.
```

## Code delta

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

The capture's shape, held to the amended leaf: `profiler.ts` beside `index.ts` in
`devpro/harnesses/resources/opencode/`, TypeScript, imported and registered from the entry the way
`guardrail.ts` is wired. It hooks `execute.before` and `execute.after`, correlating each call's id
to time it; on completion it appends one record per call to
`.devpro-temp/harness-profile/<session-id>.jsonl` under the project root — `v` 2, `harness`
`"opencode"`, `at` ISO-8601, `session`, `tool`, `duration_ms`, `ok`, and the argument and result
summaries masked the way `hp.py` masks claude's — and every field `hp.py`'s tree and page read is
present, carrying the field's empty rendering where opencode's hooks supply no value (verified
against `tree` on a scratch trace as part of the work). The idle hook appends the lifecycle record.
Failures raise nothing out of a hook: a capture that fails is silent. The record's field names and
semantics match the claude record's where the field exists, because the same `tree` and page render
both.

The wiring, the registration and the install-time probe are `index.ts`'s existing mechanisms; the
entry gains one import and one registration call, nothing else.
