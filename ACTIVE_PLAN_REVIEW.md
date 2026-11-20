# Post-plan review — the opencode profiler

Findings from four seats over commits `47ad9b0`, `eef4d9a`, `b4de8be`, each written independently in
`.devpro-temp/` (`p4-review-typescript-coder.md`, `p4-review-python-coder.md`,
`p4-review-architect.md`, `p4-review-prompt-engineer.md`). One ID per defect, naming every seat that
reported it. R23 was surfaced by the session (the lint gate's state at review time).

Severity: **Critical** — shipped behavior loses user data; **High** — a shipped feature misinforms
the agent told to use it, or a security-adjacent parity claim is false; **Medium** — a false statement
in shipped text, a contract with no pin, a mechanism sentence made false; **Low** — polish, notes,
accepted-risk consequences.

## R1 — Critical — every failed or denied call loses its record

*Seats: typescript-coder (Critical).*

`profiler.ts:35`/`:190-198`. `execute.after` reports `error: Tool.Error` (a class with `.message`);
the file declares it `string`, so `firstLine(call.error)` throws, `silently()` swallows the throw,
and the whole record for every failed call is dropped — the probe writes four records for five
calls. The capture loses exactly the calls that matter when debugging.

## R2 — High — the skill's premise names a store nothing writes

*Seats: prompt-engineer (F1, F4), architect, python-coder.*

`show_profile.py:15-16` — "The trace is the newest session recording in
`.devpro-temp/harness-profile/`": no capture writes that directory any more (`hp.py:25`,
`profiler.ts:66`). The same stale path stands in `README.md:45` and `claude.py:70`. Through the
skill's own instructions the stale path can produce a wrong "nothing recorded" answer
(`show_profile.py`'s Answer step counts lines of "that recording").

## R3 — High — masking parity is false where a credential holds a non-ASCII letter

*Seats: prompt-engineer (F6).*

Python's `\w` is Unicode; JavaScript's is ASCII — `hp.py` redacts `sk-abcéfghijklm` and
`profiler.ts` records it verbatim (probe files in `.devpro-temp/`). "The masking is its masking"
(profiler.ts:8) is false at this edge, with a data-exposure consequence.

## R4 — High — the skill offers claude-only surface unqualified, under both harnesses

*Seats: prompt-engineer (F2).*

`show_profile.py:31-33,57-59` — `init claude` and `doctor` offered without qualification; the leaf
says both stay claude-facing. The rendered body is byte-identical under both harnesses, so an
opencode agent is directed to subcommands that do not apply.

## R5 — High — the capture's behavioral contract has no pin

*Seats: python-coder, typescript-coder.*

No test seeds a second `*-profiler` store — a revert of the glob passes green, though the split is
the change's whole purpose. The entry-test runner keeps one callback per hook name, so only
registration counts are pinned; no test fires the capture end to end. The user-level payload
exclusion is likewise unexercised (the stub has no `claude/profiler`).

## R6 — Medium — the enumeration misses claude's own `profiler/` trio

*Seat: prompt-engineer (F3).*

`shipped-files.md:87-90` gives claude only its two hook scripts; the claude install dir also gains
`profiler/{hp.sh,hp.py,view.html}` (verified in the claude slot), and the paragraph at `:98-100` says
so — the leaf disagrees with itself.

## R7 — Medium — subagent and skill dispatches record the wrong names

*Seat: typescript-coder.*

`nameOf`/`argsOf` read claude's tool fields, so every subagent dispatch records `general-purpose`
and every skill call `skill` — the tree's default drawing hides them.

## R8 — Medium — `result` records the JSON envelope, not the text

*Seat: typescript-coder.*

## R9 — Medium — "**The opencode capture.**" runs on inside "**What does not exist.**"

*Seat: architect.* One paragraph break fixes it; the defect originates in the design pair, applied
verbatim, so the design's becomes-block moves with it.

## R10 — Medium — three mechanism sentences the pairs didn't cover are now false

*Seat: architect.*

SPEC's restart exception (`shipped-files.md:115-117` — `profiler.ts` also imports at load,
`index.ts:167`); `ARCHITECTURE/install/opencode-entry.md` (no mention of `profiler.ts`);
`renders-and-copies.md:62-64` (the copy list described as per-harness only).

## R11 — Medium — `repo-layout.md:18` omits `opencode/profiler.ts`

*Seats: architect, prompt-engineer (F10).*

## R12 — Medium — the skill demands token columns opencode never records

*Seat: prompt-engineer (F7).*

## R13 — Medium — `<plugin-dir>` is coined beside `<install-dir>` without binding

*Seat: prompt-engineer (F12).*

## R14 — Medium — the `<plugin-dir>/profiler/` destination is derived, though SPEC states it

*Seat: python-coder.* `install.py` derives the destination from `PurePosixPath(extra).name` where
the leaf states the path; the leaf is the contract, the derivation an implementation detail that
silently diverges from it if either changes alone.

## R15 — Medium — the start map leaks an entry per call that never completes

*Seat: typescript-coder.*

## R16 — Low — `doctor` mixes stores while claude-facing

*Seat: python-coder.*

## R17 — Low — dead `pluginId()` duplicating the entry's id

*Seat: typescript-coder.*

## R18 — Low — `dropTornTail` is a repair `hp.py` lacks

*Seat: typescript-coder.*

## R19 — Low — `clip` counts UTF-16 units; a lone surrogate crashes `hp tree`

*Seat: typescript-coder.*

## R20 — Low — the untyped entry seam

*Seat: typescript-coder.*

## R21 — Low — the idle record has no renderer; `branch` is permanently null; the stated reason for `child_agent_id` is false

*Seat: typescript-coder.*

## R22 — Low — the `todowrite` skip records nothing

*Seat: typescript-coder.*

## R23 — Low — the lint gate is red at HEAD: `devpro/render.py:41-43` unformatted

*Seat: session.* `ce89017` truncated the generated notice; the formatter was not run over the
edited file, so `just lint` exits 1 until a format pass lands. Surfaced during the review by the
python-coder seat's lint run.

## Declined

- **`agent_id` null under opencode** (typescript-coder): correct — hp.py's `agent_id` keys a
  subagent context opencode's hooks do not supply; inventing one hid every call.
- **The registration order not module-grouped** (typescript-coder): measured and pinned as the
  entry's actual behavior; no defect.
- **The double `[redacted]`** (typescript-coder): parity holds; the port's expectation was wrong,
  not the code.
