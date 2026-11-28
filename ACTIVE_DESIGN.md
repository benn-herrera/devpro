# Process consistency and internal self-alignment (MB1–MB17)

devpro's rendered process — the agents-file block, the development and guide skills, and the agent
definitions — states each of its rules consistently everywhere it is restated: unstaging that
touches only the index is allowed, the periodic review fires on one trigger and the fan-out on one
bindable cap, every seat carries the project-documents precedence and one severity ladder, the
security-to-architect pipeline is retired, and drafting, stale-plan revision and command aliasing
state the boundary or principle each was missing. The change lands in the generator source; the
rendered files are not edited. For the sessions and agents that run the process, and for the
operators and users who read it.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

## ARCHITECTURE delta

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

The leaf names three skill modules without the `skills/` package segment they moved under:
`definitions/development.py`, `definitions/profiler.py` and `definitions/guide.py` are today
`devpro/definitions/skills/development.py`, `devpro/definitions/skills/profiler.py` and
`devpro/definitions/skills/guide.py`. Three pairs:

**As it stands:**

```
- **Profile skill** — `profiler` (`definitions/profiler.py`): one `SKILL.md` with no
```

**Becomes:**

```
- **Profile skill** — `profiler` (`definitions/skills/profiler.py`): one `SKILL.md` with no
```

**As it stands:**

```
- **Guide skill** — `guide` (`definitions/guide.py`): one `SKILL.md` and two supporting files,
```

**Becomes:**

```
- **Guide skill** — `guide` (`definitions/skills/guide.py`): one `SKILL.md` and two supporting files,
```

**As it stands:**

```
- **Development skill** — `development` (`definitions/development.py`): one `SKILL.md` and seven
```

**Becomes:**

```
- **Development skill** — `development` (`definitions/skills/development.py`): one `SKILL.md` and seven
```

One discrepancy this design does not act on, for the plan to settle: CONVENTIONS.md's
[Version has one home](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/version-has-one-home.md)
leaf states `README.md`'s pipx line carries a hand-kept `@v<version>` tag, and `README.md`'s pipx
install line carries no tag at all. The plan settles which side moves — the README line gaining the
tag or the leaf's claim dropping it — and lands the correction in its change; no delta of this
design edits either file.

## Code delta

### [Rendering](PROJECT_DOCS/ARCHITECTURE/rendering/index.md) — MB6a: the precedence span states the owner's intent (user decision, 2026-11-27)

The MB6 span's "no list of qualifying documents and no carve-out" is badly worded, per the
owner: the intent is that **any** project document *might* override some element of the
process — a project document is, by definition, more specific about the project's needs than
the general process is — and "the project docs" (THESIS, SPEC, ARCHITECTURE, CONVENTIONS) is
not a special set with that power. There is no special set of documents with this property;
any project can be constructed however it needs to be. The review's R3 (the carve-out
ambiguity), W7 (heading narrower than body) and W8 ("the code you change" carried by
non-coding seats) are all this one wording defect. The decision: fix the wording — **with the owner's own words**, the whole span:

```
This is a general process, but individual projects may have specific needs. A project's
documentation of those process needs is higher precedence when it conflicts with the general
process.
```

The rendering leaves' statements about shared text stay true: the span is one constant,
carried by every agent definition, no copy in the agents-file block.


### [Agents File](PROJECT_DOCS/ARCHITECTURE/agents-file.md) — MB1a: the git ban allows index-only unstaging

`devpro/definitions/harness_agents_file.py`'s Shared working tree bullet bans `restore` and `reset`
by name, and the development skill's Dispatch section requires unstaging another package's staged
path before a commit — the two texts collide. The ban is restated by effect: the working tree is
what it protects, and the index-only unstaging forms are allowed. The bullet becomes:

```
- **Never run a git command that rewrites the working tree** — `stash`, `checkout`, `clean`, and
  every `restore` or `reset` form that touches the working tree. Unstaging a path before a commit
  (`git restore --staged <path>`, `git reset <path>`) touches the index only and is allowed. A
  working-tree rewrite reaches every file, including ones another agent is editing now, and the
  damage is silent from where you sit: that agent's next write fails against content it did not
  author or lands on top of your revert. For a baseline, read the committed side with
  `git show HEAD:<path>` or work in a separate worktree.
```

### [Agents File](PROJECT_DOCS/ARCHITECTURE/agents-file.md) — MB7: the U+2028 escape bullet is removed

The Coding list's bullet "The edit and write tools write JSON escapes for U+2028/U+2029 as raw
characters; spell those code points another way…" is deleted from
`devpro/definitions/harness_agents_file.py` and kept nowhere: the owner's decision is deletion
outright, the process stays general, and no other text cites the bullet. Nothing replaces it.

### [Agents File](PROJECT_DOCS/ARCHITECTURE/agents-file.md) — MB14: the stale-plan revision gets its boundary

The Acting on the user's words bullet that permits correcting a stale plan, handoff or status file
without a quote states no boundary today. It is restated with the boundary drawn by what the
revision does; the plan stays named in both of the block's working-document lists (the
bookkeeping bullet and this one), so no other line moves. The bullet becomes:

```
- **Keeping those documents current needs no quote at all.** Correct, rewrite or retire a stale
  plan, handoff or status file on your own initiative, so long as the revision keeps it true to
  what was approved — status, stale facts, corrections, splitting a package, rewording a step for
  executability; substantive text changes still get the skill's review of the changed text, and a
  change to what was approved — scope, a requirement, a settled decision — is the user's. Asking
  spends a turn on something nobody would refuse. It is your working surface, not the product, and
  this never reaches SPEC, ARCHITECTURE, CONVENTIONS or any other contract document.
```

### [Agents File](PROJECT_DOCS/ARCHITECTURE/agents-file.md) — MB16: the command-alias rule states the principle

The Coding list's shell-alias bullet names `rm`, `cp`, `mv` and `ls` as the whole set an operator's
profile may alias. It states the principle and keeps the four as examples. The bullet becomes:

```
- **The shell tool carries the operator's interactive aliases.** Its shell is non-interactive, yet
  an alias like `rm -i` still fires there and blocks on a prompt nobody answers. Tool commands and
  dispatched instructions call any command the operator's profile may alias through `command` —
  `command rm`, `command cp`, `command mv` and `command ls` are examples, not the whole set.
  Scripts on disk run under their own shebang and are unaffected.
```

### [Agents File](PROJECT_DOCS/ARCHITECTURE/agents-file.md) — MB12: the Must-see rule in the repository's own `AGENTS.md` states its coverage

The target is the repository's own `AGENTS.md` — the hand-maintained tail outside the rendered
block, not a `PROJECT_DOCS` leaf and not generator source. Its Must-see rule for `PROJECT_DOCS/`
entry points states no coverage; the rule's first bullet is replaced by the two below (each one
line, at most 120 characters, as the rule itself requires):

```
- Each PROJECT_DOCS/ subtree entry point (SPEC, ARCHITECTURE, CONVENTIONS) has "Must-see:" before any H2 or 'Contents:'
- The omnibus root PROJECT_DOCS/entry-point.md (THESIS) is exempt; its opening "does not" list is its critical content
```

Sub-choice, settled: coverage is stated and the root is not unified onto the Must-see form. The
root entry point is the THESIS document itself, not a routing hub — a Must-see section inside it
puts routing chrome inside a document that reads whole, and its critical content already exists as
its opening "This thesis does not" list. Stating the exception costs two hand-written lines;
unifying costs a structural change to the THESIS document for no reader gain.

### [Rendering](PROJECT_DOCS/ARCHITECTURE/rendering/index.md) — MB6: one precedence span, carried by every seat

The precedence of the project's own documents over the rendered process is stated today in partial
copies: `clauses.PROJECT_CONVENTIONS_OUTRANK` ("Project conventions outrank general practice")
reaches only the coder and platform-expert stacks, and twelve definitions — architect,
security-reviewer, tech-writer, prompt-engineer, ml-engineer, applied-mathematician,
biz-dev-strategist, economic-historian, literature-scout, marketing-comms-expert, prose-architect,
theoretical-economist — carry no precedence text at all, though an agent definition is the only
text a subagent loads. The change makes one span, worded generally, carried by every agent
definition:

- In `devpro/clauses.py`, `PROJECT_CONVENTIONS_OUTRANK` is reworked into the general precedence
  clause and renamed `PROJECT_PRECEDENCE`:

  ```python
  PROJECT_PRECEDENCE = """**The project's own documents modify the process.** What this definition carries is the general approach; a project's own document is more specific and knows its own needs. Where a project document states something that departs from what is written here, the project's document governs — its INVARIANTs included — and you follow it rather than converting the project to what is written here; there is no list of qualifying documents and no carve-out. For the code you change, the project's statements in place — a file's own header or prelude, the settled style around your change — govern the same way. Where the project states nothing, what is written here is what you bring."""
  ```

  The name changes because the clause no longer names CONVENTIONS.md or only conventions; the
  clause-group tables in `tests/test_clause_groups.py` name no entry for it (it is reached only
  inside the stacks), so the rename touches no test table — the clauses.py comments that name the
  old constant and its two inline continuations are updated with it.
- The coder and platform-expert stacks (`CODE_PRINCIPLES_CODER`, `CODE_PRINCIPLES_PLATFORM`) embed
  `PROJECT_PRECEDENCE` where `PROJECT_CONVENTIONS_OUTRANK` stood, last. The two inline continuations
  that follow the span are settled here. python-coder's continuation survives as written — "PEP 8
  is the baseline that applies when the project states nothing." still reads after the span's
  closing sentence. shell-dsl-coder's continuation repeats the span's "a file's own header"
  phrasing and names CONVENTIONS.md, which the new span retires; it becomes:

  ```
  For shell, those statements are the `set shell` line of the runner file and the variable prelude
  of the script you touch: flags, naming schemes and output conventions live there, not here.
  ```
- The twelve definitions above interpolate `{clauses.PROJECT_PRECEDENCE}` as a paragraph of their
  own, directly after the body's opening paragraph. Seven of them lack the `clauses` import today —
  `biz_dev_strategist.py`, `economic_historian.py`, `literature_scout.py`,
  `marketing_comms_expert.py`, `prose_architect.py`, `theoretical_economist.py` and
  `security_reviewer.py` — and gain `from devpro import clauses`; the other five import it already.
- The development skill's opening sentence ("Where the project's CONVENTIONS.md states a local rule
  that departs from a rule here, the project's rule governs.") is replaced by the same span, so the
  precedence is stated once, generally, at the skill's opening too, and no narrower
  CONVENTIONS-only form survives anywhere.
- The agents-file block's project-documents list describes CONVENTIONS.md as "project-specific
  additions to house rules and practices"; it becomes "project-specific modifications to house
  rules and practices" (`devpro/definitions/harness_agents_file.py`). The block carries no copy of
  the precedence sentence itself: a definition's prompt is the definition taken together with the
  agents file, and a span in both fails the no-shared-clause-twice-in-one-prompt check.

### [Rendering](PROJECT_DOCS/ARCHITECTURE/rendering/index.md) — MB13: one severity ladder across the reviewer seats

`clauses.REVIEW_SEVERITY` already carries the when-cost-lands ladder for the sixteen coder and
platform seats (through `WHEN_REVIEWING_SECTION`); tech-writer and security-reviewer carry a
fit-for-purpose ladder with a "prefer Critical" tie-break, the architect a short form of it, and
ml-engineer carries no severity text. The ladder unifies on the shared constant, which gains the
tie-break in the owner's reformulation:

```python
REVIEW_SEVERITY = """**Severity by when the cost lands**: Critical — wrong or unsafe as shipped; Warning — a rule broken, the cost falling on the next change or reader; Note — correct code, local tidiness. When uncertain which severity a finding takes, name the one whose cost lands sooner."""
```

- `tech_writer.py`: replace the `### Severity Calibration` body (heading kept) with the shared
  constant and one domain sentence:

  ```
  {clauses.REVIEW_SEVERITY} A document's Critical is a reader who cannot succeed: a flatly wrong
  claim, a load-bearing instruction that does not work, a missing prerequisite.
  ```

- `security_reviewer.py`: replace the `## Severity Calibration` body (heading kept) with the shared
  constant and one domain sentence:

  ```
  {clauses.REVIEW_SEVERITY} A hazard's Critical is the exploitable one with a realistic attack
  scenario; a real hazard whose exploitation needs unusual conditions or yields limited impact is
  a Warning.
  ```

  The section headings stand, so the "severity per the calibration above" references in both
  definitions' output formats stand with them.
- `architect.py`'s Review Process item 2 ("**Classify severity**: Critical (significant problems,
  blocking), Warning (meaningful risk/cost), Note (minor concern)") becomes
  `**Classify severity**: {clauses.REVIEW_SEVERITY}`.
- `ml_engineer.py` gains nothing: it is not a reviewer seat — it delivers a specification plus the
  measurement that would falsify it and attacks its own draft before delivering; it writes no
  findings for another seat and carries no severity text today.

### [Structural rules](PROJECT_DOCS/ARCHITECTURE/rendering/structural-rules.md) — MB9: the venv-probe sentence reaches only the Python-probing seats

`clauses.verification_evidence()` bakes the `python -c` / venv / `PYTHONPATH=` / stale-bytecode
sentence into its body, so all eighteen definitions that carry the clause render it — including
seats that never run a Python probe, and the architect, whose copy instructs a seat that "neither
builds nor runs". The change parameterizes the sentence within the function's three-keyword-only
limit:

- The sentence becomes the constant `clauses.VENV_PROBE_RULE`.
- `verification_evidence()` takes a third keyword-only parameter, `probe_rule`, defaulting to the
  empty string, composed onto the paragraph's end (its leading space included where non-empty, so
  the empty default leaves no dangling space). The docstring's note about which arguments exist for
  a seat with no Bash is extended to name the third.
- `python_coder.py` and `ml_engineer.py` — the seats that run Python probes — pass
  `probe_rule=clauses.VENV_PROBE_RULE`. Every other call site stands unchanged and renders without
  the sentence; the architect's call keeps its two custom arguments and loses the sentence with no
  edit of its own.
- The leaf's rule — "a `clauses.py` function takes at most three keyword-only parameters" — stays
  true: the function takes exactly three.

The exact text cut, byte for byte, from the `verification_evidence()` f-string in
`devpro/clauses.py` — the sentence with its leading space, following "…not every look around." in
the composed paragraph:

```
 A probe that imports this repository's package first and runs it later — a `python -c`, a one-off script — runs under this repository's own venv interpreter with `PYTHONPATH=.`, or in a fresh process, because an edit made after the first import leaves stale bytecode masking it.
```

It is cut from the f-string and becomes the body of the new constant:

```python
VENV_PROBE_RULE = " A probe that imports this repository's package first and runs it later — a `python -c`, a one-off script — runs under this repository's own venv interpreter with `PYTHONPATH=.`, or in a fresh process, because an edit made after the first import leaves stale bytecode masking it."
```

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), Development skill — MB2: the periodic review's trigger is one condition

`devpro/definitions/skills/development.py`'s Periodic review section states the trigger as two
rules that contradict in one bullet ("the next plan is a periodic review, before any other plan is
made active" against "the review also waits for a coherent feature boundary"). The section's first
bullet becomes one trigger whose two conditions are met together:

```
- The periodic review waits for one trigger whose two conditions are met together: the
  {PERIODIC_REVIEW_INTERVAL_TERM}'s count of plans has landed since the last periodic review, and
  a coherent feature boundary is reached — where a project carries incomplete work split across
  plans, the interval's being met is not enough. Other plans may be made active until both hold.
  It looks past single changes, at what has accumulated across them. *Purpose:* drift that no
  single change caused accumulates whether or not anyone looks, and is found on a count the
  process keeps, not when someone remembers; and the review's product is high-level signal about
  the whole project, which a project mid-flight buries under undone work that is not signal.
```

The guide skill restates the old form in two bullets and both move with it:
`devpro/definitions/skills/guide.py`'s periodic-review Due bullet —

```
- **Due** once the periodic review interval's count of plans (this page's *Getting started*) has
  landed since the last periodic review, counted from the landing commits' messages. A review the
  user directs over accumulated work is this same review.
```

— states the interval-only trigger with no boundary condition, the same contradiction MB2 removes;
it becomes:

```
- **Due** when two conditions are met together: the periodic review interval's count of plans
  (this page's *Getting started*) has landed since the last periodic review, counted from the
  landing commits' messages, and a coherent feature boundary is reached. A review the user directs
  over accumulated work is this same review.
```

and the bullet after it, "**What it holds up:** when due, the next plan made active is the periodic
review, before any other. A request can still be designed; its plan waits." becomes:

```
- **What it holds up:** until both conditions hold, other plans run. A request can still be
  designed; its plan waits.
```

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), Development skill — MB3: the count target is named without naming a runner

`devpro/definitions/skills/development.py`'s Periodic review section names "the runner target
`just plan-count`", assuming a justfile where the install supports justfile and Makefile projects.
The bullet opens "The {PERIODIC_REVIEW_INTERVAL_TERM}'s count is what the runner target `just
plan-count` prints:" and now opens "The {PERIODIC_REVIEW_INTERVAL_TERM}'s count is what the
`plan-count` runner target prints:"; the rest of the bullet stands.

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), Development skill — MB4: rendered process text cites no devpro source path

`devpro/definitions/skills/development.py`'s Dispatchability bullet cites the clause by symbol and
source path — the only such citation in rendered text; the coder and platform-expert definitions
carry the clause as the interpolated constant. The parenthetical is dropped:

```
- a package that adds a test names the defect the test fails on, by the test-precondition clause
  the coder and platform-expert definitions carry. *Purpose:* an order for a test with no named
  defect is refused before a dispatch exists;
```

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), Development skill — MB5: a bindable concurrency cap governs fan-out

The Dispatch section's fan-out rule keys on "the most capable model the installed agents name" —
a cost threshold that does not generalize, and a go that conflicts with an approved plan's
authority. The change resolves it as: a bindable term, `concurrent
dispatches`, default 4, counting every agent running at once (each instance of the same agent
separately), governing within an approved plan.

- In `devpro/definitions/skills/development.py`, a new term constant joins the Terms section's
  module-level constants: `CONCURRENT_DISPATCHES_TERM = "concurrent dispatches"`. In
  `devpro/clauses.py`, `CONCURRENT_DISPATCHES_DEFAULT = "4"` joins `VALUE_CONSTANTS`, beside the
  plan size limit and periodic review interval defaults it sits beside in the table.
- The *Bindable terms* table gains the row (the term has a default, so `project-setup.md` asks for
  it nowhere and stands unchanged):

  ```
  | {CONCURRENT_DISPATCHES_TERM} | {clauses.CONCURRENT_DISPATCHES_DEFAULT} | the agents that may run at once, each instance of the same agent counted separately; a dispatch that would exceed it waits for a go naming the count |
  ```

- The Dispatch bullet becomes (the "state the agent count and model" step stands, and every mention
  of the term interpolates the constant, per the skill's term rule):

  ```
  - Before dispatching, state the agent count and model. A dispatch that would raise the count of
    {CONCURRENT_DISPATCHES_TERM} past the cap — {clauses.CONCURRENT_DISPATCHES_DEFAULT}, or the
    number CONVENTIONS.md binds it to — waits for a go naming the count. The cap counts every agent
    running at once, whatever its model, each instance of the same agent separately, and it governs
    within an approved plan: up to the cap, the plan's dispatches need nothing further. *Purpose:*
    a fan-out's cost shows only once it is spent.
  ```

- The guide skill restates the old rule and moves with it: `devpro/definitions/skills/guide.py`'s
  "When the session asks the user anything" bullet "- a go for more than one agent at once on the
  most capable model the installed agents name. It names the count; answer with the count: "Go,
  3 agents."" becomes:

  ```
  - a go for a dispatch that would raise the number of agents running at once past the cap the
    development skill states (*Dispatch*). It names the count; answer with the count: "Go, 3 agents."
  ```

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), Development skill — MB15: the architect drafts the post-plan burndown items

The Post-plan review section's drafting ticket makes the session the worker ("Drafting the items
edits the plan, so the session is the worker"), contradicting the first-draft and periodic-review
rules that give the architect the draft. The ticket's work becomes a dispatch to the architect,
from the review document; the usability review, the revision and the rows' movement through the
states stay with the ticket:

```
- The drafting ticket's work: a dispatch to the {clauses.ref(name="architect")}, which drafts the
  section's items from the {REVIEW_DOCUMENT_TERM} — work packages under the section, one per
  root-cause group, each with its own ID, status-table row, rating and one-commit close — then one
  `{clauses.ref(name="prompt-engineer")}` usability review over the drafted items together, the
  revision applied, and each item's row set by its state. The session drafts the items itself only
  when the user asks the session itself to, and a request for the plan is not that ask. The
  ticket's row still moves through the states. *Purpose:* the burndown items' real dispatches are
  visible on the board, each with its own rating.
```

The current sentence "Drafting the items edits the plan, so the session is the worker" is removed
with the rewrite: the replacement above replaces the whole bullet, that sentence included, and
nothing of it survives.

The guide skill restates the old ownership and moves with it: `devpro/definitions/skills/guide.py`'s
burndown bullet "…holding its drafting ticket; the session drafts the burndown items from
`ACTIVE_PLAN_REVIEW.md` into the section…" becomes "…holding its drafting ticket; the session
dispatches the architect to draft the burndown items from `ACTIVE_PLAN_REVIEW.md` into the
section…", the rest of that bullet standing.

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), Development skill — MB17: the session drafts only on the user's ask

All three drafting rules state the same boundary in the same terms — the session drafts on the
user's ask to the session itself, and otherwise dispatches the owner; a request for the plan is not
that ask. The first-draft bullet's "writes no draft of its own" reads as barring collaboration; the
boundary sentence replaces it. This entry states the two sites whose text it changes alone; the
burndown site's sentence is carried in the MB15 entry's replacement text above.

- The Plans section's first bullet becomes:

  ```
  - The plan's first draft is the {clauses.ref(name="architect")} definition's to write: the session
    dispatches it — from the accepted design where one precedes the plan, from the findings where
    none does. The session drafts a plan itself only when the user asks the session itself to, and
    a request for the plan is not that ask. *Purpose:* the plan is written by the seat that also
    reviews and revises it, so one discipline owns the artifact, and what the session approves is
    that discipline's output.
  ```

- The Periodic review section's drafting sentence "that drafting is the
  {clauses.ref(name="architect")} definition's to write, not the session's, and the drafted items
  take the…" becomes "that drafting is the {clauses.ref(name="architect")} definition's to write —
  the session drafts it only when the user asks the session itself to, and a request for the plan
  is not that ask — and the drafted items take the…", the rest of the sentence standing.

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), Development skill — MB1b: the unstaging the skill requires names its index-only commands

The Dispatch section's shared-tree bullet requires unstaging another package's staged path before a
commit and names no command, so the reader meets the agents-file ban without the allowance in hand.
The bullet's middle sentence becomes:

```
- When dispatches are concurrent, a package stages and commits only its own paths
  (`git commit -- <paths>`), never the shared index whole; where the index holds a path another
  package staged, that path is unstaged before the commit (`git restore --staged <path>`, which
  touches the index only), or the commit waits. *Purpose:* disjoint edits stay disjoint when two
  agents share a working tree — a commit that reads the whole index either carries another
  package's work or leaves it behind.
```

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), seats — MB8: the prompt-engineer claims no plan or design-note authorship

`devpro/definitions/agents/prompt_engineer.py` claims plans and design notes as its to write — in
its description ("…skills, agent-facing docs, and the design notes and plans agents execute from…")
and in its Scope section ("A plan or design note written for agents to execute from is yours to
write.") — where the development skill gives the plan's first draft to the architect so one
discipline owns the artifact. Two changes:

- The description's authorship list drops "and the design notes and plans agents execute from", and
  its reviewer sentence takes them in: "Reviewer seat for the same, and for the design notes and
  plans agents execute from — reports findings, modifies nothing."
- The Scope line becomes: "A plan or design note written for agents to execute from is yours to
  review, not to write." Its Doc review section — the review seats for designs and plans — stands
  unchanged.

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), seats — MB10: the security-findings pipeline is retired

Neither definition describes a security-to-architect handoff or a burn-down list; the security
reviewer, invoked on request, reports like any other reviewer seat, and the architect's Security
review dimension applies in every review.

- `devpro/definitions/agents/security_reviewer.py`: the opening paragraph's "find hazards, identify
  what it takes to eliminate them, and hand that to the architect to integrate into design" becomes
  "find hazards, identify what it takes to eliminate them, and state each as a condition a design
  must meet — you do not prescribe design solutions"; the "Do not say 'consider using X library'…
  That is the architect's job" division-of-labor text stands. The "## Invocation Context" section
  (the findings-are-handed-to-the-architect paragraph) is removed whole.
- `devpro/definitions/agents/architect.py`: the description drops "Synthesizes security findings
  into unified burn-down lists."; the artifacts list "Initial designs, review reports, burn-down
  lists and plans" drops "burn-down lists"; the Pre-output Reasoning lead becomes "Before
  committing invariants or a skeleton, work through these steps explicitly:" — dropping the third
  item alone would leave "Before committing invariants, a skeleton, work through…", a comma splice;
  the paragraph "For burn-down synthesis after a security review's findings, additionally
  walk each security finding…" is removed; the Security review dimension's skip condition
  ("— *Skip this dimension when a security review's findings are being provided…*") is removed, so
  the dimension applies without the condition; and the "## Integrating Security Findings" section
  is removed whole, its burn-down list item format and retraction rule going with it.

### [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md), seats — MB11: the stale clarifying-question clause is gone

`devpro/definitions/agents/generalist_coder.py`'s "Understand the task" bullet asks a dispatched
agent to "ask one clarifying question before proceeding" — a turn a dispatched agent has no
moment for, and a clause no other coder carries; the Blocker path its Output Format already
carries covers unclear scope. The bullet becomes:

```
**Understand the task**: where the scope or requirements are unclear, report as a Blocker — don't
guess and expand.
```
