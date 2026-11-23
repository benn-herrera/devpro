### [Harness profiler](../../PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)

A refactor of the profiler pages' fills, which the leaf's page-template paragraph describes. `strict_fill`
(`devpro/profiler/pages.py`) fills literal marks only — text inert in its host language
(`<!--NAME-->` in HTML, `/*NAME*/` in CSS or JS), each replaced once by its value — and
`string.Template` and `$name` slots leave the module. The index template's four slots
(`$class_opencode`, `$class_claude`, `$opencode`, `$claude`, filled from `ZEBRA_MARKS`) become
literal marks or literal text, the executing agent's choice per slot. `strict_fill` keeps its refusals — a mark the text does not carry, a
value carrying its own mark — and refuses a value carrying any mark of the same fill, the guarantee
`string.Template`'s single pass gave; the identifier/mark split goes. `DATA_SLOT`, a literal mark,
is renamed `DATA_MARK`. The pages render as they do now, and the leaf, as the ARCHITECTURE delta's Harness profiler
entry leaves it, stays true.
