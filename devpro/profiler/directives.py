"""The directives a session starts under, as one digest: the project's harness directories' installed
files, and the project's agents file, each digested and the digests hashed into one.

Read on a capture's first record of a session (`read_stamp`), and on the opencode capture's `execute`
hook — the same set and the same hash, in the plugin's TypeScript. The set is whatever stands at that
moment, so the digest fingerprints state and not install history. Standard library only.
"""

import hashlib
from pathlib import Path

from ..install_base import INSTALLED_BANNER
from .values import Json, _json, read_text

# A harness's project harness directory below the project root. `devpro install` resolves the harness from
# the harness's own module, which loads the renderer, so the directories are stated here: a capture runs on
# the every-tool-call path and imports none of it. `.opencode/` is opencode's, beside the `.claude/` it also
# loads; `devpro/` is mage's.
PROJECT_HARNESS_DIRS = (".claude", ".opencode", "devpro")
# What a project harness directory holds is read whole: an install's files sit at depths that differ by
# harness — `.claude/skills/<plugin>/agents/<file>.md`, `.opencode/plugins/<plugin>/registry.json`,
# `devpro/skills/<plugin>/…` — and a file an install wrote is known by its banner or marker, not its path.
INSTALLED_DIRECTORY = "**/*"
# The project's agents file is the project root's `AGENTS.md`, where the install keeps its block: the
# digest covers it whenever it stands, whether or not the block is in it. It is no harness directory's file.
AGENTS_FILE = Path("AGENTS.md")
# Where a project's active plan stands: the plain plan first, then the diced plan's entry.
PLAN_FILES = (Path("ACTIVE_PLAN.md"), Path("ACTIVE_PLAN") / "entry-point.md")
HEADING = "# "
# A rendered definition's banner is written first: `# !GENERATED! from …` in its frontmatter, or inside
# the HTML comment a skill's supporting file opens with, and on the second line behind a frontmatter fence.
GENERATED_BANNER = "!GENERATED! from "
GENERATED_BANNER_HEAD = 2
# A carried file's installed banner sits on one of the file's first ten lines.
BANNER_LINES = 10


def directive_files(root: Path) -> list[Path]:
    """The directive files standing under `root`: every installed file of a project harness directory, and
    the project's agents file where it stands."""
    files = [
        path
        for name in PROJECT_HARNESS_DIRS
        if Path(root, name).is_dir()
        for path in sorted(Path(root, name).glob(INSTALLED_DIRECTORY))
        if path.is_file() and is_installed(path)
    ]
    agents_file = Path(root, AGENTS_FILE)
    return [*files, agents_file] if agents_file.is_file() else files


def is_installed(path: Path) -> bool:
    """Whether the file is one an install wrote: a rendered definition, by the `!GENERATED!` banner on one
    of its first two lines; a carried file, by its installed banner on one of its first ten."""
    text = read_text(path)
    if text is None:
        return False
    lines = text.split("\n")
    if any(GENERATED_BANNER in line for line in lines[:GENERATED_BANNER_HEAD]):
        return True
    return any(INSTALLED_BANNER.search(line) for line in lines[:BANNER_LINES])


def file_digest(path: Path) -> str:
    """sha256 of the file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_of(digested: Json) -> str:
    """The digest of the per-file digests: sha256 over their sorted `(path, digest)` pairs."""
    return hashlib.sha256(_json(sorted(digested.items())).encode("ascii")).hexdigest()


def plan_title(root: Path) -> str | None:
    """The active plan's title at `root`: the first level-1 heading of `ACTIVE_PLAN.md`, or of the diced
    plan's `ACTIVE_PLAN/entry-point.md`; nothing where neither stands."""
    for name in PLAN_FILES:
        for line in (read_text(root / name) or "").split("\n"):
            if line.startswith(HEADING):
                return line[len(HEADING) :].strip() or None
    return None


def read_stamp(root: Path) -> tuple[Json, Json]:
    """The stamp's fields for a session starting at `root`, computed from the directives standing now, and
    the per-file digests they were hashed from — what the digest's manifest records.

    A field the project gives the capture nothing for is left out: `plan` the active plan's title,
    `directives` the digest of the directive files, absent where none stands."""
    digests = {path.relative_to(root).as_posix(): file_digest(path) for path in directive_files(root)}
    found = {"plan": plan_title(root), "directives": digest_of(digests) if digests else None}
    return {key: value for key, value in found.items() if value is not None}, digests


def write_manifest(root: Path, digested: Json) -> None:
    """The digest's manifest, holding its per-file digests, where none for the digest stands: a digest's
    file list is recoverable, and two digests' difference answerable. `.profiler-directives` is no store —
    a prefix of `.profiler-` and none of the store names the readers read."""
    if not digested:
        return
    path = Path(root) / ".devpro-temp" / ".profiler-directives" / f"{digest_of(digested)}.json"
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json(digested) + "\n", encoding="utf-8")
