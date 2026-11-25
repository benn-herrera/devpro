"""A citation whose link text names a leaf's H1 must land on that leaf, not on the volume's head.

R5's shape: a link written `[file names and layout](index.md#dicing-and-checks)` carries the right
text and the wrong target, so the reader lands on the volume head and the fragment resolves. The
predicate is the link text, never the fragment: the volume-head fragments are the defect, not a
state a citation may be in.
"""

from pathlib import Path

from devpro.dicing.anchors import github_anchor, heading_anchor_list
from devpro.dicing.linkscan import scan
from devpro.dicing.textfile import FenceTracker

ROOT = Path(__file__).resolve().parents[2]
TREE = ROOT / "PROJECT_DOCS" / "SPEC" / "dicing-and-checks"

# The standing sites B2's Facts enumerate: citations whose referent is the volume head itself, not a
# leaf, so no leaf's text names them. Keyed by (file, line) because a line can carry two sites.
STANDING = {
    ("check-tree.md", 19): "misplaced section",
    ("limits.md", 18): "board's",
}


def _leaves() -> dict[str, list[Path]]:
    """Each leaf's H1 anchor, mapped to the files in the tree carrying that title."""
    leaves: dict[str, list[Path]] = {}
    for path in sorted(TREE.rglob("*.md")):
        for _, anchor in heading_anchor_list(path.read_text(encoding="utf-8").split("\n")):
            leaves.setdefault(anchor.base, []).append(path.resolve())
            break
    return leaves


def wrong_targets() -> list[str]:
    """Every citation whose link text names one leaf's H1 and whose target is another file, as
    `<file>:<line>: <target> -> <the leaf its text names>`; the standing sites are left out."""
    leaves = _leaves()
    wrong: list[str] = []
    for path in sorted(TREE.rglob("*.md")):
        fence = FenceTracker()
        for no, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if fence.inside(line) or (path.name, no) in STANDING:
                continue
            links: list[tuple[str, str]] = []

            def collect(raw: str, text: str, target: str, after: str) -> str:
                links.append((text, target))
                return raw

            scan(line, collect)
            for text, target in links:
                if "://" in target:
                    continue
                target_path = target.split("#", 1)[0]
                landed = (path.parent / target_path).resolve() if target_path else path.resolve()
                elsewhere = [leaf for leaf in leaves.get(github_anchor(text), []) if leaf != landed]
                if elsewhere:
                    named = ", ".join(str(leaf.relative_to(ROOT)) for leaf in elsewhere)
                    wrong.append(f"{path.relative_to(ROOT)}:{no}: {target} -> {named}")
    return wrong


def test_every_citation_lands_on_the_leaf_its_text_names() -> None:
    wrong = wrong_targets()
    assert wrong == [], f"{len(wrong)} citation(s) landing on a leaf other than the one its text names:\n" + "\n".join(
        wrong
    )
