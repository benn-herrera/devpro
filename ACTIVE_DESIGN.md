# devpro absorbs its tooling — the dashboard server

devpro's tooling — the document dicer and the session profiler — runs as devpro code, from
devpro's install, and one dashboard server shows a project's development: what is going on actively
and what happened in the past, the kanban board and the profiler's index and pages as panels of one
loopback site. The operator installing devpro receives every utility the project ships in that one
install, with no wrapper steps, no on-demand tool installs and no hosted clone; a session or a user
opens one URL for the board and the traces; a consuming project's capture hook keeps the contract
it has today — never blocking a tool call, its capture path free of dependencies — and the
profiler's pages attribute a child session to the one that dispatched it.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

## ARCHITECTURE delta

## Code delta

## Drafts

### The single-venv boundary and the startup-time constraint

Decided. The argument that settles absorption over composition: the single venv install by brew
handles all the utility code needs — today docdicer is not in the wheel at all, and the wrapper
(`devpro/docdicer-tools/docdicer`) builds a venv beside itself and installs docdicer from GitHub on
demand, running the pinned release outside the wheel. Absorbed, the wheel carries all utility code.
Constraint stated with it: startup time stays snappy — the claude hook path pays a capture
invocation on every tool call — so the CLI dispatches lazily, importing only the invoked verb's
module, and the capture path stays dependency-free. Today `devpro/__main__.py` imports
`devpro.cli`, whose module level imports the install and render modules wholesale; the lazy
dispatch is a change to that loading, and the profiler module must not make the hook path pay for
anything it does not use.

### The runner surface: served, not injected

Decided. How consuming projects serve their traces is answered by the dashboard: the dashboard is
the serve surface for the profiler's index and pages, in the consuming project and in this
repository, and the show-profile skill's serve instruction points at it. Alternatives recorded as
not taken: the installs' runner include lines growing a serve recipe (the mechanism exists —
[Plugins](PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md), runner include lines — and would carry an
absolute install path and a second injected surface to reach a page the dashboard already serves),
and a profiler-serve subcommand of its own (a second server for the same traces, a second URL to
hand the user). Recipe injection generally is not taken by this pass; what becomes of the existing
injected lines is the CLI-surface question below.

### The hook wiring: how the capture finds the absorbed code

Decided: the profiler's code is devpro's — `hp.py` stops shipping as a copied resource, and the
hook files refer back to devpro wherever they needed `hp.py`. The questions the pass must close,
from what stands today:

- The committed hook entry runs
  `sh "$CLAUDE_PROJECT_DIR/.claude/harness-profiler/hp.sh" capture claude` (`hp.py`, `_hook_command`),
  and `profiler init claude` copies three files — the launcher, `hp.py` and `view.html` — into
  `.claude/harness-profiler/` (`HOOK_FILES`). With no copied `hp.py` beside the launcher, what that
  directory holds, what `init` copies, and what the hook entry's command becomes are one question.
- The finder: `hp.sh` searches for an interpreter it runs directly — `python3` on PATH, the Homebrew
  and `/usr/bin` fallbacks, a 3.9-or-newer probe, the `HP_PYTHON` override. The absorbed code runs
  from the `devpro` console script, whose interpreter the wheel fixes. Whether the search survives,
  is replaced by finding `devpro` on PATH, or the launcher goes entirely, decides the finder's
  python-search logic and the launcher's fate together; brew installs a console script where
  Homebrew puts an interpreter, so the PATH reality of a hook environment is not new ground.
- The never-block rule holds in exactly the environments this question is about: hooks may run with
  a bare PATH, and where the profiler cannot run, `capture` drains stdin and exits 0 without
  output, while every other subcommand reports and exits 1 (`hp.sh`). Whatever wiring this pass
  lands, `doctor` keeps naming what is missing and where it looked.
- The rendered surface of the same wiring: the show-profile skill's locate section
  (`devpro/definitions/skills/show_profile.py`) names the two launchers it tries
  (`../../profiler/hp.sh`, then the committed copy); its text is carried by the deltas with whatever
  this pass decides.

### The profiler payload and the verbatim rule

- `view.html` is not hook-run code: `render_html` reads it from beside the module and substitutes
  (`hp.py`, `VIEW_TEMPLATE`). [Harness resources are copied
  verbatim](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/harness-resources-are-copied-verbatim.md)
  covers everything under `devpro/harnesses/resources/`. The question: which payload files become
  devpro package code (out from under the verbatim rule, stamped by the package loop) and which
  stay resources — `view.html` read as a template from its resource location, or moved beside the
  module it renders for — and where a rendering module reads it from in either case.
- What `init` copies once the code is not a resource, and what succeeds the stale-hook comparison —
  `stale_hook` byte-compares `HOOK_FILES` between the repository's committed copies and the source —
  are named by the same pass.
- The lint gate: a Python resource is inside `just lint`'s paths as any other module; the absorbed
  code is package code and linted regardless. Naming this here so the gate neither silently narrows
  nor widens when the resource files move.

### The CLI surface of the absorbed verbs

Decided: docdicer is fully absorbed, its verbs landing as flat subcommands of devpro (`devpro dice`,
`devpro undice`, the check-* verbs, `kanban`), and the profiler's verbs join the same surface.
Questions:

- The verb list and names. Docdicer's commands are `dice-doc`, `undice`, `dice-docs`, `verify`,
  `check-links`, `check-tree`, `check-plan`, `check-design`, `check-roadmap` and `kanban`; devpro's
  surface today is `render`, `install`, `install-agents-file`, `render-agents-file` and the hidden
  `harness`. Which docdicer names survive as devpro subcommand names (`dice` against `dice-doc`
  among them) is the pass's to settle, beside the profiler's `tree` and `doctor`.
- The include-line mechanism and the tools package. The docdicer tools package — the launcher, the
  runner snippets, the release pin `VERSION` in `devpro/docdicer-tools/docdicer` — exists to run a
  separately published docdicer, and every project install writes the `docdicer` runner include line
  ([Plugins](PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md)); SPEC names it a separately published
  tool in the install tree ([Surfaces and
  layout](PROJECT_DOCS/SPEC/deployed-surfaces/surfaces-and-layout.md), [Shipped
  files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)). What retires with the absorbed
  mechanism and what is repointed — the package, the snippets, the pin, and the two conventions that
  hold them ([Docdicer pin is a
  release](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/docdicer-pin-is-a-release.md),
  [Runner include line is
  exact](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/runner-include-line-is-exact.md)) —
  is a delta this pass names.
- This repository's own recipes: `dev-dd` and `docdicer-repo` (the gitignored hosted clone in
  `docdicer/`), the recipes routing through them (`dev-check-plan`, `dev-check-roadmap`,
  `dev-check-links`, `dev-check-design`, `dice-doc`, `undice`, `check-links`), `dev-kanban` and
  `dev-profiler`, and the `import?` of the docdicer snippet at the justfile's foot. They re-route to
  the absorbed verbs, and the hosted clone and `docdicer-repo` retire only once those recipes run
  through what replaced them.
- The rendered definitions: the `docdicer` skill (its one offered surface being `--help` of the
  script it names, per [a skill omits its tool's offered
  surface](PROJECT_DOCS/CONVENTIONS/adding-definitions/a-skill-omits-its-tool-s-offered-surface.md))
  and the `docdicer` rows of the [Subsystem Map](PROJECT_DOCS/ARCHITECTURE/subsystem-map.md) are
  carried by the deltas with whatever this pass decides.

### The dashboard's URL space

Decided: one module, one loopback HTTP server, the board and the traces as panels of one site; the
two servers it replaces share the contract it keeps — bind `127.0.0.1`, a free port where none is
given, the URL printed once on stdout (`hp.py`, `serve`; docdicer's `kanban`). Questions:

- The path space. The profiler serves `/` and `/page/<session-id>`; the board serves its page, the
  project's documents read-only, and a moves endpoint that writes. One routing gives both panels
  their paths without one reading the other's; the pass names them.
- The outer frame's mechanism. The legend is served once and record selection swaps the inner
  content — whether the frame swaps a served inner asset, an iframe over the profiler's page, or
  another arrangement, and what the all-records list as the inner frame's top-level view is served
  from, are this pass's choices. The inner page stays the self-contained bytes the file flow
  produces (`tree --format html`); the composition is not a rebuild of the page format.
- Response headers and read-only serving: the board's page carries a Content-Security-Policy and
  answers only its own host; one server answers for both panels, and the pass states what carries
  over to the traces' pages.

### The outer frame rides the dashboard shell

Decided. The profiler page's how-to-read guidance moves to an outer frame — shown once, not
repeated per record page — and selecting a record changes the inner frame only, the inner frame's
top-level view being the all-records list. The dashboard's shell is its natural home: the frame is
the dashboard's, and this rides the same pass as the attribution work below. The driver is the
reading experience — render-on-demand makes repetition free, so this is composition, not cost. The
served-asset shape of the frame is the URL-space question's, not this ticket's.

### The attribution record

Decided. The capture extracts the child session id parent-side into `child_agent_id` — profiler.ts
reads the dispatch result it already reads for `agentType`; the render groups children under their
dispatching session in the index, links each Agent row to `/page/<child-id>`, and heads child pages
with the session that dispatched them. The stores stay flat: the child never knows its parent at
write time, the hierarchy is metadata the parent side builds, and claude has no child session
records at all — a child's calls in claude live in the parent's trace, so `/page/<child-id>` links
exist where a child owns a trace file, under opencode. Open, as the first dashboard panel work:

- The record schema: `child_agent_id`'s place in the record both harnesses write — hp.py's
  `serialize` field order and empty renderings, the schema version's fate — and the profiler.ts
  record landing in the same shape.
- The panel's presentation of the hierarchy is the dashboard's: the index groups, links and heads
  children by this field, and the panel states where a store holds nothing to attribute.

### Migration of existing installs

What the pass must settle for what is already out there:

- Consuming projects with a committed hook: `.claude/harness-profiler/` holds the three files an
  older `init` copied, and `.claude/settings.json` holds the hook entries. The copied `hp.py` is
  self-contained and keeps working; the migration is the boundary — no half-absorbed state where an
  old `hp.py` stands beside a hook command that runs devpro, or a launcher that finds neither.
  `doctor`'s stale-hook report and the launcher's own rename precedent (the `hp` launcher before
  0.2.0, replaced in place and unlinked by the new `init`) name the shape of this migration.
- Stores: traces recorded by older code render identically — the schema the absorbed module reads
  is the one the copies wrote, version 2, and `.devpro-temp/*-profiler/` stays where it is.
- User-level installs: they copy no resource
  ([Install destination](PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md)), so the
  show-profile skill's first launcher is absent there and the committed copy is how a claude-on-web
  session records at all. Where devpro itself is on PATH after absorption, the hook-wiring decision
  decides what such a session can run.
- Mage: mage ships no profiler payload (SPEC.md, Guide and README) — the dashboard must not turn
  that into a broken surface. A mage install offers neither panel's data source and says so.
