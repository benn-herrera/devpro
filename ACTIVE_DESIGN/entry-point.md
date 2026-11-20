# One devpro plugin with optional components; the activity profiler ships as payload

devpro installs one plugin, the devpro plugin, carrying every definition the project ships, and the
kbase plugin retires: what only it delivered rides as the optional `kbase` component, turned on per
install by a `--components` CSV or the settings file's per-harness `components` key, so a project
that opts into the knowledge-base process carries it beside the full development process, and one
that does not never sees the kbase skill, its MCP server or its tools. Every claude project install
also ships the activity profiler as payload — the harness-profiler plugin's source vendored under
its MIT licence and credited in README.md — recording skill, agent and tool activity through six
hooks and rendering it through the `show-profile` skill. Consuming projects get one install
directory, one namespace and one set of MCP tool names per harness; the project gets one membership
home, one mage directory and one slot project per render slot.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The
summary text is not to be consistency checked. The design is authoritative.

Contents:

- [SPEC delta](spec-delta/index.md)
  - [SPEC.md, Deployed Surfaces, Plugins](spec-delta/spec-md-deployed-surfaces-plugins.md)
  - [SPEC.md, Deployed Surfaces, Surfaces and layout](spec-delta/spec-md-deployed-surfaces-surfaces-and-layout.md)
  - [SPEC.md, Deployed Surfaces, Install destination](spec-delta/spec-md-deployed-surfaces-install-destination.md)
  - [SPEC.md, Deployed Surfaces, Shipped files](spec-delta/spec-md-deployed-surfaces-shipped-files.md)
  - [SPEC.md, Deployed Surfaces, Installed tree](spec-delta/spec-md-deployed-surfaces-installed-tree.md)
  - [SPEC.md, Agents File](spec-delta/spec-md-agents-file.md)
  - [SPEC.md, Rendering](spec-delta/spec-md-rendering.md)
  - [SPEC.md, Package and Command](spec-delta/spec-md-package-and-command.md)
  - [SPEC.md, Write Safety](spec-delta/spec-md-write-safety.md)
  - [SPEC.md, Generated files](spec-delta/spec-md-generated-files.md)
  - [SPEC.md, Plan Status Form](spec-delta/spec-md-plan-status-form.md)
  - [SPEC.md, Guide and README](spec-delta/spec-md-guide-and-readme.md)
- [ARCHITECTURE delta](architecture-delta/index.md)
  - [ARCHITECTURE.md, Subsystem Map](architecture-delta/architecture-md-subsystem-map.md)
  - [ARCHITECTURE.md, Repo Layout](architecture-delta/architecture-md-repo-layout.md)
  - [ARCHITECTURE.md, Install, Plugins](architecture-delta/architecture-md-install-plugins.md)
  - [ARCHITECTURE.md, Install, Install entry](architecture-delta/architecture-md-install-install-entry.md)
  - [ARCHITECTURE.md, Install, Guardrail hook](architecture-delta/architecture-md-install-guardrail-hook.md)
  - [ARCHITECTURE.md, Install, Renders and copies](architecture-delta/architecture-md-install-renders-and-copies.md)
  - [ARCHITECTURE.md, Install, Opencode entry](architecture-delta/architecture-md-install-opencode-entry.md)
  - [ARCHITECTURE.md, Install, Installing this repository](architecture-delta/architecture-md-install-installing-this-repository.md)
  - [ARCHITECTURE.md, Rendering, Harnesses and families](architecture-delta/architecture-md-rendering-harnesses-and-families.md)
  - [ARCHITECTURE.md, Packaging](architecture-delta/architecture-md-packaging.md)
  - [ARCHITECTURE.md, Banner](architecture-delta/architecture-md-banner.md)
  - [ARCHITECTURE.md, Agents File](architecture-delta/architecture-md-agents-file.md)
  - [ARCHITECTURE.md, Why There Is No Verification Verb](architecture-delta/architecture-md-why-there-is-no-verification-verb.md)
  - [ARCHITECTURE.md, Recipes](architecture-delta/architecture-md-recipes.md)
  - [ARCHITECTURE.md, entry point](architecture-delta/architecture-md-entry-point.md)
  - [ARCHITECTURE.md, Install, Harness profiler](architecture-delta/architecture-md-install-harness-profiler.md)
- [Code delta](code-delta/index.md)
  - [ARCHITECTURE.md, Rendering, Harnesses and families](code-delta/architecture-md-rendering-harnesses-and-families.md)
  - [ARCHITECTURE.md, Install, Install entry](code-delta/architecture-md-install-install-entry.md)
  - [ARCHITECTURE.md, Install, Plugins](code-delta/architecture-md-install-plugins.md)
  - [SPEC.md, Deployed Surfaces, Plugins](code-delta/spec-md-deployed-surfaces-plugins.md)
  - [ARCHITECTURE.md, Agents File](code-delta/architecture-md-agents-file.md)
  - [ARCHITECTURE.md, Why There Is No Verification Verb](code-delta/architecture-md-why-there-is-no-verification-verb.md)
  - [ARCHITECTURE.md, Install, Harness profiler](code-delta/architecture-md-install-harness-profiler.md)
  - [SPEC.md, Guide and README](code-delta/spec-md-guide-and-readme.md)
  - [CONVENTIONS.md, Code definitions and install, A sentence two harness resources carry is one text](code-delta/conventions-md-code-definitions-and-install-a-sentence-two-harness-resources-carry-is-one-text.md)
  - [CONVENTIONS.md, Planning and execution, A delta application ends verified](code-delta/conventions-md-planning-and-execution-a-delta-application-ends-verified.md)
