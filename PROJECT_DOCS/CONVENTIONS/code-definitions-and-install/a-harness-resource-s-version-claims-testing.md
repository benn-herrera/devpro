# A harness resource's version claims testing

A version this project's harness resources name states what the resource has been tried with most,
or observed working from: a testing claim, not a compatibility promise. Versions below or above may
work, unverified; a resource's version line says so in one phrase, "your mileage may vary". No other
sentence in it turns the version into a guarantee, least of all for behavior the host owns.

The numeral a resource names is a floor only where its own line records the observation earning it,
and names no version of the moment: the host declarations' version has one home, `package.json`'s pin
(Recipes). Where a resource depends on a host behavior, its line notes where that behavior was
observed working from: `profiler.ts`'s floor is 2.3.0, where the `subagent` call is named `task` in
the tool table, and the child's session id it reads at `result.metadata.sessionID` — the other two
reads, `result.output.sessionID` and `result.sessionID`, are 2.3.2's and 2.4.1's.
