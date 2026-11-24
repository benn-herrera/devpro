# Post-plan review

The reviewers: the python-coder, typescript-coder, architect, tech-writer and prompt-engineer
seats, each writing independently to the scratch directory, synthesized here. The changes
reviewed: `385e03d..HEAD` — the plan's four landed packages and the session's corrections among
them. Every seat ran the gates; the suite is green at 1669 passed with the `cold_read` suite
excluded. Findings are one entry per defect, naming every seat that reported it; the burndown
groups them by root cause.

## Findings

### 1. The model-pin remedy is premised on a refuted claim, and its pin vouches by mock

Seats: typescript-coder (B1, F1–F4, N2), architect (W2), session (the host source and
declarations, read in this session's model-pin thread).

The change delivered the model through `experimental.model.resolve` and removed the transform's
model write, premised on "the runtime reads an agent's model from its own store, not from the
agent the transform edits." Three pieces of evidence refute the premise:

- The declarations: `AgentEditor.update` takes `Agent.Info`, whose `model: Model.Ref` is mutable —
  the transform's model write is the sanctioned path. The host's own config loader writes the
  model as the object (`packages/core/src/config/plugin/agent.ts:85`) through the identical
  mechanism, and the host's builtin agent plugin registers through `editor.update` too.
- The hook's documented scope: "another model from the same provider" — devpro's pins are
  cross-provider, outside it. The host source shows the runner reads the agent's model from the
  agent store before the hook fires (`session/runner/model.ts:100`), and a hook change to another
  provider does not resolve — the request errors (`ModelUnavailableError`).
- The pin passes because `opencode_entry_runner.ts` builds the resolve event from a private
  `selections` map no plugin reaches — the first case of the mock sentence `TESTS_PROTECT_LOGIC`
  gained in the same landing; its `ses_unconfigured` differential passes with the hook deleted.

Consequences carried with it: `opencode-entry.md`'s Registration bullet still lists `model` among
what the transform writes, which the code no longer does — the design's "the leaf stays as it
stands" ruling does not hold; the API bullet undercounts the session events; the resources header
and the floor claim now cover an *Experimental* hook with no 2.2.6 evidence; the hook fires for
all four `SessionRequestKind`s, so compaction and title requests take the configured model; the
unconfigured differential is a form pin; and `built()`'s comment misdescribes what `reloaded()`
compares.

**Remedy both seats point at**: restore the transform's plain object write, remove the resolve
hook, return the pin to store-level (driver-class — the stub is fuel for what the transform
writes), and the leaf stays true again. The unanswered historical question — why the pin ever
looked broken — is settled by one live 2.4.1 dispatch on a cross-provider configured model,
observed through the host's own request surface: the check the design should have required
before the removal landed.

### 2. The opencode capture's record contract has no automated check, and its evidence is homeless

Seats: architect (Critical 1).

The capture's stand-in runner and its test were removed under the mock boundary — but the deleted
test drove the shipped `profiler.ts`'s event-record construction over synthesized host-shape
*inputs* and asserted the capture's *own* outputs: the child-id read order across the three host
shapes, the non-string guard's fall-through, the failed call's message, the idle record. That is
the driver class the boundary protects — the mock got execution to the piece under test and
vouched for nothing the host reports; the host-shape facts kept their home in the
harness-profiler leaf. ARCHITECTURE states each as a fact of the code; none is checked anywhere
now. The stated replacement — a live opencode host dispatch — exists nowhere, and the roadmap
paragraph naming it as the capture's evidence was deleted in the same range.

**Remedy**: restore a contract runner over the three host-shape inputs asserting the capture's
own outputs, the boundary stated in its docstring; re-record the live-dispatch evidence as a
roadmap ticket.

### 3. The serialize measurement's input is a frozen fixture nothing derives

Seats: architect (W3).

`tests/fixtures/profiler_serialize_record.json` is a hand-frozen copy of one dispatch record; the
deleted code ran the capture runner first so the record's fields were the capture's own. If the
record gains, renames or drops a field, the fixture silently keeps the old shape while the test
docstring still claims the field set is the record's own. **Remedy**: pin the fixture's key set
against the capture's own record construction — the field set is the form that is the contract —
or record the fixture's provenance and scope the docstring.

### 4. The scratch sentence has two hand-edited homes

Seats: python-coder (W1), architect (N7), prompt-engineer (F1).

`devpro/harness.py:130–137` and `devpro/harnesses/mage.py:41–44` carry the same scratch paragraph
as inline text, edited in lockstep this landing, equal only by care, checked by nothing. The
double-delivery gate misses it because `scratch_rule` renders into the agents file, not a
definition body. `harness.py`'s `harness_dir` parameter is dead and its docstring asserts a
"beside" claim the body never makes. **Remedy**: one constant beside `clauses.PROJECT_TEMP_DIR`,
filled by both sites.

### 5. SPEC over-claims the scratch guarantee's scope

Seats: prompt-engineer (F2).

The landed SPEC (`installed-tree.md:44`) and the ARCHITECTURE passage say *a project install*
creates the scratch directory and adds the `.gitignore` line; the code and its own tests deliver
it only for claude/opencode nested-plugin project installs, and
`test_a_mage_install_prepares_no_scratch_directory` pins mage and user-level installs to neither.
SPEC asserts a guarantee undelivered for two of three harnesses. **Remedy**: the leaf states the
condition the delivery carries.

### 6. The README's changed sections are not finished

Seats: tech-writer (W1, W2, N1, plus the dry-run note).

The `.gitignore` example block dropped `.devpro-temp/` from the sample — a reader copying the
block no longer sees the finished state, and a hand-written `.devpro-temp` (no slash) yields a
duplicate; nothing marks the scratch line as the install's. "Reads the project's two stores" is
misleading for a single-harness project and omits that a store by any other name is not read —
verified lookalikes are skipped. "One per tool call" undercounts the opencode store's idle
records (predates this range). The preflight's `--dry-run` names `.gitignore` under `created:`
but not the directory it would also create, under-reporting the preparation the README's Updating
section tells readers to preview. **Remedy**: the block carries the line and its ownership; the
profiler wording names the condition; the dry-run prediction includes the directory.

### 7. Stale "glob" wording survives in the documents and docstrings

Seats: architect (N5), prompt-engineer (F5), session (the two earlier correction commits were
partial).

`harness-profiler.md:100–101` ("how many stores the glob found", "a store the glob finds but
cannot read") and `:238` (the store set stated twice — literal list and the exact-name sentence);
`devpro/profiler/pages.py:815`, `:823`, the INDEX template's comment at `:1006`. **Remedy**: the
sentences name the exact-name read; the literal list drops.

### 8. `runner_file.py`'s identity lags its duties

Seats: python-coder (N2), architect (N8), prompt-engineer (off-seat).

`subsystem-map.md` names it "writes the runner include lines"; the module now also creates the
scratch directory and writes the `.gitignore`, and its name covers three duties. **Remedy**: the
map's sentence names the third job, or the function moves to `install.py` with its imports.

### 9. Small mechanical debt from the packages

Seats: python-coder (N3–N7), architect (N4, N6), prompt-engineer (F4).

- The CRLF path re-implements `appended_paragraph`'s rule — one ending-aware helper.
- `runner_file.py:64`'s `rstrip()` is broader than "carrying the line" — errs toward touching
  nothing, traded without a note.
- The one-function `fixture_file` accessor wraps a single call.
- The dashboard's traces-feed case lost its readable claude session beside the locked store —
  the "loses no other store's session" claim is checked through opencode alone.
- The retracted glob survives as a negative pin (`assert "*" not in line`) — burndown candidate
  under *obviated code is deleted*.
- The entry runner's `requests` store is always `{}` — a key that reads as meaningful and can
  never vary; fill it from the resolved outcome or drop it.
- Two docstrings cross-reference tests the stand-ins' removal deleted.

### 10. The double-delivery ticket is live in nine coder definitions

Seats: prompt-engineer (F3).

`NEW_PROJECT_SETUP`'s dropped mandate left a restated scratch sentence — location and examples —
in nine coder definitions, one paragraph from the agents-file block that delivers it. The
roadmap's sentence-duplication ticket named this class; it now has a live instance. **Remedy**:
fold into that ticket's next pass.

### 11. Two clause and doctrine questions for the owner

Seats: typescript-coder (contract gap), prompt-engineer (voice), architect (boundary framing).

- A candidate `TESTS_PROTECT_LOGIC` sentence: *a claim about a host's runtime behavior is
  verified against the host or stated as a gap, never certified by the stand-in that models it.*
- The mock sentence restates an existing `TEST_REVIEW` bullet — provenance rather than more text.
- `ACTIVE_DESIGN.md`'s own claim that the opencode stub "vouches for nothing" is wrong by the
  same boundary — the design text and the clause it lands beside disagree.

## Strengths the seats verified

Store exactness holds in both readers and the doctor's line, pinned with the copy case and a
negative on the `*`; the scratch preparation matches its leaf byte for byte through the preflight,
gated on the nested-plugin project-install predicate, mage and user-level tested touching
nothing; the clauses and the README carry the deltas' wording consistently; the pages' deferred
verification is stated as a gap with a dated roadmap home.
