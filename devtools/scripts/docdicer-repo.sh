#!/usr/bin/env bash
# The hosted docdicer clone `dev-dd` runs from, kept at the tag the shipped launcher pins.
#
# `git clone` happens once. Every later run leaves an existing clone where it is and brings it to
# the pinned tag, so the dev recipes run the same docdicer the installed snippet routes name. The
# pin is the launcher's, read by the recipe and handed over as DOCDICER_PIN; this script carries no
# version of its own.
#
# A clone with local changes is reported and left alone, never reset: the pin follows only a clean
# clone. A pin absent from the clone after fetching tags is reported and the clone left as it is —
# an unpublished pin must not make the dev recipes fail.
#
# Inputs (environment): DOCDICER_PIN, the tag the launcher installs (`v<version>`).
set -euo pipefail

: "${DOCDICER_PIN:?DOCDICER_PIN is not set: the pinned tag the launcher installs}"

script_dir="$(cd "$(dirname "${0}")" && pwd)" || exit 1
cd "${script_dir}"
while [[ ! -d .git ]] && [[ "$(pwd)" != "/" ]]; do
  cd ".."
done
[[ -d .git ]] || { printf '%s: failed finding project root.\n' "$(basename "${0}")" 1>&2; exit 1; }

clone=docdicer
if [[ ! -d "${clone}/.git" ]]; then
    git clone git@github.com:benn-herrera/docdicer "${clone}" || exit 1
fi

# The checkout's harness resources live in this repository. A link to a directory this scratch
# checkout lacks still exists as a link, so the guard reads the link itself.
[[ -e "${clone}/.claude" || -L "${clone}/.claude" ]] || ln -vs ../.claude "${clone}/.claude"
[[ -e "${clone}/.opencode" || -L "${clone}/.opencode" ]] || ln -vs ../.opencode "${clone}/.opencode"

cd "${clone}"
current="$(git describe --tags --abbrev=0 2> /dev/null || true)"
if [[ "${current}" == "${DOCDICER_PIN}" ]]; then
    exit 0
fi

# The two links above are this script's own, not the clone's local work.
if [[ -n "$(git status --porcelain -- . ':(exclude).claude' ':(exclude).opencode')" ]]; then
    printf 'docdicer: %s has local changes — left at %s, not at the pin %s.\n' \
        "$(pwd)" "${current:-no tag}" "${DOCDICER_PIN}" >&2
    exit 0
fi

if ! git fetch --tags --quiet; then
    printf 'docdicer: could not fetch tags from origin — using the tags this clone holds.\n' >&2
fi

if ! git rev-parse -q --verify "refs/tags/${DOCDICER_PIN}" > /dev/null; then
    printf 'docdicer: no tag %s in this clone — left it at %s.\n' "${DOCDICER_PIN}" "${current:-no tag}" >&2
    exit 0
fi

git checkout -q "${DOCDICER_PIN}"
printf 'docdicer: %s checked out at the pin %s (was %s).\n' "$(pwd)" "${DOCDICER_PIN}" "${current:-no tag}"
