### A delta application is followed by a search of the doc set

An applied passage pair is followed by a search of the document set for the wording of the behavior
it replaced (`git grep -l '<the replaced phrase>' -- PROJECT_DOCS`) and a read of each hit. A
statement the application leaves false is reported to the session, not rewritten where it stands:
the entry's scope is its target leaf, and a stale statement in another leaf is that leaf's own text,
whose fix the session schedules for the commit that carries the change.
