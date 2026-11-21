# Stage-2 post-plan review — the profiler absorbed and the stores renamed

Four seats over the stage-2 commits `cf0198c..a6c077b`, each given the project documents and the
design, not the plan. Seat reviews live in `.devpro-temp/stage2-review-{coder,architect,
prompt-engineer,tech-writer}.md`. One ID per defect, naming every seat that reported it.

## R1 — Critical: the guide's source missed the stage-2 pairs entirely. *tech-writer + prompt-engineer*

`guide.py`'s Requirements bullet still gates the `just` 1.33 floor on the kbase component — but the
`devpro` include line is an `import?` on every nested-plugin project install now (the SPEC leaf,
`recipes.md` and README were all corrected; the definition was the one surface the pairs never
covered). Its *Updating* section cites the README's walk, then states a created-Makefile removal the
walk no longer performs (the devpro line lands in that same file) and "deletes `skills/docdicer/`
once" — a path that destroys the just-delivered skill and snippet package, where the README it
cites says delete `skills/docdicer/tools/`. Fix: both guide sections written from the SPEC leaf's
landed statements.

## R2 — Critical: the README's profiler bullet still names the old stores. *tech-writer*

`README.md:45` records a project install to `.devpro-temp/claude-profiler/` and
`.devpro-temp/opencode-profiler/` — the shipped constants are `.profiler-claude`/`.profiler-*`, the
install renames old stores in place, and the show-profile skill the same bullet routes to already
names the new stores. The bullet had no design pair, so no executor or check read it. Fix: the
README bullet from the landed leaf's terms.

## R3 — Critical: the rename migrates any `<name>-profiler` directory, guarded only by accident. *coder*

`profiler/hooks.py`'s `rename_stores` renames any `<name>-profiler` directory under the project
(proven: a `notes-profiler/` migration), and `install.py`'s `_one_project_renamed_once` guards only
its second real run — a plain `install()` on the documented default renames the operator's
directories with no guard, and the rename loses data if an operator named their directory in the
pattern. Fix: the rename's recognition names the two profiler stores (and any store the schema
holds), not any directory shape; the once-per-project guard covers the plain path; a test pins
both.

## R4 — Critical: the absorbed profiler's capture path pays for the renderer. *coder + architect*

`profiler/hooks.py` imports `devpro.context`, `devpro.render` and `devpro.install_base` at module
scope — seventeen devpro submodules for one `rename_stores`, with the renderer's import landing on
the every-tool-call capture path (~20 ms warm) — falsifying the module's own docstring and the
design's lazy-dispatch clause one level below the verb entry. Fix: the rename path's imports move
to the rename call (the dicing precedent's pattern at module level too), the design's Packaging
statement states the capture-path rule for the absorbed module as it states it for the verb entry,
and the two-entry `sys.modules` probe extends to the hooks import.

## R5 — High: P7's leaf rewrite negates the opencode state it rewrote. *architect*

`harness-profiler.md:101-104` claims the opencode install ships no profiler launcher and the
skill's first finder finds nothing there — the code ships it (`install.py:138`'s cross-harness
map; the test at `test_devpro_install.py:1975`) and the landed SPEC sentence states it. Fix: the
leaf's sentence to the code's truth. Its companions: the verbatim CONVENTIONS leaf names a Python
resource the tree no longer holds at all; the leaf's absolute "There is no window…" is refuted by
the design's own collision case.

## R6 — Warning: doctor's remedies cannot do what they say. *coder*

The collision remedy sends the operator to a command that cannot merge, and the straggler remedy
sends them to `install` — which in this repository deliberately does not rename. The live state
proves it: `devpro profiler tree` here reports no traces while `.devpro-temp/claude-profiler/`
sits from 01:34Z. Fix: the remedies state the manual `mv` (the deliberate boundary) and what
merging means for the operator.

## R7 — Warning: the store rename is absent from the human-facing walk. *tech-writer*

No human-facing surface states that the install renames `.devpro-temp/*-profiler/` in place — the
README's upgrade walk states the prune and the retired line but not the rename the operator sees.
Fix: the walk names the rename and its report line.

## R8 — Low notes, recorded for the burndown's judgment

`profiler.ts`'s torn-line comment says "renamed aside" where the routine truncates (coder W-4);
`rename_stores`' parameter shadows `migrate_stores` (coder W-2); `init` copies the `!INSTALLED!`
banner into every repository, and the installed-vs-committed banner distinction is unstated in
CONVENTIONS (coder W-6 + contract gap); `repo-layout.md`'s dicing-snippets row cites
`DICING_SNIPPETS_PACKAGE`, which exists nowhere (PE F3); `show_profile.py`'s *No traces* branch
stops where doctor's `old:` line would name a pre-rename store (PE F4); the README's mage-render
sentence (tech-writer #5); the guide's board section is stage 3's to revisit (tech-writer #6); the
README's upgrade walk doesn't state the include line added or rewritten in an existing runner file
(tech-writer #7); the docstrings in `hooks.py` and `install.py` describing the pre-P1 finder and
stores in historical terms (architect N, carried).

## Declined

The coder's C-1 (`development-tools/**/*` dropped in P1, the wheel omitting `cold-read.sh`) —
declined at synthesis by run: the glob stands at `pyproject.toml:29` and `just check-wheel`
returns 0 on the committed tree. The plancheck chain-drift artifact the executor's earlier report
surfaced — settled in `2425638` and outside this review's range.

## Verified holding across all four seats

The store migration's one-pattern read, skip-and-name collision, and doctor stragglers; the snippet
shape rule and the retired-line cleanup; the re-anchor rule's first application (62 landed, 2
pending = stages 3–4's, 0 drifted); six recipes argumentless with defaults; the `.profiler-*` facts
against `values.py`/`profiler.ts`/`pages.py`; the `hp.sh` finder and every cited name; the
one-program-name rule; 1541 passed, 1 skipped at the floor; the whole gate green on the committed
tree.
