# The delta application ends verified in the development skill, run by docdicer's check

The developers who work in a project devpro equips get mechanical confirmation that a design entry's
delta was applied, from the skill that tells them to apply it rather than from each project's own
conventions. The check reaches them in the runner snippets every install already writes, and devpro's
own CONVENTIONS names the local rule and target beside the skill's.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## ARCHITECTURE delta

### [Recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md)

**As it stands:**

```markdown
(SPEC.md, Guide and README). That import is the install's own snippet,
`.claude/skills/devpro/skills/docdicer/tools/runner-snippets/docdicer.just`, so this checkout needs
one `just agents` run before its docdicer recipes exist: until it has run, the `docs` surface —
`just check-links`, and so `just test` and `just test-changed` on any document — fails with
`Does not contain recipe 'docdicer'`. The byte-check over a design's pending deltas, SPEC.md and
ARCHITECTURE.md, is `check-design --deltas-applied`, which the snippet set exposes as
`docdicer-check-design-deltas-applied`; this repository runs it through the private `dev-dd`, as
`just dev-check-design-deltas-applied`, against the hosted clone. The private `_venv` recipe creates
`.venv`
```

**Becomes:**

```markdown
(SPEC.md, Guide and README). That import is the install's own snippet,
`.claude/skills/devpro/skills/docdicer/tools/runner-snippets/docdicer.just`, so this checkout needs
one `just agents` run before its docdicer recipes exist: until it has run, the `docs` surface —
`just check-links`, and so `just test` and `just test-changed` on any document — fails with
`Does not contain recipe 'docdicer'`. A design's delta application is verified by
`check-design --deltas-applied`, which the snippet set exposes as
`docdicer-check-design-deltas-applied`; this repository runs it as
`just dev-check-design-deltas-applied`, through `dev-dd` against the hosted clone. The `_venv`
recipe creates `.venv`
```

## Code delta

### [devpro/definitions/skills/development.py](devpro/definitions/skills/development.py)

The application bullet under *Design* names only the link check as what confirms an application, so
the shipped skill states no byte-check and an agent applying a delta reads its work as done once
links resolve. The bullet's confirming sentence names the project's delta check beside the link
check, states what it shows, and makes the application finish on its passing run; where the
project's runner carries the check, the sentence names its target.

**As it stands:**

```markdown
  confirms them; its delta check (`check-design --deltas-applied`, where the project carries it)
  confirms each `becomes` block occurs byte-exact in its target and, where the becomes-text does not
  contain it, that the from-text is gone. *Purpose:* the text the user accepted reaches the contract
  documents as accepted, its links still resolving, with nothing left unapplied.
```

**Becomes:**

```markdown
  confirms them. Where the project's runner carries a delta check
  (`docdicer-check-design-deltas-applied`), its run confirms each pair's `becomes` block occurs in
  its target with each run of whitespace read as one space, and the from-text is gone where the
  becomes-text does not contain it; the application is done when that run reports every pair landed.
  An entry that states a whole leaf or a removal has no pair for it to confirm.
  *Purpose:* the text the user accepted reaches the contract documents as accepted, its links still
  resolving.
```
