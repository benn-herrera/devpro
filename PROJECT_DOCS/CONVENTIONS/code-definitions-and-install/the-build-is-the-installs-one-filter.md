# The build is the install's one filter

The wheel's content is what a consumer install writes, and the build is the one filter over it: a
new copy source that stages from anything else ships what the wheel never carried. So both staging
paths — the package copy and the harness resource copy — take a tree laid out as the wheel lays it
out (`.dist-info/RECORD` that content's manifest), and `just check-wheel` holds the build to it. An
install run from a checkout (`PYTHONPATH=<clone>`) has no build under it and stages the clone's tree
as it stands; the bytecode skip is the one filter both paths share.
