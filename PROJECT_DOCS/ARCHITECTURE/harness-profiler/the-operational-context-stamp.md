# The operational-context stamp

Every record a capture writes carries the session's operational context, so the render can answer
what happened under what plan and which directives — the before-and-after comparison an agent or
skill tuning is judged by. The stamp is two fields on the record, `plan` and `directives`, taken
once per session: `plan` the active plan's title, the first level-1 heading of the project's
`ACTIVE_PLAN.md`, or of `ACTIVE_PLAN/entry-point.md` where the plan is diced; `directives` a digest
of the directives the session's harness loaded the devpro set from — the files beneath the project's
harness directory that carry an installed banner or an ownership marker (Installed tree), together
with the project's agents file, the set whatever stands at the session's start, so the digest
fingerprints state and not install history. The digest is sha256 over the sorted `(path, digest)`
pairs, each file's digest sha256 of its bytes, every path project-relative. A field the project
gives the capture nothing for — no active plan, no file carrying a banner or marker — is left out
by the Python capture and `null` by the opencode's, the absent rendering each capture's records
already take.

The stamp is taken once: where the session's store already holds records, the stamp is theirs, read
off the record whose `at` is earliest and copied onto the record being written; where the store
holds none yet, the capture reads the plan and computes the digest fresh. A digest's per-file
digests stand in `.devpro-temp/.profiler-directives/<digest>.json`, written where no manifest for
the digest stands, so a digest's file list is recoverable and two digests' difference is answerable;
the directory is not a store, and no reader of the stores reads it as one. The session's start binds
no field of its own: the store's earliest `at` is the session's start, and the stamp gives it no
second home.

The records are schema 4: `SCHEMA_VERSION` in `devpro/profiler/values.py` and the opencode
capture's own constant move together, and the tests pinning the schema and the record fields —
`tests/test_devpro_profiler.py`'s among them — move with them, the pinned expectation moving with
its requirement. The stamp rides the page data both carriers render, read off the records at the
same render that reads everything else: `tree --format html`'s page and the dashboard's session page
name the session's plan and digest alike, so the served page and the rendered one stay the same
page. A session captured before the stamp carries neither field — it renders unstamped, takes no
part in a before-and-after partition, and no association is inferred for it: the sessions are the
only observers of directive state, and a partition the records do not state is not drawn.
