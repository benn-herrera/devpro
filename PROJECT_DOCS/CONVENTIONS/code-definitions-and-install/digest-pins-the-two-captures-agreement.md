# Digest pins the two captures' agreement

The opencode capture's TypeScript derives its list the same way, and the byte-equality digest test
is the pin for the two captures' agreement: it holds them to one digest over the same project tree,
and fails where their marker lists or their walks disagree over it. The digest test plants literal
banners, so it pins the two captures' agreement and not the renderer's spelling.
