# Post-plan review — the profiler serve rework

Three seats over the packages' landed diff (`git diff 1277d4f..HEAD`), each given the project
documents and the design, not the plan. Seat reviews live in `.devpro-temp/p6-review-{coder,
architect,prompt-engineer}.md`. One ID per defect, naming every seat that reported it.

## R1 — Critical: serve resolves the project directory with capture's rule. *coder*

`hp.py:1302` — `IndexHandler.do_GET` calls `project_dir(os.getcwd())`, which prefers
`CLAUDE_PROJECT_DIR` over cwd (`hp.py:229-236`) — the committed-hook capture's rule, applied to a
foreground command. With the variable pointed at another project, the glob returns `[]` and the
index is empty; `just dev-profiler`, the design's named route, is the run that breaks. The P1 tests
pass `{**os.environ}` with the variable unset, so none can see it. Fix direction: the handler
resolves the directory as the foreground `tree` command does; a serve test drives it with the
variable set to a foreign project.

## R2 — High: the sequence panel contradicts the tree the user decided. *coder*

`view.html:164` — `drawSequence` still reads the checkbox; a tool-call-only session's sequence
panel hides the calls while P2's fallback draws them in the tree. The decided behavior — never an
empty/hidden view of a session's only activity — reaches one of the two call surfaces. Synthesis
raises the seat's Warning: the defect is the user's decided behavior unfulfilled on a visible
surface. Fix: the same fallback in `drawSequence`; the toolbar line stays truthful.

## R3 — Medium: the skill body can stall a session on the URL. *prompt-engineer*

The serve-first body says to start `sh HP serve` "out of the session's way, then hand the user that
URL" — but `serve` never completes, and the body never states the URL is read from the running
job's output. A session following the instruction can block waiting for a completion that never
comes. Fix: one clause naming the running job's output as the URL's source.

## R4 — Medium: the loopback binding is stated as fact, not as rule. *architect + coder*

The leaves state `127.0.0.1` as what `serve` binds; nothing states it as the policy — a one-word
rebind exposes unauthenticated pages holding tool-call args and results. The coder's contract gap
(the Resources paragraph names no loopback-only/no-network rule) and the architect's finding are
one defect. Fix: one sentence in the ARCH Serving paragraph — loopback only, loads nothing from
the network — and the SPEC sentence's reachability outcome where SPEC states the surface.

## R5 — Warning: `session_of` duplicates `list_sessions`' per-trace shape. *coder + architect*

The seats split, and their remedies point in opposite directions: the coder calls the duplication
a defect whose real new behavior (the `except OSError` swallow) belongs in `list_sessions`, with
`tree` ignoring the second return value; the architect calls it justified repetition,
machine-pinned by the page-equality test, recommends the opposite fold — build `list_sessions`
from `session_of` — and holds the unreadable handling's placement correct and required where it
stands, in `read_sessions` (`hp.py:1202-1206`), because `list_sessions`' `iterdir` is unguarded
and `tree` and `doctor` call it, where its raised behavior is what the design pinned. Resolution:
no action on the placement — `session_of` stands as justified repetition, the `except OSError`
stays in `read_sessions`, and `tree` and `doctor` keep today's raising behavior, which the design
pinned; the coder's remedy would change pinned behavior the design never stated. The sync stays
pinned.

## R6 — Warning: `just test` is red at HEAD on a stray bytecode file. *architect*

`check-wheel` packages a stray untracked `__pycache__/hp.cpython-311.pyc` beside the shipped
resource — written by a run that imported `hp.py` under host Python 3.11 outside the runner; the
justfile's own header comment names the trap, and recipe runs are guarded. Blocks P7's gate. Fix:
remove the stray file, harden `check-wheel.sh` against the recurrence.

## R7 — Warning: the skill module's docstring still describes file-out. *coder + prompt-engineer*

`show_profile.py:1-5` — "rendered as a page the user can open… the page it writes" — stale under
serve-first, which writes no file.

## R8 — Warning: `dev-profiler` relies on just's cwd silently. *coder*

The recipe runs the launcher in whatever directory `just` is invoked from — not the `dev-dd`
pattern the design named. The serve surface's correctness depends on the caller's directory
unbated. Fix: the recipe pins the repository root the way a foreground command needs.

## R9 — Warning: the pair application left short lines mid-paragraph in both leaves. *coder*

The becomes-blocks' hard line breaks were applied as line breaks; the leaves carry short lines
(11-15 chars) mid-paragraph. The delta check reads whitespace as one space, so reflowing keeps the
pairs landed.

## R10 — Low: the count instruction says "lines," not what the recording holds. *prompt-engineer*

"Count the lines of that recording" yields records — calls plus event markers, double-recorded
where a plugin and committed hook overlap — not "calls and contexts." Pre-existing wording on the
reviewed surface.

## R11 — Low notes, recorded for the burndown's judgment: *coder + architect*

the index fields bypass `clip(mask(...))` (html-escaped, but unclipped); `str.replace` slot
markers where `string.Template` is the stronger contract; `view.html` walks the call tree twice
for the fallback; the plan's `:1091` citation is stale by P1's own change (no action — the plan
dies at landing); `dev-check-design` reads applied pairs as problems until P7 deletes the design —
expected state, declined as a finding.

## Verified holding across all three seats

Every name in the two leaves resolves against `hp.py`; the page bytes equal `tree --format html`
including when the session is not the newest; traversal refused; loopback-only, free port, clean
shutdown; the skill's flow agrees with the leaf's finder/init/doctor story; 957 tests pass at the
3.9 floor interpreter.
