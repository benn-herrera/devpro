# The install renders and copies

A claude project install writes the plugin's rendered
files and `hooks/hooks.json`, whose profiler entries are the wiring above. It copies the harness's
resources byte-verbatim — `harnesses/resources/claude/` holds `hooks/` alone, nothing under
`profiler/` — and writes the wrapper at `skills/devpro/tools/devpro.sh`. What it removes is *What
removes the retired path*, below.
