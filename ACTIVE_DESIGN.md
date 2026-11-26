# Four changes: wheel-staged installs, TOML settings, profiler verb removal, claude agents-path overlay

The devpro install stages both of its paths from one manifest — the built wheel's — so a dev-loop
install writes exactly what consumers install; the devpro settings file is TOML, the format
`tomllib` reads with no dependency and no conversion of old files; the profiler's one-off `doctor`
and `repair` verbs are gone from the code, its usage text, its tests and every document that
records them; and the `development` skill rendered under claude states where the plugin's agents
files sit, a fact the claude session seat otherwise has no statement of. Consumers get installs
that cannot silently miss a file, a settings file whose nesting is native, a profiler surface
without dead verbs, and — under claude — a session that knows its agents directory.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Rendering](PROJECT_DOCS/SPEC/rendering.md#rendering)

**As it stands:**
```
or whole from the **devpro settings file**'s `[<harness>-model-map]` section for the harness
being rendered — a **category spec**, the text form of a category map, written in that section
as one `<glob>=<model>` entry per line: each glob matched against the six category names and its
`<model>` assigned to every category it matches, later entries silently overwriting earlier
ones (`*=<model>` names all six; `*-architect=<model>` names both architect categories; a full
category name names one), though a glob repeated in one section is refused, naming the line. An
entry matching no category is refused, and a section leaving a category unnamed at its end is
refused, with no fallback to the family.
```
**Becomes:**
```
or whole from the **devpro settings file**'s `[<harness>.model-map]` table for the harness
being rendered — a **category spec**, the text form of a category map, written in that table
as one `"<glob>" = "<model>"` entry: each glob matched against the six category names and its
`<model>` assigned to every category it matches, later entries silently overwriting earlier
ones (`"*"` names all six; `"*-architect"` names both architect categories; a full
category name names one). An
entry matching no category is refused, and a table leaving a category unnamed at its end is
refused, with no fallback to the family.
```

**As it stands:**
```
  The devpro settings file is `~/.config/devpro/devpro.cfg`, or the file `--config-file` names;
  the path is taken as given — there is no search, the default path or the one named — and the
  default file's absence is no config at all, while an explicitly named file that does not exist
  is refused, naming the path. Its sections are named per harness: `[<harness>]` carries the
  harness's settings, its `install` (SPEC.md, Install destination) and `components` (SPEC.md,
  Deployed Surfaces, Plugins) values among them;
  `[<harness>-model-map]` carries its model map. A section that is neither a supported harness's
  `[<harness>]` nor its `[<harness>-model-map]` — a `[DEFAULT]` section holding entries among
  them — is refused, naming the section and the supported harnesses; a key in a settings section
  that is no setting of it is refused, naming the map section it belongs in; a file that does not
  parse is refused before anything is written, naming the file and the line.
```
**Becomes:**
```
  The devpro settings file is `~/.config/devpro/devpro.toml`, or the file `--config-file` names;
  the path is taken as given — there is no search, the default path or the one named — and the
  default file's absence is no config at all, while an explicitly named file that does not exist
  is refused, naming the path. Its tables are named per harness: `[<harness>]` carries the
  harness's settings, its `install` (SPEC.md, Install destination) and `components` (SPEC.md,
  Deployed Surfaces, Plugins) values among them;
  `[<harness>.model-map]` carries its model map. A table that is neither a supported harness's
  `[<harness>]` nor its `[<harness>.model-map]` is refused, naming the table and the supported
  harnesses; a key in a settings table that is no setting of it is refused, naming the model-map
  table it belongs in; a file that does not
  parse is refused before anything is written, naming the file and the line.
```

### [Guide and README](PROJECT_DOCS/SPEC/guide-and-readme.md#guide-and-readme)

**As it stands:**
```
  - the devpro settings file: its location (`~/.config/devpro/devpro.cfg`, `--config-file` to
    name another), the `install` setting's three values in `[<harness>]`, and the entries in each
    harness's `[<harness>-model-map]` section;
```
**Becomes:**
```
  - the devpro settings file: its location (`~/.config/devpro/devpro.toml`, `--config-file` to
    name another), the `install` setting's three values in `[<harness>]`, and the entries in each
    harness's `[<harness>.model-map]` table;
```

### [Install destination](PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md#install-destination)

**As it stands:**
```
An install writes into its install directory: every definition its plugin carries,
rendered by that same invocation, together with the shipped packages those definitions read (Shipped files),
each at its package destination, and the harness resources, copied into that same directory as they
stand (Shipped files). What is not part of the install product does not travel: test suites and their
fixtures, caches, `.DS_Store`, backup (`.bak`) copies, a `.venv` directory, and this repository's
own project documentation. That project documentation exclusion is a list of file names (`SPEC.md`,
`ARCHITECTURE.md`, `CONVENTIONS.md`, `THESIS.md`, `ROADMAP.md`, `AGENTS.md`, `CLAUDE.md`): none is
installed at any depth under a package destination. No installed file refers its reader to one of
this repository's own project documents. `README.md` is not in that exclusion: a shipped package's
`README.md` is installed.
```
**Becomes:**
```
An install writes into its install directory: every definition its plugin carries,
rendered by that same invocation, together with the shipped packages those definitions read (Shipped files),
each at its package destination, and the harness resources, copied into that same directory as they
stand (Shipped files). What an install produces is the built package's file set, and the build is
the one thing that filters it: the wheel carries this repository's own project documentation
nowhere, and neither test suites, caches nor a `.venv`. An install from a checkout of this
repository (`PYTHONPATH=<clone> python3 -m devpro install …`) has no build between it and the
source, so it stages the clone's tree as it stands. No installed file refers its reader to one of
this repository's own project documents. `README.md` is not in that exclusion: a shipped package's
`README.md` is installed.
```

**As it stands:**
```
one invocation installs for every harness it names, in name
order, each as its own install — the render built per harness from that harness's
`[<harness>-model-map]` section, where the file has one — with this section's guarantees; a
```
**Becomes:**
```
one invocation installs for every harness it names, in name
order, each as its own install — the render built per harness from that harness's
`[<harness>.model-map]` table, where the file has one — with this section's guarantees; a
```

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md#shipped-files)

**As it stands:**
```
- `tools/devpro/`, a copy of the devpro package that ran the install, byte-verbatim, less what no
  install copies (Install destination);
```
**Becomes:**
```
- `tools/devpro/`, a copy of the devpro package that ran the install — the wheel content it staged
  from (Install destination) — byte-verbatim;
```

**As it stands:**
```
machine that runs the server. Every presentation of a recorded moment — the pages, the index, the
text tree and `profiler doctor`'s lines — reads in the reader's local time, and none shows UTC, a
```
**Becomes:**
```
machine that runs the server. Every presentation of a recorded moment — the pages, the index and the
text tree — reads in the reader's local time, and none shows UTC, a
```

The sentence `A `.venv` directly under a package destination is not install output.` is removed —
no venv is ever delivered and none is created under an install directory, so the statement names a
case that does not arise.

### [Surfaces and layout](PROJECT_DOCS/SPEC/deployed-surfaces/surfaces-and-layout.md#surfaces-and-layout)

**As it stands:**
```
Plugins states the `--components` default. From a checkout of this repository the same command runs as
`PYTHONPATH=<clone> python3 -m devpro install …`, with the same result (Package and Command).
```
**Becomes:**
```
Plugins states the `--components` default. From a checkout of this repository the same command runs as
`PYTHONPATH=<clone> python3 -m devpro install …` (Package and Command), and it stages the clone's tree
as it stands; the repository's own installs stage from the built package the build produces first
(Package and Command).
```

## ARCHITECTURE delta

### [Harnesses and families](PROJECT_DOCS/ARCHITECTURE/rendering/harnesses-and-families.md#harnesses-and-families)

**As it stands:**
```
the six
harness-specific paragraphs, typed `OptionalHarnessText` — `recipe_rule`, `kbase_project_rule`
(supplied under mage alone, whose server is started `--project-dir-required`), `reload_rule`
(supplied under claude alone: the sentence a claude install prints and the `guide` skill's
installation reference carries), `tools_reload_rule` (supplied under claude alone: the sentence the
`kbase` skill entry file and installation reference carry),
`side_by_side_rule` (supplied under opencode alone, in its own
paragraph of that reference) and `cold_read_rule` (supplied under every harness: claude and opencode share
`harness.COLD_READ_SCRIPT_RULE`, which runs `cold-read.sh`, opencode adding that the script is not yet
reliable there, and mage, whose copy of the script refuses to run, says to start the reader by
hand);
```
**Becomes:**
```
the seven
harness-specific paragraphs, typed `OptionalHarnessText` — `recipe_rule`, `kbase_project_rule`
(supplied under mage alone, whose server is started `--project-dir-required`), `reload_rule`
(supplied under claude alone: the sentence a claude install prints and the `guide` skill's
installation reference carries), `tools_reload_rule` (supplied under claude alone: the sentence the
`kbase` skill entry file and installation reference carry),
`side_by_side_rule` (supplied under opencode alone, in its own
paragraph of that reference), `agents_path` (supplied under claude alone: the sentence the
`development` skill's body carries naming the plugin's agents directory,
`.claude/skills/devpro/agents/`) and
`cold_read_rule` (supplied under every harness: claude and opencode share
`harness.COLD_READ_SCRIPT_RULE`, which runs `cold-read.sh`, opencode adding that the script is not yet
reliable there, and mage, whose copy of the script refuses to run, says to start the reader by
hand);
```

**As it stands:**
```
1. the devpro settings file's `[<harness>-model-map]` section for the harness — its keys, one
   entry per line under the grammar, joined for the parser; read and validated by
   `devpro/context.py`.
```
**Becomes:**
```
1. the devpro settings file's `[<harness>.model-map]` table for the harness — its keys, one
   `"<glob>" = "<model>"` entry each under the grammar; read and validated by
   `devpro/context.py` with `tomllib`.
```

### [Installing this repository](PROJECT_DOCS/ARCHITECTURE/install/installing-this-repository.md#installing-this-repository)

**As it stands:**
```
`just agents` installs this repository's own `.claude/` and `.opencode/` with the plain
`install` verb, once per harness, as the devpro plugin, naming this repository as TARGET and the
harness with `--harness`.
```
**Becomes:**
```
`just agents` builds the wheel, unpacks it beside it into `dist/` and installs this repository's
own `.claude/` and `.opencode/` with the plain `install` verb run from the unpacked package —
`PYTHONPATH` pointed at it — as the devpro plugin, naming this repository as TARGET, the
harnesses left to the install's own resolution. The unpacked copy stands in the build product's own
directory, there to inspect, and its parent holds no `.git` entry, so by the checkout premise
(Packaging) `PACKAGE_ROOT` resolves outside any checkout: the install stages from wheel content,
as every install does (Renders and copies), and no `git` check answers for this repository.
```

### [Recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md#recipes)

**As it stands:**
```
`agents` installs the devpro set into this checkout in one line — the target alone, no
`--components` and no `--harness` flag, the harness left to the install's own inference;
```
**Becomes:**
```
`agents` builds the wheel and installs this repository's own set from the built package beside it
(Install, Installing this repository), the target alone and any `install` flags it passes through —
an alternate `--config-file` among them — with no
`--components` and no `--harness` flag by default, the harness left to the install's own inference;
```

### [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md#renders-and-copies)

**As it stands:**
```
and removes each file under the install directory's `agents/`, `commands/` or `skills/` that this
run did not write, that `_shipped` admits, and that is ours by its own carrier: frontmatter holding a
`!GENERATED!` line, or a comment line opening with it, which is how a skill's supporting file holds
its banner.
```
**Becomes:**
```
and removes each file under the install directory's `agents/`, `commands/` or `skills/` that this
run did not write, that is ours by its own carrier: frontmatter holding a
`!GENERATED!` line, or a comment line opening with it, which is how a skill's supporting file holds
its banner — save where prune's own guard, below, keeps a file.
```

**As it stands:**
```
A `.venv` directly
under a package destination is outside what `_shipped` admits too, so its files
never enter the stale list.
```
**Becomes:**
```
The staleness rule is prune's own, stated here rather than inherited: a safety copy (a `.bak`
suffix) never enters the stale list. No venv is ever delivered and none is created under an
install directory, so the stale list has no venv case: no file a venv holds is ours by its own
carrier.
```

**As it stands:**
```
The copy exclusions are `_shipped`'s vocabulary, matched at any depth: a directory named `tests`,
`__pycache__`, `.pytest_cache` or `.venv` in the path, a `.DS_Store`, a `.bak` suffix, or one of
`SPEC.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `THESIS.md`, `ROADMAP.md`, `AGENTS.md` and
`CLAUDE.md`. Every copy skips what it excludes — the package copy, which writes each file with the mode the
process umask gives a new file plus the source's execute bits, and the harness resource copy, which
borrows the same vocabulary (below) — and `prune`
removes nothing `_shipped` excludes, so a file outside it is never stale.
```
**Becomes:**
```
Both staging paths stage from the built wheel: the package copy writes the files the running
package holds, and the harness resource copy copies its files as the resource trees stand. The
wheel's content, once built, is what a consumer install writes: it is the install's whole file set,
and the build is the one filter over it — `.dist-info/RECORD` that content's manifest, and
`just check-wheel` holds the declared package data equal to the tree and fails on any of this
repository's own project documents in the wheel (Packaging). An install run from a checkout
(`PYTHONPATH=<clone>`) has no build under it and stages the clone's tree as it stands. Every copy
writes each file with the mode the
process umask gives a new file plus the source's execute bits, and `prune`
keeps its own guard above.
```

**As it stands:**
```
The devpro tools package takes the same package copy for its two rows — `runner-snippets` to
`tools/runner-snippets/`, and the running package, `PACKAGE_ROOT`, to `tools/devpro/` through
`_shipped` and unstamped —
```
**Becomes:**
```
The devpro tools package takes the same package copy for its two rows — `runner-snippets` to
`tools/runner-snippets/`, and the running package, `PACKAGE_ROOT` — the wheel content the run
stages from — to `tools/devpro/` unstamped —
```

**As it stands:**
```
The harness resource copy borrows `_shipped` and nothing else from the package path:
`harness_resource_copies` reads `resources/<harness>/` and writes each file into the install
directory with `copyfile` and `copymode`, so it lands as the harness ships it —
```
**Becomes:**
```
The harness resource copy borrows nothing from the package path:
`harness_resource_copies` reads `resources/<harness>/` — the wheel's own copy of it — and writes
each file into the install
directory with `copyfile` and `copymode`, so it lands as the harness ships it —
```

**As it stands:**
```
The staleness rule is prune's own, stated here rather than inherited: a file below a `.venv`
directory (`VENV_DIR`) directly under a package destination, and a safety copy (a `.bak` suffix),
never enters the stale list.
```
**Becomes:**
```
The staleness rule is prune's own, stated here rather than inherited: a safety copy (a `.bak`
suffix) never enters the stale list. No venv is ever delivered and none is created under an
install directory, so the stale list has no venv case: no file a venv holds is ours by its own
carrier.
```

**As it stands:**
```
`_clear_package_destination` empties the directory a destination is, all but a `.venv`
(`VENV_DIR`) directly under it, and unlinks any other file
there.
```
**Becomes:**
```
`_clear_package_destination` empties the directory a destination is, and unlinks any other file
there.
```

**As it stands:**
```
replaces the destination of each `SHIPPED_PACKAGES` row whose owner ships whole with a copy — a `.venv` directly
below it kept — copies each
```
**Becomes:**
```
replaces the destination of each `SHIPPED_PACKAGES` row whose owner ships whole with a copy — copies each
```

**As it stands:**
```
  managed path at its position below its base. Every `.venv` (`VENV_DIR`) is omitted.
```
**Becomes:**
```
  managed path at its position below its base.
```

**As it stands:**
```
  directory and file created in its place. `.venv` directories (`VENV_DIR`) are outside it.
```
**Becomes:**
```
  directory and file created in its place.
```

### [Packaging](PROJECT_DOCS/ARCHITECTURE/packaging.md#packaging)

**As it stands:**
```
that an install with the kbase component on into a scratch project equals
the checkout's byte for byte, and that a mage install writes `devpro/CLAUDE.md`.
```
**Becomes:**
```
that an install with the kbase component on into a scratch project equals
the wheel's own files byte for byte, and that a mage install writes `devpro/CLAUDE.md`.
```

### [The code belongs to devpro](PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-code-belongs-to-devpro.md#the-code-belongs-to-devpro)

**As it stands:**
```
`hooks.py` the committed hook's wiring — `init` and `doctor` — `stores.py` the stores'
rename and their one repair, and `cli.py` the `profiler` verb's dispatch. The verb is dispatched
lazily: registering it imports none of these modules, and `cli.py` imports the one whose subcommand
runs. Its subcommands are `capture`, `tree`, `init`, `doctor` and `repair`; the records are served by
the `dashboard` verb, below.
```
**Becomes:**
```
`hooks.py` the committed hook's wiring — `init` — `stores.py` the stores'
rename, and `cli.py` the `profiler` verb's dispatch. The verb is dispatched
lazily: registering it imports none of these modules, and `cli.py` imports the one whose subcommand
runs. Its subcommands are `capture`, `tree` and `init`; the records are served by
the `dashboard` verb, below.
```

### The repair — the PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-repair.md leaf, removed

The leaf is removed.

### Doctor lines — the PROJECT_DOCS/ARCHITECTURE/harness-profiler/doctor-lines.md leaf, removed

The leaf is removed.

### Committed hook freshness — the PROJECT_DOCS/ARCHITECTURE/harness-profiler/committed-hook-freshness.md leaf, removed

The leaf is removed.

### Limits, stated — the PROJECT_DOCS/ARCHITECTURE/harness-profiler/limits-stated.md leaf, removed

The leaf is removed.

### [What `init` writes](PROJECT_DOCS/ARCHITECTURE/harness-profiler/what-init-writes.md#what-init-writes)

**As it stands:**
```
`init claude` writes the repository's rendered skill and its
`.claude/settings.json`, merging the six entries through `hooks.merge_hooks`: each command runs
`profiler capture claude` on the committed wrapper, `hooks.HOOK_COMMAND`. An entry an `init` wrote
earlier is replaced in place, so a re-run picks up new hook options.
```
**Becomes:**
```
`init claude` writes the repository's rendered skill and its
`.claude/settings.json`, merging the six entries through `hooks.merge_hooks`: each command runs
`profiler capture claude` on the committed wrapper, `hooks.HOOK_COMMAND`. An entry an `init` wrote
earlier is replaced in place, so a re-run picks up new hook options. Claude Code on the web sends
the same hook data but loads no plugin's hooks, so a cloud session records nothing until the hook
is committed to the repository, as this leaf describes.
```

### [The opencode capture](PROJECT_DOCS/ARCHITECTURE/harness-profiler/the-opencode-capture.md#the-opencode-capture)

**As it stands:**
```
A capture written before it read 2.4.1's shape carries
the child's id only in its stored result text; *The repair* below fills it.
```
**Becomes:**
```
A capture written before it read 2.4.1's shape carries
the child's id only in its stored result text, and the pages group none of those dispatches.
```

The `## Init and doctor stay claude-facing` section is removed.

### [Serving](PROJECT_DOCS/ARCHITECTURE/harness-profiler/serving.md#serving)

**As it stands:**
```
`tree`'s text reads
its time column and its session stamps in the machine's local zone, through `values._local`, which
doctor's `newest:` line reads too.
```
**Becomes:**
```
`tree`'s text reads
its time column and its session stamps in the machine's local zone, through `values._local`.
```

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/harness-profiler/index.md#harness-profiler)

**As it stands:**
```
- [Limits, stated](limits-stated.md)
- [What `init` writes](what-init-writes.md)
- [What removes the retired path](what-removes-the-retired-path.md)
- [Committed hook freshness](committed-hook-freshness.md)
- [What does not exist](what-does-not-exist.md)
- [The opencode capture](the-opencode-capture.md)
- [The repair](the-repair.md)
- [The stores and their rename](the-stores-and-their-rename.md)
- [Doctor lines](doctor-lines.md)
```
**Becomes:**
```
- [What `init` writes](what-init-writes.md)
- [What removes the retired path](what-removes-the-retired-path.md)
- [What does not exist](what-does-not-exist.md)
- [The opencode capture](the-opencode-capture.md)
- [The stores and their rename](the-stores-and-their-rename.md)
```

### [ARCHITECTURE — devpro](PROJECT_DOCS/ARCHITECTURE/entry-point.md#architecture--devpro)

**As it stands:**
```
  - [What removes the retired path](harness-profiler/what-removes-the-retired-path.md)
  - [Committed hook freshness](harness-profiler/committed-hook-freshness.md)
  - [What does not exist](harness-profiler/what-does-not-exist.md)
  - [The opencode capture](harness-profiler/the-opencode-capture.md)
  - [The repair](harness-profiler/the-repair.md)
  - [The stores and their rename](harness-profiler/the-stores-and-their-rename.md)
  - [Doctor lines](harness-profiler/doctor-lines.md)
```
**Becomes:**
```
  - [What removes the retired path](harness-profiler/what-removes-the-retired-path.md)
  - [What does not exist](harness-profiler/what-does-not-exist.md)
  - [The opencode capture](harness-profiler/the-opencode-capture.md)
  - [The stores and their rename](harness-profiler/the-stores-and-their-rename.md)
```

### [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md#repo-layout)

**As it stands:**
```
  profiler/             the absorbed activity profiler — the harness-profiler project's capture, tree, page render and committed-hook wiring as devpro code, run as the `profiler` verb's `capture`, `tree`, `init`, `doctor` and `repair`, its records served by the `dashboard` verb's profiler view (Harness profiler); importable Python, standard library only, carrying `view.html` and the decoration's `deco.js` as the package data its render and the dashboard's pages read (Packaging), its stores and the install migration devpro/install.py calls (`stores.py`), beside the committed-hook wiring in `hooks.py`; it ships no harness resource, its commands running the tree's own wrapper (Harness profiler)
```
**Becomes:**
```
  profiler/             the absorbed activity profiler — the harness-profiler project's capture, tree, page render and committed-hook wiring as devpro code, run as the `profiler` verb's `capture`, `tree` and `init`, its records served by the `dashboard` verb's profiler view (Harness profiler); importable Python, standard library only, carrying `view.html` and the decoration's `deco.js` as the package data its render and the dashboard's pages read (Packaging), its stores and the install migration devpro/install.py calls (`stores.py`), beside the committed-hook wiring in `hooks.py`; it ships no harness resource, its commands running the tree's own wrapper (Harness profiler)
```

### [Subsystem map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md#subsystem-map)

**As it stands:**
```
  command and no recipe; `references/installing.md` runs `profiler doctor` through the wrapper
  `clauses.WRAPPER` names; its install, update and
```
**Becomes:**
```
  command and no recipe; its install, update and
```

## Code delta

### [Guide and README](PROJECT_DOCS/SPEC/guide-and-readme.md#guide-and-readme)

Refactor: the repository's `README.md` drops the sentence "`devpro profiler doctor` names such a
store with the move to make." from its store-rename paragraph, and nothing replaces it — the
install's own report, which prints `renamed <old> → <new>` or that it left the old store alone, is
the signal — and the leaf's statements about what the README holds stay true.

Refactor: the README's docdicer-walk paragraph drops its trailing clause "the prune keeping a
`VENV_DIR` entry by rule." — what survives both runs survives because none of it is ours by its
own carrier, not by a keep rule: no venv is ever delivered and none is created under an install
directory. The paragraph's surviving statements stand.
