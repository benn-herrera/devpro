# ACTIVE DESIGN

## Drafts

### Every test over 100ms justifies its existence

The suite's full run is ~57-60s for ~1,700 tests, and the weight has accumulated unexamined. A
pass where every test whose setup+call+teardown exceeds 100ms justifies its existence, one of four
verdicts: *earns* (pins a real defect no cheaper test pins, or exercises a real integration no
fixture can stand in for), *cheapens* (rewritten to a fixture so it drops under threshold),
*merges* (duplicate coverage with a sibling), or *goes*. Open for the design: whether a `slow`
marker (the `cold_read` pattern) is a third way for tests that earn their cost but not their place
in the default run; any target for total full-run wall time. First probe, already in
`.devpro-temp/weight-durations.txt`: pytest `--durations=100` over the full default run.

### Tests exist only with a defect they die on

A test protects only where a defect exists that it dies on while the source reads correct to its
author. It must assert behavior, not text.

The pin test — a source literal restated in the test and compared back to the source, an exact
log output check, a polyglot 'is this doing all the things' check against an multi-property 
artifact — is a coverage-mandate fossil: built to satisfy a 100%-coverage metric, not to find a
defect. It is shaped like a test while doing the metric's job. Human projects mass-produced it, the 
training data carries it, and agents reproduce it however often a rule forbids it; prohibition alone
has had modest effect against a prior fed by ten thousand coverage-gaming suites. The same holds for
a change-detector that knows it is one, a hash against a literal. Where detecting change is
load-bearing — generated files, frozen contracts — the mechanism is the regeneration check or an
integration test over the behavior. Coverage that unit tests cannot reasonably reach belongs to the
integration test, never to a pin.

The reason this category of test is an antipattern and anathema - it produces pure friction for
no benefit. It is a suit of armor with fixed joints that requires a plasma cutter and welder
for every change of pose.

Found instances. Two pin the claude family's model assignments, both in `tests/test_devpro.py`:
`test_each_family_pins_the_member_of_every_category` asserts the category map equals a hand-copied
dict of itself; `test_claude_frontmatter_holds_the_field_order_and_spelling`, whose subject is
field order and spelling, carries `model: opus` in its expected tuple. Both photograph owner
tuning: `829f7e7` changed one model entry and the gate ran red until the pins followed. The third
pins presentation text: `tests/test_devpro_profiler.py`'s index test asserts the whole
`table { … }` declaration, so a layout change the presentation layer invites — P3's column
widths — cannot land without either shaping the CSS around the pin or editing it.

Three parts:

1. **Prune the instances.** Keep the form asserts that are contract — order, spelling, quoting,
   required fields. Assert the `model:` line is present, not its value. Rework or retire the
   members mirror.
2. **Commission tests.** Wherever a test can be born, not only in plan packages, it exists only
   with its defect named and the run that fails under that defect shown — the
   `clauses.TEST_PRECONDITION` shape.
3. **Triage a test that fails on unstated behavior, at once.** The work does not state it changes
   this behavior, yet the test fails on it: the test enters the active plan immediately as an
   interrupt — its own row, closed by one commit — and the package that tripped it does not
   proceed until the row closes. Three verdicts: *axe* (the test checks nothing); *isolate* (it
   checks something, too sensitively — refactor it to depend only on its own subject); *acquit*
   (it checks something real and the work broke it — the work is the suspect *or* it was an unavoidable
   side-effect of the required change and the test needs legitimate rework). A report to the owner
   is not the mechanism; the updated plan is.

### Change devpro config format

It's currently .cfg but .toml allows for nesting (which we are faking with <harness>-model-map group)
The upgrade to python 3.11 makes toml available without a dependency.
