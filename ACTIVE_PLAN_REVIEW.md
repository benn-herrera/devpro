# Active plan review — the wipe-semantics strip

Four seats reviewed the strip's shipped work against the project documents and the design: the
Python coder twice (conformance, consistency), the architect (structure and claims), the
prompt-engineer (model-facing text and the contract documents). Each wrote independently to
`.devpro-temp/p4-*.md`; this document is the synthesis — one entry per defect, naming every seat
that reported it. The test-suite survey (`ACTIVE_TEST_SURVEY.md`, P3) carries its own judgments
(J1–J12); the burndown drafts from both documents.

## Critical

### C1 — SPEC asserts an outcome nobody measured: the opencode watcher under the wipe

`SPEC/write-safety.md` states the wholesale replacement as settled; the design's own Drafts item
records the live-watcher question as unsettled, and `index.ts` refreshes on every event under the
install directory. The contract asserts what no observation has answered. Disposition belongs to
the plan's owner: the observation drive runs before the design is called settled, or Write Safety
carries the unsettled state. Seats: python-conformance (Critical).

### C2 — The mage agents-file pass-over has no test that can fail on the defect it exists for

The design named the test; the landed coverage (`conftest.py:2431-2456`, the mage-subdir case of
the up-to-date parametrize) cannot fail on it — the real install never runs and the staged render
is byte-identical, so the comparison reads no change even if the wipe deletes the agents file. The
pass-over is the one protection for the operator's bytes above and below the block under mage, the
only harness whose install directory *is* the harness directory. Required: a changing second mage
install over a `CLAUDE.md` holding operator text and an earlier block, asserting the text and
`backup.CLAUDE.md` survive. Seats: python-consistency (Critical, machine guarantee), architect
(W1), python-conformance (lost pin).

### C3 — `devpro/definitions/skills/guide.py:116-117` tells operators a user-level install has
"no guardrail" — false at HEAD

The rendered guide skill ships the pre-strip claim; `write-safety.md` and `install-destination.md`
state the opposite. An operator reading the installed guide is misinformed about their own plugin.
One-clause fix in the definition's text. Seats: prompt-engineer (blocker).

## High

### H1 — `SPEC/deployed-surfaces/shipped-files.md` contradicts itself on user-level resources

`:170-171` "A user-level install renders the skill and copies none of the resources" against
`:100-101` and `:272-273` (entry + guardrail copied); `:100-106` names two resources where
`:108`'s span names three. The first sentence is the one a consumer hits asking "am I guarded at
user level?" — it answers no. Seat: prompt-engineer.

### H2 — `SPEC/deployed-surfaces/shipped-files.md:108-110` states the banner guarantee as a
consumer requirement, and it is false for harness resources

Resources are copied byte-verbatim and stamp nothing (`harness_resource_copies`); the guarantee is
stated three times across SPEC and CONVENTIONS with no peak altitude, and the SPEC copy — the only
one reading as a consumer requirement — is the false one. SPEC states the shipped-as-is fact;
CONVENTIONS keeps the mechanism. Seats: prompt-engineer.

### H3 — `ARCHITECTURE/install/opencode-entry.md:10` and `:44` carry the retired user-level
settlement, contradicting four other leaves

"copies the entry alone" and "a user-level install has no `guardrail.ts`, and none runs" against
`install-destination.md:54-55`, `renders-and-copies.md:100-103`, `guardrail-hook.md:10-11`,
`guardrail-registration.md:25-27`, `shipped-files.md:100-101`. Seats: python-consistency.

### H4 — `tests/install/conftest.py`'s re-entry test stages an empty row, so the pass-over's
kept-file branch never executes

`_staged(copy, ())` makes the kept-file assertion `{} == {}`; the test passes whether or not kept
files are preserved. The design named a stale-`.pyc`-under-a-populated-copy case; the tree lacks
it. Required: stage the copy's row files plus a stale `.pyc`, assert survival and removal. Seats:
python-consistency.

## Warning

### W1 — The re-entry pass-over is a function of the copy's current content, with no guard

Delete a product file under `tools/devpro/` before re-running, and that path silently leaves
`keep` while the row that would restore it is dropped — the run completes with the copy short a
file and reports nothing. Guard: on a re-entry run, refuse when the running copy lacks a path
`_wheel_files` over `PACKAGE_ROOT` produces, naming it. Seats: python-conformance.

### W2 — The ordinary dry run lists the whole directory tree in both the created and removed
groups

`_every_entry_below` names every directory on the way; `_replaced_below` removes every directory
not on the way to a kept path; `keep` is empty on every non-re-entry run — so `created: agents/…`
and `removed: agents/…` for the same path on an unchanged tree. SPEC does not support a path in
both groups. Fix in the comparison (`preflight.py`), pinned over a non-empty install directory.
Seats: python-conformance.

### W3 — The mage hazard the wipe creates has no leaf, and mage's legacy paragraph is incomplete

Under mage the install directory is `Mage/Skills` itself: an operator's file beside `devpro/` but
inside the harness directory is removed by the next install, and nothing states it. `plugins.md:`
84-91's legacy paragraph describes a sibling's contents; the consumer fact is missing. Seats:
prompt-engineer.

### W4 — `plugins.md:50-51` and `:69-71` under-state the user-level and runner-line outcomes

"Delivers the devpro tools package alone" admits an unguarded reading; the runner-line rule is
matrix-wide ("no install edits a line it did not write") but SPEC states one historical set and
calls the line "inert" where `just` without `import?` refuses a missing path. Seats:
prompt-engineer.

### W5 — No leaf states that a symlink inside the install directory is unlinked, not followed

Pinned by `test_dry_run.py:269-285` and `_replaced_below`'s code; a reader must read code to learn
it. One clause in Write Safety (consumer: the link goes, its target survives). Seats:
prompt-engineer.

### W6 — "Git is the record" collides with README's own gitignore instruction

`installed-tree.md:3-6` and `write-safety.md:16-17` rest on the consumer's git; `README.md:83-85`
tells the operator to gitignore the tree. Either README or the leaves move — the recommendation:
README owns it (gitignore + `--dry-run` as the review surface), the leaves stop resting on git.
Seats: prompt-engineer.

### W7 — `install()`'s docstring states the pre-wipe ordering

"…then the writes; then the removals" — the replacement now precedes the writes. Seats: architect
(W2).

### W8 — `test_kbase.py:235` carries pre-wipe reasoning and duplicates a correctly-worded
conftest pin

"the marker… not pruned" describes abolished mechanisms; the body is line-for-line the conftest
twin. Keep one, reword. Seats: architect (W3), python-conformance (duplication).

### W9 — `renders-and-copies.md` carries four strip-residue defects

Stale line citations (:137, :142 — the spans moved); the pre-change four-field
`checked_agents_file` shape (:125-128); the managed-set enumeration overstatement (:126-127);
the four-negatives retirement inventory (:104-108). Seats: python-conformance, prompt-engineer
(§15).

### W10 — `install/plugins.md:62-65` still reasons from the retired docdicer set's membership

The recognition story's third member is a set the code no longer knows. Seats: python-consistency,
architect (N2), prompt-engineer (§3).

### W11 — The recognizer leaf's remaining body names dead symbols

`recognizer-spells-rendered-banner.md`'s surviving text cites `directives.is_installed` (gone) and
a recognizer the install no longer has; the title describes no recognizer. Recommendation: cut to
the digest duty and rename. Seats: python-consistency, prompt-engineer (§13), architect (partly).

### W12 — `untracked-output-is-not-source.md`'s reason is the pre-wipe one

"Replaces what it wrote, `kb-tools/` whole" — the whole tree now goes, whatever wrote it. Seats:
python-consistency, prompt-engineer (§13).

### W13 — `guardrail-hook.md:18-19` keeps a foreign/refused reason for a judgment the wipe deleted

The marker is read by `_report_shadowing` to recognize a user-level plugin — a different question;
the sentence constrains the marker's shape by a trade that no longer exists. Seat: prompt-engineer.

### W14 — The mage agents-file pass-over is invisible to `_differs`' seam record

`preflight.py:143-149` opens both sides with `filecmp.cmp(shallow=False)`; a pass-over path that
is a special file reaches the comparison. Recorded with C2's test: if the plain-`CLAUDE.md` case
passes, the seam is invisible; if not, `_differs` must read the copy's opinion without opening
either side. Seat: python-consistency.

## Note

### N1 — Strip residue in code and comments

`install.py:548`'s dead `guardrail` binding; `GUARDRAIL_RESOURCE` defined below its first use
(`install.py:384` vs `:369`); `_every_entry_below`'s docstring claiming a subtree pruning the walk
does not do; `runner_file.py:18-20`'s pre-wipe banner docstring; `conftest.py:683`, `:1171-1172`,
`:1901`'s prune/foreign-check docstring sentences; `install-entry.md:42-44` lacking "the
replacement runs after them"; `install/index.md:11-14`'s rationale clause; `install/index.md:3-5`
naming three of the four writers; `write-safety.md:8-11`'s third statement of the user-level
product; `guardrail-registration.md:8-9`'s implementation detail and rationale. Seats: architect
(N1, N3), python-consistency, python-conformance, prompt-engineer (§4–§8, §14).

### N2 — Test-suite duplication and dead definitions in `tests/install/`

conftest-collected tests duplicated verbatim by `test_staging.py`/`test_dry_run.py` subjects; the
conftest copies go. Seats: python-conformance (note), python-consistency (seen), survey (J8-J9).

### N3 — TEST_PRECONDITION labels on pre-existing tests

Two surviving re-entry tests carry "Defect (TEST_PRECONDITION)" labels whose subjects landed; an
existing test's docstring states its subject. Seats: python-conformance (note).

### N4 — The mage legacy-directory paragraph and the mage `--subdir` dry run

The legacy paragraph stays true as written but is the one legacy statement the plan did not name;
the mage `--subdir` preflight end-to-end was not probed. Raise for a uniform ruling with W3. Seats:
python-conformance (note), prompt-engineer (§2).

### N5 — Owned trades to keep on the record

A mid-wipe `OSError` leaves the install directory half-emptied with no backup (the docstring and
SPEC own it); `renders-and-copies.md:110-116`'s "unchanged install" reads ambiguously against a
changed install. Seats: architect (N5), prompt-engineer (§16).

## The survey's judgments

`ACTIVE_TEST_SURVEY.md` carries J1–J12 (real-tree case, index-vs-filesystem, banner-spelling pin,
direction check, rule-text instance gap, `test_runners.py` misfiled, `REVIEW_SEAT` ownership,
uncollected duplicate test, conftest monoliths, one repeat-count case, marginal units, the 4%
integration tier) and three contract-gap proposals. The burndown drafts from both documents.
