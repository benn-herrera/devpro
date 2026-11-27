# ACTIVE PLAN REVIEW

The second periodic review's findings, synthesized from the nine seats' independent reviews
(architect ×2, prompt-engineer ×2, tech-writer ×2, Python-coder ×2, and the test-suite audit seat —
the full reports are the per-seat files in the scratch directory, which carry each finding's
evidence and probes). One entry per defect; the seats that reported it are named. The prior
periodic review landed at devpro 0.17.2 (commit 69eed3ee).

## F1 — Critical: the agents-file marker's SPEC statement is a stale revision · architect-consistency

SPEC states the begin marker `<!-- vvv-devpro devpro <version> … -->` with a plugin word;
ARCHITECTURE states `vvv-devpro <version>` without it and calls SPEC's form an earlier revision's.
The two prescribe opposite handling of a file stamped by the earlier form (SPEC: not a marker,
append fresh; ARCH: recognized, replaced). The code sides with ARCHITECTURE
(`harness_agents_file.py:14`, `agents_file.py:95`). SPEC is stale and must be rewritten to the
marker the code and ARCHITECTURE keep.

## F2 — Critical: THESIS's scope claim excludes SPEC's third result · pe-consistency

THESIS's "What is new" reads "Two things, and only these," while SPEC's Must-see declares the
dicing/checks/kanban engine mandatory — thirty-plus leaves THESIS neither lists nor explains, with
no building-block row covering it. Fix: retitle and replace "and only these" with a sentence naming
dicing as delivered by absorption (git shows 0.16.0 dropped the column that would have covered it).

## F3 — Critical: package-data asset edits reach no gate · coder-conformance

A `deco.js`/`view.html`/`board.css` change passes `just test`, `test-changed` and `lint` untouched,
yet the `rendered/` slots are copies: an asset edit silently diverges the slots from source. The
gate's test-surface map and tsconfig both skip these files; no tool carries the "package-data
change reaches every slot" guarantee.

## F4 — Critical: `is_our_command` registers duplicates on opencode-shaped repos · coder-conformance

`profiler.hooks.is_our_command` recognizes only the `.claude/…` wrapper; a repo whose plugin is
opencode gets a duplicate registration on re-`init` (proved by probe: the opencode-shaped path
answers `False`). Whether `init`'s harness scope should widen is the user's call.

## F5 — Critical: the pipx tag pin is a hand-restamped ledger · tech-writer-consistency

README promises "the newest release tag" (README:64, 69-70), restamped by hand each release,
checked by nothing; no SPEC sentence carries that ledger. Either a check holds it or SPEC states
the manual step as the contract.

## F6 — Critical: README's `just` floor understates a universal requirement · tech-writer-conformance

README:50 states 1.27.0 "and 1.33.0 or later there wherever the devpro line ships" — but the
install writes the `import?` on every project install, so 1.33 applies universally; the obvious
reading understates the requirement. The guide skill already dropped 1.27.0 for this reason; SPEC
still repeats both numbers.

## F7 — Warning: the dashboard's stop and exit contracts diverge from Serving · coder-conformance

`POST /api/stop` requires `application/json` + `{}` (other senders get 415/400 and the server keeps
serving), and `serve` cannot distinguish a requested stop from a natural `serve_forever` return —
both exit 0, where Serving names exactly two intentional ends. The exit contract needs a decision.

## F8 — Warning: the install's document statements lag its behavior · coder-consistency

`renders-and-copies.md`'s managed set omits the project's agents file (and mage's `CLAUDE.md`),
the retired-package directory, and the re-entry run's pass-over of the devpro-copy row's clear —
each implemented in `install.py`, none stated where the documents describe the install.

## F9 — Warning: the profiler's read boundary has outgrown its statement · coder-conformance,
coder-consistency, test-audit

`pages.py` (1,714 lines) holds the read boundary, joins, detector, feed, templates and CLI; the
module list omits `directives.py`; no module boundary the documents name matches the code's shape.
The audit's layout proposal (below) and a stated module split are the remedy.

## F10 — Warning: the digest recognizer's rule and the seat literal are unbound · architect-conformance

The recognizer's tests plant literal banners, which the recognizer rule forbids for the install —
the rule was never grown to name the digest case, and one CONVENTIONS line settles it alongside
F14a's marker-list home; `REVIEW_SEAT` is a second home with no binding pin (its file-mate
`AGENT_PREFIX` got one).

## F11 — Warning: the periodic-review section states a trigger nothing computes · pe-conformance

The development skill's *Periodic review* counts landing commits from history — a machine guarantee
in prose: no target reads commit messages, and the span holds 818 commits against 17 matches. The
section also describes its eight-seat panel in sentences a seat cannot combine into a brief
(A4/F1). The section needs a stated counting mechanism and a coherent seat enumeration.

## F12 — Warning: SPEC's design form describes stages the skill cannot produce · pe-conformance

SPEC's design lifecycle (`stages`, `pending` entries, stage-scoped pairs) predates the current
entry form; `git log` does not settle which moved, and the claim stands unproduced by the skill.

## F13 — Warning: routes and terms name two things · pe-conformance, tech-writer-consistency

The board route is `kanban` in SPEC and `dashboard` in the skill; the "two reference pages" count
and the grammar's source disagree; "post-plan burndown" names a section, a ticket and a set of
items; README names `guide`/`profiler` where the guide routes the board to `docdicer`; the
"review-chain dispatch" term is defined only in ARCHITECTURE.

## F14 — Warning: CONVENTIONS rules the repository outgrew, and dangling cites · coder-consistency

*Scratch for tests and recipes* names a `HOME` shape no target enforces; *a narrowed format names
the inputs it refuses* cites the deleted `ACTIVE_PLAN.md §B3` — the one dangling reference — and
so does the CONVENTIONS leaf that repeats it; the spellings catalog pins line numbers in a file
that shifts; the hook-contract rule's stub coverage stands unverified.

## F15 — Warning: SPEC and README's coverage of the dashboard and re-entry · tech-writer-consistency

The dashboard root→`/board/` redirect and board-as-landing are stated in code and README but absent
from SPEC; the local-time and loopback-only rules are absent from README's dashboard section; the
re-entry install's pass-over is absent from README's Updating; kbase's prerequisites are
unreachable from README's Requirements.

## F16 — Warning: the test suite's shape — the audit's findings · test-audit

1,812 collected items; unit ~41%, contract ~19%, end-to-end ~39% — the 80% rule does not fire, but
the tier balance is inverted where it matters: heavy end-to-end over a thin unit layer exactly
where `pages.py`/`capture.py` logic lives. The big parametrized families are mostly deliberate
(each row fails differently); three genuine shotgun families named. No behavioral probe sets exist
(the sticky ticket's claim, verified), with the highest need located. Deliverable: a concrete
`tests/install/`, `tests/render/`, `tests/profiler/` layout split along package seams, ordered by
bite, no behavior change riding it — plus the ticket's missing acceptance test (same item count,
test-files-only diff).

## F17 — Note: text defects and stale statements · multiple seats

serving.md's fused sentences; the spellings catalog's line-number cites; the stale `.pyc`; the
profiler skill's *Answer* count and double binding; the guide's 0.17.x walk carried as rule and its
dead `docdicer` tools path; THESIS's plain-terms paragraph predating the shipped tooling surface;
the package docstring versus `repo-layout.md`'s absorbed-subpackage list; `.mypy_cache`'s
convention; the `.bak` carve-out and packaging-table row.

## F18 — Note: verifications left open · coder-consistency

The hook-contract rule's stub shapes, the real-tree case set, and two claims whose evidence the
seat could not read (`check-wheel.sh:48`, the opencode plugin stub) — gaps to close or retire in
the burndown.
