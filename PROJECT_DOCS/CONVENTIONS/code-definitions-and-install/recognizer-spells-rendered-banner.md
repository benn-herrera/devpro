# Recognizer spells rendered banner

The digest is the second recognizer, and the renderer is the spelling it reads. The rendered and
installed banners are the renderer's own constants, imported (`directives.is_installed`), and the
harness-rendered file it reads by the ownership markers `HARNESS_OWNERSHIP_MARKERS` holds in
`install_base.py`: each is the leading quoted field every `{plugin}`-bound form of a
`HarnessFile.marker` keeps, so one marker reads a file whole where the captured value differs. The
list stands there rather than beside the harnesses because the install's harness modules cannot be
loaded on the capture path. The opencode capture's TypeScript derives its list the same way, and the
byte-equality digest test is the pin for the two captures' agreement: it holds them to one digest over
the same project tree, and fails where their marker lists or their walks disagree over it.
The digest test plants literal banners, so it pins the two captures' agreement and not the renderer's
spelling.
