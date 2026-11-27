# ACTIVE DESIGN

## Drafts

### Profiler sessions page does not populate

Landing on the page starts with this warning:
```
Object { level: "warn", message: "board connection lost", error: "TypeError: NetworkError when attempting to fetch resource." }
board.js:13:61
the index could not draw the feed: ReferenceError: clip is not defined profiler:386:15
```

If you untick the 'claude' checkbox it will show opencode session entries. If you re-tick it you get a console error:
```
Uncaught ReferenceError: clip is not defined
    stampCell http://127.0.0.1:50116/profiler/:145
    row http://127.0.0.1:50116/profiler/:187
    draw http://127.0.0.1:50116/profiler/:269
    <anonymous> http://127.0.0.1:50116/profiler/:355
    EventListener.handleEvent* http://127.0.0.1:50116/profiler/:353
    <anonymous> http://127.0.0.1:50116/profiler/:393
 profiler:145:25
```

### Project name should be centered in dashboard nav bar

Right now the project name only appears on the browser tab. 
Centered, bold in current light/dark mode opposite accent color?
Correct treatment up for debate, but needs to be highly visible.

### Auto-reload devpro development skill after compaction

compaction hook to record a marker, context hook to inject the `@devpro-development` command.
note: only necessary for opencode. claude code automatically reloads active skills after a compaction (verify that)

### The profiler and hooks retirement logic is removed

The user's ruling: the retired-path machinery in `devpro/profiler/hooks.py` is a bad design and
is obviated by the wipe — an install replaces the install directory wholesale, so no inventory
of what an older `init` wrote is kept or consulted. Remove `RETIRED_LAUNCHERS`,
`RETIRED_HOOK_FILES` and `RETIRED_SKILL`, the unlink logic they drive (`hooks.py`'s retired-file
and retired-skill removal), and the tests pinning them: `test_init_clears_an_older_runs_launcher_and_files`
and `test_init_removes_the_skill_an_older_init_rendered_under_its_former_name` in
`tests/profiler/test_init.py`, and their counterparts in `tests/profiler/conftest.py`. ARCHITECTURE's `what-removes-the-retired-path.md` leaf goes with
them — its subject stops existing.

Open question: `hooks.py` also reads `RETIRED_LAUNCHERS` to rewrite settings-file hook entries
that name a retired launcher; `test_init_renames_a_committed_hook_written_under_a_launcher_name`
pins it. The settings file sits outside the install directory, so the wipe does not reach it, and
the wipe design's carve-out names the settings file's hook entries as keeping their handling —
their handling today includes this rewrite. Decide whether the rewrite goes with the deletion
logic or stays as the settings entries' handling; the test's fate follows the rewrite's.
