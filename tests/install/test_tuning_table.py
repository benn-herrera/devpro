"""the tuning table an install writes at ROOT's root"""

from pathlib import Path, PurePosixPath

import pytest

from devpro.context import Render, map_spec
from devpro.render import render_all

from .conftest import (
    _CLAUDE_RENDER,
    _MAGE_RENDER,
    _OPENCODE_RENDER,
    _definition_install,
)

# One install of each harness, and the harness directory each installs into: the plugin sits below it
# (`""` for mage, whose harness directory is the plugin itself), so ROOT — and the table at its root —
# is `harness_dir` joined with the render's bound plugin directory.
_HARNESS_INSTALLS = (
    (_CLAUDE_RENDER, ".claude"),
    (_OPENCODE_RENDER, ".opencode"),
    (_MAGE_RENDER, "plugins/devpro"),
)
_HARNESS_INSTALL_IDS = [ctx.harness.name for ctx, _ in _HARNESS_INSTALLS]


@pytest.mark.parametrize(
    ("ctx", "harness_dir"),
    _HARNESS_INSTALLS,
    ids=_HARNESS_INSTALL_IDS,
)
def test_the_install_writes_the_tuning_table_beside_its_renders(tmp_path: Path, ctx: Render, harness_dir: str) -> None:
    """The install writes the tuning table at ROOT's own root, beside the rendered definitions'
    directories, where `render_all` puts no file so the two never collide: the table the run wrote is
    read back off disk, its bytes the render's own family, effective map, stock list and harness. The
    write is one line in `install`; deleting it leaves no `tuning.md` to read back, so this fails."""
    assert PurePosixPath("tuning.md") not in dict(render_all(ctx))
    directory = tmp_path / harness_dir
    directory.mkdir(parents=True)
    _definition_install(directory, ctx, project_root=tmp_path)
    table = directory / ctx.bound_harness.plugin_dir / "tuning.md"
    assert table.read_text(encoding="utf-8") == (
        f"- family={ctx.family.name}\n"
        f"- category-map={map_spec(ctx.category_map)}\n"
        f"- stock={','.join(ctx.stock) or 'none'}\n"
        f"- harness={ctx.harness.name}\n"
    )
