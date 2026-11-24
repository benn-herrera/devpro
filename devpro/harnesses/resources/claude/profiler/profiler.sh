#!/usr/bin/env bash
# !INSTALLED! from devpro/harnesses/resources/claude/profiler/profiler.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
# Bash, invoked as `/bin/bash`: the hook entries name the interpreter absolutely, so the
# script runs under the shell its shebang names on every platform the hooks ship to,
# with a `PATH` at hook-run time that no longer matters. The repository's other shell
# scripts are bash as well (the claude harness's hook commands name their interpreter).
# Runs the devpro wrapper beside it with the `profiler` verb, the launcher's own arguments
# passed through. The first candidate standing is the one that runs: there is no probe and
# no PATH search — a foreign devpro is never run, and every failure is named by the
# wrapper's own refusal. A capture whose wrapper fails or stands not at all drains its
# stdin and exits 0 — a missing or failing profiler must never block a tool call — and
# every other subcommand reports and exits nonzero. The capture child's stdout is
# discarded whatever it wrote: a hook's stdout is the host's protocol alone, so a line
# the wrapper prints there is never read as a hook result. The script sets no `set -euo pipefail`:
# `capture` must exit 0 on every path, and `-e` or `-u` would turn an unforeseen failure
# into a nonzero exit that blocks the tool call.

# The wrapper is resolved from this launcher's own location. The installed launcher is
# <install-dir>/profiler/profiler.sh and the committed hook's is
# .claude/harness-profiler/profiler.sh; the wrapper is one file both reach, the two paths
# below apart, so the one that stands is the wrapper and the other does not exist.
here=$(CDPATH='' cd -- "$(dirname -- "${0}")" && pwd)
wrapper=
for candidate in "${here}/../tools/devpro.sh" "${here}/../skills/devpro/tools/devpro.sh"; do
  if [[ -e "${candidate}" ]]; then
    wrapper="${candidate}"
    break
  fi
done

if [[ "${1}" == "capture" ]]; then
  if [[ -z "${wrapper}" ]]; then
    cat >/dev/null 2>&1
    exit 0
  fi
  "${wrapper}" profiler "${@}" >/dev/null
  status=$?
  if [[ ${status} -ne 0 ]]; then
    cat >/dev/null 2>&1
  fi
  exit 0
fi

if [[ -z "${wrapper}" ]]; then
  echo "profiler.sh: no devpro wrapper beside the launcher (neither ${here}/../tools/devpro.sh nor ${here}/../skills/devpro/tools/devpro.sh stands). Install devpro." >&2
  exit 1
fi
"${wrapper}" profiler "${@}"
