### The gates

```
checkpoint gate: `just test`, then `just sweep-python` (A checkpoint includes the sweep)
step-down application: the dispatch's `model` parameter
```

`just test-changed [base]` is a target a package's done-line may name. It runs only the test surfaces the change touches (the mapping lives in the justfile's
`TEST_SURFACE_MAP`; a change to `PROJECT_DOCS/`, `images/` or a top-level `*.md` selects the `docs`
surface, the link and tree check). Cross-surface coupling is removed, not paid for by running
unrelated surfaces.

`check-wheel` compares the wheel's package data with `git ls-files --cached --others --exclude-standard`
(`devtools/scripts/check-wheel.sh:29-33`), so a package-data deletion cannot pass the wheel surface
before it is staged — a tree whose package-data change is unstaged fails it, with the deletion on
the index still expected and absent from the wheel.
