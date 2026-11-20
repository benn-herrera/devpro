### Where it goes

One module in `devpro/definitions/`, `devpro/definitions/agents/` or `devpro/definitions/skills/`; its
existence is its enrollment, and nothing imports it by name. A module is registered by existing under
`devpro/definitions/`; discovery walks every subpackage there. Definitions that ship together share
one group module.

A module sits in the folder of the kind its definitions render: an agent's in `agents/`, a skill's in
`skills/`, the agents file's at the top beside the package's shared code. A module of any other kind
stays at the top until a rule places it. Its name comes from its output path, not from its folder
(What it is called).

A new definition joins the devpro set by existing. To ship it with the kbase component, add it to
SPEC.md, Deployed Surfaces, Plugins and to the kbase component's member list in
`devpro/components.py`.
