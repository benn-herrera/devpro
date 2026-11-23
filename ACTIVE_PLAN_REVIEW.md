# ACTIVE PLAN REVIEW — an installation that runs its own devpro

Range reviewed: `3cb382d..HEAD` at `c9f02b2`. Seats: `devpro:python-coder` (py),
`devpro:shell-dsl-coder` (sh), `devpro:architect` (arch), `devpro:prompt-engineer` (pe),
`devpro:tech-writer` (tw). Gates at review: `just test` 1678 passed, 1 skipped; `just lint`,
`just dev-check-links`, `just dev-check-roadmap` exit 0.

One ID per defect; each names every seat that reported it. Groups are by root cause.

## A. The installation's copy is not protected from itself

The installation's own copy restores the isolation of a project's devpro from global installation
changes; these findings are the places that isolation does not yet hold.

- **R1 — Critical (py C1, arch C1).** An install run through the installation's wrapper
  (`<ROOT>/tools/devpro.sh install <project>`) empties its own copy before reading from it.
  `require_outside_package_source` (`devpro/install_target.py:89`) refuses only a target at or
  inside `PACKAGE_ROOT`, not one containing it; `install()` clears every package destination
  (`devpro/install.py:644-645`) before `source.read_bytes()` (`devpro/install.py:646`). Result: an
  empty copy, a wrapper with nothing to run, every `devpro-*` recipe failing, capture silently off.
  Fix: refuse, before any write, an install whose root contains `PACKAGE_ROOT`, naming the `devpro`
  on PATH as the way to update. SPEC first: Install destination's refusals gain this one. Test that
  fails before: a second install with `PACKAGE_ROOT` patched to the first install's copy leaves the
  copy in place and exits 2.
- **R2 — Warning (py W3).** The wrapper's `exec "${python}" -m devpro` puts the working directory
  ahead of the copy on `sys.path`, so run from a directory holding a `devpro` package — this
  repository's root among them — it runs that package, not the copy. Contradicts SPEC Shipped files
  ("runs that copy"). Fix: the wrapper runs a script beside it in `tools/` rather than `-m`, so the
  script's directory leads `sys.path` on every supported Python. Site: `devpro/install.py`,
  `_WRAPPER_TEXT`.
- **R3 — Warning (py W1).** `root / WRAPPER` is not among the targets `_refuse_foreign_targets`
  checks (`devpro/install.py:614`): a project's own `tools/devpro.sh` is overwritten silently, and a
  directory there fails the install after package copies are written. Contradicts SPEC Write Safety.
  Fix: add it to the checked targets; the wrapper's `!INSTALLED!` banner already identifies one an
  earlier install wrote.
- **R4 — Warning (sh F2, py W4).** A wrapper that exists but does not run falls through to PATH,
  which `hp.sh`'s own header rules out: `hp.sh:35` tests `-x`; `devpro_executable`
  (`devpro/profiler/hooks.py:74`) tests `X_OK`. And `profiler doctor` checks other candidates than
  the launcher does (only the repo-level path, not the launcher-relative one) and runs no
  `--version` probe, so it can name a devpro the hook does not run. Fix: both test existence and let
  the usability probe decide; doctor walks the launcher's candidates for each launcher
  `hook_sources` finds.

## B. The wrapper path has no single source

- **R5 — Warning (pe 1, arch W1).** `../../tools/devpro.sh` resolves only from the skill's own
  directory, and the definitions say so at one site of four. Profiler (`profiler.py:49`) pairs it
  with "Run it in the repository the trace belongs to", and the skill `profiler init` writes into
  `.claude/skills/profiler/` resolves it to `.claude/tools/devpro.sh`, which nothing writes. Guide
  (`guide.py:109,469,472`) carries it into `references/` pages, one directory deeper. Docdicer
  (`docdicer.py:47-59`) anchors it but does not say to run from the project root, while `dashboard`
  serves the working directory. Fix: one constant in `devpro/clauses.py`, composed into all three
  definitions — the wrapper resolved from the skill's directory to an absolute path, run with the
  project root as working directory — and, for the profiler skill `init` writes, a second candidate
  at the repository root's installed wrapper, as the launcher already has.
- **R6 — Warning (arch W2, py N1).** The claude project install's wrapper location is written in
  `hp.sh:34` and again in `devpro/profiler/hooks.py:56` (`INSTALLED_WRAPPER`), beside its source in
  the claude harness profile; no test ties them. Fix: derive `INSTALLED_WRAPPER` from the claude
  harness profile, and one test asserting `hp.sh`'s candidate equals it (`hp.sh` keeps its literal,
  as a verbatim resource).

## C. Runner snippet and shell defects

- **R7 — Critical (sh F1).** `devpro/runner-snippets/devpro.just:33,37,41,45,49` interpolate
  `{{source_directory()}}/../devpro.sh` unquoted; in a project path with a space every `devpro-*`
  just recipe exits 127 (probe: `.devpro-temp/p6-shell-probe.log`). `devpro.mk` is unaffected. Fix:
  quote the path (`{{quote(...)}}` also survives `$` and `"`); the snippet test run from a
  directory whose name holds a space fails before.
- **R8 — Note (sh F7, F8).** `hp.sh`: `find_devpro`'s `here` and `candidate` are not `local`; the
  file has no `set -euo pipefail` and its header gives no reason, as CONVENTIONS *Shell in this
  repository is bash* requires; `cd` without `CDPATH=` can corrupt `here`. The same `cd` idiom is in
  `_WRAPPER_TEXT`.
- **R9 — Note (sh F5).** `devtools/scripts/render.sh:40` and `_render-slot.sh:21` export
  `DEVPRO_DEV=1` but run no gated verb; ARCHITECTURE Recipes lists them among scripts that do. Fix:
  drop both exports and shorten the list to `render-agents-file.sh` and `_harness-value.sh`.
- **R10 — Gap (sh G1).** No runner target lints shell and `shellcheck` is not installed; no shell in
  the range has been through it. Fix: a shellcheck step in `lint` (or a `lint-shell` recipe), with
  `shellcheck` declared where ARCHITECTURE Recipes lists the suite's tools.

## D. Contract text the code contradicts

- **R11 — Warning (arch W3, sh F3, sh F4).** SPEC Package and Command (`package-and-command.md:9`):
  "the same arguments install the same product, byte for byte" — false across interpreters, since
  the wrapper records the interpreter that ran the install; `check-wheel.sh:79` runs both sides
  under one interpreter, which holds the gate but not the claim. Fix: SPEC qualifies the sentence to
  the same interpreter, naming the wrapper's recorded interpreter as the one value that follows it;
  ARCHITECTURE Recipes' account of check-wheel's checkout side (still "`python3`") is corrected.
- **R12 — Note (arch N1, py W5, sh F6).** ARCHITECTURE `install/renders-and-copies.md:59` (the
  wrapper) and `install/harness-profiler.md:19` (`hp.sh`) say "POSIX-sh"; both are bash. Fix: "bash".
- **R13 — Note (arch N4).** ARCHITECTURE Repo Layout's dependency sentence omits `profiler/` →
  `kanban/` (`devpro/profiler/pages.py:99`, the shared stylesheet) and names `dicing/` where what is
  shared is `dicing.dicerlib`.
- **R14 — Note (pe 5).** ARCHITECTURE `install/harness-profiler.md` says the launcher is claude's
  alone and, in its opencode paragraph, that an opencode install carries `profiler/hp.sh`; SPEC
  Shipped files agrees with the second. Fix the first sentence.
- **R15 — Note (pe 4).** SPEC `deployed-surfaces/installed-tree.md:40-44`: the rule for naming a
  script "inside a skill's own directory" cites the launcher and the wrapper, neither inside one
  (`shipped-files.md` puts `tools/` inside no skill's directory). Fix the rule's scope.
- **R16 — Note (pe 9).** ARCHITECTURE `subsystem-map.md:56,63,73` narrates the change ("is back",
  "retired with it", "now … has retired"). State the fact; drop the retirement clauses.
- **R17 — Note (pe off-seat).** Unsettled document claims, for the architect seat to settle in the
  burndown: `subsystem-map.md:87-88` says only the `development` and `docdicer` guide rows use a
  plain `clauses.ref` (`guide.py:37` gives `profiler` one too); `packaging.md`'s "five modules
  `tests/test_devpro.py` exempts by name" and "`devpro/cli.py` composes the other four's
  `add_verbs`".

## E. Definitions: stale and loose text

- **R18 — Warning (pe 3, pe 13, tw 1).** The retired dicing snippets package is still named as
  current: `guide.py:102` (upgrade walk), `docdicer.py:1-2` (docstring: "the dicing verbs of the
  `devpro` command"), CONVENTIONS `adding-definitions/a-skill-omits-its-tool-s-offered-surface.md:12`
  (`devpro --help`), and README (Quick Start include-line paragraph; Updating's 0.17.x paragraph).
  Each names what the install delivers today, as SPEC Shipped files names it.
- **R19 — Note (pe 6, 7, 8).** Development skill, *Plan status* Rating and *Dispatch*
  (`development.py:246,326-330`): "bounded by *Dispatch*" names no constraint; "model set" is
  defined nowhere; the *Purpose* gives one reason twice; and "a `Rating` cell's note names neither a
  model nor a step-down binding" is an unchecked never. Fix: the Rating sentence says the note names
  no model (*Dispatch*); "resolved when the dispatch is made, as *Terms* states"; `check-plan`
  refuses a Rating note holding a model name or `<category>=<model>` pair. Unverified (pe): whether
  resolution at dispatch avoids the failure the rule was written for, since the pinned
  `comm-mechanical=haiku` equals the *Terms* default.
- **R20 — Note (pe 10, 12).** `guide.py:466-475` repeats docdicer's dashboard paragraph (command,
  address, redirect, stop controls) — keep the routing sentence and what the board shows.
  `docdicer.py:54-57`: say which four recipes are the argumentless gates.

## F. README

- **R21 — Warning (tw 2).** README does not say an install gives the project its own copy of devpro
  and wrapper. The README states it as the property it is: a project's devpro is insulated from
  global installation changes — a `brew upgrade` changes no project's checks — and an upgrade reaches
  a project when its install is rerun, which Updating presents as the way to take one. Links to SPEC
  Shipped files for the wrapper's detail.
- **R22 — Warning (tw 3, 4).** Requirements omits Python 3.9 or later (generator and wrapper), and
  names no supported platforms: macOS and Linux supported, native Windows unsupported and not
  refused, stated once; the Mage-section clause becomes a pointer or goes.
- **R23 — Warning (tw 5).** README's *Next* names `just dev-dashboard` and says it passes arguments
  through; the recipe (`justfile:288`) takes none, and SPEC Guide and README says the README holds
  no runner recipe. Drop the recipe sentence.
- **R24 — Note (tw 7).** Updating's "delete `skills/docdicer/tools/`" must be unmistakable against
  the install directory's live `tools/`.
- **R25 — Note (tw 5a, 6).** Section order (dashboard before Requirements) and developer detail in
  Requirements (the profiler hook paragraph; the "Under mage" bullet). Requirements lists only what
  the reader must have.

## G. Python tidiness

- **R26 — Warning (py W2).** A session whose trace holds the text `/*DATA*/null` cannot be rendered:
  `strict_fill` refuses a value carrying its own mark (`devpro/profiler/pages.py:109-125`), and the
  session JSON leaves `/` unescaped. Probe: `.devpro-temp/p6-python-probe/data_mark_probe.log`.
  Fix: escape `/` as `\/` in one serializing helper used at both call sites (`pages.py:630,1079`),
  which also removes the duplicate serialization (py N3).
- **R27 — Note (py N2).** The install's count line omits the wrapper (`devpro/install.py:670`);
  SPEC Write Safety counts the copied files.
- **R28 — Note (arch N2).** The stamping exemption is a path test in the copy loop
  (`devpro/install.py:837`); make it a `ShippedPackage` field.
- **R29 — Note (arch N3, py N4).** `CHECK_VERBS` (`devpro/cli.py:42`) repeats the names
  `devpro/doccheck/cli.py` registers; have the module export them. The `run` preamble duplication
  with `dicing/cli.py` stays until a third copy.
- **R30 — Note (py N5, N6, N7, N8).** `hooks.py:167-169` inserts by position; `base_interpreter`
  below 3.11 resolves the whole link chain (`install.py:220-228`) — resolve one link; the
  `install.py` module docstring's opening sentence; dead `pop`/reassignment in
  `tests/test_devpro_install.py:1612-1617` and a duplicated assignment in
  `tests/test_devpro_profiler.py` near line 305.

## Needs the user

- **U1 (pe 2).** ROADMAP *Bugs*, "devpro runner-snippets import line not installing", asks
  `just agents` to write the include line into this repository's justfile; SPEC
  `deployed-surfaces/plugins.md:63` says nothing is written into this repository's own runner file.
  The user rules the SPEC sentence unauthorized: this repository's justfile carries the include line.
  State of the tree: `devpro/runner_file.py:231` returns early for `REPO_ROOT`; this repository's
  `justfile` holds no `devpro` include line, so its `devpro-*` recipes are absent. Open for the
  user: whether the install writes the line here (the skip and the SPEC sentence go) or the
  justfile carries it as tracked text (the SPEC sentence is reworded to say so). Separately (pe 11),
  two ROADMAP tickets record surroundings rather than the fact.
