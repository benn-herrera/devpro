# A hook contract is read, not assumed

An event's accepted output fields, and where its context lands, are the harness's statement in its
hook reference, never an inference from where the hook fires: a field accepted on one event is
ignored on another, and context lands where the reference says — at the next model request of the
session it names, not at the call that fired the hook. Read the reference for each event before
wiring one, and hold the code to what it says: no test here can, because the stub is not the host.

The stub is the narrower pin: `tests/opencode_plugin_stub.ts` replaces only the `@opencode/plugin`
module's `Plugin.define`, a pass-through, and each runner hands the plugin a context it declares
itself. What that stub holds is that the entry loads without the host's module; what holds the
contexts' shapes is the runners, which declare each field they hand the plugin rather than reading
it from the host, and so state the surfaces the code expects — `ctx.location.project.directory`,
`ctx.tool.hook` and `ctx.session.hook` among them — without vouching that the host reports any of
them. A field the host gains or drops is the host reference's to say; a change to what the code
reads is a change to the runners' declared contexts, in that change.
