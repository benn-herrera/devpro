# ACTIVE PLAN REVIEW

The post-plan review of the plan "The board's running agents, the lifetime scale's durability, and
the tuning data's new home" — its work landed in commits `169c1621` (P1), `bb736606` (P2), `16626da2`
(P4), `bc3de8b8` (P3); P5's slots re-taken without a commit. Three seats reviewed what shipped
against the project documents and the accepted design: the code seat (`devpro-python-coder`), the
structure seat (`devpro-architect`) and the text seat (`devpro-prompt-engineer`). Each wrote
independently in `.devpro-temp/review-*.md`; this document is the session's synthesis, one entry
per defect, naming every seat that reported it. The burndown items group these by root cause.

## R1 — Claude dispatches never close

Reported by the code seat and the structure seat, both with probes.

`devpro/profiler/read.py`'s closing matcher ends a dispatch when a stop record's key matches the
opener's id. The claude capture drops absent fields, so a `SubagentStop` event record carries no
`tool` and no `child_agent_id`; the matcher reads the *parent session id* where a claude dispatch's
id is the `Agent` call's `child_agent_id`. The stop record's own `agent_id` — the key the session
page's stop join already reads — names the child, and is what the matcher should read. Consequence:
every claude `Agent` call ever recorded shows as running forever, and the five new derivation tests
use opencode records only — the claude half of the derivation has no coverage.

## R2 — Dispatch hue is neither stable nor distinct

Reported by the code seat and the structure seat, both verified by probe.

The hue is the dispatch's place in the *current* running set (`place % 8 + 1`), so closing an
earlier dispatch re-colors every later one, and a ninth running dispatch wraps to a shared color —
against the two leaves' "each running dispatch has its own color … stable while it runs". The
pinned test covers only the opens half. Fixing it settles a real tension the leaves do not resolve:
under a records-only derivation, absolute stability (assign at open, hold by id) costs distinctness
when more than the palette runs, and the leaves claim both. The burndown fix must state which
promise holds — a decision nothing written settles, for the plan's owner.

## R3 — The board page breaks in planning mode, and both column sets contradict the contract

Reported by the structure seat.

With a design present and no `in progress`/`landed` row — the normal pre-execution state — the page
throws while drawing: planning drops the Design column from the payload's columns, but the script
still appends design cards to that column's list (`lists.get(DESIGN)` undefined). Whole board
renders as "not drawn", and no Python test reaches it. Both modes also diverge from the columns
delta as applied: the code keeps Roadmap in execution (SPEC: it goes) and drops Design in planning
(SPEC: it stays). The code's own comment states the opposite of the SPEC verbatim. One
reconciliation fixes both modes and the break together.

## R4 — The dispatch-note duty is unsatisfiable as ordered

Reported by the text seat and the structure seat.

The development skill's Dispatch bullet has the session write the dispatch note "before the agents
go", but the identifier the note carries exists only once the capture records the dispatch —
post-call — and nothing states which read yields it or who writes the row when the child also
writes the plan. The duty anchors at the wrong moment: it should anchor at the dispatch's return,
stating the capture read the note is written from.

## R5 — The tuning table's placement and stock wording are wrong in the leaves

Reported by the code seat, probed on a fresh install.

Both leaves say the table is written "at the install destination's root"; it is written under the
install directory beside the rendered definitions (`<project>/.claude/skills/devpro/tuning.md`,
`.opencode/plugins/devpro/tuning.md`) — the placement that the wholesale replacement actually
replaces, and the one to keep. The `stock=` description also mismatches: the SPEC sentence says the
table records "the categories whose member the family has no member-scoped tuning text for", while
the code writes the full category list. Whichever semantics is right, leaf and code must say the
same thing.

## R6 — The agents-column wording and the code it describes disagree

Reported by the text seat, the structure seat and the code seat.

A card's `model` reads the opening record — the *dispatching session's* model under opencode —
where the SPEC leaf promises "the model it runs"; the step-down scheme makes that routinely wrong.
The SPEC leaf's own link sentence is self-contradictory about which page a claude card links. The
plan-status-form leaf uses "identifier" without defining it, and live-following says "every record
file beneath the stores" is watched while the code watches the two directories and reports the
store path. The *Shipped files* citation the agents-column leaf leans on does not state who reads
the stores. Root cause: wording applied from the design where the design under-specified what the
derivation could know.

## R7 — A pin that cannot fail

Reported by the code seat.

`tests/render/test_frontmatter.py` names a test for the install's write of the tuning table, but
asserts `tuning_table` against a re-spelling of itself — `install.py`'s write line could be deleted
and the test still passes. The install write has no pin; the test needs to run the install (or read
what an install produced).

## R8 — Notes: stale enumerations and small drifts

Reported variously; each is a wording or pin drift, no behavior behind any.

- `serving.md` still enumerates the payload without `mode`, `agents`, `dispatch_colors`, and
  `renders-and-copies.md` does not know the tuning table as a write site (structure, text seats).
- The palette size is pinned in two code homes (`DISPATCH_HUES = 8`, the CSS `--c0…--c7`) with no
  test holding them together (structure seat).
- The board's read path parses the plan twice per board read; carrying `Plan` on the read model
  drops the parse and the window where `board` and `mode` disagree (code, structure seats).
- P5's status-table note ("no closing commit: untracked output") can be read against the
  transient lifetime's "never committed" prose; the note's wording could say the output is
  untracked rather than the package uncommitted (text seat).
- `tuning.md`'s byte-exactness across installs is unpinned (text seat).
- `render_diff.py`'s unchanged-shapes list lost the file-ends-before-the-fence case;
  `directives.py`/`profiler.ts` carry a restated comment; the justfile doc block still says
  "one of the two frontmatter banner shapes"; `board.js` reads `pkg.dispatch_colors` with no
  older-payload guard; one board-panel test writes a store beside the conftest helper (code seat).
