# agents task recipes.

# No recipe run writes bytecode into the source tree: an import of a resource the wheel grafts
# wholesale would drop a `__pycache__` beside it, and the next `check-wheel` counts that cache
# among the tree's files — bytecode for an interpreter the consumer never chose. The env var stops
# the cache at the source; nothing in the tree needs it.
export PYTHONDONTWRITEBYTECODE := "1"

# Recipe bodies are bash, not just's default `sh`. Stating it makes the
# contract explicit rather than inherited from whatever /bin/sh happens to be
# on the host. `-u` (just's own default, kept) makes an unset variable a
# failure instead of an empty string. `-o pipefail` makes a pipeline fail
# when any stage does, not just its last.
set shell := ["bash", "-cuo", "pipefail"]
# Without this, a variadic parameter reaches a recipe body only through
# `{{args}}` textual interpolation, which just renders as a bare
# space-joined string — a multi-word value like `-k "a and b"` arrives as
# four separate shell words, indistinguishable from four short ones. With
# it, recipe parameter values are also passed as the shell's own positional
# parameters ($1, $2, ...), so `"$@"` (or a slice of it) carries each
# argument through with its original word boundaries intact.
set positional-arguments := true

PROJECT_ROOT := justfile_directory()

GEN := "devpro"

default:
    @just --list

# venv layout differs by OS: POSIX puts executables in .venv/bin, Windows in
# .venv/Scripts with .exe suffixes. Resolved here via just's os() builtin.

# PROJECT_ROOT defined by consumer before importing.
VENV := PROJECT_ROOT / ".venv"
PYBIN := if os() == "windows" { "Scripts" } else { "bin" }
EXE := if os() == "windows" { ".exe" } else { "" }
VENV_PYTHON := "\"" + VENV / PYBIN / "python" + EXE + "\""
TOOLS_RECORD := VENV / "tools.txt"

# Lazy: the venv is created when its python is absent. It installs the `dev` dependency group
# `pyproject.toml` declares, and records the group's own text in .venv/tools.txt after it
# installs: when the record does not hold that text, the group is installed into the existing venv
# and recorded again, and when it does, this runs no pip. A half-built venv is repaired by deleting
# .venv and re-running. `pip` is not in the group: it installs, it does not produce output a change
# depends on.
#
# Every read of pyproject.toml refuses an empty or unexpected result, naming the read that missed,
# before anything acts on it: a silent empty group would install nothing, and a silent empty floor
# would be read as "too old" and rebuild the venv from whatever `python3` is first on PATH.
_venv:
    #!/usr/bin/env bash
    set -euo pipefail
    # The project's scratch directory, so a recipe that needs it finds it.
    mkdir -p "{{PROJECT_ROOT}}/.devpro-temp"
    # The floor's one home, read as the first X.Y a `>=`, `~=` or `==` specifier names: `>=3.11`,
    # `>=3.11,<4`, `>=3.11.0` and `==3.11.*` all yield 3.11, and a spelling this misses is refused
    # rather than acted on. Parsed with a regex, not tomllib: the python that runs this recipe is
    # not yet known to be new enough to read it.
    floor="$(sed -n 's/^requires-python *= *"\([^"]*\)".*/\1/p' "{{PROJECT_ROOT}}/pyproject.toml" | sed -En 's/.*(>=|~=|==)([0-9]+\.[0-9]+).*/\2/p' | head -n 1)"
    if [[ -z "${floor}" ]]; then
        printf '%s\n' "error: _venv found no floor in {{PROJECT_ROOT}}/pyproject.toml: requires-python must name a version as >=X.Y, ~=X.Y or ==X.Y" >&2
        exit 1
    fi
    # Runs `${1}` against the floor above; a venv that exists, or one just built, must pass it. A
    # below-floor venv is deleted and rebuilt once from `python3`, and a rebuild that lands below
    # the floor again (or an interpreter that fails the test) is refused rather than kept.
    below_floor() {
        ! "$1" -c "import sys; sys.exit(sys.version_info < tuple(map(int, '${floor}'.split('.'))))"
    }
    if [[ -x {{VENV_PYTHON}} ]] && below_floor {{VENV_PYTHON}}; then
        printf '%s\n' "note: _venv rebuilds {{VENV}}: its interpreter is below the ${floor} floor" >&2
        command rm -rf "{{VENV}}"
    fi
    if [[ ! -x {{VENV_PYTHON}} ]]; then
        python3 -m venv --upgrade-deps "{{VENV}}"
    fi
    if below_floor {{VENV_PYTHON}}; then
        printf '%s\n' "error: _venv rebuilt {{VENV}} from $(python3 -c 'import sys; print(sys.executable)') but it is below the ${floor} floor: put a Python ${floor} or later first on PATH" >&2
        exit 1
    fi
    # The record is the group's text, read from pyproject.toml — never a second copy of the list. A
    # non-empty group is also required because an empty one equals the missing-record fallback: the
    # comparison below would read a group the parse lost as "unchanged" and install nothing.
    group="$(sed -n '/^\[dependency-groups\]/,/^\[/p' "{{PROJECT_ROOT}}/pyproject.toml" | sed '1d;$d' | sed -n '/^dev = \[/,/^\]/p' | sed '1d;$d')"
    if [[ -z "${group}" ]]; then
        printf '%s\n' "error: _venv found no dev group in {{PROJECT_ROOT}}/pyproject.toml: [dependency-groups] must hold dev = [...] with one entry per line" >&2
        exit 1
    fi
    if [[ "$(cat "{{TOOLS_RECORD}}" 2>/dev/null || true)" != "${group}" ]]; then
        (cd "{{PROJECT_ROOT}}" && {{VENV_PYTHON}} -m pip install --group dev > /dev/null)
        printf '%s\n' "${group}" > "{{TOOLS_RECORD}}"
    fi


# The root the repository's own render slots sit under: gitignored, never
# committed, and the conventional place to inspect the product or diff it in
# a PR. No slot is ever read back as input to another render (see `render`
# and `render-diff` below), so this names a location under which slots live,
# not a privileged tree.
RENDERED_DIR := "rendered"

# <version> is read from `python3 -m devpro --version`. Refuses while devpro/ has uncommitted
# changes or the tag already exists.
[doc("tag HEAD v<version>; never pushes")]
tag:
    @PROJECT_ROOT="{{PROJECT_ROOT}}" GEN="{{GEN}}" ./devtools/scripts/tag.sh

[doc("bumps devpro __version__ string in __init__.py - M)ajor, m)inor, or p)atch")]
bump-version dot:
  @PROJECT_ROOT="{{PROJECT_ROOT}}" ./devtools/scripts/bump-version.sh "{{dot}}"

# Builds the working tree with the venv's setuptools; makes no git check and fetches nothing.
[doc("build the wheel and sdist into dist/")]
build: _venv
    @{{VENV_PYTHON}} -m build --no-isolation --outdir "{{PROJECT_ROOT}}/dist" "{{PROJECT_ROOT}}"

# Proves the wheel's package data equals the non-.py files under devpro/ that git tracks or would
# track, and that, installed into a throwaway venv made from <python> (default python3),
# it imports from that venv, runs as the devpro console script, and — installed with the kbase
# component on into a project — produces the install the checkout produces, compared byte for byte
# by check-wheel.sh, and writes the mage install's agents file outside a checkout.
[doc("[dev] build, then prove the wheel")]
check-wheel python="python3": build
    @PROJECT_ROOT="{{PROJECT_ROOT}}" GEN="{{GEN}}" PYBIN="{{PYBIN}}" EXE="{{EXE}}" ./devtools/scripts/check-wheel.sh "$@"

# Renders the install product at its one slot project rendered/<slug>/devpro/, with the kbase
# component on (slug defaults to latest; the first non-flag argument, in any position, is the
# slug), plus its agents file for --harness=NAME (default claude) into
# rendered/<slug>/devpro/harness/<NAME>/, or at the slot project's root for a harness-directory
# install (`mage`). Refuses a slug starting with reference, and refuses --components: the slot
# renders with the kbase component on. Every other --* flag, --harness included, forwards verbatim
# to `python3 -m devpro install` via install (--family, --config-file, --harness, --verbose, ...).
[doc("[dev] render devpro to rendered/<slug>/")]
render *args:
    @PROJECT_ROOT="{{PROJECT_ROOT}}" GEN="{{GEN}}" RENDERED_DIR="{{RENDERED_DIR}}" ./devtools/scripts/render.sh "$@"

[private]
_render-slot slug *args:
    @PROJECT_ROOT="{{PROJECT_ROOT}}" GEN="{{GEN}}" RENDERED_DIR="{{RENDERED_DIR}}" ./devtools/scripts/_render-slot.sh "$@"

# Re-takes rendered/reference-claude, reference-opencode, reference-gemma and reference-mage from
# the current generator with their fixed flags — the deliberate counterpart of render's refusal to
# touch them; run only after a content change is accepted.
[doc("[dev] re-take the four reference slots")]
retake-reference:
    @PROJECT_ROOT="{{PROJECT_ROOT}}" GEN="{{GEN}}" RENDERED_DIR="{{RENDERED_DIR}}" ./devtools/scripts/retake-reference.sh

[private]
render-agents-file harness out:
    @PROJECT_ROOT="{{PROJECT_ROOT}}" GEN="{{GEN}}" ./devtools/scripts/render-agents-file.sh "$@"

[private]
_harness-value harness key:
    @PROJECT_ROOT="{{PROJECT_ROOT}}" GEN="{{GEN}}" ./devtools/scripts/_harness-value.sh "$@"

# Splits by heading level, one or more documents into a tree of volumes, then checks every volume
# reassembles its document and every relative link resolves. --section writes the tree as a
# broken-out section instead: its root's head is index.md, and no omnibus stands above it. Every
# argument forwards verbatim.
[doc("dice markdown documents into linked leaves")]
dice *args:
    @PYTHONPATH="{{PROJECT_ROOT}}" python3 -m devpro dice {{args}}

# <tree> is the directory holding its entry-point.md, or its index.md for a broken-out section;
# <out> must be absent or empty. One document is written per volume, named for its volume directory,
# and a tree holding one document is named for the tree's directory. Then checks each document
# against its tree.
[doc("write the documents a diced tree holds into a directory")]
undice tree out:
    @PYTHONPATH="{{PROJECT_ROOT}}" python3 -m devpro undice "{{tree}}" "{{out}}"

# Checks every relative link and #anchor in PROJECT_DOCS and the top-level *.md files, then that
# every PROJECT_DOCS document is listed by its parent and reachable from its entry point; exits 1 on
# a broken link or an orphan.
[doc("check doc links and the PROJECT_DOCS tree")]
check-links:
  @PYTHONPATH="{{PROJECT_ROOT}}" python3 -m devpro check-links PROJECT_DOCS *.md
  @PYTHONPATH="{{PROJECT_ROOT}}" python3 -m devpro check-tree PROJECT_DOCS

# Reports and never gates: a difference between two slots is the expected
# outcome of doing work, so differences exit zero. Only a comparison that could
# not be MADE is fatal — a missing slot, or a file that cannot be read.
#
# Files compare by text, not by bytes: a file whose first line is `---` and whose
# next lines have exactly one of the two frontmatter banner shapes has those lines
# replaced by the one constant line `# !BANNER!`; so does a skill's supporting file,
# which has no frontmatter and carries the third shape, the two HTML comments
# `<!-- !GENERATED! ... -->` and `<!-- !TUNING! ... -->` from its first line. Then,
# outside fenced code, whitespace inside a paragraph collapses to one space, while
# headings, thematic breaks, table rows, list items, fenced blocks and frontmatter stay exact
# (devtools/render_diff.py states the rules). A copied file's `#`-comment `!INSTALLED!` banner
# is replaced the same way. Two files are the same when that text is identical. The
# output keeps `diff -rq`'s two line forms.
[doc("[dev] diff two rendered slots by text")]
render-diff a="reference-claude" b="latest":
    @PYTHONPATH="{{PROJECT_ROOT}}" RENDERED_DIR="{{RENDERED_DIR}}" python3 -m devtools.render_diff "{{a}}" "{{b}}"

# No argument runs the pytest surfaces (devpro and dupe_sweep, the cold_read marker excluded by
# default — the shipped cold-read suite costs about a fifth of the run and no checkpoint work
# touches it), then docs (just check-links with its defaults), then wheel (just check-wheel). A
# surface argument (devpro, dupe_sweep, cold-read, slow, docs, wheel) runs only that one — cold-read runs
# the marker's tests as its default -m, a caller's own -m wins everywhere. Further arguments, never
# given to docs or wheel, forward to pytest: a
# flag (-k, -x, -q, ...) keeps the surface directory, a file or file::test path narrows the run to
# it, and a path outside the surface's directory is refused.
[doc("[dev] run the tests, or one surface's")]
test surface="" *pytest_args: _venv _js-deps
    @PROJECT_ROOT="{{PROJECT_ROOT}}" VENV_PYTHON={{VENV_PYTHON}} JUST="{{just_executable()}}" JUSTFILE="{{justfile()}}" ./devtools/scripts/test.sh "$@"

FLAKE8_IGNORE := "E122,E201,E202,E203,E225,E226,E228,E261,E265,E302,E303,E501,E704,E731,W291,W293,W391,W503"
# Formats the generator (devpro), the tests and devtools, or the given path(s) in place of all of
# them.
[doc("[dev] black, isort and flake8 the python")]
format-python *paths: _venv
    @VENV_PYTHON={{VENV_PYTHON}} FLAKE8_IGNORE="{{FLAKE8_IGNORE}}" ./devtools/scripts/format-python.sh "$@"

# shellcheck over every tracked `*.sh` file, then the same three tools over the same paths as
# `format-python`, checking and writing nothing, then the shipped TypeScript resources against the
# host's published declarations, the version `package.json` pins, `@opencode/plugin`. A reviewer runs
# this one, and `format-python` is what fixes what it reports.
[doc("[dev] check the shell, the python and the shipped TypeScript are clean, writing nothing")]
lint: _venv _lint-shell _lint-typescript
    @{{VENV_PYTHON}} -m black --check --line-length=120 tests devpro devtools
    @{{VENV_PYTHON}} -m isort --profile black --check-only --line-length 120 tests devpro devtools
    @{{VENV_PYTHON}} -m flake8 --ignore="{{FLAKE8_IGNORE}}" devpro devtools tests

# A missing shellcheck fails the lint, never skips the step.
_lint-shell:
    @command -v shellcheck > /dev/null || { printf '%s\n' "error: just lint requires shellcheck on PATH" >&2; exit 1; }
    @git ls-files -z '*.sh' | xargs -0 shellcheck

# A missing bun, or an install that cannot reach the registry, fails the recipe that needs it,
# through `_js-deps`, never as a skip. The declarations the resources import arrive through
# `package.json`'s lockfile, `bun.lock`, which is pinned to the version `package.json` names.
# `tsconfig.json` scopes the program to what ships, the test runners' TypeScript being dev-time only,
# and `devtools/tsconfig.json` is the repository's own TypeScript, a dev tool rather than a shipped
# resource.
_lint-typescript: _js-deps
    @cd "{{PROJECT_ROOT}}" && bunx tsc --noEmit
    @cd "{{PROJECT_ROOT}}" && bunx tsc -p devtools/tsconfig.json --noEmit

# The bun-on-PATH guard the recipes that need the root `package.json`'s dependencies depend on. A
# missing bun fails the recipe that needs it, never skips the step.
_bun-required:
    @command -v bun > /dev/null || { printf '%s\n' "error: this recipe requires bun on PATH" >&2; exit 1; }

# The private install those recipes depend on. A missing bun, or an install that cannot reach the
# registry, fails the recipe that needs it, never skips the step. The install is read-only: it
# updates `node_modules/` and leaves `package.json` and `bun.lock` as it found them, or fails where
# the lockfile does not match them. Its output goes to stderr: stdout carries the caller's result —
# the PNG path `screenshot` prints.
_js-deps: _bun-required
    @cd "{{PROJECT_ROOT}}" && bun install --frozen-lockfile >&2

# Run after changing `package.json`'s dependencies: every other recipe installs frozen and fails on a
# stale `bun.lock`. The unfrozen install is where a rewritten `bun.lock` comes from.
[doc("[dev] install the root package.json's dependencies, rewriting bun.lock to match")]
js-lock: _bun-required
    @cd "{{PROJECT_ROOT}}" && bun install

# Screenshots a page once it has settled, for viewing: the load, the fonts, the `--wait-for`
# selector, then — where no selector was given — a bounded, advisory wait for network idle; a page
# that keeps requesting is shot when the bound expires, not failed. <page> is an http(s) URL, a route
# starting `/` with `--base <url>`, or a file path; the options are `--viewport <W>x<H>`,
# `--wait-for <selector>`, `--color-scheme light|dark`, `--timeout <ms>` and `--out <png>`, and
# `bun devtools/screenshot.ts --help` lists their defaults. It prints the PNG's path. The install
# `_js-deps` runs writes its own output to stderr, so stdout holds the path alone.
[doc("[dev] screenshot a page after it settles, for viewing")]
screenshot *args: _js-deps
    @cd "{{PROJECT_ROOT}}" && bun devtools/screenshot.ts "$@"

# Emits candidates, never verdicts, and exits zero with findings: whether two sites are one idea is
# a judgment, and a gate here would be claiming it.
# Sweeps the owned python trees (the corpus devtools/dupe_sweep/python_corpus.py names) for
# structural twins, repeated constants, and repeated docstring and comment rules; trailing args
# forward to the sweep (--rev, --min-words, --coverage).
[doc("[dev] list one-idea-two-places candidates")]
sweep-python *args:
    @PYTHONPATH="{{PROJECT_ROOT}}" python3 -m devtools.dupe_sweep python "$@"

# test-changed: run only the test surfaces a change touches.
#
# Changed paths are the uncommitted tree (`git status`: staged, unstaged and
# untracked, both sides of a rename) plus, when <base> is given, everything
# committed since it (`git diff base...HEAD`). Each path selects the surface
# its prefix names in TEST_SURFACE_MAP below; a path matching no row
# (ROADMAP_DESIGNS/, scratch) selects nothing. There are no cross-surface
# "just in case" rows. The one exception is the runner itself: `justfile`
# and `devtools/scripts/` — where every recipe body lives, inline or scripted — select
# every surface, because a change to the `test` recipe, or to the script it
# runs, cannot be validated by skipping it. With nothing selected, it says so
# and exits zero without running tests. Git is only read.
#
# One row per line: "<path prefix, or exact file> <surface | ALL>". A prefix
# ending in `/` matches everything under it; one starting `*` is a glob over
# top-level file names. `docs` is the link check: the documents it reads
# (PROJECT_DOCS/, top-level *.md, and images/, which README.md shows). `wheel` is
# check-wheel: the build configuration it builds from, and the package tree
# whose data it checks.
TEST_SURFACE_MAP := "
devpro/ devpro
devpro/ wheel
tests/ devpro
devtools/render_diff.py devpro
devtools/clause_join_sites.py devpro
devtools/ dupe_sweep
PROJECT_DOCS/ docs
*.md docs
images/ docs
pyproject.toml wheel
package.json dupe_sweep
bun.lock dupe_sweep
justfile ALL
devtools/scripts/ ALL
"

# Prints each chosen surface and the paths that chose it, and runs none when nothing maps to a
# surface.
[doc("[dev] run only the tests a change touches")]
test-changed base="":
    @PROJECT_ROOT="{{PROJECT_ROOT}}" TEST_SURFACE_MAP="{{TEST_SURFACE_MAP}}" JUST="{{just_executable()}}" JUSTFILE="{{justfile()}}" ./devtools/scripts/test-changed.sh "$@"

# Lists each definition-body unit that joins a clauses.* interpolation to the module's own text,
# one line per unit naming its first clause's line, then the count; given paths, only those
# definition modules.
[doc("[dev] list clauses.* join sites")]
clause-join-sites *paths:
    @PYTHONPATH="{{PROJECT_ROOT}}" python3 -m devtools.clause_join_sites "$@"

# A design's delta application is verified by `check-design --deltas-applied`; this repository runs
# it as `just dev-check-design-deltas-applied`, over the absorbed verb.

# Emits hits, never verdicts: American spellings are the standard, and this lists the British forms
# left in tracked text for a reader to judge. The justfile and the leaf that hold the pattern and the
# survivor list, and the plan, design and review under way, are skipped because they must quote the
# forms.
[doc("[dev] list British spellings in tracked text")]
spellings:
    @git grep -n -i -E 'behaviour|colour|organis|recognis|analyse\b|analys(ed|ing)|centr(e|ing)|licenc|defence|favour|honour|labour|neighbour|travell|modell|cancell(ed|ing)|fulfil|enrolment|programme|dialogu(e|ing)|catalogu(e|ing)|grey|judgement|acknowledgement|practis|sceptic|manoeuvr(e|ing)|plough|whilst|amongst|learnt|spelt|towards|utilis|optimis|prioritis|normalis|serialis|initialis|finalis|minimis|maximis|customis|standardis|apologis|emphasis[ei]|summaris|categoris|parametris|misspelt|labell(ed|ing)' -- . ':!justfile' ':!PROJECT_DOCS/CONVENTIONS/american-english-spellings.md' ':!ACTIVE_*' || [[ $? -eq 1 ]]

[doc("[dev] install this checkout's devpro here")]
agents:
    @PYTHONPATH="{{PROJECT_ROOT}}" python3 -m "{{GEN}}" install "{{PROJECT_ROOT}}"

# The tap clone's one source: its origin URL, which the clone and the remote
# set-up both take, and the location its .gitignore entry names.
HOSTED_TAP_DIR := "homebrew-tap"
TAP_FORMULA := "devpro"
[doc("set up the sibling Homebrew tap clone at homebrew-tap/")]
tap-repo:
  @TAP_DIR="{{HOSTED_TAP_DIR}}" devtools/scripts/tap-repo.sh

[doc("LIVE; NEEDS a pub release: sets tap formula's v<version> and sha256 then commits with signature")]
tap-update: tap-repo
  @just --justfile "{{HOSTED_TAP_DIR}}/scripts/justfile" TAP_FORMULA={{TAP_FORMULA}} tap-update

[doc("DESTRUCTIVE; reinstalls global brew devpro from scratch tap of for this repo")]
tap-local: tap-repo
  @just --justfile "{{HOSTED_TAP_DIR}}/scripts/justfile" TAP_FORMULA={{TAP_FORMULA}} tap-local

dev-devpro *args:
  @PYTHONPATH="{{PROJECT_ROOT}}" python3 -m devpro "${@}"

[doc("serve the dashboard — the board and the session records — from the checkout's devpro")]
dev-dashboard:
  @just dev-devpro dashboard

[doc("run ACTIVE_PLAN format compliance check")]
dev-check-plan:
  @just dev-devpro check-plan

[doc("run ACTIVE_DESIGN final-form check")]
dev-check-design:
  @just dev-devpro check-design

[doc("run check that ACTIVE_DESIGN deltas have been applied to project docs")]
dev-check-design-deltas-applied:
  @just dev-devpro check-design --deltas-applied

[doc("run ROADMAP format compliance check")]
dev-check-roadmap:
  @just dev-devpro check-roadmap

[doc("check doc links and the PROJECT_DOCS tree")]
dev-check-links:
  @just dev-devpro check-links PROJECT_DOCS *.md
  @just dev-devpro check-tree PROJECT_DOCS

test-undice-architecture:
  @command rm -rf .devpro-temp/undice-mono-arch
  @just dev-devpro undice PROJECT_DOCS/ARCHITECTURE .devpro-temp/undice-mono-arch

test-undice-conventions:
  @command rm -rf .devpro-temp/undice-mono-conv
  @just dev-devpro undice PROJECT_DOCS/CONVENTIONS .devpro-temp/undice-mono-conv

test-undice-spec:
  @command rm -rf .devpro-temp/undice-mono-spec
  @just dev-devpro undice PROJECT_DOCS/SPEC .devpro-temp/undice-mono-spec

import? '.claude/skills/devpro/tools/runner-snippets/devpro.just'
