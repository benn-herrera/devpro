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
| P1 | landed | expert | the floor states 3.11 everywhere it is stated or enforced |
| P2 | dispatchable | expert | workaround code the 3.11 floor orphans |
| P3 | dispatchable | expert | the annotation standard for the 3.11 floor |
| R1 | drafted | expert | the changed code and documents reviewed |
| R2 | drafted | expert | drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands |

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
   P2 work). Every finding, grep or discovered, returns its site and its reason.
3. Discovery beyond the greps is in scope — that is why this package is expert — and returns its
   site and reason like any finding. A change that alters behavior beyond orphaned-compat removal
   is out of scope and reported instead.

**Done-line**: `just lint`, `just test devpro`.

### P3 — the annotation standard for the 3.11 floor

Scope: every `devpro/`, `tests/` and `devtools/` module carrying `from __future__ import
annotations` or an old-style annotation; the CONVENTIONS leaf
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/annotations-on-the-floor.md`, rewritten
whole; nothing else.

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

**Done-line**: `just lint`, `just test` (unscoped — every module imports), `just sweep-python`.

### R1 — Post-plan review

The reviewers are the seats the change touched: `python-coder` (the Python code and its tests),
`shell-dsl-coder` (the justfile's `_venv` and `check-wheel` recipe bodies, bash),
`prompt-engineer` (the project documents and the wrapper's model-facing text), and
`tech-writer` (the README's floor line). Each reviews the landed work against the project's
standards; the session synthesizes their reviews into `ACTIVE_PLAN_REVIEW.md`.

### R2 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
