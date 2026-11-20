### [SPEC.md, Guide and README](../../PROJECT_DOCS/SPEC/guide-and-readme.md)

The guide's delivery statement, the mage directory and the requirements list take the one plugin,
the component and the profiler.

```
The `guide` skill is where a session starts or continues work with devpro. Both plugins ship it
under every harness (SPEC.md, Deployed Surfaces, Plugins).
```
becomes
```
The `guide` skill is where a session starts or continues work with devpro. Every install carries it
under every harness (SPEC.md, Deployed Surfaces, Plugins).
```

```
    which writes `~/Mage/Skills/<plugin>/`, and, for the kbase plugin, restarting Mage;
```
becomes
```
    which writes `~/Mage/Skills/devpro/`, and, with the kbase component, restarting Mage;
```

```
  - the requirements: `just` 1.33.0 or later where the consuming project's runner is a justfile,
    for the runner include lines; `perl` with core `JSON::PP` for the claude guardrail;
```
becomes
```
  - the requirements: `just` 1.33.0 or later where the consuming project's runner is a justfile,
    for the runner include lines; `perl` with core `JSON::PP` for the claude guardrail; `node` 18 or
    later for the claude activity profiler, whose captures stay silent without it;
```

