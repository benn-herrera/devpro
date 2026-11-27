# Guardrail hook

What the guardrails block and allow, and what a refusal reads, is SPEC.md, Deployed Surfaces,
[Shipped files](../../SPEC/deployed-surfaces/shipped-files.md); this leaf is how they are built.

A harness that declares a `guardrail` (`Harness.guardrail`, a `GuardrailHook`) ships a hook the
install registers rather than only copies; claude declares one, opencode sets `None` because its
plugin entry (`index.ts`) imports `guardrail.ts` and runs its `setup` inside its own, and mage sets
`None` and ships no hook at all. `guardrail.ts` keeps its `Plugin.define` export so the bun runner
loads it alone, and the entry imports it only where the file stands beside it — where a user-level
install copies it beside the entry, the guardrail runs at user level as it does in a project. Plugin discovery lists only the direct children of `plugins/`, so the file
inside the plugin directory is not also loaded as an opencode plugin module of its own. The `GuardrailHook`
names the `script` under `resources/<harness>/`, which is also its path under the install
directory; the `HarnessFile` for the plugin's `hooks/hooks.json` twice over — `registration`, built
by `_guardrail_registration` (`devpro/harnesses/claude.py`), and `registration_without_hook`, built
by `_reminder_registration`, the same file without the guardrail's entry; and a `marker`, the phrase
both hook commands' missing-script reports share (Shipped files). The marker is a phrase of ordinary
English because it is read to recognize a plugin, not to refuse a file: `_is_our_harness_file`,
whose one reader is `_report_shadowing` checking whether a user-level plugin is present, would report
one where the operator wrote a narrow phrase's near likeness. The registration holds the guardrail's `PreToolUse` entry — matcher
`Bash|Read|Write|Edit|NotebookEdit|Grep|Glob` — where the install-time probe passes, plus one
ungated plan-state reminder entry on every claude install, a `PostToolUse` matched on `Agent`,
running `<install-dir>/hooks/state-table-reminder.sh`, which reads `ACTIVE_PLAN.md` — file or,
where the plan was diced, the `ACTIVE_PLAN/` tree — at the project root and emits a one-sentence
`hookSpecificOutput.additionalContext` reminder. That sentence's text lives in the script,
`devpro/harnesses/resources/claude/hooks/state-table-reminder.sh`, which is its one home, so a
wording change is the script's alone. The entry fires at the `Agent` call's return — the
subagent's completion where the call ran in the foreground, the dispatch turn where it moved to the
background — and a background subagent's completion injects nothing. A user-level claude install
takes no guardrail, so it writes no registration and the reminder never registers there, where
opencode's entry registers its hooks on a user-level install as on a project one. Every claude
install therefore runs the guardrail script on each file-tool call as well as each Bash call, and
with the kbase component off the script finds the kbase signal absent and lets a file-tool call
through. The entry's command is a short `sh` program that
`exec`s `perl` on `${CLAUDE_PLUGIN_ROOT}/hooks/guardrail.pl` only when that is a readable file, and
otherwise writes the missing-script report to stderr and exits 1. Claude Code gives a plugin's hook
processes `CLAUDE_PLUGIN_ROOT`, so the command names no harness directory and needs no quoting
refusal. The guard exists because perl exits 2 for a script it cannot open, which Claude Code reads
as a block: a plugin that loses its `hooks/` directory would have every call the matcher names
blocked. The interpreter is `perl` on `PATH`, never an absolute path, because the plugin may be
committed or shared and read on other machines.

The script is Perl with core `JSON::PP` and nothing else at session time, a port of
`guardrail.ts`'s `mutation`, its `.index/` check and their helpers. It reads Claude Code's
`PreToolUse` JSON on stdin. It resolves a relative destination against the input's `cwd`, else the
project root (`$CLAUDE_PROJECT_DIR`, else `cwd`); `guardrail.ts` resolves against the shell call's
`workdir`, else the project root, which is also its base for file-tool calls. Every path word of a
Bash command — a shell redirection or `tee` destination, a `cp`/`mv` argument, a word the
`.index/` check reads — goes through `shell_path_of`, which implements the `$CLAUDE_PROJECT_DIR`
spelling Shipped files states, reading the variable from `$ENV{CLAUDE_PROJECT_DIR}`, and otherwise
is `path_of`.
File-tool arguments go through `path_of` alone. `path_of` collapses `..` lexically, the
`.index/` check's one resolution step. That check's search rule is judged as Shipped files states
it, by the file filter's last segment ending `.md`, and three edges are accepted with it: `*.MD` is
blocked, a brace or set glob is judged by its suffix, and a Grep `type` is unread.

Each script finds the kbase signal, the `kbase` skill's `SKILL.md`, from its own path, never
from the root or the working directory, which `--subdir` would make wrong: `guardrail.pl` from
`$0`, which is `<install-dir>/hooks/guardrail.pl`, so its signal is
`<install-dir>/skills/kbase/SKILL.md`; and `guardrail.ts` from
`import.meta.url`, which is `<install-dir>/guardrail.ts`, so its signal is
`<install-dir>/skills/kbase/SKILL.md` as well, `./skills/kbase/SKILL.md` from the script. Both are
relative to the install directory, so the signal is present where the kbase component is on and
absent where it is off.

Exit 2 is the block path alone: a failed `use` or `die` in Perl can itself exit 2, which would block
every call the matcher names, so every module beyond `strict` and `warnings` is loaded with `require`
and the whole body runs in an `eval` that writes to stderr and exits 1, which Claude Code reports as
a hook error without blocking.
