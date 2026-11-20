### Harnesses and families

A harness is a `Harness` dataclass (`devpro/harness.py`) holding everything that differs between
harnesses: the seven harness strings, typed `HarnessText` — `HarnessText.MCP_TOOL_PREFIX` among
them, `mcp__plugin_{plugin}_kbase__` under claude, `mcp_kbase_` under mage and `kbase_` under
opencode, a server tool's offered name being that prefix plus the tool's own, `display_name`, the
harness's name in prose, lowercase (`claude code`, `opencode`, `mage`) and refused otherwise, and
`scratch_rule` and `memory_file`, the agents file's rule for where scratch goes and its name for the
operator's own instructions file (Placeholders); the six
harness-specific paragraphs, typed `OptionalHarnessText` — `recipe_rule`, `kbase_project_rule`
(supplied under mage alone, whose server is started `--project-dir-required`), `reload_rule`
(supplied under claude alone: the sentence a claude install prints and the `guide` skill's
installation reference carries), `tools_reload_rule` (supplied under claude alone: the sentence the
`kbase` skill entry file and installation reference carry),
`side_by_side_rule` (supplied under opencode alone, in its own
paragraph of that reference) and `cold_read_rule` (supplied under every harness: claude and opencode share
`harness.COLD_READ_SCRIPT_RULE`, which runs `cold-read.sh`, opencode adding that the script is not yet
reliable there, and mage, whose copy of the script refuses to run, says to start the reader by
hand);
the tool spellings, the model shape it accepts, the text `inherit` renders as
(`inherit_text`) with the further `inherit_synonyms` rendering that same text, whether a bare
category spec is the whole map (`bare_category_spec_is_all`), and `definition_form`, where a
definition's
metadata goes. `definition_form` is exactly one of two values, so a harness with both or neither is
not representable and nothing checks for one: a `FrontmatterForm`, the emitter of the agent
fields and document fields between the frontmatter fences (claude, mage), or a `HarnessFile`, the
registry builder (opencode). Under opencode a definition's metadata is not frontmatter: the harness
renders one registry, `registry.json`, from the same `AgentFields` the claude and mage emitters read,
and a copied entry, `index.ts`, registers the plugin's bodies from it at run time. Opencode has no
directory layout that holds a plugin in one directory under prefixed names; an opencode plugin module's transforms
do. The registry's layout is `devpro/harnesses/opencode.py`'s, the wire format it owns, and the
entry parses nothing but JSON; `render.py` hands the builder a general-form list of what it
rendered (`ShippedDefinition`: name, reference, kind, output path, filled
description, and `AgentFields` for an agent) and shapes no harness's wire format. Under opencode
`render._comment_banner` replaces the frontmatter for every output, a definition's own included.

A harness's `kbase` MCP entry is a builder (`McpEntryBuilder`) that takes the command. Claude and mage hand theirs to `harness.mcp_json`, which
makes `.mcp.json`, a `HarnessFile` owned by `kbase`; opencode's registry builder calls its own for
the record `registry.json` carries (Install, Plugins).

The remaining fields: `guardrail`
(`GuardrailHook` or `None`), the hook script and the registration file beside it that a claude
install writes (Install); `rendered_files` (`HarnessFile`), the harness-rendered files beside the
definitions, each with a `marker` and an optional `owner` — the plugin manifest,
`harness.PLUGIN_MANIFEST`, one value claude and mage share, version included, and `.mcp.json`;
`plugin_dir`, the path below the harness directory the install product is written into
(`skills/{plugin}` under claude, `plugins/{plugin}` under opencode; empty under mage, so its install
directory is the harness directory); `reference_prefix`, put before a definition's name wherever
definition text names it (`{plugin}:` under claude and mage, `{plugin}-` under opencode);
`project_harness_dir` (`{plugin}` under mage); `entry_resource`, the resource that registers the plugin
and is copied at user level too (opencode's `index.ts`; empty elsewhere); `user_plugin_shadows`,
whether a user-level install's plugin loads in place of a project's of its name (claude alone); `default_category_spec`, the default category spec, used when the devpro settings file
supplies none (`None`: the family's map; opencode's is `default` and mage's is `*=inherit`, read by
`build_render`); and
`plugin_parent_dir`, a harness-directory plugin's trailing path of the directory its plugins sit in (`Mage/Skills`;
empty otherwise), by which install target detection knows a target that is such a
plugin's harness directory. Whether a harness is a harness-directory plugin is
`Harness.is_harness_dir_plugin`, `user_harness_dir == "."`.

The values that vary by plugin are templates over `{plugin}`: `plugin_dir`,
`reference_prefix`, `mcp_tool_prefix`, and each rendered file's and the registry's `marker`; mage's
`project_harness_dir` is the constant `devpro`.
`Harness.bound(plugin_name)` fills them once with `str.replace`, not `str.format`, and takes the name
as a string, so a harness stays a value that knows no member lists and `harness.py` never
imports `components.py`. `Render.harness` is the harness as given, templates unfilled;
`Render.bound_harness`, a `functools.cached_property`, is that harness bound to the render's plugin,
and a reader that needs a bound value reads it there. Binding again starts from the templates, so a
bound harness never holds another binding's values. Harness detection
(`install_target._detected_harness`) reads only plugin-independent values, so it runs before
binding. The manifest's `name`, both prefixes, the install directory and the MCP prefix are each derived from the
plugin's name. `inherit_synonyms` and `bare_category_spec_is_all` differ between claude and
opencode, as the harness strings above do: opencode holds
`("default",)` and `True`, with `inherit_text` empty; claude holds `()` and `False`,
`inherit_text` `inherit`, and refuses a bare category spec as no `<glob>=<model>` entry. Mage reads the shared
frontmatter emitter (`agent_frontmatter`) and recipe rule (`FOREGROUND_RECIPE_RULE`) from
`harness.py`, and holds claude's other assumed values (model pattern, aliases, tool spellings) as
copies it may revise independently.

**Plugins.** The selection is one module, `devpro/components.py`: the member lists of the optional
components and the required set — every discovered definition no component names — with `ships(name)`.
`selection()` validates a list against `discover()`, as a family is against its categories, and
`build_render` calls it for every render. It is imported by `context` beside `harness.py` and
`family.py`. The selection is a selection of definitions and no profile of its own.

A family is a
`Family` dataclass (`devpro/family.py`) holding the category map and the tuning text by anchor. An
instance is one module, in `devpro/harnesses/` or `devpro/families/`,
defining `HARNESS` or `FAMILY`, with no class in it. A harness or family is registered by its module existing, with no
list to keep: a registry that could fall out of step with the modules is not representable.
`loading.load` reads the modules of a package in name order and
keys each by its module name with `_` read as `-` (`gemma_4.py` is `gemma-4`). The constructor is
the validator: an instance missing a field, or a family not staffing exactly the six categories,
fails at import. The `Render` record (`devpro/context.py`) carries the harness, the selection, the family
and the invocation's category map, and resolves a category to its rendered model text and an anchor
to its tuning text: a category whose text is `inherit` or a synonym becomes `inherit_text`. The
map's suppliers, in the order `build_render` applies them:

1. the devpro settings file's `[<harness>-model-map]` section for the harness — its keys, one
   entry per line under the grammar, joined for the parser; read and validated by
   `devpro/context.py`.
2. the harness's `default_category_spec` — the bare reading's remaining home (a non-empty value
   holding neither `=` nor `,` is the whole map where the harness reads it so), where the harness
   declares one.
3. the family's own map.

`Render` carries the selection — the plugin and the components turned on — and `Render.bound_harness`
binds the harness to the plugin, so the bound values a render reads are always its own and no
mismatch is representable. `build_render(…, components=)` validates
every member name against `discover()`, because a misspelled
member would otherwise drop out of the contents SPEC states and nothing else would
notice. The selection's `ships(name)` is the one filter.
`Render.step_down_model` is the step-down model text: for a definition that declares a category, its
own discipline's mechanical member's rendered text — `stem-mechanical` for a category beginning
`stem-`, `comm-mechanical` for one beginning `comm-`; for a definition that declares none, both
disciplines' as `stem-mechanical=<text>, comm-mechanical=<text>`. A side whose member renders as the
harness's `inherit_text` is omitted, and the value is empty — the placeholder's paragraph drops —
where every side is. It is the one value behind the `tun` placeholder (Placeholders).
