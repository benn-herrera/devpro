# Post-plan review — the dicer mini plan

Packages reviewed: P1 (H1 re-base), P2 (rehome + dice), P3 (round-trip repairs), P4/P4b (two-pattern
model, map retirement, re-integration), P5 (the three trees re-diced). Seats: `devpro-python-coder`
(tool), `devpro-architect` (structure and claims), `devpro-prompt-engineer` (trees as documents).
Findings are de-duplicated; every entry names every seat that reported it.

## Critical

- **R1** (architect; prompt-engineer). The P5 restructure's mechanical cut deleted
  `dicing-and-checks/index.md`'s shared-behaviors preamble — the usage-error definition, Streams,
  Current directory, Text, and the `--split-level` contract (values 2/3/4, default 4, usage-error).
  Seven SPEC leaves still cite `[shared behaviors]`; every refusal table depends on the deleted
  usage-error definition; the code (`dicing/cli.py:24-33`) still honors the split-level contract it
  is now the only statement of. Fix: restore the preamble's content to the index (source:
  `git show f08a3d7^:PROJECT_DOCS/SPEC/dicing-and-checks/index.md`), then re-dice.
- **R2** (prompt-engineer). Opposite rules recorded: `dicing/check-tree.md:19-23` and
  `the-diced-tree/the-model.md:13-18` classify SPEC's top-level directories as sections vs volumes.
  Two prior cycles hit the same collision; `dc358a6` decided it in a sentence and recorded it
  nowhere. Fix: one rule in `the-diced-tree/`, one reference from `check-tree.md`.
- **R3** (architect). The volume/section classification lives twice:
  `treecheck._misplaced_head` reads all prose links of the root head; `dicedoc._volume_documents`
  reads only the Contents block. One stray prose link flips `check-tree`'s classification of a valid
  tree. Fix: one classifier, one home; the other reads it.
- **R4** (python-coder, Critical). `write_tree`'s unrebased report names `s.first` (the section's own
  heading line) rather than the heading that overflows, and gates the section on one `unrebased` id —
  a second defective heading in the same section is never named (`split.py:52-63, 81-88`). Fix: report
  the offending heading, list all offenders.
- **R5** (prompt-engineer, Critical). 62 links cite the volume's H1 (`index.md#dicing-and-checks`)
  instead of the leaf holding the text, and 28 target `../reassembly.md` for verbs that got their own
  leaves; `check-links` cannot see either class — the anchor exists on the wrong leaf. Fix: retarget
  by the mapped site classes (`.devpro-temp/p5-spec-links.py`); consider an anchor-placement check.

## Warnings

- **R6** (python-coder). `_placed_level` can return a level above 6 for a deep tree
  (`a/b/c/d/e/f.md` → 7), and the unit test asserts the impossible value. Fix: clamp to the
  model's shallowest-level rule and correct the test.
- **R7** (python-coder). `check_reassembly` runs on files `write_tree` has already declared
  unrebased — the check should treat a declared-unrebased section as verified-by-refusal, not
  compare it. Fix: skip or special-case them.
- **R8** (prompt-engineer; architect). The split's moved referents: `limits.md` opens as a fragment;
  `kanban/index.md` absorbed the board's only orientation text and `(Start, above)` now crosses
  files; a dangling `(below:` in `check-design.md:9`; `[link checks](reassembly.md)` and
  `[dice](dice.md)` name the wrong leaf after the split. Fix: retarget each reference to the leaf
  that now holds its text.
- **R9** (architect; prompt-engineer). The cross-document link rule (`Tree.documents`,
  `linkrewrite.py:199-204`/`_document_linked`) is real in code and unstated in SPEC, while
  `link-rewriting.md`'s link-target rule 3 ("reach the same file") contradicts it. Fix: state the
  rule in `the-diced-tree/` or `link-rewriting.md`, and amend rule 3.
- **R10** (architect). Dead `add` closure (`dicedoc.py:261-268`), its logic duplicated twice more —
  obviated code is deleted, not parked (CONVENTIONS). Fix: delete, single home.
- **R11** (architect). A title-less volume document writes `- [](b/entry-point.md)` and exits 0,
  against `limits.md`'s refuse-don't-accommodate rule. Fix: refuse with a named fault.
- **R12** (architect). `treecheck._misplaced_head` scans prose-wide; with R3's single classifier this
  collapses. Folded into R3's fix.
- **R13** (python-coder). `_top_is_rebased` has no corpus case holding a level-1 heading inside a
  section — the discriminator's only proof is a vanished scratch copy. Fix: one corpus case.
- **R14** (python-coder). A one-document tree with root-level leaves has no corpus case and
  `check_tree` does not accept it — a SPEC statement is needed (is it a tree?) and then a case.
- **R15** (python-coder). `_fits` and any level-5/6 heading are untested. Fix: two corpus cases.
- **R16** (python-coder; architect). Stale SPEC wording: `dice.md`'s undice section still promises
  the deleted split-level "raise", contradicting `_placed_level`/`_restored`; `reassembly.md`'s
  best-effort entry names a map that no longer exists. Fix: restate to the landed behavior.
- **R17** (prompt-engineer). `check-tree.md` restates the two-pattern model and has already drifted
  from it (folds into R2's single-home fix).

## Notes

- **R18** (python-coder). `_fits` restates `_shift`'s arithmetic; `_volumes` hand-builds head paths
  `heads.py` owns; `Volume.document_dir` is dead after P4b; `_top_is_rebased` is private with
  cross-module readers; two duplicate-coverage tests; a stale module docstring.
- **R19** (prompt-engineer). Harness-profiler trailing periods: all three carriers agree; no action.
- **R20** (prompt-engineer). Both splits (dice/undice, the reassembly eight) are clean textually.
- **R21** (architect). The model is stated once in code and once in SPEC and they agree; the
  manifest/links.tsv/`--map` retirement left no residues; undice's self-check messages match SPEC
  word for word. Strengths, recorded.
- **R22** (python-coder). `outline._HEADING` vs `anchors._ATX_HEADING` — two heading recognisers,
  predates this plan; a unification candidate.
- **R23** (python-coder). Stale `manifest.pyc` in the tree; a clean rebuild removes it.

## Contract gaps carried from the run's reports

- **G1** (P1's report): a format change that narrows the expressible set must name the inputs that
  no longer fit, and the tool must refuse them by name — proposed for CONVENTIONS
  (planning-and-execution).
- **G2** (P1's report): stale bytecode can mask a source edit; a probe must import through
  `PYTHONPATH=. .venv/bin/python` or re-probe in a fresh process.
- **G3** (P5's report; owner-ruled): a section directory's name must equal its heading's slug — the
  tool enforces it, `check-tree` alone does not; belongs in the docdicer skill's tree conventions.
- **G4** (P4b's report): where two commits' halves share a call graph such that either alone leaves
  the gate red, the split is a Blocker naming the shared definitions — proposed for the coder
  definition's Parallel Execution section.
- **G5** (B2's report): a verification entry lists the artifacts the run produced, by path; where a
  page's check needs a row the default view does not reach, the brief states the query that reaches
  it.
- **G6** (P4's report; PE F9): `dicedoc.verify` is the per-tree check whose `leaves:` line the
  re-dice reads — confirm it survived the map retirement, else re-home P5's counting method.

## Non-findings recorded

- Owner-directed non-fixes from the main plan stand (R9/R14 of the main review; the opencode
  hand-offs). The prompt-engineer seat's review confirms: 412 links, 0 broken; Contents complete in
  all three trees; every leaf's H1 slugs to its file name.
