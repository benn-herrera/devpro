# The repair

`devpro profiler repair`, run once from the project's root, reads each standing
opencode subagent record's result text and fills its `child_agent_id` where the host reported it — a
record whose id is already right stays untouched, so a second run fills nothing, and every edge a
capture writes after the update is correct at write time. It prints `repaired: <n> edges; null: <m>
records (no child id)` — the edges it filled and the subagent records left naming no child, among them
a dispatch that failed before creating one, a result clipped before the id survived, and each record
of a file left as it stands — and a file a capture appends to while the repair reads it is named on
stderr and left as it stands, never rewritten under a session's own write.
