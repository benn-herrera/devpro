# A test failing on unstated behavior is an interrupt

A test that fails on behavior the work under way does not state it changes stops its package and
enters the active plan as an interrupt: a recorded question with its verdict, not noise inside a
package's run. One of three verdicts settles it:

- **axe** — the test asserts more than a defect needs: a checksum over text, or a seam no stated
  requirement names. The test is removed, its failure with it.
- **isolate** — the behavior the test pins is real, but this work does not state it changes: the
  test is quarantined from the default run — skipped or expected to fail, naming the reason and the
  ticket that carries the behavior — and the pass proceeds. The behavior is roadmap work, not this
  plan's.
- **acquit** — the failure is not the work's doing: the test fails the same way without the work's
  changes, or on its environment alone. The record says how that was shown, and the pass proceeds
  with the test standing.

A failure that shows the work *should* change the behavior it broke is none of these: it is a scope
finding, routed through the design like any other.
