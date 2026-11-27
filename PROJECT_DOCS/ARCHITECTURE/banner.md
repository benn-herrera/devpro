# Banner

Under claude and mage a rendered definition other than a supporting file carries the generated
banner as one banner line in its frontmatter (SPEC.md, Rendering). `render.GENERATED_MARK` and
`GENERATED_NOTICE` spell the generated banner, and `install.stamped` writes the installed one. That
line is a YAML comment inside the frontmatter, so the opening `---` is still the file's first line
— the one thing a harness requires to read a frontmatter at all — and the frontmatter's field lines
follow the banner. A supporting file carries the banner as `<!-- !GENERATED! … -->` followed by a
blank line. The banner is written, never read back: what stands in the install directory is decided
by the wholesale replacement (Renders and copies), not by any file's carrier. Under opencode every
rendered file takes that comment carrier (`render._comment_banner`), a definition's own included,
because the body file holds no frontmatter; the entry strips the leading comment lines and the
blank line after them when it registers the body.
The tuning data rides on no rendered file. The set's one carrier is the **tuning table**,
written once per install at the install destination's root as `tuning.md` and replaced wholesale
with the rest of the install (Renders and copies); it records the family, the harness, the
effective category map and the stock list (SPEC.md, Rendering). No per-definition tuning line
exists, and `render.tuning_text` and `tuning_line` are gone with it. A harness-rendered file carries no banner: `registry.json` carries its marker,
`"plugin": "devpro"`, as the plugin manifest carries `"name": "devpro"` and `.mcp.json` the command
`"command": "kbase"`; `index.ts` and `guardrail.ts` carry their own `!INSTALLED!` header.

