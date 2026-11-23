### [Shipped files](../../PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```
inside the `development` skill's own directory (below), and the **dicing snippets package**
(below), under mage as under claude and opencode. An
install with the kbase component also delivers the kb-tools package (below). A user-level install
delivers none (SPEC.md,
Deployed Surfaces, Install destination). No dicing code ships in a package: the dicing, check and
board verbs run as verbs of the `devpro` command (Package and Command, Dicing and Checks); the
dicing snippets package holds only their runner shortcuts.
```

**Becomes:**

```
inside the `development` skill's own directory (below), and the **devpro tools package**, `tools/`
(below), under mage as under claude and opencode. An install with the kbase component also delivers
the kb-tools package (below). A user-level install delivers the devpro tools package alone (SPEC.md,
Deployed Surfaces, Install destination).
```

**As it stands:**

```
The dicing snippets package is a shipped package installed at its own stated destination:
`skills/docdicer/dicing-snippets/`, inside the `docdicer` skill's own directory, holding only the
runner snippets, not an importable package either, read by the consuming project through the same
runner include line. The snippets run the `devpro` command from `PATH`. They define the recipes
`devpro`, `devpro-help`, `devpro-check-plan`, `devpro-check-design`,
`devpro-check-design-deltas-applied` and `devpro-check-roadmap`: the bare `devpro` printing the
command's help, and `devpro-help` showing the commands and their doc strings.
```

**Becomes:**

```
The devpro tools package is a shipped package installed at its own stated destination: `tools/`,
directly under the install directory, inside no skill's directory. It holds:

- `tools/devpro/`, a copy of the devpro package that ran the install, byte-verbatim, less what no
  install copies (Install destination);
- `tools/devpro.sh`, the wrapper, carrying the installed banner below its shebang, which runs that
  copy as `python3 -m devpro` does, its arguments passed through: under the base interpreter that
  ran the install — that Python's own executable, never a virtual environment's — where that path
  exists; otherwise under the first `python3` on `PATH`, where it is Python 3.9 or later; otherwise
  it exits non-zero, saying devpro needs Python 3.9 or later. It looks for no other interpreter;
- `tools/runner-snippets/`, the runner snippets, not an importable package, read by the consuming
  project through the same runner include line.

Every installed file that runs devpro, and every command a definition gives a session to run
devpro, runs it through the wrapper, never the `devpro` command from `PATH` — except
`devpro install`, `devpro install-agents-file` and `devpro --version`, which install, update by
installing again, and report the version that would install, and so name the `devpro` command on
`PATH`. The `devpro` command on `PATH` never hands off to an installation's copy, and only an
install replaces the copy. The snippets define the recipes `devpro-help`, `devpro-check-plan`,
`devpro-check-design`, `devpro-check-design-deltas-applied` and `devpro-check-roadmap`:
`devpro-help` showing the commands and their doc strings, then the command's help.
```

**As it stands:**

```
`show-profile` skill, which renders a session's recorded activity
```

**Becomes:**

```
`profiler` skill, which renders a session's recorded activity
```

