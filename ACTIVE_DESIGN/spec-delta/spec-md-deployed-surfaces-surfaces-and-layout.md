### [SPEC.md, Deployed Surfaces, Surfaces and layout](../../PROJECT_DOCS/SPEC/deployed-surfaces/surfaces-and-layout.md)

The render usage line takes the components flag, and the install usage line states the one set.

```
produced to order into the output root an invocation names: `devpro render --out <dir>
[--plugin=NAME]` renders the plugin's definitions (Plugins) and the harness-rendered files it writes
```
becomes
```
produced to order into the output root an invocation names: `devpro render --out <dir>
[--components=CSV]` renders the plugin's definitions with the named components on (Plugins) and the
harness-rendered files it writes
```

````
It arrives by **install**,
the one distribution channel. Install delivers one plugin, `devpro` or `kbase`, and no other. Its usage:

```sh
devpro install TARGET [--plugin=NAME] [--harness=NAME] [--subdir=DIR] [--family=NAME] [--config-file=FILE] [--dry-run] [--verbose]
```

Plugins states `--plugin`'s default.
````
becomes
````
It arrives by **install**,
the one distribution channel. Install delivers the devpro plugin's set, with the components the
invocation names. Its usage:

```sh
devpro install TARGET [--components=CSV] [--harness=NAME] [--subdir=DIR] [--family=NAME] [--config-file=FILE] [--dry-run] [--verbose]
```

Plugins states the `--components` default.
````

