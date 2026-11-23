# kanban check recipes. This file is installed at
# <harness-relpath>/skills/docdicer/dicing-snippets/runner-snippets/ — <harness-relpath>
# being the install directory relative to the project root:
# .claude/skills/devpro under claude, .opencode/plugins/devpro under opencode — and is
# imported from the consuming project's justfile by one installed line (never
# copied into it):
#
#     import? '<harness-relpath>/skills/docdicer/dicing-snippets/runner-snippets/devpro.just'
#
# A consumer running make instead gets the `-include` line pointing at
# `<harness-relpath>/skills/docdicer/dicing-snippets/runner-snippets/devpro.mk`.
#
# `import?` requires just >= 1.33; the optional form is deliberate: if the
# installed tree is absent — not yet installed, or removed — the consumer's
# justfile keeps working and only these recipes go missing.
#
# Assumed consumer layout: the repo root (where just runs) is the project root.
# Every check finds the active file from the working directory, so these recipes
# run from the repo root.
#
# The recipes run the `devpro` command from PATH; the user installs it
# themselves — the `guide` skill's references/installing.md walks through it.
#
# Recipe names carry a `devpro-` prefix, so they cannot collide with a project's
# own check/help. Plain recipe lines, no `set shell` — nothing here
# needs bash.
#
# No recipe takes an argument, and the consumer's words are the recipes':
# `set positional-arguments` splices no word into a line by name, so a bare word
# after one — `just devpro-check-plan hi` — reads as a request for the recipe
# `hi`, as it would in the project's own justfile, and `just devpro help` is
# refused there rather than the recipe's line failing with `help: not found`.

set positional-arguments

[doc("show help on devpro just recipes")]
devpro-help:
    @just --justfile "{{justfile()}}" --list | grep -E '^[ \t]+devpro'
    @devpro --help

[doc("check the active plan's status form, as the board reads it")]
devpro-check-plan:
    @devpro check-plan

[doc("check the active design's final form and its delta pairs")]
devpro-check-design:
    @devpro check-design

[doc("check that the active design's pending doc deltas were applied")]
devpro-check-design-deltas-applied:
    @devpro check-design --deltas-applied

[doc("check ROADMAP.md's ticket layout, as the board reads it")]
devpro-check-roadmap:
    @devpro check-roadmap
