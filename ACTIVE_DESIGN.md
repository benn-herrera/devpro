# ACTIVE DESIGN

## Drafts

### The profiler's capture output moves under the project's scratch directory

Decision (user): the capture output is `.devpro-temp/harness-profile/`, not `.harness-profile/` —
the trace data joins the project's scratch directory, which the project's own convention gitignores.

Facts: the trace directory is `hp.js:17`'s `TRACE_DIR = '.harness-profile'`, resolved
project-root-relative (`:423` picks the project dir, `:416` joins the trace path); the capture
mkdirs it on first write (`:426`) and calls `excludeTraces` (`:427`), which appends
`TRACE_DIR/` to `.git/info/exclude` (`:115-122`) — the exclusion mechanism exists because the old
directory was a convention nowhere. `.devpro-temp/` is the project's scratch by the installed
agents file's invariant, and the guide skill tells the user to gitignore it — so the exclude write
retires with the move: the project's own convention carries the exclusion duty, and the capture's
mkdir already creates the scratch directory when missing. Sites naming the old path:
`claude.py:70` (comment), `show_profile.py:16` (skill text), `SPEC/deployed-surfaces/shipped-files.md:101`,
`ARCHITECTURE/install/harness-profiler.md:23-24` (capture sentence and the exclude sentence).
`init`'s committed-hook path (`.claude/harness-profiler/`) is the hook code, not the trace
directory, and does not move. No test pins `.harness-profile` (grep over `tests/` empty). The
show-profile skill's HTML render already writes `.devpro-temp/harness-profile.html` — consistent
with the new home. Existing consumer traces under `.harness-profile/` are orphaned by the move:
`tree` reads the new directory only; no migration.

Open: none — the exclude write's retirement follows from the guide's gitignore instruction; the
paths are the user's decision.

### The profiler ports from hp.js to hp.py — node leaves the installed surface

Decision (user): the port is approved ("requiring node? F that"); the original author keeps the
acknowledgement — the idea and design were theirs — but the code becomes ours.

Facts: `hp.js` is one file, Node 18+ standard library only, four subcommands (`capture`, `tree`,
`init`, `doctor`); `hp.sh` exists only to find `node` (PATH, `HP_NODE`, volta, nvm, Homebrew) —
python3 is present by definition in every devpro install, so the launcher simplifies to a python3
finder; `guide.py:76` carries the node warning, which retires with the port. The claude-centric
parts port as-is: capture's payload vocabulary, the six events, token counts from claude's
transcripts under `~/.claude/projects/`, `init`'s `.claude/settings.json` merge, `doctor`'s plugin
records. `view.html` is a self-contained template, not runtime code — it ports unchanged. Any
future opencode capture is recreated to fit the opencode plugin's TypeScript rather than preserving
the hp.js surface — no reuse attempt, no schema-cleanliness constraint carried forward.

Costs, stated: the vendoring ends — `ARCHITECTURE/install/harness-profiler.md`'s one-way copy rule
and no-version-stamping describe copied code, and a port makes us owner of all four subcommands and
the render; upstream fixes no longer flow. The README credit line stands verbatim ("whose source
was adapted"). Token-count logic re-implements and re-verifies against claude's transcript format.
Tests pin `_PROFILER_FILES = ("hp.js", "hp.sh", "view.html")` (tests/test_devpro_install.py:409)
and the payload paths move to the ported names.

Open: none — the port's scope is the user's decision; the costs above are facts, not objections.
