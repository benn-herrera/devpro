# Recognizer spells rendered banner

The install's recognizer spells the banner the renderer writes. `install.py` builds its
generated-file prefixes from `render.GENERATED_MARK`, and the package the banner's module path opens
with from `PACKAGE_ROOT.name` (`_PAYLOAD_PATH`), so what recognizes a rendered definition reads
the spelling the renderer writes. A test that plants a literal `!GENERATED!` banner does not hold
that binding — a change on either side passes it — so the case plants a rendered definition. A
harness-rendered file carries no banner: its `HarnessFile.marker` is what reads it as ours, and the
test plants a harness-rendered file the renderer wrote rather than a literal marker, for the same
reason.

The digest is the second recognizer, and the renderer is the spelling it reads. The rendered and
installed banners are the renderer's own constants, imported (`directives.is_installed`), and the
harness-rendered file it reads by the ownership markers `HARNESS_OWNERSHIP_MARKERS` holds in
`install_base.py`: each is the leading quoted field every `{plugin}`-bound form of a
`HarnessFile.marker` keeps, so one marker reads a file whole where the captured value differs. The
list stands there rather than beside the harnesses because the install's harness modules cannot be
loaded on the capture path. The opencode capture's TypeScript derives its list the same way, and the
byte-equality digest test is the pin: it holds the two captures to one digest over the same project
tree, so a marker whose spelling changes on either side fails it.
