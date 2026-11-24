"""The test fixtures read from disk, under the directory each runner takes by name.

A fixture is a file a test reads, never one that drove a run: a file that vouches for the world its
producing runner copied is the removed stand-ins' shape, and a fixture stands in its place only where
what it holds is the input a shipped function is measured over.
"""

from pathlib import Path

FIXTURES = Path(__file__).parent


def fixture_file(name: str) -> Path:
    """The fixture written under `name` in this directory."""
    return FIXTURES / name
