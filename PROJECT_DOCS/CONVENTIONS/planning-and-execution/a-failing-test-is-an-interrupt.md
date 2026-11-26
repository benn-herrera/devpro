# A failing test is an interrupt

A test failing on behavior the work under way does not state it changes is a finding the shipped
process reports, never edited to pass. This rule renames it on that record: an interrupt, the stopped
package's `State` cell note carrying the test, the verdict applied and the evidence for it. One of
three verdicts settles it:

- **axe** — the test asserts more than a defect needs: a checksum over text, unless the text is the
  contract, or a seam no stated requirement names. The test is removed, its failure with it.
- **isolate** — the behavior the test pins is real, but this work does not state it changes: the
  test leaves the default run by `xfail(strict=True)` or `pytest.mark.skip` naming its reason and
  the ticket that carries the behavior, and the pass proceeds. The behavior is roadmap work, not
  this plan's.
- **acquit** — the failure is not the work's doing: the test fails the same way without the work's
  changes. The record says how that was shown, and the pass proceeds with the test standing.

The dispatched seat stops the package and reports the interrupt to the dispatching session with the
test's name and the evidence for each verdict it considers; the session records it. A failure that
shows the work *should* change the behavior it broke is none of these: it is a scope finding, routed
through the design like any other.
