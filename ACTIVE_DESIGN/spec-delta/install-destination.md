### [Install destination](../../PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md)

**As it stands:**

```
the registry `registry.json`), prunes as any install does, and writes nothing else but, under opencode,
the plugin entry, a harness resource without which the plugin cannot register: no other harness resource, no
install-time probe or guardrail registration (Shipped files), no shipped package (none of
`kb-tools/`, the dicing snippets package and the development scripts package), no runner include
line and no runner file.
```

**Becomes:**

```
the registry `registry.json`), prunes as any install does, and writes nothing else but the devpro
tools package (Shipped files) and, under opencode, the plugin entry, a harness resource without
which the plugin cannot register: no other harness resource, no install-time probe or guardrail
registration (Shipped files), no other shipped package (neither `kb-tools/` nor the development
scripts package), no runner include line and no runner file.
```

**As it stands:**

```
unsupported name is refused before anything is written. `render` defaults it to `claude`; install
```

**Becomes:**

```
unsupported name is refused before anything is written. `dev-render` defaults it to `claude`; install
```

**As it stands:**

```
naming them, where the file selects the harnesses — `--harness` given, and `render`, do not judge
it.
```

**Becomes:**

```
naming them, where the file selects the harnesses — `--harness` given, and `dev-render`, do not
judge it.
```

