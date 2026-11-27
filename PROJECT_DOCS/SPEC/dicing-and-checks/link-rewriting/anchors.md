# Anchors

The GitHub-style anchor of a heading (ATX, levels 1 to 6, up to three leading spaces, outside
fenced code): text with closing `#` run removed, taken as plain text
([what is a link](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/link-rewriting/what-is-a-link.md#what-is-a-link)), lowercased, every character that is not a letter, digit,
space, `-` or `_` deleted (letters and digits include non-ASCII ones), spaces made `-`; so
`### [Plan Status Form](x)` anchors as `plan-status-form`. The Nth repeat of an anchor in one file
takes the suffix `-<N-1>` for N>1 (`setup`, `setup-1`, `setup-2`). In the source, repeats are
counted over the whole document; in a diced file, over that file's headings alone.
