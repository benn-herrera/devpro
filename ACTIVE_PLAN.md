# Active plan — the activity profiler is devpro's own Python, writing into the project's scratch directory

From the accepted design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — five entries:
[the Shipped files entry](ACTIVE_DESIGN.md#shipped-files) and [the Guide and README
entry](ACTIVE_DESIGN.md#guide-and-readme) under SPEC delta, [the Harness profiler
entry](ACTIVE_DESIGN.md#harness-profiler) and [the Repo layout entry](ACTIVE_DESIGN.md#repo-layout)
under ARCHITECTURE delta — each one passage pair — and [the Harness profiler entry under Code
delta](ACTIVE_DESIGN.md#harness-profiler-1) (prose, no pair; the port package composes from it).
The design is not diced; it is under the plan size limit.

Every package's intended lifetime is **shipped** — the whole process — and one commit closes each
package: the closing commit sets its Status row to `landed` as that commit lands its work.

Sequencing: P1, then P2, then P3, then P4. P1 applies the four passage pairs; P2 composes the port
from the Code delta prose; P3 and P4 are the post-plan review and burndown.

The bound checkpoint gate is `just test`, then `just sweep-python`
(`PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md:4-5`). Its `docs` surface fails for a
reason outside this work: the installed launcher pins docdicer `v0.12.0`
(`devpro/docdicer-tools/docdicer:8`, `VERSION=0.12.0`) and the tag is not published, so
`just check-links`'s pip build fails `git checkout -q v0.12.0` (observed run: `error: recipe
'docdicer' failed on line 37`, exit 1). The ROADMAP item
(`ROADMAP.md:58-62`, "The docdicer `v0.12.0` tag is unpublished") resolves it; the item leaves
ROADMAP when the tag is published. A package's gate therefore passes on every surface but `docs`,
and each package's done-line names the checks that do pass rather than the gate as if green. The
hosted-clone route `just dev-check-links` covers the document checks meanwhile (observed run:
`links checked: 171, broken: 0`, `documents checked: 88, problems: 0`, exit 0; the count moves with
the plan's own links — the pass condition is `broken: 0`, exit 0. The clone is dirty and left at
`v0.11.2`, reported, not reset — `devtools/scripts/docdicer-repo.sh` exits 0 on a dirty clone).

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | landed | mechanical | the four passage pairs applied verbatim: SPEC's profiler paragraph and guide-and-readme requirements bullet, ARCHITECTURE's harness-profiler leaf and repo-layout resources line |
| P2 | landed | expert | the port: `hp.py` replaces `hp.js`, `hp.sh` finds python3, the trace moves to `.devpro-temp/harness-profile/`, the skill text and tests follow |
| P3 | in progress | expert | Post-plan review |
| P4 | drafted | expert | Post-plan burndown |

## P1 — The four passage pairs applied

Implements [the Shipped files entry](ACTIVE_DESIGN.md#shipped-files), [the Guide and README
entry](ACTIVE_DESIGN.md#guide-and-readme), [the Harness profiler entry](ACTIVE_DESIGN.md#harness-profiler)
and [the Repo layout entry](ACTIVE_DESIGN.md#repo-layout), each as accepted: its `becomes` block
replaces its `as it stands` block, each run of whitespace read as one space, no composition; the
labels the design's blocks carry (`**As it stands:**`, `**Becomes:**`) are not written into the
target.

Scope: `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`,
`PROJECT_DOCS/SPEC/guide-and-readme.md`, `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`,
`PROJECT_DOCS/ARCHITECTURE/repo-layout.md`.

Facts, each re-run before acting on it:

- The SPEC pair's from-block sits byte-exact at
  `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:95-105` (the profiler paragraph, first line
  `A claude project install also ships the **activity profiler** payload:...`, last line `...the
  resources or the hook entries.`); the ARCHITECTURE pair's from-block is the leaf below its
  heading: `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md:3-46` (44 lines — the file is 46
  lines with the `### Harness profiler` heading at line 1 and the blank line 2, which stay).
- The Guide and README pair's from-block sits byte-exact at
  `PROJECT_DOCS/SPEC/guide-and-readme.md:37-39` (`sed -n '37,39p'` → the three lines: the
  requirements bullet's tail two lines, naming `node` 18 or later for the claude activity profiler,
  plus the following cold-read bullet, which anchors the from so the becomes-block is not a prefix
  of it). Its application drops the node clause and keeps the cold-read bullet.
- The Repo layout pair's from-block sits byte-exact as a substring of
  `PROJECT_DOCS/ARCHITECTURE/repo-layout.md:18` (`sed -n '18p'` → one line holding
  `` `claude/libexec/hp.sh`, `claude/libexec/hp.js` and `claude/libexec/view.html` (the activity
  profiler, Install, Harness profiler) ``); its application renames `hp.js` to `hp.py` in that
  fragment, the rest of the line unchanged.
- The byte-check today: `just dev-check-design-deltas-applied` → `pairs: 4, landed: 0, pending: 4,
  drifted: 0, conflicting: 0, problems: 0`, exit 1 — all four pairs unapplied, their from-blocks
  matching their targets. P1's application moves all four to landed.
- No passage carries a markdown link — the `(SPEC.md, Deployed Surfaces, Shipped files)` and similar
  mentions are parenthetical text — so nothing to rebase.
- No test pins any passage's text: `git grep -n "activity profiler" -- tests/` → only
  `tests/test_devpro_install.py:406`, a comment. P1 changes no code, so no test can break.

Work:

1. Apply the SPEC pair's becomes-block over the from-block in `shipped-files.md` verbatim.
2. Apply the Guide and README pair's becomes-block over the from-block in `guide-and-readme.md`
   verbatim.
3. Apply the ARCHITECTURE pair's becomes-block over `harness-profiler.md:3-46` verbatim; line 1's
   heading and the blank line 2 stay.
4. Apply the Repo layout pair's becomes-block over its fragment in `repo-layout.md` verbatim.
5. Run the byte-check: `just dev-check-design-deltas-applied` must report all four pairs landed
   (`landed: 4, pending: 0, problems: 0`, exit 0).

Done-line: `just dev-check-design-deltas-applied` (pending: 0), then `just dev-check-links`. One
commit closes the package.

## P2 — The port: hp.py replaces hp.js

Implements [the Harness profiler entry under Code delta](ACTIVE_DESIGN.md#harness-profiler-1),
composing the port from its prose.

Scope: `devpro/harnesses/resources/claude/libexec/hp.py` (new),
`devpro/harnesses/resources/claude/libexec/hp.js` (deleted),
`devpro/harnesses/resources/claude/libexec/hp.sh` (rewritten finder),
`devpro/harnesses/claude.py:69-71` (comment), `devpro/definitions/skills/show_profile.py:16`
(trace-directory sentence), `devpro/definitions/skills/guide.py:76-77` (node warning retires),
`README.md:45` (the same node warning sentence), `tests/test_devpro_install.py:409`
(`_PROFILER_FILES` pin becomes `("hp.py", "hp.sh", "view.html")`), `.gitignore` (the
`.harness-profile/` line at HEAD `:23` removed). `view.html` ports unchanged.

Facts, each re-run before acting on it:

- `hp.js` is 961 lines with four subcommands (`capture`, `tree`, `init`, `doctor` — `hp.js:6-9`);
  `hp.sh` is 54 lines whose whole job is finding node: `HP_NODE` override (`hp.sh:12`), `command -v
  node`, `~/.volta/bin/node`, the newest `~/.nvm/versions/node/*/bin/node`, `/opt/homebrew/bin/node`,
  `/usr/local/bin/node` (`hp.sh:13-44`), and where none: `capture` drains stdin and exits 0, other
  subcommands report and exit 1 (`hp.sh:50-51`). The port: `hp.sh` finds `python3` (`HP_PYTHON`
  overrides the search) and runs `hp.py` beside it, keeping the same silent-capture shape.
- The python3 search keeps the ordering rationale the launcher states (`hp.sh:5-8`): hooks may run
  with a bare PATH, so the finder looks past `command -v python3` into the version managers' and
  Homebrew's install locations. The exact list is the executor's call; the constraint is the
  rationale — a bare-PATH hook must find an interpreter — plus the silent-capture shape above.
- `hp.js:57` names the committed-hook set: `const HOOK_FILES = [LAUNCHER, 'hp.js', VIEW_TEMPLATE]`,
  which `init` copies (`hp.js:849`) and `doctor` compares for staleness (`hp.js:899`). The port
  renames the list's `hp.js` entry to `hp.py`: a literal port leaves `init` copying a file that no
  longer exists in the source directory and `doctor` flagging the old name forever.
- The record's shape is a port constraint, not a design decision: `hp.js:16` sets
  `SCHEMA_VERSION = 2`, `:349` and `:391` write `v: SCHEMA_VERSION` with the tool, agent, timing and
  token fields, and `tree --format html` hands those records to `view.html`'s parser. `view.html`
  ports unchanged, so `hp.py`'s records keep the schema `view.html` and `tree` read — same
  `SCHEMA_VERSION` and field names; a renamed or dropped field renders a page that opens empty.
- The capture's root resolution stays: `sed -n '128,130p' devpro/harnesses/resources/claude/libexec/hp.js`
  → `function projectDir(cwd, env = hookEnv()) { const start = env.CLAUDE_PROJECT_DIR || cwd; return gitRoot(start) || start; }`
  — the trace lands at the project root, so only the path under it changes, `.harness-profile/` →
  `.devpro-temp/harness-profile/` (`hp.js:17`, `:416`).
- The `.git/info/exclude` write retires with the move: `excludeTraces` (`hp.js:115-122`) appends
  `TRACE_DIR/` to `info/exclude`; the scratch directory's gitignore convention carries the
  exclusion duty (`.gitignore:22` holds `.devpro-temp/`). The working tree is dirty at drafting
  with exactly that edit: `.gitignore`'s `.harness-profile/` line (HEAD `:23`) removed
  (`git diff .gitignore` → the deletion, uncommitted); the user made it, the port makes it correct,
  and P2's commit carries it.
- The trace-path sites outside the resources: `devpro/harnesses/claude.py:70` (comment) and
  `devpro/definitions/skills/show_profile.py:16` (skill text); the SPEC and ARCHITECTURE sites
  (`shipped-files.md:101`, `harness-profiler.md:23-24`) are covered by P1's pairs. No test pins the
  trace path: `git grep -n "harness-profile" -- tests/` → nothing.
- The node-requirement sites: `devpro/definitions/skills/guide.py:76-77` and `README.md:45` carry
  the same warning sentence (`node` 18 or later, for the claude activity profiler: without it its
  captures stay silent and the trace is empty.); the Code delta names the guide's site, and the
  README line is the same warning in the README's rendering of the requirements. Retiring both is in
  scope. SPEC's requirements sentence naming `node` 18 is covered by P1's Guide and README pair.
- The skill finder's two candidates name `hp.sh` paths, which keep their names:
  `sed -n '22,24p' devpro/definitions/skills/show_profile.py` →
  `1. `../../libexec/hp.sh`, from this skill's own directory: the copy the project's install delivered`
  and `2. `.claude/harness-profiler/hp.sh` at the repository root: the copy a committed hook runs, which is`;
  hook code, not trace data, does not move. The skill body's `mkdir -p .devpro-temp` (`:38`) and page
  path `.devpro-temp/harness-profile.html` (`:40`) already write the scratch directory and stay.
- The registration wiring keeps its shape: `sed -n '72,73p' devpro/harnesses/claude.py` →
  `_PROFILER_SCRIPT = "libexec/hp.sh"` and
  `_PROFILER_COMMAND = f'sh "${{CLAUDE_PLUGIN_ROOT}}/{_PROFILER_SCRIPT}" capture claude'` — hp.sh
  keeps its name, so the wiring is unchanged; only the comment at `:69-71` moves to the new trace
  path and drops the node phrasing.
- The install's resource discovery is a glob (`devpro/install.py:196-201`, `source.rglob("*")` over
  `harnesses/resources/<harness>/`), so adding `hp.py` and deleting `hp.js` needs no install.py
  change; the copy follows the directory. An upgrade leaves the old file behind: the copy is
  one-way and `prune` walks only the three rendered surfaces (`devpro/install.py:295-300`), so a
  consumer's `libexec/` keeps `hp.js` beside the new `hp.py`. The amended leaf is silent on it;
  stating the limit there is the design's to amend, and the user decides that.
- The tests pinning the profiler: `git grep -n "_PROFILER\|HP_NODE" -- tests/` →
  `tests/test_devpro_install.py:408` (`_PROFILER = "libexec"`), `:409`
  (`_PROFILER_FILES = ("hp.js", "hp.sh", "view.html")`), `:418`
  (`_PROFILER_COMMAND = 'sh "${CLAUDE_PLUGIN_ROOT}/libexec/hp.sh" capture claude'`), `:472`-`:473`
  (the payload-landing test's assertions, its def at `:464`), `:487` (the hook entry shape),
  `:1425` and `:1883` (the user-level and no-opencode-copy assertions, the latter's def at `:1873`).
  Updating `:409` is in scope; the rest pass unchanged — a failure in them is reported as a
  finding, never edited to pass.
- The banner rule binds every harness resource: `hp.py` carries
  `# !INSTALLED! from devpro/harnesses/resources/claude/libexec/hp.py — ...` within its first ten
  lines — Python comment syntax; the banner test
  (`tests/test_devpro_install.py:1791-1794`) checks only the `!INSTALLED! from <origin>` text, not
  the comment marker, and `hp.js:2`'s `//` becomes `#` in the port.
- The README credit line stands verbatim: `README.md:142` ("whose source was adapted for our own
  activity profiler") — no version stamping, no origin constant.
- No test executes hp.js or hp.py: `git grep -ln "hp\.js" -- tests/` → only
  `tests/test_devpro_install.py:409` (the `_PROFILER_FILES` pin). The port's verification is the
  install pins and the byte-check, not a behavioral test; the design adds none.

Work:

1. Write `hp.py`: Python 3 standard library only, the four subcommands (`capture`, `tree`, `init`,
   `doctor`), same capture behavior — one hook payload on stdin, one record appended per event,
   exits 0 silently on a failed capture or a missing interpreter — the trace at
   `.devpro-temp/harness-profile/<session-id>.jsonl` under the project root, no `.git/info/exclude`
   write, the `!INSTALLED!` banner in its first ten lines. The record keeps the schema the
   unchanged `view.html` and `tree` parse: `SCHEMA_VERSION` 2 and the same field names
   (`hp.js:16`, `:349`, `:391`). `init`'s committed file list names `hp.py` (`hp.js:57`, used at
   `:849` and `:899`).
2. Rewrite `hp.sh`'s finder: python3 (`HP_PYTHON` overrides), `capture` drains stdin and exits 0 on
   a missing interpreter, other subcommands report and exit 1; the header comment names python3 and
   hp.py.
3. Update `devpro/harnesses/claude.py:69-71`'s comment; update `show_profile.py:16`; retire
   `guide.py:76-77`'s node warning and `README.md:45`'s; update `tests/test_devpro_install.py:409`.
   The prose edits are mechanical substitutions, stated here:
   - `claude.py:69-71`: `.harness-profile/` → `.devpro-temp/harness-profile/` in the comment's
     second line, and "exits 0 where it finds no node" → "exits 0 where it finds no python3" in its
     third.
   - `show_profile.py:16`: the sentence's one substitution — `.harness-profile/` →
     `.devpro-temp/harness-profile/` ("The trace is the newest session recording in
     `.devpro-temp/harness-profile/` at the repository root.").
   - `guide.py:76-77` and `README.md:45`: delete the node-requirement bullet from each list — the
     same sentence in both, "node 18 or later, for the claude activity profiler: without it its
     captures stay silent and the trace is empty."
4. Delete `hp.js`.
5. Observe the port where no gate executes it: in a scratch git repository under `.devpro-temp/`,
   run `sh devpro/harnesses/resources/claude/libexec/hp.sh init claude` — it copies the four files
   and exits 0, proving `HOOK_FILES` names files that exist; feed one synthetic payload through
   `sh devpro/harnesses/resources/claude/libexec/hp.sh capture claude` and run
   `sh devpro/harnesses/resources/claude/libexec/hp.sh tree --format html` — the page renders the
   record, proving the schema `view.html` parses survived the port.

Done-line: `just test devpro`, then `just test wheel`, then `just sweep-python`, then
`just dev-check-design-deltas-applied` (all four pairs still landed), then `just dev-check-links`. One
commit closes the package.

## P3 — Post-plan review

The reviewers are given the project documents and the design, not the plan, and review the changes
and their tests against the project's standards and fitness for purpose. Each writes their own
review in the scratch directory, independently, at `.devpro-temp/p3-review-<seat>.md` — one file
per seat, named for it (`p3-review-architect.md`, `p3-review-prompt-engineer.md`,
`p3-review-tech-writer.md`, `p3-review-python-coder.md`) — and the session synthesizes them into
`ACTIVE_PLAN_REVIEW.md`, never diced, de-duplicating findings and reconciling them into one account.

- `devpro-architect` — the port's shape against ARCHITECTURE.md (the amended harness-profiler leaf
  and the amended repo-layout leaf, both as P1's pairs landed them) and the definition modules'
  structure;
- `devpro-prompt-engineer` — the show-profile skill's text and the guide's retired warning
  (model-facing text changed);
- `devpro-tech-writer` — README.md:45's retirement and the credit line standing verbatim, and the
  credit-line discrepancy the review flagged: the leaf P1 lands says the acknowledgement credits
  "the source of the idea and design" while README.md:142 says "whose source was adapted" — the
  leaf's wording is the design's to amend, and the user decides that;
- `devpro-python-coder` — `hp.py` and `hp.sh` against the project's coding standards.

Done-line: `just dev-check-links`. The review document and P3's Status row land in P3's commit.

## P4 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands. This section holds the
drafting instruction until then; the landing acts below are settled now.

Done-line: `just test devpro`, then `just sweep-python`, then
`just dev-check-design-deltas-applied` (all four pairs landed), then `just dev-check-links`, then
`just dev-check-plan` — all before the landing acts, which delete the plan the last check reads;
the landing commit's own proof is that run repeated on the tree it leaves. `just test`'s `docs`
surface fails as the header states; every other surface passes.

The landing acts, after the burndown's work:

1. The landing commit deletes `ACTIVE_DESIGN.md` (not diced, so no tree).
2. The landing commit deletes `ACTIVE_PLAN_REVIEW.md`.
3. The landing commit deletes this plan (`ACTIVE_PLAN.md`) — no next plan exists at that time.
4. The landing commit bumps the version: `__version__` in `devpro/__init__.py` to `"0.18.0"` — the
   minor bump the profiler's new behavior rates (user decision) — and `README.md`'s pipx tag beside
   it, per *Version has one home*; the three rendered carriers follow from the constant at the next
   render. Committed before any `just tag`.

Every commit message and pull-request description carries the attribution line the development
skill states:

```
ai assisted by [devpro](https://github.com/benn-herrera/devpro) on opencode. submitter takes full responsibility.
```
