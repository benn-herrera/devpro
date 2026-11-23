# The Python floor is 3.11

devpro installs and runs on Python 3.11 or later, on hosts and in checkouts alike: the package's
`requires-python`, the installed wrapper's interpreter check and its refusal, and the plugins' host
requirement state 3.11, and are the only statements of the floor. The suite's venv builds from the
first `python3` on `PATH` and is rebuilt where its own interpreter is older than the floor; the
wheel check's throwaway venv defaults to the same interpreter. The code counterparts of these pairs
move with them: the justfile's floor comment dies with the recipes statement, the guide's bare-pip
paragraph with the guide-and-readme entry, the wrapper test's pins with the wrapper statement. The
CONVENTIONS leaf that states the old floor is reported by the delta-application search, not
rewritten here; its own change rewrites it whole. python_coder.py's definition text states the
mechanism for any floor and stays. Support is stated where it holds — nothing documents an
environment below the floor.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## SPEC delta

### [Package and command](PROJECT_DOCS/SPEC/package-and-command.md)

**As it stands:**
```
The devpro package installs on Python 3.9 or later, with no third-party runtime dependency. It has
```

**Becomes:**
```
The devpro package installs on Python 3.11 or later, with no third-party runtime dependency. It has
```

### [Shipped files](PROJECT_DOCS/SPEC/deployed-surfaces/shipped-files.md)

**As it stands:**
```
exists; otherwise under the first `python3` on `PATH`, where it is Python 3.9 or later; otherwise
  it exits non-zero, saying devpro needs Python 3.9 or later. It looks for no other interpreter;
```

**Becomes:**
```
exists; otherwise under the first `python3` on `PATH`, where it is Python 3.11 or later; otherwise
  it exits non-zero, saying devpro needs Python 3.11 or later. It looks for no other interpreter;
```

### [Plugins](PROJECT_DOCS/SPEC/deployed-surfaces/plugins.md)

**As it stands:**
```
devpro, the generator, needs Python 3.9 or later on the host; the kbase component's toolchain is the
```

**Becomes:**
```
devpro, the generator, needs Python 3.11 or later on the host; the kbase component's toolchain is the
```

### [Guide and README](PROJECT_DOCS/SPEC/guide-and-readme.md)

**As it stands:**
```
- running devpro: devpro installed with Homebrew from the `benn-herrera/tap` tap, else, on a
    machine without Homebrew, installed by hand with pipx or into a venv, and why a bare
    `pip install` fails on most hosts;
```

**Becomes:**
```
- running devpro: devpro installed with Homebrew from the `benn-herrera/tap` tap, else, on a
    machine without Homebrew, installed by hand with pipx or into a venv;
```

## ARCHITECTURE delta

### [Packaging](PROJECT_DOCS/ARCHITECTURE/packaging.md)

**As it stands:**
```
`license` string. The package has no runtime dependency (`dependencies = []`); `requires-python` is
  `>=3.9`.
```

**Becomes:**
```
`license` string. The package has no runtime dependency (`dependencies = []`); `requires-python` is
  `>=3.11`.
```

**As it stands:**
```
`.venv`'s
  install line in the justfile's `_venv` recipe therefore pins `setuptools~=82.0.1` and
  `build~=1.4.4`, the last releases that run on Python 3.9. The build makes no git check.
```

**Becomes:**
```
`.venv`'s
  install line in the justfile's `_venv` recipe therefore pins `setuptools~=82.0.1` and
  `build~=1.4.4`. The build makes no git check.
```

**As it stands:**
```
installs the wheel into a throwaway venv under
  `.devpro-temp/` made from `python` (default `/usr/bin/python3`, the Python 3.9 floor on macOS only).
```

**Becomes:**
```
installs the wheel into a throwaway venv under
  `.devpro-temp/` made from `python` (default `python3`).
```

### [Recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md)

**As it stands:**
```
where its python is absent. On macOS it makes it from `/usr/bin/python3` where present, the Xcode
command-line tools' Python 3.9.6, so the suite there runs on the Python 3.9 floor. It installs the
```

**Becomes:**
```
where its python is absent or older than the floor, from the first `python3` on `PATH`. It installs
the
```
