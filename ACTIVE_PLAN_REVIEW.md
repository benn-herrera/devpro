# Post-plan review — ACTIVE_PLAN.md, four seats

The plan's landed changes (range `889c3e8c^..32cbdbca`, packages P1–P7) reviewed by the four
post-plan seats: python-coder, typescript-coder, architect, prompt-engineer. Each wrote its own
review to `.devpro-temp/pr-review-<seat>.md`; this document is the session's synthesis — one
entry per defect, every seat that reported it named, de-duplicated, conflicts settled against the
artifacts. The review document is never diced; the burndown items cite the entry IDs below.

Gates the seats ran and what they cannot see: `just test devpro` (159–160 passed, 1 platform
skip), `just lint` (black, isort, flake8, mypy, shellcheck, `bunx tsc --noEmit` against the
pinned `@opencode/plugin` 2.4.1 declarations) — all exit 0 at `32cbdbca`. The findings below are
about what those checks cannot see, not about a red gate; where a seat ran a probe, the probe is
the evidence.

## The live compaction test (routed in per the plan)

The prompt-attachment front door was confirmed live before this review: the session compacted
manually (`/compact`), the first exchange after it carried the `devpro-development` skill's full
text as a fresh activation block, and the next exchange attached nothing — the marker spent.
Recorded at `.devpro-temp/compaction-hooks/live-test-2-observation.md` with the operator's
account. No burndown item on its account — but note its blind spot: the test session's own
Agents file carries the marker text, so R6's false-positive is invisible in it. The live test
neither confirms nor contradicts R6.

## Findings

### The tests living in `conftest.py` (root cause: P6's deletion caught the `test_init.py` copies, not the `conftest.py` ones)

- **R1 — Critical (architect; python-coder reported the test copy, misreading its color).**
  `tests/profiler/conftest.py:1277` `test_init_removes_the_skill_an_older_init_rendered_under_its_former_name`
  asserts machinery P6 deleted — `init` unlinking `.claude/skills/show-profile/SKILL.md` and
  staging its removal. It **fails when run** (architect-verified at `conftest.py:1299`,
  `assert not (retired / "SKILL.md").exists()`, both parametrizations), and `just test` never
  sees it: pytest does not collect test functions from `conftest.py` during directory traversal
  (verified by `--collect-only`). Settled against the artifacts: the printed `git add` line is
  **correct** — `devpro/profiler/hooks.py`'s `staged` list names only the current skill and
  `.claude/settings.json`; the python-coder's "stale entry" claim and its "still green" reading
  are withdrawn. The behavior's removal was deliberate (the design: wholesale replacement
  obviates the retired path; "Obviated code is deleted, not parked"), so the fix is **delete the
  test copy** — and the `shlex` import at `conftest.py:7` if nothing else uses it — not rewire
  `init`. Owner: a coder dispatch.
- **R2 — Note (python-coder).** The byte-identical
  `test_the_strict_fill_refuses_unknown_and_unfilled_marks_and_leaves_none_standing` is pinned
  twice (`conftest.py:2039–2085`, `test_fill.py:27–75`), including the P2 marks; the range
  extended both copies without merging. Delete the `conftest.py` copy and the duplicated mark
  loop inside `test_every_script_spelling_of_the_prefix_is_the_services_one` (`conftest.py:1736`)
  in favour of `test_fill.py`'s. Same root cause as R1. Owner: a coder dispatch.
- **R3 — Note (architect).** `tests/profiler/test_init.py:1`'s module docstring still names
  retired launchers and skill removal, whose tests are gone. Trim to what remains. Owner: a
  coder dispatch.

### The marker read (root cause: the marker was built on a message shape the pinned declarations do not give)

- **R4 — Critical (typescript-coder).** `devpro/harnesses/resources/opencode/index.ts:84–102`:
  the comment asserts a skill message nests its body under a `content` part — the declarations
  contradict it (`SessionMessage.Skill` carries a plain `text` field, no `content`;
  `@opencode/schema/dist/session-message.d.ts:540–554`) — and `textOf` is written to walk the
  contradicted shape, so the code is right by accident and a later editor trusting the reason
  will break the marker. The comment also states as fact something the design's own fact block
  leaves unknown (whether the host's compaction builder carries the skill message at all),
  against CONVENTIONS' *A hook contract is read, not assumed*. Fix: rewrite the comment to state
  what is established; drop the `content` walk absent a live observation of it.
- **R5 — Critical (typescript-coder).** `tests/opencode_entry_runner.ts` models the same
  unproducible shape (`Compact` typed as content-part messages; `skillMessage` a
  `{ role, content: [{ type: "text", text }] }` stub), so the marker test proves the marker
  matches the runner's invented shape, not the host's — CONVENTIONS' stand-in rule names exactly
  this: a stand-in answering by invented semantics "reports a state the real mechanism cannot
  reach". The lint recipe deliberately excludes the runner from the type-checked program, which
  is why the check cannot see it. Fix: give the stand-in the declared
  `SessionRequestMessage`/`SessionMessage.Skill` shape and type-check it against the pinned
  declarations.
- **R6 — Critical, design-level (typescript-coder, architect).** The marker is the substring
  `devpro-development` over every text of every compaction message (`holdsInvocation`,
  `index.ts:89–91`). The project's Agents file is loaded into every session of every consuming
  project and names the skill twice, so essentially every session marks at its first compaction
  whether or not the skill was ever activated — the next prompt then carries the full skill
  text. SPEC's landed clause promises attachment only "where the session's context held the
  skill before it"; the architect's version: the entry promises "never touched" for contexts
  that never held the skill, and the prose claims more than the machine gives. Fix direction:
  prefer matching the message kind the declarations give (`type: "skill"` + `name`) — but
  whether a skill message survives into the compaction request as that kind is a live
  observation, not a declaration; probe the host, and where the kind is unreachable, narrow the
  SPEC clause and the entry's comment to what a textual marker establishes ("held the skill's
  text or its name"), never leave SPEC claiming what the check does not deliver. Either way one
  runner case is added: a context holding the Agents text and no skill message.
- **R7 — Warning (typescript-coder).** `textOf` takes `unknown`, casts to
  `Record<string, unknown>` and recurses, where the hook's parameter is already typed
  (`SessionCompaction.messages` → `SessionRequestMessage`; `part.text` type-checks under a
  narrowing — probe verified). The unparsed walk also accepts shapes the host cannot produce,
  which is what made R4's wrong comment plausible. Fix: take the declared type, read
  `part.text` under narrowing, delete the cast.
- **R8 — Note (prompt-engineer, typescript-coder).** The entry explains the reload three times
  (header, block comment, prompt-hook comment) and `skillMark` is `skillName` assigned to
  itself — a second constant kept so a comment can say its content is not the text matched.
  Fix: one block comment above the two hooks stating the marker's lifecycle (recorded at a
  compaction whose context held the skill, spent by the next prompt, N compactions reload N
  times); the header keeps one clause; `skillMark` collapses into `skillName`. Highest-cost
  duplication in the range: the file ships byte-verbatim to every consumer.
- **R9 — Note (typescript-coder).** The runner's `fireCompaction`/`firePrompt` throw when no
  compaction/prompt hook is registered — state the code reaching them has already established —
  while the real hazard (a throwing callback aborting the whole registration group, untested)
  is unguarded in the plain `for` loop that awaits every hook. Fix: delete the two conditional
  throws or replace with one set-comparison assertion; consider the abort ordering.
- **R10 — Note (python-coder).** `_run_entry`'s default `compactions=("", "")` builds "a
  session that compacted an empty context" — the rarer case — conflating it with "nothing
  compacted"; the new tests override the default, so the assertions are sound, but the default
  is a setup nobody's session has. Fix: make the default the live case (`("devpro-development",)`)
  or no compaction at all, and pass the empty case explicitly.
- **R11 — Note (typescript-coder).** `index.ts:229` passes a descriptive string as `log`'s
  `err`, printing `…: nothing to activate: nothing to activate`; the test pins the doubled text
  as a fixed form, and the exact-string assertion is itself a form pin — pin the substring.
  Fix: one-argument `log` (or the whole sentence as the message) and the test's substring.
- **R12 — Note (typescript-coder).** `index.ts:232–238` brands with `String(listed.id)` and
  asserts back with `as { id: … }`, under a comment saying "no maker stands in the published
  declarations" — but `@opencode/schema/skill` exposes `Skill.ID.make` (`skill.d.ts:3`,
  compile-probe verified). The value handed the host is right; the `as` is the defect the
  project's `as T` rule forbids. Fix: use the maker, correct the comment.

### Version claims (root cause: the floor was stripped from SPEC and the leaf in P2/P7 while the header kept claims the range had just made false)

- **R13 — Warning (typescript-coder, architect, prompt-engineer).** The entry's floor claim no
  longer describes the file: `index.ts:3, 11` say floor 2.3.0 while the reload stands on
  `SessionHooks.prompt`/`compaction`, which only the pin's declarations are observed to declare
  (`2.4.1`); `index.ts:15–16`'s "the hooks register on every install" is a host-behavior
  assumption nothing verifies; and the leaf
  `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md:20–24` still reads "The floor is a
  behavioral one, not an API one: every API the entry uses exists at 2.2.6" — the reload's two
  hooks are API surface, so the paragraph contradicts the file's own (floor-less) opening
  (`:2`, "It is written for opencode"). Fix: read the host reference for what an undeclared hook
  does at registration; then one floor claim, the host reference's — either 2.4.1 outright, or
  2.3.0 with "your mileage may vary" plus a sentence naming the reload's two hooks observed at
  2.4.1 and unverified below — and the leaf's `:20–24` cut to its load-bearing content (the
  `subagent`-foreground observation).
- **R14 — Warning (prompt-engineer).** No contract document states the entry's host-version
  requirement any more: SPEC `shipped-files.md`'s parenthetical was struck in P2, the leaf's in
  P7, and the only leaf naming 2.3.0
  (`CONVENTIONS/code-definitions-and-install/a-harness-resource-s-version-claims-testing.md`)
  makes a resource's numeral a testing claim, not a requirement — SPEC is where a
  consumer-facing requirement lives. Fix: one SPEC sentence in `shipped-files.md`'s opencode
  paragraph (the entry requires an opencode that returns the `subagent` call at dispatch and
  declares the `SessionHooks` events it registers on — 2.3.0 or later, observed at 2.4.1), with
  ARCH citing it. Owner: prompt-engineer, on an authorizing dispatch.
- **R15 — Warning (architect, prompt-engineer).** `index.ts:15` restates the pin's version
  (`2.4.1`) in a resource header — the version's one home is `package.json`'s pin, "which a
  resource's header never restates" (CONVENTIONS, *A host version is checked against the host's
  declarations*); it rots the moment the pin moves. Fix: "the `@opencode/plugin` declarations
  `package.json` pins".
- **R16 — Note (prompt-engineer).** The header states the floor twice (line 6's label
  `(floor 2.3.0)` and lines 11–14's paragraph), and line 15's "no path here checks the host's
  version" is a negative the reader cannot act on — `no-version-conditional-code-paths.md`
  already forbids the branch — copied into every consumer's install. Fix: the floor paragraph is
  the single statement; cut the label and the negative clause.

### The documents' altitudes (root cause: the plan's new paragraphs restate instead of citing, and the nav's name is stated at four sites)

- **R17 — prompt-engineer.** `ARCHITECTURE/install/opencode-entry.md`'s reload paragraph
  reproduces SPEC's outcome then restates it in mechanism spellings (`skills`, marker). Fix:
  ARCH keeps the entry's placement (which hooks it registers; the id resolved from the skill
  domain; a failed lookup attaches nothing and logs) and cites SPEC for the outcome.
- **R18 — prompt-engineer.** "never assumed" appears twice in two consecutive sentences of the
  same paragraph; the second is the CONVENTIONS leaf's own sentence, cited one clause later.
  Fix: drop it from the id clause.
- **R19 — prompt-engineer.** The leaf's Contexts bullet list has one bullet per hook group and
  no bullet for the reload, though the reload is two registered hooks the entry owns; the
  opening sentence carries the reminder's group and the reload on one em-dash. Fix: a "*The
  skill's reload.*" bullet beside "*Reminder.*"; the opening reduced to a clause naming it.
- **R20 — prompt-engineer, python-coder.** The nav's project name is stated at four sites
  (SPEC `shipped-files.md`, ARCH `serving.md`, ARCH `the-page-template-and-its-presentation.md`,
  the board-page paragraph) and three add different facts: SPEC and `serving.md` say "served",
  but the standalone render's name is the directory `tree` ran in, and the board's span is
  filled client-side by `board.js` from the payload, which neither the template leaf's
  strict-fill sentence nor the board paragraph says. Code side (python-coder): four call sites
  each derive the name with `os.path.basename` and no test binds the board's title to the
  profiler's nav — the binding SPEC states. Fix: SPEC owns what the name is and the grammar
  every page's nav must hold (including the board's); `serving.md` keeps element order only;
  the template leaf names both carriers (strict fill for the templates' pages, the payload for
  the board's); one test asserting the board's `<title>` and the profiler's `<title>` and
  `.project-name` all carry the same name.
- **R21 — prompt-engineer.** SPEC's "where it cannot read as the stop's label" is intent in the
  contract — position and separator are the requirement; the reason belongs to the design
  record. Fix: cut the clause.
- **R22 — prompt-engineer, python-coder.** The name's docstrings drift: `pages.project_fill`'s
  docstring implies it takes an escaped name while `project_fills` re-escapes (python-coder's
  probe confirmed no double-encode today — a footgun, not a bug; fix the docstring to "always
  takes the raw name"), and it claims the board's span, which the payload fills (prompt-engineer;
  "a fill the strict fill carries" also uses "fill" twice for different things in one clause).
  Owner: a coder dispatch, with the leaf clause for the prompt-engineer.

### The test instruments (root cause: the runner's contract is prose the range did not keep current)

- **R23 — prompt-engineer, typescript-coder.** `tests/opencode_entry_runner.ts`'s header: the
  stdout contract is a run-on whose field order does not match its prose; `attachments` is
  described by where the ids came from ("the ids the operator's own prompt already attached")
  rather than what it is; the "fails where" list omits the reload hooks it now fires; the
  reflowed reload paragraph wraps at ~150 columns where the rest wraps at ~100, lost its lead-in,
  and claims the runner models "the host admits the prompt a compaction is followed by" — the
  runner's construction, not a host fact (exactly what R5 shows it does not verify). Fix: keys
  one per line in output order (as `profiler_contract_runner.ts` does); keep prose to the driven
  surface; describe ids as "the prompt draft carries before the hook runs"; extend the failures
  sentence; restore the wrap and drop the host-fact claim until R5's fix gives the runner the
  declared shape.
- **R24 — prompt-engineer (arithmetic corrected against the file during drafting).** The reload
  group in `tests/test_opencode_entry.py` is the five tests at `:323, 349, 373, 405, 437`; none
  of them carries the `clauses.TEST_PRECONDITION` clause — all paraphrase it as "It fails on…" —
  while the sibling suites embed the clause object itself (`tests/profiler/test_fill.py`,
  `tests/dashboard/test_server.py`). Fix: the five gain the clause embedding, following the
  siblings' pattern.
- **R25 — prompt-engineer.** `test_a_skill_the_domain_does_not_list_attaches_nothing_and_reports`'s
  docstring claims the differential comparison a different test makes. Fix: cut the sentence.
- **R26 — Note (architect; typescript-coder flagged the sibling).** Two form pins the suites
  carry: `test_the_board_pages_nav_slot_is_filled_from_the_payloads_project` asserts the exact
  JS statement `$("project-name").textContent = payload.project;` — the stronger check is
  running `board.js` under bun as the index-script test does, worth doing when `board.js` next
  changes; and `sessionHooks` asserts the registration order `["model.request", …, "prompt",
  "compaction"]`, a source-order pin that breaks on any no-op reordering — pre-existing style,
  left to the plan's owner.

### `ROADMAP.md`, the new ticket

- **R27 — prompt-engineer.** The ticket's second sentence argues from a rule the reader already
  holds ("the noise the project's own emphasis-economy rule forbids…"); the roadmap's job is the
  fact and the direction, which the next paragraph already carries. Fix: cut the rule citation.
- **R28 — prompt-engineer.** The ticket's third paragraph names three instruments — `git grep`
  over the render machinery, `render-diff`, "the render-property assertions" — none of them a
  resolvable path (the recipe target and the test file unnamed). *References must resolve.* Fix:
  name the recipe target and the test file, or state the search without the enumeration.

### Contract gaps (findings about the `CONVENTIONS/` tree, with proposed wording in the seats' reports)

- **R29 — python-coder, architect.** No leaf states that tests live in `test_*.py` and
  `conftest.py` carries fixtures — the rule R1 and R2 turn on, and the collection trap that hid
  R1. Adopt the python-coder's proposed leaf under *Planning and Execution*.
- **R30 — typescript-coder.** No leaf requires a runner's stand-in to be type-checked against
  the pinned host declarations — the lint recipe excludes runners from the program on purpose,
  which is why R5 was invisible. Adopt the proposed leaf: type-check the stand-in in the change
  that edits it, or a comment names the field it models and where the declarations declare it.
- **R31 — typescript-coder.** Worth one CONVENTIONS sentence: the type check holds *that a name
  exists*, never *that a read is right* — the gap that produced R4 and R5.
- **R32 — python-coder.** Proposed leaf "a script helper used by two page templates is one
  text" — **withdrawn**: the architect's reading is the leaf's own (each page script is an IIFE,
  helpers module-private by design, because classic scripts share one global scope; the deco
  publishes exactly one name). The `clip` duplication P3 landed is compliant; what survives is a
  note — P3's row-draw test binds one copy, and any future drift between the copies stays
  unreported unless a binding test is wanted. No CONVENTIONS change, no code change.

## Addendum — the conftest sweep's true scope (found during burndown drafting)

R1–R3's scope was `tests/profiler/conftest.py`'s leftovers. During the burndown's drafting, the
owner ruled wider and named the rot directly: **no function in any `conftest.py` starts with
`test_`** — the three rotten files are `tests/install/conftest.py`, `tests/profiler/conftest.py`
and `tests/render/conftest.py` (`tests/conftest.py` and `tests/dashboard/conftest.py` are
clean), every test-shaped function in them is invisible to `just test` (R1's traversal trap),
and each is one of **a duplicate** of collected coverage, **a helper with a bad (test-prefixed)
name**, or **a zombie** asserting machinery an earlier plan removed.

The counts and overlap (scan kept at `.devpro-temp/conftest-scan/`):
`grep -c '^def test_' tests/{profiler,install,render}/conftest.py` → 54, 146, 116. Name-diff
against each directory's `test_*.py`: render 116/116 by-name duplicates; profiler 53/54
duplicates (the one unique is R1's retired-path test — a zombie); install 135/146 duplicates,
11 names appearing in no `test_*.py` — triaged per the owner's taxonomy (duplicates under
renamed forms, misnamed helpers, or zombies), never moved on the executor's own reading. The
four seats reviewed the landed range and none swept past the profiler conftest; this addendum
is the record of the extension. B1 carries the scope.

## Settled-without-finding (for the record)

- The dashboard CLI failures in `tests/dashboard/test_server.py` (ten) are pre-existing: the
  architect reproduced them on the base commit in a scratch worktree at `889c3e8c^`
  (`.devpro-temp/base-889`, removed after).
- No tracked file cites the retired-design scratch records (`live-test.md`,
  `raw-observation.md`); the citation warning the typescript-coder raised does not apply.
- The plan added the `!TUNING!` roadmap ticket (`184e49ef`) outside this design's scope —
  ROADMAP is the right home; flagged by the architect, no action.
- Verified clean by the architect: the strict-fill marks on every carrier, the reload Set's
  lifetime across the watcher's `refresh()`, the hook names type-checked against the pin,
  `SessionPrompt.prompt`'s `skills` mutation type-legal, and the doc claims on nav order, title
  forms and both render paths.
- Verified clean by the typescript-coder: no residue of the deleted idle mention-delivery leg
  (the runner's synthetic records are the reminder's alone); the justfile's TS target is
  correct for the shipped resource.
