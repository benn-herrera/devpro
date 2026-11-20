# Post-plan review — the profiler port

Findings from four seats over commits `56d5141` and `d5f54b4`, each written independently in
`.devpro-temp/`: `p3-review-architect.md`, `p3-review-prompt-engineer.md`, `p3-review-python-coder.md`,
`p3-review-tech-writer.md`. One ID per defect, naming every seat that reported it. Two findings (R9,
R10) were surfaced by the python-coder during P2's execution and recorded by the session.

Severity: **High** — breaks a sentence SPEC states or leaves a user misinformed by a shipped path;
**Medium** — a false statement in shipped text, a contract with no pin, or a stated convention
contradicted; **Low** — polish, pre-existing drift, or an accepted-risk consequence.

## R1 — High — a capture can exit non-zero with output, against SPEC's sentence

*Seats: python-coder (C1).*

`hp.sh:20-27`. SPEC *Shipped files* states a capture that fails "exits 0 with no output". Three
reachable paths break it before the interpreter runs: a `PATH` python3 older than 3.9 (hp.py's
syntax fails at compile), `HP_PYTHON` set to a directory (`[ -x ]` passes), and `hp.py` missing
beside the launcher — exits 1/126/2 with stderr. Verified against all five failure cases with a
patched launcher. The fix: every pre-interpreter failure drains stdin and exits 0 silently, like the
no-interpreter path already does.

## R2 — High — the show-profile skill reads "nothing recorded" from a tree that draws no leaf calls

*Seats: prompt-engineer (1).*

`show_profile.py:45,56`. The skill counts calls from default `tree` output, which draws only
`Skill`/`Agent` calls; a Bash/Edit-only trace prints the header alone and exits 0 (probe-confirmed).
The agent then tells the user nothing was recorded while the trace holds calls. The fix: read the
count from `--verbose` or the raw trace, or state what the default tree draws.

## R3 — Medium — the leaf's account of the README credit disagrees with the README's credit

*Seats: tech-writer (1), prompt-engineer (6).*

`ARCHITECTURE/install/harness-profiler.md:5-6` says the acknowledgement credits "the source of the
idea and design"; `README.md:141` says the plugin's "source was adapted". MIT attribution turns on
the difference, and the README line is frozen verbatim by user ruling — the leaf bends to the
README's actual wording, in the change that also moves the design's becomes-block (the pair is
byte-pinned).

## R4 — Medium — the port's core contract has no automated pin

*Seats: architect (W1), python-coder (W1).*

No test executes `hp.py`; the only test change in `d5f54b4` renames the filename tuple. SPEC's
capture outcomes and the record/D-payload contract with `view.html` have no regression check. The
guidance both seats give: one test driving the installed launcher with a synthetic payload and
asserting the record and the rendered page's inline JSON keys.

## R5 — Medium — `mkdir -p .devpro-temp` in the show-profile skill is provably dead

*Seats: prompt-engineer (2).*

`show_profile.py:38,43`. A successful `tree` proves the trace directory exists, since the port moved
the trace under `.devpro-temp/`; the block also answers the always-loaded scratch rule the other
way. Retire it.

## R6 — Medium — the skill says `init` commits; it writes and prints the `git add`

*Seats: prompt-engineer (3).*

`show_profile.py:30`. The clause overstates `init`'s act.

## R7 — Medium — the failure path hands the user `doctor`'s false "hook: not installed" line

*Seats: prompt-engineer (4).*

`show_profile.py:45`. `doctor`'s plugin-record grep cannot see the payload copy, so its remediation
hint names an `init` the user may already have run — the skill should not relay it unchecked.

## R8 — Medium — the README's pipx line names no release, while CONVENTIONS names it a version carrier

*Seats: tech-writer (2). Pre-existing.*

`README.md:57` carries no `@v<version>`; `version-has-one-home.md` calls it the fourth carrier.
Reconcile the two: either the line names the tag or the leaf stops calling it one.

## R9 — Medium — a Python harness resource inside `just lint`'s paths is stated nowhere

*Seat: session (surfaced by the python-coder during P2).*

`hp.py` is a shipped resource and a Python module, so `just lint` covers it — black, isort, flake8
at line length 120 — as well as the banner rule. CONVENTIONS'
`code-definitions-and-install/harness-resources-are-copied-verbatim.md` says nothing about a
resource written in Python, and adding or deleting one changes what the lint gate covers.

## R10 — Medium — `just test wheel` reads the git index, and no leaf says so

*Seat: session (surfaced by the python-coder during P2).*

`check-wheel.sh:29` builds its expected package set from
`git ls-files --cached --others --exclude-standard`, so a package-data deletion cannot pass the
wheel surface before it is staged; a bare working tree fails for that reason alone. P2's done-line
needed this fact mid-task. `planning-and-execution/the-gates.md` should state it.

## R11 — Low — two payload shapes lose a whole record the JS kept

*Seat: python-coder (N1).* `hp.py:352-366`, `:601`.

## R12 — Low — upgrades leave the old tool behind: `init` leaves `hp.js` in a committed-hook directory, and a consumer's `libexec/` keeps `hp.js` beside `hp.py`

*Seat: python-coder (N2); the plan records the consumer side.* `hp.py:1222-1225`. `prune` walks only
rendered surfaces, so neither stale copy is removed.

## R13 — Low — `USAGE` duplicates the usage block

*Seat: python-coder (N3).* `hp.py:1320-1324` against `:7-10`.

## R14 — Low — one unparseable sentence in the module docstring

*Seat: python-coder (N4).* `hp.py:219-221`.

## R15 — Low — injection seams with no caller and no test

*Seat: python-coder (N5).* `hp.py:499`, `:552`, `:586-588`, `:1292`.

## R16 — Low — stdin and stdout are text I/O with the encoding left to the locale

*Seat: python-coder (N6).* `hp.py:1330`, `:1349`, `:1352`, `:1355`.

## R17 — Low — the install test pins the payload's names, not its bytes

*Seat: python-coder (N7).* `tests/test_devpro_install.py:472`.

## R18 — Low — the capture creates the directory the convention says the user creates

*Seat: python-coder (N8).* `hp.py:598` mkdirs `.devpro-temp/harness-profile/` where the agents-file
invariant has the user create the scratch directory and the session stop when it is missing.

## R19 — Low — `hp.sh`'s not-found message does not distinguish a bad `HP_PYTHON`

*Seat: architect (N2).* `hp.sh:13`.

## R20 — Low — the finder's gloss on candidate 1 is false under a user-level install

*Seats: prompt-engineer (5).* `show_profile.py:22` — "the copy the install delivered beside it" does
not hold where the install copied no resource.

## R21 — Low — the profiler has no human-facing description; the credit is its only mention

*Seat: tech-writer (3).*

## R22 — Low — the credit names no license, which the leaf and the acknowledgement's source both carry

*Seat: tech-writer (4).*

## R23 — Low — no human-facing text states the interpreter floor, and the launcher checks existence only

*Seat: tech-writer (5).* Related to R1's first path.

## Declined

- **Session-id sanitization `\w` difference** (architect N3): Python's Unicode-aware `\w` vs JS's
  ASCII set differs only for session ids carrying non-ASCII word characters; ids are UUIDs in
  practice. No behavioral consequence on any reachable input.
- **Trace untracked-ness moved from mechanism to convention** (architect N1): the design accepted
  this when it retired the exclude write; recording it as a defect would reopen a settled call.
- **Second homes for git-root resolution and hook-entry construction** (architect judgment 4):
  forced by the leaf's one-file stdlib-only constraint, not DRY violations.
