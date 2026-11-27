# Write Safety

The install directory is the plugin's own, entire. An install replaces it wholesale: before the
first write it removes the install directory's contents — every file and subdirectory, whatever
wrote them — and writes the fresh tree into the emptied directory: what the install ships — the
rendered definitions, the shipped packages and the harness-rendered files the component selection
admits, and the harness resources the installing harness ships, the guardrail script's only where
its install-time probe succeeds (Shipped files). A user-level install
replaces wholesale as a project install does: the destination directory it owns is wiped and what it
ships is written into it (Install destination states that set) — so the plugin a user-level install
leaves behind loads, and a file the consumer kept in it goes like any other. Nothing inside the
install directory is refused, recognized or preserved: no banner is read to decide an overwrite or a
removal, no file is judged ours or foreign, no stale list is kept, and no removal is exempt — a
file the consumer left inside the plugin's directory, hand-written or a safety copy it made, goes
with the tree. The install directory itself is never removed, and an install keeps no backup of
what it replaces: `--dry-run` lists what it would remove, and nothing else is kept of it. Banners are
written as Installed tree states them; no install reads one back to decide what it may write.

Two pass-overs stand inside the replacement, and one refusal stands at its boundary. The
**re-entry run** — an install from an installation's own copy into the installation holding that
copy — passes over the devpro copy under `tools/devpro/` and the wrapper `tools/devpro.sh` that
runs it: the replacement leaves the copy's own files and the wrapper standing and removes anything
else inside the copy's tree, a stale bytecode file included, and neither pass-over is reported
(Shipped files). The
**agents file**, where it sits inside the install directory — under mage, whose install directory
is the harness directory itself — is passed over too: the agents file keeps its marked-block
handling (Agents File), and the replacement never deletes the file that handling edits. A symlink
inside the install directory is unlinked as the link it is and never followed: the link goes, and
whatever it named, inside the directory or outside, survives. An install whose devpro-copy
destination is a symlink is refused before anything is written, as is one whose install directory
itself is a symlink, each refusal naming the link.

Everything the install touches outside the install directory keeps its handling: the agents file's
block (Agents File), whose one rolling backup stays the only backup an install's writes keep; the
profiler stores, an install renaming an old one in place and leaving the old store alone where the
new name already stands, never merging or deleting either (ARCHITECTURE.md, Harness profiler, The
stores and their rename); the runner include lines and the runner file (Plugins); the scratch
directory and its `.gitignore` line; and the hook entries `profiler init` writes into a settings
file — that verb's work, not the install's. A changing install's report ends with one line counting
the rendered files and the copied files; harness
resources are counted as copied. The changing install does not enumerate its removals: the dry run
is the enumeration surface.

No install writes `.claude/settings*`, `opencode.json` or `opencode.jsonc`. A guardrail script joins the copies only where one install-time run of the script succeeds
(Shipped files); where the probe fails, the registration is written without the entry, and no
guardrail script stands in the install directory after the run — the replacement removed the one an
earlier install wrote. The report names the skip and its reason, and no path: the banner read the
old report's name relied on is gone.

An up-to-date run reports `up to date: <harness-dir> — nothing written`, exits 0 and touches
nothing: no file written, no mode or modification time changed, no package destination replaced.
"Nothing" is judged on the result: what the install would write is byte-identical and
mode-identical to what stands, file for file, and nothing stands that the install would not write.
Changing `--harness`, `--family`, the category map or `--components` changes bytes, so that
install proceeds.

`--dry-run` runs the same judgment and writes nothing, in the target or elsewhere that outlives the
run. It prints what the install would change, grouped as created, changed and removed, each path
relative to the project root, or absolute for a file outside it, such as the global agents file, and
exits 0; where nothing would change it says the harness directory is up to date. The removed group
is where the replacement's removals are enumerated: a file standing in the install directory that
the install would not write is listed there, whatever wrote it. Every path it prints and every
refusal it reports names the path. What the install would leave alone or skip, with the reason, is
reported on stderr on an up-to-date run and a dry run as on a changing one. It reports the refusals
it can foresee.
