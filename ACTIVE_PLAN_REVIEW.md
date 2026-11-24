# Post-plan review — profiler dashboard corrections and sweep granularity

Seats: `devpro-python-coder`, `devpro-architect`, `devpro-prompt-engineer`; each reviewed
independently from the project documents and the design, not the plan. The session synthesized
this document from the three reviews, de-duplicating and reconciling. Findings carry one ID per
defect and name every seat that reported it. Range reviewed: `81d6eb0..e4f1edd` (P1 `6854bb9`,
P2 `74c5f7e`, P3 `99f0f4d`, P4 `e4f1edd`).

## Findings

- **R1** (coder, critical): The sentence-grain double-delivery check has no case over the real
  renderings — every caller of `_double_paragraphs` uses 2–3-line fixtures. The grain ships
  unexercised on its actual inputs (the seat's probe: 89 prompts, 19,192 sentences, zero findings
  — correct, but nothing asserts it).
- **R2** (coder, critical): The DISSENT expectation was weakened from a constant-form assertion to
  a list the production splitter computes from the same constant — a splitter change moves both
  sides and the test cannot fail. Restore the constant form.
- **R3** (coder + architect): `_sentence_list`'s marker strip has two defects — it strips the first
  `N. `/`N) ` *anywhere* in the unit (the docstring says leading; the regex is unanchored), and it
  runs on every prose unit regardless of kind, though the plan's intent was item text only. A unit
  with an internal `2. ` splits differently from its numbered twin: a false negative in the check
  P2 sharpened. Fix: anchor `^`, scope by kind, add the pin that fails before the fix.
- **R4** (PE + coder + session): The failed-feed outcome is half-documented. The leaf says a failed
  feed "names itself in an in-page notice"; the code closes the connection — no status line, the
  server writes a traceback, `http.client` raises `RemoteDisconnected` (pinned by
  `test_a_store_the_feed_cannot_read_fails_the_feed`) — so no notice is reachable through a failing
  feed, and `dashboard/server.py`'s docstring still claims a per-store entry. **Open decision for
  the owner:** (a) the handler answers a failure status so the notice path is real, or (b) the leaf
  states plainly that the request gets no answer beyond the closed connection. Under the owner's
  ruling (unreadable states are a user error), either is coherent.
- **R5** (PE): `devpro/dashboard/server.py:19-20`'s endpoint-map docstring still says "one per
  store that could not be read" — false since P3; the P3 doc-set search missed it because it
  searched "unreadable" and this line says "could not be read".
- **R6** (coder + PE): `definition_text.py` reports every sentence of a multi-line literal at the
  literal's opening line, and its docstring overclaims ("the line the reader opens the module at").
  Number the lines, as `_docstrings` does.
- **R7** (coder + architect): The `devpro-` prefix is spelled in four places (`AGENT_PREFIX`, the
  index script, `view.html`'s `shownName`, the child row) with no shared source; the `view.html`
  copy can rot silently. Pin equality or give it one home.
- **R8** (coder + architect, with dissent): Three pins assert inline-script substrings — form pins,
  not effect pins; the coder would retire them into served-page runtime probes, the architect notes
  they follow the established house pattern. P4's own TDZ escape showed compile checks don't
  exercise branches; the browser-eye check remains the real witness.
- **R9** (coder + architect): Tests reach the sweep's private `_split_sentences`; make it public or
  reach it through `block_sentences`.
- **R10** (PE): `_repeatable_sentence` raises an unnamed `StopIteration` when it finds no sentence.
- **R11** (coder + PE): `docstring_nodes` re-implements `_docstrings`' docstring detection — one
  helper should decide.
- **R12** (coder): `view.html`'s return-link fix uses `location.search` alone against an assumed
  same-origin path; `pathname` would survive an absolute `href`.
- **R13** (PE): `shownName` returns `undefined` for a missing name; every caller guards it — return
  `''`.
- **R14** (PE): `test_a_rendered_agent_name_drops_the_set_prefix` claims to pin the served page but
  byte-matches template source — name it a form pin (R8's question) or make it served.
- **R15** (architect, warning): `rendered_name` is unconditional, so a Bash call whose recorded
  head is `devpro-check-plan` renders as `check-plan (Bash)` — the page misstates recorded data.
  Gate the drop on the Agent tool and flip the pin that enshrines the overreach; `view.html:288`'s
  grouped-skills label renders raw names, so the commit's "every rendered-name site" claim was
  false there too.
- **R16** (architect + PE): `repo-layout.md`'s `dupe_sweep/` row says "the string literals the
  trees carry", but the code reads only the three definition areas — narrow the wording.
- **R17** (PE): The leaf's "no store it cannot read is one `stores` entry" sits awkwardly against
  its next sentence ("a store … cannot read fails the feed") — the qualifier describes a state the
  new sentence says the feed cannot survive; reword.
- **R18** (architect): `devpro/families/gemma_4.py`'s anchor paragraph is rendered prose outside
  `DEFINITION_TEXT_PREFIXES` — a known hole in the literals corpus, surfaced by the review.
- **R19** (session, from P3's report): `devpro/profiler/cli.py` and `devpro/dashboard/cli.py`
  module docstrings are 90–100% duplicated — a live sweep candidate the sweep itself reports.
- **R20** (session, from P2's report): `just test`/`just test devpro` leave `.pytest_cache` under
  the project root rather than the scratch directory the CONVENTIONS name for build outputs.
- **R21** (session): `.devpro-temp/` accumulates packages' scratch with no cleanup rule.

## Contract gaps

- **G1** (coder): Neither CONVENTIONS nor the definitions require a repository-wide check's case
  set to include one run over the real tree it polices — the gap that let R1 happen. Proposed
  line: "A repository-wide check's own case set includes one run over the real tree it polices;
  a fixture-only case leaves the check unexercised on its inputs."
- **G2** (PE): The doc-set search a delta application ends with has no synonym requirement — R5's
  stale docstring survived a search the rule mandates. A line naming synonyms ("could not be read"
  vs "unreadable") closes it.

## The owner's decisions this review rides on

The unreadable-store removal and the negative-space pin removal were owner rulings carried into
the design; no seat contested them. R4's outcome (a) or (b) is the one decision the burndown
cannot make without the owner.
