"""`devpro install TARGET [--components CSV]`, once `devpro.install_target` has resolved the harness
directory and the project root from TARGET. The set is written into ROOT, the harness's `plugin_dir`
below the harness directory, or the harness directory itself where that is empty.

ROOT is the plugin's own, entire: an install replaces it wholesale. After every check and before the
first write, the install removes ROOT's contents — every file and subdirectory below it, whatever wrote
them — and writes the fresh tree into the emptied directory. Nothing inside ROOT is read to decide its
fate: no banner, no stale list, no file judged ours or foreign. Two pass-overs are taken by path: on a
re-entry run the devpro copy's own files and the wrapper stand, and the agents file's path stands where
it falls inside ROOT (mage). ROOT itself is never removed, and an install keeps no backup of what it
replaces: the consumer's git is the record of what an install changed.

Every definition the selection ships is rendered into ROOT's agents/, commands/ and skills/. Each
skill-owned shipped package whose owning definition rendered is copied to its stated destination: the
development scripts inside the development skill's directory, and the kb-tools package, with the
`kbase` MCP entry, inside the kbase skill's. Every install writes the devpro tools package into ROOT's
tools/ — the running package's own copy, the wrapper that runs it and the runner snippets. A project
install writes the include line of each copied package carrying runner snippets into the consumer's
runner file. Each file the installing harness ships is copied into ROOT as it stands, and the harness's
hooks are registered in a file of their own under ROOT, its guardrail's entry only where one
install-time run of the guardrail succeeds. A harness-directory install below its project root also
gets its agents file in its harness directory. The project's profiler stores from before the
`.profiler-*` rename — `claude-profiler` and `opencode-profiler` — are renamed in place, once, with the
move printed.

A target that resolves into the running devpro package's own source is refused before anything is
written, and so are an install run from an installation's own copy into that installation, one whose
devpro-copy destination is a symlink, and one whose install directory itself is a symlink: each link
would let the replacement clear and write through it into whatever it names. Where the devpro
settings file names harnesses and `--harness` is not given, `install_selected` drives one install per
harness it names, each rendered from that harness's settings-file map and component list."""

import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path, PurePosixPath
from typing import NamedTuple

from devpro import __version__, clauses, install_base
from devpro.agents_file import (
    AgentsFileWrite,
    FollowedAgentsFile,
    checked_agents_file,
    checked_followed_agents_file,
    write_agents_file,
    write_followed_agents_file,
)
from devpro.components import NAME
from devpro.context import HarnessSettings, MapSupply, Render, harness_named
from devpro.errors import InputError
from devpro.harness import KBASE_OWNER, GuardrailHook, Harness, HarnessFile
from devpro.install_base import (
    KB_TOOLS_DIR,
    PACKAGE_ROOT,
    TOOLS_DIR,
    WRAPPER,
    report_left_alone,
)
from devpro.install_target import (
    require_existing_target,
    require_outside_package_source,
    require_subdir_inside,
    resolve_install_target,
    target_holds_harness_dir,
    user_dir_harnesses,
)
from devpro.preflight import run_preflighted
from devpro.profiler.stores import OLD_STORE_SUFFIX, OLD_STORES
from devpro.profiler.stores import rename_stores as migrate_stores
from devpro.profiler.values import NEW_STORE_PREFIX, TRACE_DIR
from devpro.render import (
    GENERATED_NOTICE,
    harness_file_text,
    render_all,
    shipped_harness_files,
    write_renders,
)
from devpro.runner_file import (
    JUSTFILE_NAMES,
    MAKEFILE_NAMES,
    SnippetSet,
    check_runner,
    install_include_lines,
    prepare_scratch_directory,
)


def uncommitted_sources() -> tuple[str, ...]:
    """Every `git status --porcelain` line under this package's directory, untracked included: the
    agents file is a function of the package, so an uncommitted change is an unpublished one. Outside
    a checkout there is no commit state, so nothing is uncommitted and git is not run."""
    if install_base.REPO_ROOT is None:
        return ()
    command = ["git", "-C", str(install_base.REPO_ROOT), "status", "--porcelain", "--", PACKAGE_ROOT.name]
    try:
        out = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InputError(f"cannot read the commit state of {PACKAGE_ROOT}: {exc}") from exc
    return tuple(line for line in out.splitlines() if line)


# The development scripts package, inside the development skill's own directory: the cold-read runner.
DEVELOPMENT_SCRIPTS_PACKAGE = "skills/development/scripts"


class ShippedPackage(NamedTuple):
    """A package an install copies: its source directory in this package (`.` for the package itself),
    its destination below ROOT, the definition it ships with — none for the plugin's own, which ships on
    every install — the runner snippets it carries, their directory below the destination, whose
    include line a project install writes into the project's runner file, and whether its script and
    build files take the installed banner: the devpro copy is byte-verbatim, so takes none."""

    source: str
    destination: str
    owner: str | None
    snippets: SnippetSet | None = None
    stamps: bool = True

    def installed_snippets(self) -> SnippetSet | None:
        """`snippets` with its directory below ROOT, as an include line names it."""
        if self.snippets is None:
            return None
        return self.snippets._replace(directory=PurePosixPath(self.destination, self.snippets.directory).as_posix())


# Below ROOT: the installation's own copy of the running package, which the wrapper runs.
DEVPRO_COPY = f"{TOOLS_DIR}/devpro"
# Every package an install may ship: an owned one where its owner renders, on a project install alone,
# and an ownerless one — the devpro tools package's — on every install, user-level included. A
# destination is a consumer contract — a skill names its own tools relative to its directory, and an
# installed runner line names its snippets directory — so each is stated, never derived.
# `package_copies`, the `!INSTALLED!` stamping and the runner include lines all read this table; the
# include lines land in its order.
SHIPPED_PACKAGES: tuple[ShippedPackage, ...] = (
    ShippedPackage("development-tools", DEVELOPMENT_SCRIPTS_PACKAGE, "development"),
    ShippedPackage(
        "runner-snippets",
        f"{TOOLS_DIR}/runner-snippets",
        None,
        SnippetSet("devpro", ".", {"just": "devpro.just", "make": "devpro.mk"}),
    ),
    ShippedPackage(".", DEVPRO_COPY, None, stamps=False),
    ShippedPackage(
        "kb-tools",
        KB_TOOLS_DIR,
        KBASE_OWNER,
        SnippetSet("kb", "runner-snippets", {"just": "kb.just", "make": "kb.mk"}),
    ),
)
# The harness resources: files a harness ships that land in ROOT as they stand, copied and never
# rendered. The directory below this one in the source is the harness's own
# name, and the destination is ROOT itself — both stated, neither derived from a directory listing.
HARNESS_RESOURCES_SOURCE = "harnesses/resources"
# The interpreter the install-time probe runs a guardrail hook script under, found on PATH, and how long
# that run may take before it counts as failed.
GUARDRAIL_INTERPRETER = "perl"
GUARDRAIL_PROBE_SECONDS = 5.0
# Copied package files of a script or build-file type carry the one-line installed banner: by suffix,
# or by name for an extensionless script. Every other file — a `.gitignore` among them — is copied
# byte-verbatim.
STAMPED_SUFFIXES = frozenset({".py", ".sh", ".mk", ".just"})
STAMPED_NAMES: frozenset[str] = frozenset()
_INSTALLED_NOTICE = GENERATED_NOTICE


# The wrapper `tools/devpro.sh`, its `@INTERPRETER@` slot filled with the shell-quoted path of the
# Python that ran the install. It is bash and Python at once: bash reads `''':'` as `:` and execs the
# interpreter on this same file, which Python reads with the bash lines as one string. Run as a script,
# the file's own directory, `tools/`, leads `sys.path`, where `-m` would put the working directory
# first and run a `devpro` package there in the copy's place; a separate bootstrap script would be one
# more installed file. The bash lines must hold no `'''` and no backslash. `${@+"${@}"}` because bash
# 3.2, macOS's `/bin/bash`, reads an empty `"${@}"` as unbound under `set -u`.
#
# The wrapper states no floor: `devpro/__init__.py` refuses below it before any other module of the
# copy is imported. An interpreter older than 3.12 reads the bash lines as the literal's own text,
# consuming each backslash escape: the bash lines round it carry no `\` and no `%`. One consequence of
# that read: an interpreter older than 3.12 reached some way the entry point could not refuse prints
# bash's own `import: command not found`, not a floor message.
_WRAPPER_TEXT = """\
#!/usr/bin/env bash
''':'
# Runs this installation's own copy of devpro, the `devpro/` beside this file, as `python3 -m devpro`
# runs it: under the Python that ran the install while that path exists, else under the first
# `python3` on PATH. It looks for no other interpreter.
set -euo pipefail

recorded=@INTERPRETER@
here=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "${recorded}" ]]; then
  python="${recorded}"
else
  python=$(command -v python3)
fi
export PYTHONPATH="${here}${PYTHONPATH:+:${PYTHONPATH}}"
exec "${python}" "${BASH_SOURCE[0]}" ${@+"${@}"}
'''
import runpy

runpy.run_module("devpro", run_name="__main__", alter_sys=True)
"""


def base_interpreter() -> str:
    """The Python running this process as it stands outside any virtual environment: a venv's python is
    gone with the venv, while the interpreter it was made from outlives it.

    `sys._base_executable` is CPython's own answer to this: for a venv, the base interpreter it was
    made from (`--copies` alike); outside one, the interpreter itself. The leading underscore marks it
    documented but not guaranteed stable across releases, so it is read here and nowhere else."""
    return str(Path(sys._base_executable))  # type: ignore[attr-defined]  # CPython's own, documented above


def wrapper_text(interpreter: str) -> str:
    """The wrapper's text, recording `interpreter` as the Python it runs the copy under."""
    return _WRAPPER_TEXT.replace("@INTERPRETER@", shlex.quote(interpreter))


def _installed_version(init: Path) -> str | None:
    """The `__version__` an installed copy's `__init__.py` assigns, or None where it holds none or
    cannot be read."""
    try:
        text = init.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    match = re.search(r'^__version__ = "([^"]*)"$', text, re.MULTILINE)
    return match.group(1) if match else None


def _wheel_files(root: Path) -> list[Path]:
    """Every file below a staging source, `__pycache__` directories left out: bytecode is no wheel
    content, and a pip-compiled install of the wheel holds some the wheel itself does not."""
    return [
        path for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.relative_to(root).parts
    ]


def package_copies(root: Path, package: ShippedPackage) -> list[tuple[Path, Path]]:
    """(source file, target under `root`) for every file `package` delivers, each landing under its
    destination. The source is the running package's own content. Built, that content is the wheel's:
    the wheel's file set is what a consumer install writes, the build is the one filter over it, and
    `.dist-info/RECORD` is that content's manifest. Run from a checkout (`PYTHONPATH=<clone>`), the
    source is the clone's tree as it stands, a `__pycache__` directory left out."""
    source_root = PACKAGE_ROOT / package.source
    return [
        (source, root / package.destination / source.relative_to(source_root)) for source in _wheel_files(source_root)
    ]


def harness_resource_copies(root: Path, *, harness: str) -> list[tuple[Path, Path]]:
    """(source file, target under `root`) for every file `harness` ships: `resources/<harness>/` as
    the wheel carries it, delivered into ROOT, so `resources/claude/hooks/guardrail.pl` lands at
    `<ROOT>/hooks/guardrail.pl`.

    These files are the harness's own, not this repository's generated product: each is copied
    byte-verbatim with its mode preserved and nothing else — no `!INSTALLED!` banner, no stamping. Each
    carries its own `!INSTALLED! … devpro` header in its first ten lines, as shipped: it tells an
    operator the source is elsewhere, and no install reads one back. A harness shipping no resources
    directory copies nothing, which is not an error. No harness's list reaches another harness's
    directory: opencode's capture is its plugin's own, and the profiler's resources are gone.

    What lands here stays only as long as the release ships it: the next install's wholesale
    replacement of ROOT removes a resource file this repository drops, and everything else standing
    beside it."""
    source = PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / harness
    return _harness_resource_pairs(source, root)


def _harness_resource_pairs(source: Path, root: Path) -> list[tuple[Path, Path]]:
    """(source file, target under `root`) for every file below `source`, each landing at its path
    relative to `source`. Nothing where `source` is absent, which is not an error."""
    if not source.is_dir():
        return []
    return [(path, root / path.relative_to(source)) for path in _wheel_files(source)]


def stamped(data: bytes, *, origin: str) -> bytes:
    """`data` with the one-line installed banner on top, or below its shebang line."""
    banner = f"# {install_base.INSTALLED_MARK} from {origin} — {_INSTALLED_NOTICE}\n".encode("utf-8")
    if not data.startswith(b"#!"):
        return banner + data
    shebang, _, rest = data.partition(b"\n")
    return shebang + b"\n" + banner + rest


def _is_our_harness_file(path: Path, *, marker: str) -> bool:
    """A harness-rendered file this repository wrote: the marker the file states about itself appears in
    it. A file that cannot be read or decoded is not ours. Its one reader is `_report_shadowing`, which
    reads a user harness directory outside the replacement: no install gates a write or a removal on it."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return marker in text


def _guardrail_probe(script: Path, *, project: Path) -> str | None:
    """None when `script`, run once under `GUARDRAIL_INTERPRETER` on a command it allows — a redirect
    into `clauses.PROJECT_TEMP_DIR` — exits 0 within `GUARDRAIL_PROBE_SECONDS`; otherwise why it did not:
    the exit status and the first stderr line, the timeout, or the `OSError` raised starting the
    interpreter. The argv runs with no shell, so a missing
    interpreter raises rather than exiting 127, and `CLAUDE_PROJECT_DIR` is removed so the hook reads
    the root from the input, as it does when that variable is unset."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": f"echo x > {clauses.PROJECT_TEMP_DIR}/probe"},
        "cwd": str(project),
    }
    env = {name: value for name, value in os.environ.items() if name != "CLAUDE_PROJECT_DIR"}
    argv = [GUARDRAIL_INTERPRETER, str(script)]
    try:
        result = subprocess.run(
            argv,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            check=False,
            timeout=GUARDRAIL_PROBE_SECONDS,
        )
    except OSError as exc:
        return f"'{GUARDRAIL_INTERPRETER}' could not be run: {exc}"
    except subprocess.TimeoutExpired:
        return f"'{' '.join(argv)}' did not exit within {GUARDRAIL_PROBE_SECONDS:g} seconds"
    if result.returncode == 0:
        return None
    first = next(iter(result.stderr.splitlines()), "")
    return f"'{' '.join(argv)}' exited {result.returncode}: {first}"


def _lexical(path: Path) -> Path:
    """`path` made absolute and normalized."""
    return Path(os.path.normpath(path.absolute()))


def _harness_relpath(root: Path, project: Path) -> str:
    """ROOT's path relative to the project root, both as spelled — the `<harness-relpath>` every
    consumer-facing line under the project spells."""
    return _lexical(root).relative_to(project).as_posix()


def _installs_agents_file(harness_dir: Path, harness: Harness, *, project: Path) -> bool:
    """Whether an install into `harness_dir` writes an agents file there: a harness-directory plugin installed
    below its project root, judged as both are spelled."""
    return harness.is_harness_dir_plugin and _lexical(harness_dir) != project


def _is_project_install_of_a_nested_plugin(harness: Harness, *, user_level: bool) -> bool:
    """Whether an install is a project install of a nested plugin. Such an install keeps the agents-file
    block current in the one place it lives and, for each shipped package carrying runner snippets,
    writes its include line in the project's runner file. A harness-directory plugin's agents file is its
    own, and it is no repo project, so it has no consumer runner file and none is created."""
    return not user_level and not harness.is_harness_dir_plugin


def _guardrail_in_play(harness: Harness, *, user_level: bool) -> GuardrailHook | None:
    """The guardrail hook an install delivers, before the probe decides whether it registers: the
    harness's own on a project install, none on a user-level one."""
    return None if user_level else harness.guardrail


def _resource_copies(root: Path, *, harness: Harness, user_level: bool) -> list[tuple[Path, Path]]:
    """The harness resources an install copies: every one on a project install, and on a user-level one
    the entry that registers the plugin and the guardrail resource beside it — opencode's `index.ts` and
    `guardrail.ts` — so the entry runs the guardrail at user level as it does in a project. A harness
    with no entry copies nothing at user level."""
    copies = harness_resource_copies(root, harness=harness.name)
    if not user_level:
        return copies
    if not harness.entry_resource:
        return []
    entry = PurePosixPath(harness.entry_resource)
    beside_the_entry = {entry.as_posix(), (entry.parent / GUARDRAIL_RESOURCE).as_posix()}
    return [(source, target) for source, target in copies if target.relative_to(root).as_posix() in beside_the_entry]


GUARDRAIL_RESOURCE = "guardrail.ts"
"""The guardrail resource an entry that registers itself runs from beside itself."""


def is_the_running_copy(root: Path) -> bool:
    """Whether `root`'s devpro copy is the package this install runs from: its resolved destination is the
    running package's source. An install from an installation's own copy into the installation holding that
    copy — a re-entry run — passes over that copy and the wrapper that runs it: the replacement leaves
    the copy's own files and the wrapper standing, so the copy the run executes from stays whole."""
    return (root / DEVPRO_COPY).resolve() == PACKAGE_ROOT


def _refuse_symlinked_copy(root: Path) -> None:
    """Refuse an install whose devpro-copy destination is a symlink. `is_the_running_copy` reads that
    destination resolved and the replacement's pass-over reads it as it resolves, so a link there lets
    the pass-over's two paths be defeated — the copy cleared and rewritten through the link into whatever
    it names. Refuse, naming the link, before either reads it."""
    copy = root / DEVPRO_COPY
    if copy.is_symlink():
        raise InputError(
            f"install refuses '{copy}': the copy destination is a symlink, not a real directory — an "
            "install would clear and write through it into whatever it names; remove the link, then "
            "re-install; nothing written"
        )


def _refuse_symlinked_install_directory(root: Path) -> None:
    """Refuse an install whose install directory is a symlink: the wholesale replacement would clear and
    write through the link into whatever it names. Decided on the real paths, before anything is
    written, as the devpro copy's own refusal is."""
    if root.is_symlink():
        raise InputError(
            f"install refuses '{root}': the install directory is a symlink, not a real directory — the "
            "install replaces its contents wholesale and would clear and write through the link into "
            "whatever it names; remove the link, then re-install; nothing written"
        )


def _replaced(root: Path, *, keep: frozenset[str]) -> None:
    """Empty the install directory for the fresh tree: every entry below `root` removed — a directory
    tree removed, any other entry unlinked, a symlink unlinked as the link it is and never followed —
    save the paths `keep` names, relative to `root`, which stand as they are, and a directory `keep`
    names or holds a path below: that one is walked, so a file beside the kept ones goes like any other.
    `root` itself stays. No error is swallowed: an `OSError` propagates, and the install stops rather
    than writing over what it could not clear."""
    if root.is_dir():
        _replaced_below(root, prefix="", keep=keep)


def _replaced_below(directory: Path, *, prefix: str, keep: frozenset[str]) -> None:
    """`_replaced` for one directory of the walk, `prefix` its path relative to the install directory."""
    for entry in directory.iterdir():
        relative = f"{prefix}{entry.name}"
        if entry.is_symlink() or not entry.is_dir():
            if relative not in keep:
                entry.unlink()
        elif any(kept.startswith(f"{relative}/") for kept in keep) or relative in keep:
            # A directory on the way to a kept path, or one `keep` names: it stands, and everything inside
            # it that `keep` does not name goes — a stale bytecode file beside the copy's own files is no
            # passed-over path.
            _replaced_below(entry, prefix=f"{relative}/", keep=keep)
        else:
            shutil.rmtree(entry)


def _re_entry_kept(copy: Path) -> frozenset[str]:
    """The paths a re-entry run's replacement passes over, relative to the install directory: the devpro
    copy's own files — the tree its `SHIPPED_PACKAGES` row ships, `_wheel_files`' filter applied to the
    copy the run executes from — and the wrapper that runs it. The row ships a filtered tree, never the
    copy's listing, so a stale bytecode file beside the copy's own files is no passed-over path.
    Everything else inside the copy's tree goes with the tree."""
    row = next(package for package in SHIPPED_PACKAGES if package.destination == DEVPRO_COPY)
    shipped = (path for path in _wheel_files(copy / row.source) if path.suffix != ".pyc")
    own = (path.relative_to(copy / row.source).as_posix() for path in shipped)
    return frozenset({*(f"{DEVPRO_COPY}/{relative}" for relative in own), WRAPPER})


def _write_created(target: Path, data: bytes, *, mode: int) -> None:
    """Write `data` to `target`, its parents created, asking for `mode` at creation: a `chmod` after the
    write would ignore the umask."""
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)


def _package_copy_mode(source: Path) -> int:
    """The mode a package copy asks the OS for when it creates a file from `source`: a new file's, plus
    `source`'s execute bits. Group and other bits are left to the process umask, which a `chmod` after
    the write would ignore."""
    return 0o666 | (stat.S_IMODE(source.stat().st_mode) & 0o111)


def _report_shadowing(root: Path, *, harness: Harness, files: Iterable[HarnessFile], user_level: bool) -> None:
    """Report a plugin the harness loads in place of another of the same name, for a harness whose
    user-level plugin does so: a user-level install always shadows every project's; a project install
    is shadowed where the user-level ROOT holds every one of `files`, the harness's own files this
    install renders, each carrying the marker that makes it ours."""
    if not harness.user_plugin_shadows:
        return
    if user_level:
        report_left_alone(
            f"{root} is user-level: the harness loads it in place of every project's plugin of the same name"
        )
        return
    user_root = harness.user_dir / harness.plugin_dir
    if all(_is_our_harness_file(user_root / file.path, marker=file.marker) for file in files):
        report_left_alone(
            f"{root} is shadowed by {user_root}, a user-level plugin of the same name: the harness loads that "
            "one, and this project's plugin — its tuning, version and MCP server — does not load"
        )


def install(
    harness_dir: Path,
    ctx: Render,
    *,
    verbose: bool,
    project_root: Path | None = None,
    uncommitted: Callable[[], tuple[str, ...]],
    real_harness_dir: Path | None = None,
    real_project: Path | None = None,
    global_dir: Path | None = None,
    store_migration: Callable[[Path], list[str]] | None = None,
) -> None:
    """Install the set `ctx` renders into ROOT, `harness_dir / ctx.bound_harness.plugin_dir`. Every
    check runs first, so a refusal writes nothing; then the writes; then the removals.

    `verbose` prints each file written. `project_root` is the project the harness directory belongs to,
    defaulting to `harness_dir`. `uncommitted` names the uncommitted changes to the sources, called only
    where a write must refuse on them. `real_harness_dir` and `real_project` are the harness directory
    and project root the install is for, where `harness_dir` and `project_root` are a scratch copy of
    them, each defaulting to the path written. `global_dir` is the harness's user harness directory, or a
    scratch copy of it, defaulting to the directory itself. `store_migration` renames a project's
    `claude-profiler` and `opencode-profiler` stores to their `.profiler-*` names, called for the project
    written and returning the lines the report names; where not given it is the project's stores renamed
    once (`_one_project_renamed_once`), so a run's preflight scratch copy is renamed and no second call
    renames what the report already named."""
    root = harness_dir / ctx.bound_harness.plugin_dir
    project = _lexical(harness_dir if project_root is None else Path(project_root))
    user_level = ctx.harness.name in user_dir_harnesses(harness_dir if real_harness_dir is None else real_harness_dir)
    harness_relpath = _harness_relpath(root, project)
    # Every check runs before the replacement and the first write: a symlinked copy destination and a
    # symlinked install directory, the running copy's own installation, the render, the guardrail probe
    # that decides whether its script is a copy, the runner file where a shipped package carries runner
    # snippets, and the agents file's. ROOT itself is created only after all of them.
    real_root = (harness_dir if real_harness_dir is None else real_harness_dir) / ctx.bound_harness.plugin_dir
    _refuse_symlinked_copy(real_root)
    _refuse_symlinked_install_directory(real_root)
    re_entry = is_the_running_copy(real_root)
    renders = render_all(ctx)
    packages = [
        package
        for package in SHIPPED_PACKAGES
        if package.owner is None or (not user_level and ctx.plugin.ships(package.owner))
    ]
    if re_entry:
        # A re-entry run passes over the copy it runs from: dropping its row keeps its files from being
        # rewritten. The replacement passes over them too, by path (`_re_entry_kept`).
        packages = [package for package in packages if package.destination != DEVPRO_COPY]
    package_files = [
        (package, source, target) for package in packages for source, target in package_copies(root, package)
    ]
    resource_files = _resource_copies(root, harness=ctx.harness, user_level=user_level)
    guardrail = _guardrail_in_play(ctx.bound_harness, user_level=user_level)
    snippet_sets = [snippets for package in packages if (snippets := package.installed_snippets()) is not None]
    # A project install of a nested plugin touches the project's runner file: it writes each shipped
    # set's include line, whichever shipped packages it carries. Its scratch directory and `.gitignore`
    # line are prepared on the same condition but not by this write: a project already holding the line
    # writes nothing here and is still prepared below. Nothing else — a mage or user-level install —
    # reads or writes any of them.
    nested_project_install = _is_project_install_of_a_nested_plugin(ctx.harness, user_level=user_level)
    guardrail_skipped: str | None = None
    own_files = shipped_harness_files(ctx)
    guardrail = _guardrail_in_play(ctx.bound_harness, user_level=user_level)
    if guardrail is not None:
        script = PACKAGE_ROOT / HARNESS_RESOURCES_SOURCE / ctx.harness.name / guardrail.script
        guardrail_skipped = _guardrail_probe(script, project=project)
        if guardrail_skipped is not None:
            resource_files = [(source, target) for source, target in resource_files if source != script]
        # The registration is written on every install, holding what the file holds without the hook
        # where the probe fails: a render is replaced whole, so a later probe failure rewrites it.
        registration = guardrail.registration if guardrail_skipped is None else guardrail.registration_without_hook
        renders = (*renders, (PurePosixPath(registration.path), harness_file_text(registration, ctx)))
    registers_the_hook = guardrail is not None and guardrail_skipped is None
    # Everything this install copies, the wrapper with it, in one list for the report and for verbose's
    # write log. A re-entry run writes neither the copy (dropped from `packages` above) nor the wrapper.
    wrapper = root / WRAPPER
    copied = [
        *(target for _, _, target in package_files),
        *(() if re_entry else (wrapper,)),
        *(target for _, target in resource_files),
    ]
    if nested_project_install:
        check_runner(project)
    agents_file: AgentsFileWrite | None = None
    if _installs_agents_file(harness_dir, ctx.harness, project=project):
        agents_file = checked_agents_file(harness_dir, ctx.harness, ctx.plugin, real_directory=real_harness_dir)
    followed: FollowedAgentsFile | None = None
    if _is_project_install_of_a_nested_plugin(ctx.harness, user_level=user_level):
        followed = checked_followed_agents_file(
            project,
            ctx.harness,
            ctx.plugin,
            global_dir=ctx.harness.user_dir if global_dir is None else global_dir,
            uncommitted=uncommitted,
            real_project=real_project,
        )

    root.mkdir(parents=True, exist_ok=True)
    # The version the report names is the one standing before the replacement: the copy it names is
    # removed by the replacement a moment later.
    replaced_version = _installed_version(root / DEVPRO_COPY / "__init__.py")
    pass_over: frozenset[str] = frozenset()
    if re_entry:
        pass_over |= _re_entry_kept(root / DEVPRO_COPY)
    if agents_file is not None:
        pass_over |= {path.relative_to(root).as_posix() for path in agents_file.paths if path.is_relative_to(root)}
    _replaced(root, keep=pass_over)
    for package, source, target in package_files:
        data = source.read_bytes()
        if package.stamps and (source.suffix in STAMPED_SUFFIXES or source.name in STAMPED_NAMES):
            data = stamped(data, origin=source.relative_to(PACKAGE_ROOT.parent).as_posix())
        _write_created(target, data, mode=_package_copy_mode(source))
    if not re_entry:
        # A re-entry run passes over the wrapper that runs its own copy, leaving the installed one in
        # place rather than rewriting it.
        wrapper_data = wrapper_text(base_interpreter()).encode("utf-8")
        _write_created(wrapper, stamped(wrapper_data, origin=f"{PACKAGE_ROOT.name}/install.py"), mode=0o777)
    for source, target in resource_files:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        shutil.copymode(source, target)
    written = write_renders(root, renders)
    if agents_file is not None:
        write_agents_file(agents_file)
    if followed is not None:
        write_followed_agents_file(followed)

    print(f"installed: {len(written)} rendered files, {len(copied)} copied files → {root}")
    copy_dir = root / DEVPRO_COPY
    if not re_entry:
        # A re-entry run passes over the copy, so neither sentence about it prints: each names the copy's
        # destination, one of the two passed-over paths.
        if replaced_version is None:
            print(f"devpro {__version__} installed → {copy_dir}")
        else:
            print(f"devpro {replaced_version} replaced by devpro {__version__} → {copy_dir}")
    if verbose:
        for path in [*copied, *written]:
            print(f"wrote {path}")
    if nested_project_install:
        install_include_lines(project, snippet_sets, harness_relpath=harness_relpath)
    # The preparation is the install's, not the runner file's: a project already holding the line writes
    # nothing there, and the scratch directory is still the install's to keep ready. Its idempotence is
    # what leaves a prepared `.gitignore` as it stands.
    if nested_project_install:
        prepare_scratch_directory(project)
    # The profiler's stores from before their rename, for the project written: the preflight's scratch run
    # renames its copy, which is what shows the preflight a move, and the real project is renamed once.
    # Called straight, with no migration passed, this call is the only one, so it makes the one rename.
    for line in (store_migration or _one_project_renamed_once(project))(project):
        print(line)
    if guardrail is not None and not registers_the_hook:
        # The replacement removed any earlier install's script, so none stands after the run; the skip
        # and its reason are reported, and no path.
        report_left_alone(f"guardrail hook skipped, neither installed nor registered: {guardrail_skipped}")
    _report_shadowing(root, harness=ctx.bound_harness, files=own_files, user_level=user_level)
    if ctx.harness.reload_rule:
        print(ctx.harness.reload_rule)


def _install_managed_paths(
    harness_dir: Path,
    ctx: Render,
    *,
    project: Path,
    user_level: bool,
) -> list[tuple[Path, list[str]]]:
    """(base, paths relative to it) for everything an install of `ctx` into `harness_dir` may read or
    write: the project root as spelled, the harness directory, ROOT and the harness's user harness
    directory, in that order, ROOT keeping its position below the harness directory.

    ROOT is managed whole: the replacement removes every entry below it, so the managed set is every one
    of them — the re-entry pass-over trees and, under mage, the agents file's path included, each staged
    as it stands — and the preflight's comparison reads the removals the replacement makes against that
    whole staging. The bases outside it keep the paths they name — the runner file and the runner-file
    names, the scratch `.gitignore`, the agents files, the stores' rename pairs — so every write outside
    the replacement stays predicted. Each decision the install takes on what only its run knows — the
    guardrail probe, the re-entry judgment — is taken here as though it went the way that writes more;
    the pass-over itself lives in the replacement's exclusions, not in this set."""
    harness, bound = ctx.harness, ctx.bound_harness
    root = harness_dir / bound.plugin_dir
    under_harness_dir: list[str] = []
    under_project: list[str] = []
    if _is_project_install_of_a_nested_plugin(harness, user_level=user_level):
        under_project += [
            *JUSTFILE_NAMES,
            *MAKEFILE_NAMES,
            # The `.gitignore` line a project install prepares: a file that may be absent, which the
            # copy makes where the real project holds nothing. The scratch directory is not managed:
            # the install creates it where missing and the prediction does not contemplate it.
            ".gitignore",
        ]
    # The profiler's stores: each old-pattern one the install renames, and the name it renames to, so the
    # preflight sees the move it would make rather than reporting the target up to date.
    store_dir = TRACE_DIR.parent.as_posix()
    renamed = [
        (f"{store_dir}/{store}{OLD_STORE_SUFFIX}", f"{store_dir}/{NEW_STORE_PREFIX}{store}") for store in OLD_STORES
    ]
    under_project += [path for pair in renamed for path in pair]
    if _installs_agents_file(harness_dir, harness, project=project):
        write = checked_agents_file(harness_dir, harness, ctx.plugin)
        under_harness_dir += [path.relative_to(harness_dir).as_posix() for path in write.paths]
    global_dir = harness.user_dir
    under_global_dir: list[str] = []
    if _is_project_install_of_a_nested_plugin(harness, user_level=user_level):
        followed = checked_followed_agents_file(
            project, harness, ctx.plugin, global_dir=global_dir, uncommitted=lambda: ()
        )
        for path in followed.paths:
            if path.is_relative_to(project):
                under_project.append(path.relative_to(project).as_posix())
            else:
                under_global_dir.append(path.relative_to(global_dir).as_posix())
    return [
        (project, under_project),
        (harness_dir, under_harness_dir),
        (root, _every_entry_below(root)),
        (global_dir, under_global_dir),
    ]


def _every_entry_below(root: Path) -> list[str]:
    """Every entry below `root`, relative to it: each directory and each file, the tree below a directory
    walked and its entries named one by one, so an obstacle an install's checks read anywhere in the tree
    stands in the copy at its own path. A symlink to a directory is named as the link it is and not
    entered, which is what keeps the walk off what it points at; every other directory is walked into.
    Nothing where `root` is absent, nothing where it is a symlink, and `root` itself where it is a file,
    which the install's own refusal reads."""
    if root.is_symlink():
        return []
    if not root.is_dir():
        return [root.as_posix()] if root.exists() else []
    entries: list[str] = []
    for directory, subdirs, names in os.walk(root):
        links = [name for name in subdirs if Path(directory, name).is_symlink()]
        subdirs[:] = sorted(name for name in subdirs if name not in links)
        entries += [Path(directory, name).relative_to(root).as_posix() for name in [*subdirs, *links]]
        entries += [Path(directory, name).relative_to(root).as_posix() for name in sorted(names)]
    return entries


def preflighted_install(
    harness_dir: Path,
    ctx: Render,
    *,
    verbose: bool,
    project_root: Path | None = None,
    uncommitted: Callable[[], tuple[str, ...]],
    dry_run: bool = False,
    store_migration: Callable[[Path], list[str]] | None = None,
) -> None:
    """`install` behind the preflight: run first into a scratch copy of the paths it manages, with the
    real harness directory and project root as its identity. Where that changed nothing, the harness
    directory is reported up to date and nothing in the target is touched — no file, no package
    destination, no `.venv`. With `dry_run`, what would be created, changed and removed is printed
    relative to the project root, and nothing is written. Otherwise the install runs exactly as
    `install` does. Every printed path and refusal names the real target. `store_migration` is
    `install`'s, defaulting to the project's stores renamed once; a run installing for several harnesses
    passes one shared across them, so the real project is renamed by its first real run alone."""
    project = _lexical(harness_dir if project_root is None else Path(project_root))
    user_level = ctx.harness.name in user_dir_harnesses(harness_dir)
    managed = _install_managed_paths(harness_dir, ctx, project=project, user_level=user_level)
    run_preflighted(
        managed,
        install=lambda bases: install(
            bases[1],
            ctx,
            verbose=verbose,
            project_root=bases[0],
            uncommitted=uncommitted,
            real_harness_dir=harness_dir,
            real_project=project,
            global_dir=bases[3],
            # One harness per run, so one rename: the preflight's scratch run renames its own copy, and
            # the real run renames the real project.
            store_migration=store_migration or _one_project_renamed_once(project),
        ),
        dry_run=dry_run,
        target=harness_dir,
        report_root=project,
        # The scratch directory's creation is the install's own conditional, not a managed path: named
        # in the prediction where the real tree lacks it, created by the run itself.
        prepared_directories=(
            (scratch,)
            if (scratch := project / clauses.PROJECT_TEMP_DIR)
            and not scratch.exists()
            and _is_project_install_of_a_nested_plugin(ctx.harness, user_level=user_level)
            else ()
        ),
    )


def _one_project_renamed_once(project: Path) -> Callable[[Path], list[str]]:
    """The stores' rename for one project, called by `install` itself where no migration was passed: the
    preflight's scratch runs rename their own copies, and the real project is renamed by the first real
    call alone, so a run for several harnesses finds nothing to move on the second and the report names
    each rename once. A call renaming inline in `install` passes no migration, and this is the migration
    it makes, so the policy holds whichever caller reaches `install`."""
    renamed = False

    def rename(directory: Path) -> list[str]:
        nonlocal renamed
        in_preflight = Path(directory).resolve() != project.resolve()
        if renamed and not in_preflight:
            return []
        renamed = renamed or not in_preflight
        return migrate_stores(directory)

    return rename


INSTALL_SETTINGS = ("always", "detect", "never")
"""The devpro settings file's `install` setting, per harness: `always` installs for it whatever the target
holds, `detect` where the target holds its own harness directory, `never` installs nothing for it."""
DEFAULT_INSTALL_SETTING = "detect"
"""The setting for a harness the file names without an `install` key."""


def _install_setting(entry: HarnessSettings) -> str:
    """The harness's setting: its `install` value as written, `detect` where the file sets none."""
    return DEFAULT_INSTALL_SETTING if entry.install is None else entry.install


def components_value(components: str | None, settings: Mapping[str, HarnessSettings] | None, harness: str) -> str:
    """The component list the install for `harness` takes: `--components` given, else the devpro settings
    file's value for that harness, else none."""
    if components is not None:
        return components
    entry = None if settings is None else settings.get(harness)
    return "" if entry is None or entry.components is None else entry.components


def install_selected(
    target: Path,
    settings: Mapping[str, HarnessSettings],
    *,
    path: Path | None,
    tuned: Callable[[str, MapSupply | None, str], Render],
    components: str | None,
    subdir: str | None,
    verbose: bool,
    dry_run: bool,
    uncommitted: Callable[[], tuple[str, ...]],
) -> None:
    """Install for every harness the devpro settings file names, in name order, each as its own install:
    the setting judged first — `never` skips, `detect` where the target holds the harness's own harness
    directory — then the harness's target resolved and its render built by `tuned` from its map and its
    component list, `components` replacing the file's wherever it is given. The target's existence and
    `--subdir`'s reach into it are refused before the file's harnesses are judged, so the refusals hold
    whatever the settings say. A file naming no harness installs nothing, and reports the file's path and
    the ways an install happens, on stderr, and returns without writing. Every named harness's setting is
    judged against `INSTALL_SETTINGS` before anything is written. The loop stops at the first refusal,
    naming the harness that refused; earlier harnesses' installs stand."""
    require_existing_target(target)
    require_outside_package_source(target)
    if subdir is not None:
        require_subdir_inside(subdir)
    if not settings:
        report_left_alone(
            f"nothing installed: '{path}' names no harness — pass --harness=NAME; or add the harness to the "
            f"file, either table of it: install = always in [<harness>] installs whatever the target holds, "
            f"and the detect default installs where the target holds the harness's own directory (create that "
            f"directory where absent)"
        )
        return
    settings_by_harness = {name: _install_setting(entry) for name, entry in sorted(settings.items())}
    for name, setting in settings_by_harness.items():
        if setting not in INSTALL_SETTINGS:
            raise InputError(
                f"devpro settings file '{path}', table '[{name}]': install '{setting}' is not one of "
                f"{', '.join(INSTALL_SETTINGS)}; nothing written"
            )
    store_migrations: dict[Path, Callable[[Path], list[str]]] = {}
    for name, setting in settings_by_harness.items():
        if setting == "never":
            continue
        if setting == "detect" and not target_holds_harness_dir(target, harness_named(name)):
            continue
        entry = settings[name]
        chosen = components_value(components, settings, name)
        try:
            resolved = resolve_install_target(target, harness=name, plugin=NAME, subdir=subdir)
            # One rename per project across the loop: the second harness's install must not move a store
            # the first run's report already named.
            migration = store_migrations.setdefault(
                resolved.project_root, _one_project_renamed_once(resolved.project_root)
            )
            preflighted_install(
                resolved.harness_dir,
                tuned(name, entry.supply, chosen),
                verbose=verbose,
                project_root=resolved.project_root,
                uncommitted=uncommitted,
                dry_run=dry_run,
                store_migration=migration,
            )
        except InputError as exc:
            raise InputError(f"harness '{name}': {exc}") from exc
