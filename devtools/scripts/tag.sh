#!/usr/bin/env bash
# `tag`'s body: a tag names a commit whose own files carry the number it is tagged with, so this
# refuses while `devpro/` is uncommitted — the same reasoning
# `install.uncommitted_sources` applies to publishing the agents file, and the lines it prints
# are that check's own. The number is read from the `--version` flag rather than restated here,
# `__version__` in `devpro/__init__.py` holding the one copy. The tag is signed and annotated
# (`git tag -s`), so it needs a gpg secret key and a TTY, and nothing is pushed: the maintainer pushes.
set -euo pipefail
: "${PROJECT_ROOT:?PROJECT_ROOT is empty or unset — run this script through its justfile recipe}"
: "${GEN:?GEN is empty or unset — run this script through its justfile recipe}"

# The `devpro` pathspec below is relative to the working directory, so the
# repository root is named rather than assumed.
cd "${PROJECT_ROOT}"
dirty="$(git status --porcelain -- devpro)"
if [[ -n "${dirty}" ]]; then
    printf '%s\n' "error: devpro/ has uncommitted changes — a tag must name a commit whose files carry the version it is tagged with:" >&2
    printf '%s\n' "${dirty}" >&2
    exit 1
fi
version="$(PYTHONPATH="${PROJECT_ROOT}" python3 -m "${GEN}" --version)"
# An empty reading would tag the commit `v` instead of failing, and a wrong
# tag is the one thing this recipe can produce that nothing else corrects.
if [[ -z "${version}" ]]; then
    printf '%s\n' "error: 'python3 -m ${GEN} --version' printed nothing — nothing tagged" >&2
    exit 1
fi
tag="v${version}"
if git rev-parse --verify --quiet "refs/tags/${tag}" > /dev/null; then
    printf '%s\n' "error: tag '${tag}' already exists — bump __version__ in devpro/__init__.py before tagging again" >&2
    exit 1
fi
# README.md's pipx install line carries a hand-kept `@v<version>` tag, edited beside each
# __version__ bump. A tag cut while that line names a different version ships a README pointing at a
# release tag that does not exist, and nothing else corrects it — the same wrong-tag class the
# checks above refuse. The `|| true` lets the read come back empty (no tag on the line yet); the
# mismatch against ${tag} below is what refuses that, naming the line.
readme_tag="$(grep -E 'pipx install' README.md | grep -oE 'devpro@v[0-9]+\.[0-9]+\.[0-9]+' | head -n 1 | sed 's/.*@//' || true)"
if [[ "${readme_tag}" != "${tag}" ]]; then
    printf '%s\n' "error: README.md's pipx install line pins @${readme_tag:-<none>}, but __version__ is ${tag#v} — hand-edit the README's @v<version> tag beside the __version__ bump before tagging" >&2
    exit 1
fi
GPG_TTY=$(tty) git tag -s "${tag}" -m"release ${tag}"
git tag -v "${tag}"
