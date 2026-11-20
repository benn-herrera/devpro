### [ARCHITECTURE.md, Why There Is No Verification Verb](../../PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md)

The render and wheel scripts collapse to one slot project per slot: `devtools/scripts/render.sh`
renders one slot project with `--components=kbase` and drops its `--plugin` refusal,
`_render-slot.sh` writes `rendered/<slug>/devpro/` alone, `check-wheel.sh` runs one install with the
component on and asserts `devpro/CLAUDE.md`, and `_plugin-names.sh` is deleted. The test pins
re-anchor: `tests/test_plugins.py`'s include/exclude, two-plugin-render and agents-file pins rewrite
to the components shape; `tests/test_devpro.py`'s `mcp__plugin_kbase_kbase__query` pin becomes
`mcp__plugin_devpro_kbase__query` and its KBASE-plugin render pins become component-on pins;
`tests/test_devpro_install.py`'s DEVPRO/KBASE parametrization becomes a components matrix and its
doubled-path pin spells the single path; `tests/test_install_target.py`'s `--plugin=kbase` pins
become `--components=kbase` pins; `tests/test_kbase_surface.py`, `tests/test_opencode_entry.py` and
`tests/_structure.py` re-anchor to the one install directory. Obviated pins are deleted, not parked.
The rewritten statements are the delta entries above.

