# ACTIVE PLAN

# The install replaces the plugin directory wholesale, then the test-suite survey

The active design ([ACTIVE_DESIGN.md](ACTIVE_DESIGN.md)) lands in two tickets, in this order: the
strip — the install's fully-owned wipe semantics (ROADMAP Maintenance, "The install's fully-owned
wipe semantics") — then the test-suite survey (ROADMAP Maintenance, "The periodic review's panel
gains the test-suite audit seat"). The strip's outcomes: an install — project or user-level —
replaces the plugin directory wholesale, so what a harness loads is exactly what the release ships;
the shared files outside the directory keep their handling; the re-entry pass-over and its
symlinked-copy refusal are preserved exactly. The survey's outcome: a findings document over the
remaining suite, feeding this plan's burndown — fixes, never the survey itself.

## Status

| Package | State | Rating |
| --- | --- | --- |
| P1 | landed | mechanical |
| P2 | landed | expert |
| P3 | landed | expert |
| P4 | landed | expert |
| P5 | drafted | expert |
| B19 | drafted | expert |
| B20 | drafted | mechanical |
| B21 | drafted | expert |
| B22 | drafted | expert |
| B23 | drafted | expert |
| B24 | drafted | expert |
| B25 | drafted | expert |
| B26 | drafted | expert |

## Ticket 1 — the strip

**Serial order.** P1 before P2 — the documents state the wipe the code implements, and P2's test
revisions read the applied leaves; the design-delta check turns green at P1's end and stays green
through P2. P2 before ticket 2 — the survey inventories the tests the strip leaves, on a quiescent
repository.

**Boundaries that hold across the packages.** The re-entry pass-over — the copy's own files under
`tools/devpro/` and the wrapper `tools/devpro.sh` stand, the symlinked-copy refusal intact — is
preserved exactly ([Renders and copies](ACTIVE_DESIGN.md#renders-and-copies), [Shipped
files](ACTIVE_DESIGN.md#shipped-files)); `devpro/agents_file.py` is unchanged and the hook entries
`profiler init` writes into a settings file are unchanged ([Write
Safety](ACTIVE_DESIGN.md#write-safety)); the THESIS Pieces-table row is applied in P1, the
CONVENTIONS recognizer leaf's first paragraph retires in P2.

### P1 — the deltas and the THESIS row applied

Intended lifetime: shipped. Rating: mechanical.

Scope: the design's delta leaves, each receiving its entry verbatim apart from relative links —
`PROJECT_DOCS/SPEC/write-safety.md` (five pairs), `PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md`,
`PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md`, `PROJECT_DOCS/SPEC/generated-files.md`
(two pairs), `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md` (four pairs),
`PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md` — [the SPEC
entries](ACTIVE_DESIGN.md#write-safety); `PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md`
(eight pairs), `PROJECT_DOCS/ARCHITECTURE/install/index.md`,
`PROJECT_DOCS/ARCHITECTURE/install/install-entry.md` (three pairs),
`PROJECT_DOCS/ARCHITECTURE/install/guardrail-registration.md` (two pairs),
`PROJECT_DOCS/ARCHITECTURE/install/plugins.md` (two pairs),
`PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md`, `PROJECT_DOCS/ARCHITECTURE/banner.md`,
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/what-removes-the-retired-path.md`,
`PROJECT_DOCS/ARCHITECTURE/packaging.md`, `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md` — [the
ARCHITECTURE entries](ACTIVE_DESIGN.md#renders-and-copies). Thirty-five pairs in all. The same
package applies the THESIS Pieces-table row the design's Drafts item quotes as a pair ([the Drafts
item](ACTIVE_DESIGN.md#the-thesis-pieces-tables-install-row-names-the-wholesale-replacement)) to
`PROJECT_DOCS/entry-point.md`.

Fact (run): `just dev-check-design` answers `entries: 19, problems: 0`; `just
dev-check-design-deltas-applied` answers `pairs: 35, drifted: 0, conflicting: 0` — every from-text
matches its target as the design stands.

In-scope tests: none — document only. Done-line: `just check-links`,
`just dev-check-design-deltas-applied` — re-run at this package's end, answering `pairs: 35,
landed: 35, pending: 0, problems: 0`, exit 0.

### P2 — the strip: the wipe's mechanism and the tests that pin it

Intended lifetime: shipped. Rating: expert.

Scope: `devpro/install.py` (the replacement step, the symlinked-install-directory refusal, the
banner readers' removal, the retirement inventory's removal, the report's shape, the version read
before the replacement), `devpro/runner_file.py` (`retired_set` and its handling gone),
`devpro/preflight.py` and `install._install_managed_paths` (the install directory managed whole, the
bases outside it keeping their paths), `devpro/harnesses/resources/opencode/index.ts` (the
user-level-guardrail comment corrected) — the [Install machinery
entry](ACTIVE_DESIGN.md#install-machinery) states what keeps, what drops and what adds, and the
write-pass rule its opening paragraph states: the replacement writes what the install ships and
nothing else, membership by `ships(name)` at the install's level, resources by the harness's list at
that level, the guardrail script by the probe. Kept, and named so no executor "fixes" it:
`_report_shadowing` and `_is_our_harness_file` — the shadow report's marker reader, the one banner
reader that survives. Comments citing the prune step or a retirement list reword to the replacement:
`devpro/install_target.py:89` and `devpro/definitions/__init__.py:70`.

The CONVENTIONS edits land here, with the code they follow: the first paragraph of
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/recognizer-spells-rendered-banner.md` retires
with the recognizer it describes, its digest paragraph standing; and in
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/harness-resources-are-copied-verbatim.md`'s
first paragraph, the sentence "That installed banner is required (SPEC.md, Write Safety), and the
source test enforces it for every file a harness ships." is replaced — the banner is shipped text
the source test still enforces, required by nothing — the paragraph's stamping-loop and
master-tree rules standing.

Reference search (run): `git grep -n "RETIRED_SNIPPET_SET\|retired_set" -- devpro tests devtools`
answers `devpro/install.py:158,770`, `devpro/runner_file.py:161,163,170,174,175,179,228,243,270,272,282`,
and `tests/install/conftest.py:35,1462,1591,1595,1609,1626,1638`,
`tests/install/test_runner_file.py:13,199,243,260,272`,
`tests/install/test_scratch.py:12,125,129` — every referencing file is in this package's scope.
Reference search (run): `git grep -ln "from devpro.install import" -- devpro tests` answers
`devpro/cli.py`, `tests/install/{conftest,test_checkout,test_dry_run,test_kbase,test_prune,test_runner_file,test_scratch,test_staging}.py`,
`tests/render/conftest.py` and `tests/render/test_families.py` (both `INSTALL_SETTINGS`),
`tests/test_devpro_floor_check.py` (`wrapper_text`), `tests/test_guardrail.py`
(`HARNESS_RESOURCES_SOURCE`) — the last four import symbols that survive; they are in scope to
verify, not to change.

The tests the strip's behavior changes, all in scope: `tests/install/test_prune.py` removed whole;
the refusal battery, retirement tests and guardrail-skip pair in `tests/install/test_dry_run.py`;
`tests/install/test_kbase.py`'s operator-manifest refusal; `tests/install/test_staging.py`'s
second-install prune test; `tests/install/test_runner_file.py`'s four retired-docdicer tests;
`tests/install/test_scratch.py`'s user-level entry-and-no-guardrail test;
`tests/install/conftest.py`'s fixture and collected-test rewordings. A test failing on behavior this
package does not state it changes is reported as a finding, never edited to pass.

The dry run's removal groups after the wipe: the removed group keeps its two forms — files, and
directories with the trailing `/` — so the wipe's subdirectory removals are named both ways, and a
store rename still reads as one path removed and one path created (`preflight._moves` keeping that
work), so `test_a_dry_run_lists_a_renamed_profiler_store_as_a_path_removed_and_a_path_created`
(`tests/install/test_dry_run.py:769`) stands unchanged.

The tests this package adds, each naming the defect it fails on:

- a foreign file inside the install directory is removed and named in the dry run's removed group —
  fails on a foreign file surviving a changing install, or a dry run that misses its removal;
- a symlinked install directory is refused, nothing written — fails on the wipe clearing and
  writing through a link into the directory it names;
- a symlinked file inside the install directory is removed, not followed — fails on the wipe
  following a link out of the install directory;
- a stale `.pyc` under `tools/devpro/` is absent after a re-entry run whose copy files are
  byte-identical — fails on the pass-over preserving junk or rewriting the copy;
- a failed probe into a tree holding an earlier install's `guardrail.pl` leaves none after the run —
  fails on a skipped probe leaving an unregistered script standing;
- a second run over a fresh tree reports up to date and changes no byte or mode — fails on the
  replacement's rewrite touching a byte or mode the first run left, the up-to-date report saying
  nothing written while the tree changed;
- the mage agents file inside the install directory survives with its block current — fails when
  the wipe deletes the file the agents-file mechanism edits, the block written against an emptied
  file and the operator's own content gone with it;
- two successive user-level opencode installs leave `index.ts` and `guardrail.ts` as this release
  ships them and the plugin's setup reaches the watcher — fails when the wipe deletes a plugin file
  the user-level run does not rewrite, the second run's setup then missing the guardrail, or the
  entry left absent and the plugin not registering.

Cited, not edited: `README.md:100-109` and `README.md:216-224` state the dicing-snippets removal and
the docdicer include-line removal this strip makes inert — `devpro-tech-writer`'s, through the
post-plan review. In-scope fixtures: `tests/install/conftest.py`. Done-line: `just test devpro`,
`just test wheel`, `just lint`.

## Ticket 2 — the test-suite survey

### P3 — the test-suite survey runs and writes its findings

Intended lifetime: shipped. Rating: expert.

Scope: `ACTIVE_TEST_SURVEY.md` — one artifact, created here, deleted in the commit that lands this
plan. Its content: the inventory of the collected suite as the strip leaves it (`tests/` and
`devtools/tests/`), the baseline run recorded inside it, the S1–S3 dispositions each with its
command and its answer, the three lenses' verdicts and the reorganization inventory — the lenses,
the eighty-percent reading rule and the reorganization deliverable are the ROADMAP ticket's own text
(Maintenance, "The periodic review's panel gains the test-suite audit seat"), cited there and
applied here, not restated. Its findings are drafted into this plan's burndown by P5 alongside the
post-plan review's; work it locates beyond this plan's scope lands as ROADMAP tickets. The survey
runs the suite's own runner targets and adds no test. Done-line: `just check-links`.

The three run-born findings fold in as the inventory opens, each a fact to verify with commands, not
a conclusion; the survey states which half of each is the finding:

- **S1 — the real-tree case check-wheel lacks.** The rule
  (`PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-repository-wide-check-runs-a-real-tree-case.md`)
  requires a repository-wide check's own case set to include one run over the real tree it polices,
  the recipe's own run explicitly not counting. Verify: `git grep -n "check-wheel" tests/` — does
  any test hand check-wheel the repository? And the tree the wheel comparison reads is `git
  ls-files`'s (index plus untracked), not the filesystem tree a checkout install stages from
  (`install._wheel_files`): `sed -n '44,52p' devtools/scripts/check-wheel.sh`. Probe: a gitignored
  file planted under `devpro/`, then `just check-wheel` and a `PYTHONPATH=.` install into a scratch
  project — pass and stage, or not.
- **S2 — the digest test's literal-banner plants.** The digest recognizer's fixtures plant literal
  `!GENERATED!`/`!INSTALLED!` banners and literal ownership markers — locate them with
  `grep -rn "GENERATED! from devpro\|INSTALLED! from devpro" tests/profiler/` (the plants stand at
  `tests/profiler/conftest.py:235-501` and `1151-1160`, `tests/profiler/test_stamp.py:49`), and the
  TS side's literal banner constants the byte-equality fixture holds to the Python side:
  `sed -n '430,442p' devpro/harnesses/resources/opencode/profiler.ts`. The finding is that the
  plants pin the two captures' agreement, not the renderer's spelling — the statement
  `recognizer-spells-rendered-banner.md`'s second paragraph (which P2 keeps) already makes; the
  survey states what rule the digest's case is then held by, and whether the plants are the test's
  subject.
- **S3 — the module-split rule's upward-edge half.**
  `PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-module-split-runs-one-way.md` states a
  split's lower module never imports the upper one it was split from. Verify whether the check that
  holds the import graph holds the rule's direction or only acyclicity:
  `sed -n '1,30p' tests/render/test_package_invariants.py`; and whether any lower module holds an
  upward edge today: an import-direction scan over `devpro/` (the survey writes the scan), the
  named splits enumerated from `git grep -n "split" PROJECT_DOCS/ARCHITECTURE/repo-layout.md`.

## P4 — Post-plan review

Intended lifetime: shipped. Rating: expert.

The post-plan reviewers are given the project documents and the design, not the plan, and review
the changes and their tests against the project's standards and fitness for purpose: the Python
coder (`install.py`, `runner_file.py`, `preflight.py` and the install suite), the TypeScript coder
(`index.ts`), `devpro-architect` (the structure and the applied leaves), and
`devpro-prompt-engineer` (the project documents' claims about the code). Each writes their own
review in the scratch directory, independently — the reviewer's done-line observation: each seat's
report file present in `.devpro-temp/`, its entries grouped by root cause; the session synthesizes
them into `ACTIVE_PLAN_REVIEW.md` — one entry per defect, naming every seat that reported it —
de-duplicating without waiting for an approval between the last report and the write-up. This
package's row lands in the commit that adds the review document; `just dev-check-plan` is the
row-update check that commit's status edit runs, not a check of the review document, which carries
no machine check. A user-flow audit joins the review where the user asks for one; none is asked.

Done-line: the four seats' report files are in `.devpro-temp/`, each grouped; `ACTIVE_PLAN_REVIEW.md`
exists, committed, its entries naming their seats.

## Post-plan burndown

The items below are drafted from `ACTIVE_PLAN_REVIEW.md` — the four seats' findings — with the
test-suite survey's judgments (`ACTIVE_TEST_SURVEY.md`) drafted alongside them, grouped by root
cause. The strip's residue items (B19–B24) close the seams the strip opened; the survey's small
fixes (B25) and the deferred structural judgments close the survey's. Each closes in one commit.

### B19 — the strip's SPEC and rendered-definition reconciliation

Intended lifetime: shipped. Rating: expert. Fixes H1, H2, W3, W4, W5, W6 (the leaves' half), C3.

Scope: `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md` (:170-171 the false user-level
sentence; :100-106 the two-vs-three resource count; :108-110 the banner guarantee restated as the
shipped-as-is fact), `plugins.md` (:50-51 the user-level "alone" completed; :69-71 the matrix-wide
runner-line rule and the "inert" qualification; :84-91 the mage hazard — a file the operator keeps
inside the harness directory outside `devpro/` is removed by the next install), `write-safety.md`
(:20-31 the symlink-unlinked clause added to the consumer outcome; :8-11 the user-level product
list cut to the wipe half citing Install destination; the stores-and-backup pointer clause),
`devpro/definitions/skills/guide.py:116-117` — the false "no guardrail" sentence replaced with the
guardrail-resource truth. Facts: the contradictions are quoted in `ACTIVE_PLAN_REVIEW.md` H1–H3,
W3–W6; re-run `grep -n` on each span before editing. The mage `--subdir` dry-run case (N4) is
probed during this item and its outcome recorded in the item's report.

In-scope tests: the rendered-definition structural tests (`tests/render/`) over guide.py. Done-
line: `just check-links`, `just test`, `just lint`.

### B20 — the strip's ARCHITECTURE and CONVENTIONS residue

Intended lifetime: shipped. Rating: mechanical. Fixes W9, W10, W11, W12, W13, and the document
halves of N1.

Scope, each fix enumerated in `ACTIVE_PLAN_REVIEW.md`: `ARCHITECTURE/install/renders-and-copies.md`
(:104-108 the four negatives; :110-116 the stale line citations; :125-128 the managed-set
enumeration; :126-127 the four-field `checked_agents_file` shape), `install/plugins.md:62-65`
(the retired docdicer set's recognition membership), `install/guardrail-hook.md:18-19` (the
foreign/refused reason for a deleted judgment), `install/guardrail-registration.md:8-9`
(implementation detail and rationale cut), `install/index.md:3-5` (the fourth writer named) and
`:11-14` (the rationale clause), `install-entry.md:42-44` ("the replacement runs after them"),
`CONVENTIONS/code-definitions-and-install/recognizer-spells-rendered-banner.md` (cut to the digest
duty, rename to "Digest pins the two captures' agreement", `entry-point.md` and `index.md`
following), `untracked-output-is-not-source.md:6-7` (the whole-tree reason). In-scope tests: none
— document only. Done-line: `just check-links`.

### B21 — README owns the record decision and the stale upgrade prose

Intended lifetime: shipped. Rating: expert. Fixes W6 (README's half), and the tech-writer findings
the review names.

Scope: `README.md` (:100-104 and :216-224 the piecewise docdicer-removal claims replaced with the
wipe's outcome — the retired home and earlier files go with the tree, the include line stays until
the operator deletes it; :229-234 the `.venv`-survival paragraph cut — the directory is gone under
the wipe; :83-95 the gitignore instruction given its reason; the missing paragraph after :113 —
the install replaces the directory whole, `--dry-run` lists what would go, a file you need lives
outside). Recommended wording is in `.devpro-temp/p4-pe.md` §11. Done-line: `just check-links`.

### B22 — the preserved pairs' failing tests

Intended lifetime: shipped. Rating: expert. Fixes C2, H4, W14, and the version-direction lost pin.

Scope: `tests/install/`. Three tests the design named that cannot fail, plus one seam: (1) the
mage agents-file pass-over — a changing second mage install over a `CLAUDE.md` holding operator
text and an earlier block, asserting text and `backup.CLAUDE.md` survive and the path is absent
from the dry run's removed group (must fail with `pass_over` minus the agents path); (2) the
re-entry pass-over — the copy's row staged populated plus a stale `.pyc`, asserting the files
survive and the `.pyc` does not (must fail on the empty-row staging it replaces); (3) the
version-direction report — an older and a newer `__version__` written into `tools/devpro/__init__.py`,
the report naming both directions. The `_differs` seam (a special-file pass-over path) is probed
by (1): if the plain case passes, the seam is invisible and recorded as such. Each carries its
defect in the house docstring form. Facts and spans are quoted in `ACTIVE_PLAN_REVIEW.md` C2, H4,
W14 and the conformance seat's report. Done-line: `just test`, `just lint`.

### B23 — the re-entry integrity guard

Intended lifetime: shipped. Rating: expert. Fixes W1.

Scope: `devpro/install.py` (`_re_entry_kept`'s caller, before the replacement). On a re-entry run,
refuse — the same `InputError` shape the other refusals use — when the running copy lacks a
relative path `_wheel_files` over `PACKAGE_ROOT` produces, naming the path: the replacement would
remove what the pass-over cannot restore. Test: a copy with a planted-missing shipped path fails
the install naming it. Done-line: `just test`, `just lint`.

### B24 — the dry-run both-groups defect

Intended lifetime: shipped. Rating: expert. Fixes W2, and the architect's N4 trailing-slash note.

Scope: `devpro/preflight.py` (the comparison — a directory the run also makes is not a removal, a
file the run also wrote is not removed), `devpro/install.py:717-723` (`_every_entry_below`'s
docstring stating a pruning the walk does not do — reworded or the walk pruned), `_shown`'s
trailing-slash-from-disk note. Test: a `_assert_dry_run_predicts` case over a non-empty install
directory — the existing case at `conftest.py:2036` runs the real install, not the dry run.
Done-line: `just test`, `just lint`.

### B25 — the watcher observation drive

Intended lifetime: shipped. Rating: expert. Fixes C1.

Scope: the behavioral observation the design's Drafts item records as unsettled — what a wipe does
to a live opencode session whose entry watches the install directory (`index.ts:251`): run an
install under a live session, record what the watcher does (the events, the refresh, the session's
state after), and write the answer where it belongs — the measured fact into the survey's
successor record and a SPEC caveat if the outcome is one an operator must know. The observation's
method is recorded in `.devpro-temp/` before it runs. No code change is in scope; a code change
the observation makes necessary is a finding for the next plan. Done-line: `just check-links`
(the recorded outcome lands in a leaf).

### B26 — the survey's small fixes and the deferred rest

Intended lifetime: shipped. Rating: expert. Fixes J1, J2, J3, J6, J8, J10 of
`ACTIVE_TEST_SURVEY.md`; J4, J5 are the CONVENTIONS clauses B20/B22 carry; J7, J9, J11, J12 and
the three contract-gap proposals defer to `ROADMAP.md` (the Maintenance ticket this plan's
 ROADMAP ticket names), where `check-roadmap` holds their form.

Scope: `tests/install/` — J1 the real-tree case for `check-wheel` (the CONVENTIONS rule's case:
the test hands the check the repository the index names; the gitignored-stray gap the survey
proved is the `__pycache__` shape `_wheel_files` closes — the test pins that); J6 `test_runners.py`
re-homed to the seam it serves; J8 the uncollected duplicate test in `conftest.py:1361` removed;
J10 the repeat-count case read against its tier; J2 the index-vs-filesystem statement placed in
the leaf J1's rule names; J3 the banner-spelling pin following `profiler_digest_runner.ts`'s
rewrite-the-source pattern where the survey locates it. Each fix's TEST_PRECONDITION-style defect
statement rides the test it adds or changes. Done-line: `just test`, `just lint`, `just
check-links`.

### P5 — Post-plan burndown

Intended lifetime: shipped. Rating: expert.

The items above are drafted from `ACTIVE_PLAN_REVIEW.md` and `ACTIVE_TEST_SURVEY.md`; their rows
move through the states as the items dispatch and land, and the plan lands once the last item's
row is `landed`.
