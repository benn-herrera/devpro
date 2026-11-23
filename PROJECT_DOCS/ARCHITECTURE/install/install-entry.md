### Install entry

`devpro install` is the install's one entry, and `python3 -m devpro install` the same verb
(Packaging); no recipe of this repository's runner file stands in front of it. The verb takes
TARGET, its one positional
argument, and `--components=CSV`, the optional components the invocation turns on, default none
(`cli._add_components`); a second positional is an argument argparse does not
recognize, refused with exit 2 before anything is written.
`devpro/install_target.py` resolves the target, writing nothing: `resolve_install_target`
normalizes the target lexically — made absolute, `..` collapsed — detects the harness from values
no component changes (`_detected_harness`), binds that harness to the plugin, and returns the harness,
the harness directory (`InstallTarget.harness_dir`) and the project root (`InstallTarget.project_root`),
each built from that lexical path.

The devpro settings file, where it exists, selects the harnesses `install` drives — the
naming rule and the settings' semantics are SPEC.md, Install destination. `install_target.py`
provides the per-harness directory judgment the `detect` setting needs;
`_detected_harness`'s single-harness resolution stays the no-config path's. Without the file, or
with `--harness` given, the resolution is the one above. One read of the file serves the
selection and every harness's render. `install` uses the project root as spelled, and resolves it
only to compare it with this checkout (`REPO_ROOT`, `runner_file.install_include_lines`), so
two spellings of the checkout compare equal. The install directory's path relative to it
(`_harness_relpath`) is taken as both are spelled. The harness and harness directory follow
SPEC.md, Install destination; every directory name is read from the `Harness` values
(`project_harness_dir`, `user_harness_dir`, and `plugin_parent_dir` for a harness-directory plugin,
`Harness.is_harness_dir_plugin`: a harness whose harness directory is itself a plugin), and the
home-directory and user-harness-directory comparisons resolve both sides, so two spellings of one
directory compare equal. The resolver decides neither the install directory nor whether the
install is user-level; `cli.py` passes the harness directory to `install`, which computes
`root = harness_dir / harness.plugin_dir` and decides user-level from
`user_dir_harnesses(harness_dir)` naming the harness, whatever the route to it, and then renders
and prunes and skips the packages, guardrail and the runner include lines, and the harness resources
but the entry that registers the plugin (Install, Renders and copies). Prune is in terms of
the install directory, and the agents file in terms of the harness directory, which holds the
install directory. `install.py` writes the agents file in the harness directory for a harness-directory
plugin whose harness directory is not the project root. A claude or opencode project install also
runs `agents_file.checked_followed_agents_file` (Agents File). `resolve_install_target` makes the
target, harness and `--subdir` refusals of SPEC.md, Install destination, before anything is written;
the `--subdir` refusal is judged as typed. It adds the unexpanded-`~` hint to the target refusal
where the target's first component is `~`. Refused too, with nothing written: a rendered-definition
or harness-resource destination holding a file without the generated banner, and a harness-rendered
file without its marker. `check_runner` refuses a runner file that
cannot be read or decoded. Every such check, the agents file's included, runs before the first
write, and the install directory itself is created after them. A write that then fails at the
operating system is reported by `cli.main` as `error:` with exit 2.

