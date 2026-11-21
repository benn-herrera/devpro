"""The profile skill: this session's activity trace, served to the user as a page in their browser.

It carries no supporting file and no harness text: the launcher it finds is the one the install
copies beside it, and the page `serve` renders is the same page everywhere. The skill writes no
page file — the trace reaches the user through the served URL alone.
"""

from devpro.definition import Definition
from devpro.vocabulary import Kind

_DESCRIPTION = (
    "Use when the user asks to see the profile, the trace, the call tree, or what this session's "
    "skills and agents cost; NOT for reading or editing a trace by hand."
)

_BODY = """Serve this session's recorded trace to the user as a page in their browser. The trace is the newest
session recording under `.devpro-temp/` at the repository root: `.devpro-temp/claude-profiler/` under
claude, `.devpro-temp/opencode-profiler/` under opencode. `sh HP tree` reads both stores.

## Locate the profiler

Use the first launcher that exists:

1. `../../profiler/hp.sh`, from this skill's own directory: the installed copy, present where a
   project install delivered it beside the skill; a user-level install copies no resource, so the
   file does not exist there.
2. `.claude/harness-profiler/hp.sh` at the repository root: the copy a committed hook runs, which is
   how a claude-on-web session records anything at all.

Where neither stands, the profiler is not installed here: say so and stop. A repository can carry
both, and the committed copy can be older than the installed one, so the installed one goes first.

Under claude, where the hook is not installed and the session cannot install it, `sh HP init claude`
writes it into this repository's `.claude/` and prints the `git add` line to commit; run it only when
the user asks for profiling there. `init` and `doctor` are claude's alone: opencode's plugin records
every call itself, so an opencode session needs neither.

Call the launcher `HP` below and run it with `sh`.

## Serve the trace

```
sh HP serve
```

`serve` prints the URL it serves on stdout and runs until interrupted: start it out of the
session's way — it never completes, so the URL is read from the running job's output once it
prints — then hand the user that URL. Its index lists this repository's recorded sessions,
each linking to its page. Where a one-off export is wanted, `sh HP tree --format html >
.devpro-temp/harness-profile.html` writes a session's page to a file.

## Answer

In two or three lines: how many records the trace holds — count the lines of that recording, where
a record is a call or an event marker, and a call the plugin and the committed hook both recorded
appears twice — and, for a claude session, the three most expensive contexts by duration with their
tokens, read from `sh HP tree --verbose`: the plain tree draws only the skills, agents and
compactions, so a session of plain tool calls prints the column header alone. An opencode session
records no token counts, so say so where those columns are blank. Then the URL `serve` printed. Do
not paste the tree.

Where the verbose tree prints the column header alone, nothing was recorded: say so, and, under
claude, run `sh HP doctor`, report what it printed about the traces and the newest session, and that
its plugin-record check cannot see the payload copy, and stop. Where `tree` instead says
`No traces in …`, the repository holds no recording at all: say so and stop."""

DEFINITIONS = (
    Definition(
        name="show-profile",
        kind=Kind.SKILL,
        description=_DESCRIPTION,
        body=_BODY,
    ),
)
