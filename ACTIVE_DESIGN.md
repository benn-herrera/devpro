# The test suite earns its keep

The repository's test run carries only weight that earns its place, and its records state no more
than carries forward. The default run targets 30 seconds. The screenshot suite — six end-to-end
tests of the shipped screenshot tool, two-thirds of the current run's wall time — keeps its
existence and leaves the default run under a `slow` marker, for a test that earns its cost but not
its place in the default run. Every test whose setup, call and teardown exceed 100ms earns its
place or is rewritten, merged, retired or marked `slow`. A test that is a checksum — it fails on a
change outside its subject, asserting text rather than behavior — is removed. A test is commissioned
only with the defect it dies on, and a test that fails on behavior the work does not state it
changes enters the active plan as an interrupt, its verdicts — *axe*, *isolate*, *acquit* — defined
in a CONVENTIONS leaf this design's plan writes; a project convention, not the shipped process's
law. The opencode pin has one home: the resources' headers drop the version `package.json` already
holds, and the test that guarded that duplication retires with it. The pass does not edit the
install suite's tests: installation is the project's most fraught operation. The profiler's
`doctor` and `repair` tests get no pass work: their operations' retirement is coming work, ticketed
on the roadmap as *Eliminate profiler `repair` and `doctor`* — this design invests nothing there.
For whom: the operator whose gate this run is, and the consumers who read what ships.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## ARCHITECTURE delta

### [repo-layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

**As it stands:**

```
  tests/                the devtools test suite — dupe_sweep (`test_dupe_sweep` and its import-structure test), clause_join_sites, render_diff and screenshot — run as the `dupe_sweep` test surface (`just test dupe_sweep`)
tests/                  the root test suite, the `devpro` package's tests and the repository-wide checks, run as the `devpro` test surface (`just test devpro`) with the `cold_read` marker excluded by default — the cold-read suite's subprocess cases run as the `cold-read` surface (`just test cold-read`) — never installed; the double-delivery check among the repository-wide checks compares sentences
```

**Becomes:**

```
  tests/                the devtools test suite — dupe_sweep (`test_dupe_sweep` and its import-structure test), clause_join_sites, render_diff and screenshot — run as the `dupe_sweep` test surface (`just test dupe_sweep`), its screenshot cases marked `slow`, run as the `slow` surface (`just test slow`)
tests/                  the root test suite, the `devpro` package's tests and the repository-wide checks, run as the `devpro` test surface (`just test devpro`) with the `cold_read` and `slow` markers excluded by default — the cold-read suite's subprocess cases run as the `cold-read` surface (`just test cold-read`) — never installed; the double-delivery check among the repository-wide checks compares sentences
```

**As it stands:**

```
The package's modules depend one way: `kanban/` imports `doccheck/` and `dicing/`,
`doccheck/` imports `dicing/`, `profiler/` reads `kanban/`'s stylesheet as package data,
`dashboard/` imports the panels it serves, and none of them depends on a module that depends on it.
```

**Becomes:**

```
The suite earns its keep: a test exists only where a defect exists that it dies on while the source
reads correct to its author, and it asserts behavior, not text — a source literal restated in the
test and compared back, a module's own contents mirrored against a hand copy, and a hash or exact
output compared against a literal is a checksum: it fails on a change outside its subject, not on a
defect; where detecting change is load-bearing, the mechanism is the regeneration check or the
integration test over the behavior. A test is commissioned only with the run that fails under its
defect, shown. A test whose setup, call and teardown exceed 100ms justifies its existence — it pins
a real defect no cheaper test pins, or exercises a real integration no fixture can stand in for —
or loses the weight: rewritten to a fixture, merged into a sibling, retired, or marked `slow`, the
marker for a test that earns its cost but not its place in the default run; every default run
excludes it, and `just test slow` runs the marked tests. The default run targets 30 seconds.

The package's modules depend one way: `kanban/` imports `doccheck/` and `dicing/`,
`doccheck/` imports `dicing/`, `profiler/` reads `kanban/`'s stylesheet as package data,
`dashboard/` imports the panels it serves, and none of them depends on a module that depends on it.
```

### [recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md)

**As it stands:**

```
against the host's published declarations — `@opencode/plugin`'s own types are the authority, no
devpro-owned stand-in for a published package shadows them. The declarations reach the check as a
dev-time dependency installed before `tsc` runs — a root `package.json` holds it — and the check
```

**Becomes:**

```
against the host's published declarations — `@opencode/plugin`'s own types are the authority, no
devpro-owned stand-in for a published package shadows them. The declarations reach the check as a
dev-time dependency installed before `tsc` runs — a root `package.json` holds it, and the pin's
version has no second home: a resource's header names the floor its header already names, never the
pin of the moment — and the check
```

## Code delta

### [repo-layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md)

Fixes, the code against the leaf as amended; the law the ARCHITECTURE delta adds stands in the
paragraph ahead of the leaf's module-dependency paragraph.

- The members mirror (`test_each_family_pins_the_member_of_every_category`) compares the families'
  category maps against hand copies of themselves — checksums over owner tuning, failing on a
  change outside their subject — against the leaf's law. The test is retired; the structural claim
  under it stays as an assertion over the map's keys: every category slot filled, no other.
- The two frontmatter tests (`test_claude_frontmatter_holds_the_field_order_and_spelling`,
  `test_an_unrestricted_agent_frontmatter_matches_the_pre_1_0_render`) keep the contract they
  assert — field order, spelling, presence — and drop the tuned values they carry beside it
  (`model:`'s value, the color hexes), which fail on owner tuning outside their subject.
- The stylesheet-literal assertion in
  `tests/test_devpro_profiler.py::test_the_served_index_links_the_shared_layers_own_text` is
  removed: the neighboring assertions already carry the structural invariant it gestures at, so it
  is redundant as well as a checksum.
- The headers-versus-lockfile version test,
  `tests/test_devpro_install.py::test_the_opencode_resources_name_the_host_version_the_check_is_pinned_to`,
  is retired: with the headers no longer restating the pin, the seam it guarded no longer exists.
- The six screenshot tests in `devtools/tests/test_screenshot.py` take the `slow` marker,
  registered in `pyproject.toml` beside `cold_read`; `devtools/scripts/test.sh` excludes the marker
  from the `devpro` and `dupe_sweep` surfaces and the no-surface run, and its `slow` surface runs
  the marked tests. No other test takes the marker in this design's work.

The 100ms threshold and the 30-second target are planning-time measurements, taken from the test
runner's durations report — not a check the pass runs.

### [recipes](PROJECT_DOCS/ARCHITECTURE/recipes.md)

Fix, the code against the leaf as amended: the three opencode resources' headers drop the version
`package.json` pins from their header comments, keeping the floor its header already names and the
prose — the version numbers inside the prose are behavior observations and stay. The records that
name the header-named version move with the change: the lint recipe's comment stating the lockfile
is pinned to the version the resources name, and the CONVENTIONS leaf stating the check is pinned
to the version the headers name.
