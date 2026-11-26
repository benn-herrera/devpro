# A top-level key is a bare harness name

The devpro settings file's tables are named per harness: a top-level key is a bare harness name,
`[claude]` naming claude's table, and `[<harness>.model-map]` is that harness's nested subtable —
its model map. A quoted dotted top-level key (`["claude.model-map"]`) names no harness's table:
TOML reads the quoted key as one table whose name is the whole dotted string, not a harness table
and its subtable, so it is refused with the unknown tables, naming the table and the supported
harnesses. The trap the rule answers: a quoted key parses and reads plausibly — a reader meets a
table that looks meant and re-litigates whether it should stand — and so it is refused, not
tolerated. The behavior — the refusal and what its message names — is SPEC.md, Rendering's.
