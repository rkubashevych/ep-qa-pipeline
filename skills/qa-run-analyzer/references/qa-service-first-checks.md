# QA Service first — the analyzer's stage-3 and publish-completeness checks (0.50.0, 0.50.1)

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
- 🟡 **requirements not in a folder** (0.50.1) — a requirement of this
  ticket with no `folderPath` in `get_suite`. Fix with
  `group_requirements` (`scope: "unfiled"`).
- **QA Service review** (0.50.1) — one `register_review_status`:
  - 🟡 **review never started** — none of this ticket's entries has a
    review verdict, and no job is running. Fix: `start_register_review`
    with this ticket's stableIds.
  - 🟡 **failing review** — each failing requirement or case, with the
    reviewer's finding verbatim. It must be on the ledger or a To do;
    absent from both is a 🔴 [Pipeline] (a finding silently dropped).
  - 🔴 **override approval** — an entry of this ticket approved with
    `approvedVia: override`. The pipeline never calls
    `approve_register_entry`; name who did.
- **Sign-off and source watch** (0.54.0):
  - 🟡 **sign-off not checked** — a stage-10 summary with no `QA Service
    sign-off:` footer line while the connector was present;
  - 🟡 **a ticket blocker missing from the summary** — a `feature_signoff`
    blocker on this ticket's cases that is neither a Bug, a To do nor a
    Question;
  - 🟡 **source-watch notice not carried** — an open `stale_quote` /
    `new_material` notice on this ticket's requirements that is not in
    `<KEY>-sources.md` or the ledger.
- **API cases checked against the code** (0.56.0):
  - 🟡 **no claim review** — `<KEY>-api-tests.md` exists but no
    `<KEY>-claim-review.json`: the API cases were linked or implemented
    without being checked against the code (MEXP V2, 2026-10-14);
  - 🔴 **spec-backed case "corrected" to the code** — an
    `edit_test_case` / `edit_requirement` correction on a case or
    requirement whose `sources` carry a Jira / Confluence quote. That
    hides a possible defect; it should have been a ledger row and a bug
    offer.
- Report the split in the findings summary: adopted A · written here W
  · code-level K, and the level histogram of this ticket's cases. All
  cases at `M` / `E2E` with a pure rule among the requirements is a 🟡
  "no lower level considered".
