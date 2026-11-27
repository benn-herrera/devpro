"""stamped_/stored_• directives digest• ownership markers"""

import hashlib
import json
from pathlib import Path

from devpro.components import NAME
from devpro.harnesses import claude, mage, opencode
from devpro.install_base import HARNESS_OWNERSHIP_MARKERS
from devpro.profiler.capture import mask, stored_stamp
from devpro.profiler.directives import read_stamp
from devpro.profiler.values import earliest_stamp

from .conftest import _HERE, _MASK_SAMPLES, _digest_runner, _plan, _run_ts


def test_the_two_masks_redact_alike(tmp_path: Path) -> None:
    """The profiler's `mask` and the port's, over one sample list: each sample's masked text is the same on
    both sides, the non-ASCII credential included, and an `apikey` key masked by both — the port's
    alternation once read `api_?key`, which left that key alone."""
    samples = (_HERE / _MASK_SAMPLES).read_text(encoding="utf-8").splitlines()
    run = _run_ts(_HERE / "profiler_mask_runner.ts", directory=tmp_path, arg=str(_HERE / _MASK_SAMPLES))
    ported = [json.loads(line) for line in run.stdout.splitlines()]

    assert ported == [mask(sample) for sample in samples]


def test_the_two_captures_digest_one_project_state_alike(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: the two captures walked different file sets and hashed them
    with two encodings — the TS side skipped a file link and read an ownership marker only where its list
    held one, the Python's `ensure_ascii` escape diverged from `JSON.stringify` on a non-ASCII path — so one
    project state gave two digests, and no test ran the TS side's digest at all.

    The one fixture project, its files planted in every walked directory: a banner-carried file and a
    rendered one under `.claude/`, the ownership-markered registry under `.opencode/` and mage's guardrail
    registration under `devpro/`, a file link and a non-ASCII-named file, a directory link to a file outside
    the harness directories, its `AGENTS.md`. The shipped `profiler.ts`'s stamp is byte-equal to the one
    `devpro/profiler/directives` computes for the same root, digest and per-file manifest alike; the
    symlinked file is hashed as its target, and the directory link's file and the `CLAUDE.md` redirect enter
    neither."""
    project = tmp_path / "project"
    harness = project / ".claude" / "skills" / "devpro"
    marked = project / ".opencode" / "plugins" / "devpro"
    registration = project / "devpro" / "skills" / "devpro" / "hooks.json"
    outside = tmp_path / "outside"
    for directory in (harness / "agents", marked, registration.parent, outside):
        directory.mkdir(parents=True)
    _plan(project, "a plan")
    (harness / "agents" / "coder.md").write_text("# !GENERATED! from devpro/a.py\nbody\n", encoding="utf-8")
    (harness / "scripts" / "run.sh").parent.mkdir()
    (harness / "scripts" / "run.sh").write_text(
        "#!/bin/sh\n# !INSTALLED! from devpro/x.sh — devpro\n", encoding="utf-8"
    )
    (marked / "registry.json").write_text('{\n  "plugin": "devpro"\n}\n', encoding="utf-8")
    registration.write_text('{"message": "no readable script at x"}\n', encoding="utf-8")
    (outside / "shared.md").write_text("# !GENERATED! from devpro/b.py\nshared\n", encoding="utf-8")
    (harness / "agents" / "linked.md").symlink_to(harness / "agents" / "coder.md")
    (harness / "agents" / "café.md").write_text("# !GENERATED! from devpro/c.py\nbody\n", encoding="utf-8")
    (harness / "elsewhere").symlink_to(outside, target_is_directory=True)
    (project / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
    (project / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")

    stamp, manifest = read_stamp(project)
    ported = _digest_runner(project, tmp_path / "probe")

    assert ported["stamp"] == stamp
    assert ported["manifest"] == manifest
    assert sorted(manifest) == [
        ".claude/skills/devpro/agents/café.md",
        ".claude/skills/devpro/agents/coder.md",
        ".claude/skills/devpro/agents/linked.md",
        ".claude/skills/devpro/scripts/run.sh",
        ".opencode/plugins/devpro/registry.json",
        "AGENTS.md",
        "devpro/skills/devpro/hooks.json",
    ]


def test_the_ts_digest_reads_an_ownership_marker_the_python_reads(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: the two captures' marker lists drifted — the TS side held no
    registry's, so a project whose only directive was `registry.json` digested to nothing on that side and
    to a digest on the Python's.

    A project holding no banner but the ownership-markered `registry.json`: both captures digest it, and
    they agree."""
    project = tmp_path / "project"
    registry = project / ".opencode" / "plugins" / "devpro" / "registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text('{\n  "plugin": "devpro"\n}\n', encoding="utf-8")
    stamp, digests = read_stamp(project)

    assert digests == {".opencode/plugins/devpro/registry.json": hashlib.sha256(registry.read_bytes()).hexdigest()}
    ported = _digest_runner(project, tmp_path / "probe")
    # No plan stands, so the Python capture leaves `plan` out and the port writes it `null`: the digest and
    # its manifest are the two captures' to agree on.
    assert ported["stamp"]["directives"] == stamp["directives"]
    assert ported["manifest"] == digests


def test_the_ownership_markers_agree_with_the_harnesses_that_write_them(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: a harness-rendered file's ownership marker was recognized by
    nothing at the digest, so `registry.json` and `hooks.json` never reached it, and the TS side's list had
    no home from which the Python's could be read.

    Every marker a harness of this project writes — each rendered file's, each registry's, each guardrail
    registration's, the `{plugin}` filled — starts with one of `HARNESS_OWNERSHIP_MARKERS`, and the shipped
    `profiler.ts`'s list is the same set: where these drift, one side's digest holds a file the other's
    does not."""
    bound = [harness.HARNESS.bound(NAME) for harness in (claude, opencode, mage)]
    written = [
        *((file.marker for file in bound_harness.harness_files) for bound_harness in bound),
        *((bound_harness.guardrail.registration.marker,) for bound_harness in bound if bound_harness.guardrail),
    ]
    assert all(marker.startswith(HARNESS_OWNERSHIP_MARKERS) for markers in written for marker in markers)
    ported = _digest_runner(tmp_path, tmp_path / "probe", markers=True)["markers"]
    assert ported == list(HARNESS_OWNERSHIP_MARKERS)


def test_the_capture_and_the_read_side_select_the_earliest_stamp_by_one_rule(tmp_path: Path) -> None:
    """`clauses.TEST_PRECONDITION`. The defect: the read side and the capture selected a store's
    earliest stamp differently — the read skipped a record with no `at` where the capture ordered by
    it — so a store holding one stamped a page stated as unstamped while the capture copied that
    stamp onto every later record, the page and the capture disagreeing about one session's stamp.

    A record with no `at` never governs the ordering, on either side: the two readers pick the one
    stamped record carrying an `at`, whichever order the records stand in, and a store of stamped
    records none of which carries one is unstamped to both."""
    store = tmp_path / "s.jsonl"
    unplaced = {"session": "s", "plan": "no moment", "directives": "d" * 64}
    placed = {"session": "s", "at": "2026-01-01T00:00:00.000Z", "plan": "at start", "directives": "a" * 64}
    store.write_text("\n".join(json.dumps(record) for record in (unplaced, placed)) + "\n", encoding="utf-8")

    assert earliest_stamp([unplaced, placed]) == {"plan": "at start", "directives": "a" * 64}
    assert stored_stamp(store) == {"plan": "at start", "directives": "a" * 64}
    store.write_text(json.dumps(unplaced) + "\n", encoding="utf-8")

    assert earliest_stamp([unplaced]) == {}
    assert stored_stamp(store) is None
