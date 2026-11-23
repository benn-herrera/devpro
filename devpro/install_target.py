"""Where an install lands: the harness, the harness directory and the project root, resolved from the
target an operator names, without writing anything. ROOT, where the set is written, is not decided
here, nor whether the install is user-level: `install` derives both from the harness directory and the
harness.

The harness is, in order: the one `--harness` names; the one whose harness directory sits inside the
target — its project harness directory, or, in the home directory, its user harness directory; the
one the target itself is a harness directory of, matched on the target's trailing path elements;
otherwise none, and the install is refused. Held to one harness, the same values answer whether a target
holds its harness directory (`target_holds_harness_dir`), the `detect` install setting's judgment. Every
directory name is read from the harnesses' own values, so none is spelled here. The target is normalized
lexically, for that matching and for the harness directory and project root built from it; it is resolved
only where it is compared with the home directory, so two spellings of home compare equal. A target that
resolves into the running devpro package's own source — `install_base.PACKAGE_ROOT`, the directory the
package was imported from — is refused: an install there writes the set into the package it is reading,
and an editable install then serves that set as the package's own.
"""

import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from devpro.context import harness_named, harnesses
from devpro.errors import InputError
from devpro.harness import Harness
from devpro.install_base import PACKAGE_ROOT

_HOME_PREFIX = "~/"


@dataclass(frozen=True)
class InstallTarget:
    """A resolved install: the harness's name; and the harness directory and the project root, each
    built from the target normalized."""

    harness: str
    harness_dir: Path
    project_root: Path


def _user_dir_in_home(harness: Harness) -> str | None:
    """`harness`'s user harness directory relative to the home directory, None where it is not one."""
    home = harness.user_harness_dir
    return home.removeprefix(_HOME_PREFIX) if home.startswith(_HOME_PREFIX) else None


def _dir_inside(harness: Harness, *, at_home: bool) -> str | None:
    """The directory whose presence inside a target selects `harness`: its user harness directory in
    the home directory, its project harness directory anywhere else, and never a plugin's."""
    if at_home:
        return _user_dir_in_home(harness)
    return None if harness.is_harness_dir_plugin else harness.project_harness_dir


def _own_dir_names(harness: Harness) -> tuple[str, ...]:
    """The trailing paths a directory that is itself `harness`'s harness directory ends in. A harness-directory
    plugin's project harness directory is its own name, which a clone of this repository also bears, so
    such a plugin is known only by the directory its plugins sit in."""
    if harness.is_harness_dir_plugin:
        return (harness.plugin_parent_dir,) if harness.plugin_parent_dir else ()
    in_home = _user_dir_in_home(harness)
    return (harness.project_harness_dir, *(() if in_home is None else (in_home,)))


def _is_own_dir(target: Path, harness: Harness) -> bool:
    """Whether the normalized `target` ends in one of `harness`'s own directory names."""
    return any(
        target.parts[-len(trailing) :] == trailing
        for trailing in (PurePosixPath(name).parts for name in _own_dir_names(harness))
    )


def _lexical_target(target: Path) -> tuple[Path, bool]:
    """`target` made absolute with `..` collapsed, and whether it is the home directory."""
    normalized = Path(os.path.normpath(target.absolute()))
    return normalized, normalized.resolve() == Path.home().resolve()


def require_existing_target(target: Path) -> None:
    """Refuse `target` where it is not an existing directory, naming an unexpanded `~` as the cause."""
    if target.is_dir():
        return
    cause = "'~' was not expanded; pass an absolute path" if target.parts[:1] == ("~",) else "create the project first"
    raise InputError(f"install target '{target}' is not an existing directory — {cause}")


def require_outside_package_source(target: Path) -> None:
    """Refuse `target` where it resolves to the running package's source or into it, naming the boundary:
    an install there would overwrite or prune the very set `devpro` is."""
    resolved = target.resolve()
    if resolved == PACKAGE_ROOT or resolved.is_relative_to(PACKAGE_ROOT):
        raise InputError(
            f"install target '{target}' is the running devpro package's source, {PACKAGE_ROOT}, or inside it: an "
            "install there would write into the package running it — name a project outside it; nothing written"
        )


def require_subdir_inside(subdir: str) -> None:
    """Refuse `subdir` where it is an absolute path or, normalized, climbs out of the target."""
    normalized = os.path.normpath(subdir)
    if os.path.isabs(subdir) or normalized == ".." or normalized.startswith("../"):
        raise InputError(f"--subdir '{subdir}' must name a directory inside the target — nothing written")


def target_holds_harness_dir(target: Path, harness: Harness) -> bool:
    """Whether `target` holds `harness`'s own harness directory — its user harness directory in the home
    directory, its project harness directory anywhere else — or is that directory itself. The `detect`
    install setting's per-harness judgment: the same two predicates `_detected_harness` composes, read one
    harness at a time, so a change to either belongs in both. The install's `--subdir` does not enter it."""
    normalized, at_home = _lexical_target(target)
    directory = _dir_inside(harness, at_home=at_home)
    return (directory is not None and (normalized / directory).is_dir()) or _is_own_dir(normalized, harness)


def _only(target: Path, matches: dict[str, str]) -> str | None:
    """The one harness `matches` names (harness → what matched), None for none; several are refused."""
    if len(matches) > 1:
        found = " and ".join(f"'{what}' ({name})" for name, what in matches.items())
        raise InputError(f"'{target}' matches {found} — pass --harness=NAME to choose one; nothing written")
    return next(iter(matches), None)


def _detected_harness(target: Path, *, at_home: bool) -> str:
    """The one harness `target` holds the harness directory of, or is the harness directory of;
    `target_holds_harness_dir` is the same judgment read one harness at a time, so a change to either
    belongs in both. None, or several, is refused."""
    known = harnesses()
    inside = {
        name: directory
        for name, harness in known.items()
        if (directory := _dir_inside(harness, at_home=at_home)) is not None and (target / directory).is_dir()
    }
    found = _only(target, inside)
    if found is None:
        found = _only(target, {name: str(target) for name, harness in known.items() if _is_own_dir(target, harness)})
    if found is None:
        raise InputError(
            f"cannot tell the harness for '{target}': it holds no harness directory and is not one — "
            f"pass --harness=NAME, one of {', '.join(known)}; nothing written"
        )
    return found


def resolve_install_target(target: Path, *, harness: str | None, plugin: str, subdir: str | None) -> InstallTarget:
    """The harness, harness directory and project root for installing the set under the one name `plugin`
    into `target`. The harness is detected from values no selection changes; the directories are then
    resolved with it bound to `plugin`. With `subdir` given, the harness directory is `<target>/<subdir>`
    (`""`: the target itself). Otherwise, in the home directory, it is the harness's user harness directory
    there; a target that is itself the nested-plugin harness's directory is the harness directory, under
    its parent as the project root; any other target holds it at `<target>/<project harness directory>`. A
    target that is not an existing directory, or that resolves into the running package's source, is
    refused."""
    require_existing_target(target)
    require_outside_package_source(target)
    target, at_home = _lexical_target(target)
    name = _detected_harness(target, at_home=at_home) if harness is None else harness
    selected = harness_named(name).bound(plugin)
    in_home = _user_dir_in_home(selected) if at_home else None
    project_root = target
    if subdir is not None:
        require_subdir_inside(subdir)
        harness_dir = target / subdir
    elif in_home is not None:
        harness_dir = target / in_home
    elif not selected.is_harness_dir_plugin and _is_own_dir(target, selected):
        harness_dir = target
        project_root = target.parent
    else:
        harness_dir = target / selected.project_harness_dir
    return InstallTarget(harness=name, harness_dir=harness_dir, project_root=project_root)


def _absolute_user_dir(harness: Harness) -> Path | None:
    """`harness`'s user harness directory, `~` expanded, or None where it is relative: a relative one
    names no directory of its own."""
    path = harness.user_dir
    return path if path.is_absolute() else None


def user_dir_harnesses(directory: Path) -> list[str]:
    """Every harness whose absolute user harness directory is `directory`, both resolved so two
    spellings of one directory compare equal."""
    resolved = directory.resolve()
    return [
        name
        for name, harness in harnesses().items()
        if (user_dir := _absolute_user_dir(harness)) is not None and user_dir.resolve() == resolved
    ]


def agents_file_harness(directory: Path, harness: str | None) -> str:
    """`harness`, or — when it is None or "" — the one harness whose user harness directory is
    `directory`; none or several are refused, naming the harnesses inference covers."""
    if harness:
        return harness
    matches = user_dir_harnesses(directory)
    if len(matches) == 1:
        return matches[0]
    inferable = ", ".join(name for name, entry in harnesses().items() if _absolute_user_dir(entry) is not None)
    if matches:
        cause = f"it is the user directory of {' and '.join(matches)}"
    else:
        cause = "it is no harness's user directory"
    raise InputError(f"cannot infer the harness for '{directory}': {cause} — pass --harness, one of {inferable}")
