# Plan — the dicer writes leaves as documents: a diced leaf's top heading is an H1

No design stands behind this plan: the requirements are the rulings below, stated in Facts, and the
work goes straight to the plan. Every work package below is **shipped**, and each closes in one
commit. The packages run serially, in ID order: P2's re-dice of ARCHITECTURE would resurrect the
file P2's rehome removes, and P3 regenerates the trees the re-dice standardizes.

## Facts the packages rely on

- The dicer is `devpro/dicing/`; its tests are `tests/dicing/`. Check: `ls devpro/dicing/*.py | wc -l`
  → 14; `ls tests/dicing/*.py | wc -l` → 17. The write pass is `devpro/dicing/split.py:write_tree`;
  the line that copies a section's text verbatim is
  `body.append(lines[k] if fenced[k] else linker.forward(lines[k], leaf_dir, next_line))`
  (`split.py:35`) — the defect: a leaf's top heading keeps the level it was split at. Check:
  `git grep -n 'body.append' devpro/dicing/split.py`.
- The reassembly check is `devpro/dicing/reassemble.py:check_reassembly`; on a difference it prints
  `reassemble: first difference at monolith line <k> (<path>)` (`reassemble.py:56`; the compare loop
  is `:47-59`). Check: `git grep -n 'first difference at monolith line' devpro/dicing/reassemble.py`.
- `Section` (`devpro/dicing/outline.py`) carries `level`; `kind` is `"E"` the entry point, `"I"` a
  section index, `"L"` a leaf. Check: `git grep -n 'kind: str' devpro/dicing/outline.py`.
- A leaf's file name derives from the heading text alone: `outline.section_name` strips the number,
  slugs the title, and takes no level — `write_tree`'s shift changes a line's `#` run, not its text,
  so no leaf is renamed and no path moves. Check:
  `git grep -n 'def section_name' devpro/dicing/outline.py`.
- A section's leaf contains no split-level heading other than its own top (`outline.py:106`): a
  diced tree carries no absolute heading levels, and many monoliths dice to the same tree. The
  contract is that a diced tree dices back to the same tree (`SPEC/dicing-and-checks.md`,
  Reversible), not byte-exact `undice(dice(m)) == m`.
- Anchors are text-based and level-independent: the anchor is the heading's plain text
  (`devpro/dicing/anchors.py`), so re-basing a ladder cannot move one, and two same-text headings
  disambiguate by `-N` in document order as before. The sixteen promoted run-in titles are distinct:
  `grep '^\*\*' PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md | sort | uniq -d` → empty.
  Check: `git grep -n 'def heading_anchor' devpro/dicing/anchors.py`.
- The ruled write form: a non-entry-point section's heading ladder is re-based so its top heading
  writes at level 1 and every heading inside shifts by the same delta (`Section.level - 1`), fenced
  lines excepted. Check: none — the requirement, stated by the owner's ruling; P1 states it.
- Reassembly (and undice's reconstruction) restores a leaf's ladder before the compare. Check:
  none — requirement.
- The three standing trees were diced under the old behavior; their leaves open at `##` or deeper —
  25 at `##`, 65 at `###`, none deeper — and no level-5 or level-6 heading stands anywhere in the
  three trees, so the re-base's interior shift has no instances in real content; the corpus carries
  that coverage. Check: `git grep -n '^#####\|^######' PROJECT_DOCS/SPEC PROJECT_DOCS/ARCHITECTURE
  PROJECT_DOCS/CONVENTIONS` → nothing.
- `harness-profiler.md`: `wc -l` → 308; it opens at `### Harness profiler`; 16 bold run-ins, all
  titles, **all sixteen ending with a terminal period**, all distinct; the intro paragraph is the
  section's own text above the first run-in. The file carries no links, no `§`-references and no
  fences — the only `](\|#`-shaped hit is line 1's heading — so a direct dice has no link form to
  restore and `dangling: 0` is structural; a promoted-heading dice needs no link map (a 1-intro +
  3-run-in reproduction dices `dangling: 0`), and the map branch is taken only where the real run
  reports `dangling`.
- The reference inventory for the rehome: five lines carry six occurrences of the title parenthetical
  `(Install, Harness profiler)` — `repo-layout.md:15` twice, `:16`, `:22`, `subsystem-map.md:80`,
  `install/opencode-entry.md:46` once each; two link sites: `install/index.md:29` and
  `ARCHITECTURE/entry-point.md:20` (`git grep -n 'harness-profiler\.md' PROJECT_DOCS` finds exactly
  those two). After the edits, `git grep -n 'Install, Harness profiler' PROJECT_DOCS` prints
  nothing.
- The runner targets: `just dice-doc monolith out [map]`, `just undice tree monolith`;
  `--split-level` defaults to 4 (`outline.py:15`, `DEEPEST_SPLIT_LEVEL = 4`); `dice-doc` refuses a
  non-empty out-dir. The checkpoint gate is `just test`, then `just sweep-python` (CONVENTIONS,
  *The gates*).

## Status

| Package | State | Rating | Agent | Scope |
| --- | --- | --- | --- | --- |
| P1 | in progress | expert | `devpro:python-coder` | the dicer writes every section's heading ladder re-based to an H1 top; reassembly and undice restore it |
| P2 | dispatchable | expert | `devpro:python-coder` | the harness profiler rehomed to its own area and diced with the fixed tool |
| P3 | drafted | expert | `devpro:python-coder` | the three standing trees re-diced under the new behavior |
| P4 | drafted | expert | session | Post-plan review of what shipped, to `ACTIVE_PLAN_REVIEW.md` |
| B0 | drafted | expert | session | Post-plan burndown drafting |

## P1 — the dicer writes every section's heading ladder re-based to an H1 top

**Scope.** `devpro/dicing/split.py` (`write_tree`); `devpro/dicing/reassemble.py`
(`check_reassembly`); `devpro/dicing/dicedoc.py` (`_restored`, `_undiced_lines`); the dicing test
corpus `tests/dicing/data/` and the tests that pin the written form — `test_split.py`,
`test_reassemble.py`, `test_dicer.py`, `test_undice.py`, `test_treecheck.py`; and the three contract
wording sites the change amends — `PROJECT_DOCS/SPEC/dicing/tree.md` (§File content),
`PROJECT_DOCS/SPEC/dicing/checks.md` (§Reassembly), `PROJECT_DOCS/SPEC/dicing/verbs.md` (§undice).
`devpro/dicing/heads.py` and `outline.py` are out of scope; a change that needs one is reported as a
finding, not made.

**Verification boundary.** This package's verification lives entirely in `tests/dicing/` and the
scratch demonstration: no document under `PROJECT_DOCS/` is read as evidence of the code change. The
package does carry the contract wording it amends — the three SPEC sites in scope — edited in the
same commit, never cited as evidence.

**Guidance.**

1. In `write_tree` (`split.py:26`), a section written to its file carries its heading ladder
   re-based. Using the `fenced` list the function already builds (`split.py:29`, from
   `textfile.fence_flags`): line `s.first - 1` — the section's top heading — rewrites to `#` (this
   is its shift), and every **other** line in `body` that `fence_flags` marks *not* fenced and that
   `outline._HEADING` matches (`outline.py:11`, `r"#+ "`, matched at column 0) shifts by
   `s.level - 1`, the shift editing only the leading `#` run, title text and number unchanged. A
   line inside a fence is copied as it stands: `check_reassembly` compares fenced lines verbatim
   (`reassemble.py:47-59`), so a shifted fenced line is a reassembly failure. Kinds `"I"` and `"L"`;
   `"E"` is written as it stands. The heading pattern is `outline._HEADING`'s (`outline.py:11`);
   import it, do not copy or restate it in `split.py`. If it should carry a shared exported name,
   that is a finding: `outline.py` is out of scope and the rename is not made here.
2. In `check_reassembly`, before the line-for-line compare, a leaf whose top heading reads level 1
   — the new write form, kinds `"I"` and `"L"`; the entry point's own level is 1 and its delta is 0
   — has its non-fenced heading lines shifted down by `s.level - 1` for the section `s` being
   compared, the shift editing only the leading `#` run, fenced lines compared as they stand; a leaf
   whose top reads any other level is the pre-change form and compares as it stands, which is
   today's behavior. The pre-change form never presents a level-1 top: `plan_sections` plans no
   level-1 section (`outline.py:70-75`). The check then reproduces the monolith exactly for either
   form. No shifted line lands below level 1: an internal heading is never shallower than its
   section's top (`plan_sections`'s parent rule, `outline.py:80-86`), so the clamp guards a case the
   planner excludes.
3. The reconstruction (`dicedoc._restored`) restores each part's heading ladder before the text is
   planned and written. A part whose top heading reads level 1 — the new write form — shifts its
   non-fenced heading lines (`outline._HEADING`, fenced lines excepted) so the section sits at the
   shallowest level its position in the tree permits: the part path's directory count + 1, raised
   where an internal heading would otherwise land at a split level — the self-check reports such a
   collision, and a tree that cannot be placed is reported, not guessed. A part whose top reads any
   other level is the pre-change form and passes through as it stands — today's behavior,
   unchanged. The tree does not carry the absolute level a re-based section came from, so the
   restored document is *the document the tree holds*, not necessarily the document last diced; the
   contract is the round trip (`SPEC/dicing/verbs.md`, undice Round trip; `SPEC/dicing-and-checks.md`,
   Reversible).
4. Tests, each per `clauses.TEST_PRECONDITION` naming the defect (a leaf whose top heading reads
   `##`/`###` is a fragment, not a document). Pinned by the corpus, not by assertions in the `.py`
   files: `test_dicer.py` compares `expected/tree/` whole; a corpus case whose `expected/tree/`
   holds an old-level top heading is updated in scope — fixtures this change rewrites are listed in
   the commit body by case name. The cases: every leaf and index top at `#` with internals
   distributed below; dice → undice → dice reproduces the tree byte for byte (the undice round
   trip); a tree in the pre-change form — leaf tops at their sections' own levels, a hand-authored
   fixture — undices with `reassemble ok`; an `####`-topped section's ladder is a single heading;
   and the tree's file names are unchanged by the shift — leaf paths are those `section_name`
   derives from the heading text. A test failing on something beyond this change is a finding, never
   edited to pass.
5. Scratch demonstration under `.devpro-temp/`: dice a sample monolith, show the leaf tops at `#`,
   undice it back, and run the round-trip check.

**Done-line.** `just test-changed`, then `just lint`. The done-line runs once, after the last edit;
before the commit, the checkpoint gate runs once: `just test`, then `just sweep-python`.

## P2 — the harness profiler rehomed to its own area and diced

**Scope.** `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` (heading promotion, then diced
into `PROJECT_DOCS/ARCHITECTURE/harness-profiler/`); `PROJECT_DOCS/ARCHITECTURE/install/index.md`;
`PROJECT_DOCS/ARCHITECTURE/entry-point.md`; `PROJECT_DOCS/ARCHITECTURE/repo-layout.md`;
`PROJECT_DOCS/ARCHITECTURE/subsystem-map.md`; `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md`.

**Guidance.**

1. Promote the file's sixteen bold run-in titles to `####` headings, wording unchanged: the run-in's
   bold text becomes the heading, the sentence's remainder stays the paragraph's opening text; a
   title keeps its terminal period — heading text is not re-punctuated (all sixteen carry one). The
   intro paragraph above the first run-in stays under the `### Harness profiler` heading.
2. Dice to `.devpro-temp/harness-profiler-fresh/`. If the run reports `dangling:` on stderr, write
   the link map from those numbers and dice again into a second empty directory with the map; the
   mapped run is the one moved. Then place the area: `git rm` the old
   `install/harness-profiler.md`; move `index.md` and the section files of the fresh dice into
   `PROJECT_DOCS/ARCHITECTURE/harness-profiler/`. The fresh dice's `entry-point.md` is the
   sub-dice's tree-root head and is **not** moved: a directory that is not a tree root opens at
   `index.md` (`heads.py:directory_head`), as `install/` and `rendering/` do today. After the move,
   `harness-profiler/index.md` opens `# Harness profiler` with the intro paragraph (`head -3` shows
   it).
3. Rewrite the citations: `install/index.md`'s member link is removed (the install area's list
   shrinks) and any install-area prose that pointed below at the profiler is checked;
   `ARCHITECTURE/entry-point.md`'s line — the install leaf's link — becomes the area entry
   `harness-profiler/`; the title parentheticals — six occurrences on five lines,
   `repo-layout.md:15` twice, `:16`, `:22`, `subsystem-map.md:80`, `install/opencode-entry.md:46` —
   change `(Install, Harness profiler)` to `(Harness profiler)`, the area they name having changed.
   The two link sites are rewritten by these edits.
4. Check: `just check-links` over `PROJECT_DOCS` with `problems: 0`; `check-tree` over the new
   tree; and `git grep -n 'Install, Harness profiler' PROJECT_DOCS` prints nothing.

**Done-line.** `just test-changed`, then `just lint`, then `just dev-check-links`. The checkpoint
gate runs once before the commit, as P1 states.

## P3 — the three standing trees re-diced under the new behavior

**Scope.** `PROJECT_DOCS/SPEC/`, `PROJECT_DOCS/ARCHITECTURE/`, `PROJECT_DOCS/CONVENTIONS/`
(regenerated whole); the monoliths are work products under `.devpro-temp/`.

**Guidance.**

1. Per tree: `just undice <tree-dir> .devpro-temp/<name>-undiced.md` (it refuses an existing
   target), then `just dice-doc .devpro-temp/<name>-undiced.md .devpro-temp/<name>-fresh/`. Undice
   and dice at the default split level 4, the level the trees were diced at. Take `reassemble ok`
   from the undice and `reassemble ok` plus `dead: 0` from the dice as the preconditions of step 2;
   a difference reported by either is a finding for P1, not something P3 patches. This is also the
   first end-to-end exercise of P1's form-conditional shift on a tree P1 did not write.
2. Replace, don't merge: `git rm -r <tree-dir>`, then
   `mv .devpro-temp/<name>-fresh <tree-dir>`. The fresh tree is the whole of the directory
   afterwards; a file the old tree held and the fresh tree does not is gone.
3. After all three replacements: `just check-links` with `problems: 0`, and
   `just dev-check-links`. The commit body names each tree re-diced and its leaf count — the count
   comes from a per-tree `devpro check-links <tree-dir>` run, its `documents checked:` line less
   that tree's `index.md` and `entry-point.md` heads, the method stated in the commit body. The
   counts are taken after P2, which changes ARCHITECTURE's inventory; no pre-measured baseline
   belongs in this plan.

P3 runs after P2 and not before: the ARCHITECTURE re-dice regenerates the tree from its undiced
monolith, and run first it would write `install/harness-profiler.md` back, undoing P2's `git rm`.

**Done-line.** `just test-changed`, then `just lint`, then `just dev-check-links`. The checkpoint
gate runs once before the commit, as P1 states.

## P4 — Post-plan review

**Lifetime.** The review package lands nothing but `ACTIVE_PLAN_REVIEW.md`; its row is `landed` in
the commit that adds the file.

The post-plan reviewers review what P1–P3 shipped, and get the project documents, not this plan:

- `devpro:python-coder`, for the dicing tool and its tests;
- `devpro:architect`, for the structure and the documents' claims about the tool;
- `devpro:prompt-engineer`, for the re-diced trees as documents.

Each writes a review under `.devpro-temp/`. The session synthesizes them into
`ACTIVE_PLAN_REVIEW.md`. The row is `landed` in the commit that adds that file.

**Done-line.** `just dev-check-links` passes over the tree holding `ACTIVE_PLAN_REVIEW.md`.

## Post-plan burndown

The items the post-plan review's findings group into, one work package per root cause.

### B0 Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
