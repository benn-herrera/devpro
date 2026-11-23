## Packaging

How the package and command of SPEC.md, Package and Command are built. `pyproject.toml` at the
devpro project root is the whole build configuration.

- **Backend.** setuptools (`setuptools.build_meta`). `[build-system] requires` is `setuptools>=77.0`, the first release that reads a PEP 639
  `license` string. The package has no runtime dependency (`dependencies = []`); `requires-python` is
  `>=3.9`.
- **Version.** `dynamic = ["version"]` with `[tool.setuptools.dynamic]` reading
  `devpro.__version__`. `pyproject.toml` holds no version literal (CONVENTIONS.md, Version has one
  home).
- **Package data.** `[tool.setuptools.package-data]` lists six patterns, `kb-tools/**/*`,
  `harnesses/resources/**/*`, `development-tools/**/*`, `dicing-snippets/**/*`,
  `profiler/view.html` and `dicing/kanban/assets/**/*`: the trees `install.py`
  reads through `PACKAGE_ROOT` (`HARNESS_RESOURCES_SOURCE` and each `SHIPPED_PACKAGES` source,
  the kb-tools, development-tools and dicing-snippets trees), the board's assets (Repo Layout) and
  the profiler's page template (Harness profiler), which `importlib.resources` serves. A glob
  sweeps in whatever sits
  under its tree, so `just check-wheel` holds the list equal to the tree: the wheel's non-`.py`
  files under `devpro/` must be exactly the non-`.py` files git tracks or would track there
  (`git ls-files --cached --others --exclude-standard`). A shipped tree missing from the list fails
  it, and so does a stray file the list sweeps in.
- **Console script.** `devpro = "devpro.cli:main"`. argparse's `prog` is `"devpro"`, so
  `devpro --help` and `python3 -m devpro --help` print the same text. The dispatch is lazy: the
  entry point imports only the verb invoked, and every verb imports no third-party dependency
  (Package and Command), so no verb pays for another verb's imports. Registered at parser build,
  the verbs themselves import nothing: `devpro.cli`, the dicing verbs' `dicing/cli.py`, the check
  verbs' `doccheck/cli.py`, `profiler/cli.py` and `dashboard/cli.py` import each verb's
  implementation where they dispatch it, which are their only function-level imports and the
  module-level-import house rule's one exception, the five modules `tests/test_devpro.py` exempts by
  name. `devpro/cli.py` composes the other four's `add_verbs`. The profiler's hook wiring carries the rule's second exception, which the same test names: the
  hook-run capture imports `hooks.py`, so the renderer's import lives in `show_skill_text`, the
  function that renders the skill a hook writes, and never at module scope — the hook-write path
  imports only what it executes, as the capture path does.
- **Offline build.** `just build` runs `python -m build --no-isolation` in `.venv` and writes the
  wheel and sdist to `dist/`, so it uses the venv's own setuptools, not a downloaded one. `.venv`'s
  install line in the justfile's `_venv` recipe therefore pins `setuptools~=82.0.1` and
  `build~=1.4.4`, the last releases that run on Python 3.9. The build makes no git check. A build also
  writes `devpro.egg-info/` at the devpro project root, which `.gitignore` covers. The sdist is
  a byproduct of the build: SPEC.md, Package and Command names no sdist install source, and
  `check-wheel` checks only that the sdist exists.
- **Check.** `just check-wheel [python]` builds, then installs the wheel into a throwaway venv under
  `.devpro-temp/` made from `python` (default `/usr/bin/python3`, the Python 3.9 floor on macOS only). With `PYTHONPATH` unset and
  `GIT_CEILING_DIRECTORIES` at that scratch directory, it checks that `devpro` imports from the
  venv, that the console script and `python -m devpro` print the same `--help` and the checkout's
  version, that an install with the kbase component on into a scratch project equals the checkout's
  byte for byte, and that a mage install writes `devpro/CLAUDE.md`. It is the `wheel` test surface:
  `just test wheel`, and the last step of an unscoped `just test`. A change to `pyproject.toml` or
  under `devpro/` selects it in `just test-changed`.

**The checkout premise.** devpro runs from a checkout when `PACKAGE_ROOT.parent` holds a `.git` entry: a directory in a
clone, a file in a worktree. `install_base.checkout_root` tests for it without running a subprocess, and
`REPO_ROOT` is that parent, or `None` outside a checkout. An editable install's `PACKAGE_ROOT` is
inside the clone. A wheel's, in site-packages, is not, and `git` there would answer for the
surrounding project. `PACKAGE_ROOT` and `REPO_ROOT` are defined in `install_base.py` alone.

| check | in a checkout | outside |
|---|---|---|
| `install_include_lines`: no include lines for the repository itself, written by a project install | skips that project | stands down: writes the lines for any project |
| `uncommitted_sources`, before an agents-file write into a user harness directory | refuses on uncommitted sources; a failed `git status` refuses with `InputError` | returns `()` without running git |

Only a missing premise stands a check down: in a checkout nothing changes.
