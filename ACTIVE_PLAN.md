# Plan — the dicer writes leaves as documents: a diced leaf's top heading is an H1

No design stands behind this plan: the requirements are the rulings below, stated in Facts, and the
work goes straight to the plan. Every work package below is **shipped**, and each closes in one
commit. The packages run serially, in ID order: the repair (P3) precedes the model change (P4),
because P4 restates the head convention P3 has just corrected and both edits touch `heads.py`; the
model change precedes the re-dice (P5), because the re-dice writes the trees in the model P4 settles;
and none of P4's own tests reads a document, so P4 does not wait on P3's SPEC residue to be repaired.

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
- A root-head area is a first-class folder beside its siblings: a project document tree's root area
  (`SPEC/`, `CONVENTIONS/`, `ARCHITECTURE/`), and `directory_head`'s `tree_root` marks that area and
  no other. A directory inside the tree is not one, however the tree was built: it opens at
  `index.md` (`heads.py`'s docstring carries the convention; P3 establishes it in the trees).
  Check: none — the owner's ruling; P3 states it.
- The runner targets: `just dice-doc monolith out [map]`, `just undice tree monolith`;
  `--split-level` defaults to 4 (`outline.py:15`, `DEEPEST_SPLIT_LEVEL = 4`); `dice-doc` refuses a
  non-empty out-dir. The checkpoint gate is `just test`, then `just sweep-python` (CONVENTIONS,
  *The gates*).

## Status

| Package | State | Rating | Agent | Scope |
| --- | --- | --- | --- | --- |
| P1 | landed | expert | `devpro:python-coder` | the dicer writes every section's heading ladder re-based to an H1 top; reassembly and undice restore it |
| P2 | landed | expert | `devpro:python-coder` | the harness profiler rehomed to its own area and diced with the fixed tool |
| P3 | landed | expert | `devpro:prompt-engineer` | CONVENTIONS and ARCHITECTURE round-trip, the head convention corrected; SPEC's residue re-homed to P4 (the tool defect) and P5 (re-dice under the settled model) |
| P4 | landed | expert | `devpro:python-coder` | the dicer's two patterns: volumes and broken-out sections; the manifest retires |
| P4b | landed | expert | `devpro:python-coder` | the reconstruction's stragglers, the re-integration links, and the links.tsv cache retires |
| P5 | landed | expert | `devpro:python-coder` | the three standing trees re-diced under the settled model |
| P6 | landed | expert | session | Post-plan review of what shipped, to `ACTIVE_PLAN_REVIEW.md` |
| B0 | landed | expert | session | Post-plan burndown drafting |
| B1 | dispatchable | expert | `devpro:prompt-engineer` | restore the dicing-and-checks index preamble and the `--split-level` contract |
| B2 | dispatchable | expert | `devpro:prompt-engineer` | the anchor retarget class: every link lands on the leaf whose text it names |
| B3 | dispatchable | expert | `devpro:python-coder` | the tool: one classifier, honest faults, no dead code |
| B4 | dispatchable | expert | `devpro:architect` | single-home the model rules, and the corpus's missing shapes — first act: R2's decision |
| B5 | dispatchable | expert | `devpro:prompt-engineer` | the contract gaps the run named |

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

1. Two promotions, wording unchanged in each. The file's own `### Harness profiler` title becomes
   `# Harness profiler`, and the intro paragraph stays under it. The sixteen bold run-in titles
   become `####` headings: the run-in's bold text becomes the heading, the sentence's remainder
   stays the paragraph's opening text; a title keeps its terminal period — heading text is not
   re-punctuated (all sixteen carry one).
2. Dice to `.devpro-temp/harness-profiler-fresh/`. If the run reports `dangling:` on stderr, write
   the link map from those numbers and dice again into a second empty directory with the map; the
   mapped run is the one moved. The fresh tree is the area whole, and it is one level: its
   `entry-point.md` — the tree root's head, holding the `# Harness profiler` title and the intro
   paragraph — and its sixteen section files (one `.md` per promoted run-in, no subdirectory, no
   `index.md`) move to `PROJECT_DOCS/ARCHITECTURE/harness-profiler/`, `entry-point.md` at the area
   root (a tree root's head; roots alone carry one, `heads.py:directory_head`), and `git rm` removes
   the old `install/harness-profiler.md`. `PROJECT_DOCS/ARCHITECTURE/harness-profiler/` must not
   exist before the move (a `mv` into an existing directory nests the tree one level deeper); where
   a partial move left it, `git rm -r` it and move again. After the move,
   `ls ARCHITECTURE/harness-profiler | wc -l` is 17 and `head -3
   ARCHITECTURE/harness-profiler/entry-point.md` shows the title, the intro's first line and its
   third. This step's head-name sentence stated the pre-P3 convention; P3 established the
   nested-area head (`index.md`) and P4's model confirms it — P2's landed tree is the authority
   here, not this step's wording.
3. Rewrite the citations: `install/index.md`'s member link at :29 is removed (the install area's
   list shrinks by one line); `ARCHITECTURE/entry-point.md`'s line at :20 — the install leaf's
   link — becomes the area entry `harness-profiler/entry-point.md`; the title parentheticals — six
   occurrences on five lines, `repo-layout.md:15` twice, `:16`, `:22`, `subsystem-map.md:80`,
   `install/opencode-entry.md:46` — change `(Install, Harness profiler)` to `(Harness profiler)`,
   the area they name having changed. Those are the complete set: after the edits
   `grep -rn 'harness-profiler\.md' PROJECT_DOCS` prints nothing.
4. Check: `just check-links` over `PROJECT_DOCS` with `problems: 0` — the recipe is `check-links`
   then `check-tree PROJECT_DOCS` (`justfile:180-183`), so this is the check that the moved area is
   every one of its own documents' parent's link, and is reachable from the volume's entry point;
   `PYTHONPATH=. python3 -m devpro check-tree PROJECT_DOCS/ARCHITECTURE/harness-profiler` with
   `problems: 0`; and `git grep -n 'Install, Harness profiler' PROJECT_DOCS` prints nothing.

**Done-line.** `just test-changed`, then `just lint`, then `just dev-check-links`. The checkpoint
gate runs once before the commit, as P1 states.

## P3 — the standing trees round-trip: repair what undice exposes

**State.** CONVENTIONS (`reassemble ok: 558 lines`, `dead: 0`), ARCHITECTURE (`reassemble ok: 1694
lines`, `dead: 0`) and the head convention are repaired and committed. This package is not landed:
the SPEC tree still fails undice, and its remedy is a code defect no document fix reaches — report,
not make. When that defect is repaired, SPEC's repair as Guidance step 2 directs, its entry point's
line 29 corrected at the same time, is the one commit that lands this package.

Agent `devpro:prompt-engineer` (writer mode; the `devpro-docdicer` skill's conventions govern every
repair).

**Scope.** `PROJECT_DOCS/SPEC/entry-point.md`, `PROJECT_DOCS/SPEC/dicing-and-checks.md`,
`PROJECT_DOCS/SPEC/dicing/`; `PROJECT_DOCS/CONVENTIONS/entry-point.md` and the two CONVENTIONS
leaves whose headings disagree with their file names;
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/` (its head file) and
`PROJECT_DOCS/ARCHITECTURE/entry-point.md` (the area entry line); and `devpro/dicing/heads.py`'s
module docstring, whose stale volume-head sentence the repairs contradict.

**Facts.**

- The round-trip failures, run 2026-11-25, logs `.devpro-temp/p3-spec-undice.log`,
  `.devpro-temp/p3-conventions-undice.log`, `.devpro-temp/p3-architecture-undice.log`:
  `just undice PROJECT_DOCS/SPEC .devpro-temp/spec-undiced.md` exits 1 with `reassemble: cannot read
  PROJECT_DOCS/SPEC/shared-behaviors.md`; CONVENTIONS exits 1 with `cannot read
  .../a-sentence-two-harness-resources-carry-is-one-text.md`; ARCHITECTURE exits 1 with `cannot read
  PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`.
- SPEC declares its dicing volume twice: `SPEC/entry-point.md:31` links `dicing/index.md`, and
  `SPEC/dicing-and-checks.md` — a leaf — carries a Contents block repeating the same `dicing/*`
  leaves; undice plans `dicing/index.md` as a section, which collides, and reports strays.
- CONVENTIONS: `entry-point.md:41` links `a-sentence-two-resources-carry-is-one-text.md` under the
  title "A sentence two harness resources carry is one text", and `entry-point.md:53` links
  `a-delta-application-ends-by-searching-the-doc-set.md` under "A delta application is followed by a
  search of the doc set" — each link text names a title the leaf's own heading does not carry, the
  heading–file-name disagreement. And two leaves stand in `planning-and-execution/` with no
  entry-point line: `evidence-commands-run-before-they-ship.md`,
  `source-line-width-is-not-enforced.md`.
- ARCHITECTURE: the failure traces to the area's head — `harness-profiler/entry-point.md` is a
  tree-root head inside a volume. `heads.py:directory_head` is the convention and is not
  configurable: ENTRY_POINT where tree_root, INDEX otherwise — ARCHITECTURE's nested volumes
  (`install/`, `rendering/`) and SPEC's (`dicing/`) open at `index.md`.
- SPEC's second defect, found by P3's run and confirmed in `dicedoc.py`: a volume must stand on its
  own root. `_undiced_lines` reads exactly the entry point and its first Contents block, so
  `dicing/index.md` is read as a section — and its child, the H1 top, lands at level 1, which
  `plan_sections` reads as the tree's title: `undice: path collision: shared-behaviors.md`.
  `dicedoc._all_reproduced` recognizes a nested tree only by an `entry-point.md` below the root, so a
  volume headed `index.md` is read as four `not reproduced` strays. `manifest._write_group_indexes`
  writes `entry-point.md` for every volume it builds. No arrangement of the tree's files satisfies
  all three; the leaf's form is not the cause.
- `.devpro-temp/p3-dev-check-links.log`: `dev-check-links` reports
  `PROJECT_DOCS/SPEC/entry-point.md:29: dicing-and-checks.md: missing file` — the SPEC entry point
  still declaring the leaf the repair retired. It stands while the remedy is unmet: relinking the
  line to `dicing/index.md` leaves the tree's defect, and the entry point declaring its volume at a
  `dicing/index.md` line is the form the tree carries today.

**Guidance.**

1. Load the `devpro-docdicer` skill before editing; its undice-fix conventions govern (a leaf whose
   heading disagrees with its file name: edit the heading to match the name, not the file, which
   would move the path).
2. SPEC: the dicing volume is declared once, by `entry-point.md`'s member list, and the volume's
   index stands on its own root — moved to `SPEC/dicing-and-checks.md` with its heading at H1, the
   re-based write form its leaves carry, and no Contents block. A `dicing/index.md` cannot round-trip
   (`dicedoc._all_reproduced` reads it as a stray, `plan_sections` collides its H1 top with the
   tree's title); nothing inside `dicing/` declares the volume. Check: `just undice
   PROJECT_DOCS/SPEC .devpro-temp/<name>-undiced.md` exits 0. **Superseded by P5's restructure:**
   the volume's index keeps its directory (`SPEC/dicing/index.md`) and its heading, because a
   section directory's head stays in the directory whose child sections it lists; the
   "move to `SPEC/dicing-and-checks.md`" remedy applied when the leaves were the ones to move, and
   the restructure is the one that moves them.
3. CONVENTIONS: edit the two mismatched headings to the titles their file names and entry-point
   links carry, and add the two omitted leaves to the entry point's list.
4. ARCHITECTURE: rename the area's head to the nested-volume convention
   (`harness-profiler/entry-point.md` → `harness-profiler/index.md`), update
   `ARCHITECTURE/entry-point.md`'s area entry to `harness-profiler/index.md`, and replace the removed
   head's own Contents block with the area's members listed in the root entry point, below the area
   line: a nested area's head carries no Contents block (`_undiced_lines` reads only the root's; the
   dicer writes none). The owner's root-headed-area ruling names the area's standing — its own
   folder, first-class beside `SPEC/` and `CONVENTIONS/` — not the head file's name; the head name is
   the tool's convention. Correct `heads.py`'s module docstring to state the convention the function
   and the standing trees carry: the tree's root opens at ENTRY_POINT; every directory inside the
   tree opens at INDEX.
5. Verification per tree: `just undice <tree-dir> .devpro-temp/<name>-undiced.md` exits 0 with
   `reassemble ok`, and `just dev-check-links` reports `broken: 0` and `problems: 0`.

**Done-line.** `just dev-check-links`.

## P4 — the dicer's two patterns: volumes and broken-out sections; the manifest retires

**Scope.** `devpro/dicing/heads.py` (the head convention re-ruled); `devpro/dicing/dicedoc.py`
(`_restored`, `_undiced_lines`, `_placed_level`, `_all_reproduced`, `verify` — reconstruction and
checking per the two patterns); `devpro/dicing/linkrewrite.py` (`Linker.written`; the map's removal
is P4c's, declared in P4's commit as deferred — P4's row); `devpro/dicing/split.py` (the writer:
volume heads for input documents); `devpro/dicing/dice.py` (the writer's multi-input entry, in this
package: the `manifest.py` it absorbs); `devpro/dicing/treecheck.py` (the head wording of the two
patterns); `devpro/dicing/manifest.py` (deleted) and `devpro/dicing/cli.py` (the `dice-docs` verb
removed); `devpro/cli.py` (`DICING_VERBS`); the `justfile` recipe `dice-docs`; `tests/dicing/`
(corpus and tests; the `links.tsv` expectations are P4c's); the SPEC dicing leaves that state the
forms — `PROJECT_DOCS/SPEC/dicing/{index,link-rewriting,the-diced-tree,reassembly,dice}.md` — and
`PROJECT_DOCS/SPEC/package-and-command.md` (the surface verb list); and the management rules — the
two splitting paths, the growth-shape decision, the omnibus-head bounds and misuses — land in the
`devpro-docdicer` skill's definition, `devpro/definitions/skills/docdicer.py`, which is the text a
reader consults while managing a tree; the SPEC leaves carry the mechanics and state none of it.

**Facts.**

- The model, the owner's ruling: two structural patterns only. `entry-point.md` is the top document
  of a volume — an original whole document; `index.md` is the top document of a broken-out section —
  a piece diced out of a parent. `dice A.md B.md T/` makes every input document a volume under the
  omnibus: one directory per input at the output root, named for the input's base name without
  `.md`, holding its `entry-point.md` and its section children — `T/A/entry-point.md`,
  `T/B/entry-point.md` — and `T/entry-point.md` as the omnibus's own head. A volume's
  `entry-point.md` holds its document's title at level 1 and the document's own text above its first
  split heading; the document's title and its section ladders are written as `dice-doc` writes them.
  Each input's name must be distinct among the inputs, and no volume directory may take the name an
  `index.md` head already gives a section directory: where either would hold, the verb reports the
  collision and exits 2 writing nothing. `undice T/` emits one document per directory carrying
  `entry-point.md`; `index.md`-headed directories never become documents. No nested subvolumes: a
  joining document becomes a top-level volume or is subsumed and loses separate-document identity.
  A broken-out section round-trips as text without becoming a document: `undice` reads any head
  directory — an `index.md`-headed section undices to one document, its children folded — and
  `dice --section` states the identity on the way back, writing the section root's head as
  `index.md` and re-basing the ladder by the same arithmetic. The flag carries one bit: this
  document is a section, not a volume.
- The omnibus's own head carries bounded text: it orients the reader in the content and themes or
  guides navigation, and stays concise — under 100 lines, not counting the volume-listing section.
  Two misuses count even under the bound: specificity that belongs in a leaf, and covering material
  that belongs to one of the volumes — the first goes to the leaf it describes, the second to that
  volume's `entry-point.md`. Content whose growth would require splitting the head is misplaced the
  same way; needing the split is the indication of misuse, and the remedy is moving the content,
  never splitting the file.
- Leaf splitting has two paths, and they cover entry-point content too. **Simple fission** — a leaf
  that has grown laterally, denser or accumulated coverage at the same logical level, splits into
  sibling leaves. **Sub-dicing** — a leaf that has grown hierarchically, subtopics getting covered
  of their own, breaks out a new subdirectory with `index.md`; at the omnibus root, that sub-dicing
  is a new volume with `entry-point.md`. The decision is the growth's shape: hierarchical subtopics
  sub-dice, lateral accumulation fissures. This rule, with the omnibus-head rules above, is
  management guidance and lands in the `devpro-docdicer` skill; the SPEC dicing leaves keep the
  mechanics — what the tool writes and reconstructs — and state none of it.
- The manifest is not needed for creation or reconstruction: `dice-docs`, `devpro/dicing/manifest.py`
  and the manifest concept retire. Check, which must print nothing and is P4's done-line:
  `git grep -n 'dice-docs\|manifest\|links\.tsv' -- devpro/dicing devpro/cli.py justfile` and
  `git grep -n 'dice-docs\|manifest' -- PROJECT_DOCS/SPEC tests/dicing`.
- The map retires entirely: it was a compute cache — every row derivable from the document's own
  heading structure, the tree's two-pattern conventions, and the anchors' deterministic
  disambiguation of repeated heading text — and a cached resolution disagrees with the docs silently
  when they move. Links resolve at run time from the documents and the tree; a target that resolves
  nowhere is reported (`dangling:`), never cached. The rest of `manifest.py` — its manifest reader,
  the group-index and entry writers, and the post-write check — has no caller and is deleted, not
  ported; the map outlives it in P4's tree and is retired by P4c, whose Facts carry the analysis.
- Today's writer writes each section at the path `plan_sections` computes — `<name>/index.md` for a
  section with children, `<name>.md` otherwise (`outline.py:101`, `split.py:76`) — so the section
  half of the model is already the standing behavior; the writer has no head-name abstraction and
  the volume half is a change to the path plan, not just a head file: the plan's root section
  becomes `entry-point.md` and each input's document becomes a second tree under the root. Check:
  `git grep -n 'directory_head' devpro/dicing/*.py`.
- Today's reconstruction recognizes a nested tree only by an `entry-point.md` below the root
  (`dicedoc._all_reproduced`) — the form the model keeps for a volume, but it reads only the root's
  first Contents block (`_undiced_lines`) and so cannot reconstruct the multi-volume form at all.
  It also treats `index.md` as its directory's own section, one level above its siblings
  (`_placed_level`): correct while every head was a section index, wrong under the fold, where an
  `index.md` is a child of its volume's `entry-point.md` like any other section file. Check:
  `git grep -n '_all_reproduced\|_undiced_lines\|_placed_level' devpro/dicing/dicedoc.py`.

**Guidance.**

1. `heads.py`: the head convention becomes the two patterns — a volume's top document is
   `entry-point.md`, a broken-out section's top document is `index.md`. Which pattern a directory is
   is answered by the tree, not by the file: a directory is a volume root where it is the tree root
   or a direct child of the tree root holding an `entry-point.md`; every other directory holding an
   `index.md` is a broken-out section. `directory_head`'s callers state which pattern they are
   writing, and the function states it in its name, not as a boolean `tree_root`: `volume_head()`
   beside `section_head()`, or one function taking the pattern. The distinction is a checksum of
   structure: a top-level directory — the tree root's direct child — whose head is `index.md` is a
   misplaced section, and `check-tree` names it as one. The docstring states the model, the
   function implements it; `treecheck.py`'s module docstring and its `_head` state the same split,
   and the SPEC's `check-tree` section restates it. `heads.py` was P3's to correct (its committed
   docstring reads "every directory inside the tree opens at INDEX, the tree's own volumes
   included", which this step supersedes); P3 has landed, so the sole edit here is allowed — state
   it in the commit body. If a `heads.py` change outside this scope appears before this package
   lands, report and stop rather than edit it.
2. `dice` gains the multi-input form. Its output root holds exactly `entry-point.md` and one
   directory per input. The root's `entry-point.md` is the omnibus's own head: a level-1 title and a
   Contents block whose every section is a volume's `entry-point.md`, one line each, link text the
   volume document's title (its first level-1 heading's plain text) — the block `undice` reads to
   reach the volumes. A Contents link carries no text after it, so the volume's first-sentence
   purpose has no place in the block: state this in the SPEC leaves rather than carry a `Volumes:`
   block the form does not have. The single-input form is the multi-input form with one input, so a
   one-document `dice-doc` tree and a one-volume omnibus differ only in the root's Contents line
   count.
3. `undice` takes a tree directory, not a target: it writes into a directory named on the command
   line, one document per included directory — a volume directory `T/A/` writes `<out>/A.md` — and
   no document for a directory headed `index.md`; the omnibus root's document writes
   `<out>/<tree dir base name>.md`, and `<out>` must be absent or empty (exit 2 with that message,
   by `dice-doc`'s rule). A volume's reconstruction folds its `index.md`-headed sections back into
   its document — the sub-sections become the headings they had when the document was diced, by P1's
   ladder arithmetic — and drop any non-contract section link target it sees when dicing it back. A
   tree whose contents sit directly under its root (a one-document `dice-doc` tree, the three
   project-document trees) reconstructs as one document named for the tree directory: the form
   distinguishes them by whether `entry-point.md`'s direct sections are `index.md` or
   `entry-point.md` files.
4. Delete the manifest: `manifest.py`, the `dice-docs` verb and its recipe, and every test that
   exercises them. `dicedoc.verify` is not deleted with it: it becomes the per-tree check the
   re-dice and the board run, taking a tree directory instead of `(monolith, out)` pairs, and its
   `leaves:` line is where P5 reads leaf counts. Retire the SPEC dicing leaves' manifest wording in
   the same commit. The SPEC leaves state their coordination with the skill: they carry the
   implementation spec — what the tool writes and reconstructs — and the `devpro-docdicer` skill
   carries the usage conventions for managing a tree, and the two are to remain coordinated; a
   change to one that touches the other changes both.
5. Tests, per `clauses.TEST_PRECONDITION` (defect: the reconstruction cannot read the form the
   writer writes, and the manifest is a third party where two patterns suffice): the owner's example
   — `dice A.md B.md T/` produces the model tree; `undice T/` reproduces `A.md` and `B.md` with each
   volume's sections restored to their pre-dice levels; a section with children — the
   `index.md`-headed case, at any depth, with or without children of its own — is never emitted as a
   document, while the directory above it that carries `entry-point.md` always is; and two cases for
   the directory collision the model admits: an input whose base name is a section's directory name
   exits 2 writing nothing, and the same for two inputs of one base name.
6. The section round-trip. `undice` works on any directory with a head file: an `index.md`-headed
   section undices to one document — its title from the head, its children folded by the same
   ladder arithmetic as a volume's. `dice --section <md> <out-dir>` writes the output root's head
   as `index.md` and applies the inverse shift — the flag states the identity the head name
   records, so the demotion is declared, never inferred. The round trip is byte-checkable:
   `dice --section` of an undiced section reproduces the original directory. Tests, per
   `clauses.TEST_PRECONDITION` (defect: a section cannot be revised whole — the writer's own form
   strands it): `undice` of a section directory, then `dice --section` of the result, byte-equal
   tree.

**Done-line.** `just test-changed`, then `just lint`. The checkpoint gate runs once before the
commit, as P1 states.

## P4b — the reconstruction's stragglers, and the links.tsv cache retires

Fixes the two P4 tool defects P5's State section records, and retires the links.tsv map beside
them: the four changes share one call graph — `dicedoc.py`'s reconstruction and `linkrewrite.py`'s
rewriter call into each other's definitions, and each half alone leaves the suite red — so they
land as one package. Agent `devpro:python-coder`.

**Scope.** `devpro/dicing/dicedoc.py` (`_placed_level`, `dice`'s re-base root, the map's write and
read: `_map_rows`, `_run_path`, `_tree`'s map path, `dice`'s map argument and its `not a file`
fault, `_document`'s load, and `Volume`'s docstring clause); `devpro/dicing/linkrewrite.py`
(`Linker.written`, `LinkMap`, `Tree.link_map`, the map branches of `written` and `_rebase`, and
`_QUOTED_HEADING`/`_BARE_TAIL` with them); `devpro/dicing/cli.py` (the `--map` flag, and the call
it forwards to `dice`); the `justfile` `dice` recipe's comment; `tests/dicing/` (the reproduction
cases as corpus and tests, the `links.tsv` expectations, the round-trip test's `skip="links.tsv"`
and its "without a map" wording, and the `dice-map` and `dice-map-not-file` cases); the SPEC dicing
leaves where the map is stated — `PROJECT_DOCS/SPEC/dicing/link-rewriting.md` (§The link map and
link-target rule 3), `dice.md` (the usage line, `--map`'s fault, undice's map branch, and the round
trip's map clause) and `reassembly.md` (the undice best-effort entry).

**Facts.**

- `_placed_level` (`dicedoc.py:352`) raises a section index's child by the child's own heading
  depth: a leaf opening `## X` with `###` beneath restores at level 4 beside a sibling at level 3,
  so the re-plan reads the section index as a leaf. Minimal reproduction, four files, no SPEC
  content: `.devpro-temp/p5-repro-tree/`; the shape is the spec — any section index whose children
  carry deeper headings than a sibling.
- `dice` rebases a monolith's relative links against the run directory rather than the monolith's
  own directory (`linkrewrite.Linker.written`, `dice`'s `root=run_dir`), adding spurious `../`
  segments to every cross-tree link at any depth other than the output root's. Reproduction:
  `.devpro-temp/p5-lk/`.
- The map is a compute cache, not data: every row is derivable — in-dice targets from the heading
  structure, other inputs from the two-pattern convention, ambient targets from the same scan
  `check-links` already runs — and recomputation is cheaper than trust, because a cached resolution
  disagrees with the docs silently when they move.
- Resolution is deterministic without a cache: repeated heading text disambiguates by the anchors'
  document-order suffixes; a target that resolves nowhere is reported `dangling:` — the honest
  behavior, never a cached guess.
- What stays is the mapping in memory: built at run time from the inputs on the command line, alive
  for the execution, and written nowhere. What retires is persistence and re-ingestion — no file of
  a run survives it, so no later run reads anything a previous one wrote. `dice` and `undice` are
  self-contained: all inputs on the command line, all outputs declared, and the tree holds documents
  and nothing else — a file that is not one of its documents is a file the verb wrote and a later run
  may read.

**Guidance.**

1. `_placed_level` computes a restored part's level from its position in the tree and its own head's
   pattern — never from the part's heading depth relative to a sibling: a section index's child
   restores beside its siblings, not below them by its own depth. The two-pattern model is the
   authority; the corpus case pins it.
2. `Linker.written`'s re-base roots at the document's own directory, never the run directory: a
   cross-tree link survives a dice and an undice unchanged. Corpus case: a monolith whose link
   exits its directory, diced one level deep, links unchanged in the written tree.
3. Tests, per `clauses.TEST_PRECONDITION` (defect: the reconstruction restores a section index's
   child at its own depth, and the link re-base roots at the run directory): both reproduction
   shapes as corpus cases, demonstrated red before the fix.
4. The map retires entirely: remove its write and read (`dicedoc.py:217,238,391` region) and the
   `--map` flag — `dice` writes nothing into the output tree but the tree itself, and `undice` reads
   no map; remove the map handling from `linkrewrite.py` (`LinkMap`, `Tree.link_map`, the map
   branches of `written` and `_rebase`, and the regexes they alone use). `Tree` is a dataclass whose
   construction sites are all in this package's scope except `tests/dicing/test_linkrewrite.py`,
   which already names exactly its remaining fields and takes no edit. Check:
   `grep -rn 'Tree(' --include=*.py devpro tests` names every construction site and each names the
   fields the class declares; `grep -rn 'dice(' --include=*.py devpro tests` names one call site, in
   `cli.py`, whose argument count matches the definition.
5. The SPEC leaves' map wording retires with the concept: `link-rewriting.md`'s §The link map and
   link-target rule 3, `dice.md`'s usage line, `--map`'s fault, undice's map branch and the round
   trip's map clause — whose Round trip paragraph becomes: "For a tree as `dice` wrote it at
   `<level>`: move `<tree-dir>` aside, `undice` it to `<out-dir>`, then `dice` the documents
   `<out-dir>` holds at `<level>`, with `--section` where the tree is a section, from `<out-dir>` as
   the current directory; every file of the new tree equals the old byte for byte." — and
   `reassembly.md`'s undice best-effort entry is deleted outright.
6. Tests for the retirement, per `clauses.TEST_PRECONDITION` (defect: sideband data persisted into
   the tree, giving a later run an ambient dependency on a previous run's state): the `dice-map` and
   `dice-map-not-file` cases and the round-trip test's `skip` removed with the flag and its fault;
   and a case that asks the model's question of every file — `dice` a multi-input document into a
   tree, then assert each file is one the tree's head convention places (a volume root's
   `entry-point.md`, a section directory's `index.md`, a leaf elsewhere, every one `.md`) and the
   set is exactly the files the run declares; a second run over the same tree and output directory
   adds no file and changes none — the relocated cache this case catches and a "no sideband files"
   assertion does not.
7. The re-integration case: a link between two documents of the same dice resolves
   tree-internally — relative between their positions in the output tree — never against the
   directory the monolith was read from or the run directory. `Linker.written`'s base for a written
   leaf is the leaf's own directory in the output tree. Corpus case: dice a two-volume tree, move
   the whole tree to a different parent, and assert `check-links` stays green and the tree undices
   identically. Defect: links written against the run directory resolve only where the dice ran
   (evidence: SPEC's re-dice blocked, `.devpro-temp/p5-spec-finding.md`).

**Done-line.** `just test-changed`, then `just lint`, then the inventory's `git grep`, which prints
nothing: `git grep -in 'links\.tsv\|link map\|--map' -- devpro tests justfile PROJECT_DOCS` (and
`git grep -in 'link map' -- devpro/definitions/`, which prints nothing now and after). The
checkpoint gate runs once before the commit, as P1 states.

## P5 — the three standing trees re-diced under the settled model

**State.** All three trees are re-diced and placed, and each passes every check. SPEC was restructured
to the model and then re-diced; ARCHITECTURE and CONVENTIONS were re-diced in the package's first run
and are unchanged since.

SPEC's restructure, per the section below: `dice.md` split into `dice.md` + `undice.md`;
`reassembly.md` split into eight leaves (`reassembly.md`, `link-check.md`, `check-links.md`,
`check-tree.md`, `check-plan.md`, `check-design.md`, `check-roadmap.md`, `limits.md`); `kanban/`,
`link-rewriting/` and `the-diced-tree/` sub-diced into `index.md` plus their children; the volume
directory is `dicing-and-checks/`, the slug of its heading `Dicing and Checks` (the tool derives a
section's directory from its heading, so the directory had to take that name — no title is coined);
every leaf's file name equals its heading's slug; the entry point's member list and the volume index
rebuilt. Wording is unchanged: each leaf is its section's text, cut at heading lines, with only its
top heading promoted to level 1. The re-dice then put every tree in the re-based H1 write form.

Measured after the re-dice: `check-links PROJECT_DOCS *.md` -> 420 links, `broken: 0`; `check-tree
PROJECT_DOCS` -> 140 documents, `problems: 0`; per tree, SPEC 45 documents / 0 problems,
ARCHITECTURE 39 / 0, CONVENTIONS 55 / 0. Undice: SPEC `reassemble ok: 2218 lines`, `dead: 0`; dice
`reassemble ok: 2218 lines`, `dead: 0`, `dangling: 0`; ARCHITECTURE `reassemble ok: 1694 lines`,
CONVENTIONS `reassemble ok: 558 lines`, both `dead: 0`.

Two tool defects this package found and reported were repaired by P4b (`3b4d7f7`): the write side
now makes a link between two of a dice's documents tree-internally, so a diced tree resolves wherever
it is placed. One read-side gap remains and is not SPEC's: undice restores a link from a nested
section up to its volume's own `entry-point.md` against the run directory (`Linker._unrebase`), so a
second undice of the placed tree reports that one line as a difference. It is reproduced at three
files in `.devpro-temp/p5-up/`, does not affect any tree check, and is a P4b/P1 finding for the next
package; the round trip the Guidance names — undice to a monolith, dice to a fresh tree — passes.

**Scope.** `PROJECT_DOCS/SPEC/`, `PROJECT_DOCS/ARCHITECTURE/`, `PROJECT_DOCS/CONVENTIONS/`
(regenerated whole; SPEC additionally restructured, below); the monoliths are work products under
`.devpro-temp/`.

**Restructure (SPEC's `dicing/` area, to the model's shape).** The area's two leaves carry same-level
sibling sections the re-based form collapses, so the tree as it stands is not representable. Restructure:
split `dicing/dice.md` into two leaves (`dice`, `undice`); split `dicing/reassembly.md` into its
sections' own leaves; sub-dice `kanban`, `link-rewriting`, `the-diced-tree` into section directories
with `index.md`; update `SPEC/entry-point.md`'s member list, every Contents block, and the links the
move retargets. **The split targets, by the tree's headings:** `dice.md` → `dice.md` (its title and
preamble) and `undice.md` (its `## undice` body); `reassembly.md` → `reassembly.md` (its preamble),
`link-check.md`, `check-links.md`, `check-tree.md`, `check-plan.md`, `check-design.md`,
`check-roadmap.md`, `limits.md` — eight leaves in `dicing/`; `kanban.md` → `kanban/index.md` plus
its seven `###` children as leaves; `link-rewriting.md` → `link-rewriting/index.md` plus its four;
`the-diced-tree.md` → `the-diced-tree/index.md` plus its five. A leaf keeps its section's text and
title exactly; only its top heading's level moves, `##` to `#`. No new titles are coined.
**Retargeted links, by site class:** each split leaf's own internal links and anchors — every
`<leaf>.md#<anchor>` a split leaf names becomes `<leaf>/<child>.md#<anchor>` (or
`<leaf>/index.md#<anchor>` where the anchor is the leaf's own title), and each cross-leaf link takes
the split leaf's new directory; the mapping is worked out in `.devpro-temp/p5-spec-links.py`. The
count is a derived number, not a target: `git grep -n 'dicing/' -- PROJECT_DOCS/SPEC` and
`just dev-check-links` enumerate the sites. All citing sites: `SPEC/entry-point.md:30-35` (six
member lines), each split leaf's own links, and `ARCHITECTURE/repo-layout.md:17,48-49` — but only
where the cited path is a SPEC doc path; `dicing/` at `repo-layout.md:17` is the Python package and
does not move. `ARCHITECTURE/packaging.md:28` and `devpro/definitions/skills/docdicer.py` cite
dicing only as module names and verbs; they are unchanged. `PROJECT_DOCS/CONVENTIONS/` carries no
`dicing/` path and needs no edit.

**Guidance.**

1. Per tree: `just undice <tree-dir> .devpro-temp/<name>-undiced.md` (it refuses an existing
   target), then `just dice-doc .devpro-temp/<name>-undiced.md .devpro-temp/<name>-fresh/`. Undice
   and dice at the default split level 4, the level the trees were diced at. Take `reassemble ok`
   from the undice and `reassemble ok` plus `dead: 0` from the dice as the preconditions of step 2;
   a difference reported by either is a finding for P1, not something P5 patches — for ARCHITECTURE
   and CONVENTIONS, which round-trip; for SPEC, the pre-restructure undice's `cannot read` and
   `would be re-diced as` lines are this package's own State evidence, and `reassemble ok` is
   reached only after the restructure. A difference the **post-restructure** undice reports is a P1
   finding, or a defect in the restructure; name which from the failing leaf's heading, and stop
   rather than patch either. This is also the
   first end-to-end exercise of P1's form-conditional shift on a tree P1 did not write.
2. Replace, don't merge: `git rm -r <tree-dir>`, then
   `mv .devpro-temp/<name>-fresh <tree-dir>`. The fresh tree is the whole of the directory
   afterwards; a file the old tree held and the fresh tree does not is gone.
3. After all three replacements: `just check-links` with `problems: 0`, and
   `just dev-check-links`. The commit body names each tree re-diced and its leaf count — the count
   comes from the per-tree `check-tree` run's `documents checked:` line less that tree's head files
   (`entry-point.md`/`index.md`), the method stated in the commit body. The counts are taken after
   P2 and P4, which change ARCHITECTURE's inventory; no pre-measured baseline belongs in this plan.

P5 runs after P4 and P3: the re-dice regenerates the trees from their undiced monoliths, and running
it before the repair would freeze the trees' defects into regenerated form, while running it before
the model change would write trees the reconstruction cannot read.

**Fallback** (owner-directed, for a sideways run). Restore `PROJECT_DOCS/` to its state at P1's
landing (`9b0f8df` — the harness-profiler leaf still in `install/`, the dicer fix landed) with a
path-scoped `git checkout 9b0f8df -- PROJECT_DOCS`; then `undice`/`dice` each tree — the round trip
fixes the heading form; then move the leaf to the top of `ARCHITECTURE/` and dice it in place; then
rename its head `entry-point.md` → `index.md` and fix the links into it. Two addenda, from walking
the sequence: (a) at `9b0f8df` the leaf's run-ins are still bold, not headings — re-apply the
promotion (wording-neutral; the promoted file is `d58b1b1`'s) before dicing, or the dice splits
nothing; (b) CONVENTIONS' two heading mismatches and SPEC's double-declared volume exist at that
state too — re-apply `c8ac105`'s small edits when the undice names them; the failure is the repair
list, not a tool defect. For a partial sideways run, the cheaper fallback is per-tree: CONVENTIONS
and ARCHITECTURE are verified round-trippers at pre-P5 HEAD, so only the mangled tree restores.

**Done-line.** `just test-changed`, then `just lint`, then `just dev-check-links`. The checkpoint
gate runs once before the commit, as P1 states.

## P6 — Post-plan review

**Lifetime.** The review package lands nothing but `ACTIVE_PLAN_REVIEW.md`; its row is `landed` in
the commit that adds the file.

The post-plan reviewers review what P1–P5 shipped, and get the project documents, not this plan:

- `devpro:python-coder`, for the dicing tool and its tests;
- `devpro:architect`, for the structure and the documents' claims about the tool;
- `devpro:prompt-engineer`, for the re-diced trees as documents.

Each writes a review under `.devpro-temp/`. The session synthesizes them into
`ACTIVE_PLAN_REVIEW.md`. The row is `landed` in the commit that adds that file.

**Done-line.** `just dev-check-links` passes over the tree holding `ACTIVE_PLAN_REVIEW.md`.

## Post-plan burndown

The items the post-plan review's findings group into, one work package per root cause.

### B0 Post-plan burndown

Drafts the items below from `ACTIVE_PLAN_REVIEW.md`.

### B1 — restore the dicing-and-checks index preamble and the `--split-level` contract

Fixes R1. Agent `devpro:prompt-engineer`.

**Scope.** `PROJECT_DOCS/SPEC/dicing-and-checks/index.md`; `the-diced-tree/the-head-files.md:6`;
the leaves whose citations resolve to `devpro/dicing/cli.py:24-33`'s contract — `dice.md:3-5`,
`undice.md:3-4`; `devpro/dicing/cli.py` (no change expected; listed so a coder edit is not made
silently from a writer's item).

**Facts.**

- `git show f08a3d7^:PROJECT_DOCS/SPEC/dicing-and-checks/index.md` prints the source: a `## Dicing
  and Checks` heading, the Contents block, then **five** paragraphs with no headings — the
  usage-error definition; `**Streams.**`; `**Current directory.**`; `**Text.**`; `**Split level.**`
  — four bold run-ins, no `#streams` or `#split-level` anchor anywhere in the file.
- The code's contract: `.venv/bin/python -m devpro dice --help` → `--split-level {2,3,4}`, deepest
  heading level that splits into sections (default 4); an out-of-range value exits 2 with argparse's
  `invalid choice`. `devpro/dicing/cli.py:24-33` is the function that sets the choices, default and
  help string.
- The seven citations: `git grep -n 'shared behaviors' PROJECT_DOCS/SPEC` → 7 sites, all linking
  `dicing-and-checks/index.md#dicing-and-checks`. One of them, `the-head-files.md:6`, claims the
  shared behaviors "names the module that holds them"; no module SPEC names holds it.

**Guidance.**

1. **The restore, in place.** In `dicing-and-checks/index.md`, below the Contents block (a section
   index legitimately holds its section's text), write the five paragraphs as `##` sections with
   "Shared behaviors" as their heading, then the four bold run-ins as they stand; rewrite the
   `## Split level` link to `the-diced-tree/which-headings-split.md` — its slug is
   `#which-headings-split`. The restored anchor is `#shared-behaviors`, not `#dicing-and-checks`;
   the seven sites' fragments change too — state each: `#shared-behaviors`.
2. **Live in the head, not in a leaf.** The preamble is the volume's own text and is restored there;
   no leaf is cut for it — the index's H1 must be the volume's title (`# Dicing and Checks`), and
   `the-head-files.md:6`'s claim about a module is deleted.
3. **The split-level contract.** Keep `## Split level` in the index as the source restored it;
   re-state the contract to the code's current behavior: values `2`, `3`, `4`; default `4`; any other
   value a usage error. This is what the code does; do not invent a different message.
4. **The seven sites.** Re-point all seven to `#shared-behaviors`. `the-head-files.md:6`'s
   parenthetical is deleted (B2 owns that file's other line).
5. **The check.** `git grep -n 'shared behaviors' PROJECT_DOCS/SPEC` shows the seven sites, each
   fragment `#shared-behaviors`; `git grep -n '#streams\|#split-level\|#shared-behaviors'
   PROJECT_DOCS/SPEC` shows the anchors the index now carries and every site that names them.
   `just dev-check-links` exits 0.

**Done-line.** `just dev-check-links`.

### B2 — every link lands on the leaf whose text it names

Fixes R5, R8. Agent `devpro:prompt-engineer`.

**Scope.** `PROJECT_DOCS/SPEC/dicing-and-checks/` (every leaf holding a site below);
`PROJECT_DOCS/SPEC/dicing-and-checks/reassembly.md` (its opening sentence names the check it is);
`PROJECT_DOCS/SPEC/dicing-and-checks/the-diced-tree/the-head-files.md` (the parenthetical whose
referent is stated in B1's index text).

**Facts.**

- The sites are the output of two commands. `git grep -n 'index\.md#dicing-and-checks'
  PROJECT_DOCS/SPEC` → 59 sites: 10 `[file names and layout]`, 7 `[shared behaviors]`, 7
  `[link targets]`, 6 `[file content]`, 5 `[link rewriting]`, 4 `[the diced tree]`, 4
  `[section references]`, 4 `[anchors]`, 2 `[which headings split]`, 2 `[what is a link]`, 2
  `[the model]`, 2 `[the board]`, 1 `[the project's files]`, 1 `[moves between Roadmap and Design]`,
  1 `[misplaced section]`, 2 `[board's]`. `git grep -n '(\.\./reassembly\.md)' PROJECT_DOCS/SPEC` →
  28 sites: 8 `[check-plan]`, 8 `[check-roadmap]`, 7 `[check-design]`, 4 `[check-tree]`, 1
  `[check-links]`. `devpro check-links PROJECT_DOCS *.md` → `links checked: 420, broken: 0`, so none
  of the 87 is a broken link.
- Every one of the 87 is a retarget. The 7 `[shared behaviors]` sites land on the preamble B1
  restores, at `#shared-behaviors`; each of the other 80 lands on the leaf whose H1 is its link
  text — except `[misplaced section]` and the two `[board's]`, whose referent is
  `dicing-and-checks/index.md` and which stay as they stand. The 77 that land on the volume today
  are the class `check-links` cannot see.
- **B1 lands before this item**; until `dicing-and-checks/index.md` holds the preamble again, the
  seven `[shared behaviors]` sites have no target and are left as they stand.

**Guidance.**

1. Retarget the 87 sites by the mapping above; each retarget's referent is the leaf whose heading
   text the link names — verify by reading the target's H1 (`head -1`), and state the count of
   sites whose anchor is not their target's H1 in the commit body.
2. Pin the class with a test in `tests/dicing/` that reads the tree and asserts the list is empty,
   printing the same list before the fix (the red state). `check-links` cannot settle it, and a
   commit-body list does not.

**Done-line.** `just test-changed`, then `just lint`, then `just dev-check-links`, then the test,
whose output states the count — zero after the fix.

### B3 — the tool: one classifier, honest faults, no dead code

Fixes R3, R4, R6, R7, R10, R11, R12, R18's code half. Agent `devpro:python-coder`.

**Scope.** `devpro/dicing/split.py` (`write_tree`, `_fits`);
`devpro/dicing/treecheck.py` (`_misplaced_head`);
`devpro/dicing/dicedoc.py` (`_volume_documents`, `_placed_level`, the `add` closure in `_walk`,
the title-less-volume refusal); `devpro/dicing/linkrewrite.py`; `_top_is_rebased`'s rename
(`reassemble.py:29`, touching `dicedoc.py` and `split.py`); `tests/dicing/` (the corpus cases and
any unit test pinning the four functions).

**Guidance.** Each fix lands with its corpus case red before the fix, per
`clauses.TEST_PRECONDITION`; the defect and case, one per fix:
R3 — one stray prose link to `x/entry-point.md` in a root head flips `check-tree` on a valid
one-document tree; case: that tree, `problems: 0`. R4 — a `--split-level 2` document whose leaf
holds `###### Heading` names the section's first line; case: `dice-heading-too-deep`, `names` holds
the offending line and level. R6 — `_placed_level('a/b/c/d/e/f.md')` is 7; case: the unit test
returns `None`. R7 — `dice` of a document with an unrebased section prints the writer's line and no
`reassemble: first difference` line; case: `names` asserts the absence. R10 —
`grep -c 'def add' devpro/dicing/dicedoc.py` → 1 and `visit` calls it. R11 — a title-less document
dices to exit 2, `volume b: no opening level-1 heading`, nothing written. R12 — it is R3.

**Done-line.** `just test-changed`, then `just lint`; `just dev-check-links` once B1 lands. The
checkpoint gate runs once before the commit, as P1 states.

### B4 — single-home the model rules, and the corpus's missing shapes

Fixes R2, R9, R13, R14, R15, R17. Agent `devpro:architect` — R2 is a decision, and this seat owns it.

**Scope.** `PROJECT_DOCS/SPEC/dicing-and-checks/the-diced-tree/the-model.md`;
`PROJECT_DOCS/SPEC/dicing-and-checks/the-diced-tree/file-content.md`;
`PROJECT_DOCS/SPEC/dicing-and-checks/check-tree.md`;
`PROJECT_DOCS/SPEC/dicing-and-checks/link-rewriting/link-targets.md`;
`PROJECT_DOCS/SPEC/dicing-and-checks/undice.md` (R9's restore half, R14's tree statement).

**Guidance.** R2's decision is taken before any other entry here, and is this seat's: which of
`the-model.md`'s `SPEC/` clause and `check-tree.md`'s example list is the contract; this item's
executor writes the model's sentence and reduces `check-tree.md` to a reference. R14's tree
statement lands in `the-model.md`, beside R2's sentence. `link-rewriting.md` states the
cross-document link rule (R9) and `link-targets.md`'s rule 3 is amended. The corpus cases (R13, R14,
R15) wait on R2's decision; R18's `_top_is_rebased` rename is B3's.

**Done-line.** `just test-changed`, then `just lint`, then `just dev-check-links`.

### B5 — the contract gaps the run named

Fixes G1, G2, G4, G5 and the re-based/rebased spelling. Agent `devpro:prompt-engineer`.

**Scope.** `PROJECT_DOCS/CONVENTIONS/planning-and-execution/` (`the-gates.md` or
`evidence-commands-run-before-they-ship.md` for G5 — the item names one);
`CONVENTIONS/planning-and-execution/index.md` (each new leaf's Contents line);
`devpro/definitions/skills/development.py` (*Verification evidence*, for G5's sentence; G2's probe
line); `devpro/clauses.py` (`PE_LEAD`'s section, for G4 — it renders into every coder definition);
`PROJECT_DOCS/SPEC/dicing-and-checks/` (the `re-based`/`rebased` spelling sites:
`git grep -n 're-based\|rebased' PROJECT_DOCS/SPEC`).

**Guidance.** G1: a format change that narrows the expressible set names the inputs that no longer
fit, and the tool refuses them by name — the leaf cites R11 as its worked instance, and its home is
`planning-and-execution/` because the review proposed it there. G4: where two commits' halves share
a call graph such that either alone leaves the gate red, the split is a Blocker naming the shared
definitions — one edit in `clauses.py`'s `PE_LEAD` section reaches every coder definition; the
worked instance is the P4b/P4c merge (`313f95d`, `c9b4cd0`: "P4c merges into P4b — the halves share
one call graph"). G5: a verification entry lists the artifacts the run produced, by path. G2's
probe line states which interpreter the rule means, scoped to this repository's checkout. Spelling:
pick one of re-based/rebased across the SPEC dicing leaves. G3 — a section directory's name must
equal its heading's slug — lands in the `devpro-docdicer` skill's tree conventions
(`devpro/definitions/skills/docdicer.py`), beside the two-pattern model; B4's restructure is the
worked instance.

**Done-line.** `just dev-check-links`.
