# A repository-wide check runs a real-tree case

A repository-wide check's own case set includes one run over the real tree it polices; a fixture-only
case leaves the check unexercised on its inputs. A check that passes against fixtures alone proves
the fixtures, not the check over the trees it will actually read.

The recipe's own run is not that case: a check the recipe hands this repository's tree to passes or
fails in a target nobody counts as a test, and its fixture cases say only what the fixtures hold. The
case is a test that hands the check the repository it ships in — the checkout's `PROJECT_DOCS` or
`devpro/` tree — and passes where that tree does.
