### [ARCHITECTURE.md, Agents File](../../PROJECT_DOCS/ARCHITECTURE/agents-file.md)

The block is the one plugin's, and the marker section loses the two-plugin cases.

```
reference to `development` in its own paragraph, and both plugins ship it, so both blocks carry it.
```
becomes
```
reference to `development` in its own paragraph, and every install carries it, so the block carries it.
```

```
**The plugin on the marker.** The begin marker line reads `vvv-devpro <plugin> <version> …`: the
plugin is `@!plg-name!@` (`clauses.PLUGIN_NAME`), the version `@!agf-version!@`. A file holds one
block, because two blocks with different markers would deliver the shared rules twice to every
session that reads the file (SPEC.md, Rendering). `agents_file._block_plugin` reads the first word
after the marker's opening as a plugin name, and `_release` the word after it. A begin line whose
first word is no plugin's name is a block of no plugin, with no release. On a project install
`checked_followed_agents_file` keeps a global block current as the plugin `_held_plugin` reads from its
begin line (`install-agents-file --plugin=<plugin>` into the user harness directory is what changes it), and a
block of no plugin as the installing plugin's. The block of no plugin differs in content from the
plugin's, so it is rewritten under the existing rule for a stamp that is not a release version. Mage
writes the plugin's block into `<plugin>/CLAUDE.md` in its own directory, so no conflict arises.
```
becomes
```
**The plugin on the marker.** The begin marker line reads `vvv-devpro devpro <version> …`: the
plugin word is `@!plg-name!@` (`clauses.PLUGIN_NAME`), the version `@!agf-version!@`. A file holds one
block, because two blocks would deliver the shared rules twice to every
session that reads the file (SPEC.md, Rendering). `agents_file._block_plugin` reads the first word
after the marker's opening as a plugin name, and `_release` the word after it. A begin line whose
first word is not `devpro` is a block of no plugin, with no release — a legacy `kbase`-stamped block
reads as one. On a project install
`checked_followed_agents_file` keeps a global block current as `_held_plugin` reads it from its
begin line (`install-agents-file` into the user harness directory is what changes it), and a
block of no plugin as the installing plugin's. The block of no plugin differs in content from the
plugin's, so it is rewritten under the existing rule for a stamp that is not a release version. Mage
writes the plugin's block into `devpro/CLAUDE.md` in its own directory, so no conflict arises.
```

