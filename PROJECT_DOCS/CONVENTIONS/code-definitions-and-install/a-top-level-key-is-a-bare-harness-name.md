# A top-level key is a bare harness name

The settings file's tables are named per harness: a top-level key is a bare harness name, `[claude]`
naming claude's table, and `[<harness>.model-map]` is that harness's nested subtable — its model
map. A quoted dotted top-level key (`["claude.model-map"]`) is not a way to write that subtable: it
parses, and as a table named for the whole dotted string it reads as the subtable meant, so a reader
meets it and re-litigates whether it should stand.
