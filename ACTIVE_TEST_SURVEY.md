# ACTIVE TEST SURVEY

The test-suite survey of [the active plan](ACTIVE_PLAN.md)'s P3: an inventory of the suite the strip
left, three lenses over it, the three run-born findings verified each with the command that answers it,
and the judgments the plan's burndown drafts from. This document fixes nothing and runs no behavior
probe of its own beyond the commands it states; it is created here and deleted in the commit that lands
the plan.

The repository was quiescent at the survey's open: `git status --short` answered nothing, HEAD was
`74b91e9f` (P3 dispatches — the test-suite survey inventories what remains), and the strip's last
commit `ed621256` was in history. Every command below ran at that state; each one's output is quoted
where the finding reads it.

- [The inventory](#the-inventory)
- [Lens one — shotgun versus deliberate](#lens-one--shotgun-versus-deliberate)
- [Lens two — tier balance](#lens-two--tier-balance)
- [Lens three — gap by mechanism](#lens-three--gap-by-mechanism)
- [The reorganization inventory's health](#the-reorganization-inventorys-health)
- [S1 — the real-tree case check-wheel lacks](#s1--the-real-tree-case-check-wheel-lacks)
- [S2 — the digest test's literal-banner plants](#s2--the-digest-tests-literal-banner-plants)
- [S3 — the module-split rule's upward-edge half](#s3--the-module-split-rules-upward-edge-half)
- [The judgments](#the-judgments)

The three lenses are the ROADMAP ticket's own
([Maintenance](ROADMAP.md), "The periodic review's panel gains the test-suite audit seat"), applied and
not restated: shotgun versus deliberate, tier balance with its eighty-percent reading rule, gap by
mechanism.

## The inventory

The command per directory, run from the repository root with the venv's pytest and `PYTHONPATH=.`:

```
PYTHONPATH=. .venv/bin/python -m pytest --collect-only -q -m "not cold_read and not slow" <dir>
```

`tests/` collects as the root files and five subdirectories; `devtools/tests/` is the sixth suite the
plan names. The default runs (what `just test` gives) exclude the `cold_read` and `slow` markers, so
those cases are listed separately.

| *tests* | *Default cases* | *Marker cases* | *Subject, in one line* |
| --- | ---: | ---: | --- |
| `tests/test_guardrail.py` | 282 | — | The two guardrail implementations (opencode's `.ts`, claude's `.pl`) held to one case table in `tests/guardrail_cases.json`. |
| `tests/test_cold_read_tools.py` | 5 | 34 (`cold_read`) | The shipped `cold-read.sh` run as a consumer runs it, stub CLIs first on PATH. |
| `tests/test_clause_groups.py` | 20 | — | Definitions sharing a membership clause carry what their group's table lists. |
| `tests/test_cross_references.py` | 15 | — | Definition text names another definition only through a reference hole. |
| `tests/test_install_target.py` | 43 | — | The install verb's target, driven through `main([...])`: harness, root, refusals, agents file. |
| `tests/test_plugins.py` | 21 | — | Component selection in the render: membership, validation, references. |
| `tests/test_kbase_surface.py` | 8 | — | The kbase names the kbase skill cites, held to the installed kbase's stdio surface. |
| `tests/test_opencode_entry.py` | 5 | — | `index.ts` under `bun` against a stub plugin context over a real `kbase` install. |
| `tests/test_devpro_floor_check.py` | 5 | — | The entry point's below-floor refusal and the wrapper that leaves it to the entry point. |
| `tests/_structure.py`, `tests/conftest.py`, `tests/fixtures/` | 0 | 0 | Not tests: the source-rule checker `tests/_structure.py` (which `tests/render/` and `tests/install/` consume), the shared `tests/conftest.py` fixtures, and the one frozen probe record under `tests/fixtures/`. |
| `tests/install/` | 199 | — | The install: target selection, agents file, checkout refusals, dry run, kbase install, redirects, runner file, scratch, selection, staging. |
| `tests/profiler/` | 63 | — | The capture's records, the directives digest, stores, tree render, page data, init, bun runners. |
| `tests/render/` | 282 | — | The renderer: families, frontmatter forms, placeholders, prose rules, refusals, settings, structural rules, package invariants. |
| `tests/dashboard/` | 125 | — | The dashboard's serve surface and the board panel it hands `/board/` and `/api/*` to. |
| `tests/dicing/` | 615 | — | The dicing verbs: the docdicer and kanban case trees, link rewriting and scanning, plan and design forms, the checks. |
| `devtools/tests/` | 78 | 6 (`slow`) | `dupe_sweep` and its import structure, `clause_join_sites`, `render_diff`, `screenshot`. |

The totals the run recorded: `1761/1801` collected with the markers excluded (`40 deselected`), the
`cold_read` surface collects 34 and the `slow` surface 6. The plan's own baseline run, `just test`,
answered `1759 passed, 1 skipped, 40 deselected in 51.72s` plus `links checked: 454, broken: 0`,
`documents checked: 144, problems: 0` and `check-wheel: Python 3.11.18, …devpro-0.18.0-py3-none-any.whl`
(`.devpro-temp/p3-test.log` in the survey's scratch directory, cleared when the plan lands). The one
skip is the filesystem's, not the suite's: `the file system refuses a name that is not UTF-8`
(`tests/dashboard/test_board_panel.py:219`).

By file, where the size sits:

| Directory | File | Cases |
| --- | --- | ---: |
| `tests/install/` | `test_dry_run.py` | 60 |
| | `test_runner_file.py` | 24 |
| | `test_selection.py` | 23 |
| | `test_kbase.py` | 17 |
| | `test_agents_file.py` | 16 |
| | `test_global_agents.py` | 16 |
| | `test_staging.py` | 15 |
| | `test_scratch.py` | 12 |
| | `test_redirects.py` | 9 |
| | `test_checkout.py` | 7 |
| `tests/profiler/` | `test_capture.py` | 16 |
| | `test_init.py` | 13 |
| | `test_tree.py` | 13 |
| | `test_page_data.py` | 7 |
| | `test_served.py` | 5 |
| | `test_stamp.py` | 5 |
| | `test_fill.py` | 2 |
| | `test_runners.py`, `test_stores.py` | 1 each |
| `tests/render/` | `test_structural_rules.py` | 85 |
| | `test_families.py` | 54 |
| | `test_placeholders.py` | 35 |
| | `test_render_refusals.py` | 34 |
| | `test_settings.py` | 31 |
| | `test_prose.py` | 25 |
| | `test_frontmatter.py` | 17 |
| | `test_package_invariants.py` | 1 |
| `tests/dashboard/` | `test_server.py` | 86 |
| | `test_board_panel.py` | 39 |
| `tests/dicing/` | `test_planform.py` | 129 |
| | `test_dicer.py` | 114 |
| | `test_board.py` | 107 |
| | `test_linkrewrite.py` | 72 |
| | `test_plancheck.py` | 37 |
| | `test_outline.py` | 36 |
| | `test_textfile.py` | 29 |
| | `test_reassemble.py` | 26 |
| | `test_linkscan.py` | 18 |
| | `test_anchors.py` | 15 |
| | `test_undice.py` | 11 |
| | `test_cli_surface.py` | 7 |
| | `test_split.py` | 6 |
| | `test_treecheck.py` | 5 |
| | `test_one_document_tree.py` | 2 |
| | `test_citation_targets.py` | 1 |
| `devtools/tests/` | `test_dupe_sweep.py` | 46 |
| | `test_render_diff.py` | 21 |
| | `test_clause_join_sites.py` | 8 |
| | `test_dupe_sweep_structure.py` | 3 |

The suite's conftest modules carry a large share of the tests' weight:
`tests/install/conftest.py` 2,859 lines, `tests/render/conftest.py` 2,423, `tests/profiler/conftest.py`
2,163, `tests/dashboard/conftest.py` 149. The two large files hold test functions of their own (148 in
the install conftest, 116 in the render conftest), and the install one holds a function named exactly as
`tests/install/test_checkout.py:35` — `test_this_checkout_is_one_and_its_commit_state_reads`, a
duplicated name the collection does not reach.

## Lens one — shotgun versus deliberate

The question per family: can two of its cases fail differently? A deliberate family states a property
or oracle, each case a separate way the property can break; a shotgun family iterates an input space
and proves one trivial fact on every member.

The families, read from their param tables and case directories:

| Family | Cases | Verdict |
| --- | ---: | --- |
| `tests/dicing/test_dicer.py::test_cases` (the `data/` case trees) | 88 | **Deliberate.** Each case directory is a stated input with an `args`, an `exit`, a `names` and an expected tree: a directory case, a heading case, a collision, a dead link, a split level, an undice round trip. The oracle is the tree comparison; the failure modes are as many as the trees. |
| `tests/dicing/test_dicer.py::test_undice_then_dice_reproduces_the_tree` | 14 | **Deliberate.** A round-trip property over every case that dices and exits 0: the failure is a case the dicing does not invert, and each is a distinct tree shape. |
| `tests/dicing/test_planform.py` (17 tables) | 129 | **Deliberate at its core, sprawling at its rim.** The plan-form tables (`heading-matched-by-whole-id`, `state-word-and-note`, `headers-case-insensitive` …) each name a distinct refusal or acceptance; the formatter and layout tables that follow are narrower and read as one property each. |
| `tests/dicing/test_board.py` (23 tables) | 107 | **Mixed.** The plan-column, header and card tables are deliberate (one form per case); the later tables (`each-state-in-its-column`, `no-lifetime-or-rating-column`) are deliberate too, but a run of small two-case tables proves one fact each — a property per table, one or two counterexamples. |
| `tests/render/test_structural_rules.py` | 85 | **Mixed.** `test_definition_refusals` and `test_check_source_refuses_*` are deliberate — each case a source breaking one rule, the rule named in the id. `test_is_stdlib_tells_the_standard_library_from_everything_else` (7 cases) is a qualification table of the probe over the modules, deliberate. |
| `tests/test_guardrail.py` | 282 | **Deliberate, the suite's single largest property set.** One case table drives both implementations; each case is a shell command or tool call with its expected reason. A case fails on a guardrail's decision, and the two implementations are held together — the family's distinct failure modes are the table's rows, not an input-space sweep. |
| `tests/render/test_families.py` (12 tables) | 54 | **Deliberate.** Each table varies one render dimension (harness, category, overlay) with a distinct expected text; the failure is a render that drops or keeps the wrong paragraph for that dimension. |
| `tests/install/test_dry_run.py` (11 tables) | 60 | **Deliberate at its last tables, shotgun in its removal groups.** The listed/removed-path tables are distinct behavioural claims; a few tables over path shapes prove the same prediction for several inputs. |
| `tests/dashboard/test_server.py` (9 tables) | 86 | **Deliberate.** Route, status, body and header tables: each case a distinct serve decision. |
| `tests/render/test_render_refusals.py`, `test_settings.py`, `test_placeholders.py`, `test_frontmatter.py`, `test_prose.py` (6/6/7/3/4 tables) | 152 | **Deliberate.** One refusal or form per case, each naming the message or the hole it is about. |
| `tests/test_install_target.py` (7 tables) | 43 | **Mixed.** The refusal tables are deliberate; the harness-detection tables over flag spellings are a small shotgun — several spellings proving one selection rule. |
| `tests/install/test_selection.py`, `test_agents_file.py`, `test_global_agents.py`, `test_runner_file.py` (3/3/4/5 tables) | 75 | **Deliberate.** Each table one marker, mode or include line. |
| `tests/test_plugins.py` (6 tables) | 21 | **Deliberate.** Membership and reference cases, each a distinct selection outcome. |
| `tests/profiler/test_init.py` (3 tables) | 13 | **Deliberate.** Retired-launcher, skill-removal and store-rename cases. |
| `tests/dicing/test_textfile.py`, `test_outline.py`, `test_linkrewrite.py`, `test_reassemble.py`, `test_linkscan.py`, `test_anchors.py` (4/4/5/5/2/2 tables) | 183 | **Deliberate, the anchors narrow.** The text, outline, link and reassembly tables each state a distinct rewrite or split fact; `test_anchors.py`'s tables state distinct anchor rules too, and only a three-repeat count iterates a value one repeat would carry. |
| `devtools/tests/test_dupe_sweep.py` (4 tables) | 46 | **Deliberate.** Each table a distinct sweep candidate over a corpus. |
| `tests/test_cold_read_tools.py` (6 tables, `cold_read`) | 34 | **Deliberate.** Each case a CLI shape and its argument rendering; the cases are subprocess runs and the cost is the marker's. |

**The shotgun families, collapsed to the envelope of their distinct failure modes.** No family is
shotgun outright; the two nearest are narrow and each states distinct facts:

- `tests/dicing/test_anchors.py::test_github_anchor` (8 cases) reduces a title to its anchor. Read
  closely, the cases are distinct rules — spaces become hyphens, punctuation is deleted with spaces
  kept, underscores and hyphens survive, backticks go, a dot goes, non-ASCII letters lower, a
  non-ASCII digit survives, a link reduces to its text — not one rule iterated. Its envelope is the
  table's own claim, and nothing collapses.
- `tests/dicing/test_anchors.py::test_heading_anchor_list` (7 cases) proves one property over distinct
  heading shapes: a repeated anchor is suffix-numbered, a closing hash goes, a fence is not counted, a
  heading needs a space. Its failure modes are the shapes it varies; only the three-repeat count
  (`third-repeat`: one, two, three repeats) is an iterated value where one repeat would carry the rule.
- The path-shape tables of `tests/dicing/test_board.py` and `tests/install/test_dry_run.py` are the
  same border: each proves one property over two or three counterexamples — the property-plus-
  counterexample shape, not a sweep.

The one input-space iteration this survey reads as shotgun is `third-repeat` above, and collapsing it
to its envelope is a single case's worth, not a count worth moving. **The family count does not drop
as a side effect, because there is no shotgun family of size to drop**: the case tables are written as
claims with ids, and the ids are what makes them read as claims. A family that cannot fail differently
from its sibling would be a shotgun member wearing a deliberate id; this survey found none whose
collapse would be visible in the count.

## Lens two — tier balance

Each test classified by what it exercises, from its subject and its fixtures:

| Tier | Cases | Share |
| --- | ---: | ---: |
| **Unit / component** — one function or one module, fixtures or a tmp tree standing in for the world | 1,342 | 76% |
| **Contract** — an oracle that is another implementation or a stated interface, not this one's function | 361 | 20% |
| **Integration / end-to-end** — the install or the CLI driven over a real tree, a shipped script or a bun process | 63 | 4% |

The counts are the collected cases (1,766 of the 1,801; the 34 `cold_read` and 6 `slow` marker cases
count far more than their share of the integration set, so they are set aside here), each module placed
whole by the reading of its subject; the classification script the survey wrote for it is in
`.devpro-temp/`, a scratch probe rather than a shipped check. The
boundaries, since the labels are judgment:

- **Unit**: the renderer's tables (`tests/render/`, 282), the dicing model and its case trees
  (`tests/dicing/`, 605 — a case tree drives `_dicing` as a subprocess over the repo's own module,
  which is the verb, not `main`), the dashboard server and board panel (125), the install unit tables
  that call the install functions against a tmp project rather than through `main` (192), the profiler
  (58), the devtools sweep (78).
- **Contract**: `test_guardrail.py` (282) — two implementations held to one table; `test_plugins.py`
  (21, the definitions' membership against discovery); `test_clause_groups.py` (20) and
  `test_cross_references.py` (15) over the definition text; `test_kbase_surface.py` (8);
  `test_opencode_entry.py` (5, the TS entry under `bun` against a stub plugin context);
  `test_devpro_floor_check.py` (5); `test_stamp.py` (5, the TypeScript digest held to the Python one).
- **Integration**: `test_install_target.py` (43, the install verb through `main([...])`),
  `tests/install/test_checkout.py` (7, the real checkout's commit state among them), the dicing CLI
  surface (7) and citation targets (1), and `test_cold_read_tools.py` (5, the shipped script run as a
  consumer runs it; its other 34 cases are the `cold_read` marker's, set aside like the 6 `slow`).

**The reading.** The unit layer is 76% — near the eighty-percent line, under it. The reading
rule applies at its edge: the marginal unit tests are the prime suspects, and the set to read first is
the one the integration tier already holds:

| The unit case | What the integration tier already holds |
| --- | --- |
| `tests/install/test_staging.py` (15) — `package_copies`, `_wheel_files`, duplicate output | `check-wheel`'s wheel-vs-unpacked diff proves the built wheel's content; no test hands staging a real checkout tree, and no integration case drives `package_copies` over the checkout (S1). |
| `tests/install/test_dry_run.py`'s path tables (60) — `preflight._moves` and the removed group | The install's own `_install` runs over tmp projects exercise the replacement the dry run predicts; the dry run's report is the claim only its own cases hold, so most of the tables stand and the predictions duplicated by an install run are the marginal ones. |
| `tests/render/test_families.py` (54) — render text by harness, category, overlay | No integration render case: the rendered product is a gitignored build (`rendered/`), and `retake-reference` is a recipe, not a test. The families are the render's whole behavior, so they are load-bearing, not marginal. |
| `tests/dicing/test_board.py` (107) — the board model | `tests/dashboard/test_board_panel.py` serves the same model over `/api/*`; the unit tables whose claim the panel's cases already exercise end to end are the marginal ones. |
| `tests/profiler/test_page_data.py` (7), `test_served.py` (5) — page data and the served index | `tests/dashboard/test_server.py` serves the same pages at `/profiler/` and `/page/<session-id>`, over the files `devpro/profiler/pages.py` renders; the unit pair restates the served claim the dashboard tier already holds. |

Organic bloat or metric chasing: no coverage tool exists in the venv (`pytest-cov` is not installed), so
the suite is not coverage-driven — no threshold chases. The 76% is organic: a package that ships mostly
pure functions (the dicing model, the renderer, the board) earns unit tests by the house rule's own
account of where algorithmic behavior belongs. The bloat that is present is directory-shaped, not
metric-shaped: the dicing tier's 605 unit cases are the imported docdicer suite's whole behavior, and
their case trees are that package's own acceptance corpus. The tier the suite is thin in is the
integration one — 63 cases, 43 of them the install verb through `main` — and the thinnest seam is the
real-tree one S1 names.

## Lens three — gap by mechanism

A gap is never the finding by itself; each is named with the mechanism it needs.

| Gap | Mechanism the gap needs |
| --- | --- |
| No case hands `check-wheel` this repository's own tree (S1). | A test — the real-tree case the CONVENTIONS rule names: the recipe's own run is not the case. |
| The digest recognizer's spelling is held by nothing on the capture path (S2). | A unit assertion over `is_installed` with real and foreign banners, and a structural comparison of the TypeScript constants to the Python ones. |
| The module split's direction is held by no check (S3). | A structural check over the import graph: a direction assertion beside the acyclicity one. |
| The `profiler/__init__.py` stub means a package-level edge upward leaves no trace in the package graph. | Structural: the direction check reads module-to-module pairs, not package-to-package. |
| No test runs the install from a real checkout's tree as `package_copies` stages it, over a tree holding a stray (S1). | Integration: the install over the checkout's own `devpro/`, with a planted stray, asserting what it stages. |
| `tests/install/conftest.py` holds a duplicate test name the collection never reaches. | None — a deletion, not a mechanism. |

## The reorganization inventory's health

The ROADMAP ticket's deliverable was a reorganization item for the accumulated test monoliths —
`tests/test_devpro_profiler.py`-scale files — collecting tests by subject and splitting along the
package's seams, the layout `tests/dashboard/` and `tests/dicing/` model. **The split is landed**: there
is no `tests/test_devpro_profiler.py`, and `tests/`'s root holds only the repository-wide checks, the
renderer's crossing checks and the shared fixtures; the profiler, dashboard and dicing suites sit under
their seams, as the B14 layout's `install/`, `profiler/`, `render/`, `dashboard/` and `dicing/`.

Where the seams' case mass sits:

| Seam | Cases | Largest file |
| --- | ---: | --- |
| `tests/dicing/` | 615 | `test_planform.py` (129) |
| `tests/` root | 399 | `test_guardrail.py` (282) |
| `tests/render/` | 282 | `test_structural_rules.py` (85) |
| `tests/install/` | 199 | `test_dry_run.py` (60) |
| `tests/dashboard/` | 125 | `test_server.py` (86) |
| `devtools/tests/` | 78 | `test_dupe_sweep.py` (46) |
| `tests/profiler/` | 63 | `test_capture.py` (16) |

The layout's health, read against the deliverable's terms:

- **One file still interleaves subjects.** `tests/profiler/test_runners.py` measures nothing of the
  runners its name and docstring name — the bun contract, serialize, digest, mask and stamp runners
  moved out from under it — and its one test is the `REVIEW_SEAT` pin over the development
  definition's `post-plan reviewers` term. It belongs with the definition-clause pins
  (`tests/test_clause_groups.py`, `tests/render/test_families.py`'s definition-text tables), not under
  the profiler seam.
- **One seam is a stub.** `tests/profiler/test_stores.py` holds one store-reader test
  (`test_the_readers_read_a_copy_of_a_store_as_no_store_at_all`) for the profiler's two store readers,
  and its docstring still names the subject it was written for (`list_sessions• read_sessions•
  copy-as-no-store`). The rest of the profiler's store behavior is read through `test_served.py`'s
  served index and `test_tree.py`'s renders, which exercise the readers without pinning them.
- **The largest file is not the largest seam's.** `tests/render/test_structural_rules.py` (85) is a
  single seam's structural checker, and its bulk is one property set over the package — deliberate
  under lens one, not a monolith.
- **Two conftest files are the layout's real monoliths**: `tests/install/conftest.py` (2,859 lines, 148
  tests) and `tests/render/conftest.py` (2,423 lines, 116 tests). They hold test functions beside the
  fixtures, and the duplication below sits in the first.

The duplicate: `test_this_checkout_is_one_and_its_commit_state_reads` is defined twice, at
`tests/install/conftest.py:307` and `tests/install/test_checkout.py:35`; only the second is collected.
The organization the deliverable wanted is the layout's; what is left is one misfiled test and one
uncollected duplicate.

## S1 — the real-tree case check-wheel lacks

**The rule** ([A repository-wide check runs a real-tree
case](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-repository-wide-check-runs-a-real-tree-case.md)):
a repository-wide check's own case set includes one run over the real tree it polices; the recipe's own
run explicitly does not count.

**Command, run:** `git grep -n "check-wheel" tests/` — exit 1, no output. No test names, invokes or
hands anything to `check-wheel`; the check's cases are its recipe's run alone (`just test wheel`,
`devtools/scripts/check-wheel.sh`) and nothing else. The rule's own sentence applies: "its fixture
cases say only what the fixtures hold", and here there are no cases at all.

**The tree check-wheel reads.** `sed -n '44,52p' devtools/scripts/check-wheel.sh` states the comparison's
tree side:

```bash
in_tree="$(git -C "${PROJECT_ROOT}" ls-files --cached --others --exclude-standard "${GEN}" \
  | awk '!/\.py$/' | sort)"
```

That is the index plus untracked-but-not-ignored files. The install's staging side is the filesystem:
`devpro/install.py:235` `_wheel_files(root)` walks `root.rglob("*")` and drops `__pycache__`
directories, and `package_copies` (`devpro/install.py:243`) stages from `PACKAGE_ROOT / package.source`
— the running package's own directory as it stands.

**Probe, run.** A probe tree cloned from `devpro/` in two shapes, then a scratch script calling
`install.package_copies` over each (`.devpro-temp/p3-s1-probe.py`, in the survey's scratch directory):

| Shape | Files staged |
| --- | ---: |
| `plain` — the tree as a checkout holds it, `__pycache__` removed | 111 |
| `stray` — the same plus `devpro/__pycache__/zz_probe_module.cpython-311.pyc` and `devpro/zz_probe_stray.txt` | 112; staged files: `['zz_probe_stray.txt']` |

The staged stray landed at `<install>/tools/devpro/devpro/zz_probe_stray.txt`. The `__pycache__` file
is dropped by `_wheel_files`, as its docstring says; the plain stray is not. Meanwhile
`git ls-files --cached --others --exclude-standard devpro | awk '!/\.py$/'` lists 15 files, none under
`__pycache__` and none named `zz_probe_stray`.

**The gitignored-stray probe the plan asks for.** A file planted with `touch` where `.gitignore`
covers it answers differently, and the answer is the interest:

- A file under `devpro/__pycache__/` is gitignored (`.gitignore:3:__pycache__/` matches it), so neither
  `git status --short` nor `git ls-files --cached --others --exclude-standard` lists it; `_wheel_files`
  drops it from staging. The two sides agree, by `_wheel_files`'s rule rather than the index's.
- Any other stray under `devpro/` (a scratch log, an editor swap file, a downloaded artifact) is
  *untracked, not ignored*: `git check-ignore` exits 1 for it and `git ls-files --cached --others
  --exclude-standard devpro` lists it as an untracked file — so the tree side counts it, fails
  `in_tree` against the wheel, and the stray cannot reach a passing check. That half of the plan's
  probe does not bite.
- The filesystem and the index therefore disagree in exactly one way for this repository's own ignore
  rules: on paths `.gitignore` covers, the filesystem tree (which `package_copies` walks when install
  runs from a checkout, and only then) holds files the index never sees, and `_wheel_files`'s
  `__pycache__` exclusion is the one rule that keeps the two sides agreeing. `install.py`'s docstring
  already names that gap in its own words: bytecode is left out because "a pip-compiled install of the
  wheel holds some the wheel itself does not"; a `.pyc` for a *running* interpreter is bytecode the
  wheel never carries.

The full `just check-wheel` at the survey's open ran green (`exit=0`, last line
`check-wheel: Python 3.11.18, …devpro-0.18.0-py3-none-any.whl`), with no stray in the working tree:
the tree side and the wheel agreed over the 15 tracked/untracked data files. The real-tree case is
the test the rule wants — one that hands `check-wheel` this checkout and fails where a stray under
`devpro/` reaches a passing wheel — and it does not exist.

**The finding is the rule's two halves:** (a) the case set lacks its real-tree case outright — no test
hands `check-wheel` anything; and (b) the tree the wheel comparison reads is the index's, while the tree
the checkout install stages from is the filesystem's, so the two sides are compared over different
inputs wherever the two disagree. The one disagreement this repository's own ignore rules produce is
under `__pycache__`, and `_wheel_files` closes that one by its own rule, not the index's. A `.gitignore`
line covering any other path under `devpro/` opens the same gap with nothing closing it. The recipe's
own run is not the case the rule means in either half.

## S2 — the digest test's literal-banner plants

**The plants.** `grep -rn "GENERATED! from devpro\|INSTALLED! from devpro" tests/profiler/` answers 21
files' lines: 18 plants across four modules, plus three `__pycache__` matches a directory walk also
reports (bytecode, not source). The source plants:

| Site | Plant |
| --- | --- |
| `tests/profiler/conftest.py:235, 348, 433, 469, 501` | `<!-- !GENERATED! from devpro/definitions/agents/coder.py -->\nbody\n` |
| `tests/profiler/conftest.py:1151, 1158, 1160` | `# !GENERATED! from devpro/{a,b,c}.py\n` |
| `tests/profiler/conftest.py:1154` | `#!/bin/sh\n# !INSTALLED! from devpro/x.sh — devpro\n` |
| `tests/profiler/test_stamp.py:49, 56, 58` | the same three `GENERATED` plants |
| `tests/profiler/test_stamp.py:52` | the same `INSTALLED` plant |
| `tests/profiler/test_capture.py:40, 153, 238, 274, 306` | the comment-form `GENERATED` plant |

`sed -n '430,442p' devpro/harnesses/resources/opencode/profiler.ts` states the TypeScript side's
literal constants: `const GENERATED_BANNER = "!GENERATED! from "`, `const INSTALLED_BANNER =
/!INSTALLED! .* devpro/`, and `OWNERSHIP_MARKERS = ["no readable script at", '"name": "', '"command":
"', '"plugin":']`.

**What the plants pin.** They are the fixture project a run digests; the test's oracle is the other
capture — `tests/profiler/test_stamp.py::test_the_two_captures_digest_one_project_state_alike` asserts
`ported["stamp"] == stamp` and `ported["manifest"] == manifest`, and a witness manifest of expected
paths. The plants are the test's *input*, not its subject; the subject is the TS/Python agreement over
one tree. The literal `!GENERATED! from` matches both recognizers' constants — `install_base.GENERATED_MARK`
imported by `devpro/profiler/directives.py` and the TS's own `GENERATED_BANNER` — so the plants cannot
distinguish a capture that reads the renderer's spelling from one that carries its own copy of the
string.

**The rule the digest's case is then held by.** The kept second paragraph of
[Recognizer spells rendered banner](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/recognizer-spells-rendered-banner.md)
already says it: "The digest test plants literal banners, so it pins the two captures' agreement and
not the renderer's spelling." So the plants are not a defect in the test — the test states what it
pins. What the rule does not name, and the survey adds, is the consequence: **nothing in the suite holds
the digest's spelling to the renderer's, on either side.** A grep of `tests/` for `GENERATED_MARK`,
`GENERATED_BANNER` or `INSTALLED_BANNER` finds no assertion over the constants. The
`test_the_ownership_markers_agree_with_the_harnesses_that_write_them` case holds the *marker list* to
the harnesses and to the TS list; no such case holds the *banner spelling* to `render.generated_text`
and `install.stamped`.

**Probe, run** (a scratch script calling `devpro.profiler.directives.is_installed` over three files,
`.devpro-temp/p3-s2-origin.py` in the survey's scratch directory, since cleared):

| File | `is_installed` |
| --- | --- |
| `# !GENERATED! from devpro/a.py\nbody\n` (the plant's shape) | `True` |
| `# !GENERATED! from devpro/definitions/agents/coder.py — rendered by devpro\nbody\n` (the renderer's shape) | `True` |
| `# !GENERATED! from another-tool/b.py\nbody\n` (another tool's file) | `True` |

The third row is the tell: the recognizer accepts a foreign tool's banner, and the constant it reads is
right — the recognizer spells what the rule says it spells. What answers to nothing on the capture path
is that the *renderer writes the same string*: `devpro/render.py:89` `generated_text` and
`install_base.GENERATED_MARK` are one pair, and the TS constant is a second spelling of it that no test
compares. The plants are the test's subject in the sense that they *are* the fixture; they are not the
subject whose spelling the test could catch.

**The finding:** the digest's case is held by the rule's second paragraph, deliberately, and the
plants are its input — the defect is not the plants but the missing pin they leave behind: the two
captures' spellings are held to each other over a planted tree and to nothing that writes a banner. The
`test_the_ownership_markers_agree…` pattern (`ported["markers"] == list(HARNESS_OWNERSHIP_MARKERS)`,
and the Python list held to the harnesses' markers) is the shape a banner-spelling pin would take. It
does not exist: the three constants `GENERATED_BANNER`, `INSTALLED_BANNER` and `GENERATED_MARK` are
asserted nowhere in `tests/`.

## S3 — the module-split rule's upward-edge half

**The rule** ([A module split runs one
way](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-module-split-runs-one-way.md)): a lower
module never imports the upper one it was split from; a function-level import from the upper is not
the way back. The worked instance is `devpro/profiler/read.py`.

**The check.** `sed -n '1,30p' tests/render/test_package_invariants.py` is one test,
`test_the_import_graph_is_acyclic` (lines 8–26): it builds the module graph and `visit`s it, failing on
a revisit of a node in the trail. It holds acyclicity and nothing of the rule's direction — a lower
module importing its upper one where the upper imports nothing back is acyclic, and passes.

The named splits: `git grep -n "split" PROJECT_DOCS/ARCHITECTURE/repo-layout.md` answers one line, and it
is the devtools file's own clause (`clause_join_sites.py … splits units with render_diff.py's line
classification`, line 28) — no split is named there. The splits the rule's claimants state are in
`repo-layout.md`'s direction paragraph — `kanban/` imports `doccheck/` and `dicing/`, `doccheck/`
imports `dicing/`, `profiler/` reads `kanban/`'s stylesheet as package data, `dashboard/` imports the
panels it serves, "and none of them depends on a module that depends on it" — and the one the rule file
itself names, `pages.py` → `read.py` (the read boundary split from the page render).

**The scan, run** (an import-direction scan over `devpro/` written for this survey, and a clone
sensitivity run; the script is `.devpro-temp/p3-s3-mutual.py` in the survey's scratch directory):

| Tree | `profiler/read.py` imports | Mutual pairs in `profiler/` (direct or reach) | Package pairs both ways |
| --- | --- | --- | --- |
| `devpro/` (real) | `['devpro.profiler.values']` | none | none |
| clone with `read.py` importing `pages.py` (the rule's forbidden instance) | `['devpro.profiler.pages', 'devpro.profiler.values']` | `devpro.profiler.pages <-> devpro.profiler.read` | none |

The package direction the scan reads from the real tree — `dashboard → kanban, profiler`, `kanban →
dicing, doccheck`, `doccheck → dicing` — is exactly `repo-layout.md`'s paragraph, and no pair runs both
ways. The sensitivity clone is not decoration: the scan is proved to catch the edge the rule forbids,
because a scan that reports "no upward edge" over a tree holding one would prove nothing. The package
graph the scan reads has no package pair running both ways either, which is the second half of
`repo-layout.md`'s sentence ("none of them depends on a module that depends on it").

**Why the naive scan misses the split.** An edge "upward" judged by the containing package's own imports
reads the package's `__init__.py`, and `devpro/profiler/__init__.py` is a stub holding `pass` — as are
`devpro/`, `devpro/dashboard/`, `devpro/dicing/`, `devpro/doccheck/`, `devpro/kanban/`,
`devpro/definitions/{__init__,agents,skills}` and `devpro/families/`. A scan built on package imports
therefore reports zero upward edges even when `read.py` imports `pages.py` (the first scan written for
this survey did exactly that). The rule's own statement does not reach the package boundary either: "the
lower module's own imports name only modules at or below it" — `read.py`'s import of `pages.py`, the very
split it names, is an edge to the module that imports it, and the rule's sentence does not say so.

**The finding:** the split's direction is held by no check — the only import-graph test pins
acyclicity, which the forbidden edge passes — and today no lower module holds an upward edge in the
profiler split or between packages, so the rule is honoured by the code and unheld by the suite. Two
sub-answers the survey adds: the package graph cannot carry the check because every seam's
`__init__.py` is a stub, so the check reads module-to-module pairs (the mutual-pair shape above); and
the rule's own text, read as written, does not cover the worked instance, so a checker built on its
sentence would check a different thing from the one it names.

## The judgments

Each: the defect, the seat that saw it (one of the ROADMAP ticket's three lenses, the S-item's own door,
or the reorganization deliverable), and the fix's shape — never the fix.

| # | Defect | Seat | Fix's shape |
| --- | --- | --- | --- |
| J1 | No test hands `check-wheel` this repository's tree: the real-tree case the rule names does not exist, and the recipe's own run is not it. | **S1** (run-born) | A test in `tests/install/` that runs `check-wheel` (its script, or the comparison it makes) over the checkout's own `devpro/` and fails where a stray reaches a passing wheel. |
| J2 | The wheel's tree side reads the index (`git ls-files --cached --others --exclude-standard`) while a checkout install stages from the filesystem (`package_copies` → `_wheel_files`), so the two sides are compared over different inputs where `.gitignore` covers a path under `devpro/`. | **S1** (run-born) | A decision, then a mechanism: the real-tree case (J1) answers it for the checkout path; alternatively `package_copies` stages from the build's filtered set, not a directory walk. The shape is stated, the choice is the architect's. |
| J3 | The digest recognizer's spelling is held to nothing that writes a banner: the plants are the fixture, the two captures are held to each other, and no case holds `GENERATED_MARK`/`INSTALLED_BANNER` to `render.generated_text`/`install.stamped` or to the TS constants. | **S2** (run-born) | A unit assertion over `is_installed` with the renderer's banner and a foreign one; a structural comparison of the TS constants to the Python ones, in the shape `test_the_ownership_markers_agree…` already uses. |
| J4 | The module-split rule's direction half is unheld: `test_the_import_graph_is_acyclic` pins acyclicity only. | **S3** (run-born) | A direction assertion beside the acyclicity one, over module-to-module pairs (not package imports: every seam's `__init__.py` is a stub). |
| J5 | The rule's own text does not cover its worked instance: "only modules at or below it" does not name an import of the module that imports it, and nothing names a seam's stub `__init__.py` as the reason the check must read pairs. | **S3** (run-born) | The CONVENTIONS leaf's sentence states the pair relation (a lower module never imports a module that imports it), and the check (J4) is built on that sentence. |
| J6 | `tests/profiler/test_runners.py` is misfiled: it measures none of the runners it names, and its one test pins the `REVIEW_SEAT` against the development definition's term. | **Reorganization deliverable** | Move the test to the definition-clause seam (`tests/test_clause_groups.py` or `tests/render/`), and rename the module for its subject. |
| J7 | `test_the_review_seat_is_the_definition_sets_post_plan_reviewer` holds two homes together by importing one: `devpro.profiler.read.REVIEW_SEAT` and the development definition's `POST_PLAN_REVIEWERS_TERM`. | **Tier balance (seams)** | A decision on which seam owns the constant and its pin; the test follows the owner. |
| J8 | `test_this_checkout_is_one_and_its_commit_state_reads` is defined twice, at `tests/install/conftest.py:307` and `tests/install/test_checkout.py:35`; only the second is collected. | **Reorganization deliverable** | Delete the uncollected copy; the collected one stands. |
| J9 | `tests/install/conftest.py` (2,859 lines, 148 tests) and `tests/render/conftest.py` (2,423, 116) hold test functions beside fixtures — the seam's tests split across two files, one named for fixtures. | **Reorganization deliverable** | Tests out of the conftest, into the seam's `test_*.py` files; the conftest keeps fixtures. |
| J10 | `tests/dicing/test_anchors.py::test_heading_anchor_list`'s `third-repeat` case iterates a repeat count where one repeat carries the suffix rule. | **Lens one (shotgun)** | Drop the two-repeat and three-repeat lines from that one case; its distinct heading shapes stand. |
| J11 | The marginal unit set duplicates what a richer tier holds: the page-data and served-index units against the dashboard's own serve cases, and the board model's tables against the board panel's integration cases. | **Lens two (tier balance)** | Merge the duplicated units into the case that already holds them; retain the units that pin a claim the integration tier does not. |
| J12 | The integration tier holds 4% of the suite, and its thin seam is the one the install actually meets a consumer at — the checkout's staging and the wheel check. | **Lens three (gap by mechanism)** | Integration instruments: the real-tree case (J1), one staging case over the checkout's own tree, the CLI driven over a tmp project (which `test_install_target.py` already is). |
