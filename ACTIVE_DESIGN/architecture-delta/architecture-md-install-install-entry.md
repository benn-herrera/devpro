### [ARCHITECTURE.md, Install, Install entry](../../PROJECT_DOCS/ARCHITECTURE/install/install-entry.md)

The verb takes the components CSV, detection reads component-independent values, and the mage
dependency sentence retires.

```
The verb takes TARGET, its one positional
argument, and `--plugin=NAME`, a choice among the plugins `devpro/plugins/` holds, default
`context.DEFAULT_PLUGIN` (`cli._add_plugin`); a second positional is an argument argparse does not
recognize, refused with exit 2 before anything is written.
```
becomes
```
The verb takes TARGET, its one positional
argument, and `--components=CSV`, the optional components the invocation turns on, default none
(`cli._add_components`); a second positional is an argument argparse does not
recognize, refused with exit 2 before anything is written.
```

```
detects the harness from values
no plugin changes (`_detected_harness`), binds that harness to the plugin, and returns the harness,
```
becomes
```
detects the harness from values
no component changes (`_detected_harness`), binds that harness to the plugin, and returns the harness,
```

```
One read of the file serves the
selection and every harness's render. Only mage's harness directory depends on the plugin, its
`project_harness_dir` being `{plugin}`. `install` uses the project root as spelled,
```
becomes
```
One read of the file serves the
selection and every harness's render. `install` uses the project root as spelled,
```

