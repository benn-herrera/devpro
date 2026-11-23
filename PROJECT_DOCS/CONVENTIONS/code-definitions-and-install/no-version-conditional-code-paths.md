### No version-conditional code paths

Code runs on the floor and above with one path. A feature the floor provides is used presumptively;
compat code for a version below it leaves by deletion — never as a check rewritten to branch the
other way, and nothing the floor provides is withheld for the sake of a later interpreter either.

A version branch is a second path to test for the same task, and the tests that would cover it are
the ones nobody writes. A new mechanism must win by a wide margin to be worth that second path; a
workaround for an older interpreter never does.

The floor has one home and it is enforcement, not a branch: `requires-python`, the venv recipe that
rebuilds a venv below it, and the wrapper's refusal. A statement of support, a refusal below the
floor, is not compat code.
