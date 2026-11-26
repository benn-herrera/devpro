"""The include lines an install writes into the consumer's runner file (justfile or Makefile) so the
project can reach the runner snippets its shipped packages carry, the cleanup of the line a retired
package left there, and the project's scratch directory and its `.gitignore` line. Which snippet sets
exist is the caller's: each function here takes the sets it is given."""

import re
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import NamedTuple

from devpro import clauses
from devpro.context import harnesses
from devpro.install_base import report_left_alone, utf8_text
from devpro.render import appended_paragraph, write_text_verbatim

JUSTFILE_NAMES = ("justfile", "Justfile", ".justfile")
MAKEFILE_NAMES = ("Makefile", "makefile", "GNUmakefile")
# The banner the first line of every runner file this install creates: what tells a file it created
# from one the consumer wrote, which the install never removes.
CREATED_MAKEFILE_BANNER = "# Makefile — created by the devpro installer."


class SnippetSet(NamedTuple):
    """Runner snippets a shipped package carries: the name messages call the set by, the snippets
    directory — below ROOT in every set the functions here take — and the snippet each runner's include
    line names — a justfile's `.just`, a Makefile's `.mk`."""

    label: str
    directory: str
    snippets: Mapping[str, str]


def _runner_file(project: Path) -> tuple[str, Path] | None:
    """(runner, file) probed at the project root: any justfile variant selects `just`, else any make
    variant selects `make`."""
    for runner, names in (("just", JUSTFILE_NAMES), ("make", MAKEFILE_NAMES)):
        for name in names:
            if (project / name).exists():
                return runner, project / name
    return None


def check_runner(project: Path) -> None:
    """Read `project`'s runner file before an install's first write: an unreadable or undecodable file is
    refused there, not raised out of the write phase with packages and renders already landed."""
    found = _runner_file(project)
    if found is not None:
        utf8_text(found[1])


def prepare_scratch_directory(project: Path) -> None:
    """The scratch directory a project install leaves ready: `project / clauses.PROJECT_TEMP_DIR` created
    where it is missing, and `project/.gitignore` carrying the one line `.devpro-temp/`, the
    file created holding that line where the project has none. A `.gitignore` already carrying the line
    is left as it stands, its text kept byte for byte otherwise."""
    temp = clauses.PROJECT_TEMP_DIR
    (project / temp).mkdir(exist_ok=True)
    gitignore = project / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(f"{temp}/\n", encoding="utf-8", newline="")
        print(f"created {gitignore} with the {temp}/ line")
        return
    text = utf8_text(gitignore)
    # The line's own ending alone, not the trailing spaces a wider strip would take too: a line the
    # file holds with spaces after it may be the operator's, and that errs toward touching nothing.
    if any(line.rstrip("\r\n") == f"{temp}/" for line in text.splitlines()):
        return
    write_text_verbatim(gitignore, appended_paragraph(text, f"{temp}/", ending="\r\n" if "\r\n" in text else "\n"))


def _snippets_path(snippet_set: SnippetSet, *, runner: str, harness_relpath: str) -> str:
    """The canonical path `runner`'s include line names for `snippet_set`, relative to the project root."""
    return f"{harness_relpath}/{snippet_set.directory}/{snippet_set.snippets[runner]}"


def include_line(snippet_set: SnippetSet, *, runner: str, harness_relpath: str) -> str:
    """The canonical include line for `snippet_set` and `runner`: the non-fatal `import?` form for a
    justfile (just >= 1.33), or the `-include` form for a Makefile, each naming the installed snippets
    under the ROOT `harness_relpath` names relative to the project root."""
    snippets = _snippets_path(snippet_set, runner=runner, harness_relpath=harness_relpath)
    return {"just": f"import? '{snippets}'", "make": f"-include {snippets}"}[runner]


def _snippet_pattern(snippet_set: SnippetSet, *, runner: str) -> re.Pattern[str]:
    """An include line is recognized by the shape of the path it names, never by a list of spellings:
    any path ending `<directory>/<the set's snippets directory name>/<that runner's snippet>`, so a tree
    no release here wrote — the consumer's own hand — is still a line this install owns rather than one
    it appends a second copy beside. The path's first segment is the harness directory the line is a
    line for."""
    directory = re.escape(PurePosixPath(snippet_set.directory).name)
    snippet = re.escape(snippet_set.snippets[runner])
    return re.compile(rf"(?P<path>[^\s/'\"]+(?:/[^\s/'\"]+)*/{directory}/{snippet})")


def _harness_dirs() -> dict[str, str]:
    """harness name → its project-harness-dir, for every harness this installation knows."""
    return {name: harness.project_harness_dir for name, harness in harnesses().items()}


class _NamedLine(NamedTuple):
    """An existing runner include line `_named_harnesses` recognized: the harness it names — or the raw
    first path segment when no harness claims it — its index in the file, and the span of the snippets
    path it spells."""

    name: str
    # `index` shadows `tuple.index`; the field is the position, and tests read it by that name.
    index: int  # type: ignore[assignment]
    start: int
    end: int


def _named_harnesses(text: str, snippet_set: SnippetSet, *, runner: str) -> list[_NamedLine]:
    """A `_NamedLine` for every non-comment line naming `runner`'s installed snippets of `snippet_set`,
    under whatever tree the path spells; empty when no line names one. A commented-out line is prose
    about an install, not one."""
    dirs = _harness_dirs()
    pattern = _snippet_pattern(snippet_set, runner=runner)
    found: list[_NamedLine] = []
    for index, line in enumerate(text.splitlines()):
        if line.lstrip().startswith("#"):
            continue
        match = pattern.search(line)
        if match is None:
            continue
        start, end = match.span("path")
        segment = line[start:end].split("/", 1)[0]
        name = next((name for name, directory in dirs.items() if directory == segment), segment)
        found.append(_NamedLine(name, index, start, end))
    return found


def _without_lines(text: str, indexes: Sequence[int]) -> str:
    """`text` without the lines at `indexes`, every other byte as written."""
    dropped = set(indexes)
    return "".join(line for index, line in enumerate(text.splitlines(keepends=True)) if index not in dropped)


def _remove_a_created_runner_file_left_without_a_line(path: Path, text: str, *, line_removed: bool) -> None:
    """Remove `path` when the cleanup left it holding no include line and nothing but the comments this
    install creates it with — a Makefile it created and the consumer added nothing to. One holding the
    consumer's own targets is left, reported: it is theirs now, and the install removes only what it
    created and only while that holds nothing of the consumer's. `line_removed` is what this run removed;
    a file left with no line where the run removed none is reported as found, not as left over."""
    lines = text.splitlines()
    if (
        not lines
        or lines[0] != CREATED_MAKEFILE_BANNER
        or not all(not line.strip() or line.lstrip().startswith("#") for line in lines[1:])
    ):
        report_left_alone(
            f"left {path} in place holding no include line: it holds content other than this install's"
            if line_removed
            else f"left {path} in place: it holds no include line, and this install removed none"
        )
        return
    path.unlink()
    print(f"removed {path}: the installer created it and it holds no include line")


def _remove_retired_line(
    text: str, retired_set: SnippetSet, *, runner: str, path: str, harness_relpath: str
) -> tuple[str, list[str], bool]:
    """`text` without this install's include line for `retired_set` — every such line, the set having
    no package left to write one beside — the messages naming what the cleanup did, and whether it
    removed a line. A line naming this harness directory is recognized by the shape `_snippet_pattern`
    reads and removed; one naming another harness directory's snippets is reported and left. Lines of
    any other set are untouched."""
    removed: list[int] = []
    messages: list[str] = []
    for named_line in _named_harnesses(text, retired_set, runner=runner):
        line = text.splitlines(keepends=True)[named_line.index]
        if line[named_line.start : named_line.end].split("/", 1)[0] != harness_relpath.split("/", 1)[0]:
            report_left_alone(
                f"no {retired_set.label} include line removed: {path} line {named_line.index + 1} names the "
                f"retired {retired_set.label} snippets for harness '{named_line.name}'"
            )
            continue
        removed.append(named_line.index)
        messages.append(f"removed the retired {retired_set.label} include line from {path} line {named_line.index + 1}")
    return _without_lines(text, removed), messages, bool(removed)


def _with_include_line(
    text: str, snippet_set: SnippetSet, *, runner: str, path: Path, harness_relpath: str
) -> tuple[str, str | None]:
    """`text` with `snippet_set`'s include line in place, and the message naming the change; `text`
    unchanged and None where the line is reported and left."""
    label = snippet_set.label
    named = _named_harnesses(text, snippet_set, runner=runner)
    if len(named) > 1:
        indexes = ", ".join(str(named_line.index + 1) for named_line in named)
        report_left_alone(
            f"no include line written: {path} names the {label} snippets on lines {indexes}; merge them into one"
        )
        return text, None
    if not named:
        line = include_line(snippet_set, runner=runner, harness_relpath=harness_relpath)
        return appended_paragraph(text, line), f"installed: appended the {label} include line to {path}"
    named_line = named[0]
    lines = text.splitlines(keepends=True)
    prior = lines[named_line.index]
    # The line is this install's when it spells the same first segment — the harness directory — as
    # ROOT's path does; the whole path token, ROOT's own path below that segment included, is then
    # this install's to replace.
    if prior[named_line.start : named_line.end].split("/", 1)[0] != harness_relpath.split("/", 1)[0]:
        report_left_alone(
            f"no include line written: {path} line {named_line.index + 1} already includes the {label} "
            f"snippets for harness '{named_line.name}'"
        )
        return text, None
    canonical = _snippets_path(snippet_set, runner=runner, harness_relpath=harness_relpath)
    rewritten = f"{prior[: named_line.start]}{canonical}{prior[named_line.end :]}"
    if rewritten == prior:
        report_left_alone(
            f"no include line written: {path} line {named_line.index + 1} already names the installed "
            f"{label} snippets for harness '{named_line.name}'"
        )
        return text, None
    lines[named_line.index] = rewritten
    return "".join(lines), f"rewrote the {label} include line in {path}"


def install_include_lines(
    project: Path,
    snippet_sets: Sequence[SnippetSet],
    *,
    harness_relpath: str,
    retired_set: SnippetSet | None = None,
) -> None:
    """Write each of `snippet_sets`' canonical include lines, in order, into `project`'s runner file:
    the justfile or Makefile probed there, else a `Makefile` created carrying every one.

    Each set is judged alone, and one set's line never counts as another's. One line per set. A line
    naming this run's harness directory is recognized by the shape of the snippets path it names,
    whatever tree sits between its first segment — the harness directory, matched against the first
    segment of `harness_relpath` — and the snippets directory, and its whole path token is rewritten in
    place to the canonical one — so an assignment's left-hand side and a trailing comment survive — with
    no second line appended. A line naming another harness directory is reported and left alone, and so
    is a file holding more than one line for the set, which the operator merges by hand; either leaves
    the other sets' lines to be written. Only the runner file this run selected is examined: a second
    runner file's stale line is left to the operator and is non-fatal.

    `retired_set` is a set no shipped package carries any more: its lines are removed rather than
    written (`_remove_retired_line`), and removing the last one from a runner file this run created
    removes the file. No runner file is created, or a `Makefile` touched, when neither there is a line
    to write nor that runner file holds a retired line."""
    labels = " and ".join(snippet_set.label for snippet_set in snippet_sets)
    found = _runner_file(project)
    if found is None:
        if not snippet_sets:
            return
        path = project / "Makefile"
        lines = "".join(
            f"{include_line(snippet_set, runner='make', harness_relpath=harness_relpath)}\n"
            for snippet_set in snippet_sets
        )
        path.write_text(
            f"{CREATED_MAKEFILE_BANNER}\n"
            f"# Each include line below pulls in targets from the installed tree under {harness_relpath} "
            f"({labels}); add project targets below them.\n\n{lines}",
            encoding="utf-8",
        )
        print(f"created {path} with the include lines for {labels}")
        return
    runner, path = found
    prior = utf8_text(path)
    text = prior
    messages: list[str] = []
    line_removed = False
    if retired_set is not None:
        text, messages, line_removed = _remove_retired_line(
            text, retired_set, runner=runner, path=str(path), harness_relpath=harness_relpath
        )
    for snippet_set in snippet_sets:
        text, message = _with_include_line(text, snippet_set, runner=runner, path=path, harness_relpath=harness_relpath)
        if message is not None:
            messages.append(message)
    if text != prior:
        write_text_verbatim(path, text)
    for message in messages:
        print(message)
    if retired_set is not None and text != prior:
        _remove_a_created_runner_file_left_without_a_line(path, text, line_removed=line_removed)
