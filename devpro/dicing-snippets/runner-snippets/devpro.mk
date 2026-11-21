# dicing check targets. This file is installed at
# <harness-relpath>/skills/docdicer/dicing-snippets/runner-snippets/ — <harness-relpath>
# being the install directory relative to the project root:
# .claude/skills/devpro under claude, .opencode/plugins/devpro under opencode — and is
# included from the consuming project's Makefile by one installed line (never
# copied into it):
#
#     -include <harness-relpath>/skills/docdicer/dicing-snippets/runner-snippets/devpro.mk
#
# A consumer running just instead gets the `import?` line pointing at
# `<harness-relpath>/skills/docdicer/dicing-snippets/runner-snippets/devpro.just`
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
# The targets run the `devpro` command from PATH; the user installs it
# themselves — the `guide` skill's references/installing.md walks through it.
#
# Target names carry a `devpro-` prefix, so they cannot collide with a project's
# own check/help. Plain POSIX recipe lines — no SHELL override;
# existing recipes keep their own shell.
#
# Targets:
#   devpro-help:                          show help on devpro make targets
#   devpro:                               print the devpro command's help
#   devpro-check-plan:                    check the active plan's status form, as the board reads it
#   devpro-check-design:                  check the active design's final form and its delta pairs
#   devpro-check-design-deltas-applied:   check that the active design's pending doc deltas were applied
#   devpro-check-roadmap:                 check ROADMAP.md's ticket layout, as the board reads it

# dicing checks
DEVPRO := devpro
DEVPRO_SNIPPET_FILE := $(lastword $(MAKEFILE_LIST))

.PHONY: devpro-help devpro devpro-check-plan devpro-check-design devpro-check-design-deltas-applied devpro-check-roadmap

devpro-help:
	@grep '^#   devpro' "$(DEVPRO_SNIPPET_FILE)" | sed 's:^#: :'

devpro:
	@$(DEVPRO) --help

devpro-check-plan:
	@$(DEVPRO) check-plan

devpro-check-design:
	@$(DEVPRO) check-design

devpro-check-design-deltas-applied:
	@$(DEVPRO) check-design --deltas-applied

devpro-check-roadmap:
	@$(DEVPRO) check-roadmap
