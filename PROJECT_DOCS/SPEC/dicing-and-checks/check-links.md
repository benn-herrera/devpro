# check-links

`devpro check-links <root>...` checks markdown files that need not come from a dicing. A directory
root contributes every `.md` file beneath it in sorted order; a file root is checked alone; a file
reached twice is checked once. Every root must exist, else exit 2 (`no such root: <roots>`). Every
file so contributed must be readable as a file; before any link is checked, each that is not prints
`cannot read: <path>` to stderr and the verb exits 2.

In text outside fenced code and code spans, every link is checked except those with an empty
target, a target opening with `/`, or a URL scheme ([link targets](../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks), step 2).
The target's path part (the linking file itself, if empty) must exist, else the problem is
`missing file`; given a `#fragment` it must name a markdown file with a heading whose anchor equals
the fragment ([anchors](../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks), repeats counted over the file), else `missing anchor`.
Each problem prints to stderr `<file>:<line>: <target>: <problem>`. The summary
`links checked: <N>, broken: <B>` goes to stdout. Exit 1 if any link is broken.
