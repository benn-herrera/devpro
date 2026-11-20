### [ARCHITECTURE.md, Subsystem Map](../../PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

The kbase bullet becomes the component's, and the both-plugins phrases name the one install.

```
- **kbase plugin + kbase** — the `kbase` skill alone: the definition the devpro plugin excludes by name
  and the kbase plugin delivers with the others SPEC.md, Deployed Surfaces, Plugins lists
  (`devpro/plugins/kbase.py`). `kbase.py` owns a directory,
```
becomes
```
- **kbase component + kbase** — the `kbase` skill alone: the definition the kbase component adds to
  the devpro set, named among the component's contents in SPEC.md, Deployed Surfaces, Plugins
  (`devpro/components.py`). `kbase.py` owns a directory,
```

```
consuming project's `kb-root/AGENTS.md`, under every harness. The kbase plugin reaches kbase, the
```
becomes
```
consuming project's `kb-root/AGENTS.md`, under every harness. The kbase component reaches kbase, the
```

```
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered with its
  tools package by both plugins.
```
becomes
```
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered with its
  tools package by every install.
```

```
  `references/installing.md` and `references/using.md`, carried as `SkillFile`s, delivered by both
  plugins under every harness.
```
becomes
```
  `references/installing.md` and `references/using.md`, carried as `SkillFile`s, delivered
  under every harness.
```

```
The `development` and `docdicer` rows name their skill
  by a plain reference (`clauses.ref`), safe because both plugins ship both.
```
becomes
```
The `development` and `docdicer` rows name their skill
  by a plain reference (`clauses.ref`), safe because every install carries both.
```

```
  - an optional reference to `kbase` (`clauses.optional_ref`), which hands installing kbase itself
    to that skill. It is kept in the kbase plugin alone.
```
becomes
```
  - an optional reference to `kbase` (`clauses.optional_ref`), which hands installing kbase itself
    to that skill. It is kept where the kbase component is on.
```

```
  `adopting.md`, `release.md`, `design.md`), carried as `SkillFile`s, delivered by both plugins under every
  harness, mage included.
```
becomes
```
  `adopting.md`, `release.md`, `design.md`), carried as `SkillFile`s, delivered under every
  harness, mage included.
```

```
  `docdicer` references are optional references (Rendering, Placeholders), and `docdicer` ships
  with both plugins, so each fills. The *Plan status* and *Roadmap tickets* sections render whole
  under every plugin; each one's
```
becomes
```
  `docdicer` references are optional references (Rendering, Placeholders), and `docdicer` ships
  with every install, so each fills. The *Plan status* and *Roadmap tickets* sections render whole
  under every install; each one's
```

