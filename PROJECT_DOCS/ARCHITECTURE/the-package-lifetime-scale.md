# The package lifetime scale

The development skill's process scales with a package's **lifetime**, which names the code's
durability — where it will live — and nothing else. The scale has three values, stated in the
development skill's *Plans* section and in the guide's *Lifetime* bullet:

- **shipped** — the package reaches a user. It buys the whole process: design, plan, dispatch,
  review, the post-plan review included.
- **persistent** — the package is tracked in the repository and reaches no user: tests, the project
  documents, `ROADMAP.md`, CI and configuration. It buys the done-line and the checkpoint gate, and
  no post-plan review: its tests verify by running and its documents by their checks.
- **transient** — the package lives in the scratch directory only and is never committed.

The scale is held in the definition sources alone — `devpro/definitions/skills/development.py` and
`devpro/definitions/skills/guide.py`; no SPEC leaf states it, the skill being its own statement. A
release's plans carry shipped packages only: a persistent package taken into a release is re-rated
shipped before the hardening plan runs. An experiment kept becomes persistent; one discarded is
transient.
