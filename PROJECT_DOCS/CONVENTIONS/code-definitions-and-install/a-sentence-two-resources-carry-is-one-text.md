### A sentence two harness resources carry is one text

A harness resource is copied, never rendered, so a sentence two of them carry has no constant to
share ([Shared text is one constant](shared-text-is-one-constant.md)): it is one text by the edit that
changes both, and by a test that reads both and fails where they differ. `tests/test_guardrail.py`
holds the two guardrail scripts to one policy; the plan-state reminder sentence claude's
`state-table-reminder.sh` and opencode's `index.ts` carry is one text the same way.

A predicate two of them carry is held the same way, though not as one text: the gate
`state-table-reminder.sh` and `index.ts` both read — the plan file or the diced tree, nothing else —
has no second form to drift to, and the tests that drive each resource's gate fail where a standing
plan opens one and not the other.
