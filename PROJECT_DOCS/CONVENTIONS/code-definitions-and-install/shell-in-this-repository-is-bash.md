### Shell in this repository is bash

A script here opens `#!/usr/bin/env bash`, sets `set -euo pipefail`, and uses two-space indent,
`function name() {` and a brace on every expansion, `${VAR}` and `"${1}"` included. A script that
needs another shell states why in its header. A script whose exit contract forbids `-e` — a hook
launcher that must exit 0 on every path — states that in its header, naming the failures `-e` or
`-u` would turn into a blocking exit.
