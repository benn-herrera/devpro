### [Plugins](../../PROJECT_DOCS/ARCHITECTURE/install/plugins.md)

**As it stands:**

```
**Owners.** A supporting artifact ships iff the definition that uses it ships. Each package is a row
of `SHIPPED_PACKAGES` (`devpro/install.py`), a `ShippedPackage` of source, destination, owner and `snippets` (a `runner_file.SnippetSet`, or none):
```

**Becomes:**

```
**Owners.** A supporting artifact ships iff the definition that uses it ships; the devpro tools
package is the plugin's own, and its rows name no owner. Each package is a row of `SHIPPED_PACKAGES`
(`devpro/install.py`), a `ShippedPackage` of source, destination, owner (or none) and `snippets` (a
`runner_file.SnippetSet`, or none):
```

**As it stands:**

```
| `dicing-snippets` | `skills/docdicer/dicing-snippets` | `docdicer` |
| `kb-tools` | `skills/kbase/kb-tools` | `kbase` |

`install` takes the rows whose owner the selection's `ships(name)` admits, and none on a user-level
install.
```

**Becomes:**

```
| `kb-tools` | `skills/kbase/kb-tools` | `kbase` |
| `runner-snippets` | `tools/runner-snippets` | none |
| the package itself, `PACKAGE_ROOT` | `tools/devpro` | none |

`install` takes the rows whose owner the selection's `ships(name)` admits and every row with no
owner, and on a user-level install the rows with no owner alone.
```

**As it stands:**

```
set on the
dicing snippets row (`devpro`) and the kb-tools row (`kb`).
```

**Becomes:**

```
set on the runner-snippets row (`devpro`) and the kb-tools row (`kb`).
```

**As it stands:**

```
`.claude/skills/devpro/skills/docdicer/dicing-snippets/runner-snippets/devpro.just` and
```

**Becomes:**

```
`.claude/skills/devpro/tools/runner-snippets/devpro.just` and
```

