# Stage-1 post-plan review — the docdicer absorption

Four seats over the work commits `0481156..84f514f` plus their uncommitted edges, each given the
project documents and the design, not the plan. Seat reviews live in
`.devpro-temp/stage1-review-{coder,architect,prompt-engineer,tech-writer}.md`. One ID per defect,
naming every seat that reported it.

## R1 — Critical: the board names docdicer at a version it never reports. *coder*

`board.js:134` renders `docdicer v${payload.docdicer_version}` from `devpro/dicing/__init__.py`'s
`0.12.0`, while the landed SPEC (`dicing/kanban.md:296`) states the hover carries `devpro
v<version>` — what `devpro --version` prints. The payload key exists only to feed the wrong name;
`test_server.py:241` asserts it against the same constant. Fix: the three-line alignment to the
SPEC's statement, which also removes the package's second version constant.

## R2 — Critical: the REPO_ROOT exemption creates a runner file where none should exist. *coder*

`runner_file.py:225`'s `REPO_ROOT` exemption guards the in-place path, but the `Makefile` creation
branch sits after the return — a no-runner-file project root gets a runner file created anyway.
Its test (`test_devpro_install.py:1326`) passes only because this repo has a `justfile`, so the
creation branch never runs there. Fix: the guard covers the creation branch (or the branch's
behavior is stated where the test runs), and a test exercises a no-runner-file root.

## R3 — Critical: the upgrade from a 0.17.x install is undocumented. *tech-writer*

The install's absorbed-state behaviors — pruning `skills/docdicer/tools/`, removing the retired
include line, removing or reporting a created runner file — are walked once by every existing user
on the day the release lands, and neither README nor guide states any of them. Fix: the README's
Updating section states the upgrade's consequences once, in the prune's real terms.

## R4 — High: the lazy dispatch is false as landed. *architect*

`build_parser()` (`devpro/cli.py:83`) imports `devpro.dicing.cli` unconditionally, whose
module-level imports pull all nine verbs' implementations including the kanban server — verified
by probe. The pinning test never builds the parser, so it cannot observe the failure its docstring
names. Fix: `dicing/cli.py`'s implementation imports move into `run()`'s branches (the exact
pattern `devpro/cli.py` uses and the invariant already exempts), the Packaging leaf states the
exemption for both modules, and the probe adds `build_parser()`.

## R5 — Medium: the `just` floor is stated three ways. *tech-writer + prompt-engineer*

`README.md:43` and `guide.py:73` say 1.33.0 unconditionally; `recipes.md:35-37` and
`SPEC/guide-and-readme.md:38` say 1.27.0 generally, 1.33.0 where kbase ships; the changelog checks
out — `[doc]` is 1.27.0, optional imports 1.21.0. The session-facing texts are stale. Fix:
README and the guide's Requirements bullet state the conditional floor the SPEC leaves state.

## R6 — Medium: README promises include lines and a Makefile per install. *tech-writer*

`README.md:83-88` promises both unconditionally; with one snippet set left, a project without
kbase gets neither, and a stale docdicer line is removed rather than added. Fix: the README's
statement matches the landed `plugins.md`.

## R7 — Medium: the pipx line names a tag that does not exist. *tech-writer*

`README.md:58` names `@v0.18.0`; the repository's newest tag is `v0.17.5`. The absorbed work is
unreleased; the README names the next release before it is cut. Fix: the README names the newest
existing tag, and the release process stamps it at cut time — stated in the plan that lands the
release.

## R8 — Medium: the docdicer credit names a build package that retired. *tech-writer*

`README.md:158` credits docdicer as a build package; its dicer, checks and board now live at
`devpro/dicing` and no ported-source credit states the move. Fix: the acknowledgments state the
absorption — the ideas and the ported source the project credits, now devpro's own code.

## R9 — Low: the leftover tools tree is the user's to delete, and nothing says so. *tech-writer*

Nothing human-facing states that a 0.17.x install's `skills/docdicer/tools/` lingers inert and is
the operator's to delete. This checkout still holds it under both harness directories. Fix: the
upgrade story (R3) carries it.

## R10 — Low: `plugins.md:54-56` still illustrates a docdicer include line. *architect*

Two sentences after stating kb alone carries snippets, the leaf's example shows the docdicer
snippets path. Fix: the example names the kb line.

## R11 — Low: `install.py:4-6`, `:303` docstrings name the retired package as shipped. *architect*

Fix: the docstrings state the two-row reality.

## R12 — Low: the removal report claims a removal it did not make. *coder*

`runner_file.py`'s created-file path prints `left …/justfile in place holding no include line` on
an install that removed nothing (reproduced; the created-then-emptied transition was not probed
end to end — the report makes no claim on that specific path). Fix: the message states what the
run actually did, with a test where the plan's P7 tests reach it.

## R13 — Notes, recorded for the burndown's judgment

*PE* — the guide's two-hop route to the board; *tech-writer* — the stale 0.17.1 screenshot, the
"no docdicer script" wording in Global setup; *coder* — eight notes on the absorbed package's
inherited shape (its own wire keys, `served_files` untraced, the planform/board form logic left to
the SPEC seat's standards), `STAMPED_NAMES` empty leaving the stamp-by-name path untested, and
`_pair_state` classifying empty-`becomes` deletions as conflicting once applied (the design's own
contract states the behavior; a future design defect).

## Verified holding across all four seats

One shape rule for write and remove; the wheel glob matching the `files(__package__)` read; all
five pending pairs' old text intact with no leaf contradicting a pending stage; nine verbs
resolving; no recipe or launcher name in any definition; the CONVENTIONS re-points resolving; the
dicing contract clean of absorbed internals; 1525 passed, 1 skipped at the 3.9 floor; the whole
gate green with the absorbed state.
