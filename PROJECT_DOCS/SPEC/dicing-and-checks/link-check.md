# Link check

Every link in the text ([link rewriting](index.md#dicing-and-checks)) of every file
[file names and layout](index.md#dicing-and-checks) assigns, taken without its `#fragment`, must
name a readable file relative to that file's directory. Skipped: empty targets (bare `#frag`),
targets opening with `/`, and targets with a URL scheme
([link targets](index.md#dicing-and-checks), step 2). Everything else is probed relative to the file and
so is dead unless it exists there; a directory is dead. An assigned file that cannot be read
contributes no links ([reassembly](reassembly.md#reassembly) reports it). Each dead link prints
`dead link: <file>:<line> -> <target>` to the error stream; the summary
`links checked: <N>, dead: <D>` goes to the output stream.
