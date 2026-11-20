### [ARCHITECTURE.md, Install, Plugins](../../PROJECT_DOCS/ARCHITECTURE/install/plugins.md)

`install.py` takes the `SHIPPED_PACKAGES` rows whose owner the selection's `ships(name)` admits, and
`runner_file.install_include_lines` writes the lines of the sets those rows carry — the docdicer
line always, the `kb` line with the component on; `_install_managed_paths` needs no change, already
naming every destination. The `harness.mcp_json` owner and the opencode registry gate stay keyed on
the `kbase` definition shipping, which the component decides. The kb-tools snippets' header comments
(`devpro/kb-tools/runner-snippets/kb.just`, `kb.mk`) reword their spelled install paths to
`.claude/skills/devpro/skills/kbase` and `.opencode/plugins/devpro` and drop the `--plugin=kbase`
writer line. The rewritten statements are the delta entries above.

