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

# The floor is enforced on the interpreter handed in, before any venv or wheel work: a below-floor
# interpreter would build its venv to fail the wheel's install, reporting a wheel defect where the
# cause is the interpreter. It is read from pyproject.toml's requires-python, the floor's one home,
# parsed as `_venv` parses it — the first X.Y a `>=`, `~=` or `==` specifier names — and a spelling
# that yields no floor is refused rather than skipped.
floor="$(sed -n 's/^requires-python *= *"\([^"]*\)".*/\1/p' "${PROJECT_ROOT}/pyproject.toml" | sed -En 's/.*(>=|~=|==)([0-9]+\.[0-9]+).*/\2/p' | head -n 1)"
[[ -n "${floor}" ]] || fail "${PROJECT_ROOT}/pyproject.toml names no Python floor: requires-python must name a version as >=X.Y, ~=X.Y or ==X.Y"
# One run reads the version and executable together: an interpreter that cannot run at all fails
# here, naming it, instead of dying inside a substitution with no message.
handed="$("${python}" -c 'import sys; print("%d.%d %s" % (*sys.version_info[:2], sys.executable))')" \
  || fail "cannot run '${python} -c' — check-wheel needs a working Python ${floor} or later interpreter as its argument"
handed_floor="${handed%% *}"
if ! "${python}" -c "import sys; sys.exit(sys.version_info < tuple(map(int, '${floor}'.split('.'))))"; then
  # A bare name is reported as the interpreter it resolved to, which is the file the reader acts on.
  fail "the interpreter handed in, ${handed#* }, is Python ${handed_floor}: check-wheel needs Python ${floor} or later"
fi

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

# Bytecode is never package data: a `__pycache__` in the wheel was written beside a shipped resource
# by an import that ran outside the runner, which exports PYTHONDONTWRITEBYTECODE (the justfile's
# header states the trap). Failing on it, rather than excluding it, names each file and the cure.
stray_bytecode="$(grep -E '(^|/)__pycache__/' <<<"${in_wheel}" || true)"
if [[ -n "${stray_bytecode}" ]]; then
  while IFS= read -r stray; do
    printf 'check-wheel: stray bytecode in the tree: %s\n' "${PROJECT_ROOT}/${stray}" >&2
  done <<<"${stray_bytecode}"
  fail "an import outside the runner wrote bytecode beside a shipped resource; run it through its recipe, \
then remove every __pycache__ the above names"
fi

if [[ "${in_wheel}" != "${in_tree}" ]]; then
  comm -13 <(printf '%s\n' "${in_wheel}") <(printf '%s\n' "${in_tree}") | sed 's/^/missing from the wheel: /' >&2
  comm -23 <(printf '%s\n' "${in_wheel}") <(printf '%s\n' "${in_tree}") | sed 's/^/extra in the wheel: /' >&2
  fail "the wheel's package data differs from the tree"
fi

# The package declares no runtime dependencies, so its METADATA carries no Requires-Dist entry of
# any kind — a dev group stays in pyproject.toml and never reaches a wheel. Read from the wheel's
# own METADATA rather than inferred: `pip install --no-index` below proves only that nothing
# resolved, which a --find-links or an index would change.
requires_dist="$(unzip -p "${wheel}" '*dist-info/METADATA' | grep '^Requires-Dist' || true)"
if [[ -n "${requires_dist}" ]]; then
  while IFS= read -r entry; do
    printf 'check-wheel: the wheel declares a runtime dependency: %s\n' "${entry}" >&2
  done <<<"${requires_dist}"
  fail "the wheel's METADATA carries Requires-Dist; the package declares no runtime dependencies"
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
PYTHONPATH="${PROJECT_ROOT}" "${venv}/${PYBIN}/python${EXE}" -m "${GEN}" install "${scratch}/from-checkout/project" --components=kbase > /dev/null
diff -r from-wheel from-checkout || fail "the wheel's install differs from the checkout's"

mkdir plugins
from_wheel "${venv}/${PYBIN}/devpro${EXE}" install "${scratch}/plugins" --components=kbase --harness=mage > /dev/null
[[ -f "plugins/devpro/CLAUDE.md" ]] || fail "the mage install wrote no plugins/devpro/CLAUDE.md"

printf 'check-wheel: Python %s, %s\n' "$("${venv}/${PYBIN}/python${EXE}" -c 'import platform; print(platform.python_version())')" "${wheel}"
