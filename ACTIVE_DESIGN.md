# Profiler dashboard corrections and sweep granularity

The profiler dashboard reads true of its own stores — a store it cannot read fails the feed, and
the failed-feed notice says so — spends its columns on the facts, and carries the reader's controls
through its own navigation. The duplication sweep reads every sentence the renderings carry, and
the double-delivery check compares at sentence grain, so prose copied between two renderings cannot
diverge unseen. Tests that guard nothing are gone. The outcomes serve the operator reading the
dashboard and the project keeping its renderings honest.

The preceding is a summary of the detailed design below. Summaries are unavoidably lossy. The summary text is not to be consistency checked. The design is authoritative.

## ARCHITECTURE delta

### [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md#repo-layout)

**As it stands:**

```
  dupe_sweep/           the duplication sweep, run as `python3 -m devtools.dupe_sweep` — enumerates one-idea-two-places candidates over the owned python trees (justfile `sweep-python`)
```

**Becomes:**

```
  dupe_sweep/           the duplication sweep, run as `python3 -m devtools.dupe_sweep` — enumerates one-idea-two-places candidates over the owned python trees, the string literals the trees carry among its sentence units (justfile `sweep-python`)
```

**As it stands:**

```
tests/                  the root test suite, the `devpro` package's tests and the repository-wide checks, run as the `devpro` test surface (`just test devpro`) with the `cold_read` marker excluded by default — the cold-read suite's subprocess cases run as the `cold-read` surface (`just test cold-read`) — never installed
```

**Becomes:**

```
tests/                  the root test suite, the `devpro` package's tests and the repository-wide checks, run as the `devpro` test surface (`just test devpro`) with the `cold_read` marker excluded by default — the cold-read suite's subprocess cases run as the `cold-read` surface (`just test cold-read`) — never installed; the double-delivery check among the repository-wide checks compares sentences
```

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md#harness-profiler)

**As it stands:**

```
The script puts `harness` and `records` under their own names, `id` in the session column,
`agents` in the dispatched-agents count, `first` and `last` in the first-to-last line, `span` in the
span column, and draws `dispatcher` in no column at all, as the child row under its dispatcher's row.
```

**Becomes:**

```
The script puts `harness` and `records` under their own names, `id` in the session column,
`agents` in the dispatched-agents count, `first` and `last` in the first-to-last line, `span` in the
span column, and draws `dispatcher` in no column at all, as the child row under its dispatcher's row.
The agents cell reads the count with the postscript `agents` — `1 agent`, `3 agents`. The index's
row links and the session page's return link carry the query, so the controls' state and the sort
in force survive the page's own navigation. An agent name a page renders drops the `devpro-`
prefix: the reader knows the set's provenance already.
```

**As it stands:**

```
A feed with no session and no unreadable store is one `stores` entry naming how many stores the
exact names read; a store an exact name finds but cannot read is an entry among them, marked
unreadable, and the server raises nothing for it.
```

**Becomes:**

```
A feed with no session and no store it cannot read is one `stores` entry naming how many stores the
exact names read. A store an exact name finds but cannot read fails the feed.
```

## Code delta

### [Repo Layout](PROJECT_DOCS/ARCHITECTURE/repo-layout.md#repo-layout)

The code reworks to match the leaf as it becomes, and the leaf stays true of the result. The
sweep's python pass reads the string literals of `devpro/definitions/`, `devpro/harnesses/` and
`devpro/clauses.py` as sentence units, the candidates reporting like the rest — sorted, byte-stable,
advisory. `tests/test_devpro.py`'s `_double_paragraphs` compares sentences: each prose unit — the
joined, whitespace-collapsed text the check already walks, not its raw lines — splits into
sentences by reusing `devtools/dupe_sweep/doc_sentences.py`'s splitter rather than carrying a
second, its punctuation split and its abbreviation behaviour included, and the repeat count runs
over the prompt's sentences instead of its units; the false-positive surface stays bounded by the
check's own scope, one prompt being one plugin's agents file and the outputs its `@` lines load, so
the families' deliberate parallel structure across different agents stays out of it. The
retired-scratch-name pin, `test_no_rendering_names_a_retired_scratch_directory` at
`tests/test_devpro.py:778`, is removed whole with its rendering loop: the scratch name flows
through one constant, and `test_the_scratch_rule_names_the_one_scratch_directory` at line 770
positively pins every harness's `scratch_rule` to that constant, so the only catch left to the pin
is a deliberate reintroduction of names nothing produces — and a negative-space test without a
credible hazard is not kept.

### [Harness profiler](PROJECT_DOCS/ARCHITECTURE/install/harness-profiler.md#harness-profiler)

The code reworks to match the leaf as it becomes, and the leaf stays true of the result.
`devpro/profiler/pages.py` stops collecting unreadable stores (`unreadable` around line 772) and
stops answering `{unreadable: <store name>}` entries (the serialization around lines 822–841); a
store the exact names find but cannot read is not converted into a feed entry — the read's
`OSError` propagates out of the feed's assembly, the handler answers the failed request by its
default failure answer, and the leaf's failed-feed notice is the reader's account of it. The
template text that consumed the entries goes with their producer: the `unreadable` renderer, its
branch and its filter in the index's script (lines 1136, 1199, 1205–1206), and the feed-keys
comment naming `unreadable` (line 1006). With no unreadable under consideration, `read_sessions`
returns the session list alone — its second, always-empty element is gone — and its callers change
with it: `dashboard/server.py:156`, the feed's unpack at `pages.py:828`, and `session_for`'s unpack
at `pages.py:1326`; `tests/dashboard/test_server.py`'s counting wrappers at lines 517 and 547
return the list; `tests/test_devpro_profiler.py:1184` drops its `[0]` and the always-empty
assertion at line 1185 goes. The guard `session_for` runs before its unpack — an unknown id returns
`None` there — stays as it stands.

Three tests pin the removed behavior and change with it: `tests/dashboard/test_server.py`'s
unreadable-store case at line 104 is removed whole; its traces-feed case at line 131 loses its
locked store, the `{"unreadable": ".profiler-claude"}` expectation at line 193, the third key-tuple
in the assertion at line 195, and the docstring sentence, its name dropping
"names_unreadable_stores"; `tests/test_devpro_profiler.py`'s served-feed case at line 996 is
removed whole. The `_denied` helper at `test_server.py:198`, used by nothing else, goes with them;
the `_unreadable` helper stays, the roadmap-refusal case at line 802 using it. Line 996's case was
also the only pin on an unknown session id's `/page/<id>` answering 404 rather than a traceback;
that pin is kept by a test with no locked store — the unknown-id path reads the stores, finds no
match and returns `None`, so without a lock the pin holds unmodified.

The link behavior, the cell postscript and the prefix drop are the leaf's sentences implemented:
the index's row links carry `location.search` into the session URL, and the session page's script
sets the return link's `href` to the profiler path with that query — the server-side band fill
keeps writing the return link's base `href`, the `return_to` the dashboard server passes staying
`PROFILER_PATH`; the agents cell's postscript is `agents`, singular and plural as the leaf's
examples show; the agent-name and cell-text sites are what the reference search finds. These
outcomes are visual, so they are verified on the served page before they land. The locked-store
drop that probing this scenario surfaced is closed with it: externally sourced or misconfigured
unreadable states are a user error the project does not support, so the drop has no in-scope
trigger.
