r"""End-to-end tests for the dicing verbs.

Each case under data/ is one test: the CLI runs as a subprocess in a copy of the case's input/,
made in the test's tmp_path, with the arguments in `args` (one per line). The exit status and
every file of expected/tree/ must match byte for byte. expected/names asserts the values the output
carries, never its wording: each of its lines is an entry `<stream>[\t<name>...]`, <stream> being
stdout or stderr, and each entry stands for one line of that stream. A stream must end in a newline
unless empty, and must have exactly as many lines as it has entries, each entry given a distinct
line it matches; a stream with no entries is empty. An entry with no names matches any line;
otherwise its names are found in the line left to right, each as a whole token (no ASCII letter or
digit beside it, nor a `.` or `-` joined to one), compared as UTF-8 bytes with surrogateescape.

COLUMNS is set wide so that argparse never wraps a usage line. Cases are written from SPEC.md.

Each case that dices and exits 0 is also a round-trip test: its tree, undiced and
then diced again from the same run directory at the case's `--split-level`, comes back byte for
byte.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

MODULE = "devpro"
HERE = Path(__file__).resolve().parent
TESTDATA = HERE / "data"


def _files(root: Path, skip: str = "") -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.relative_to(root).as_posix() != skip
    }


def _case_env(case: Path) -> dict[str, str]:
    return {**os.environ, "COLUMNS": "1000"}


def _cases() -> list[Path]:
    return sorted(p for p in TESTDATA.iterdir() if p.is_dir())


def _args(case: Path) -> list[str]:
    return (case / "args").read_text(encoding="utf-8").splitlines()


def _split_level_apart(args: list[str]) -> tuple[list[str], list[str]]:
    """args' `--split-level <level>`, empty where they hold none, and the other args in order."""
    if "--split-level" not in args:
        return [], args
    at = args.index("--split-level")
    return args[at : at + 2], args[:at] + args[at + 2 :]


def _round_trip_cases() -> list[Path]:
    return [
        case
        for case in _cases()
        if _args(case)[0] == "dice"
        and "--out" in _args(case)
        and (case / "expected" / "exit").read_text(encoding="utf-8") == "0\n"
    ]


def _dicing(run: Path, args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([sys.executable, f"-m{MODULE}", *args], cwd=run, env=env, capture_output=True)


def _lines(data: bytes, what: str) -> list[bytes]:
    """data split at newlines after removing its final one; empty data has no lines."""
    if not data:
        return []
    assert data.endswith(b"\n"), f"{what} does not end in a newline:\n{data!r}"
    return data[:-1].split(b"\n")


def _token(name: bytes) -> "re.Pattern[bytes]":
    return re.compile(
        rb"(?<![A-Za-z0-9])(?<![A-Za-z0-9][.-])" + re.escape(name) + rb"(?![A-Za-z0-9])(?![.-][A-Za-z0-9])"
    )


def _entry_matches(names: list[bytes], line: bytes) -> bool:
    pos = 0
    for name in names:
        # search from pos rather than slicing, so the lookbehinds see the bytes before pos
        found = _token(name).search(line, pos)
        if found is None:
            return False
        pos = found.end()
    return True


def _one_to_one(entries: list[list[bytes]], lines: list[bytes]) -> bool:
    """True when each entry can be given a distinct line it matches: bipartite matching by
    augmenting paths, since a first-fit choice can take the only line a later entry matches."""
    holder: dict[int, int] = {}

    def place(entry: int, tried: set[int]) -> bool:
        for line, text in enumerate(lines):
            if line not in tried and _entry_matches(entries[entry], text):
                tried.add(line)
                if line not in holder or place(holder[line], tried):
                    holder[line] = entry
                    return True
        return False

    return all(place(entry, set()) for entry in range(len(entries)))


def _assert_names(names_file: Path, streams: dict[str, bytes]) -> None:
    text = names_file.read_text(encoding="utf-8", errors="surrogateescape")
    expected: dict[bytes, list[list[bytes]]] = {stream.encode(): [] for stream in streams}
    for entry in _lines(text.encode("utf-8", "surrogateescape"), str(names_file)):
        stream, *names = entry.split(b"\t")
        assert stream in expected and all(names), f"malformed names line: {entry!r}"
        expected[stream].append(names)
    for stream, data in streams.items():
        entries, lines = expected[stream.encode()], _lines(data, stream)
        assert len(lines) == len(entries) and _one_to_one(entries, lines), f"{stream} vs {entries!r}:\n{data!r}"


@pytest.mark.parametrize(
    "line, found",
    [(b"x 1", True), (b"x 12", False), (b"x 1.1", False), (b"\xc2\xa71(2)", True), (b"level 1.", True), (b"-1", True)],
)
def test_a_name_matches_as_a_whole_token(line: bytes, found: bool) -> None:
    assert _entry_matches([b"1"], line) is found


def test_names_are_found_left_to_right() -> None:
    assert _entry_matches([b"a", b"b"], b"a then b")
    assert not _entry_matches([b"b", b"a"], b"a then b")


def test_entries_take_distinct_lines_where_first_fit_would_not() -> None:
    assert _one_to_one([[], [b"x"]], [b"x 1", b"y 2"])
    assert not _one_to_one([[b"x"], [b"x"]], [b"x 1", b"y 2"])


def test_cases_exist() -> None:
    assert _cases(), "no cases under data/"


@pytest.mark.parametrize("case", _cases(), ids=lambda case: case.name)
def test_cases(case: Path, tmp_path: Path) -> None:
    run = tmp_path / "run"
    shutil.copytree(case / "input", run, symlinks=True)
    args = _args(case)
    proc = _dicing(run, args, _case_env(case))
    expected = case / "expected"
    assert f"{proc.returncode}\n" == (expected / "exit").read_text(encoding="utf-8")
    assert _files(run) == _files(expected / "tree")
    _assert_names(expected / "names", {"stdout": proc.stdout, "stderr": proc.stderr})


def test_round_trip_cases_exist() -> None:
    assert _round_trip_cases(), "no case dices and exits 0"


@pytest.mark.parametrize("case", _round_trip_cases(), ids=lambda case: case.name)
def test_undice_then_dice_reproduces_the_tree(case: Path, tmp_path: Path) -> None:
    """A tree the case dices: undiced to its document, then diced again from the same run
    directory, both at the case's split level, it comes back byte for byte, both runs exiting 0."""
    run = tmp_path / "run"
    shutil.copytree(case / "expected" / "tree", run, symlinks=True)
    split_level, args = _split_level_apart(_args(case))
    out = args[args.index("--out") + 1]
    env = _case_env(case)
    undiced = _dicing(run, ["undice", *split_level, out, "undoc"], env)
    assert undiced.returncode == 0, undiced.stderr
    section = ["--section"] if "--section" in args else []
    (run / out).rename(run / "diced")
    # a document's links are relative to the directory the verb runs in, which is where undice
    # wrote the documents; a volume tree's undice writes one document per volume, the omnibus's own
    # head is not written, and those documents are what the re-dice is given
    (run / "undoc").rename(run / "documents")
    documents = sorted(p.name for p in (run / "documents").glob("*.md"))
    rediced = subprocess.run(
        [sys.executable, f"-m{MODULE}", "dice", *split_level, *section, *documents, "--out", f"../{out}"],
        cwd=run / "documents",
        env=env,
        capture_output=True,
    )
    assert rediced.returncode == 0, rediced.stderr
    assert _files(run / out) == _files(run / "diced")


def _unplaced(files: dict[str, bytes]) -> list[str]:
    """The tree's files that are not a document its form places: every one is `.md`, and its name is
    a head's (`entry-point.md`, `index.md`) or it is a leaf under a directory that has a head."""
    names = set(files)
    unplaced = []
    for path in files:
        if not path.endswith(".md"):
            unplaced.append(path)
            continue
        name = path.rsplit("/", 1)[-1]
        directory = path.rsplit("/", 1)[0] if "/" in path else ""
        if name in ("entry-point.md", "index.md"):
            continue
        if directory and any(f"{directory}/{head}" in names for head in ("entry-point.md", "index.md")):
            continue
        if not directory and "entry-point.md" in names:
            continue  # a one-document tree's section beside its root head
        unplaced.append(path)
    return sorted(unplaced)


def test_a_tree_holds_only_the_documents_its_form_places_and_no_run_adds_one(tmp_path: Path) -> None:
    """A tree `dice` writes is its documents and nothing else: every file is one the head convention
    places, and a second run over the same tree and output directory adds no file and changes none.

    The defect: sideband data persisted into the tree — the retired map cache — gave a later run an
    ambient dependency on a previous run's state, and no assertion over the files a run declares
    catches a file a run leaves behind."""
    run = tmp_path / "run"
    run.mkdir()
    (run / "alpha.md").write_text("# Alpha\n\nIntro.\n\n## One\n\none text\n", encoding="utf-8")
    (run / "beta.md").write_text("# Beta\n\nIntro.\n\n## First\n\nfirst text\n", encoding="utf-8")
    env = _case_env(run)
    first = _dicing(run, ["dice", "alpha.md", "beta.md", "--out", "tree"], env)
    assert first.returncode == 0, first.stderr
    tree = run / "tree"
    files = _files(tree)
    assert list(files), "the dice wrote no tree"
    assert _unplaced(files) == []
    assert any(path.endswith("entry-point.md") for path in files), "the dice wrote no volume head"
    # the second run targets the same tree and output directory: a tree that is not empty is refused
    # rather than merged into, so no file can be added to the first one
    second = _dicing(run, ["dice", "alpha.md", "beta.md", "--out", "tree"], env)
    assert second.returncode == 2, second.stderr
    assert _files(tree) == files


def test_a_trees_links_between_its_own_documents_resolve_wherever_the_tree_stands(tmp_path: Path) -> None:
    """A link between two documents of one dice resolves between their positions in the tree, so it
    is the same link wherever the tree is placed: move the whole tree under another parent and every
    link still resolves and the tree undices to the same document.

    The defect: links written against the directory the documents were read from resolve only at the
    place the dice ran; moved, a tree whose shape is right no longer resolves, as SUB's re-dice of
    SPEC showed."""
    source = TESTDATA / "dice-reintegration" / "input"
    run = tmp_path / "run"
    shutil.copytree(source, run, symlinks=True)
    env = _case_env(run)
    diced = _dicing(run, ["dice", "alpha.md", "beta.md", "--out", "tree"], env)
    assert diced.returncode == 0, diced.stderr
    tree = run / "tree"
    before = _files(tree)
    # the tree moves into a parent it did not stand under, and the run directory's documents go
    # with it, so anything resolved against them would break
    moved = tmp_path / "moved" / "deeper"
    moved.mkdir(parents=True)
    shutil.move(str(tree), str(moved / "tree"))
    shutil.rmtree(run)
    placed = moved / "tree"
    links = _dicing(moved, ["check-links", "tree"], env)
    assert links.returncode == 0, links.stderr
    assert _files(placed) == before
