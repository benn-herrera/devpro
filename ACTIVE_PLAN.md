# Active plan — the activity profiler is devpro's own Python, writing into the project's scratch directory

From the accepted design: [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md) — five entries:
[the Shipped files entry](ACTIVE_DESIGN.md#shipped-files) and [the Guide and README
entry](ACTIVE_DESIGN.md#guide-and-readme) under SPEC delta, [the Harness profiler
entry](ACTIVE_DESIGN.md#harness-profiler) and [the Repo layout entry](ACTIVE_DESIGN.md#repo-layout)
under ARCHITECTURE delta — each one passage pair — and [the Harness profiler entry under Code
delta](ACTIVE_DESIGN.md#harness-profiler-1) (prose, no pair; the port package composes from it).
The design is not diced; it is under the plan size limit.

Every package is **shipped**: the whole process, one commit closing each package.

Sequencing: P1, then P2, then P3, then P4. P1 applies the four passage pairs; P2 composes the port
from the Code delta prose; P3 and P4 are the post-plan review and burndown.

Each package's checkpoint gate runs `just test`, then `just sweep-python`. Its `docs` surface is red
for a reason outside this work: the installed launcher pins docdicer `v0.12.0`
(`devpro/docdicer-tools/docdicer:8`, `VERSION=0.12.0`) and the tag is not published, so
`just check-links`'s pip build fails `git checkout -q v0.12.0` (observed run: `error: recipe
'docdicer' failed on line 37`, exit 1). The ROADMAP item
(`ROADMAP.md:58-62`, "The docdicer `v0.12.0` tag is unpublished") resolves it; the item leaves
ROADMAP when the tag is published. The hosted-clone route `just dev-check-links` covers the
document checks meanwhile (observed run: `links checked: 162, broken: 0`, `documents checked: 88,
problems: 0`, exit 0; the clone is dirty and left at `v0.11.2`, reported, not reset —
`devtools/scripts/docdicer-repo.sh` exits 0 on a dirty clone).

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | drafted | mechanical | the four passage pairs applied verbatim: SPEC's profiler paragraph and guide-and-readme requirements bullet, ARCHITECTURE's harness-profiler leaf and repo-layout resources line |
| P2 | drafted | expert | the port: `hp.py` replaces `hp.js`, `hp.sh` finds python3, the trace moves to `.devpro-temp/harness-profile/`, the skill text and tests follow |
| P3 | drafted | expert | Post-plan review |
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
  resources or the hook entries.`); the ARCHITECTURE pair's from-block is the whole leaf
  `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` (46 lines, `wc -l` → 46).
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
3. Apply the ARCHITECTURE pair's becomes-block over the whole leaf in `harness-profiler.md`
   verbatim.
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
(`_PROFILER_FILES` pin becomes `("hp.py", "hp.sh", "view.html")`). `view.html` ports unchanged.

Facts, each re-run before acting on it:

- `hp.js` is 961 lines with four subcommands (`capture`, `tree`, `init`, `doctor` — `hp.js:6-9`);
  `hp.sh` is 54 lines whose whole job is finding node: `HP_NODE` override, `command -v node`,
  `~/.volta/bin/node`, the newest `~/.nvm/versions/node/*/bin/node`, `/opt/homebrew/bin/node`,
  `/usr/local/bin/node` (`hp.sh:13-52`), and where none: `capture` drains stdin and exits 0, other
  subcommands report and exit 1 (`hp.sh:46-51`). The port: `hp.sh` finds `python3` (`HP_PYTHON`
  overrides the search) and runs `hp.py` beside it, keeping the same silent-capture shape.
- The capture's root resolution stays: `projectDir` resolves `gitRoot(start) || start`
  (`hp.js:126-130`), so the trace lands at the project root — only the path under it changes,
  `.harness-profile/` → `.devpro-temp/harness-profile/` (`hp.js:17`, `:416`).
- The `.git/info/exclude` write retires with the move: `excludeTraces` (`hp.js:115-122`) appends
  `TRACE_DIR/` to `info/exclude`; the scratch directory's gitignore convention carries the
  exclusion duty (`.gitignore:22` holds `.devpro-temp/`).
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
  `show_profile.py:22` (`../../libexec/hp.sh`) and `:24` (`.claude/harness-profiler/hp.sh`); hook
  code, not trace data, does not move. The skill body's `mkdir -p .devpro-temp` (`:38`) and page
  path `.devpro-temp/harness-profile.html` (`:40`) already write the scratch directory and stay.
- The registration wiring keeps its shape: `devpro/harnesses/claude.py:72-73` names
  `_PROFILER_SCRIPT = "libexec/hp.sh"` and the command
  `sh "${CLAUDE_PLUGIN_ROOT}/libexec/hp.sh" capture claude` — hp.sh keeps its name, so the wiring
  is unchanged; only the comment at `:69-71` moves to the new trace path and drops the node
  phrasing.
- The install's resource discovery is a glob (`devpro/install.py:196-201`, `source.rglob("*")` over
  `harnesses/resources/<harness>/`), so adding `hp.py` and deleting `hp.js` needs no install.py
  change; the copy follows the directory.
- The tests pinning the profiler: `tests/test_devpro_install.py:409` (`_PROFILER_FILES`), `:464`
  (payload landing), `:473` (`os.access(libexec / "hp.sh", os.X_OK)` — hp.sh keeps its name),
  `:1873` (no-opencode-copy). Updating `:409` is in scope; the others pass unchanged.
- The banner rule binds every harness resource: `hp.py` carries
  `# !INSTALLED! from devpro/harnesses/resources/claude/libexec/hp.py — ...` within its first ten
  lines — Python comment syntax; the banner test
  (`tests/test_devpro_install.py:1788-1795`) checks only the `!INSTALLED! from <origin>` text, not
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
   write, the `!INSTALLED!` banner in its first ten lines.
2. Rewrite `hp.sh`'s finder: python3 (`HP_PYTHON` overrides), `capture` drains stdin and exits 0 on
   a missing interpreter, other subcommands report and exit 1; the header comment names python3 and
   hp.py.
3. Update `devpro/harnesses/claude.py:69-71`'s comment; update `show_profile.py:16`; retire
   `guide.py:76-77`'s node warning and `README.md:45`'s; update `tests/test_devpro_install.py:409`.
4. Delete `hp.js`.

Done-line: `just test devpro`, then `just test wheel`, then `just sweep-python`, then
`just dev-check-design-deltas-applied` (all four pairs still landed), then `just dev-check-links`. One
commit closes the package.

## P3 — Post-plan review

The reviewers are given the project documents and the design, not the plan, and review the changes
and their tests against the project's standards and fitness for purpose. Each writes their own
review in the scratch directory, independently; the session synthesizes them into
`ACTIVE_PLAN_REVIEW.md`, never diced, de-duplicating findings and reconciling them into one account.

- `devpro-architect` — the port's shape against ARCHITECTURE.md (the amended harness-profiler leaf
  and the amended repo-layout leaf, both as P1's pairs landed them) and the definition modules'
  structure;
- `devpro-prompt-engineer` — the show-profile skill's text and the guide's retired warning
  (model-facing text changed);
- `devpro-tech-writer` — README.md:45's retirement and the credit line standing verbatim;
- the Python coder — `hp.py` and `hp.sh` against the project's coding standards.

Done-line: `just dev-check-links`. The review document and P3's Status row land in P3's commit.

## P4 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands. This section holds only that
until then.

The landing acts, after the burndown's work:

1. The landing commit deletes `ACTIVE_DESIGN.md` (not diced, so no tree).
2. The landing commit deletes `ACTIVE_PLAN_REVIEW.md`.
3. The landing commit deletes this plan (`ACTIVE_PLAN.md`) — no next plan exists at that time.

Done-line: `just test devpro`, then `just sweep-python`, then
`just dev-check-design-deltas-applied` (all four pairs landed), then `just dev-check-links`, then
`just dev-check-plan`. `just test`'s `docs` surface fails as the header states; every other surface
passes.

Every commit message and pull-request description carries the attribution line the development
skill states:

```
ai assisted by [devpro](https://github.com/benn-herrera/devpro) on opencode. submitter takes full responsibility.
```
