# Install stages from the wheel

Both staging paths — the package copy and the harness resource copy — read the running package's own
content, which once built is the wheel's: `.dist-info/RECORD` is the one manifest of what ships. The
built package is the one filter: a new copy source that stages from anything else ships what the
wheel never declared.
