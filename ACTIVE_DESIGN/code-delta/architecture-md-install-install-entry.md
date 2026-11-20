### [ARCHITECTURE.md, Install, Install entry](../../PROJECT_DOCS/ARCHITECTURE/install/install-entry.md)

`cli.py`'s `_add_plugin` becomes the `--components` CSV parsing and validation — optional components
only, required names refused, hard override — and every `args.plugin` / `plugin=` call site across
the verbs retargets to it. The hidden `plugins` verb and its only consumer,
`devtools/scripts/_plugin-names.sh`, are deleted. `devtools/scripts/_harness-value.sh` calls
`python3 -m devpro harness NAME KEY` with no selection flag. The rewritten statements are the delta
entries above.

