### [Harness profiler](../../PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

**As it stands:**

```
`hp.sh`, the POSIX-sh launcher, which finds the `devpro` command and runs its `profiler` verb (no
environment variable overrides the search).
```

**Becomes:**

```
`hp.sh`, the POSIX-sh launcher, which finds a devpro — the installation's own wrapper first — and
runs its `profiler` verb (no environment variable overrides the search).
```

**As it stands:**

```
**The launcher's finder.** The finder extends `PATH` with `/opt/homebrew/bin`, `/usr/local/bin` and
`~/.local/bin`, since a hook may run with a `PATH` where only the shell's builtins are found, and
runs one `command -v` over the whole of it. A candidate is the devpro when it runs and exits 0 on
`--version` — the found command is the one `profiler` runs —
```

**Becomes:**

```
**The launcher's finder.** Its first candidate is the installation's wrapper (SPEC.md, Deployed
Surfaces, Shipped files), resolved from the launcher's own location: `../tools/devpro.sh` from
`<install-dir>/profiler/hp.sh`, and `../skills/devpro/tools/devpro.sh` from the committed
`.claude/harness-profiler/hp.sh`. Its fallback extends `PATH` with `/opt/homebrew/bin`,
`/usr/local/bin` and `~/.local/bin`, since a hook may run with a `PATH` where only the shell's
builtins are found, and runs one `command -v` over the whole of it. A candidate, the wrapper as any
other, is the devpro when it runs and exits 0 on `--version`, so a wrapper that finds no usable
Python is treated as absent and the capture still exits 0 with no output — the found command is the
one `profiler` runs —
```

**As it stands:**

```
It carries no palette of its own: its
`<style>` opens with the `CSS_SLOT` mark, which `render_html` fills with the presentation layer's
text — the board's own stylesheet, `devpro/dicing/kanban/assets/board.css`, read the same way — for
the standalone page alone, which loads nothing from the network and so cannot link it.
```

**Becomes:**

```
It carries no palette of its own: its head carries the layer's carriage mark, `<!--LAYER-->`
(`LAYER_MARK`), which `render_html` fills with the presentation layer's text inline — the board's
own stylesheet, `devpro/kanban/assets/board.css`, read the same way — for the standalone page,
which loads nothing from the network and so cannot link it, and which the serve path
(`served_page`) fills with a link to that stylesheet.
```

**As it stands:**

```
The template's `LEGEND_SLOT` mark is where
the how-to-read legend goes:
```

**Becomes:**

```
The frame band's `<!--LEGEND-->` mark is where the how-to-read legend goes:
```

**As it stands:**

```
The index's `INDEX` template fills the same `CSS_SLOT`,
```

**Becomes:**

```
The index's `INDEX` template carries the same `<!--LAYER-->` mark,
```

**As it stands:**

```
sibling panel, `devpro.dicing.kanban.server`'s `KanbanServer` over the dashboard's root.
```

**Becomes:**

```
sibling panel, `devpro.kanban.server`'s `KanbanServer` over the dashboard's root.
```

**As it stands:**

```
**The skill.** `show-profile` ships as a rendered skill definition under `devpro/definitions/`, so it
carries the generated banner and the harness's namespace (`devpro:show-profile` under claude)
```

**Becomes:**

```
**The skill.** `profiler` ships as a rendered skill definition under `devpro/definitions/`, so it
carries the generated banner and the harness's namespace (`devpro:profiler` under claude)
```

**As it stands:**

```
`.claude/skills/show-profile/SKILL.md` from the definition,
```

**Becomes:**

```
`.claude/skills/profiler/SKILL.md` from the definition,
```

**As it stands:**

```
unlinks the files an older `init` left beside the launcher: `hp.py` and `view.html`, which no install
ships any more.
```

**Becomes:**

```
unlinks the files an older `init` left beside the launcher: `hp.py` and `view.html`, which no install
ships any more — and the skill an older `init` rendered under its former name,
`.claude/skills/show-profile/SKILL.md`, with its directory where that leaves it empty.
```

**As it stands:**

```
`profiler/hp.sh` beside the plugin's `profiler.ts`, and the show-profile skill's first finder
candidate resolves it. The payload is copied, not wired: opencode registers no hook entry, so no
committed copy arises, and the store the plugin writes is read by `devpro profiler tree` run from the
`devpro` command's `PATH`.
```

**Becomes:**

```
`profiler/hp.sh` beside the plugin's `profiler.ts`, and the profiler skill's first finder
candidate resolves it. The payload is copied, not wired: opencode registers no hook entry, so no
committed copy arises, and the store the plugin writes is read by `profiler tree` run through the
launcher, whose finder takes the installation's wrapper first.
```

**As it stands:**

```
`devpro profiler doctor` reports `devpro:` the executable the launcher's finder
would resolve — `devpro_executable`'s first candidate that exists and is executable, the same search
the launcher's one `command -v` makes,
```

**Becomes:**

```
`devpro profiler doctor` reports `devpro:` the executable the launcher's finder
would resolve — `devpro_executable`'s first candidate that exists and is executable, the same search
the launcher makes, the installation's wrapper first and then the one `command -v`,
```

**As it stands:**

```
or `not found on PATH, in Homebrew or ~/.local/bin (install devpro)`
```

**Becomes:**

```
or `not found in the installation, on PATH, in Homebrew or ~/.local/bin (install devpro)`
```

