---
name: qa-manual-results
description: >
  Stage 10 of task processing — the write-back half of the manual
  round. Takes the walk results written by qa-manual-walk, or a
  completed run sheet (the Result/Notes columns a tester filled in),
  or a triage file; joins the verdicts to test cases BY TC ID (never by
  row position), reconciles them against the published automated
  verdicts, and writes the outcome back to Jira and the QA Service
  suite — including explicit RETRACTIONS where the human result
  overturns a published PASS/FAIL. Invoked automatically at the end of
  a walk; use it directly when the user says "ingest the manual
  results", "the tester finished the run sheet", "read the completed
  runsheet", "write back the manual results", "process the test
  results", or uploads/pastes a filled run sheet or TC/Result/Notes
  table. Do NOT use to run the session itself (qa-manual-walk), or to
  answer "what were the results?" — that is read from the report.
---

# QA Manual Results

> **Tool names:** `addCommentToJiraIssue` etc. are tools of the
> **Atlassian MCP connector**; `get_test_run` / `record_case_result` /
> `reopen_test_run` / `close_test_run` / `suggest_test_case` belong to
> the **QA Service MCP connector** (install-specific server prefix
> varies — match by tool name).

The per-case record this stage writes into is the QA Service **test
run** step 6 opened for this pass — rules, verdict mapping and the
retraction target rule: `../qa-pipeline/references/test-runs.md`. The
cross-round memory it closes rows in:
`../qa-pipeline/references/open-items-ledger.md`.

The pipeline publishes automated verdicts at code-phase step 6 — before
the human walks the run sheet. This stage exists so what the human
found actually reaches the record. Without it, the truest verdicts of
the run live in a spreadsheet nothing reads, and the system of record
keeps asserting PASSes everyone knows are wrong.

## Input

1. **The completed results — any of these forms:**
   - `<ISSUEKEY>-walk-results.md` written by `qa-manual-walk`
     (`../qa-manual-walk/references/walk-results-format.md`) — the
     usual form since 0.31.0. It carries, per case, the verdict, the
     tester's words verbatim, evidence, the card kind and the
     `source` (`manual`, or `machine (witnessed)` for cards the agent
     executed), plus `Case corrections`, `Blocked reasons` and
     `Observations` sections. **Check its `Run:` line names the run you
     are about to write to** — a results file from an earlier round
     beside this round's reports is the stale-artefact trap EP-56197
     r4 recorded (open-items #24); on mismatch stop and ask;
   - `<ISSUEKEY>-runsheet.xlsx` with the Result column (K) filled
     (values from its dropdown: PASS / FAIL / BLOCKED / SKIPPED) and
     the Notes column;
   - an exported/pasted TSV or CSV with columns `TC`, `Result`,
     `Notes` (this is what testers actually hand over — accept it);
   - a triage file (`<ISSUEKEY>-remaining-cases-triage.md`) when one
     was produced;
   - **a one-line verdict from the user** ("the fix works", bug-fix
     mode) — treated as a TC / Result / Notes row per mini case,
     `source: manual`, principal = the user; anything less than a clear
     PASS / FAIL per case is asked about, never inferred.
2. **The story / QA sub-task key** — ask if not derivable.
3. Optional, for reconciliation: this run's verdict files
   (`<ISSUEKEY>-code-review.md`, `-api-testing.md`, `-web-testing.md`)
   from the run folder (`runs/<ISSUEKEY>/r<N>/`). **They exist only
   there** (no archive is posted since 0.33.0) — on another machine
   they will be missing: the QA Service run still gives every machine
   verdict (`get_test_run`), so reconcile against the run and say the
   report prose is unavailable, rather than reconciling against
   nothing. Pre-0.33 tickets may carry legacy archive comments.
4. Optional: the QA Service suite (connector present) — the write-back
   target.

If no Result data is provided at all — ask for the completed sheet or
table; do not proceed on guesses.

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
(run folder first — a new chat is not a reason to ask for an
upload; then the suite; asking the user is the last resort, not the
first — Jira archive comments are legacy, read only on pre-0.33 tickets).

## Hard rules

- **Join on the TC id column, never on row position.** Sheets get
  sorted, filtered, and re-generated; position is meaningless. A row
  whose TC id does not match any known case goes to the report's
  "Unmatched rows" section — never silently dropped, never guessed.
- **Expand `Covers` lists.** A row carrying `Covers: TC-x, TC-y` applies
  its Result to every listed case, unless the tester's Notes single a
  case out — then the note's verdict wins for that case. Cases the
  plan settled without a card (its Coverage section; an exported
  sheet's Reference tab) are recorded as machine-only, never as
  human-confirmed.
- Empty Result = not run. Report it as such; it is not SKIPPED and not
  PASS.
- **Honour the `source` column of a walk-results file.** A row marked
  `machine (witnessed)` was executed by the agent during the walk with
  the tester watching: record it with `source: machine` and the
  principal `ep-qa-pipeline agent (<KEY> walk, witnessed by <tester>)`,
  and count it in the summary as machine-in-walk, never as
  human-confirmed. Only `manual` rows carry the tester's e-mail. (The
  0.30.0 rule against mislabelling the source cuts both ways.)
- **A `Half` row is half a verdict.** The human PASS covers the
  visible half; the note names the machine verdict the rest rests on.
  Record the human verdict with that note; the summary's PARTIALLY
  VERIFIED wording covers it.
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
bug keys, evidence links, source. When both a runsheet and a triage file exist
and disagree on a case, the LATER source wins and the disagreement is
listed under "Conflicts (resolved by recency)". A walk-results file
marked `Completeness: stopped early` is a partial round: say so, list
its `Not run` cases as not run, and ask whether to write back now or
wait for the walk to resume — never record half a round as the round.
`complete (N cards declared not run)` is a finished round: write it
back without asking; the declared cards stay `not_run` and are named
in the summary's "not tested" line. Keep `<ISSUEKEY>-walk-state.json`
beside the results file — it is the session's audit trail (every
earlier answer in `history`); never delete it.

### Step 2 — Reconcile against the published record

For each case with a manual Result, fetch what the record currently
says: connector present → the pass's QA Service run (`list_test_runs`
on the suite, title `<KEY> …`; then `get_test_run` — each roster row's
current verdict, principal and note; `case_execution_history` for a
case with a longer past). The stage reports are the fallback record when
there is no run (connector absent, or a bug-fix run with no suite).

Classify each case:
- **CONFIRMS** — manual result agrees with the published verdict.
- **FILLS** — case had no automated verdict (a `not_run` roster row —
  QA / routed / not executed / a machine FAIL or PARTIAL awaiting the
  human); the manual result is the first real verdict.
- **RETRACTS** — manual result contradicts a published verdict
  (e.g. published PASS, human found FAIL). These are the most
  important rows of this stage. Never soften them. For each, record
  **where the old verdict was published** — the run id, and the Jira
  ticket + comment id if it reached a comment (the retest-scope file
  carries this; otherwise find it) — because the retraction comment
  goes there (`test-runs.md` → "Retraction target rule").

### Step 3 — Report

Write `<ISSUEKEY>-manual-results.md` per
`references/output-template.md`: counts, the RETRACTS list first, then
FILLS, CONFIRMS, non-standard verdicts, unmatched rows, not-run cases,
and the bug-key table.

### Step 4 — Write back (REQUIRED PAUSE / CONFIRM)

**Run the publication gate on the drafted summary first**
(`../qa-pipeline/references/sources-of-record.md` § 7). This comment is
the first and often only thing a human reads, so it is the highest-stakes
compression in the pipeline: every line presented as a defect carries its
register row and its verbatim clause, a line with no clause is labelled
`OBSERVATION (no source checked)` and phrased as a question or cut, an
observation the stage reports labelled correctly does not reappear as a
defect (nor as a row in a failure table, nor under a column implying a
requirement), and a defect owned by another ticket names that key on its
line. Retractions are held to the same standard: state what the record
said, what was measured, and the clause the new verdict rests on.

Show the user exactly what will be written — including **every `fail`
about to be recorded, case by case**, because recording a `fail` on the
run files one deduplicated Jira defect for that case (`test-runs.md`);
that list is the per-bug yes — then on explicit yes:

- **QA Service run** (connector present): for every case with a
  Result, `record_case_result` on the pass's run — **`source` and
  `principal` follow the row**: a `manual` row → `source: manual`,
  `principal` = the tester's e-mail (never the agent label); a
  `machine (witnessed)` row (an AGENT-RUNS card) → `source: machine`,
  `principal` = `ep-qa-pipeline agent (<KEY> walk, witnessed by
  <tester>)`. The note = the tester's Notes verbatim, plus
  ` · Half: rests on <machine verdict>` on a `Half` row; the bug key /
  jam link as evidence. Human
  PASS / FAIL / BLOCKED / SKIPPED → `pass` / `fail` / `blocked` /
  `skipped`; non-standard entries are not recorded. A case the machine
  already recorded is simply re-recorded — the service supersedes and
  keeps both; that IS the retraction. If the run is `completed`, call
  `reopen_test_run` first. When the sheet is fully ingested,
  `close_test_run` (`closed`; `aborted` only if the pass was abandoned).
  Never change lifecycle `status`; write no run lines into notes (the
  pre-0.30 `SUPERSEDES` / `⚠ CURRENT VERDICT:` forms are retired).
- **Retraction comments** — one per ticket that published a now-retracted
  verdict, **on that ticket**, ≤ 6 lines (run id, `<case> — <old> →
  <new>`, reason, the ticket/run that established the new verdict). This
  is the one sanctioned cross-ticket comment; it is not a dump.
- **Jira**: always post **the run's FIRST human-facing summary**
  (two-wave rule: the code phase posted only a one-line status
  comment) — to the QA sub-task when the ticket has one, otherwise to
  the ticket under test. **No archive of any kind** (retired 0.33.0):
  `<ISSUEKEY>-manual-results.md` stays in the run folder and the run
  holds every verdict; a fenced dump on any ticket is a ❌. Write the
  summary as the complete
  picture, not a delta — overall verdict, stage table, confirmed bugs,
  **Retractions listed first with old → new and reason**, what needs a
  human, what was not tested — because no earlier human summary
  exists. Where the machine's verdict and the human's disagree, state
  the human's and note the machine's in one clause. (On older tickets
  where a pre-two-wave summary WAS posted, open with "supersedes the
  <date> summary for N cases".) End the summary with **Carried
  forward** — one line per still-open row of `<ISSUEKEY>-open-items.md`,
  so the reader sees what this round did *not* settle.
- **The ledger** (`../qa-pipeline/references/open-items-ledger.md`):
  this is the only stage that closes a row — and it also **appends** a
  row for anything this round reported but did not settle (a
  non-roster FAIL the user declined to file, an observation carried as
  a question, a case correction not yet applied), because the analyzer
  does not run after stage 10 and a leftover with no row is forgotten
  by round 2. For every open item a
  decision landed on in this round — a ruling given, a case promoted, a
  bug filed (write the key), a risk row executed to a verdict — fill
  `Decision` and `Closed`. Rows the user drops get the reason as their
  Decision; never delete a row.
- **Case corrections** (walk-results `Case corrections` section, or a
  tester's note that says the case is wrong): apply to the suite under
  the same confirm — `suggest_test_case` / `edit_test_case` per
  `../qa-pipeline-docs/references/qa-service-publish.md` — and list
  what changed in the report. A correction that reveals the expected
  result was wrong makes the case's verdict a **case-premise** finding,
  not a product defect: do not record a `fail` for it.
- **Observations** (walk-results `Observations`): reported in the human
  summary as `OBSERVATION (no source checked)` questions per
  `sources-of-record.md` § 7 — never as defects, never as `fail`.
- Connector absent → the run write-back is skipped with a visible note;
  the Jira comments still carry everything.

### Step 4b — The deferred handback (this stage owns it)

The code phase deliberately posts NOTHING human-facing — no summary, no
story note, no transitions, no bug filings, no questions to named
people (two-wave rule, `qa-pipeline-code` step 6). This stage is where
all of it happens, on verdicts a human has confirmed. Now that the
manual results are in:

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

A human `fail` on a **roster case** already filed (or linked) its
defect through the run — read the keys back with `run_defects` and put
them in the report. The offer below is for FAILs with **no roster
case**: risk rows never promoted, observations the tester confirmed, a
FAIL on a run without a suite. One offer listing them all — via the
`/knowledge-base` skill when installed, else per
`../qa-pipeline-code/references/bug-report-template.md` with duplicate
search first. File only what the user confirms.

## Final response

Report: the report path; counts (CONFIRMS / FILLS / RETRACTS /
non-standard / unmatched / not run); every RETRACTION on its own line
(case, old → new, reason, and the ticket its retraction comment went
to); bugs linked and bugs filed (run-filed keys from `run_defects` and
template-filed keys, separately); the run id and its final status
(`closed`, or why not); the ledger rows closed and the rows carried
forward; and what is still untested.
