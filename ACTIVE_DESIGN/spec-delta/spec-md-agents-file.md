### [SPEC.md, Agents File](../../PROJECT_DOCS/SPEC/agents-file.md)

The marker's plugin word is constant, the verb loses its flag, and the other-plugin case retires.

```
`<!-- vvv-devpro <plugin> <version> … devpro-vvv -->` to an end marker line
`<!-- ^^^-devpro … devpro-^^^ -->`. A file holds one block, and the plugin on the begin marker
says whose it is.
```
becomes
```
`<!-- vvv-devpro devpro <version> … devpro-vvv -->` to an end marker line
`<!-- ^^^-devpro … devpro-^^^ -->`. A file holds one block, and the plugin word on the begin marker
says whose it is.
```

```
`devpro install-agents-file DIR [--plugin=NAME] [--harness=NAME]`, the plugin defaulted as Deployed
Surfaces, Plugins states, installs that plugin's agents file into the directory the operator names —
the harness's user harness directory or a project's own — and is the only way the agents-file block
first reaches a user harness directory, or changes the plugin a global block belongs to.
```
becomes
```
`devpro install-agents-file DIR [--harness=NAME]` installs the devpro plugin's agents file into the
directory the operator names — the harness's user harness directory or a project's own — and is the
only way the agents-file block first reaches a user harness directory.
```

```
    removed and why. A block whose begin marker names no plugin is kept as the installing plugin's.
    A global block of the other plugin stays that plugin's: no install reports it, refuses on it or
    reconciles it. Only the block goes from the project: every other byte of the project's
```
becomes
```
    removed and why. A block whose begin marker names no plugin — a legacy `kbase`-stamped block
    included — is kept as the installing plugin's. Only the block goes from the project: every other
    byte of the project's
```

```
Both plugins' blocks name the `development` skill. `install-agents-file` installs no skill, so a
```
becomes
```
The block names the `development` skill. `install-agents-file` installs no skill, so a
```

