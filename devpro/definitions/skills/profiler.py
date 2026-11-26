"""The profile skill: this session's activity trace, served to the user as a page in their browser.

It carries no supporting file, and of the harness's text only the path of the tree's own wrapper — the
project's committed one where `init` rendered the skill, the installation's own where the install
rendered it — and the page the dashboard serves is the same page everywhere. The skill writes no page
file — the trace reaches the user through the served URL alone.
"""

from devpro import clauses
from devpro.definition import Definition
from devpro.vocabulary import Kind

_DESCRIPTION = (
    "Use when the user asks to see the profile, the trace, the call tree, or what this session's "
    "skills and agents cost; NOT for reading or editing a trace by hand."
)

DEFINITIONS = (
    Definition(
        name="profiler",
        kind=Kind.SKILL,
        description=_DESCRIPTION,
        body=f"""Serve this session's recorded trace to the user as a page in their browser. The trace is the newest
session recording under `.devpro-temp/` at the repository root: `.devpro-temp/.profiler-claude/` under
claude, `.devpro-temp/.profiler-opencode/` under opencode. `PROFILER` below is the tree's own wrapper,
`{clauses.PROJECT_WRAPPER}`, run with `bash`; `bash PROFILER tree` reads both stores.

## Locate the profiler

`PROFILER` is `{clauses.PROJECT_WRAPPER}` at the repository root: the project's committed wrapper where
`init` rendered this skill beside it, and the installation's own where the install rendered it. Where
that file does not stand — always, under mage, whose install ships no profiler — the profiler is not
installed here: say so and stop.

Under claude, where the hook is not installed and the session cannot install it, `bash PROFILER init claude`
writes it into this repository's `.claude/` and prints the `git add` line to commit; run it only when
the user asks for profiling there. `init` is claude's alone: opencode's plugin records
every call itself, so an opencode session does not need it.

{clauses.WRAPPER_PROFILER}

## Serve the trace

The records are served by the dashboard, `DP dashboard`: it opens on the project's board, and its
profiler view at `/profiler/` — reached from the page's top nav — is this repository's recorded
sessions, each linking to its page. It prints the URL it serves on stdout and runs until
interrupted: start it out of the session's way — it never completes, so the URL is read from the
running job's output once it prints — then hand the user that URL. Where a one-off export is
wanted, `bash PROFILER tree --format html > .devpro-temp/harness-profile.html` writes a session's page to
a file.

## Answer

In two or three lines: how many records the trace holds, as the profiler's own view of the session
states it — the trace list at `/profiler/`, whose row for the session states the count, is its
source; never a count of lines you take yourself, where a record is a call or an event marker and a
call the plugin and the committed hook both recorded appears twice — and, for a claude session, the
three
most expensive contexts by duration with their tokens, read from `bash PROFILER tree --verbose`, which draws
every node of the session; the plain tree draws the placeholder and marker nodes and the calls whose
tool is in `PARENT_TOOLS` — the skills, agents and compactions — so a session of plain tool calls
prints the column header alone on the plain tree. An opencode session records no token counts,
so say so where those columns are blank. Then the URL the dashboard printed. Do not paste the tree.

Where the plain tree prints the column header alone, nothing was recorded: say so and stop. Where
`tree` instead exits 1 with `No traces in …` on stderr, no store `tree` reads holds a record. Under
claude, run `bash PROFILER init claude`: it registers the hook in the repository, which a session
loading no plugin's hooks picks up, renames a store an older name left behind, and writes the
committed settings and the skill copy the repository carries — the git-visible writes `init`
reports. Under opencode the hook is the plugin's and already runs, so a store under the older name
is what stands in the way, and the next install renames it.""",
    ),
)
