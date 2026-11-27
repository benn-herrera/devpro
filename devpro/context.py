"""`Render`, the one parameter a render receives, the selection and the devpro settings file that
build it, and the settings file's reader, its validation and the map's parse. Composes no text."""

import functools
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path
from typing import cast

from devpro.components import Components, selection
from devpro.errors import InputError
from devpro.family import Family
from devpro.harness import Harness
from devpro.loading import load
from devpro.vocabulary import CATEGORIES, Anchor, Category

CategoryMap = Mapping[Category, str]
INHERIT_MODEL = "inherit"
DEFAULT_HARNESS = "claude"
DEFAULT_FAMILY = "claude"
SETTINGS_FILE = Path(".config/devpro/devpro.toml")
"""The devpro settings file, below the home directory, where `--config-file` names none."""
MODEL_MAP_TABLE = "model-map"
"""A harness's map is its dotted subtable: `[<harness>.model-map]`."""
INSTALL_KEY = "install"
COMPONENTS_KEY = "components"
"""The two keys a harness's `[<harness>]` table carries."""


def parse_category_map(spec: str, *, supplier: str, separator: str = ",") -> dict[Category, str]:
    """`spec`, the text form of a category map, as a total map in CATEGORIES order: `separator`-separated
    `<glob>=<model>` entries, each glob matched against the six category names and its model assigned to
    every category it matches, later entries silently overwriting earlier ones. `supplier` leads every
    refusal: the provenance of the spec. The settings file reads its entries joined by a newline, a
    separator no glob or model holds.

    There is no per-category fallback to the family or to anything else. An entry matching no category is
    refused, and a spec leaving a category unnamed at its end is refused. Values are not validated here:
    the harness's shape check runs on the rendered text (`build_render`).
    """
    named: dict[str, str] = {}
    for raw in spec.split(separator):
        entry = raw.strip()
        glob, sep, value = entry.partition("=")
        glob, value = glob.strip(), value.strip()
        if not sep or not glob or not value or "=" in value:
            raise InputError(f"{supplier}: '{entry}' is not a <glob>=<model> entry")
        if any(part.split() != [part] for part in (glob, value)):
            raise InputError(f"{supplier}: '{entry}' contains whitespace inside a glob or a model")
        matched = [category for category in CATEGORIES if fnmatchcase(category, glob)]
        if not matched:
            raise InputError(f"{supplier}: '{entry}' names no category — categories are {', '.join(CATEGORIES)}")
        named.update((category, value) for category in matched)
    missing = [category for category in CATEGORIES if category not in named]
    if missing:
        raise InputError(
            f"{supplier}: names no value for {', '.join(missing)} — a map names every category "
            f"({','.join(f'{category}=<value>' for category in CATEGORIES)})"
        )
    return {category: named[category] for category in CATEGORIES}


def map_spec(mapping: CategoryMap) -> str:
    """`stem-architect=…,stem-expert=…,stem-mechanical=…,comm-architect=…,comm-expert=…,comm-mechanical=…`,
    always CATEGORIES order."""
    return ",".join(f"{category}={mapping[category]}" for category in CATEGORIES)


@dataclass(frozen=True)
class Render:
    """The one parameter a render receives: harness, selection, family, the invocation's category map,
    and the category of the definition being rendered. `harness` is the harness as given;
    `bound_harness` is it bound to the selection's one name, for every value a `{plugin}` template
    fills."""

    harness: Harness
    plugin: Components
    family: Family
    category_map: CategoryMap  # effective category -> member; total
    category: Category | None = None  # render_definition binds it
    scope: str = ""  # the agents file's scope name; render_agents_file binds it

    def __post_init__(self) -> None:
        """Refuse a non-total map, a category outside the vocabulary, or a family member override no
        category reaches (family categories ∪ category_map)."""
        if set(self.category_map) != set(CATEGORIES):
            raise InputError(f"a category map must name exactly {', '.join(CATEGORIES)}")
        if self.category is not None and self.category not in CATEGORIES:
            raise InputError(f"category '{self.category}' is not one of {', '.join(CATEGORIES)}")
        reachable = set(self.family.categories.values()) | set(self.category_map.values())
        declared = {member for overlay in self.family.overlays.values() for member in overlay.members}
        unreachable = sorted(declared - reachable)
        if unreachable:
            raise InputError(
                f"family '{self.family.name}' overrides member(s) no category reaches: {', '.join(unreachable)} — "
                f"reachable members are {', '.join(sorted(reachable))}"
            )

    @functools.cached_property
    def bound_harness(self) -> Harness:
        """The harness bound to this render's one name (`Harness.bound`)."""
        return self.harness.bound(self.plugin.name)

    def model(self, category: Category) -> str:
        """The category's rendered model text: "inherit" and the harness's inherit synonyms render
        harness.inherit_text."""
        text = self.category_map[category]
        if text == INHERIT_MODEL or text in self.harness.inherit_synonyms:
            return self.harness.inherit_text
        return text

    def overlay(self, anchor: Anchor) -> str:
        """The anchor's text: category_map[category]'s member override, else family-wide text, else ""
        (category None: family-wide only)."""
        overlay = self.family.overlays.get(anchor)
        if overlay is None:
            return ""
        if self.category is not None and self.category_map[self.category] in overlay.members:
            return overlay.members[self.category_map[self.category]]
        return overlay.text or ""

    @property
    def step_down_model(self) -> str:
        """The step-down model text: for a definition that declares a category, its own discipline's
        mechanical member's rendered text; for one that declares none, both disciplines' as
        `stem-mechanical=<text>, comm-mechanical=<text>`. A side whose member renders as the harness's
        inherit text is omitted, and the value is empty where every side is."""
        if self.category is not None:
            # A discipline's mechanical member: the prefix of this category's own, one of the six.
            text = self.model(cast(Category, f"{self.category.rsplit('-', 1)[0]}-mechanical"))
            return "" if text == self.harness.inherit_text else text
        sides = []
        for name in ("stem-mechanical", "comm-mechanical"):
            text = self.model(name)
            if text != self.harness.inherit_text:
                sides.append(f"{name}={text}")
        return ", ".join(sides)

    @property
    def stock(self) -> tuple[Category, ...]:
        """Categories, in CATEGORIES order, whose category_map member has no member override anywhere in
        the family."""
        tuned = {member for overlay in self.family.overlays.values() for member in overlay.members}
        return tuple(category for category in CATEGORIES if self.category_map[category] not in tuned)


def harnesses() -> dict[str, Harness]:
    """Every harness this installation knows, by name, in name order."""
    return cast(dict[str, Harness], load("devpro.harnesses", "HARNESS"))


def harness_named(name: str) -> Harness:
    """The harness `name` loads as; an unknown name is refused, listing the names there are."""
    known = harnesses()
    if name not in known:
        raise InputError(f"unknown harness '{name}' — harnesses are {', '.join(known)}")
    return known[name]


def families() -> dict[str, Family]:
    """Every model family this installation knows, by name, in name order."""
    return cast(dict[str, Family], load("devpro.families", "FAMILY"))


def _bare_category_spec_expanded(harness: Harness, spec: str) -> str:
    """`spec`, or `*=<spec>` where the harness reads a bare value as the whole map — a non-empty value
    holding neither `=` nor `,`, so `default` but not `default,stem-*=omlx/X`."""
    if not harness.bare_category_spec_is_all or "=" in spec or "," in spec or not spec.strip():
        return spec
    return f"*={spec}"


@dataclass(frozen=True)
class MapSupply:
    """A category map the devpro settings file supplied, and the provenance every refusal names it by."""

    category_map: CategoryMap
    supplier: str


@dataclass(frozen=True)
class HarnessSettings:
    """One harness the devpro settings file names: its `install` and `components` values as written, each
    None where the file sets none, and its map, where it has a model-map table."""

    install: str | None
    supply: MapSupply | None
    components: str | None


def read_settings(config_file: str | None) -> tuple[dict[str, HarnessSettings] | None, Path | None]:
    """`(settings, path)`: the harnesses the devpro settings file names, in name order, each with its
    `install` and `components` values as written and its map parsed. `settings` is an empty mapping where
    the file is there and names no harness, and None where no file is there to read at all; `path` is the
    file's path as this read took it, or None beside a None `settings`. The file is the one `config_file`
    names, taken as given, or the default under the home directory where no file is named: a missing
    default file is no config, an explicitly named file that does not exist is refused, naming the path.

    The file's shape is validated here, so both render and install refuse on it: a key at its top level
    that is no harness's name is refused, naming the key and the harnesses, and so is a subtable of a
    harness's table that is no model-map table, and a key in a settings table that is no setting of it,
    naming the model-map table it belongs in, and either setting holding a value that is no string. A
    quoted dotted top-level key is one such key: `["claude.model-map"]` is a table named `claude.model-map`,
    not the map `[claude]` nests, and is refused. A map table's entries join, in file order, into the
    category spec `parse_category_map` parses, its refusals leading with the table they came from. The
    values are read as written and judged no further: `devpro.install` judges `install` where it consumes
    it, and `build_render` the component list.
    """
    path = _settings_file(config_file)
    if path is None:
        return None, None
    known = harnesses()
    document = _settings_parser(path)
    unknown = [key for key in document if key not in known]
    for key, table in document.items():
        if not isinstance(table, dict):
            continue
        unknown += [
            f"{key}.{inner}" for inner, nested in table.items() if isinstance(nested, dict) and inner != MODEL_MAP_TABLE
        ]
    if unknown:
        raise InputError(
            f"devpro settings file '{path}', table '[{unknown[0]}]': no harness names it — a table is "
            f"'[<harness>]' or '[<harness>.{MODEL_MAP_TABLE}]' for {', '.join(known)}, and no key outside one"
        )
    settings: dict[str, HarnessSettings] = {}
    for name in known:
        table = document.get(name)
        if not isinstance(table, dict):
            continue
        supply = None
        if (map_table := table.get(MODEL_MAP_TABLE)) is not None:
            supplier = f"--config-file {path}, table '[{name}.{MODEL_MAP_TABLE}]'"
            entries = _settings_entries(map_table, path=path, table=f"{name}.{MODEL_MAP_TABLE}")
            supply = MapSupply(
                category_map=parse_category_map(entries, supplier=supplier, separator="\n"), supplier=supplier
            )
        install, components = _settings_values(table, path=path, name=name)
        settings[name] = HarnessSettings(install=install, supply=supply, components=components)
    return settings, path


def _settings_file(config_file: str | None) -> Path | None:
    """The settings file to read: `config_file` as given, refused where no file is there, or the default
    under the home directory, None where it is absent."""
    if config_file is not None:
        named = Path(config_file)
        if not named.is_file():
            raise InputError(
                f"--config-file '{config_file}' names no file — name a settings file that exists, or omit the "
                f"flag for ~/.config/devpro/devpro.toml"
            )
        return named
    default = Path.home() / SETTINGS_FILE
    return default if default.is_file() else None


def _settings_parser(path: Path) -> dict[str, object]:
    """`path` parsed as TOML. A file that does not parse — a repeated glob key among the parse errors,
    `tomllib` names its position — is refused, naming the file and the line."""
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except UnicodeError as exc:
        raise InputError(f"devpro settings file '{path}' is not UTF-8 text: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise InputError(f"devpro settings file '{path}' does not parse: {exc}") from exc


def _settings_values(table: Mapping[str, object], *, path: Path, name: str) -> tuple[str | None, str | None]:
    """`[<name>]`'s `install` and `components` values as written, each None where the key is absent; a key
    that is no setting of the harness is refused, naming the keys a harness's table takes and the
    model-map table the other keys belong in, and so is either setting holding a value that is no
    string, naming the key and the value's type."""
    legal = (INSTALL_KEY, COMPONENTS_KEY, MODEL_MAP_TABLE)
    for key in table:
        if key not in legal:
            raise InputError(
                f"devpro settings file '{path}', table '[{name}]': '{key}' is no setting of it — a "
                f"harness's settings are {', '.join(legal)}, and map entries belong in "
                f"'[{name}.{MODEL_MAP_TABLE}]'"
            )
    for key in (INSTALL_KEY, COMPONENTS_KEY):
        value = table.get(key)
        if value is not None and not isinstance(value, str):
            raise InputError(
                f"devpro settings file '{path}', table '[{name}]': '{key}' names a value that is no string — "
                f"{key} is a string, and this one is of type {type(value).__name__}"
            )
    install, components = table.get(INSTALL_KEY), table.get(COMPONENTS_KEY)
    return (
        install if isinstance(install, str) else None,
        components if isinstance(components, str) else None,
    )


def _settings_entries(entries: object, *, path: Path, table: str) -> str:
    """A model-map table's entries as `parse_category_map`'s spec, in file order. A value that is no
    string — a number, a nested table — is refused, naming where it sits."""
    if not isinstance(entries, dict):
        raise InputError(f"devpro settings file '{path}', table '[{table}]': it is no table of entries")
    spec = []
    for glob, model in entries.items():
        if not isinstance(model, str):
            raise InputError(
                f"devpro settings file '{path}', table '[{table}]': '{glob}' names a value that is no model — "
                f"a model is a string"
            )
        spec.append(f"{glob}={model}")
    return "\n".join(spec)


def build_render(*, harness: str, components: str, family: str, supply: MapSupply | None = None) -> Render:
    """The CLI's Render. Unknown harness/family names are refused, listing the names there are (a
    path-shaped --family included), and so is a component list naming no optional component, or a
    component whose member list names a definition discovery does not find (`components.selection`). The
    map comes from `supply`, the devpro settings file's for this harness, where the read gave one;
    otherwise from the harness's `default_category_spec` — a bare value read as `*=<value>` where the
    harness reads it so — and otherwise from the family. Then every category's model text is checked
    against harness.model_pattern, refusing with category, value, supplier and model_shape."""
    loaded_harness = harness_named(harness)
    loaded_components = selection(components)
    known_families = families()
    if family not in known_families:
        raise InputError(f"--family '{family}' names no family — families are {', '.join(known_families)}")
    loaded = known_families[family]
    if supply is not None:
        category_map, supplier = supply.category_map, supply.supplier
    elif loaded_harness.default_category_spec is not None:
        supplier = f"the harness '{harness}' default category spec"
        defaulted = _bare_category_spec_expanded(loaded_harness, loaded_harness.default_category_spec)
        category_map = parse_category_map(defaulted, supplier=supplier)
    else:
        category_map, supplier = dict(loaded.categories), f"the family '{family}' categories (--family)"
    render = Render(harness=loaded_harness, plugin=loaded_components, family=loaded, category_map=category_map)
    for category, text in category_map.items():
        if render.harness.model_pattern.fullmatch(text) is None:
            raise InputError(
                f"harness '{harness}' does not accept model '{text}' at category {category}, supplied by {supplier} — "
                f"a model for this harness is {render.harness.model_shape}"
            )
    return render
