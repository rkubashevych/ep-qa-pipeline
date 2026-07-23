# <ISSUEKEY> - Test cases

Checklist: <path to the checklist file>
Notes: <carry forward any warning/unresolved-conflict note from the checklist file; omit the line if none>
Generated: <YYYY-MM-DD>

---

## Format rules (Jira-friendly — read before generating)

Test cases are read by humans in a Jira comment and by the code phase.
Optimise for both: keep them **scannable top-to-bottom with short lines**.

- **No wide tables.** Do NOT use the `| # | Step | Test data | Expected |`
  table layout — wide rows force painful horizontal scrolling inside
  Jira code blocks. Use the vertical block layout shown below.
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
  (`### TC-REQ-1.2 — Returning to the full list  [UI]`). The per-case
  tag is what api-testing and web-testing route on.

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
requirement, in the same order as the checklist file.

---

## Statistics

Close the file with:

- Requirements covered: <N> (<REQ-1, REQ-2, ...>)
- Requirements needing clarification: <N>
- Channel breakdown: [UI] <N> · [API] <N> · [mobile] <N> ·
  [export/email] <N>
- Total number of test cases: <N>