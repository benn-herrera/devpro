### Shell in this repository is bash

A script here opens `#!/usr/bin/env bash`, sets `set -euo pipefail`, and uses two-space indent,
`function name() {` and a brace on every expansion, `${VAR}` and `"${1}"` included. A script that
needs another shell states why in its header.
