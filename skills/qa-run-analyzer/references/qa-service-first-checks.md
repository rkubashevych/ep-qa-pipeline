# QA Service first — the analyzer's stage-3 checks (0.50.0)

Part of § 4 "QA Service sync" in `../SKILL.md`. Read
`<KEY>-qs-cases.md`, the export docs stage 3 writes
(`../../qa-pipeline-docs/references/qa-service-first.md`), and report:

- 🟡 **stage 3 did not run** while the connector was present and the
  user did not decline: no export file. Every case was written by the
  pipeline alone, and the feature's existing tests were not
  discovered.
- 🟡 **a QA Service case unaccounted for** — in the export, but
  neither `Adopted:` in the test-cases file nor listed under "QA
  Service cases not adopted". `reconcile_counts.py` does not check
  this; compare the stableIds.
- 🟡 **discovery did not finish** — the export's `Discovery:` line
  reports a timeout, a refused read, `truncated` or `scanned: 0`.
  Name the To do and the ledger row.
- 🟡 [Pipeline] **QA Service's test-design skill changed** — the
  `QA Service skills:` digest of `test-planning-and-design` differs
  from the one `../../qa-test-cases/references/test-levels.md` mirrors.
  Fix: re-read its "Level Assignment Rules", refresh the mirror, add a
  CHANGELOG entry.
- Report the split in the findings summary: adopted A · written here W
  · code-level K, and the level histogram of this ticket's cases. All
  cases at `M` / `E2E` with a pure rule among the requirements is a 🟡
  "no lower level considered".
