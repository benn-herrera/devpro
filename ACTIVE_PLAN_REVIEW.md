# ACTIVE PLAN REVIEW

The post-plan review of `75bb1ddd..85a9ff10` (develop) — the four changes as shipped, reviewed
independently by the coder, architect, prompt-engineer and tech-writer seats. Each seat wrote its
own review in `.devpro-temp/review-<seat>.md`; this document is the session's synthesis,
de-duplicated to one entry per defect with every seat that reported it named. Evidence pointers are
repeatable: probes and logs named live under `.devpro-temp/`.

The burndown section of `ACTIVE_PLAN.md` cites these IDs. The gates as the coder ran them at HEAD:
`just test devpro` exit 0 (1660 passed), `just test` exit 0 (1738 passed, tech-writer's run),
`just check-wheel`, `just check-links` exit 0 — **`just lint` exit 1 (R2)**.

## R1 — Critical: prune's venv guard is indexed off the surface, and its test pins the defect
*Reported by: coder (W1, W2), architect (C1).*

`devpro/install.py:264` guards with `relative.parts[1] == VENV_DIR` — a `.venv` directly under a
*surface*. The destinations `renders-and-copies.md:23-24` names sit two components deeper
(`skills/kbase/kb-tools/`, `skills/development/scripts/`), so their venvs never match. The probe
(`probe_venv_guard.py`, `review-coder-probe-venv2.py`) shows `prune` deleting a banner-carrying file
below `kb-tools/.venv/` that the design, the leaf (`renders-and-copies.md:22-24`) and both
docstrings say must never enter the stale list. The test written for the rule
(`test_devpro_install.py:2176-2204`) asserts the file's **removal** while its name and docstring
claim preservation — it passes only because the guard is broken. `_is_ours` hides the exposure
today (venv content carries no generated banner); the documented guarantee is false. Answer: guard
against the destination (the path runs through `<package destination>/.venv` for a known
destination, as `_clear_package_destination` judges it), and the test asserts the venv file's
survival directly with the plain file as the pruned contrast.

## R2 — Critical: the profiler removal's residue beyond imports — lint is red at HEAD
*Reported by: coder (C1, W7), architect (W3, W4).*

`just lint` exits 1: three F401s the removal left (`stores.py:9` `_json`; test imports
`OLD_HOOK_COMMANDS`, `TRACE_STORES`), all used only by deleted code — while `f772d99d`'s message
claims the imports were trimmed. The next layer is definitions: `hook_sources`, `stale_hook`,
`devpro_command` (`hooks.py:55,183,203`) and `_atomic_text` (`stores.py:52`) have no caller left,
their docstrings still speak of doctor/repair, and `_atomic_text` takes `import os` with it. The
sweep also stopped one file short in the documents: the CONVENTIONS stand-in leaf
(`a-stand-in-models-the-api-s-real-semantics.md:3`) still cites "doctor's `devpro:` line" as its
example — re-anchor it to a live stand-in (the harnesses' literal wrapper paths, or the preflight's
`--dry-run` listing).

## R3 — Critical: the TOML reader silently ignores malformed values the .cfg reader refused
*Reported by: coder (C3, W3), architect (W1), prompt-engineer (unsettled #1, settings probe).*

`context.py:295-299` reads a non-string `install`/`components` as absent: `components = ["kbase"]`
installs with no component and `install = true` becomes `detect`, silently — where the .cfg reader
refused both through the same `INSTALL_SETTINGS` check, and the model-map side refuses its
non-string values (`_settings_entries`). Three more silent paths: a quoted dotted top-level key
`["claude.model-map"]` passes validation and is then dropped (`_harness_of` accepts the dotted
name, `read_settings` reads only top-level keys — probe in `probe_settings.py`); a bare top-level
key (`foo = "bar"`) is skipped, though `_table_names`' docstring claims it handled; and the
docstring at `read_settings` still says "Neither setting value is judged here", which the discarded
value makes false. Answer: refuse non-string settings values naming the table and key, fold bare
top-level keys into the unknown-table refusal (making the docstring true), base validation and
reading on the same key space, and tests beside `test_a_settings_section_key_that_is_no_setting_is_refused_naming_the_map_section`.

## R4 — Critical: three filters are named where the code has one, and two tests pin the negation
*Reported by: coder (C2), architect (N1, N2), prompt-engineer (unsettled #2).*

`install-destination.md:73-77` still states the enumerated exclusions ("test suites… `.DS_Store`…
none of it installed at any depth"); the CONVENTIONS leaf and `package_copies`' docstring say
"`.dist-info/RECORD` is the one manifest of what ships" (nothing reads RECORD); `renders-and-copies.md:29-33`
says a copy can find only what package data declares — true of a wheel, false of the documented
checkout path (`surfaces-and-layout.md:45-46`), where `_wheel_files` filters nothing but
`__pycache__` and ships a gitignored `.DS_Store` `check-wheel` cannot see. Two shipped tests
(`test_devpro_install.py:581`, `:604`) plant those files and assert they land — the negation of the
SPEC sentence. This needs a ruling before it dispatches: either the SPEC retires the enumerated
exclusions for the design's own statement (the built package is what travels; the checkout path
travels its tree) or `_wheel_files` restores them against the design's wording. Architect's word
owns the choice; `check-wheel`'s `from-checkout` side label (`N2`) and a missing check of the
exclusion property (`N1`) ride the same account.

## R5 — Warning: the upgrade walks never mention the settings rename
*Reported by: tech-writer (F1), coder (W6), architect (W2).*

The default path moved to `devpro.toml` with no fallback and no message (`context.py:237-249`
returns None on an absent default), and neither upgrade walk — README's *Updating* (the 0.17.x
walk the project keeps for exactly this) nor the guide's — names the rename: an upgrading
operator's `install = never` and model map silently stop applying, the fresh path succeeds and the
upgrade path fails. Answer: one sentence in README's *Updating* and the guide's page (the old file
is not read; move and convert it), and one `report_left_alone` line where a default `devpro.cfg`
exists beside an absent `devpro.toml`. `ROADMAP.md:258` still names `devpro.cfg` — same sweep,
same item.

## R6 — Warning: the agents-path sentence is project-only, literal where a derived twin exists, and pinned by itself
*Reported by: coder (W5, W4, N4), tech-writer (F2), prompt-engineer (findings 1, 4 and probes).*

The sentence names `.claude/skills/devpro/agents/` — a project-relative path that is false under
the documented user-level install (`~/.claude/skills/devpro/agents/`, which shadows project copies)
and names one deployment of two where the project's own `WRAPPER_PROFILER` clause names both. The
value is a literal where `placeholders.md:36-39` derives exactly this class of path
(`project_wrapper`); the probe (`pe-postplan-agents-path-probe.py`) shows a moved `plugin_dir`
leaves the sentence stale while both assertions of its pinning test still pass — the literal at
`test_devpro.py:1127` is compared against the constant containing it (`N4`). The smallest
sufficient step: word the sentence to hold in both installs (`../../agents/` from the skill's own
directory — exact at either level), apply it at `claude.py`, `harnesses-and-families.md:17-18` and
`placeholders.md` (whose six-count and missing `agents_path` enumeration are this overlay's second
missed statement, `W4`), and pin the test on the constant. The derived-value design (a
`PluginText` member filled as `PROJECT_WRAPPER` is) is the architect-and-coder alternative — the
burndown item carries the choice.

## R7 — Warning: the profiler skill's No-traces branch asserts a cause it cannot check
*Reported by: prompt-engineer (finding 2), tech-writer (F4), coder (N7).*

"under claude a store an older name left behind is the cause" states as settled one of several
causes (a session whose hooks never load — the state `what-init-writes.md` records — among them),
gives an opencode session no branch at all, and its remedy runs `init` — which writes settings and
a skill copy into the repository the session was asked to read — without saying so. The branch text
PE proposes names cause from remedy and opencode's install remedy; F4 asks the sentence to state
the whole effect of the command it names. The residue phrasing "so an opencode session needs it
not" (`N7`) rides the same text.

## R8 — Warning: the section→table sweep stopped short in SPEC and tests
*Reported by: prompt-engineer (finding 3, finding 7), architect (N3), coder (W4's count half rides R6).*

SPEC still says "section" for the TOML table at four sites (`install-destination.md:88,104,107` —
the last quoting report output the code no longer prints — and `plugins.md:14`), where the same
leaves use "section" for document sections; three test names and a parametrize variable still say
"section" (`test_devpro.py:248,257,270`); `installing-this-repository.md:9` carries an unwrapped
161-column paragraph folding an unrelated statement into the recipe's account.

## R9 — Note: the guide page's settings literals are pinned by nothing
*Reported by: tech-writer (F3).*

`~/.config/devpro/devpro.toml` and `[<harness>.model-map]` are hand-copied literals in the
rendered installation reference, while its sibling claim — the `install` values — is pinned to
`INSTALL_SETTINGS` by an existing test. A test holds the page's path and table literals to
`context.SETTINGS_FILE` and `context.MODEL_MAP_TABLE`.

## Verified as correct (recorded so they are not re-opened)

- The `guide` skill's dropped WRAPPER clause and doctor line: `DP` has no other reader there;
  `clauses.WRAPPER` survives for `docdicer`. (prompt-engineer)
- The four harness-profiler leaf removals and their TOC lines: no remaining reference anywhere in
  `PROJECT_DOCS/`. (prompt-engineer)
- The dropped "glob repeated in one section" SPEC clause: the parse-refusal sentence covers the
  outcome. (prompt-engineer)
- README's store-rename paragraph reads complete without the doctor sentence. (prompt-engineer)
- `the-opencode-capture.md:42` "the pages group none of those dispatches": true by construction —
  the parent side builds the hierarchy from `child_agent_id`, which those records do not carry.
  (session verification of the prompt-engineer's unsettled #3)
- The `agents` pass-through holds for flags spelled like just's own options (`--dry-run` reached
  the install). (architect, coder)

## Strengths

- Wheel staging is a genuine deletion — denylist, `_shipped`, and their tests left with the
  mechanism that replaced them, and the no-bytecode discipline is real on both paths. (architect,
  coder)
- The TOML conversion kept every refusal's place, and the reference maps' consumer path is
  coherent. (architect)
- The overlay is minimal and generic: seventh member, `""` default, `render.py` untouched, both
  presence and drop pinned. (architect)
- The doctor/repair removal is thorough inside its own tree, and the store-rename remedy stays
  reachable through `init`, which genuinely calls `rename_stores`. (architect)

## Contract gaps

- `CONVENTIONS/planning-and-execution/the-gates.md` names `just test` and `just sweep-python` and
  no `just lint` — which is why a red lint could land. Proposed: `checkpoint gate: just test,
  just lint, then just sweep-python`, and one sentence that a plan is landed when the gates have
  run on the last landing commit. (coder, contract gap)
- The P1 brief's fixture-continuity clause and P2's settings-fixture wording are the two plan-text
  notes the runs acted on; no other gap reached a definition.
