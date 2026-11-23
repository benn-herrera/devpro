#!/usr/bin/env bash
# !INSTALLED! from devpro/harnesses/resources/claude/hooks/state-table-reminder.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
#
# Claude Code hook for the `Agent` tool's return: a project holding `ACTIVE_PLAN.md` or the diced
# `ACTIVE_PLAN/` tree at its root gets one sentence of context, and a project holding none of them,
# or a call naming no root, gets silence.
#
# The sentence reaches the parent on its next model request after the hook fires, which is the `Agent`
# call's return: the subagent's completion where the call ran in the foreground, the dispatch turn
# where it moved to the background. A background subagent's own completion fires no parent-side hook,
# so nothing is injected then.
#
# Exit 0 with the JSON on stdout is the only answer: Claude Code reads a hook's stdout as its JSON
# output, and `hookSpecificOutput` must name the event the input carries.

set -euo pipefail

input="$(cat)"
# The event's own fields precede the tool's, so the scan below reads a top-level `cwd` or
# `hook_event_name` alone: a tool input's own field of either name sits past this bound.
input="${input%%'"tool_input"'*}"

# The first field of the input named ${1}, as Claude Code writes it: what follows the first `"${1}"`
# up to its closing quote. A field the input does not carry prints nothing.
function field() {
  local rest="${input#*\""${1}"\"}"
  if [[ "${rest}" == "${input}" ]]; then
    return 0
  fi
  rest="${rest#*:}"
  rest="${rest#*\"}"
  printf '%s' "${rest%%\"*}"
}

root="${CLAUDE_PROJECT_DIR:-}"
if [[ -z "${root}" ]]; then
  root="$(field cwd)"
fi
if [[ -z "${root}" ]]; then
  exit 0
fi
if [[ ! -f "${root}/ACTIVE_PLAN.md" && ! -d "${root}/ACTIVE_PLAN" ]]; then
  exit 0
fi
event="$(field hook_event_name)"
if [[ -z "${event}" ]]; then
  exit 0
fi

# The one sentence. Claude Code reads hook context as project information rather than as an
# out-of-band instruction, so it states the table and no act.
reminder='Reminder: keep the ACTIVE_PLAN state table up to date.'
printf '{"hookSpecificOutput": {"hookEventName": "%s", "additionalContext": "%s"}}\n' "${event}" "${reminder}"
