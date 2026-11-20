"""The selection of definitions an install delivers, and the one name every install takes.

The required set is every discovered definition no component names, so a new definition joins it by
existing. Each optional component adds its member list when it is turned on, and every install reads
the result through `Components.ships`: a member list is the one place its component's members are
decided, and no harness, install step, render or test holds one.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from devpro.definitions import discover
from devpro.errors import InputError

NAME = "devpro"
"""The one name every install takes: the directory the set lands in and every `{plugin}` template's fill."""

COMPONENTS: Mapping[str, frozenset[str]] = {"kbase": frozenset({"kbase"})}
"""Each optional component, by name, and the definitions turning it on adds to the required set."""

_OPTIONAL_MEMBERS = frozenset().union(*COMPONENTS.values())


@dataclass(frozen=True)
class Components:
    """The selection a render carries: the optional components turned on."""

    on: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        """Refuse a name that is no optional component, naming the ones there are."""
        unknown = sorted(self.on.difference(COMPONENTS))
        if unknown:
            raise InputError(f"unknown component '{unknown[0]}' — optional components are {', '.join(COMPONENTS)}")

    @property
    def name(self) -> str:
        """The one name every install takes."""
        return NAME

    @property
    def members(self) -> frozenset[str]:
        """The definitions the turned-on components add."""
        return frozenset().union(*(COMPONENTS[component] for component in self.on))

    def ships(self, name: str) -> bool:
        """Whether the definition `name` ships: every definition no component names, and each turned-on
        component's members."""
        return name in self.members or name not in _OPTIONAL_MEMBERS


def selection(spec: str) -> Components:
    """`spec`, the comma-separated optional component names the CLI flag or the settings file names, as
    the selection it names: blanks are skipped, so an empty spec turns nothing on. Every component's
    member list is then checked against discovery, a member discovery does not find refused naming its
    component, because a misspelled member would otherwise drop out of the install unnoticed."""
    components = Components(on=frozenset(part.strip() for part in spec.split(",") if part.strip()))
    discovered = {defn.name for _, entries in discover() for defn in entries}
    for component, members in COMPONENTS.items():
        missing = sorted(members - discovered)
        if missing:
            raise InputError(f"component '{component}' names no discovered definition: {', '.join(missing)}")
    return components
