"""The claude harness: the set written as one skills-directory plugin below the harness directory."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence

from devpro.harness import (
    COLD_READ_SCRIPT_RULE,
    FOREGROUND_RECIPE_RULE,
    PLUGIN_MANIFEST,
    FrontmatterForm,
    GuardrailHook,
    Harness,
    HarnessFile,
    ShippedDefinition,
    agent_frontmatter,
    mcp_json,
    scratch_rule,
)
from devpro.vocabulary import Tool

# Claude Code registers a freshly written plugin's components only after a restart or `/reload-plugins`.
# The sentence names the symptom and the remedy alone: the cause is Claude Code's and may change.
_RELOAD_RULE = (
    "If the new agents are not available after using `devpro install`, `/reload-plugins` rescans the agent list."
)

# The kbase MCP server's tools register the same way, so after an install its tools are not offered until
# the plugin's servers are rescanned. Same remedy as _RELOAD_RULE, the kbase tools named instead of the agents.
_TOOLS_RELOAD_RULE = (
    "If the kbase tools are not offered after an install, `/reload-plugins` rescans the plugin's servers."
)


def _mcp_entry(*, command: str) -> dict[str, str | list[str]]:
    """A `command`/`args` entry."""
    return {"command": command, "args": ["mcp"]}


_GUARDRAIL_SCRIPT = "hooks/guardrail.pl"
_REMINDER_SCRIPT = "hooks/state-table-reminder.sh"
_REGISTRATION = "hooks/hooks.json"
# The hook command. Claude Code gives a plugin's hook processes the plugin's root, and runs a command
# with no `args` through a shell, so the path is quoted. Claude Code reads exit 2 as a block, and that
# is an interpreter's status for a script it cannot open, so the command runs the script only where it
# stands and otherwise names it on stderr and exits 1, which Claude Code reports without blocking. The
# interpreter is named on PATH, never by absolute path: the file registering it is often committed and
# shared across machines.
_MISSING_SCRIPT_REPORT = "guardrail hook: no readable script at $s"
_MISSING_REMINDER_REPORT = "state-table reminder: no readable script at $s"


def _hook_command(*, interpreter: str, script: str, report: str) -> str:
    """The command running `interpreter` on `script` under the plugin's root where that is a readable
    file, and otherwise writing `report` to stderr and exiting 1."""
    return (
        f's="${{CLAUDE_PLUGIN_ROOT}}/{script}"; if [ -f "$s" ] && [ -r "$s" ]; then exec {interpreter} "$s"; fi; '
        f'echo "{report}" >&2; exit 1'
    )


_PLUGIN_GUARDRAIL_COMMAND = _hook_command(interpreter="perl", script=_GUARDRAIL_SCRIPT, report=_MISSING_SCRIPT_REPORT)
_PLUGIN_REMINDER_COMMAND = _hook_command(interpreter="sh", script=_REMINDER_SCRIPT, report=_MISSING_REMINDER_REPORT)
# The registration's marker: the phrase both commands' reports write for a script they cannot open.
# The reminder entries outlive a failed probe, so the file is written without the guardrail's report
# in it, and a later install still has to read it as this repository's own.
_REGISTRATION_MARKER = "no readable script at"
_GUARDRAIL_MATCHER = "Bash|Read|Write|Edit|NotebookEdit|Grep|Glob"
# A subagent is dispatched by the `Agent` tool, named that since v2.1.63, and its report comes back
# either as that call's result or through `SubagentHandback`'s own call.
_DISPATCH_MATCHER = "Agent"
_COMPLETION_MATCHER = "Agent|SubagentHandback"


def _hook_entry(*, matcher: str, command: str) -> dict[str, object]:
    """One matcher group: the matcher it fires on and the single command it runs."""
    return {"matcher": matcher, "hooks": [{"type": "command", "command": command}]}


def _registration_hooks(*, with_guardrail: bool) -> dict[str, list[dict[str, object]]]:
    """The registration's `hooks` object: the plan-state reminder on a subagent's dispatch and on its
    completion, and the guardrail's entry on every Bash and file-tool call where `with_guardrail` says
    the install-time probe leaves it."""
    guardrail_entry = (
        [_hook_entry(matcher=_GUARDRAIL_MATCHER, command=_PLUGIN_GUARDRAIL_COMMAND)] if with_guardrail else []
    )
    reminder = _hook_entry(matcher=_DISPATCH_MATCHER, command=_PLUGIN_REMINDER_COMMAND)
    return {
        "PreToolUse": [*guardrail_entry, reminder],
        "PostToolUse": [_hook_entry(matcher=_COMPLETION_MATCHER, command=_PLUGIN_REMINDER_COMMAND)],
    }


def _guardrail_registration(plugin: str, shipped: Sequence[ShippedDefinition]) -> str:
    """The plugin's `hooks/hooks.json` where the install-time probe passes, the same for every plugin."""
    return json.dumps({"hooks": _registration_hooks(with_guardrail=True)}, indent=2) + "\n"


def _reminder_registration(plugin: str, shipped: Sequence[ShippedDefinition]) -> str:
    """The same file where the probe does not pass: the plan-state reminder alone, the guardrail
    neither registered nor shipped."""
    return json.dumps({"hooks": _registration_hooks(with_guardrail=False)}, indent=2) + "\n"


_AGENTS_FILE = "CLAUDE.md"
_PROJECT_HARNESS_DIR = ".claude"
_USER_HARNESS_DIR = "~/.claude"

HARNESS = Harness(
    name="claude",
    agents_file=_AGENTS_FILE,
    project_harness_dir=_PROJECT_HARNESS_DIR,
    display_name="claude code",
    user_harness_dir=_USER_HARNESS_DIR,
    plugin_dir="skills/{plugin}",
    # a plugin's components register only under the plugin's namespace, its MCP tools included
    reference_prefix="{plugin}:",
    mcp_tool_prefix="mcp__plugin_{plugin}_kbase__",
    scratch_rule=scratch_rule(harness_dir=_PROJECT_HARNESS_DIR),
    memory_file=f"`{_USER_HARNESS_DIR}/{_AGENTS_FILE}`",
    user_plugin_shadows=True,
    reload_rule=_RELOAD_RULE,
    tools_reload_rule=_TOOLS_RELOAD_RULE,
    cold_read_rule=COLD_READ_SCRIPT_RULE,
    recipe_rule=FOREGROUND_RECIPE_RULE,
    kbase_project_rule="",
    tools={
        Tool.READ: ("Read",),
        Tool.GREP: ("Grep",),
        Tool.GLOB: ("Glob",),
        Tool.EDIT: ("Edit",),
        Tool.WRITE: ("Write",),
        Tool.BASH: ("Bash",),
        Tool.WEBFETCH: ("WebFetch",),
        Tool.WEBSEARCH: ("WebSearch",),
        Tool.AGENT: ("Agent",),
    },
    model_pattern=re.compile(r"^(fable|opus|sonnet|haiku|inherit|claude-\S+)$"),
    model_shape="a Claude alias (fable, opus, sonnet, haiku), a full model id such as claude-opus-4-1, or inherit",
    inherit_text="inherit",
    inherit_synonyms=(),
    bare_category_spec_is_all=False,
    definition_form=FrontmatterForm(agent=agent_frontmatter, document=()),
    rendered_files=(PLUGIN_MANIFEST, mcp_json(_mcp_entry)),
    guardrail=GuardrailHook(
        script=_GUARDRAIL_SCRIPT,
        registration=HarnessFile(path=_REGISTRATION, text=_guardrail_registration, marker=_REGISTRATION_MARKER),
        registration_without_hook=HarnessFile(
            path=_REGISTRATION, text=_reminder_registration, marker=_REGISTRATION_MARKER
        ),
    ),
)
