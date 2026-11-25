"""Link rewriting: section references become links to their files, links outside the document are
rebased to resolve from each leaf, and a link to another document is rebased to that document's own
path in the tree. Every resolution is run-time: the document's headings, its anchors and the tree's
files are what a link is resolved against, and nothing a previous run wrote is read.
"""

import posixpath
import re
from dataclasses import dataclass, field

from .anchors import heading_anchor_list
from .linkscan import OnLink, OnRef, scan
from .outline import Outline

URL_SCHEME = re.compile(r"[a-z]+:")
_SECTION_LINK_TEXT = re.compile(r"§[0-9]")
_NAMED_CHILD = re.compile(r" `([^`]+)`")
_OTHER_DOCUMENT = re.compile(r"(?:SPEC|ARCHITECTURE|THESIS|CONVENTIONS)(?:\.md)? $")


def rel(from_dir: str, to: str) -> str:
    """Relative path from directory `from_dir` ("" is the root) to file `to`."""
    a = from_dir.split("/") if from_dir else []
    b = to.split("/") if to else []
    i = 0
    while i < len(a) and i < len(b) - 1 and a[i] == b[i]:
        i += 1
    return "../" * (len(a) - i) + "/".join(b[i:])


def parent_dir(path: str) -> str:
    return path.rpartition("/")[0]


@dataclass
class Tree:
    """A diced document's output directory and the absolute paths its links resolve against.
    documents maps a document's base name, as the monolith's links name it, to the tree path its
    head is written at: the dice's own inputs, so a link from one document of a dice to another is
    known even though the tree holds no file of the source's name."""

    out: str  # as given, prefixed to the files written and the paths reported
    outabs: str  # out, absolute and with symlinks resolved
    root: str  # the run directory, absolute: links in the monolith are relative to it
    documents: dict[str, str] = field(default_factory=dict)
    volume: str = ""  # the volume being written or checked, relative to outabs: "" at the root


def _anchor_homes(outline: Outline, lines: list[str]) -> dict[str, tuple[str, str]]:
    """For each heading anchor of the monolith, the file of the diced tree that holds the heading
    and its anchor there: "" where the heading opens that file (a link to the file needs none),
    else its anchor within the file, whose repeat suffixes count that file's headings alone."""
    owner = {}  # monolith line -> section holding it
    for s in outline.sections:
        for no in range(s.first, s.last + 1):
            owner[no] = s
    homes: dict[str, tuple[str, str]] = {}
    per_file: dict[int, list[str]] = {}
    for no, anchor in heading_anchor_list(lines):
        s = owner.get(no)
        if s is None:
            continue
        local = per_file.setdefault(s.id, [])
        local.append(anchor.base)
        n = local.count(anchor.base) - 1
        within = f"{anchor.base}-{n}" if n else anchor.base
        own = no == s.first and s.id > 0
        homes.setdefault(anchor.name, (s.path, "" if own else within))
    return homes


class Linker:
    """Rewrites lines of one diced document; counts the section references it resolved and the
    ones it could not."""

    def __init__(self, outline: Outline, tree: Tree, lines: list[str] | None = None) -> None:
        self.outline = outline
        self.tree = tree
        self.resolved = 0
        self.dangling: dict[str, int] = {}
        self.anchors = _anchor_homes(outline, lines or [])
        self._anchor_at = {home: name for name, home in self.anchors.items()}

    def forward(self, line: str, leaf_dir: str, next_line: str) -> str:
        """Link section references and rebase outside links, for a line written under leaf_dir."""
        return scan(line, self._rebaser(leaf_dir, next_line), self._ref_linker(leaf_dir))

    def rebase_only(self, line: str, leaf_dir: str, next_line: str) -> str:
        return scan(line, self._rebaser(leaf_dir, next_line))

    def written(self, line: str, leaf_dir: str, next_line: str) -> str:
        """A monolith line as the tree's file at leaf_dir writes it, section references left as the
        source has them: the reassembly check's expected line. Its links are made against the leaf's
        own place in the tree, so a link between two documents of one dice lands between their
        positions in the tree whatever directory the verb ran in or the documents were read from."""
        return self.rebase_only(line, leaf_dir, next_line)

    def revert(self, line: str, leaf_dir: str) -> str:
        """Undo the section links `forward` made; every other link stays."""

        def unlink(raw: str, text: str, target: str, after: str) -> str:
            return text if self._made_by_forward(text, target, leaf_dir) else raw

        return scan(line, unlink)

    def restore(self, line: str, leaf_dir: str) -> str:
        """Undo `forward` for a line read from under leaf_dir, as far as the tree allows: section
        links become their text, a link to a heading's home becomes `#<anchor>`, every other relative
        link is rebased back to the run directory."""

        def restore_link(raw: str, text: str, target: str, after: str) -> str:
            if self._made_by_forward(text, target, leaf_dir):
                return text
            anchor = self._anchor_linked(target, leaf_dir)
            if anchor:
                return f"[{text}](#{anchor})"
            document = self._document_linked(target, leaf_dir)
            if document:
                return f"[{text}]({document})"
            return f"[{text}]({self._unrebase(target, leaf_dir)})"

        return scan(line, restore_link)

    def _document_linked(self, target: str, leaf_dir: str) -> str:
        """The document name a target under leaf_dir restores as, when the target lands on another
        document's head in the tree: the name a monolith's link to a second document carried. "" where
        it lands anywhere else. documents maps each document's name to the tree path of its head, and
        a target is resolved from the volume being restored, which is where the tree's links are
        made from."""
        if never_rebased(target):
            return ""
        path = target.partition("#")[0]
        here = posixpath.join(self.tree.volume, leaf_dir) if self.tree.volume else leaf_dir
        landed = posixpath.normpath(posixpath.join(here, path))
        for name, head in self.tree.documents.items():
            if posixpath.normpath(head) == landed:
                return name
        return ""

    def _rebaser(self, leaf_dir: str, next_line: str) -> OnLink:
        def rebase(raw: str, text: str, target: str, after: str) -> str:
            return f"[{text}]({self._rebase(target, leaf_dir, after, next_line)})"

        return rebase

    def _ref_linker(self, leaf_dir: str) -> OnRef:
        def link_ref(ref: str, s: str, p: int, before: str) -> tuple[str, int]:
            number = ref[1:]
            if _OTHER_DOCUMENT.search(before):
                return ref, p
            if number not in self.outline.by_number:
                self.dangling[number] = self.dangling.get(number, 0) + 1
                return ref, p
            target, text = self.outline.path_of_number(number), ref
            m = _NAMED_CHILD.match(s, p)
            if m:
                child = self.outline.child_path_naming(number, m.group(1))
                if child:
                    target, text, p = child, ref + m.group(), m.end()
            self.resolved += 1
            return f"[{text}]({rel(leaf_dir, target)})", p

        return link_ref

    def _made_by_forward(self, text: str, target: str, leaf_dir: str) -> bool:
        if not _SECTION_LINK_TEXT.match(text):
            return False
        number, name = text[1:], ""
        i = number.find(" `")
        if i >= 0:
            number, name = number[:i], number[i + 2 :]
            if name.endswith("`"):
                name = name[:-1]
        if number not in self.outline.by_number:
            return False
        if name:
            dest = self.outline.child_path_naming(number, name)
        else:
            dest = self.outline.path_of_number(number)
        return target == rel(leaf_dir, dest)

    def _anchor_linked(self, target: str, leaf_dir: str) -> str:
        """The anchor of the heading whose home in the tree a target under leaf_dir names; "" if none."""
        if never_rebased(target):
            return ""
        path, _, fragment = target.partition("#")
        return self._anchor_at.get((posixpath.normpath(posixpath.join(leaf_dir, path)), fragment), "")

    def _rebase(self, target: str, leaf_dir: str, after: str, next_line: str) -> str:
        """An outside link target made relative to leaf_dir: a heading of the document goes to its
        home in the tree, a link to a second document of the same dice goes to that document's head
        in the tree, and every other target is rebased to the file its path names from the run
        directory."""
        if target.startswith("#") and target[1:] in self.anchors:
            path, anchor = self.anchors[target[1:]]
            return rel(leaf_dir, path) + (f"#{anchor}" if anchor else "")
        if never_rebased(target):
            return target
        path, _, fragment = target.partition("#")
        document = self.tree.documents.get(path)
        if document is not None:
            fragment = ""
            destination = posixpath.normpath(f"{self.tree.outabs}/{document}")
            return rel(self._here(leaf_dir), destination)
        destination = posixpath.normpath(f"{self.tree.root}/{path}")
        return rel(self._here(leaf_dir), destination) + ("#" + fragment if fragment else "")

    def _unrebase(self, target: str, leaf_dir: str) -> str:
        """A target relative to leaf_dir made relative to the run directory again: the lexical
        inverse of `_rebase`'s `rel`, so a `./` or `..` the source wrote survives the round trip."""
        if never_rebased(target):
            return target
        path, hash_, fragment = target.partition("#")
        here = self._here(leaf_dir).split("/")
        while path.startswith("../") and len(here) > 1:
            path = path[3:]
            here.pop()
        return rel(self.tree.root, "/".join([*here, path])) + hash_ + fragment

    def _here(self, leaf_dir: str) -> str:
        """The absolute path of leaf_dir, a directory of the tree, under the volume being written or
        checked: the tree's root where no volume stands below it."""
        here = posixpath.join(self.tree.outabs, self.tree.volume) if self.tree.volume else self.tree.outabs
        return posixpath.join(here, leaf_dir) if leaf_dir else here


def never_rebased(target: str) -> bool:
    """Empty, bare-fragment, root-absolute and URL targets mean the same from any directory."""
    return target == "" or bool(URL_SCHEME.match(target)) or target[0] in "#/"
