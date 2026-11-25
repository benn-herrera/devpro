## dice-doc

`devpro dice-doc [--split-level <level>] <monolith.md> <out-dir> [map.tsv]` dices one document
([the diced tree](tree.md), [link rewriting](links.md)) at the deepest split level `<level>`
([shared behaviors](index.md#shared-behaviors)), using `map.tsv` as the link map
([the link map](links.md#the-link-map)) if given.

Order of effects and failures:

| Condition | stderr | Exit |
|---|---|---|
| `monolith` is not a file | `not a file: <monolith>` | 2 |
| `map` given and not a file | `not a file: <map>` | 2 |
| `out-dir` exists and is not a directory | `not a directory: <out-dir>` | 2 |
| `out-dir` exists and is not empty | `out-dir not empty: <out-dir>` | 2 |
| Planning fails ([file names and layout](tree.md#file-names-and-layout)) | that section's message | 1 |
| A section's heading ladder cannot be re-based ([file content](tree.md#file-content)) | `heading too deep to re-base at line <N> (<level>): written at its monolith level` | 1 |

Otherwise `out-dir` is created if absent, the tree is written, and stderr receives the
`refs linked` line ([section references](links.md#section-references)) and any warnings of
[the diced tree](tree.md). The [reassembly check](checks.md#reassembly) then runs; on failure its
message goes to stderr and the verb exits 1 without running the link check. The
[link check](checks.md#link-check) follows; its `dead link` lines go to stderr and its summary to
stdout. Exit 0 only when both checks pass. Files already written remain on failure.

## undice

`devpro undice [--split-level <level>] <tree-dir> <monolith.md>` writes the document a diced tree
holds as one file. `<level>` ([shared behaviors](index.md#shared-behaviors)) names the deepest
split level the tree was diced at; links are restored at that level. `<monolith.md>` need not be
the document the tree was diced from.

**Round trip.** For a tree as `dice-doc` wrote it at `<level>` without a map, with well-formed
Contents links ([file content](tree.md#file-content)): move `<tree-dir>` aside and dice the
unchanged `<monolith.md>` with `dice-doc` at `<level>`, without a map, from the same current
directory, into `<tree-dir>`; the new tree equals the old byte for byte.

| Condition | stderr | Exit |
|---|---|---|
| `<tree-dir>/entry-point.md` is not a readable file | `not a tree: <tree-dir>` | 2 |
| `monolith` exists | `<monolith> exists: name another output, or move or delete it` | 2 |
| `monolith` cannot be written | `cannot write: <monolith>` | 2 |

**Content.** The entry point's lines, then each file linked from its last `Contents:` line on, in
that order; a linked file that cannot be read prints `undice: cannot read <tree-dir>/<target>` to
stderr, is left out, and fails the verb (exit 1). From each file read that is named
`entry-point.md` or `index.md`, the Contents block and every line after it are dropped
([reassembly](checks.md#reassembly)'s cut). Each other file's heading ladder is restored before it
is written: a file whose top heading reads level 1 is in the re-based form
([file content](tree.md#file-content)) and is put back at the shallowest level its place in the tree
permits — one below its directory's depth, raised where a heading below its top would otherwise
land at a split level and split it into two sections — and a file whose top reads any other level is
the pre-change form and is written as it stands. The tree does not record the level a re-based
section came from, and no two documents with the same tree can be told apart, so the document
written is the one the tree holds: it need not be the document the tree was diced from, and it
dices back to the same tree ([undice](#undice)'s round trip). Links are restored outside fenced code
and code spans:

- A section link ([section references](links.md#section-references), step 3) becomes its link text:
  `§<number>`, or `§<number>` and the backticked name.
- A link to a heading's place in the tree, as [link targets](links.md#link-targets) step 1 writes
  it, becomes `#<anchor>`, the heading's anchor in `<monolith.md>`
  ([anchors](links.md#anchors)).
- Every other relative link is rebased from its file's directory to the current directory, fragment
  kept. Links left unchanged by [link targets](links.md#link-targets) step 2 stay unchanged.

**Self-check.** After writing, `<monolith.md>` is planned at `<level>` ([the diced tree](tree.md),
its messages to stderr as in [dice-doc](#dice-doc)); a planning failure exits 1 there. Otherwise
the [reassembly](checks.md#reassembly) and [link checks](checks.md#link-check) run on it against
`<tree-dir>`, with their messages and streams as in [dice-doc](#dice-doc). Every `.md` file under
`<tree-dir>` must also be one [file names and layout](tree.md#file-names-and-layout) assigns,
except files under a directory below the root that holds its own `entry-point.md` (a nested
volume). Each other prints to stderr, naming the remedy rather than applying one:

| The file | Message |
|---|---|
| was read as a section that [file names and layout](tree.md#file-names-and-layout) places at another path | `undice: <file> would be re-diced as <tree-dir>/<path>: rename the file or edit its heading to match` |
| was read, but opens no section | `undice: <file> opens no section: start it with a level 2 to <level> heading, or remove it and its Contents line` |
| was not read | `undice: not reproduced: <file>: link it from <tree-dir>/entry-point.md's Contents, or remove it` |

A file was read when a link from the entry point's last `Contents:` line on resolves to it. It was
read as a section when its first line opens a section of `<monolith.md>` other than the entry
point; a file read more than once was read as the first such section in document order. Contents
blocks are not compared, so a hand-edited block is regenerated by the round trip without a report.
Exit 0 if all pass, else 1; `<monolith.md>` is kept either way.

## dice-docs and the manifest

`devpro dice-docs <manifest.tsv> <src-dir> <work-dir>` dices several documents into one tree of
**volumes** that link to each other.

### Manifest

Tab-separated rows of `file`, `outdir`, `flags`, `label`; missing trailing fields are empty. Empty
lines and lines starting with `#` are skipped.

| Field | Meaning |
|---|---|
| `file` | Source file under `<src-dir>`. Other documents link to this volume by this text ([link targets](links.md#link-targets), step 3). |
| `outdir` | Output directory of the volume. |
| `flags` | Comma list, may be empty: `entry` (see below). |
| `label` | Title of a volume group (below). |

A row flagged `entry` is not diced: its file is copied verbatim to `<outdir>/entry-point.md`,
followed by a blank line, `Volumes:`, a blank line, and one line per volume whose `outdir` has
`<outdir>` as its parent directory, in manifest order:

```markdown
- [<volume dir name>](<volume dir name>/entry-point.md): <purpose>
```

`<purpose>` is the first sentence of the volume document's opening paragraph (the first paragraph
after its first `# ` line, joined into one line, as plain text
([what is a link](links.md#what-is-a-link)); the sentence ends at the first `. `, else the whole
paragraph). A manifest has at most one effective `entry` row (the last wins).

A volume whose `outdir` is `<parent>/<group>/<name>`, where `<parent>` is another volume's `outdir`,
belongs to a **group**. The group directory gets an `index.md` — `# <label>`, a blank line,
`Contents:`, a blank line, then `- [<document title>](<name>/entry-point.md)` for each of its
volumes in manifest order — and the parent volume's `entry-point.md` gains the line
`- [<label>](<group>/index.md)` after its Contents block. `<label>` is taken from the first volume
of the group; `<document title>` is the plain text of the heading text
([file names and layout](tree.md#file-names-and-layout)) of the volume document's first `# ` line.
Parents must precede their children in the manifest. Other nesting depths are unspecified.

### Effects

In order:

1. A manifest that is not a file exits 2 with `not a file: <manifest>`; a source directory that is
   not a directory exits 2 with `not a directory: <src-dir>`. `<work-dir>` is then created if
   absent.
2. Rows are read in order. A row whose source is absent ends the verb (stderr
   `missing source: <src-dir>/<file>`, exit 2). A row whose `flags` hold anything but `entry` ends
   the verb (stderr `unknown flag: <flag> in row for <file> (the only flag is entry)`, exit 2).
3. The link map is written ([the link map](links.md#the-link-map)).
4. Before dicing: the `entry` row's `<outdir>/entry-point.md` is removed (its directory is
   created), and each volume's output directory is removed with its contents unless it lies inside
   another volume's output directory.
5. Each volume is diced as by [dice-doc](#dice-doc) with the link map. Its output is preceded by
   `=== <file>` on stdout; its stderr is merged into stdout, and its `dead link:` lines are
   suppressed. A failed dicing does not stop the others; it surfaces in step 7.
6. Group indexes and the entry point are written ([manifest](#manifest)).
7. The [reassembly](checks.md#reassembly) and [link checks](checks.md#link-check) run on every
   volume with the link map — the dicing's own commit gate
   ([Dicing and Checks](../entry-point.md)), applied per volume.
8. A final check over the files written in step 6 prints
   `=== files written by this script: link targets exist`, then `  checked <file>` per file, and
   `  DEAD <file> -> <target>` for each link ([what is a link](links.md#what-is-a-link)) in the
   text ([link rewriting](links.md)) of those files whose target ends in `.md`, has no `#`, and
   names no existing file relative to the file's directory.

Exit 0 only if step 7 and step 8 pass; otherwise 1.
