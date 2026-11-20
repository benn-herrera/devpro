### [SPEC.md, Rendering](../../PROJECT_DOCS/SPEC/rendering.md)

The settings section names its two keys, and the namespace and shipped-set statements lose the
two-plugin phrasing.

```
Its sections are named per harness: `[<harness>]` carries the
  harness's settings, its `install` value among them (SPEC.md, Install destination);
```
becomes
```
Its sections are named per harness: `[<harness>]` carries the
  harness's settings, its `install` (SPEC.md, Install destination) and `components` (SPEC.md,
  Deployed Surfaces, Plugins) values among them;
```

```
Apart from the plugin's name and the namespace it gives references, text differs between plugins only
by an optional reference's paragraph being present or absent.
```
becomes
```
Apart from the namespace, text differs between installs only
by an optional reference's paragraph being present or absent.
```

```
References close within the shipped set, the definitions the render's plugin carries.
```
becomes
```
References close within the shipped set, the definitions the render carries — the plugin's set with
its components on.
```

