### Installing this repository

`just agents` installs this repository's own `.claude/` and `.opencode/` with the plain
`install` verb, once per harness, as the devpro plugin, naming this repository as TARGET and the
harness with `--harness`. opencode and mage need no category map: their `default_category_spec`
values leave every model unpinned. Each
install also keeps the agents-file block current, in the global agents file where that holds
a marker line and else in this repository's `AGENTS.md`. Under claude the install lands in the
plugin, `.claude/skills/devpro/`, and under opencode in `.opencode/plugins/devpro/`.
`install_include_lines` writes this repository's include lines as it writes any project's. None are
written for a harness-directory plugin
(mage, whose `project_harness_dir` is `devpro` and whose `user_harness_dir` is `.`): the install
skips that call there, so a mage install writes no include line and creates no `Makefile`.
