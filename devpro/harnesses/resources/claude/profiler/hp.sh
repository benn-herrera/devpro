#!/bin/sh
# !INSTALLED! from devpro/harnesses/resources/claude/profiler/hp.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
# POSIX sh, not bash: the hook entries invoke it as `sh`, and a hook may run
# with a `PATH` where `bash` is not found.
# Finds python3 and runs hp.py beside this script. Hooks may run with a bare
# PATH, so it also looks where Homebrew and the system put an interpreter;
# HP_PYTHON overrides the search. An interpreter is used only where it can run
# hp.py: 3.9 or newer, a file, executable. Without a usable python3, or where
# hp.py is missing beside this launcher, `capture` drains stdin and exits 0
# without output — a missing profiler must never block a tool call — and every
# other subcommand reports and exits 1.

case $0 in */*) here=${0%/*} ;; *) here=. ;; esac

# An interpreter is usable when it can run hp.py: a file, executable, 3.9 or
# newer. The probe is cheap, standard library, and silent. HP_BAD records an
# HP_PYTHON that was set but unusable, so the not-found message can name it.
RUNS_HP_PY='import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'
python=
hp_bad=

usable() {
  [ -f "$1" ] && [ -x "$1" ] && "$1" -c "$RUNS_HP_PY" >/dev/null 2>&1
}

find_python() {
  if [ -n "${HP_PYTHON+set}" ]; then
    if usable "$HP_PYTHON"; then python=$HP_PYTHON; else hp_bad=1; fi
    return
  fi
  for candidate in "$(command -v python3 2>/dev/null)" /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
    if usable "$candidate"; then python=$candidate; return; fi
  done
}

report_missing() {
  if [ -n "$hp_bad" ]; then
    echo "hp: HP_PYTHON is set but unusable: \"$HP_PYTHON\" is not a runnable Python 3.9+ interpreter." >&2
  else
    echo "hp: python3 not found on PATH, in Homebrew or /usr/bin. Install Python 3.9+ or set HP_PYTHON." >&2
  fi
}

find_python
if [ -z "$python" ]; then
  case $1 in
    capture) cat >/dev/null 2>&1; exit 0 ;;
    *) report_missing; exit 1 ;;
  esac
fi
if [ ! -f "$here/hp.py" ]; then
  case $1 in
    capture) cat >/dev/null 2>&1; exit 0 ;;
    *) echo "hp: hp.py not found beside this launcher (expected $here/hp.py); the install is incomplete." >&2; exit 1 ;;
  esac
fi
exec "$python" "$here/hp.py" "$@"
