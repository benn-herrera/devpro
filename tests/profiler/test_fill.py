"""strict_fill"""

from pathlib import Path

import pytest

from devpro.profiler.pages import (
    BAND_LEGEND,
    DATA_MARK,
    DECO_MARK,
    DISPATCHED_MARK,
    INDEX,
    LAYER_MARK,
    PROJECT_MARK,
    PROJECT_TITLE_MARK,
    RETURN_MARK,
    index_html,
)

from .conftest import _PACKAGE_ROOT, _fetch, _installed_wrapper, _run, _serve, _write_store


def test_the_strict_fill_refuses_unknown_and_unfilled_marks_and_leaves_none_standing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`clauses.TEST_PRECONDITION`: a test a package adds is written for a named defect and the run
    that fails under it before the change. The defect is the render's silent no-op `str.replace` — a
    mark the fill is told to fill but the text no longer carries, left unfilled without a word — and
    the run fails before the strict fill exists to raise on it.

    The strict fill every profiler fill now runs through refuses a placeholder it is told to fill
    that the text no longer carries, and leaves no mark it filled standing. `index_html`, fed an
    `INDEX` whose legend mark the text no longer carries yet still told to fill it, raises;
    `strict_fill` on `view.html` with a mark removed, still told to fill it, raises the same. A rendered session page
    and the served page and index then carry no mark the fill was handed standing — the title's
    project-name mark and the nav's among them, filled on every page that carries them. The `INDEX` swap
    is for this check alone: `monkeypatch` reverts at the end and the serve below runs in a child
    process that reads `INDEX` from disk, so nothing after it sees the swap."""
    # (a) `index_html`: an `INDEX` whose legend mark the text no longer carries, still told to fill it.
    monkeypatch.setattr("devpro.profiler.pages.INDEX", INDEX.replace(BAND_LEGEND, ""))
    with pytest.raises(KeyError):
        index_html("project")
    # (a) the fill itself: `view.html` with a mark removed, still told to fill it.
    from devpro.profiler.pages import project_fills, strict_fill

    view_text = (_PACKAGE_ROOT / "devpro" / "profiler" / "view.html").read_text(encoding="utf-8")
    fills = {DATA_MARK: "data", LAYER_MARK: "layer", BAND_LEGEND: "legend", **project_fills("project")}
    with pytest.raises(KeyError):
        strict_fill(view_text.replace(BAND_LEGEND, ""), fills)
    # (a) the fill's own strictness: a value carrying its mark leaves it standing — refused.
    with pytest.raises(KeyError):
        strict_fill(BAND_LEGEND, {BAND_LEGEND: BAND_LEGEND})
    # (b) nothing the fill was handed is left standing, standalone or served.
    project = tmp_path / "project"
    project.mkdir()
    _write_store(project, ".profiler-claude", "s-claude", "2026-01-01T00:00:00.000Z", harness="claude", records=2)
    launcher = _installed_wrapper(tmp_path / "harness")
    printed = _run(launcher, "tree", "s-claude", "--format", "html", cwd=project)
    assert printed.returncode == 0, printed.stderr
    marks = (
        LAYER_MARK,
        DECO_MARK,
        DATA_MARK,
        BAND_LEGEND,
        DISPATCHED_MARK,
        RETURN_MARK,
        PROJECT_TITLE_MARK,
        PROJECT_MARK,
    )
    for mark in marks:
        assert mark not in printed.stdout, f"{mark} left standing in the rendered page"
    with _serve(cwd=project) as url:
        page = _fetch(f"{url}page/s-claude")
        index = _fetch(f"{url}profiler/")
    for mark in marks:
        assert mark not in page, f"{mark} left standing in the served page"
        assert mark not in index, f"{mark} left standing in the served index"
    assert "$rows" not in index


def test_the_strict_fill_refuses_a_value_carrying_another_marks_mark() -> None:
    """`clauses.TEST_PRECONDITION`: the defect is a fill that refuses a value carrying its own mark
    only, so a value carrying a later mark is read as that mark and filled. A value is inserted as
    it stands, never read for a mark of the same fill, so such a value is refused, not filled."""
    from devpro.profiler.pages import strict_fill

    with pytest.raises(KeyError):
        strict_fill(f"{BAND_LEGEND}{RETURN_MARK}", {BAND_LEGEND: RETURN_MARK, RETURN_MARK: "back"})
