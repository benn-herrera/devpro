"""Dicing one document or several, undicing a tree back into its documents, and re-checking trees
that already exist.

A tree has two structural patterns and no third ([heads](heads.py)): a volume's top document is
`entry-point.md` and a broken-out section's is `index.md`. `dice A.md B.md T/` makes every input
document a volume under the omnibus — `T/A/entry-point.md` and `T/B/entry-point.md` beside the
omnibus's own `T/entry-point.md` — and one input is written with its head at the tree's root and its
sections beneath, the one-document form.

A verb passes around two kinds of path. A **tree path** is relative to the tree's root and names a
file there. A **document path** is relative to a volume's head: the path a section would have if the
volume's document were planned at that head, which is what planning and reassembly compare.
"""

import io
import os
import posixpath
from dataclasses import dataclass
from typing import TextIO

from .heads import (
    CONTENTS,
    ENTRY_POINT,
    HEADS,
    INDEX,
    below_block,
    contents_line,
    heads_of,
    section_head,
    volume_head,
)
from .linkcheck import check_links, markdown_files
from .linkrewrite import Linker, Tree, parent_dir
from .linkscan import link_targets, plain_text
from .outline import _HEADING, DEEPEST_SPLIT_LEVEL, LAST_LEVEL, Outline, Section, plan_sections, split_number
from .reassemble import check_reassembly, own_end, top_is_rebased
from .split import _rebased, write_tree
from .textfile import FenceTracker, read_lines, write_lines


@dataclass
class Volume:
    """One document of a tree: the tree path of its head file, the tree path of the directory its
    sections are written in, the title it is listed under, and the document's own path as the verbs
    read or write it."""

    head: str
    directory: str
    title: str
    source: str = ""


def _warn_duplicate_numbers(sections: list[Section], *, err: TextIO) -> None:
    for number in Outline(sections).duplicate_numbers:
        print(f"duplicate section number {number}", file=err)


def _tree(out: str, root: str = "") -> Tree:
    """Links in a monolith are relative to the run directory root, so it anchors their rebasing."""
    return Tree(out=out, outabs=os.path.realpath(out), root=root)


def title_of(lines: list[str]) -> str:
    """A document's title: the plain text of its opening level-1 heading, outside fenced code and
    without its number. "" where the document opens no level-1 heading."""
    fence = FenceTracker()
    for line in lines:
        m = _HEADING.match(line) if not fence.inside(line) else None
        if m and m.end() == 2:
            return split_number(plain_text(line[2:].rstrip(" ")))[1]
    return ""


def _out_ready(out: str, *, err: TextIO) -> bool:
    """Whether out is a directory a verb may write: absent or empty. A refusal is reported."""
    if os.path.exists(out) and not os.path.isdir(out):
        print(f"not a directory: {out}", file=err)
        return False
    if os.path.isdir(out) and os.listdir(out):
        print(f"out-dir not empty: {out}", file=err)
        return False
    return True


def _document_path(volume: Volume, tree_path: str) -> str:
    """A tree path as the document path it is in the volume: below its head's directory."""
    return posixpath.relpath(tree_path, volume.directory) if volume.directory else tree_path


def _tree_path(volume: Volume, document_path: str) -> str:
    """A document path as the tree path the volume writes it at."""
    return f"{volume.directory}/{document_path}" if volume.directory else document_path


def _plan(lines: list[str], volume: Volume, *, err: TextIO, deepest: int) -> tuple[list[Section], bool]:
    """A volume's document's sections, planned with its head's document path as the entry point's."""
    return plan_sections(lines, err=err, deepest=deepest, root_path=_document_path(volume, volume.head))


# --- dice ---------------------------------------------------------------------------------------------------------


def _volumes(monoliths: list[str], *, section: bool) -> list[Volume]:
    """One volume per input: the single input's at the tree's root, and each of several in a
    directory named for its base name without `.md`. A section is one document, written at the tree's
    root, its head the root's `index.md`."""
    volumes = []
    for monolith in monoliths:
        base = os.path.basename(monolith)
        name = base[: -len(".md")] if base.endswith(".md") else base
        directory = "" if len(monoliths) == 1 else name
        volumes.append(Volume(volume_head(directory), directory, "", monolith))
    if section:
        volumes[0].head = section_head("")
    return volumes


def _refusals(volumes: list[Volume], *, err: TextIO) -> bool:
    """Report a name a volume directory cannot take, and whether one does. Two documents of one base
    name would both claim `<out-dir>/<name>`, so the name is refused. A section directory cannot
    collide with a volume directory: a volume's sits at the output root and a section's inside it, so
    no name is shared between them."""
    refused = False
    taken: set[str] = set()
    for volume in volumes:
        if volume.directory in taken:
            print(f"volume {volume.directory}: two documents of one name", file=err)
            refused = True
        taken.add(volume.directory)
    return refused


def _omnibus_lines(volumes: list[Volume]) -> list[str]:
    """The omnibus root's own head: a level-1 title and a Contents block listing each volume's head,
    its link text the volume's title."""
    lines = ["# Omnibus", "", CONTENTS, ""]
    return lines + [contents_line("", text=volume.title, path=volume.head) for volume in volumes]


def _volume_tree(out: str, root: str, base: str) -> Tree:
    """The tree as one volume of it is checked: tree.out is the volume's own directory and tree.outabs
    the tree's, so a section's path is read from the volume's directory while the links it finds are
    resolved under the tree's. base is the volume directory the tree's root holds the volume at. out
    is taken as relative to root, the directory the verb ran in, so the tree's absolute path does not
    depend on the process's own working directory."""
    out_dir = out if os.path.isabs(out) else os.path.join(root, out)
    return Tree(
        out=os.path.join(out, base) if base else out,
        outabs=os.path.realpath(out_dir),
        root=root,
        volume=base,
    )


def dice(
    monoliths: list[str],
    out: str,
    *,
    root: str,
    stdout: TextIO,
    stderr: TextIO,
    deepest: int = DEEPEST_SPLIT_LEVEL,
    section: bool = False,
) -> int:
    """Dice every document named into a tree under out (empty or absent), the one form both the
    single-input and the several-input spelling take, then check every volume. With section, the
    tree is a broken-out section's: its root's head is `index.md` and no omnibus stands above it.
    root is the run directory the documents' links are relative to. 0 ok, 1 a failed step, 2 a
    refusal."""
    for monolith in monoliths:
        if not os.path.isfile(monolith):
            print(f"not a file: {monolith}", file=stderr)
            return 2
    if not _out_ready(out, err=stderr):
        return 2
    volumes = _volumes(monoliths, section=section)
    texts = {v.head: read_lines(monolith) for v, monolith in zip(volumes, monoliths)}
    for volume in volumes:
        volume.title = title_of(texts[volume.head])
        if not volume.title:
            print(f"volume {volume.directory or volume.source}: no opening level-1 heading", file=stderr)
            return 2
    plans: dict[str, list[Section]] = {}
    for volume in volumes:
        lines = texts[volume.head]
        sections, ok = _plan(lines, volume, err=stderr, deepest=deepest)
        if not ok:
            return 1
        plans[volume.head] = sections
        _warn_duplicate_numbers(sections, err=stderr)
    if _refusals(volumes, err=stderr):
        return 2
    os.makedirs(out, exist_ok=True)
    if not section:
        write_lines(os.path.join(out, ENTRY_POINT), _omnibus_lines(volumes))
    tree = _tree(out, root)
    documents = {os.path.basename(volume.source): volume.head for volume in volumes}
    tree.documents = documents
    failed = False
    for volume, monolith in zip(volumes, monoliths):
        lines = texts[volume.head]
        sections = plans[volume.head]
        for s in sections:
            os.makedirs(os.path.join(out, posixpath.dirname(_tree_path(volume, s.path))), exist_ok=True)
        if write_tree(sections, lines, tree, err=stderr, base=volume.directory):
            failed = True
    if failed:
        return 1
    ok = True
    for volume in volumes:
        sections = plans[volume.head]
        ok = (
            _write_check(
                volume,
                texts[volume.head],
                sections,
                documents,
                out=out,
                root=root,
                stdout=stdout,
                stderr=stderr,
            )
            and ok
        )
    return 0 if ok else 1


# --- undice -------------------------------------------------------------------------------------------------------


def _own(out: str, tree_path: str) -> tuple[list[str], list[str]]:
    """A tree file's own lines and, for a head, its Contents block with every line after it."""
    lines = read_lines(os.path.join(out, tree_path))
    end = own_end(tree_path, lines)
    return lines[:end], lines[end:]


def _head_refusals(tree_dir: str, *, err: TextIO) -> bool:
    """Report each head file of the tree that carries text below its Contents block, and whether
    one does. A head's own text ends at its Contents block: the dicer writes nothing below it, so
    text below it is not the document's and undice refuses the tree rather than drop it."""
    refused = False
    for f in markdown_files([tree_dir]):
        if os.path.basename(f) not in HEADS:
            continue
        try:
            lines = read_lines(f)
        except OSError:
            continue  # a head the walk cannot read is reported there
        no = below_block(lines)
        if no >= 0:
            print(
                f"{f}: text below the Contents block at line {no}:" " remove it or rehome it above the Contents: line",
                file=err,
            )
            refused = True
    return refused


def _volume_documents(out: str) -> list[Volume]:
    """The documents a tree holds: one for each volume root `heads_of` reads below the root's head,
    and the root's own head as the one document where it reads none. The root's head is never
    itself a volume; `dice` writes the omnibus there. A root opening at `index.md` is a broken-out
    section, and its head holds its document."""
    root_head = INDEX if os.path.isfile(os.path.join(out, INDEX)) else ENTRY_POINT
    root = os.path.join(out, root_head)
    volumes = []
    for directory in sorted(heads_of(root)):
        head = posixpath.join(directory, ENTRY_POINT)
        volume = Volume(head, directory, title_of(read_lines(os.path.join(out, head))))
        volume.source = posixpath.basename(directory) + ".md"
        volumes.append(volume)
    if volumes:
        return volumes
    return [Volume(root_head, "", title_of(read_lines(root)))]


def _walk(
    out: str, head: str, *, err: TextIO
) -> tuple[list[tuple[str, list[str]]], list[tuple[str, int | None]], bool]:
    """A volume's parts in reading order: its head file, then each file its Contents links reach,
    depth first in link order and once each. A linked file that cannot be read is reported and left
    out. Returns each part's tree path with its own lines, each part's directory-relative path with
    the document line it starts at, and whether every linked file was read."""
    directory = posixpath.dirname(head)
    parts: list[tuple[str, list[str]]] = []
    reads: list[tuple[str, int | None]] = []
    seen: set[str] = set()
    all_read = True

    def visit(referrer: str, target: str) -> None:
        """Record the part a link names and its own lines, then the parts its Contents links reach:
        the one place a part is recorded, the head included."""
        nonlocal all_read
        tree_path = posixpath.normpath(posixpath.join(posixpath.dirname(referrer), target.partition("#")[0]))
        if tree_path in seen:
            return
        try:
            own, contents = _own(out, tree_path)
        except OSError:
            print(f"undice: cannot read {out}/{tree_path}", file=err)
            all_read = False
            return
        seen.add(tree_path)
        first = sum(len(lines) for _, lines in parts) + 1
        reads.append((posixpath.relpath(tree_path, directory) if directory else tree_path, first))
        parts.append((tree_path, own))
        for line in contents:
            for link in link_targets(line):
                visit(tree_path, link)

    visit(head, posixpath.basename(head))
    return parts, reads, all_read


def _restored(
    head: tuple[str, list[str]], parts: list[tuple[str, list[str]]], tree: Tree, *, deepest: int, err: TextIO
) -> list[str] | None:
    """The head's own lines and then the parts' with their heading ladders restored, their links
    restored against the sections, split at level 2 to deepest; None where a part cannot be placed,
    which is reported on err.

    A part whose top heading reads level 1 is the re-based write form and has its ladder put back to
    the level its place in the tree fixes (`_placed_level`), fenced lines as they stand; a part whose
    top reads any other level is the pre-change form and passes through as it stands. A part that
    opens no heading is written as it stands: the self-check reports it, as it reports any file of
    the tree the planned sections do not reproduce. A head's own text is its document's title and
    opening text, and writes as it stands: a volume's head holds them, and a broken-out section's
    head is that section's opening, which the document it folds into holds above its children.

    The sections are planned over the head's text and the parts together, the head's title being the
    plan's title: the parts' first level is the document's first section, and the plan reads it there.
    """

    def restore_ladder(document_path: str, own: list[str]) -> list[str] | None:
        if not top_is_rebased(own):
            return own
        level = _placed_level(document_path)
        if level is None:
            print(f"undice: {document_path} sits deeper than a document's last heading level", file=err)
            return None
        fence = FenceTracker()
        restored = []
        for no, line in enumerate(own):
            heading = not fence.inside(line) and _HEADING.match(line)
            restored.append(_rebased(line, delta=level - 1, top=level if no == 0 else None) if heading else line)
        return restored

    placed = []
    for path, own in parts:
        ladder = restore_ladder(path, own)
        if ladder is None:
            return None
        placed.append((path, ladder))
    whole = head[1] + [line for _, own in placed for line in own]
    links, _ = plan_sections(whole, err=io.StringIO(), deepest=deepest)
    linker = Linker(Outline(links), tree, whole)
    fence = FenceTracker()
    head_dir = parent_dir(head[0])
    restored = [[line if fence.inside(line) else linker.restore(line, head_dir) for line in head[1]]]
    for path, own in placed:
        fence = FenceTracker()
        leaf_dir = parent_dir(path)
        restored.append([line if fence.inside(line) else linker.restore(line, leaf_dir) for line in own])
    return [line for run in restored for line in run]


def _placed_level(path: str) -> int | None:
    """The level a part's top heading is restored to: the level its place in the tree fixes, and
    nothing else. Every section file sits one level below its parent's head, so a section of the
    document's first level takes level 2 and one at depth d takes level d + 1, a directory holding a
    section index counting as that index's level: `a/index.md` is a section at the document's first
    level, `a/b.md` at its second. A part's own headings never move it: the writer re-bases each
    part's ladder to a level-1 top whatever depth it had, so its headings are relative to its own
    top, and the deepest split level bounds the document the parts are planned into. None where the
    place is deeper than the last heading level: no document can hold the part there."""
    directory = parent_dir(path)
    depth = len(directory.split("/")) if directory else 0
    if directory and posixpath.basename(path) == INDEX:
        depth -= 1
    return depth + 2 if depth + 2 <= LAST_LEVEL else None


def _document(
    volume: Volume,
    parts: list[tuple[str, list[str]]],
    *,
    out: str,
    root: str,
    deepest: int,
    documents: dict[str, str],
    err: TextIO,
) -> list[str] | None:
    """A volume's document: its head's own lines, then each part read after it, its ladder restored
    and its links restored against the document; None where a part cannot be placed. root is the run
    directory the document's links are relative to, and documents maps each volume's head to the
    document name a link to it restores as."""
    head, *rest = parts
    relative = [(_document_path(volume, path), own) for path, own in rest]
    tree = Tree(
        out=os.path.join(out, volume.directory) if volume.directory else out,
        outabs=os.path.realpath(out),
        root=os.path.realpath(root),
        documents=documents,
        volume=volume.directory,
    )
    return _restored((_document_path(volume, head[0]), head[1]), relative, tree, deepest=deepest, err=err)


def undice(tree_dir: str, out: str, *, stdout: TextIO, stderr: TextIO, deepest: int = DEEPEST_SPLIT_LEVEL) -> int:
    """Write each document a diced tree holds into the directory out, which must be absent or empty:
    one document per volume, named for its head's directory, and a tree holding one document named
    for the tree's own directory. Then check each document against its volume. root is the directory
    every document is written in, which its links come out relative to. 0 ok, 1 a failed check, 2 a
    refusal."""
    if not any(os.path.isfile(os.path.join(tree_dir, head)) for head in HEADS):
        print(f"not a tree: {tree_dir}", file=stderr)
        return 2
    if not _out_ready(out, err=stderr):
        return 2
    if _head_refusals(tree_dir, err=stderr):
        return 2
    os.makedirs(out, exist_ok=True)
    tree_base = os.path.basename(os.path.normpath(tree_dir))
    document_root = os.path.realpath(out)
    tree_root = os.path.realpath(tree_dir)
    volumes = _volume_documents(tree_dir)
    # a link to a volume's head in the tree restores as that volume's document name: the name a
    # monolith's link to a second document of the same dice carried
    documents = {volume.source: volume.head for volume in volumes if volume.source}
    ok = True
    for volume in volumes:
        parts, reads, all_read = _walk(tree_dir, volume.head, err=stderr)
        lines = _document(
            volume, parts, out=tree_dir, root=document_root, deepest=deepest, documents=documents, err=stderr
        )
        if lines is None:
            ok = False
            continue
        name = os.path.basename(volume.directory) if volume.directory else tree_base
        document = os.path.join(out, f"{name}.md")
        write_lines(document, lines)
        print(f"=== {document}", file=stdout)
        checks = [
            all_read,
            _self_check(
                volume,
                lines,
                parts,
                reads,
                documents,
                out=tree_dir,
                root=document_root,
                tree_root=tree_root,
                deepest=deepest,
                stdout=stdout,
                stderr=stderr,
            ),
        ]
        ok = all(checks) and ok
    return 0 if ok else 1


# --- the checks the write side runs -------------------------------------------------------------------------------


def _write_check(
    volume: Volume,
    lines: list[str],
    sections: list[Section],
    documents: dict[str, str],
    *,
    out: str,
    root: str,
    stdout: TextIO,
    stderr: TextIO,
) -> bool:
    """One document just written against its volume: the reassembly check (the sections reproduce
    the document line for line) and the link check. documents maps the dice's own documents to the
    heads their links resolve to."""
    tree = _volume_tree(out, root, volume.directory)
    tree.documents = documents
    rebuilt = check_reassembly(sections, lines, tree, out=stdout, err=stderr)
    linked = check_links(sections, tree, out=stdout, err=stderr)
    return rebuilt and linked


# --- the checks the read side runs --------------------------------------------------------------------------------


def _self_check(
    volume: Volume,
    lines: list[str],
    parts: list[tuple[str, list[str]]],
    reads: list[tuple[str, int | None]],
    documents: dict[str, str],
    *,
    out: str,
    root: str,
    tree_root: str,
    deepest: int,
    stdout: TextIO,
    stderr: TextIO,
) -> bool:
    """One document against the volume it was written from: planned at the deepest split level, its
    sections must reproduce the volume's files line for line, its links must resolve, and no file of
    the volume may go unwritten. A planning failure is reported and fails the check. root is the
    directory the document was written in, which its links are relative to."""
    sections, planned = _plan(lines, volume, err=stderr, deepest=deepest)
    _warn_duplicate_numbers(sections, err=stderr)
    if not planned:
        return False
    tree = _volume_tree(tree_root, root, volume.directory)
    tree.documents = documents
    rebuilt = check_reassembly(sections, lines, tree, out=stdout, err=stderr)
    linked = check_links(sections, tree, out=stdout, err=stderr)
    reproduced = _reproduced(volume, sections, reads, out=out, err=stderr, deepest=deepest)
    return rebuilt and linked and reproduced


def _reproduced(
    volume: Volume,
    sections: list[Section],
    reads: list[tuple[str, int | None]],
    *,
    out: str,
    err: TextIO,
    deepest: int,
) -> bool:
    """Report each `.md` file of a volume the document's sections do not write, naming the remedy: a
    file read as a section is renamed or its heading edited, a file read that opens none gets a
    heading or is removed, any other is linked or removed. Returns whether the volume holds none.
    reads are the volume's (document path, line the part starts at) pairs, the first part's lines
    starting at line 1 of the document."""
    assigned = {s.path for s in sections}
    opened = {s.first: s for s in sections if s.id > 0}
    read_as: dict[str, Section] = {}
    read = {path for path, _ in reads}
    for path, first in reads:
        if first in opened:
            read_as.setdefault(path, opened[first])
    strays = 0
    for f in markdown_files([os.path.join(out, volume.directory) if volume.directory else out]):
        path = _document_path(volume, "/".join(os.path.relpath(f, out).split(os.sep)))
        if path in assigned:
            continue
        strays += 1
        if path in read_as:
            print(
                f"undice: {f} would be re-diced as {out}/{_tree_path(volume, read_as[path].path)}:"
                " rename the file or edit its heading to match",
                file=err,
            )
        elif path in read:
            print(
                f"undice: {f} opens no section: start it with a heading the document splits on"
                f" (level 2 to {deepest} in the document, written at level 1), or remove it and its Contents line",
                file=err,
            )
        else:
            head = os.path.join(out, volume.head)
            print(f"undice: not reproduced: {f}: link it from {head}'s Contents, or remove it", file=err)
    return not strays
