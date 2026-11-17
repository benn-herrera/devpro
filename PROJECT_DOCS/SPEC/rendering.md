## Rendering

A **model family** (`--family`) is a named group of models that assigns a model to each category and
may add tuning text at anchors (below). A **category map** assigns one model, the category's
**member**, to each of six **categories** — `stem-architect`, `stem-expert`, `stem-mechanical`,
`comm-architect`, `comm-expert`, `comm-mechanical` — the kind of work an agent does, `stem` (science,
technology, engineering, math) or `comm` (communication), joined with the difficulty of the work,
`architect`, `expert` or `mechanical`.

A definition's **base text** is its untuned text. An **anchor** is a named place in it where a
model family may add **tuning text**. Family-wide tuning text applies at every category. Member-scoped
tuning text applies only where the definition's category resolves to one named member.

Every rendering of the definitions in the deployed surfaces has five observable properties:

- **Single-sourcing.** Text shared across two or more definitions has exactly one source. Wherever
  a rendered definition shares text with another, that text is identical.
- **Kind membership.** Every definition of a kind carries the clauses that kind carries. An omission
  is admitted only where the definition is named with its reason, and a stale exemption is a defect.
- **No shared clause twice in one prompt.** No prompt delivers one shared clause, paragraph or list
  item twice. A prompt is one rendered definition taken together with the installed agents file, and
  for a command or skill also every rendered definition reached from it through `@<path>` lines,
  following on from each reached command or skill (an agent or supporting file reached loads
  nothing further); the agents file's own rendered definition is a prompt alone. The property covers a
  definition's base text; tuning text and the values a rendering or a clause fills into a definition
  — a directory name, a tool spelling, the agents-file name — are not held to it.
- **Additive-only tuning text.** A model family's tuning text may extend a definition's base text at
  anchors; it can never replace, suppress, or fork that text. A definition whose anchors the loaded
  family does not fill is byte-identical, below its banner, to its base text rendered under the same
  harness and category map. Base text may itself carry the step-down model: for an agent, the model
  its own discipline's mechanical category renders with — `stem-mechanical` for an agent whose
  category begins `stem-`, `comm-mechanical` for one whose category begins `comm-`; for a definition
  that declares no category, both disciplines' as `stem-mechanical=<model>, comm-mechanical=<model>`.
  A side whose member renders as the harness's **inherit text** — what the harness renders for
  `inherit` or a synonym it declares (an **inherit word**), which tells the harness to use the
  session's own model — is omitted, and where every side is, the step-down model appears nowhere. No
  family tuning text reaches it.
- **Tuning by category, recorded in the rendered definition.** Every agent definition declares a
  category, and the effective category map, the one model source on every harness, resolves it: the
  category's member is both what the definition is tuned against and the model it renders with. The
  category map comes from one of: the family; a harness's default category spec where it declares
  one; or whole from the **devpro settings file**'s `[<harness>-model-map]` section for the harness
  being rendered — a **category spec**, the text form of a category map, written in that section
  as one `<glob>=<model>` entry per line: each glob matched against the six category names and its
  `<model>` assigned to every category it matches, later entries silently overwriting earlier
  ones (`*=<model>` names all six; `*-architect=<model>` names both architect categories; a full
  category name names one), though a glob repeated in one section is refused, naming the line. An
  entry matching no category is refused, and a section leaving a category unnamed at its end is
  refused, with no fallback to the family.

  The devpro settings file is `~/.config/devpro/devpro.cfg`, or the file `--config-file` names;
  the path is taken as given — there is no search, the default path or the one named — and the
  default file's absence is no config at all, while an explicitly named file that does not exist
  is refused, naming the path. Its sections are named per harness: `[<harness>]` carries the
  harness's settings, its `install` value among them (SPEC.md, Install destination);
  `[<harness>-model-map]` carries its model map. A section that is neither a supported harness's
  `[<harness>]` nor its `[<harness>-model-map]` — a `[DEFAULT]` section holding entries among
  them — is refused, naming the section and the supported harnesses; a key in a settings section
  that is no setting of it is refused, naming the map section it belongs in; a file that does not
  parse is refused before anything is written, naming the file and the line. A harness declares the
  model shape a rendered model must have — a model outside it fails rendering before anything is
  written, naming the category, the value, and the settings-file entry, the harness default, or the
  family that supplied it — and the text each of
  its inherit words renders as, `inherit` among them; an empty rendering leaves the definition
  without a model line. Every rendered definition's tuning line, its `!TUNING!` line, records the
  family's name, the definition's category and that category's member (each `none` for a definition
  that declares no category), the effective category map, the categories whose member the family has
  no member-scoped tuning text for (as `stock=`), and the harness it was rendered for, so what it is
  tuned for and what it dispatches on are readable from the definition alone. Documents, commands
  and skills declare no category and stand outside this resolution; family-wide tuning text still
  fills their anchors. A family whose member-scoped tuning text names a member no category reaches
  — in neither its own category map nor the effective category map — is refused before anything is
  rendered.

A cross-definition reference renders with the plugin's namespace under the harness: under claude and
mage `<plugin>:<name>` for an agent, a command or a skill, and under opencode `<plugin>-<name>`.
Apart from the plugin's name and the namespace it gives references, text differs between plugins only
by an optional reference's paragraph being present or absent.

References close within the shipped set, the definitions the render's plugin carries. A render in
which a definition refers to one outside that set is refused,
naming the definition that refers and the one it refers to, and nothing is written. An **optional
reference** is the one exception: where its referent does not ship, the paragraph holding it is
dropped whole, and the rest of the definition is unchanged.

An install renders the definitions under the tuning arguments it was given and the devpro settings
file, where it supplies entries; Generated files, below, holds whatever they are.

