# Stage 1 — the dicing verbs (devpro absorbs its tooling)

The plan executes stage 1 of the accepted design `ACTIVE_DESIGN.md` (17 entries; final form,
user-accepted). The design's one stage-marker line — `(Stages 2-4: the five pairs below wait for
their stages' plans; the four pairs above are stage 1's.)` at `ACTIVE_DESIGN.md:229` — defers the
five pairs whose `As it stands:` lines are 231, 244, 256, 273 and 284, all in the *Shipped files*
entry. Every other pair is stage 1's: 35 of the design's 40 pairs (`grep -c '\*\*As it stands:\*\*'
ACTIVE_DESIGN.md` → 40). This plan applies those 35 and carries the work they describe; the five
deferred pairs stay pending for stages 2–4.

Every package's intended lifetime is **shipped**. Each package closes in one commit, whose message
carries the attribution line every commit here carries. Dispatches read this plan's section plus the
cited design entries, not the whole design.

## Status

| Package | State | Rating | Lifetime | Done |
|---|---|---|---|---|
| | drafted | — | — | kickoff: this plan is committed and its checks run |
| P1 | landed | expert | shipped | `just dev-check-links` |
| P2 | landed | mechanical | shipped | `just test devpro`, `just check-wheel` |
| P3 | in progress | mechanical | shipped | `just test devpro` |
| P4 | dispatchable | expert | shipped | `just test devpro` |
| P5 | dispatchable | mechanical | shipped | `just test` |
| P6 | dispatchable | mechanical | shipped | `just test devpro`, `just check-wheel` |
| P7 | dispatchable | expert | shipped | `just test devpro` |
| P8 | dispatchable | expert | shipped | `just dev-check-links`, `just dev-check-design-deltas-applied` |
| PR | dispatchable | expert | shipped | `just dev-check-links` on the review document |
| PB | dispatchable | expert | shipped | review document's findings have packages |

Sequencing is P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8. The order matters in three places: P5
rewrites the justfile before P6 removes the source tree the old recipes read; P6's
`retake-reference` runs after P4 has changed the rendered bodies, so one retake covers both; P7's
cleanup mechanism tests the state P6 creates (no shipped docdicer row). Packages sharing the tree
run serially.

## P1 — the Dicing and Checks section, carried whole

**Scope.** New: `PROJECT_DOCS/SPEC/dicing-and-checks.md`, `PROJECT_DOCS/SPEC/dicing/**`. Edited:
`PROJECT_DOCS/SPEC/entry-point.md` (one line, the entry's pair).

**The design leaves two decisions to this package:** how the carried contract splits across the
section's leaves, and what of the hosted clone's docs tree is absorbed.

**Work.**

1. Create `PROJECT_DOCS/SPEC/dicing-and-checks.md` holding the *Dicing and Checks* entry's
   `Becomes` block verbatim (`ACTIVE_DESIGN.md:86–129`), then list the carried leaves below it.
   This applies that entry's pair and the *SPEC entry point* pair (`ACTIVE_DESIGN.md:133–143`,
   the link line `- [Dicing and Checks](dicing-and-checks.md)`); two of the stage-1's 35 pairs.
2. Carry docdicer's full verb contract into the leaves, stated implementation-agnostically. The
   source is `docdicer/SPEC.md` §3–§10 (lines 51–676 of that file) plus the shared behaviors §2
   states that the section text does not: streams, current directory, text handling, and the
   split-level option (`dice-doc` and `undice` take it — the source's third taker, `verify`, is
   not offered). Guided split, which the executor may regroup provided every leaf is listed
   by its parent and every message table is carried whole:
   `dicing/index.md` (entry point, lists the leaves, carries the shared behaviors),
   `dicing/tree.md` (§3, §3.1–§3.3), `dicing/links.md` (§4, §4.1–§4.4, §5),
   `dicing/verbs.md` (§6, §6.1, §7, §7.1, §7.2), `dicing/checks.md` (§8 as the offered surface
   holds it — §8.1–§8.2 and §8.4–§8.8, with §9), `dicing/kanban.md` (§10, §10.1–§10.7).
   §8.3 is not carried: the offered `verify` verb left the surface in the design's amendment
   (commit `8a88e92`), and the round-trip check it re-ran — the monolith re-diced, the tree
   reassembled, the links resolved — is the dicing's own commit gate, as the section text states;
   the reassembly (§8.1) and link (§8.2) checks it re-runs are carried in their own right as that
   gate's machinery.
   Implementation-agnostic substitutions: the program name `docdicer` reads as the dicing verbs of
   the `devpro` command; every verb name is kept as-is; references to `tools/docdicer`, the
   launcher, the on-demand venv install and docdicer's own version are dropped — the section text
   states the prerequisite is the devpro package on the host, and `devpro --version` is the
   version. The checks' message tables and §10's board moves and refusals are carried verbatim.
3. The hosted clone's docs tree — `docdicer/docs/` (`checks.md`, `commands.md`, `development.md`,
   `dicing.md`, `kanban.md`, `images/`) — is absorbed **in nothing**: `commands.md` restates the
   offered surface the section already forbids restating beyond the contract, and the rest is
   how-to prose the rewritten skill will not carry. It retires with the clone (P6 deletes it).
   Fact: `command ls docdicer/docs` → those six entries.

**Done.** `just dev-check-links`, run once, at the end. Every new file is listed by its parent and
reachable from `SPEC/entry-point.md` (check-tree), and every relative link and anchor resolves
(check-links).

## P2 — the absorbed dicing package

**Scope.** New: `devpro/dicing/**` (from `docdicer/docdicer/`), `tests/dicing/**` (from
`docdicer/docdicer/test/`). Edited: `devpro/cli.py` (verb wiring only), `pyproject.toml`
(package-data patterns), `tests/conftest.py` only if the moved tests need a fixture.

**Facts.** `command ls docdicer/docdicer` → `__init__.py __main__.py dicerlib kanban test`;
`command ls docdicer/docdicer/kanban/assets` → `board.css board.js index.html`;
`docdicer/pyproject.toml` → `requires-python = ">=3.9"`, `dependencies = []`, package data
`"docdicer.kanban" = ["assets/*"]`. devpro is `dependencies = []` too (`pyproject.toml:14`) — no
third-party dependency enters. `git grep -c docdicer -- devpro/ tests/` → eleven files:
`devpro/definitions/skills/development.py` 9, `devpro/definitions/skills/docdicer.py` 23,
`devpro/definitions/skills/guide.py` 6, `devpro/docdicer-tools/docdicer` 7,
`devpro/docdicer-tools/runner-snippets/docdicer.just` 24,
`devpro/docdicer-tools/runner-snippets/docdicer.mk` 24, `devpro/install.py` 9,
`tests/test_cross_references.py` 3, `tests/test_devpro_install.py` 34,
`tests/test_docdicer_tools.py` 24, `tests/test_plugins.py` 1. None import docdicer: the three
definitions files are P4's, the `docdicer-tools` tree P6's; P6 updates the remaining counts.

**Decisions this plan makes.**

- Layout: rename only the outer package. `devpro/dicing/` holds `dicerlib/` and `kanban/` as they
  stand, `kanban/assets/**/*` the package data. docdicer's `__main__.py` is not carried; its
  argparse verbs and dispatch move to `devpro/dicing/cli.py` exposing `add_verbs(subparsers)` and
  `run(args) -> int`, preserving the argument handling, the exit codes (0 success, 1 a step or
  check failed, 2 usage error or refusal; `kanban` serves until interrupted and exits 0 either
  way) and the message text the contract carries. docdicer's `__version__` constant is not carried
  as an offered version.
- `devpro/cli.py` gains the nine subparsers — names as-is: `dice-doc undice dice-docs
  check-links check-tree check-plan check-design check-roadmap kanban` — from
  `devpro.dicing.cli.add_verbs`, dispatched in `_run` by the dicing branch, which passes the
  returned exit code through `sys.exit`. The install verbs' behavior is unchanged. The absorbed
  code keeps its internal `verify` function — the round-trip check `dice-doc` and `dice-docs` run
  before committing their write, the dicing's own commit gate — but it gains no subparser: only
  the offered verb is gone, not the mechanism.
- `pyproject.toml` `[tool.setuptools.package-data]` gains the pattern `dicing/kanban/assets/**/*`
  (the `.*`-pattern need does not arise: no dotfile ships). `[tool.setuptools.packages.find]`
  already includes `devpro.*`.
- Tests: the fifteen test modules of `docdicer/docdicer/test/` join `tests/dicing/` under the same
  names, with `docdicer.test.data` → `tests/dicing/data/` and the `temp/` scratch recreated by the
  tests under pytest's `tmp_path` where they used it; imports rewritten `docdicer.` →
  `devpro.dicing.`. The devpro test surface runs `tests/` (`justfile` TEST_SURFACE_MAP:
  `tests/ devpro`), so they join it under that name.

**Tests.** The moved tests pin the absorbed behavior wholesale. One new test,
`tests/dicing/test_cli_surface.py`: `devpro --help` lists the nine verbs. Its defect, by the
test-precondition clause (`clauses.TEST_PRECONDITION`,
`devpro/clauses.py:170`): the nine verbs are the dicing surface's command-line offering; before the
change `devpro dice-doc` is refused by argparse (`invalid choice: 'dice-doc'`, exit 2), so the
offered surface does not include them. Failing run before the change:
`PYTHONPATH=. python3 -m devpro --help` lacks every verb name.

**Done.** `just test devpro`, then `just check-wheel` — the wheel proof reads every non-`.py` file
git tracks under `devpro/`, so the asset files must be in the pattern or it fails.

## P3 — lazy dispatch at the entry point

**Scope.** `devpro/cli.py` only, plus one stated exemption in a pinning test: the lazy dispatch's
function-level imports are what `tests/test_devpro.py:1461`'s `test_every_import_is_at_module_level`
walk forbids, and the design's *Packaging* entry states the lazy outcome — so the test gains
`devpro.cli` as its one exempt module, stated as the design's exception: the entry point imports
verb modules at dispatch time. The house rule (every import at module level) holds for every other
module of the package, and the test keeps asserting it package-wide except for the one module. The
design's *Packaging* entry states the outcome
(`ACTIVE_DESIGN.md:505–507`): "The dispatch is lazy: the entry point imports only the verb invoked,
and every verb imports no third-party dependency (Package and Command), so no verb pays for
another verb's imports."

**Fact.** `devpro/cli.py:14–32` imports `agents_file`, `components`, `context`, `errors`,
`install`, `install_target`, `render` and `vocabulary` at module level; `git grep -n 'import'
devpro/cli.py` shows them. `components`, `context`, `vocabulary` and `errors` feed parser help
text (`families()`, `COMPONENTS`, `HarnessText`, `key`) and stay module-level; the heavy verb
modules — `agents_file`, `install`, `install_target`, `render`, and the new `devpro.dicing.cli` —
move inside `_run`'s branches.

**Test.** New, in `tests/test_devpro.py`: a subprocess imports `devpro.cli` and asserts none of
`devpro.install`, `devpro.render`, `devpro.agents_file`, `devpro.dicing` is in `sys.modules`. Its
defect: the entry point imports every verb's module while building the parser, so running any verb
— `--help` included — pays for the install machinery, and a later stage's verb could not opt out
of another's import cost. Failing run before the change: the same import shows `devpro.install` in
`sys.modules`. The invariant test's edit is the exemption above: `devpro.cli` named as the one
module whose imports the design moves to dispatch time, with the house rule re-stated for the rest.

**Done.** `just test devpro`.

## P4 — the definitions route the verbs

**Scope.** Edited: `devpro/definitions/skills/docdicer.py`, `devpro/definitions/skills/guide.py`,
`devpro/definitions/skills/development.py` (one sentence), `tests/test_cross_references.py` (one
constant). This carries the code side of the *Subsystem Map* entry (`ACTIVE_DESIGN.md:704–766`).

**Facts.** `devpro/definitions/skills/docdicer.py:45–67` is the body's *The script* section, naming
`tools/docdicer`, the recipes `docdicer-check-plan` … `docdicer-kanban` and the on-demand install.
`devpro/definitions/skills/guide.py:451–457` names `tools/docdicer kanban --help`, `just
docdicer-kanban` and the include line; `guide.py:36` and `guide.py:109` stay as they stand.
`devpro/definitions/skills/development.py:148–153` names
`docdicer-check-design-deltas-applied` — the runner recipe the entry's third pair retires.
`tests/test_cross_references.py:30` — `_PROGRAM_NAMES = frozenset({"docdicer", "kbase"})` — pins
the retiring fact that docdicer is a program; the absorbed verbs are devpro's own, and no
definition body may spell a program name outside a reference hole.

**Work.**

1. `docdicer.py`: rewrite the body per the entry's first pair — the skill routes the session to
   devpro's dicing verbs run from the command line, does not restate their `--help`, carries no
   install step and no runner instruction; the *The script* section and the recipe names are
   deleted. The `kanban` paragraph keeps its offer, and the `kb-root/` paragraph keeps its
   optional kbase reference. The description keeps the uses it lists.
2. `guide.py`: the board section (451–457) routes the board through the docdicer skill's routing
   and names no launcher path or recipe; the `*The script*` cross-reference at 451 is deleted with
   the section it names.
3. `development.py`: the delta-application sentence names no runner recipe — the application is
   verified by `check-design --deltas-applied`, the recipe it named retired with the docdicer
   tools package.
4. `tests/test_cross_references.py`: `_PROGRAM_NAMES` becomes `{"kbase"}`. The pinning state
   already holds before 1–3 and holds after: `git grep -n '`docdicer`' -- devpro/definitions/`
   exits 1 with no matches — no definition body spells `docdicer` as a bare program in backticks
   at all (the ` skill` forms the rule admits and the `tools/docdicer` paths are not backtick-
   delimited bare words) — so this item narrows a set whose check passes before and after, and no
   rendered output changes from it.

**Pinning.** `tests/test_kbase_surface.py` checks the kbase names only — untouched.
`tests/test_plugins.py:53` parametrizes the refusal cases over `docdicer` as a definition name —
the skill still ships, untouched. The rendered reference slots go stale here and in P6; P6's
single `retake-reference` covers both.

**Done.** `just test devpro`.

## P5 — the justfile runs the absorbed verbs

**Scope.** `justfile` only, plus the retirement of `devtools/scripts/docdicer-repo.sh` and
`devtools/tests/test_docdicer_repo.py`. Carries the code side of the *Recipes* entry
(`ACTIVE_DESIGN.md:512–539`).

**Facts.** `justfile:353` — `import? ".opencode/plugins/devpro/skills/docdicer/tools/runner-snippets/docdicer.just"`.
Recipes routing through the clone: `docdicer-repo` (317), `dev-dd` (321), `dev-kanban` (325),
`dev-check-plan` (333), `dev-check-design` (337), `dev-check-design-deltas-applied` (341),
`dev-check-roadmap` (345), `dev-check-links` (349). Recipes routing through `just docdicer` (the
installed snippet): `dice-doc` (162), `dice-docs` (168), `undice` (174), `check-links` (181). The
only justfile comment block naming the hosted tool and the pin is the delta-check comment at
283–286; the justfile carries no toolchain comment (`grep -n '1\.33\|1\.27\|toolchain' justfile`
→ no hits) — the toolchain-floor statement the *Recipes* pair changes lives in
`PROJECT_DOCS/ARCHITECTURE/recipes.md` and lands with its pair (P8).
`devtools/tests/test_docdicer_repo.py` reads the `docdicer-repo` recipe body and
`devpro/docdicer-tools/docdicer` — both retire here.

**Work.**

1. `dice-doc`, `dice-docs`, `undice`, `check-links` run the absorbed verbs:
   `PYTHONPATH="{{PROJECT_ROOT}}" python3 -m devpro <verb> …` — the install recipes' idiom, needing
   no venv since the package imports nothing third-party.
2. `dev-check-plan/design/design-deltas-applied/roadmap/links` run the absorbed verbs the same
   way, with no file argument where the old recipe gave none (`check-plan` reads the active file
   under the project root), and `dev-check-design-deltas-applied` passing `--deltas-applied`.
3. Retire: the `docdicer-repo`, `dev-dd`, `dev-kanban` recipes; the `import?` line; the delta-check
   comment block at 283–286, rewritten to the entry's statement — the design's delta application
   is verified by `check-design --deltas-applied` over the absorbed verb. There is no second
   justfile comment block to rewrite (see Facts): the toolchain floor is the *Recipes* pair's own
   text, landing in `PROJECT_DOCS/ARCHITECTURE/recipes.md` at P8.
4. Delete `devtools/scripts/docdicer-repo.sh` and `devtools/tests/test_docdicer_repo.py` — the
   script's last references are the recipes this package retires (`git grep -n 'docdicer-repo' --
   justfile devtools/` → `justfile:318` and the test, both gone with this package), and the
   test's subject — the recipe and the pin it reads — is gone with them.

**Named breakage the plan accounts for.** `just dev-check-design-deltas-applied` reports the
design's pairs not yet applied — 33 miss until P8; the five stage-2–4 pairs report pending
permanently in this stage. Neither is this package's failure.

**Done.** `just test` — the full run exercises the justfile directly (TEST_SURFACE_MAP:
`justfile ALL`) and covers the devtools tests that remain.

## P6 — the tools package retires

**Scope.** Edited: `devpro/install.py`, `pyproject.toml`, `devtools/scripts/render.sh` (one
comment), `tests/test_devpro_install.py`. Deleted: `devpro/docdicer-tools/**`,
`tests/test_docdicer_tools.py`, the gitignored `docdicer/` clone. Carries the code side of the
*Repo Layout*, *Plugins* (install) and *Renders and copies* entries.

**Facts.** `devpro/install.py:79` — `DOCDICER_TOOLS_PACKAGE = "skills/docdicer/tools"`;
`:110–115` — the `docdicer-tools` row with `SnippetSet("docdicer", "runner-snippets", …)`;
`pyproject.toml:30` — the patterns `docdicer-tools/**/*` and `docdicer-tools/**/.*`;
`devtools/scripts/render.sh:36` — the comment naming the docdicer include line in slot projects.
`git grep -c docdicer -- devpro/ tests/ devtools/` → fourteen files (the eleven of P2's Facts plus
`devtools/scripts/docdicer-repo.sh` 8, `devtools/scripts/render.sh` 1,
`devtools/tests/test_docdicer_repo.py` 11). At P6's start, P5 has removed the script, its test and
the justfile references, and P4 has rewritten the three definitions files (their counts drop); run
the same command before editing and reconcile what it shows against this.

**Work.**

1. `install.py`: delete `DOCDICER_TOOLS_PACKAGE`, the `docdicer-tools` `ShippedPackage` row and
   the `docdicer` `SnippetSet` — the table holds the development-tools and kb-tools rows. The
   stale-list walk and banner stamping (`STAMPED_NAMES` drops `docdicer`) read the table.
   **Verified code truth, and what the retirement leaves:** the old `skills/docdicer/tools/`
   destination is *not* pruned by a later install, and neither half of that is a removal with a
   `.venv` carve-out. `prune`'s stale test reads `_is_ours` (`devpro/install.py:319–323`), which
   reads the *generated* banner, never the *installed* one a copied package file carries
   (`_is_ours` at `:245–254`; the docstring at `:310–313` states it — a copied package file "is
   untouched here rather than pruned") — and a `.venv` is outside `_shipped` by `EXCLUDED_DIRS`
   (`:142`). So no row replaces the old destination, and nothing prunes it: every install after
   this one leaves `skills/docdicer/tools/` and its `.venv` in place, inert once P7 has removed
   the include line that routed to it. The design states no removal of it, and none is added
   here; the lingering copy is the operator's to delete. What does clear it: the reference slots
   (item 7 — `_render-slot.sh` removes and rebuilds each slot) and P7's include-line cleanup.
2. Delete `devpro/docdicer-tools/` and `tests/test_docdicer_tools.py`.
3. `pyproject.toml`: drop the two `docdicer-tools` patterns.
4. `tests/test_devpro_install.py`: update the tests pinning the row — the include-line fixtures
   (603, 651, 1197, 1210, 1253–1272), the packages-ship assertions (587–603), the launcher-stamp
   and venv tests (1454–1487) — to the two-row state. `tests/test_plugins.py:53` is untouched.
5. `devtools/scripts/render.sh`: the slot comment names the kb line only.
6. Delete the gitignored `docdicer/` clone (`command rm -rf docdicer`): P5 retired every recipe
   that routed to it, and P1 carried its contract. Untracked, so no commit content records it.
7. `just retake-reference` — the rendered reference slots lose `skills/docdicer/tools/` and gain
   P4's definition bodies; the retake re-takes all four from the current generator, in this change.

**Done.** `just test devpro`, then `just check-wheel`.

## P7 — the runner-file cleanup and the empty runner file

**Scope.** `devpro/runner_file.py`, `devpro/install.py` (the call site's retired-set argument),
tests in `tests/test_devpro_install.py`. Carries the code side of the *Plugins* entry's second
pair (`ACTIVE_DESIGN.md:348–352`), whose mechanism the design states at `ACTIVE_DESIGN.md:605–609`
— recognized by the same shape rule that recognizes its own lines (`_snippet_pattern`).

**Facts.** `devpro/runner_file.py:62–70` — `_snippet_pattern` recognizes a line by the shape of the
path it names; `:89–106` — `_named_harnesses` finds every non-comment line, naming the harness its
first path segment claims; `:149–195` — `install_include_lines` writes each set's line and creates
a `Makefile` when the project has neither runner file (`:170–183`), whose banner is the constant
`# Makefile — created by the devpro installer.` at `:177`.

**Decisions this plan makes.**

1. **Cleanup of the retired set.** The install recognizes the docdicer set's lines with
   `_snippet_pattern` on the retired set's directory and snippet names, removes every such
   non-comment line whose first path segment is this install's harness directory, names each
   removal in the install report, and reports-and-leaves a docdicer line naming another harness
   directory's snippets. A retired set removes lines; it never writes one, so the merge-refusal
   path does not apply.
2. **No runner file is created for no lines.** `install_include_lines` returns before the
   `Makefile` branch when `snippet_sets` is empty: a project with neither runner file and no
   include line to write gets neither created nor touched.
3. **The created Makefile left holding no line.** A runner file the install itself created — its
   first line the constant banner — that holds no include line after the docdicer line's removal
   and nothing the consumer wrote beyond the banner and blank lines is removed by the same
   cleanup, the removal named in the install report. One holding consumer content (its own
   targets, added below the banner as the banner invites) is left, reported as holding no include
   line. The install never removes a runner file it did not create.

**Tests.** Three, in `tests/test_devpro_install.py` beside the include-line fixtures, each named
by the test-precondition clause:

- *The retired line outlives the package it names.* Defect: after P6 no install touches a
  docdicer include line, so a consumer's justfile holds an `import?` for snippets the next install
  prunes — the recipes vanish silently. Failing run: install a claude-project fixture whose
  justfile carries the docdicer line twice, assert both are gone and both removals reported.
- *A runner file is created for no lines.* Defect: a project install without the kbase component
  into a project with neither runner file creates a `Makefile` holding a banner and no include
  line — a runner file that runs nothing. Failing run: the same install asserts no `Makefile`
  exists.
- *The install-created Makefile is removed with its last line.* Defect: the cleanup removes the
  docdicer line but leaves the install-created file holding nothing. Failing run: a fixture
  `Makefile` holding the banner, one blank line and the docdicer line is removed; a second holding
  the banner and a consumer target is left with a report.

**Done.** `just test devpro`.

## P8 — the stage-1 pairs land and CONVENTIONS re-points

**Scope.** Edited: the PROJECT_DOCS leaves the 33 remaining stage-1 pairs target, plus the three
CONVENTIONS changes, `PROJECT_DOCS/SPEC/guide-and-readme.md`, `README.md` (one line). This
package applies every stage-1 pair not already landed — P1 applied two; the remaining 33:

Plan Status Form (1), Package and Command (2), Surfaces and layout (1), Shipped files (4),
Plugins (3), Installed tree (3), Install destination (1), Write Safety (2), Repo Layout (2),
Packaging (2), Recipes (1), Plugins-install (3), Renders and copies (4),
Why-there-is-no-verification-verb (1), Subsystem Map (3). Each `becomes` block replaces its from
block in the entry's named target, with each run of whitespace read as one space.

**Work.**

1. Apply the 33 pairs verbatim.
2. CONVENTIONS: delete
   `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/docdicer-pin-is-a-release.md` and its
   two Contents lines — `code-definitions-and-install/index.md:23` and
   `CONVENTIONS/entry-point.md:33` (`git grep -n 'docdicer-pin' -- PROJECT_DOCS` → exactly those
   two, plus the deleted leaf). Re-point
   `adding-definitions/a-skill-omits-its-tool-s-offered-surface.md`: the docdicer paragraph names
   `devpro --help` as the offered surface — the dicing verbs' help — and drops the pin and its
   version. Re-point `planning-and-execution/a-delta-application-ends-verified.md`: the runner
   target runs the absorbed verb — `just dev-check-design-deltas-applied` runs `python3 -m devpro
   check-design --deltas-applied`; the hosted clone and the pin are named no more.
3. `PROJECT_DOCS/SPEC/guide-and-readme.md:38`: the justfile floor reads the *Recipes* entry's
   statement — 1.27.0 generally, 1.33.0 where the kbase component ships. The design cites this
   leaf; this edit is implementing it.
4. `README.md:9`: "Work packages on the board `docdicer kanban` serves" names the board command —
   `devpro kanban` now. The acknowledgments entries at 30 and 158 credit the absorbed project and
   stand.

**Done.** `just dev-check-links`, then `just dev-check-design-deltas-applied`. The run reports
every stage-1 pair landed; it exits non-zero naming the five Shipped-files pairs — the stage-2–4
work this design holds pending — which is the stage's expected state, not a failure of this
package. After writing: run `just dev-check-plan` and `just dev-check-links`; fix what they report.

## PR — post-plan review

The reviewers receive the project documents and `ACTIVE_DESIGN.md`, not this plan, and review the
changes and their tests against the project's standards: the project's Python coder agent (the
absorbed package, the entry point, the runner file), `devpro-architect` (structure), and
`devpro-prompt-engineer` (the rewritten skill bodies are model-facing text). The
`devpro-tech-writer` seat joins for the README and guide changes. Each reviewer writes their own
review in `.devpro-temp/`; the session synthesizes `ACTIVE_PLAN_REVIEW.md` from them,
de-duplicating, without waiting between the last report and the write-up.

**Done.** `just dev-check-links`, run once, at the end. The target checks the tracked documents —
`PROJECT_DOCS` and the top-level `*.md` files. The review document lives in scratch and is not in
its path; the done-line claims no coverage of it.

## PB — post-plan burndown

Until PR lands, this section holds only: "Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan
review lands." Then the burndown's work list is drafted from the review document, replacing this
text; it takes `devpro-prompt-engineer` usability review and revision before it is dispatchable.

## Notes the packages run under

- **Pair application.** A pair lands when its `becomes` block occurs in its target with each run
  of whitespace read as one space and the from-text gone where the becomes-text does not contain
  it. P1 applies two; P8 applies the remaining 33; the delta check at P8 confirms all 35.
- **The status table.** A package's row states the condition that makes it what it is, and is
  updated in the commit that carries its work.
- **Dispatchability.** Every scope above is named in files and symbols; every fact carries the
  command that produced it; every behavior change names the tests and fixtures pinning it; every
  new test names its defect by the test-precondition clause; every done-line names the runner
  targets, run once at the package's end.
