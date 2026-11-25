# File names and layout

The heading text is what follows the `#` run, with leading and trailing spaces removed. A heading
is **numbered** when the plain text ([what is a link](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks)) of its heading text
opens with digits optionally followed by `.digits` groups, an optional `.`, and a space (`1.`, `2 `,
`1.1.1.`). Its **number** is that prefix without the trailing `.`; its **title** is the rest. An
unnumbered heading's title is its whole plain text: `### [Plan Status Form](x)` is titled
`Plan Status Form`.

The **slug** of a title: ASCII uppercase lowered, backticks deleted, every maximal run of
characters outside `a-z0-9` replaced by one `-`, leading and trailing `-` removed. Non-ASCII
letters are separators, not transliterated.

The **name** of a section: `<number>-<slug>` when numbered with a non-empty slug; `<number>` when
numbered with an empty slug; `<slug>` when unnumbered. An unnumbered heading with an empty slug is
an error.

| Section | Path |
|---|---|
| Tree root (the output directory) | `entry-point.md`; `index.md` where `--section` writes it |
| Has child sections | `<parent dir>/<name>/index.md` |
| No child sections | `<parent dir>/<name>.md` |
| A volume directory (`dice` with several documents) | `<out dir>/<document base name>/entry-point.md` |

**Errors, all exit 1 with nothing written to the tree** (the output directory may be left created
and empty):

- `empty slug for heading at line <N>`: reported for the first such heading only.
- `path collision: <path> (lines <A> and <B>)`: two sections would write the same path. Every
  collision is reported, each against the previous holder of the path.

**Duplicate numbers.** Headings sharing a number are reported on stderr as
`duplicate section number <number>`, once per document `dice` dices and per document `undice`
writes. Dicing continues; a reference to the number resolves to the last heading that carries it
([section references](../../../../PROJECT_DOCS/SPEC/dicing-and-checks/index.md#dicing-and-checks)).
