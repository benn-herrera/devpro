### A formatted time test pins the locale

A test asserting a formatted time or date pins the locale beside the time zone: a runner's ICU
settings decide locale-aware formatting as the `TZ` setting decides the zone, so a pin holding
the zone alone passes under whatever locale the runner carries. The pin is hostile to the locale:
the expected text is built from the date's own fields, reading the same under any locale, and the
runner's ICU settings are set hostile in the test's own setup, so the shape the assertion holds
is the code's, not the runner's settings'.
