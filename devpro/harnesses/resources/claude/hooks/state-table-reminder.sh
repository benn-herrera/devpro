#!/bin/sh
# !INSTALLED! from devpro/harnesses/resources/claude/hooks/state-table-reminder.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
#
# Claude Code hook for the Agent tool, at a subagent's dispatch and at its completion: a project
# holding `ACTIVE_PLAN.md` or `ACTIVE_DESIGN.md` at its root gets one sentence of context naming the
# plan's status table, and a project holding neither, or a call naming no root, gets silence.
#
# Exit 0 with the JSON on stdout is the only answer: Claude Code reads a hook's stdout as its JSON
# output, and `hookSpecificOutput` must name the event the input carries.

set -u

input=$(cat)

# The input's own top-level string field `name`, as Claude Code writes it: what follows the first
# `"name"` up to its closing quote. A field the input does not carry prints nothing.
field() {
    rest=${input#*"\"$1\""}
    if [ "$rest" = "$input" ]; then
        return 0
    fi
    rest=${rest#*:}
    rest=${rest#*\"}
    printf '%s' "${rest%%\"*}"
}

root=${CLAUDE_PROJECT_DIR:-}
if [ -z "$root" ]; then
    root=$(field cwd)
fi
if [ -z "$root" ]; then
    exit 0
fi
if [ ! -f "$root/ACTIVE_PLAN.md" ] && [ ! -f "$root/ACTIVE_DESIGN.md" ]; then
    exit 0
fi
event=$(field hook_event_name)
if [ -z "$event" ]; then
    exit 0
fi

# The one sentence. Claude Code reads hook context as project information rather than as an
# out-of-band instruction, so it states the status table as what it is.
printf '{"hookSpecificOutput": {"hookEventName": "%s", "additionalContext": "%s"}}\n' "$event" \
    "The active plan records each package's state in a status table, which is expected to match the tree as the work lands."
