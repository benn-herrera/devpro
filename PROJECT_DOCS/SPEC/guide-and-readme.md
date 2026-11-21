## Guide and README

The `guide` skill is where a session starts or continues work with devpro. Every install carries it
under every harness (SPEC.md, Deployed Surfaces, Plugins). It applies when the user wants to start
a design, to learn how the development process runs or where their work stands, to see the
consuming project's board, or to install, update, inspect or change the installed set. It also
applies when a file carrying the devpro project's generated banner seems to need a change. It does
not apply to a change to the consuming project's own code.

Before any starting place, the skill says never to edit a file carrying the devpro project's
generated banner, anything in the plugin's install directory, or the devpro Python package the
consuming project installed. Then it lists the starting places, and each names what
serves it:

- starting a design: the `development` skill's *Design*;
- how the development process runs, or where the user's work stands: this skill's usage reference;
- the board: the `docdicer` skill's `kanban`;
- installing, updating, inspecting and changing the set: this skill's installation reference;
- the consuming project's own design: that project's contract documents.

The skill carries two reference pages, which the session reads when its starting place is reached.

- **Installation** covers every harness, including a user-level install:
  - running devpro: devpro installed with Homebrew from the `benn-herrera/tap` tap, else, on a
    machine without Homebrew, installed by hand with pipx or into a venv, and why a bare
    `pip install` fails on most hosts;
  - updating: upgrade the installed devpro, through Homebrew or by installing the next release into
    the same venv, preview with `--dry-run`, then rerun the same install; this holds under every
    harness;
  - inspecting: `devpro --version` gives the version that installs, and `devpro install … --dry-run`
    shows whether the installed set differs from what it would write;
  - global setup: a user-level install, and `install-agents-file` for a user harness directory;
  - under mage: an install into Mage's skills directory, `~/Mage/Skills`, made first where absent,
    which writes `~/Mage/Skills/devpro/`, and, with the kbase component, restarting Mage; and the
    `~/Mage/Skills/kbase/` directory an install from before the component left, which Mage loads
    beside the current one, so it is removed once;
  - the agents file: where an install keeps its block, and the `CLAUDE.md` redirect;
  - the requirements: `just` 1.27.0 or later, and 1.33.0 or later where the devpro line ships — on
    every project install of a nested plugin — for the `import?` of the include lines, the kb line
    with the kbase component riding the same floor; `perl` with core `JSON::PP` for the claude
    guardrail; and the
    `show-profile` skill's recording of a claude or opencode project install, which needs no more
    than what delivers it (Shipped files, the activity profiler), and ships nothing under mage;
  - what the operator sets up for a cold read: `DEVPRO_COLD_READ_DIR`;
  - rendering for another model family: it names the flag and leaves its grammar to SPEC.md,
    Rendering;
  - what a rendering pins by default: a claude install pins its family's members; an opencode or
    mage install pins none — under opencode the definitions carry no model, under mage they carry
    `model: inherit` — unless the devpro settings file carries entries for the harness;
  - the devpro settings file: its location (`~/.config/devpro/devpro.cfg`, `--config-file` to
    name another), the `install` setting's three values in `[<harness>]`, and the entries in each
    harness's `[<harness>-model-map]` section;
  - under claude, agents not offered after an install: run `/reload-plugins`. If a restart or
    `/reload-plugins` does not bring them, the plugin has not loaded. That happens when the session
    started away from the project root or before the trust dialog, when managed settings block it,
    when the `kbase` server is unapproved, or for an error that `/plugin`'s Errors tab shows. Each
    cause has its remedy. A user-level plugin shadowing a consuming project's is the other claude
    problem, also with its remedy;
  - under opencode, a claude install's skills reaching the opencode session, and how to stop it;
  - each install refusal SPEC.md specifies (Plugins, Write Safety, Agents File), with its remedy;
  - customizing the set: the consuming project's own rules go in its CONVENTIONS.md, or in its
    agents file outside the install's markers; a lasting change is made through a vendored copy
    or a fork.

  Where the `kbase` skill ships, the page hands installing kbase itself to the `kbase` skill.
- **Usage** lets an agent that has read only this skill take a user who has never used the
  workflow from a fresh install to their first landed plan, and, from the files present
  (`ACTIVE_*`, a plan's Status table, `ROADMAP.md`), tell a returning user where their work stands
  and what comes next. It walks one request through as an example, from the user's first words to
  the landed plan. For each step it says what the user decides and does, what they tell the
  session, what appears in the project, and what comes next:
  - getting started: a new project, or one with its process or contract documents already
    written, and the setup the `development` skill routes each to;
  - what the user's go is: the words that authorize an act, and the session's answer to a message
    that holds a question;
  - bringing a request, the design it becomes, and what accepting the design means;
  - the plan cut from it, and approving the plan, after which it runs to completion;
  - running the plan: the go the session needs before it acts (the agents file devpro installs),
    what it dispatches and commits, and when and why it asks the user anything;
  - the post-plan review, the burndown and landing the plan;
  - a release: what the user decides, the hardening plan, and tagging;
  - the periodic review: when it comes due and what it holds up;
  - the roadmap: tickets in `ROADMAP.md`, work set aside in `ROADMAP_DESIGNS/`, and when work
    leaves it;
  - lighter process: a step skipped at the user's direction, and work that goes straight to a
    plan;
  - the board: the session offers to run it in the background, or hands the command line, the
    user choosing;
  - where work stands: the files present and the state each names, for a returning user.

  It describes each step from the user's side: their decisions, their words, the files they see. It
  states no rule the session follows except as what the user observes, and names the `development`
  skill section, or the agents file, that holds the rule. It walks one request through as an
  example, from the user's first words to the landed plan.

The repository's `README.md` holds these things:

- what devpro is, with a screenshot of the board;
- what using devpro asks of the user;
- what using devpro gets the user;
- a minimal installation path, with no runner recipe:
  - installing devpro with Homebrew, or with pipx where Homebrew is absent, and the new shell the
    pipx bin directory needs before the next command runs;
  - for claude and opencode: the command that installs into the consuming project, and the lines
    to add to `.gitignore`, each harness's own;
  - for mage: making `~/Mage/Skills` first where absent, and the install into it for the mage
    harness; then, for the project the development process runs in, the claude or opencode install
    this path gives — the mage install alone installing into no project;
- what to do next: ask your agent, which loads the `guide` skill, invoked as SPEC.md, Deployed
  Surfaces, Install destination spells it, or the `show-profile` skill for a session's profile; and,
  after a mage install alone, the claude or opencode install into the project first: the guide's
  getting-started step for a project with nothing yet creates the project documents in the directory
  the session runs in, and a mage session starts outside any project the install reached;
- the third-party acknowledgments, a list of the packages the build runs, with the ideas and the
  ported source the project credits named above it.

No install delivers human-facing documentation.
