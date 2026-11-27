"""The test fixtures read from disk, under the directory each runner takes by name.

A fixture is a file a test reads, never one that drove a run: a file that vouches for the world its
producing runner copied is the removed stand-ins' shape, and a fixture stands in its place only where
what it holds is the input a shipped function is measured over.

`profiler_serialize_record.json` is a probe dispatch record from the shipped `profiler.ts`, written
through the capture runner and frozen here when that runner was removed. It is the input
`test_a_line_over_the_bound_is_fitted_at_its_root` measures `serialize` over, and it is not derived
from the capture: a field the record gains, renames or drops leaves the fixture holding the old shape,
and no test reads the record's key set from the construction. The capture's own records are the
contract runner's, `tests/profiler_contract_runner.ts`.
"""

from pathlib import Path

FIXTURES = Path(__file__).parent


def fixture_file(name: str) -> Path:
    """The fixture written under `name` in this directory."""
    return FIXTURES / name
