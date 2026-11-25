# What it sets

`kind`, `folder` and each kind's fields: ARCHITECTURE.md, Rendering, Kinds. A skill's `description`
is all the model sees before it loads the skill.

A `body` is a triple-quoted string whose closing quotes sit on the last text line: a body whose
closing `"""` stands on a line of its own carries a trailing newline and is refused
(`devpro.definition._check_body`).
