### A lint recipe is read-only

Formatting and linting are checked by a `lint` recipe that leaves the source as it found it —
`shellcheck` over the tracked `*.sh` files, `black --check`, `isort --check-only` and `flake8` over
the paths `format-python` takes, and `bunx tsc --noEmit` over the shipped TypeScript resources, which
installs the declarations it reads and emits nothing; `format-python` is the rewriting form, run to
fix what `lint` reports. A reviewer changes nothing, so it runs `lint`: `format-python` run in its
place reports success over a tree it just changed.
