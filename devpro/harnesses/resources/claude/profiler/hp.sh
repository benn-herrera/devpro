#!/usr/bin/env bash
# !INSTALLED! from devpro/harnesses/resources/claude/profiler/hp.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
# Bash, invoked as `/bin/bash`: the hook entries name the interpreter absolutely, so the
# script runs under the shell its shebang names on every platform the hooks ship to,
# with a `PATH` at hook-run time that no longer matters. The repository's other shell
# scripts are bash as well (the claude harness's hook commands name their interpreter).
# Finds the devpro command and runs its profiler verb. Hooks may run with a bare
# PATH, so it also looks where Homebrew and `~/.local/bin` put it; HP_DEVPRO
# overrides the search. A candidate is used only where it runs. Without a usable
# devpro, `capture` drains stdin and exits 0 without output — a missing profiler
# must never block a tool call — and every other subcommand reports and exits 1.

# A devpro is usable when it runs: the probe is cheap and silent. HP_BAD records
# an HP_DEVPRO that was set but unusable, so the not-found message can name it.
devpro=
devpro_bad=false

function usable() {
  "${1}" --version >/dev/null 2>&1
}

function find_devpro() {
  if [[ -n "${HP_DEVPRO+set}" ]]; then
    if usable "${HP_DEVPRO}"; then devpro=${HP_DEVPRO}; else devpro_bad=true; fi
    return
  fi
  for candidate in "$(command -v devpro 2>/dev/null)" /opt/homebrew/bin/devpro /usr/local/bin/devpro "${HOME}/.local/bin/devpro"; do
    if usable "${candidate}"; then devpro=${candidate}; return; fi
  done
}

function report_missing() {
  if ${devpro_bad}; then
    echo "hp: HP_DEVPRO is set but unusable: \"${HP_DEVPRO}\" does not run." >&2
  else
    echo "hp: devpro not found on PATH, in Homebrew or ~/.local/bin. Install devpro or set HP_DEVPRO." >&2
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
