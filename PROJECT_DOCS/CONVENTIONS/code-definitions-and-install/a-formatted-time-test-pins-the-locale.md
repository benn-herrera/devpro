# A formatted time test pins the locale

A test asserting a formatted time or date pins the reader's zone with `TZ`: the zone decides
which day and clock a date draws into, so a pin holding no zone asserts on whatever the runner
carries. The locale is not holdable under the embedded bun, which ignores the locale environment
— `LC_ALL=de_DE.UTF-8 bun` still resolves `en-US` — so the pin holds the locale by construction
instead: the expected text is built from the date's own fields, reading the same under any locale
the runner carries.
