# Post-plan review

The review of the plan's landed work — commits `7941698`, `af43ee7`, `8a6762e`, `897b8e4`, `5bf027c`,
`96bddb0`, `877b7fe`, `b441303` — against the project documents and the design, by three
independent seats writing their own findings: the coder (`REVIEW-coder.md`), the architect
(`REVIEW-architect.md`) and the prompt-engineer (`REVIEW-prompt-engineer.md`), all in the scratch
directory. This document is the de-duplicated synthesis; one entry per defect, naming every seat
that reported it. The burndown cites these IDs and groups the findings by root cause.

## Verified sound (the seats' own accounts, reconciled)

- The one-strict-fill rule is structural: all three assembly paths walked, both templates, no mark
  standing rendered or served (architect).
- The feed's schema is one place *with a machine check*: the bun runner proxies the feed and asserts
  the exact key set the script reads (architect).
- The byte pin honestly undoes exactly the layer carriage plus the band's per-page facts — no other
  difference (architect).
- The quiet client-gone guard landed on `DashboardServer`, where the method actually lives; the
  retired panel method was a genuine `AttributeError` (coder).
- The `877b7fe` correction is true of the code: run live, plain `profiler tree` prints the column
  header alone and `--verbose` prints 72 more lines; `visible()` agrees (prompt-engineer).
- The deco renaming is complete and clean: `git grep -i chrome` over the tracked tree leaves only
  the browser's `Chrome` in `web_app_expert.py`; the root documents carry none; all four reference
  slots render the corrected sentence (prompt-engineer).
- SPEC and ARCHITECTURE agree post-amendment; every named retirement is verified gone
  (`with_frame`, `nav_html`, `band_html`, `deco_script`, `NAV_SERVER`, `format_span`, the
  server-side row builders) (architect).
- `ROADMAP.md`'s ticket layout is uniform and read uniformly (architect).

## Blocker

- **R1** *(prompt-engineer)* — `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md:71-78` as landed by
  `b441303` ends a clause on a stranded `— and`: the leaf reads "the plain tree … `PARENT_TOOLS` —
  and finds the profiler's launcher", which a model parses as the tree finding the launcher — false.
  The source is the design's own `Becomes` block (`ACTIVE_DESIGN.md:177-184`): fix entry and leaf
  together. *(The design retires at the plan's landing commit, so the surviving artifact is the
  leaf; the entry fix matters until then.)*

## Findings

- **R2** *(coder)* — `/api/traces` is answered without `page=True`
  (`dashboard/server.py:216`): the feed is browser-loadable JSON built from record text, and the
  branch four lines above sets the Content-Security-Policy the pages are served under. One keyword.
- **R3** *(coder, architect)* — `index_html` (`pages.py:836`) reads and parses every `.jsonl` store
  per `/profiler/` request and discards the result: the static index needs no rows, and the feed
  re-reads the stores; its docstring's justification ("read for the legend's band") is true of
  nothing — the band's fills read module constants. Dead per-request work on the hot path.
- **R4** *(coder)* — `link_layer` (`pages.py:847`) is a fill outside the one strict fill: a global
  `str.replace(SHARED_CSS, "")` and a whitespace-keyed `<style>\n` replace, both silent no-ops when
  their input shifts — the silent-replace defect the strict fill exists to refuse. The
  ARCHITECTURE claim (`harness-profiler.md:52-56`, every fill runs through the strict fill) is not
  yet true of the layer's carriage. *(architect, adjacent: the `SHARED_CSS` strip is unbounded —
  the same replace, the same concern.)*
- **R5** *(coder)* — `profiler_page` is declared twice: the dashboard's copy (`server.py:84`) a
  bare delegation of the pages' own (`pages.py`).
- **R6** *(coder)* — `strict_fill` internals: the mark-still-standing check after a mark replace is
  unreachable (a replace that leaves the mark can only loop, and the earlier existence check
  already raised) with a misleading `KeyError`; the slot and mark existence checks duplicate one
  walk; a docstring sentence names a "later stage" that does not exist; `isidentifier()` admits
  Unicode identifiers `string.Template` rejects.
- **R7** *(coder)* — the deco's moments sweep races the index's fetch (`deco.js:103` runs at load;
  the rows arrive asynchronously): on a slow load the fresh moments cells stay raw UTC. No test
  pins the ordering.
- **R8** *(coder, architect)* — `deco.js`'s header says the dashboard "inlines this text into each
  of its pages": retired by `8a6762e` — the pages link `/profiler/deco.js` and the dashboard serves
  it. The terminology pass fixed the coinage, not the carriage claim.
- **R9** *(architect)* — `test_a_session_page_is_served_without_reading_the_stores_a_second_time`
  is a false-confidence test: it pins "one store read per `/page/` request" but the code performs
  two (`session_for` and `dispatcher_of` each call `read_sessions`); the monkeypatch counts
  `pages.read_sessions` while `dispatcher_of` resolves the name through the dashboard's own import,
  so the second read is uncounted. The test passes against a property that does not hold.
- **R10** *(prompt-engineer)* — the plan's Code-delta citations
  (`ACTIVE_DESIGN.md#install--harness-profiler`, `#subsystem-map`) land on the *first* of two
  duplicate `###` headings — the ARCHITECTURE-delta section's. `just dev-check-links` passes
  because it collects anchors into a set; the reader lands on the wrong section. Fix: `-1`
  fragments.
- **R11** *(prompt-engineer)* — the skill says "where `tree` instead says `No traces in …`", but
  that message is on stderr with exit 1 (`UsageError`, `cli.py:66-68`); a model reading the
  command's stdout never sees it. The skill's fallback path is unreachable as written.
- **R12** *(prompt-engineer)* — "count the lines of that recording" puts a counting guarantee on
  the executing model: no test observes it and no tool carries it. Either the skill drops the
  count or names how it is arrived at.
- **R13** *(prompt-engineer)* — the mage slot ships `show-profile` with no launcher and no
  `.claude/` anywhere, so the skill's finder always takes "not installed and stop": the skill is
  inert under mage. Either mage ships no skill or the finder's stop is stated as the mage case.
- **R14** *(prompt-engineer)* — the plan's Sequencing says "both ARCHITECTURE passage pairs"; the
  leaves hold seven (six plus one). A count that misleads the next reader of the plan's own
  account.
- **R15** *(architect)* — the `INDEX` template's dark zebra rule is now a no-op duplicate (the
  layer's `--zebra` switches with the scheme already), and its comment describes a "motif pair"
  the template does not carry.
- **R16** *(architect)* — `view.html:2`'s "works from file://" overstates: the standalone render
  fetches nothing, but the claim is broader than the page survives.
- **R17** *(architect)* — an unreadable *trace inside* a readable store still raises where the
  leaf names only the store-level case: the glob's promise and the read's behavior differ at the
  file level.
- **R18** *(architect)* — the row-rendering script's `console.warn({...})` logs an object where a
  message is wanted.

## Observations (no change)

- The byte pin is a strong property; it is proved against a Python re-implementation of the JS
  formatting and excludes the band's content, which other tests cover (coder).
- One pre-existing colour-literal pin in the index test is a form pin (coder).
- The `INDEX`'s empty-feed and span scales are now pinned in the runner test (in-repo state, noted
  for the burndown's grouping).
- The `rendered/` tree is gitignored, so the plan's "the retake runs in this package's commit"
  (`plain-tree-skill`) described a tree that does not exist; the retake's evidence lives in the
  session's verification, and the done-line's "stated clean" is unachievable as written — the
  achievable observation (the one-difference check) is what verified it. Plan-text defects for the
  record.
- The `SPEC/plugins.md:71` include-path citation (`docdicer.just`/`docdicer.mk`) is stale — the
  shipped files are `devpro.just`/`devpro.mk` (found during the run's terminology verification).
