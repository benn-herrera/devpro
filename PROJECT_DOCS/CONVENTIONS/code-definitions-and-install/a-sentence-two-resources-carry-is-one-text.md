### A sentence two harness resources carry is one text

A harness resource is copied, never rendered, so a sentence two of them carry has no constant to
share ([Shared text is one constant](shared-text-is-one-constant.md)): it is one text by the edit that
changes both, and by a test that reads both and fails where they differ. `tests/test_guardrail.py`
holds the two guardrail scripts to one policy; the plan-state reminder sentence claude's
`state-table-reminder.sh` and opencode's `index.ts` carry is one text the same way.

The rule's scope reaches a resource and a devpro module where one behavior runs in both. The
profiler's capture is the case: it runs in two places — the opencode plugin's TypeScript resource,
`profiler.ts`, and devpro's own `devpro/profiler/capture.py` — and one of them is no harness resource,
so the one-text test reads one resource and one module: what `profiler.ts` redacts and what
`capture.py`'s `mask` redacts is one text, held by `tests/test_devpro_profiler.py`'s
`test_the_two_masks_redact_alike` over one sample list. The mechanism is unchanged — a test that reads
both and fails where they differ — and the one text is the edit that changes both.

A predicate two of them carry is held the same way, though not as one text: the gate
`state-table-reminder.sh` and `index.ts` both read — the plan file or the diced tree, nothing else —
has no second form to drift to, and the tests that drive each resource's gate fail where a standing
plan opens one and not the other.
