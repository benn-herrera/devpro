# Untracked output is not source

An untracked file under `.claude/`, `.opencode/` or `rendered/` is render or install output, not
source. SPEC.md states what an install ships and to which destination (Deployed Surfaces), and
what a re-install replaces (Write Safety); ARCHITECTURE.md's Repo Layout holds the trees each is
sourced from. The next install replaces the install directory whole — the whole tree goes, whatever
wrote it, so a change placed there is gone on the next install, and `skills/kbase/kb-tools/` among
the rest. A change belongs at the source, not in the copy. Before an edit brief names a path, `git ls-files <path>` settles
which it is, and the brief names the source. Running definitions point at the copy, which is how a
brief comes to name it.

`rendered/` is the whole of that: it is gitignored, every slot under it is output the render and the
retake write, and nothing it holds is ever read back as input. A worktree or a render placed there
is scratch, deleted with the rest of the tree it stands beside.
