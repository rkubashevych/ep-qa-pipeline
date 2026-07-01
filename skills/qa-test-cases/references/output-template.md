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
- **Channel tags go on the requirement heading**, not each line, e.g