### [Subsystem Map](../../PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

**As it stands:**

```
`docdicer.py` routes the session to devpro's dicing verbs — `devpro dice-doc`, `devpro undice`
  and the check verbs — run from the command line,
```

**Becomes:**

```
`docdicer.py` routes the session to devpro's dicing verbs — `dice-doc`, `undice` and the check
  verbs — run from the command line through the installation's wrapper, `../../tools/devpro.sh`
  from the skill's directory (SPEC.md, Deployed Surfaces, Installed tree),
```

**As it stands:**

```
with a direct `devpro` call for any other
  (Plugins). Its board paragraph names the `devpro dashboard` verb for the board
```

**Becomes:**

```
with a direct call through the wrapper for any other
  (Plugins). Its board paragraph names the `dashboard` verb, run through the wrapper, for the board
```

**As it stands:**

```
served over HTTP: its serve sections name the `devpro dashboard` verb,
```

**Becomes:**

```
served over HTTP: its serve sections name the `dashboard` verb, run through the installation's
  wrapper,
```

**As it stands:**

```
the launcher
  runs the `profiler` verb of the `devpro` command it finds (Install, Harness profiler).
```

**Becomes:**

```
the launcher
  runs the `profiler` verb of the devpro its finder resolves, the installation's wrapper first
  (Install, Harness profiler).
```

**As it stands:**

```
Its board section routes the board to the `devpro dashboard` verb — the
  board is the dashboard's panel — and names no launcher path or recipe: the launcher paths and
  recipes it named are retired with the docdicer tools package (Plugins).
```

**Becomes:**

```
Its board section routes the board to the `dashboard` verb, run through the installation's
  wrapper — the board is the dashboard's panel — and names no recipe; its install, update and
  version commands name the `devpro` command on `PATH` (SPEC.md, Deployed Surfaces, Shipped files).
```

**As it stands:**

```
project's runner includes that set, the checks run through the recipes (`devpro`, and by name
  `devpro-help`,
```

**Becomes:**

```
project's runner includes that set, the checks run through the recipes (by name `devpro-help`,
```

**As it stands:**

```
- **Profile skill** — `show-profile` (`definitions/show_profile.py`):
```

**Becomes:**

```
- **Profile skill** — `profiler` (`definitions/profiler.py`):
```

