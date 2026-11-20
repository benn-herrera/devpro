### [ARCHITECTURE.md, Agents File](../../PROJECT_DOCS/ARCHITECTURE/agents-file.md)

`agents_file.py`'s `_block_plugin` and `_held_plugin` look the marker word up in the one plugin
name: a begin line whose first word is not `devpro` is a block of no plugin, so a legacy
`kbase`-stamped global block is replaced by the existing no-plugin rule with no migration code. The
rewritten statements are the delta entries above.

