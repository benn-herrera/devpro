# A verification entry names what the run produced

A verification entry states the runner targets or commands it ran and what they returned, and lists
by path the artifacts the run produced.

> "Produced" is the run's own writes — a report, a rendered file, a placed tree — not a pass value:
> a runner target's pass is the entry's *returned*, stated beside nothing. The commit audit counts
> evidence that exists only in the report as evidence that does not exist, so a path is the proof.

("Returned" is the pass or the captured failure text, never the tool's full output, quoted only where
the report rests on a specific line. Provenance: observed — Write tool calls end with a "Wrote file
successfully" line printed to the conversation, which enters a report unquoted no less easily than
full output, and models trained on terminal transcripts quote it as tool output.)
