# kanban check recipes and dashaboard runner. This file is installed at
# <harness-relpath>/tools/runner-snippets/ — <harness-relpath>
# being the install directory relative to the project root:
# .claude/skills/devpro under claude, .opencode/plugins/devpro under opencode — and is
# imported from the consuming project's justfile by one installed line (never
# copied into it):
#
#     import? '<harness-relpath>/tools/runner-snippets/devpro.just'
#
# A consumer running make instead gets the `-include` line pointing at
# `<harness-relpath>/tools/runner-snippets/devpro.mk`.
#
# `import?` requires just >= 1.33; the optional form is deliberate: if the
# installed tree is absent — not yet installed, or removed — the consumer's
# justfile keeps working and only these recipes go missing.
#
# Assumed consumer layout: the repo root (where just runs) is the project root.
# Every check finds the active file from the working directory, so these recipes
# run from the repo root.
#
# The recipes run the installation's wrapper, `../devpro.sh` beside this snippet file's installed
# directory — located from the file's own directory, not the recipe's working directory, the repo
# root — never `devpro` from PATH, so each check runs the install's own copy of devpro.
#
# Recipe names carry a `devpro-` prefix, so they cannot collide with a project's
# own check/help. Plain recipe lines, no `set shell` — nothing here
# needs bash.
#

[doc("show help on devpro just recipes")]
devpro-help:
    @just --justfile "{{justfile()}}" --list | grep -E '^[ \t]+devpro'
    @{{quote(source_directory() / ".." / "devpro.sh")}} --help

[doc("check the active plan's status form, as the board reads it")]
devpro-check-plan:
    @{{quote(source_directory() / ".." / "devpro.sh")}} check-plan

[doc("check the active design's final form and its delta pairs")]
devpro-check-design:
    @{{quote(source_directory() / ".." / "devpro.sh")}} check-design

[doc("check that the active design's pending doc deltas were applied")]
devpro-check-design-deltas-applied:
    @{{quote(source_directory() / ".." / "devpro.sh")}} check-design --deltas-applied

[doc("check ROADMAP.md's ticket layout, as the board reads it")]
devpro-check-roadmap:
    @{{quote(source_directory() / ".." / "devpro.sh")}} check-roadmap

[doc("manually launch the devpro dashboard http server (blocks)")]
devpro-dashboard:
    @{{quote(source_directory() / ".." / "devpro.sh")}} dashboard
