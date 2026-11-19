### A harness resource's floor is behavioral

A harness resource that names a target version and a floor is read as stating its behavior holds from
the floor. Where the host changed a behavior the resource depends on inside that range, the resource
states the version that behavior holds from, and the floor covers only what the resource does there:
opencode's entry names 2.3.2 with floor 2.3.0 because its dispatch nudge holds from 2.3.0, where the
`subagent` call started returning at once.
