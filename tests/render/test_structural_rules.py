"""check_structure• folder kind  (consumes _structure.py)"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

import pytest

from devpro.definition import Definition
from devpro.definitions import definitions_of, discover
from devpro.errors import InputError
from devpro.render import keyed_by_path
from devpro.vocabulary import ALL, Kind
from devtools import clause_join_sites
from tests._structure import (
    ARGUMENT_RULE,
    ASSIGNMENT_RULE,
    BODY_RULE,
    CALL_RULE,
    DEFINITION_CALL_RULE,
    DEFINITION_TOP_RULE,
    FILES_RULE,
    FOLDER_KIND_RULE,
    FUNCTION_RULE,
    IMPORT_RULE,
    TEXT_TOP_RULE,
    check_source,
    check_structure,
    definition_paths,
)

from .conftest import (
    _CORPUS_JOIN_SITES,
    _DEFINITION_HEAD,
    _HOOK_WIRING,
    _PACKAGE,
    _REFERENCE,
    _definitions_of_body,
    _definitions_of_files,
    _hook_wiring_imports,
    _imported,
    _is_stdlib,
    _modules,
    _walked,
)


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"tools": ()}, "tools must be ALL"),
        ({"body": ""}, "body must be"),
        ({"body": "edge newline\n"}, "body must be"),
        ({"description": 'holds a "quote"'}, "description must be"),
        ({"category": None}, "an agent requires category"),
        ({"kind": Kind.DOCUMENT}, "a document takes no description, tools, category"),
        (
            {"kind": Kind.COMMAND, "description": None, "tools": None, "category": None, "color": "#000000"},
            "takes no color",
        ),
        ({"folder": "nested/Design"}, "folder 'nested/Design'"),
        ({"kind": Kind.SKILL, "description": None}, "a skill requires description"),
        (
            {"kind": Kind.SKILL, "description": "a probe", "tools": ALL, "category": None},
            "a skill takes no tools",
        ),
        (
            {"kind": Kind.SKILL, "description": "a probe", "tools": None, "category": None, "color": "#000000"},
            "a skill takes no color",
        ),
        (
            {"kind": Kind.SKILL, "description": "a probe", "tools": None, "category": None, "folder": "sub"},
            "a skill takes no folder",
        ),
        (
            {
                "kind": Kind.SKILL,
                "description": "a probe",
                "tools": None,
                "category": None,
                "files": (_REFERENCE, _REFERENCE),
            },
            "files names a path twice",
        ),
        (
            {"kind": Kind.COMMAND, "description": None, "tools": None, "category": None, "files": (_REFERENCE,)},
            "a command takes no files",
        ),
    ],
)
def test_definition_refusals(changes: dict, message: str) -> None:
    fields = {
        "name": "probe",
        "kind": Kind.AGENT,
        "description": "a probe",
        "tools": ALL,
        "category": "stem-expert",
        "body": "ok",
    }
    with pytest.raises(InputError, match="definition 'probe'") as caught:
        Definition(**{**fields, **changes})
    assert message in str(caught.value)


def test_output_paths_not_names_are_unique() -> None:
    command = Definition(name="probe", kind=Kind.COMMAND, body="x")
    document = Definition(name="probe", kind=Kind.DOCUMENT, folder="nested", body="x")
    paths = [defn.output_path for _, defn in keyed_by_path([("m.a", (command,)), ("m.b", (document,))])]
    assert paths == [PurePosixPath("agents/nested/probe.md"), PurePosixPath("commands/probe.md")]
    with pytest.raises(InputError, match=re.escape("'commands/probe.md' is produced by both m.a and m.b")):
        keyed_by_path([("m.a", (command,)), ("m.b", (command,))])


def test_an_agents_file_has_no_output_path() -> None:
    defn = Definition(name="probe", kind=Kind.AGENTS_FILE, body="x")
    with pytest.raises(InputError, match="definition 'probe': an agents file has no output path"):
        defn.output_path


def test_discovery_refuses_a_module_without_definitions() -> None:
    with pytest.raises(InputError, match="'devpro.definitions.probe' defines no DEFINITIONS"):
        definitions_of("devpro.definitions.probe", None)


def test_discovery_raises_where_a_subpackage_does_not_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A subpackage that does not import takes every definition under it out of the set — silently,
    since nothing else reads the folder — and an install then prunes their files. Discovery raises
    the failure instead of reporting a shorter set."""
    package = tmp_path / "planted"
    package.mkdir()
    (package / "__init__.py").write_text("raise ImportError('planted does not import')\n", encoding="utf-8")
    (package / "child.py").write_text("X = 1\n", encoding="utf-8")
    monkeypatch.setattr("devpro.definitions.__path__", [str(tmp_path)])
    with pytest.raises(ImportError, match=re.escape("devpro.definitions.planted")):
        discover()


def test_module_walk_skips_hidden_directories(tmp_path: Path) -> None:
    hidden = tmp_path / ".venv"
    hidden.mkdir()
    (hidden / "planted.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "mod.py").write_text("x = 1\n", encoding="utf-8")
    assert {path.name for path in _walked(tmp_path)} == {"mod.py"}


def test_definitions_and_text_reach_nothing_outside_their_arguments() -> None:
    banned = {"os", "sys", "subprocess", "time", "random"}
    offenders = []
    for path, tree in _modules("definitions", "clauses.py"):
        offenders += [f"{path} imports {name}" for name in _imported(tree) if name.split(".")[0] in banned]
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                called = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", None)
                if called == "open":
                    offenders.append(f"{path}:{node.lineno} calls open")
    assert offenders == []


def test_the_hook_wiring_carve_out_admits_only_its_two_imports_in_the_writer() -> None:
    """The carve-out is not a hole: the renderer's two imports are admitted where `profiler_skill_text` holds
    them, and neither is admitted anywhere else — a third import in the writer, or either import in
    another function, reads as the offender it is."""
    source = (
        "def profiler_skill_text():\n"
        "    from devpro.render import render_all\n"
        "    from devpro.context import build_render\n"
        "    import json\n"
        "\n"
        "def launcher_resource():\n"
        "    from devpro.render import render_all\n"
    )
    admitted = _hook_wiring_imports(ast.parse(source))
    assert admitted == {
        (_HOOK_WIRING, "from devpro.render import render_all"),
        (_HOOK_WIRING, "from devpro.context import build_render"),
    }


def test_every_import_is_at_module_level() -> None:
    # The entry point is the one exception: its dispatch is lazy, importing each verb's module at dispatch
    # time so no verb pays for another's imports, so its function-level imports are the deliberate
    # exception and are not walked here. The house rule holds for every other module of the package.
    # The absorbed dicing verbs' entry point carries the same exception, for the same reason: its `run`
    # imports each verb's implementation where it dispatches that verb. The profiler's entry point is
    # the third: its verb is one remainder the dispatch resolves, and its `run` imports the subcommands'
    # modules so the `devpro --help` build pays for none of them. The dashboard's entry point is the
    # fourth, for the same reason: its `run` imports the server where it dispatches. The check verbs'
    # entry point is the fifth: its `run` imports the checks' implementation where it dispatches each.
    # The profiler's hook wiring is the one other module, and the same reason one level down: the
    # hook-run capture imports it, so the renderer's imports live in `profiler_skill_text`, the function that
    # renders the skill a hook writes, rather than at module scope, and the renderer never reaches the
    # every-tool-call capture path. `_hook_wiring_imports` reads them from the module, so an import
    # moved back to module scope leaves nothing carved out and reads as the offender it would be.
    offenders = [
        f"{path}:{node.lineno}"
        for path, tree in _modules()
        if path
        not in (
            "devpro/cli.py",
            "devpro/dicing/cli.py",
            "devpro/doccheck/cli.py",
            "devpro/profiler/cli.py",
            "devpro/dashboard/cli.py",
        )
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and node not in tree.body
        and (path, ast.unparse(node)) not in _hook_wiring_imports(tree)
    ]
    assert offenders == []


@pytest.mark.parametrize(
    ("module", "expected"),
    [
        ("__future__", True),
        ("ast", True),
        ("_thread", True),
        ("json", True),
        ("pytest", False),
        ("devpro", False),
        ("no_such_module_anywhere", False),
    ],
)
def test_is_stdlib_tells_the_standard_library_from_everything_else(module: str, expected: bool) -> None:
    assert _is_stdlib(module) is expected


def test_every_import_is_stdlib_or_the_package() -> None:
    offenders = [
        f"{path} imports {name}"
        for path, tree in _modules()
        for name in _imported(tree)
        if name.split(".")[0] != "devpro" and not _is_stdlib(name.split(".")[0])
    ]
    assert offenders == []


def test_importing_the_entry_point_imports_no_verb_module() -> None:
    """The dispatch is lazy: building the parser and choosing no verb imports no verb's module, so `--help`
    and every verb pay for no other's imports. Before the change the parser build imported every verb's
    implementation — all nine, the kanban server among them — so this same parser build showed
    `devpro.install` and the dicing verbs' modules in `sys.modules`. The dicing registration chain is the
    pair of the package and its verb surface; no other `devpro.dicing` module is imported by it, the
    board's server among them. The dashboard's own pair is the same: its registration chain loads the
    package, its verb surface and the cli's own imports, and the server it serves from is imported where
    the verb dispatches."""
    probe = (
        "import sys\n"
        "import devpro.cli\n"
        "devpro.cli.build_parser()\n"
        "banned = ('devpro.install', 'devpro.render', 'devpro.agents_file')\n"
        "present = [name for name in banned if name in sys.modules]\n"
        "for package, surface in (('devpro.dicing', 'devpro.dicing.cli'),\n"
        "                         ('devpro.doccheck', 'devpro.doccheck.cli'),\n"
        "                         ('devpro.dashboard', 'devpro.dashboard.cli')):\n"
        "    loaded = {\n"
        "        name for name in sys.modules if name == package or name.startswith(package + '.')\n"
        "    }\n"
        "    present += sorted(loaded - {package, surface})\n"
        "assert not present, present\n"
    )
    env = {**os.environ, "PYTHONPATH": str(_PACKAGE.parent)}
    result = subprocess.run([sys.executable, "-c", probe], env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def test_importing_the_profiler_hook_wiring_never_reaches_the_renderer() -> None:
    """The capture path pays for nothing it does not run: the hook-run capture imports the profiler's hook
    wiring for its two names, and the install imports it for the stores' rename, so neither may pull the
    renderer in — seventeen devpro submodules for the rename alone, the renderer's import on the
    every-tool-call capture path. The modules that register the profiler verb are the only others the
    chain may name."""
    probe = (
        "import sys\n"
        "import devpro.profiler.hooks\n"
        "banned = ('devpro.render', 'devpro.context', 'devpro.definitions', 'devpro.loading', 'devpro.family')\n"
        "present = [name for name in banned if name in sys.modules]\n"
        "assert not present, present\n"
    )
    env = {**os.environ, "PYTHONPATH": str(_PACKAGE.parent)}
    result = subprocess.run([sys.executable, "-c", probe], env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def test_the_definition_modules_and_the_text_module_hold_their_structure() -> None:
    violations = check_structure([*definition_paths(), _PACKAGE / "clauses.py"])
    assert violations == [], "\n".join(violations)


def test_development_bodies_spell_each_term_through_its_constant() -> None:
    """A project binds a term by its exact spelling, so a body writing one out literally drifts from the
    constant every other mention renders from."""
    tree = ast.parse((_PACKAGE / "definitions" / "skills" / "development.py").read_text(encoding="utf-8"))
    terms = {
        node.targets[0].id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign) and node.targets[0].id.endswith("_TERM")
    }
    assert terms, "no *_TERM constant found, so the check below would pass vacuously"
    literals = [
        node
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        for keyword in call.keywords
        if keyword.arg == "body"
        for node in ast.walk(keyword.value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    found = [
        f"a development.py body writes out {term} as {value!r}"
        for node in literals
        for term, value in terms.items()
        if value in node.value
    ]
    assert found == [], "\n".join(found)


def test_the_join_sites_are_the_ones_the_corpus_holds(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The clause-paragraph rule's judgment is manual, so the corpus's join sites are pinned: a new
    site fails until the tuple is updated deliberately, and a moved line, whose site's line number
    the key drops, does not."""
    monkeypatch.chdir(_PACKAGE.parent)
    clause_join_sites.main([])
    lines = capsys.readouterr().out.splitlines()
    assert lines[-1].startswith("sites: ")
    keys = []
    for line in lines[:-1]:
        match = re.fullmatch(r"(.+?):\d+: (.+)", line)
        assert match is not None, f"not a join-site line: {line}"
        keys.append(f"{match[1]}: {match[2]}")
    assert sorted(keys) == sorted(_CORPUS_JOIN_SITES)


@pytest.mark.parametrize(
    "source, line, rule",
    [
        (f'{_DEFINITION_HEAD}_N = len("x")\n', 3, ASSIGNMENT_RULE),
        (f'{_DEFINITION_HEAD}_D = {{"a": "b"}}\n', 3, ASSIGNMENT_RULE),
        (f'{_DEFINITION_HEAD}_T = ("a", _X)\n', 3, ASSIGNMENT_RULE),
        (f'{_DEFINITION_HEAD}_C = "".join(x for x in "ab")\n', 3, ASSIGNMENT_RULE),
        (f'{_DEFINITION_HEAD}_F = f"{{clauses.DISSENT}}"\n', 3, ASSIGNMENT_RULE),
        (_definitions_of_body('f"{clauses.dissent(x=clauses.other())}"'), 3, ARGUMENT_RULE),
        (_definitions_of_body('f"{_S.format(x=_V)}"', head='_S = "{x}"\n_V = f"{_S}"\n'), 5, ""),
        (_definitions_of_body("f\"{_F.format(x='a')}\"", head='_A = "a"\n_F = f"{_A} {{x}}"\n'), 5, CALL_RULE),
        (_definitions_of_body('f"{len(_S)}"', head='_S = "s"\n'), 4, CALL_RULE),
        (_definitions_of_body('f"{_S.upper()}"', head='_S = "s"\n'), 4, CALL_RULE),
        (_definitions_of_body('f"{clauses.x(**_K)}"'), 3, ARGUMENT_RULE),
        (_definitions_of_body('f"{_S if _S else _S}"', head='_S = "s"\n'), 4, BODY_RULE),
        (_definitions_of_files('(SkillFile(path="references/r.md", body="b"),)'), 3, ""),
        (_definitions_of_files('(SkillFile(path="references/r.md", body=f"{clauses.dissent()}"),)'), 3, ""),
        (_definitions_of_files('(SkillFile(path=clauses.f(), body="b"),)'), 3, FILES_RULE),
        (_definitions_of_files("(SkillFile(path=_P, body='b'),)"), 3, FILES_RULE),
        (_definitions_of_files("(clauses.f(),)"), 3, CALL_RULE),
        (_definitions_of_files('(SkillFile(path="references/r.md", body=f"{len(_S)}"),)'), 3, CALL_RULE),
        (
            f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", description=f"{{clauses.ref(name=\'x\')}}", body="b"),)\n',
            3,
            "",
        ),
        (
            f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", description=f"{{len(_S)}}", body="b"),)\n',
            3,
            CALL_RULE,
        ),
        (f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", tools=clauses.f(), body="b"),)\n', 3, CALL_RULE),
        (f'{_DEFINITION_HEAD}DEFINITIONS = (Definition("p", "b", kind=Kind.AGENT),)\n', 3, DEFINITION_CALL_RULE),
        (f"{_DEFINITION_HEAD}def helper():\n    pass\n", 3, DEFINITION_TOP_RULE),
        (f"{_DEFINITION_HEAD}DEFINITIONS = (_ONE,)\n", 3, DEFINITION_TOP_RULE),
        ("from devpro.clauses import X\n", 1, IMPORT_RULE),
        ("from devpro import clauses as c\n", 1, IMPORT_RULE),
        ("import devpro.clauses\n", 1, IMPORT_RULE),
    ],
)
def test_check_structure_refuses_a_definition_module_off_its_rules(source: str, line: int, rule: str) -> None:
    expected = [f"m.py:{line}: {rule}"] if rule else []
    assert check_source(source, where="m.py", text_module=False) == expected


@pytest.mark.parametrize(
    "source, rule",
    [
        ('_X = "a"\nY = f"{_X}"\ndef f(*, a, b="x", c=_X) -> str:\n    """doc"""\n    return f"{a}{b}{c}{Y}"\n', ""),
        ("from devpro.vocabulary import hole\n", TEXT_TOP_RULE),
        ("class C:\n    pass\n", TEXT_TOP_RULE),
        ('X = hole("a")\n', ASSIGNMENT_RULE),
        ('X = f"{g()}"\n', ASSIGNMENT_RULE),
        ('X = Y\nY = "y"\n', ASSIGNMENT_RULE),
        ('X = (Y,)\nY = "y"\n', ""),
        ("X = (a,)\n", ASSIGNMENT_RULE),
        ('def f(a):\n    return f"{a}"\n', FUNCTION_RULE),
        ('def f(*, a, b, c, d):\n    return f"{a}{b}{c}{d}"\n', FUNCTION_RULE),
        ('def f(*args):\n    return "x"\n', FUNCTION_RULE),
        ("def f(*, a):\n    return g(a=a)\n", FUNCTION_RULE),
        ('def f(*, a):\n    return f"{g(a=a)}"\n', FUNCTION_RULE),
        ('def f(*, a):\n    b = a\n    return f"{b}"\n', FUNCTION_RULE),
        ('def f(*, a=g()):\n    return f"{a}"\n', FUNCTION_RULE),
        ('def f(*, a):\n    return f"{a!r}"\n', FUNCTION_RULE),
    ],
)
def test_check_structure_refuses_a_text_module_off_its_rules(source: str, rule: str) -> None:
    expected = [f"clauses.py:1: {rule}"] if rule else []
    assert check_source(source, where="clauses.py", text_module=True) == expected


@pytest.mark.parametrize(
    ("folder", "kind", "violates"),
    [
        ("agents", "AGENT", False),
        ("skills", "SKILL", False),
        ("definitions", "AGENTS_FILE", False),
        ("agents", "SKILL", True),
        ("skills", "AGENT", True),
        ("definitions", "AGENT", True),
        ("definitions", "SKILL", True),
    ],
)
def test_check_structure_holds_a_definition_module_to_its_folder(
    tmp_path: Path, folder: str, kind: str, violates: bool
) -> None:
    """The folder a module sits in is the kind it renders: a module under `agents/` declares
    Kind.AGENT, under `skills/` Kind.SKILL, and one at the package's top neither."""
    directory = tmp_path / folder
    directory.mkdir()
    path = directory / "m.py"
    path.write_text(
        f'{_DEFINITION_HEAD}DEFINITIONS = (Definition(name="p", kind=Kind.{kind}, body="b"),)\n', encoding="utf-8"
    )
    assert check_structure([path]) == ([f"{path}:3: {FOLDER_KIND_RULE}"] if violates else [])


def _references_clauses(tree: ast.Module, name: str) -> bool:
    """True where the module names `clauses.<name>` — an attribute access on the `clauses` name — anywhere."""
    return any(
        isinstance(node, ast.Attribute)
        and node.attr == name
        and isinstance(node.value, ast.Name)
        and node.value.id == "clauses"
        for node in ast.walk(tree)
    )


def _passes_venv_probe_rule(tree: ast.Module) -> bool:
    """True where the module calls `clauses.verification_evidence(probe_rule=clauses.VENV_PROBE_RULE)`."""
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "verification_evidence"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "clauses"
        ):
            continue
        for keyword in node.keywords:
            value = keyword.value
            if (
                keyword.arg == "probe_rule"
                and isinstance(value, ast.Attribute)
                and value.attr == "VENV_PROBE_RULE"
                and isinstance(value.value, ast.Name)
                and value.value.id == "clauses"
            ):
                return True
    return False


def test_the_reach_invariants_are_pinned() -> None:
    """Two corpus facts the suite holds to. The venv-probe sentence reaches only the two seats that run a
    Python probe: `python_coder` and `ml_engineer` pass `probe_rule=clauses.VENV_PROBE_RULE` to
    `verification_evidence`, and no other call site does. The review-severity ladder is named in only four
    bodies — `architect`, `security_reviewer`, `tech_writer` and `shell_dsl_coder` — the fixed home of the
    two Critical definitions it carries. A corpus change that reaches either constant at a new home, or
    drops it from one of these, fails here; either set grows only by a deliberate edit."""
    modules = _modules("definitions")
    probe_rule_sites = {PurePosixPath(path).stem for path, tree in modules if _passes_venv_probe_rule(tree)}
    assert probe_rule_sites == {"python_coder", "ml_engineer"}, sorted(probe_rule_sites)
    severity_carriers = {
        PurePosixPath(path).stem for path, tree in modules if _references_clauses(tree, "REVIEW_SEVERITY")
    }
    expected = {"architect", "security_reviewer", "tech_writer", "shell_dsl_coder"}
    assert severity_carriers == expected, sorted(severity_carriers)
