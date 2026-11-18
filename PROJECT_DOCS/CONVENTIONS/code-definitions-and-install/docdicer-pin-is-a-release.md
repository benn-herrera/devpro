### Docdicer pin is a release

`VERSION` in `devpro/docdicer-tools/docdicer` (ARCHITECTURE.md, Subsystem Map) names a released
docdicer version, one tagged `v<VERSION>` and pushed, never a commit, a branch or an untagged
version.

`just docdicer …`, and every recipe routing through it, runs the installed copy of the launcher
under `.opencode/plugins/devpro/skills/docdicer/tools/` (ARCHITECTURE.md, Plugins), not the source
here: a change to the launcher reaches that copy only at the next `devpro install`, and a recipe run
before it is evidence about the copy, not about the edit.

The pin's value has no machine check: `tests/test_docdicer_tools.py` reads `VERSION` and builds the
installed URL from it, with pip stubbed, so a `VERSION` naming a tag no remote holds passes every
test and fails only where the launcher builds the venv beside itself. Bump `VERSION` only once the
tag is pushed.
