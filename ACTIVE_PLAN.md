# Active plan — one devpro plugin with optional components; the activity profiler ships as payload

From the accepted design, diced: [ACTIVE_DESIGN/entry-point.md](ACTIVE_DESIGN/entry-point.md) — 36
entries under `spec-delta/`, `architecture-delta/` and `code-delta/`; the monolith `ACTIVE_DESIGN.md`
stands beside the tree as the delta byte-check's source. Every package is **shipped**: the whole
process, one commit closing each package.

Sequencing: P1, then P2, then P3, then P4, then P5, then P6. Each package leaves the tree green. P1
carries every CLI caller and every test pin the components flip breaks. From P1 until P4 lands, the
contract leaves still describe the two-plugin world while the code runs one-plugin-plus-components —
no runner target compares the documents' claims to the code, so the gates stay green across that
gap; the plan names the gap here rather than leaving it unspoken.

The delta byte-check (`just check-deltas`) today exits 1 with 88 `becomes` blocks not applied and 2
problems — the two `Harness profiler` entries' headings name no target leaf (`ACTIVE_DESIGN.md:1191`
and `:1307`), so the check cannot find one. P2 adds the two links when it creates the profiler leaf
(the check cannot resolve the entry without one, and a heading link changes no accepted wording),
leaving 0 problems and 87 not applied; P3 applies every SPEC delta block; P4 every remaining
ARCHITECTURE delta block; from P4 the run reports `0 not applied, 0 problems` and exits 0.

## Status

| Package | State | Rating | Changes |
| --- | --- | --- | --- |
| P1 | drafted | expert | the components selection replaces the plugin machinery — code, CLI callers, README, every pin |
| P2 | drafted | expert | the activity profiler payload vendored and wired, its leaf created, the README credit |
| P3 | drafted | mechanical | the twelve SPEC delta entries applied to their leaves |
| P4 | drafted | mechanical | the fourteen remaining ARCHITECTURE delta entries applied to their leaves |
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
`devpro/harnesses/mage.py`, `devpro/definitions/skills/guide.py`, `devpro/__init__.py`;
`devpro/kb-tools/runner-snippets/kb.just` and `kb.mk`; `devtools/scripts/_plugin-names.sh` deleted,
`_harness-value.sh`, `render.sh`, `_render-slot.sh`, `check-wheel.sh`, `render-agents-file.sh`
edited; the justfile's `install` and `install-agents-file` flag comments; `README.md`; the tests
named below.

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
`install` (`:30-31` quoted: `INSTALL_KEY = "install"` / `"""The one key a harness's `[<harness>]`
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
`harness` verb binds the one plugin (`cli.py:194`). `render.sh` drops its `--plugin` refusal and its
"renders every plugin" comment (the refusal quoted:
`printf '%s\n' "error: render renders every plugin; --plugin is not accepted" >&2`).
`_render-slot.sh` writes `rendered/<slug>/devpro/` alone, one install with `--components=kbase`
(`:22-24` plugin_names loop, `:50-58` the per-plugin install and agents-file calls — quoted
`"${PROJECT_ROOT}/devtools/scripts/render-agents-file.sh" "${harness}" "${agents_target}" "${plugin}"`).
`check-wheel.sh` runs one install with the component on and asserts `devpro/CLAUDE.md`
(`:21` plugin_names line, `:60-76` the per-plugin installs and the mage assertion). 
`render-agents-file.sh` drops its third positional and its `plugin_flag=()` block (`:5-12,15+`).

**The guide skill and README.** `guide.py`'s `--plugin={clauses.PLUGIN_NAME}` phrases (`:63,65,83,
105,108,184` — `:184` quoted `refused. Name the plugin as \`--plugin=NAME\`.`) take the components
form; `:84` "After installing the kbase plugin, restart Mage" takes the component wording.
`README.md`: `:104` (`devpro install ~/Mage/Skills --plugin=devpro --harness=mage`) takes
`--components=kbase`; `:107-110` (`--plugin=kbase` writes `~/Mage/Skills/kbase/` …) retires into the
one mage directory and the kbase component's toolchain statements, as SPEC.md, Guide and README
states them; `:116` ("kbase plugin, restart Mage") and `:138` ("… the `kbase` plugin drives") take
the component wording.

**Tests.** The flip changes stated behavior; these pins update in this package (each currently
passes, pinning the two-plugin shape, so the flip sends each red until rewritten):

- `tests/test_plugins.py` — rewritten to the components shape: the include/exclude refusals
  (`:44-62`), the by-exclusion/by-enumeration pins (`:65-72`), the kbase binding and guardrail
  marker (`:75-91`), the both-plugins' agents files (`:117-132`), the both-plugins × every-harness
  render (`:28-41`).
- `tests/test_devpro.py` — per-plugin MCP servers (`:633-655`), the KBASE-plugin mage render and
  manifest name (`:660-668`), the `mcp__plugin_kbase_kbase__query` pin (`:702`) →
  `mcp__plugin_devpro_kbase__query`, the KBASE-plugin render pins (`:1060-1103`).
- `tests/test_devpro_install.py` — the DEVPRO/KBASE parametrized install contents (`:364-613`)
  becomes a components off/on matrix, the plugin inferred from `skills/kbase/SKILL.md` presence
  (`:658-669`), the `--plugin=kbase` CLI pins (`:698-715`) → `--components=kbase`.
- `tests/test_install_target.py` — the plugin-bound path pins (`:45-52,91-93,211,217,274-280,310-335`).
- `tests/test_kbase_surface.py` — rendered "as the kbase plugin ships it" (`:33-40,193-203`) → with
  the component on.
- `tests/test_opencode_entry.py` — the real opencode install of kbase (`:28,54-77`) → with the
  component on.
- `tests/_structure.py:60-61` — `kbase_skill_output_paths`.
- `tests/test_cold_read_tools.py:72` — `build_render(harness="opencode", plugin="devpro", …)` →
  components.

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
install path, and no document), then `just lint`. One commit.

## P2 — The activity profiler ships as payload

Implements [the profiler payload](ACTIVE_DESIGN/code-delta/architecture-md-install-harness-profiler.md),
[the README credit](ACTIVE_DESIGN/code-delta/spec-md-guide-and-readme.md), creates the leaf the
entry [ARCHITECTURE.md, Install, Harness profiler](ACTIVE_DESIGN/architecture-delta/architecture-md-install-harness-profiler.md)
states, and applies [ARCHITECTURE.md, entry point](ACTIVE_DESIGN/architecture-delta/architecture-md-entry-point.md).

Scope: `devpro/harnesses/resources/claude/libexec/hp.sh`, `hp.js`, `view.html` (vendored);
`devpro/harnesses/claude.py` (`_registration_hooks` and its builders); `devpro/definitions/skills/`
gains the `show-profile` definition; `README.md` (the credit line only);
`PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` (new leaf);
`PROJECT_DOCS/ARCHITECTURE/entry-point.md`; the two profiler entries' headings in `ACTIVE_DESIGN.md`
and their two tree leaves; tests.

**The resources.** Vendored from the harness-profiler source (upstream
`github.com/afurmanov/harness-profiler`, MIT) — the sibling checkout `../harness-profiler` holds it
(`ls ../harness-profiler/plugin/libexec` → `hp.js  hp.sh  view.html`, run this session); upstream is
the durable reference where the checkout is absent. Each file is copied as it stands and gains the
`!INSTALLED! … devpro` banner line within its first ten lines at vendoring — the banner rule binds
every harness resource (CONVENTIONS.md, Harness resources are copied verbatim; the render-time check
is `install.py:154-156,188-193`). The one-way copy rule applies.

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

**The leaf and the entry-point line.** `PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md` is
created with the content of the entry's fenced block, verbatim (the block carries no relative link
to rebase — read). `PROJECT_DOCS/ARCHITECTURE/entry-point.md`'s contents list gains the
`[Harness profiler](install/harness-profiler.md)` line between the opencode-entry and
installing-this-repository lines, per the entry — `check-tree` fails on an unlisted document, so
the two edits land in one commit.

**The links.** The two `### ARCHITECTURE.md, Install, Harness profiler` headings
(`ACTIVE_DESIGN.md:1191` and `:1307`, quoted above) gain the leaf link —
`(PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)` in the monolith,
`(../../PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md)` in the tree leaves
`ACTIVE_DESIGN/architecture-delta/architecture-md-install-harness-profiler.md` and
`ACTIVE_DESIGN/code-delta/architecture-md-install-harness-profiler.md` — so `check-deltas` resolves
the entries and the 2 PROBLEMs leave. The link changes no accepted wording; both sides are edited so
the monolith and its tree stay one document.

**The credit.** README.md's Third Party Acknowledgments section gains exactly the design's credit
line ([the README credit] entry above) and nothing else records the origin — no version stamping
anywhere.

Added pins, each naming the defect it fails on (current code):

- the rendered claude `hooks/hooks.json` carries the six profiler entries beside the guardrail's and
  the reminder's — fails while the entries are absent: a hooks file missing an entry ships a claude
  install that records no activity of that kind.
- the three resources land under the install directory's `libexec/`, each bannered — fails while the
  payload is absent or an unbannered file is vendored (the banner check then refuses the render).
- `show-profile` renders under every harness; no opencode or mage install copies the resources or
  the hook entries; a user-level claude install renders the skill and copies no resource — fails
  while the skill is absent or the copies cross harnesses.

Done-line: `just test devpro`, then `just lint`, then `just check-links`, then `just check-deltas` —
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

## P4 — The ARCHITECTURE delta entries applied

Scope: the fourteen remaining ARCHITECTURE delta entries applied to their leaves (the profiler leaf
and the entry-point line landed in P2). Each entry is the authority; the application is as P3's:
byte-exact `becomes` blocks, no rebase wanted — the one link inside an ARCHITECTURE block
(`[Plugins](../../SPEC/deployed-surfaces/plugins.md)`, Install, Plugins) is already leaf-relative.

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
  harness binding) and the contract documents' claims about the code;
- `prompt-engineer` — the model-facing text: the guide skill's prose, the `show-profile` skill, and
  the applied contract leaves.

No tech-writer seat: README's changes are the credit line and the flag and mage re-anchoring
SPEC.md, Guide and README already states — not substantive.

Done-line: `just check-links`. One commit carries the review document, and its row lands with it.

## P6 — Post-plan burndown

Drafted from `ACTIVE_PLAN_REVIEW.md` once the post-plan review lands. One commit closes the
package; the items cite their review IDs, grouped by root cause.

Done-line: the checkpoint gate (`just test`, then `just sweep-python`), then `just check-links`. One
commit; the commit that lands the plan follows it, deleting `ACTIVE_PLAN.md`,
`ACTIVE_PLAN_REVIEW.md`, `ACTIVE_DESIGN.md` and the `ACTIVE_DESIGN/` tree.
