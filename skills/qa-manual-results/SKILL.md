---
name: qa-manual-results
description: >
  Stage 10 of task processing — the return leg of the manual run. Takes
  the completed run sheet (the Result/Notes columns the human tester
  filled in) and/or a triage file, joins the verdicts to test cases BY
  TC ID (never by row position), reconciles them against the published
  automated verdicts, and writes the outcome back to Jira and the QA
  Service suite — including explicit RETRACTIONS where the human result
  overturns a published PASS/FAIL. Use when the user says "ingest the
  manual results", "the tester finished the run sheet", "read the
  completed runsheet", "write back the manual results", "process the
  test results", or uploads/pastes a filled run sheet or TC/Result/Notes
  table.
---

# QA Manual Results

The pipeline publishes automated verdicts at code-phase step 6 — before
the human walks the run sheet. This stage exists so what the human
found actually reaches the record. Without it, the truest verdicts of
the run live in a spreadsheet nothing reads, and the system of record
keeps asserting PASSes everyone knows are wrong.

## Input

1. **The completed results — any of these forms:**
   - `<ISSUEKEY>-runsheet.xlsx` with the Result column (K) filled
     (values from its dropdown: PASS / FAIL / BLOCKED / SKIPPED) and
     the Notes column;
   - an exported/pasted TSV or CSV with columns `TC`, `Result`,
     `Notes` (this is what testers actually hand over — accept it);
   - a triage file (`<ISSUEKEY>-remaining-cases-triage.md`) when one
     was produced.
2. **The story / QA sub-task key** — ask if not derivable.
3. Optional, for reconciliation: this run's verdict files
   (`<ISSUEKEY>-code-review.md`, `-api-testing.md`, `-web-testing.md`)
   or, in a fresh chat, the archive comment on the QA sub-task
   (extract per `../qa-pipeline-code/references/results-comment-template.md`).
4. Optional: the QA Service suite (connector present) — the write-back
   target.

If no Result data is provided at all — ask for the completed sheet or
table; do not proceed on guesses.

## Hard rules

- **Join on the TC id column, never on row position.** Sheets get
  sorted, filtered, and re-generated; position is meaningless. A row
  whose TC id does not match any known case goes to the report's
  "Unmatched rows" section — never silently dropped, never guessed.
- Empty Result = not run. Report it as such; it is not SKIPPED and not
  PASS.
- Normalize statuses case-insensitively to PASS / FAIL / BLOCKED /
  SKIPPED; anything else (e.g. "N/A — spec premise false") is recorded
  verbatim under "Non-standard verdicts" for a human decision, not
  coerced.
- Extract bug keys (`EP-\d+`) and evidence links (jam.dev etc.) from
  Notes and attach them to the case's entry.
- Read-only toward the product: this stage never touches the tested
  system — only Jira, the suite, and its own report file.

## Workflow

### Step 1 — Parse and join

Read the results source(s). Build one entry per TC id: Result, Notes,
bug keys, evidence links. When both a runsheet and a triage file exist
and disagree on a case, the LATER source wins and the disagreement is
listed under "Conflicts (resolved by recency)".

### Step 2 — Reconcile against the published record

For each case with a manual Result, fetch what the record currently
says: the automated verdict (from the verdict files or archive
comment) and, when the connector is present, the suite case's current
notes (`get_test_case`).

Classify each case:
- **CONFIRMS** — manual result agrees with the published verdict.
- **FILLS** — case had no automated verdict (QA/routed/not executed);
  the manual result is the first real verdict.
- **RETRACTS** — manual result contradicts a published verdict
  (e.g. published PASS, human found FAIL). These are the most
  important rows of this stage. Never soften them.

### Step 3 — Report

Write `<ISSUEKEY>-manual-results.md` per
`references/output-template.md`: counts, the RETRACTS list first, then
FILLS, CONFIRMS, non-standard verdicts, unmatched rows, not-run cases,
and the bug-key table.

### Step 4 — Write back (REQUIRED PAUSE / CONFIRM)

Show the user exactly what will be written, then on explicit yes:

- **QA Service suite** (connector present): for every case with a
  manual Result, append to the case notes per the retraction
  convention in
  `../qa-pipeline-docs/references/qa-service-publish.md` → "Result
  write-back": a normal run line for CONFIRMS/FILLS
  (`Run <date> (<STORY> manual): PASS|FAIL — <reason>; bug <KEY>`),
  and for RETRACTS additionally the supersede form
  (`Run <date> — SUPERSEDES <prior> (<old> → <new>): <reason>`) plus
  the single `⚠ CURRENT VERDICT:` first line. Never change lifecycle
  `status`.
- **Jira QA sub-task**: post TWO comments, same convention as
  code-phase step 6 — a machine archive (the full
  `<ISSUEKEY>-manual-results.md` in a fenced block preceded by
  `File: <ISSUEKEY>-manual-results.md`) and a human summary (≤25
  lines: verdict counts, **Retractions listed first with old → new
  and reason**, bugs filed/linked, what remains untested). If a prior
  human summary is now wrong, the new summary's first line says so
  plainly ("supersedes the 2026-07-28 summary for N cases").
- Connector absent → suite write-back is skipped with a visible note;
  the Jira comments still carry everything.

### Step 4b — The deferred handback (this stage owns it)

The code phase deliberately does NOT post the final "QA passed" story
note or apply the "QA done" transition — automated verdicts are
provisional until this stage runs. Now that the manual results are in:

- Overall verdict still ✅ PASS after ingestion (no unresolved RETRACTS
  to FAIL, no new FAILs): offer the "Story note — QA passed" to the
  PARENT story (template:
  `../qa-pipeline-code/references/results-comment-template.md`) and
  the "QA done" transition from publish-config, exactly as step 8
  would have — same confirm rules.
- Verdict flipped to ❌ (retractions/new FAILs): offer the reassign +
  "Story note — QA failed" path from `qa-pipeline-code` step 8
  instead, and make sure any earlier provisional story note is
  superseded by a comment stating the corrected outcome.

### Step 5 — Offer to file unfiled bugs

Any FAIL whose Notes carry no bug key: one offer listing them all —
via the `/knowledge-base` skill when installed, else per
`../qa-pipeline-code/references/bug-report-template.md` with duplicate
search first. File only what the user confirms.

## Final response

Report: the report path; counts (CONFIRMS / FILLS / RETRACTS /
non-standard / unmatched / not run); every RETRACTION on its own line
(case, old → new, reason); bugs linked and bugs filed; whether the
suite write-back happened; and what is still untested.
