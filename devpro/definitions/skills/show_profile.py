"""The profile skill: this session's activity trace, rendered as a page the user can open.

It carries no supporting file and no harness text: the launcher it finds is the one the install
copies beside it, and the page it writes is the same page everywhere.
"""

from devpro.definition import Definition
from devpro.vocabulary import Kind

_DESCRIPTION = (
    "Use when the user asks to see the profile, the trace, the call tree, or what this session's "
    "skills and agents cost; NOT for reading or editing a trace by hand."
)

_BODY = """Render this session's trace and put the page where the user can open it. The trace is the newest
session recording in `.devpro-temp/harness-profile/` at the repository root.

## Locate the profiler

Use the first launcher that exists:

1. `../../libexec/hp.sh`, from this skill's own directory: the copy the project's install delivered
   beside it.
2. `.claude/harness-profiler/hp.sh` at the repository root: the copy a committed hook runs, which is
   how a claude-on-web session records anything at all.

Where neither stands, the profiler is not installed here: say so and stop. A repository can carry
both, and the committed copy can be older than the installed one, so the installed one goes first.

Where the hook is not installed and the session cannot install it, `sh HP init claude` commits it to
this repository's `.claude/`; run it only when the user asks for profiling there.

Call the launcher `HP` below and run it with `sh`.

## Render the trace

```
mkdir -p .devpro-temp
sh HP tree
sh HP tree --format html > .devpro-temp/harness-profile.html
```

The page goes to the project's scratch directory. Where `mkdir` cannot create it, say so and stop.

Where `tree` reports that no calls were recorded, say so, run `sh HP doctor`, report what it prints,
and stop.

## Deliver the page

On the user's machine, give them the path and open the page: `open` on macOS, `xdg-open` on Linux,
`start` on Windows. Where the session cannot open a page for them, publish it as an artifact where
the harness offers one, and otherwise give them the path.

## Answer

In two or three lines: how many calls and contexts the tree holds, and the three most expensive
contexts by duration with their tokens, read from the text tree. Then the page's path. Do not paste
the tree."""

DEFINITIONS = (
    Definition(
        name="show-profile",
        kind=Kind.SKILL,
        description=_DESCRIPTION,
        body=_BODY,
    ),
)
