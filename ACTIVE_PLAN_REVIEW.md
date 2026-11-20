# Periodic review — the accumulated whole since 69eed3e

Findings from the eight-seat panel (four conformance, four consistency) over `69eed3e..HEAD` —
seven landed plans, 0.17.2 → 0.18.0. Seat reviews live in `.devpro-temp/review-<agent>-<seat>.md`
(five flat-named); full diffs for the consistency pairs in `.devpro-temp/spec.diff`/`arch.diff`.
One ID per defect, naming every seat that reported it.

## Criticals

**F1 — README's Mage install command is broken.** *tech-writer conformance.* `README.md:105`:
the `--harness\=mage` escape collapsed (range commit `f0b32ab`); the documented command fails for
anyone who copies it.

**F2 — README's install paragraph contradicts SPEC.** *tech-writer conformance.* `README.md:71-73,
88-94` restate the harness rule and the agents-file rule; both depart from SPEC (Install
destination; Agents File).

**F3 — README's Updating section contradicts itself.** *tech-writer conformance.* `README.md:130-133`:
the legacy `~/Mage/Skills/kbase/` is "left alone" and, one paragraph later, loads a second set of
servers.

**F4 — README's profiler bullet overclaims across harnesses.** *tech-writer conformance +
tech-writer consistency (C1).* `README.md:45` says each tool call of a session is recorded, for all
harnesses; ARCHITECTURE says claude-on-web records nothing until `init`, mage ships nothing, and the
recorded events are the six hook events — the one line a user reads before installing.

**F5 — the two-acts reminder description is stale in two leaves.** *coder consistency (R1) +
architect conformance (W1).* `ARCHITECTURE/install/opencode-entry.md:63-66` and
`guardrail-hook.md:24-25` describe the reminder naming "the status table's two acts"; both harnesses
inject only "keep the ACTIVE_PLAN state table up to date." (`4e88064` shortened the sentence; the
leaves entered later.)

**F6 — the capture's user-level claim contradicts the code and a sibling leaf.** *coder consistency
(R2).* `opencode-entry.md:7-9` says the capture ships on a project install and none at user level;
`install.py:410-416`'s filter drops it at user level, and `renders-and-copies.md:63-64` states that
without a mode condition.

## High/Medium

**F7 — the rendered carriers are stale.** *prompt-engineer conformance + tech-writer conformance.*
`e1c0652` changed the interval default to 5; the installed development SKILL.md and guide still
render 3 — live in every session's context, including this review's trigger. A render run fixes the
text; the freshness gap is the finding.

**F8 — the docdicer skill's *The script* section is stale.** *prompt-engineer conformance.*
"check-design has no recipe of its own" / "Nor has check-roadmap" are false (both recipes exist);
`docdicer-check-design-deltas-applied` — the recipe the development skill and the CONVENTIONS leaf
point at — is absent from the skill that owns docdicer's command surface.

**F9 — the guide instructs a step SPEC doesn't.** *tech-writer conformance.* `using.md:46-49` tells
a new user to create `.devpro-temp/` before their first design; its SPEC bullet states no such step.

**F10 — show-profile is undiscoverable.** *tech-writer consistency (W1).* Shipped by SPEC, named in
neither README's Next section nor the guide's Route.

**F11 — the pipx instructions omit `ensurepath` + new-shell**, install and update paths both.
*tech-writer consistency (W3, W4).*

**F12 — README's `.gitignore` block is claude-only; mage gets no guidance.** *tech-writer
consistency (W2).*

**F13 — README's mage migration paragraph appears in no SPEC leaf**, though SPEC says the
Installation reference covers every harness. *tech-writer consistency (W4).*

**F14 — SPEC never states the claude reminder half.** *architect consistency (R-arch-1).*
`shipped-files.md` states the opencode entry; the claude `PostToolUse`-on-`Agent` entry and its
injection are designed in `guardrail-hook.md` but promised by no SPEC sentence.

**F15 — `structural-rules.md` runs its sweeps per-plugin on a symbol the consolidation removed.**
*architect consistency (R-arch-2).* `_PLUGIN_RENDERS` and the second-plugin premise are stale; the
`test_plugins.py` companion claim carries it.

**F16 — `recipes.md`'s agents paragraph is stale twice.** *architect conformance (W2) + coder
consistency (R4).* The "once per nested harness / two `--harness` lines" claim (the recipe is one
line, no flag) and the docdicer-recipes credit (they route through `docdicer-repo`).

**F17 — `profiler.ts` floor 2.3.0 vs the subagent spelling it maps.** *coder conformance (C1).*
`SUBAGENT_TOOLS`/`KIND_ARGS` match only the post-rename `subagent`; below it, dispatches record as
`task` under a generic context.

**F18 — the plugin module's `id` has three answers and no document.** *coder conformance (C3).*
`index.ts` reads the registry, `profiler.ts` carries a literal citing an undocumented precedent,
`guardrail.ts` holds the third; no test pins any.

**F19 — `childAgentTypeOf` never reads `agentType`** — a `forked` context draws `fresh`. *coder
conformance (C5).*

**F20 — `check-wheel.sh` installs with no scratch `HOME`**, against the CONVENTIONS scratch rule.
*coder consistency (R3).*

**F21 — the guardrail false-positives scratch redirects.** *coder conformance (noted; observed
twice this session).* `> file 2>&1` into `.devpro-temp/` is blocked as a violation.

**F22 — SPEC's guide-and-readme lists no longer match the surfaces they govern.** *tech-writer
conformance.* `guide-and-readme.md:86-99`, `:60-84`.

**F23 — `hp.py` measures a line under one encode policy and writes under another.** *coder
conformance (C6).*

**F24 — the version bump's wording and diagnostic are stale.** *architect conformance (N1, N2) +
coder consistency (N).* `version-has-one-home.md`'s "hand edit" predates `bump-version.sh`, whose
diagnostic prints a leaked `{{dot}}` placeholder.

## Low

**F25 — THESIS's building-block table has no row for the optional component kind** SPEC's plugins
leaf asserts. *prompt-engineer consistency (F1).* Fix is a one-line THESIS term — user decision.
**F26 — THESIS's Installed-resources row** ("helper scripts, hook scripts") doesn't describe
`view.html` or `profiler.ts`. *prompt-engineer consistency (F2).* Same class.
**F27 — two flagged decisions:** THESIS's adopter-audience sentence no human-facing surface speaks
to; `USER_README.md` required by seat conventions but unnamed in the project documents.
*tech-writer conformance.*
**F28 — three stale citations:** `placeholders.md:35`'s `--plugin=` (the last in any tracked md);
the subsystem map's missing `show-profile` entry; SPEC's omission of the `opencode-profiler` store.
*architect consistency (R-arch-3, R-arch-5, R-arch-4).*
**F29 — torn-tail repair and its LINE_LIMIT bound are stated in code, nowhere in the contract;
the repair protects the opencode store but not claude's.** *coder conformance (C2, N4).*
**F30 — the seat files' Notes tiers** (coder C7–C12, tech-writer's 12 Notes, architect N3–N4)
carry further low-severity polish — the burndown drafts from them directly.

## Declined

- `README.md`'s "Acknowledgments" spelling — moved toward SPEC's, correct.
- The session-id sanitization `\w` difference — no reachable consequence (carried from the port
  review; unchanged).
