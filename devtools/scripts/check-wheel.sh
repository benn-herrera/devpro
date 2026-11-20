#!/usr/bin/env bash
# `check-wheel`'s body. Proves the wheel `build` left in dist/: its package data is the tree's, and,
# installed into a throwaway venv made from $1, it runs as the shipped package rather than as the
# checkout. Every wheel-side command runs with PYTHONPATH unset and GIT_CEILING_DIRECTORIES at the
# scratch directory, so neither the working tree nor the repository around it can answer for it.
# From the scratch directory's creation on, HOME is a fresh, empty home inside it, removed on exit,
# so no install here reads or writes the operator's real one.
set -euo pipefail
: "${PROJECT_ROOT:?PROJECT_ROOT is empty or unset — run this script through its justfile recipe}"
: "${GEN:?GEN is empty or unset — run this script through its justfile recipe}"
: "${PYBIN:?PYBIN is empty or unset — run this script through its justfile recipe}"
: "${EXE?EXE is unset — run this script through its justfile recipe}"
python="${1:?usage: check-wheel.sh PYTHON}"

function fail() {
  printf 'check-wheel: %s\n' "${1}" >&2
  exit 1
}

ver="$(PYTHONPATH="${PROJECT_ROOT}" python3 -m "${GEN}" --version)"
wheel="${PROJECT_ROOT}/dist/${GEN}-${ver}-py3-none-any.whl"
sdist="${PROJECT_ROOT}/dist/${GEN}-${ver}.tar.gz"
for product in "${wheel}" "${sdist}"; do
  [[ -f "${product}" ]] || fail "missing build product ${product}"
done

# A package-data glob sweeps in whatever sits under its tree, so a stray file shows up as extra.
in_wheel="$(unzip -Z1 "${wheel}" | awk -v top="${GEN}/" 'index($0, top) == 1 && !/\.py$/ && !/\/$/' | sort)"
in_tree="$(git -C "${PROJECT_ROOT}" ls-files --cached --others --exclude-standard "${GEN}" \
  | awk '!/\.py$/' | sort)"
if [[ "${in_wheel}" != "${in_tree}" ]]; then
  comm -13 <(printf '%s\n' "${in_wheel}") <(printf '%s\n' "${in_tree}") | sed 's/^/missing from the wheel: /' >&2
  comm -23 <(printf '%s\n' "${in_wheel}") <(printf '%s\n' "${in_tree}") | sed 's/^/extra in the wheel: /' >&2
  fail "the wheel's package data differs from the tree"
fi

scratch="${PROJECT_ROOT}/.devpro-temp/check-wheel"
venv="${scratch}/venv"
command rm -rf "${scratch}"
mkdir -p "${scratch}/home"
trap 'command rm -rf "${scratch}"' EXIT
export HOME="${scratch}/home"
"${python}" -m venv "${venv}"
"${venv}/${PYBIN}/python${EXE}" -m pip install -q --disable-pip-version-check --no-index "${wheel}"

function from_wheel() {
  env -u PYTHONPATH GIT_CEILING_DIRECTORIES="${scratch}" "$@"
}

cd "${scratch}"
imported="$(from_wheel "${venv}/${PYBIN}/python${EXE}" -I -c 'import devpro; print(devpro.__file__)')"
[[ "${imported}" == "${venv}/"* ]] || fail "devpro imported from ${imported}, outside ${venv}"
wheel_ver="$(from_wheel "${venv}/${PYBIN}/devpro${EXE}" --version)"
[[ "${wheel_ver}" == "${ver}" ]] || fail "the wheel reports version ${wheel_ver}, the checkout ${ver}"
script_help="$(from_wheel "${venv}/${PYBIN}/devpro${EXE}" --help)"
module_help="$(from_wheel "${venv}/${PYBIN}/python${EXE}" -I -m devpro --help)"
[[ "${script_help}" == "${module_help}" ]] || fail "devpro --help differs from python -m devpro --help"

# Each project is named `project`: its AGENTS.md is titled with the project directory's name. One
# project on each side, each installed with the kbase component on, so the whole install is compared.
for side in from-wheel from-checkout; do
  mkdir -p "${side}/project/.claude"
  : > "${side}/project/justfile"
done
from_wheel "${venv}/${PYBIN}/devpro${EXE}" install "${scratch}/from-wheel/project" --components=kbase > /dev/null
PYTHONPATH="${PROJECT_ROOT}" python3 -m "${GEN}" install "${scratch}/from-checkout/project" --components=kbase > /dev/null
diff -r from-wheel from-checkout || fail "the wheel's install differs from the checkout's"

mkdir plugins
from_wheel "${venv}/${PYBIN}/devpro${EXE}" install "${scratch}/plugins" --components=kbase --harness=mage > /dev/null
[[ -f "plugins/devpro/CLAUDE.md" ]] || fail "the mage install wrote no plugins/devpro/CLAUDE.md"

printf 'check-wheel: Python %s, %s\n' "$("${venv}/${PYBIN}/python${EXE}" -c 'import platform; print(platform.python_version())')" "${wheel}"
