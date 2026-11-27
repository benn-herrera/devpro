# ACTIVE PLAN

# The project's name leads the dashboard, the development skill survives a compaction, the retired path is deleted

Written from [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), its six entries cited per package below. Every
package's work is shipped-lifetime code; the whole process applies. Each package closes in exactly
one commit; the closing commit carries a body and the attribution line (*Commits and pull requests*,
the development skill). The checkpoint gate is `just test`, then `just lint`, then `just
sweep-python` (CONVENTIONS, [The
gates](PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md)) — run once, before the
checkpoint commit, never between edits. Run order is serial, P1 → P2 → P3 → P4 → P5 → P6: the
packages share the tree. P4 precedes P5 because P5 writes hook names only what the pinned host declares may give it,
and P4 is the run that reads and records them.

The design's delta application is verified by `just dev-check-design-deltas-applied`; the check has
no subset mode — it exits 1 whenever any pair has not landed. The design states six pairs and two
no-pair entries: ACTIVE_DESIGN.md :20, :41 and :60 — SPEC [Shipped
files](ACTIVE_DESIGN.md#shipped-files), landed by P1; :91 — [Serving](ACTIVE_DESIGN.md#serving),
landed by P1; :110 — [Opencode entry](ACTIVE_DESIGN.md#opencode-entry), landed by P1; :138 — [The
page template and its
presentation](ACTIVE_DESIGN.md#the-page-template-and-its-presentation), landed by P1; [What removes
the retired path](ACTIVE_DESIGN.md#what-removes-the-retired-path), a whole leaf with no pair,
removed by P6; [Serving, The index](ACTIVE_DESIGN.md#serving-the-index), a code-delta entry with no
pair, closed by P3. The two no-pair entries are witnessed by P3's and P6's done-lines, and the
design's delta application is complete when both have landed.

No row below is `dispatchable` yet: each package still owes its `devpro-prompt-engineer` usability
review and `devpro-architect` revision (*Dispatchability*), which run after this draft returns.

## Status

| Package | State | Rating |
| --- | --- | --- |
| P1 | landed | mechanical |
| P2 | landed | expert |
| P3 | landed | expert |
| P4 | dispatchable | expert |
| P5 | dispatchable | expert |
| P6 | dispatchable | mechanical |
| PR | dispatchable | expert |
| PB | dispatchable | expert |

### P1 — the paired deltas applied to the project documents

Intended lifetime: shipped. Rating: mechanical.

Scope: the design's paired entries, each applied verbatim apart from relative links rebased to the
destination leaf — `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md` (three pairs: the nav's
text, the nav's grammar, the compaction-reload sentence in the opencode paragraph; [Shipped
files](ACTIVE_DESIGN.md#shipped-files), ACTIVE_DESIGN.md :20, :41, :60);
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md` (one pair, the nav's text; [Serving](ACTIVE_DESIGN.md#serving), :91);
`PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md` (one pair, the compaction reload; [Opencode
entry](ACTIVE_DESIGN.md#opencode-entry), :110);
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-page-template-and-its-presentation.md` (one pair,
the project-name slot in the index template's deco; [The page template and its
presentation](ACTIVE_DESIGN.md#the-page-template-and-its-presentation), :138). Six pairs in all.
Not in scope: the two no-pair entries — the retired-path leaf stands until P6 deletes it, and the
index script's helper until P3.

Fact (run): `just dev-check-design` answers `entries: 6, problems: 0`; `just
dev-check-design-deltas-applied` answers `pairs: 6, landed: 0, pending: 6, drifted: 0, conflicting:
0, problems: 0`, one `pending` line per pair at ACTIVE_DESIGN.md lines 20, 41, 60, 91, 110, 138 —
every from-text matches its target as the design stands.

After each pair's application — not after all six — the doc-set search for the replaced wording
(`git grep -l '<the replaced phrase>'
-- PROJECT_DOCS`, then the rule in its other phrasings) and a read of each hit (CONVENTIONS, [A
delta application ends by searching the doc
set](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-by-searching-the-doc-set.md)).
A statement the application leaves false outside these four leaves is reported to the session, not
rewritten here; a hit inside `serving.md` or `opencode-entry.md` that the leaf's own pair already
replaces needs no second edit.

In-scope tests: none — document only. Done-line: `just dev-check-links`, `just
dev-check-design-deltas-applied` — run at this package's end, exit 0 with `pairs: 6, landed: 6,
pending: 0, drifted: 0, conflicting: 0, problems: 0`.

### P2 — the project name leads the nav and the profiler titles

Intended lifetime: shipped. Rating: expert.

Outcome: on every page the dashboard serves, the served project's name opens the nav, bold in the
foreground color; the `devpro` brand stands at the nav's far edge, past the server block, behind a
hairline separator, where it cannot read as the stop's label; the profiler pages' titles read
`<project>: devpro profiler <page-name>` — `sessions` on the index, `session` on a session's page —
the project named as the board's title names it ([Shipped
files](ACTIVE_DESIGN.md#shipped-files), [Serving](ACTIVE_DESIGN.md#serving), [The page template and
its presentation](ACTIVE_DESIGN.md#the-page-template-and-its-presentation)).

Scope: `devpro/profiler/pages.py` — the `INDEX` template's nav and title (:1006), the project
name's strict-fill mark and its fills through `index_html`, `_rendering`, `render_html`, `page_for`
and `served_page` (the serve path filling the served project's name, the standalone render the
project it renders for); `devpro/profiler/view.html` — the nav (:39) and the title (:4);
`devpro/kanban/assets/index.html` — the nav's project-name element; `devpro/kanban/assets/board.js`
— the fill in `render` from the payload's project field; `devpro/kanban/assets/board.css` — the
nav grammar:
the project name's rule, the brand's demotion to the far edge, the separator. The approved visual
treatment is the design's; the scratch mock at `.devpro-temp/nav-mock/index.html` (gitignored) is a
reference, never a spec.

Facts (quoted):

- `devpro/kanban/server.py:174` — `"project": os.path.basename(self.root),` — the board's payload
  already carries the project name; the nav's fill is a new reader of that field, no server change.
- `devpro/kanban/assets/board.js:133-135` — `const title = \`${payload.project} kanban\`;`
  `document.title = title;` `$("page-title").textContent = title;` — the board's title already
  leads with the project and is unchanged by this package.
- `devpro/kanban/assets/index.html:10-21` — the board page's nav is static HTML, the brand
  `<span class="brand">devpro</span>` first; the project name is filled by the script, the page
  carrying the element.
- `devpro/profiler/view.html:39` and the `INDEX` template (`devpro/profiler/pages.py`, nav at the
  template's head) — the profiler pages' nav is the templates' own text, brand first; the design
  makes the project name a strict-fill mark there, so the strict-fill tests must walk the new mark.

Fact (run): `just test devpro tests/profiler/test_page_data.py tests/dashboard/test_server.py`
answers `93 passed` in 8.76s on the tree carrying the uncommitted title strings — no test references
the title text.

Fact (run): `git diff -U0 devpro/profiler/pages.py devpro/profiler/view.html` answers the two
`<title>` lines below — the tree carries an uncommitted two-string change:
`devpro/profiler/pages.py:1006` and `devpro/profiler/view.html:4` read `devpro — profiler:
sessions` / `devpro — profiler: session` (was `devpro — profiler view: …`). The design's
`<project>: devpro profiler <page-name>` format supersedes it; this package's closing commit
carries the strings and their replacement.

Reference search (run) — every referencing file of the fill path the package may change (where the
project name becomes a parameter or argument of these functions, each is in scope to update):
`git grep -n "served_page\|index_html\|page_for\|render_html\|profiler_page" -- devpro tests`
answers `devpro/dashboard/server.py:16,83,91,95,158,181` (the callers at :158 and :95),
`tests/profiler/conftest.py:48,1665,1800,2103,2109,2112`, `tests/profiler/test_fill.py:15,30,36,39`,
`tests/profiler/test_page_data.py:18,128`, `tests/profiler/test_served.py:193`,
`tests/dashboard/test_server.py:578` (docstring mention). No file outside this list imports the
fill path.

The tests pinning the behavior this package changes, all in scope to update:
`tests/dashboard/test_server.py:511` (`test_the_profiler_view_carries_its_nav_and_no_legend` —
asserts the nav's text), `:533` (`test_every_profiler_view_page_renders_the_way_the_file_flow_renders_it`
— the two carriers' agreement, the nav's shape and no unfilled mark), `:591`
(`test_the_board_page_holds_its_deco_once_and_the_nav_supplies_it`), `:578`
(`test_the_served_pages_link_a_shared_layer_whose_bytes_are_the_one_homes`);
`tests/profiler/test_fill.py:21` and `tests/profiler/conftest.py:2094`
(`test_the_strict_fill_refuses_unknown_and_unfilled_marks_and_leaves_none_standing` — the
project-name mark is added to the tuple of marks asserted absent, and the fill that hands it is
added wherever the fills are assembled), `tests/profiler/test_served.py:193`
(`test_the_served_page_is_the_html_the_file_flow_writes`). A test failing on behavior this package
does not state it changes is reported as a finding, never edited to pass.

The tests this package adds, each naming the defect it fails on by the test-precondition clause:

- the served index and a served session page carry the project name in the nav's opening slot, and
  the index's and the session page's `<title>` read `<project>: devpro profiler …` — fails on a
  served page whose nav opens with the brand or whose title names no project: the operator with
  several dashboard windows open cannot tell whose records each shows;
- `devpro/kanban/assets/index.html` carries the project-name element and `board.js`'s `render`
  fills it from `payload.project` — fails on a board page whose nav's project slot stands empty:
  the fill the board's payload carries is dropped on the board page.

In-scope fixtures: the dashboard `serve` fixture (no change expected) and the profiler conftest's
serve helpers. Done-line: `just test devpro`, `just test wheel`, `just lint`.

### P3 — the index's script gets the helper it calls

Intended lifetime: shipped. Rating: expert.

Outcome: the profiler index's feed draws — the script that renders the entries `/api/traces`
answers runs to its end instead of dying on its first row ([Serving, The
index](ACTIVE_DESIGN.md#serving-the-index)).

Scope: the `INDEX` template's script in `devpro/profiler/pages.py`; the helper is defined in the
script's own definition — where `view.html:63` already defines the same helper in the session
template's script — not in the shared presentation layer, whose deco publishes exactly one name,
`globalThis.devproFormat`.

Facts (quoted): `devpro/profiler/view.html:63` — `const clip = (t, n) => (t.length > n ?
t.slice(0, n - 1) + '…' : t);` — the helper's only definition, inside the session template's script;
`devpro/profiler/pages.py:1147` — `stampCell`'s body calls `clip(value, chars)` and the `INDEX`
defines `clip` nowhere; the scripts' IIFEs share nothing (ARCHITECTURE, The page template and its
presentation, The scripts and `globalThis.devproFormat`), so the call raises
`ReferenceError: clip is not defined` while drawing a row and the feed renders none.

The test this package adds, in `tests/profiler/test_page_data.py`, naming the defect it fails on:
every helper the `INDEX` script calls is defined by that script or published by the deco's
`globalThis.devproFormat` — a static read of `index_html()`'s script against what it defines and
against `deco.js`'s published names; it fails on exactly the defect
above, a page whose feed draws no rows because a helper stands undefined.

Done-line: `just test devpro`, `just lint`.

### P4 — the pinned host's compaction declarations read and recorded

Intended lifetime: shipped (its product steers shipped code). Rating: expert.

Outcome: what the pinned host declares for a compaction — the hook event's name, the output fields
its reference accepts, and where its context lands — is known from the host's published
declarations and recorded as P5's fact, read and never assumed (CONVENTIONS, [A hook contract is
read, not
assumed](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-hook-contract-is-read-not-assumed.md)).

Scope: read-only over the pinned declarations. `package.json:6` pins the host surface:
`"@opencode/plugin": "2.4.1"`; the declarations stand under `node_modules/@opencode/plugin/`, the
tree `just lint`'s `_js-deps` installs frozen. No source, test or build file changes. The one
tracked edit is this plan: P5's fact block below filled with the read's command and its answer;
raw excerpts go to `.devpro-temp/compaction-hooks/` (scratch).

The read: search the declarations' type surface for the compaction and context events (`grep -rn
"compact" node_modules/@opencode/plugin/dist --include='*.d.ts'`; the first hits are
`dist/effect/session.d.ts:52` and `:65`), read each candidate event's declaration whole, and record
the three answers as three lines — `event: <name>` / `accepted: <field>, <field>` / `lands:
<where>` — each with its `file:line`. What the read tells apart: a hook is a name `ctx.tool.hook`
or `ctx.session.hook` accepts; `SessionRequestKind` and `SessionCompaction` are a request shape
`ctx.session.compact` takes, not a hook. Where the host declares no compaction hook, that is the
answer.

In-scope tests: none. Done-line: `just dev-check-links` (the plan is the package's one tracked
edit).

### P5 — the development skill's reload after a compaction

Intended lifetime: shipped. Rating: expert.

Outcome: given P4's answer, an opencode session whose context held the `devpro-development` skill
keeps it through a compaction: the hook the host gives a compaction records the session's marker —
that its context held the skill — and the injection that follows the compaction re-delivers the
skill's invocation, `@devpro-development`, where the marker stands ([Opencode
entry](ACTIVE_DESIGN.md#opencode-entry); the SPEC sentence P1 landed, [Shipped
files](ACTIVE_DESIGN.md#shipped-files) :60).

Fact (run, recorded here by P4): three lines — `event: <name>` / `accepted: <field>, <field>` /
`lands: <where>` — each with its declaration `file:line`. This package writes no hook name P4's
answer does not give; the name is the host's published declarations' to give, and until P4's run
the design's compaction premise stays unsettled. Where P4's answer is that the host declares no
compaction hook, this package returns to the session with the design's premise unmet rather than
wiring an assumed name.

Scope: `devpro/harnesses/resources/opencode/index.ts` — the compaction hook and the follow-up
injection, beside the reminder's two hooks; `tests/test_opencode_entry.py`;
`tests/opencode_entry_runner.ts`; `tests/opencode_plugin_stub.ts`. The stub replaces only
`@opencode/plugin`'s `Plugin.define`; what the new hook reads is a field the runners declare
themselves, and a change to what the code reads is a change to the runners' declared contexts, in
this change (CONVENTIONS, A hook contract is read, not assumed).

Reference search (run) — the test doubles' referencing files and the synthetic record:
`git grep -n "opencode_plugin_stub\|opencode_entry_runner\|synthetics" -- tests` answers
`tests/opencode_entry_runner.ts:3,9,21,131,168,216`, `tests/guardrail_ts_runner.ts:10`,
`tests/profiler/profiler_banner_runner.ts:11`, `tests/profiler/profiler_contract_runner.ts:19`,
`tests/profiler/profiler_digest_runner.ts:12`, `tests/profiler/profiler_mask_runner.ts:7`,
`tests/profiler/profiler_serialize_runner.ts:8`, `tests/profiler/profiler_stamp_runner.ts:10`,
`tests/test_opencode_entry.py:31` (`_RUNNER`), `:172,232,262,300` (`synthetics`). The guardrail and
profiler runners import the stub only; they change only where the stub's pass-through shape does.

The tests pinning the behavior this package must not disturb, in scope to verify:
`tests/test_opencode_entry.py:112`
(`test_the_opencode_entry_registers_and_reloads_what_the_plugin_holds`), `:240`
(`test_the_gate_is_the_plan_file_or_tree_and_silent_for_a_design_or_nothing`), `:281`
(`test_both_harnesses_inject_one_sentence` — the reminder's one-sentence shape survives the third
hook). A third hook that also injects a synthetic changes no assertion in these, but the runner
records each synthetic with its firing event (`synthetics`, the runner's header), so any test
reading `synthetics` for a session may see one more — `:172`, `:232`, `:262` and `:300` above. A
test failing on behavior this package does not state it changes is reported as a finding,
never edited to pass.

The tests this package adds, each naming the defect it fails on by the test-precondition clause:

- a session whose context held the skill goes through a compaction, and the invocation
  `@devpro-development` is re-delivered once the compaction ends — fails on a compaction that
  drops the skill's text and restores nothing, the session continuing without the development
  process;
- a session whose context held no marker injects nothing at the compaction's end — fails on an
  injection keyed to every compaction, the skill forced on sessions that never carried it;
- a session whose context held the skill goes through a second compaction, and the invocation is
  re-delivered again — fails on a marker that latches the first compaction's delivery and silences
  every later one: the session's second compaction leaves it running without the development
  process though its context held the skill at it, a surface no single-compaction test reaches.

Done-line: `just test devpro`, `just lint` — lint type-checks the entry against the pinned
declarations; it does not check a hook's name string — that is P4's answer's job only.

### P6 — the retired-path machinery deleted

Intended lifetime: shipped. Rating: mechanical.

Outcome: `profiler init` carries no retired-path machinery — the launchers' constants, the unlink
logic and the retired-command recognition are gone — and the ARCHITECTURE leaf that described it is
deleted with its listings ([What removes the retired
path](ACTIVE_DESIGN.md#what-removes-the-retired-path)).

Scope, every edit enumerated: `devpro/profiler/hooks.py` — the constants `RETIRED_LAUNCHERS`,
`RETIRED_HOOK_FILES`, `RETIRED_SKILL` (:42-46) with their comments; `OLD_HOOK_COMMANDS` (:74-78)
with its comment; `_OUR_COMMAND_SPELLINGS` (:81-85) deleted whole — the search below shows nothing
reads it; `is_recognized_command`'s `*OLD_HOOK_COMMANDS` arm (:111); the docstrings and comments
naming "an older launcher" (:40-41, :109-110, :115); `merge_hooks`' docstring line naming "an
older `init`" (:139 — "An entry an older `init` wrote is replaced in place, so a re-run picks up
new hook options.", the replace-in-place behavior the `*OLD_HOOK_COMMANDS` arm drives);
`init`'s retired unlink block, the
retired-skill unlink and the `retired_dirs`/`retired` entries in the staged-path list (:202-218).
`tests/profiler/test_init.py` — the import at :10 and three tests deleted: :18
(`test_init_clears_an_older_runs_launcher_and_files`), :42
(`test_init_renames_a_committed_hook_written_under_a_launcher_name`, named by the user's ruling),
:131 (`test_init_removes_the_skill_an_older_init_rendered_under_its_former_name`).
`tests/profiler/conftest.py` — the import at :31 and two tests deleted: :1228 and :1252, uncollected
twins of :18 and :42 (pytest collects no test functions from a conftest). No test replaces them:
the job is removed, nothing is left to prove. `PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-install-renders-and-copies.md`
— its :7 sentence pointing at the leaf this package deletes ("What it removes is *What removes the
retired path*, below.") deleted with the leaf it names.

Consequence stated, not decided: a settings entry whose hook command spells a retired launcher is
no longer recognized as this tool's — `foreign_hook_command` reports it and `init` refuses naming
it, where before the run replaced the entry in place. The deleted leaf's closing sentence ("A hook
command spelling a retired launcher stays this tool's: `hooks.is_our_command` recognizes it, and
an `init` re-run replaces it.") is the removed statement. No test is
edited to hide the refusal.

Reference searches (run), every hit in this package's scope:

- `git grep -n 'RETIRED_LAUNCHERS\|RETIRED_HOOK_FILES\|RETIRED_SKILL'` answers
  `devpro/profiler/hooks.py:42,44,46,77,82,203,208`, `tests/profiler/test_init.py:10,17,29`,
  `tests/profiler/conftest.py:31,1227,1239`, and the deleted leaf
  `PROJECT_DOCS/ARCHITECTURE/harness-profiler/what-removes-the-retired-path.md:6`.
- `git grep -n "OLD_HOOK_COMMANDS"` answers `devpro/profiler/hooks.py:76,84,111` only.
- `git grep -n "_OUR_COMMAND_SPELLINGS"` answers `devpro/profiler/hooks.py:81` only — defined,
  never read.

The leaf and its listings: `PROJECT_DOCS/ARCHITECTURE/harness-profiler/what-removes-the-retired-path.md`
deleted, and both listings naming it removed in the same change —
`PROJECT_DOCS/ARCHITECTURE/harness-profiler/index.md:18` and `PROJECT_DOCS/ARCHITECTURE/entry-point.md:30`
(CONVENTIONS, [A renamed leaf takes its contents
entries](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-renamed-leaf-takes-its-contents-entries.md)).

Doc-set search (run) for the removed rule's wording: `git grep -n "hp\.sh\|show-profile\|profiler\.sh\|retired launcher\|retired path" -- PROJECT_DOCS`
answers hits inside the leaf this package deletes, its two listings above, and
`the-install-renders-and-copies.md:7` — the cross-reference in scope above. A hit this search
finds at execution time outside these is reported to the session, never
rewritten here.

In-scope tests beyond the deletions: the surviving `init` suite — `tests/profiler/test_init.py:83`
(the opencode-shaped refusal), `:165` onward (the store renames) — must pass unedited. Done-line:
`just test devpro`, `just dev-check-links`, `just dev-check-design-deltas-applied`, `just lint`.

## PR — Post-plan review

Intended lifetime: shipped (it reviews shipped work). Rating: expert.

The post-plan reviewers are the agent for each domain the plan changed substantively — here, the
coder for Python (`devpro/profiler/pages.py`, `devpro/profiler/hooks.py`, the dashboard and kanban
suites), the coder for TypeScript (`devpro/harnesses/resources/opencode/index.ts` and the opencode
test doubles), `devpro-architect` (the structure and the applied leaves), and
`devpro-prompt-engineer` (the project documents' claims about the code). P4 ships no code and no
document; its read is reviewed by no seat, and its only artifact is the plan's fact block. They are
given the project documents and [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), not the plan — the reviewers
of P5's work are also given P4's fact block, the design deferring the hook's name to it — and
review the changes and their tests against the project's standards and fitness for purpose. Each
reviewer writes their own review in the scratch directory, independently — each reviewer's report
file present in `.devpro-temp/`, its entries grouped by root cause; the session synthesizes
the reviews into `ACTIVE_PLAN_REVIEW.md`, one entry per defect naming every seat that reported it,
de-duplicating without waiting for an approval between the last report and the write-up. This
package's row is `landed` in the commit that adds the review
document; `just dev-check-plan` is the row-update check that commit's status edit runs, not a check
of the review document, which carries no machine check.

Done-line: the four seats' report files are in `.devpro-temp/`, each grouped; `ACTIVE_PLAN_REVIEW.md`
exists, committed, its entries naming their seats.

## Post-plan burndown

### PB Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands.
