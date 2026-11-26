# ACTIVE_PLAN_REVIEW — post-plan review of the profiler/install/index plan

The four seats reviewed the changes independently (`git diff 772e47f3..HEAD`): typescript-coder,
python-coder, architect, prompt-engineer. This document is the synthesized account — one finding per
defect, naming every seat that reported it. Findings are grouped by root cause; the plan's burndown
items cite these IDs. Reviews in full live in `.devpro-temp/p6-review-*.md` (scratch, untracked).

## R1 — the `running` render flag is dead on every path (typescript-coder, python-coder, architect)

`pages.py`'s `with_stop` narrows its `running` branch by re-testing `LAUNCH_NOTICE` against
`call.get("result")` — but on the notice path `call` is the result-stripped mapping (never matches),
and claude's current background launches record `result` as the `async_launched` JSON
(`capture.py:336`, `:103–108`; the notice string was an older shape), so the branch is dead for claude
too. Effects: a still-running claude background dispatch renders as finished with the launch cost as
its duration; the opencode dispatch avoids the mis-render only by unreachability, not by the intended
harness test; and no test pins either path, so the suite stays green over the defect. Fix: key the
opencode exclusion on the record's `harness`, keep `call.get("background")` for claude, and add the
failing tests both ways.

## R2 — a stopped claude background subagent still renders "runs in the background" (python-coder)

The stop merge keeps `background` and never clears the running flag, so a *stopped* claude background
subagent's row carries the running wording. Same flag family as R1; fix together — the stop path
ends the running state it once began.

## R3 — the episode-end signal's semantics are undecided where the leaf states them (typescript-coder)

A child that dispatched its own background work idles with a non-empty `background` array; whether an
empty-background idle follows (the wake after that work) and when, is the host's runtime behavior, not
a documented contract. The span the join computes may therefore include background-wait time, and the
recorded count discards the listing's `kind`/`sessionID`, so no reader can recover what was
outstanding. The leaf states the signal as contract; the design decision it needs — which idle ends a
child, and what the span then means — is the burndown's to make explicit, with tests writing the
decided shapes both ways.

## R4 — the idle stamp breaks the capture's own record invariants (typescript-coder)

`eventRecord` adds `agent_type`/`model`/`background` keys conditionally while the capture's stated
invariant is every field present on every record; the idle stamps the agent/model of the last
`model.request` of *any* `kind`; `String(request.agent)` can persist the literal `"undefined"`; and
the stamped `background` is a count where claude's record field is a bool, read by one predicate in
`pages.py`. Fix with the schema's own conventions: every key present, absent inputs recorded as
`null`, the kind filter applied at the stamp.

## R5 — the `episodes` threading misses its read-boundary seam (architect, python-coder)

`child_episodes`' result threads through nine signatures (`pages.py`, `server.py`) with silent
`None` defaults, and server.py duplicates the comprehension `pages.py` already performs; the design's
own "join at read" points to computing it once at the `read_sessions` boundary. The map also keys on
`session` alone, so a cross-store join rides on id spelling across stores. Fix: compute at the read
boundary, thread nothing, and scope the key to what the store names (harness or store identity with
the session id).

## R6 — leaf-claim accuracy over the changed leaves (prompt-engineer; architect corroborating)

The applied text and its neighbors carry: `install/opencode-entry.md` describing the idle as
registered "for a session whose `parentID` is set" beside the capture leaf's unconditional child idle
(two leaves, two registrations, one reader misled); "the capture's declared session hooks as they
report" (unresolvable phrasing); a degrade instruction restating the positive rule three lines below;
"an opencode record's `model` … at capture alone" no longer covering dispatch records; serving.md's
em-dash aside that is not the consequence of the "so" it sits in; `child-record rows` where the page's
own label reads `child rows`; SPEC's `tools/devpro/` lacking its install-directory anchor; the store
path spelled two ways; and opencode-entry.md's pre-existing "three hooks" count. One pass, one commit.

## R7 — the minimum-specificity bullet's second sentence overstates its first (prompt-engineer)

"…never transcribes it" forbids what the first sentence's own test admits (a reader who must *check*
the form). Revise to: transcribes it only where the document's reader must check that form. The
bullet lives in the development skill's definition; the change re-renders with the next install.

## R8 — re-entry edges the tests do not reach (python-coder)

A symlinked copy destination is cleared and written through into whatever it names (refuse the
symlink, naming the path); a user-level re-entry reports "up to date" and is untested; and the
wrapper's recorded interpreter can never update on a re-entry run — a consequence the contract should
state in `shipped-files.md`, with the proposed sentence the seat drafted. Plus test-wording pins to
cut (`not "running" in tree.stdout`).

## Noted, no finding

The TS seat's D1 (does the child's session reach the capture's hooks) is answered by the record: the
captured child stores hold idle records the capture wrote — delivery is observed, 400+ stores. The
python-coder seat withdrew two of its own constructions after probing (the preflight does reach
`is_the_running_copy`; the launch-notice dispatch is not mis-marked) — recorded so the burndown does
not chase them. The store census behind the latest-idle reading (50 stores with ≥2 idles; 24 tool
calls after a first idle in the sampled store) lives with the stores, dated 2026-11-26.
