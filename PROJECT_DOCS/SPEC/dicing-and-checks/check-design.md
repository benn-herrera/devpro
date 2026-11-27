# check-design

`devpro check-design [--deltas-applied] [<design>]` checks that a design is in its final form,
ready to plan from: beside the form, every pair's from passage still matches its target, so a
design is accepted only against the targets it changes. With `--deltas-applied` it instead checks
that every pair has been applied: its target holds the becomes passage and no longer the from, an
addition excepted. A design still being drafted fails it in either mode.

**Terms.** [check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)'s terms, and [check-roadmap](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap)'s (below:
layout, category, ticket, old-form item), are used as defined there, with these additions:

- **design**: a tracked markdown document, a monolith or a diced tree given by its
  `entry-point.md`. A diced design is its entry point and every other `.md` file beneath the entry
  point's directory, each read once, in **document order**:
  - the entry point;
  - the files its Contents links reach, depth first: from a **head file**, a file named
    `entry-point.md` or `index.md`, each link from its last `Contents:` line on is followed in link
    order; a linked file is read where its link is first met and, where it is a head file, its own
    links are followed there, before the next link. A Contents link to anything but a `.md` file
    beneath the entry point's directory is ignored;
  - the files those links do not reach: a directory's own files before its subdirectories', each
    level in name order.

  Each head file is read without its Contents block and what follows it.
- **H1**: the design's first level-1 heading, as for a plan ([check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)).
- **delta heading**: a level-2 heading whose text
  ([file names and layout](../../../PROJECT_DOCS/SPEC/dicing-and-checks/the-diced-tree/file-names-and-layout.md#file-names-and-layout): after the `#` run, surrounding spaces
  removed) is exactly `SPEC delta`, `ARCHITECTURE delta` or `Code delta`; that is their **order**.
  Its **delta** runs to the next heading of level 1 or 2, or the end of the design.
- **entry**: a ticket ([check-roadmap](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap)) inside a delta. A delta with no entries is
  valid.
- **target**: the file an entry heading's one link names, resolved relative to the file the entry
  is in ([link rewriting](../../../PROJECT_DOCS/SPEC/dicing-and-checks/link-rewriting/index.md#link-rewriting)). A heading whose link is empty, opens with `#`, or opens with
  a scheme ([link targets](../../../PROJECT_DOCS/SPEC/dicing-and-checks/link-rewriting/link-targets.md#link-targets), step 2) gives no target; a fragment-only link's
  fragment is not resolved here, [check-links](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-links.md#check-links) doing that. An entry heading that
  carries more than one link gives no target.
- **pair**: in an entry with a target, an `**As it stands:**` line — outside fenced code, alone on
  its line — and the fenced block whose opening line is the next non-blank line after it, the
  pair's **from**, then a `**Becomes:**` line — outside fenced code, alone on its line — and the
  fenced block whose opening line is the next non-blank line after it, the pair's **becomes**. An
  entry without a target has no pairs. The checks below run over an entry's pairs and its heading's
  links; its other text and unlabeled fenced blocks are not checked.

Every line outside a delta is free except a level-2 heading and what the layout
([check-roadmap](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap)) does not admit.

**The form, as checked.** The design is read in the layout ([check-roadmap](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap)): each
breach of the layout is a breach of the design form, reported as
[check-roadmap](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap) reports it. The delta rules add these:

| Breach | Reported at | `found` text |
|---|---|---|
| a level-2 heading that is not a delta heading but equals one when compared without regard to case, with each run of whitespace read as one space | the heading | the heading line |
| any other level-2 heading that is not a delta heading | the heading | the heading line |
| a delta heading that repeats an earlier one | the later heading | the heading line |
| a delta heading, not a repeat, that follows a delta heading the order places after it | that heading | the heading line |
| no delta heading | the H1, else line 1 of the design's first file | the line |
| a non-blank line inside a delta before its first entry, other than one the layout reports; reported once per delta, at the first such line | the line | the line |
| an entry heading that carries more than one link and whose title is not empty once its links are reduced to their text | the heading | the heading line |
| a pair label that opens no pair | the label line | the line |
| a pair's target that cannot be read | the pair's `**As it stands:**` line | the target's path |
| a pair whose from does not match | the pair's `**As it stands:**` line | the from passage's first line |
| a pair that has drifted | the pair's `**As it stands:**` line | the from passage's first line |
| a pair that is conflicting | the pair's `**As it stands:**` line | the from passage's first line |

Each form breach's accepted form is the form the Terms give, except a pair's, whose accepted text
the delta claims give.

Whether an entry's link resolves is not checked: [check-links](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-links.md#check-links) does that.

**The delta claims.** The check reads each pair's target file and matches its passages against
the target's text with each run of whitespace on either side read as one space, every other
character exact. Without `--deltas-applied`, every pair's from must match; one that does not is
a breach. With `--deltas-applied`, the matching of both passages classifies each pair: from
present and becomes absent, the pair is **pending**; from absent and becomes present, it is
**landed**; both absent, it is **drifted**; both present, it is **conflicting**. A pair whose
target cannot be read has no matching to classify and is **unreadable**. An addition is a pair
whose from passage is not empty and whose becomes passage contains it: a present becomes means
landed, a present from alone means pending, and an addition is never conflicting. A pair whose
from passage contains its becomes passage is a removal: it is conflicting while its from is
present, and landed only once its from is gone. Landed is the passing state, pending the expected
mid-execution state; a drifted or conflicting pair is a breach. Each pair breach is reported at
the pair's `**As it stands:**` line, its `accepted` text `matching in <target>`; a target that
cannot be read is a breach reported there too, its `accepted` text `a readable target file`. Where
a drifted or conflicting pair's target is also the target of a landed pair of the same design, the
breach line is followed on stderr by
`interference: <target> also holds the becomes passage of a landed pair of this design`. The
checks read their targets, never write them.

**The design checked.** With `<design>`, that design. Without it, the active design of the project
root ([check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)), at the path [the project's files](../../../PROJECT_DOCS/SPEC/dicing-and-checks/kanban/the-project-s-files.md#the-projects-files)
gives; where both exist as files, the verb exits 2 before reading either.

**Output.** One stderr line per breach, in the form [check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan) gives
(`<file>:<line>: <problem>: <found>; accepted: <accepted form>`), in document order. An empty
`found` text renders as [check-roadmap](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-roadmap.md#check-roadmap) gives. Current `<problem>` wording:

| Breach | `<problem>` |
|---|---|
| misspelled delta heading | `delta heading misspelled` |
| other level-2 heading | `section is not a delta` |
| repeated delta heading | `delta heading repeated` |
| delta heading out of order | `delta heading out of order` |
| no delta heading | `design has no delta` |
| content before the first entry | `delta holds content outside an entry` |
| an entry heading that carries more than one link | `entry heading carries more than one link` |
| a pair label that opens no pair | `pair is incomplete` |
| a pair's target that cannot be read | `target cannot be read` |
| a pair whose from does not match | `from not found` |
| a pair that has drifted | `pair has drifted` |
| a pair that is conflicting | `pair is conflicting` |

The summary `design checked: <design>, entries: <N>, problems: <P>` goes to stdout. With
`--deltas-applied`, one stdout line per pair, in document order,
`<file>:<line>: <state>: <target>` — `<line>` the pair's `**As it stands:**` line's number,
`<state>` one of pending, landed, drifted, conflicting, unreadable — and the summary is
`design checked: <design>, pairs: <N>, landed: <L>, pending: <G>, drifted: <D>, conflicting: <C>,
problems: <P>`. A pair counted in no state is unreadable: its count is `<N>` less the four
states' sum.

**Exit status.** As [check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)'s table, with these changes: in the row "without
`<plan>`, no active plan under the root", the message is `no active design in <root>`; the row
"without `<plan>`, both forms of the active plan exist" applies with `design` for `plan`, and its
message is `both forms of the active design exist: <monolith> and <entry-point>: remove one`; a
named design that is not a file is the usage error `no such design file: <design> (name a design's
markdown file, or a diced design's entry-point.md)`; the no-project-root message names
`devpro check-design` and `devpro check-design <design>`. A diced design's unreadable file is as a
diced plan's ([check-plan](../../../PROJECT_DOCS/SPEC/dicing-and-checks/check-plan.md#check-plan)), or a `.md` file beneath the entry point's directory that
a Contents link names and that cannot be read as a file: `cannot read: <file>`, exit 2. A Contents
link to anything else is ignored (Terms). With `--deltas-applied`, the verb returns 0 where every
pair has landed and no breach stands, and 1 while any pair has not landed or a breach stands:
the summary's counts and the stderr breach lines say which pairs remain, pending being the
expected mid-execution state rather than a fault of the design.
