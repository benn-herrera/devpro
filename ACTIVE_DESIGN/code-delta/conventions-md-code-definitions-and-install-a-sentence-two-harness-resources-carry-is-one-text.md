### [CONVENTIONS.md, Code definitions and install, A sentence two harness resources carry is one text](../../PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/a-sentence-two-resources-carry-is-one-text.md)

The state-table reminder's sentence is one text in two harness resources —
`devpro/harnesses/resources/claude/hooks/state-table-reminder.sh:52` and
`devpro/harnesses/resources/opencode/index.ts:107` — and both sites change together. The sentence

> Where the active plan carries a status table, a package is `in progress` when it is dispatched
> and `landed` when its work is accepted and committed.

is replaced by

> A package in the active plan's status table is `in progress` when dispatched, `landed` when
> accepted and committed.

— the shorter form chosen for brevity and so the injection does not elicit a reply from the session
it pokes. The tokens the tests hold (`status table`, `in progress`, `landed`) survive unchanged;
rendered and installed copies follow by regeneration.
