## Subsystem Map

Every entry below but the last is rendered from the definition module under `devpro/definitions/`
named for its output path, or for its group module (Rendering). A shared-text name given
here is a constant or function in `devpro/clauses.py`, and an anchor is spelled `fam-<key>`.

- **Implementation and review seats** — generalist-coder, language coders (c, cpp, go, lua, python,
  rust, typescript), shell-dsl-coder, platform experts (android/ios/linux/macos/web/windows-app-expert,
  linux-kernel-driver-expert), architect, and — sharing the coding-review domain — security-reviewer
  and tech-writer, which is both the authoring and the reviewing agent for READMEs and human-facing guides.
  A *group* is narrower than this list and is the defined term: the definitions whose own
  `Definition(...)` call names one membership clause (CONVENTIONS.md, Group membership). The coder and
  platform-expert groups carry the test-precondition clause, one constant in `clauses.py` beside
  `clauses.TESTS_PROTECT_LOGIC`, which keeps defining the checksum the precondition forbids ordering:
  a package that adds a test states the defect the test fails on before the change — the defect, and
  the run that fails before the fix and passes after — and where the only failure the test can catch
  is the artifact's own text or structure changing, the test is a checksum and is not written; a
  property two renders are held to together is not such a pin.

  `clauses.DISSENT`, which nineteen definitions carry, directs the dispute its closing sentence
  names: an order whose result satisfies every stated requirement but whose only possible variation
  is form.
- **kbase component + kbase** — the `kbase` skill alone: the definition the kbase component adds to
  the devpro set, named among the component's contents in SPEC.md, Deployed Surfaces, Plugins
  (`devpro/components.py`). `kbase.py` owns a directory,
  `skills/kbase/SKILL.md` routing by request and `skills/kbase/references/reading.md`,
  `building.md`, `maintaining.md`, `scoring.md`, `scoring-system.md` and `installing.md` carrying
  what each route needs; the skill entry file is the only text every session pays for, and the rule
  that a supporting file is read only when its route is reached is the skill entry file's own — its
  *Route by the request* section says so, and nothing but that text stops a read.
  `clauses.kb_orientation`, carrying the KB system model with a per-supporting-file `role=` clause,
  goes to the two supporting files that work a KB the build has finished with — reading, which
  reports, and maintaining, which modifies; `building.md` and `scoring.md` carry what their own job
  needs. The skill and its supporting files are project-portable — per-project facts live in the
  consuming project's `kb-root/AGENTS.md`, under every harness. The kbase component reaches kbase, the
  executable the operator installs (no install writes it), only through the harness's `kbase` MCP
  server, offered under that harness's `mcp_tool_prefix`. The minimum version and the formula are
  written once, as `KBASE_MIN_VERSION` and `KBASE_TAP_FORMULA` in `kbase.py`, and filled into the
  skill entry file and `installing.md`. `clauses.KB_RUNNER_TARGETS` goes to the maintaining
  supporting file. The consuming project's runner targets are the `kb-`-prefixed recipes of this
  repository's `devpro/kb-tools/runner-snippets/kb.just` and `kb.mk`, prefixed so they cannot
  collide with a consuming project's own targets. The skill entry file's not-offered branch and
  `installing.md`'s restart section carry a harness-conditional paragraph, the `tools_reload_rule`
  `OptionalHarnessText` hole beside the guide's `reload_rule`: where the harness reloads plugins, it
  names that remedy for the `kbase` MCP server's tools; a harness without one drops the paragraph.
- **Specialists** — applied-mathematician, biz-dev-strategist, economic-historian, literature-scout,
  marketing-comms-expert, ml-engineer, prompt-engineer, prose-architect, theoretical-economist:
  single-purpose, invoked directly rather than as part of a coding pipeline.
  applied-mathematician carries the `fam-ask-vs-stipulate` anchor.
- **Tool-driving skill:** `docdicer`, one `SKILL.md` with no supporting files, delivered by every
  install.
  `docdicer.py` routes the session to devpro's dicing verbs — `dice`, `undice` and the check
  verbs — run from the command line through the installation's wrapper, which `clauses.WRAPPER`
  names: `../../tools/devpro.sh` resolved from the skill's directory (SPEC.md, Deployed Surfaces,
  Installed tree), run with the project root as working directory. It does not restate the verbs'
  `--help` (CONVENTIONS.md, A skill omits its tool's offered surface). The skill carries no install
  step. Its runner instruction names the recipes of the `devpro` snippet set: where the project's
  runner includes that set, the checks run through the recipes — `devpro-help`, and the four gates
  `devpro-check-plan`, `devpro-check-design`, `devpro-check-design-deltas-applied` and
  `devpro-check-roadmap`, which take no argument, each checking the active file under the project
  root — the active plan, the active design, the active design's applied deltas and `ROADMAP.md` —
  with a direct call through the wrapper for any other (Plugins). Its board paragraph names the
  `dashboard` verb, run through the wrapper, for the board, the dashboard's panel, offering to run
  it as a background process or handing over the command line, the user choosing.
  It also carries a paragraph, an optional reference to `kbase` (Rendering, Placeholders), saying
  `kb-root/` belongs to kbase and docdicer leaves it alone unless the user directs otherwise; it
  renders only where kbase ships.
- **Profile skill** — `profiler` (`definitions/profiler.py`): one `SKILL.md` with no
  supporting files, delivered under every harness. It renders the newest session's trace — read from
  either `.profiler-claude/` or `.profiler-opencode/` under `.devpro-temp/`, the two stores
  `devpro profiler tree` walks — as text, as a self-contained HTML page, or
  served over HTTP by the dashboard's profiler view: its serve section names the `dashboard` verb,
  run through the tree's own wrapper, which `clauses.WRAPPER_PROFILER` names — the project's committed
  wrapper where `init` rendered the skill outside the install directory, the installation's own where
  the install rendered it (Rendering, Placeholders). The
  tree's drawing is the code's rule: `tree --verbose` draws every node of the session, and the
  plain tree draws the placeholder and marker nodes and the calls whose tool is in `PARENT_TOOLS`.
  The skill runs the profiler through that one wrapper, which dispatches the `profiler` verb and its
  `tree` subcommand
  (Harness profiler).
- **Guide skill** — `guide` (`definitions/guide.py`): one `SKILL.md` and two supporting files,
  `references/installing.md` and `references/using.md`, carried as `SkillFile`s, delivered
  under every harness. Its board section routes the board to the `docdicer` skill and names no
  command and no recipe; `references/installing.md` runs `profiler doctor` through the wrapper
  `clauses.WRAPPER` names; its install, update and
  version commands name the `devpro` command on `PATH` (SPEC.md, Deployed Surfaces, Shipped files). The description names the uses SPEC.md, Guide and README lists, and
  says it is not for a change to the consuming project's own code. `SKILL.md` is a route, as the
  `development` skill's *Route* table is: one row per starting place SPEC.md, Guide and README
  lists, under the never-edit rule it states. The `development`, `docdicer` and `profiler` rows name
  their skill by a plain reference (`clauses.ref`), safe because every install carries all three.
  `references/installing.md` carries everything else about the installed set. That includes three
  paragraphs of its own, each dropped where its value is empty:
  - the `reload_rule` placeholder (Rendering, Placeholders), which says to run `/reload-plugins`
    when the agents an install wrote are not offered. It is kept under claude alone;
  - the `side_by_side_rule` placeholder, which says how to stop opencode loading a claude
    install's skills. It is kept under opencode alone;
  - an optional reference to `kbase` (`clauses.optional_ref`), which hands installing kbase itself
    to that skill. It is kept where the kbase component is on.

  The plugin is named through `clauses.PLUGIN_NAME`, and the repository through
  `clauses.REPOSITORY_URL`.
- **Development skill** — `development` (`definitions/development.py`): one `SKILL.md` and six
  supporting files (`references/new-project.md`, `project-documents.md`, `project-setup.md`,
  `adopting.md`, `release.md`, `design.md`), carried as `SkillFile`s, delivered under every
  harness, mage included. Beside them in the skill's directory sits the development scripts
  package, `scripts/cold-read.sh`, owned by `development`: a shipped package, not one of the
  `SkillFile`s (Install, Renders and copies). The skill states one development process for the main
  session; the agents file's *Task management* points the session at it. `development.py` writes
  the roadmap's tickets, plan, review document, design and set-aside locations and the forms stated
  in SPEC.md, Plan Status Form, at seven sites: the *Terms* section's fixed table (the locations),
  the entry body's `## Plan status`, `## Roadmap tickets` and `## Design` sections, its `## Plans`
  section (the plan under way at `ACTIVE_PLAN.md`, or the tree `ACTIVE_PLAN/` where the plan was
  diced, read through its `entry-point.md`; a design diced at its `##` and `###` headings only),
  `references/design.md` (a
  design's final form, its fixed line one constant) and `references/release.md`. The *Design*
  section has the session run `check-design` before a design is offered for acceptance and again
  on an entry added to an accepted design, and *Roadmap tickets* has it run `check-roadmap` after
  each edit to `ROADMAP.md`. Each term the process names (active plan, step-down model and the
  rest), and a design's fixed summary line, is one module-level `*_TERM` constant that every mention
  in `SKILL.md` and its six supporting files interpolates; a test reads `development.py` and fails
  where a term's value is written literally in a body string, so no two mentions can name a term
  differently. Its
  `docdicer` references are optional references (Rendering, Placeholders), and `docdicer` ships
  with every install, so each fills. The *Plan status* and *Roadmap tickets* sections render whole
  under every install; each one's `check-plan` or `check-roadmap` instruction is a paragraph of its
  own, so an optional reference that fills to nothing drops that paragraph alone. The *Design*
  section's delta-application sentence names no runner recipe: the application is verified by
  `check-design --deltas-applied`, the runner recipe it named retired with the docdicer tools
  package (Recipes). The sentence
  naming the default step-down model is
  `clauses.STEP_DOWN_MODEL`, the `tun` placeholder (Rendering, Placeholders), so that sentence alone
  renders only where the rendering names a mechanical member to step down to. The entry body's
  `## Commits and pull requests` section gives the attribution line every commit message and
  pull-request description carries; it names the harness by `clauses.DISPLAY_NAME`, the
  harness's `display_name` (Rendering, Placeholders), and no model, and links the repository by
  `clauses.REPOSITORY_URL`. The *Dispatchability* section requires what the coding seats' bullet
  states: a package that adds a test names the defect it fails on.
- **Install machinery** — the one entry not rendered from a definition: `install.py` renders, copies
  and prunes; `install_base.py` holds what the install modules share (the package and checkout
  paths, the kb-tools package paths, `VENV_DIR`, the path checks, UTF-8 text reading and the report of what an
  install left alone); `runner_file.py` writes the runner include lines, one per `SnippetSet` the
  install passes it, prepares the project's scratch directory and writes the `.gitignore` line for it;
  `preflight.py` runs that install into a scratch copy and compares (Install, Renders and copies);
  `agents_file.py` does the same for the agents file (Agents File). The imports layer: `install_base.py`
  and `install_target.py` import no other install module; `preflight.py` imports `install_base.py`;
  `runner_file.py` imports `install_base.py`; `agents_file.py` imports
  `install_base.py`, `install_target.py` and `preflight.py`; `install.py` imports all of them.
