# ACTIVE DESIGN

## Drafts

### The `just install` target retires — the CLI's install verb is the only front door

`just install` is a checkout-side runner for the install verb, and no one reaches installation
that way: the only front door for installing devpro — outside internal test renderings, which
drive the CLI verb directly — is the install verb of the CLI itself (`devpro install` /
`python -m devpro install`), the surface check-wheel exercises and every install document states.
A user cloning this repository to run `just install` is not a flow that exists. The target
retires as a mechanism past its use; the recipe, its docstring and any test or document naming
it go with it. Its sibling `install-agents-file` is the same question — a checkout-side runner
for a verb the CLI serves — and retires with it or survives with its own statement, as the
executor's reference search and the agents-file churn ticket's fix decide.

### The modules' homes: kanban out of dicing, the checkers into doccheck

The modules' locations correspond to usage **and to the dependency direction**, and — the
boundary's principle — **kanban consumes a known-good doc set and serves it up; the module's job
is presentation, not validation**. Dicing and validation are different jobs. The shape:
`devpro.dicing.kanban` — the board, the dashboard's panel — becomes `devpro.kanban`;
**`plancheck.py` (the check verbs' implementation) and `planform.py` (the workflow documents'
model they validate against) become `devpro.doccheck`** — the validation world — whose model
`devpro.kanban` consumes. `dicing.cli`'s reverse arrow (`.kanban.plancheck`) is what blocks the
clean arrangement today. The target arrows point one way only: `devpro.kanban` →
`devpro.doccheck` → `devpro.dicing`, `devpro.dashboard` → the front ends, nothing back;
`dicerlib` flattening into `devpro.dicing` is the optional half. The CLI layer follows the same
line: **doccheck owns its commands' argparse and dispatch** (`check-plan`/`check-design`/
`check-roadmap`, lazy, the verb-entry pattern — the invariant test's exemption tuple gains it),
`devpro.dicing.cli` keeps the dicing verbs including `check-links`/`check-tree` (the dicing
operations' own verification), and `devpro/cli.py` composes the fourth `add_verbs` — the house
pattern the profiler and dashboard already follow. The generic verb-registry alternative is the
over-engineering trap the thesis's building-blocks table names.

### The install surface's stale and dev-only shapes

Four decisions, settled while the assemble-once plan ran (its record retired at landing; the
decisions are the work):

- **The dev-verb family gated.** `render` renames to `dev-render`; `render-agents-file` and the
  `harness` query verb go with it — the three dev-only subparsers registered during parser
  construction only under `DEVPRO_DEV=1`: absent from `--help`, refused with argparse's stock
  invalid-choice when unset, no user-facing documentation. The justfile's dev scripts
  (`render.sh`, `_render-slot.sh`, `render-agents-file.sh`) export the envar once.
- **The `dicing-snippets/` flattening and rehoming.** `devpro/dicing-snippets/runner-snippets/`
  becomes `devpro/runner-snippets/`, and the snippets leave the docdicer skill's directory — the
  outer name described docdicer's historical monopoly while the files run `devpro` from PATH for
  any consumer, and the install home inside `skills/docdicer/` carried the same stale ownership.
  Renames the shipped package (`install.py`'s `SHIPPED_PACKAGES`, pyproject's package-data) and
  relocates its install home; the include-line writer, the `.just`/`.mk` self-referencing
  comments, the tests pinning include paths, and the SPEC/plugins + ARCHITECTURE rows go with it.
  The stale `SPEC/plugins.md` citation (`docdicer.just`/`docdicer.mk` naming the retired set)
  corrects here.
- **`show-profile` renames to `profiler`.** The one verb-y name in a noun family
  (`development`, `docdicer`, `guide`, `kbase`), and the noun names the domain it reports on. The
  definition source, `values.py`'s `SHOW_SKILL`, `hooks.py`'s copy/messages, `guide.py`'s ref, the
  tests' `_SHOW_PROFILE`, the SPEC and README mentions, the rendered copies regenerate. Sequenced
  after any design whose delta pairs cite `show_profile.py`.
- **The bare `devpro` recipe removed** from the runner snippets — the one prefix-less recipe in a
  file whose own header promises `devpro-` prefixes so recipes cannot collide; `just devpro` runs
  `devpro --help`, which the consumer types anyway. The `.just`/`.mk` twins, the docstring, and
  the six-to-five `devpro-help` listing.

Each touches install behavior — a design first, then a plan.

### A naming rule for the strict fill's keys: literal marks are `_MARK`, `$name` slots are `_SLOT`

`strict_fill` splits its fills by whether the key is a `$name` slot or a literal mark, and the
call sites' names already agree (`DATA_SLOT`, `CSS_SLOT` retired, `BAND_LEGEND`, `DISPATCHED_MARK`,
`RETURN_MARK`, `LAYER_MARK`) — but no rule states it, and `LAYER_SLOT`-shaped names were proposed
before the `_MARK` convention was noticed. One CONVENTIONS sentence: a literal strict-fill mark is
named `_MARK`; a `$name` slot is named `_SLOT`. Carried by the next plan touching the fill.
