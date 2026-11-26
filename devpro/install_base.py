"""What the install modules share: where this package and its checkout sit, the kbase skill's directory
and the kb-tools package's destination inside it, the devpro tools package's directory and its wrapper,
the one-line banners a carried file and a harness resource each state their origin in, UTF-8 text reading
that keeps each line's ending, and
the stderr report of what an install left alone."""

import re
import sys
from pathlib import Path

from devpro.errors import InputError


def checkout_root(package_root: Path) -> Path | None:
    """`package_root`'s parent when it holds a `.git` entry — a directory in a clone, a file in a
    worktree — else None. A package installed outside a checkout of this repository, a wheel in
    site-packages, is not in one even where another project's repository encloses it."""
    parent = package_root.parent
    return parent if (parent / ".git").exists() else None


PACKAGE_ROOT = Path(__file__).resolve().parent
"""The directory the running devpro package resolves to: the one source `require_outside_package_source`
refuses an install into, the installation's copy an install run from it refuses to replace, and the one
`init` refuses a repository's root being."""
REPO_ROOT = checkout_root(PACKAGE_ROOT)

KBASE_SKILL_DIR = "skills/kbase"
# Below ROOT: where the kb-tools package is delivered, inside the kbase skill's own directory.
KB_TOOLS_DIR = f"{KBASE_SKILL_DIR}/kb-tools"
# Below ROOT: the devpro tools package — the installation's own copy of devpro and the runner snippets
# — and the wrapper that runs that copy, which every installed hook and skill names by its own knowledge.
TOOLS_DIR = "tools"
WRAPPER = f"{TOOLS_DIR}/devpro.sh"
# The mark a carried file's banner opens with: `stamped` writes it, and a harness resource carries it as
# its own text on one of its first lines, in whatever comment syntax its format takes.
INSTALLED_MARK = "!INSTALLED!"
# A carried file's installed banner: the mark, a word naming where it came from, and the repository's
# name. A harness resource and a rendered definition's digest (`devpro.profiler.directives`) read it.
INSTALLED_BANNER = re.compile(re.escape(INSTALLED_MARK) + r" .* devpro")


def untranslated_text(path: Path) -> str:
    """`path`'s text, decoded as UTF-8 with no newline translation so a rewrite keeps each line's own
    ending. Raises what opening or decoding it raises."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def utf8_text(path: Path) -> str:
    """`path`'s `untranslated_text`. A file that cannot be read or decoded is refused, naming it."""
    try:
        return untranslated_text(path)
    except (OSError, UnicodeError) as exc:
        raise InputError(f"'{path}' is not readable UTF-8 text: {exc}") from exc


def report_left_alone(message: str) -> None:
    """Print `message`, naming something the install left alone or skipped, on stderr: the write log
    is stdout, which the preflight discards, and this report is owed on every run."""
    print(message, file=sys.stderr)
