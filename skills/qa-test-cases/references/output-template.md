# <ISSUEKEY> - Test cases

Requirements: <path to the requirements file>
Notes: <carry forward any warning/unresolved-conflict note from the requirements file; omit the line if none>
Generated: <YYYY-MM-DD>

---

## Format rules (scan-friendly — read before generating)

Test cases are read by the code phase (each block becomes a QA Service
case), rendered card by card in the manual walk, and read by humans.
Optimise for all three: keep them **scannable top-to-bottom with short
lines**.

- **No wide tables.** Do NOT use the `| # | Step | Test data | Expected |`
  table layout — wide rows do not survive the mapping to a case's
  `detail.steps` or a chat card. Use the vertical block layout below.
- **Keep every line short** (aim <= ~64 characters). Wrap long steps or
  expected results onto the next indented line rather than one long row.
- **One step per line**, numbered. Inline short test data as
  `[data: ...]`; only break it onto its own line if it is long.
- **Steps are actions; results live in `Exp:`.** Put the expected
  outcome(s) under a single `Exp:` block at the end of the case. Only
  attach a per-step expected when a mid-flow check is essential.
- **Channel tags:** the requirement heading carries the union of its
  cases' tags (`## REQ-1 — State select filters leads  [UI]`); each
  test-case heading carries exactly ONE tag
  (`### TC-REQ-1.2 — Returning to the full list  [UI]`) — except
  provenance-sensitive cases (counter/analytics/lead/notification
  assertions), which carry the dual tag
  (`### TC-REQ-5.1 — Counter increments  [API][UI]`; SKILL.md Step 1).
  The per-case tag is what api-testing and web-testing route on.
- **Core marker:** the requirement's ONE core case additionally
  carries ` [core]` after its channel tag
  (`### TC-REQ-1.1 — Filtering by state  [UI] [core]`). Stage 9
  always walks core cases; routing ignores the marker.
- **Structural checks are lines, not cases** (since 0.40.0 — the
  former checklist file is gone). They sit in their own section after
  the last requirement group, one line each, id `REQ-N/struct-k`.

---

## Structure

```
## REQ-N — <requirement label>  [risk: <High|Medium|Low>] [<channel tag(s)>]

Applied techniques: <technique(s) — once per requirement group>

### TC-REQ-N.M — <scenario name>  [<channel tag>]

Pre: <precondition>
Steps:
1. <action> [data: <value, or a realistic example marked [test data]>]
2. <action>
Exp:
- <concrete expected result — no "correctly"/"properly">
- <concrete expected result>
Post: <postcondition — only if the system state changes; omit otherwise>
```

Repeat `### TC-REQ-N.M` blocks per test case and `## REQ-N` groups per
requirement, in the same order as the requirements file. A structural
requirement (only presence / label / type / default checks) has no
group — its lines are in the section below.

```
## Structural checks  [UI]

> Presence / label / type / default-state checks — no scenario needed,
> no test case by design. Each line becomes one `<PREFIX>-STRUCT-NN`
> case at publish; `REQ-N/struct-k` is its `detail.pipelineId`. Not
> counted in the test-case total.

- [ ] REQ-N/struct-1 [UI] <element + the property it must have>
- [ ] REQ-N/struct-2 [UI] <…>
- [ ] REQ-M/struct-1 [UI] <…>
```

Lines are grouped by requirement in requirement order; `k` counts
from 1 under each REQ. After the publish, the code phase rebuilds each
line with its suite id: `- [ ] REQ-N/struct-1 · <PREFIX>-STRUCT-01 [UI] <…>`.
Omit the whole section only when the ticket has no structural check.

---

## Statistics

Close the file with:

- Requirements covered: <N> (<REQ-1, REQ-2, ...>)
- Requirements needing clarification: <N>
- Channel breakdown: [UI] <N> · [API] <N> · [API][UI] <N> (dual-tagged,
  counted once, here) · [mobile] <N> · [export/email] <N>
- Core cases: <N> (= behavioural requirements)
- Structural checks: <S> (not in the total)
- Total number of test cases: <N>

Every number is re-derivable with
`python3 ../qa-run-analyzer/scripts/reconcile_counts.py <ISSUEKEY>`
(it prints the id count, the tag histogram, the core count and the
structural-line count for this file).
