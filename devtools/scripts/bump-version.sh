#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ROOT:?PROJECT_ROOT is empty or unset — run this script through its justfile recipe}"
cd "${PROJECT_ROOT}"

ver_file="./devpro/__init__.py"
ver=$(awk '/^__version__[ \t]*=/ { gsub(/\"/, ""); print $NF; }' "${ver_file}")
old_ver=${ver}
ver=(${ver//\./ })
M=${ver[0]}
m=${ver[1]}
p=${ver[2]}
case "${1}" in
  M*) M=$((M + 1)); m=0; p=0;;
  m*) m=$((m + 1)); p=0;;
  p*) p=$((p + 1));;
  *) printf 'invalid arg "%s". valid args are M)ajor, m)inor, or p)atch.\n' "{{dot}}" >&2; exit 1;;
esac

function sedi() {
  [[ "$(uname)" == Darwin ]] && { sed -i "" "${@}"; return $?; }
  sed -i "${@}"
}

sedi "$(printf 's:^__version__.*:__version__ = "%s.%s.%s":g' "${M}" "${m}" "${p}")" "${ver_file}"
echo "version bumped: ${old_ver} -> ${M}.${m}.${p}"
