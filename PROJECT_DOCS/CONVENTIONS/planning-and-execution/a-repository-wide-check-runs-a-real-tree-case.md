# A repository-wide check runs a real-tree case

A repository-wide check's own case set includes one run over the real tree it polices; a fixture-only
case leaves the check unexercised on its inputs. A check that passes against fixtures alone proves
the fixtures, not the check over the trees it will actually read.

The recipe's own run is not that case: a check the recipe hands this repository's tree to passes or
fails in a target nobody counts as a test, and its fixture cases say only what the fixtures hold. The
case is a test that hands the check the repository it ships in — the checkout's `PROJECT_DOCS` or
`devpro/` tree — and passes where that tree does.

Which trees the case reads is the check's to state, and a check whose own sides read different trees is
pinned side by side. `check-wheel` holds the wheel's package data to the index — `git ls-files
--cached --others --exclude-standard` — while an install run from a checkout stages `devpro/` from the
filesystem. The two agree on every path `.gitignore` covers only where the walk drops it by its own rule:
`__pycache__` is out of staging as bytecode, and the index never lists it. Every other path is on both
sides or on neither — an untracked stray the index does not ignore is counted by both — so the case pins
that over this checkout's `devpro/` tree, a gitignored stray excluded by both and any other stray counted
by both.
