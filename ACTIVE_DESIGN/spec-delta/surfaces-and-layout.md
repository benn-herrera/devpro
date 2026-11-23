### [Surfaces and layout](../../PROJECT_DOCS/SPEC/deployed-surfaces/surfaces-and-layout.md)

**As it stands:**

```
produced to order into the output root an invocation names: `devpro render --out <dir>
[--components=CSV]` renders
```

**Becomes:**

```
produced to order into the output root an invocation names: `devpro dev-render --out <dir>
[--components=CSV]`, a maintainer verb (Package and Command), renders
```

**As it stands:**

```
A project install places each shipped package in the
directory of the skill it belongs to, where that skill ships:
- the development scripts package — a script that runs one agent on a brief with no tools — in the
  `development` skill's;
- the dicing snippets package — the absorbed dicing verbs' runner shortcuts (Shipped files) — in the
  `docdicer` skill's;
- the kb-tools package in the `kbase` skill's.
```

**Becomes:**

```
A project install places each skill-owned shipped package in the directory of the skill it belongs
to, where that skill ships, and the devpro tools package at the install directory's `tools/`
(Shipped files):
- the development scripts package — a script that runs one agent on a brief with no tools — in the
  `development` skill's;
- the kb-tools package in the `kbase` skill's.
```

