# A delta application ends by searching the doc set

An applied passage pair is followed by a search of the document set for the wording of the behavior
it replaced (`git grep -l '<the replaced phrase>' -- PROJECT_DOCS`) and a read of each hit. A
statement the application leaves false is reported to the session, not rewritten where it stands:
the entry's scope is its target leaf, and a stale statement in another leaf is that leaf's own text,
whose fix the session schedules for the commit that carries the change.

The search reads for the rule, not only its exact words: a stale statement phrases the same rule
with different words, so where the replaced phrase finds nothing, also grep for the rule in another
form. `could not be read` and `unreadable` are one rule stated two ways; a search for `unreadable`
alone leaves the `could not be read` docstring standing.
