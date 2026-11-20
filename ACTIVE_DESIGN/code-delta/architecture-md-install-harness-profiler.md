### ARCHITECTURE.md, Install, Harness profiler

The three resource files land at `devpro/harnesses/resources/claude/libexec/` (`hp.sh`, `hp.js`,
`view.html`), each gaining the `!INSTALLED! … devpro` banner line within its first ten lines at
vendoring; `devpro/harnesses/claude.py`'s `_registration_hooks` gains the six profiler entries as
data; and the `show-profile` skill joins `devpro/definitions/skills/` as a rendered definition whose
finder names `../../libexec/hp.sh`. The leaf the delta above creates states them.

