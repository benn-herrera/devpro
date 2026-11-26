# ACTIVE DESIGN

## Drafts

### A strict type-check gate for the Python

`just lint` checks the shipped TypeScript against the host's published declarations, but the
Python rides on convention: nothing machine-checks a name, a signature or a record field across
`devpro/` and `devtools/`, so every reference check is model attention, spent fresh each time it
is needed. The change: mypy or pyright in strict mode over the Python, pinned like the venv's
other tools so a checker release cannot change what the gate reports with no change here, wired
into `just lint` as a gate — the point is that the generate → vet → revise cycle carries a
mechanical vet the work can rely on being there every time, not a standard maintained by voluntary
care. The tests are the open surface: fixture and conftest indirection is where a checker helps
least, so the gate lands over the package and devtools first and takes `tests/` only where the
signal proves worth the quieting it demands. What it does not buy: type checking catches reference
and type drift, not the conceptual load — the documents' interlock with the code stays attention
work regardless.

### Group traces with plans — the operational-context stamp

Sessions recorded by the profiler carry their operational context, so the dashboard can answer
what happened under what set of operational directives and when — before-and-after comparison for
an agent or skill tuning being the use the whole forensic layer serves. The stamp binds three
things to each trace group at capture time: the plan the session worked under; the directives
state in effect — a fingerprint of the installed agent and skill definitions and the agents file,
taken once per session start, so two sessions under the same plan but different definitions are
distinguishable; and the session's start time, which orders the fingerprint transitions: before
and after a tuning change are defined by observed transitions in session order — the sessions
through the last carrying the old fingerprint are before it, those from the first carrying the new
one are after it — the change moment bounded by the sessions either side, not exact. A change no
session straddles is invisible and no defect: the sessions are the only observers of directive
state, and the comparison needs the partition, not the moment. Open decisions for the pass's own
design work: the fingerprint's exact scope and mechanism, how association renders in the
dashboard's index, and whether pre-stamping traces get inference-based association marked as
inferred. Rides after the attribution pass: capability layers land in order, each on the clean
foundation the previous layer left.

### Nested agent fan-outs read as the process, or the detector names them

The one-level dispatch shape the process keeps — every agent-facing brief crossing the
main session's reviewable chain (draft, PE review, revise, dispatch with a named package and a
state cell) — holds while agents are dispatched directly from the main session. Nested fan-outs
(an executor dispatching its own reviewers and workers) can be legitimate exactly when the trace
reads as the process working: the executor drafts its brief, dispatches its own PE review,
revises, and only then dispatches the worker — every step a named agent call the profiler's
capture already records. Two halves, one ticket: a detector that walks the flat profiler stores
for any Agent row whose child session dispatched further agents, reporting one whose trace
carries no review chain beside it (the unreviewed fan-out — today caught by nothing), and the
attribution render showing the depth-2 chain itself, so the board reader sees the process
working rather than that something ran. The index stays one level deep (the flat table of
sessions); the session page is the depth view. Rides after the attribution pass, whose
grouping and child pages this extends.
