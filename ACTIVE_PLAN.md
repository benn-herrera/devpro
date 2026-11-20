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
(`PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md:4-5`). The gate's `docs` surface was
red while the plan ran: the installed launcher pins docdicer `v0.12.0`
(`devpro/docdicer-tools/docdicer:8`, `VERSION=0.12.0`) and the tag was unpublished, so
`just check-links`'s pip build failed `git checkout -q v0.12.0`. The tag shipped mid-run (merged,
tagged, pushed), and the surface is green: `just check-links` → `links checked: 171, broken: 0`,
`documents checked: 88, problems: 0`. The full gate passes on the tree; the hosted-clone route
`just dev-check-links` remains equivalent, its pass condition `broken: 0`, exit 0. The hosted clone
is dirty and left at `v0.11.2`, reported, not reset — `devtools/scripts/docdicer-repo.sh` exits 0 on
a dirty clone.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | landed | mechanical | the four passage pairs applied verbatim: SPEC's profiler paragraph and guide-and-readme requirements bullet, ARCHITECTURE's harness-profiler leaf and repo-layout resources line |
| P2 | landed | expert | the port: `hp.py` replaces `hp.js`, `hp.sh` finds python3, the trace moves to `.devpro-temp/harness-profile/`, the skill text and tests follow |
| P3 | landed | expert | Post-plan review |
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

Drafted from `ACTIVE_PLAN_REVIEW.md` (landed at `da25a3a`): 2 High, 8 Medium, 13 Low — 23 findings.
Seven items below; the declined list accounts for the rest, every finding named: 18 in the items
(B1: R1, R19; B2: R2, R5, R6, R7, R20; B3: R3; B4: R4, R17; B5: R9, R10; B6: R11, R13, R14, R15,
R16; B7: R21), five declined (R8, R12, R18, R22, R23), plus the sanitization note (architect N3)
declined with them. Each item names its surfaces and its verification.

**B1 — the capture's silence restored (`R1`, `R19`).** `devpro/harnesses/resources/claude/libexec/hp.sh`
(27 lines): every pre-interpreter `capture` failure path drains stdin and exits 0 with no output —
stdout and stderr both empty. The failure cases, named: (a) a PATH python3 older than 3.9 that
cannot run `hp.py` — the finder verifies the interpreter it found can run the payload before exec'ing
it, and treats one that cannot as not-found (the check is the executor's call: cheap, stdlib-only,
silent); (b) `HP_PYTHON` set to a directory — the finder tests it with `[ -f ]` as well as `[ -x ]`
(`hp.sh:13`), so a directory falls through to the PATH search; (c) `hp.py` missing beside the
launcher; (d) no interpreter at all — the shape already correct (`hp.sh:20-26`; the drain at `:23`,
`capture) cat >/dev/null 2>&1; exit 0 ;;`); (e) a broken-JSON payload. Where output is allowed
(non-capture subcommands), the not-found message distinguishes a bad `HP_PYTHON` from an absent
interpreter: the finder remembers `HP_PYTHON` was set but unusable, and the message names it.
Verify, by hand in a scratch project — not the coder seat's probe — running each case against the
ported launcher `devpro/harnesses/resources/claude/libexec/hp.sh`: every capture failure case exits
0 with stdout and stderr both empty; `tree` with no interpreter still exits 1 with its message on
stderr; `HP_PYTHON=/nonexistent sh hp.sh tree` on a PATH with no python3 prints a line naming
`HP_PYTHON`, distinct from the no-interpreter line.

**B2 — the show-profile skill reads the ported tool whole (`R2`, `R5`, `R6`, `R7`, `R20`).**
`devpro/definitions/skills/show_profile.py`: the "no calls recorded" branch's test is that the
verbose tree prints the header alone (`render_tree` returns the header joined to the drawn rows,
`hp.py:1042-1044`; `visible()` draws every node under `--verbose`, `hp.py:880-883`), replacing
`:45`'s attribution to a `tree` report `tree` never makes; the count comes from the trace file's
line count, `--verbose` only deciding the empty case; the dead `mkdir -p .devpro-temp` block
(`:38,43`) is deleted — a successful `tree` proves the directory; `init`'s clause states
write-and-print-`git add`, not commit (`:30`); the failure path stops relaying `doctor`'s
"hook: not installed" line unchecked (`:45`) — the skill says what `doctor` said and that its
plugin-record check cannot see the payload copy; the finder's candidate-1 gloss holds for project
installs and states the user-level case (`:22`). Verify: `just render`, then the rendered skill's
instructions walked against a scratch trace holding only Bash calls — the count is nonzero and no
"nothing recorded" branch fires.

**B3 — the credit clause reconciled (`R3`).** The leaf
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md`'s clause "credits the source of the idea and
design" becomes "credits the source" — the README's verbatim line is the acknowledgement, and the
leaf stops characterizing it beyond what it says. The design's ARCHITECTURE becomes-block carries the
identical clause change in the same commit, so the byte-pinned pair stays landed. Verify:
`just dev-check-design-deltas-applied` still reports `landed: 4`.

**B4 — one regression pin for the port's contract (`R4`, `R17`).** `tests/test_devpro_profiler.py`
runs the installed launcher's `capture` with a synthetic `PostToolUse` payload in a scratch project
and asserts the record line's schema (`v: 2`, the field names) and that `tree --format html`'s page
data carries the keys `view.html` parses. The payload is the four keys `fix.sh:9` sends —
`hook_event_name`, `session_id`, `tool_name`, `tool_input`; the install route is
`_definition_install(root, project_root=tmp_path)` (`tests/test_devpro_install.py:470-473`); the
interpreter is pinned with `HP_PYTHON=sys.executable`, so the test asserts against the harness
host's own interpreter, not whatever PATH holds. The defect it fails on, named per the
test-precondition clause (`devpro/clauses.py:170`): a port that renames or drops a record field the
page data carries — a field rename or drop ships green and renders an empty page. The planted
mutation, with its red run: drop `ctxTokens` from the payload `hp.py`'s `capture` builds, or bump
`SCHEMA_VERSION` to 3 — the page-data assertion fails red while every current check stays green;
observe the failure, revert, and quote it. The byte pin (`R17`): one line asserts the installed
launcher's bytes equal the source resource's — `read_bytes()` equality against
`devpro/harnesses/resources/claude/libexec/hp.py` — so a stamp or reflow landing in `hp.py` through
`packages.find` is caught. Scope: B4 pins the record/D-payload contract half of R4; the
capture-outcome half is covered by B1's five-case probe. `just test devpro` runs it.

**B5 — the two contract facts stated (`R9`, `R10`).**
`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/harness-resources-are-copied-verbatim.md`
gains: a harness resource written in Python is inside `just lint`'s paths (`justfile:214-216`) like
any other module, so it must pass black, isort and flake8 as well as carrying its banner — adding or
deleting one changes what the lint gate covers, not just what a consumer receives.
`PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md` gains: `check-wheel` compares the
wheel's package data with `git ls-files --cached --others --exclude-standard`
(`devtools/scripts/check-wheel.sh:29-33`), so a package-data deletion cannot pass the wheel surface
before it is staged — a tree whose package-data change is unstaged fails it, with the deletion on
the index still expected and absent from the wheel.

**B6 — hp.py fidelity and hygiene (`R11`, `R13`, `R14`, `R15`, `R16`).** Restore the JS
record-keeping for the two payload shapes `hp.py:352-366` and `:601` drop — the two edits, named:
`except OSError` → `except (OSError, ValueError, TypeError)` at `:365`, and `errors="replace"` on
the append's `open` at `:601`. Deduplicate `USAGE`: the constant (`:1320-1324`) is the home; the
four docstring lines at `:7-10` are cut. Fix the unparseable docstring sentence (`:219-221`). Delete
the four injection seams (`:499`, `:552`, `:586-588`, `:1292`) — no justification exists after B4,
which tests through the launcher and calls none of them. Pin stdin/stdout to UTF-8 at the entry
points (`:1330`, `:1349`, `:1352`, `:1355`). Verify: the differential payload replay from the coder
seat's review — the two shapes now keep their records.

**B7 — the README's profiler sentence (`R21`).** README.md: one sentence naming the activity
profiler — what it records, that the trace lands in `.devpro-temp/harness-profile/`, rendered by the
show-profile skill — as a bullet after `README.md:44`, the requirements list's last bullet. No
interpreter floor and no "(MIT)": the credit line is frozen verbatim by user ruling, and the floor
is a SPEC requirement the user decides.

Declined: **R8** — resolved by landing act 4 (the pipx tag is the hand edit beside the bump);
**R12** — no shipped command reports or cleans the stale copy: `hp.js` appears nowhere in `hp.py`
and `HOOK_FILES = (LAUNCHER, "hp.py", VIEW_TEMPLATE)` (`hp.py:71`) excludes it — `stale_hook`
(`:1283`) compares only those names, so a leftover committed `hp.js` is invisible to `doctor` —
so fixing it means `init` deleting user-owned files or `doctor` growing an inventory, design
questions; input to the next design, whose opencode profiler work touches the same surface;
**R18** — the capture creating the scratch directory is the graceful act for a hook that cannot
stop-and-say-so; the agents-file invariant binds sessions, not hooks (the design states no sentence
about the mkdir — `ACTIVE_DESIGN.md` has no `mkdir` occurrence — so the decline rests on the
behavior, not a quotation); **R22** — the credit line is frozen verbatim by user ruling; naming a
license on it edits frozen text, and the README's acknowledgements list names licenses per
dependency already; **R23** — a stated interpreter floor is a SPEC requirement and needs a user
decision; B1's silence makes the missing statement safe — an old interpreter no-ops silently, the
never-block behavior the design states — so no floor wording in B7; **architect N3** — the
sanitization note; no reachable consequence.

Done-line: `just test` (the full gate, all four surfaces), then `just lint`, then
`just sweep-python`, then `just dev-check-design-deltas-applied` (all four pairs landed), then
`just dev-check-links`, then `just dev-check-plan` — all before the landing acts.

The landing proof: the landing commit's tree carries `just test` (full gate, all four surfaces) and
`just sweep-python` passing. The document checks (`dev-check-design-deltas-applied`,
`dev-check-links`, `dev-check-plan`) run before the deletions, on the pre-landing tree — the landing
commit deletes the plan and review document those checks read, so the pre-landing run is their
proof, not the landing commit's.

The landing acts, after the burndown's work:

1. The landing commit deletes `ACTIVE_DESIGN.md` (not diced, so no tree).
2. The landing commit deletes `ACTIVE_PLAN_REVIEW.md`.
3. The landing commit deletes this plan (`ACTIVE_PLAN.md`) — no next plan exists at that time. The
   deletion is P4's row resolution: no Status row is set, the row dies with the plan.
4. The landing commit bumps the version: `__version__` in `devpro/__init__.py` to `"0.18.0"` — the
   minor bump the profiler's new behavior rates; the plan's approval covers the value and the edit —
   and `README.md`'s pipx tag beside it, per *Version has one home*; the three rendered carriers
   follow from the constant at the next render. Committed before any `just tag`.

Every commit message and pull-request description carries the attribution line the development
skill states:

```
ai assisted by [devpro](https://github.com/benn-herrera/devpro) on opencode. submitter takes full responsibility.
```
