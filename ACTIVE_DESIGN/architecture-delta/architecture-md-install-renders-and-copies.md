### [ARCHITECTURE.md, Install, Renders and copies](../../PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md)

The prune-walk statement keeps its reason under one install directory.

```
What moves between plugins is the install directory: under claude another plugin's install directory
(`.claude/skills/kbase/`) sits inside the harness directory's `skills/`, so a walk wider than the
install directory would delete a different plugin.
```
becomes
```
The walk is one install directory's: under claude the install directory
(`.claude/skills/devpro/`) sits inside the harness directory's `skills/` beside what the project
keeps there, so a walk wider than the install directory would delete a neighbor's.
```

