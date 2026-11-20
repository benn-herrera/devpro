### [ARCHITECTURE.md, Rendering, Harnesses and families](../../PROJECT_DOCS/ARCHITECTURE/rendering/harnesses-and-families.md)

`devpro/plugin.py` and `devpro/plugins/` (`__init__.py`, `devpro.py`, `kbase.py`) are deleted, and
`devpro/components.py` replaces them: the optional components' member lists (`kbase` enumerating the
`kbase` skill), the required set being every discovered definition no component names — the
joins-by-existing mechanism `devpro.py` embodied stays for it — with `ships(name)` read as before.
`context.py`'s `plugins()`, `plugin_named()` and `DEFAULT_PLUGIN` retire with them; `build_render`
takes the components and validates every member name against `discover()`; `Render` carries the
selection; `clauses.PLUGIN_NAME` fills the one name. `harnesses/mage.py`'s `project_harness_dir`
becomes the constant `devpro`, the `{plugin}` binding machinery in `harness.py` staying for the
markers and prefixes. The rewritten statements are the delta entries above.

