# The install replaces the plugin directory wholesale

For whoever installs devpro — a project, a user's harness setup, or this repository's own trees — an
install leaves nothing of what came before it inside the plugin's directory: the install directory is
the plugin's own, and each install, a project's and a user-level's alike, replaces its contents
whole, the tree removed and the fresh one written, so what the harness loads is exactly what this
release ships. What the install touches
outside the directory keeps its shared-file handling — the agents file's block, the runner include
lines, the hook entries `profiler init` writes into a settings file — and a run from an
installation's own copy still passes over the copy it runs from and the wrapper that runs it, its
symlinked-copy refusal intact. The up-to-date check and `--dry-run` keep their roles; the dry run is
where a replacement's removals are enumerated.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Write Safety](PROJECT_DOCS/SPEC/write-safety.md)

**As it stands:**

```
An install overwrites every rendered definition where the destination is absent or carries a
generated banner: the `!GENERATED!` line inside the frontmatter, or the comment form a supporting
file opens with, which every rendered file does under opencode. A generated banner names a source
under `devpro/` (`!GENERATED! from devpro/…`). A harness-rendered file is ours when it holds its ownership marker, and any other file at that path refuses like any foreign file. Any other file at a destination — one a project
wrote itself, or a directory — refuses the install with nothing written, naming each such path. A
rendered file or harness resource a release before 0.17.0 wrote names its source under the
generator's earlier name, so it is foreign: at a destination it refuses the install, and prune
leaves it.
```

**Becomes:**

```
The install directory is the plugin's own, entire. An install replaces it wholesale: before the
first write it removes the install directory's contents — every file and subdirectory, whatever
wrote them — and writes the fresh tree into the emptied directory: the rendered definitions, the
shipped packages, the harness resources and the harness-rendered files. A user-level install
replaces wholesale as a project install does: the destination directory it owns is wiped and the
full product it ships is written into it — under opencode the plugin entry and the guardrail
resource beside it are rewritten on every user-level run, never deleted — so the plugin a
user-level install leaves behind loads. Nothing inside the install
directory is refused, recognized or preserved: no banner is read to decide an overwrite or a
removal, no file is judged ours or foreign, no stale list is kept, and no removal is exempt — a
file the consumer left inside the plugin's directory, hand-written or a safety copy it made, goes
with the tree. The install directory itself is never removed, and an install keeps no backup of
what it replaces: the consumer's git is the record of what an install changed. Banners are written
as Installed tree states them; no install reads one back to decide what it may write.

Two pass-overs stand inside the replacement, and one refusal stands at its boundary. The
**re-entry run** — an install from an installation's own copy into the installation holding that
copy — passes over the devpro copy under `tools/devpro/` and the wrapper `tools/devpro.sh` that
runs it: the replacement leaves the copy's own files and the wrapper standing and removes anything
else inside the copy's tree, a stale bytecode file included, and neither pass-over is reported
(Shipped files). The
**agents file**, where it sits inside the install directory — under mage, whose install directory
is the harness directory itself — is passed over too: the agents file keeps its marked-block
handling (Agents File), and the replacement never deletes the file that handling edits. An install
whose devpro-copy destination is a symlink is refused before anything is written, as is one whose
install directory itself is a symlink, each refusal naming the link: the replacement would clear
and write through the link into whatever it names.
```

**As it stands:**

```
The install removes — naming each in its install report — every file under a deployed surface of
its install directory, and of no other directory, that it did not write and that carries a generated
banner, and with them any
directory that leaves empty; this removal takes no file that lacks a generated banner. A safety
copy — a file carrying the `.bak` suffix — never enters that stale list. The install
directory itself is never removed, and a directory that was already empty stays. A package
destination is replaced whole, `skills/kbase/kb-tools/` included. The development scripts and devpro
tools packages are replaced the same way. The
install removes `skills/docdicer/dicing-snippets/`, the dicing snippets package's retired home, with
everything under it, where an earlier install left it.
A harness resource is replaced whole on each
install when the file already at its path carries `!INSTALLED! … devpro` in its first ten lines;
any other file there refuses the install the same way. It is not removed by prune: a harness
resource this repository stops shipping stays until the consuming project removes it. A
harness-rendered file takes the first two rules: replaced whole on each install where it holds its
ownership marker, and not removed, since prune walks the three deployed surfaces only. The install
report names each path it pruned. A changing install's report ends with one line counting the
rendered files and the copied files; harness resources are counted as copied. An install keeps no
backup of a file it overwrites or removes. The agents file's one rolling backup (Agents File) is
the only one.
```

**Becomes:**

```
Everything the install touches outside the install directory keeps its handling: the agents file's
block (Agents File), whose one rolling backup stays the only backup an install's writes keep; the
runner include lines and the runner file (Plugins); the scratch directory and its `.gitignore`
line; and the hook entries `profiler init` writes into a settings file — that verb's work, not the
install's. A changing
install's report ends with one line counting the rendered files and the copied files; harness
resources are counted as copied. The changing install does not enumerate its removals: the dry run
is the enumeration surface.
```

**As it stands:**

```
A guardrail skipped for a
failed install-time probe leaves any script an earlier install wrote where it stands and rewrites
the registration without its entry; the report names the earlier install's script, left where it
stands.
```

**Becomes:**

```
A guardrail script joins the copies only where one install-time run of the script succeeds
(Shipped files); where the probe fails, the registration is written without the entry, and no
guardrail script stands in the install directory after the run — the replacement removed the one an
earlier install wrote. The report names the skip and its reason, and no path: the banner read the
old report's name relied on is gone.
```

**As it stands:**

```
An up-to-date run reports `up to date: <harness-dir> — nothing written`, exits 0 and touches
nothing: no file
written, no mode or modification time changed, no package destination replaced. "Nothing" is judged
on the result: every file the install would
write is already byte-identical and mode-identical, and none would be created or removed. Changing
`--harness`, `--family`, the category map or `--components` changes bytes, so that install proceeds.
```

**Becomes:**

```
An up-to-date run reports `up to date: <harness-dir> — nothing written`, exits 0 and touches
nothing: no file written, no mode or modification time changed, no package destination replaced.
"Nothing" is judged on the result: what the install would write is byte-identical and
mode-identical to what stands, file for file, and nothing stands that the install would not write.
Changing `--harness`, `--family`, the category map or `--components` changes bytes, so that
install proceeds.
```

**As it stands:**

```
`--dry-run` runs the same judgment and writes nothing, in the target or elsewhere that outlives the
run. It prints what the install would change, grouped as created, changed and removed, each path
relative to the project root, or absolute for a file outside it, such as the global agents file, and
exits 0; where nothing would change it says the harness directory is up to date. A directory the
install would remove is listed with a trailing `/`. Every path it prints and every refusal it reports
names the path. What the install would leave alone or skip, with the reason, is reported on stderr
on an up-to-date run and a dry run as on a changing one. It reports the refusals it can foresee.
```

**Becomes:**

```
`--dry-run` runs the same judgment and writes nothing, in the target or elsewhere that outlives the
run. It prints what the install would change, grouped as created, changed and removed, each path
relative to the project root, or absolute for a file outside it, such as the global agents file, and
exits 0; where nothing would change it says the harness directory is up to date. The removed group
is where the replacement's removals are enumerated: a file standing in the install directory that
the install would not write is listed there, whatever wrote it. Every path it prints and every
refusal it reports names the path. What the install would leave alone or skip, with the reason, is
reported on stderr on an up-to-date run and a dry run as on a changing one. It reports the refusals
it can foresee.
```

### [Installed tree](PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md)

**As it stands:**

```
An installed tree is not for local edit: a re-install overwrites the files that carry this
repository's banner and removes what this repository no longer produces, and over any other file at
a rendered-definition or harness-resource destination it refuses and writes nothing (SPEC.md,
Write Safety). A package destination belongs to this repository entire, and no file there is for local
edit.
```

**Becomes:**

```
An installed tree is not for local edit: each install replaces the install directory wholesale —
the fresh tree overwrites everything that stands in it, whatever wrote it (SPEC.md, Write Safety) —
so no file in the install directory, a package destination included, is for local edit, and the
consumer's git is the record of what an install changed.
```

### [Install destination](PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md)

**As it stands:**

```
the registry `registry.json`), prunes as any install does, and writes nothing else but the devpro
tools package (Shipped files) and, under opencode, the plugin entry, a harness resource without
which the plugin cannot register: no other harness resource, no install-time probe or guardrail
registration (Shipped files), no other shipped package (neither `kb-tools/` nor the development
scripts package), no runner include line and no runner file.
```

**Becomes:**

```
the registry `registry.json`), replaces the install directory wholesale as any install does
(SPEC.md, Write Safety), and writes nothing else but the devpro tools package (Shipped files) and,
under opencode, the plugin entry and the guardrail resource beside it, both rewritten on every
user-level run, never deleted — so the entry runs the guardrail at user level as it does in a
project. No install-time probe or guardrail registration (Shipped files), no other shipped package
(neither `kb-tools/` nor the development scripts package), no runner include line and no runner
file; and the capture `profiler.ts` is not copied, the activity capture staying a project install's.
```

### [Generated files](PROJECT_DOCS/SPEC/generated-files.md)

**As it stands:**

```
- Its content is exactly what the generator renders for it from its source, deterministically; a
  rendered file whose source no longer exists is pruned on the next install.
```

**Becomes:**

```
- Its content is exactly what the generator renders for it from its source, deterministically; a
  rendered definition whose source no longer exists is absent from the next install's tree.
```

**As it stands:**

```
A file without a generated banner is not a rendered definition this repository produced, and is
outside this guarantee — Write Safety, below, is what governs meeting one at a destination.
```

**Becomes:**

```
A file without a generated banner is not a rendered definition this repository produced, and is
outside this guarantee; inside the install directory the wholesale replacement removes it (Write
Safety), and no install writes a rendered definition anywhere else.
```

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**

```
reporting nothing about the pass-over, and installs everything else, each write under the overwrite
rules Write safety states.
```

**Becomes:**

```
reporting nothing about the pass-over, and installs everything else under the wholesale replacement
Write safety states.
```

**As it stands:**

```
The wrapper records the interpreter the install ran under; a re-entry run replaces the copy, not
the interpreter — the installed version stays the one the operator chose.
```

**Becomes:**

```
Neither passed-over path is written or read back: the interpreter the wrapper records is the one
the installation's own wrapper already carries, untouched by a re-entry run, and the installed
version stays the one the operator chose.
```

**As it stands:**

```
An install copies the harness
resources into the install directory, except a user-level install, which copies only opencode's
entry, and save a file conditional on the install-time probe (below), so a resource lands
```

**Becomes:**

```
An install copies the harness
resources into the install directory — a user-level install's copies being opencode's entry and the
guardrail resource beside it — and save a file conditional on the install-time probe (below), so a
resource lands
```

**As it stands:**

```
A user-level install copies no `guardrail.ts`, and the plugin entry then runs none.
```

**Becomes:**

```
A user-level install copies the guardrail resource beside the entry, and the entry runs it there as
it does in a project.
```

### [Plugins](PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md)

**As it stands:**

```
A project with neither runner file gets a `Makefile`
created to hold every line the install writes. The line an install wrote for the docdicer tools
package — retired with the absorbed dicing verbs, and none of its snippet paths point at anything
any more — the install removes itself: a non-comment line
whose snippets path ends `runner-snippets/docdicer.just` or `runner-snippets/docdicer.mk` and whose
first path segment is the harness directory this install writes is removed, the removal named in the
install report; a docdicer line naming another harness directory's snippets is reported and left.
```

**Becomes:**

```
A project with neither runner file gets a `Makefile`
created to hold every line the install writes. A line naming a set no install ships any more — the
retired docdicer set's — is no set's line to judge: it is left as written, inert where the snippets
it names are gone.
```

The retired-docdicer sentence is replaced by its successor statement: no retirement inventory
survives the wipe — the `RETIRED_*` inventory named whole in the ruling — and a docdicer include
line names snippet paths that no longer exist, an inert line in the project's runner file, the
operator's to delete.

## ARCHITECTURE delta

### [Renders and copies](PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md)

**As it stands:**

```
An install renders every definition its plugin ships — for a skill, its skill entry file and then
each supporting file it lists — and every harness-rendered file whose owner ships (the plugin
manifest and `.mcp.json` under claude and mage, `registry.json` under opencode), replaces
the destination of each `SHIPPED_PACKAGES` row whose owner ships whole with a copy — copies each
harness resource the installing harness ships into the install directory as it stands — bar a
guardrail script whose probe fails (below) — writes the rendered definitions over what is there,
and removes each file under the install directory's `agents/`, `commands/` or `skills/` that this
run did not write, that is ours by its own carrier: frontmatter holding a
`!GENERATED!` line, or a comment line opening with it, which is how a skill's supporting file holds
its banner — save where prune's own guard, below, keeps a file. `prune` walks the three surfaces (`_files_below`) of the install directory and nothing
else, and the upward walk visits only a stale file's ancestors and stops at the install directory.
The walk is one install directory's: under claude the install directory
(`.claude/skills/devpro/`) sits inside the harness directory's `skills/` beside what the project
keeps there, so a walk wider than the install directory would delete a neighbor's. That walk needs no carve-out for a package destination: the development scripts package and the
kb-tools package sit inside the install directory's `skills/` — `skills/development/scripts/` and
`skills/kbase/kb-tools/`, each in its skill's own directory — where every file they hold is stamped
installed or left unstamped, never generated, and the devpro tools package sits at `tools/`,
outside the three surfaces the walk visits, so every file under those trees is still either ours or
untouched. The staleness rule is prune's own, stated here rather than inherited: a safety copy (a
`.bak` suffix) never enters the stale list. No venv is ever delivered and none is created under an
install directory, so the stale list has no venv case: no file a venv holds is ours by its own
carrier. A definition of ours that this run did not write, such as one its plugin
does not ship, is stale and goes — every one of its files, a skill's included. Every definition is
rendered before the first write. A file at a rendered-definition destination that has lost the
generated banner, or is a directory, refuses the install.
```

**Becomes:**

```
An install renders every definition its plugin ships — for a skill, its skill entry file and then
each supporting file it lists — and every harness-rendered file whose owner ships (the plugin
manifest and `.mcp.json` under claude and mage, `registry.json` under opencode), replaces
the destination of each `SHIPPED_PACKAGES` row whose owner ships whole with a copy — copies each
harness resource the installing harness ships into the install directory as it stands — bar a
guardrail script whose probe fails (below) — and writes the rendered definitions. The fresh tree is
made in one step: after every check and before the first write, the install removes the install
directory's contents — every file and subdirectory below it, whatever wrote them — save the two
pass-overs it takes by path, never by content: on a re-entry run, the devpro copy's own files under
`tools/devpro/` — the set its `SHIPPED_PACKAGES` row stages — and the wrapper `tools/devpro.sh`
stand while everything else inside the copy's tree, stale bytecode included, goes; and the agents
file's path stands where it sits inside the install directory (mage). Then the copies, the
resources and the renders fill the emptied directory. Nothing inside the install directory is read
to decide its fate: no generated banner, no installed header, no ownership marker gates a write or
a removal, no stale list is kept, no removal is exempt and no file is judged ours or foreign — the
install directory is the plugin's own, and what a consumer left inside it goes with the tree. A
user-level install's product is the plugin's definitions, the harness-rendered files, the devpro
tools package and, under opencode, the entry and the guardrail resource beside it, each rewritten
by the run that ships it. The install directory is refused where it is a symlink, beside the devpro
copy's own symlink refusal — both decided on the real paths, before anything is written — for the
same hazard: the replacement would clear and write through the link into whatever it names. Every
definition is rendered before the first write.
```

**As it stands:**

```
Every copy writes each file with the mode the
process umask gives a new file plus the source's execute bits, and `prune`
keeps its own guard above.
```

**Becomes:**

```
Every copy writes each file with the mode the process umask gives a new file plus the source's
execute bits.
```

**As it stands:**

```
Its one file, `cold-read.sh`, is stamped by suffix and keeps its execute bits under the umask's mode,
and the
package is replaced whole and never pruned.
```

**Becomes:**

```
Its one file, `cold-read.sh`, is stamped by suffix and keeps its execute bits under the umask's
mode, and the package is replaced whole.
```

**As it stands:**

```
**Re-entry.** An install whose devpro-copy destination resolves to the package it runs from
(`is_the_running_copy`) is a re-entry run — an install from an installation's own copy into the
installation holding it (`:539-544`) — and it passes over that copy and the wrapper that runs it. The
copy's `SHIPPED_PACKAGES` row is dropped before the copies are built (`:640-644`), so its destination
is never cleared and its files are never rewritten; the wrapper's write is skipped (`:719-723`); and
the sentence naming the copy's destination in the report is skipped with it, so neither passed-over
path is written or reported (`:747-753`). Everything else the install does, it does as any install
does. A symlinked copy destination refuses the install before either read (`_refuse_symlinked_copy`,
`:547-558`): the pass-over reads that destination resolved and the copy writes it as it resolves, so a
link there would let the two passed-over paths be cleared and rewritten through it.
```

**Becomes:**

```
**Re-entry.** An install whose devpro-copy destination resolves to the package it runs from
(`is_the_running_copy`) is a re-entry run — an install from an installation's own copy into the
installation holding it — and it passes over that copy and the wrapper that runs it: the wholesale
replacement removes everything below the install directory except the copy's own files — the set
its `SHIPPED_PACKAGES` row stages — and the wrapper, everything else inside the copy's tree going
with the tree; the copy's
`SHIPPED_PACKAGES` row is dropped before the copies are built, the wrapper's write is skipped, and
the sentence naming the copy's destination in the report is skipped with it, so neither passed-over
path is written or reported and the copy the run executes from stays whole. Everything else the
install does, it does as any install does. A symlinked copy destination refuses the install before
either read (`_refuse_symlinked_copy`): the pass-over reads that destination resolved and the copy
writes it as it resolves, so a link there would let the two passed-over paths be cleared and
rewritten through it.
```

**As it stands:**

```
A
user-level install copies one resource only, the harness's entry (`Harness.entry_resource`,
opencode's `index.ts`): the plugin cannot register without it, and the entry imports the guardrail
only where `guardrail.ts` stands beside it.
```

**Becomes:**

```
A
user-level install's resource copies are the harness's entry (`Harness.entry_resource`,
opencode's `index.ts`) and the guardrail resource beside it: the plugin cannot register without the
entry, and the entry imports the guardrail only where `guardrail.ts` stands beside it — the
guardrail running at user level through the entry, as it does in a project.
```

**As it stands:**

```
Before the
first write, `_RESOURCE_BANNER` (`!INSTALLED! .* devpro`) is matched against the first ten lines
of an existing destination. Package destinations are exempt from the banner and marker checks.
`_clear_package_destination` empties the directory a destination is, and unlinks any other file
there. No error is swallowed: an `OSError` from the clear propagates. The harness resources join the same `copies` list as the packages', so the prune's
`keep` holds them and the install report counts them: a harness resource never reads as a stale
rendered definition. The copy is one-way, not a mirror — `prune` owns the install directory's
`agents/`, `commands/` and `skills/` and nothing outside them — with one exception: a file
`RETIRED_RESOURCE_FILES` names is removed where it carries this
repository's header, on every install, and a directory `RETIRED_RESOURCE_DIRS` names is removed once
that leaves it empty, a directory holding anything else being the consumer's. One directory goes
whole rather than only when it empties: `RETIRED_PACKAGE_DIR`
(`skills/docdicer/dicing-snippets`, `install.py:154`), the dicing snippets package's home before it
joined the devpro tools package, which `install` removes with everything under it where an earlier
install left it (`:724`) and names in its report (`:754`) — `prune` leaves its files standing, since
its files carry the installed banner. A harness-rendered file is checked a
third way, by its `HarnessFile.marker`.
```

**Becomes:**

```
The harness resources join the same `copies` list as the packages', and the install report counts
them. The copy is not a mirror and keeps no retirement inventory: the wholesale replacement removes
whatever stands and the fresh tree holds only what this release ships — no retired resource name,
no retired package directory, no banner or marker check on any destination, no per-destination
clearing. The changing install's report does not enumerate removals; the dry run is the
enumeration surface.
```

**As it stands:**

```
`_install_managed_paths` is a hand-kept list of
where it may write, and the dry-run prediction tests
```

**Becomes:**

```
`_install_managed_paths` is a hand-kept list of
where it may write and remove, and the dry-run prediction tests
```

**As it stands:**

```
Under the install directory: the three deployed surfaces, which the
    prune walks, the destination of every `SHIPPED_PACKAGES` row whichever definitions the plugin
    ships, the harness's resource destinations (at user level, the entry alone), every
    harness-rendered file — the manifest, `.mcp.json`, `registry.json` — the retired resource names
    (`RETIRED_RESOURCE_FILES`' and `RETIRED_RESOURCE_DIRS`', unlinked and removed on every install),
    `RETIRED_PACKAGE_DIR` (read and removed, so the preflight predicts the removal), and
    the guardrail registration.
```

**Becomes:**

```
Under the install directory: the install directory managed whole — the managed set is every entry
    below it, the re-entry pass-over trees and, under mage, the agents file's path included, each
    staged as it stands, a link staged as the link it is and never followed — so the scratch run's
    replacement meets what the real tree holds, passes over what it passes over, and the comparison
    reads the removals it makes against that whole staging.
```

### [Install](PROJECT_DOCS/ARCHITECTURE/install/index.md)

**As it stands:**

```
- It removes each file under the install directory's `agents/`, `commands/` and `skills/` that
  is ours and was not written by this run (Renders and copies). Removing, renaming and
  relocating installed files is standard maintenance: an install removes the files of ours it no
  longer writes, so none accumulate.
```

**Becomes:**

```
- It replaces the install directory wholesale: the tree is removed and the fresh one written,
  whatever stood in it (Renders and copies). Removing, renaming and relocating installed files is
  standard maintenance that needs no inventory: the replacement leaves nothing stale behind to
  accumulate.
```

### [Install entry](PROJECT_DOCS/ARCHITECTURE/install/install-entry.md)

**As it stands:**

```
and then renders
and prunes and skips the packages, guardrail and the runner include lines, and the harness resources
but the entry that registers the plugin (Install, Renders and copies).
```

**Becomes:**

```
and then renders
and skips the packages, guardrail and the runner include lines, and the harness resources but the
entry that registers the plugin and the guardrail resource beside it (Install, Renders and copies).
```

**As it stands:**

```
Prune is in terms of
the install directory, and the agents file in terms of the harness directory, which holds the
install directory.
```

**Becomes:**

```
The wholesale replacement is in terms of
the install directory, and the agents file in terms of the harness directory, which holds the
install directory.
```

**As it stands:**

```
Refused too, with nothing written: a rendered-definition
or harness-resource destination holding a file without the generated banner, and a harness-rendered
file without its marker.
```

**Becomes:**

```
Refused too, with nothing written: an install directory that is a symlink — the wholesale
replacement would clear and write through it into whatever it names. The refusal is not one of
these: it is decided inside `install`, beside the devpro-copy symlink refusal and after `root` is
computed, still before the first write (Renders and copies).
```

### [Guardrail registration](PROJECT_DOCS/ARCHITECTURE/install/guardrail-registration.md)

**As it stands:**

```
- **Probe.** Before `_refuse_foreign_targets`, the install runs the source script once, with
  `GUARDRAIL_INTERPRETER` and no `CLAUDE_PROJECT_DIR`, on one allowed Bash call, and requires exit
  0 within `GUARDRAIL_PROBE_SECONDS`. A missing interpreter, a missing module, a broken script and
  a hang all fail it. A failed probe drops the script and writes the registration without the
  guardrail's entry.
  Its report line carries the exit status and first stderr line, the timeout, or the `OSError`, and
  names an earlier install's script, left where it stands, by its installed banner. The probe is
  one allowed call, not the case table, which runs in the test suite only.
```

**Becomes:**

```
- **Probe.** Before the first write, the install runs the source script once, with
  `GUARDRAIL_INTERPRETER` and no `CLAUDE_PROJECT_DIR`, on one allowed Bash call, and requires exit
  0 within `GUARDRAIL_PROBE_SECONDS`. A missing interpreter, a missing module, a broken script and
  a hang all fail it. A failed probe drops the script and writes the registration without the
  guardrail's entry.
  Its report line carries the exit status and first stderr line, the timeout, or the `OSError` —
  the skip and its reason, and no path: the banner read the old report's name relied on is gone.
  Whatever the probe's outcome, a guardrail script stands in the install directory after the run
  only where the probe passed: the replacement removed any earlier install's. The probe is one
  allowed call, not the case table, which runs in the test suite only.
```

**As it stands:**

```
A user-level install runs no probe: `install` takes no guardrail for it.
```

**Becomes:**

```
A user-level install runs no probe: `install` takes no `GuardrailHook` for it, the registration
staying a project install's; opencode's entry runs the guardrail resource beside it at user level as
in a project.
```

### [Plugins](PROJECT_DOCS/ARCHITECTURE/install/plugins.md)

**As it stands:**

```
`install` takes the rows whose owner the selection's `ships(name)` admits and every row with no
owner, and on a user-level install the rows with no owner alone. Those rows are
what `package_copies` copies and `_clear_package_destination` empties before the copy, so the
destination is emptied in place while the skill's `SKILL.md` and supporting files beside it are not
touched.
```

**Becomes:**

```
`install` takes the rows whose owner the selection's `ships(name)` admits and every row with no
owner, and on a user-level install the rows with no owner alone. Those rows are
what `package_copies` copies into the fresh tree the wholesale replacement writes (Renders and
copies); nothing inside the install directory is cleared apart from that replacement.
```

**As it stands:**

```
Where the project has no runner file, one `Makefile` is created holding every line.

The retired docdicer set's line is still this install's to clean up, the cleanup staying as stage 1
landed it: the dicing verbs are devpro's own (Dicing and Checks), and the install removes the
docdicer line as SPEC.md, Plugins, states it — recognized by the same shape rule that recognizes
its own lines (`_snippet_pattern`), removed, and the removal named in the install report; a
docdicer line naming another harness directory's snippets is reported and left. The cleanup stands
beside the devpro line's return: the retired set's snippets are `docdicer.just` and `docdicer.mk`,
paths that point at nothing any more, and the devpro set ships `devpro.just` and `devpro.mk`, so
the cleanup never touches a line of the new set.

`runner_file` reads the runner file through
```

**Becomes:**

```
Where the project has no runner file, one `Makefile` is created holding every line.

`runner_file` reads the runner file through
```

The retired-docdicer paragraph is removed with the retirement it describes: `runner_file.py` keeps
the own-set line handling alone, and the `retired_set` argument `install_include_lines` takes goes
with it.

### [Guardrail hook](PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md)

**As it stands:**

```
`guardrail.ts` keeps its `Plugin.define` export so the bun runner
loads it alone, and the entry imports it only where the file stands beside it, which a user-level
install does not copy.
```

**Becomes:**

```
`guardrail.ts` keeps its `Plugin.define` export so the bun runner
loads it alone, and the entry imports it only where the file stands beside it — where a user-level
install copies it beside the entry, the guardrail runs at user level as it does in a project.
```

### [Banner](PROJECT_DOCS/ARCHITECTURE/banner.md)

**As it stands:**

```
A supporting file carries the pair as `<!-- !GENERATED! … -->` and
`<!-- !TUNING! … -->` followed by a blank line, and the `!GENERATED!` line alone marks it as ours for
removal (`_is_ours`).
```

**Becomes:**

```
A supporting file carries the pair as `<!-- !GENERATED! … -->` and
`<!-- !TUNING! … -->` followed by a blank line. The banners are written, never read back: what
stands in the install directory is decided by the wholesale replacement (Renders and copies), not
by any file's carrier.
```

### [What removes the retired path](PROJECT_DOCS/ARCHITECTURE/harness-profiler/what-removes-the-retired-path.md)

**As it stands:**

```
`install`'s copy step
removes, on every install, the retired launcher files standing in the install directory —
`RETIRED_RESOURCE_FILES`: `profiler/profiler.sh` and `profiler/hp.sh` — where each carries this
repository's installed header, then removes `profiler/` where that leaves it empty
(`RETIRED_RESOURCE_DIRS`). `install` deletes only a file carrying the header it stamps; `init`
deletes by name, under `.claude/` in the repository it targets. The preflight predicts both from the
same lists.
```

**Becomes:**

```
`install`'s wholesale replacement removes whatever stands in the install directory, the retired
launcher files included; `init` deletes by name, under `.claude/` in the repository it targets. The
preflight predicts both.
```

The leaf's closing sentence — a hook command spelling a retired launcher stays this tool's,
`hooks.is_our_command` recognizing it — stands: `hooks.py` is untouched by this design.

### [Packaging](PROJECT_DOCS/ARCHITECTURE/packaging.md)

**As it stands:**

```
| the two refused writes — a foreign file at a rendered-definition destination, and the no-write paths (`.claude/settings*`, `opencode.json`, `opencode.jsonc`) | refuses the install, naming each path | the same refusal; git is not run |
```

**Becomes:**

```
| the refused write — the no-write paths (`.claude/settings*`, `opencode.json`, `opencode.jsonc`) | refuses the install, naming each path | the same refusal; git is not run |
```

### [Subsystem map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

**As it stands:**

```
- **Install machinery** — the one entry not rendered from a definition: `install.py` renders, copies
  and prunes; `install_base.py` holds what the install modules share
```

**Becomes:**

```
- **Install machinery** — the one entry not rendered from a definition: `install.py` renders, copies
  and replaces the install directory wholesale; `install_base.py` holds what the install modules share
```

## Code delta

### [Install machinery](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md)

The install modules' new shape, the documents above carrying the behavior:

`devpro/install.py` keeps, unchanged in behavior: `is_the_running_copy` and
`_refuse_symlinked_copy` — the re-entry pass-over and its symlink refusal, preserved exactly; the
guardrail probe and the registration's two forms; the agents-file calls
(`checked_agents_file`, `checked_followed_agents_file`, `write_agents_file`,
`write_followed_agents_file` — `devpro/agents_file.py` untouched); the runner include lines'
own-set writing and `check_runner` (`devpro/runner_file.py` keeps everything but the retired set);
the scratch-directory preparation and its `.gitignore` line; the stores' rename; the shadow report
(`_report_shadowing`, which keeps `_is_our_harness_file` — its one remaining reader, a read of the
user harness directory outside the replacement) and the reload rule; the staging machinery
(`package_copies`, `harness_resource_copies`, `stamped`, `STAMPED_SUFFIXES`, `_package_copy_mode`,
`_write_created`); and the version read for the report, taken before the replacement.

It drops: `_refuse_foreign_targets` and the banner-reading helpers it feeds on (`_is_ours`,
`_bannered`, `_is_our_resource`, `_GENERATED`, `_COMMENT_GENERATED`, `_PAYLOAD_PATH`,
`_RESOURCE_BANNER`, `_RESOURCE_BANNER_LINES`, the `GENERATED_MARK` import); `prune`, `_files_below`,
`_is_stale_candidate`, `EXCLUDED_SUFFIX` and the `SURFACES` walk; `_clear_package_destination`;
`RETIRED_PACKAGE_DIR`, `RETIRED_RESOURCE_FILES`, `RETIRED_RESOURCE_DIRS`,
`_retired_resource_targets`, `_retired_resource_dirs`; `RETIRED_SNIPPET_SET` and the `retired_set`
argument `install_include_lines` takes; and the per-item removal report lines (`removed …`,
`pruned …`).

It adds: the replacement step — after every check and before the first write, remove the install
directory's contents, save the pass-overs the replacement takes by path: on a re-entry run, the
copy's own files under `tools/devpro/` — the set its `SHIPPED_PACKAGES` row stages, enumerated even
where the row is dropped from the copies — and the wrapper, everything else inside the copy's tree
removed; and the agents file's path where it falls inside the install directory — and the
symlinked-install-directory refusal, decided beside the devpro-copy refusal on the real paths.
`_resource_copies`' user-level set becomes the harness's entry and the guardrail resource beside it
(opencode's alone today), and the entry's own comment saying a user-level install ships no guardrail
is corrected with it. Comments citing the prune step
or a retirement list (`devpro/install_target.py`'s overwrite-or-prune sentence,
`devpro/definitions/__init__.py`'s prune-step sentence) reword to the replacement.
`devpro/preflight.py` and `_install_managed_paths` take the managed set the Preflight passage
states: one base, the install directory, whose managed paths are every entry below it — the
pass-over trees included, staged as they stand, a link staged as the link it is and never followed —
the pass-over itself living in the replacement's exclusions, not in the managed set; the two symlink
refusals read the real paths, so the scratch run raises them as the real run would.

One CONVENTIONS leaf is invalidated with no delta of this design's to carry it: the first paragraph
of `CONVENTIONS/code-definitions-and-install/recognizer-spells-rendered-banner.md` describes the
recognizer this design deletes, and its digest paragraph survives. The plan retires that paragraph in
the change that lands the wipe.

### [Repo layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

The test surfaces whose expectations move, named by their files in `tests/install/`; the tests' text
is the coders':

- `tests/install/test_prune.py` is removed whole: its tests pin the stale list, the banner
  recognition and the `.bak` carve-out, all dissolved by the wipe.
- `tests/install/test_dry_run.py`: the refusal battery
  (`test_a_hand_written_file_at_a_render_target_is_refused_with_nothing_written`,
  `test_a_wrapper_no_install_wrote_is_refused_with_nothing_written`,
  `test_a_directory_at_a_render_target_is_refused_with_nothing_written`,
  `test_every_failing_target_is_named_in_one_refusal`,
  `test_a_resource_target_passes_only_with_the_header_in_its_first_ten_lines`) and the retirement
  tests (`test_an_install_removes_the_dicing_snippets_package_an_earlier_install_left`,
  `test_an_install_removes_the_retired_launcher_and_its_directory`,
  `test_an_install_leaves_a_retired_name_it_did_not_write`,
  `test_the_stale_list_keeps_a_safety_copy`,
  `test_reinstall_prunes_only_our_stale_definitions`) lose their subjects and go;
  `test_a_failed_probe_leaves_the_earlier_script_in_place_and_names_it` and
  `test_a_failed_probe_names_no_script_an_install_did_not_write` reword to the probe-failure
  removal; `test_every_shipped_resource_carries_the_header_its_reinstall_needs` rewords to the
  banner-as-shipped fact. The re-entry, symlink, version-report, up-to-date and dry-run
  removed-list tests stand. New tests state the wipe: a foreign file inside the install directory
  is removed and named in the dry run's removed group, a fresh install is byte-identical
  thereafter, the mage agents file inside the install directory survives the replacement with its
  block current, and the symlinked install directory is refused.
- `tests/install/test_kbase.py`: `test_an_operators_manifest_without_the_marker_is_refused_with_nothing_written`
  loses its subject — the marker no longer gates anything — and goes; the mage manifest's
  second-install byte-identity test stands.
- `tests/install/test_staging.py`:
  `test_a_second_install_leaves_the_copied_plugin_standing_and_prunes_only_the_stale_render`
  rewords to the wholesale replacement — the second install's tree byte-identical, the stale render
  gone without a prune list;
  `test_an_install_changes_nothing_outside_its_own_install_directory` stands, the wipe's boundary
  pin.
- `tests/install/test_runner_file.py`: the four retired-docdicer tests
  (`test_a_retired_docdicer_line_is_removed_and_reported`,
  `test_a_runner_file_holding_no_retired_line_is_reported_as_found_not_as_left`,
  `test_a_devpro_set_line_survives_the_retired_docdicer_lines_cleanup`,
  `test_the_retired_cleanup_leaves_a_devpro_set_line_alone_in_a_makefile`) lose their subject and
  go; the own-set line tests stand.
- `tests/install/test_scratch.py`:
  `test_a_user_level_opencode_install_copies_the_entry_and_no_guardrail` pins the user-level
  resource set the wholesale settlement reverses — it goes, and the two-successive-user-level-opencode-installs
  probe takes its place: the second install leaves `index.ts` and `guardrail.ts` as this release
  ships them and the plugin's setup reaches the watcher. Its other tests stand, the package-copy
  and staging pins among them.
- `tests/install/test_selection.py`, `test_agents_file.py`, `test_global_agents.py`,
  `test_redirects.py`, `test_checkout.py`, and `tests/test_install_target.py` stand unchanged in
  subject — the preflight predictions and the nothing-outside-the-install-directory pin among them,
  the wipe's boundary tests — and `tests/install/conftest.py`'s collected tests stand as its
  fixtures do; its fixtures that stage foreign files, banners and `.bak` files as refusal
  prerequisites reword to removal expectations.

### Drafts

#### The THESIS Pieces table's Install row names the wholesale replacement

A THESIS.md change is not one of a design's deltas, so the plan carries it, applying this pair to the
Pieces table's Install row in `PROJECT_DOCS/entry-point.md`:

**As it stands:**

```
| Install | A deploy step: each harness has its own layout, and the rendered files are copied to the places and names that layout gives | A package manager |
```

**Becomes:**

```
| Install | A deploy step: each harness has its own layout, and the install replaces the plugin directory whole — the rendered files written fresh to the places and names that layout gives | A package manager |
```

The "is not" column stands: the wipe is the replace half of a deploy, not dependency management.

#### The opencode entry's watcher under the wipe is a behavioral fact the plan records as unsettled

The entry's watcher refreshes on any filesystem event under the install directory
(`devpro/harnesses/resources/opencode/index.ts:251`), and the wipe is thousands of delete and create
events in one run: installed agent definitions vanish for the run's duration. Whether that reads as
one reload, several, or a window a session can register into is a behavioral fact nothing in the
written record answers. The plan records it as unsettled, and the strip's drive observes what a wipe
does to a live opencode session before any remediation is designed.

