#!/bin/sh
# !INSTALLED! from devpro/harnesses/resources/claude/libexec/hp.sh — do not edit here: request changes from the devpro project; local needs belong in your CONVENTIONS.md.
# POSIX sh, not bash: the hook entries invoke it as `sh`, and a hook may run
# with a `PATH` where `bash` is not found.
# Finds node and runs hp.js beside this script. Hooks may run with a bare
# PATH, so it also looks where Volta, nvm and Homebrew put node; HP_NODE
# overrides the search. Without node, `capture` exits 0 silently: a missing
# profiler must never block a tool call. Only shell builtins run before node.
case $0 in */*) here=${0%/*} ;; *) here=. ;; esac

find_node() {
  if [ -n "${HP_NODE+set}" ]; then [ -x "$HP_NODE" ] && echo "$HP_NODE"; return; fi
  if command -v node >/dev/null 2>&1; then command -v node; return; fi
  if [ -x "$HOME/.volta/bin/node" ]; then echo "$HOME/.volta/bin/node"; return; fi
  # nvm keeps one directory per version, and the glob orders them as text, so v9 sorts after
  # v18. Take the highest version, not the last match.
  newest=
  newest_major=-1 newest_minor=0 newest_patch=0
  for candidate in "$HOME"/.nvm/versions/node/*/bin/node; do
    [ -x "$candidate" ] || continue
    version=${candidate#"$HOME"/.nvm/versions/node/}
    version=${version%%/*}
    version=${version#v}
    case $version in
      *.*) major=${version%%.*}; rest=${version#*.} ;;
      *) major=$version; rest= ;;
    esac
    case $rest in
      *.*) minor=${rest%%.*}; patch=${rest#*.} ;;
      *) minor=$rest; patch=0 ;;
    esac
    major=${major%%[!0-9]*}; minor=${minor%%[!0-9]*}; patch=${patch%%[!0-9]*}
    major=${major:-0}; minor=${minor:-0}; patch=${patch:-0}
    if [ "$major" -gt "$newest_major" ] ||
      { [ "$major" -eq "$newest_major" ] && [ "$minor" -gt "$newest_minor" ]; } ||
      { [ "$major" -eq "$newest_major" ] && [ "$minor" -eq "$newest_minor" ] && [ "$patch" -gt "$newest_patch" ]; }; then
      newest=$candidate
      newest_major=$major newest_minor=$minor newest_patch=$patch
    fi
  done
  if [ -n "$newest" ]; then echo "$newest"; return; fi
  for candidate in /opt/homebrew/bin/node /usr/local/bin/node; do
    if [ -x "$candidate" ]; then echo "$candidate"; return; fi
  done
}

node=$(find_node)
if [ -z "$node" ]; then
  case $1 in
    capture) cat >/dev/null 2>&1; exit 0 ;;
    *) echo "hp: node not found on PATH, in ~/.volta, ~/.nvm or Homebrew. Install Node 18+ or set HP_NODE." >&2; exit 1 ;;
  esac
fi
exec "$node" "$here/hp.js" "$@"
