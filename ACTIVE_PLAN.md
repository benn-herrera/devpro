# ACTIVE PLAN

# The project's name leads the dashboard, the development skill survives a compaction, the retired path is deleted

Written from [ACTIVE_DESIGN.md](ACTIVE_DESIGN.md), its six entries cited per package below. Every
package's work is shipped-lifetime code; the whole process applies. Each package closes in exactly
one commit; the closing commit carries a body and the attribution line (*Commits and pull requests*,
the development skill). The checkpoint gate is `just test`, then `just lint`, then `just
sweep-python` (CONVENTIONS, [The
gates](PROJECT_DOCS/CONVENTIONS/planning-and-execution/the-gates.md)) — run once, before the
checkpoint commit, never between edits. Run order is serial, P1 → P2 → P3 → P4 → P5 → P6 → P7: the
packages share the tree. P4 precedes P5 because P5 writes hook names only what the pinned host declares may give it,
and P4 is the run that reads and records them; P7 reads its hook's name from the same declarations
(`session.d.ts:199`), after the live test it stands behind.

The design's delta application is verified by `just dev-check-design-deltas-applied`; the check has
no subset mode — it exits 1 whenever any pair has not landed. The design states ten pairs and two
no-pair entries: ACTIVE_DESIGN.md :20, :41 — SPEC [Shipped
files](ACTIVE_DESIGN.md#shipped-files), landed by P1; the entry's third pair, :60, revised and
landed by P7; the entry's fourth pair, added by B4 and revised by B5; :111 — [Serving](ACTIVE_DESIGN.md#serving), landed by P1, revised by B5;
:132 — [Opencode
entry](ACTIVE_DESIGN.md#opencode-entry), landed by P1, revised and re-applied by P7, revised by
B5; :189 — [The page template and its
presentation](ACTIVE_DESIGN.md#the-page-template-and-its-presentation), landed by P1, revised by
B5; B5's two added pairs, in the same two leaves — the Opencode entry's Contexts bullet and the
template leaf's board-page paragraph; [What removes
the retired path](ACTIVE_DESIGN.md#what-removes-the-retired-path), a whole leaf with no pair,
removed by P6; [Serving, The index](ACTIVE_DESIGN.md#serving-the-index), a code-delta entry with no
pair, closed by P3. The two no-pair entries are witnessed by P3's and P6's done-lines, and the
design's delta application is complete when both have landed. The revised pairs — the Shipped
files entry's third pair and the Opencode-entry pair — carry the P7 decision: the re-activation
rides the session's next prompt, the host's own attachment path, the idle mention injection the
live compaction test found inert deleted — and P7 applies the revised text.

P7 owes its `devpro-prompt-engineer` usability review and `devpro-architect` revision
(*Dispatchability*); P1–P6 are landed and owe neither; PR is landed, PB's drafting is in
progress.

## Status

| Package | State | Rating |
| --- | --- | --- |
| P1 | landed | mechanical |
| P2 | landed | expert |
| P3 | landed | expert |
| P4 | landed | expert |
| P5 | landed | expert |
| P6 | landed | mechanical |
| P7 | landed | expert |
| PR | landed | expert |
| PB | landed | expert |
| B1 | landed | expert |
| B2 | landed | expert |
| B3 | landed | mechanical |
| B4 | landed | expert |
| B5 | landed | expert |
| B6 | landed | expert |
| B7 | landed | mechanical |
| B8 | landed | mechanical |
| B9 | landed | expert |

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

P4's answer. The read ran `grep -rn "compact" node_modules/@opencode/plugin/dist
--include='*.d.ts'` over the pinned `@opencode/plugin` 2.4.1 declarations (first hits
`dist/effect/session.d.ts:52` and `:65`); raw excerpts in `.devpro-temp/compaction-hooks/`:

- `event: compaction` — the hook `ctx.session.hook` accepts is `"compaction"`,
  `dist/effect/session.d.ts:201` (`readonly compaction: SessionCompaction` in `SessionHooks`,
  reached through `SessionDomain`'s `hook: ModelHooks<SessionHooks>` at `:215`), the line-identical
  `dist/promise/session.d.ts:201` beside it; `SessionRequestKind`'s `"compaction"` member (`:65`)
  stays a request kind, not a hook, as P4's text above warns.
- `accepted: result (summary, native, metadata, tokens)` — the hook callback returns `void`
  (`dist/effect/registration.d.ts:10`, `dist/promise/registration.d.ts:9`), so output is set on the
  hook's input: `result`, the `SessionCompactionResult` the compaction replays
  (`dist/effect/session.d.ts:53`, fields at `:44`–`:50`), beside the inherited mutable context
  fields `system`, `messages`, `options` (`:33`–`:35`) and `tools` (`:39`–`:42`).
- `lands: before the compaction's model request` — the hook's context is the pre-compaction
  context, and the `result` it sets becomes the compaction the session resumes from, skipping the
  model request (`dist/effect/session.d.ts:52`); no declared hook fires when the compacted context
  resumes.

Each answer's authority sits in the pinned host's published declarations,
`node_modules/@opencode/plugin/dist/effect/session.d.ts` with the line-identical
`dist/promise/session.d.ts` twin and the hook signatures' `void` callback returns in
`dist/effect/registration.d.ts:10` and `dist/promise/registration.d.ts:9` — which for P5's
implementation choice means the hook name is `"compaction"` as above, the marker is read from the
hook's pre-compaction context, and the re-delivery of `@devpro-development` must be carried in the
`result` that context lets the hook set (the compaction the session resumes from), because the
declarations give no hook that fires when the compacted context resumes.

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

### P7 — the compaction's re-activation rides the session's next prompt

Intended lifetime: shipped. Rating: expert.

Outcome: an opencode session whose context held the `devpro-development` skill keeps it through a
compaction: the compaction hook records the session's marker as P5 landed it, and the session's
next prompt — the `prompt` hook — carries the skill attached to its `skills`, the host's own
activation path, so the host activates the skill with that exchange ([Shipped
files](ACTIVE_DESIGN.md#shipped-files), [Opencode entry](ACTIVE_DESIGN.md#opencode-entry), the
revised pairs). The live test that ran before the review — an opencode session on the updated
install compacted with the skill in context; the record at
`.devpro-temp/compaction-hooks/raw-observation.md`, with the operator's account — delivered the
injection as a bare `@devpro-development` with no skill content: the host never expands a mention
in a synthetic message, and a synthetic can never *be* an activation, whose message type the
synthetic input does not carry. The idle mention injection P5 landed is inert, and this package
replaces its leg.

Facts (quoted, the pinned host's published declarations):

- `node_modules/@opencode/plugin/dist/effect/session.d.ts:199` — `readonly prompt: SessionPrompt;`
  — the hook name `"prompt"` stands in `SessionHooks`, reached through `SessionDomain`'s
  `hook: ModelHooks<SessionHooks>` (`:215`).
- `node_modules/@opencode/plugin/dist/effect/session.d.ts:16` — `prompt:
  Types.DeepMutable<PromptInput.Prompt>;` — the prompt hook's input is deep-mutable, and the hook
  callbacks return `void` (`dist/effect/registration.d.ts:10`, P4's read), so mutation is the
  output.
- `node_modules/@opencode/client/dist/effect/api/api.d.ts:249` — `readonly skills?:
  ReadonlyArray<PromptInput.SkillAttachment> | undefined;` in `SessionPromptInput` (`:243–255`) —
  a prompt input carries skill attachments.
- `node_modules/@opencode/schema/dist/prompt-input.d.ts:34-45` — `SkillAttachment` is
  `{ readonly id: Schema.brand<Schema.String, "Skill.ID">, mention?: { start, end, text } }` — the
  shape a parsed mention becomes; the id is the brand, `Skill.ID` the prose gloss.
- `node_modules/@opencode/schema/dist/session-message.d.ts:542-555` — a skill activation is a
  session message `type: "skill"` with typed `skill` and `name` fields;
  `SessionSyntheticInput` (`node_modules/@opencode/client/dist/effect/api/api.d.ts:269-279`) has
  no type field — the synthetic vehicle is closed, this package's premise.

Scope: `devpro/harnesses/resources/opencode/index.ts` — the delivery leg P5 added deleted whole,
`index.ts:235–240` (the `experimental.idle` that consumes the marker and sends the
`@devpro-development` synthetic) with `deliverSkill` (:219–230); the reminder's idle hook
(:204–212) stands untouched. The `prompt` hook added: on a prompt whose session id stands in the
marker set — the set the compaction hook (`index.ts:231–234`) adds to, cleared by the prompt
hook's delivery and by nothing else — the hook appends the development skill to the prompt's
`skills`, the id resolved from the plugin's skill domain
(`node_modules/@opencode/plugin/dist/effect/plugin.d.ts:55`; the domain at
`dist/effect/skill.d.ts:12–15`, the editor its `transform` hands at `:5–11`), matched to the skill
the marker names, never hardcoded; a lookup that matches no skill reports and appends nothing.
The compaction hook and its marker set stand as P5 landed them. `tests/test_opencode_entry.py` —
the P5 delivery tests rewritten for the attachment, each naming its defect below;
`tests/opencode_entry_runner.ts` — the runner declares the prompt hook's context and its `skill`
double gains `list()`, a change to what the code reads being a change to the runners' declared
contexts, in this change (CONVENTIONS, [A hook contract is read, not
assumed](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-hook-contract-is-read-not-assumed.md));
`tests/opencode_plugin_stub.ts` — only where the pass-through shape does.

Reference search: `git grep -n "opencode_plugin_stub\|opencode_entry_runner\|synthetics" -- tests`
— the P5 block's search, re-run at execution, every hit outside the four files above reported to
the session. The search that survives this package's change and states its own scope:
`git grep -n "synthetics" -- tests/test_opencode_entry.py`, re-run after the rewrite, every hit in
the rewritten tests' scope in this package's scope — the reader the deletion removes
(`filter injected["text"] == "@devpro-development"`) is gone, so no pre-change line list is
restated here. The guardrail and profiler runners import the stub only and change only where the
stub's pass-through shape does.

The tests pinning the behavior this package must not disturb, in scope to verify:
`tests/test_opencode_entry.py:112`
(`test_the_opencode_entry_registers_and_reloads_what_the_plugin_holds`), `:240`
(`test_the_gate_is_the_plan_file_or_tree_and_silent_for_a_design_or_nothing`), `:281`
(`test_both_harnesses_inject_one_sentence`), and the profiler runners named above. A test failing
on behavior this package does not state it changes is reported as a finding, never edited to pass.

The tests this package changes and adds, each naming the defect it fails on by the
test-precondition clause:

- a session whose context held the skill goes through a compaction, and the session's next prompt
  carries the skill in its `skills` — fails on a prompt hook that attaches to a prompt of a session
  the marker never recorded, or to every prompt;
- a session whose context held no marker attaches nothing at any prompt — fails on an attachment
  keyed to every prompt, the skill forced on sessions that never carried it;
- a session whose context held the skill goes through a second compaction, and the next prompt
  after it carries the attachment again, while a second prompt on the same session, the marker
  spent, attaches nothing — fails on a marker that latches the first delivery and silences every
  later one, or one that delivers again on every prompt;
- the attachment's id is the id the plugin's skill domain lists for the development skill — fails
  on an attachment whose id names no skill the domain lists, the host having nothing to activate;
- a lookup that matches no skill appends nothing and reports — fails on an attachment appended
  after a failed lookup, the host having nothing to activate.

The two revised pairs are applied to their leaves in this package
(`PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md` — the pair's span from "A session whose
context the host compacts" to "…the plugin is what restores it.";
`PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md`, the reload sentences), with the doc-set
search each application ends by running (CONVENTIONS, [A delta application ends by searching the
doc set](PROJECT_DOCS/CONVENTIONS/planning-and-execution/a-delta-application-ends-by-searching-the-doc-set.md));
a statement the application leaves false outside these leaves is reported to the session, not
rewritten here. The floor question is settled by measurement, not by a new numeral: the pinned
`@opencode/plugin` 2.4.1's `SessionHooks` declares both `prompt` and `compaction`, and so do the
published 2.2.6, 2.3.0, 2.3.2 and 2.4.0 tarballs — no version adds the hooks, no numeral is earned,
and the host declarations' version has one home, `package.json`'s pin, not the resource
(CONVENTIONS, [A harness resource's version claims
testing](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-harness-resource-s-version-claims-testing.md)).
The leaf's floor line stands as it is; the ARCH pair's trailing "the floor line below extends to
what it adds" is deleted as false — the entry's reload uses no API the floor sentence does not
already cover. The same application drops the parenthetical the SPEC leaf carries at
`shipped-files.md:237` — its sentence reads `The plugin entry is written for opencode and is the
same file for both plugins;` — and the ARCH pair's applied text drops it from the leaf's opening
sentence with it, the numeral a resource names a floor only where its own line records the
observation earning it.

Done-line: `just test devpro`, `just dev-check-links`, `just dev-check-design-deltas-applied` —
exit 0 with `pairs: 6, landed: 6, pending: 0, drifted: 0, conflicting: 0, problems: 0` —
`just lint`.

After this package lands, the user live-tests the mechanism: a skill-holding session compacts,
the first exchange carries the skill's activation with its content in that same request. Where
the activation lands only on the turn after, the throw-away exchange returns and the user's
ruling is straight to the feature's removal — the fallback, a later decision, not this package's
work.

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
review the changes and their tests against the project's standards and fitness for purpose. The
live compaction observation the run deferred has run, before this review: a skill-holding session
on the updated install compacted, the injection delivered as a bare `@devpro-development` with no
skill content, and the record — the prediction, the operator's account, the vehicle rulings —
stands at `.devpro-temp/compaction-hooks/raw-observation.md`. Its finding enters the review
document as a finding, so any issue it surfaces is a burndown item. Each
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

Drafted from [ACTIVE_PLAN_REVIEW.md](ACTIVE_PLAN_REVIEW.md) — the post-plan review landed at
`1088921f` — one item per root-cause group, each citing its findings' IDs. The findings' severity
is the review document's; the items carry the fix. B5, B8 and B9's leaf and ticket text is the
prompt-engineer seat's to write; the other items go to the coder seats. The items' usability
review has run (`.devpro-temp/pb-pe-review.md`); the `devpro-architect` revision follows it, its
report at `.devpro-temp/pb-architect-revision.md` (*Dispatchability*); after both, the ticket's
remaining work is each item's row set by its state, then the dispatches. Run order: B1 lands
before the rest — until its commit, the conftest check keeps `just lint` red on the live tree, and
every item's done-line or checkpoint gate runs `just lint`; B2 lands before B3 and B7, whose items
state the dependency; nothing else orders the items. Items that edit a
landed SPEC or ARCHITECTURE leaf also revise that leaf's pair in `ACTIVE_DESIGN.md` — the
pair's from-text becomes the leaf's current text, its becomes the new, the pairs re-verified
with `just dev-check-design-deltas-applied` — and `ACTIVE_DESIGN.md` is left unstaged, as it is
through the run.

### PB Post-plan burndown

The ticket's remaining work after the items' usability review and `devpro-architect` revision:
each item's row set by its state, then the dispatches.

### B1 — every conftest's test-shaped functions eliminated (R1, R2, R3; the owner's ruling extends it to every conftest in the repository)

Intended lifetime: shipped. Rating: expert.

**No function in a `conftest.py` starts with `test_`** — pytest collects no test function from a
`conftest.py` in directory traversal (`--collect-only` verified), so the prefix there is either a
helper doing its job under a name that hides it or a test the gate never runs. The three files
carrying test-shaped functions: `tests/install/conftest.py`, `tests/profiler/conftest.py`,
`tests/render/conftest.py`; `tests/conftest.py` and `tests/dashboard/conftest.py` have none.

Scope (facts — commands and answers):
- `grep -c '^def test_' tests/{profiler,install,render}/conftest.py` → **54, 146, 116**.
- Name-diff of each conftest's test functions against the same directory's `test_*.py` (the
  scan is kept at `.devpro-temp/conftest-scan/`): **render 116 of 116** by-name duplicates;
  **profiler 53 of 54** duplicates, the one unique being R1's retired-path test; **install 135
  of 146** duplicates, **11 tests that exist only in the conftest** —
  `test_a_failed_probe_leaves_no_earlier_script_and_names_the_skip_and_its_reason`,
  `test_a_safety_copy_inside_the_install_directory_goes_with_the_tree`,
  `test_a_second_install_of_a_plugin_with_a_manifest_rewrites_the_same_manifest`,
  `test_a_second_install_replaces_the_tree_whole_and_leaves_no_stale_render`,
  `test_a_second_run_over_a_fresh_tree_reports_up_to_date_and_changes_no_byte_or_mode`,
  `test_a_user_level_opencode_install_copies_the_entry_and_the_guardrail_beside_it`,
  `test_an_install_removes_the_retired_launcher_and_its_directory`,
  `test_an_install_under_a_symlinked_install_directory_is_refused_with_nothing_written`,
  `test_an_operators_manifest_without_the_marker_is_refused_with_nothing_written`,
  `test_install_writes_every_render_and_stamps_the_packages_once`,
  `test_reinstalling_over_a_copy_of_another_version_reports_both_versions`.
- `tests/render/conftest.py`: delete all 116 `def test_` functions — each duplicates a collected
  test by name; the collected copy governs.
- `tests/profiler/conftest.py`: delete all 54 — the 53 by-name duplicates and R1's
  `test_init_removes_the_skill_an_older_init_rendered_under_its_former_name` (defined at
  `:1277`; a re-run no longer removes `.claude/skills/show-profile/SKILL.md` — P6 deleted that
  machinery — so the test fails when run; delete, do not rewire). R2's duplicated strict-fill
  test (`:2030–2085`) and its mark loop (`:1736`) are within the 53.
- `tests/install/conftest.py`: delete the 135 by-name duplicates. The 11 whose names appear in
  no `test_*.py` are triaged — each is one of: **a duplicate** whose
  collected copy exists under a different name (the earlier elimination renamed tests while
  moving them; verify by matching the body's coverage against `test_*.py`, then delete the
  conftest copy), **a helper misnamed with the `test_` prefix** (bare-rename it if something
  uses it; delete it if nothing does), or **a zombie** asserting machinery an earlier plan
  removed (the R1 pattern — `test_an_install_removes_the_retired_launcher_and_its_directory`
  names one; delete it, recording in the report what it asserted). The report names each of the
  11 with its category and the fact that puts it there — the counterpart's file:line for a
  duplicate, the dead assertion for a zombie; the done-line's checks cannot catch a wrong
  category, so this record is the item's completion observation. A test that is none of the
  three — genuinely unique live coverage — is reported to the session before any action, never
  moved or deleted on the executor's own reading.
- Trim `tests/profiler/test_init.py:1`'s module docstring to its surviving topics (R3).
- The check that keeps this eliminated: the `lint` recipe's python section now ends with
  `@! grep '^def test_' tests/conftest.py tests/*/conftest.py` — added ahead of the deletions, so
  `just lint` is red against the live tree until this package lands;
  its failure prints the offending lines. The red run is recorded before any deletion
  (`.devpro-temp/conftest-scan/lint-check-red.md`: exit 1, the 316 live lines printed) — the
  evidence the pattern matches, so the check's later green is not vacuous. The deletions above
  are what make it green, and this package's commit stages the justfile line with them.
- No fixture or helper any `test_*.py` file uses is deleted — the gate proves it.

In-scope tests: deletions and bare-renames only — the gate's collected count is unchanged,
because nothing the conftests held was ever collected. Done-line: `just test devpro`,
`just dev-check-links`, `just lint` (whose python section now carries the conftest check).
Checkpoint gate once before the commit: `just test`, `just lint`, `just sweep-python`. The
commit stages, beside its own paths, `ACTIVE_PLAN.md` and `ACTIVE_PLAN_REVIEW.md` — the review
document's addendum records this scope extension.

### B2 — the marker read: the declared shape, the host probe, the match or the narrowing (R4, R5, R6, R7, R10)

Intended lifetime: shipped. Rating: expert.

Outcome: the entry's marker matches a shape the pinned host declares; the runner's stand-in
models the declared shape and is type-checked against the pin; SPEC's clause states exactly what
the marker establishes — never more.

Scope (facts from the review document's R4–R7, R10):
- `devpro/harnesses/resources/opencode/index.ts:84–102`: rewrite the block comment to state what
  is established — the host records a skill activation as a `SessionMessage.Skill` whose body is
  a plain `text` field (`@opencode/schema/dist/session-message.d.ts:540–554`, no `content`);
  whether the host's compaction builder carries the skill message into the hook's `messages` is
  a live observation, not a declaration (R4). Take `textOf`'s parameter as the declared
  `SessionRequestMessage` type and read `part.text` under a `"text" in part` narrowing; delete
  the `as Record<string, unknown>` cast (R7 — the hook's parameter is already typed;
  `SessionCompaction.messages` → `Array<SessionRequestMessage>`, a narrowing probe compiles).
- `tests/opencode_entry_runner.ts`: give `Compact` and `skillMessage` the declared shapes — a
  skill activation is `{ type: "skill", skill, name, text }`, its body in `text`, and user
  messages' parts are `TextPart | MediaPart` — and type-check the runner against
  `@opencode/plugin`'s re-exports in this change (R5; the runner is deliberately outside
  `tsconfig.json`'s program, `justfile:240`, which is why the invented shape passed the gate).
- The host probe (R6): the probe is one run against the pinned host — a session whose context
  held an activated skill goes through a compaction, and the compaction hook's `messages` are
  read: the observation is whether any message is skill-kind (`type: "skill"` carrying the
  skill's `name`). The report names the probe, its output, and the branch it selects; where the
  probe cannot run headless, the report says so and the session runs it with the operator, the
  branch selection following its output. Where the
  kind is reachable — match the kind (`type === "skill" && name === skillName`, or
  `skill === id`), and add the runner case whose context holds the Agents file's text and no
  skill message, asserting nothing attaches (the empty case exists), the case's comment naming
  its defect — R6's false positive, the marker firing on the Agents file's text with no skill
  activation. Where it is not — keep the
  textual marker, change nothing else, and report to the session before touching SPEC
  (narrowing SPEC's "where the session's context held the skill before it" to "held the skill's
  text or its name" is a requirement change the user decides): the runner case is not added
  until the session rules, and the marker's behavior is unchanged until then — this package
  closes on this branch's own work, the narrowing and any runner case a later change once the
  session rules.
- `tests/test_opencode_entry.py:85–110`: the default `compactions` becomes the live case —
  `("devpro-development",)` — and the two tests needing "context held nothing" pass
  `("", "")` explicitly (R10; the current default conflates "no compaction" with "compacted an
  empty context").

In-scope tests: the runner's rewrite is the R5 fix — the stand-in models the API's real
semantics (`PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-stand-in-models-the-api-s-real-semantics.md`),
the leaf R6 turns on; the rewritten tests pin the branch R6's probe selects. The runner's
type-check is a new justfile recipe (`lint-runner-typescript`, `_js-deps`-dependent, running
`bunx tsc --noEmit` over a tsconfig whose `include` takes the runner — the lint recipe's own
scope comment, `justfile:240`, is why the main program excludes it), added in this package.
Done-line: `just test devpro`, `just dev-check-links`, `just lint`, `just lint-runner-typescript`.
Checkpoint gate once before the commit: `just test`, `just lint`, `just sweep-python`.

### B3 — the entry's text and small code notes (R8, R9, R11, R12)

Intended lifetime: shipped. Rating: mechanical.

Outcome: the entry explains the reload once; the runner's `fireCompaction`/`firePrompt` carry
no redundant guard throws; the log line reads once; the brand is made by the schema's maker.

Scope (facts from the review document's R8, R9, R11, R12; B2's rewritten comment at `:84–102`
is the text this item dedups — lands after B2):
- `index.ts`: one block comment above the two hooks stating the marker's lifecycle (recorded at
  a compaction whose context held the skill, spent by the next prompt, N compactions reload N
  times); the header keeps one clause; `skillMark` (`:82`) collapses into `skillName` (R8).
- `tests/opencode_entry_runner.ts`: delete `fireCompaction`/`firePrompt`'s unconditional-guard
  throws (R9 — the code reaching them has already established a hook is registered).
- `index.ts:229`: the failed-lookup `log` call takes the whole sentence as its message and drops
  the `err` argument — today it prints `…: nothing to activate: nothing to activate`; update
  `tests/test_opencode_entry.py`'s pin to the substring (`nothing to activate`), not the whole
  line (R11).
- `index.ts:232–238`: replace the `as { id: … }` assertion with `Skill.ID.make` from
  `@opencode/schema/skill` (`skill.d.ts:3`, `Schema.brand<Schema.String, "Skill.ID">` with
  `.make`; compile-probe verified) and correct the "no maker stands in the published
  declarations" comment (R12).

In-scope tests: `tests/test_opencode_entry.py`'s R11 pin update names its defect — the
doubled-print is the defect the exact-string assertion pinned. Done-line: `just test devpro`,
`just dev-check-links`, `just lint`. Checkpoint gate once: `just test`, `just lint`,
`just sweep-python`.

### B4 — the version claims (R13, R14, R15, R16)

Intended lifetime: shipped. Rating: expert.

Outcome: one floor claim, the host reference's, stated where a consumer reads it and where the
entry's own rules put the pin's numeral.

Scope (facts from the review document's R13–R16):
- Read the host reference — `node_modules/@opencode/plugin/dist/promise/session.d.ts`, the
  `ModelHooks`/`SessionHooks` declarations (the twin `effect/session.d.ts` is line-identical) —
  for what an undeclared hook name does at `ctx.session.hook`/`ctx.tool.hook` registration, and
  quote the finding in the report (never an inference — CONVENTIONS, *A hook contract is read,
  not assumed*). On that read the executor selects the branch and states the choice in the
  report: where an undeclared hook throws, the entry's floor line states 2.4.1 outright; where
  it is accepted as a no-op, the floor line states 2.3.0 with "your mileage may vary" plus a
  sentence naming the reload's two hooks (`SessionHooks.prompt`, `SessionHooks.compaction`)
  observed at 2.4.1 and unverified below it (R13).
- `index.ts:3, 6, 11–16`: the floor paragraph is the single statement — the `(floor 2.3.0)`
  label on line 6 is cut, the negative clause "no path here checks the host's version" is cut
  (CONVENTIONS, *No version-conditional code paths*, already forbids the branch), and the
  numeral `2.4.1` is replaced by "the `@opencode/plugin` declarations `package.json` pins"
  (R15, R16).
- `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md`, the opencode paragraph: one sentence
  stating the consumer-facing requirement — the entry requires an opencode that returns the
  `subagent` call at dispatch and declares the `SessionHooks` events it registers on, with the
  numeral the selected branch's: 2.4.1 or later where the read supports the throws branch, 2.3.0
  or later — the two hooks observed at 2.4.1 — where it supports the no-op branch — and
  `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md:20–24`
  cut to its load-bearing content (the `subagent`-foreground observation), citing the SPEC
  sentence, with "not an API one: every API the entry uses exists at 2.2.6" gone (R13, R14).
  Both leaves' pairs in `ACTIVE_DESIGN.md` are revised in the same commit.

In-scope tests: none — document and header edits; `just dev-check-links` and
`just dev-check-design-deltas-applied` confirm the pairs. Done-line: `just dev-check-links`,
`just dev-check-design-deltas-applied`, `just lint`. Checkpoint gate once: `just test`,
`just lint`, `just sweep-python`.

### B5 — the documents' altitudes (R17, R18, R19, R21, R22's leaf clause)

Intended lifetime: shipped. Rating: expert.

Outcome: SPEC owns the outcomes; ARCHITECTURE cites them; each site states the facts only it
adds.

Scope (facts from the review document's R17–R22; line numbers the usability review checked):
- `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md:3–14`: the reload paragraph keeps the entry's
  placement (which hooks it registers; the id resolved from the plugin's skill domain; a failed
  lookup attaches nothing and logs) and cites SPEC for the outcome (R17); "domain and never
  assumed" is dropped from the id clause — the CONVENTIONS citation one clause later is the only
  statement of the rule (R18); the Contexts list gains a "*The reload's surface…*" bullet ahead of
  the reminder's, which today carries the reload's two hooks unnamed, and the registration they
  are moves there (R19).
- `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md:128`: the clause "where it cannot read as
  the stop's label" is cut — position and separator are the requirement, the reason belongs to the
  design record (R21). The same paragraph's name clause states what the name is — the served
  project root directory's name — and the title sentence takes it from the nav, so no surface
  reads its name from another's (R20's document half).
- `PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-page-template-and-its-presentation.md:53`: the
  clause "the name a fill the strict fill carries" uses `fill` twice for two things — the
  fill mark and the filling act; name the machinery's operation once (R22's leaf half).
- R20's document half: SPEC owns what the name is and the grammar every page's nav must hold,
  including the board's; `PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md:113–117` keeps the
  nav's element order and drops the restatement of the name's grammar; the template leaf
  (`:52–60`) says its slot is filled through the strict fill and drops what the name is, citing
  SPEC; the board-page paragraph (`:81–83`) names the carrier the templates' leaf does not — the
  payload its script fills from. The board's `<title>` clause is R20's code half's.
- Each edited leaf's pair in `ACTIVE_DESIGN.md` is revised in the same change, per the section
  opening. A pair whose target moved after the pair landed reads `drifted` — its As stands in no
  leaf while its Becomes does — and re-points its As to the leaf's current text.

In-scope tests: none — document edits; the delta check and the link check confirm. Done-line:
`just dev-check-links`, `just dev-check-design-deltas-applied`, `just dev-check-plan`.
Checkpoint gate once: `just test`, `just lint`, `just sweep-python`. The design's pairs after this
change number ten — the six P1 landed, B4's SPEC-sentence pair, the Opencode-entry Contexts pair,
and this item's three revised pairs — every one landed.

### B6 — the project name's binding test and docstrings (R20's code half, R22's docstring half)

Intended lifetime: shipped. Rating: expert.

Outcome: the board's title and the profiler's nav and title are bound to one name by a test;
the name's docstrings state their own contracts.

Scope (facts from the review document's R20, R22):
- One test in `tests/dashboard/test_server.py`, beside
  `test_the_board_pages_nav_slot_is_filled_from_the_payloads_project` (`:624`) and using the
  same `serve` fixture the suite's server tests use: open `/board/`, `/profiler/` and
  `/page/<sid>`, read the project name from the board's `<title>`, the profiler's `<title>` and
  its `.project-name` span, and assert all equal — what the binding SPEC's clause states (R20).
  The test embeds `clauses.TEST_PRECONDITION` naming its defect: the three call sites derive
  the served project's name independently and no test binds them (R20's code half), so a surface
  whose derivation changes alone lands unchecked.
  Three call sites each derive the name with `os.path.basename`
  (`devpro/dashboard/server.py:161, 186`, `devpro/profiler/pages.py:846`) and nothing binds
  them; `devpro/kanban/server.py:174` is out of scope — the board payload's `project:` field is
  the board's own.
- `devpro/profiler/pages.py:285–293` (R22): `project_fill`'s docstring states it always takes
  the raw (unescaped) name — today it implies the name arrives escaped while `project_fills`
  re-escapes the same value (a probe confirmed no double-encode ships; the footgun is the
  docstring's implied contract).

In-scope tests: the added test names its defect — R20's code half, the unbound derivations
above; R22 changes no behavior. Done-line:
`just test devpro`, `just dev-check-links`, `just lint`. Checkpoint gate once: `just test`,
`just lint`, `just sweep-python`.

### B7 — the test instruments' contracts (R23, R24, R25)

Intended lifetime: shipped. Rating: mechanical.

Outcome: the runner's stdout contract is parseable in one pass; the reload tests carry the
convention's clause; no docstring claims a comparison another test makes. Lands after B2 — its
header's host-fact clause drops only once B2 gives the stand-in the declared shape.

Scope (facts from the review document's R23–R25):
- `tests/opencode_entry_runner.ts` header (R23): the JSON's keys one per line in output order,
  as `tests/profiler/profiler_contract_runner.ts` does; the prose states the driven surface
  (which input keys the runner fires, in what order); `attachments` described as "the ids the
  prompt draft carries before the hook runs" — not where they came from; the "fails where"
  sentence extended to the reload hooks (`fireCompaction`/`firePrompt`); the reflowed reload
  paragraph restored to its ~100-column wrap and the "the host admits the prompt a compaction
  is followed by" clause cut — the header states what the runner constructs; what the host
  admits is B2's probe's observation, never the runner's claim.
- `tests/test_opencode_entry.py` (R24, corrected against the file): the reload group is the
  five tests at `:323, 349, 373, 405, 437`; none of them carries the
  `clauses.TEST_PRECONDITION` clause — all paraphrase it as "It fails on…" — while the sibling
  suites embed the clause object itself (`tests/profiler/test_fill.py`,
  `tests/dashboard/test_server.py`). The five gain the clause embedding, following the
  siblings' pattern; the review document's R24 said "two of six lack the marker four siblings
  carry" and is corrected there.
- `tests/test_opencode_entry.py` (R25): `test_a_skill_the_domain_does_not_list_attaches_nothing_and_reports`
  (`:437`) loses the sentence claiming the differential comparison
  `test_the_attachment_names_the_skill_the_domain_lists` (`:405`) makes.

In-scope tests: docstring and header edits; the runner's header is prose its own output must
match, checked by the suite. Done-line: `just test devpro`, `just dev-check-links`, `just lint`.
Checkpoint gate once: `just test`, `just lint`, `just sweep-python`.

### B8 — the ROADMAP ticket's text (R27, R28)

Intended lifetime: shipped. Rating: mechanical.

Outcome: the ticket states facts and direction; its instruments resolve.

Scope (facts from the review document's R27, R28):
- Cut the second sentence's rule citation ("the noise the project's own emphasis-economy rule
  forbids…") — the next paragraph already carries the direction, and the ticket's third
  paragraph already states the fact without surroundings (R27).
- The third paragraph's instrument enumeration resolves: name the recipe target
  (`render-diff`'s slot per
  `PROJECT_DOCS/CONVENTIONS/planning-and-execution/render-diff-slots-and-output.md`) and the test
  file the render-property assertions live in; where they live in no one file, state the search
  without the enumeration (R28).

In-scope tests: none. Done-line: `just dev-check-roadmap`, `just dev-check-links`. Checkpoint
gate once: `just test`, `just lint`, `just sweep-python`.

### B9 — the CONVENTIONS leaves the review's gaps named (R29, R30, R31, R33)

Intended lifetime: shipped. Rating: expert.

Outcome: the house rules name the two traps the review found and the one sentence that scopes
the type check.

Scope (facts from the review document's R29–R31, R33; the proposals they carry are quoted at
their sources):
- A new leaf under the [Planning and Execution](PROJECT_DOCS/CONVENTIONS/entry-point.md) tree: **no function in a `conftest.py` starts with `test_`**; the file
  carries fixtures and bare-named helpers, and a test-shaped function found there is one of a
  stale duplicate, a misnamed helper, or a zombie asserting removed machinery — the pytest
  traversal-collection trap is why the prefix never runs (R29; the proposed wording stands at
  `.devpro-temp/pr-review-python-coder.md:265–268`).
- A new leaf under the [Code, Definitions and Install](PROJECT_DOCS/CONVENTIONS/entry-point.md)
  tree: a runner's stand-in is type-checked against the pinned host declarations in the change
  that edits it; where it cannot be, a comment names the field it models and where in the
  declarations it is declared (R30; the proposed wording stands at
  `.devpro-temp/pr-review-typescript-coder.md:268–271`).
- R31's one sentence — the type check holds that a name exists, never that a read is right —
  lands where its reader looks for it: the prompt-engineer writing these leaves decides which
  leaf carries it (R30's, a stand-in's own, or the hook-contract leaf) and writes the smallest
  statement.
- A third new leaf, beside R29's (R33): **no dispatched run writes a package-manager lock,
  manifest or vendor file into the repository root** — a tool one agent's environment happens to
  carry is not thereby the project's, and tooling the project has not adopted waits on the
  owner's decision. This bullet's text is changed after the items' `devpro-prompt-engineer`
  usability review and `devpro-architect` revision, and takes its review of the change only
  before this item dispatches (*Plans*).

In-scope tests: none. Done-line: `just dev-check-links`, `just dev-check-plan`. Checkpoint gate
once: `just test`, `just lint`, `just sweep-python`.
