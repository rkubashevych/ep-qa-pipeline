---
name: qa-run-analyzer
description: >
  Post-run health check for the QA pipeline. Reads whatever pipeline
  output files are present (context, requirements, checklist,
  test-cases, pr-summary, code-review, web-testing) and reports how the
  run went: coverage/traceability gaps, weak inputs, signs a stage
  misbehaved, and a findings digest. Writes a short run report and a
  chat summary. Auto-called at the end of qa-pipeline-docs and
  qa-pipeline-code; also run on demand. Use when the user says "analyze
  the run", "run health check", "how did that run go", "what's worth
  fixing", or after any pipeline phase.
---

# QA Run Analyzer

A meta-review of the pipeline RUN, not the product. Read-only: it never
edits the pipeline files, only inspects them and writes its own report.

## Input

Reads from the working directory whichever of these exist (upload them
if the chat is new):
`<ISSUEKEY>-context.md`, `<ISSUEKEY>-requirements.md`,
`<ISSUEKEY>-checklist.md`, `<ISSUEKEY>-test-cases.md`,
`<ISSUEKEY>-pr-summary.md`, `<ISSUEKEY>-code-review.md`,
`<ISSUEKEY>-api-testing.md`, `<ISSUEKEY>-web-testing.md`,
`<ISSUEKEY>-manual-results.md`,
`<ISSUEKEY>-remaining-cases-triage.md`, and any tester results table
(`<ISSUEKEY>-preserved-entries.tsv` or similar TC/Result/Notes file).
The last three carry post-publication corrections: when present, they
are MORE current than the stage reports — a stage-report PASS
contradicted there is a retracted verdict, not a pass.

Detect the phase from what is present:
- Docs phase = context/requirements/checklist/test-cases.
- Code phase = pr-summary/code-review/api-testing/web-testing.
Analyze whatever is there; do not require files from the other phase.

## What to check

Group every issue under one of three buckets so the fix is obvious:
- **Pipeline/skill** — the run or a stage misbehaved; fix the process
  or the skill.
- **Input** — the ticket/AC was weak; fix upstream (Jira/Confluence).
- **Product** — a real defect in the software; file/track a bug.

Severity: use 🔴 blocker, 🟡 warning, 🟢 ok.

### 1. Run / coverage health (Pipeline)
- Every REQ-N in the requirements file has >=1 checklist item; every
  behavioural requirement has >=1 test case. List orphans (REQ with no
  checks / no test cases).
- **The AC→REQ seam** (the only unguarded end of the chain): when
  `<KEY>-context.md` is present, every numbered/bulleted item in its
  Requirements and "Additional requirements (from comments)" sections
  maps to a REQ-N in the requirements file (grooming numbers them in
  order of appearance, so this is a count + ordering comparison). An
  AC item with no REQ is 🔴 — the whole downstream coverage guarantee
  is anchored on this seam.
- REQ-ID traceability is intact across requirements -> checklist ->
  test-cases -> code-review -> web-testing. Flag IDs that appear in one
  file but vanish in the next.
- Counts reconcile (where a shell is available, run
  `scripts/reconcile_counts.py --selftest` first — if the self-test
  fails, do NOT trust the script: recount by hand and raise a 🔴
  [Pipeline] finding. When it passes, run
  `scripts/reconcile_counts.py <ISSUEKEY>` from this skill's folder and
  verify its ID sets / status counts instead of recounting by hand —
  you still judge WHY a gap exists. Note: `source PASS(code)=N` is a
  source-marker tally, not a verdict count; range rows are expanded;
  `RISK-*` ids appear as "ids NOT in test-cases" — that is expected for
  risk-chasing rows, judge them, don't suppress them):
  code-review TC count == test-cases TC count;
  web-testing executed == QA+FAIL `[UI]` items + routed-in cases
  (api-testing's "Route to web-testing" + code-review `RE-ROUTE [UI]`);
  api-testing executed == QA+FAIL `[API]` items minus those it routed
  to web-testing. Flag `[API]` items that
  are neither in api-testing nor routed out. Do not "certify" the
  routing by arithmetic alone — if a case's hazard (from code-review
  findings) lives on a surface its channel never touched, flag it 🔴
  even when the counts balance.
- Structural checklist items (`[UI]` presence/type/label checks with
  no test case) appear in web-testing's "Structural checks" section —
  as executed or explicitly "not visited". Flag structural checks
  that are neither there nor explained by a Notes line.
- BLOCKED test cases (web-testing / api-testing) and any
  empty/placeholder sections.
- Completeness integrity: 🔴 when a report whose `Completeness:`
  header says `partial` (or that lacks the header AND has internal
  disagreement) feeds the run's final verdict without its missing
  cases being named in the human summary; 🔴 when any single report's
  Scope and Statistics totals disagree with each other (a real report
  shipped Scope 60 vs Statistics 62 and was resumed as "done").
- Unmapped changes: if code-review's "Unmapped changes" section is
  non-empty, surface each entry as 🟡 "PR behaviour with no covering
  case — scope creep or missing requirement; decide which". If the
  section is absent entirely (not even "None"), flag 🟡 that the
  reverse gap check did not run.
- Blast radius: if the pr-summary's "Shared / high blast-radius files"
  section is non-empty, surface it as 🟡 with a one-line note per file
  ("shared file X changed — flows outside this ticket may be affected;
  not covered by this ticket-scoped run"). This is a visibility flag
  for regression risk, not a failure of the run.

### 2. Input quality (Input)
- Missing-AC warning present (no Confluence acceptance criteria)?
- Any "(unresolved conflict)" left in requirements?
- "Requirements needing clarification" > 0 in test-cases stats?
- Grooming findings that were left as-is / skipped by the user.

### 3. Skill / process malfunctions (Pipeline/skill)
- A stage produced no output or a malformed file (missing the sections
  its template defines).
- Channel tags (`[UI]`/`[API]`/`[mobile]`/`[export/email]`) missing on
  checklist or test cases.
- A stage that clearly errored or was skipped in the chain.

### 4. QA Service sync (Pipeline) — only when the connector is present

Skip this section entirely (and say so in one line) when the QA
Service MCP tools are not in the session, or when the user declined
publishing for this run — record the reason and treat it as a normal
outcome, never a gap or a 🔴. Otherwise, locate the
ticket's suite (`list_suites` match on the story / the `QA Service
suite:` line in the QA sub-task description) and report ONE of:

- 🟢 **in sync** — suite exists; its requirement stableIds and case
  count match the requirements/test-cases files (compare via
  `get_suite`; account for deliberately skipped duplicates listed in
  the publish preview).
- 🟢 **not published yet** — no suite found AND this analyzer run is
  inside the docs orchestrator (publish is its step 6, which runs
  after this check — expected, not a failure).
- 🔴 **publish incomplete / mismatch** — suite exists but counts or
  IDs diverge from the files: list the missing/extra stableIds.
- 🟡 **write-back missing** — code phase only, when run after step 6:
  executed cases whose suite notes lack the run line. (In the
  orchestrated flow this analyzer runs BEFORE step 6, so this check
  cannot fire there — the orchestrator's mandatory **post-publish
  verification** after step 9 covers it instead. On an on-demand
  analyzer run after publish, check it here.)
- 🔴 **zeroed status buckets** — every case-status bucket reads 0
  against a non-zero total: the cases were written with a `status`
  outside `planned/implemented/partial/deferred/na` (e.g. `draft`).
  Fixable with a re-`edit_test_case` pass, not a re-publish.
- 🔴 **collapsed requirement kinds** — 0 rules AND 0 invariants AND 0
  risks among the suite's requirements: everything was filed as `fr`.
  Fixable in place with `edit_requirement` (`kind` + corrected
  `stableId`, which rewrites references).
- 🔴 **zeroed level table** — `stats.byLevel` sums to 0 against a
  non-zero case total: the cases were written without the `levels` code
  array (`AE`/`E2E`/`M`/`U`/`I`/`C`…). Those cases are also invisible to
  the implement workflow. Fixable with a re-`edit_test_case` pass.
- 🟡 **empty trace graph** — `traceLinks` is `[]` while cases carry
  `traceability`: the links never materialized; re-sending
  `traceability` on a case rebuilds the suite's edges.
- 🟡 **bare suite header** — no `summary` / `owner` / `status` /
  `lastReviewed` on the suite. Fixable with `edit_suite`.

This is the independent check on the QA Service publish — the publish
step verifies itself, but this skill re-checks it with fresh
instructions in a later stage/chat, so a silently skipped or partial
publish surfaces here.

### 5. Evidence quality (Pipeline) — can the verdicts be believed?

Audit against `../api-testing/references/absence-check-protocol.md`:

- 🔴 any absence-check PASS (in api-testing or web-testing) with no
  positive control recorded on the same surface in this run.
- 🔴 any PASS/PARTIAL on an instrumented-surface assertion (counter /
  lead / analytics / statistics / notification / dashboard) whose
  precondition provenance is API-created or unstated.
- 🔴 the same surface cited as conclusive evidence in one case and
  dismissed as unmeasurable/lagging in another case of the same run
  (one run carried nine PASSes and one BLOCKED on the same
  "No data to show" read — those cannot both be right).
- 🟡 any absence verdict from a single immediate read with no second
  read after the measured ingestion lag.
- 🟡 routing integrity: every case in api-testing's "Route to
  web-testing" section and every code-review `RE-ROUTE [UI]` case
  appears in web-testing's Results (or its Not-executed-here with a
  reason). A routed case that vanished is a coverage hole, not a pass.
- 🔴 retraction integrity: any case whose manual result / triage entry
  contradicts a published verdict with no supersede line recorded
  (`qa-service-publish.md` → "Retraction convention"). The record is
  asserting something the run's own artifacts disprove — flag it until
  `qa-manual-results` has been run.
- 🟡 manual results never ingested: runsheet outputs exist for this
  ticket (`<KEY>-runsheet.xlsx` / testdata files, or the run report
  says stage 9 ran) but no `<KEY>-manual-results.md` exists and no
  manual-results comment is on the QA sub-task. The ticket's verdicts
  are still PROVISIONAL however old they are — say so, never let
  silence read as "verified".

### 6. Findings summary (Product)
- Docs phase: # requirements, # checks, # test cases, channel
  breakdown, # needing clarification.
- Code phase: code-review PASS/FAIL/QA/RE-ROUTE/N/A; api-testing PASS/FAIL/
  FAIL CONFIRMED/FAIL REJECTED/PARTIAL/BLOCKED/NOT-TESTABLE (older
  reports may use QA for this) plus NOT-TESTABLE (instrumentation)
  routed cases and any
  endpoint-mapping corrections (ticket endpoint != real endpoint);
  web-testing PASS/FAIL/FAIL CONFIRMED/FAIL REJECTED/BLOCKED/OBSERVATION;
  the list of confirmed bugs; what was routed to "Not executed here"
  (mobile/export-email); overall verdict.

## Output

Write `<ISSUEKEY>-run-report.md` per references/output-template.md, then
give a chat summary in the exact shape of the **"Chat summary format"**
section of that template (≤10 lines: health line, top-3 issues, one
counters line). The detail lives in the file, not the chat.

If the run is clean, say so plainly — do not invent issues.

