"""The preflight `install` and `install-agents-file` run before writing anything: the unchanged install,
run into a scratch copy of the paths it manages, and that copy compared with the target. The result
decides the run: the target is up to date and untouched, or `--dry-run` prints what would change, or
the real install runs. The install itself decides what is written, run where its writes cannot reach
the target; `install._install_managed_paths` names where it may write, and the tests'
`_assert_dry_run_predicts` holds the two together."""

import contextlib
import filecmp
import glob
import io
import os
import shutil
import stat
import sys
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from devpro.errors import InputError


@dataclass(frozen=True)
class Difference:
    """What an install would do to its target, each path a real one: the files it would create and the
    directories, those files whose bytes or mode it would change, the files and directories it would
    remove, and the lines it would print on stderr — what it would leave alone or skip — naming the
    real target. `created` and `removed` hold every path, `created_directories` and `removed_directories`
    the ones that are directories, which the dry run prints with a trailing `/`."""

    created: tuple[Path, ...]
    changed: tuple[Path, ...]
    removed: tuple[Path, ...]
    reports: tuple[str, ...]
    created_directories: tuple[Path, ...] = ()
    removed_directories: tuple[Path, ...] = ()

    def is_empty(self) -> bool:
        return not (self.created or self.changed or self.removed)


def _scratch_bases(bases: Sequence[Path], *, scratch: Path) -> tuple[list[Path], list[int]]:
    """Each real base's counterpart under `scratch`, in order, and the indexes of the outermost bases. A
    base inside an earlier one, both made absolute and normalized, sits at the same position below that
    one's counterpart, so the relation between them holds in the copy; any other base is outermost and
    sits at `scratch/<index>/<its own name>`."""
    normalized = [Path(os.path.normpath(base.absolute())) for base in bases]
    placed: list[Path] = []
    outermost: list[int] = []
    for index, base in enumerate(bases):
        nesting = next(
            (
                (earlier, normalized[index].relative_to(normalized[earlier]))
                for earlier in range(index)
                if normalized[index].is_relative_to(normalized[earlier])
            ),
            None,
        )
        if nesting is None:
            placed.append(scratch / str(index) / base.name)
            outermost.append(index)
        else:
            earlier, relative = nesting
            placed.append(placed[earlier] / relative)
    return placed, outermost


def _copy_managed(managed: Sequence[tuple[Path, Sequence[str]]], *, scratch_bases: Sequence[Path]) -> None:
    """Copy each managed path that exists to the same position below its base's counterpart: a directory
    as its tree, and a file as its bytes. A directory a managed path sits in is
    created where the real one exists, since an install's checks read whether it does; where a regular
    file stands in its place instead, or in a base's, the outermost such file is copied, so the install
    meets the same obstacle. A relative naming a wildcard stands for every path it matches, as the
    install's own glob reads it, and nothing where it matches none. A directory the real tree does not
    hold is never created: the run makes it, and that is what the comparison reads."""
    for (base, paths), scratch_base in zip(managed, scratch_bases):
        if base.is_dir():
            scratch_base.mkdir(parents=True, exist_ok=True)
        elif base.is_file():
            scratch_base.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(base, scratch_base)
            continue
        for relative in paths:
            real, copy = base / relative, scratch_base / relative
            if glob.has_magic(relative):
                for match in sorted(base.glob(relative)):
                    at = Path(match.relative_to(base))
                    if match.is_dir():
                        shutil.copytree(
                            match,
                            scratch_base / at,
                            symlinks=True,
                            dirs_exist_ok=True,
                        )
                    elif match.is_file():
                        (scratch_base / at).parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(match, scratch_base / at)
                continue
            if real.parent.is_dir():
                (scratch_base / real.parent.relative_to(base)).mkdir(parents=True, exist_ok=True)
            else:
                obstacle = next(
                    (
                        parent
                        for parent in reversed(tuple(Path(relative).parents)[:-1])
                        if (base / parent).exists() and not (base / parent).is_dir()
                    ),
                    None,
                )
                if obstacle is not None and (base / obstacle).is_file():
                    (scratch_base / obstacle).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(base / obstacle, scratch_base / obstacle)
            if real.is_dir():
                shutil.copytree(real, copy, symlinks=True, dirs_exist_ok=True)
            elif real.is_file():
                shutil.copy2(real, copy)


def _tree(base: Path) -> tuple[set[Path], set[Path]]:
    """Every file and every directory below `base`, relative to it. `base` is read
    as it resolves, so a spelling that reaches the tree through a symlink reads the same one."""
    files: set[Path] = set()
    directories: set[Path] = set()
    root = base.resolve()
    for directory, subdirs, names in os.walk(root):
        files.update(Path(directory, name).relative_to(root) for name in names)
        directories.update(Path(directory, name).relative_to(root) for name in subdirs)
    return files, directories


def _differs(copy: Path, real: Path) -> bool:
    """Whether `copy` and `real` differ in bytes or in permission bits."""
    if not (copy.exists() and real.exists()):
        return copy.exists() != real.exists()
    if not filecmp.cmp(copy, real, shallow=False):
        return True
    return stat.S_IMODE(copy.stat().st_mode) != stat.S_IMODE(real.stat().st_mode)


def _in_real_terms(message: str, *, scratch_bases: Sequence[Path], bases: Sequence[Path]) -> str:
    """`message` with every scratch base replaced by the real base it stands for, the longest first so
    a base nested in another is replaced whole."""
    for scratch_base, base in sorted(zip(scratch_bases, bases), key=lambda pair: len(str(pair[0])), reverse=True):
        message = message.replace(str(scratch_base), str(base))
    return message


def preflight(
    managed: Sequence[tuple[Path, Sequence[str]]], *, install: Callable[[Sequence[Path]], None]
) -> Difference:
    """The difference `install` would make to the files `managed` names, found by running it into a
    scratch copy of them and comparing. `managed` is (base, paths relative to it) per real directory the
    install writes under, outermost first; `install` takes the bases it is to write under, in the same
    order. Its stdout is discarded and its stderr kept as the difference's reports; an `InputError` it
    raises, or an `OSError` the copy or the run raises, is raised as an `InputError`; each names the
    real bases. The copy is removed before this returns."""
    bases = [base for base, _ in managed]
    with tempfile.TemporaryDirectory() as temp:
        # Resolved here, before anything takes a scratch name: a base spelled through a symlink still
        # reaches the real tree, and every path the install is handed must be below the scratch copy.
        bases = [base.resolve() for base in bases]
        managed = [(base, paths) for base, (_, paths) in zip(bases, managed)]
        scratch = Path(temp).resolve()
        scratch_bases, outermost = _scratch_bases(bases, scratch=scratch)
        # A nested base's files are found through the base that holds it.
        outer = [(bases[index], scratch_bases[index]) for index in outermost]
        stderr = io.StringIO()
        try:
            _copy_managed(managed, scratch_bases=scratch_bases)
            before = [_tree(scratch_base) for _, scratch_base in outer]
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                install(scratch_bases)
        except (InputError, OSError) as exc:
            raise InputError(_in_real_terms(str(exc), scratch_bases=scratch_bases, bases=bases)) from exc
        reports = tuple(
            _in_real_terms(line, scratch_bases=scratch_bases, bases=bases) for line in stderr.getvalue().splitlines()
        )
        created: list[Path] = []
        created_directories: list[Path] = []
        changed: list[Path] = []
        removed: list[Path] = []
        removed_directories: list[Path] = []
        for (base, scratch_base), (prior, prior_directories) in zip(outer, before):
            after, after_directories = _tree(scratch_base)
            # A directory the install moved reads as one path removed and one created, its files the same
            # bytes under new names, rather than every file in it listed on both sides.
            moves = _moves(
                base,
                prior=prior,
                prior_directories=prior_directories,
                after=after | after_directories,
                scratch_base=scratch_base,
            )
            # The directories the moved stores left: removed as directories, and named so a store's files
            # do not read as a second set of removals beside the directory that held them.
            left = set(moves) | {path for old in moves for path in prior if path.is_relative_to(old)}
            # What the run wrote: each file under its own name, and each directory it made and left
            # holding nothing — the scratch directory among them — which is the install's own write.
            # A directory made to hold a file the run wrote is that file's, and the dry run names the
            # file, as it always has.
            made = after_directories - prior_directories
            left_empty = {
                relative
                for relative in made - set(moves.values())
                if not any(other != relative and other.is_relative_to(relative) for other in after | after_directories)
            }
            created += [base / relative for relative in sorted(after - prior - set(moves.values()) | left_empty)]
            created_directories += [base / relative for relative in sorted(left_empty)]
            removed_at = (prior - after - left) | (prior_directories - after_directories)
            removed += [base / relative for relative in sorted(removed_at)]
            removed_directories += [base / relative for relative in sorted(removed_at & prior_directories)]
            changed += [
                base / relative
                for relative in sorted(after & prior)
                if _differs(scratch_base / relative, base / relative)
            ]
    return Difference(
        created=tuple(created),
        changed=tuple(changed),
        removed=tuple(removed),
        reports=reports,
        created_directories=tuple(created_directories),
        removed_directories=tuple(removed_directories),
    )


def _moves(
    base: Path,
    *,
    prior: set[Path],
    prior_directories: set[Path],
    after: set[Path],
    scratch_base: Path,
) -> dict[Path, Path]:
    """Each directory the run removed, paired with the directory it created in its place with the same
    files: a store the install renamed.

    The removed directory is gone from the copy, so its files are read from `base`, the real tree the
    preflight has not touched; the created one is read from the copy, and the two must hold the same files
    byte for byte. Only a directory beside the removed one, under the removed one's parent, is a
    candidate."""
    removed = sorted(prior_directories - after)
    appeared = [path for path in sorted(after - prior) if (scratch_base / path).is_dir()]
    moves: dict[Path, Path] = {}
    for old in removed:
        files = sorted(path for path in prior if path.is_relative_to(old) and path != old)
        for match in appeared:
            if old.parent == match.parent and _same_files(base, old, files, scratch_base / match):
                moves[old] = match
                break
    return moves


def _same_files(base: Path, old: Path, files: Sequence[Path], copy: Path) -> bool:
    """Whether `copy` holds the files the departed directory `old` held, `files` its snapshot paths
    relative to `base`, each under the same relative name and byte for byte."""
    held, _ = _tree(copy)
    names = {Path(path).relative_to(old) for path in files}
    return held == names and all(not _differs(base / old / name, copy / name) for name in names)


def _shown(path: Path, *, report_root: Path, directory: bool = False) -> str:
    """`path` relative to `report_root` where it sits below it, else whole. A path the run would create
    and one it would remove read as directories with a trailing `/`, never from the path on disk, which
    a created directory is not yet and a removed one no longer is."""
    shown = str(path.relative_to(report_root)) if path.is_relative_to(report_root) else str(path)
    return f"{shown}/" if directory or path.is_dir() else shown


def run_preflighted(
    managed: Sequence[tuple[Path, Sequence[str]]],
    *,
    install: Callable[[Sequence[Path]], None],
    dry_run: bool,
    target: Path,
    report_root: Path,
    prepared_directories: Sequence[Path] = (),
) -> None:
    """Run `install` into the real bases only where `preflight` finds it would change something. Where
    it would change nothing, report `target` up to date and write nothing — where `prepared_directories`
    name real paths the install creates when missing, not even then: the run would make them. With
    `dry_run`, print what
    would be created, changed and removed, each path relative to `report_root`, and write nothing.
    Where nothing is written, what the install would have left alone or skipped is printed on stderr;
    the real install prints its own."""
    difference = preflight(managed, install=install)
    if difference.is_empty() and not prepared_directories:
        print(f"up to date: {target} — nothing written")
        _print_reports(difference)
        return
    if not dry_run:
        install([base for base, _ in managed])
        return
    print(f"dry run, nothing written — the install would change these files under {report_root}:")
    created_directories = [*prepared_directories, *difference.created_directories]
    for group, paths, is_directory in (
        ("created", difference.created, created_directories),
        ("changed", difference.changed, ()),
        ("removed", difference.removed, difference.removed_directories),
    ):
        if paths:
            print(f"{group}:")
            for path in paths:
                print(f"  {_shown(path, report_root=report_root, directory=path in is_directory)}")
    _print_reports(difference)


def _print_reports(difference: Difference) -> None:
    for line in difference.reports:
        print(line, file=sys.stderr)
