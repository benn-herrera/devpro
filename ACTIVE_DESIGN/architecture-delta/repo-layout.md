### [Repo Layout](../../PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

**As it stands:**

```
the board panel `devpro/dicing/kanban`'s (Install, Harness profiler)
```

**Becomes:**

```
the board panel `devpro/kanban`'s (Install, Harness profiler)
```

**As it stands:**

```
the walk is repeated rather than shared, so the dashboard loads nothing of the check seam.
```

**Becomes:**

```
the walk is repeated rather than shared, so the dashboard's root walk calls nothing of the check seam; through its board panel the dashboard loads `doccheck/`'s model, and runs none of the check verbs.
```

**As it stands:**

```
  dicing/               the absorbed dicing package — the docdicer project's dicer, checks and board as devpro code, run as devpro's dicing and check verbs (Dicing and Checks); importable Python, the board's assets (kanban/assets/) the package data it ships (Packaging), the absorbed project's contract documents carried into Dicing and Checks, its tests joining the devpro test surface
  dicing-snippets/      shipped package, owned by `docdicer` and so delivered by every project install — the runner snippets (devpro.just, devpro.mk) a project install writes the consuming project's include line for, which run the `devpro` command from `PATH`; nothing importable; installed under <install-dir>/skills/docdicer/dicing-snippets/, inside the docdicer skill's own directory (the `SHIPPED_PACKAGES` row, devpro/install.py)
```

**Becomes:**

```
  dicing/               the absorbed dicing package — the docdicer project's dicer and its tree and link checks as devpro code, run as devpro's dicing verbs, `check-links` and `check-tree` among them (Dicing and Checks); importable Python, the absorbed project's contract documents carried into Dicing and Checks, its tests joining the devpro test surface
  doccheck/             the workflow documents' validation — `planform.py` the model of the plan, design and roadmap forms, `plancheck.py` the check verbs' implementation, `cli.py` the `check-plan`, `check-design` and `check-roadmap` verbs' argparse and dispatch (Packaging); importable Python
  kanban/               the board, the dashboard's board panel — it presents the document set `doccheck/`'s model reads and validates nothing itself; importable Python, its assets (kanban/assets/) package data (Packaging)
  runner-snippets/      shipped in the devpro tools package, delivered by every install — the runner snippets (devpro.just, devpro.mk) a project install writes the consuming project's include line for, which run devpro through the installation's wrapper, `tools/devpro.sh`; nothing importable; installed under <install-dir>/tools/runner-snippets/ (the `SHIPPED_PACKAGES` row, devpro/install.py)
```

**As it stands:**

```
The three deployed surfaces are absent from this listing:
```

**Becomes:**

```
The package's modules depend one way: `kanban/` imports `doccheck/` and `dicing.dicerlib`,
`doccheck/` imports `dicing.dicerlib`, `profiler/` reads `kanban/`'s stylesheet as package data,
`dashboard/` imports the panels it serves, and none of them depends on a module that depends on it.

The three deployed surfaces are absent from this listing:
```

