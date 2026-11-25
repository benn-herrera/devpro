# What does not exist.

The profiler ships no launcher resource: `harnesses/resources/claude/` holds
nothing under `profiler/`. No companion-plugin mechanism is built, so the profiler has no namespace of
its own and no carrier but the devpro plugin. Should it become optional later, it becomes a
`--components` value.

