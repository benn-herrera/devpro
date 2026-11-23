# kanban check targets and dashaboard runner. This file is installed at
# <harness-relpath>/tools/runner-snippets/ — <harness-relpath>
# being the install directory relative to the project root:
# .claude/skills/devpro under claude, .opencode/plugins/devpro under opencode — and is
# included from the consuming project's Makefile by one installed line (never
# copied into it):
#
#     -include <harness-relpath>/tools/runner-snippets/devpro.mk
#
# A consumer running just instead gets the `import?` line pointing at
# `<harness-relpath>/tools/runner-snippets/devpro.just`
# (just >= 1.33).
#
# The non-fatal `-include` form is deliberate: if the installed tree is
# absent — not yet installed, or removed — the consumer's Makefile keeps
# working and only these targets go missing.
#
# Assumed consumer layout: the repo root (where make runs) is the project root.
# Every check finds the active file from the working directory, so these targets
# run from the repo root.
#
# The targets run the installation's wrapper, `../devpro.sh` beside this snippet file's installed
# directory — located from the file's own directory via `$(DEVPRO_SNIPPET_FILE)`, not the recipe's
# working directory, the repo root — never `devpro` from PATH, so each check runs the install's own
# copy of devpro.
#
# Target names carry a `devpro-` prefix, so they cannot collide with a project's
# own check/help. Plain POSIX recipe lines — no SHELL override;
# existing recipes keep their own shell.
#
# Targets:
#   devpro-help:                          show help on devpro make targets
#   devpro-check-plan:                    check the active plan's status form, as the board reads it
#   devpro-check-design:                  check the active design's final form and its delta pairs
#   devpro-check-design-deltas-applied:   check that the active design's pending doc deltas were applied
#   devpro-check-roadmap:                 check ROADMAP.md's ticket layout, as the board reads it
#   devpro-dashboard:                     manually run the devpro dashboard http server (blocks)

# dicing checks
# Recipes run from the consumer's repo root, so the wrapper is located from this snippet file's own
# directory — `$(DEVPRO_SNIPPET_FILE)` is fixed at parse, before DEVPRO, never a bare `../devpro.sh`
# which would resolve against the repo root.
DEVPRO_SNIPPET_FILE := $(lastword $(MAKEFILE_LIST))
DEVPRO := $(dir $(DEVPRO_SNIPPET_FILE))../devpro.sh

.PHONY: devpro-help devpro-check-plan devpro-check-design devpro-check-design-deltas-applied devpro-check-roadmap devpro-dashboard

devpro-help:
	@grep '^#   devpro' "$(DEVPRO_SNIPPET_FILE)" | sed 's:^#: :'
	@$(DEVPRO) --help

devpro-check-plan:
	@$(DEVPRO) check-plan

devpro-check-design:
	@$(DEVPRO) check-design

devpro-check-design-deltas-applied:
	@$(DEVPRO) check-design --deltas-applied

devpro-check-roadmap:
	@$(DEVPRO) check-roadmap

devpro-dashboard:
	@$(DEVPRO) dashboard
