"""The directives a session starts under, as one digest: every file beneath the project's harness
directories that carries an installed banner or an ownership marker, and the project's `AGENTS.md`, each
digested and the digests hashed into one.

Read on a capture's first record of a session (`read_stamp`), and on the opencode capture's `execute`
hook — the same set, walked the same way, hashed by the same construction, in the plugin's TypeScript,
where `tests/profiler_digest_runner.ts` holds the two byte-equal. The set is whatever stands at that
moment, so the digest fingerprints state and not install history. Standard library only.
"""

import hashlib
import os
from pathlib import Path

from ..install_base import HARNESS_OWNERSHIP_MARKERS, INSTALLED_BANNER
from .values import Json, _json, read_text

# A harness's project harness directory below the project root. `devpro install` resolves the harness from
# the harness's own module, which loads the renderer, so the directories are stated here: a capture runs on
# the every-tool-call path and imports none of it. `.opencode/` is opencode's, beside the `.claude/` it also
# loads; `devpro/` is mage's. The digest covers all three whatever harness the session runs on, so one
# project state is one digest on either capture.
PROJECT_HARNESS_DIRS = (".claude", ".opencode", "devpro")
# The project's agents file is the project root's `AGENTS.md`, where the install keeps its block: the
# digest covers it whenever it stands and is no redirect, whether or not the block is in it. It is no
# harness directory's file.
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
# The prefix of a redirect file's only line: `@AGENTS.md`, written by a harness that reads the agents file
# under another name. `devpro.agents_file.REDIRECT_PREFIX` holds it, named here because that module is the
# install's and a capture imports none of it.
REDIRECT_PREFIX = "@"


def directive_files(root: Path) -> list[Path]:
    """Every file beneath each of `root`'s harness directories that carries an installed banner or an
    ownership marker, then `root`'s `AGENTS.md` where it stands — every path walked, whatever harness the
    session runs on.

    The walk is `os.walk`'s, which enters no directory link — so it cannot leave a harness directory or
    cycle — and follows a file link's target, as the opencode capture's walk does; a file is a file where
    what it points at is one. An `AGENTS.md` that is a redirect naming another file — its only non-blank
    line `@<path>` — carries no directive of its own, and the digest omits it."""
    files = [
        Path(directory, name)
        for harness in PROJECT_HARNESS_DIRS
        for directory, _, names in os.walk(Path(root, harness))
        for name in sorted(names)
        if is_installed(Path(directory, name))
    ]
    agents_file = Path(root, AGENTS_FILE)
    if agents_file.is_file() and not is_redirect(read_text(agents_file)):
        files.append(agents_file)
    return sorted(files)


def is_redirect(text: str | None) -> bool:
    """Whether `text` is a redirect — its only non-blank line `@<path>` — which names another file and
    carries no directive of its own. Read as `devpro.agents_file` writes and follows one."""
    lines = [line.strip() for line in (text or "").split("\n") if line.strip()]
    return len(lines) == 1 and lines[0].startswith(REDIRECT_PREFIX) and len(lines[0]) > len(REDIRECT_PREFIX)


def is_installed(path: Path) -> bool:
    """Whether the file is one an install wrote: a rendered definition, by the `!GENERATED!` banner on one
    of its first two lines; a carried file, by its installed banner on one of its first ten, or by the
    ownership marker a harness-rendered file states in its content."""
    text = read_text(path)
    if text is None:
        return False
    lines = text.split("\n")
    if any(GENERATED_BANNER in line for line in lines[:GENERATED_BANNER_HEAD]):
        return True
    if any(INSTALLED_BANNER.search(line) for line in lines[:BANNER_LINES]):
        return True
    return any(marker in text for marker in HARNESS_OWNERSHIP_MARKERS)


def file_digest(path: Path) -> str:
    """sha256 of the file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: object) -> bytes:
    """The encoder a digest is hashed through: compact JSON, its non-ASCII text as UTF-8 bytes and its
    separators as the two ASCII characters. `ensure_ascii=False` is the half that binds the two captures:
    `profiler.ts` hashes the same text to the same bytes, where a `\\uXXXX` escape would diverge from it."""
    return _json(value, ensure_ascii=False).encode("utf-8")


def digest_of(digested: Json) -> str:
    """The digest of the per-file digests: sha256 over their sorted `(path, digest)` pairs, path and
    digest the bytes `_canonical` gives them."""
    return hashlib.sha256(_canonical(sorted(digested.items()))).hexdigest()


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
    """The digest's manifest, holding its per-file digests: a digest's file list is recoverable, and two
    digests' difference answerable. The per-file digests are recomputed from the files as they stand, so
    a manifest written here may postdate the digest it is keyed by and name files that have moved since.
    What `digested` does not hold — a digest copied off a store, whose files it never recomputed — is
    written nowhere: a manifest of nothing is no manifest. `.profiler-directives` is no store — a prefix
    of `.profiler-` and none of the store names the readers read."""
    if not digested:
        return
    path = Path(root) / ".devpro-temp" / ".profiler-directives" / f"{digest_of(digested)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json(digested) + "\n", encoding="utf-8")
