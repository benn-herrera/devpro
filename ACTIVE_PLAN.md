# The plan — the Python floor is 3.11

From `ACTIVE_DESIGN.md` (accepted); packages cite its entries by anchor. Every package's intended
lifetime is **shipped**. The checkpoint gate is `just test`, then `just sweep-python`, run before
every package's checkpoint commit — a package's done-line names what that package adds to prove,
not the gate. The only expected test failures in any gate run are the two foreign
`devpro-dashboard` recipe pins —
`tests/test_devpro_install.py::test_the_shipped_devpro_snippets_list_the_same_five_recipes_in_both_runners`
(just and make) — the user's hand-added sixth recipe breaks the five-recipe parity the pins assert,
and the user owns their fate. Any other failure belongs to the package being done.

## Status

| Package | State | Rating | Note |
| --- | --- | --- | --- |
| P1 | landed: commit e9d0b89 | expert | the floor states 3.11 everywhere it is stated or enforced |
| P2 | landed | expert | workaround code the 3.11 floor orphans; its pins verdict superseded by P4 |
| P3 | landed: commit fbb8e04 | expert | the annotation standard for the 3.11 floor |
| P4 | landed: commit ee87157 | expert | the dev toolchain lives in pyproject; pins move to latest 3.11 lines |
| R1 | landed: commit c089c10 | expert | the changed code and documents reviewed |
| R2 | in progress: B1 executing, B2–B5 dispatchable | expert | the burndown, its items below; drafted from ACTIVE_PLAN_REVIEW.md |
| B1 | landed: commit e845d82 | expert | `_venv` refuses what it cannot parse |
| B2 | landed: commit a0e50a6 | mechanical | the wheel surface asserts the clean claim |
| B3 | landed: commit 8997a13 | mechanical | check-wheel checks the floor on the interpreter it is handed |
| B4 | dispatchable — serial after B2/B3 (shares install.py with B5) | expert | the wrapper enforces the floor on both branches |
| B5 | dispatchable — serial after B4 | mechanical | the wording debts |

### P1 — the floor states 3.11

Scope: `pyproject.toml`, `justfile` (`_venv`, `check-wheel`), `devpro/install.py`
(`_WRAPPER_TEXT`), `devpro/definitions/skills/guide.py`, `tests/test_devpro_install.py`, `README.md`,
and the eight pairs of all six design entries, applied to their targets.

**Facts acted on** (each verified this session):

- `pyproject.toml:12` reads `requires-python = ">=3.9"`.
- `justfile:55-59`, the `_venv` recipe's hack:
  ```
  if [[ ! -x {{VENV_PYTHON}} ]]; then
      # if /usr/bin/python3 is installed it is the crappy 3.9.6 from xcode command line tools
      # that is actually our minspec, so use it to ensure we're not using any features
      # beyond its ken
      [[ "$(uname)" == Darwin ]] && export PATH=/usr/bin/:${PATH} || true
      python3 -m venv --upgrade-deps "{{VENV}}"
  fi
  ```
  This checkout's `.venv` was built on that hack: `.venv/bin/python --version` → `Python 3.9.6`,
  while the first `python3` on `PATH` is 3.11.18.
- `justfile:92,96`: `check-wheel python="/usr/bin/python3": build` — its default is the 3.9
  interpreter; under `requires-python >= 3.11` that venv would refuse the wheel at install.
- `devpro/install.py:206-221` (`_WRAPPER_TEXT` and its leading comment): `supported()` runs
  `'import sys; sys.exit(sys.version_info < (3, 9))'`; the refusal reads
  `"devpro needs Python 3.9 or later: ${recorded} is gone, and no python3 on PATH is 3.9 or later"`;
  two comment lines read "where it is Python 3.9 or later".
- `tests/test_devpro_install.py:1844-1864` pins that behavior: docstring "3.9 or later" (twice),
  and `assert "Python 3.9 or later" in refused.stderr`. Updating these pins is in scope.
- `README.md:45` reads `- Python 3.9 or later, which runs devpro and the wrapper each install
  writes into the project; the wrapper exits non-zero, saying so, where it finds none.` — the
  value becomes 3.11 (user's direction: the line rides this package).
- `devpro/definitions/skills/guide.py:59-61` reads: ``A bare `pip install` outside a venv fails on
  most hosts: Homebrew's and most distributions' Python refuse it as
  `externally-managed-environment`, and Apple's `/usr/bin/python3` puts the command in
  `~/Library/Python/3.9/bin`, which is not on `PATH`.`` — the dead-end explanation the
  [guide-and-readme](ACTIVE_DESIGN.md#guide-and-readme) entry stops asking for.

**Work**:

1. Apply every design entry's eight pairs to its target as written, and nothing else
   ([package-and-command](ACTIVE_DESIGN.md#package-and-command),
   [shipped-files](ACTIVE_DESIGN.md#shipped-files), [plugins](ACTIVE_DESIGN.md#plugins),
   [guide-and-readme](ACTIVE_DESIGN.md#guide-and-readme), [packaging](ACTIVE_DESIGN.md#packaging),
   [recipes](ACTIVE_DESIGN.md#recipes)).
2. `pyproject.toml` → `requires-python = ">=3.11"`.
3. `justfile` `_venv`: delete the floor hack and its comment; the recipe then creates `.venv` from
   the first `python3` on `PATH`, and — implementing the recipes pair's statement — recreates it
   where the venv's own interpreter is older than the floor. Read the floor once, from
   `pyproject.toml`'s `requires-python`, parsed without `tomllib` — the builder python is not yet
   known to be 3.11 — so the floor keeps its one home. The comparison's mechanism is the
   executor's call.
4. `justfile` `check-wheel`: default argument `python3`.
5. `_WRAPPER_TEXT`: the version test, both refusal strings, and every comment line read 3.9 → 3.11;
   the leading comment likewise.
6. `tests/test_devpro_install.py`: the pins in the fact above move to 3.11 — no other expectation
   changes; the `too_old` fixture (a stub that exits 1) needs no edit.
7. `README.md:45` → `Python 3.11 or later`.
8. `guide.py`: delete the bare-pip dead-end sentence; the sentence that follows ("Every later
   `devpro` command runs as the `devpro` of that install: …") stays.
9. Recreate `.venv` (`command rm -rf .venv`; the next `_venv` call rebuilds at 3.11) and leave the
   installed trees alone: they refresh on the user's next `devpro install`. The `rendered/` slots
   are gitignored renders: the `latest` slot regenerates on the next `dev-render`, and the four
   `reference-*` slots refresh only via `just retake-reference` — `render` refuses their slugs —
   which nothing here runs.

**Done-line** (once, at the end): `just lint`, `just test devpro`, `just test wheel`, and
`just dev-check-design-deltas-applied` reporting all eight pairs landed, problems 0.

### P2 — workaround code the 3.11 floor orphans

Scope: compat code and version-bound tooling under `devpro/`, `justfile`'s tool list, and
`PROJECT_DOCS/ARCHITECTURE/packaging.md`'s pins sentence where a pin moves.

**Facts acted on**:

- The sweep greps find no orphaned compat once P1 has landed. `git grep -n 'version_info' -- devpro`
  finds only `devpro/install.py`'s wrapper check, and
  `git grep -n '3, 9\|3,9\|sys.version' -- devpro tests` returns that same single line —
  `sys.version` matches as a prefix of `sys.version_info` — which P1 step 5 updates to `(3, 11)`.
  The other 3.9 spellings in the tree are dot-form statements of support — refusal strings,
  comments, the test pins, the guide and `python_coder.py` texts — all P1's to change or
  protected, not mechanism compat. Both greps returning only the updated check is the expected
  sweep result, not an empty sweep.
- `PROJECT_DOCS/ARCHITECTURE/packaging.md`'s pins sentence now reads "the venv's install line in
  the justfile's `_venv` recipe therefore pins `setuptools~=82.0.1` and `build~=1.4.4`." — the
  "last releases that run on Python 3.9" rationale deleted by P1's pair (landed, commit `cdae3ed`).
  The pins themselves survive P1 as stated. No other pin in the tool list carries a stated floor
  rationale.
- `devpro/vocabulary.py`'s `Tools` and `RenderValue` spell runtime unions `typing.Union` (the
  CONVENTIONS leaf's two names); they are P3's, not this package's.

**Work**:

1. Evaluate the two floor-rationale pins: where a newer minor line exists that the 3.9 floor alone
   excluded, move the pin to it (keeping `~=`); where the bound is current or serves another
   purpose, leave it. Report which and why. A move updates the pins sentence in `packaging.md` in
   the same commit.
2. Run the compat greps above and remove what existed only for 3.9 — on the clean sequence,
   nothing: the greps' only expected hit is the P1-updated wrapper check. Sites discovery may
   reach that are not this package's: `devpro/definitions/agents/python_coder.py` (its definition
   text states the mechanism for any floor and stays) and
   `devpro/definitions/skills/guide.py` (P1 deletes that site; present means P1 incomplete, not
   P2 work). Every finding, grep or discovered, returns its site and its reason. Removal is
   straight-up deletion: a version check that exists as compat logic leaves together with its
   alternate path — not rewritten as a `3.11` check that branches the other way. Nothing here is
   complicated enough to justify version-conditional code paths on a 3.11 floor. The wrapper's
   `supported()` check is floor *enforcement* — a refusal below the floor is a statement of
   support — and stays as P1 landed it.
3. Discovery beyond the greps is in scope — that is why this package is expert — and returns its
   site and reason like any finding. A change that alters behavior beyond orphaned-compat removal
   is out of scope and reported instead.

**Result** (landed, executed against the P1 tree):

- *Pins: none moves.* All six `_venv` tools sit on the last release that admits Python 3.9 —
  verified against PyPI's version index and the `.venv` dist-info, which agree on every one. Each
  therefore has a newer line the floor excluded, so the plan's first clause is met six times; the
  second clause is what decides them, and it is the justfile's own range rule (`justfile:45-49`):
  a `~=X.Y.Z` takes the newest patch of the named line, and "a minor or major bump is an edit to
  that line, visible in the diff." Every candidate move is such a bump (`pytest` 9, `black` 25.12,
  `flake8` 7.4, `setuptools` 83, `build` 1.5, `isort` 7). The floor's removal restores the choice
  of line to the maintainer and leaves that rule untouched; no pin is an orphaned-compat artefact.
  `packaging.md` names only `setuptools` and `build`, neither moving, so it is unchanged.
  `flake8~=7.3.0` is named separately: its newest line, 7.5.0, is the first to require `>=3.11`,
  now choosable; it remains a minor bump under the same rule.
- *Greps: the expected one hit each* — `devpro/install.py:213`, the P1-updated wrapper check.
  Nothing existed only for 3.9.

(Supersession: the owner's P4 decision moves the pins to the `dev` dependency group at the latest
3.11-supporting lines — the "no pin moves" answer above is dead; P4 is its successor, not its
echo.)
- *Discovery: one finding, deleted.* `devpro/install.py:233` (`base_interpreter`, called only from
  the generator at `:684`) carried a `getattr(sys, "_base_executable", ...)` fallback and a
  symlink-following `while` loop, both reachable only below 3.11: on 3.11 a venv's
  `_base_executable` is the base interpreter, outside `sys.prefix`, where on 3.9 it is the venv's
  own python. Both are deleted — the body is now `str(Path(sys._base_executable))` — under the
  owner's rule that workaround code leaves by deletion, not by a rewritten branch. Proved
  behavior-identical first, on four states (in a venv, outside one, `venv --copies`,
  `venv --symlinks`), and that the recorded interpreter still outlives the venv it was made from.
  The docstring's "Before 3.11" clause went with the branch it documented. `just test`'s wheel
  step installs and runs the wrapper from the built wheel, exercising the new form end to end.

**Done-line**: `just lint`, `just test devpro`.

### P3 — the annotation standard for the 3.11 floor

Scope: every `devpro/`, `tests/` and `devtools/` module carrying `from __future__ import
annotations` or an old-style annotation; the CONVENTIONS leaf
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/annotations-on-the-floor.md`, rewritten
whole; and a new CONVENTIONS leaf beside it,
`code-definitions-and-install/no-version-conditional-code-paths.md`, created per the owner's
decision (the version-conditional rule's own home), with its entry added to the tree's index;
nothing else.

**Facts acted on**:

- `git grep -l 'from __future__ import annotations' -- devpro tests` → 35 files; the same grep
  over `devtools` → 11 more, which carry no old-style union form
  (`git grep -n 'typing.Union\|Optional\[' -- devtools` returns nothing). The rewritten leaf
  states a house rule, so the import goes from `devtools/` too — excluding a tree the rule
  governs would bake in an exception nobody decided.
- The CONVENTIONS leaf
  `code-definitions-and-install/annotations-on-the-floor.md` states the rule this package inverts:
  *"The Python floor is 3.9, and a union written `X | Y` does not evaluate there"*; it names
  `typing.Union` as the runtime-union spelling and `devpro/vocabulary.py`'s `Tools` and
  `RenderValue` as the two such.
- `git grep -n 'get_type_hints' -- devpro tests` finds no caller — only the mention in
  `devpro/definitions/agents/python_coder.py`'s definition text. Nothing evaluates annotations at
  runtime.
- `devpro/definitions/agents/python_coder.py:59-65` states the floor-following rule for any
  project's floor — it stays untouched.

**Work**:

1. Remove every `from __future__ import annotations` import. With it gone, annotations evaluate
   eagerly: a genuine forward reference that previously resolved lazily becomes a `NameError` at
   import — quote the annotation the import's `NameError` names, and only it, as a string.
2. Replace old-style annotation forms: `Optional[X]` → `X | None`, `Union[A, B]` → `A | B`,
   `typing.List`/`Dict`/`Tuple` → their builtins. `vocabulary.py`'s `Tools` and `RenderValue` move
   to `X | Y` inline — on the 3.11 floor the runtime form is the annotation form.
3. Rewrite the CONVENTIONS leaf whole, in its own voice: the floor is 3.11; a union evaluates
   natively in an annotation and at runtime; the `__future__` import is cruft — not added, and
   removed from code touched; a genuine forward reference is that annotation quoted as a string.
   The leaf's macOS-venv sentence is gone — the recipes statement owns it.
4. Create the new CONVENTIONS leaf `no-version-conditional-code-paths.md` — the owner's rule, its
   own home: no version-conditional code paths — compat code leaves by deletion, never a
   rewritten check; the floor's features are used presumptively, nothing 3.11 provides withheld
   and nothing the later versions take away (3.12 through 3.15 remove nothing); a version branch
   would be one more path to test for the same task, and a new mechanism must win outrageously to
   be worth a second path; the floor's one home is enforcement (`requires-python`, the wrapper's
   refusal) — a statement of support, not a compat branch. Add the leaf to the tree's index. Its
   shape is the tree's house shape: a `###` heading naming the rule, then the prose argument. It
   states the version rule only — the annotations leaf's rewrite carries the annotation rules,
   and neither leaf restates the other's.

**Done-line**: `just lint`, `just test` (unscoped — every module imports), `just sweep-python`.

### P4 — the dev toolchain lives in pyproject

The owner's decision, superseding P2's pins answer (its "no pin moves" reading is moot: the move
happens here, not as a compat removal): the hand-held version pins in the justfile are a bad
holdover — `pyproject.toml` declares dev-only dependencies as a PEP 735 dependency group, which
pip installs cleanly and which no wheel of the package can drag in, a Homebrew local wheel build
included. The pins move to that group at the latest lines supporting Python 3.11.

Scope: `pyproject.toml` (`[dependency-groups]`), `justfile` (`_venv`: the tools list, the comment
above the recipe — both its record paragraph and its range-rule paragraph — and the tools-record),
and the two pending design pairs ([packaging](ACTIVE_DESIGN.md#packaging),
[recipes](ACTIVE_DESIGN.md#recipes)).

**Facts acted on**:

- `.venv/bin/pip` is 26.3, which supports `pip install --group` (verified: the `--group` option in
  its `install --help`).
- The six tools and their floor-era lines, from the justfile's tools list:
  `pytest~=8.4.2`, `isort~=6.1.0`, `black~=25.11.0`, `flake8~=7.3.0`, `setuptools~=82.0.1`,
  `build~=1.4.4`.
- PEP 735: a dependency group is development-only and never distribution metadata — the wheel
  `python -m build` produces carries nothing of it, so nothing exists for a brew local wheel build
  to drag in.

**Work**:

1. Declare a `dev` group in `pyproject.toml` holding the six tools at the latest lines supporting
   Python 3.11 — verify each line's Requires-Python against PyPI's index, not memory. The jumps
   are multi-major: the candidates are `isort` 9, `black` 26, `pytest` 9, `setuptools` 84,
   `build` 1.6 — not P2's first-excluded lines, which understate the move. Each tool's line is
   named with a compatible-release specifier (`~=X.Y`) — the range policy's home now that the
   justfile's range-rule comment dies with its list. `flake8` moves to 7.5.0, the first line to
   require 3.11 (P2's finding). A `black` line move may reformat files; any such reformat rides
   this package's commit. A `setuptools` move also moves the tool that builds the shipped wheel —
   `just build` runs the venv's setuptools with `--no-isolation` — so the wheel and sdist are
   re-proven under the moved pin by the done-line's `just test wheel`.
2. `_venv` installs the group — `pip install --group dev` from the project root — and the
   tools-record satisfies one invariant: it derives from `pyproject.toml`'s declared group, never
   from a second hand-held copy, so any change to the group's content makes the next `_venv`
   reinstall and an unchanged group keeps `_venv` a no-op. The comparison's mechanics are the
   executor's call. The hand-held list and the range-rule comment beside it are deleted; the
   comment's record paragraph is rewritten to match what survives.
3. Apply the two pending design pairs.

**Done-line**: `just lint`, `just test devpro`, `just test wheel`, and
`just dev-check-design-deltas-applied` reporting 8 pairs landed, 0 pending, problems 0.
`just test wheel` is also the proof of the packaging pair's no-drag-in claim: its throwaway venv
is fresh and the wheel installs `--no-index` (`devtools/scripts/check-wheel.sh:56-57`), so any
`Requires-Dist` a botched group left in the wheel fails resolution there — no separate check
needed.

### R1 — Post-plan review

The reviewers are the seats the change touched: `python-coder` (the Python code and its tests),
`shell-dsl-coder` (the justfile's `_venv` and `check-wheel` recipe bodies, bash),
`prompt-engineer` (the project documents and the wrapper's model-facing text), and
`tech-writer` (the README's floor line). Each reviews the landed work against the project's
standards; the session synthesizes their reviews into `ACTIVE_PLAN_REVIEW.md`.

### R2 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` (landed, `c089c10`). Lifetime shipped. Items B1–B3 are one
commit each under the checkpoint gate; B4 and B5 likewise. D8 dissolved by the owner: the guide's
silence stands — Homebrew manages the requirement on its route, pip names the floor at the moment
of failure on the others; enforcement lives in the tools, and a prose statement would be lore.

| Item | Source | Rating |
| --- | --- | --- |
| B1 | D1 (three seats) | expert |
| B2 | D2 | mechanical |
| B3 | D3 | mechanical |
| B4 | D9 | expert |
| B5 | D4, D5, D6, D7, D10, D12, D13, D14 | mechanical |

#### B1 — `_venv` refuses what it cannot parse

Scope: `justfile`'s `_venv` recipe. Every parse
feeds an act only after refusing an empty or unexpected result with the recipe's own error naming
which parse failed: the floor parse refuses `""` — widened to the spellings `requires-python`
actually takes (`>=3.11,<4`, `>=3.11.0`, `==3.11.*`) — before the version test and before any
deletion; the group parse refuses `""` before the record comparison; the rebuild guard's failure
is visible and stops the recipe — a below-floor or unverifiable venv is never silently kept, its
message reaching the user. Reading the values with the builder python's `tomllib` instead of
`sed` is the executor's call, bounded by: tomllib needs a ≥3.11 reader and the builder python is
only known ≥3.11 after the floor check passes — the refusals are required under either choice.
The refusals are floor enforcement, not version branches; the version leaf's rule is not
implicated. Verification, direct on a copy of the tree: the two layout variants that yield an empty group (a
same-line list, a renamed table) each error naming the cause — a comment above `dev = [` parses
fine and must stay harmless, as B1's measurements showed. An unchanged
group stays a no-op; a below-floor venv is refused, not kept. Done-line: `just lint`, `just test
devpro`.

#### B2 — the wheel surface asserts the clean claim

Scope: `devtools/scripts/check-wheel.sh`. One
check on the built wheel's METADATA: it carries no `Requires-Dist` entry at all — the package
declares no runtime dependencies — failing the check otherwise, so "no wheel carries the dev
group" is read where it is claimed instead of inferred from `--no-index` resolution. Done-line:
`just test wheel`.

#### B3 — `check-wheel` checks the floor on the interpreter it is handed

Scope:
`devtools/scripts/check-wheel.sh`. A guard immediately after the interpreter is resolved and
before any venv or wheel work: below the floor, exit non-zero with the floor message. The
done-line proves both the happy path and the guard's position: `just test wheel`, and `just
check-wheel /usr/bin/python3`, which must fail with the floor message — not a wheel defect.

#### B4 — the wrapper enforces the floor on both branches

Scope: `devpro/install.py`
(`_WRAPPER_TEXT`), `tests/test_devpro_install.py`. The recorded branch runs `supported` before
trusting the recorded interpreter; the refusal message has two branch-dependent forms — the
recorded-path form and the PATH form — and both name what the reader can act on (the recorded
path, or the `python3` found and rejected). A new test case pins the recorded-branch refusal: a
recorded path that exists and is below the floor, modeled on the `too_old` fixture, is refused,
not run — the case does not exist today and would otherwise go unpinned. Done-line: `just lint`,
`just test devpro`.

#### B5 — the wording debts

Scope: documents and one code file, each enumerated:
1. `annotations-on-the-floor.md`'s `typing` list: complete it to the set the tree actually
   imports — enumerate with a grep over `typing` imports in `devpro`, `tests` and `devtools`,
   then name exactly those (`D4`).
2. `no-version-conditional-code-paths.md`: drop the dated parenthetical "3.12 through 3.15 remove
   nothing" (`D5`).
3. `pyproject.toml`'s group comment: drop to a pointer at the packaging leaf, the rule's home
   (`D6`).
4. `annotations-on-the-floor.md`'s floor list: gains `plugins.md`'s host-requirement statement
   (`D7`).
5. `README.md:45`'s bullet: names pip's `Requires-Python` refusal beside the wrapper's, and
   states its enforcement like its `just` and `perl` neighbours (`D10`).
6. `packaging.md`: names `tools.txt` and the reinstall-on-group-edit half of the invariant
   (`D13`).
7. `devpro/install.py`'s `base_interpreter` docstring: states the CPython guarantee the code
   relies on (`D12`).
8. `devpro/doccheck/planform.py:410`: the stale `"re.Pattern[str]"` quote is unquoted (`D14`).
9. `packaging.md`'s "Check." bullet: names the two new guards — the METADATA `Requires-Dist`
   check and the floor guard on the handed interpreter (`D2`, `D3`).
10. `PROJECT_DOCS/ARCHITECTURE/recipes.md`'s check-wheel sentence: names the floor guard (`D3`).
11. `recipes.md`'s "through `install`" claim: the script reaches devpro only via `--version`
    (B2/B3 report, noted) — the sentence reads what the script does.
12. `justfile:124`'s `[doc]` prose: "installs byte-identically to the checkout" reads as the
    rendered-output comparison it actually performs (B2/B3 report, noted).
Done-line: `just lint`. The prose items' truth is the enumeration grep and the acceptance audit;
the gate's unscoped run already carries item 8's import-time evaluation and the docs surface — a
done-line restating it would be git-verification, not a test.

Out of scope, noted: `D11` (the tap's unversioned `depends_on` — tap-side work); the installed
copies' staleness (the owner's reinstall, after the plan lands); the two foreign recipe-pin
failures (the owner's); `D8` dissolved by the owner's decision above; tech-writer's F6 (no test
ties README's line to `pyproject.toml` — prose is read only by the spellings sweep), left as
noted; the PATH-`python3`-too-old raw death at `check-wheel.sh:34` — inherent in the justfile
`build` dependency, which needs an interpreter before any check runs (B2/B3 report). The seats'
full notes stay in their review files under `.devpro-temp/`.
