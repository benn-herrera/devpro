#!/usr/bin/env bash
# !INSTALLED! from devpro/harnesses/resources/claude/profiler/hp.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
# Bash, invoked as `/bin/bash`: the hook entries name the interpreter absolutely, so the
# script runs under the shell its shebang names on every platform the hooks ship to,
# with a `PATH` at hook-run time that no longer matters. The repository's other shell
# scripts are bash as well (the claude harness's hook commands name their interpreter).
# Finds the devpro command and runs its profiler verb. Hooks may run with a bare
# PATH, so the finder extends it with where Homebrew and `~/.local/bin` put devpro
# and runs one `command -v` over the whole thing. The one devpro it resolves is
# probed once — `--version` — and one that fails is reported and treated as absent:
# a broken install is never silently executed. Without a devpro, `capture` drains
# stdin and exits 0 without output — a missing profiler must never block a tool
# call — and every other subcommand reports and exits 1.

# A devpro is usable when it runs: the probe is cheap and silent.
devpro=
unusable=

function usable() {
  "${1}" --version >/dev/null 2>&1
}

function find_devpro() {
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
    echo "hp: devpro not found on PATH, in Homebrew or ~/.local/bin. Install devpro." >&2
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
