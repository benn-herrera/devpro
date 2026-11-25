# What removes the retired path.

`init` unlinks, in the repository, the retired launcher
`profiler.sh` and the names it carried before it — `hp.sh`, `hp` — with `hp.py` and `view.html` beside
them, then removes `.claude/harness-profiler/` where that leaves it empty (`hooks.init`, over
`RETIRED_LAUNCHERS` and `RETIRED_HOOK_FILES`). It unlinks `.claude/skills/show-profile/SKILL.md`,
the skill under its former name, with its directory where that leaves it empty. `install`'s copy step
removes, on every install, the retired launcher files standing in the install directory —
`RETIRED_RESOURCE_FILES`: `profiler/profiler.sh` and `profiler/hp.sh` — where each carries this
repository's installed header, then removes `profiler/` where that leaves it empty
(`RETIRED_RESOURCE_DIRS`). `install` deletes only a file carrying the header it stamps; `init`
deletes by name, under `.claude/` in the repository it targets. The preflight predicts both from the
same lists. A hook command spelling a retired launcher stays this tool's: `hooks.is_our_command`
recognizes it, and an `init` re-run replaces it.

