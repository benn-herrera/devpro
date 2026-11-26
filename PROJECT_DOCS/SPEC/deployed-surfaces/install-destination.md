# Install destination

An install names a **target**, its first argument that is not a flag. A target that is not an
existing directory is refused with nothing written. Where the target starts with a literal `~`,
the refusal says the shell did not expand it. The **harness** is, in order: the one
`--harness` names; otherwise the one whose harness directory sits inside the target — its
**project harness directory** (where the harness looks for a project's materials, such as
`.claude/`) or, in the user's home directory, its **user harness directory** (where it looks for
the user's own, such as `~/.claude/`); otherwise the one the target itself is the
directory of, matched on the target's trailing path elements (`.claude`, `.opencode`,
`.config/opencode`, and `Mage/Skills` for mage); otherwise the install is refused, naming
`--harness`. More than one harness directory inside the target is refused the same way. No other
part of a path selects a harness.

The install's **harness directory** is where its harness starts looking for its materials, in a
project or user-level. A project install also resolves the **project root**, the top directory of
the project it installs into; a user-level install places nothing relative to a project:

| target | harness directory | project root |
|---|---|---|
| any, with `--subdir=<dir>` | `<target>/<dir>`; an empty `--subdir=` is the target itself | the target |
| a harness directory (mage: `Mage/Skills`) | the target (mage: `<target>/devpro`) | the target's parent (mage: the target) |
| the user's home directory, for a harness whose user harness directory is inside it | the harness's user harness directory inside it | — (user-level) |
| any other | `<target>/<project-harness-dir>` | the target |

The project harness directory is `.claude/` by default, `.opencode/` for `opencode`, and `devpro/`
for mage, so a `Mage/Skills` target gives `<target>/devpro`. A home-directory target with
`--harness=mage` takes the last row, mage having no user harness directory: it is a project install
with the project root `~`, the plugin at `~/devpro/`, every package shipped, and the agents file in
`~/devpro/CLAUDE.md` titled `Global`, as a user harness directory's is. Mage loads nothing at
`~/devpro/`; under mage the target is `~/Mage/Skills`.

The install's **install directory** is where it writes the install product, a directory of the
plugin's own below the harness directory:

| harness | install directory |
|---|---|
| claude | `<harness-dir>/skills/<plugin>/` |
| opencode | `<harness-dir>/plugins/<plugin>/` |
| mage | `<harness-dir>` itself |

Under claude and mage the install product is one plugin, so its agents,
commands and skills are invoked as `<plugin>:<name>`, in a project and at user level alike. Under
opencode the install product is one plugin directory, and its definitions register as
`<plugin>-<name>`. The install directory may be absent and is created once every check has passed.

An install is **user-level** when its harness directory is the harness's user harness directory,
however the target reached it, and names the plugin's directory: `~/.claude/skills/devpro/` or
`~/.config/opencode/plugins/devpro/`. A user-level install renders the definitions the install
carries — the plugin's set with its components on — and the harness-rendered files (the plugin
manifest and `.mcp.json` where `kbase` ships, or
the registry `registry.json`), prunes as any install does, and writes nothing else but the devpro
tools package (Shipped files) and, under opencode, the plugin entry, a harness resource without
which the plugin cannot register: no other harness resource, no install-time probe or guardrail
registration (Shipped files), no other shipped package (neither `kb-tools/` nor the development
scripts package), no runner include line and no runner file. A user-level install with the kbase
component under opencode registers the `kbase` MCP server through the registry ([Plugins](plugins.md)).

A user-level claude install and a project's of the same plugin share a name, and Claude Code loads the
user-level one alone. A claude install reports this on stderr and never refuses over it: a
user-level install says it takes precedence over every project's copy of that plugin; a project
install says its plugin does not load where a user-level install of it is already
present. The install report is made on a dry run and on an up-to-date run as on a changing one. No
other harness reports it.

A claude install that writes the plugin prints one sentence after it: "If the new agents are not
available after using `devpro install`, `/reload-plugins` rescans the agent list." The installed
`guide` skill says the same.

An install writes into its install directory: every definition its plugin carries,
rendered by that same invocation, together with the shipped packages those definitions read (Shipped files),
each at its package destination, and the harness resources, copied into that same directory as they
stand (Shipped files). What is not part of the install product does not travel: test suites and their
fixtures, caches, `.DS_Store`, backup (`.bak`) copies, a `.venv` directory, and this repository's
own project documentation. That project documentation exclusion is a list of file names (`SPEC.md`,
`ARCHITECTURE.md`, `CONVENTIONS.md`, `THESIS.md`, `ROADMAP.md`, `AGENTS.md`, `CLAUDE.md`): none is
installed at any depth under a package destination. No installed file refers its reader to one of
this repository's own project documents. `README.md` is not in that exclusion: a shipped package's
`README.md` is installed. The optional tuning arguments — `--family`, and the entries in the
devpro settings file `--config-file=<file>` names — render the definitions under them (SPEC.md,
Rendering). The optional harness
argument names the supported
harness whose values the definitions are rendered with, and whose metadata they carry — in the
frontmatter under claude and mage, in the registry under opencode: each
field in the spelling that harness reads, and absent where that harness has no use for it; an
unsupported name is refused before anything is written. `dev-render` defaults it to `claude`; install
has no default, and resolves its harness as this section's first paragraph states. The devpro
settings file's `install` setting replaces that resolution where the file names the harness. The
file names a harness when either of its sections exists; each named harness installs per its
`install` setting.

Per harness, the setting is one of `always`, `detect` and `never`: `always` installs for that
harness whatever the target holds; `detect` installs where the harness's own harness directory is
one the target holds, judged per harness; `never` installs nothing for it.

`detect` is the setting's default where the file names the harness but sets no `install` key.

With the file naming any harness, one invocation installs for every harness it names, in name
order, each as its own install — the render built per harness from that harness's
`[<harness>.model-map]` table, where the file has one — with this section's guarantees; a
harness it does not name is not installed. The loop stops at the first refusal, naming the
harness that refused, and earlier harnesses' installs stand. A target that is not an existing
directory, and a `--subdir` outside it, are refused before the harnesses the file names are
judged. `--harness` given installs for that harness only, whatever the file's `install` setting
says, its section's model map still applying. Without the file, or with `--harness` given, the
resolution is the one above. A file naming no harness installs nothing, and says so: the report
names the settings file and the ways an install happens — pass `--harness=NAME`; or add the
harness to the file, either section of it: `install = always` in `[<harness>]` installs whatever
the target holds, and the `detect` default installs where the target holds the harness's own
directory (create that directory where absent). The report is made on a dry run and on an
up-to-date run as on a changing one. The refusal of a target that is not an existing directory,
and of a `--subdir` outside it, precedes this report where both fire. The file is validated
before anything is written (SPEC.md, Rendering); an `install` value outside the three is refused
naming them, where the file selects the harnesses — `--harness` given, and `dev-render`, do not
judge it.

An install directory may be any directory prepared to receive the install product. `--subdir`
names a directory inside the target: an absolute path, or one that leaves the target, is refused
with nothing written. That refusal names `--subdir` as typed. Every other refusal names the path
made absolute, with `..` collapsed.
