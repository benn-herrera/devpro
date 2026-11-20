# ACTIVE DESIGN

## Drafts

### The profiler serves its pages over HTTP

Decision (user): the render path turns from file-out to serve-on-demand — `hp.py` renders pages in
memory behind a small HTTP server, and the server's main page is the list of record files it can
render to HTML from.

Facts: the page is already built in memory — `tree --format html` performs the template substitution
and returns the HTML string (`hp.py:1072`); the file step is only the shell redirect the skill
instructs. `list_sessions` (`hp.py:1080`) already reads every `*-profiler` store with record counts
and first/last moments — the index's data source, both harnesses included. The subcommand dispatch
(`hp.py:1341`) gains the verb; `http.server` is standard library, so the one-file stdlib-only
constraint and the 3.9 floor hold. The payload's file set stays `hp.sh`, `hp.py`, `view.html` — the
index page is generated inline rather than adding a second template.

Shape (proposed): `hp serve [--port N]` binds 127.0.0.1 only — the records are masked but stay
local — and prints the URL it serves. Routes: `/` renders the index inline, one row per record file
across both stores (harness from the store's directory name, session id, record count, first and
last moments), each row linking to its page; `/page/<session-id>` renders the existing page for that
session's records in memory, byte-for-byte what `tree --format html` produces today. The default
port is 8765, `--port` overrides. The CLI's file-redirect form remains as a capability the skill no
longer instructs.

Open: whether the show-profile skill's flow switches to `serve` as the primary render path
(proposed: yes — the skill's instruction becomes start the server, hand the user the URL — with the
file-redirect demoted to a mention) or keeps both forms side by side.
