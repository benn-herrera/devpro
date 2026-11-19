# ACTIVE_PLAN_REVIEW — the session nudge and the kanban wording

The post-plan review of the five commits `cfa22e7..49b6f22`. Five seats reviewed independently —
`python-coder`, `typescript-coder`, `shell-dsl-coder`, `architect`, `prompt-engineer` — each given
the project documents and `ACTIVE_DESIGN.md`, not the plan, writing their own review to
`.devpro-temp/review-<seat>.md`. This document is the session's synthesis: one ID per defect
however many seats reported it, seats named. The per-seat files remain in `.devpro-temp/` for their
evidence until the plan lands.

Verified green before review: `just test` (870), `just check-deltas` (7/7 byte-exact),
`just check-links` (163/0), `just sweep-python`, `just check-wheel`.

## Findings

### D1 — the claude mechanism cannot deliver "at dispatch and at completion" as stated
Seats: shell-dsl-coder (findings 1, 2). Session-verified against the Claude Code hooks reference
(additionalContext is inserted "at the point where the hook fired" and read "on the next model
request"; `SubagentHandback` is the subagent's own report-delivery tool; `PostToolUse` on `Agent`
fires at the call's return with `status` distinguishing `completed`/`async_launched`; no parent-side
event exists for a background subagent's completion).
- A foreground `Agent` call blocks the parent, so the `PreToolUse` "dispatch" sentence is read at
  completion, beside the `PostToolUse` sentence — every dispatch injects the identical sentence
  twice. A background launch reads both at the launch turn — also twice.
- `SubagentHandback` in the completion matcher fires inside the finishing subagent; the sentence
  has no reader there. The reference names `PostToolUse` on `Agent` as the parent-side route.
- The decision between the repairs is the user's (raised mid-run; options stated: one `PostToolUse`
  on `Agent`, or keep both and reword the claims to the actual delivery). The burndown item takes
  its shape from that answer.

### D2 — the reminder sentence misstates its moment, its audience, and its twin
Seats: prompt-engineer (F1, F2, F3), shell-dsl-coder (N7).
- Both harnesses' sentences end "as the work lands" while firing at dispatch and completion; at
  dispatch the anchor names nothing, and acting at completion can move a row `dispatchable` →
  `landed`, skipping `in progress` (SPEC, Plan Status Form forbids).
- The claude form ("is expected to") and the opencode form ("Update") state one rule at two
  strengths, with nothing comparing the two copied resources; the mood split's rationale lives only
  in one script comment.
- Where only `ACTIVE_DESIGN.md` stands, the gate opens and the sentence asserts a status table a
  design-only project does not have.
Fix direction: one sentence naming both acts (e.g. in-progress when a package is dispatched, landed
when accepted and committed), true in both gated states; byte-equal across the two resources or the
split's rationale stated where a maintainer looks.

### D3 — `check_deltas.py` closes a fenced block on any fence line, and can pass a partial application
Seats: python-coder (F1, demonstrated false pass). `_is_fence`/`_read_fence` accept any ```` ``` ````
or `~~~` line as a closer without matching the opener's character or length, so an applied passage
containing an inner fenced example is checked only up to the inner fence — a leaf holding one third
of the applied text exited 0. Fix: the CommonMark closer rule already pinned at
`devtools/render_diff.py:43-44`; add the demonstrated case as a regression test (with D4).

### D4 — `check_deltas.py` ships with no test
Seats: python-coder (F2), architect (W6). Alone among `devtools/*.py`; the surface map already
routes `devtools/` changes to `devtools/tests`. Fix: `devtools/tests/test_check_deltas.py` over both
verdicts and each named failure mode, plus D3's case.

### D5 — no test executes the registered reminder command
Seats: shell-dsl-coder (4), python-coder (F3). Every reminder test runs the source script or
asserts matchers; a mistyped `_REMINDER_SCRIPT` or interpreter keeps the suite green while every
real install reports `no readable script` forever. The guardrail's equivalent test exists. Fix:
generalize `_run_registered_hook` (tests/test_devpro_install.py:1815) to run the reminder entry.

### D6 — statements the change falsified were left stale (the doc-set search gap)
Seats: architect (W4, W5, N1), python-coder (F8, F5), prompt-engineer (F4, F6, F7, F13),
shell-dsl-coder (9). The change updated seven statements and left others in the same paragraphs and
neighbouring leaves:
- `guardrail-registration.md:8-9` — the report still "names an earlier install's script or
  registration"; only the script is ever named now (`_earlier_guardrail` deleted).
- `ARCHITECTURE/install/index.md:15-16` — still says a failed probe "skips the script and its
  registration".
- `repo-layout.md` — missing the new resource `claude/hooks/state-table-reminder.sh` and
  `devtools/check_deltas.py` with its recipe.
- `guardrail-hook.md` — names one registration builder where two shipped (`registration_without_hook`,
  `_reminder_registration` appear in no document), states no event/matcher for the two reminder
  entries, and "the script" is now ambiguous; `guardrail-registration.md` same pair unnamed.
- `devpro/harness.py` — `GuardrailHook`'s docstring and the `InputError` still describe one
  registration; two are required.
- `write-safety.md:33` — "names the script that is the install's own" reads awkwardly for the
  rewritten rule.
- `a-delta-application-ends-verified.md` — states the check twice in adjacent sentences (the
  justfile comment states it a third time).
- Notes riding with this root: the marker-breadth price ("only this repository writes" vs a 21-char
  common phrase — python-coder F4); the leaf's paraphrase vs the emitted sentence (architect N3);
  the check's occurrence-not-diff contract and its link-rebasing limitation (architect N4); the
  user-level claude asymmetry worth one sentence (architect N2).
Fix: one sweep item fixing all of the above, plus the CONVENTIONS rule the gap proves (below).

### D7 — the opencode version claims disagree across SPEC, ARCHITECTURE and the resources
Seats: architect (W2, W3), prompt-engineer (F5), typescript-coder (4), python-coder (seen).
SPEC `shipped-files.md:100-102` says "written for opencode v2.2.6"; `opencode-entry.md` and
`index.ts:3` say "2.3.2 (floor 2.2.6)"; `guardrail.ts:3` still says "v2.2.6". One file, three
version statements. Fix: one form everywhere (and see D8 — the floor is behavioral).

### D8 — the stated floor is behavioral, and the dispatch claim holds from 2.3.0 only
Seats: typescript-coder (1). At v2.2.6/v2.2.7 the `subagent` tool defaults to foreground, so
`execute.after` fires at completion, behind the idle hook — on the floor version the parent gets two
completion nudges and none at dispatch. `background`-always landed in 2.3.0. Fix: state the
behavioral floor in `opencode-entry.md` and the entry comment (or raise the floor), landing with D7
so one version claim survives.

### D9 — the gate misses the diced plan
Seats: typescript-coder (2), prompt-engineer (design line b). SPEC's Plan Status Form and the shipped
guide skill carry the plan as the tree `ACTIVE_PLAN/` once diced; both harnesses' gates test only the
two files (`[ ! -f … ]`, `existsSync`), so the long plan — where the table matters most — never gets
a nudge. Fix: gate on file-or-directory for both names, both harnesses, plus a runner case.

### D10 — the opencode gate reads the opened directory, not the project root
Seats: typescript-coder (3). `ctx.location.directory` is the directory the session opened at;
`ctx.location.project.directory` is the checkout root. A session opened in a subdirectory never
injects. Fix: gate on the project root; correct the ARCHITECTURE sentence naming the field.

### D11 — the opencode nudge fires where nothing completed
Seats: typescript-coder (5). `execute.after` ignores `call.status` (a denied or failed subagent call
nudges); the idle hook ignores `background` (a child that dispatched a grandchild or left a shell
nudges "landed" while work still runs, then again). Fix: `status !== "completed"` return; skip while
`background.length > 0` (or state the per-idle nudge as wanted); runner fires for both.

### D12 — the board-offer wording's second-order gaps
Seats: prompt-engineer (F9, F11, F12), python-coder (F9).
- Neither skill text says who stops a background board process or how; "It serves until stopped."
  leaves the stop with nobody — a live server left behind is the failure.
- `subsystem-map.md:57-58` — the paragraph "offers … or hands", a dangling subject (a paragraph does
  not hand a command line).
- `docdicer.py` — the colon attaches "the user chooses" to the command list, not the choice.
- The offer pulls against the rendered `FOREGROUND_RECIPE_RULE` for dispatched agents (a dispatched
  agent is told opposite things; the recipe never completes so the foreground rule cannot be obeyed
  either) — reconcile in the wording, not the rule.
Fix: the four small wording changes, in both skills / leaves as applicable.

### D13 — ROADMAP carries the harness-profiler item as two tickets
Seats: shell-dsl-coder (seen), prompt-engineer (F10). `## Features` (lines 10-17) and `## Testing`
(lines 114-125); the Testing one opens with first-person intent plus decision record, which the file
header excludes, and the Features ticket's open list is a superset. The Features ticket is the
session's design-phase addition and duplicated the existing item. Fix: delete lines 114-125.

### D14 — small defects and notes
- `check_deltas.py` exits through a traceback on a missing design file (python-coder F6) and is not
  black-clean at :177-179 (python-coder F7).
- `field()`'s comment claims a top-level guarantee the scan does not implement; the one-line bound
  (`input=${input%%'"tool_input"'*}`) or a reworded comment (shell-dsl-coder 5).
- `_hook_command` interpolates into shell source and reports with `echo`; `printf '%s\n'` and a
  docstring line stating `report` is shell source (shell-dsl-coder 6).
- The reminder's tests live in `test_guardrail.py`, whose docstring scopes the module to the
  guardrails (shell-dsl-coder 8, python-coder F10) — move or name.
- The new script is POSIX `sh` where every other script in the repository is `env bash` with braced
  expansions and two-space indent (shell-dsl-coder 3) — conform or state the POSIX need in the
  header.
- The injection's `delivery` mode is implicit (`"steer"` default) — pass and record it explicitly
  (typescript-coder 6).
- `ACTIVE_DESIGN.md` alone never opens the gate in any opencode test; the claude side parametrizes
  both (typescript-coder 7).
- Comment-pinned external assumptions are recorded, no action required (architect N5); the
  byte-exact application carries the design's line breaks into leaves — a formatting artifact whose
  fix belongs in a design block, nil cost for a model reader (prompt-engineer note).

## Probes the burndown should name (unverified claims)
From the prompt-engineer seat: U1 — does the claude descriptive form land at dispatch (scratch
project, one mechanical dispatch, read the row from the diff)? U2 — what does one
`ctx.session.synthetic` cost in parent turns? U3 — is the completion nudge recalled at the commit
that carries the work? U4 — how often does the design-only gate fire on a design→plan run?

## Contract gaps (to the owners named)
- CONVENTIONS: a delta application ends by searching the doc set for the replaced behaviour's
  wording; statements it leaves false are reported, not rewritten (surfaced by P3's coder; D6
  proves the need).
- CONVENTIONS: a `devtools/*.py` tool joins `devtools/tests/` with a test (python-coder gap 2).
- CONVENTIONS: the byte-check's parser contract — fences read as CommonMark does (python-coder
  gap 3).
- CONVENTIONS: a harness resource's floor is behavioral (typescript-coder gap 2).
- CONVENTIONS: a read-only `lint` recipe alongside `format-python` (python-coder gap 1).
- CONVENTIONS: harness hook contracts are read, not assumed — where context lands is the harness's
  statement (shell-dsl-coder gap).
- ROADMAP: the "No shell lint" item names the hooks tree (shell-dsl-coder gap).
- Agent definitions: shell-dsl's shellcheck instruction for a host without the target;
  typescript-coder's shipped-resource/runtime wording (typescript-coder gap 1).

## Strengths to preserve
The probe-failure path got simpler, not more complex; `_hook_command` DRYed the second hook instead
of duplicating the first; both harnesses gate at fire time so a planless project pays nothing; the
boundary code is tested at its real contracts; the tests assert behavior, not form; `check-deltas`
gave the delta-application rule the mechanical witness its leaf said it lacked.
