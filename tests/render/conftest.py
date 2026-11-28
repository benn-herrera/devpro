"""Shared helpers and fixtures for the render tests: the inherit selection, the prefixed harnesses, the claude render, and the skill and agent definitions."""

import ast
import dataclasses
import importlib.util
import inspect
import re
import sysconfig
import types
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import pytest

import devpro
import devpro.clauses
from devpro.context import MapSupply, Render, harnesses
from devpro.definition import Definition, SkillFile
from devpro.families.claude import FAMILY as CLAUDE_FAMILY
from devpro.family import Family, Overlay
from devpro.harness import AgentFields, FrontmatterForm, Harness
from devpro.harnesses.claude import HARNESS as CLAUDE
from devpro.harnesses.mage import HARNESS as MAGE
from devpro.harnesses.opencode import HARNESS as OPENCODE
from devpro.render import definitions, filled_text, render_all, render_definition
from devpro.vocabulary import (
    ALL,
    CATEGORIES,
    AgentsFileText,
    Anchor,
    HarnessText,
    Kind,
    OptionalHarnessText,
    PluginText,
    Tool,
    TuningText,
    hole,
)
from devtools import render_diff
from devtools.dupe_sweep import doc_sentences
from tests._structure import ClauseRoot, body_roots, clause_graph, definition_paths, repeated_clause_reaches
from tests.conftest import PLAIN, WITH_KBASE

_ALL_INHERIT = dict.fromkeys(CATEGORIES, "inherit")
_SELECTIONS = (PLAIN, WITH_KBASE)
_PACKAGE = Path(devpro.__file__).parent
_SUPPLIER = "--config-file /home/me/.config/devpro/devpro.toml, table '[claude.model-map]'"


def _security_reviewer() -> Definition:
    return Definition(
        name="security-reviewer",
        kind=Kind.AGENT,
        description=(
            "Adversarial security review of code and designs. Identifies hazards, attack vectors, and the "
            "specific conditions that must hold to prevent exploitation. Does not prescribe design solutions — "
            "that is the architect's job. Review only, never modifies files."
        ),
        tools=(Tool.BASH, Tool.READ, Tool.GREP, Tool.GLOB, Tool.WRITE, Tool.EDIT, Tool.WEBSEARCH, Tool.WEBFETCH),
        category="stem-architect",
        body="body",
        color="#DC2626",
    )


_SECURITY_REVIEWER_DESCRIPTION = (
    'description: "Adversarial security review of code and designs. Identifies hazards, attack vectors, and '
    "the specific conditions that must hold to prevent exploitation. Does not prescribe design solutions — "
    "that is the architect's job. Review only, never modifies files.\""
)


def _claude_frontmatter(fields: AgentFields) -> tuple[str, ...]:
    form = CLAUDE.definition_form
    assert isinstance(form, FrontmatterForm)
    return form.agent(fields)


_PYTHON_CODER_DESCRIPTION = 'description: "Python implementation specialist."'


def _python_coder() -> Definition:
    [defn] = [defn for _, defn in definitions() if defn.name == "python-coder"]
    return defn


_OPENCODE_PERMISSIONS = {
    "read": "allow",
    "grep": "allow",
    "glob": "allow",
    "list": "allow",
    "edit": "allow",
    "shell": "allow",
    "webfetch": "allow",
    "websearch": "allow",
    "subagent": "deny",
}
_COMMAND = Definition(
    name="probe",
    kind=Kind.COMMAND,
    body=f"Read the operator's notes under {hole(HarnessText.USER_HARNESS_DIR)}.",
)
_DOCUMENT = Definition(
    name="note",
    kind=Kind.DOCUMENT,
    body=f"Read the operator's conventions under {hole(HarnessText.USER_HARNESS_DIR)}.",
)


Discovered = tuple[tuple[str, Definition], ...]


@pytest.fixture(scope="module")
def discovered() -> Discovered:
    """Every definition the package discovers, with its module."""
    return definitions()


def _found(discovered: Discovered, path: str) -> tuple[str, Definition]:
    [found] = [(module, defn) for module, defn in discovered if defn.output_path == PurePosixPath(path)]
    return found


def _skill(**changes: object) -> Definition:
    """A skill named `probe` with one reference, its required description filled, overridable."""
    fields = {
        "name": "probe",
        "kind": Kind.SKILL,
        "description": "Use when the user asks about the knowledge base.",
        "body": "Route the request to the reference it asks for.",
        "files": (SkillFile(path="references/reading.md", body="Read a claim before you cite it."),),
    }
    return Definition(**{**fields, **changes})


_OPENCODE_RENDER = Render(harness=OPENCODE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT)


_MAGE_RENDER = Render(
    harness=MAGE, plugin=WITH_KBASE, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories)
)
_MAGE_MANIFEST = PurePosixPath(".claude-plugin/plugin.json")


def _user_install_paths() -> set[str]:
    """Each loaded harness's user plugin directory as the guide spells it, and the directory mage's plugin
    parent names, read from the profiles."""
    paths = set()
    for harness in harnesses().values():
        if harness.plugin_dir:
            paths.add(f"{harness.user_harness_dir}/{harness.plugin_dir.replace('{plugin}', '<plugin>')}/")
        if harness.plugin_parent_dir:
            paths.add(f"~/{harness.plugin_parent_dir}/")
    return paths


def _routed_references(router: str) -> set[str]:
    """The reference paths the router's tables route to, read off the table cells themselves."""
    routed = set()
    for line in router.split("\n"):
        if not line.startswith("|"):
            continue
        for cell in line.strip("|").split("|"):
            path = cell.strip().strip("`")
            if path.startswith("references/"):
                routed.add(path)
    return routed


_SKILLS_WITH_FILES = [defn for _, defn in definitions() if defn.kind is Kind.SKILL and defn.files]


_PREFIXED = [CLAUDE, dataclasses.replace(CLAUDE, reference_prefix="x:")]


_NAMESPACED = [harness for harness in (CLAUDE, MAGE, OPENCODE) if harness.reference_prefix]


_STEP_DOWN_BODY = f"before\n\nDefault: `{devpro.clauses.STEP_DOWN_MODEL}`, unless bound.\n\nafter"
_OMLX_SUPPLY = MapSupply(category_map=dict.fromkeys(CATEGORIES, "omlx/Qwen3.8-Flash-Next"), supplier=_SUPPLIER)
_INHERIT_SUPPLY = MapSupply(category_map=_ALL_INHERIT, supplier=_SUPPLIER)


_TUNING_HOLES = re.compile("|".join(re.escape(hole(part)) for part in TuningText))
_LIST_OR_TABLE_LINE = re.compile(r"^\s*(?:[-*] |\d+\. |\|)", re.MULTILINE)


def _kbase_skill_render(harness: Harness) -> dict[PurePosixPath, str]:
    """Every file of `harness`'s render of the kbase skill, keyed by its output path."""
    ctx = Render(harness=harness, plugin=WITH_KBASE, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    return dict(render_all(ctx))


_TUNED = Family(
    "tuned",
    {
        "stem-architect": "big",
        "stem-expert": "big",
        "stem-mechanical": "mid",
        "comm-architect": "big",
        "comm-expert": "big",
        "comm-mechanical": "mid",
    },
    overlays={Anchor.ASK_VS_STIPULATE: Overlay(text="family-wide", members={"mid": "for mid"})},
)


def _with_family_text(*, family: Family, category: str, body: str) -> str:
    defn = Definition(name="probe", kind=Kind.AGENT, description="a probe", tools=ALL, category=category, body=body)
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=family, category_map=dict(family.categories))
    return render_definition(defn, ctx, module="devpro.definitions.probe").split("---\n\n", 1)[1]


_OVERLAY = hole(Anchor.ASK_VS_STIPULATE)


_BAIT = hole(HarnessText.AGENTS_FILE)
_BAITED_FAMILY = Family(
    "baited",
    {
        "stem-architect": "big",
        "stem-expert": "big",
        "stem-mechanical": f"mid{_BAIT}",
        "comm-architect": "big",
        "comm-expert": "big",
        "comm-mechanical": "small",
    },
    overlays={Anchor.ASK_VS_STIPULATE: Overlay(text=f"overlay {_BAIT}")},
)


def _clause_with_a_baited_harness_value() -> tuple[Definition, Render, str]:
    """A clause constant's own holes are filled once; the value one fills to stays as it is."""
    harness = dataclasses.replace(CLAUDE, project_harness_dir=f"temp{_BAIT}")
    clause = devpro.clauses.NEW_PROJECT_SETUP
    expected = clause.replace(hole(HarnessText.PROJECT_HARNESS_DIR), f"temp{_BAIT}")
    defn = Definition(name="probe", kind=Kind.COMMAND, body=clause)
    return defn, Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT), expected


def _baited_harness_text() -> tuple[Definition, Render, str]:
    harness = dataclasses.replace(CLAUDE, user_harness_dir=f"~/home{_BAIT}")
    defn = Definition(name="probe", kind=Kind.COMMAND, body=f"see {hole(HarnessText.USER_HARNESS_DIR)}")
    return (
        defn,
        Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT),
        f"see ~/home{_BAIT}",
    )


def _baited_optional_harness_text() -> tuple[Definition, Render, str]:
    harness = dataclasses.replace(CLAUDE, recipe_rule=f"rule {_BAIT}")
    defn = Definition(name="probe", kind=Kind.COMMAND, body=hole(OptionalHarnessText.RECIPE_RULE))
    return (
        defn,
        Render(harness=harness, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT),
        f"rule {_BAIT}",
    )


def _baited_family_overlay() -> tuple[Definition, Render, str]:
    defn = Definition(
        name="probe", kind=Kind.AGENT, description="a probe", tools=ALL, category="stem-expert", body=_OVERLAY
    )
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=_BAITED_FAMILY, category_map=dict(_BAITED_FAMILY.categories))
    return defn, ctx, f"overlay {_BAIT}"


def _baited_scope_name() -> tuple[Definition, Render, str]:
    defn = Definition(name="probe", kind=Kind.AGENTS_FILE, body=f"# {hole(AgentsFileText.SCOPE_NAME)}")
    return (
        defn,
        Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=_ALL_INHERIT, scope=f"s{_BAIT}"),
        f"# s{_BAIT}",
    )


def _baited_step_down_model() -> tuple[Definition, Render, str]:
    """The family member a mechanical side pins carries the hole."""
    defn = _skill(body=f"use {hole(TuningText.STEP_DOWN_MODEL)}")
    ctx = Render(harness=CLAUDE, plugin=PLAIN, family=_BAITED_FAMILY, category_map=dict(_BAITED_FAMILY.categories))
    return defn, ctx, f"use stem-mechanical=mid{_BAIT}, comm-mechanical=small"


_REFERENCE = SkillFile(path="references/reading.md", body="Read it.")


def _walked(root: Path) -> list[Path]:
    """Each module under a root, a directory or one file, a hidden directory's files left out: a
    launcher's `.venv` beside its tools is not package source."""
    paths = [root] if root.is_file() else root.rglob("*.py")
    return [path for path in paths if not any(part.startswith(".") for part in path.relative_to(root).parts)]


def _modules(*subpaths: str) -> list[tuple[str, ast.Module]]:
    """Every module under each subpath of the package (a directory or one file), or the whole package."""
    roots = [_PACKAGE.joinpath(*sub.split("/")) for sub in subpaths] or [_PACKAGE]
    files = sorted({path for root in roots for path in _walked(root)})
    return [
        (path.relative_to(_PACKAGE.parent).as_posix(), ast.parse(path.read_text(encoding="utf-8"))) for path in files
    ]


def _imported(tree: ast.Module) -> list[str]:
    """Every module an import statement names, a relative import as under devpro, and each name a
    from-import takes as a possible submodule (`from devpro import clauses` names `devpro.clauses`)."""
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = f"devpro.{node.module}" if node.level else node.module
            names += [module, *(f"{module}.{alias.name}" for alias in node.names)]
    return names


_HOOK_WIRING = "devpro/profiler/hooks.py"
_HOOK_WIRING_IMPORTS = ("from devpro.context import build_render", "from devpro.render import render_all")


def _hook_wiring_imports(tree: ast.Module) -> set[tuple[str, str]]:
    """The `(path, statement)` pairs the hook wiring's carve-out admits: the renderer's two imports, held
    inside `profiler_skill_text`, the function that renders the skill a hook writes. `tree` is the module's
    own, so the carve-out is read against the file it exempts and admits nothing the file does not hold
    there."""
    held = {
        ast.unparse(stmt)
        for function in tree.body
        if isinstance(function, ast.FunctionDef) and function.name == "profiler_skill_text"
        for stmt in function.body
        if isinstance(stmt, (ast.Import, ast.ImportFrom))
    }
    return {(_HOOK_WIRING, stmt) for stmt in held & set(_HOOK_WIRING_IMPORTS)}


def _is_stdlib(module: str) -> bool:
    """Whether the top-level module resolves into the running interpreter's
    standard library: built in, frozen, or a file under its stdlib directory
    outside any site-packages."""
    spec = importlib.util.find_spec(module)
    if spec is None or spec.origin is None:
        return False
    if spec.origin in ("built-in", "frozen"):
        return True
    stdlib = Path(sysconfig.get_paths()["stdlib"]).resolve()
    origin = Path(spec.origin).resolve()
    return stdlib in origin.parents and "site-packages" not in origin.relative_to(stdlib).parts


_CORPUS_JOIN_SITES = (
    "devpro/definitions/agents/android_app_expert.py: clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/android_app_expert.py: clauses.PROJECT_SETUP_PLATFORM + clauses.STDLIB_FIRST_ALWAYS",
    "devpro/definitions/agents/architect.py: clauses.MACHINE_GUARANTEES",
    "devpro/definitions/agents/architect.py: clauses.PROVE_REPLACEMENT_RULE",
    "devpro/definitions/agents/architect.py: clauses.REVIEW_SEVERITY",
    "devpro/definitions/agents/architect.py: clauses.SEPARATION_OF_CONCERNS",
    "devpro/definitions/agents/c_coder.py: clauses.DATA_FORMATS_SCOPE",
    "devpro/definitions/agents/c_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/c_coder.py: clauses.data_race_frame + clauses.TSAN_VISIBILITY",
    "devpro/definitions/agents/cpp_coder.py: clauses.DATA_FORMATS_SCOPE",
    "devpro/definitions/agents/cpp_coder.py: clauses.DEPENDENCIES_LEAD_PACKAGES + clauses.ISSUE_TRACKER_HEALTH + clauses.manual_over_large_dependency",
    "devpro/definitions/agents/cpp_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/cpp_coder.py: clauses.data_race_frame + clauses.TSAN_VISIBILITY",
    "devpro/definitions/agents/generalist_coder.py: clauses.SHELL_HOUSE_STYLE",
    "devpro/definitions/agents/generalist_coder.py: clauses.heavy_logging_framework + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/generalist_coder.py: clauses.unit_test_scope_coder + clauses.COVERAGE_METRIC + clauses.MOCKING_THRESHOLD_GENERAL",
    "devpro/definitions/agents/go_coder.py: clauses.build_system_lead",
    "devpro/definitions/agents/go_coder.py: clauses.heavy_logging_framework + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/ios_app_expert.py: clauses.OSLOG_LOGGING_LEAD + clauses.logging_backend_seam + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/linux_app_expert.py: clauses.PROJECT_SETUP_PLATFORM + clauses.STDLIB_FIRST_ALWAYS",
    "devpro/definitions/agents/linux_app_expert.py: clauses.logging_backend_seam + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/linux_kernel_driver_expert.py: clauses.PROJECT_SETUP_PLATFORM + clauses.STDLIB_FIRST_ALWAYS",
    "devpro/definitions/agents/linux_kernel_driver_expert.py: clauses.logging_backend_seam + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/lua_coder.py: clauses.DATA_FORMATS",
    "devpro/definitions/agents/lua_coder.py: clauses.DEPENDENCIES_LEAD_PACKAGES + clauses.ISSUE_TRACKER_HEALTH + clauses.manual_over_large_dependency",
    "devpro/definitions/agents/lua_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/lua_coder.py: clauses.NEW_PROJECT_SETUP + clauses.new_project_runner_recipes",
    "devpro/definitions/agents/lua_coder.py: clauses.boundary_checks_lead + clauses.boundary_check_coder_body + clauses.BOUNDARY_CHECK_CONSUMERS_CODER",
    "devpro/definitions/agents/lua_coder.py: clauses.build_system_lead",
    "devpro/definitions/agents/macos_app_expert.py: clauses.OSLOG_LOGGING_LEAD + clauses.logging_backend_seam + clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/prompt_engineer.py: clauses.machine_guarantees",
    "devpro/definitions/agents/prompt_engineer.py: clauses.pe_declare_bullet",
    "devpro/definitions/agents/python_coder.py: clauses.CODE_PRINCIPLES_CODER",
    "devpro/definitions/agents/python_coder.py: clauses.DATA_FORMATS",
    "devpro/definitions/agents/rust_coder.py: clauses.DATA_FORMATS",
    "devpro/definitions/agents/rust_coder.py: clauses.DEPENDENCIES_LEAD_CRATES + clauses.ISSUE_TRACKER_HEALTH + clauses.manual_over_large_dependency",
    "devpro/definitions/agents/rust_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/rust_coder.py: clauses.boundary_checks_lead + clauses.boundary_check_coder_body + clauses.BOUNDARY_CHECK_CONSUMERS_CODER",
    "devpro/definitions/agents/rust_coder.py: clauses.build_system_lead",
    "devpro/definitions/agents/security_reviewer.py: clauses.REVIEW_SEVERITY",
    "devpro/definitions/agents/shell_dsl_coder.py: clauses.CODE_PRINCIPLES_CODER",
    "devpro/definitions/agents/shell_dsl_coder.py: clauses.DEPENDENCIES_LEAD_PACKAGES + clauses.ISSUE_TRACKER_HEALTH + clauses.manual_over_large_dependency",
    "devpro/definitions/agents/shell_dsl_coder.py: clauses.boundary_checks_lead + clauses.CHEAP_OVER_THOROUGH + clauses.BOUNDARY_CHECK_CONSUMERS_CODER",
    "devpro/definitions/agents/shell_dsl_coder.py: clauses.unit_test_scope_coder + clauses.COVERAGE_METRIC + clauses.MOCKING_THRESHOLD_GENERAL",
    "devpro/definitions/agents/tech_writer.py: clauses.REVIEW_SEVERITY",
    "devpro/definitions/agents/typescript_coder.py: clauses.DATA_FORMATS",
    "devpro/definitions/agents/typescript_coder.py: clauses.LOGGING_ABSTRACTION_NOTE + clauses.LOGS_NOT_STDOUT",
    "devpro/definitions/agents/typescript_coder.py: clauses.NEW_PROJECT_SETUP + clauses.new_project_runner_recipes",
    "devpro/definitions/agents/typescript_coder.py: clauses.boundary_checks_lead + clauses.boundary_check_coder_body + clauses.BOUNDARY_CHECK_CONSUMERS_CODER",
    "devpro/definitions/agents/typescript_coder.py: clauses.build_system_lead",
    "devpro/definitions/agents/web_app_expert.py: clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/agents/windows_app_expert.py: clauses.LOGGING_ABSTRACTION_NOTE",
    "devpro/definitions/skills/kbase.py: clauses.kb_orientation_docs",
)


_DEFINITION_HEAD = "from devpro import clauses\nfrom devpro.definition import Definition\n"


def _definitions_of_body(body: str, *, head: str = "") -> str:
    """A definition-module source whose one Definition has `body` as its body= source text."""
    return f'{_DEFINITION_HEAD}{head}DEFINITIONS = (Definition(name="p", kind=Kind.COMMAND, body={body}),)\n'


def _definitions_of_files(files: str) -> str:
    """A definition-module source whose one skill has `files` as its files= source text."""
    return f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", kind=Kind.SKILL, files={files}),)\n'


_CLAUDE_RENDER = Render(harness=CLAUDE, plugin=PLAIN, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
_SELECTION_RENDERS = tuple(
    Render(harness=CLAUDE, plugin=components, family=CLAUDE_FAMILY, category_map=dict(CLAUDE_FAMILY.categories))
    for components in _SELECTIONS
)
RENDERED_DEFINITION_LINE_CAP = 500  # a runaway guard, not a target; the 100-column wrap makes lines a fair size


def _credited_text() -> types.SimpleNamespace:
    """The clauses module with every constant and function standing as a sentinel naming it; a
    constant that is a bare placeholder keeps its value, so prose around it is not credited to it."""
    standing: dict[str, object] = {}
    for name, value in vars(devpro.clauses).items():
        if isinstance(value, str) and not devpro.render.PLACEHOLDER.fullmatch(value):
            standing[name] = f"<<devpro.clauses.{name}>>"
        elif isinstance(value, str):
            standing[name] = value
        elif inspect.isfunction(value) and value.__module__ == devpro.clauses.__name__:
            standing[name] = lambda _sentinel=f"<<devpro.clauses.{name}()>>", **_: _sentinel
    return types.SimpleNamespace(**standing)


def _source_definitions(source: str, *, module: str, credited: bool) -> tuple[Definition, ...]:
    """DEFINITIONS as the module's source builds them; credited, with each of the module's string
    constants and everything it reaches through `clauses` standing as a sentinel naming it."""
    tree = ast.parse(source)
    namespace: dict[str, object] = {"__name__": module}
    if credited:
        namespace["clauses"] = _credited_text()
        body = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and any(alias.name == "clauses" for alias in node.names):
                continue
            target = node.targets[0].id if isinstance(node, ast.Assign) else ""
            if target and target != "DEFINITIONS":
                node = ast.copy_location(ast.Assign(targets=node.targets, value=ast.Constant(f"<<{target}>>")), node)
            body.append(node)
        tree.body = body
        ast.fix_missing_locations(tree)
    exec(compile(tree, module, "exec"), namespace)
    return namespace["DEFINITIONS"]


_ENUMERATION_MARKER = re.compile(rb"^\d+[.)] ")


def _prose_unit_list(body: str) -> list[bytes]:
    """The paragraphs and list items of a body in order, each as devtools.render_diff collapses it; a
    heading, a table row and a line of a fenced block are not prose."""
    lines = render_diff.collapsed(body.encode("utf-8")).split(b"\n")
    return [line for line, kind in zip(lines, render_diff.line_kinds(lines)) if kind in ("item", "text")]


def _sentence_list(body: str) -> list[str]:
    """The sentences of a body's prose units in order, each split by the sweep's own splitter so a
    sentence means here what it means there: punctuation splits it, abbreviation or not, and each
    unit is rejoined across its hard wrap first.

    A unit's leading enumeration marker is dropped before the split, anchored at the unit's start. A
    marker is the list's numbering, not prose: one output carrying two numbered lists splits into the
    same `1.`…`5.` twice, which two outputs repeating one sentence do not. A number written mid-sentence
    is prose, and dropping it would split that unit unlike its unnumbered twin."""
    return [
        sentence
        for unit in _prose_unit_list(body)
        for _, sentence in doc_sentences.block_sentences([(1, _ENUMERATION_MARKER.sub(b"", unit, count=1).decode())])
    ]


def _prose_units(body: str) -> set[bytes]:
    return set(_prose_unit_list(body))


def _outputs(defn: Definition, sentinel: Definition) -> list[tuple[str, str, str]]:
    """(label, the definition's own text, its credited twin's) for every file it renders: its output
    first, labeled by the path it renders to, then each supporting file."""
    if defn.kind is Kind.AGENTS_FILE:
        return [(defn.name, defn.body, sentinel.body)]
    pairs = [(str(defn.output_path), defn.body, sentinel.body)]
    assert len(defn.files) == len(sentinel.files)
    pairs += [
        (str(defn.file_output_path(file)), file.body, twin.body) for file, twin in zip(defn.files, sentinel.files)
    ]
    return pairs


def _in_selection(defn: Definition, ctx: Render) -> bool:
    """Whether `ctx`'s selection carries `defn`: a definition it ships, or the agents file every selection
    has."""
    return defn.kind is Kind.AGENTS_FILE or ctx.plugin.ships(defn.name)


def _definition_sources() -> dict[str, str]:
    """Each definition module's dotted name, mapped to its source text."""
    return {
        ".".join(path.relative_to(_PACKAGE.parent).with_suffix("").parts): path.read_text(encoding="utf-8")
        for path in definition_paths()
    }


def _uncredited_shared_paragraphs(sources: dict[str, str]) -> list[str]:
    """Every prose unit two or more outputs of one plugin write out rather than take from a constant, a
    slot constant or a text function: the unit survives each one's credited render unchanged."""
    found: dict[str, None] = {}
    for ctx in _SELECTION_RENDERS:
        written: dict[bytes, list[str]] = {}
        for module, source in sources.items():
            rendered = _source_definitions(source, module=module, credited=False)
            credited = _source_definitions(source, module=module, credited=True)
            assert len(rendered) == len(credited)
            for defn, sentinel in zip(rendered, credited):
                if not _in_selection(defn, ctx):
                    continue
                for label, literal_body, credited_body in _outputs(defn, sentinel):
                    literal = _prose_units(filled_text(literal_body, defn, ctx, where=label)) & _prose_units(
                        filled_text(credited_body, sentinel, ctx, where=label)
                    )
                    for unit in literal:
                        written.setdefault(unit, []).append(label)
        found.update(
            (f"written out in {', '.join(written[unit])}: {unit.decode()[:120]}", None)
            for unit in sorted(written)
            if len(written[unit]) > 1
        )
    return list(found)


_FIXTURE_HEAD = (
    "from devpro import clauses\nfrom devpro.definition import Definition\nfrom devpro.vocabulary import Kind\n"
)
_SKILL_FIXTURE_HEAD = (
    "from devpro import clauses\nfrom devpro.definition import Definition, SkillFile\n"
    "from devpro.vocabulary import Kind\n"
)


def _fixture_module(*bodies: tuple[str, str], head: str = "") -> str:
    """A definition-module source of one command per (name, body source text)."""
    entries = "".join(f'Definition(name="{name}", kind=Kind.COMMAND, body={body}),' for name, body in bodies)
    return f"{_FIXTURE_HEAD}{head}DEFINITIONS = ({entries})\n"


def _skill_fixture_module(*file_bodies: str) -> str:
    """A definition-module source of one skill whose supporting files carry `file_bodies`."""
    names = ("one", "two", "three")
    entries = "".join(
        f'SkillFile(path="references/{names[index]}.md", body={body}),' for index, body in enumerate(file_bodies)
    )
    return (
        f'{_SKILL_FIXTURE_HEAD}DEFINITIONS = (Definition(name="s", kind=Kind.SKILL, description="a skill", '
        f'body="Own router.", files=({entries})),)\n'
    )


def _definition_sentences() -> list[str]:
    """Every sentence a definition module holds in its definitions' own text — a description included,
    which a rendering writes too — read off their source."""
    found = []
    for module, source in _definition_sources().items():
        for defn in _source_definitions(source, module=module, credited=False):
            bodies = [defn.body, *(file.body for file in defn.files)]
            found += [
                sentence
                for body in (*bodies, defn.description or "")
                for sentence in _sentence_list(filled_text(body, defn, _SELECTION_RENDERS[0], where=defn.name))
            ]
    return found


def _repeatable_sentence() -> str:
    """A sentence the check writes into a fixture: long enough that a repeat is worth catching, plain
    enough to hold inside a definition source written by string formatting — no quote, no backslash —
    and not opening with a digit, which a list item would read as its enumeration marker."""
    for sentence in _definition_sentences():
        if len(sentence) > 40 and not re.search(r'["\\]', sentence) and not sentence[0].isdigit():
            return sentence
    raise LookupError(
        "every definition sentence is too short, carries a quote or backslash, or opens with a digit — "
        "no sentence can stand in a fixture written by string formatting"
    )


_CLAUSE_GRAPH = clause_graph((_PACKAGE / "clauses.py").read_text(encoding="utf-8"))
_HARNESS_STRINGS = {hole(part) for part in (*HarnessText, *PluginText)}
_SENTENCE_HOLES = (
    frozenset(
        name for name, value in vars(devpro.clauses).items() if isinstance(value, str) and value in _HARNESS_STRINGS
    )
    | {devpro.clauses.ref.__name__, devpro.clauses.optional_ref.__name__}
    | {
        name
        for name, value in vars(devpro.clauses).items()
        if isinstance(value, str) and value in set(devpro.clauses.VALUE_CONSTANTS)
    }
)


@dataclass(frozen=True)
class _PromptOutput:
    """One rendered file: its label, its text filled under the claude render, and the clause roots its
    body names. `loads` marks a command's or skill's own body, whose `@` lines can load another
    output; `path` is None for the agents file, which no `@` line can name."""

    label: str
    path: PurePosixPath | None
    text: str
    roots: tuple[ClauseRoot, ...]
    loads: bool


def _prompts(sources: dict[str, str]) -> list[list[_PromptOutput]]:
    """Every prompt of every plugin: an output with that plugin's installed agents file, and for a command
    or skill body each output of the plugin an `@` line of it names, transitively; the agents file's own
    output is a prompt alone."""
    prompts = []
    for ctx in _SELECTION_RENDERS:
        outputs = []
        for module, source in sources.items():
            roots = body_roots(source, _CLAUSE_GRAPH)
            for defn in _source_definitions(source, module=module, credited=False):
                if not _in_selection(defn, ctx):
                    continue
                keys = (None, *(file.path for file in defn.files))
                defn_outputs = _outputs(defn, defn)
                assert len(keys) == len(defn_outputs)
                for key, (label, body, _) in zip(keys, defn_outputs):
                    outputs.append(
                        _PromptOutput(
                            label=label,
                            path=None if defn.kind is Kind.AGENTS_FILE else PurePosixPath(label),
                            text=filled_text(body, defn, ctx, where=label),
                            roots=roots[defn.name, key],
                            loads=key is None and defn.kind in (Kind.COMMAND, Kind.SKILL),
                        )
                    )
        agents_file = [output for output in outputs if output.path is None]
        prompts += [
            [output, *(_loaded(output, outputs) if output.loads else ()), *(agents_file if output.path else ())]
            for output in outputs
        ]
    return prompts


def _loaded(output: _PromptOutput, outputs: list[_PromptOutput]) -> list[_PromptOutput]:
    """The outputs `output`'s `@` lines name, and those named by the `@` lines of each such output that
    loads, transitively, each once in first-reached order and never `output` itself. A line names an
    output when its path ends in the output's."""
    reached: list[_PromptOutput] = []
    pending = [output]
    while pending:
        current = pending.pop(0)
        named = [PurePosixPath(line[1:].strip()).parts for line in current.text.splitlines() if line.startswith("@")]
        for parts in named:
            for target in outputs:
                if target.path is None or parts[-len(target.path.parts) :] != target.path.parts:
                    continue
                if target is output or target in reached:
                    continue
                reached.append(target)
                if target.loads:
                    pending.append(target)
    return reached


def _double_clause_deliveries(sources: dict[str, str]) -> list[str]:
    """Each clause a prompt reaches twice, named with the prompt and both chains that reach it, each finding
    once however many selections deliver the prompt."""
    found = []
    for prompt in _prompts(sources):
        rooted = [(output.label, output.roots) for output in prompt]
        for node, *reaches in repeated_clause_reaches(_CLAUSE_GRAPH, rooted, uncounted=_SENTENCE_HOLES):
            paths = " | ".join(f"{label}: {' → '.join(chain)}" for label, chain in reaches)
            found.append(f"{prompt[0].label}: {node} reached twice — {paths}")
    return list(dict.fromkeys(found))


def _double_paragraphs(sources: dict[str, str]) -> list[str]:
    """Each sentence a prompt carries twice, named with the prompt, each finding once however many
    selections deliver the prompt."""
    found = []
    for prompt in _prompts(sources):
        counts = Counter(sentence for output in prompt for sentence in _sentence_list(output.text))
        found += [
            f"{prompt[0].label}: written twice: {sentence[:120]}" for sentence, count in counts.items() if count > 1
        ]
    return list(dict.fromkeys(found))


def _chain_output(name: str, *loads: str) -> _PromptOutput:
    text = "\n".join(f"@commands/{target}.md" for target in loads)
    return _PromptOutput(
        label=f"commands/{name}.md", path=PurePosixPath(f"commands/{name}.md"), text=text, roots=(), loads=True
    )
