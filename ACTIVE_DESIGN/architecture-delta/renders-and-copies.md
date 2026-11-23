### [Renders and copies](../../PROJECT_DOCS/ARCHITECTURE/install/renders-and-copies.md)

**As it stands:**

```
That walk needs no carve-out for a package
destination: the three `SHIPPED_PACKAGES` rows, the development scripts
package, the dicing snippets package and the kb-tools package, all sit inside the install directory's `skills/` —
`skills/development/scripts/`, `skills/docdicer/dicing-snippets/` and `skills/kbase/kb-tools/`, each in its
skill's own directory — where every file they hold is stamped installed or left unstamped, never
generated, so every file under those trees is still either ours or untouched.
```

**Becomes:**

```
That walk needs no carve-out for a package destination: the development scripts package and the
kb-tools package sit inside the install directory's `skills/` — `skills/development/scripts/` and
`skills/kbase/kb-tools/`, each in its skill's own directory — where every file they hold is stamped
installed or left unstamped, never generated, and the devpro tools package sits at `tools/`,
outside the three surfaces the walk visits, so every file under those trees is still either ours or
untouched.
```

**As it stands:**

```
A copied file takes the
installed banner when its suffix is in `STAMPED_SUFFIXES`
```

**Becomes:**

```
A copied file outside the devpro copy (`tools/devpro/`, copied byte-verbatim) takes the installed
banner when its suffix is in `STAMPED_SUFFIXES`
```

**As it stands:**

```
Mage's install of the devpro plugin ships the
file too, since `development` ships there, and there it refuses.
```

**Becomes:**

```
Mage's install of the devpro plugin ships the
file too, since `development` ships there, and there it refuses.

The devpro tools package takes the same package copy for its two rows — `runner-snippets` to
`tools/runner-snippets/`, and the running package, `PACKAGE_ROOT`, to `tools/devpro/` through
`_shipped` and unstamped — and adds one written file, the wrapper `tools/devpro.sh`: a POSIX-sh
script carrying the installed banner below its shebang, holding the path of the running
interpreter's base executable — the Python a virtual environment was made from, where the install
runs in one — and running the copy as SPEC.md, Shipped files states. A changed interpreter path is
a changed file to the preflight's comparison, as any other. The version change the install report
names is read from the replaced copy's `tools/devpro/__init__.py` and the running package's
`__version__`.
```

