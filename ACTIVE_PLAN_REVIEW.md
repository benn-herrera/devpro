# ACTIVE_PLAN_REVIEW — the Python floor is 3.11

Synthesized from four independent seat reviews (`python-coder`, `shell-dsl-coder`,
`prompt-engineer`, `tech-writer`) of the landed P1–P4 work. One entry per defect, naming every
seat that reported it. The burndown groups by root cause.

Environment note (not a defect): the installed copies — `.opencode/plugins/devpro/`,
`.claude/skills/devpro/`, `rendered/` — carry pre-P1 text until the owner re-runs `devpro install`.
This checkout's own sessions load the `.opencode` copy, so its wrapper still enforces 3.9 until
then. Old wrappers run fine on newer interpreters; the refresh is a post-landing step, not work.

## D1 — `_venv`'s parses fail open, and one fails into the wrong action (critical)

Seats: `python-coder`, `shell-dsl-coder`, `prompt-engineer` — three seats, one root cause: the
recipe parses pyproject.toml with chained `sed`s and acts on the result without refusing an empty
or unexpected parse.

- The group parse (four `sed` stages) yields `""` on a comment above `dev = [`, a same-line list,
  a wrapped specifier, a renamed table, or a reorder; `""` equals the missing-record fallback, so
  the recipe installs nothing and records the empty string — a silent no-op on a toolless venv.
  `shell-dsl-coder` measured this on three variants; `python-coder` adds that the failure then
  surfaces as an unexplained `just lint`/`just test` failure.
- The floor parse yields `""` on `>=3.11,<4`, `>=3.11.0`, or `==3.11.*`; the version test then
  raises, the `!` reads that as "too old", and **`.venv` is deleted** — rebuilt from a `python3`
  that may be below the floor, ending in pip's message rather than the recipe's own
  (`shell-dsl-coder`, warning).
- The rebuild guard's stderr is dropped and the venv kept on failure (`prompt-engineer` F1).

Fix shape: refuse an empty `${floor}`/`${group}` between parse and act (or read with the builder
python's own tomllib, now known to be ≥3.11 only *after* the floor check — the sequencing note in
the usability review stands). Probe variants exist under `.devpro-temp/probe/`.

## D2 — the no-drag-in guarantee is incidental, not checked

Seat: `python-coder`. The commit message and `packaging.md` say the wheel proves the dev group
never leaks; `check-wheel.sh:57` installs `--no-index`, which proves resolution, not cleanliness —
the guarantee dies with a `--find-links`. The wheel is clean today (METADATA read). Fix: one
`grep -q '^Requires-Dist'` line on the wheel surface, making the claim direct.

## D3 — `check-wheel` checks no floor on the interpreter it is handed

Seats: `shell-dsl-coder`, `python-coder`. P1 fixed the macOS half (the `/usr/bin/python3`
default); the new `python3` default puts a below-floor interpreter in reach and it reports as a
wheel failure instead of a floor refusal. Fix: one guard line beside the others.

## D4 — the annotations leaf's `typing` list reads as closed

Seat: `prompt-engineer`. The rewritten leaf lists six `typing` names as the ones with no
builtin/abc form; the tree imports nine (`Any`, `IO`, `NoReturn` also in use, `Generic` named by
`python_coder.py`). Fix: state the list as open or complete it.

## D5 — a dated fact sits inside the version leaf's standing rule

Seat: `prompt-engineer`. `no-version-conditional-code-paths.md` puts "3.12 through 3.15 remove
nothing" inside the standing rule whose next clause already carries the point. The clause dates
the rule. Fix: drop the parenthetical; the presumptive-use statement stands alone.

## D6 — the compatible-release convention is stated at three sites

Seat: `prompt-engineer`. `pyproject.toml`'s comment repeats the packaging leaf's rule including a
maintenance clause; the leaf is the home. Fix: the comment drops to a pointer or dies.

## D7 — SPEC `plugins.md` is a fourth floor statement the leaf omits

Seat: `prompt-engineer`. The annotations leaf's floor-home list names three enforcement sites;
`plugins.md`'s host requirement is a fourth statement of support. Fix: one line in the leaf.

## D8 — the guide's requirements page states no Python requirement at all

Seat: `tech-writer`. The design's "support is stated where it holds" does not hold for the page a
session is told to consult to install. The owner's ruling — that stating the prerequisite and
documenting remediation is general lore — produced this silence deliberately; the tension is real
and the owner decides whether the installing page gains one floor line. (Related settled call: the
Apple-3.9 dead-end paragraph stays deleted.)

## D9 — the wrapper checks the floor on one branch only

Seat: `tech-writer`. The wrapper's refusal names `${recorded}` — the interpreter that ran the
install, which the reader cannot restore — and never the `python3` it found and rejected; and the
recorded branch (`if [[ -x "${recorded}" ]]`) checks existence, not the floor, so a recorded
pre-floor interpreter runs the copy with no refusal. Reaching that state requires an old-install-
plus-new-copy combination the update paths don't produce today, but the asymmetry is real. Fix:
the same `supported` check on the recorded branch, and a refusal message naming both
interpreters.

## D10 — README's Python bullet under-states its own enforcement

Seat: `tech-writer`. The bullet credits the wrapper alone; a pip install actually reports the
wheel's `Requires-Python` refusal, and the bullet — unlike its `just` and `perl` neighbours —
states no enforcement at all. Fix: one wording pass on the bullet.

## D11 — the Homebrew formula's `depends_on "python"` is unversioned

Seat: `tech-writer`. The channel the README sends readers down carries no version statement. The
formula lives in the tap, outside this repository — likely a tap-side note, not devpro work.

## D12 — `sys._base_executable`'s guarantee is stated nowhere

Seat: `python-coder`. P2's simplification rests on CPython's guarantee that the attribute names
the base interpreter in any venv; the seat verified pyenv 3.11 and Homebrew 3.15, both venv
flavours. Fix: one docstring line in `install.py` stating what the code relies on.

## D13 — `packaging.md` never names the record mechanism

Seat: `shell-dsl-coder`. The leaf states where the toolchain is declared but not `tools.txt` nor
the reinstall-on-group-edit half of the invariant — the half that stops a stale record from
passing every gate. Fix: one sentence.

## D14 — a stale quote survived P3 untouched

Seat: `python-coder`. `planform.py:410`'s `"re.Pattern[str]"` quotes `re` — imported, not a
forward reference — a lazy-annotation leftover the floor no longer needs. P3 never touched the
line; it belongs to the standard it just wrote.

## Probes the burndown may use

`prompt-engineer` lists U1–U4 in its review file (`.devpro-temp/review-p1to4-prompt-engineer.md`)
for what only behavior settles; `shell-dsl-coder`'s probe variants live under
`.devpro-temp/probe/`; `python-coder`'s module-import walk is one command.
