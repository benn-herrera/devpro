#!/usr/bin/env bash
# !INSTALLED! from devpro/harnesses/resources/claude/profiler/hp.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
# Bash, invoked as `/bin/bash`: the hook entries name the interpreter absolutely, so the
# script runs under the shell its shebang names on every platform the hooks ship to,
# with a `PATH` at hook-run time that no longer matters. The repository's other shell
# scripts are bash as well (the claude harness's hook commands name their interpreter).
# Finds a devpro and runs its profiler verb. Its first candidate is the
# installation's own wrapper, beside this launcher; only where no wrapper stands
# does it fall back to the `devpro` command on PATH, extended with where Homebrew
# and `~/.local/bin` put devpro (a hook may run with a bare PATH). Each candidate
# is probed once — `--version` — and one that fails is reported and treated as
# absent: a broken install is never silently executed, and a wrapper that exists
# but does not run is the fault to name, not a reason to run a foreign devpro.
# Without a devpro, `capture` drains stdin and exits 0 without output — a missing
# profiler must never block a tool call — and every other subcommand reports and
# exits 1. The script sets no `set -euo pipefail`: `capture` must exit 0 on every path, and
# `-e` or `-u` would turn an unforeseen failure into a nonzero exit that blocks the tool call.

# A devpro is usable when it runs: the probe is cheap and silent.
devpro=
unusable=

function usable() {
  "${1}" --version >/dev/null 2>&1
}

function find_devpro() {
  # The installation's wrapper, resolved from this launcher's own location, is the first candidate.
  # The installed launcher is <install-dir>/profiler/hp.sh and the committed hook's is
  # .claude/harness-profiler/hp.sh; the wrapper is one file both reach, the two paths below apart, so
  # the one that stands is the wrapper and the other does not exist. A wrapper that runs is the
  # devpro; a wrapper that exists and does not run is the fault to report, not a reason to run a
  # foreign devpro from PATH. Only when no wrapper stands does the search fall to PATH, below.
  local here candidate
  here=$(CDPATH='' cd -- "$(dirname -- "${0}")" && pwd)
  for candidate in "${here}/../tools/devpro.sh" "${here}/../skills/devpro/tools/devpro.sh"; do
    [[ -e "${candidate}" ]] || continue
    if usable "${candidate}"; then
      devpro="${candidate}"
      return
    fi
    unusable="${candidate}"
    return
  done
  devpro=$(PATH="${PATH}:/opt/homebrew/bin:/usr/local/bin:${HOME}/.local/bin" command -v devpro 2>/dev/null) || devpro=
  if [[ -n "${devpro}" ]] && ! usable "${devpro}"; then
    unusable="${devpro}"
    devpro=
  fi
}

function report_missing() {
  if [[ -n "${unusable}" ]]; then
    echo "hp: devpro is unusable: \"${unusable}\" does not run." >&2
  else
    echo "hp: devpro not found in the installation, on PATH, in Homebrew or ~/.local/bin. Install devpro." >&2
  fi
}

find_devpro
if [[ -z "${devpro}" ]]; then
  case $1 in
    capture) cat >/dev/null 2>&1; exit 0 ;;
    *) report_missing; exit 1 ;;
  esac
fi
exec "${devpro}" profiler "${@}"
