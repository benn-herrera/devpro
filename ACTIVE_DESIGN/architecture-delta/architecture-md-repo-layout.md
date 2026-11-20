### [ARCHITECTURE.md, Repo Layout](../../PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

The slots hold one project, the plugin rows give way to the components module, and the resources
row names the profiler's files.

```
rendered/               gitignored build product — this repo's own rendered tree, one slot per rendering, each holding one slot project per plugin (`rendered/<slug>/devpro/`, `rendered/<slug>/kbase/`), and the four `reference*` slots, one per harness plus gemma, `render-diff` compares against (justfile RENDERED_DIR); created on demand
```
becomes
```
rendered/               gitignored build product — this repo's own rendered tree, one slot per rendering, each holding one slot project (`rendered/<slug>/devpro/`), and the four `reference*` slots, one per harness plus gemma, `render-diff` compares against (justfile RENDERED_DIR); created on demand
```

```
  plugin.py             the `Plugin` type: a name and either the definition names it ships or the ones it leaves out, with `ships(name)` (Rendering, Harnesses and families)
  plugins/              one module per plugin, each defining `PLUGIN` and nothing else — `devpro.py` and `kbase.py`; which definitions each ships is SPEC.md, Deployed Surfaces, Plugins (CONVENTIONS.md, Plugin membership has one home)
```
becomes
```
  components.py         the definition selection: the member lists of the optional components (`kbase`), the required set being every discovered definition no component names, with `ships(name)` (Rendering, Harnesses and families); which definitions ship is SPEC.md, Deployed Surfaces, Plugins (CONVENTIONS.md, Plugin membership has one home)
```

```
  kb-tools/             shipped package, owned by `kbase` and so delivered only by the kbase plugin — the runner snippets
```
becomes
```
  kb-tools/             shipped package, owned by `kbase` and so delivered only with the kbase component — the runner snippets
```

```
  docdicer-tools/       shipped package, owned by `docdicer` and so delivered by every project install of either plugin — the `docdicer` bash launcher,
```
becomes
```
  docdicer-tools/       shipped package, owned by `docdicer` and so delivered by every project install — the `docdicer` bash launcher,
```

```
  development-tools/    shipped package, owned by `development` and so delivered by every project install of either plugin — `cold-read.sh`,
```
becomes
```
  development-tools/    shipped package, owned by `development` and so delivered by every project install — `cold-read.sh`,
```

```
and `claude/hooks/guardrail.pl` and `claude/hooks/state-table-reminder.sh`, and no `__init__.py`, so `load` still reads one harness per module; mage ships none
```
becomes
```
and `claude/hooks/guardrail.pl` and `claude/hooks/state-table-reminder.sh`, and `claude/libexec/hp.sh`, `claude/libexec/hp.js` and `claude/libexec/view.html` (the activity profiler, Install, Harness profiler), and no `__init__.py`, so `load` still reads one harness per module; mage ships none
```

