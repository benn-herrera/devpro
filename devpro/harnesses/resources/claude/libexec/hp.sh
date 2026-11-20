#!/bin/sh
# !INSTALLED! from devpro/harnesses/resources/claude/libexec/hp.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
# POSIX sh, not bash: the hook entries invoke it as `sh`, and a hook may run
# with a `PATH` where `bash` is not found.
# Finds python3 and runs hp.py beside this script. Hooks may run with a bare
# PATH, so it also looks where Homebrew and the system put an interpreter;
# HP_PYTHON overrides the search. Without python3, `capture` exits 0 silently:
# a missing profiler must never block a tool call. Only shell builtins run
# before python3.
case $0 in */*) here=${0%/*} ;; *) here=. ;; esac

find_python() {
  if [ -n "${HP_PYTHON+set}" ]; then [ -x "$HP_PYTHON" ] && echo "$HP_PYTHON"; return; fi
  if command -v python3 >/dev/null 2>&1; then command -v python3; return; fi
  for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
    if [ -x "$candidate" ]; then echo "$candidate"; return; fi
  done
}

python=$(find_python)
if [ -z "$python" ]; then
  case $1 in
    capture) cat >/dev/null 2>&1; exit 0 ;;
    *) echo "hp: python3 not found on PATH, in Homebrew or /usr/bin. Install Python 3.9+ or set HP_PYTHON." >&2; exit 1 ;;
  esac
fi
exec "$python" "$here/hp.py" "$@"
