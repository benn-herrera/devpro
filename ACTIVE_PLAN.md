# Active plan — one devpro plugin with optional components; the activity profiler ships as payload

From the accepted design, diced: [ACTIVE_DESIGN/entry-point.md](ACTIVE_DESIGN/entry-point.md) — 38
entries under `spec-delta/`, `architecture-delta/` and `code-delta/`, the tree being the design's one
source and the delta byte-check's (P1b retired the monolith `ACTIVE_DESIGN.md`).
Every package is **shipped**: the whole
process, one commit closing each package; the landing commit that deletes the plan (P6) stands
outside the package commits, so "one commit closing each package" and P6's landing sentence describe
two different commits, not one.

Sequencing: P1b, then P1, then P1a, then P1c, then P1d, then P2, then P3, then P4, then P5, then
P6. Each package leaves the tree green; P1b is landed, its work done before the run proper. P1
carries every CLI
caller and every test pin the components flip breaks; P1a re-anchors the
six CONVENTIONS leaves P1 falsifies. From P1 until P4 lands, the SPEC and ARCHITECTURE leaves still
describe the two-plugin world while the code runs one-plugin-plus-components —
no runner target compares the documents' claims to the code, so the gates stay green across that
gap; the plan names the gap here rather than leaving it unspoken.

The delta byte-check (`just check-deltas`) today exits 1 with 88 `becomes` blocks not applied and 2
problems — the two `Harness profiler` entries' headings name no target leaf (the tree leaves
`ACTIVE_DESIGN/architecture-delta/architecture-md-install-harness-profiler.md` and
`ACTIVE_DESIGN/code-delta/architecture-md-install-harness-profiler.md`), so the check cannot find one. P2 adds the two links when it creates the profiler leaf
(the check cannot resolve the entry without one, and a heading link changes no accepted wording),
leaving 0 problems and 87 not applied; P3 applies every SPEC delta block; P4 every remaining
ARCHITECTURE delta block; from P4 the run reports `0 not applied, 0 problems` and exits 0.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | landed | expert | the components selection replaces the plugin machinery — code, CLI callers, README, every pin |
| P1a | landed | expert | the six two-plugin CONVENTIONS leaves re-anchored to the one-plugin-plus-components reality |
| P1b | landed | expert | `check-deltas` reads the diced design tree; the design's monolith retires |
| P1c | landed | expert | the diced-design lifecycle rule lands in the skill texts — development.py, guide.py, docdicer.py |
| P1d | landed | mechanical | the state-table reminder's sentence reworded at both harness resources |
| P2 | landed | expert | the activity profiler payload vendored and wired, its leaf created, the README credit |
| P3 | in progress | mechanical | the twelve SPEC delta entries applied to their leaves |
| P4 | dispatchable | mechanical | the fourteen remaining ARCHITECTURE delta entries applied to their leaves |
| P5 | drafted | expert | Post-plan review |
| P6 | drafted | expert | Post-plan burndown |

## P1 — The components selection replaces the plugin machinery

Implements [components and render](ACTIVE_DESIGN/code-delta/architecture-md-rendering-harnesses-and-families.md),
[the install entry](ACTIVE_DESIGN/code-delta/architecture-md-install-install-entry.md),
[install and runner lines](ACTIVE_DESIGN/code-delta/architecture-md-install-plugins.md),
[the settings key](ACTIVE_DESIGN/code-delta/spec-md-deployed-surfaces-plugins.md) and
[the agents file](ACTIVE_DESIGN/code-delta/architecture-md-agents-file.md).

Scope: `devpro/components.py` (new); `devpro/plugin.py` and `devpro/plugins/` (`__init__.py`,
`devpro.py`, `kbase.py`) deleted; `devpro/context.py`, `devpro/cli.py`, `devpro/render.py`,
`devpro/install.py`, `devpro/install_target.py`, `devpro/agents_file.py`,
`devpro/harnesses/mage.py`, `devpro/definitions/skills/guide.py`, `devpro/__init__.py` (its module
map's `plugin.py`/`plugins/` rows, `:17-18`, and its second copy of the CLI usage, `:40-45`, as well
as the `DEFAULT_PLUGIN` line the search names), `devpro/loading.py` (its docstring's
`plugins/`-among-the-instance-packages sentence, `:1-3`);
`devpro/kb-tools/runner-snippets/kb.just` and `kb.mk`; `devtools/scripts/_plugin-names.sh` deleted,
`_harness-value.sh`, `render.sh`, `_render-slot.sh`, `check-wheel.sh`, `render-agents-file.sh`
edited; the justfile's `install` and `install-agents-file` flag comments, the `render` recipe's
comment and doc line (`:122-129` — the slot-project sentence, the "every plugin is rendered"
statements, and the `--plugin`-refusal wording that retires with the refusal), and the two private
recipes' parameter lists — `_harness-value plugin harness key` → `harness key` (`:149`, which after
`_harness-value.sh` drops its first argument would otherwise pass the plugin name where the harness
name is read) and `render-agents-file harness out plugin=""` → without the plugin parameter
(`:145`); `README.md`; the tests and sites named below — the enumeration is complete for what the
fact-finding found, and `just test` is the authority on completeness: any pin it surfaces that the
list missed joins this package's work rather than stalling it.

**The selection.** `devpro/components.py` holds the optional components' member lists (`kbase`: the
`kbase` skill), the required set being every discovered definition no component names, with
`ships(name)`; member names validated against `discover()` (`devpro/definitions/__init__.py:46`,
`def discover()`), as a family is against its categories. Deleted:
`devpro/plugins/devpro.py:4`, quoted —

```python
PLUGIN = Plugin(name="devpro", exclude=frozenset({"kbase"}))
```

— and with it the whole include/exclude `Plugin` form (`devpro/plugin.py:17-46`),
`context.plugins()`/`context.plugin_named()` (`context.py:162-184`) and `DEFAULT_PLUGIN`
(`context.py:26`, quoted: `DEFAULT_PLUGIN = "devpro"`); the discovered-name validation moves into
the selection. `build_render` takes the components and `Render` carries the selection
(`context.py:319` `loaded_plugin = plugin_named(plugin)`, `context.py:332`,
`render.py:292`). `render.py:176` fills `PluginText.NAME` from the one name.

**The selection's shape.** The selection is the object `Render.plugin` holds, and no rename rides
with it: it answers the one name (`name`, constant `devpro`) and `ships(name)`, so the 13
`ctx.plugin` sites (`devpro/render.py` 7, `devpro/install.py` 5, `tests/test_devpro.py` 1) and
`bound_harness`'s `self.plugin.name` (`context.py:105`) change nothing, and
`resolve_install_target(..., plugin: str)` (`install_target.py:131,142`) keeps its parameter, fed
the selection's name. None of these sites greps as `plugin=`; they surface through
`ctx.plugin` and `.plugin.name`, which is why they are not in the searches above.

**The package docstrings.** `devpro/__init__.py`'s module map retargets the `plugin.py` and
`plugins/` rows (`:17-18`) to one `components.py` row, its second copy of the CLI usage (`:40-45`)
takes the components form, and the sentence beneath it ("The plugin is the name of a module in
`plugins/`, default `context.DEFAULT_PLUGIN`", `:46`) retires with the machinery it describes.
`devpro/loading.py`'s docstring (`:1-3`) names `plugins/` among the instance packages, which P1
deletes — the sentence re-words to the instance packages that remain.

**Mage's constant directory.** `devpro/harnesses/mage.py:35`, quoted
`project_harness_dir="{plugin}",` → the constant `"devpro"`; the `{plugin}` binding machinery
(`harness.py:244-274`) stays for the markers and prefixes.

**Every referencing file** of the retired names — the searches and their answers:

- `git grep -n -F 'DEFAULT_PLUGIN' -- devpro tests devtools` → `devpro/__init__.py:46`,
  `devpro/cli.py:18,62,73`, `devpro/context.py:26`; no test or devtools hit.
- `git grep -n -F 'plugin_named' -- devpro tests` → `devpro/cli.py:26,184,188,194`,
  `devpro/context.py:172,319`, `tests/test_plugins.py:14,39`.
- `git grep -n -F 'plugins()' -- devpro` → `devpro/agents_file.py:91`, `devpro/cli.py:61,64,192`,
  `devpro/context.py:176`.
- `git grep -n -F 'plugin=' -- devpro devtools tests` → `devpro/cli.py:138,160,175`,
  `devpro/context.py:332`, `devpro/definitions/skills/guide.py` (6 hits), `devpro/install.py:711`,
  `devpro/render.py:292`, `devpro/kb-tools/runner-snippets/kb.just:13`, `kb.mk:13`;
  `devtools/scripts/_harness-value.sh:11`, `_render-slot.sh` (1), `check-wheel.sh` (3),
  `render-agents-file.sh` (1), `render.sh` (2); `tests/test_devpro.py` (50),
  `test_devpro_install.py` (33), `test_install_target.py` (6), `test_kbase_surface.py` (1),
  `test_opencode_entry.py` (2), `test_plugins.py` (5), `test_cold_read_tools.py:72`.
- `git grep -n 'plugin' -- devpro/install_target.py` → `:47-58` (harness-dir-plugin machinery,
  unchanged) and `:131-142` — `resolve_install_target(..., plugin=...)`, quoted
  `def resolve_install_target(target: Path, *, harness: str | None, plugin: str, subdir: str | None) -> InstallTarget:`;
  the harness detection is selection-independent, `plugin` feeding only `Harness.bound` (`:142`).
- `git grep -n -F '_plugin-names' -- devtools` → `_render-slot.sh:22`, `check-wheel.sh:21`.
- `git grep -n -F 'PLUGIN_NAME' -- devpro tests` → `devpro/clauses.py:25` (the hole stays, filling
  the one name), `devpro/definitions/harness_agents_file.py:14`,
  `devpro/definitions/skills/guide.py:44,63,65,83,84,105,108`, `tests/test_devpro.py:881`.

**The CLI.** `_add_plugin` (`cli.py:58-65`, quoted: `choices=list(plugins()),` /
`default=DEFAULT_PLUGIN,`) becomes the `--components=CSV` parsing and validation — optional
components only, a required component (`development`, `docdicer`) not a legal value, `--components`
the hard override — and every `args.plugin` / `plugin=` call site retargets to it
(`cli.py:138,160,175,184,188,194`). The usage docstring `cli.py:73`
(`[--plugin=NAME]`, default `context.DEFAULT_PLUGIN`) takes the components form. The hidden
`plugins` verb retires (`cli.py:131`, `:192` quoted `print("\n".join(plugins()))`).
`install-agents-file` loses the flag (`cli.py:184`); `install_selected` (`cli.py:170-180`) passes
each named harness's settings value, `--components` given replacing it.

**The settings key.** `context.py`'s `[<harness>]` legal keys extend with `components` beside
`install` (`:31-32` quoted: `INSTALL_KEY = "install"` / `"""The one key a harness's `[<harness>]`
section carries."""`); the unknown-key refusal (`context.py:298-307`) names both keys; each named
harness's value drives that harness's install.

**Install and runner lines.** `install.py:465` filters `SHIPPED_PACKAGES` by the selection's
`ships(name)`; `runner_file.install_include_lines` writes the docdicer line always and the `kb`
line with the component on; `_install_managed_paths` (`install.py:579-580`) needs no change — it
already names every destination regardless of what ships. The kb-tools snippets' header comments
reword: the spelled paths become `.claude/skills/devpro/skills/kbase` and
`.opencode/plugins/devpro`, and the writer line retires — `kb.just:13`, quoted:

```sh
# The line is written by `devpro install . --plugin=kbase`, run from the consumer root — not
```

**The agents file.** `agents_file.py:91`, quoted
`return plugins().get(words[0]) if words else None`, and `_held_plugin` (`:331-335`) look the
marker word up in the one plugin name: a begin line whose first word is not `devpro` is a block of
no plugin, so a legacy `kbase`-stamped global block is replaced by the existing no-plugin rule
(`:276-285`) — no migration code.

**The scripts.** `_harness-value.sh:11`, quoted
`value="$(PYTHONPATH="${PROJECT_ROOT}" python3 -m "${GEN}" harness --plugin="${1}" "${2}" "${3}")"`
→ `harness NAME KEY`, no selection flag (its `:7` usage line drops the plugin argument); the hidden
`harness` verb binds the one plugin (`cli.py:194`), and `_render-slot.sh`'s two `_harness-value.sh`
call sites (`:40-41`) drop their first argument with it. `render.sh`'s refusal lines and flag
handling go (`render.sh:44-47`); the comments the flip falsifies re-word in place rather than dropping
wholesale — the "one slot project per plugin" sentence (`:9-12`), the flag-refusal paragraph
(`:30-31`), and the slot-contents comment (`:33-36`), which is the only statement in the tree of
what a slot project holds until P4 applies its delta: it re-anchors to the one slot project holding
the kb-tools package with the component on, the harness's MCP entry, and the runner include lines
(`render.sh:33-36`). `_render-slot.sh` writes `rendered/<slug>/devpro/` alone, one install with
`--components=kbase` (`:22-24` plugin_names loop, `:50-58` the per-plugin install and agents-file
calls — quoted
`"${PROJECT_ROOT}/devtools/scripts/render-agents-file.sh" "${harness}" "${agents_target}" "${plugin}"`).
`check-wheel.sh` runs one install with the component on and asserts `devpro/CLAUDE.md`
(`:21` plugin_names line, `:60-76` the per-plugin installs and the mage assertion).
`render-agents-file.sh` drops its `plugin_flag=()` block (`:14-17`) and its `--plugin` forwarding;
the third positional stays accepted and ignored — the header's version-skew rule (`:2-6`, quoted
`Its name and its arguments, HARNESS OUT [PLUGIN], never change incompatibly`) re-words to the same
guarantee without PLUGIN: a newer caller of an older copy passes nothing, and an older caller of a
newer copy passes `PLUGIN` where a third argument is read and dropped, so neither pairing breaks.

**The guide skill and README.** `guide.py`'s `--plugin={clauses.PLUGIN_NAME}` phrases (`:63,65,83,
105,108,184` — `:184` quoted `refused. Name the plugin as \`--plugin=NAME\`.`) take the components
form; `:84` "After installing the kbase plugin, restart Mage" takes the component wording.
`README.md`: `:104` (`devpro install ~/Mage/Skills --plugin=devpro --harness=mage`) takes
`--components=kbase`; `:107-110` becomes this text —

```
This writes `~/Mage/Skills/devpro/`. The install runs the `kbase` executable only with the kbase
component on (`--components=kbase`), and no devpro install provides or checks it: on macOS and
Linux, install it with `brew install benn-herrera/tap/kbase` (0.11.1 or later); native Windows is
unsupported for the component. Restart Mage after installing it.
```

— the one mage directory plus the component's toolchain statements, as SPEC.md, Deployed Surfaces,
Plugins and Guide and README state them; `:116` ("kbase plugin, restart Mage") and `:138`
("… the `kbase` plugin drives") take the component wording.

**Tests.** The flip changes stated behavior; these pins update in this package (each currently
passes, pinning the two-plugin shape, so the flip sends each red until rewritten):

- `tests/test_plugins.py` — split, per the design's Obviated code is deleted, not parked:
  deleted, because the form they pin is deleted (`devpro/plugin.py:17-46`), the include/exclude
  refusals (`:44-62`) and the by-exclusion/by-enumeration pins (`:65-72`); rewritten to the
  components shape, the kbase binding and guardrail marker (`:75-91`), the both-plugins' agents
  files (`:117-132`, becoming the one selection's agents files), and the both-plugins ×
  every-harness render (`:28-41`, becoming the component off/on matrix).
- `tests/test_devpro.py` — per-plugin MCP servers (`:633-655`), the KBASE-plugin mage render and
  manifest name (`:660-668`), the `mcp__plugin_kbase_kbase__query` pin (`:702`) →
  `mcp__plugin_devpro_kbase__query`, the KBASE-plugin render pins (`:1060-1103`); the module-level
  imports of the deleted modules (`:47-49`) and the `load("devpro.plugins", "PLUGIN")` sites
  (`:355,750,770,1705`) re-target `devpro.components`.
- `tests/test_devpro_install.py` — the DEVPRO/KBASE parametrized install contents (`:364-613`)
  becomes a components off/on matrix, the plugin inferred from `skills/kbase/SKILL.md` presence
  (`:658-669`), the `--plugin=kbase` CLI pins (`:698-715`) → `--components=kbase`; the module-level
  imports of the deleted modules (`:51-53,643-655`) and the `load("devpro.plugins", "PLUGIN")` site
  (`:654`) re-target; the `--plugin` grep hits `:555,1982,2000,2007,2042,2067,2085,2398` take the
  components form.
- `tests/test_install_target.py` — the plugin-bound path pins (`:45-52,91-93,211,217,274-280,310-335`);
  the module-level import of the deleted module (`:19`) re-targets; the `--plugin=nosuch` refusal
  pin (`:140`) keeps its refusal, its message changing to the components form.
- `tests/test_kbase_surface.py` — rendered "as the kbase plugin ships it" (`:33-40,193-203`) → with
  the component on; the module-level import of the deleted module (`:36`) re-targets.
- `tests/test_opencode_entry.py` — the real opencode install of kbase (`:28,54-77`) → with the
  component on (`:28` is both the import site and the pin).
- `tests/_structure.py:60-61` — `kbase_skill_output_paths`.
- `tests/test_cold_read_tools.py:72` — `build_render(harness="opencode", plugin="devpro", …)` →
  components.

The pin sources beyond `plugin=`: `git grep -n -- '--plugin' -- tests` returns the
`test_devpro_install.py` and `test_install_target.py:140` sites named above; the deleted modules'
import sites and `load("devpro.plugins", "PLUGIN")` sites are the ones named above.

Added pins, each naming the defect it fails on (current code):

- `--components=kbase` accepted on `render` and `install` and turning the component on — fails
  today: argparse refuses the unknown flag (`cli.py:58-65` adds only `--plugin`).
- an unknown component name refused, naming the optional components, and a required component
  (`development`) refused as not a legal value — fails today: no components validation exists.
- the settings file's `[<harness>]` `components` key read, its unknown-key refusal naming both
  keys, and `--components` the hard override — fails today: the key is refused as unknown
  (`context.py:298-307`).
- a legacy `kbase`-stamped global agents-file block reads as a block of no plugin and is replaced —
  fails today: `_held_plugin` (`:331-335`) holds it as the kbase plugin's.

Mage's constant directory needs no new pin: a mage devpro install already writes `devpro/CLAUDE.md`;
the rewritten `check-wheel.sh` assertion covers it.

Done-line: `just test` (all four surfaces — the flip touches the devpro package, the wheel check's
install path, and README, a top-level `*.md` that selects the docs surface), then `just lint`. One
commit.

## P1a — The six two-plugin CONVENTIONS leaves re-anchored to the components reality

The components flip falsifies six CONVENTIONS leaves, and no gate reads them for staleness: the tree
stays green while CONVENTIONS instructs an agent to edit a file P1 deleted. The design's final form
carries no CONVENTIONS delta (a change to CONVENTIONS.md is not one of a design's deltas), so this
package carries the re-anchoring itself: the restatements below are the change, written as judgment
prose under the accepted one-plugin-plus-components statements —
[components and render](ACTIVE_DESIGN/code-delta/architecture-md-rendering-harnesses-and-families.md)
and the entries it names — not enumerated byte-edits. Each leaf keeps its heading and its links: the
applied Repo Layout text P4 lands cites the plugin-membership rule by name
(`ACTIVE_DESIGN/architecture-delta/architecture-md-repo-layout.md:16,20`),
so the rule's home survives with the components form.

Each site, quoted as it stands and restated as it becomes:

- [Plugin membership has one home](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/plugin-membership-has-one-home.md)
  — the whole body, `:3-6`, quoted:

  ```
  A plugin's members are decided in one place in code, its module in `devpro/plugins/`, per definition
  name: the devpro plugin by exclusion, kbase by enumeration. No harness, install step, render or test holds a
  list of a plugin's members; each reads `Plugin.ships(name)`. A change to a plugin module changes
  SPEC.md, Deployed Surfaces, Plugins with it.
  ```

  becomes, restated over the components module:

  ```
  The definitions that ship are decided in one place in code, the member lists in
  `devpro/components.py`: the required set is every discovered definition no component names, the
  optional components' lists enumerate their members. No harness, install step, render or test holds
  a list of members; each reads the selection's `ships(name)`. A change to a member list changes
  SPEC.md, Deployed Surfaces, Plugins with it.
  ```

- [Where it goes](PROJECT_DOCS/CONVENTIONS/adding-definitions/where-it-goes.md), `:13-14`, quoted:

  ```
  A new definition joins the devpro plugin by existing. To also ship it in the kbase plugin, add it to
  SPEC.md, Deployed Surfaces, Plugins and to `devpro/plugins/kbase.py`.
  ```

  becomes:

  ```
  A new definition joins the devpro set by existing. To ship it with the kbase component, add it to
  SPEC.md, Deployed Surfaces, Plugins and to the kbase component's member list in
  `devpro/components.py`.
  ```

- [Agents file changes explicitly](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/agents-file-changes-explicitly.md),
  `:6-7`, quoted:

  ```
  Adopt with
  `just install-agents-file <dir> [--plugin=NAME] [--harness NAME]`, which replaces only the agents-file block
  between the `devpro` marker lines with that plugin's block and appends it to a file that has none.
  ```

  becomes the same sentence without the flag and without the second plugin's block:

  ```
  Adopt with `just install-agents-file <dir> [--harness NAME]`, which replaces only the agents-file
  block between the `devpro` marker lines and appends it to a file that has none.
  ```

- [Cross-references are placeholders](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/cross-references-are-placeholders.md),
  `:7-14`, both bullets, quoted in part:

  ```
  - **A plain reference must resolve in every plugin that ships its citing definition.** References
    close within the shipped set, so a plain reference to a definition outside a plugin refuses that
    plugin's render. Where the text does not need the out-of-plugin name, state the role instead of the
    name ("a security review's findings"), so the text holds in both plugins.
  ```

  ```
  - **An optional reference** is `clauses.optional_ref(name="development")`. … never one that shares
    its paragraph with a heading or text the other plugin keeps.
  ```

  becomes, restated over the shipped set and the component toggle: a plain reference must resolve in
  the install's shipped set — every definition no component leaves out, the components' members
  included — and where the text does not need the not-shipped name it states the role instead, so the
  text reads the same with the component off; an optional reference's paragraph is one that goes with
  the reference, holding nothing the render keeps with the component off. The second bullet's
  opening sentence (`clauses.optional_ref(name="development")` and how it fills) stands unchanged.

- [Install parameters ship with their flags](PROJECT_DOCS/CONVENTIONS/code-definitions-and-install/install-parameters-ship-with-their-flags.md),
  `:8`, quoted: the sentence's last clause, `the shape the plugin argument has.` →
  `the shape the components argument has.`
- [`render-diff` slots and output](PROJECT_DOCS/CONVENTIONS/planning-and-execution/render-diff-slots-and-output.md),
  `:7`, quoted:

  ```
  A slot holds a slot project per plugin (`rendered/<slot>/devpro/`, `rendered/<slot>/kbase/`),
  ```

  becomes: `A slot holds one slot project` with the one path `rendered/<slot>/devpro/` in its
  parens; the sentence's tail —
  `so a pair is a file at the same path below both slots, slot project included` — stands.

The six leaves were checked whole: outside the sites above, nothing in them speaks the two-plugin
shape — the review's cites are the complete set, and this package carries them all. The edits touch
no delta block (CONVENTIONS leaves are not the byte-check's source) and change no link, so
`check-deltas`' arithmetic and `check-links`' count are untouched by this package.

Scope: those six leaves, nothing else.

Done-line: `just check-links`. One commit.

## P1b — The delta byte-check reads the design's one source

Landed: `devtools/check_deltas.py` resolves a same-stem directory carrying `entry-point.md` beside
the design path and reads the tree in place of the document — each leaf one entry, its heading's
link resolved from the leaf's own directory — and the design's monolith (`ACTIVE_DESIGN.md`) retired
with it, the equivalence gate holding (88/2/89, the document read's counts). The design entry is
[CONVENTIONS.md, Planning and execution, A delta application ends verified](ACTIVE_DESIGN/code-delta/conventions-md-planning-and-execution-a-delta-application-ends-verified.md).

## P1c — The diced-design lifecycle rule lands in the skill texts

The design's decision — a diced design keeps no monolith beside its tree: the dice's passing exit
retires the monolith, and the tree is the design's one source from then on, both copies present
reported as a problem by `check-design` and `check-plan` — is recorded in
[CONVENTIONS.md, Planning and execution, A delta application ends verified](ACTIVE_DESIGN/code-delta/conventions-md-planning-and-execution-a-delta-application-ends-verified.md).
The skill and guide texts state the rule in pieces that do not agree today — the dicer's own skill
says both versions remain — so this package applies the drafted pairs to the definitions: the sentences the pairs change state
one rule. The docdicer skill's two undice bullets (`docdicer.py:23-35`) stay as written — they state
the tool's conversion machinery for any document (undice to a monolith, re-dice back, a failed
undice's monolith kept until the user directs removal), while D1's bullet governs the design's end
state and itself routes a revision through one working monolith, "leaving no monolith behind".
Process text is the plan's to carry, so the pairs below are the package's scope.

Scope: `devpro/definitions/skills/development.py`, `devpro/definitions/skills/guide.py`,
`devpro/definitions/skills/docdicer.py`. No test fixture pins these sentences (the standing-text
search over `tests/` returns only incidental hits; the definitions' own guards — the spelling rule
of `test_cross_references`, the router at `test_devpro.py:801` — were checked against the added text
and pass). Rendered slots follow by regeneration — `just render` for every slot but the four
reference slots (its slug rule refuses `reference*`, `justfile:125-126`), `just retake-reference`
for those four (`justfile:141`). Each pair was verified to match its site exactly once; the
executor re-runs the match on the live files before applying — a scratch script under
`.devpro-temp/` counting whole-text occurrences of each pair's first fenced block in its target
file, exactly one required (`grep -c` counts lines, not blocks). P1's guide.py edits (the
`--plugin` phrases) do not touch these sites, so the pairs survive P1. Three
constraints the application keeps: the added text names no skill outside a clause hole (the
cross-reference guard); `optional_ref` keeps its own paragraph, so no optional reference joins D1's
bullet; D1's bullet sits between the dice rule and the approved-plan rule, in that order.

**D1 — `development.py`, the bullet after the dice rule**

```
- A plan or design longer than the {PLAN_SIZE_LIMIT_TERM} when it is offered for approval is diced
  (the `{clauses.optional_ref(name="docdicer")}` skill), and dispatches cite its leaves. A design is
  diced at its `##` and `###` headings only, so each entry and each ticket is one file. Once approved,
  a plan is diced only when the user asks. *Purpose:* each executor reads whole the part it acts on.

- An approved plan runs to completion: blockers that need the user surface during planning.
```

becomes

```
- A plan or design longer than the {PLAN_SIZE_LIMIT_TERM} when it is offered for approval is diced
  (the `{clauses.optional_ref(name="docdicer")}` skill), and dispatches cite its leaves. A design is
  diced at its `##` and `###` headings only, so each entry and each ticket is one file. Once approved,
  a plan is diced only when the user asks. *Purpose:* each executor reads whole the part it acts on.

- A diced design keeps no monolith beside its tree: the dice's passing exit — the leaves reassembling
  the monolith, every link resolving — retires the monolith, and the tree is the design's one source
  from then on. Edit a diced design leaf by leaf, or undice it to one working monolith, edit that and
  re-dice the tree from it, leaving no monolith behind. *Purpose:* two copies diverge, and each
  reader takes a different text as the design.

- An approved plan runs to completion: blockers that need the user surface during planning.
```

**D2 — `development.py`, the {ACTIVE_DESIGN_TERM} row**

```
| {ACTIVE_DESIGN_TERM} | `ACTIVE_DESIGN.md` at the repository root | the one design under way, which feeds a plan |
```

becomes

```
| {ACTIVE_DESIGN_TERM} | `ACTIVE_DESIGN.md` at the repository root, else the `ACTIVE_DESIGN/` tree there, read from its `entry-point.md` | the one design under way, which feeds a plan |
```

**D3 — `guide.py`, the design's Appearing bullet**

```
- **Appearing:** `ACTIVE_DESIGN.md` at the root. While in progress it holds a `## Drafts` section:
  the requirements, decisions, constraints and open questions, one `###` ticket each. The session
  asks the user the open questions; each answer is the user's decision.
```

becomes

```
- **Appearing:** `ACTIVE_DESIGN.md` at the root, or the `ACTIVE_DESIGN/` tree that replaces it where
  the design is longer than the plan size limit. While in progress it holds a `## Drafts` section:
  the requirements, decisions, constraints and open questions, one `###` ticket each. The session
  asks the user the open questions; each answer is the user's decision.
```

**D4 — `guide.py`, a decision that changes the requirements**

```
- **A decision that changes the requirements**, an escalation's answer or the user's own, is entered
  in `ACTIVE_DESIGN.md` as an entry recording it and checked again, and may add a package to the
  plan; only the changed text is reviewed. Say it with its go: "Exports include refunds too. Update
  the design and the plan."
```

becomes

```
- **A decision that changes the requirements**, an escalation's answer or the user's own, is entered
  in the design — `ACTIVE_DESIGN.md`, or a leaf of its tree where it is diced — as an entry recording
  it and checked again, and may add a package to the plan; only the changed text is reviewed. Say it
  with its go: "Exports include refunds too. Update the design and the plan."
```

**D5 — `guide.py`, landing**

```
- **Landing:** one commit deletes `ACTIVE_PLAN.md` (or replaces it with the next plan),
  `ACTIVE_DESIGN.md` and `ACTIVE_PLAN_REVIEW.md`; its message says it lands a plan. **Next:** a new
  request or a roadmap ticket, or the periodic review where it is due.
```

becomes

```
- **Landing:** one commit deletes `ACTIVE_PLAN.md` (or replaces it with the next plan), the design
  (`ACTIVE_DESIGN.md` or its tree) and `ACTIVE_PLAN_REVIEW.md`; its message says it lands a plan.
  **Next:** a new request or a roadmap ticket, or the periodic review where it is due.
```

**G4 — `guide.py`, nothing under way**

```
- **No `ACTIVE_*` file:** nothing under way. Next: a request, a `ROADMAP.md` ticket or work in
  `ROADMAP_DESIGNS/`, unless the periodic review is due (`git log`: plans landed since the last
  periodic review).
```

becomes

```
- **No `ACTIVE_*` file or diced tree:** nothing under way. Next: a request, a `ROADMAP.md` ticket or
  work in `ROADMAP_DESIGNS/`, unless the periodic review is due (`git log`: plans landed since the
  last periodic review).
```

**G5 — `guide.py`, setting the work aside**

```
- **Setting the work aside** (*Plans*): "Set this work aside as orders-export." Every `ACTIVE_*` file
  moves into `ROADMAP_DESIGNS/` as `<topic>_DESIGN.md`, `<topic>_PLAN.md` and so on, and the plan
  drops its `Release:` line; the root is free for other work, and landed packages stay committed. It
  returns under its `ACTIVE_` names once no `ACTIVE_*` file is at the root: "Bring back
  orders-export." Dropped for good, it is abandoned and leaves `ROADMAP_DESIGNS/`.
```

becomes

```
- **Setting the work aside** (*Plans*): "Set this work aside as orders-export." Every `ACTIVE_*` file
  or diced tree moves into `ROADMAP_DESIGNS/` as `<topic>_DESIGN.md` or `<topic>_DESIGN/`,
  `<topic>_PLAN.md` and so on, and the plan drops its `Release:` line; the root is free for other
  work, and landed packages stay committed. It returns under its `ACTIVE_` names once no `ACTIVE_*`
  file or diced tree is at the root: "Bring back orders-export." Dropped for good, it is abandoned
  and leaves `ROADMAP_DESIGNS/`.
```

**G6 — `guide.py`, the roadmap's set-aside forms**

```
- `ROADMAP_DESIGNS/` holds work set aside, as `<topic>_DESIGN.md`, `<topic>_PLAN.md` and so on, and
  names no release.
```

becomes

```
- `ROADMAP_DESIGNS/` holds work set aside, as `<topic>_DESIGN.md` or `<topic>_DESIGN/`,
  `<topic>_PLAN.md` and so on, and names no release.
```

**B1 — `docdicer.py`, the dicer skill's own text.** The file is this repository's skill definition,
not the docdicer package: the fix rides this package so every text agrees, and the docdicer session's
work stays the tool-side check and the pin bump (the RFE names them).

```
- After each operation, both versions remain. Removing the one(s) no longer wanted is a separate step,
  taken at the user's direction.
```

becomes

```
- After each operation, both versions remain, apart from the active design's own monolith: a dice
  retires it, because the design lives in its tree from then on (the `{clauses.ref(name="development")}`
  skill, *Plans*). Removing any other one(s) no longer wanted is a separate step, taken at the user's
  direction.
```

Done-line: `just render`, then `just retake-reference`, then `just test`. One commit.

## P1d — The state-table reminder's sentence, one text in two resources

Implements [the reminder sentence](ACTIVE_DESIGN/code-delta/conventions-md-code-definitions-and-install-a-sentence-two-harness-resources-carry-is-one-text.md):
the sentence is one text in two harness resources and both sites change together. Current state,
verified — both sites carry the longer form, unchanged since the entry landed:

> Where the active plan carries a status table, a package is `in progress` when it is dispatched
> and `landed` when its work is accepted and committed.

The entry's shorter form replaces it:

> A package in the active plan's status table is `in progress` when dispatched, `landed` when
> accepted and committed.

— the shorter form chosen for brevity and so the injection does not elicit a reply from the session
it pokes. The tokens the tests hold (`status table`, `in progress`, `landed`) survive unchanged, so
no test edits; rendered and installed copies follow by regeneration — `just render` for every slot
but the four reference slots (its slug rule refuses `reference*`, `justfile:125-126`),
`just retake-reference` for those four (`justfile:141`).

Scope: `devpro/harnesses/resources/claude/hooks/state-table-reminder.sh` (the sentence, `:52`) and
`devpro/harnesses/resources/opencode/index.ts` (the sentence, `:107`), nothing else.

Done-line: `just render`, then `just retake-reference`, then `just test`. One commit.

## P2 — The activity profiler ships as payload

Implements [the profiler payload](ACTIVE_DESIGN/code-delta/architecture-md-install-harness-profiler.md),
[the README credit](ACTIVE_DESIGN/code-delta/spec-md-guide-and-readme.md), creates the leaf the
entry [ARCHITECTURE.md, Install, Harness profiler](ACTIVE_DESIGN/architecture-delta/architecture-md-install-harness-profiler.md)
states, and applies [ARCHITECTURE.md, entry point](ACTIVE_DESIGN/architecture-delta/architecture-md-entry-point.md).

Scope: `devpro/harnesses/resources/claude/libexec/hp.sh`, `hp.js`, `view.html` (vendored);
`devpro/harnesses/claude.py` (`_registration_hooks` and its builders); `devpro/definitions/skills/`
gains the `show-profile` definition; `README.md` (the credit line only);
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` (new leaf);
`PROJECT_DOCS/ARCHITECTURE/install/index.md` (its parent link line for the new leaf);
`PROJECT_DOCS/ARCHITECTURE/entry-point.md`; the two profiler entries' headings in their tree
leaves (`ACTIVE_DESIGN/architecture-delta/architecture-md-install-harness-profiler.md` and
`ACTIVE_DESIGN/code-delta/architecture-md-install-harness-profiler.md`); the pins land in
`tests/test_devpro_install.py`, the file that already
pins hooks.json, the harness resource copies and their banner.

**The resources.** Vendored from the harness-profiler source (upstream
`github.com/afurmanov/harness-profiler`, MIT) — the sibling checkout `../harness-profiler` holds it
(`ls ../harness-profiler/plugin/libexec` → `hp.js  hp.sh  view.html`, run this session); upstream is
the durable reference where the checkout is absent. Each file is copied as it stands and gains the
`!INSTALLED! … devpro` banner line within its first ten lines at vendoring — the banner rule binds
every harness resource (CONVENTIONS.md, Harness resources are copied verbatim), and its enforcement
is install-time, not render-time: the banner's regex pair (`install.py:154-156`) and the check that
refuses a target carrying an unbannered resource (`install.py:236-239`), the exact required shape
pinned by `tests/test_devpro_install.py:1699-1706`. The one-way copy rule applies.

**The wiring.** Data in `harnesses/claude.py`'s `_registration_hooks` (`:88-106`, quoted in part):

```python
    hooks["PostToolUse"] = [_hook_entry(matcher=_AGENT_MATCHER, command=_PLUGIN_REMINDER_COMMAND)]
    return hooks
```

The profiler's six entries join the guardrail's and the reminder's: `PostToolUse`,
`PostToolUseFailure`, `PreCompact`, `PostCompact`, `SessionStart`, `SubagentStop`, each
`matcher "*"`, `async: true`, `timeout: 5`, running
`sh "${CLAUDE_PLUGIN_ROOT}/libexec/hp.sh" capture claude`. No entry is gated on the install-time
probe.

**The skill.** A rendered definition, so it carries the generated banner and the harness namespace
(`devpro:show-profile` under claude) and renders under every harness; its finder's first candidate
is `../../libexec/hp.sh` (the upstream finder's candidate 1), resolving to
`<install-dir>/libexec/hp.sh` where the resources land; a user-level install renders the skill and
copies no resource; no opencode or mage install ships the resources or the hook entries.

**The leaf and its parent links.** `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` is
created with the content of the entry's fenced block, verbatim (the block carries no relative link
to rebase — read). Two parent links join it in the same commit: `PROJECT_DOCS/ARCHITECTURE/install/index.md`
gains the line for the new leaf, and `PROJECT_DOCS/ARCHITECTURE/entry-point.md`'s contents list gains
the `[Harness profiler](install/harness-profiler.md)` line between the opencode-entry and
installing-this-repository lines, per the entry — three edits, one commit. The reason is the parent
rule: `check-tree` makes a document's parent its directory's `index.md`
(`docdicer/…/treecheck.py:53-62`), so an unlinked new leaf fails `just check-links` via `check-tree`.

**The links.** The two `### ARCHITECTURE.md, Install, Harness profiler` headings — in the tree
leaves `ACTIVE_DESIGN/architecture-delta/architecture-md-install-harness-profiler.md` and
`ACTIVE_DESIGN/code-delta/architecture-md-install-harness-profiler.md`, quoted above — gain the leaf
link `(../../PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)`, so `check-deltas` resolves the
entries and the 2 PROBLEMs leave. The link changes no accepted wording. This is an edit to the
accepted design that changes no accepted wording — the design's own final form permits plain text
where the change creates it, and a link is that form's default; the alternative, relaxing
`check_deltas` to tolerate linkless entries for an entry that creates its leaf, was not taken.

**The credit.** README.md's Third Party Acknowledgments section gains exactly the design's credit
line ([the README credit] entry above) and nothing else records the origin — no version stamping
anywhere.

Added pins, each naming the defect it fails on (current code):

- the rendered claude `hooks/hooks.json` carries the six profiler entries beside the guardrail's and
  the reminder's — fails while the entries are absent: a hooks file missing an entry ships a claude
  install that records no activity of that kind.
- the three resources land under the install directory's `libexec/` — fails while the payload is
  absent. The banner half stays where it already lives,
  `test_every_shipped_resource_carries_the_header_its_reinstall_needs`
  (`tests/test_devpro_install.py:1695`): an unbannered vendored file fails that existing test, which
  is the coverage; this pin adds only the placement.
- `show-profile` renders under every harness — fails while the skill is absent.
- no opencode or mage install copies the resources or the hook entries — fails while a copy crosses
  harnesses.
- a user-level claude install renders the skill and copies no resource — fails while the resource
  copies reach a user-level install.

Done-line: `just test-changed` (the packaged resources sit under `devpro/`, which `TEST_SURFACE_MAP`
sends to both the `devpro` and the `wheel` surfaces, and README selects `docs` — the gates leaf's
target for the surfaces the change touches), then `just lint`, then `just check-links`, then
`just check-deltas` —
the named state it may leave: 87 not applied, 0 problems (the remaining misses are P3's and P4's
work). One commit.

## P3 — The SPEC delta entries applied

Scope: the twelve SPEC delta entries applied to their leaves. Each entry is the authority: replace
its before-text with its `becomes` block, byte-exact — `check-deltas` verifies the applied text as a
substring of the leaf, so no rewrap and no rebase is wanted. The only markdown link inside any SPEC
`becomes` block is `[Plugins](plugins.md)` (Install destination), already relative to its leaf.
Each package here changes only documents, so its checks are document checks.

| Entry | Leaf | blocks |
| --- | --- | --- |
| [Plugins](ACTIVE_DESIGN/spec-delta/spec-md-deployed-surfaces-plugins.md) | `PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md` | 11 |
| [Surfaces and layout](ACTIVE_DESIGN/spec-delta/spec-md-deployed-surfaces-surfaces-and-layout.md) | `PROJECT_DOCS/SPEC/deployed-surfaces/surfaces-and-layout.md` | 2 |
| [Install destination](ACTIVE_DESIGN/spec-delta/spec-md-deployed-surfaces-install-destination.md) | `PROJECT_DOCS/SPEC/deployed-surfaces/install-destination.md` | 4 |
| [Shipped files](ACTIVE_DESIGN/spec-delta/spec-md-deployed-surfaces-shipped-files.md) | `PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md` | 3 |
| [Installed tree](ACTIVE_DESIGN/spec-delta/spec-md-deployed-surfaces-installed-tree.md) | `PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md` | 4 |
| [Agents File](ACTIVE_DESIGN/spec-delta/spec-md-agents-file.md) | `PROJECT_DOCS/SPEC/agents-file.md` | 4 |
| [Rendering](ACTIVE_DESIGN/spec-delta/spec-md-rendering.md) | `PROJECT_DOCS/SPEC/rendering.md` | 3 |
| [Package and Command](ACTIVE_DESIGN/spec-delta/spec-md-package-and-command.md) | `PROJECT_DOCS/SPEC/package-and-command.md` | 2 |
| [Write Safety](ACTIVE_DESIGN/spec-delta/spec-md-write-safety.md) | `PROJECT_DOCS/SPEC/write-safety.md` | 1 |
| [Generated files](ACTIVE_DESIGN/spec-delta/spec-md-generated-files.md) | `PROJECT_DOCS/SPEC/generated-files.md` | 1 |
| [Plan Status Form](ACTIVE_DESIGN/spec-delta/spec-md-plan-status-form.md) | `PROJECT_DOCS/SPEC/plan-status-form.md` | 3 |
| [Guide and README](ACTIVE_DESIGN/spec-delta/spec-md-guide-and-readme.md) | `PROJECT_DOCS/SPEC/guide-and-readme.md` | 3 |

Done-line: `just check-deltas` — the named state it may leave: 46 not applied, 0 problems (the
ARCHITECTURE blocks P4 applies); then `just check-links`. One commit.

The Plugins row counts 11 because P3 applies 11: the entry's leaf carries 12 blocks in
`check-deltas`, one of them already applied in `PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md` — a
reader diffing the table against the tool sees 12 for that row.

## P4 — The ARCHITECTURE delta entries applied

Scope: the fourteen remaining ARCHITECTURE delta entries applied to their leaves (the profiler leaf,
its index line and the entry-point line landed in P2, so the entry-point entry is not P4's). Each
entry is the authority; the application is as P3's: byte-exact `becomes` blocks, no rebase wanted —
no ARCHITECTURE block carries a link that needs rebasing, the links they carry being already
leaf-relative: the entry-point block's three (`install/opencode-entry.md`,
`install/harness-profiler.md`, `install/installing-this-repository.md`), applied in P2, and Install
Plugins' `[Plugins](../../SPEC/deployed-surfaces/plugins.md)`.

| Entry | Leaf | blocks |
| --- | --- | --- |
| [Subsystem Map](ACTIVE_DESIGN/architecture-delta/architecture-md-subsystem-map.md) | `PROJECT_DOCS/ARCHITECTURE/subsystem-map.md` | 8 |
| [Repo Layout](ACTIVE_DESIGN/architecture-delta/architecture-md-repo-layout.md) | `PROJECT_DOCS/ARCHITECTURE/repo-layout.md` | 6 |
| [Install, Plugins](ACTIVE_DESIGN/architecture-delta/architecture-md-install-plugins.md) | `PROJECT_DOCS/ARCHITECTURE/install/plugins.md` | 5 |
| [Install, Install entry](ACTIVE_DESIGN/architecture-delta/architecture-md-install-install-entry.md) | `PROJECT_DOCS/ARCHITECTURE/install/install-entry.md` | 3 |
| [Install, Guardrail hook](ACTIVE_DESIGN/architecture-delta/architecture-md-install-guardrail-hook.md) | `PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md` | 2 |
| [Install, Renders and copies](ACTIVE_DESIGN/architecture-delta/architecture-md-install-renders-and-copies.md) | `PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md` | 1 |
| [Install, Opencode entry](ACTIVE_DESIGN/architecture-delta/architecture-md-install-opencode-entry.md) | `PROJECT_DOCS/ARCHITECTURE/install/opencode-entry.md` | 1 |
| [Install, Installing this repository](ACTIVE_DESIGN/architecture-delta/architecture-md-install-installing-this-repository.md) | `PROJECT_DOCS/ARCHITECTURE/install/installing-this-repository.md` | 1 |
| [Rendering, Harnesses and families](ACTIVE_DESIGN/architecture-delta/architecture-md-rendering-harnesses-and-families.md) | `PROJECT_DOCS/ARCHITECTURE/rendering/harnesses-and-families.md` | 7 |
| [Packaging](ACTIVE_DESIGN/architecture-delta/architecture-md-packaging.md) | `PROJECT_DOCS/ARCHITECTURE/packaging.md` | 2 |
| [Banner](ACTIVE_DESIGN/architecture-delta/architecture-md-banner.md) | `PROJECT_DOCS/ARCHITECTURE/banner.md` | 1 |
| [Agents File](ACTIVE_DESIGN/architecture-delta/architecture-md-agents-file.md) | `PROJECT_DOCS/ARCHITECTURE/agents-file.md` | 2 |
| [Why There Is No Verification Verb](ACTIVE_DESIGN/architecture-delta/architecture-md-why-there-is-no-verification-verb.md) | `PROJECT_DOCS/ARCHITECTURE/why-there-is-no-verification-verb.md` | 1 |
| [Recipes](ACTIVE_DESIGN/architecture-delta/architecture-md-recipes.md) | `PROJECT_DOCS/ARCHITECTURE/recipes.md` | 6 |

Done-line: `just check-deltas` — passing, `0 not applied, 0 problems`; then `just check-links`. One
commit.

## P5 — Post-plan review

The reviewers are the agent for each domain the plan changed substantively; each gets the project
documents and the design tree, not the plan, and reviews the changes and their tests against the
project's standards. Each writes their own review in the scratch directory, independently; the
session synthesizes them into `ACTIVE_PLAN_REVIEW.md`, never diced, de-duplicating findings and
reconciling them into one account.

- `python-coder` — the components selection, the render/install/agents-file/CLI changes, and the
  re-anchored Python tests;
- `shell-dsl-coder` — the devtools scripts and the vendored launcher's banner line;
- `architect` — the structure (one selection module beside `harness.py` and `family.py`, the
  harness binding), the CONVENTIONS re-anchoring, and the contract documents' claims about the code;
- `prompt-engineer` — the model-facing text: the guide skill's prose, the `show-profile` skill, and
  the applied contract leaves;
- `tech-writer` — the README's human-facing prose: the mage paragraph and the kbase component's
  toolchain sentences P1 authors (`README.md:107-110`), and the credit line's fit in the
  acknowledgments section.

Done-line: `just check-links`. One commit carries the review document, and its row lands with it.

## P6 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands. One commit closes the
package; the items cite their review IDs, grouped by root cause.

Done-line: the checkpoint gate (`just test`, then `just sweep-python`), then `just check-links`. One
commit; the commit that lands the plan follows it, deleting `ACTIVE_PLAN.md`,
`ACTIVE_PLAN_REVIEW.md` and the `ACTIVE_DESIGN/` tree.
