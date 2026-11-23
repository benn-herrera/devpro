### [Installed tree](../../PROJECT_DOCS/SPEC/deployed-surfaces/installed-tree.md)

**As it stands:**

```
An installed tree needs no devpro installation: removing the devpro package, or replacing it with
another version, changes nothing any installed file does, and only the next `devpro install` needs
the package.
```

**Becomes:**

```
An installed tree needs no devpro installation: it runs its own copy of devpro, the devpro tools
package (Shipped files), so removing the devpro package, or replacing it with another version,
changes nothing any installed file does, and only the next `devpro install` needs the package. That
install replaces the copy whichever of the two versions is the newer, and its report names the
version it replaces and the version it installs.
```

**As it stands:**

```
A copied package file of a script or
build-file type (`.py`, `.sh`, `.mk`, `.just`)
carries an installed banner at its top,
```

**Becomes:**

```
A copied package file of a script or build-file type (`.py`, `.sh`, `.mk`, `.just`), the devpro
copy's files excepted, carries an installed banner at its top,
```

**As it stands:**

```
Every other copied file — a package's `.gitignore` among them — and every harness
resource is installed byte-verbatim.
```

**Becomes:**

```
Every other copied file — a package's `.gitignore` and every file of the devpro copy among them —
and every harness resource is installed byte-verbatim.
```

**As it stands:**

```
profiler's launcher sits in the install directory's `profiler/` and is named relative to the skill's
directory (`../../profiler/hp.sh`).
```

**Becomes:**

```
profiler's launcher sits in the install directory's `profiler/` and is named relative to the skill's
directory (`../../profiler/hp.sh`), and so is the installation's wrapper, in its `tools/`
(`../../tools/devpro.sh`). A command a definition gives a session to run devpro runs it through
that wrapper, never the `devpro` command from `PATH` — except the commands that install, update or
report the version that installs, which are the installing `devpro` command's (Package and Command).
```

