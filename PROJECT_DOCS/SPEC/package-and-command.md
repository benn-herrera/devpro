## Package and Command

The devpro package installs on Python 3.9 or later, with no third-party runtime dependency. It has
two install sources: a release tag's git URL,
`git+https://github.com/benn-herrera/devpro@v<version>`, or a built wheel. No package index publishes
it. A Homebrew tap is a distribution channel for that release archive, not a package index.

The installed package provides the `devpro` command. `python3 -m devpro` is the same command:
both print the same `--help`, and the same arguments install the same product, byte for byte.
The install verbs — `render`, `install`, `install-agents-file`, `render-agents-file` and the
hidden `harness` — exit 0 on success and 2 on a refusal or an operating-system failure, printing
`error: <message>` on
stderr; the dicing and check verbs of Dicing and Checks exit 0, 1 and 2 as that section
states. Every command that
takes components takes them as `--components=CSV`, with the default
Deployed Surfaces, Plugins states.

devpro also runs from a checkout of this repository, as `PYTHONPATH=<clone> python3 -m devpro
install …` (Deployed Surfaces). The install product is the same from a checkout or from an installed package.

The command also carries the dicing and check surface: `devpro dice-doc`, `devpro undice`,
`devpro dice-docs`, `devpro check-links`, `devpro check-tree`, `devpro check-plan`,
`devpro check-design` and `devpro check-roadmap` (Dicing and Checks), and the
`devpro dashboard [<project-dir>] [--port <number>]` verb — devpro's one loopback server for the
web interface: its traces panel the rendering the retired `devpro profiler serve` drove, its board
panel the board the retired `devpro kanban` served. The verbs run wherever the `devpro` command
runs; they are not part of the install product.

A check that protects or assumes a checkout holds only when devpro runs from one. A worktree and
an editable install of a clone count as one. The devpro package installed into a Python
environment does not, wherever the environment sits, including inside another project's repository.
Run from an installed package:

- A project install writes its runner include lines for any project (Deployed
  Surfaces, Plugins).
- Installing the agents file is not refused for uncommitted changes (Agents File).

From a checkout, every one of these checks holds; the uncommitted-changes refusal there covers only
the writes Agents File names.
