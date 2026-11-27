"""map grammar• settings file• read_settings"""

import re
from pathlib import Path

import pytest

from devpro.context import MapSupply, build_render, parse_category_map, read_settings
from devpro.errors import InputError
from devpro.vocabulary import CATEGORIES
from tests.conftest import settings_file

from .conftest import _SUPPLIER


@pytest.mark.parametrize(
    "spec, expected",
    [
        (
            "stem-architect=a,stem-expert=b,stem-mechanical=c,comm-architect=d,comm-expert=e,comm-mechanical=f",
            {
                "stem-architect": "a",
                "stem-expert": "b",
                "stem-mechanical": "c",
                "comm-architect": "d",
                "comm-expert": "e",
                "comm-mechanical": "f",
            },
        ),
        (
            "comm-mechanical=f,comm-expert=e,comm-architect=d,stem-mechanical=c,stem-expert=b,stem-architect=a",
            {
                "stem-architect": "a",
                "stem-expert": "b",
                "stem-mechanical": "c",
                "comm-architect": "d",
                "comm-expert": "e",
                "comm-mechanical": "f",
            },
        ),
        (
            "*=haiku,stem-expert=opus",
            {
                "stem-architect": "haiku",
                "stem-expert": "opus",
                "stem-mechanical": "haiku",
                "comm-architect": "haiku",
                "comm-expert": "haiku",
                "comm-mechanical": "haiku",
            },
        ),
        (
            "stem-expert=opus,*=haiku",
            dict.fromkeys(CATEGORIES, "haiku"),
        ),
    ],
)
def test_parse_category_map_is_total_in_category_order(spec: str, expected: dict[str, str]) -> None:
    parsed = parse_category_map(spec, supplier=_SUPPLIER)
    assert parsed == expected
    assert list(parsed) == list(CATEGORIES)


@pytest.mark.parametrize(
    "spec, message",
    [
        (
            "stem-expert=opus",
            "names no value for stem-architect, stem-mechanical, comm-architect, comm-expert, comm-mechanical",
        ),
        ("*=x,middle=y", "'middle=y' names no category"),
        ("*-architect=y", "names no value for stem-expert, stem-mechanical, comm-expert, comm-mechanical"),
        ("*=x,stem-expert", "'stem-expert' is not a <glob>=<model> entry"),
        ("*=x,stem-expert=a=b", "'stem-expert=a=b' is not a <glob>=<model> entry"),
        ("*=x,stem-expert=two words", "contains whitespace inside a glob or a model"),
        ("*=x,", "'' is not a <glob>=<model> entry"),
    ],
)
def test_parse_category_map_refusals(spec: str, message: str) -> None:
    with pytest.raises(InputError, match=re.escape(f"{_SUPPLIER}: ")) as caught:
        parse_category_map(spec, supplier=_SUPPLIER)
    assert message in str(caught.value)


def test_the_settings_file_names_its_harnesses_in_name_order_with_their_install_and_map(tmp_path: Path) -> None:
    """A table names its harness, either table; `install` arrives as written or absent; a map
    table's entries join in file order, so a later entry overwrites an earlier one."""
    path = settings_file(
        tmp_path,
        '[opencode]\ninstall = "always"\n\n[claude.model-map]\n"*" = "haiku"\n"stem-expert" = "opus"\n',
    )
    settings, _ = read_settings(str(path))
    assert list(settings) == ["claude", "opencode"]
    assert settings["opencode"].install == "always"
    assert settings["opencode"].supply is None
    assert settings["claude"].install is None
    assert settings["claude"].supply == MapSupply(
        category_map={**dict.fromkeys(CATEGORIES, "haiku"), "stem-expert": "opus"},
        supplier=f"--config-file {path}, table '[claude.model-map]'",
    )


def test_a_settings_file_naming_no_harness_names_nothing_but_is_not_no_file(tmp_path: Path) -> None:
    """A file that exists and names no harness reads as an empty mapping: the file is there, and it
    names nothing. Only the absence of every file reads as None."""
    settings, _ = read_settings(str(settings_file(tmp_path, "")))
    assert settings == {}
    assert settings is not None


def test_a_missing_default_settings_file_is_no_config(_home: Path) -> None:
    settings, path = read_settings(None)
    assert settings is None and path is None


def test_the_default_settings_file_is_read_from_the_home_directory(_home: Path) -> None:
    """The default path is consulted with no flag given, under the home directory the environment names."""
    path = _home / ".config/devpro/devpro.toml"
    path.parent.mkdir(parents=True)
    path.write_text('[claude]\ninstall = "never"\n', encoding="utf-8")
    settings, _ = read_settings(None)
    assert settings["claude"].install == "never"


@pytest.mark.parametrize("config_file", ["~/devpro.toml", "devpro-absent.toml"], ids=["tilde", "relative"])
def test_a_named_settings_file_that_does_not_exist_is_refused_naming_the_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, config_file: str
) -> None:
    """The path is taken as given: no expansion, no search."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(InputError, match=re.escape(f"--config-file '{config_file}' names no file")):
        read_settings(config_file)


@pytest.mark.parametrize(
    "table",
    ["[claude-code]", "[nonesuch.model-map]", '[DEFAULT]\ninstall = "always"'],
    ids=["settings", "map", "default"],
)
def test_a_settings_file_table_no_harness_names_is_refused(tmp_path: Path, table: str) -> None:
    path = settings_file(tmp_path, f"{table}\n")
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert table.removeprefix("[").split(".")[0].split("]")[0] in message
    assert "claude, mage, opencode" in message


def test_a_settings_tables_components_key_is_read_and_its_unknown_keys_name_both_keys(tmp_path: Path) -> None:
    """`components` is a harness's second setting, read beside `install`; before it existed the key was
    refused as unknown. A key that is no setting still names both keys it could be."""
    path = settings_file(tmp_path, '[claude]\ninstall = "always"\ncomponents = "kbase"\n')
    settings, _ = read_settings(str(path))
    assert settings["claude"].components == "kbase"
    path = settings_file(tmp_path, '[claude]\ncomponents = "kbase"\nbogus = 1\n')
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert "'bogus'" in message and "install, components" in message and "'[claude.model-map]'" in message


def test_a_settings_table_key_that_is_no_setting_is_refused_naming_the_map_table(tmp_path: Path) -> None:
    path = settings_file(tmp_path, '[claude]\n"*" = "haiku"\n')
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert "'*'" in message and "'[claude.model-map]'" in message


@pytest.mark.parametrize(
    "table, key, type_name",
    [
        ('[claude]\ncomponents = ["kbase"]\n', "components", "list"),
        ("[claude]\ninstall = true\n", "install", "bool"),
        ("[claude]\ninstall = 5\n", "install", "int"),
    ],
    ids=["components-list", "install-bool", "install-int"],
)
def test_a_settings_value_that_is_no_string_is_refused_naming_the_table_key_and_type(
    tmp_path: Path, table: str, key: str, type_name: str
) -> None:
    """A discarded value was read as absent: a component list installed with no component, an `install`
    flag fell back to the detect default. A value that is no string is refused, naming where it sits."""
    path = settings_file(tmp_path, table)
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert "table '[claude]'" in message and f"'{key}'" in message and f"type {type_name}" in message


def test_a_quoted_dotted_top_level_key_is_refused_naming_the_table(tmp_path: Path) -> None:
    """`["claude.model-map"]` is a top-level table named `claude.model-map`, not the map `[claude]` nests:
    the grammar accepts a bare harness name or a harness's map subtable, so it is refused, naming it."""
    path = settings_file(tmp_path, '["claude.model-map"]\n"*" = "haiku"\n')
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert "'[claude.model-map]'" in message and "claude, mage, opencode" in message


def test_a_quoted_harness_table_is_read_as_the_table_it_names(tmp_path: Path) -> None:
    """`["claude"]` is the one key `claude`: nothing sets the table another way, so its settings read."""
    settings, _ = read_settings(str(settings_file(tmp_path, '["claude"]\ninstall = "always"\n')))
    assert settings is not None and settings["claude"].install == "always"


def test_a_bare_top_level_key_is_refused_as_a_table_no_harness_names(tmp_path: Path) -> None:
    """`foo = "bar"` beside no table is a key the file sets where only a harness's tables belong."""
    path = settings_file(tmp_path, 'install = "always"\n')
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert "'[install]'" in message and "no harness names it" in message


def test_a_map_entry_whose_value_holds_a_comma_is_one_model(tmp_path: Path) -> None:
    """Map entries join on a newline, not the comma the rendered spec joins on: a model holding a comma
    stays one model rather than splitting into two entries, and renders so for every category."""
    path = settings_file(tmp_path, '[opencode.model-map]\n"*" = "omlx/a,b"\n')
    settings, _ = read_settings(str(path))
    assert settings is not None and (supply := settings["opencode"].supply) is not None
    render = build_render(components="", harness="opencode", family="claude", supply=supply)
    assert dict(render.category_map) == dict.fromkeys(CATEGORIES, "omlx/a,b")
    assert [render.model(category) for category in CATEGORIES] == ["omlx/a,b"] * len(CATEGORIES)


@pytest.mark.parametrize(
    "text",
    ["[claude]\nthis is not an entry\n", '[claude.model-map]\n"*" = "haiku"\n"*" = "opus"\n'],
    ids=["unparseable", "duplicate-key"],
)
def test_a_settings_file_that_does_not_parse_is_refused_naming_the_file_and_the_line(tmp_path: Path, text: str) -> None:
    path = settings_file(tmp_path, text)
    with pytest.raises(InputError) as caught:
        read_settings(str(path))
    message = str(caught.value)
    assert str(path) in message and "line" in message
